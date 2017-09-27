#define _CRT_SECURE_NO_DEPRECATE

#include "sc2api/sc2_api.h"
#include "sc2utils/sc2_manage_process.h"
#include "ReplayObserver.h"


const char* kReplayFolder = "D:/StarCraftAI/SC2-Replays/";

int main(int argc, char* argv[]) {
	sc2::Coordinator coordinator;
	coordinator.SetProcessPath("C:/Program Files (x86)/StarCraft II/Versions/Base57507/SC2_x64.exe");
	if (!coordinator.SetReplayPath(kReplayFolder)) {
		std::cout << "Unable to find replays." << std::endl;
		return 1;
	}

	Replay* replay_observer = new Replay();

	//add replay_observer to coordinator
	//you can add multiple instances of replay_observer to coordinator, and it will play multiple replays simulataneously. 
	coordinator.AddReplayObserver(replay_observer);

	while (coordinator.Update());
	while (!sc2::PollKeyPress());
}