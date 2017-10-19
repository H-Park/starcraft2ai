from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time


# Taken straight from pysc2's repo
def run_loop(agent, env, max_frames=0):
    """A run loop to have agents and an environment interact."""
    start_time = time.time()

    try:
        while True:
            num_frames = 0
            timesteps = env.reset()
            agent.reset()
            while True:
                num_frames += 1
                last_timesteps = timesteps
                actions = [agent.step(timestep) for timestep in timesteps]
                timesteps = env.step(actions)
                # PLAY AROUND WITH ME ( ;) ) until it feels comfortable
                # time.sleep(.08)
                # Only for a single player!
                is_done = (num_frames >= max_frames) or timesteps[0].last()
                yield [last_timesteps[0], actions[0], timesteps[0]], is_done
                if is_done:
                    break
    except KeyboardInterrupt:
        pass
    finally:
        elapsed_time = time.time() - start_time
        print("Took %.3f seconds" % elapsed_time)
