# The ILE and Hypercube Scene Generators

## Setup

Please use Python 3.8

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

## ILE Scene Generator

The Ideal Learning Environment (ILE) will be used to generate training scenes for Eval 5 and beyond. If you wish to request a new feature to report a bug, please post on this GitHub repository's [Issues page](https://github.com/NextCenturyCorporation/mcs-scene-generator/issues).

The ILE runs using a YAML config file to set scene options. To see all config file properties, please review the [ILE_API.md](./ILE_API.md) documentation.

The ILE outputs JSON files in the [MCS scene format](https://nextcenturycorporation.github.io/MCS/schema.html) to be run with the [machine_common_sense](https://github.com/NextCenturyCorporation/MCS) python library and corresponding Unity application.

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


### Agent Scenes

#### Passive Agent Training Videos

If you would prefer to train for the passive agent tasks using video frames rather than having to generate each scene's images by running the MCS simulation environment (and avoid having to use our Hypercube Scene Generator for the passive agent tasks), here are videos of all the training scenes that were rendered for you using the MCS simulation environment.

2021 Background/Training:

- [agent_instrumental_action_training_videos.zip](https://nyu-datasets.s3.amazonaws.com/agent_instrumental_action_training_videos.zip)
- [agent_multiple_agents_training_videos.zip](https://nyu-datasets.s3.amazonaws.com/agent_multiple_agents_training_videos.zip)
- [agent_object_preference_training_videos.zip](https://nyu-datasets.s3.amazonaws.com/agent_object_preference_training_videos.zip)
- [agent_single_object_training_videos.zip](https://nyu-datasets.s3.amazonaws.com/agent_single_object_training_videos.zip)

#### Hypercube Scene Generator Setup

First, download and unzip the bundles containing the NYU agent scene JSON files that we convert:

Winter 2020 Background/Training:

- [agents_background_object_preference.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_object_preference.zip)
- [agents_background_single_object.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_single_object.zip)

Winter 2020 Evaluation/Testing:

- [agents_evaluation_object_preference.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_object_preference.zip)
- [agents_evaluation_efficient_action_a.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_a.zip)
- [agents_evaluation_efficient_action_b.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_b.zip)

2021 Background/Training:

- [agents_background_instrumental_action.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_instrumental_action.zip)
- [agents_background_multiple_agents.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_multiple_agents.zip)
- [agents_background_object_preference_v2.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_object_preference_v2.zip)
- [agents_background_single_object_v2.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_single_object_v2.zip)

2021 Evaluation/Testing:

- [agents_evaluation_efficient_action_irrational.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_irrational.zip)
- [agents_evaluation_efficient_action_irrational.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_irrational.zip)
- [agents_evaluation_efficient_action_irrational.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_irrational.zip)
- [agents_evaluation_inaccessible_goal.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_inaccessible_goal.zip)
- [agents_evaluation_instrumental_action_blocking_barriers.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_blocking_barriers.zip)
- [agents_evaluation_instrumental_action_inconsequential_barriers.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_inconsequential_barriers.zip)
- [agents_evaluation_instrumental_action_no_barriers.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_no_barriers.zip)
- [agents_evaluation_multiple_agents.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_multiple_agents.zip)
- [agents_evaluation_object_preference_eval_4.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_object_preference_eval_4.zip)

Unzipping each bundle should extract a corresponding folder (containing the JSON files) nested within this folder, with a name like "agents_background_object_preference".

Now you can generate the MCS agent scene JSON files, converted from the NYU JSON files.

#### Agent and Goal Objects

The Eval 3.5 Gravity Support scenes only use the following object types:

- Agent (set with the `--agent` flag):
  - `circle_frustum`
  - `cone`
  - `cube`
  - `cylinder`
  - `pyramid`
  - `square_frustum`
  - `tube_narrow`
  - `tube_wide`
- Goal Objects (set with the `--target` and `--non-target` flags):
  - `cube_hollow_narrow`
  - `cube_hollow_wide`
  - `cube`
  - `cylinder`
  - `hash`
  - `letter_x`
  - `semi_sphere`
  - `sphere`
  - `square_frustum`
  - `tube_narrow`
  - `tube_wide`

#### Training Agent Datasets

Training agent scenes are not unexpected and do not have any "untrained" objects.

```
python generate_public_scenes.py -p <prefix> -t AgentInstrumentalActionTraining
python generate_public_scenes.py -p <prefix> -t AgentMultipleAgentsTraining
python generate_public_scenes.py -p <prefix> -t AgentObjectPreferenceTraining
python generate_public_scenes.py -p <prefix> -t AgentSingleObjectTraining
```

#### Agent Scene Conversion Validation

To validate our conversion from NYU to MCS scene data, you can download and watch the NYU movies for the corresponding scenes:

Winter 2020 Background/Training:

- [agents_background_object_preference_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_object_preference_movies.zip)
- [agents_background_single_object_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_single_object_movies.zip)

Winter 2020 Evaluation/Testing:

- [agents_evaluation_object_preference_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_object_preference_movies.zip)
- [agents_evaluation_efficient_action_a_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_a_movies.zip)
- [agents_evaluation_efficient_action_b_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_b_movies.zip)

2021 Background/Training:

- [agents_background_instrumental_action.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_instrumental_action_movies.zip)
- [agents_background_multiple_agents.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_multiple_agents_movies.zip)
- [agents_background_object_preference_v2_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_object_preference_v2_movies.zip)
- [agents_background_single_object_v2_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_single_object_v2_movies.zip)

2021 Evaluation/Testing:

- [agents_evaluation_efficient_action_irrational_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_irrational_movies.zip)
- [agents_evaluation_efficient_action_irrational_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_irrational_movies.zip)
- [agents_evaluation_efficient_action_irrational_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_irrational_movies.zip)
- [agents_evaluation_inaccessible_goal_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_inaccessible_goal_movies.zip)
- [agents_evaluation_instrumental_action_blocking_barriers_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_blocking_barriers_movies.zip)
- [agents_evaluation_instrumental_action_inconsequential_barriers_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_inconsequential_barriers_movies.zip)
- [agents_evaluation_instrumental_action_no_barriers_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_no_barriers_movies.zip)
- [agents_evaluation_multiple_agents_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_multiple_agents_movies.zip)
- [agents_evaluation_object_preference_eval_4_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_object_preference_eval_4_movies.zip)

NYU's webpage: [https://www.kanishkgandhi.com/bib](https://www.kanishkgandhi.com/bib)

#### New Agent Scene Files

If you want to run your own custom agent scene files (in the NYU JSON data format), the easiest way to do so is:

1. Remove all of the existing JSON files from `./agents_examples/`
2. Copy all of your NYU agent scene JSON files into `./agents_examples/`
3. Run the scene generator with `-t` of either `AgentExamplesTraining` if the data is only `e.json` ("expected") files, or `AgentExamplesEvaluation` if the data is pairs of `e.json` ("expected") and `u.json` ("unexpected") files. Use `-c <count>` to run on more than one file. Files are chosen for conversion randomly from all of the files in `./agents_examples/`.
4. The resulting agent scene files (in the MCS JSON data format) are saved in your current directory as both `.json` (the data we give to ML algorithms) and `_debug.json` (with additional debug information) versions. You can now run the scenes using the [MCS interactive 3D simulation environment](https://github.com/NextCenturyCorporation/MCS/tree/master).

## Validating

In the `MCS` repository, in the `scripts` folder, use one of the following scripts to run all of the new scenes, depending on if you're running an interactive or passive (intuitive physics, agents, etc.) hypercube.

- [run_interactive_scenes.py](https://github.com/NextCenturyCorporation/MCS/blob/development/scripts/run_interactive_scenes.py) to load each scene (JSON file) starting with a given prefix and rotate in a circle.
- [run_passive_scenes.py](https://github.com/NextCenturyCorporation/MCS/blob/development/scripts/run_passive_scenes.py) to load each scene (JSON file) starting with a given prefix and pass until the scene is finished.

```
python run_interactive_scenes.py <mcs_unity_app> <file_path_prefix>
python run_passive_scenes.py <mcs_unity_app> <file_path_prefix>
```

(Please see the [scripts README](https://github.com/NextCenturyCorporation/MCS/blob/development/scripts/README.md) for more information.)

If you're validating scenes that you just made, and they're all in this folder, then the `<file_path_prefix>` will be `<mcs-scene-generator>/<prefix>`, where `<prefix>` is the filename prefix that you used to run the scene generator.

## Developer Usage

### Testing

Please note that the tests will take a few minutes to run!

Also note that some of the "unit" tests are not completely deterministic (specifically, the hypercube tests generate random hypercubes and verify that their scenes are made within expected parameters). If you see a test fail, it may only do so intermittently, but it's also useful if you can save the error log and notify TA2. Thanks.

To run:

```
python -m pytest -vv
```

If you have a lot of extra files in this folder (scenes, images, videos, zips, etc.), the tests may take a long time to start, so you can just run:

```
python -m pytest tests/* -vv
```

### Linting

We are currently using [flake8](https://flake8.pycqa.org/en/latest/) and [autopep8](https://pypi.org/project/autopep8/) for linting and formatting our Python code. This is enforced within the python_api and scene_generator projects. Both are [PEP 8](https://www.python.org/dev/peps/pep-0008/) compliant (besides some inline exceptions), although we are ignoring the following rules:
- **E402**: Module level import not at top of file
- **W504**: Line break occurred after a binary operator

A full list of error codes and warnings enforced can be found [here](https://flake8.pycqa.org/en/latest/user/error-codes.html)

Both have settings so that they should run on save within Visual Studio Code [settings.json](../.vscode/settings.json) as well as on commit after running `pre-commit install` (see [.pre-commit-config.yaml](../../.pre-commit-config.yaml) and [.flake8](../../.flake8)), but can also be run on the command line:


```
flake8 --per-file-ignores="materials.py:E501"
```

and

```
autopep8 --in-place --aggressive --recursive <directory>
```

or

```
autopep8 --in-place --aggressive <file>
```

### Creating New ILE Components

The ILE uses "ILE Components" to manage specific subsets of ILE config file properties. An ILE Component reads and saves the properties from the config file that are relevant to its behavior, validates those properties, creates default values for any unassigned properties, and updates those properties in scene templates to generate scenes. To add support for new config file properties, you either need to create a new ILE Component for those properties, or extend an existing ILE Component (whatever makes the most sense within the codebase).

To create an ILE Component subclass:
1. Create a new class that extends ILEComponent (from `ideal_learning_env/components.py`). Steps 2-5 affect this new component.
2. Define each config file property as an attribute on the class with a type hint and a docstring. The type should be a primitive, a Python class, a list of primitives or Python classes, or a union of primitives, lists, and/or Python classes; please avoid using dicts if possible. The docstring should have both a "Simple Example" and an "Advanced Example" blocks of working YAML code surrounded by two sets of three backticks (see the example below). Any class attributes that are not also intended to be config file properties should be marked as protected or private (named with a leading underscore `_`).
3. Define a `set_<property_name>(self, data: Any) -> None` function for each class attribute you defined in Step 2 above with an `@ile_config_setter()` decorator (from `ideal_learning_env/decorators.py`). The function should just set your class's attribute to the given data: `self.<property_name> = data`. The decorator will automatically read the property from the config file data, validate its type, and cast it. You can run additional validation (e.g. ensure that a number is within a specific range, or that the X/Y/Z attributes of a Vector are not null), by passing an `ILEValidator` using the `validator` argument to the decorator function: `@ile_config_setter(validator=<ILEValidator()>)`.
4. Optionally (but recommended), define a `get_property_name(self)` function for each class attribute to return that variable, or a default value if it wasn't configured. Get input from the design team to decide on what the defaults should be. You can use the `choose_random` functions (from `ideal_learning_env/choosers.py`) to randomly choose single values from lists or MinMax classes.
5. Override the `update_ile_scene` function. Hopefully this is just a matter of setting the relevant properties on the scene with the output of your corresponding getter functions. Please see the [JSON schema](https://nextcenturycorporation.github.io/MCS/schema.html) for details on all of the scene file properties.
6. Add your new class to the list of `ILE_COMPONENTS` in `ile.py`
7. Add your new properties to a config file and run the ILE to test your component.
8. Create some unit tests for your new class and run the unit test suite.
9. When you commit your new class, the API doc and sample config files should automatically update with the new properties.

Example ILE Component attribute and docstring:
```python
    room_dimensions: Union[VectorIntConfig, List[VectorIntConfig]] = None
    """
    ([VectorIntConfig](#VectorIntConfig) dict, or list of VectorIntConfig
    dicts) -- The total dimensions for the room, or list of dimensions, from
    which one is chosen at random for each scene. Rooms are always rectangular
    or square. The X and Z must each be within [2, 15] and the Y must be within
    [2, 10]. The room's bounds will be [-X/2, X/2] and [-Z/2, Z/2].
    Default: random

    Simple Example:
    ```
    room_dimensions: null
    ```

    Advanced Example:
    ```
    room_dimensions:
        x: 10
        y:
            - 3
            - 4
            - 5
            - 6
        z:
            min: 5
            max: 10
    ```
    """
```

## Resources

- [MCS BAA Core Domains](./docs/MCS_BAA_Core_Domain_List.jpeg)

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

Copyright 2021 CACI (formerly Next Century Corporation)
