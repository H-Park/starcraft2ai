#include "sc2api/sc2_api.h"
#include "sc2utils/sc2_manage_process.h"

#include <vector>

struct Unit_Features
{
	int team;
	int type;
	float hp;
	float pos_x;
	float pos_y;
	float shields;
	float energy;

	Unit_Features();
	Unit_Features(const sc2::Unit* unit);
};

struct Building_Features
{
	int team;
	int type;
	float hp;
	float pos_x;
	float pos_y;
	float shields;
	float build_progress;

	Building_Features();
	Building_Features(const sc2::Unit* unit);
};

struct Data_Point
{
	std::vector<std::vector<float> > u_features;
	std::vector<std::vector<float> > b_features;

	//label
	int unit_id;

	Data_Point(std::map<int, std::map<sc2::Tag, Unit_Features>> unit_f, std::map<int, std::map<sc2::Tag, Building_Features>> building_f, sc2::Unit production_unit);

	friend bool operator==(const Data_Point &p1, const Data_Point &p2);
};