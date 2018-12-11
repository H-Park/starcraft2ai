from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from terran_bot import TerranBot

run_game(maps.get("DreamcatcherLE"), [
    Bot(Race.Terran, TerranBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=False)
