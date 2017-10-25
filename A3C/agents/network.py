from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import tensorflow.contrib.layers as layers
import tensorflow.contrib.rnn as rnn
from pysc2.lib.features import SCREEN_FEATURES, MINIMAP_FEATURES


def build_net(minimap, screen, info, msize, ssize, num_action, ntype):
    if ntype == 'atari':
        return build_atari(minimap, screen, info, msize, ssize, num_action)
    elif ntype == 'fcn':
        return build_fcn(minimap, screen, info, msize, ssize, num_action)
    elif ntype == 'innovationdx':
        return build_innovationdx(minimap, screen, info, ssize, num_action)
    else:
        raise 'FLAGS.net must be atari, fcn, or innovationdx'


def build_innovationdx(minimap, screen, info, ssize, num_action):
    # Extract features, while preserving the dimensions
    m_pp = layers.conv2d(tf.transpose(minimap, [0, 2, 3, 1]),
                         num_outputs=1,
                         kernel_size=1,
                         stride=1,
                         padding="SAME",
                         scope='m_pp')
    mconv1 = layers.conv2d(m_pp,
                           num_outputs=16,
                           kernel_size=5,
                           stride=1,
                           padding="SAME",
                           scope='mconv1')
    mconv2 = layers.conv2d(mconv1,
                           num_outputs=32,
                           kernel_size=3,
                           stride=1,
                           padding="SAME",
                           scope='mconv2')
    s_pp = layers.conv2d(tf.transpose(screen, [0, 2, 3, 1]),
                         num_outputs=1,
                         kernel_size=1,
                         stride=1,
                         padding="SAME",
                         scope='s_pp')
    sconv1 = layers.conv2d(s_pp,
                           num_outputs=16,
                           kernel_size=5,
                           stride=1,
                           padding="SAME",
                           scope='sconv1')
    sconv2 = layers.conv2d(sconv1,
                           num_outputs=32,
                           kernel_size=3,
                           stride=1,
                           padding="SAME",
                           scope='sconv2')

    # Create the state representation by concatenating on the channel axis
    state_representation = tf.concat([mconv2, sconv2, tf.reshape(info, [-1, ssize, ssize, 1])], axis=3)

    # Preform another convolution, but preserve the dimensions by using params (1, 1, 1)
    spatial_action_policy = layers.conv2d(state_representation,
                                          num_outputs=1,
                                          kernel_size=1,
                                          stride=1,
                                          activation_fn=None,
                                          scope='spatial_feat')

    lstm_layer_cell = rnn.BasicLSTMCell(layers.flatten(spatial_action_policy).shape)

    outputs, states = rnn.dynamic_rnn(lstm_layer_cell, layers.flatten(spatial_action_policy), dtype=tf.float32)

    spatial_action = tf.nn.softmax(outputs)

    feat_fc = layers.fully_connected(layers.flatten(spatial_action_policy),
                                     num_outputs=256,
                                     activation_fn=tf.nn.relu,
                                     scope='feat_fc')
    non_spatial_action = layers.fully_connected(feat_fc,
                                                num_outputs=num_action,
                                                activation_fn=tf.nn.softmax,
                                                scope='non_spatial_action')
    value = layers.fully_connected(feat_fc,
                                   num_outputs=1,
                                   activation_fn=None,
                                   scope='value')

    return spatial_action, non_spatial_action, value


