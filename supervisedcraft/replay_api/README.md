## Downloading Replays Guide

`download_replays.py` is a script provided by Blizzard to download replay packs (aggregated into zip files) via Blizzard Game Data APIs. Once the script is run successfully, any matching replay packs will be downloaded to the directory provided.

To access StarCraft II replay packs, you must agree to the [AI and Machine Learning License](https://blzdistsc2-a.akamaihd.net/AI_AND_MACHINE_LEARNING_LICENSE.html). The files are password protected with the password `iagreetotheeula`.  
**By typing in the password `iagreetotheeula` you agree to be bound by the terms of the [AI and Machine Learning License](https://blzdistsc2-a.akamaihd.net/AI_AND_MACHINE_LEARNING_LICENSE.html)**

## Preliminary Setup

1. Create an account for calling the APIs in the [Blizzard Developer Portal](https://dev.battle.net).
2. Get API key and secret associated with the account.
    1. You can find them under the 'My Account' page after logging into the developer portal.

## How to run
Run `download_replays.py`.  


[download]
key = abc
secret = def
download_dir = ../../download
extract_dir = ../../replays
extract = True
filter = sort
remove = True

#### Parameters
- `key`: API client key
- `secret`: API client secret
- `version`: default: `4.10.0`. StarCraft II client version
    - **Replays are version dependent**. Ensure the version you request is consistent with the build environment in which you intend to utilize them.  
    - A version list can be found in [/buildinfo/versions.json](https://github.com/Blizzard/s2client-proto/blob/master/buildinfo/versions.json).  
        - The StarCraft II bot ladder, [AI Arena](https://aiarena.net/), uses `4.10.0` 
- `extract`: whether to extract the replay packs
- `filter`:
    - Options:
      - `sort`: sort the replays according to game version. This flag is recommended as Blizzard often lets a few replays of different versions slip into other replay packs. For instance, when specifynig `--version="4.10.0"`, there are ~2k `4.9.3` replays of the ~103k total replays that will be downloaded. 
      - `remove`: Remove the game versions that do not match `version`,
    - In order to use the `filter` param, `extract: True` must also be supplied. 
