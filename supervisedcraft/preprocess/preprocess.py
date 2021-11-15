from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags
import configparser
import glob
import os
import json
import multiprocessing
import queue as Queue
import signal
import sys
import threading
import time

from itertools import chain
from future.builtins import range
from google.protobuf.json_format import MessageToJson, Parse

from pysc2 import run_configs
from pysc2.lib import replay
from pysc2.lib.remote_controller import RequestError
from s2clientprotocol import sc2api_pb2 as sc_pb
from s2clientprotocol import common_pb2 as sc_common


FLAGS = flags.FLAGS
FLAGS(sys.argv)

config = configparser.ConfigParser()
config.read("../settings.conf")

def valid_replay(info, ping):
    """Make sure the replay isn't corrupt, and is worth looking at."""
    if info.HasField("error"):
        return False
    if info.base_build != ping.base_build:
        return False
    if info.game_duration_loops < int(config["preprocess"]["min_duration"]):
        return False
    if len(info.player_info) != 2:
        return False
    for player_info in info.player_info:
        if player_info.player_apm < int(config["preprocess"]["min_apm"]) or player_info.player_mmr < int(config["preprocess"]["min_mmr"]):
            # Low APM = player AFK
            # Low MMR = player not at least Diamond MMR
            return False
        if player_info.player_result.result not in {1, 2}:
            return False
    return True

class ReplayProcessor(multiprocessing.Process):
    """A Process that pulls replays and processes them."""
    def __init__(self, run_config, replay_queue, counter, bad_counter, high_quality_replays, total_num):
        super(ReplayProcessor, self).__init__()
        self.run_config = run_config
        self.replay_queue = replay_queue
        self.counter = counter
        self.bad_counter = bad_counter
        self.high_quality_replays = high_quality_replays
        self.total_num = total_num

    def run(self):
        signal.signal(signal.SIGTERM, lambda a, b: sys.exit())  # Exit quietly.
        with self.run_config.start() as controller:
            while not self.replay_queue.empty():
                try:
                    replay_path = self.replay_queue.get()
                    try:
                        replay_data = self.run_config.replay_data(replay_path)
                        try:
                            info = controller.replay_info(replay_data)
                            info_json = MessageToJson(info)
                            proto = Parse(info_json, sc_pb.ResponseReplayInfo())
                            if valid_replay(proto, controller.ping()):
                                players_info = proto.player_info
                                races = '_vs_'.join(sorted(sc_common.Race.Name(player_info.player_info.race_actual)
                                    for player_info in players_info))
                                self.high_quality_replays[races].append(replay_path)
                        except RequestError as _:
                            with self.bad_counter.get_lock():
                                self.bad_counter.value += 1
                        finally:
                            with self.counter.get_lock():
                                self.counter.value += 1
                                print('Processing {}/{} ...'.format(self.counter.value, self.total_num))
                    except Exception as _:
                        with self.bad_counter.get_lock():
                            self.bad_counter.value += 1
                except Queue.Empty:
                    return 
                finally:
                    self.replay_queue.task_done()
def replay_queue_filler(replay_queue, replay_list):
    """A thread that fills the replay_queue with replay paths."""
    for replay_path in replay_list:
        replay_queue.put(replay_path)

def main():
    if not os.path.isdir(config["global"]["info_path"]):
        os.makedirs(config["global"]["info_path"])

    run_config = run_configs.get(version=config["global"]["version"])
    try:
        replay_list = sorted(chain(*[run_config.replay_paths(path)
                                        for path in config["global"]["replay_dir"].split(';')
                                            if len(path.strip()) > 0]))
        replay_queue = multiprocessing.JoinableQueue(int(config["preprocess"]["n_instance"]) * 10)
        replay_queue_thread = threading.Thread(target=replay_queue_filler,
                                               args=(replay_queue, replay_list))
        replay_queue_thread.daemon = True
        replay_queue_thread.start()

        races = ["Protoss_vs_Protoss",
                "Protoss_vs_Terran",
                "Protoss_vs_Zerg",
                "Terran_vs_Terran",
                "Terran_vs_Zerg",
                "Zerg_vs_Zerg"]
        high_quality_replays = {}
        manager = multiprocessing.Manager()
        for race in races:
            high_quality_replays[race] = manager.list()

        counter = multiprocessing.Value('i', 0)
        bad_counter = multiprocessing.Value('i', 0)
        replay_processors = []
        for _ in range(int(config["preprocess"]["n_instance"])):
            rp = ReplayProcessor(run_config, replay_queue, counter, bad_counter, high_quality_replays,len(replay_list))
            rp.daemon = True
            rp.start()
            replay_processors.append(rp)
            time.sleep(3)   # Stagger startups, otherwise they seem to conflict somehow

        replay_queue.join() # Wait for the queue to empty.
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, exiting.")

    time.sleep(3)
    print("Saving good replay paths...")
    for match_up, replay_infos in high_quality_replays.items():
        if match_up == races[-1]:
            print(match_up, ":\t\t", str(len(replay_infos)))
        else:
            print(match_up, ":\t", str(len(replay_infos)))
        with open(os.path.join(config["global"]["info_path"], match_up+'.txt'), 'w') as f:
            num_replays = len(replay_infos)
            for i, replay_info in enumerate(replay_infos):
                if i != num_replays:
                    f.write(replay_info + "\n")
                else:
                    f.write(replay_info)

    with bad_counter.get_lock():
        print("Corrupt replays:\t", str(bad_counter.value))



if __name__ == '__main__':
    main()
