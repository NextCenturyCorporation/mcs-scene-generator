# The Hypercube Scene Generator

For the main docs, including setup instructions and validation tips, please see the main [README](./README.md) file.

## Hypercube Scene Generator

The public Scene Generator is used to generate training scenes for Eval 3 and 4.

### Notes

- Eval 4: If you generate Eval 3 hypercubes for training (interactive container, interactive obstacle, interactive occluder, intuitive physics shape constancy), please note that all "untrained"/"novel" shapes will be chosen from the same set of "trained"/"familiar" shapes that are currently available for all training in Eval 4.
- Eval 5 and beyond: Please use the [ILE Scene Generator](#ile-scene-generator) for training.

### Running

To see all of the scene generator's options:

```
python generate_public_scenes.py --help
```

The scene generator creates one or more "hypercubes" of one or more scenes for a specific task like "Object Permanence" or "Container Retrieval". Each scene is output as two JSON files: a "normal" version that is given to performers for training and validation, and a "debug" version (with filenames ending in `_debug.json`) with answers (ground truth) and debug information for our Evaluation Dashboard UI.

Common arguments:

- `-p <prefix>` (required): Filename prefix for the output JSON scene files.
- `-t <type>` (required): Type of hypercubes to generate.
- `-c <count>` (optional): Number of hypercubes to generate. Default: 1
- `-e <eval>` (optional): Evaluation name to save in the scene tags. Default: None
- `-s <seed>` (optional): Random seed.
- `--sort-hypercube` (optional): Sort the hypercube scenes alphabetically by cell name, so A1 is always scene 1, A2 is always scene 2, etc.
- `--stop-on-error` (optional): Stop scene generation on any error.

You can generate scenes containing specific objects by passing the [object type](https://github.com/NextCenturyCorporation/MCS/blob/master/machine_common_sense/scenes/SCHEMA.md#object-list) to the scene generator using the following arguments (please note that the color and size of the object is currently chosen randomly, within the usual range):

- `--agent <type>` (optional): Force the agent object to be a specific type (shape). Used in agent scenes.
- `--asymmetric <type>` (optional): Force the asymmetric target object to be a specific type (shape). Used in gravity support scenes.
- `--container <type>` (optional): Force the primary container object (that contains the target) to be a specific type (shape). Used in interactive container scenes.
- `--context <type>` (optional): Force one context object to be a specific type (shape). Used in interactive scenes.
- `--non-target <type>` (optional): Force the non-target object to be a specific type (shape). Used in intuitive physics (but not gravity support) and agent scenes.
- `--obstacle <type>` (optional): Force the obstacle object to be a specific type (shape). Used in interactive obstacle scenes.
- `--occluder <type>` (optional): Force the primary occluder object (that occludes the target) to be a specific type (shape). Used in interactive occluder scenes.
- `--second-agent <type>` (optional): Force the second agent object in multi-agent scenes to be a specific type (shape). Used in agent scenes.
- `--symmetric <type>` (optional): Force the symmetric target object to be a specific type (shape). Used in gravity support scenes.
- `--target <type>` (optional): Force the target object to be a specific type (shape). Used in intuitive physics (but not gravity support) and agent scenes. Please note that the target object in interactive scenes is currently always a soccer ball.

### Intuitive Physics Scenes

For information on what each passive intuitive physics scene should depict (and how each scene is labeled), please see [this documentation](https://github.com/NextCenturyCorporation/mcs-private/blob/master/scene_generator/docs/).

#### Intuitive Physics Objects

The Eval 3.5 Gravity Support scenes only use the following object types:

- Symmetric target (set with the `--symmetric` flag):
  - `circle_frustum`
  - `cone`
  - `cube`
  - `cylinder`
  - `pyramid`
  - `square_frustum`
- Asymmetric target (set with the `--asymmetric` flag):
  - `letter_l_narrow`
  - `letter_l_wide`
  - `triangle`
- Support (hard-coded):
  - `cube`

The Eval 3 Object Permanence and Shape Constancy scenes only use the following target and non-target object types:

- `car_1`
- `circle_frustum`
- `cone`
- `cube`
- `cylinder`
- `dog_on_wheels`
- `duck_on_wheels`
- `pyramid`
- `racecar_red`
- `sphere`
- `square_frustum`
- `train_1`
- `trolley_1`
- `truck_1`
- `tube_narrow`
- `tube_wide`
- `turtle_on_wheels`

The Eval 3 Spatio-Temporal Continuity scenes, and all the Eval 4 scenes, only use the following target and non-target object types:

- `car_1`
- `cylinder`
- `dog_on_wheels`
- `duck_on_wheels`
- `racecar_red`
- `sphere`
- `train_1`
- `trolley_1`
- `truck_1`
- `tube_narrow`
- `tube_wide`
- `turtle_on_wheels`

The Eval 4 Object Permanence and Spatio-Temporal Continuity scenes (both during training and the Eval) use the same objects as listed above EXCEPT they cannot use spheres.

#### Training Intuitive Physics Datasets

Training intuitive physics scenes are not implausible and do not have any "untrained" objects.

```
python generate_public_scenes.py -p <prefix> -t CollisionTraining
python generate_public_scenes.py -p <prefix> -t GravitySupportTraining
python generate_public_scenes.py -p <prefix> -t ObjectPermanenceTraining3
python generate_public_scenes.py -p <prefix> -t ObjectPermanenceTraining4
python generate_public_scenes.py -p <prefix> -t ShapeConstancyTraining
python generate_public_scenes.py -p <prefix> -t SpatioTemporalContinuityTraining3
python generate_public_scenes.py -p <prefix> -t SpatioTemporalContinuityTraining4
```

- Each Collisions training hypercube contains 3 scenes.
- Each Gravity Support training hypercube contains 8 scenes.
- Each Eval 3 or 4 Object Permanence training hypercube contains 2 scenes.
- Each Shape Constancy training hypercube contains 2 scenes.
- Each Eval 3 Spatio-Temporal Continuity training hypercube contains 9 scenes.
- Each Eval 4 Spatio-Temporal Continuity training hypercube contains 2 scenes.

#### Evaluation Intuitive Physics Datasets

Evaluation intuitive physics scenes are either plausible or implausible and can have "untrained" objects.

```
python generate_public_scenes.py -p <prefix> -t GravitySupportEvaluation
python generate_public_scenes.py -p <prefix> -t ObjectPermanenceEvaluation3
python generate_public_scenes.py -p <prefix> -t ShapeConstancyEvaluation
python generate_public_scenes.py -p <prefix> -t SpatioTemporalContinuityEvaluation3
```

- Each Gravity Support evaluation hypercube contains 16 scenes.
- Each Eval 3 Object Permanence evaluation hypercube contains 90 scenes.
- Each Shape Constancy evaluation hypercube contains 42 scenes.
- Each Eval 3 Spatio-Temporal Continuity evaluation hypercube contains 42 scenes.

### Interactive Scenes

For information on what each interaction scene should depict (and how each scene is labeled), please see [this documentation](https://github.com/NextCenturyCorporation/mcs-private/blob/master/scene_generator/docs/).

#### Generic Interactive Scenes

To generate an interactive scene that's just a random collection of objects in a room with a random starting location (and doesn't follow a hypercube design):

```
python generate_public_scenes.py -p <prefix> -t Retrieval
```

- Each retrieval scene contains the soccer ball as the target object.

#### Training Interactive Datasets

Training interactive scenes do not have any "untrained" objects.

```
python generate_public_scenes.py -p <prefix> -t ContainerRetrievalTraining
python generate_public_scenes.py -p <prefix> -t ObstacleRetrievalTraining
python generate_public_scenes.py -p <prefix> -t OccluderRetrievalTraining
```

- Each container training hypercube contains 18 scenes.
- Each obstacle training hypercube contains 4 scenes.
- Each occluder training hypercube contains 12 scenes.

#### Evaluation Interactive Datasets

Evaluation interactive scenes can have "untrained" objects.

```
python generate_public_scenes.py -p <prefix> -t ContainerRetrievalEvaluation
python generate_public_scenes.py -p <prefix> -t ContainerRetrievalEvaluation4
python generate_public_scenes.py -p <prefix> -t ObstacleRetrievalEvaluation
python generate_public_scenes.py -p <prefix> -t OccluderRetrievalEvaluation
```

- Each container evaluation hypercube contains 36 scenes.
- Each Eval 4 container evaluation hypercube contains 12 scenes.
- Each obstacle evaluation hypercube contains 8 scenes.
- Each occluder evaluation hypercube contains 24 scenes.

### Passive Agent Training Scenes

#### Evaluation 5 (July 2022)

- [Efficiency - Irrational](https://eval-5.s3.amazonaws.com/eval_5_passive_agent_efficient_action_irrational_training_scenes.zip)
- [Efficiency - Path Control](https://eval-5.s3.amazonaws.com/eval_5_passive_agent_efficient_action_path_training_scenes.zip)
- [Efficiency - Time Control](https://eval-5.s3.amazonaws.com/eval_5_passive_agent_efficient_action_time_training_scenes.zip)
- [Inaccessible Goal](https://eval-5.s3.amazonaws.com/eval_5_passive_agent_inaccessible_goal_training_scenes.zip)
- [Instrumental Action - Blocking Barriers](https://eval-5.s3.amazonaws.com/eval_5_passive_agent_instrumental_action_blocking_barriers_training_scenes.zip)
- [Instrumental Action - Inconsequential Barriers](https://eval-5.s3.amazonaws.com/eval_5_passive_agent_instrumental_action_inconsequential_barriers_training_scenes.zip)
- [Instrumental Action - No Barriers](https://eval-5.s3.amazonaws.com/eval_5_passive_agent_instrumental_action_no_barriers_training_scenes.zip)
- [Multiple Agents](https://eval-5.s3.amazonaws.com/eval_5_passive_agent_multiple_agents_training_scenes.zip)
- [Object Preference](https://eval-5.s3.amazonaws.com/eval_5_passive_agent_object_preference_training_scenes.zip)

### Passive Agent Training Videos

If you would prefer to train for the passive agent tasks using video frames rather than having to generate each scene's images by running the MCS simulation environment (and avoid having to use our Hypercube Scene Generator for the passive agent tasks), here are videos of all the training scenes that were rendered for you using the MCS simulation environment.

#### Evaluation 5 (July 2022)

TODO

Copyright 2022 CACI
