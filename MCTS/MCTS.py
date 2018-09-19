#!/usr/bin/env python
import random
import math
import hashlib
import logging
from copy import deepcopy

# MCTS scalar.  Larger scalar will increase exploitation, smaller will increase exploration.
SCALAR = 1/math.sqrt(2.0)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('MyLogger')


class State():
    NUM_TURNS = 10
    GOAL = 0

    def __init__(self, all_units={}):
        self.units = all_units

    def next_state(self):
        # TODO: get all possible build options from self.units

        # get all of the race's units (Terran)

        # see if we have the units tech requirements
        # if yes, add to possible build option
        # if no, continue

        units = deepcopy(self.units)
        state2 = State(units)
        state2.add_unit("Marine")

        return state2

    def add_unit(self, unit):
        for unit in self.units:
        	if unit not in self.units.keys():
        		self.units[unit] = 1
        	else:
        		self.units[unit] += 1

    def terminal(self, goal):
    	return self.units == goal

    def reward(self):
        # TODO: evaluate build order time (Get inspiration from dave's BOSS)
        return 1

    def __eq__(self, other):
        return self.units == other.units

    def __repr__(self):
        return "Units: {}".format(' '.join(self.units))


class Node():
    def __init__(self, state, parent=None):
        self.visits = 1
        self.reward = 0.0
        self.state = state
        self.children = []
        self.parent = parent

    def add_child(self, child_state):
        child = Node(child_state, self)
        self.children.append(child)

    def update(self, reward):
        self.reward += reward
        self.visits += 1

    def fully_expanded(self):
        # TODO: This
        return len(self.children) == 1

    def __repr__(self):
        s = "Node; children: %d; visits: %d; reward: %f" % (
            len(self.children), self.visits, self.reward)
        return s


def UCTSEARCH(budget, root, goal):
    for iter in range(int(budget)):
        print(iter)
        if iter % 10000 == 9999:
            logger.info("simulation: %d" % iter)
            logger.info(root)
        front = TREEPOLICY(root, goal)
        reward = DEFAULTPOLICY(front.state, goal)
        BACKUP(front, reward)
    return BESTCHILD(root, 0)


def TREEPOLICY(node, goal):
    # a hack to force 'exploitation' in a game where there are many options, and you may never/not want to fully expand first
    while not node.state.terminal(goal):
        if len(node.children) == 0:
            return EXPAND(node)
        elif random.uniform(0, 1) < .5:
            node = BESTCHILD(node, SCALAR)
        else:
            if not node.fully_expanded():
                return EXPAND(node)
            else:
                node = BESTCHILD(node, SCALAR)
    return node


def EXPAND(node):
    tried_children = [c.state for c in node.children]
    new_state = node.state.next_state()
    while new_state in tried_children:
        new_state = node.state.next_state()
    logger.info(new_state.units)
    node.add_child(new_state)
    logger.info(node.children[-1].state.units)
    return node.children[-1]

# current this uses the most vanilla MCTS formula it is worth experimenting with THRESHOLD ASCENT (TAGS)


def BESTCHILD(node, scalar):
    best_score = 0.0
    best_children = []
    print(node.children)
    for c in node.children:
        exploit = c.reward / c.visits
        explore = math.sqrt(2.0*math.log(node.visits)/float(c.visits))
        score = exploit + scalar * explore
        if score == best_score:
            best_children.append(c)
        if score > best_score:
            best_children = [c]
            best_score = score
    if len(best_children) == 0:
        logger.warn("OOPS: no best child found, probably fatal")
    return random.choice(best_children)


def DEFAULTPOLICY(state, goal):
    while not state.terminal(goal):
        state = state.next_state()
    return state.reward()


def BACKUP(node, reward):
    while node is not None:
        node.visits += 1
        node.reward += reward
        node = node.parent
    return
