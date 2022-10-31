import glob
import json
import logging
import os
import random
from typing import Any, Callable, Dict, List

from generator import Scene, SceneException, tags

from .agent_scene_pair_json_converter import convert_scene_pair
from .hypercubes import Hypercube, HypercubeFactory

logger = logging.getLogger(__name__)


class AgentHypercube(Hypercube):
    def __init__(
        self,
        filename_prefix: str,
        starter_scene: Scene,
        task_type: str,
        role_to_type: Dict[str, str],
        training=False,
        untrained=False
    ) -> None:
        self._filename_prefix = filename_prefix
        self._role_to_type = role_to_type
        self._untrained = untrained
        super().__init__(
            task_type,
            starter_scene,
            task_type,
            training=training
        )

    # Override
    def _create_scenes(
        self,
        starter_scene: Scene,
        goal_template: Dict[str, Any]
    ) -> List[Scene]:
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
                logger.info(
                    f'Reading {category} agent scene JSON file: '
                    f'{json_filename[category]}'
                )
                json_data[category] = json.load(json_file)

        # Create the pair of MCS scenes from the JSON data, which should be a
        # list of trials that each have a list of frames.
        scenes = convert_scene_pair(
            starter_scene,
            goal_template,
            json_data['expected'],
            json_data['unexpected'],
            self._filename_prefix,
            self._role_to_type,
            self._untrained
        )

        # Remember a training hypercube will only have its expected scene.
        scenes[0].goal['sceneInfo'][tags.SCENE.ID] = [os.path.splitext(
            os.path.basename(json_filename['expected'])
        )[0]]
        if len(scenes) > 1:
            scenes[1].goal['sceneInfo'][tags.SCENE.ID] = [os.path.splitext(
                os.path.basename(json_filename['unexpected'])
            )[0]]

        return scenes

    # Override
    def _get_training_scenes(self) -> List[Scene]:
        # Each AgentHypercubeFactory will handle training flag validation.
        return self._scenes


class AgentHypercubeFactory(HypercubeFactory):
    def __init__(
        self,
        name: str,
        folder_name: str,
        task_type: str,
        training: bool
    ) -> None:
        super().__init__(name, training)
        self._folder_name = folder_name
        self._task_type = task_type
        self._untrained = False

    # Override
    def _build(self, starter_scene: Scene) -> Hypercube:
        return AgentHypercube(
            self._filename_prefix,
            starter_scene,
            self._task_type,
            self.role_to_type,
            self.training,
            # Must use only untrained shapes in 50% of scenes.
            untrained=self._untrained
        )

    # Override
    def build(
        self,
        total: str,
        starter_scene_function: Callable[[], Scene],
        role_to_type: Dict[str, str],
        throw_error=False,
        sort_data=False
    ) -> List[Hypercube]:
        # Save this now in case it's used by a hypercube factory subclass.
        self.role_to_type = role_to_type

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

        logger.info(
            f'Agent hypercube factory found {len(prefix_to_number.items())} '
            f'pairs of scene JSON files in {self._folder_name}'
        )

        # Randomize (or sort, for testing) the order of the files.
        randomized_prefix_to_number = list(prefix_to_number.items())
        if sort_data:
            randomized_prefix_to_number.sort()
        else:
            random.shuffle(randomized_prefix_to_number)

        # Generate one hypercube per valid pair of files.
        count = 0
        failed_filename_list = []
        for prefix, number in randomized_prefix_to_number:
            if (not self.training) and (number < 2):
                logger.warn(
                    f'[NOTE] Agent hypercube factory found only one scene '
                    f'JSON file in {self._folder_name} but expected two '
                    f'named {prefix + "e.json"} and {prefix + "u.json"}'
                )
                continue
            count += 1
            logger.info(f'Generating agent hypercube {count} / {total}')
            self._filename_prefix = prefix
            try:
                hypercube = self._build(starter_scene_function())
                hypercubes.append(hypercube)
                # Every other scene pair should have untrained objects.
                self._untrained = (not self._untrained)
            except (
                RuntimeError,
                ZeroDivisionError,
                TypeError,
                SceneException,
                ValueError
            ) as e:
                if throw_error:
                    raise
                logger.warn(f'[ERROR] Failed to create {self.name} hypercube')
                logger.exception(e)
                failed_filename_list.append(prefix)
            if count == total:
                break

        if count < total:
            logger.debug(
                f'[NOTE] Agent hypercube factory found only '
                f'{count} valid pairs of scene JSON files in '
                f'{self._folder_name} but {total} were required '
                f'via command line argument.'
            )

        if len(failed_filename_list) > 0:
            logger.warn('[NOTE] The following agent scene files failed:')
        for filename in failed_filename_list:
            logger.warn(f'{filename}')

        return hypercubes


class AgentInstrumentalActionTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentInstrumentalActionTraining',
            'agents_background_instrumental_action',
            tags.TYPES.AGENT_BACKGROUND_INSTRUMENTAL_ACTION,
            training=True
        )


class AgentMultipleAgentsTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentMultipleAgentsTraining',
            'agents_background_multiple_agents',
            tags.TYPES.AGENT_BACKGROUND_MULTIPLE_AGENTS,
            training=True
        )


class AgentObjectPreferenceTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentObjectPreferenceTraining',
            'agents_background_object_preference',
            tags.TYPES.AGENT_BACKGROUND_OBJECT_PREFERENCE,
            training=True
        )


class AgentSingleObjectTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentSingleObjectTraining',
            'agents_background_single_object',
            tags.TYPES.AGENT_BACKGROUND_SINGLE_OBJECT,
            training=True
        )


class AgentEfficientActionIrrationalEvaluationHypercubeFactory(
    AgentHypercubeFactory
):
    def __init__(self) -> None:
        super().__init__(
            'AgentEfficientActionIrrational',
            'agents_evaluation_efficient_action_irrational',
            tags.TYPES.AGENT_EVALUATION_EFFICIENT_IRRATIONAL,
            training=False
        )


class AgentEfficientActionPathEvaluationHypercubeFactory(
    AgentHypercubeFactory
):
    def __init__(self) -> None:
        super().__init__(
            'AgentEfficientActionPath',
            'agents_evaluation_efficient_action_path',
            tags.TYPES.AGENT_EVALUATION_EFFICIENT_PATH,
            training=False
        )


class AgentEfficientActionTimeEvaluationHypercubeFactory(
    AgentHypercubeFactory
):
    def __init__(self) -> None:
        super().__init__(
            'AgentEfficientActionTime',
            'agents_evaluation_efficient_action_time',
            tags.TYPES.AGENT_EVALUATION_EFFICIENT_TIME,
            training=False
        )


class AgentInaccessibleGoalEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentInaccessibleGoal',
            'agents_evaluation_inaccessible_goal',
            tags.TYPES.AGENT_EVALUATION_INACCESSIBLE_GOAL,
            training=False
        )


class AgentInstrumentalActionBlockingBarriersEvaluationHypercubeFactory(
    AgentHypercubeFactory
):
    def __init__(self) -> None:
        super().__init__(
            'AgentInstrumentalActionBlockingBarriers',
            'agents_evaluation_instrumental_action_blocking_barriers',
            tags.TYPES.AGENT_EVALUATION_INSTRUMENTAL_BLOCKING_BARRIERS,
            training=False
        )


class AgentInstrumentalActionInconsequentialBarriersEvaluationHypercubeFactory(
    AgentHypercubeFactory
):
    def __init__(self) -> None:
        super().__init__(
            'AgentInstrumentalActionInconsequentialBarriers',
            'agents_evaluation_instrumental_action_inconsequential_barriers',
            tags.TYPES.AGENT_EVALUATION_INSTRUMENTAL_INCONSEQUENTIAL_BARRIERS,
            training=False
        )


class AgentInstrumentalActionNoBarriersEvaluationHypercubeFactory(
    AgentHypercubeFactory
):
    def __init__(self) -> None:
        super().__init__(
            'AgentInstrumentalActionNoBarriers',
            'agents_evaluation_instrumental_action_no_barriers',
            tags.TYPES.AGENT_EVALUATION_INSTRUMENTAL_NO_BARRIERS,
            training=False
        )


class AgentMultipleAgentsEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentMultipleAgents',
            'agents_evaluation_multiple_agents',
            tags.TYPES.AGENT_EVALUATION_MULTIPLE_AGENTS,
            training=False
        )


class AgentObjectPreferenceEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentObjectPreference',
            'agents_evaluation_object_preference',
            tags.TYPES.AGENT_EVALUATION_OBJECT_PREFERENCE,
            training=False
        )


class AgentExamplesTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentExamplesTraining',
            'agents_examples',
            'agents examples',
            training=True
        )


class AgentExamplesEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentExamples',
            'agents_examples',
            'agents examples',
            training=False
        )


AGENT_TRAINING_HYPERCUBE_LIST = [
    AgentInstrumentalActionTrainingHypercubeFactory(),
    AgentMultipleAgentsTrainingHypercubeFactory(),
    AgentObjectPreferenceTrainingHypercubeFactory(),
    AgentSingleObjectTrainingHypercubeFactory(),
    AgentExamplesTrainingHypercubeFactory()
]


AGENT_EVALUATION_HYPERCUBE_LIST = [
    AgentEfficientActionIrrationalEvaluationHypercubeFactory(),
    AgentEfficientActionPathEvaluationHypercubeFactory(),
    AgentEfficientActionTimeEvaluationHypercubeFactory(),
    AgentInaccessibleGoalEvaluationHypercubeFactory(),
    AgentInstrumentalActionBlockingBarriersEvaluationHypercubeFactory(),
    AgentInstrumentalActionInconsequentialBarriersEvaluationHypercubeFactory(),
    AgentInstrumentalActionNoBarriersEvaluationHypercubeFactory(),
    AgentMultipleAgentsEvaluationHypercubeFactory(),
    AgentObjectPreferenceEvaluationHypercubeFactory(),
    AgentExamplesEvaluationHypercubeFactory()
]
