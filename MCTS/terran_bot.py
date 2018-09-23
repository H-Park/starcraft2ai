import pickle
import sc2
from sc2.ids import unit_typeid as sc2_units
from MCTS import MCTS
from copy import deepcopy
import time


class TerranBot(sc2.BotAI):
    def __init__(self):
        super().__init__()

    async def on_step(self, iteration):
        friendly_units, enemy_units, resource_vector = self.vectorize_macro_state()

        stripped_friendly = [unit[0] for unit in friendly_units]

        input_units = {}
        for unit in stripped_friendly:
            if unit not in input_units.keys():
                input_units[unit] = 1
            else:
                input_units[unit] += 1
        goal = deepcopy(input_units)
        goal[sc2_units.UnitTypeId.MARINE] = 5
        goal[sc2_units.UnitTypeId.BATTLECRUISER] = 2
        
        start = time.time()
        mcts = MCTS(self.race, self._game_data, self.state)
        optimal_build_order = mcts.find_build_order(input_units, goal)
        end = time.time()
        print("Total MCTS Time: " + str(end - start))

    # Create various high level snapshots of the current stae of the game
    # Friendly units, enemy units, friendly current resources, upgrades.

    def vectorize_macro_state(self):
        # 1. Create a snapshot of friendly units
        # [[unit1, pos x1, pos y1, hp_%, shield_%, build_progress(?), ], ..]
        friendly_units = []
        for unit in self.units:
            friendly_units.append(self.create_unit_vector(unit))

        # Finally, sort friendly_units to provide consistency for the model's input.
        friendly_units.sort(key=lambda unit_vector: unit_vector[0].value)

        # # Pickle our matrix
        # outfile = open("friendly", 'wb')
        # pickle.dump(friendly_units, outfile)
        # outfile.close()

        # 2. Create a snapshot of enemy units
        # [[unit1, pos x1, pos y1, hp_%, shield_%, build_progress(?), ], ..]
        enemy_units = []
        for enemy_unit in self.known_enemy_units:
            enemy_units.append(self.create_unit_vector(enemy_unit))
        for enemy_unit in self.known_enemy_structures:
            enemy_units.append(self.create_unit_vector(enemy_unit))

        # Finally, sort macroUnitVector to provide consistency for the model's input.
        enemy_units.sort(key=lambda unit_vector: unit_vector[0].valu)

        # # Pickle our matrix
        # outfile = open("enemy", 'wb')
        # pickle.dump(enemy_units, outfile)
        # outfile.close()

        # 3. Don't forget about minerals and gas and income of each
        resource_vector = [self.minerals, self.vespene]

        # # Pick our matrix
        # outfile = open("resource", 'wb')
        # pickle.dump(resource_vector, outfile)
        # outfile.close()

        return friendly_units, enemy_units, resource_vector

    def create_unit_vector(self, unit):
        shield_percentage = -1
        energy_percentage = -1
        try:
            shield_percentage = unit.sheild_percentage
        except AttributeError:
            # unit does not have shields do nothing
            pass
        try:
            energy_percentage = unit.energy_percentage
        except AttributeError:
            # unit does not have shields do nothing
            pass
        return [unit.type_id,
                unit.position.x/self.game_info.map_size.width,
                unit.position.y/self.game_info.map_size.height,
                unit.health_percentage,
                shield_percentage,  # percentage of shield, -1 if unit doesn't have shields
                energy_percentage,  # percentage of energy, -1 if unit doesn't have energy
                unit.build_progress]  # scaled between 0-1.0
