# Supervised SC2

This project aims to reproduce Deepmind's initial results of their supervised agent by similarly training a Convolutional Neural Network (CNN) in a supervised fashion from players Diamond 1 and better. 

## Requirements
1. Install Pygame
   - Arch Linux: `yay -S python-pygame`
   - Fedora: `yum install python3-pygame`
   - Mac:`python3 -m pip install -U pygame==2.0.0.dev12`
   - OpenSUSE: `zypper install python3-pygame`
   - Windows: `py -m pip install pygame`
   - Ubuntu: `apt install python3-pygame`

2. Install the rest of the requirements requirements `pip install -r requirements.txt`

## Steps
1. Download Starcraft II
   - `Linux`: Download and unzip StarCraft II Linux Package [4.10.0](https://github.com/Blizzard/s2client-proto#downloads) into `~/StarCraftII`
   - `Windows and Mac`: Download StarCraft II as you regularly would
   - Make sure that whatever maps your replays use are in `StarCraftII/Maps`.
      - `4.10.0`, the maps can be found [here](https://github.com/Blizzard/s2client-proto#map-packs)
2. [Acquire replays](replay_api/README.md)
3. [Preprocess the replays](preprocess/README.md)
4. Parse the replays
5. Extract the features
6. Train a model

## Dataset Overview

`todo!()`

## Dataset Usage Guide

`todo!()`
