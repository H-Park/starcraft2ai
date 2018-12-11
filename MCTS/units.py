from sc2.ids import unit_typeid as sc2_units

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
    sc2_units.UnitTypeId.VIKINGFIGHTER, sc2_units.UnitTypeId.MEDIVAC, sc2_units.UnitTypeId.BATTLECRUISER}

protoss_buildings = {}
protoss_units = {}

zerg_buildings = {}
zerg_units = {}


# get the tech requirements for unit
def get_tech_requirements(game_data, unit: sc2_units.UnitTypeId):
    # unit.tech requirement only works with buildings
    tech_requirements = []
    tech_requirement = game_data.units[unit.value].tech_requirement
    if tech_requirement is not None:
        if type(tech_requirement) is list:
            while len(tech_requirement) > 0:
                tech_requirements.append(tech_requirement)
                tech_requirement = game_data.units[tech_requirement.value].tech_requirement
        else:
            tech_requirements.append(tech_requirement)
    else:
        if unit == sc2_units.UnitTypeId.SCV:
            return []

        # unit is an actual unit
        tech_requirements = [sc2_units.SUPPLYDEPOT]
        if unit in terran_units:
            if unit == sc2_units.UnitTypeId.MARINE or unit == sc2_units.UnitTypeId.REAPER or unit == sc2_units.UnitTypeId.MARAUDER:
                tech_requirements.append(sc2_units.UnitTypeId.BARRACKS)
            elif unit == sc2_units.UnitTypeId.HELLION or unit == sc2_units.UnitTypeId.CYCLONE or unit == sc2_units.UnitTypeId.SIEGETANK:
                tech_requirements.append(sc2_units.UnitTypeId.BARRACKS)
                tech_requirements.append(sc2_units.UnitTypeId.FACTORY)
            elif unit == sc2_units.UnitTypeId.VIKINGFIGHTER or unit == sc2_units.UnitTypeId.MEDIVAC or unit == sc2_units.UnitTypeId.BATTLECRUISER:
                tech_requirements.append(sc2_units.UnitTypeId.BARRACKS)
                tech_requirements.append(sc2_units.UnitTypeId.STARPORT)
    return tech_requirements
