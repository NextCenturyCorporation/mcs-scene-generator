import logging
from dataclasses import dataclass
from typing import List, Union

from generator.agents import (
    AGENT_DIMENSIONS,
    AGENT_TYPES,
    add_agent_action,
    create_agent,
)
from generator.scene import Scene
from ideal_learning_env.defs import ILEException
from ideal_learning_env.feature_creation_service import (
    BaseFeatureConfig,
    BaseObjectCreationService,
    FeatureCreationService,
    FeatureTypes,
)
from ideal_learning_env.object_services import add_random_placement_tag

from .choosers import choose_position, choose_random
from .defs import RandomizableBool, RandomizableString
from .numerics import MinMaxInt, RandomizableInt, VectorFloatConfig

logger = logging.getLogger(__name__)


@dataclass
class AgentActionConfig():
    """Represents what animations an agent is to perform.
    - `id` (str or list of str): The ID of the animation the agent should
    perform.  Default: no deafult, must be set.
    - `step_begin` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict):
    The step in that this animation should start.
    Default: no default, must be set.
    - `step_end` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict):
    The step in that this animation should end.
    Default: unset - animation won't end until another animation changes it or
    the animation finishes.
    - `is_loop_animation` (bool or list of bool): Determines whether the
    animation should loop or end when finished.  Default: False
    """
    step_begin: RandomizableInt = None
    step_end: RandomizableInt = None
    is_loop_animation: RandomizableBool = False
    id: RandomizableString = None


@dataclass
class AgentSettings():
    # TODO copied from MCS.  See if we can use MCS version after release.
    """Describes the appearance of the agent.  Detailed information can be
    found in the MCS schema documentation.  All values Default to a random
    value in the full range of that value.
    """
    chest: RandomizableInt = 0
    chestMaterial: RandomizableInt = 0
    eyes: RandomizableInt = 0
    feet: RandomizableInt = 0
    feetMaterial: RandomizableInt = 0
    glasses: RandomizableInt = 0
    hair: RandomizableInt = 0
    hairMaterial: RandomizableInt = 0
    hatMaterial: RandomizableInt = 0
    hideHair: RandomizableBool = False
    isElder: RandomizableBool = False
    jacket: RandomizableInt = 0
    jacketMaterial: RandomizableInt = 0
    legs: RandomizableInt = 0
    legsMaterial: RandomizableInt = 0
    showBeard: RandomizableBool = False
    showGlasses: RandomizableBool = False
    showJacket: RandomizableBool = False
    showTie: RandomizableBool = False
    skin: RandomizableInt = 0
    tie: RandomizableInt = 0
    tieMaterial: RandomizableInt = 0


@dataclass
class AgentConfig(BaseFeatureConfig):
    """Represents the template for a specific object (with one or more possible
    variations) that will be added to each scene. Each template can have the
    following optional properties:
    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict): The number
    of agents with this template to generate in each scene. For a list or a
    MinMaxInt, a new number will be randomly chosen for each scene.
    Default: `1`
    - `actions` ([AgentActionConfig](#AgentActionConfig)) or list of
    ([AgentActionConfig](#AgentActionConfig)): The config for agent actions
    or animations.  Enties in a list are NOT choices.  Each entry will be kept
    and any randomness will be reconciled inside the entry.
    - `agent_settings` ([AgentSettings](#AgentSettings) or list of
    [AgentSettings](#AgentSettings)): The settings that describe how an agent
    will look. Default: random
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The position of this object in each scene. For a
    list, a new position will be randomly chosen for each scene.
    Default: random
    - `rotation_y` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict):
    The rotation of this object in each scene. For a
    list, a new rotation will be randomly chosen for each scene.
    Default: random
    - `type`: (string or list of strings) string to indicate the model of
    agent to use.  Options are: agent_female_01, agent_female_02,
    agent_female_04, agent_male_02, agent_male_03, agent_male_04.
    Default: random

    Example:
    ```
    num: 1
    type: agent_female_02
    agent_settings:
      chest: 2
      eyes: 1
    position:
      x: 3
      z: 3
    rotation_y: 90
    actions:
      id: TPE_wave
      step_begin: [3, 5]
      step_end:
        min: 8
        max: 11
      is_loop_animation: [True, False]
    ```
    """
    type: Union[str, List[str]] = None
    agent_settings: Union[AgentSettings, List[AgentSettings]] = None
    position: Union[VectorFloatConfig, List[VectorFloatConfig]] = None
    rotation_y: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    actions: List[AgentActionConfig] = None


def get_default_agent_settings():
    return AgentSettings(
        chest=MinMaxInt(0, 8),
        chestMaterial=MinMaxInt(0, 14),
        eyes=MinMaxInt(0, 3),
        feet=MinMaxInt(0, 2),
        feetMaterial=MinMaxInt(0, 11),
        glasses=MinMaxInt(0, 10),
        hair=MinMaxInt(0, 9),
        hairMaterial=MinMaxInt(0, 9),
        hatMaterial=MinMaxInt(0, 11),
        hideHair=[True, False, False, False, False],
        isElder=[True, False, False, False, False],
        jacket=0,
        jacketMaterial=0,
        legs=MinMaxInt(0, 3),
        legsMaterial=MinMaxInt(0, 14),
        showBeard=False,
        showGlasses=False,
        showJacket=False,
        showTie=[True, False],
        skin=MinMaxInt(0, 11),
        tie=MinMaxInt(0, 2),
        tieMaterial=MinMaxInt(0, 9)
    )


DEFAULT_TEMPLATE_AGENT = AgentConfig(
    num=0, type=AGENT_TYPES, agent_settings=get_default_agent_settings(),
    position=None, actions=None,
    rotation_y=MinMaxInt(0, 359))


class AgentCreationService(BaseObjectCreationService):
    bounds = []

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_AGENT
        self._type = FeatureTypes.AGENT

    def _handle_dependent_defaults(
            self, scene: Scene, template: AgentConfig,
            source_template: AgentConfig
    ) -> AgentConfig:
        # We want to retain the list of actions so we pull them from the
        # source.  Anything inside these actions will be reconciled.
        template.actions = source_template.actions
        reconciled_actions = []
        for action in template.actions or []:
            reconciled_actions.append(choose_random(action))
            template.actions = reconciled_actions
        template.position = choose_position(
            template.position,
            AGENT_DIMENSIONS['x'],
            AGENT_DIMENSIONS['z'],
            scene.room_dimensions.x,
            scene.room_dimensions.z
        )
        return template

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: AgentConfig,
            source_template: AgentConfig):
        agent = create_agent(
            type=reconciled.type,
            position_x=reconciled.position.x,
            position_z=reconciled.position.z,
            rotation_y=reconciled.rotation_y,
            settings=vars(reconciled.agent_settings),
            position_y_modifier=reconciled.position.y)
        for action in reconciled.actions or []:
            if not action.id:
                raise ILEException(
                    f'Agent action must have id, but id={action.id}')
            if (not isinstance(
                    action.step_begin, int) or action.step_begin < 0):
                raise ILEException(
                    f'Agent action must have valid step_begin, '
                    f'but step_begin={action.step_begin}')
            add_agent_action(
                agent=agent,
                action_id=action.id,
                step_begin=action.step_begin,
                step_end=action.step_end,
                is_loop=action.is_loop_animation or False)
        add_random_placement_tag(
            agent, source_template)
        return agent


FeatureCreationService.register_creation_service(
    FeatureTypes.AGENT, AgentCreationService)
