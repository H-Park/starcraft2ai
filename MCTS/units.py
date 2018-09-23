from sc2.ids import unit_typeid as sc2_units
from sc2.game_data import UnitTypeData

terran_buildings = {
    sc2_units.UnitTypeId.REFINERY, sc2_units.UnitTypeId.SUPPLYDEPOT, sc2_units.UnitTypeId.COMMANDCENTER,
    sc2_units.UnitTypeId.BARRACKS, sc2_units.UnitTypeId.ENGINEERINGBAY, sc2_units.UnitTypeId.BUNKER,
    sc2_units.UnitTypeId.SENSORTOWER, sc2_units.UnitTypeId.MISSILETURRET,
    sc2_units.UnitTypeId.FACTORY, sc2_units.UnitTypeId.GHOSTACADEMY,
    sc2_units.UnitTypeId.STARPORT, sc2_units.UnitTypeId.ARMORY, sc2_units.UnitTypeId.FUSIONCORE,
    sc2_units.UnitTypeId.TECHLAB, sc2_units.UnitTypeId.REACTOR,
}
terran_units = {
    sc2_units.UnitTypeId.MARINE, sc2_units.UnitTypeId.MARAUDER, sc2_units.UnitTypeId.REAPER,
    sc2_units.UnitTypeId.HELLION, sc2_units.UnitTypeId.CYCLONE, sc2_units.UnitTypeId.SIEGETANK,
    sc2_units.UnitTypeId.VIKINGFIGHTER, sc2_units.UnitTypeId.MEDIVAC}

protoss_buildings = {}
protoss_units = {}

zerg_buildings = {}
zerg_units = {}


# get the tech requirements for unit
def get_tech_requirements(game_data, unit: UnitTypeData):
    # unit.tech requirement only works with buildings
    tech_requirements = []
    tech_requirement = unit.tech_requirement
    while tech_requirement is not None:
        tech_requirements.append(tech_requirement)
        tech_requirement = tech_requirement.

        return tech_requirement
    else:
        # unit is an actual unit
        tech_requirements = [sc2_units..SUPPLYDEPOT]
        if unit in terran_units:UnitTypeId
            if unit == sc2_units.UnitTypeId.MARINE or unit == sc2_units.UnitTypeId.REAPER:
                tech_requirements.append(sc2_units.UnitTypeId.BARRACKS)
            elif unit == sc2_units.UnitTypeId.MARAUDER:
                tech_requirements.append(sc2_units.UnitTypeId.BARRACKS)
                tech_requirements.append(sc2_units.UnitTypeId.TECHLAB)
            elif unit == sc2_units.UnitTypeId.HELLION:
                tech_requirements.append(sc2_units.UnitTypeId.BARRACKS)
                tech_requirements.append(sc2_units.UnitTypeId.FACTORY)
