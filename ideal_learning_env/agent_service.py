import copy
import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from machine_common_sense.config_manager import Vector3d
from shapely.geometry import Point, Polygon

from generator import SceneObject
from generator.agents import (
    AGENT_DIMENSIONS,
    AGENT_TYPES,
    add_agent_action,
    add_agent_movement,
    add_agent_pointing,
    create_agent,
    estimate_move_step_length,
    get_random_agent_settings
)
from generator.geometry import (
    MAX_TRIES,
    calculate_rotations,
    create_bounds,
    move_to_location,
    validate_location_rect
)
from generator.scene import Scene

from .choosers import choose_position, choose_random
from .defs import (
    ILEConfigurationException,
    ILEDelayException,
    ILEException,
    RandomizableBool,
    RandomizableString,
    find_bounds
)
from .feature_creation_service import (
    BaseFeatureConfig,
    BaseObjectCreationService,
    FeatureCreationService,
    FeatureTypes
)
from .interactable_object_service import KeywordLocationConfig
from .numerics import (
    MinMaxFloat,
    MinMaxInt,
    RandomizableFloat,
    RandomizableInt,
    RandomizableVectorFloat3d
)
from .object_services import (
    KeywordLocation,
    ObjectRepository,
    add_random_placement_tag,
    reconcile_template
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
    `points` field is set, the `bounds` and `num_points` fields will
    be ignored.
    - `animation` (str, or list of str): The animation that will be shown while
    the agent moves. Default: 'TPM_walk' or 'TPM_run'
    - `bounds` (list of [VectorFloatConfig](#VectorFloatConfig) dicts): A set
    of points that create a polygon, inside of which the movement `points` will
    be chosen randomly. If `bounds` has fewer than 3 points, then the entire
    room is used as the bounds. This option is ignored if `points` is
    configured. Default: Entire room
    - `num_points` (int, or [MinMaxInt](#MinMaxInt) dict, or list of ints
    and/or MinMaxInt dicts): The number of random movement points to generate
    inside of the `bounds`. This option is ignored if `points` is set.
    Default: between 2 and 10, inclusive.
    - `points` (list of [VectorFloatConfig](#VectorFloatConfig)): The list of
    points to which the agent should move. If set, `points` takes precedence
    over `bounds` and `num_points`. Default: Use `bounds`
    - `repeat` (bool or list of bool): Whether the agent's movement pattern
    should loop indefinitely (`true`) or end when finished (`false`).
    Default: random
    - `step_begin` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict):
    The step at which this movement should start. Required.
    """
    animation: RandomizableString = None
    step_begin: RandomizableInt = None
    points: List[RandomizableVectorFloat3d] = None
    bounds: List[RandomizableVectorFloat3d] = None
    num_points: RandomizableInt = None
    repeat: RandomizableBool = None


@dataclass
class AgentPointingConfig():
    """Represents the agent pointing.
    - `object_label` (string, or list of strings): The label of the object in
    the scene at which to point. Default: The agent points in whatever
    direction it's facing (based on its `rotation_y` setting).
    The step in which the pointing should start. Default: 1
    - `step_begin` (int, or [MinMaxInt](#MinMaxInt) dict, or list of ints
    and/or MinMaxInt dicts): The step on which the pointing should start.
    The agent will idle up to this step. If `walk_distance` is set, then the
    movement will begin on this step, and the pointing will happen immediately
    after the movement. Default: 1
    `walk_distance` (float, or [MinMaxFloat](#MinMaxFloat) dict, or list of
    floats and/or MinMaxFloat dict): If set, adjusts the agent's starting
    position (which can still be set normally using the `position` option) by
    the configured distance in the direction away from the object corresponding
    to `object_label`; the agent will then turn around, walk two times the
    configured distance, and then point at the object. Will override
    `step_begin` to be after the movement ends. Use the `step_begin` option to
    configure when the movement should begin. Default: no movement
    """
    object_label: RandomizableString = None
    step_begin: RandomizableInt = None
    walk_distance: RandomizableFloat = None


@dataclass
class AgentSettings():
    # TODO copied from MCS.  See if we can use MCS version after release.
    """Describes the appearance of the agent. Each property defaults to a
    random valid setting. Please see the sections in our [schema doc](
    https://nextcenturycorporation.github.io/MCS/schema.html#agent-settings)
    for the available options.
    - `chest` (int, or list of ints)
    - `chestMaterial` (int, or list of ints)
    - `eyes` (int, or list of ints)
    - `feet` (int, or list of ints)
    - `feetMaterial` (int, or list of ints)
    - `glasses` (int, or list of ints)
    - `hair` (int, or list of ints)
    - `hairMaterial` (int, or list of ints)
    - `hatMaterial` (int, or list of ints)
    - `hideHair` (bool, or list of bools)
    - `isElder` (bool, or list of bools)
    - `jacket` (int, or list of ints)
    - `jacketMaterial` (int, or list of ints)
    - `legs` (int, or list of ints)
    - `legsMaterial` (int, or list of ints)
    - `showBeard` (bool, or list of bools)
    - `showGlasses` (bool, or list of bools)
    - `showJacket` (bool, or list of bools)
    - `showTie` (bool, or list of bools)
    - `skin` (int, or list of ints)
    - `tie` (int, or list of ints)
    - `tieMaterial` (int, or list of ints)
    """
    # All default values should be None!
    chest: RandomizableInt = None
    chestMaterial: RandomizableInt = None
    eyes: RandomizableInt = None
    feet: RandomizableInt = None
    feetMaterial: RandomizableInt = None
    glasses: RandomizableInt = None
    hair: RandomizableInt = None
    hairMaterial: RandomizableInt = None
    hatMaterial: RandomizableInt = None
    hideHair: RandomizableBool = None
    isElder: RandomizableBool = None
    jacket: RandomizableInt = None
    jacketMaterial: RandomizableInt = None
    legs: RandomizableInt = None
    legsMaterial: RandomizableInt = None
    showBeard: RandomizableBool = None
    showGlasses: RandomizableBool = None
    showJacket: RandomizableBool = None
    showTie: RandomizableBool = None
    skin: RandomizableInt = None
    tie: RandomizableInt = None
    tieMaterial: RandomizableInt = None


@dataclass
class AgentConfig(BaseFeatureConfig):
    """Represents the template for a specific agent (with one or more possible
    variations) that will be added to each scene. Each template can have the
    following optional properties:
    - `num` (int, or [MinMaxInt](#MinMaxInt) dict, or list of ints and/or
    MinMaxInt dicts): The number of agents with this template to generate in
    each scene. For a list or a MinMaxInt, a new number will be randomly chosen
    for each scene. Default: `1`
    - `actions` ([AgentActionConfig](#AgentActionConfig)) dict, or list of
    AgentActionConfig dicts): Configures the agent's actions (a.k.a.
    animations). If configured as a list, each action will be applied, and any
    randomness will be reconciled within each array element for each scene.
    Default: idle
    - `agent_settings` ([AgentSettings](#AgentSettings) dict, or list of
    AgentSettings dicts): Configures the agent's appearance. Default: random
    - `keyword_location` ([KeywordLocationConfig](#KeywordLocationConfig)
    dict): A keyword location for this agent.
    - `movement` (bool, or [AgentMovementConfig](#AgentMovementConfig)) dict,
    or list of bools and/or AgentMovementConfig dicts): Configures this agent
    to move (walk/run) around the room. If `true`, the agent will be assigned
    a random movement pattern for each scene. If configured as a list, one
    option will be randomly chosen for each scene. Default: no movement
    - `pointing` ([AgentPointingConfig](#AgentPointingConfig) dict, or list of
    AgentPointingConfig dicts): Configures this agent to start pointing on a
    specific step. The pointing lasts indefinitely. This cancels out any other
    actions or movement. Use `pointing.object_label` to point at a specific
    object. Use `pointing.walk_distance` to turn around and walk toward the
    object before pointing at it. If configured as a list, one option will be
    randomly chosen for each scene. Default: no pointing
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The position of this agent in each scene. If
    configured as a list, a new position will be randomly chosen for each
    scene. Default: random
    - `rotation_y` (float, or [MinMaxFloat](#MinMaxFloat) dict, or list of
    floats and/or MinMaxFloat dicts): The rotation of this agent in each scene.
    If configured as a list, a new rotation will be randomly chosen for each
    scene. Default: random
    - `type` (string, or list of strings) The model ("type") of the agent.
    Please see the list in our [schema doc](
    https://nextcenturycorporation.github.io/MCS/schema.html#agents) for all
    available options. Default: random

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
    type: RandomizableString = None
    agent_settings: Union[AgentSettings, List[AgentSettings]] = None
    position: RandomizableVectorFloat3d = None
    rotation_y: RandomizableFloat = None
    actions: List[AgentActionConfig] = None
    movement: Union[
        bool,
        AgentMovementConfig,
        List[Union[bool, AgentMovementConfig]]
    ] = None
    keyword_location: KeywordLocationConfig = None
    pointing: Union[AgentPointingConfig, List[AgentPointingConfig]] = None
    labels: RandomizableString = None


DEFAULT_TEMPLATE_AGENT = AgentConfig(
    num=0, type=AGENT_TYPES, agent_settings=None,
    position=None, actions=None, rotation_y=MinMaxFloat(0, 359),
    pointing=None, labels=None)

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
            if template.movement is True:
                template.movement = AgentMovementConfig()
            template.movement = reconcile_template(
                DEFAULT_TEMPLATE_AGENT_MOVEMENT,
                template.movement
            )

            if template.movement.bounds:
                template.movement.bounds = [
                    choose_random(bound)
                    for bound in source_template.movement.bounds.copy()
                ] or None

            if template.movement.points:
                template.movement.points = [
                    choose_random(point)
                    for point in source_template.movement.points.copy()
                ] or None

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

        reconciled_settings = reconciled.agent_settings or AgentSettings()
        full_settings = get_random_agent_settings(
            reconciled.type,
            settings=vars(reconciled_settings)
        )
        logger.trace(f"Agent settings: {full_settings}")

        agent = create_agent(
            type=reconciled.type,
            position_x=reconciled.position.x,
            position_z=reconciled.position.z,
            rotation_y=reconciled.rotation_y,
            settings=full_settings,
            position_y_modifier=reconciled.position.y
        )

        if reconciled.keyword_location:
            if source_template.position:
                raise ILEConfigurationException(
                    "Cannot assign position and keyword location for agent")
            if (reconciled.keyword_location.keyword in [
                KeywordLocation.ASSOCIATED_WITH_AGENT,
                KeywordLocation.IN_CONTAINER,
                KeywordLocation.IN_CONTAINER_WITH_OBJECT,
                KeywordLocation.OCCLUDE_OBJECT
            ]):
                raise ILEConfigurationException(
                    f"Agents cannot use keyword location "
                    f"{reconciled.keyword_location.keyword}")
            # If random, just pass through as we already set a random position
            # when reconciling template.
            if reconciled.keyword_location.keyword != KeywordLocation.RANDOM:
                KeywordLocation.move_to_keyword_location(
                    instance=agent,
                    reconciled=reconciled.keyword_location,
                    source=source_template.keyword_location,
                    performer_start=scene.performer_start,
                    room_dimensions=scene.room_dimensions,
                    bounds=self.bounds)

        if reconciled.pointing:
            AgentCreationService.add_pointing(agent, scene, reconciled)

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
            if movement is True or not movement.points:
                AgentCreationService.add_random_agent_movement(
                    scene, agent, movement)
            else:
                points = [(p.x, p.z) for p in movement.points]
                add_agent_movement(
                    agent,
                    movement.step_begin,
                    points,
                    movement.animation,
                    movement.repeat)

        add_random_placement_tag(agent, source_template)

        return agent

    def add_pointing(
        agent: Dict[str, Any],
        scene: Scene,
        reconciled: AgentConfig
    ) -> None:
        # Cannot configure any actions or movement.
        reconciled.actions = None
        reconciled.movement = None

        add_agent_pointing(
            agent=agent,
            step_begin=(reconciled.pointing.step_begin or 1)
        )

        # If the agent is not pointing at a specific object, return here.
        if not reconciled.pointing.object_label:
            return

        # Retrieve the object using the label, or delay if necessary.
        object_repository = ObjectRepository.get_instance()
        object_idl = object_repository.get_one_from_labeled_objects(
            reconciled.pointing.object_label
        )
        if not object_idl:
            raise ILEDelayException(
                f'Cannot find object_label={reconciled.pointing.object_label} '
                f'for agent pointing configuration.'
            )
        # Rotate the agent to face the configured object.
        agent_position = agent['shows'][0]['position']
        object_position = object_idl.instance['shows'][0]['position']
        _, rotation_y = calculate_rotations(
            Vector3d(**agent_position),
            Vector3d(**object_position),
            no_rounding_to_tens=True
        )
        agent['shows'][0]['rotation']['y'] = rotation_y

        # If the agent is not walking toward a specific object, return here.
        if not reconciled.pointing.walk_distance:
            return

        # Calculate the agent's new starting position, as well as its ending
        # position, by drawing a line from the object's position to the agent's
        # original position, and adding or subtracting the walk distance.
        distance = math.dist(
            [object_position['x'], object_position['z']],
            [agent_position['x'], agent_position['z']]
        )
        begin_distance = distance + reconciled.pointing.walk_distance
        end_distance = distance - reconciled.pointing.walk_distance

        distance_x = agent_position['x'] - object_position['x']
        distance_z = agent_position['z'] - object_position['z']
        angle_radians = math.atan2(distance_z, distance_x)
        angle_cos = math.cos(angle_radians)
        angle_sin = math.sin(angle_radians)

        begin_x = round(object_position['x'] + (begin_distance * angle_cos), 4)
        begin_z = round(object_position['z'] + (begin_distance * angle_sin), 4)
        end_x = round(object_position['x'] + (end_distance * angle_cos), 4)
        end_z = round(object_position['z'] + (end_distance * angle_sin), 4)

        # Save the original position for use elsewhere in the code.
        agent['debug']['originalPosition'] = agent['shows'][0]['position']
        # Move the agent to its new location based on the walk_distance.
        agent = move_to_location(agent, {
            'position': {
                'x': begin_x,
                'y': agent_position['y'],
                'z': begin_z
            },
            'rotation': {
                'x': 0,
                'y': round(agent['shows'][0]['rotation']['y'] + 180, 2) % 360,
                'z': 0
            }
        })
        bounds_without_agent = find_bounds(scene, ignore_ids=[agent['id']])
        ending_bounds = create_bounds(
            agent['debug']['dimensions'],
            agent['debug']['offset'],
            {'x': end_x, 'y': agent['shows'][0]['position']['y'], 'z': end_z},
            {'x': 0, 'y': agent['shows'][0]['rotation']['y'] + 180, 'z': 0},
            agent['debug']['positionY']
        )
        # Ensure the agent's new position will not cause any collisions.
        if not validate_location_rect(
            agent['shows'][0]['boundingBox'],
            vars(scene.performer_start.position),
            # Ignore the agent's bounding box here.
            bounds_without_agent,
            vars(scene.room_dimensions)
        ) or not validate_location_rect(
            ending_bounds,
            vars(scene.performer_start.position),
            # Ignore the agent's bounding box here.
            bounds_without_agent,
            vars(scene.room_dimensions)
        ):
            raise ILEException(
                f'The configured walk_distance for a pointing agent causes a '
                f'collision with another object: '
                f'position={agent["shows"][0]["position"]} '
                f'walk_distance={reconciled.pointing.walk_distance}'
            )
        # Add the walking movement at the configured step, or 1 by default.
        walk_step = reconciled.pointing.step_begin or 1
        add_agent_movement(agent, walk_step, [(end_x, end_z)])
        move_step_length = estimate_move_step_length(
            {'x': begin_x, 'z': begin_z},
            {'x': end_x, 'z': end_z}
        )
        # Reset the agent's pointing action to be after the movement.
        agent['actions'] = []
        add_agent_pointing(agent, walk_step + move_step_length)

    @staticmethod
    def add_random_agent_movement(
            scene: Scene, agent: SceneObject, config: AgentMovementConfig):
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
