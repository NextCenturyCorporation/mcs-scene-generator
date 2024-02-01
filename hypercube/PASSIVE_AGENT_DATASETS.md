# Passive Agent Datasets

Developer information for generating passive agent datasets from NYU data.

## Agent Scenes

### Hypercube Scene Generator Setup

First, download and unzip the bundles containing the NYU agent scene JSON files that we convert:

#### Winter 2020 Background/Training:

- [agents_background_object_preference.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_object_preference.zip)
- [agents_background_single_object.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_single_object.zip)

#### Winter 2020 Evaluation/Testing:

- [agents_evaluation_object_preference.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_object_preference.zip)
- [agents_evaluation_efficient_action_a.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_a.zip)
- [agents_evaluation_efficient_action_b.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_b.zip)

#### 2021 Background/Training:

- [agents_background_instrumental_action.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_instrumental_action.zip)
- [agents_background_multiple_agents.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_multiple_agents.zip)
- [agents_background_object_preference_v2.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_object_preference_v2.zip)
- [agents_background_single_object_v2.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_single_object_v2.zip)

#### 2021 Evaluation/Testing:

- [agents_evaluation_efficient_action_irrational.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_irrational.zip)
- [agents_evaluation_efficient_action_path.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_path.zip)
- [agents_evaluation_efficient_action_time.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_time.zip)
- [agents_evaluation_inaccessible_goal.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_inaccessible_goal.zip)
- [agents_evaluation_instrumental_action_blocking_barriers.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_blocking_barriers.zip)
- [agents_evaluation_instrumental_action_inconsequential_barriers.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_inconsequential_barriers.zip)
- [agents_evaluation_instrumental_action_no_barriers.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_no_barriers.zip)
- [agents_evaluation_multiple_agents.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_multiple_agents.zip)
- [agents_evaluation_object_preference_eval_4.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_object_preference_eval_4.zip)

#### Spring 2023 Background/Training:

* Please note: The format for some of these scene files has changed, so some datasets may no longer work properly. If you have trouble with them, use the evaluation/testing datasets instead, or ask NYU for more background/training data if necessary. *

- [agents_background_agent_one_goal.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_agent_one_goal.zip)
- [agents_background_agent_preference.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_agent_preference.zip)
- [agents_background_collect.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_collect.zip)
- [agents_background_instrumental_approach.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_instrumental_approach.zip)
- [agents_background_instrumental_imitation.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_instrumental_imitation.zip) * Please note: Scene 000000iie.json is a bad file! Ignore it. *
- [agents_background_non_agent_one_goal.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_non_agent_one_goal.zip)
- [agents_background_non_agent_preference.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_non_agent_preference.zip)
- [agents_background_social_approach.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_social_approach.zip)
- [agents_background_social_imitation.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_social_imitation.zip)

#### Spring 2023 Evaluation/Testing:

- [agents_evaluation_approach.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_approach.zip)
- [agents_evaluation_imitation_fixed.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_imitation_fixed.zip)
- [agents_evaluation_non_agent.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_non_agent.zip)

#### Fall 2023 Background/Training:

