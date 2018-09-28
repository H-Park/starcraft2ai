#!/usr/bin/env python
import random
import math
import logging
from copy import deepcopy

import sc2
from sc2 import Race
from sc2.ids import unit_typeid as sc2_units

from units import get_tech_requirements


from units import terran_units, protoss_units, zerg_units

# MCTS scalar.  Larger scalar will increase exploitation, smaller will increase exploration.
SCALAR = 1/math.sqrt(2.0)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('MyLogger')

race = None
game_data = None
state = None
units = None


def contains(list1, list2):
    for i in list2:
        if i not in list1:
            return False
    return True


# Make a list of all the units needed to get goal_g
def get_relevant_units(goal):
    needed_units = []
    units = []
    for unit, value in goal.items():
        units.append(unit)

    while len(units) > 0:
        print("popping a unit off")
        unit = units.pop()
        print(unit)
        tech_requirements = get_tech_requirements(game_data, unit)
        if len(tech_requirements) == 0:
            print(str(unit) + " has no tech requirements")
            print()
        while len(tech_requirements) > 0:
            print("Tech requirements for " + str(unit) + " are: ")
            print(tech_requirements)
            print("Current Build order: ")
            print(needed_units)
            for i in tech_requirements:
                if i in needed_units:
                    print(str(i) + " already in build order, removing from tech_requirements")
                    tech_requirements.remove(i)
                    continue
                print("Particular tech requirement unit " + str(i))
                if i == sc2_units.UnitTypeId.SUPPLYDEPOT and i not in needed_units:
                    print("Adding " + str(i) + " to build order")
                    tech_requirements.remove(i)
                    needed_units.append(i)
                    continue
                print("Computing sub_tech_requirements...")
                sub_tech_requirements = get_tech_requirements(game_data, i)
                if type(sub_tech_requirements) is list:
                    for sub_tech_requirement in sub_tech_requirements:
                        if sub_tech_requirement not in needed_units:
                            print("Adding " + str(sub_tech_requirement) + " to needed_units")
                            tech_requirements.append(sub_tech_requirement)
                else:
                    if sub_tech_requirements not in needed_units:
                        print("Adding " + str(sub_tech_requirements) + " to needed_units")
                        tech_requirements.append(sub_tech_requirements)
                print(needed_units)
            print()
    for unit, value in goal.items():
        needed_units.append(unit)

    print(needed_units)

    if sc2_units.UnitTypeId.MARAUDER in needed_units:
        barrack_index = needed_units.index(sc2_units.UnitTypeId.BARRACKS)
        needed_units.insert(barrack_index + 1, sc2_units.UnitTypeId.TECHLAB)
    if sc2_units.UnitTypeId.SIEGETANK in needed_units:
        factory_index = needed_units.index(sc2_units.UnitTypeId.FACTORY)
        needed_units.insert(factory_index+1, sc2_units.UnitTypeId.TECHLAB)
    if sc2_units.UnitTypeId.BATTLECRUISER in needed_units:
        starport_index = needed_units.index(sc2_units.UnitTypeId.STARPORT)
        needed_units.insert(starport_index+1, sc2_units.UnitTypeId.TECHLAB)

    print(needed_units)
    print()
    import sys
    sys.exit()
    return needed_units


class MCTS(object):
    def __init__(self, player_race, g_data, game_state):
        global race, game_data, state
        race = player_race
        game_data = g_data
        state = game_state

    # use a MCTS to find the optimal build order from intial_state to goal
    def find_build_order(self, initial_state, goal):
        levels = 5
        num_sims = 25
        current_node = Node(State(all_units=initial_state))
        final_node = current_node
        for l in range(levels):
            final_node = utc_search(num_sims / (l + 1), current_node, goal)
        return self.get_build_order_from_node(final_node)

    # traverse up the tree to get the build order
    @staticmethod
    def get_build_order_from_node(node):
        build_actions = [] # container for the build commmands at each node visited
        n = node
        # while we have a parent node
        while n:
            build_actions.append(n.action)
            n = n.parent

        # reverse the build order, as we traversed up the tree
        build_actions.reverse()

        # return our build actions
        return build_actions

    # Create a straight forward build order
    def get_basic_build_order(self, initial_state, goal):
        return get_relevant_units(goal)


