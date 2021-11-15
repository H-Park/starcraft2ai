REPLAY_SET="../high_quality_replays/Protoss_vs_Protoss.json"
REPLAY_SET="$REPLAY_SET ../high_quality_replays/Protoss_vs_Terran.json"
REPLAY_SET="$REPLAY_SET ../high_quality_replays/Protoss_vs_Zerg.json"
REPLAY_SET="$REPLAY_SET ../high_quality_replays/Terran_vs_Terran.json"
REPLAY_SET="$REPLAY_SET ../high_quality_replays/Terran_vs_Zerg.json"
REPLAY_SET="$REPLAY_SET ../high_quality_replays/Zerg_vs_Zerg.json"

for replay_set in $REPLAY_SET
do
    python3 extract_actions.py --hq_replay_set $replay_set --n_instance $1 &&
    python3 sample_actions.py --hq_replay_set $replay_set &&
    python3 parse_replay.py --hq_replay_set $replay_set --n_instance $1 &&
    python3 replay2global_features.py --hq_replay_set $replay_set
done