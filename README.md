# The ILE Scene Generator

#### Table of Content

- [Overview](#Overview)
- [Setup](#Setup)
- [Usage](#Usage)
- [Scene Validation](#Scene-Validation)
- [Additional Documentation](#Additional-Documentation)
- [Troubleshooting](#Troubleshooting)
- [Acknowledgements](#Acknowledgements)
- [Apache 2 Open Source License](#Apache-2-Open-Source-License)

## Overview

The ILE ("Ideal/Interactive Learning Environment") Scene Generator is used to generate training scenes for MCS Eval 5 and beyond. The intent of the ILE is to allow teams to train on concepts core to common sense reasoning, like physics, occlusion, navigation, localization, agency, and more. Test scenes will be comprised of combinations of these concepts, and the simulation environment (or the "world") is the same for both training (via the ILE) and testing. Please note the ILE does not rely on the hypercube designs that the MSC evaluation team uses to generate its test scenes.

The ILE runs using a YAML config file to set scene options. To see all config file properties, please review the [ILE_API.md](./ILE_API.md) documentation.

The ILE outputs JSON files in the [MCS scene format](https://nextcenturycorporation.github.io/MCS/schema.html) to be run with the [machine_common_sense](https://github.com/NextCenturyCorporation/MCS) python library and corresponding Unity build.

If you wish to request a new feature or report a bug, please post on this GitHub repository's [Issues page](https://github.com/NextCenturyCorporation/mcs-scene-generator/issues).

## Setup

Please use Python 3.8+

### Create a Virtual Environment

From this folder, create a virtual environment and activate it.

```
python3 -m venv --prompt scene_gen venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

### Install Requirements

```
python -m pip install -r requirements.txt
```

You may need to install `testresources`:

```
sudo apt install python3-testresources
```

## Usage

### Running

To see all of the scene generator's options:

```
python ile.py --help
```

Common arguments:

- `-c <config>` (optional): ILE YAML config file
- `-n <number>` (optional): Number of output scene files to generate
- `-p <prefix>` (optional): Filename prefix of all output scene files

Example:

```
python ile.py -c ile_config.yaml -n 10 -p scene
```

### Latest Release Notes

#### Release 1.0

- Areas of lava do not yet impose a negative reward. We plan to implement this feature for a future release.
- All `soccer_ball` objects are restricted in scale to only values between 1 and 3 (inclusive). Invalid `soccer_ball` scale configurations will be ignored. The default scale for all `soccer_ball` objects is `MinMaxFloat(min=1.0, max=3.0)`.

### Example Configuration Files

- [auto_generated_null_template.yaml](./ile_configs/auto_generated_null_template.yaml) Template config file containing all available options set to null (fall back to defaults). Automatically generated from source code documentation.
- [containment.yaml](./ile_configs/containment.yaml) Generates scenes with many closed containers and a soccer ball retrieval target hidden inside one of the containers.
- [devices.yaml](./ile_configs/devices.yaml) Generates scenes with many devices (droppers, placers, and throwers) and a soccer ball retrieval target held by one such device.
- [empty_room.yaml](./ile_configs/empty_room.yaml) Generates scenes with no objects by overriding the default random generation behavior.
- [forced_choice.yaml](./ile_configs/forced_choice.yaml) Generates scenes with the performer agent positioned on top of a tall platform bisecting the room and a randomly positioned soccer ball retrieval target.
- [navigation_2d.yaml](./ile_configs/navigation_2d.yaml) Generates scenes with holes, walls, and lava and a randomly positioned soccer ball retrieval target.
- [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml) Generates scenes with many large objects and a soccer ball retrieval target either hidden behind an object or visible in front of an object.
- [occlusion_by_structure.yaml](./ile_configs/occlusion_by_structure.yaml) Generates scenes with many large structures and a soccer ball retrieval target either hidden behind a structure or visible in front of a structure.
- [ramps.yaml](./ile_configs/ramps.yaml) Generates scenes with a ramp leading up to a platform and a soccer ball retrieval target either on top of the platform or on the floor adjacent to the platform.
- [room_of_many_colors.yaml](./ile_configs/room_of_many_colors.yaml) Generates scenes with randomly colored outer room walls and areas of floor.
- [starts_frozen.yaml](./ile_configs/starts_frozen.yaml) Generates scenes in which the performer agent begins frozen for the first 5 to 100 steps.
- [starts_look_rotate_only.yaml](./ile_configs/starts_look_rotate_only.yaml) Generates scenes in which the performer agent begins able to only use the Look and Rotate actions for the first 5 to 100 steps.
- [target_soccer_ball.yaml](./ile_configs/target_soccer_ball.yaml) Generates scenes with a soccer ball retrieval target.
- [two_kidnappings.yaml](./ile_configs/two_kidnappings.yaml) Generates scenes in which the performer agent is kidnapped on steps 501 and 550.

## Scene Validation

In the `MCS` repository, in the `scripts` folder, use one of the following scripts to run all of the new scenes, depending on if you're running an interactive or passive (intuitive physics, agents, etc.) hypercube.

- [run_interactive_scenes.py](https://github.com/NextCenturyCorporation/MCS/blob/development/scripts/run_interactive_scenes.py) to load each scene (JSON file) starting with a given prefix and rotate in a circle.
- [run_passive_scenes.py](https://github.com/NextCenturyCorporation/MCS/blob/development/scripts/run_passive_scenes.py) to load each scene (JSON file) starting with a given prefix and pass until the scene is finished.

```
python run_interactive_scenes.py <mcs_unity_app> <file_path_prefix>
python run_passive_scenes.py <mcs_unity_app> <file_path_prefix>
```

(Please see the [scripts README](https://github.com/NextCenturyCorporation/MCS/blob/development/scripts/README.md) for more information.)

If you're validating scenes that you just made, and they're all in this folder, then the `<file_path_prefix>` will be `<mcs-scene-generator>/<prefix>`, where `<prefix>` is the filename prefix that you used to run the scene generator.

## Additional Documentation

- [Developers](./DEV_README)
- [Hypercube Scene Generator](./HYPERCUBE_SCENE_GENERATOR_README)

## Troubleshooting

[mcs-ta2@machinecommonsense.com](mailto:mcs-ta2@machinecommonsense.com)

## Acknowledgements

This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) and Naval Information Warfare Center, Pacific (NIWC Pacific) under Contract No. N6600119C4030. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the DARPA or NIWC Pacific.

## Apache 2 Open Source License

Code in this repository is made available by [CACI][4] (formerly [Next Century
Corporation][1]) under the [Apache 2 Open Source License][2].  You may
freely download, use, and modify, in whole or in part, the source code
or release packages. Any restrictions or attribution requirements are
spelled out in the license file.  For more information about the
Apache license, please visit the [The Apache Software Foundation’s
License FAQ][3].

[1]: http://www.nextcentury.com
[2]: http://www.apache.org/licenses/LICENSE-2.0.txt
[3]: http://www.apache.org/foundation/license-faq.html
[4]: http://www.caci.com

Copyright 2022 CACI
