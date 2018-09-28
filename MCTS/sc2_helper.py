
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from terran_bot import TerranBot

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, TerranBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=False)
