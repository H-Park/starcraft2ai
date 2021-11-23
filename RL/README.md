# PySC2 agents


## Requirements
- PySC2 is a learning environment of StarCraft II provided by DeepMind. It provides an interface for RL agents to interact with StarCraft II, getting observations and sending actions. You can follow the tutorial in [PySC2 repo](https://github.com/deepmind/pysc2) to install it.

- Python packages might miss: tensorflow. If `pip` is set up on your system, it can be easily installed by running
```shell
pip install tensorflow-gpu
```

### Training
Train a model by yourself:
```shell
python -m main --map=MoveToBeacon
```

*Licensed under The MIT License.*
