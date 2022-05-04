import copy
import logging
import random
from dataclasses import dataclass
from typing import List, Union

from machine_common_sense.config_manager import Vector3d
from shapely.geometry import Point, Polygon

from generator.agents import (
    AGENT_DIMENSIONS,
    AGENT_TYPES,
    add_agent_action,
    add_agent_movement,
    create_agent,
)
from generator.geometry import MAX_TRIES
from generator.scene import Scene
from ideal_learning_env.defs import ILEException
from ideal_learning_env.feature_creation_service import (
    BaseFeatureConfig,
    BaseObjectCreationService,
    FeatureCreationService,
    FeatureTypes,
)
from ideal_learning_env.object_services import (
    add_random_placement_tag,
    reconcile_template,
)

from .choosers import choose_position, choose_random
from .defs import RandomizableBool, RandomizableString
from .numerics import (
    MinMaxInt,
    RandomizableInt,
    RandomizableVectorFloat3d,
    VectorFloatConfig,
)

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
class AgentMovementConfig():
    """Represents what movements the agent is to perform.  If the
    'points' field is set, the 'bounds' and 'num_points' fields will
    be ignored.
    - `animation` (str or list of str): Determines animation that
    should occur while movement is happening.
    Default: 'TPM_walk' or 'TPM_run'
    - `step_begin` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict):
    The step at which this movement should start.
    - `points` (list of [VectorFloatConfig](#VectorFloatConfig)): List of
    points the agent should move to.  If this value is set, it will take
    precedence over 'bounds' and 'num_points'.  Default: Use bounds
    - `bounds` (list of [VectorFloatConfig](#VectorFloatConfig)): A set of
    points that create a polygon in which points will be generated inside.
    If there are less than 3 points, the entire room will be used.  This
    option will be ignored if 'points' is set.
    Default: Entire room
    - `num_points` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict):
    The number of points to generate inside the bounds.  Only valid if points
    is not used.  Default: random between 2 and 10 inclusive.
    - `repeat` (bool or list of bool): Determines whether the
    set of movements should loop or end when finished.
    Default: Random
    """

    animation: RandomizableString = None
    step_begin: RandomizableInt = None
    points: List[RandomizableVectorFloat3d] = None
    bounds: List[RandomizableVectorFloat3d] = None
    num_points: RandomizableInt = None
    repeat: RandomizableBool = None


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
    - `movement` ([AgentMovementConfig](#AgentMovementConfig)) or list of
    ([AgentMovementConfig](#AgentMovementConfig)): The config for agent
    movement.
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
    movement: Union[AgentMovementConfig, List[AgentMovementConfig]] = None


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
        skin=MinMaxInt(0, 3),
        tie=MinMaxInt(0, 2),
        tieMaterial=MinMaxInt(0, 9)
    )


DEFAULT_TEMPLATE_AGENT = AgentConfig(
    num=0, type=AGENT_TYPES, agent_settings=get_default_agent_settings(),
    position=None, actions=None,
    rotation_y=MinMaxInt(0, 359))

DEFAULT_TEMPLATE_AGENT_MOVEMENT = AgentMovementConfig(
    animation=['TPM_walk', 'TPM_run'], step_begin=MinMaxInt(0, 20),
    num_points=MinMaxInt(2, 10), repeat=[True, False]
)


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
        template.actions = copy.deepcopy(source_template.actions)
        reconciled_actions = [choose_random(action)
                              for action in template.actions or []]
        if template.movement:
            template.movement = reconcile_template(
                DEFAULT_TEMPLATE_AGENT_MOVEMENT, template.movement)
            if template.movement.bounds:
                template.movement.bounds = copy.deepcopy(
                    source_template.movement.bounds)
                reconciled_bounds = [
                    choose_random(bound) for bound in
                    template.movement.bounds or []]
                template.movement.bounds = reconciled_bounds
            if template.movement.points:
                template.movement.points = copy.deepcopy(
                    source_template.movement.points)
                reconciled_points = [
                    choose_random(point) for point in
                    template.movement.points or []]
                template.movement.points = reconciled_points
        template.actions = reconciled_actions

        template.position = choose_position(
            template.position,
            AGENT_DIMENSIONS['x'],
            AGENT_DIMENSIONS['z'],
            scene.room_dimensions.x,
            scene.room_dimensions.y,
            scene.room_dimensions.z
        )
        return template

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: AgentConfig,
            source_template: AgentConfig):
        logger.trace(f"Creating agent:\n{source_template=}\n{reconciled=}")
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
        if reconciled.movement:
            movement = reconciled.movement
            if movement.points:
                points = [(p.x, p.z) for p in movement.points]
                add_agent_movement(
                    agent,
                    movement.step_begin,
                    points,
                    movement.animation,
                    movement.repeat)
            else:
                AgentCreationService.add_random_agent_movement(
                    scene, agent, movement)
        add_random_placement_tag(
            agent, source_template)
        return agent

    @staticmethod
    def add_random_agent_movement(
            scene: Scene, agent: dict, config: AgentMovementConfig):
        logger.trace(f"Adding random agent movement:\n{config=}")
        def_temp: AgentMovementConfig = choose_random(
            DEFAULT_TEMPLATE_AGENT_MOVEMENT)
        x_limit = scene.room_dimensions.x / 2.0
        z_limit = scene.room_dimensions.z / 2.0
        bounds = config.bounds
        repeat = (config.repeat if config.repeat is not None else
                  def_temp.repeat)
        # Allow users to provide 0 points for a choice which will skip adding
        # this movement.
        if config.num_points is not None and config.num_points < 1:
            return

        num_points = (config.num_points or def_temp.num_points)
        step_begin = (
            config.step_begin if config.step_begin is not None
            else def_temp.step_begin)

        if not bounds:
            bounds = [Vector3d(x=-x_limit, y=0, z=-z_limit),
                      Vector3d(x=x_limit, y=0, z=-z_limit),
                      Vector3d(x=x_limit, y=0, z=z_limit),
                      Vector3d(x=-x_limit, y=0, z=z_limit)]
        if len(bounds) in {1, 2}:
            return

        x_min = x_limit
        x_max = -x_limit
        z_min = z_limit
        z_max = -z_limit
        for point in bounds:
            x_min = min(point.x, x_min)
            x_max = max(point.x, x_max)
            z_min = min(point.z, z_min)
            z_max = max(point.z, z_max)

        poly = Polygon([[p.x, p.z] for p in bounds])

        waypoints = []
        animation = config.animation or def_temp.animation
        start_pos = agent['shows'][0]['position']
        previous_position = (start_pos['x'], start_pos['z'])
        for _ in range(num_points):
            # maybe we only want walk?
            waypoint = False
            for _ in range(MAX_TRIES):
                x = random.uniform(x_min, x_max)
                z = random.uniform(z_min, z_max)
                pos = (x, z)
                if Point(x, z).within(poly) and previous_position != pos:
                    waypoints.append(pos)
                    waypoint = True
                    previous_position = pos
                    break
            if not waypoint:
                raise ILEException(
                    "Failed to generate path inside bounds for "
                    "agent.  Try increasing bounds.")
        logger.trace(
            f"Agent movement: {agent['id']=} {animation=} {repeat=} "
            f"{step_begin=} {waypoints=}"
        )
        add_agent_movement(agent, step_begin, waypoints, animation, repeat)


FeatureCreationService.register_creation_service(
    FeatureTypes.AGENT, AgentCreationService)
