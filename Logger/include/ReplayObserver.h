#include "sc2api/sc2_api.h"
#include "sc2utils/sc2_manage_process.h"

#include "Features.h"

#include <cstdio>
#include <iostream>
#include <stdio.h>
#include <fstream>
#include <string.h>
#include <cstdio>

#include <Windows.h>

class Replay : public sc2::ReplayObserver {
public:
	Replay();
	~Replay();

	//Given metadata about a replay, determine if we want to process it
	bool IgnoreReplay(const sc2::ReplayInfo &replay_info, uint32_t &player_id);

	//Called once at the beginning of the game
	void OnGameStart();

	//Callled when a unit it created (not initiated)
	void OnUnitCreated(const sc2::Unit& unit);
	
	//Called at every step of the replay
	void OnStep();

	//Called every time a unit enters vision
	void OnUnitEnterVision(const sc2::Unit& unit);

	//Called when the game ends,
	//This is where the data gets logged to file
	void OnGameEnd();

	//Called when a unit on either team gets destroyed
	void Replay::OnUnitDestroyed(const sc2::Unit& unit);

	//Update the featuers of the unit
	void update_unit(const sc2::Unit* unit);

	//Helper function for OnStep that updates all information of every unit currently in vision
	void update();

	//Cleans up the memory for the next replay. Clears unit_features, building_features, and data points
	void reset();

private:
	// features[player][unit.tag] = features
	std::map<int, std::map<sc2::Tag , Unit_Features >> unit_features;
	std::map<int, std::map<sc2::Tag, Building_Features>> building_features;
	std::vector<Data_Point> data_points;

	const char* dataFolder = "D:/StarCraftAI/data/";

	uint32_t last_echoed_gameloop_;
	std::string last_action_text_;
};
