#include "Features.h"

Building_Features::Building_Features()
{
	this->team = -1;
	this->type = -1;
	this->hp = -1;
	this->pos_x = -1;
	this->pos_y = -1;
	this->shields = -1;
	this->build_progress = -1;
}

Building_Features::Building_Features(const sc2::Unit* unit)
{
	this->team = unit->owner;
	this->type = unit->unit_type;
	this->hp = unit->health;
	this->pos_x = unit->pos.x;
	this->pos_y = unit->pos.y;
	this->shields = unit->shield;
	this->build_progress = unit->build_progress;
}

Unit_Features::Unit_Features()
{
	this->team = -1;
	this->type = -1;
	this->hp = -1;
	this->pos_x = -1;
	this->pos_y = -1;
	this->shields = -1;
	this->energy = -1;
}

Unit_Features::Unit_Features(const sc2::Unit* unit)
{
	this->team = unit->owner;
	this->type = unit->unit_type;
	this->hp = unit->health;
	this->pos_x = unit->pos.x;
	this->pos_y = unit->pos.y;
	this->shields = unit->shield;
	this->energy = unit->energy;
}

Data_Point::Data_Point(std::map<int, std::map<sc2::Tag, Unit_Features>> unit_f, std::map<int, std::map<sc2::Tag, Building_Features>> building_f, sc2::Unit production_unit)
{
	//clean our unit data
	//go through each player
	for (const std::pair<int, std::map<sc2::Tag, Unit_Features>> & player_unit_features : unit_f)
	{
		//go through each unit that we know the player has at this time
		for (const std::pair<sc2::Tag, Unit_Features > & unit : player_unit_features.second)
		{
			//make a vector to store the features of this unit
			//type, hp, pos_x, pos_y, shields, energy
			std::vector<float> unit_features = { static_cast<float>(unit.second.type), unit.second.hp, unit.second.pos_x, unit.second.pos_y, unit.second.shields, unit.second.energy };

			// if production unit and this unit are on the same team, make the team id 1
			// else make it 2
			// this standardizes our team data. a 1 will always be friendly and a 2 will always be an enemy.
			if (unit.second.team == production_unit.owner)
			{
				unit_features.insert(unit_features.begin(), 1);
			}
			else
			{
				unit_features.insert(unit_features.begin(), 2);
			}

			//lastly, add our data point to our master list of unit features
			this->u_features.push_back(unit_features);
		}
	}
	//clean our building data
	//go through each player
	for (const std::pair<int, std::map<sc2::Tag, Building_Features>> const & player : building_f)
	{
		//go through each building we know the player has at this time
		for (const std::pair<sc2::Tag, Building_Features > & building : player.second)
		{
			//make a vector to store the features of this building
			//type, hp, pos_x, pos_y, shields, build_progress
			std::vector<float> building_features = { static_cast<float>(building.second.type), building.second.hp, building.second.pos_x, building.second.pos_y, building.second.shields, building.second.build_progress };

			// if production unit and this unit are on the same team, make the team id 1
			// else make it 2
			if (building.second.team == production_unit.owner)
			{
				building_features.insert(building_features.begin(), 1);
			}
			else
			{
				building_features.insert(building_features.begin(), 2);
			}

			//lastly, add our data to point to our master list of building features
			this->b_features.push_back(building_features);
		}
	}

	//very lastly, tag on our production action
	this->unit_id = production_unit.unit_type;
}

bool operator== (const Data_Point &p1, const Data_Point &p2)
{
	return p1.b_features == p2.b_features && p1.u_features == p2.u_features && p1.unit_id == p2.unit_id;
}