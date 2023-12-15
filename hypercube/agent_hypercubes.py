import glob
import json
import logging
import os
import random
from typing import Callable, Dict, List

from machine_common_sense.config_manager import Goal

from generator import Scene, tags

from .agent_scene_pair_json_converter import OccluderMode, convert_scene_pair
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
        untrained=False,
        toggle=False,
        occluder_mode=None
    ) -> None:
        self._filename_prefix = filename_prefix
        self._role_to_type = role_to_type
        self._untrained = untrained
        self._toggle = toggle
        self._occluder_mode = occluder_mode
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
        goal_template: Goal
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
            self._untrained,
            toggle=self._toggle,
            occluder_mode=self._occluder_mode
        )

        # Remember a training hypercube will only have its expected scene.
        scenes[0].goal.scene_info[tags.SCENE.ID] = [os.path.splitext(
            os.path.basename(json_filename['expected'])
        )[0]]
        if len(scenes) > 1:
            scenes[1].goal.scene_info[tags.SCENE.ID] = [os.path.splitext(
                os.path.basename(json_filename['unexpected'])
            )[0]]

        return scenes

    # Override
    def get_info(self) -> str:
        """Return unique hypercube info. Can override as needed."""
        return self._filename_prefix

    # Override
    def _get_slices(self) -> List[str]:
        """Return all of this hypercube's slices (string tags)."""
        return []

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
        self._toggle = 0
        self._occluder_mode = OccluderMode.NONE

    # Override
    def _build(self, starter_scene: Scene) -> Hypercube:
        return AgentHypercube(
            self._filename_prefix,
            starter_scene,
            self._task_type,
            self.role_to_type,
            self.training,
            # Must use only untrained shapes in 50% of scenes.
            untrained=self._untrained,
            # Toggle to vary the room setup every 2 scenes in some tasks.
            toggle=(self._toggle % 4 in [0, 1]),
            # For the agent/non-agent scenes.
            occluder_mode=self._occluder_mode
        )

    # Override
    def generate_hypercubes(
        self,
        total: int,
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

        if self.training:
            logger.info(
                'Agent hypercube factory set to generate training scenes; '
                'only "expected" JSON scene files are required (ending with '
                '"e.json")'
            )
        else:
            logger.info(
                'Agent hypercube factory set to generate evaluation scenes; '
                'both "expected" and "unexpected" JSON scene files are '
                'required (ending with "e.json" or "u.json" respectively)'
            )

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
            f'sets of scene JSON files in {self._folder_name}'
        )

        # Randomize (or sort, for testing) the order of the files.
        randomized_prefix_to_number = list(prefix_to_number.items())
        if sort_data:
            randomized_prefix_to_number.sort()
        else:
            random.shuffle(randomized_prefix_to_number)

        # Generate one hypercube per valid pair of files.
        count = 0
        for prefix, number in randomized_prefix_to_number:
            if (not self.training) and (number < 2):
                logger.warn(
                    f'Agent hypercube factory found only one scene '
                    f'JSON file in {self._folder_name} but expected two '
                    f'named {prefix + "e.json"} and {prefix + "u.json"}'
                )
                continue
            count += 1
            self._filename_prefix = prefix
            hypercube = self._build(starter_scene_function())
            hypercubes.append(hypercube)
            # Every other scene pair should have untrained objects.
            self._untrained = (not self._untrained)
            # Half of the scene pairs for some tasks will have a different
            # room setup.
            self._toggle = int(self._toggle + 1)
            if count % 100 == 0:
                logger.info(
                    f'Finished initialization of {count} / '
                    f'{len(randomized_prefix_to_number)} '
                    f'{self._task_type} hypercubes...'
                )

        if count < total:
            logger.info(
                f'Agent hypercube factory found only '
                f'{count} valid pairs of scene JSON files in '
                f'{self._folder_name} but {total} were required '
                f'via command line argument.'
            )
        if count > total:
            logger.info(
                f'Agent hypercube factory found {count} valid pairs of scene '
                f'JSON files in {self._folder_name} but only {total} were '
                f'required via command line argument; extra scenes will only '
                f'be used if other scenes fail.'
            )

        return hypercubes


class InstrumentalActionTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentInstrumentalActionTraining',
            'agents_background_instrumental_action',
            tags.TASKS.AGENT_BACKGROUND_INSTRUMENTAL_ACTION,
            training=True
        )


class MultipleAgentsTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentMultipleAgentsTraining',
            'agents_background_multiple_agents',
            tags.TASKS.AGENT_BACKGROUND_MULTIPLE_AGENTS,
            training=True
        )


class ObjectPreferenceTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentObjectPreferenceTraining',
            'agents_background_object_preference',
            tags.TASKS.AGENT_BACKGROUND_OBJECT_PREFERENCE,
            training=True
        )


class SingleObjectTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentSingleObjectTraining',
            'agents_background_single_object',
            tags.TASKS.AGENT_BACKGROUND_SINGLE_OBJECT,
            training=True
        )


class EfficientActionIrrationalEvaluationHypercubeFactory(
    AgentHypercubeFactory
):
    def __init__(self) -> None:
        super().__init__(
            'AgentEfficientActionIrrational',
            'agents_evaluation_efficient_action_irrational',
            tags.TASKS.AGENT_EVALUATION_EFFICIENT_IRRATIONAL,
            training=False
        )


class EfficientActionPathEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentEfficientActionPath',
            'agents_evaluation_efficient_action_path',
            tags.TASKS.AGENT_EVALUATION_EFFICIENT_PATH,
            training=False
        )


class EfficientActionTimeEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentEfficientActionTime',
            'agents_evaluation_efficient_action_time',
            tags.TASKS.AGENT_EVALUATION_EFFICIENT_TIME,
            training=False
        )


class HelperHindererEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentHelperHinderer',
            'agents_evaluation_helper_hinderer',
            tags.TASKS.AGENT_EVALUATION_HELPER_HINDERER,
            training=False
        )
        self._occluder_mode = OccluderMode.HELPER_HINDERER


class InaccessibleGoalEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentInaccessibleGoal',
            'agents_evaluation_inaccessible_goal',
            tags.TASKS.AGENT_EVALUATION_INACCESSIBLE_GOAL,
            training=False
        )


class InstrumentalActionBlockingBarriersEvaluationHypercubeFactory(
    AgentHypercubeFactory
):
    def __init__(self) -> None:
        super().__init__(
            'AgentInstrumentalActionBlockingBarriers',
            'agents_evaluation_instrumental_action_blocking_barriers',
            tags.TASKS.AGENT_EVALUATION_INSTRUMENTAL_BLOCKING_BARRIERS,
            training=False
        )


class InstrumentalActionInconsequentialBarriersEvaluationHypercubeFactory(
    AgentHypercubeFactory
):
    def __init__(self) -> None:
        super().__init__(
            'AgentInstrumentalActionInconsequentialBarriers',
            'agents_evaluation_instrumental_action_inconsequential_barriers',
            tags.TASKS.AGENT_EVALUATION_INSTRUMENTAL_INCONSEQUENTIAL_BARRIERS,
            training=False
        )


class InstrumentalActionNoBarriersEvaluationHypercubeFactory(
    AgentHypercubeFactory
):
    def __init__(self) -> None:
        super().__init__(
            'AgentInstrumentalActionNoBarriers',
            'agents_evaluation_instrumental_action_no_barriers',
            tags.TASKS.AGENT_EVALUATION_INSTRUMENTAL_NO_BARRIERS,
            training=False
        )


class MultipleAgentsEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentMultipleAgents',
            'agents_evaluation_multiple_agents',
            tags.TASKS.AGENT_EVALUATION_MULTIPLE_AGENTS,
            training=False
        )


class ObjectPreferenceEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentObjectPreference',
            'agents_evaluation_object_preference',
            tags.TASKS.AGENT_EVALUATION_OBJECT_PREFERENCE,
            training=False
        )


class TrueFalseBeliefEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentTrueFalseBelief',
            'agents_evaluation_true_false_belief',
            tags.TASKS.AGENT_EVALUATION_TRUE_FALSE_BELIEF,
            training=False
        )
        self._occluder_mode = OccluderMode.TRUE_FALSE_BELIEF


class ExamplesTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentExamplesTraining',
            'agents_examples',
            tags.TASKS.AGENT_EXAMPLE,
            training=True
        )


class ExamplesEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentExamples',
            'agents_examples',
            tags.TASKS.AGENT_EXAMPLE,
            training=False
        )


class AgentOneGoalTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentOneGoal',
            'agents_background_agent_one_goal',
            tags.TASKS.AGENT_BACKGROUND_AGENT_ONE_GOAL,
            training=True
        )
        self._occluder_mode = OccluderMode.NONAGENT_TRAINING


class AgentPreferenceTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentPreference',
            'agents_background_agent_preference',
            tags.TASKS.AGENT_BACKGROUND_AGENT_PREFERENCE,
            training=True
        )
        self._occluder_mode = OccluderMode.NONAGENT_TRAINING


class CollectTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentCollect',
            'agents_background_collect',
            tags.TASKS.AGENT_BACKGROUND_COLLECT,
            training=True
        )


class HelperHindererTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentHelperHindererTraining',
            'agents_background_helper_hinderer',
            tags.TASKS.AGENT_BACKGROUND_HELPER_HINDERER,
            training=True
        )
        self._occluder_mode = OccluderMode.HELPER_HINDERER


class InstrumentalApproachTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentInstrumentalApproach',
            'agents_background_instrumental_approach',
            tags.TASKS.AGENT_BACKGROUND_INSTRUMENTAL_APPROACH,
            training=True
        )


class InstrumentalImitationTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentInstrumentalImitation',
            'agents_background_instrumental_imitation',
            tags.TASKS.AGENT_BACKGROUND_INSTRUMENTAL_IMITATION,
            training=True
        )


class NonAgentEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentNonAgent',
            'agents_evaluation_non_agent',
            tags.TASKS.AGENT_EVALUATION_AGENT_NON_AGENT,
            training=False
        )
        self._occluder_mode = OccluderMode.NONAGENT_EVAL


class NonAgentOneGoalTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentNonAgentOneGoal',
            'agents_background_non_agent_one_goal',
            tags.TASKS.AGENT_BACKGROUND_NON_AGENT_ONE_GOAL,
            training=True
        )
        self._occluder_mode = OccluderMode.NONAGENT_TRAINING


class NonAgentPreferenceTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentNonAgentPreference',
            'agents_background_non_agent_preference',
            tags.TASKS.AGENT_BACKGROUND_NON_AGENT_PREFERENCE,
            training=True
        )
        self._occluder_mode = OccluderMode.NONAGENT_TRAINING


class SocialApproachEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentApproach',
            'agents_evaluation_approach',
            tags.TASKS.AGENT_EVALUATION_APPROACH,
            training=False
        )


class SocialApproachTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentSocialApproach',
            'agents_background_social_approach',
            tags.TASKS.AGENT_BACKGROUND_SOCIAL_APPROACH,
            training=True
        )


class SocialImitationEvaluationHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentImitation',
            'agents_evaluation_imitation',
            tags.TASKS.AGENT_EVALUATION_IMITATION,
            training=False
        )


class SocialImitationTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentSocialImitation',
            'agents_background_social_imitation',
            tags.TASKS.AGENT_BACKGROUND_SOCIAL_IMITATION,
            training=True
        )


class TrueFalseBeliefTrainingHypercubeFactory(AgentHypercubeFactory):
    def __init__(self) -> None:
        super().__init__(
            'AgentTrueFalseBeliefTraining',
            'agents_background_true_false_belief',
            tags.TASKS.AGENT_BACKGROUND_TRUE_FALSE_BELIEF,
            training=True
        )
        self._occluder_mode = OccluderMode.TRUE_FALSE_BELIEF


AGENT_TRAINING_HYPERCUBE_LIST = [
    AgentOneGoalTrainingHypercubeFactory(),
    AgentPreferenceTrainingHypercubeFactory(),
    CollectTrainingHypercubeFactory(),
    HelperHindererTrainingHypercubeFactory(),
    InstrumentalActionTrainingHypercubeFactory(),
    InstrumentalApproachTrainingHypercubeFactory(),
    InstrumentalImitationTrainingHypercubeFactory(),
    MultipleAgentsTrainingHypercubeFactory(),
    NonAgentOneGoalTrainingHypercubeFactory(),
    NonAgentPreferenceTrainingHypercubeFactory(),
    ObjectPreferenceTrainingHypercubeFactory(),
    SingleObjectTrainingHypercubeFactory(),
    SocialApproachTrainingHypercubeFactory(),
    SocialImitationTrainingHypercubeFactory(),
    TrueFalseBeliefTrainingHypercubeFactory(),
    ExamplesTrainingHypercubeFactory()
]


AGENT_EVALUATION_HYPERCUBE_LIST = [
    EfficientActionIrrationalEvaluationHypercubeFactory(),
    EfficientActionPathEvaluationHypercubeFactory(),
    EfficientActionTimeEvaluationHypercubeFactory(),
    HelperHindererEvaluationHypercubeFactory(),
    InaccessibleGoalEvaluationHypercubeFactory(),
    InstrumentalActionBlockingBarriersEvaluationHypercubeFactory(),
    InstrumentalActionInconsequentialBarriersEvaluationHypercubeFactory(),
    InstrumentalActionNoBarriersEvaluationHypercubeFactory(),
    MultipleAgentsEvaluationHypercubeFactory(),
    NonAgentEvaluationHypercubeFactory(),
    ObjectPreferenceEvaluationHypercubeFactory(),
    SocialApproachEvaluationHypercubeFactory(),
    SocialImitationEvaluationHypercubeFactory(),
    TrueFalseBeliefEvaluationHypercubeFactory(),
    ExamplesEvaluationHypercubeFactory()
]