def build_atari(minimap, screen, info, msize, ssize, num_action):
    # Extract features
    mconv1 = layers.conv2d(tf.transpose(minimap, [0, 2, 3, 1]),
                           num_outputs=16,
                           kernel_size=8,
                           stride=4,
                           scope='mconv1')
    mconv2 = layers.conv2d(mconv1,
                           num_outputs=32,
                           kernel_size=4,
                           stride=2,
                           scope='mconv2')
    sconv1 = layers.conv2d(tf.transpose(screen, [0, 2, 3, 1]),
                           num_outputs=16,
                           kernel_size=8,
                           stride=4,
                           scope='sconv1')
    sconv2 = layers.conv2d(sconv1,
                           num_outputs=32,
                           kernel_size=4,
                           stride=2,
                           scope='sconv2')
    info_fc = layers.fully_connected(layers.flatten(info),
                                     num_outputs=256,
                                     activation_fn=tf.tanh,
                                     scope='info_fc')

    # Compute spatial actions, non spatial actions and value
    feat_fc = tf.concat([layers.flatten(mconv2), layers.flatten(sconv2), info_fc], axis=1)
    feat_fc = layers.fully_connected(feat_fc,
                                     num_outputs=256,
                                     activation_fn=tf.nn.relu,
                                     scope='feat_fc')

    spatial_action_x = layers.fully_connected(feat_fc,
                                              num_outputs=ssize,
                                              activation_fn=tf.nn.softmax,
                                              scope='spatial_action_x')
    spatial_action_y = layers.fully_connected(feat_fc,
                                              num_outputs=ssize,
                                              activation_fn=tf.nn.softmax,
                                              scope='spatial_action_y')
    spatial_action_x = tf.reshape(spatial_action_x, [-1, 1, ssize])
    spatial_action_x = tf.tile(spatial_action_x, [1, ssize, 1])
    spatial_action_y = tf.reshape(spatial_action_y, [-1, ssize, 1])
    spatial_action_y = tf.tile(spatial_action_y, [1, 1, ssize])
    spatial_action = layers.flatten(spatial_action_x * spatial_action_y)

    non_spatial_action = layers.fully_connected(feat_fc,
                                                num_outputs=num_action,
                                                activation_fn=tf.nn.softmax,
                                                scope='non_spatial_action')
    value = tf.reshape(layers.fully_connected(feat_fc,
                                              num_outputs=1,
                                              activation_fn=None,
                                              scope='value'), [-1])

    return spatial_action, non_spatial_action, value


def build_fcn(minimap, screen, info, msize, ssize, num_action):
    # Extract features, while preserving the dimensions
    m_one_hot = layers.one_hot_encoding(tf.transpose(minimap, [0, 2, 3, 1]),
                                         num_classes=MINIMAP_FEATURES.player_relative.scale
                                         )[:, :, :, 1:]
    m_pp = layers.conv2d(m_one_hot,
                         num_outputs=1,
                         kernel_size=1,
                         stride=1,
                         padding="SAME",
                         scope='m_pp')
    mconv1 = layers.conv2d(m_pp,
                           num_outputs=16,
                           kernel_size=5,
                           stride=1,
                           padding="SAME",
                           scope='mconv1')
    mconv2 = layers.conv2d(mconv1,
                           num_outputs=32,
                           kernel_size=3,
                           stride=1,
                           padding="SAME",
                           scope='mconv2')
    s_one_hot = layers.one_hot_encoding(tf.transpose(screen, [0, 2, 3, 1]),
                                         num_classes=SCREEN_FEATURES.player_relative.scale
                                         )[:, :, :, 1:]
    s_pp = layers.conv2d(s_one_hot,
                         num_outputs=1,
                         kernel_size=1,
                         stride=1,
                         padding="SAME",
                         scope='m_pp')
    sconv1 = layers.conv2d(s_pp,
                           num_outputs=16,
                           kernel_size=5,
                           stride=1,
                           padding="SAME",
                           scope='sconv1')
    sconv2 = layers.conv2d(sconv1,
                           num_outputs=32,
                           kernel_size=3,
                           stride=1,
                           padding="SAME",
                           scope='sconv2')

    # Create the state representation by concatenating on the channel axis
    state_representation = tf.concat([mconv2, sconv2, tf.reshape(info, [-1, ssize, ssize, 1])], axis=3)

    # Preform another convolution, but preserve the dimensions by using params (1, 1, 1)
    spatial_action_policy = layers.conv2d(state_representation,
                                          num_outputs=1,
                                          kernel_size=1,
                                          stride=1,
                                          activation_fn=None,
                                          scope='spatial_feat')
    spatial_action = tf.nn.softmax(layers.flatten(spatial_action_policy))

    feat_fc = layers.fully_connected(layers.flatten(state_representation),
                                     num_outputs=256,
                                     activation_fn=tf.nn.relu,
                                     scope='feat_fc')
    non_spatial_action = layers.fully_connected(feat_fc,
                                                num_outputs=num_action,
                                                activation_fn=tf.nn.softmax,
                                                scope='non_spatial_action')
    value = layers.fully_connected(feat_fc,
                                   num_outputs=1,
                                   activation_fn=None,
                                   scope='value')

    return spatial_action, non_spatial_action, value
