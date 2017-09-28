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

#Acknowledgements
The A3C implementation is from [Xiaowei Hu](https://github.com/xhujoy/pysc2-agents). I am in the process of adding a recurrent based model to allow for memory. 

*Licensed under The MIT License.*
