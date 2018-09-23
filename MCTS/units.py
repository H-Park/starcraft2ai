from sc2.ids import unit_typeid as sc2_units

terran_units = {
    # buildings
    sc2_units.UnitTypeId.REFINERY, sc2_units.UnitTypeId.SUPPLYDEPOT, sc2_units.UnitTypeId.COMMANDCENTER,
    sc2_units.UnitTypeId.BARRACKS, sc2_units.UnitTypeId.ENGINEERINGBAY, sc2_units.UnitTypeId.BUNKER,
    sc2_units.UnitTypeId.SENSORTOWER, sc2_units.UnitTypeId.MISSILETURRET,
    sc2_units.UnitTypeId.FACTORY, sc2_units.UnitTypeId.GHOSTACADEMY,
    sc2_units.UnitTypeId.STARPORT, sc2_units.UnitTypeId.ARMORY, sc2_units.UnitTypeId.FUSIONCORE,
    sc2_units.UnitTypeId.TECHLAB, sc2_units.UnitTypeId.REACTOR,

    # units
    sc2_units.UnitTypeId.MARINE, sc2_units.UnitTypeId.MARAUDER, sc2_units.UnitTypeId.REAPER,
    sc2_units.UnitTypeId.HELLION, sc2_units.UnitTypeId.CYCLONE, sc2_units.UnitTypeId.SIEGETANK,
    sc2_units.UnitTypeId.VIKINGFIGHTER, sc2_units.UnitTypeId.MEDIVAC}

protoss_units = {}

zerg_units = {}

def get_tech_requirements(unit):
    pass