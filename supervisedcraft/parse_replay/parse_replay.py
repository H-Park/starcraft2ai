from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import sys
import json
import time
import signal
import threading
import queue as Queue
import multiprocessing
from absl import flags
from future.builtins import range

from google.protobuf.json_format import MessageToJson

from pysc2 import run_configs
from pysc2.lib import point
from s2clientprotocol import sc2api_pb2 as sc_pb
from s2clientprotocol import common_pb2 as sc_common

import stream

FLAGS = flags.FLAGS

flags.DEFINE_string(name='version', default='4.10.0',
                    help='Game version to use, if replays don\'t match, ignore them')
flags.DEFINE_string(name='hq_replay_set', default='../high_quality_replays/Terran_vs_Zerg.json',
                    help='File storing replays list')
flags.DEFINE_string(name='save_path', default='../parsed_replays',
                    help='Path for saving results')

flags.DEFINE_integer(name='n_instance', default=1,
                     help='# of processes to run')
flags.DEFINE_integer(name='batch_size', default=1,
                     help='# of replays to process in one iter')

flags.DEFINE_integer(name='width', default=84,
                     help='World width')
flags.DEFINE_integer(name='map_size', default=64,
                     help='Map size')
FLAGS(sys.argv)


size = point.Point(FLAGS.map_size, FLAGS.map_size)
interface = sc_pb.InterfaceOptions(raw=True, score=True,
                feature_layer=sc_pb.SpatialCameraSetup(width=FLAGS.width))
size.assign_to(interface.feature_layer.resolution)
size.assign_to(interface.feature_layer.minimap_resolution)


# Configure save path globally, as windows and mac don't like editing flags values
race_vs_race = os.path.basename(FLAGS.hq_replay_set).split('.')[0]
save_path = os.path.join(FLAGS.save_path, 'SampledObservations', race_vs_race)

for race in set(race_vs_race.split('_vs_')):
    path = os.path.join(save_path, race)
    if not os.path.isdir(path):
        os.makedirs(path)

    path = path.replace('SampledObservations', 'GlobalInfos')
    if not os.path.isdir(path):
        os.makedirs(path)

class ReplayProcessor(multiprocessing.Process):
    """A Process that pulls replays and processes them."""
    def __init__(self, run_config, replay_queue, counter, total_num):
        super(ReplayProcessor, self).__init__()
        self.run_config = run_config
        self.replay_queue = replay_queue
        self.counter = counter
        self.total_num = total_num

    def run(self):
        signal.signal(signal.SIGTERM, lambda a, b: sys.exit())  # Exit quietly.
        while True:
            with self.run_config.start() as controller:
                for _ in range(FLAGS.batch_size):
                    try:
                        replay_path = self.replay_queue.get()
                    except Queue.Empty:
                        return
                    try:
                        with self.counter.get_lock():
                            self.counter.value += 1
                            print('Processing {}/{} ...'.format(self.counter.value, self.total_num))
                        sampled_action_path = os.path.join(save_path.replace(
                            'SampledObservations', 'SampledActions'), os.path.basename(replay_path))
                        if not os.path.isfile(sampled_action_path):
                            return
                        with open(sampled_action_path) as f:
                            actions = json.load(f)
                        actions.insert(0, 0)

                        replay_data = self.run_config.replay_data(replay_path)
                        info = controller.replay_info(replay_data)
                        map_data = None
                        if info.local_map_path:
                            map_data = self.run_config.map_data(info.local_map_path)

                        for player_info in info.player_info:
                            race = sc_common.Race.Name(player_info.player_info.race_actual)
                            player_id = player_info.player_info.player_id

                            observation_path = os.path.join(save_path, race,
                                                            '{}@{}'.format(player_id, os.path.basename(replay_path)))
                            global_info_path = observation_path.replace('SampledObservations', 'GlobalInfos')

                            if os.path.isfile(observation_path) and os.path.isfile(global_info_path):
                                continue
                            
                            ostream = stream.open(observation_path, 'wb', buffer_size=1000)
                            self.process_replay(controller, replay_data, map_data, player_id, actions,
                                                ostream, global_info_path)
                            ostream.close()
                    except Exception as e:
                        try:
                            ostream.close()
                            if os.path.isfile(observation_path):
                                os.remove(observation_path)

                            if os.path.isfile(global_info_path):
                                os.remove(global_info_path)
                        except:
                            pass

                        print(e)
                        break
                    finally:
                        self.replay_queue.task_done()

    def process_replay(self, controller, replay_data, map_data, player_id, actions, ostream, global_info_path):
        controller.start_replay(sc_pb.RequestStartReplay(
            replay_data=replay_data,
            map_data=map_data,
            options=interface,
            observed_player_id=player_id))

        global_info = {'game_info': controller.game_info(),
                       'data_raw': controller.data_raw()}
        with open(global_info_path, 'w') as f:
            json.dump({k:MessageToJson(v) for k, v in global_info.items()}, f)

        controller.step()
        for pre_id, id in zip(actions[:-1], actions[1:]):
            controller.step(id - pre_id)
            obs = controller.observe()
            ostream.write(obs)

def replay_queue_filler(replay_queue, replay_list):
    """A thread that fills the replay_queue with replay filenames."""
    for replay_path in replay_list:
        replay_queue.put(replay_path)

def main():
    run_config = run_configs.get(version=FLAGS.version)
    try:
        with open(FLAGS.hq_replay_set) as f:
            replay_list = json.load(f)
        replay_list = sorted([p for p, _ in replay_list])

        replay_queue = multiprocessing.JoinableQueue(FLAGS.n_instance)
        replay_queue_thread = threading.Thread(target=replay_queue_filler,
                                           args=(replay_queue, replay_list))
        replay_queue_thread.daemon = True
        replay_queue_thread.start()

        counter = multiprocessing.Value('i', 0)
        for _ in range(FLAGS.n_instance):
            p = ReplayProcessor(run_config, replay_queue, counter, len(replay_list))
            p.daemon = True
            p.start()
            time.sleep(1)   # Stagger startups, otherwise they seem to conflict somehow

        replay_queue.join() # Wait for the queue to empty.
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, exiting.")

if __name__ == '__main__':
    main()
