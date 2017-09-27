#include "ReplayObserver.h"

//Given the attributes of a unit, return true if it is a building (structure), false otherwise.
bool is_building(std::vector<sc2::Attribute> attributes)
{
	for (const auto& attribute : attributes)
	{
		if (attribute == sc2::Attribute::Structure)
		{
			return true;
		}
	}
	return false;
}

//Create a folder given the following path
void CreateFolder(std::string path)
{
	if (!CreateDirectoryA(path.c_str(), NULL))
	{
		return;
	}
}

std::string random_string(size_t length)
{
	auto randchar = []() -> char
	{
		const char charset[] =
			"0123456789"
			"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
			"abcdefghijklmnopqrstuvwxyz";
		const size_t max_index = (sizeof(charset) - 1);
		return charset[rand() % max_index];
	};
	std::string str(length, 0);
	std::generate_n(str.begin(), length, randchar);
	return str;
}

Replay::Replay() 
{
	sc2::ReplayObserver();
}
//Destructor
Replay::~Replay()
{
	this->reset();
}

bool Replay::IgnoreReplay(const sc2::ReplayInfo &replay_info, uint32_t &player_id) {
	for (int i = 0; i < replay_info.num_players; i++)
	{
		if (replay_info.players[i].mmr < 3800)
		{
			return true;
		}
	}
	return false;
}
void Replay::OnGameStart() {
}

void Replay::OnUnitCreated(const sc2::Unit& unit) {
}

void Replay::OnStep() {
	this->update();

	const sc2::ObservationInterface* obs = Observation();

	const sc2::RawActions raw_actions = obs->GetRawActions();

	for (const sc2::ActionRaw action : raw_actions)
	{
		std::string ability_name  = sc2::AbilityTypeToName(action.ability_id);

		std::vector<std::string> production_actions = { "BUILD", "MORPH", "RESEARCH", "TRAIN" };
		for (const std::string production_action : production_actions)
		{
			if (ability_name.find(production_action) != std::string::npos)
			{
				std::cout << ability_name << std::endl;
			}
		}
	}
}

void Replay::OnUnitEnterVision(const sc2::Unit& unit) {
	this->update_unit(&unit);
}

void Replay::OnGameEnd() {
	//log all our data!
	//loop through all our data points
	for (const Data_Point data_point : this->data_points)
	{
		//construct the base string which we will be working with, aka our absolute, root directory
		std::string local_path = dataFolder + std::to_string(data_point.unit_id);
		CreateFolder(local_path);

		//create a unique directory inside of dataFolder/unit_id to store our unit and building data pair
		std::string data_point_folder = local_path.append("/" + random_string(10));
		CreateFolder(local_path);

		//finally, write our data
		//write unit data by looping through each unit feature and writing it to a line  dataFolder/unit_id/XXXX/unit_features.txt
		std::ofstream f_u(local_path + "/unit_features.txt");
		for (const std::vector<float> unit_f : data_point.u_features)
		{
			for (const float feature : unit_f)
			{
				f_u << feature << ' ';
			}
			f_u << '\n';
		}
		f_u.close();
		//write unit data by looping through each building feature and writing it to a line  dataFolder/unit_id/XXXX/building_features.txt
		std::ofstream f_b(local_path + "/building_features.txt");
		for (const std::vector<float> building_f : data_point.b_features)
		{
			for (const float feature : building_f)
			{
				f_b << feature << ' ';
			}
			f_b << '\n';
		}
		f_b.close();
	}
	std::cout << "Data Points Logged: " << this->data_points.size() << std::endl;

	//clean up our memory for the next game!
	this->reset();
}

void Replay::OnUnitDestroyed(const sc2::Unit& unit)
{
	const sc2::ObservationInterface* obs = Observation();
	// determine whether the unit is a building or not
	std::vector<sc2::Attribute> attributes = obs->GetUnitTypeData().at(unit.unit_type).attributes;
	if (is_building(attributes))
	{
		this->building_features[unit.owner].erase(unit.tag);
	}
	else
	{
		this->unit_features[unit.owner].erase(unit.tag);
	}
}

void Replay::update_unit(const sc2::Unit* unit)
{
	// determine whether the unit is a building or not
	const sc2::ObservationInterface* obs = Observation();
	std::vector<sc2::Attribute> attributes = obs->GetUnitTypeData().at(unit->unit_type).attributes;
	if (is_building(attributes))
	{
		this->building_features[unit->owner][unit->tag] = Building_Features(unit);
	}
	else
	{
		this->unit_features[unit->owner][unit->tag] = Unit_Features(unit);
	}
}

void Replay::update()
{
	const sc2::ObservationInterface* obs = Observation();
	sc2::Units units = obs->GetUnits();
	for (auto unit : units)
	{
		this->update_unit(&unit);
	}
}

void Replay::reset()
{
	this->building_features.clear();
	this->unit_features.clear();
	this->data_points.clear();
}