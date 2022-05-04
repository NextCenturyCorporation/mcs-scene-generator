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

If you wish to request a new feature or report a bug, please post on the MCS Slack tagging `@ta2devs`, or this GitHub repository's [Issues page](https://github.com/NextCenturyCorporation/mcs-scene-generator/issues).

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

#### Release 1.3

Changelog:
- Changed throwers to use "impulse" force mode by default; this is our recommended configuration moving forward. Please update your old thrower configurations (in your YAML files) to either use the `impulse: false` setting or adjust the `throw_force` setting (a good rule-of-thumb is to divide all of your non-impulse forces by 100). All of the example configs in this repository (the YAML files in `ile_configs/`) have been updated appropriately. For more information on force modes, please see `ForceMode.Force` and `ForceMode.Impulse` in [this documentation](https://docs.unity3d.com/ScriptReference/Rigidbody.AddForce.html).
- Created new example YAML configs for the [agent identification](./ile_configs/interactive_agent_identification.yaml) and [moving target prediction](./ile_configs/interactive_moving_target_prediction.yaml) tasks.
- Added `movement` config option under `specific_agents` to set a specific or random movement (either walking or running) path for an simulation-controlled agent.
- Added `auto_last_step` config option to set `last_step` relative to each scene's room dimensions.
- Added `circles` config option to force the performer agent to rotate in a complete clockwise circle (by using only RotateRight actions) at specific action steps.
- Added `performer_look_at` config option to make the performer agent start in a scene looking at a specific object.
- Added `dimensions` config option for all interactable objects that can be used instead of `scale` to set an object's size.
- Added `throw_force_multiplier` config option under `structural_throwers` to set throw forces relative to each scene's room dimensions.
- Added `has_blocking_wall` config option under `shortcut_bisecting_platform`.
- Added `auto_adjust_platforms` config option under `structural_platforms`.
- Fixed a bug where objects on top of containers held by placers (like the soccer ball in scenes generated with the interactive_support_relations.yaml config file) would fall and bounce rather than descending smoothly.
- Fixed a bug where holes and lava would be randomly positioned underneath other objects.
- Fixed a bug where scenes with manually-configured room dimensions and a random performer start position may cause the performer agent to start outside the room.
- Improved ILE startup time.
- Updated `shortcut_lava_room` config option to make use of the `partitionFloor` property recently introduced in MCS version 0.5.4.
- Updated `ile_configs/collisions.yaml` so the performer agent always faces the target.

#### Release 1.2

Changelog:
- Updated documentation and example configs, including: added new example configs corresponding to most new evaluation tasks; updated comments in existing example configs; restructured tables for example configs in the README; fixed bugs in the passive physics example configs to correctly drop objects behind occluders
- Added config options for generating agents in interactive scenes, either holding or not holding the retrieval target object (soccer ball)
- Updated the check_valid_path config option so it will now consider possible paths up and down ramps and across attached platforms
- Updated shapes allowed with droppers, placers, and throwers to include primitive types like triangles
- Added new containers for the support relations task
- Added config options to position objects relative to other objects
- Added a config option to randomize the target’s position via shortcut_lava_target_tool
- Added a config option to create a platform extension via shortcut_triple_door_choice
- Added an interactable object config option to generate objects with the same shape and size as another object
- Added a moving occluder config option to have the occluder move up again before last_step
- Added a placer config option to set its deactivation step
- Replaced the “rotation” thrower config option (for up/down rotation) with separate “rotation_y” and “rotation_z” config options to set both up/down and left/right rotation
- Improved error messages for delayed actions
- Fixed a bug where throwers with height 0 were incorrectly positioned inside the floor
- Fixed a bug where passive scenes were missing the goal’s “category” property
- Removed the shortcut_ramp_to_platform config option because it's redundant with recently-added platform options. To replace this in your configs, please use the following:

```yaml
structural_platforms:
    num: 1
    attached_ramps: 1
```

#### Release 1.1

Changelog:
- Added `check_valid_path` to generate scenes with a valid path between the performer agent's starting position and the retrieval target's position. Considers holes, lava, and all heavy objects in the scene. Does not currently consider ascending or descending ramps.
- Added `identical_to` as a configurable property for interactable objects to make them identical to another random object in the scene with regard to shape, scale, and material (color/texture).
- Added many new options for `structural_platforms`, including: `lips` to add lips around the perimeter of the platform; `attached_ramps` to add ramps attached to the platform; `platform_underneath` and `platform_underneath_attached_ramps` to generate two-level platforms.
- Added `open_topped_containers` as a possible `keyword` option for `keyword_objects`. The `in` option for `keyword_location` now works for open-topped containers.
- Added `shortcut_lava_room` to generate scenes with lava on both the left and right sides.
- Added `shortcut_start_on_platform` to generate scenes with the performer agent starting on a specifically-labeled, randomly-positioned platform.
- Added `shortcut_triple_door_choice` to generate "door occluders" like they will appear during the evaluation.
- Added [tool shapes](https://nextcenturycorporation.github.io/MCS/schema.html#tool-objects) and new options to configure tools, including: `tools`, for tools on their own; `shortcut_lava_target_tool`, to generate a tool, an island completely surrounded by lava, and a retrieval target positioned on the island.
- Created many new example config files and updated this README to map the evaluation tasks with useful configs.
- Generating a door now causes walls to be generated around the door.
- Fixed a bug with objects held by placers being set to the wrong height.
- Updated the max room dimensions to be 100 by 100.

Other Notes:
- Generated scenes should be run with [MCS release version 0.5.3](https://github.com/NextCenturyCorporation/MCS/releases/tag/0.5.3) or later.
- Areas of lava in scenes generated by ILE release 1.0 will not work correctly. If you wish to use old lava scenes, in their JSON files, please replace `floorTextures` with `lava`, and update the property's format as described in [our schema](https://nextcenturycorporation.github.io/MCS/schema.html).

#### Release 1.0

- Areas of lava do not yet impose a negative reward. We plan to implement this feature for a future release.
- All `soccer_ball` objects are restricted in scale to only values between 1 and 3 (inclusive). Invalid `soccer_ball` scale configurations will be ignored. The default scale for all `soccer_ball` objects is `MinMaxFloat(min=1.0, max=3.0)`.

### Example Configuration Files

We've made some example ILE YAML configuration files to get you started.

#### Basic Use Cases

List of example ILE configuration files for basic use cases:

- [auto_generated_null_template.yaml](./ile_configs/auto_generated_null_template.yaml) Template config file containing all available options set to null (fall back to defaults). Automatically generated from source code documentation.
- [door_occluder.yaml](./ile_configs/door_occluder.yaml) Generates scenes with an occluding wall containing three doors, a tall platform bisecting the room, and a randomly positioned soccer ball retrieval target.
- [empty_room.yaml](./ile_configs/empty_room.yaml) Generates scenes with no objects by overriding the default random generation behavior.
- [forced_choice.yaml](./ile_configs/forced_choice.yaml) Generates scenes with the performer agent positioned on top of a tall platform bisecting the room and a randomly positioned soccer ball retrieval target.
- [last_step.yaml](./ile_configs/last_step.yaml) Generates scenes with an action/step limit ("last step") scaled relative to the room's random dimensions.
- [specific_object.yaml](./ile_configs/specific_object.yaml) Generates scenes with a consistently sized and colored blue toy car object.
- [starts_frozen.yaml](./ile_configs/starts_frozen.yaml) Generates scenes in which the performer agent begins frozen for the first 5 to 100 steps.
- [starts_look_rotate_only.yaml](./ile_configs/starts_look_rotate_only.yaml) Generates scenes in which the performer agent begins able to only use the Look and Rotate actions for the first 5 to 100 steps.
- [target_soccer_ball.yaml](./ile_configs/target_soccer_ball.yaml) Generates scenes with a soccer ball retrieval target.
- [two_kidnappings.yaml](./ile_configs/two_kidnappings.yaml) Generates scenes in which the performer agent is kidnapped on steps 501 and 550.

#### Learning Core Common Sense Concepts

See the list of the Core Domains in our [MCS BAA Table doc](./docs/MCS_BAA_TABLE.md).

| MCS Core Domains | Example Config Files |
| --- | --- |
| P1, P6, P7 | [navigation_2d.yaml](./ile_configs/navigation_2d.yaml), [navigation_3d.yaml](./ile_configs/navigation_3d.yaml) |
| P2, P3 | [room_of_many_colors.yaml](./ile_configs/room_of_many_colors.yaml) |
| P4 | [containment.yaml](./ile_configs/containment.yaml), [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml), [occlusion_by_structure.yaml](./ile_configs/occlusion_by_structure.yaml) |
| O2 | [collisions.yaml](./ile_configs/collisions.yaml), [throwers.yaml](./ile_configs/throwers.yaml) |
| O3 | [collisions.yaml](./ile_configs/collisions.yaml), [droppers.yaml](./ile_configs/droppers.yaml), [placers.yaml](./ile_configs/placers.yaml) |
| O4 | [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml), [occlusion_by_structure.yaml](./ile_configs/occlusion_by_structure.yaml) |
| O6 | [droppers.yaml](./ile_configs/droppers.yaml), [placers.yaml](./ile_configs/placers.yaml) |
| O8 | [throwers.yaml](./ile_configs/throwers.yaml) |
| A5 | [agents.yaml](./ile_configs/agents.yaml) |

List of example ILE configuration files helpful for learning core common sense concepts:

- [agents.yaml](./ile_configs/agents.yaml) Generates scenes with one interactive simulation-controlled agent holding the soccer ball retrieval target.
- [collisions.yaml](./ile_configs/collisions.yaml) Generates scenes with a randomly positioned soccer ball retrieval target and a rolled ball that may or may not collide with it.
- [containment.yaml](./ile_configs/containment.yaml) Generates scenes with many closed containers and a soccer ball retrieval target hidden inside one of the containers.
- [droppers.yaml](./ile_configs/droppers.yaml) Generates scenes with many droppers and a soccer ball retrieval target held by one such device.
- [navigation_2d.yaml](./ile_configs/navigation_2d.yaml) Generates scenes with holes, walls, and lava as well as a randomly positioned soccer ball retrieval target.
- [navigation_3d.yaml](./ile_configs/navigation_3d.yaml) Generates scenes with holes, walls, lava, and platforms with ramps, as well as a randomly positioned soccer ball retrieval target.
- [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml) Generates scenes with many large objects and a soccer ball retrieval target either hidden behind an object or visible in front of an object.
- [occlusion_by_structure.yaml](./ile_configs/occlusion_by_structure.yaml) Generates scenes with many large structures and a soccer ball retrieval target either hidden behind a structure or visible in front of a structure.
- [placers.yaml](./ile_configs/placers.yaml) Generates scenes with many placers and a soccer ball retrieval target held by one such device.
- [room_of_many_colors.yaml](./ile_configs/room_of_many_colors.yaml) Generates scenes with randomly colored outer room walls and areas of floor, as well as a soccer ball retrieval target.
- [throwers.yaml](./ile_configs/throwers.yaml) Generates scenes with many throwers and a soccer ball retrieval target held by one such device.

#### Scenes for Specific Evaluation Tasks

See the list of the Core Domains in our [MCS BAA Table doc](./docs/MCS_BAA_TABLE.md).

Eval 3.X Tasks:

| Eval 3.X Task | MCS Core Domains | Example Config Files |
| --- | --- | --- |
| Containers (Interactive) | P1, P4 | [containment.yaml](./ile_configs/containment.yaml) |
| Gravity Support (Passive) | O6, P1 | [passive_physics_gravity_support.yaml](./ile_configs/passive_physics_gravity_support.yaml) |
| Obstacles (Interactive) | P1 | [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml) |
| Occluders (Interactive) | O1, P1, P4 | [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml) |
| Passive Object Permanence | O1, O4 | [passive_physics_fall_down.yaml](./ile_configs/passive_physics_fall_down.yaml), [passive_physics_move_across.yaml](./ile_configs/passive_physics_move_across.yaml) |
| Shape Constancy (Passive) | O1, O4 | [passive_physics_fall_down.yaml](./ile_configs/passive_physics_fall_down.yaml) |
| Spatio-Temporal Continuity (Passive) | O1, O4 | [passive_physics_move_across.yaml](./ile_configs/passive_physics_move_across.yaml) |

Eval 4 Tasks:

| Eval 4 Task | MCS Core Domains | Example Config Files |
| --- | --- | --- |
| Collisions (Passive) | O1, O2, O3 | [passive_physics_collisions.yaml](./ile_configs/passive_physics_collisions.yaml) |
| Interactive Object Permanence | O4 | [interactive_object_permanence.yaml](./ile_configs/interactive_object_permanence.yaml) |
| Spatial Reorientation (Interactive) | P2, P3 | TODO |

Eval 5 Tasks:

| Eval 5 Task | MCS Core Domains | Example Config Files |
| --- | --- | --- |
| Agent Identification (Interactive) | A5 | [interactive_agent_identification.yaml](./ile_configs/interactive_agent_identification.yaml) |
| Moving Target Prediction (Interactive) | O8 | [interactive_moving_target_prediction.yaml](./ile_configs/interactive_moving_target_prediction.yaml) |
| Navigation: Holes (Interactive) | P7 | [holes.yaml](./ile_configs/holes.yaml) |
| Navigation: Lava (Interactive) | P7 | [lava.yaml](./ile_configs/lava.yaml) |
| Navigation: Ramps (Interactive) | P6 | [ramps.yaml](./ile_configs/ramps.yaml) |
| Solidity (Interactive) | O3 | [interactive_solidity.yaml](./ile_configs/interactive_solidity.yaml) |
| Spatial Elimination (Interactive) | P4 | [interactive_spatial_elimination.yaml](./ile_configs/interactive_spatial_elimination.yaml) |
| Support Relations (Interactive) | O6 | [interactive_support_relations.yaml](./ile_configs/interactive_support_relations.yaml) |
| Tool Use (Interactive) | O5 | [tools.yaml](./ile_configs/tools.yaml) |

List of example ILE configuration files for generating scenes similar to specific evaluation tasks:

- [holes.yaml](./ile_configs/holes.yaml) Generates scenes with many holes and a randomly positioned soccer ball retrieval target.
- [interactive_agent_identification.yaml](./ile_configs/interactive_agent_identification.yaml) Generates scenes similar to the interactive agent indentification eval tasks: start on a platform bisecting the room; an agent on one side of the platform; must walk up to the agent and request for it to produce the target.
- [interactive_moving_target_prediction.yaml](./ile_configs/interactive_moving_target_prediction.yaml) Generates scenes similar to the interactive moving target prediction eval tasks: start on a platform; lava extending across both sides of the room; must first rotate in a 360 degree circle; then a thrower rolls a soccer ball from one end of the room toward the other; must predict the speed and trajectory of the soccer ball in order to intercept it efficiently.
- [interactive_object_permanence.yaml](./ile_configs/interactive_object_permanence.yaml) Generates scenes similar to the interactive object permanence eval tasks: start on a platform bisecting the room; an L-occluder on each side; and a thrower that tosses the soccer ball into the room.
- [interactive_solidity.yaml](./ile_configs/interactive_solidity.yaml) Generates scenes similar to the interactive solidity eval tasks: start on a platform bisecting the room; a placer holding the soccer ball descends from the ceiling; a door occluder descends from the ceiling; the placer releases the soccer ball so it falls somewhere behind the door occluder.
- [interactive_spatial_elimination.yaml](./ile_configs/interactive_spatial_elimination.yaml) Generates scenes similar to the interactive spatial elimination eval tasks: start on a platform bisecting the room; an occlusing wall on each side; and a soccer ball either in front of or behind an occluding wall.
- [interactive_support_relations.yaml](./ile_configs/interactive_support_relations.yaml) Generates scenes similar to the interactive support relations eval tasks: start on a platform bisecting the room; placers holding a container with the soccer ball descend from the ceiling; a door occluder descends from the ceiling; the placers release the container so it and the soccer ball land either fully, partially, or not on the platform.
- [lava.yaml](./ile_configs/lava.yaml) Generates scenes with many pools of lava and a randomly positioned soccer ball retrieval target.
- [passive_physics_collisions.yaml](./ile_configs/passive_physics_collisions.yaml) Generates scenes similar to passive physics collisions eval tasks: same view; similarly sized and positioned moving-and-rotating occluders; multiple objects, possibly colliding; only able to use Pass actions.
- [passive_physics_gravity_support.yaml](./ile_configs/passive_physics_gravity_support.yaml) Generates scenes similar to passive physics gravity support eval tasks: same view; similarly sized and positioned platforms; placers lowering objects into the scene, possibly above the platforms, and then releasing them; only able to use Pass actions.
- [passive_physics_fall_down.yaml](./ile_configs/passive_physics_fall_down.yaml) Generates scenes similar to passive physics eval tasks with objects falling down: same view; similarly sized and positioned moving-and-rotating occluders; multiple objects falling into the scene; only able to use Pass actions.
- [passive_physics_move_across.yaml](./ile_configs/passive_physics_move_across.yaml) Generates scenes similar to passive physics eval tasks with objects moving across: same view; similarly sized and positioned moving-and-rotating occluders; multiple objects moving across the scene; only able to use Pass actions.
- [ramps.yaml](./ile_configs/ramps.yaml) Generates scenes with ramps leading up to platforms and a soccer ball retrieval target either on top of the platform or on the floor adjacent to the platform.
- [tools.yaml](./ile_configs/tools.yaml) Generates scenes with a large moveable block tool and a soccer ball retrieval target completely surrounded by lava.

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
