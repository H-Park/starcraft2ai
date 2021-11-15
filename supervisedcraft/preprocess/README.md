# Proprocess

This folder is the first step in creating a dataset of `(state, action)` pairs from human experts for StarCraft II. This step filters a folder of replays according to a few key player metrics outlined below.
  
## Usage
`python3 preprocess.py`

#### Parameters:
The following values are specified in `settings.conf`.
- `info_path`: The folder of the replays. Note: when specifying a local path, the local path must be in with respect to `../../../StarCraftII/Replays`. 
- `n_instance`: `8`. The amount of instances of StarCraft II to launch to process the replays. A general rule of thumb is one instance per CPU core.
- `version`: `4.10.0`
    - The game version to use. Replays not from this game version will not be processed in further steps.
- `min_duration`: `1000`. Minimum number of games steps a game must have
- `min_apm`: `10`. Minimun actions per minute (APM) both players must have in the game
    - Culls replays where one or both players didn't play
- `min_mmr`: `3500`. Minimum MMR both players must have in the match. 3500 is about Diamond rank.
    - Culls replays where one or both players are not at least Diamond rank.