class State(object):
    NUM_TURNS = 10
    GOAL = 0

    def __init__(self, all_units):
        self.units = all_units
        self.action = None

    def next_state(self):
        # get all of the race's units (Terran)

        # see if we have the units tech requirements
        # if yes, add to possible build option
        # if no, continue

        # get all possible build command from the current state
        possible_units_to_add = []
        if race == Race.Terran:
            for unit in terran_units:
                if self.has_tech_requirement(unit) and self.has_supply(unit):
                    possible_units_to_add.append(unit)
        elif race == Race.Protoss:
            for unit in protoss_units:
                if self.has_tech_requirement(unit) and self.has_supply(unit):
                    possible_units_to_add.append(unit)

        elif race == Race.Zerg:
            for unit in protoss_units:
                if self.has_tech_requirement(unit) and self.has_supply(unit):
                    possible_units_to_add.append(unit)

        unit_to_add = random.choice(possible_units_to_add)
        units = deepcopy(self.units)
        state2 = State(units)
        state2.add_unit(unit_to_add)
        state2.action = unit_to_add

        return state2

    # Given a unit, determine if the tech requirements is a subset of self.units,
    # If the building is an addon, determine if there is room for it
    def has_tech_requirement(self, unit):
        tech_requirments = game_data.units[unit.value].tech_requirement
        if tech_requirments is None:
            return True
        if type(tech_requirments) is list:
            for tech_requirment in tech_requirments:
                if tech_requirment.value not in self.units.keys():
                    return False
            return True
        else:
            return tech_requirments.value not in self.units.keys()

    def has_supply(self, unit):
        supply_required = game_data.units[unit.value]._proto.food_required
        # print(supply_required)
        if supply_required == 0:
            return True

        # get our current supply used and our current supply cap
        supply_used = 0
        supply_cap = 0
        for unit, quantity in self.units.items():
            supply_used += game_data.units[unit.value]._proto.food_required * quantity
            supply_cap += game_data.units[unit.value]._proto.food_provided * quantity

        # cap our supply at 200
        if supply_cap > 200:
            supply_cap = 200

        # print(self.units)
        # print(supply_used, supply_cap)
        # print()

        return supply_cap > (supply_used + supply_required)

    def add_unit(self, unit):
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


class Node(object):
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


def utc_search(budget, root, goal):
    global units
    units = get_relevant_units(goal)
    for iter in range(int(budget)):
        front = tree_policy(root, goal)
        reward = default_policy(front.state, goal)
        backup(front, reward)
    return best_child(root, 0)


def tree_policy(node, goal):
    # a hack to force 'exploitation' in a game where there are many options, and you may never/not want to fully expand first
    while not node.state.terminal(goal):
        if len(node.children) == 0:
            return expand(node)
        elif random.uniform(0, 1) < .5:
            node = best_child(node, SCALAR)
        else:
            if not node.fully_expanded():
                return expand(node)
            else:
                node = best_child(node, SCALAR)
    return node


def expand(node):
    tried_children = [c.state for c in node.children]
    new_state = node.state.next_state()
    while new_state in tried_children:
        new_state = node.state.next_state()
    node.add_child(new_state)
    return node.children[-1]

# current this uses the most vanilla MCTS formula it is worth experimenting with THRESHOLD ASCENT (TAGS)


def best_child(node, scalar):
    best_score = 0
    best_children = []
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


def default_policy(state, goal):
    while not state.terminal(goal):
        state = state.next_state()
    return state.reward()


def backup(node, reward):
    while node is not None:
        node.visits += 1
        node.reward += reward
        node = node.parent