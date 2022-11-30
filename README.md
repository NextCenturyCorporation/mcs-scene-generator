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

The ILE ("Interactive Learning Environment") Scene Generator is used to generate training scenes for MCS Eval 5 and beyond. The intent of the ILE is to allow teams to train on concepts core to common sense reasoning, like physics, occlusion, navigation, localization, agency, and more. Test scenes will be comprised of combinations of these concepts, and the simulation environment (or the "world") is the same for both training (via the ILE) and testing. Please note the ILE does not rely on the hypercube designs that the MSC evaluation team uses to generate its test scenes.

The ILE runs using a YAML config file to set scene options. To see all config file properties, please review the [ILE_API.md](./ILE_API.md) documentation.

Please note that we consider our "passive" tasks to be a subset of our "interactive" tasks. Therefore the Interactive Learning Environment is also built to support generating training scenes for passive tasks as well.

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

### Install Pre-Commit

```
pre-commit install
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

#### Release 1.6

Changelog:
- Implemented asymmetric (a.k.a. "hooked" or "L-shape") tool shapes, and added the "tool_type" config option for the shortcut_lava_target_tool property to configure the type of tool.
- Implemented containers with separate lids that are placed onto them (shape="separate_container").
- Implemented devices that look like our "placers" but pick up or drag objects rather than placing them (see the "placers" property). Also added the "placed_object_above" config option for placers.
- Implemented new options for the shortcut_bisecting_platform property, including "is_short", "is_thin", and "other_platforms".
- Implemented "pointing" config option for agents.
- Added the restrict_open_objects property for generating Set Rotation and Shell Game scenes.
- Added the shortcut_imitation_task property for generating Imitation scenes.
- Added the shortcut_tool_choice property for generating Tool Choice scenes.
- Added the turntables_agent_non_agent_config property for generating Spatial Reference scenes.
- Revised the "adjacent" keyword_location to work in global coordinates (using the new "adjacent_distance" property), rather than based on the position of the performer agent.
- Updated the "placers" ILE config file to include examples of "placers" picking up objects.
- Added new example ILE config files:
    - Basic usage and core common sense concepts:
        - `agent_pointing_at_hidden_target`
        - `container_with_separate_lid`
    - New evaluation tasks:
        - `interactive_imitation`
        - `interactive_set_rotation`
        - `interactive_shell_game`
        - `interactive_spatial_reference`
        - `interactive_tool_choice`

#### Release 1.5

Changelog:
- Major changes to how all passive physics scenes are made, so they fully align with the evaluation data:
    - Replaced the `passive_physics_floor: true` config option with `passive_physics_scene: true`, which automatically assigns the `room_dimensions`, `performer_start_position`, and other properties for the scene. Please see the ILE API for more information.
    - Added the `passive_physics_setup` config property for the `structural_throwers` option, which sets the thrower's position and rotation to values used in our passive physics evaluation scenes. Possible choices include `"roll_angled"`, `"roll_straight"`, and `"toss_straight"`.
    - Added the `passive_physics_throw_force: true` and `passive_physics_collision_force: true` config properties for the `structural_throwers` option, which sets the thrower's `throw_force` to a value used in our passive physics evaluation scenes. We recommend against directly configuring `throw_force` for all passive physics scenes moving forward.
    - Added the `stop_position` confg property for the `structural_throwers` option, which sets the thrower's `throw_force` based on movement data we have recorded for use in our passive physics evaluation scenes. Possible choices include setting specific `x` and `z` values, setting `offscreen: true`, or setting `behind` with an object label to make the thrown object come to a stop behind a specific object (an occluder).
    - Updated all of the passive physics ILE example config files, and added `passive_physics_move_behind.yaml`.
    - Internally, the ILE Scene Generator now sets the `"intuitive_physics": true` tag in all passive physics JSON scene files, which instructs our Unity environment to automatically configure the room to preset specificiations. This tag is used in all of our passive physics evaluation scenes.
- Updated `goal` so that `"multi retrieval"` (used in number comparison and arithmetic tasks) and `"passive"` (used in seeing-leads-to-knowing tasks) are valid options for the `category`. Also added `targets` as a valid `goal` property for Multi-Retrieval goals. Please see our [Python API](https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.GoalCategory) for more information on goals.
- Added the `performer_starts_near` config option to ensure the performer agent always starts a specific distance away from a specific object (including containers, occluders, platforms, ramps, the target, etc.).
- Added the `structural_turntables` config option to generate scenes containing rotating turntables (a.k.a. cogs).
- Added the `position_relative_to_start` config property for the `on_center` `keyword_location` to position objects on top of turntables and other furniture.
- Added the `adjacent_performer` `keyword_location` to position objects adjacent to the performer agent.
- Added the `along_wall` `keyword_location` to position objects adjacent to a specific exterior room wall.
- Added the `empty_placer` config property to the `placers` option to generate scenes containing empty placers (that do not hold any objects).
- Added the `end_height_relative_object_label` config property to the `placers` option so placers can dynamically adjust their drop height based on another object's height. Updated the passive physics gravity support example ILE config file to use this property so it more closely aligns with the corresponding evaluation task.
- Added the `distance_between_performer_and_tool` config property to the `shortcut_lava_target_tool` option for setting a specific distance between the performer agent's starting position and the tool.
- Added the `left_lava_width` and `right_lava_width` config properties to the `shortcut_lava_target_tool` option.
- Added the `has_long_blocking_wall` config property to the `shortcut_bisecting_platform` option.
- Added the `num_targets_minus` config property for generating a number of interactable objects based on the number of targets (especially useful for Multi-Retrieval tasks).
- Added the `side_wall_opposite_colors` and `wall_material` config options for setting textures on exterior room walls.
- Added the `trapezoidal_room` config option for generating scenes in trapezoidal rooms.
- Added the `labels`, `position`, and `rotation` config properties to the `keyword_objects` option.
- Added the `look_at_center` config property to the `teleports` option.
- Improved error messages.
- Fixed minor bugs with placers.
- Added new example ILE config files:
    - Basic usage and core common sense concepts:
        - `multiple_targets`
        - `starts_near_object`
        - `turntable`
    - New evaluation tasks:
        - `holes_with_agent`
        - `interactive_number_comparison`
        - `interactive_spatial_reorientation`
        - `lava_with_agent`
        - `ramps_with_agent`

#### Release 1.4

Changelog:
- Updated passive physics example YAML configs:
  - Added the `passive_physics_floor: true` config option to lower the friction of the floor to the same amount that's used in the passive physics evaluation scenes.
  - Removed the second platform and second "placed" object from `passive_physics_gravity_support.yaml` to better align with the evaluation task.
  - Updated the room dimensions to depict deeper rooms used in Evaluation 5.
  - Tweaked some `last_step` amounts to better align with the evaluation tasks.
- Added the `rotate_cylinders` config option to automatically rotate cylindrical objects onto their rolling sides in the `passive_physics_collisions` example config.
- Added the `opposite_x` and `opposite_z` keyword locations and made use of `opposite_x` in the `interactive_agent_identification` example config to bring it in closer alignment with the setup for the corresponding evaluation task.
- Updated the `passive_physics_collisions` example config to demonstrate how the static object can be positioned properly if you remove the occluder from the scene.
- Fixed a bug with cylinders being made too thin in some scenes.

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
- Generated scenes should be run with [MCS release version 0.5.5](https://github.com/NextCenturyCorporation/MCS/releases/tag/0.5.5) or later.
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
- [multiple_targets.yaml](./ile_configs/multiple_targets.yaml) Generates scenes with four soccer ball multi retrieval targets.
- [specific_object.yaml](./ile_configs/specific_object.yaml) Generates scenes with a consistently sized and colored blue toy car object.
- [starts_frozen.yaml](./ile_configs/starts_frozen.yaml) Generates scenes in which the performer agent begins frozen for the first 5 to 100 steps.
- [starts_look_rotate_only.yaml](./ile_configs/starts_look_rotate_only.yaml) Generates scenes in which the performer agent begins able to only use the Look and Rotate actions for the first 5 to 100 steps.
- [starts_near_object.yaml](./ile_configs/starts_near_object.yaml) Generates scenes in which the performer agent begins at a specific distance from an object (either a ramp, a random container, or a soccer ball retrieval target).
- [target_soccer_ball.yaml](./ile_configs/target_soccer_ball.yaml) Generates scenes with a soccer ball retrieval target.
- [two_kidnappings.yaml](./ile_configs/two_kidnappings.yaml) Generates scenes in which the performer agent is kidnapped on steps 501 and 550.

#### Learning Core Common Sense Concepts

See the list of the Core Domains in our [MCS BAA Table doc](./docs/MCS_BAA_TABLE.md).

| MCS Core Domains | Example Config Files |
| --- | --- |
| P1, P6, P7 | [navigation_2d.yaml](./ile_configs/navigation_2d.yaml), [navigation_3d.yaml](./ile_configs/navigation_3d.yaml) |
| P2, P3 | [room_of_many_colors.yaml](./ile_configs/room_of_many_colors.yaml) |
| P4 | [container_with_separate_lid.yaml](./ile_configs/container_with_separate_lid.yaml), [containment.yaml](./ile_configs/containment.yaml), [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml), [occlusion_by_structure.yaml](./ile_configs/occlusion_by_structure.yaml) |
| O2 | [collisions.yaml](./ile_configs/collisions.yaml), [throwers.yaml](./ile_configs/throwers.yaml) |
| O3 | [collisions.yaml](./ile_configs/collisions.yaml), [droppers.yaml](./ile_configs/droppers.yaml), [placers.yaml](./ile_configs/placers.yaml) |
| O4 | [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml), [occlusion_by_structure.yaml](./ile_configs/occlusion_by_structure.yaml) |
| O6 | [droppers.yaml](./ile_configs/droppers.yaml), [placers.yaml](./ile_configs/placers.yaml) |
| O8 | [throwers.yaml](./ile_configs/throwers.yaml) |
| A5 | [agent_holds_target.yaml](./ile_configs/agent_holds_target.yaml),[agent_pointing_at_hidden_target.yaml](./ile_configs/agent_pointing_at_hidden_target.yaml) |
| TODO | [turntable.yaml](./ile_configs/turntable.yaml) |

List of example ILE configuration files helpful for learning core common sense concepts:

- [agent_holds_target.yaml](./ile_configs/agent_holds_target.yaml) Generates scenes with one interactive simulation-controlled agent holding the soccer ball retrieval target.
- [agent_pointing_at_hidden_target.yaml](./ile_configs/agent_pointing_at_hidden_target.yaml) Generates scenes with one interactive simulation-controlled agent pointing at a closed container in which the soccer ball retrieval target is hidden.
- [container_with_separate_lid.yaml](./ile_configs/agent_pointing_at_hidden_target.yaml) Generates scenes with a cuboid container which has a separate lid that is attached to the container by a placer.
- [collisions.yaml](./ile_configs/collisions.yaml) Generates scenes with a randomly positioned soccer ball retrieval target and a rolled ball that may or may not collide with it.
- [containment.yaml](./ile_configs/containment.yaml) Generates scenes with many closed containers and a soccer ball retrieval target hidden inside one of the containers.
- [droppers.yaml](./ile_configs/droppers.yaml) Generates scenes with many droppers and a soccer ball retrieval target held by one such device.
- [navigation_2d.yaml](./ile_configs/navigation_2d.yaml) Generates scenes with holes, walls, and lava as well as a randomly positioned soccer ball retrieval target.
- [navigation_3d.yaml](./ile_configs/navigation_3d.yaml) Generates scenes with holes, walls, lava, and platforms with ramps, as well as a randomly positioned soccer ball retrieval target.
- [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml) Generates scenes with many large objects and a soccer ball retrieval target either hidden behind an object or visible in front of an object.
- [occlusion_by_structure.yaml](./ile_configs/occlusion_by_structure.yaml) Generates scenes with many large structures and a soccer ball retrieval target either hidden behind a structure or visible in front of a structure.
- [placers.yaml](./ile_configs/placers.yaml) Generates scenes with many placers (some placers will be empty, and some placers will instead pick up objects) and a soccer ball retrieval target held by one such device.
- [room_of_many_colors.yaml](./ile_configs/room_of_many_colors.yaml) Generates scenes with randomly colored outer room walls and areas of floor, as well as a soccer ball retrieval target.
- [throwers.yaml](./ile_configs/throwers.yaml) Generates scenes with many throwers and a soccer ball retrieval target held by one such device.
- [turntable.yaml](./ile_configs/throwers.yaml) Generates scenes with a turntable (cog), a container, and a soccer ball retrieval target; sometimes the soccer ball and/or the container are on top of the turntable; sometimes the soccer ball is hidden inside of the container; the turntable rotates either 90, 180, 270, or 360 degrees.

#### Scenes for Specific Evaluation Tasks

See the list of the Core Domains in our [MCS BAA Table doc](./docs/MCS_BAA_TABLE.md).

Eval 3.X Tasks:

| Eval 3.X Task | MCS Core Domains | Example Config Files |
| --- | --- | --- |
| Containers (Interactive) | P1, P4 | [containment.yaml](./ile_configs/containment.yaml) |
| Gravity Support (Passive) | O6, P1 | [passive_physics_gravity_support.yaml](./ile_configs/passive_physics_gravity_support.yaml) |
| Obstacles (Interactive) | P1 | [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml) |
| Occluders (Interactive) | O1, P1, P4 | [occlusion_by_furniture.yaml](./ile_configs/occlusion_by_furniture.yaml) |
| Passive Object Permanence | O1, O4 | [passive_physics_fall_down.yaml](./ile_configs/passive_physics_fall_down.yaml), [passive_physics_move_across.yaml](./ile_configs/passive_physics_move_across.yaml), [passive_physics_move_behind.yaml](./ile_configs/passive_physics_move_behind.yaml) |
| Shape Constancy (Passive) | O1, O4 | [passive_physics_fall_down.yaml](./ile_configs/passive_physics_fall_down.yaml) |
| Spatio-Temporal Continuity (Passive) | O1, O4 | [passive_physics_move_across.yaml](./ile_configs/passive_physics_move_across.yaml) |

Eval 4 Tasks:

| Eval 4 Task | MCS Core Domains | Example Config Files |
| --- | --- | --- |
| Collisions (Passive) | O1, O2, O3 | [passive_physics_collisions.yaml](./ile_configs/passive_physics_collisions.yaml) |
| Interactive Object Permanence | O4 | [interactive_object_permanence.yaml](./ile_configs/interactive_object_permanence.yaml) |

Eval 5 Tasks:

| Eval 5 Task | MCS Core Domains | Example Config Files |
| --- | --- | --- |
| Agent Identification (Interactive) | A5 | [interactive_agent_identification.yaml](./ile_configs/interactive_agent_identification.yaml) |
| Moving Target Prediction (Interactive) | O8 | [interactive_moving_target_prediction.yaml](./ile_configs/interactive_moving_target_prediction.yaml) |
| Navigation: Holes (Interactive) | P7 | [holes.yaml](./ile_configs/holes.yaml), [holes_with_agent.yaml](./ile_configs/holes_with_agent.yaml) |
| Navigation: Lava (Interactive) | P7 | [lava.yaml](./ile_configs/lava.yaml) [lava_with_agent.yaml](./ile_configs/lava_with_agent.yaml) |
| Navigation: Ramps (Interactive) | P6 | [ramps.yaml](./ile_configs/ramps.yaml) [ramps_with_agent.yaml](./ile_configs/ramps_with_agent.yaml) |
| Solidity (Interactive) | O3 | [interactive_solidity.yaml](./ile_configs/interactive_solidity.yaml) |
| Spatial Elimination (Interactive) | P4 | [interactive_spatial_elimination.yaml](./ile_configs/interactive_spatial_elimination.yaml) |
| Support Relations (Interactive) | O6 | [interactive_support_relations.yaml](./ile_configs/interactive_support_relations.yaml) |
| Tool Use (Interactive) | O5 | [tools.yaml](./ile_configs/tools.yaml) |

List of example ILE configuration files for generating scenes similar to specific evaluation tasks:

- [holes.yaml](./ile_configs/holes.yaml) Generates scenes with many holes and a randomly positioned soccer ball retrieval target.
- [holes_with_agent.yaml](./ile_configs/holes_with_agent.yaml) Generates scenes with many holes and a randomly positioned agent holding a soccer ball retrieval target.
- [interactive_agent_identification.yaml](./ile_configs/interactive_agent_identification.yaml) Generates scenes similar to the interactive agent indentification eval tasks: start on a platform bisecting the room; an agent on one side of the platform; a static object on the other side of the room; must walk up to the agent and request for it to produce the target.
- [interactive_moving_target_prediction.yaml](./ile_configs/interactive_moving_target_prediction.yaml) Generates scenes similar to the interactive moving target prediction eval tasks: start on a platform; lava extending across both sides of the room; must first rotate in a 360 degree circle; then a thrower rolls a soccer ball from one end of the room toward the other; must predict the speed and trajectory of the soccer ball in order to intercept it efficiently.
- [interactive_object_permanence.yaml](./ile_configs/interactive_object_permanence.yaml) Generates scenes similar to the interactive object permanence eval tasks: start on a platform bisecting the room; an L-occluder on each side; and a thrower that tosses the soccer ball into the room.
- [interactive_solidity.yaml](./ile_configs/interactive_solidity.yaml) Generates scenes similar to the interactive solidity eval tasks: start on a platform bisecting the room; a placer holding the soccer ball descends from the ceiling; a door occluder descends from the ceiling; the placer releases the soccer ball so it falls somewhere behind the door occluder.
- [interactive_spatial_elimination.yaml](./ile_configs/interactive_spatial_elimination.yaml) Generates scenes similar to the interactive spatial elimination eval tasks: start on a platform bisecting the room; an occlusing wall on each side; and a soccer ball either in front of or behind an occluding wall.
- [interactive_support_relations.yaml](./ile_configs/interactive_support_relations.yaml) Generates scenes similar to the interactive support relations eval tasks: start on a platform bisecting the room; placers holding a container with the soccer ball descend from the ceiling; a door occluder descends from the ceiling; the placers release the container so it and the soccer ball land either fully, partially, or not on the platform.
- [lava.yaml](./ile_configs/lava.yaml) Generates scenes with many pools of lava and a randomly positioned soccer ball retrieval target.
- [lava_with_agent.yaml](./ile_configs/lava_with_agent.yaml) Generates scenes with many pools of lava and a randomly positioned agent with a soccer ball retrieval target.
- [passive_physics_collisions.yaml](./ile_configs/passive_physics_collisions.yaml) Generates scenes similar to passive physics collisions eval tasks: same view; similarly sized and positioned moving-and-rotating occluders; multiple objects, possibly colliding; only able to use Pass actions.
- [passive_physics_gravity_support.yaml](./ile_configs/passive_physics_gravity_support.yaml) Generates scenes similar to passive physics gravity support eval tasks: same view; one similarly sized and positioned platform; one placer lowering an object into the scene, possibly above the platform, and then releasing it; only able to use Pass actions.
- [passive_physics_fall_down.yaml](./ile_configs/passive_physics_fall_down.yaml) Generates scenes similar to passive physics eval tasks with objects falling down: same view; similarly sized and positioned moving-and-rotating occluders; multiple objects falling into the scene; only able to use Pass actions.
- [passive_physics_move_across.yaml](./ile_configs/passive_physics_move_across.yaml) Generates scenes similar to passive physics eval tasks with objects moving across: same view; similarly sized and positioned moving-and-rotating occluders; multiple objects moving across the scene; only able to use Pass actions.
- [passive_physics_move_behind.yaml](./ile_configs/passive_physics_move_behind.yaml) Generates scenes similar to passive physics eval tasks with objects moving and stopping behind occluders: same view; similarly sized and positioned moving-and-rotating occluder; one object moving across the scene; only able to use Pass actions.
- [ramps.yaml](./ile_configs/ramps.yaml) Generates scenes with ramps leading up to platforms and a soccer ball retrieval target either on top of the platform or on the floor adjacent to the platform.
- [ramps_with_agent.yaml](./ile_configs/ramps_with_agent.yaml) Generates scenes with ramps leading up to platforms and an agent with a soccer ball retrieval target.
- [tools.yaml](./ile_configs/tools.yaml) Generates scenes with a large moveable block tool and a soccer ball retrieval target completely surrounded by lava.

Eval 6 Tasks:

| Eval 6 Task | MCS Core Domains | Example Config Files |
| --- | --- | --- |
| Imitation (Interactive) | O5 | [interactive_imitation.yaml](./ile_configs/interactive_imitation.yaml) |
| Navigation: Holes (Interactive) | P7 | New variations with agents; see the Eval 5 Tasks above |
| Navigation: Lava (Interactive) | P7 | New variations with agents; see the Eval 5 Tasks above |
| Navigation: Ramps (Interactive) | P6 | New variations with agents; see the Eval 5 Tasks above |
| Number Comparison (Interactive) | TODO | [interactive_number_comparison.yaml](./ile_configs/interactive_number_comparison.yaml) |
| Set Rotation (Interactive) | TODO | [interactive_set_rotation.yaml](./ile_configs/interactive_set_rotation.yaml) |
| Shell Game (Interactive) | TODO | [interactive_shell_game.yaml](./ile_configs/interactive_shell_game.yaml) |
| Spatial Reference (Interactive) | TODO | [interactive_spatial_reference.yaml](./ile_configs/interactive_spatial_reference.yaml) |
| Spatial Reorientation (Interactive) | P2, P3 | [interactive_spatial_reorientation.yaml](./ile_configs/interactive_spatial_reorientation.yaml) |
| Tool Choice (Interactive) | O5 | [interactive_tool_choice.yaml](./ile_configs/interactive_tool_choice.yaml) |
| Tool Use (Interactive) | O5 | New variations with asymmetric (hooked) tools; see the Eval 5 Tasks above |

List of example ILE configuration files for generating scenes similar to specific evaluation tasks:

- [interactive_imitation.yaml](./ile_configs/interactive_imitation.yaml) Generates scenes similar to the interactive imitation eval tasks.
- [interactive_number_comparison.yaml](./ile_configs/interactive_number_comparison.yaml) Generates scenes similar to the interactive number comparison eval tasks: start on a platform bisecting the room; one or more soccer ball multi-retrieval targets on one side; fewer soccer balls on the other side.
- [interactive_set_rotation.yaml](./ile_configs/interactive_set_rotation.yaml) Generates scenes similar to the interactive set rotation eval tasks: start in a room with one or more identical containers positioned on top of a turntable (giant cog); a soccer ball retrieval target is placed inside a container; lids are placed on all containers; the turntable rotates between 90 and 360 degrees.
- [interactive_shell_game.yaml](./ile_configs/interactive_shell_game.yaml) Generates scenes similar to the interactive shell game eval tasks: start in a room with one or more identical containers; a soccer ball retrieval target is placed inside a container; lids are placed on all containers; a placer drags the target's container to a new location.
- [interactive_spatial_reference.yaml](./ile_configs/interactive_spatial_reference.yaml) Generates scenes similar to the interactive spatial reference eval tasks: start on a platform bisecting the room; identical closed containers on both sides; an agent walks and points at the container hiding the soccer ball retrieval target; a turntable (giant cog) rotates a non-agent object so it "points" at a container, which may be the same container, or the opposite container.
- [interactive_spatial_reorientation.yaml](./ile_configs/interactive_spatial_reorientation.yaml) Generates scenes similar to the interactive spatial reorientation eval tasks: start on a platform bisecting the room; identical bins on either side of the room; a placer drops a soccer ball retrieval target into one bin; the performer agent is kidnapped and sometimes teleported to the other side of the room; sometimes one room wall is a different color, and/or the room is trapezoidal.
- [interactive_tool_choice.yaml](./ile_configs/interactive_tool_choice.yaml) Generates scenes similar to the interactive tool choice eval tasks: start on a platform bisecting the room; soccer balls surrounded by lava on both sides; one side has a useful tool, but the other side does not have a tool, or has a tool that is too small to use.

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
