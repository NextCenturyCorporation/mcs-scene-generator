import copy
import glob
import json
import random
import os
from typing import Any, Callable, Dict, List

from agent_scene_pair_json_converter import EXPECTED, UNEXPECTED, \
    convert_scene_pair
import exceptions
import hypercubes
import tags


AGENT_GOAL_TEMPLATE = {
    'category': tags.tag_to_label(tags.SCENE.AGENTS),
    'description': '',
    'domainsInfo': {
        'agents': [
            tags.DOMAINS.AGENTS_2,
            tags.DOMAINS.AGENTS_3,
            tags.DOMAINS.AGENTS_7
        ],
        'objects': [],
        'places': []
    },
    'sceneInfo': {},
    'metadata': {
        'choose': [EXPECTED, UNEXPECTED]
    }
}

AGENT_GOAL_TEMPLATE['sceneInfo'][tags.SCENE.PRIMARY] = (
    tags.tag_to_label(tags.SCENE.PASSIVE)
)
AGENT_GOAL_TEMPLATE['sceneInfo'][tags.SCENE.SECONDARY] = (
    tags.tag_to_label(tags.SCENE.AGENTS)
)
AGENT_GOAL_TEMPLATE['sceneInfo'][tags.SCENE.QUATERNARY] = (
    tags.tag_to_label(tags.SCENE.ACTION_NONE)
)


class AgentHypercube(hypercubes.Hypercube):
    def __init__(
        self,
        filename_prefix: str,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any],
        role_to_type: Dict[str, str],
        training=False,
        untrained=False
    ) -> None:
        self._filename_prefix = filename_prefix
        self._role_to_type = role_to_type
        self._untrained = untrained
        super().__init__(
            goal_template['sceneInfo'][tags.SCENE.TERTIARY],
            body_template,
            goal_template,
            training=training
        )

    # Override
    def _create_scenes(
        self,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Each JSON filename will have a suffix of either 'e.json' or 'u.json'
        json_filename = {
            'expected': self._filename_prefix + 'e.json',
            'unexpected': self._filename_prefix + 'u.json'
        }

        json_data = {
            'expected': None,
            'unexpected': None
        }

        category_list = ['expected']
        if not self._training:
            category_list.append('unexpected')

        for category in category_list:
            # Ensure the JSON scene file exists.
            if not os.path.exists(json_filename[category]):
                raise ValueError(f'Agent hypercube cannot find {category} '
                                 f'scene JSON file: {json_filename[category]}')

            # Read the data from the JSON scene file.
            with open(json_filename[category]) as json_file:
                print(f'Reading {category} agent scene JSON file: '
                      f'{json_filename[category]}')
                json_data[category] = json.load(json_file)

        # Create the pair of MCS scenes from the JSON data, which should be a
        # list of trials that each have a list of frames.
        scenes = convert_scene_pair(
            body_template,
            goal_template,
            json_data['expected'],
            json_data['unexpected'],
            self._filename_prefix,
            self._role_to_type,
            self._untrained
        )

        # Remember a training hypercube will only have its expected scene.
        scenes[0]['goal']['sceneInfo'][tags.SCENE.ID] = [os.path.splitext(
            os.path.basename(json_filename['expected'])
        )[0]]
        if len(scenes) > 1:
            scenes[1]['goal']['sceneInfo'][tags.SCENE.ID] = [os.path.splitext(
                os.path.basename(json_filename['unexpected'])
            )[0]]

        return scenes

    # Override
    def _get_training_scenes(self) -> List[Dict[str, Any]]:
        # Each AgentHypercubeFactory will handle training flag validation.
        return self._scenes


class AgentHypercubeFactory(hypercubes.HypercubeFactory):
    def __init__(
        self,
        name: str,
        folder_name: str,
        goal_template: str,
        training: bool
    ) -> None:
        super().__init__(name, training)
        self._folder_name = folder_name
        self._goal_template = goal_template
        self._untrained = False

    # Override
    def _build(self, body_template: Dict[str, Any]) -> hypercubes.Hypercube:
        return AgentHypercube(
            self._filename_prefix,
            body_template,
            self._goal_template,
            self.training,
            # Must use only untrained shapes in 50% of scenes.
            untrained=self._untrained
        )

    # Override
    def build(
        self,
        total: str,
        body_template_function: Callable[[], Dict[str, Any]],
        throw_error=False
    ) -> List[hypercubes.Hypercube]:
        # Return one hypercube per pair of expected/unexpected JSON scene files
        # in the folder associated with this factory, or up to the given total.
        hypercubes = []

        prefix_to_number = {}
        # Each JSON filename will have a suffix of either 'e.json' or 'u.json'
        for suffix in ['e.json', 'u.json']:
            for json_filename in glob.glob(self._folder_name + '/*' + suffix):
                # Remove the filename suffix.
                prefix_to_number[json_filename[:-6]] = (
                    prefix_to_number.get(json_filename[:-6], 0) + 1
                )

        print(f'Agent hypercube factory found {len(prefix_to_number.items())} '
              f'pairs of scene JSON files in {self._folder_name}')

        # Randomize the order of the files.
        randomized_prefix_to_number = list(prefix_to_number.items())
        random.shuffle(randomized_prefix_to_number)

        # Generate one hypercube per valid pair of files.
        count = 0
        failed_filename_list = []
        for prefix, number in randomized_prefix_to_number:
            if (not self.training) and (number < 2):
                print(f'[NOTE] Agent hypercube factory found only one scene '
                      f'JSON file in {self._folder_name} but expected two '
                      f'named {prefix + "e.json"} and {prefix + "u.json"}')
                continue
            count += 1
            print(f'Generating agent hypercube {count} / {total}')
            self._filename_prefix = prefix
            try:
                hypercube = self._build(body_template_function())
                hypercubes.append(hypercube)
                # Every other scene pair should have untrained objects.
                self._untrained = (not self._untrained)
            except (
                RuntimeError,
                ZeroDivisionError,
                TypeError,
                exceptions.SceneException,
                ValueError
            ) as e:
                if throw_error:
                    raise
                print(f'[ERROR] Failed to create {self.name} hypercube')
                print(e)
                failed_filename_list.append(prefix)
            if count == total:
                break

        if count < total:
            print(f'[NOTE] Agent hypercube factory found only '
                  f'{count} valid pairs of scene JSON files in '
                  f'{self._folder_name} but {total} were required '
                  f'via command line argument.')

        if len(failed_filename_list) > 0:
            print('[NOTE] The following agent scene files failed:')
        for filename in failed_filename_list:
            print(f'{filename}')

        return hypercubes


class AgentSingleObjectTrainingHypercubeFactory(AgentHypercubeFactory):
    GOAL_TEMPLATE = copy.deepcopy(AGENT_GOAL_TEMPLATE)
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.TERTIARY] = (
        tags.TYPES.AGENT_BACKGROUND_SINGLE_OBJECT
    )

    def __init__(self) -> None:
        super().__init__(
            'AgentSingleObjectTraining',
            'agents_background_single_object',
            self.GOAL_TEMPLATE,
            training=True
        )


