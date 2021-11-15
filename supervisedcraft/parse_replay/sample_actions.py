from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import json
from absl import flags
from tqdm import tqdm

from google.protobuf.json_format import Parse

from pysc2.lib import features
from s2clientprotocol import sc2api_pb2 as sc_pb
from s2clientprotocol import common_pb2 as sc_common


FLAGS = flags.FLAGS
flags.DEFINE_string(name='version', default='4.10.0',
                    help='Game version to use, if replays don\'t match, ignore them')
flags.DEFINE_string(name='hq_replay_set', default='../high_quality_replays/Terran_vs_Zerg.json',
                    help='File storing replays list')
flags.DEFINE_string(name='parsed_replays', default='../parsed_replays',
                    help='Path for parsed actions')
flags.DEFINE_string(name='infos_path', default='../replays_infos',
                    help='Paths for infos of replays')
flags.DEFINE_integer(name='step_mul', default=8,
                     help='step size')
flags.DEFINE_integer(name='skip', default=96,
                     help='# of skipped frames')
FLAGS(sys.argv)

RECTANGULAR_DIMENSIONS = features.Dimensions(screen=(84, 80), minimap=(64, 67))

def sample_action_from_player(action_path):
    feats = features.Features(features.AgentInterfaceFormat(
        feature_dimensions=RECTANGULAR_DIMENSIONS,
        hide_specific_actions=False))
    with open(action_path) as f:
        actions = json.load(f)

    frame_id = 0
    result_frames = []
    for action_strs in actions:
        action_name = None
        for action_str in action_strs:
            action = Parse(action_str, sc_pb.Action())
            try:
                func_id = feats.reverse_action(action).function
                if func_id.split('.')[1] in {'Build', 'Train', 'Research', 'Morph', 'Cancel', 'Halt', 'Stop'}:
                    action_name = func_id
                    break
            except:
                pass
        if frame_id > 0 and (action_name is not None or frame_id%FLAGS.skip == 0):
            result_frames.append(frame_id-FLAGS.step_mul)

        frame_id += FLAGS.step_mul

    return result_frames

def sample_action(replay_path, action_path, sampled_path):
    replay_info = os.path.join(FLAGS.infos_path, replay_path)
    if not os.path.isfile(replay_info):
        return
    with open(replay_info) as f:
        info = json.load(f)

    result = []
    proto = Parse(info['info'], sc_pb.ResponseReplayInfo())
    for p in proto.player_info:
        player_id = p.player_info.player_id
        race = sc_common.Race.Name(p.player_info.race_actual)

        action_file = os.path.join(action_path, race, '{}@{}'.format(player_id, replay_path))
        if not os.path.isfile(action_file):
            return

        result.append(sample_action_from_player(action_file))
        
    assert len(result) == 2
    sampled_actions = sorted(set(result[0]) | set(result[1]))

    with open(os.path.join(sampled_path, replay_path), 'w') as f:
        json.dump(sampled_actions, f)

def main():
    with open(FLAGS.hq_replay_set) as f:
        replay_list = json.load(f)
    replay_list = sorted([p for p, _ in replay_list])

    race_vs_race = os.path.basename(FLAGS.hq_replay_set).split('.')[0]
    sampled_path = os.path.join(FLAGS.parsed_replays, 'SampledActions', race_vs_race)
    if not os.path.isdir(sampled_path):
        os.makedirs(sampled_path)
    action_path = os.path.join(FLAGS.parsed_replays, 'Actions', race_vs_race)

    pbar = tqdm(total=len(replay_list), desc='#Replay')
    for replay_path in replay_list:
        sample_action(os.path.basename(replay_path), action_path, sampled_path)
        pbar.update()

if __name__ == '__main__':
    main()
