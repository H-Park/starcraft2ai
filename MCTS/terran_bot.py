import pickle
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from MCTS import Node, State, UCTSEARCH

class TerranBot(sc2.BotAI):
    async def on_step(self, iteration):
        friendly_units, enemy_units, resource_vector = self.vectorize_macro_state()

        stripped_friendly = [unit[0] for unit in friendly_units]

        input_units = {}
        for unit in stripped_friendly:
            if unit not in input_units.keys():
                input_units[unit] = 1
            else:
                input_units[unit] += 1
        goal = input_units
        goal["Marine"] = 5
        
        self.MCTS(input_units, goal)

    # Create various high level snapshots of the current stae of the game
    # Friendly units, enemy units, friendly current resources, upgrades.

    def vectorize_macro_state(self):
        map_size = self.game_info.map_size

        # 1. Create a snapshot of friendly units
        # [[unit1, pos x1, pos y1, hp_%, shield_%, build_progress(?), ], ..]
        friendly_units = []
        unit: sc2.unit
        for unit in self.units:
            friendly_units.append(self.create_unit_vector(unit))

        # Finally, sort macroUnitVector to provide consistency for the model's input.
        friendly_units.sort(key=lambda unitVector: unitVector[0])

        # Pickle our matrix
        outfile = open("friendly", 'wb')
        pickle.dump(friendly_units, outfile)
        outfile.close()

        # 2. Create a snapshot of enemy units
        # [[unit1, pos x1, pos y1, hp_%, shield_%, build_progress(?), ], ..]
        enemy_units = []
        enemy_unit: sc2.unit
        for enemy_unit in self.known_enemy_units:
            enemy_units.append(self.create_unit_vector(enemy_unit))
        for enemyUnit in self.known_enemy_structures:
            enemy_units.append(self.create_unit_vector(enemy_unit))

        # Finally, sort macroUnitVector to provide consistency for the model's input.
        enemy_units.sort(key=lambda unitVector: unitVector[0])

        # Pickle our matrix
        outfile = open("enemy", 'wb')
        pickle.dump(enemy_units, outfile)
        outfile.close()

        # 3. Don't forget about minerals and gas and income of each
        resource_vector = [self.minerals, self.vespene]

        # Pick our matrix
        outfile = open("resource", 'wb')
        pickle.dump(resource_vector, outfile)
        outfile.close()

        return friendly_units, enemy_units, resource_vector

    def create_unit_vector(self, unit: sc2.unit):
        shield_percentage = -1
        energy_percentage = -1
        try:
            shield_percentage = unit.sheild_percentage
        except:
            # unit does not have shields do nothing
            pass
        try:
            energy_percentage = unit.energy_percentage
        except:
            # unit does not have shields do nothing
            pass
        return [unit.name,
                unit.position.x/self.game_info.map_size.width,
                unit.position.y/self.game_info.map_size.height,
                unit.health_percentage,
                shield_percentage,  # percentage of shield, -1 if unit doesn't have shields
                energy_percentage,  # percentage of energy, -1 if unit doesn't have energy
                unit.build_progress]  # scaled between 0-1.0

    def MCTS(self, initial_state, goal):
        levels = 5
        num_sims = 25
        current_node = Node(State(all_units=initial_state))
        for l in range(levels):
            current_node = UCTSEARCH(num_sims/(l+1), current_node, goal)
            print("level %d" % l)
            print("Num Children: %d" % len(current_node.children))
            for i, c in enumerate(current_node.children):
                print(i, c)
            print("Best Child: %s" % current_node.state)
            print("--------------------------------")