class AgentObjectPreferenceTrainingHypercubeFactory(AgentHypercubeFactory):
    GOAL_TEMPLATE = copy.deepcopy(AGENT_GOAL_TEMPLATE)
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.TERTIARY] = (
        tags.TYPES.AGENT_BACKGROUND_OBJECT_PREFERENCE
    )

    def __init__(self) -> None:
        super().__init__(
            'AgentObjectPreferenceTraining',
            'agents_background_object_preference',
            self.GOAL_TEMPLATE,
            training=True
        )


class AgentObjectPreferenceEvaluationHypercubeFactory(AgentHypercubeFactory):
    GOAL_TEMPLATE = copy.deepcopy(AGENT_GOAL_TEMPLATE)
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.TERTIARY] = (
        tags.TYPES.AGENT_EVALUATION_OBJECT_PREFERENCE
    )

    def __init__(self) -> None:
        super().__init__(
            'AgentObjectPreferenceEvaluation',
            'agents_evaluation_object_preference',
            self.GOAL_TEMPLATE,
            training=False
        )


class AgentEfficientActionAEvaluationHypercubeFactory(AgentHypercubeFactory):
    GOAL_TEMPLATE = copy.deepcopy(AGENT_GOAL_TEMPLATE)
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.TERTIARY] = (
        tags.TYPES.AGENT_EVALUATION_EFFICIENT_ACTION_A
    )

    def __init__(self) -> None:
        super().__init__(
            'AgentEfficientActionAEvaluation',
            'agents_evaluation_efficient_action_a',
            self.GOAL_TEMPLATE,
            training=False
        )


class AgentEfficientActionBEvaluationHypercubeFactory(AgentHypercubeFactory):
    GOAL_TEMPLATE = copy.deepcopy(AGENT_GOAL_TEMPLATE)
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.TERTIARY] = (
        tags.TYPES.AGENT_EVALUATION_EFFICIENT_ACTION_B
    )

    def __init__(self) -> None:
        super().__init__(
            'AgentEfficientActionBEvaluation',
            'agents_evaluation_efficient_action_b',
            self.GOAL_TEMPLATE,
            training=False
        )


class AgentExamplesTrainingHypercubeFactory(AgentHypercubeFactory):
    GOAL_TEMPLATE = copy.deepcopy(AGENT_GOAL_TEMPLATE)
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.TERTIARY] = 'agents examples'

    def __init__(self) -> None:
        super().__init__(
            'AgentExamplesTraining',
            'agents_examples',
            self.GOAL_TEMPLATE,
            training=True
        )


class AgentExamplesEvaluationHypercubeFactory(AgentHypercubeFactory):
    GOAL_TEMPLATE = copy.deepcopy(AGENT_GOAL_TEMPLATE)
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.TERTIARY] = 'agents examples'

    def __init__(self) -> None:
        super().__init__(
            'AgentExamplesEvaluation',
            'agents_examples',
            self.GOAL_TEMPLATE,
            training=False
        )


AGENT_TRAINING_HYPERCUBE_LIST = [
    AgentSingleObjectTrainingHypercubeFactory(),
    AgentObjectPreferenceTrainingHypercubeFactory(),
    AgentEfficientActionAEvaluationHypercubeFactory(),
    AgentEfficientActionBEvaluationHypercubeFactory(),
    AgentObjectPreferenceEvaluationHypercubeFactory(),
    AgentExamplesTrainingHypercubeFactory()
]


AGENT_EVALUATION_HYPERCUBE_LIST = [
    AgentSingleObjectTrainingHypercubeFactory(),
    AgentObjectPreferenceTrainingHypercubeFactory(),
    AgentEfficientActionAEvaluationHypercubeFactory(),
    AgentEfficientActionBEvaluationHypercubeFactory(),
    AgentObjectPreferenceEvaluationHypercubeFactory(),
    AgentExamplesEvaluationHypercubeFactory()
]
