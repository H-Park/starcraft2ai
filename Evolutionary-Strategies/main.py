from __future__ import absolute_import, division, print_function

import os
import sys

from absl import flags
from absl.flags import FLAGS

import torch

from model import ES
from train import train_loop, render_env
from pysc2.env.sc2_env import SC2Env
from sc2.sc2toatari import SC2AtariEnv


def make_sc2env():
    env_args = dict(
      map_name=FLAGS.map_name,
      step_mul=FLAGS.step_mul,
      game_steps_per_episode=0,
      screen_size_px=(FLAGS.resolution,) * 2,
      minimap_size_px=(FLAGS.resolution,) * 2,
      visualize=FLAGS.visualize
    )
    env = SC2Env(**env_args)
    return SC2AtariEnv(env, dim=FLAGS.resolution)


if __name__ == '__main__':

    flags.DEFINE_string('map_name', 'MoveToBeacon', 'environment')
    flags.DEFINE_integer('step_mul', 8, 'number of from to skip between actions')
    flags.DEFINE_integer('resolution', 32, 'resolution of the environment to run at')
    flags.DEFINE_boolean('visualize', False, 'show pygame visualisation')
    flags.DEFINE_float('lr', 0.1, 'learning rate')
    flags.DEFINE_float('lr_decay', 1, 'learning rate decay')
    flags.DEFINE_float('sigma', 0.05, 'noise standard deviation')
    flags.DEFINE_boolean('useAdam', True, 'bool to determine if to use adam optimizer')
    flags.DEFINE_integer('n', 8, 'batch size, must be even')
    flags.DEFINE_integer('max_episode_length', 240, 'maximum length of an episode')
    flags.DEFINE_integer('max_gradient_updates', 10000000, 'maximum number of updates')
    flags.DEFINE_string('restore', '', 'checkpoint from which to restore')
    flags.DEFINE_boolean('silent', False, 'Silence print statements during training')
    flags.DEFINE_boolean('test', False, 'Just render the env, no training')
    flags.DEFINE_boolean('variable_ep_len', True, "?")

    FLAGS(sys.argv)

    if not FLAGS.test:
      assert FLAGS.n % 2 == 0

    envs = []
    # add one for the unperturbed model
    for i in range(FLAGS.n + 1):
      envs.append(make_sc2env())

    chkpt_dir = 'checkpoints/%s/' % FLAGS.map_name
    if not os.path.exists(chkpt_dir):
        os.makedirs(chkpt_dir)
    synced_model = ES(envs[0].observation_space.shape[0],
                      envs[0].action_space)
    for param in synced_model.parameters():
        param.requires_grad = False
    if FLAGS.restore:
        state_dict = torch.load(FLAGS.restore)
        synced_model.load_state_dict(state_dict)

    if FLAGS.test:
        render_env(synced_model, envs[0])
    else:
        train_loop(FLAGS, synced_model, envs, chkpt_dir)