- [false_belief_background.zip](https://nyu-datasets.s3.amazonaws.com/false_belief_background.zip)
- [helper_hinderer_background.zip](https://nyu-datasets.s3.amazonaws.com/helper_hinderer_background.zip)
- [true_belief_background.zip](https://nyu-datasets.s3.amazonaws.com/true_belief_background.zip)

#### Fall 2023 Evaluation/Testing:

- [agents_evaluation_helper_hinderer.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_helper_hinderer.zip)
- [agents_evaluation_true_false_belief.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_true_false_belief.zip)

Unzipping each bundle should extract a corresponding folder (containing the JSON files) nested within this folder, with a name like "agents_background_object_preference".

Now you can generate the MCS agent scene JSON files, converted from the NYU JSON files.

### Agent and Goal Objects

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

### Training Agent Datasets

Training agent scenes are not unexpected and do not have any "untrained" objects.

```
python generate_public_scenes.py -p <prefix> -t AgentInstrumentalActionTraining
python generate_public_scenes.py -p <prefix> -t AgentMultipleAgentsTraining
python generate_public_scenes.py -p <prefix> -t AgentObjectPreferenceTraining
python generate_public_scenes.py -p <prefix> -t AgentSingleObjectTraining
```

### Agent Scene Conversion Validation

To validate our conversion from NYU to MCS scene data, you can download and watch the NYU movies for the corresponding scenes:

#### Winter 2020 Background/Training:

- [agents_background_object_preference_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_object_preference_movies.zip)
- [agents_background_single_object_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_single_object_movies.zip)

#### Winter 2020 Evaluation/Testing:

- [agents_evaluation_object_preference_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_object_preference_movies.zip)
- [agents_evaluation_efficient_action_a_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_a_movies.zip)
- [agents_evaluation_efficient_action_b_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_b_movies.zip)

#### 2021 Background/Training:

- [agents_background_instrumental_action.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_instrumental_action_movies.zip)
- [agents_background_multiple_agents.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_multiple_agents_movies.zip)
- [agents_background_object_preference_v2_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_object_preference_v2_movies.zip)
- [agents_background_single_object_v2_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_background_single_object_v2_movies.zip)

#### 2021 Evaluation/Testing:

- [agents_evaluation_efficient_action_irrational_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_irrational_movies.zip)
- [agents_evaluation_efficient_action_path_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_path_movies.zip)
- [agents_evaluation_efficient_action_time_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_efficient_action_time_movies.zip)
- [agents_evaluation_inaccessible_goal_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_inaccessible_goal_movies.zip)
- [agents_evaluation_instrumental_action_blocking_barriers_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_blocking_barriers_movies.zip)
- [agents_evaluation_instrumental_action_inconsequential_barriers_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_inconsequential_barriers_movies.zip)
- [agents_evaluation_instrumental_action_no_barriers_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_instrumental_action_no_barriers_movies.zip)
- [agents_evaluation_multiple_agents_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_multiple_agents_movies.zip)
- [agents_evaluation_object_preference_eval_4_movies.zip](https://nyu-datasets.s3.amazonaws.com/agents_evaluation_object_preference_eval_4_movies.zip)

NYU's webpage: [https://www.kanishkgandhi.com/bib](https://www.kanishkgandhi.com/bib)

### New Agent Scene Files

If you want to run your own custom agent scene files (in the NYU JSON data format), the easiest way to do so is:

1. Remove all of the existing JSON files from `./agents_examples/`
2. Copy all of your NYU agent scene JSON files into `./agents_examples/`
3. Run the scene generator with `-t` of either `AgentExamplesTraining` if the data is only `e.json` ("expected") files, or `AgentExamplesEvaluation` if the data is pairs of `e.json` ("expected") and `u.json` ("unexpected") files. Use `-c <count>` to run on more than one file. Files are chosen for conversion randomly from all of the files in `./agents_examples/`.
4. The resulting agent scene files (in the MCS JSON data format) are saved in your current directory as both `.json` (the data we give to ML algorithms) and `_debug.json` (with additional debug information) versions. You can now run the scenes using the [MCS interactive 3D simulation environment](https://github.com/NextCenturyCorporation/MCS/tree/master).

### Passive Agent Training Videos

If you would prefer to train for the passive agent tasks using video frames rather than having to generate each scene's images by running the MCS simulation environment (and avoid having to use our Hypercube Scene Generator for the passive agent tasks), here are videos of all the training scenes that were rendered for you using the MCS simulation environment.

#### 2021 Background/Training:

- [agent_instrumental_action_training_videos.zip](https://nyu-datasets.s3.amazonaws.com/agent_instrumental_action_training_videos.zip)
- [agent_multiple_agents_training_videos.zip](https://nyu-datasets.s3.amazonaws.com/agent_multiple_agents_training_videos.zip)
- [agent_object_preference_training_videos.zip](https://nyu-datasets.s3.amazonaws.com/agent_object_preference_training_videos.zip)
- [agent_single_object_training_videos.zip](https://nyu-datasets.s3.amazonaws.com/agent_single_object_training_videos.zip)

Copyright 2022 CACI
