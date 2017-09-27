# PySC2 agents
This is a simple implementation of DeepMind's PySC2 RL agents. In this project, the agents are defined according to the original [paper](https://deepmind.com/documents/110/sc2le.pdf), which use all feature maps and structured information to predict both actions and arguments via an A3C algorithm.


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
