import copy
import logging
import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from machine_common_sense.config_manager import Goal, Vector3d

from generator import (
    MAX_TRIES,
    ObjectBounds,
    Scene,
    SceneObject,
    geometry,
    instances,
    materials,
    structures,
    tags
)
from generator.base_objects import (
    LARGE_BLOCK_TOOLS_TO_DIMENSIONS,
    create_soccer_ball
)
from generator.imitation import (
    IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL,
    IMITATION_CONTAINER_TELEPORT_ROTATIONS_LEFT_SIDE,
    IMITATION_CONTAINER_TELEPORT_ROTATIONS_RIGHT_SIDE,
    ImitationKidnapOptions,
    ImitationTriggerOrder,
    add_imitation_task
)
from generator.lava import LavaIslandSizes
from generator.mechanisms import create_placer
from generator.structures import (
    BASE_DOOR_HEIGHT,
    BASE_DOOR_WIDTH,
    create_guide_rails_around
)
from generator.tools import (
    HOOKED_TOOL_BUFFER,
    INACCESSIBLE_TOOL_BLOCKING_WALL_MINIMUM_SEPARATION,
    L_SHAPED_TOOLS,
    MAX_TOOL_LENGTH,
    MIN_LAVA_ISLAND_LONG_ROOM_DIMENSION_LENGTH,
    MIN_LAVA_ISLAND_SHORT_ROOM_DIMENSION_LENGTH,
    MIN_TOOL_CHOICE_X_DIMENSION,
    TOOL_TYPES,
    create_broken_tool,
    create_inaccessible_tool,
    get_tool_shape
)
from ideal_learning_env.action_service import ActionService
from ideal_learning_env.actions_component import StepBeginEnd
from ideal_learning_env.agent_service import (
    AgentActionConfig,
    AgentConfig,
    AgentMovementConfig,
    AgentPointingConfig
)

from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import (
    ILEDelayException,
    ILEException,
    RandomizableBool,
    RandomizableString,
    choose_random,
    find_bounds,
    return_list
)
from .goal_services import GoalConfig, GoalServices
from .interactable_object_service import (
    InteractableObjectConfig,
    KeywordLocationConfig,
    ToolConfig,
    create_user_configured_interactable_object
)
from .numerics import (
    MinMaxFloat,
    RandomizableFloat,
    RandomizableInt,
    RandomizableVectorFloat3d,
    VectorFloatConfig,
    VectorIntConfig
)
from .object_services import (
    InstanceDefinitionLocationTuple,
    KeywordLocation,
    ObjectRepository,
    RelativePositionConfig
)
from .structural_object_service import (
    DOOR_MATERIAL_RESTRICTIONS,
    FeatureCreationService,
    FeatureTypes,
    FloorAreaConfig,
    PartitionFloorConfig,
    StructuralDoorConfig,
    StructuralPlacerConfig,
    StructuralPlatformConfig
)
from .validators import (
    ValidateList,
    ValidateNumber,
    ValidateOptions,
    ValidateOr
)

logger = logging.getLogger(__name__)


DOOR_OCCLUDER_MIN_ROOM_Y = 5
TWO_DOOR_OCCLUDER_MIN_ROOM_Y = 4

EXTENSION_LENGTH_MIN = 0.5
EXTENSION_WIDTH = 1

MIN_LAVA_ISLAND_SIZE = 1
MAX_LAVA_ISLAND_SIZE = 5

# Max lava width should be 6 for rect tools, 3 for hooked.
# (determined based on MAX_LAVA_WITH_ISLAND_WIDTH values)
MIN_LAVA_WIDTH_HOOKED_TOOL = 1
MAX_LAVA_WIDTH_HOOKED_TOOL = 3
MIN_LAVA_WIDTH = 2
MAX_LAVA_WIDTH = 6

# Min lava with island width should be 5
MAX_LAVA_WITH_ISLAND_WIDTH = 9
MIN_LAVA_WITH_ISLAND_WIDTH_HOOKED_TOOL = 3
MAX_LAVA_WITH_ISLAND_WIDTH_HOOKED_TOOL = 7

IMITATION_TASK_CONTAINER_SCALE = 1
IMITATION_TASK_TARGET_SEPARATION = 0.6
IMITATION_AGENT_START_X = 0.3
IMITATION_AGENT_END_X = 0.4


class ImprobableToolOption(str, Enum):
    NO_TOOL = 'no_tool'
    TOO_SHORT_TOOL = 'too_short'


TARGET_CONTAINER_LABEL = 'target_container'

# for seeing leads to knowing tasks
PLACER_ACTIVATION_STEP = 50
PLACER_DEACTIVATION_STEP = 65
BIN_LEFT_X_POS = -1
BIN_RIGHT_X_POS = 1
BIN_REAR_Z_POS = 0.5
BIN_FRONT_Z_POS = -0.5


@dataclass
class LavaTargetToolConfig():
    """
    Defines details of the shortcut_lava_target_tool shortcut.  This shortcut
    creates a room with a target object on an island surrounded by lava. There
    will also be a block tool to facilitate acquiring the goal object.
    - `front_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles of lava in front of the island.  Must produce value
    between 2 and 6 for rectangular tools, 1 to 3 for hooked and isosceles
    tools.
    Default: Random based on room size and island size
    - `guide_rails` (bool, or list of bools): If True, guide rails will be
    generated to guide the tool in the direction it is oriented.  If a target
    exists, the guide rails will extend to the target.  This option cannot be
    used with `tool_rotation`. Default: False
    - `island_size` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): The width and length of the island inside the
    lava.  Must produce value from 1 to 5 for rectangular tools, 1 to 3
    for hooked and isosceles tools.
    Default: Random based on room size
    - `left_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles of lava left of the island.  Must produce value
    between 2 and 6 for rectangular tools, but will be ignored for hooked and
    isosceles tools, since the lava should extend to the wall in that case.
    Default: Random based on room size and island size
    - `random_performer_position` (bool, or list of bools): If True, the
    performer will be randomly placed in the room. They will not be placed in
    the lava or the island   Default: False
    - `random_target_position` (bool, or list of bools): If True, the
    target object will be positioned randomly in the room, rather than being
    positioned on the island surrounded by lava. Default: False
    - `rear_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles of lava behind of the island.  Must produce value
    between 2 and 6 for rectangular tools, 1 to 3 for hooked and isosceles
    tools.
    Default: Random based on room size, island size, and other lava widths.
    - `right_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles right of the island.  Must produce value
    between 2 and 6 for rectangular tools, but will be ignored for hooked and
    isosceles tools, since the lava should extend to the wall in that case.
    Default: Random based on room size and island size
    - `random_performer_position` (bool, or list of bools): If True, the
    performer will be randomly placed in the room. They will not be placed in
    the lava or the island. If the `tool_type` is inaccessible the performer
    will randomly start on the side of the room where the target is where
    they cannot access the tool. Default: False
    - `tool_rotation` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts):
    Angle that tool should be rotated out of alignment with target.
    This option cannot be used with `guide_rails`, or the `broken` and
    `inaccessible` `tool_type` choices. For `hooked` and `isosceles` tools,
    we advice against setting a rotation higher than 315.
    Defaults to one of the following: 0, 45, 90, 135, 180, 225, 270, 315
    - `distance_between_performer_and_tool` (float, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of floats and/or MinMaxFloat
    dicts): Distance between the performer agent and the tool. If set to `0`,
    will try all distances between `0.5` and the bounds of the room. If set to
    a MinMaxFloat with a `max` of `0` or greater than the room bounds, will
    try all distances between the configured `min` and the bounds of the room.
    If set to a MinMaxFloat with a `min` of `0`, will try all distances
    between the configured `max` and `0.5`. This cannot be used in combination
    with `random_performer_position`. Default: None
    - `tool_offset_backward_from_lava` (float, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of floats and/or MinMaxFloat dicts): The vertical offset of
    the tool: either further into the lava, for `hooked` and `isosceles` tools,
    or further from the lava, for other tools. Must be 0 or greater. Cannot be
    used with `hooked` and `isosceles` tools when `tool_rotation` is non-zero.
    Default: 0
    - `tool_horizontal_offset` (float, or [MinMaxFloat](#MinMaxFloat) dict, or
    list of floats and/or MinMaxFloat dicts): The horizontal offset of tool
    either left or right from being aligned with the target. If `tool_type` is
    inaccessible this has alternate behavior. See
    `inaccessible_tool_blocking_wall_horizontal_offset` for description.
    Default: 0
    - `inaccessible_tool_blocking_wall_horizontal_offset` (
    [RandomizableFloat](#RandomizableFloat)): The horizontal offset
    of the blocking wall away from the target's horizontal position.
    Must be less than or equal to 0.5 (right side) or greater than or
    equal to 0.5 (left side).
    The performer will spawn on the side with the target. The tool will spawn
    on the opposite side of the wall. Setting `tool_horizontal_offset` has
    alternate behavior when combined with this property.
    `tool_horizontal_offset` will offset the tool from the the blocking
    wall and take the absolute value of the offset. The offset is based
    on the closest edges of the tool and the wall. For example, if the tool
    is rotated 90 degrees and the `tool_horizontal_offset` is 3 while
    `inaccessible_tool_blocking_wall_horizontal_offset` is -2 the the tool's
    closest edge to the wall will be a distance of 3 to the left of the wall
    since the wall has a negative offset to the left.
    Default: None
    - `tool_type` (str, or list of strs): The type of tool to generate, either
    `rectangular`, `hooked`, `isosceles`, `small`, `broken`, or `inaccessible`.
    Both `hooked` and isosceles` tools are L-shaped; `hooked` tools always have
    width 3, and `isosceles` tools always have width equal to their length.
    If `hooked` and `isosceles` tools are chosen and lava widths are not
    specified, the room will default to having an island size of 1, with lava
    extending all the way to the walls in both the left and right directions.
    The front and rear lava in the default hooked/isosceles tool case will each
    have a size of 1.
    If `small` is chosen the tool will always be a length of 1.
    If `broken` is chosen the tool will be the correct length but have
    scattered positions amd rotations for each individual broken piece.
    The tool will still have an overall rotation if `tool_rotation` is set.
    If `inaccessible` the room will be divided vertically by a blocking wall
    with a short height.
    Default: `rectangular`

    """
    island_size: RandomizableInt = None
    front_lava_width: RandomizableInt = None
    rear_lava_width: RandomizableInt = None
    left_lava_width: RandomizableInt = None
    right_lava_width: RandomizableInt = None
    guide_rails: RandomizableBool = False
    tool_rotation: RandomizableFloat = None
    random_performer_position: RandomizableBool = False
    random_target_position: RandomizableBool = False
    distance_between_performer_and_tool: RandomizableFloat = None
    tool_offset_backward_from_lava: RandomizableFloat = 0
    tool_horizontal_offset: RandomizableFloat = 0
    inaccessible_tool_blocking_wall_horizontal_offset: RandomizableFloat = None
    tool_type: RandomizableString = TOOL_TYPES.RECT


@dataclass
class InaccessibleToolProperties():
    # internal class for storing inaccessible tool properties
    tool: SceneObject = None
    wall: SceneObject = None
    short_direction: str = None
    blocking_wall_pos_cutoff: float = None
    room_wall_pos_cutoff: float = None


@dataclass
class TripleDoorConfig():
    """
    Defines details of the triple door shortcut.  This short cut contains a
    platform that bisects the room.  A wall with 3 doors (a.k.a. door occluder,
    or "door-cluder" or "doorcluder") will bisect the room
    in the perpendicular direction.

    - `add_extension` (bool, or list of bools): If true, add an extension to
    one side of the far end (+Z) of the platform with the label
    "platform_extension". Default: False
    - `add_freeze` (bool, or list of bools): If true and 'start_drop_step is'
    greater than 0, the user will be frozen (forced to Pass) until the wall and
    doors are in position.  If the 'start_drop_step' is None or less than 1,
    this value has no effect.  Default: True
    - `add_lips` (bool, or list of bools): If true, lips will be added on the
    platform beyond the doors and wall such that the performer will be forced
    to go through the corresponding door to enter the area behind it.
    Default: True
    - `bigger_far_end` (bool, or list of bools): If true, increases the height
    and the width of the far end of the platform so it's too tall for the
    performer to walk onto and it's twice as wide. Default: false
    - `door_material` (string, or list of strings): The material or material
    type for the doors.
    - `extension_length` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): If
    `add_extension` is true, set the length of the extension (on the X axis).
    Default: Up to half of the room's X dimension.
    otherwise, don't add a platform extension.
    - `extension_position` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): If
    `add_extension` is true, set the position of the extension (on the Z axis).
    If the position is positive, the extension will be on the right side (+X).
    If the position is negative, the extension will be on the left side (-X).
    Default: Up to half of the room's Z dimension.
    - `restrict_open_doors` (bool, or list of bools): If true, the performer
    will only be able to open one door.  Using this feature and 'add_lips'
    will result in a forced choice by the performer.  Default: True
    - `start_drop_step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): Step number to start dropping the bisecting
    wall with doors.  If None or less than 1, the wall will start in position.
    Default: None
    - `wall_height` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): The
    height for the wall. The height for the center door will be -2 to
    account for being on top of the platform.
    - `wall_material` (string, or list of strings): The material or material
    type for the wall.
    """
    start_drop_step: RandomizableInt = None
    add_lips: RandomizableBool = True
    add_freeze: RandomizableBool = True
    restrict_open_doors: RandomizableBool = True
    door_material: RandomizableString = None
    wall_material: RandomizableString = None
    add_extension: RandomizableBool = False
    extension_length: RandomizableFloat = None
    extension_position: RandomizableFloat = None
    bigger_far_end: RandomizableBool = False
    wall_height: RandomizableFloat = None


@dataclass
class DoubleDoorConfig():
    """
    Defines details of the double door shortcut. A wall with 2 doors
    (a.k.a. door occluder, or "door-cluder" or "doorcluder") will bisect the
    room in the perpendicular direction. A platform can be added to the
    middle back wall where the AI will be positioned at the beginning of the
    scene. Lava can be added down the middle of the floor splitting the room
    in half.

    - `add_freeze` (bool, or list of bools): If true and 'start_drop_step is'
    greater than 0, the user will be frozen (forced to Pass) until the wall and
    doors are in position.  If the 'start_drop_step' is None or less than 1,
    this value has no effect. Default: True
    - `add_lava` (bool, or list of bools): If true adds lava along the z axis
    of the room. Default: True
    - `add_platform` (bool, or list of bools): If true adds a platform at the
    back of the room where the AI will start on. Default: True
    - `door_material` (string, or list of strings): The material or material
    type for the doors.
    - `occluder_wall_position_z` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts):
    Where the occluder wall will cross the
    z-axis in the room. `occluder_distance_from_performer` will override this
    value. Default: 0 (middle of the room)
    - `occluder_distance_from_performer` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts):
    If there is a platform the, the performer
    will start on top of the platform and the occluder wall will be placed
    this distance (`occluder_distance_from_performer`) from the performer. Must
    be greater than 1 or null
    Default: 6.5
    - `platform_height` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts):
    The height (y scale) of the platform
    Default: 1.5
    - `platform_length` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts):
    The lenth (z scale) of the platform
    Default: 1
    - `platform_width` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts):
    The width (z scale) of the platform
    Default: 1
    - `start_drop_step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): Step number to start dropping the bisecting
    wall with doors.  If None or less than 1, the wall will start in position.
    Default: None
    - `wall_material` (string, or list of strings): The material or material
    type for the wall.
    """
    add_freeze: RandomizableBool = True
    add_lava: RandomizableBool = True
    add_platform: RandomizableBool = True
    door_material: RandomizableString = None
    occluder_wall_position_z: RandomizableFloat = None
    occluder_distance_from_performer: RandomizableFloat = None
    platform_height: RandomizableFloat = 1.5
    platform_length: RandomizableFloat = 1
    platform_width: RandomizableFloat = 1
    restrict_open_doors: RandomizableBool = True
    start_drop_step: RandomizableInt = 1
    wall_material: RandomizableString = None


@dataclass
class AgentTargetConfig():
    """
    Defines all the configurable options for
    [shortcut_agent_with_target](#shortcut_agent_with_target).
    - `agent` ([AgentConfig](#AgentConfig) dict, or list of AgentConfig dicts):
    Configures the settings for the agent.
    - `agent_position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list
    [VectorFloatConfig](#VectorFloatConfig) dicts): Deprecated. Please use
    `agent.position`
    - `movement` (bool, or list of bools): Deprecated. Please use
    `agent.movement`
    - `movement_bounds` (list of [VectorFloatConfig](#VectorFloatConfig)
    dicts): Deprecated. Please use `agent.bounds`
    """
    agent: Union[AgentConfig, List[AgentConfig]] = None
    agent_position: RandomizableVectorFloat3d = None
    movement_bounds: List[RandomizableVectorFloat3d] = None
    movement: RandomizableBool = None


@dataclass
class BisectingPlatformConfig():
    """
    Defines details of the shortcut_bisecting_platform shortcut.  This shortcut
    creates a platform that bisects the room, where the performer will start.
    On default, a blocking wall is on that platform, forcing the performer
    to choose a side to drop off of the platform, but this can be disabled.
    - `has_blocking_wall` (bool): Enables the blocking wall so that the
    performer has to stop and choose a side of the room. Default: True
    - `has_double_blocking_wall` (bool): Enables the double blocking wall used
    in Spatial Reorientation tasks. Overrides both `has_blocking_wall` and
    `has_long_blocking_wall`. Default: False
    - `has_long_blocking_wall` (bool): Enables the extra-long blocking wall.
    Overrides `has_blocking_wall`. Default: False
    - `is_short` (bool): Makes the platform short (a Y scale of 0.5 rather
    than 1). Default: False
    - `is_thin` (bool): Makes the platform thin (an X scale of 0.5 rather
    than 1). Default: False
    - `other_platforms` ([StructuralPlatformConfig](#StructuralPlatformConfig)
    dict, or list of StructuralPlatformConfig dicts): Configurations to
    generate other platforms that may intersect with the bisecting platform.
    Default: No other platforms
    - `position_z` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The starting Z position for the
    performer agent. Default: 0.5 away from the back wall
    """
    has_blocking_wall: bool = True
    has_double_blocking_wall: bool = False
    has_long_blocking_wall: bool = False
    is_short: bool = False
    is_thin: bool = False
    other_platforms: Union[
        StructuralPlatformConfig,
        List[StructuralPlatformConfig]
    ] = None
    position_z: RandomizableFloat = None


@dataclass
class ImitationTaskConfig():
    """
    Defines details of the shortcut_imitation_task shortcut.
    - `trigger_order` (string, or list of strings): The combination the three
    containers must be openend in order to make the target appear. Oriented
    by facing the front of the containers. Must be one of the following.
    For opening 2 containers: left_middle, left_right, middle_left,
    middle_right, right_middle, right_left. For opening 1 container:
    left, middle, right.
    Default: random
    - `containers_on_right_side` (bool, or list of bools): Whether the
    containers should be to the right or left of the performer.
    Default: random
    - `kidnap_option`: (string, or list of strings): Dictates
    what teleports in the scene after the agent performs its imitation sequence
    to and the performer is kidnapped. Options are:
    1) agent_only: The imitation agent teleports away from the
    containers but in view. Nothing else is teleported.
    2) containers: The containers are teleported anr rotated but still in view.
    The imitation agent is teleported away from the containers but in view.
    4) performer: The performer is teleported to a random part of the room
    but looks at the center of the room where the containers still are.
    The imitation agent is teleported away from the containers but in view.
    Default: random
    - `relative_container_rotation`: (int, or list of int): Dictates
    what degree of rotation change the containers will rotate relative to
    their clockwise starting rotation. For example, if the they are facing
    270 (starting on the right side) and container_rotation of 45 will make
    the final rotation 315. Examples of what rotations containers cannot
    rotate:
    1) 360 and 180 for both left and right because the containers will
    face identical or opposite from their start.
    2) 90 on right side, 270 on left which will make the containers face
    directly away from the performer.
    Direction containers can rotate for right side: [45, 135, 225, 270, 315]
    Direction containers can rotate for left side: [45, 90, 135, 225, 315]
    Default: random
    - `global_container_rotation`: (int, or list of int): Dictates
    what degree of rotation change the containers will rotate on based on
    the absolute global rotation. Options are: [45, 135, 180, 225, 315].
    Will override `relative_container_rotation`
    Default: random
    """
    trigger_order: RandomizableString = None
    containers_on_right_side: RandomizableBool = None
    kidnap_option: RandomizableString = None
    relative_container_rotation: RandomizableInt = None
    global_container_rotation: RandomizableInt = None


@dataclass
class ToolChoiceConfig():
    """
    Defines details of the shortcut_tool_choice shortcut.  This shortcut
    creates a room with bisecting platform, with two identical lava islands on
    either side. The performer has to choose the side with the tool that can be
    used to obtain the target.
    - `improbable_option` (str, or list of strs): Determines the tool (if any)
    that will be placed on the side where it is not possible to obtain the ball
    without stepping in lava. Possible values: 'no_tool', 'too_short'.

    """

    improbable_option: RandomizableString = None


@dataclass
class SeeingLeadsToKnowingConfig():
    """
    Defines details of the shortcut_seeing_leads_to_knowing shortcut.
    In this shortcut, the performer starts with four open containers in view.
    An agent will then walk into view. Placers will descend into each
    container, with only one having the soccer ball. After the placers are
    finished moving, the agent will attempt to go to the container that has
    the target object. The performer will then have to pick whether the scene
    is plausible or implausible based on the agent's behavior (note that for
    training, all generated scenes are plausible).
    - `target_behind_agent` (bool, or list of bools): Determines whether or not
    the target is behind the agent. If target is behind the agent, the agent
    will guess and go towards one of the buckets behind itself.

    """
    target_behind_agent: RandomizableBool = None


@dataclass
class TurntablesAgentNonAgentConfig():
    """
    Defines all of the configurable options for
    [turntables_with_agent_and_non_agent]
    (#turntables_with_agent_and_non_agent).
    - `agent_label` (string): The label for an existing agent on top of one of
    the turntables. The turntable underneath this agent will NOT rotate.
    - `non_agent_label` (string): The label for an existing non-agent object on
    top of one of the turntables. The turntable underneath this object will
    rotate so the object faces one of the objects corresponding to the
    `direction_labels`. The turntable may rotate either clockwise or
    counter-clockwise, but always in 5-degree-per-step increments. The rotation
    will begin after the agent's movement, unless the agent's movement begins
    after step 45, in which case the rotation will begin on step 1.
    - `turntable_labels` (list of strings): The labels for all turntables to be
    affected.
    - `direction_labels` (list of strings): One or more labels for the objects
    in the scene toward which the non-agent object may face. If multiple labels
    are configured, then one object is randomly chosen for each scene.
    """
    agent_label: str
    non_agent_label: str
    turntable_labels: RandomizableString
    direction_labels: RandomizableString


@dataclass
class KnowledgeableAgentPairConfig():
    """
    Defines all of the configurable options for
    [knowledgeable_agent_pair]
    (#knowledgeable_agent_pair).
    - `position_1` (Vector3): One possible location for an agent to be.
    - `position_2` (Vector3): One possible location for an agent to be.
    - `pointing_step` (int): Starting step of pointing action.
    - `target_labels` (str): Label for the knowledgeable agent to use to find
    the goal.
    - `non_target_labels` (str): Label so the non-knowledgeable agent to use to
    find what it should be pointing to.
    """
    position_1: RandomizableVectorFloat3d
    position_2: RandomizableVectorFloat3d
    pointing_step: RandomizableInt = 0
    target_labels: RandomizableString = "target"
    non_target_labels: RandomizableString = None


@dataclass
class PlacersWithDecoyConfig():
    """
    Defines the configureable options for [placers_with_decoy]
    (#placers_with_decoy)
    - `activation_step` List[int]: A list of steps that the placer/decoy can
    be activated.
    - `object_end_position_x` List[float]: A list of x positions that the
    placer/decoy can move to.
    - `decoy_y_modifier` float: The distance that the decoy should stop short
    so it doesn't go all the way to the ground. Should be the height of the
    target object.
    - `placed_object_position` RandomizableVectorFloat3d: Starting position of
    the placer/decoy.
    - `labels` RandomizableString: The labels that should be applied the to
    placer/decoy.
    - `move_object_y` RandomizableFloat: A modifier to the release height of
    the target object.
    - `move_object_z` RandomizableFloat: A modifier to the release depth of
    the target object.
    - `placed_object_labels` RandomizableString: Labels to be applied to the
    target object.
    - `placed_object_rotation` RandomizableFloat: Rotation to be applied to
    the target object during release.
    """
    activation_step: List[int]
    object_end_position_x: List[float]
    decoy_y_modifier: float
    placed_object_position: RandomizableVectorFloat3d
    labels: RandomizableString = 'target_placers'
    move_object_y: RandomizableFloat = 0
    move_object_z: RandomizableFloat = 0
    placed_object_labels: RandomizableString = 'target'
    placed_object_rotation: RandomizableFloat = 0.0


class ShortcutComponent(ILEComponent):
    """Manages the settings for common shortcuts for an ILE scene."""

    # Ramp to platform constants
    RAMP_ANGLE_MAX = 40
    RAMP_ANGLE_MIN = 5
    RAMP_TO_PLATFORM_PLATFORM_LENGTH_MIN = 1
    RAMP_TO_PLATFORM_PLATFORM_LENGTH_MAX = 5
    RAMP_TO_PLATFORM_MIN_HEIGHT = 1
    RAMP_TO_PLATFORM_MIN_DIST_TO_CEILING = 1
    LABEL_START_PLATFORM = "start_structure"

    shortcut_bisecting_platform: Union[bool, BisectingPlatformConfig] = False
    """
    (bool or [BisectingPlatformConfig](#BisectingPlatformConfig)):
    Creates a platform bisecting the room.  If True, the default behavior will
    be that the performer starts on one end with a blocking wall in front of
    them such that the performer is forced to make a choice on which side they
    want to drop off and they cannot get back to the other side. This overrides
    the `performer_start_position` and `performer_start_rotation`, if
    configured. Note that the blocking wall can be disabled if needed.
    Default: False

    Simple Example:
    ```
    shortcut_bisecting_platform: False
    ```

    Advanced Example:
    ```
    shortcut_bisecting_platform:
        has_blocking_wall: False
    ```
    """

    shortcut_triple_door_choice: Union[bool, TripleDoorConfig] = False
    """
    (bool or [TripleDoorConfig](#TripleDoorConfig)):
    Creates a platform bisecting the room with a wall with 3 doors
    (a.k.a. door occluder, or "door-cluder" or "doorcluder").
    The performer starts on one end such that the performer is forced to make
    a choice on which door they want to open.  By default, the doors will be
    restricted so only one can be opened.  Will increase the Y room dimension
    to 5 if it is lower than 5.  Default: False

    Simple Example:
    ```
    shortcut_triple_door_choice: False
    ```

    Advanced Example:
    ```
    shortcut_triple_door_choice:
      start_drop_step:
        min: 2
        max: 5
      add_lips: True
      add_freeze: [True, False]
      restrict_open_doors: True
    ```
    """

    shortcut_double_door_choice: Union[bool, DoubleDoorConfig] = False
    """
    (bool or [DoubleDoorConfig](#DoubleDoorConfig)):
    Creates a wall with 2 doors, a platform at the back wall and lava down
    the length of the room. (a.k.a. door occluder, or "door-cluder" or
    "doorcluder"). The performer starts on the platform on one end such that
    the performer is forced to make a choice on which door they want to open.
    Default: False

    Simple Example:
    ```
    shortcut_double_door_choice: True
    ```

    Advanced Example:
    ```
    shortcut_double_door_choice:
        add_freeze: False
        start_drop_step:
            min: 2
            max: 5
        occluder_wall_position_z: None
        occluder_distance_from_performer: 6.5
        add_platform: True
        platform_width: 1
        platform_height: 1.5
        platform_length: 1
        add_lava: True
    ```
    """

    shortcut_start_on_platform: bool = False
    """
    (bool): Ensures that the performer will start on top of a platform. In
    order for this to work, `structural_platforms` needs to be specified
    using the label `start_structure`. This ignores any configured
    `performer_start_position` setting. Default: False

    Simple Example:
    ```
    shortcut_start_on_platform: False
    ```

    Advanced Example:
    ```
    shortcut_start_on_platform: True
    ```
    """

    shortcut_lava_room: bool = False
    """
    (bool): Creates a room with lava on either side of the performer. The
    performer will start in the center (non-lava) part. Default: False

    Simple Example:
    ```
    shortcut_lava_room: False
    ```

    Advanced Example:
    ```
    shortcut_lava_room: True
    ```
    """

    shortcut_lava_target_tool: Union[bool, LavaTargetToolConfig] = False
    """
    (bool or [LavaTargetToolConfig](#LavaTargetToolConfig)):
    Creates a room with a goal object on an island surrounded by lava.
    There will also be a block tool to facilitate acquiring the goal object.
    One dimension of the room must be 13 or greater. The other dimension must
    be 7 or greater. Rectangular block tools are used on default, and for
    these, the max width across for front + island_size + rear is 9. The min
    width across for front + island_size + rear is 5. Lava can be asymmetric
    but the same restrictions of width min: 5 and max: 9 apply for left +
    island_size + right as well. By default, the target is a soccer ball
    with scale between 1 and 3.

    For hooked and isosceles tools, different min/max rules apply. See
    LavaTargetToolConfig for details.

    The tool is a pushable/pullable tool object with a length equal
    to or greater than the span from the front of the lava over the island to
    the back of the lava. It will have a width of either 0.5, 0.75, 1.0.

    Default: False

    Simple Example:
    ```
    shortcut_lava_target_tool: False
    ```

    Advanced Example:
    ```
    shortcut_lava_target_tool:
      island_size:
        min: 1
        max: 3
      front_lava_width: 2
      rear_lava_width: [2, 3]
      left_lava_width: 2
      right_lava_width:
        min: 2
        max: 4
      guide_rails: [True, False]
    ```
    """

    shortcut_agent_with_target: Union[
        bool,
        AgentTargetConfig,
        List[Union[bool, AgentTargetConfig]]
    ] = None
    """
    (bool, or [AgentTargetConfig](#AgentTargetConfig) dict, or list of bools
    and/or AgentTargetConfig dicts): Each scene will have an agent carrying a
    target object; you will need to use the InteractWithAgent action on the
    agent to request it to produce the target object, so you can then use the
    PickupObject action to pick up the target object.

    Will use a target already configured via the `goal` option, or, if no
    target object is configured, will automatically set a retrieval goal,
    generate a soccer ball, and assign it as the retrieval target object.

    If `true`, will randomize all of the agent configuration options.

    Default: false

    Simple Example:
    ```
    shortcut_agent_with_target: False
    ```

    Advanced Example:
    ```
    shortcut_agent_with_target:
      agent:
        position:
          x:
            min: 1
            max: 3
          y: 0
          z: [2, 3]
        bounds:
          - x: 0
            z: 2
          - x: 2
            z: 0
          - x: 0
            z: -2
          - x: -2
            z: 0
    ```
    """

    shortcut_imitation_task: \
        Union[bool, ImitationTaskConfig,
              List[Union[bool, ImitationTaskConfig]]] = False
    """
    (bool or [ImitationTaskConfig](#ImitationTaskConfig)):
    Creates a room with an imitation task.
    The performer watches an agent open containers in a specific order. Then
    the performer is kidnaped. After the kidnaping either the performer
    is not moved and the containers are not moved, the containers are moved
    and possibly rotated by 90 degrees but the performer does not move, or
    the performer is moved but the containers stay the same. In all
    cases the agent is moved away from the containers but still nearby to
    be seen after the kidnap.
    The room is always rectangular.
    The short dimension is either 8, 9, 10 and the long is 16, 18, 20.
    The room height is always 3.

    Simple Example:
    ```
    shortcut_imitation_task: False
    ```

    Advanced Example:
    ```
    shortcut_imitation_task:
      trigger_order: [left_right, middle_left, right_middle]
      containers_on_right_side: True
      kidnap_options: containers_rotate
    ```
    """

    shortcut_tool_choice: Union[bool,
                                ToolChoiceConfig] = False
    """
    (bool, ToolChoiceConfig): Creates a room with a bisecting platform, with
    two mirrored lava islands containing targets and a different tool option
    (one valid tool that can be used to obtain the target, and one incorrect
    option). If True, the default behavior will be that the performer starts
    on one end, having to eventually pick a side, and they cannot get back
    to the other side. This overrides the `performer_start_position` and
    `performer_start_rotation`, if configured. Note that this shortcut
    requires a minimum x-axis room size of 20.

    Default: False

    Simple Example:
    ```
    shortcut_tool_choice: False
    ```

    Advanced Example:
    ```
    shortcut_tool_choice:
        improbable_choice: 'no_tool'
    ```
    """

    turntables_with_agent_and_non_agent: TurntablesAgentNonAgentConfig = None
    """
    ([TurntablesAgentNonAgentConfig](#TurntablesAgentNonAgentConfig) dict):
    Useful for the Spatial Reference task. Rotates a turntable underneath
    a non-agent object so it faces another object in the scene.

    Simple Example:
    ```
    turntables_with_agent_and_non_agent: null
    ```

    Advanced Example:
    ```
    turntables_with_agent_and_non_agent:
      agent_label: my_agent
      non_agent_label: my_rotating_object
      turntable_labels: [my_turntable_1, my_turntable_2]
      direction_labels: [my_static_object_1, my_static_object_2]
    ```
    """

    shortcut_seeing_leads_to_knowing: Union[bool,
                                            SeeingLeadsToKnowingConfig] = False
    """
    (bool): Shortcut for the seeing leads to knowing task. The performer
    starts with four open containers in view. An agent will then walk into
    view. Placers will descend into each container, with only one having
    the soccer ball. After the placers are finished moving, the agent
    will attempt to go to the container that has the target object. The
    performer will then have to pick whether the scene is plausible or
    implausible based on the agent's behavior (note that for training,
    all generated scenes are plausible).

    Default: False

    Simple Example:
    ```
    shortcut_seeing_leads_to_knowing: False
    ```

    Advanced Example:
    ```
    shortcut_seeing_leads_to_knowing:
        target_behind_agent: True
    ```
    """

    knowledgeable_agent_pair: Union[bool, KnowledgeableAgentPairConfig] = False
    """
    (bool, KnowledgeableAgentPairConfig): Config to create a pair of agents.
    One agent will be knowledgeable (will know where the goal is), the other
    won't know and will point into space.

    Simple Example:
    ```
    knowledgeable_agent_pair:
            position_1:
                x: 1.0
                y: 0
                z: 0
            position_2:
                x: -1.0
                y: 0
                z: 0
    ```

    Advanced Example
    Simple Example:
    ```
    knowledgeable_agent_pair:
        position_1:
            x: 1.0
            y: 0
            z: 0
        position_2:
            x: -1.0
            y: 0
            z: 0
        pointing_step: 10,
        target_labels: target
    """

    placers_with_decoy: Union[bool, PlacersWithDecoyConfig] = False
    """
    (bool): Creates one placer to move and the target object and another that
    is a decoy that pretends to move something. The placers have the order
    and location they will move to randomized.
    Default: False

    Simple Example:
    ```
    placers_with_decoy: False
    ```

    Advanced Example 1:
    ```
    'placers_with_decoy': {
            'activation_step': [13, 59],
            'object_end_position_x': [2.0, -2.0],
            'placed_object_position': VectorFloatConfig(x=1, y=0.501, z=2),
            'decoy_y_modifier': 0.22
        }
    ```

    Advanced Example 2:
    ```
    placers_with_decoy:
        'placers_with_decoy': {
            'activation_step': [13, 59],
            'object_end_position_x': [2.0, -2.0],
            'labels': 'target_placers',
            'move_object_y': 0,
            'move_object_z': 0,
            'placed_object_labels': 'target',
            'placed_object_position': VectorFloatConfig(x=1, y=0.501, z=2),
            'placed_object_rotation': 0.0,
            'decoy_y_modifier': 0.22
        }
    ```
    """

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self._delayed_perf_pos = False
        self._delayed_perf_pos_reason = None
        self._delayed_turntables_with_agent_and_non_agent = False
        self._delayed_turntables_with_agent_and_non_agent_reason = None
        self._delayed_knowledgeable_agent_pair = []
        self._delayed_knowledgeable_agent_pair_reason = None

    @ile_config_setter()
    def set_shortcut_bisecting_platform(self, data: Any) -> None:
        self.shortcut_bisecting_platform = data

    def get_shortcut_bisecting_platform(
            self) -> Union[bool, BisectingPlatformConfig]:
        if self.shortcut_bisecting_platform is False:
            return False
        config = self.shortcut_bisecting_platform
        if self.shortcut_bisecting_platform is True:
            config = BisectingPlatformConfig()
        return config

    @ile_config_setter(validator=ValidateOptions(
        props=['door_material'],
        options=(DOOR_MATERIAL_RESTRICTIONS +
                 ["METAL_MATERIALS", "PLASTIC_MATERIALS", "WOOD_MATERIALS"]
                 )
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['wall_material'],
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    @ile_config_setter(validator=ValidateNumber(
        props=['start_drop_step'], min_value=0))
    @ile_config_setter(validator=ValidateNumber(
        props=['extension_length'],
        min_value=EXTENSION_LENGTH_MIN,
        null_ok=True
    ))
    @ile_config_setter(validator=ValidateOr(validators=[
        ValidateNumber(
            props=['extension_position'],
            min_value=(EXTENSION_WIDTH / 2.0),
            null_ok=True
        ),
        ValidateNumber(
            props=['extension_position'],
            max_value=-(EXTENSION_WIDTH / 2.0),
            null_ok=True
        )
    ]))
    @ile_config_setter(validator=ValidateNumber(
        props=['wall_height'],
        min_value=structures.BASE_DOOR_HEIGHT,
        null_ok=True
    ))
    def set_shortcut_triple_door_choice(self, data: Any) -> None:
        self.shortcut_triple_door_choice = data

    def get_shortcut_triple_door_choice(
            self) -> Union[bool, TripleDoorConfig]:
        if self.shortcut_triple_door_choice is False:
            return False
        config = self.shortcut_triple_door_choice
        if self.shortcut_triple_door_choice is True:
            config = TripleDoorConfig()
        config = choose_random(config)
        return config

    @ile_config_setter(validator=ValidateOptions(
        props=['door_material'],
        options=(DOOR_MATERIAL_RESTRICTIONS +
                 ["METAL_MATERIALS", "PLASTIC_MATERIALS", "WOOD_MATERIALS"]
                 )
    ))
    @ile_config_setter(validator=ValidateNumber(
        props=['occluder_distance_from_performer'], min_value=1, null_ok=True))
    @ile_config_setter(validator=ValidateNumber(
        props=['platform_height'], min_value=1))
    @ile_config_setter(validator=ValidateNumber(
        props=['platform_length'], min_value=1))
    @ile_config_setter(validator=ValidateNumber(
        props=['platform_width'], min_value=1))
    @ile_config_setter(validator=ValidateNumber(
        props=['start_drop_step'], min_value=0, null_ok=True))
    @ile_config_setter(validator=ValidateOptions(
        props=['wall_material'],
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_shortcut_double_door_choice(self, data: Any) -> None:
        self.shortcut_double_door_choice = data

    def get_shortcut_double_door_choice(
            self) -> Union[bool, DoubleDoorConfig]:
        if self.shortcut_double_door_choice is False:
            return False
        config = self.shortcut_double_door_choice
        if self.shortcut_double_door_choice is True:
            config = DoubleDoorConfig()
        config = choose_random(config)
        return config

    def set_shortcut_start_on_platform(self, data: Any) -> None:
        self.shortcut_start_on_platform = data

    def get_shortcut_start_on_platform(
            self) -> bool:
        return self.shortcut_start_on_platform

    def set_shortcut_lava_room(self, data: Any) -> None:
        self.shortcut_lava_room = data

    def get_shortcut_lava_room(
            self) -> bool:
        return self.shortcut_lava_room

    @ile_config_setter(validator=ValidateNumber(
        props=['island_size'],
        min_value=MIN_LAVA_ISLAND_SIZE,
        max_value=MAX_LAVA_ISLAND_SIZE,
        null_ok=True
    ))
    @ile_config_setter(validator=ValidateNumber(
        props=[
            'front_lava_width',
            'rear_lava_width'],
        min_value=MIN_LAVA_WIDTH_HOOKED_TOOL,
        max_value=MAX_LAVA_WIDTH,
        null_ok=True
    ))
    @ile_config_setter(validator=ValidateNumber(
        props=['distance_between_performer_and_tool'],
        min_value=0, null_ok=True))
    def set_shortcut_lava_target_tool(self, data: Any) -> None:
        self.shortcut_lava_target_tool = data

    def get_shortcut_lava_target_tool(self) -> Optional[LavaTargetToolConfig]:
        if self.shortcut_lava_target_tool is False:
            return None
        if self.shortcut_lava_target_tool is True:
            return LavaTargetToolConfig()
        return self.shortcut_lava_target_tool

    @ile_config_setter()
    def set_shortcut_agent_with_target(self, data: Any) -> None:
        self.shortcut_agent_with_target = data

    def get_shortcut_agent_with_target(self) -> Union[bool, AgentTargetConfig]:
        if not self.shortcut_agent_with_target:
            return False
        if isinstance(self.shortcut_agent_with_target, List):
            return random.choice(self.shortcut_agent_with_target)
        if self.shortcut_agent_with_target is True:
            return AgentTargetConfig()
        return self.shortcut_agent_with_target

    @ile_config_setter()
    def set_turntables_with_agent_and_non_agent(self, data: Any) -> None:
        self.turntables_with_agent_and_non_agent = data

    @ile_config_setter(validator=ValidateOptions(
        props=['trigger_order'],
        options=(
            ImitationTriggerOrder.LEFT,
            ImitationTriggerOrder.MIDDLE,
            ImitationTriggerOrder.RIGHT,
            ImitationTriggerOrder.LEFT_MIDDLE,
            ImitationTriggerOrder.LEFT_RIGHT,
            ImitationTriggerOrder.MIDDLE_LEFT,
            ImitationTriggerOrder.MIDDLE_RIGHT,
            ImitationTriggerOrder.RIGHT_MIDDLE,
            ImitationTriggerOrder.RIGHT_LEFT)
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['kidnap_option'],
        options=(
            ImitationKidnapOptions.AGENT_ONLY,
            ImitationKidnapOptions.CONTAINERS,
            ImitationKidnapOptions.PERFORMER)
    ))
    def set_shortcut_imitation_task(self, data: Any) -> None:
        self.shortcut_imitation_task = data

    def get_shortcut_imitation_task(
            self) -> Union[bool, ImitationTaskConfig]:
        if not self.shortcut_imitation_task:
            return False
        if self.shortcut_imitation_task is True:
            config = ImitationTaskConfig()
            return config
        template = copy.deepcopy(self.shortcut_imitation_task)
        if isinstance(self.shortcut_imitation_task, List):
            config = random.choice(template)
        elif isinstance(self.shortcut_imitation_task, ImitationTaskConfig):
            config = template
        config = choose_random(config)
        return config

    @ile_config_setter(validator=ValidateList(
        props=['object_end_position_x'],
        min_count=2)
    )
    @ile_config_setter(validator=ValidateList(
        props=['object_end_position_x'],
        min_count=2)
    )
    def set_placers_with_decoy(self, data: Any) -> None:
        self.placers_with_decoy = data

    def get_placers_with_decoy(self) -> Union[bool, PlacersWithDecoyConfig]:
        if self.placers_with_decoy is False:
            return False
        config = self.placers_with_decoy
        if self.placers_with_decoy is True:
            config = PlacersWithDecoyConfig()
        config = choose_random(config)
        return config

    @ile_config_setter(validator=ValidateOptions(
        props=['improbable_option'],
        options=(
            ImprobableToolOption.TOO_SHORT_TOOL,
            ImprobableToolOption.NO_TOOL
        )
    ))
    def set_shortcut_tool_choice(self, data: Any) -> None:
        self.shortcut_tool_choice = data

    def get_shortcut_tool_choice(
            self) -> Union[bool, ToolChoiceConfig]:
        if self.shortcut_tool_choice is False:
            return False
        config = self.shortcut_tool_choice
        if self.shortcut_tool_choice is True:
            config = ToolChoiceConfig()
        config = choose_random(config)
        return config

    @ile_config_setter()
    def set_shortcut_seeing_leads_to_knowing(self, data: Any) -> None:
        self.shortcut_seeing_leads_to_knowing = data

    def get_shortcut_seeing_leads_to_knowing(
            self) -> Union[bool, SeeingLeadsToKnowingConfig]:
        if self.shortcut_seeing_leads_to_knowing is False:
            return False
        config = self.shortcut_seeing_leads_to_knowing
        if self.shortcut_seeing_leads_to_knowing is True:
            config = SeeingLeadsToKnowingConfig()
        config = choose_random(config)
        return config

    @ile_config_setter()
    def set_knowledgeable_agent_pair(self, data: Any) -> None:
        self.knowledgeable_agent_pair = data

    def get_knowledgeable_agent_pair(
            self) -> Union[bool, KnowledgeableAgentPairConfig]:
        if self.knowledgeable_agent_pair is False:
            return False
        config = self.knowledgeable_agent_pair
        if self.knowledgeable_agent_pair is True:
            config = KnowledgeableAgentPairConfig()
        config = choose_random(config)
        return config

    # Override
    def update_ile_scene(self, scene: Scene) -> Scene:
        logger.info('Configuring shortcut options for the scene...')
        room_dim = scene.room_dimensions

        scene = self._add_bisecting_platform(scene, room_dim)
        scene = self._add_triple_door_shortcut(scene, room_dim)
        scene = self._add_double_door_shortcut(scene, room_dim)
        scene = self._add_lava_shortcut(scene, room_dim)
        scene = self._delay_performer_placement(scene, room_dim)
        scene = self._add_tool_lava_goal(scene, room_dim)
        scene = self._add_agent_holds_target(scene)
        scene = self._add_imitation_task(scene)
        scene = self._add_lava_tool_choice_goal(scene, room_dim)
        scene = self._add_seeing_leads_to_knowing(scene)
        scene = self._add_placers_with_decoys(scene)

        try:
            scene = self._update_turntables_with_agent_and_non_agent(scene)
        except ILEDelayException as e:
            self._delayed_turntables_with_agent_and_non_agent = True
            self._delayed_turntables_with_agent_and_non_agent_reason = e

        try:
            scene = self._add_knowledgeable_agent_pair(scene)
        except ILEDelayException as e:
            self._delayed_knowledgeable_agent_pair_reason = e

        return scene

    def _add_bisecting_platform(self, scene: Scene, room_dim: Vector3d):
        config = self.get_shortcut_bisecting_platform()
        if not config:
            return scene

        logger.trace("Adding bisecting platform shortcut")
        reconciled = choose_random(config)
        self._do_add_bisecting_platform(
            scene,
            room_dim,
            blocking_wall=reconciled.has_blocking_wall,
            platform_height=(0.5 if reconciled.is_short else 1),
            double_blocking_wall=reconciled.has_double_blocking_wall,
            long_blocking_wall=reconciled.has_long_blocking_wall,
            is_thin=reconciled.is_thin,
            # Use all of the other_platforms from the source config.
            other_platforms=(
                config.other_platforms
                if isinstance(config.other_platforms, list)
                else [config.other_platforms]
            ) if config.other_platforms else [],
            position_z=choose_random(reconciled.position_z, float)
        )

        return scene

    def _do_add_bisecting_platform(
        self,
        scene: Scene,
        room_dim: Vector3d,
        blocking_wall: bool = False,
        platform_height: float = 1,
        double_blocking_wall: bool = False,
        long_blocking_wall: bool = False,
        is_thin: bool = False,
        other_platforms: List[StructuralPlatformConfig] = None,
        position_z: float = None
    ) -> None:

        # Second platform is the wall to prevent performer from moving too
        # far before getting off the platform.  Since walls go to the
        # ceiling and platforms all start on the floor, we overlap this
        # platform.

        bounds = find_bounds(scene)
        half_room_z = room_dim.z / 2.0
        performer_z = -half_room_z + 0.5
        if position_z is not None and -half_room_z < position_z < half_room_z:
            performer_z = position_z
        scale_x = 0.5 if is_thin else 1
        platform_config = StructuralPlatformConfig(
            num=1, position=VectorFloatConfig(0, 0, 0), rotation_y=0,
            scale=VectorFloatConfig(scale_x, platform_height, room_dim.z))

        # Create the blocking wall.
        wall_position_z = 0 if long_blocking_wall else (performer_z + 1)
        if double_blocking_wall:
            wall_position_z = -half_room_z + 3
        blocking_wall_config = StructuralPlatformConfig(
            num=1,
            material=materials.BLACK.material,
            position=VectorFloatConfig(0, 0, wall_position_z),
            rotation_y=0,
            scale=VectorFloatConfig(
                scale_x - 0.01,
                platform_height + 0.25,
                (scene.room_dimensions.z - 3) if long_blocking_wall else 0.25
            )
        )

        scene.set_performer_start_position(
            x=0, y=platform_config.scale.y, z=performer_z)
        # Start looking down if the room is short.
        rotation_x = (10 if scene.room_dimensions.z <= 8 else 0)
        scene.set_performer_start_rotation(rotation_x, 0)

        platform_instance = FeatureCreationService.create_feature(
            scene,
            FeatureTypes.PLATFORMS,
            platform_config,
            # Use a copy of the bounds list here because we want to ignore the
            # bounds of the new platform within this function.
            bounds.copy()
        )[0]

        if blocking_wall or long_blocking_wall or double_blocking_wall:
            wall = FeatureCreationService.create_feature(
                scene,
                FeatureTypes.PLATFORMS,
                blocking_wall_config,
                bounds.copy()
            )[0]
            wall['id'] = wall['id'].replace('platform', 'blocking_wall')
        if double_blocking_wall:
            blocking_wall_config.position.z = -blocking_wall_config.position.z
            wall = FeatureCreationService.create_feature(
                scene,
                FeatureTypes.PLATFORMS,
                blocking_wall_config,
                bounds.copy()
            )[0]
            wall['id'] = wall['id'].replace('platform', 'blocking_wall')

        for other_config in (other_platforms or []):
            if not other_config.material:
                other_config.material = platform_instance['materials']
            FeatureCreationService.create_feature(
                scene,
                FeatureTypes.PLATFORMS,
                other_config,
                bounds.copy()
            )

        return find_bounds(scene)

    def _add_triple_door_shortcut(self, scene, room_dim):
        if config := self.get_shortcut_triple_door_choice():
            logger.trace("Adding triple door occluding choice shortcut")
            self._do_add_triple_door_shortcut(
                scene, room_dim, config=config)
        return scene

    def _add_double_door_shortcut(self, scene, room_dim):
        if config := self.get_shortcut_double_door_choice():
            logger.trace("Adding double door occluding choice shortcut")
            self._do_add_double_door_shortcut(
                scene, room_dim, config=config)
        return scene

    def _add_platform_extension(
        self,
        scene: Scene,
        platform: SceneObject,
        extension_length: float,
        extension_position: float,
        bounds: List[ObjectBounds]
    ) -> List[ObjectBounds]:
        """Add an extension to the far end of a platform, and return the new
        list of bounding boxes."""
        room_dimensions = scene.room_dimensions
        platform_scale = platform['shows'][0]['scale']
        height = platform_scale['y']
        max_extension_length = (room_dimensions.x - platform_scale['x']) / 2.0
        length = round(
            random.uniform(EXTENSION_LENGTH_MIN, max_extension_length), 4
        ) if extension_length is None else extension_length
        position_x = 0.0001 + (length + platform_scale['x']) / 2.0
        max_extension_z = (room_dimensions.z / 2.0) - EXTENSION_WIDTH
        position_z = round(
            random.uniform(EXTENSION_WIDTH / 2.0, max_extension_z), 4
        ) if extension_position is None else abs(extension_position)
        is_left_side = (
            random.choice([True, False]) if extension_position is None else
            (extension_position < 0)
        )
        if is_left_side:
            position_x *= -1
        platform_extension_config = StructuralPlatformConfig(
            num=1,
            material=platform['materials'],
            position=VectorFloatConfig(position_x, 0, position_z),
            rotation_y=0,
            scale=VectorFloatConfig(length, height, EXTENSION_WIDTH),
            labels=['platform_extension']
        )
        platform_extension = FeatureCreationService.create_feature(
            scene,
            FeatureTypes.PLATFORMS,
            platform_extension_config,
            bounds
        )[0]
        if platform.get('lips', {}).get('gaps'):
            lips_property = 'left' if is_left_side else 'right'
            divisor = room_dimensions.z
            platform['lips']['gaps'][lips_property].append({
                'high': 0.5 + (position_z + (EXTENSION_WIDTH / 2.0)) / divisor,
                'low': 0.5 + (position_z - (EXTENSION_WIDTH / 2.0)) / divisor
            })
            platform_extension['lips'] = {
                'back': True,
                'front': True,
                'left': is_left_side,
                'right': not is_left_side
            }
        return bounds

    def _do_add_triple_door_shortcut(
            self, scene, room_dim, config: TripleDoorConfig):
        if config is None:
            config = TripleDoorConfig()
        dropping = (
            config.start_drop_step is not None and config.start_drop_step > 0)
        room_dim.y = max(room_dim.y, DOOR_OCCLUDER_MIN_ROOM_Y)
        add_y = room_dim.y if dropping else 0
        bounds = self._do_add_bisecting_platform(scene, room_dim, False, 2)
        plat = scene.objects[-1]

        default_wall_height = 4.25

        if config.wall_height:
            default_wall_height = config.wall_height

        if config.bigger_far_end:
            # Create a bigger platform on top of the existing platform.
            bigger_platform = StructuralPlatformConfig(
                num=1,
                material=plat['materials'],
                position=VectorFloatConfig(0, 0, room_dim.z / 4.0),
                rotation_y=0,
                scale=VectorFloatConfig(2, 2.25, room_dim.z / 2.0)
            )
            FeatureCreationService.create_feature(
                scene,
                FeatureTypes.PLATFORMS,
                bigger_platform,
                []
            )

        if config.add_lips and not config.bigger_far_end:
            plat['lips']['left'] = True
            plat['lips']['right'] = True
            plat['lips']['gaps'] = {
                'left': [{'high': 0.5, 'low': 0}],
                'right': [{'high': 0.5, 'low': 0}]}

        if config.add_extension and not config.bigger_far_end:
            bounds = self._add_platform_extension(
                scene,
                plat,
                config.extension_length,
                config.extension_position,
                bounds
            )

        rot_y = 0
        door_center_template = StructuralDoorConfig(
            num=1, position=VectorFloatConfig(
                0, 2 + add_y, 0), rotation_y=rot_y,
            wall_scale_x=1,
            wall_scale_y=default_wall_height - 2,
            material=config.door_material,
            wall_material=config.wall_material)

        door_index = len(scene.objects)

        door_objs = FeatureCreationService.create_feature(
            scene, FeatureTypes.DOORS, door_center_template, [])
        wall = door_objs[-1]
        wall_mat = wall['materials'][0]
        doors = [door_objs[0]]
        door_mat = door_objs[0]['materials'][0]
        side_wall_scale_x = room_dim.x / 2.0 - 0.5
        side_wall_position_x = side_wall_scale_x / 2.0 + 0.5

        # Note: default_wall_height(4.25)is from height of platform, height of
        # door, plus what we added to the center door top so all top walls
        # line up.
        door_right_template = StructuralDoorConfig(
            num=1, position=VectorFloatConfig(
                side_wall_position_x, add_y, 0), rotation_y=rot_y,
            wall_scale_x=side_wall_scale_x,
            wall_scale_y=default_wall_height,
            wall_material=wall_mat,
            material=door_mat)
        door_left_template = StructuralDoorConfig(
            num=1, position=VectorFloatConfig(
                -side_wall_position_x, add_y, 0), rotation_y=rot_y,
            wall_scale_x=side_wall_scale_x,
            wall_scale_y=default_wall_height,
            wall_material=wall_mat,
            material=door_mat)

        door_objs = FeatureCreationService.create_feature(
            scene, FeatureTypes.DOORS, door_right_template, [])
        doors.append(door_objs[0])
        door_objs = FeatureCreationService.create_feature(
            scene, FeatureTypes.DOORS, door_left_template, [])
        doors.append(door_objs[0])
        # Override the bounds of all the doors using a smaller Z dimension so
        # we can position other objects near them. In some scenes we just want
        # the door opened and an object within reach on the other side.
        for door in doors:
            door['shows'][0]['boundingBox'] = geometry.create_bounds(
                dimensions={
                    'x': BASE_DOOR_WIDTH,
                    'y': BASE_DOOR_HEIGHT,
                    'z': 0.25
                },
                offset={'x': 0, 'y': 1, 'z': 0},
                position=door['shows'][0]['position'],
                rotation=door['shows'][0]['rotation'],
                standing_y=0
            )

        if dropping:
            self._add_door_drops(scene, config.start_drop_step,
                                 add_y, door_index)
            if config.add_freeze:
                goal = scene.goal or Goal()
                step_end = (int)(config.start_drop_step + add_y * 4)
                freezes = [StepBeginEnd(1, step_end)]
                ActionService.add_freezes(goal, freezes)
        scene.restrict_open_doors = config.restrict_open_doors

    def _do_add_double_door_shortcut(
            self, scene: Scene, room_dim, config: DoubleDoorConfig):
        if config is None:
            config = DoubleDoorConfig()
        dropping = (
            config.start_drop_step is not None and config.start_drop_step > 0)
        room_dim.y = max(room_dim.y, TWO_DOOR_OCCLUDER_MIN_ROOM_Y)
        add_y = room_dim.y if dropping else 0
        rot_y = 0
        bounds = find_bounds(scene)

        # Add Lava
        if config.add_lava:
            for lava_z in range(-math.floor(room_dim.z / 2),
                                math.floor(room_dim.z / 2) + 1, 1):
                # Put laval down the middle along the Z axis
                lava_template = FloorAreaConfig(
                    num=1, position_x=0, position_z=lava_z)
                FeatureCreationService.create_feature(
                    scene, FeatureTypes.LAVA, lava_template, bounds.copy())

        # Add Platform
        if config.add_platform:
            performer_z = (-room_dim.z / 2.0) + 0.5
            platform_config = StructuralPlatformConfig(
                num=1, position=VectorFloatConfig(
                    0,
                    0,
                    -(room_dim.z / 2) + (config.platform_length / 2)),
                rotation_y=0,
                scale=VectorFloatConfig(
                    config.platform_width,
                    config.platform_height, config.platform_length))
            scene.set_performer_start_position(
                x=0, y=platform_config.scale.y, z=performer_z)
            # Performer starts looking down
            rotation_x = 10
            scene.set_performer_start_rotation(rotation_x, 0)
            FeatureCreationService.create_feature(
                scene,
                FeatureTypes.PLATFORMS,
                platform_config,
                bounds.copy()
            )[0]

        # occluder wall positioning
        if config.occluder_distance_from_performer is not None:
            occluder_position_z = scene.performer_start.position.z + \
                config.occluder_distance_from_performer
        elif config.occluder_wall_position_z is not None:
            occluder_position_z = config.occluder_wall_position_z
        else:
            occluder_position_z = 0

        # Add Doors
        door_index = len(scene.objects)
        side_wall_scale_x = room_dim.x / 2.0
        side_wall_position_x = side_wall_scale_x / 2.0

        door_right_template = StructuralDoorConfig(
            num=1, position=VectorFloatConfig(
                side_wall_position_x, add_y, occluder_position_z),
            rotation_y=rot_y,
            wall_scale_x=side_wall_scale_x,
            wall_scale_y=room_dim.y,
            wall_material=config.wall_material,
            material=config.door_material)

        door_objs = FeatureCreationService.create_feature(
            scene, FeatureTypes.DOORS, door_right_template, [])

        doors = [door_objs[0]]
        wall = door_objs[-1]
        wall_mat = wall['materials'][0]

        door_left_template = StructuralDoorConfig(
            num=1, position=VectorFloatConfig(
                -side_wall_position_x, add_y, occluder_position_z),
            rotation_y=rot_y,
            wall_scale_x=side_wall_scale_x,
            wall_scale_y=room_dim.y,
            wall_material=wall_mat,
            material=door_objs[0]['materials'][0])
        door_objs = FeatureCreationService.create_feature(
            scene, FeatureTypes.DOORS, door_left_template, [])
        doors.append(door_objs[0])
        # Override the bounds of all the doors using a smaller Z dimension so
        # we can position other objects near them. In some scenes we just want
        # the door opened and an object within reach on the other side.
        for door in doors:
            door['shows'][0]['boundingBox'] = geometry.create_bounds(
                dimensions={
                    'x': BASE_DOOR_WIDTH,
                    'y': BASE_DOOR_HEIGHT,
                    'z': 0.25
                },
                offset={'x': 0, 'y': 1, 'z': 0},
                position=door['shows'][0]['position'],
                rotation=door['shows'][0]['rotation'],
                standing_y=0
            )

        if dropping:
            self._add_door_drops(scene, config.start_drop_step,
                                 add_y, door_index)
            if config.add_freeze:
                goal = scene.goal or Goal()
                step_end = (int)(config.start_drop_step + add_y * 4)
                freezes = [StepBeginEnd(1, step_end)]
                ActionService.add_freezes(goal, freezes)
        scene.restrict_open_doors = config.restrict_open_doors

    def _add_door_drops(self, scene: Scene,
                        start_drop_step, add_y, door_index):
        for i in range(door_index, len(scene.objects)):
            obj = scene.objects[i]
            obj['shows'][0]['boundingBox'].extend_bottom_to_ground()
            moves = []
            obj['moves'] = moves
            moves.append({
                "stepBegin": start_drop_step,
                "stepEnd": start_drop_step + add_y * 4 - 1,
                "vector": {
                    "x": 0,
                    "y": -0.25,
                    "z": 0
                }
            })

    def _add_lava_shortcut(self, scene: Scene, room_dim: Vector3d):
        if self.get_shortcut_lava_room():
            logger.trace("Adding lava shortcut")
            bounds = find_bounds(scene)
            # position performer in the center non-lava part,
            # in the back of the room, facing forward.
            scene.set_performer_start_position(
                0, scene.performer_start.position.y or 0,
                -1 * (room_dim.z / 2.0) + 0.5)
            scene.set_performer_start_rotation(0, random.randint(-90, 90))

            FeatureCreationService.create_feature(
                scene, FeatureTypes.PARTITION_FLOOR,
                PartitionFloorConfig(
                    2.0 / 3.0, 2.0 / 3.0), bounds)

        return scene

    def _delay_performer_placement(self, scene: Scene, room_dim: Vector3d):
        if not self.get_shortcut_start_on_platform():
            return scene

        self._delayed_perf_pos = True
        logger.trace("Delaying start on platform shortcut")

        # Place performer outside of room until their
        # start platform is created
        scene.set_performer_start_position(room_dim.x, 0, room_dim.z)

        return scene

    def _position_performer_on_platform(self, scene):
        logger.trace("Adding start on platform shortcut")
        obj_repo = ObjectRepository.get_instance()

        bounds = find_bounds(scene)

        structs = obj_repo.get_all_from_labeled_objects(
            self.LABEL_START_PLATFORM
        )
        if structs is None:
            raise ILEException(
                f"Attempt to position performer on chosen "
                f"platform failed due to missing platform with "
                f"'{self.LABEL_START_PLATFORM}' label.")

        attempts = 0
        valid = False
        for struct in structs:
            if attempts == len(structs):
                raise ILEException(
                    f"Attempt to position performer on chosen "
                    f"platform failed. Unable to place performer "
                    f"on platform with '{self.LABEL_START_PLATFORM}' "
                    f"label.")
            struct_pos = struct.instance['shows'][0]['position']
            struct_scale = struct.instance['shows'][0]['scale']

            # If platform found, choose random position on platform
            # Note: the 0.1 with padding is accounting for platform lips/
            # not being placed too close to the edge
            padding = 0.1 + geometry.PERFORMER_HALF_WIDTH
            min_x = struct_pos['x'] - ((struct_scale['x'] / 2.0) - padding)
            max_x = struct_pos['x'] + ((struct_scale['x'] / 2.0) - padding)
            min_z = struct_pos['z'] - ((struct_scale['z'] / 2.0) - padding)
            max_z = struct_pos['z'] + ((struct_scale['z'] / 2.0) - padding)

            perf_pos = {}
            for _ in range(MAX_TRIES):

                perf_pos = Vector3d(
                    x=round(random.uniform(min_x, max_x), 3),
                    y=struct_scale['y'],
                    z=round(random.uniform(min_z, max_z), 3)
                )

                max_y = scene.room_dimensions.y - \
                    geometry.PERFORMER_HEIGHT

                if perf_pos.y > max_y:
                    # platform is too tall
                    break

                new_perf_bounds = geometry.create_bounds(
                    dimensions={
                        "x": geometry.PERFORMER_WIDTH,
                        "y": geometry.PERFORMER_HEIGHT,
                        "z": geometry.PERFORMER_WIDTH
                    },
                    offset=None,
                    position=vars(perf_pos),
                    rotation=vars(scene.performer_start.rotation),
                    standing_y=0
                )

                valid = geometry.validate_location_rect(
                    location_bounds=new_perf_bounds,
                    performer_start_position=vars(
                        scene.performer_start.position),
                    bounds_list=bounds,
                    room_dimensions=vars(scene.room_dimensions)
                )

                if valid:
                    break

            attempts += 1
            if valid:
                scene.performer_start.position = perf_pos
                self._delayed_perf_pos = False
                self._delayed_perf_pos_reason = None
        if not valid:
            raise ILEException(
                f"Attempt to position performer on chosen "
                f"platform failed. Unable to place performer "
                f"on platform with '{self.LABEL_START_PLATFORM}' label.")

    def _add_tool_lava_goal(self, scene: Scene, room_dim: Vector3d):
        last_exception = None
        source_config = self.get_shortcut_lava_target_tool()
        if not source_config:
            return scene
        config = choose_random(source_config)
        logger.trace("Adding tool to goal shortcut")
        num_prev_objs = len(scene.objects)
        num_prev_lava = len(scene.lava)

        # Do not use choose_random for the distance_between_performer_and_tool.
        # Keep the source config for now.
        distance_between_performer_and_tool = (
            source_config.distance_between_performer_and_tool
        )
        if isinstance(distance_between_performer_and_tool, list):
            # For lists, choose a random configuration from it.
            distance_between_performer_and_tool = random.choice(
                distance_between_performer_and_tool
            )

        if config.guide_rails and (
            config.tool_rotation or
                config.tool_type == TOOL_TYPES.INACCESSIBLE or
                config.tool_type == TOOL_TYPES.BROKEN):
            raise ILEException(
                "Unable to use 'guide_rails' and 'tool_rotation' or "
                "tool_types: 'inaccessible' or 'broken' from "
                "shortcut_lava_target_tool at the same time")
        if (distance_between_performer_and_tool is not None and
                config.random_performer_position):
            raise ILEException(
                "Cannot have distance_between_performer_and_tool "
                "and random_performer_position"
            )
        if (distance_between_performer_and_tool is not None and
                config.tool_type == TOOL_TYPES.INACCESSIBLE):
            raise ILEException(
                "Cannot have distance_between_performer_and_tool "
                "or random_performer_position with an "
                "'inaccessible' tool_type"
            )
        if (config.inaccessible_tool_blocking_wall_horizontal_offset is not None and  # noqa
            (abs(config.inaccessible_tool_blocking_wall_horizontal_offset) <
             INACCESSIBLE_TOOL_BLOCKING_WALL_MINIMUM_SEPARATION)):
            raise ILEException(
                "The minimum separation of the inaccessible tool blocking "
                "wall should always be greater than or equal to "
                f"{INACCESSIBLE_TOOL_BLOCKING_WALL_MINIMUM_SEPARATION} or "
                f"less than or equal to "
                f"-{INACCESSIBLE_TOOL_BLOCKING_WALL_MINIMUM_SEPARATION}")
        if (max(scene.room_dimensions.x, scene.room_dimensions.z) <
                MIN_LAVA_ISLAND_LONG_ROOM_DIMENSION_LENGTH):
            raise ILEException(
                f"One scene room dimension must be at least "
                f"{MIN_LAVA_ISLAND_LONG_ROOM_DIMENSION_LENGTH} "
                f"to place lava and tool")

        if (min(scene.room_dimensions.x, scene.room_dimensions.z) <
                MIN_LAVA_ISLAND_SHORT_ROOM_DIMENSION_LENGTH):
            raise ILEException(
                f"Scene room dimensions must not be below "
                f"{MIN_LAVA_ISLAND_SHORT_ROOM_DIMENSION_LENGTH} "
                f"to place lava and tool")
        if (
            config.tool_rotation is not None and config.tool_rotation != 0 and
            config.tool_offset_backward_from_lava and
            config.tool_type in L_SHAPED_TOOLS
        ):
            # This can cause the tool to collide with the target.
            raise ILEException(
                f"Cannot set 'tool_offset_backward_from_lava' on 'hooked' and "
                f"'isosceles' tools with a non-zero 'tool_rotation': "
                f"tool_offset_backward_from_lava="
                f"{config.tool_offset_backward_from_lava} "
                f"tool_rotation={config.tool_rotation} "
                f"tool_type={config.tool_type}"
            )

        for _ in range(MAX_TRIES):
            try:
                self.remove_target_on_error = False
                bounds = find_bounds(scene)
                # Test room size and determine sizes
                long_length = max(room_dim.x, room_dim.z)
                short_length = min(room_dim.x, room_dim.z)
                long_key, short_key = (
                    ('z', 'x') if long_length == room_dim.z else (
                        'x', 'z'))

                # place performer
                start = scene.performer_start.position
                setattr(start, long_key, - (long_length / 2.0 - 0.5))
                scene.performer_start.rotation.y = (
                    0 if long_key == 'z' else 90)

                sizes = self._compute_lava_sizes(
                    long_length, short_length, config)

                setattr(
                    start,
                    short_key,
                    0 if sizes.island_size %
                    2 == 1 else 0.5)

                tool_length = (
                    sizes.rear +
                    sizes.front +
                    sizes.island_size)

                if config.tool_type in L_SHAPED_TOOLS:
                    tool_length = random.randint(
                        tool_length + HOOKED_TOOL_BUFFER, MAX_TOOL_LENGTH)
                if config.tool_type == TOOL_TYPES.SMALL:
                    tool_length = 1

                # if size 13, edge is whole tiles at 6, buffer should be 6,
                # if size 14, edge is half tile at 7, buffer should be 6

                # buffer here not used for hooked tools
                far_island_buffer = (
                    1 if config.tool_type not in L_SHAPED_TOOLS else 0
                )
                # additional buffer of lava needed for hooked tool scenes
                # with even sized long dimension
                rear_lava_buffer = (
                    1 if config.tool_type in L_SHAPED_TOOLS and
                    long_length % 2 == 0 else 0
                )

                long_buffer_coord = math.floor(long_length / 2.0 - 0.5)
                long_far_island_coord = (
                    long_buffer_coord - sizes.rear - far_island_buffer)
                long_near_island_coord = (
                    long_far_island_coord - sizes.island_size + 1)
                short_left_island_coord = - \
                    math.floor((sizes.island_size - 1) / 2)
                short_right_island_coord = math.ceil(
                    (sizes.island_size - 1) / 2.0)

                # start point for tool and target along short length axis
                # (line up with middle of island)
                short_coord = (0 if sizes.island_size % 2 == 1 else 0.5)

                # Find or create the target and position it on the island
                if not config.random_target_position:
                    self._add_target_to_lava_island(
                        scene,
                        long_key,
                        short_key,
                        short_coord,
                        long_far_island_coord,
                        long_near_island_coord
                    )
                    target = scene.objects[-1]

                # Encircle island with lava
                self._add_lava_around_island(
                    scene, bounds, long_key, sizes,
                    list(
                        range(
                            long_near_island_coord,
                            long_far_island_coord +
                            1)),
                    list(
                        range(
                            short_left_island_coord,
                            short_right_island_coord +
                            1)),
                    rear_lava_buffer
                )

                # Add the island to the bounds list so that no additional
                # objects will be randomly positioned there in the future.
                island_bounds = self._find_island_bounds(
                    long_key,
                    long_far_island_coord,
                    long_near_island_coord,
                    short_left_island_coord,
                    short_right_island_coord)

                # Add block tool
                tool_shape = get_tool_shape(
                    tool_length, config.tool_type)
                tool = self._add_tool(
                    scene,
                    bounds + [island_bounds],
                    sizes.island_size,
                    long_key,
                    short_key,
                    short_coord,
                    sizes.front,
                    tool_length,
                    long_near_island_coord,
                    config.tool_type,
                    tool_shape,
                    config.tool_rotation,
                    config.tool_horizontal_offset,
                    config.tool_offset_backward_from_lava,
                    config.inaccessible_tool_blocking_wall_horizontal_offset)

                if config.guide_rails:
                    self._add_guide_rails(scene, long_key, short_key,
                                          tool_length, target, tool)

                # Create the target and position it randomly, if needed
                if config.random_target_position:
                    targets = scene.get_targets()
                    target = random.choice(targets) if targets else None
                    if not target:
                        # Ensure the bounds list is up-to-date.
                        bounds = find_bounds(scene)
                        self._add_lava_target(
                            scene,
                            None,
                            bounds + [island_bounds]
                        )
                        target = scene.objects[-1]

                if config.random_performer_position:
                    if config.tool_type == TOOL_TYPES.INACCESSIBLE:
                        self._place_performer_in_inaccessible_zone(
                            scene, short_key, long_key,
                            long_near_island_coord,
                            sizes.front,
                            tool.room_wall_pos_cutoff,
                            tool.blocking_wall_pos_cutoff)
                    else:
                        self._randomize_performer_position(
                            scene,
                            long_key, short_key, long_near_island_coord,
                            long_far_island_coord, sizes)

                elif distance_between_performer_and_tool is not None:
                    if isinstance(distance_between_performer_and_tool, float):
                        distance_between_performer_and_tool = MinMaxFloat(
                            min=distance_between_performer_and_tool,
                            max=distance_between_performer_and_tool
                        )
                    referenced_tool = tool
                    func = geometry.get_position_distance_away_from_obj
                    bounds_list = bounds + [island_bounds]
                    if config.tool_type == TOOL_TYPES.BROKEN:
                        referenced_tool = random.choice(tool)
                    elif config.tool_type in L_SHAPED_TOOLS:
                        func = geometry.get_position_distance_away_from_hooked_tool  # noqa
                        # QUESTION: Why is this different?
                        bounds_list = find_bounds(scene) + [island_bounds]
                    try:
                        (x, z) = func(
                            scene.room_dimensions,
                            referenced_tool,
                            distance_between_performer_and_tool.min,
                            distance_between_performer_and_tool.max,
                            bounds_list
                        )
                        scene.set_performer_start_position(x=x, y=0, z=z)
                    except Exception as e:
                        raise ILEException(
                            f'Cannot find any valid locations for '
                            f'"distance_between_performer_and_tool" (in the '
                            f'"shortcut_lava_target_tool" config option) of '
                            f'{distance_between_performer_and_tool}'
                        ) from e

                return scene

            except Exception as e:
                last_exception = e
                logger.debug(
                    "failed to create lava island with tool due to",
                    exc_info=last_exception,
                )

                # remove added objects on failure
                scene.objects = scene.objects[:num_prev_objs]
                scene.lava = scene.lava[:num_prev_lava]
                if self.remove_target_on_error:
                    meta = (scene.goal or Goal()).metadata or {}
                    if 'target' in meta:
                        meta.pop('target')
                config = choose_random(source_config)

        raise ILEException(
            "Failed to create lava island with tool") from last_exception

    def _add_lava_tool_choice_goal(self, scene: Scene, room_dim: Vector3d):
        last_exception = None
        config = self.get_shortcut_tool_choice()
        if not config:
            return scene
        logger.trace("Adding mirrored lava tool shortcut")
        num_prev_objs = len(scene.objects)
        num_prev_lava = len(scene.lava)

        # X minimum has to account for two pools of lava, plus platform,
        # with enough space around each to reach the ball.
        # Z minimum is simply the long room dimension min for lava islands
        if (scene.room_dimensions.x < MIN_TOOL_CHOICE_X_DIMENSION):
            raise ILEException(
                f"X-axis room dimension must not be below "
                f"{MIN_TOOL_CHOICE_X_DIMENSION} "
                f"to place mirrored lava islands")

        if (scene.room_dimensions.z <
                MIN_LAVA_ISLAND_LONG_ROOM_DIMENSION_LENGTH):
            raise ILEException(
                f"Z-axis room dimension must not be below "
                f"{MIN_LAVA_ISLAND_LONG_ROOM_DIMENSION_LENGTH} "
                f"to place mirrored lava islands")

        # Get the dimensions for one side of the platform,
        # in order to create each lava island on either side
        x_dim = math.floor(room_dim.x / 2.0 - 0.5)
        one_side_dim = Vector3d(x=x_dim, y=0, z=room_dim.z)

        for _ in range(MAX_TRIES):
            try:
                self.remove_target_on_error = False

                # Add bisecting platform and place performer on it
                self._do_add_bisecting_platform(
                    scene,
                    room_dim,
                    blocking_wall=False,
                    long_blocking_wall=False
                )

                bounds = find_bounds(scene)
                # Test room size and determine sizes
                # "Long length" in this case should always be z,
                # since the bisecting platform always runs
                # along the z axis.
                long_length = one_side_dim.z
                short_length = one_side_dim.x
                long_key, short_key = ('z', 'x')

                # Limit these widths a bit more than defaults for
                # mirrored lava scenes
                choose_island_size = random.randint(1, 3)
                left_right_width = MIN_LAVA_WIDTH

                (island_size, front, rear) = self._get_island_and_lava_size_by_dimension(  # noqa
                    long_length,
                    choose_island_size,
                    None,
                    None,
                    True,
                    "front_lava_width",
                    "rear_lava_width",
                    TOOL_TYPES.RECT)
                (_, left, right) = self._get_island_and_lava_size_by_dimension(
                    short_length,
                    island_size,
                    left_right_width,
                    left_right_width,
                    False,
                    "left_lava_width",
                    "right_lava_width",
                    TOOL_TYPES.RECT)

                sizes = LavaIslandSizes(island_size, front, rear, left, right)

                # Ensuring gap of 1 here between platform and lava
                short_length_offset = math.floor(1.5 + left + (island_size / 2.0))  # noqa

                tool_length = (
                    sizes.rear +
                    sizes.front +
                    sizes.island_size)

                # this buffer is not needed for mirrored lava scenes (for
                # now), so set to 0
                rear_lava_buffer = 0

                # if size 13, edge is whole tiles at 6, buffer should be 6,
                # if size 14, edge is half tile at 7, buffer should be 6
                long_buffer_coord = math.floor(long_length / 2.0 - 0.5)
                long_far_island_coord = (
                    long_buffer_coord - sizes.rear - 1)
                long_near_island_coord = (
                    long_far_island_coord - sizes.island_size + 1)
                orig_short_left_island_coord = - \
                    math.floor((sizes.island_size - 1) / 2)
                orig_short_right_island_coord = math.ceil(
                    (sizes.island_size - 1) / 2.0)

                short_left_island_coord = (
                    orig_short_left_island_coord + short_length_offset)
                short_right_island_coord = (
                    orig_short_right_island_coord + short_length_offset)

                is_valid = random.choice([True, False])

                # x-axis coordinate for target and tool on positive x-axis side
                short_coord = (short_length_offset if island_size %
                               2 == 1 else 0.5 + short_length_offset)

                self.create_lava_on_one_side(
                    scene,
                    bounds,
                    config,
                    long_key,
                    short_key,
                    sizes,
                    short_coord,
                    tool_length,
                    rear_lava_buffer,
                    long_far_island_coord,
                    long_near_island_coord,
                    short_left_island_coord,
                    short_right_island_coord,
                    is_valid
                )

                # swap left/right settings for "mirrored" side
                short_left_island_coord = (
                    orig_short_right_island_coord * -1) - short_length_offset
                short_right_island_coord = (
                    orig_short_left_island_coord * -1) - short_length_offset

                sizes.right = left
                sizes.left = right

                # flip short coord
                short_coord = short_coord * -1

                self.create_lava_on_one_side(
                    scene,
                    bounds,
                    config,
                    long_key,
                    short_key,
                    sizes,
                    short_coord,
                    tool_length,
                    rear_lava_buffer,
                    long_far_island_coord,
                    long_near_island_coord,
                    short_left_island_coord,
                    short_right_island_coord,
                    not is_valid
                )

                # Add forced rotation at the beginning of tool choice scenes
                scene.goal.action_list = ([['RotateRight']] * 36)

                return scene
            except Exception as e:
                last_exception = e
                logger.debug(
                    "failed to create mirrored lava island tool scene due to",
                    exc_info=last_exception,
                )

                # remove added objects on failure
                scene.objects = scene.objects[:num_prev_objs]
                scene.lava = scene.lava[:num_prev_lava]
                if self.remove_target_on_error:
                    meta = (scene.goal or Goal()).metadata or {}
                    if 'target' in meta:
                        meta.pop('target')
                config = self.get_shortcut_tool_choice()

        raise ILEException(
            "Failed to create mirrored lava islands") from last_exception

    def create_lava_on_one_side(self, scene, bounds,
                                config: ToolChoiceConfig,
                                long_key,
                                short_key, sizes, short_coord,
                                tool_length, rear_lava_buffer,
                                long_far_island_coord,
                                long_near_island_coord,
                                short_left_island_coord,
                                short_right_island_coord,
                                valid_tool=True):

        # Find or create the target and position it on the island
        if (valid_tool):
            self._add_target_to_lava_island(
                scene,
                long_key,
                short_key,
                short_coord,
                long_far_island_coord,
                long_near_island_coord
            )

            # Make duplicate of target for the opposite side of the platform
            non_target_config = InteractableObjectConfig(
                keyword_location=KeywordLocationConfig(
                    KeywordLocation.OPPOSITE_X,
                    relative_object_label="target"),
                labels='non_target',
                shape='soccer_ball',
                identical_to='target'
            )

            create_user_configured_interactable_object(
                scene,
                bounds,
                non_target_config,
                is_target=False
            )

        # Encircle island with lava
        self._add_lava_around_island(
            scene, bounds, long_key, sizes,
            list(
                range(
                    long_near_island_coord,
                    long_far_island_coord +
                    1)),
            list(
                range(
                    short_left_island_coord,
                    short_right_island_coord +
                    1)),
            rear_lava_buffer
        )

        # Add the island to the bounds list so that no additional
        # objects will be randomly positioned there in the future.
        island_bounds = self._find_island_bounds(
            long_key,
            long_far_island_coord,
            long_near_island_coord,
            short_left_island_coord,
            short_right_island_coord)

        # Add block tool
        if (valid_tool):
            tool_shape = get_tool_shape(tool_length, TOOL_TYPES.RECT)
        else:
            # if improbable_option set to no_tool, nothing left to do, return
            if (config.improbable_option == ImprobableToolOption.NO_TOOL):
                return

            tool_shape = self._get_too_small_tool()
            tool_length = LARGE_BLOCK_TOOLS_TO_DIMENSIONS[tool_shape][1]

        self._add_tool(
            scene,
            bounds + [island_bounds],
            sizes.island_size,
            long_key,
            short_key,
            short_coord,
            sizes.front,
            tool_length,
            long_near_island_coord,
            TOOL_TYPES.RECT,
            tool_shape,
            tool_rotation=0
        )

    def _find_island_bounds(self, long_key, long_far_island_coord,
                            long_near_island_coord, short_left_island_coord,
                            short_right_island_coord):
        long_points = sorted([
            long_near_island_coord,
            long_far_island_coord
        ])
        short_points = sorted([
            short_left_island_coord,
            short_right_island_coord
        ])
        x_points = (
            long_points if long_key == 'x' else short_points
        )
        z_points = (
            long_points if long_key == 'z' else short_points
        )
        island_bounds = ObjectBounds(box_xz=[
            Vector3d(x=x_points[0] - 0.5, y=0, z=z_points[1] + 0.5),
            Vector3d(x=x_points[1] + 0.5, y=0, z=z_points[1] + 0.5),
            Vector3d(x=x_points[1] + 0.5, y=0, z=z_points[0] - 0.5),
            Vector3d(x=x_points[0] - 0.5, y=0, z=z_points[0] - 0.5)
        ], max_y=1000, min_y=0)

        return island_bounds

    def _add_guide_rails(self, scene, long_key,
                         short_key, tool_length, target, tool):
        tool_pos = tool['shows'][0]['position']
        rot = tool['shows'][0]['rotation']['y']
        end_guide_rail = copy.deepcopy(target['shows'][0]['position'])
        center = VectorIntConfig(y=tool_pos['y'])
        if any([tool_type in tool['type'] for tool_type in L_SHAPED_TOOLS]):
            max_long_dim = (scene.room_dimensions.z if short_key ==
                            'x' else scene.room_dimensions.x) / 2.0
            end_guide_rail[short_key] = tool_pos[short_key]
            end_guide_rail[long_key] = max_long_dim

        setattr(
            center,
            short_key,
            end_guide_rail[short_key])

        c = ((
            end_guide_rail[long_key] + tool_pos[long_key] -
            tool_length / 2.0) / 2.0)
        setattr(center, long_key, c)
        length = (end_guide_rail[long_key] - tool_pos[long_key] +
                  tool_length / 2.0)
        width, _ = LARGE_BLOCK_TOOLS_TO_DIMENSIONS[
            tool['type']]
        mat = self._get_guide_rail_material_tuple(scene)
        rails = create_guide_rails_around(
            position_x=center.x, position_z=center.z,
            rotation_y=rot,
            length=length, width=width, material_tuple=mat,
            bounds=[])
        scene.objects += rails

    def _get_guide_rail_material_tuple(
            self, scene: Scene) -> materials.MaterialTuple:
        invalid_mats = [(scene.ceiling_material or ""),
                        (scene.floor_material or ""),
                        (scene.wall_material or "")]
        invalid_mats = set(invalid_mats)
        room_mats = vars(scene.room_materials) if scene.room_materials else {}
        for mat in room_mats.values():
            invalid_mats.add(mat)
        valid = False
        while (not valid):
            mat = random.choice(materials.ROOM_WALL_MATERIALS)
            valid = mat[0] not in invalid_mats
        return mat

    def _randomize_performer_position(self, scene: Scene,
                                      long_key, short_key,
                                      long_near_island_coord,
                                      long_far_island_coord,
                                      sizes: LavaIslandSizes):
        no_go_long_min = long_near_island_coord - sizes.front - 0.5
        no_go_long_max = long_far_island_coord + sizes.rear + 0.5

        # for island size 1, 2, 3; island bounds are :
        # min is -0.5, -0.5, -1.5
        # max is 0.5, 1.5, 1.5
        no_go_short_min = math.floor(-sizes.island_size / 2.0) + \
            0.5 - sizes.left
        no_go_short_max = math.floor(
            sizes.island_size / 2.0) + 0.5 + sizes.right

        # here 0.5 is a buffer so the performer doesn't end up in the wall
        long_extent = getattr(scene.room_dimensions, long_key) / 2.0 - 0.5
        short_extent = getattr(scene.room_dimensions, short_key) / 2.0 - 0.5
        template = VectorFloatConfig(y=0)
        setattr(template, long_key, MinMaxFloat(-long_extent, long_extent))
        setattr(template, short_key, MinMaxFloat(-short_extent, short_extent))

        for _ in range(MAX_TRIES):
            pos = choose_random(template)
            if (no_go_long_min <= getattr(pos, long_key) <= no_go_long_max and
                    no_go_short_min <= getattr(
                    pos, short_key) <= no_go_short_max):
                continue
            for obj in scene.objects:
                if not geometry.validate_location_rect(
                        obj['shows'][0]['boundingBox'], vars(pos), [],
                        vars(scene.room_dimensions)):
                    continue
            scene.set_performer_start_position(pos.x, None, pos.z)
            return
        raise ILEException("Failed to find random performer location")

    def _place_performer_in_inaccessible_zone(
            self, scene: Scene, short_key, long_key, near_island_coord,
            front_lava_width, range_one, range_two):
        max_pos_touching_lava = (
            near_island_coord - front_lava_width -
            0.5 - geometry.PERFORMER_HALF_WIDTH)
        min_against_wall_pos = (-getattr(scene.room_dimensions, long_key) / 2 +
                                geometry.PERFORMER_HALF_WIDTH)

        for _ in range(MAX_TRIES):
            long_pos = round(random.uniform(
                min_against_wall_pos, max_pos_touching_lava), 2)
            short_pos = round(random.uniform(range_one, range_two), 2)
            x = short_pos if short_key == 'x' else long_pos
            z = short_pos if short_key == 'z' else long_pos

            new_perf_bounds = geometry.create_bounds(
                dimensions={
                    "x": geometry.PERFORMER_WIDTH,
                    "y": geometry.PERFORMER_HEIGHT,
                    "z": geometry.PERFORMER_WIDTH
                },
                offset=None,
                position=vars(Vector3d(x=x, y=0, z=z)),
                rotation=vars(scene.performer_start.rotation),
                standing_y=0
            )

            valid = geometry.validate_location_rect(
                location_bounds=new_perf_bounds,
                performer_start_position=vars(
                    scene.performer_start.position),
                bounds_list=find_bounds(scene),
                room_dimensions=vars(scene.room_dimensions)
            )

            if valid:
                scene.set_performer_start_position(x, None, z)
                return
        raise ILEException(
            "Failed to find valid performer location inside "
            "inaccessible tool zone")

    def _add_target_to_lava_island(
            self, scene: Scene, long_key, short_key, short_coord,
            long_far_island_coord, long_near_island_coord):
        targets = scene.get_targets()
        target = random.choice(targets) if targets else None

        # put target in middle of island
        pos = VectorFloatConfig()
        pos.y = 0
        long_coord = (long_far_island_coord +
                      long_near_island_coord) / 2.0
        setattr(pos, short_key, short_coord)
        setattr(pos, long_key, long_coord)

        if target is not None:
            rot = target['shows'][0]['rotation']
            location = {
                'position': {'x': pos.x, 'y': pos.y, 'z': pos.z},
                'rotation': rot
            }
            geometry.move_to_location(
                object_instance=target,
                object_location=location)
        else:
            self._add_lava_target(scene, pos)

    def _add_lava_target(
        self,
        scene: Scene,
        position: VectorFloatConfig,
        bounds_list: List[ObjectBounds] = None
    ) -> None:
        self.remove_target_on_error = True
        goal_template = GoalConfig(
            category=tags.SCENE.RETRIEVAL,
            target=InteractableObjectConfig(
                shape='soccer_ball',
                position=position,
                scale=MinMaxFloat(1.0, 3.0)))
        GoalServices.attempt_to_add_goal(scene, goal_template)

    def _add_tool(self, scene, bounds, island_size, long_key, short_key,
                  short_coord, front_lava_width, tool_length,
                  long_near_island_coord, tool_type, tool_shape,
                  tool_rotation=None,
                  tool_horizontal_offset=0,
                  tool_offset_backward_from_lava=0,
                  blocking_wall_horizontal_offset=None):
        bounds_to_check = bounds
        tool_rot = 0 if long_key == 'z' else 90
        if tool_rotation is None:
            # If tool_offset_backward_from_lava is set, a non-zero rotation can
            # cause a hooked or isosceles tool to collide with the target.
            if tool_type in L_SHAPED_TOOLS and tool_offset_backward_from_lava:
                tool_rotation = 0
            elif tool_type in [TOOL_TYPES.INACCESSIBLE, TOOL_TYPES.BROKEN]:
                tool_rotation = 0
            else:
                tool_rotation = random.choice(geometry.VALID_ROTATIONS)
        tool_rot += tool_rotation
        tool_pos = VectorFloatConfig(y=0)
        long_tool_pos = (long_near_island_coord -
                         front_lava_width - tool_length / 2.0 - 0.5)
        setattr(tool_pos, short_key, short_coord)

        if tool_type == TOOL_TYPES.INACCESSIBLE:
            if not blocking_wall_horizontal_offset:
                # If no value is setup use the island size to minimum range
                # as a default offset
                negative = round(random.uniform(-island_size, -0.5), 2)
                positive = round(random.uniform(0.5, island_size), 2)
                blocking_wall_horizontal_offset = \
                    random.choice([negative, positive])
            tool_horizontal_offset = abs(tool_horizontal_offset) * \
                (-1 if blocking_wall_horizontal_offset < 0 else 1)
            material = random.choice(materials.CUSTOM_WOOD_MATERIALS)
            (tool, wall, width_direction, blocking_wall_pos_cutoff,
             room_wall_pos_cutoff) = create_inaccessible_tool(
                tool_type=tool_shape,
                long_direction=long_key,
                short_direction=short_key,
                original_short_position=short_coord,
                original_long_position=long_tool_pos,
                tool_horizontal_offset=tool_horizontal_offset,
                tool_offset_backward_from_lava=tool_offset_backward_from_lava,
                blocking_wall_horizontal_offset=blocking_wall_horizontal_offset,  # noqa
                tool_rotation_y=tool_rot,
                room_dimension_x=scene.room_dimensions.x,
                room_dimension_z=scene.room_dimensions.z,
                blocking_wall_material=material,
                bounds=None
            )
            scene.objects.append(tool)
            scene.objects.append(wall)

            valid = geometry.validate_location_rect(
                location_bounds=tool['shows'][0]['boundingBox'],
                performer_start_position=vars(
                    scene.performer_start.position),
                bounds_list=find_bounds(
                    scene=scene, ignore_ids=tool['id']),
                room_dimensions=vars(scene.room_dimensions)
            )
            if not valid:
                scene.objects = scene.objects[:-2]
                raise ILEException(
                    "Inaccessible tool position is outside of the room "
                    "or obstructed."
                )
            valid = geometry.validate_location_rect(
                location_bounds=wall['shows'][0]['boundingBox'],
                performer_start_position=vars(
                    scene.performer_start.position),
                bounds_list=find_bounds(
                    scene=scene, ignore_ground=True, ignore_ids=wall['id']),
                room_dimensions=vars(scene.room_dimensions)
            )
            if not valid:
                scene.objects = scene.objects[:-2]
                raise ILEException(
                    "Inaccessible tool blocking wall position is outside "
                    "of the room or obstructed."
                )
            tool['debug']['length'] = tool_length
            return InaccessibleToolProperties(
                tool, wall, width_direction,
                blocking_wall_pos_cutoff, room_wall_pos_cutoff)

        # Direction left is negative when long direction is on z axis
        # But positive when long direction is x axis and tool is facing right
        direction_left = 1 if long_key == 'z' else -1
        if tool_type == TOOL_TYPES.BROKEN:
            max_tool_pos = (
                long_near_island_coord - front_lava_width - 1 -
                tool_offset_backward_from_lava)
            min_tool_pos = (
                max_tool_pos - tool_length + 1 -
                tool_offset_backward_from_lava)
            width_position = (
                getattr(tool_pos, short_key) + tool_horizontal_offset *
                direction_left)
            rotation_for_entire_tool = \
                tool_rot if long_key == 'z' else tool_rot - 90
            tools = create_broken_tool(
                object_type=tool_shape,
                direction=long_key,
                width_position=width_position,
                max_broken_tool_length_pos=max_tool_pos,
                min_broken_tool_length_pos=min_tool_pos,
                length=tool_length,
                rotation_for_entire_tool=rotation_for_entire_tool)
            scene.objects.extend(tools)
            for tool in tools:
                valid = geometry.validate_location_rect(
                    location_bounds=tool['shows'][0]['boundingBox'],
                    performer_start_position=vars(
                        scene.performer_start.position),
                    bounds_list=find_bounds(
                        scene=scene, ignore_ids=tool['id']),
                    room_dimensions=vars(scene.room_dimensions)
                )
                if not valid:
                    scene.objects = scene.objects[:-len(tools)]
                    raise ILEException(
                        "A broken tool position is outside of the room "
                        "or obstructed."
                    )
            for tool in tools:
                tool['debug']['length'] = 1
            return tools

        if (tool_type in L_SHAPED_TOOLS):
            bounds_to_check = []
            tool_width = LARGE_BLOCK_TOOLS_TO_DIMENSIONS[tool_shape][0]
            tool_buffer = max(1.0 - (tool_width / 3.0), 0)

            # make sure tool is placed directly behind island
            rear_buffer = 1.0
            lava_front_to_behind_island = (
                front_lava_width +
                island_size + rear_buffer)
            tool_pos_increment = lava_front_to_behind_island - tool_buffer
            long_tool_pos = long_tool_pos + tool_pos_increment
            short_coord = short_coord + (tool_buffer / 2.0 * direction_left)
            tool_offset_backward_from_lava *= -1

        setattr(tool_pos, short_key,
                short_coord + tool_horizontal_offset * direction_left)
        setattr(tool_pos, long_key,
                long_tool_pos - round(tool_offset_backward_from_lava, 4))
        tool_template = ToolConfig(
            num=1,
            position=tool_pos,
            rotation_y=tool_rot,
            shape=tool_shape)
        FeatureCreationService.create_feature(
            scene, FeatureTypes.TOOLS, tool_template, bounds_to_check)
        # helps with distance_between_performer_and_tool calculations for
        # hooked bounding box shapes
        tool = scene.objects[-1]
        if tool_type == TOOL_TYPES.HOOKED:
            tool['debug']['tool_thickness'] = tool_width / 3.0
        if tool_type == TOOL_TYPES.ISOSCELES:
            tool['debug']['tool_thickness'] = tool_length
        tool['debug']['length'] = tool_length
        return tool

    def _add_asymmetric_lava_around_island(
            self,
            scene: Scene,
            bounds,
            long_key,
            island_range_long: list,
            island_range_short: list,
            sizes: LavaIslandSizes,
            rear_lava_buffer):
        """
        Get the ranges of the lava pools. If any of those points are inside the
        island, do not place them.
        """
        z_is_front = long_key == 'z'
        left, right = (
            sizes.left, sizes.right) if z_is_front else (
            sizes.front, sizes.rear + rear_lava_buffer)
        front, rear = (
            sizes.front, sizes.rear + rear_lava_buffer) if z_is_front else (
            sizes.right, sizes.left)
        island_range_x, island_range_z = (
            (island_range_short, island_range_long) if
            z_is_front else (island_range_long, island_range_short))
        lava_range_x_min = island_range_x[0] - left
        lava_range_x_max = island_range_x[-1] + \
            1 + right
        lava_range_z_max = island_range_z[-1] + rear + 1
        lava_range_z_min = island_range_z[0] - front

        total_lava_range_x = range(lava_range_x_min, lava_range_x_max)
        total_lava_range_z = range(lava_range_z_min, lava_range_z_max)
        for x in total_lava_range_x:
            for z in total_lava_range_z:
                island_x = x in island_range_x
                island_z = z in island_range_z
                inside_island = island_x and island_z
                if not inside_island:
                    lava = FloorAreaConfig(
                        num=1, position_x=x, position_z=z)
                    FeatureCreationService.create_feature(
                        scene, FeatureTypes.LAVA, lava, bounds
                    )

    def _get_island_and_lava_size_by_dimension(
            self, dimension_length, island_size,
            side_one, side_two, long_side, side_one_label,
            side_two_label, tool_type):

        min_lava_width = (
            MIN_LAVA_WIDTH_HOOKED_TOOL
            if tool_type in L_SHAPED_TOOLS else MIN_LAVA_WIDTH
        )
        buffer = 1.5 if long_side else \
            (3 if dimension_length % 2 == 0 else 1.5)
        total_max_width_in_dimension = math.floor(
            (dimension_length / (2 if long_side else 1)) - buffer)
        total_max_width_in_dimension = min(
            MAX_LAVA_WITH_ISLAND_WIDTH,
            total_max_width_in_dimension)

        if long_side and tool_type in L_SHAPED_TOOLS:
            if (not side_one and not side_two):
                total_max_width_in_dimension = (
                    MIN_LAVA_WITH_ISLAND_WIDTH_HOOKED_TOOL if (
                        not side_one and not side_two) else min(
                        MAX_LAVA_WITH_ISLAND_WIDTH_HOOKED_TOOL,
                        total_max_width_in_dimension))
        total_accumulated_size = 0

        # Island
        max_island_size = min(
            total_max_width_in_dimension - min_lava_width * 2,
            MAX_LAVA_ISLAND_SIZE)
        if island_size:
            if island_size > max_island_size:
                raise ILEException(
                    f"Island size ({island_size}) is larger than "
                    f"max island size ({max_island_size})")
        else:
            island_size = (
                1 if tool_type in L_SHAPED_TOOLS else
                random.randint(MIN_LAVA_ISLAND_SIZE, max_island_size)
            )

        total_accumulated_size += island_size

        # for the left and right lava sides in hooked tool scenes,
        # make sure lava extends to the wall
        if (not long_side and tool_type in L_SHAPED_TOOLS):
            side_size = math.ceil((dimension_length - island_size) / 2.0)
            return island_size, side_size, side_size
        # Side 1
        side_two = side_two if side_two else min_lava_width
        max_side_one_width = (
            total_max_width_in_dimension - total_accumulated_size - side_two)

        if (tool_type in L_SHAPED_TOOLS and (side_two or side_one)):
            max_side_one_width = min(
                max_side_one_width,
                MAX_LAVA_WIDTH_HOOKED_TOOL)

        if side_one:
            if side_one > max_side_one_width:
                raise ILEException(
                    f"{side_one_label}: ({side_one}) is larger than max width "
                    f"available in this dimension with length: "
                    f"{int(dimension_length)}, island size: {island_size}, "
                    f"and {side_two_label}: {side_two}. Max width available "
                    f"for {side_one_label}: ({max_side_one_width})")
            elif side_one < min_lava_width:
                raise ILEException(
                    f"{side_one_label}: {side_one} is smaller "
                    f"than {min_lava_width}")
        else:
            side_one = random.randint(
                min_lava_width, max_side_one_width)
        total_accumulated_size += side_one

        # Side 2
        max_side_two_width = total_max_width_in_dimension - \
            total_accumulated_size

        if (tool_type in L_SHAPED_TOOLS and (side_two or side_one)):
            max_side_two_width = min(
                max_side_two_width,
                MAX_LAVA_WIDTH_HOOKED_TOOL)

        if side_two:
            if side_two > max_side_two_width:
                raise ILEException(
                    f"{side_two_label}: ({side_two}) is larger than max width "
                    f"available in this dimension with length: "
                    f"{int(dimension_length)}, island size: {island_size}, "
                    f"and {side_one_label}: {side_one}. Max width available "
                    f"for {side_two_label}: ({max_side_one_width})")
            elif side_two < min_lava_width:
                raise ILEException(
                    f"{side_two_label}: {side_two} is smaller "
                    f"than {min_lava_width}")
        else:
            side_two = random.randint(
                min_lava_width, max_side_two_width)

        total_accumulated_size += side_two
        if total_accumulated_size > total_max_width_in_dimension:
            raise ILEException(
                f"{side_one_label} ({side_one}) + Island Size ({island_size}) "
                f"+ {side_two_label} ({side_two}) width larger than "
                f"max width available in dimension "
                f"({total_max_width_in_dimension})")

        return island_size, side_one, side_two

    def _compute_lava_sizes(
            self, long_length, short_length,
            config: LavaTargetToolConfig):
        (island_size, front, rear) = self._get_island_and_lava_size_by_dimension(  # noqa
            long_length,
            config.island_size,
            config.front_lava_width,
            config.rear_lava_width,
            True,
            "front_lava_width",
            "rear_lava_width",
            config.tool_type)
        (_, left, right) = self._get_island_and_lava_size_by_dimension(
            short_length,
            island_size,
            config.left_lava_width,
            config.right_lava_width,
            False,
            "left_lava_width",
            "right_lava_width",
            config.tool_type)

        return LavaIslandSizes(island_size, front, rear, left, right)

    def _add_lava_around_island(
            self, scene, bounds, long_key, sizes: LavaIslandSizes,
            island_long_range, island_short_range, rear_lava_buffer):
        try:
            self._add_asymmetric_lava_around_island(
                scene, bounds, long_key,
                island_long_range, island_short_range, sizes,
                rear_lava_buffer)
        except Exception as e:
            scene.lava = []
            # sourcery recommends the 'from e'
            raise e from e

    # Using only tools with a length of 1 for now
    def _get_too_small_tool(self):
        tools = [
            tool
            for tool, (_, length) in LARGE_BLOCK_TOOLS_TO_DIMENSIONS.items()
            if tool.startswith('tool_rect') and length == 1
        ]
        return random.choice(tools)

    def _add_agent_holds_target(self, scene: Scene):
        config: AgentTargetConfig = self.get_shortcut_agent_with_target()
        if not config:
            return scene
        logger.trace("Adding agent with target shortcut")

        agent_config = config.agent or AgentConfig()
        if config.agent_position:
            agent_config.position = config.agent_position
        if config.movement:
            agent_config.movement = config.movement
        if config.movement_bounds is not None:
            if not isinstance(agent_config.movement, AgentMovementConfig):
                agent_config.movement = AgentMovementConfig()
            agent_config.movement.bounds = config.movement_bounds
        agent = FeatureCreationService.create_feature(
            scene, FeatureTypes.AGENT, agent_config, find_bounds(scene))[0]

        target = self._get_or_add_soccer_ball_target(scene)
        agent_keyword_location = KeywordLocationConfig(
            keyword=KeywordLocation.ASSOCIATED_WITH_AGENT,
            relative_object_label=agent['id']
        )
        KeywordLocation.associate_with_agent(agent_keyword_location, target)

        return scene

    def _get_or_add_soccer_ball_target(self, scene: Scene) -> SceneObject:
        """Returns the existing target, or creates and returns a new soccer
        ball target with scale 1/1/1."""
        targets = scene.get_targets()
        target = random.choice(targets) if targets else None
        if not target:
            goal_template = GoalConfig(
                category=tags.SCENE.RETRIEVAL,
                target=InteractableObjectConfig(
                    shape='soccer_ball',
                    scale=VectorFloatConfig(1, 1, 1),
                    rotation=VectorIntConfig(0, 0, 0)
                )
            )
            targets = GoalServices.attempt_to_add_goal(scene, goal_template)
            target = targets[0]
        return target

    def _get_by_label(self, key: str, label: str, prop: str) -> List[Dict]:
        object_repository = ObjectRepository.get_instance()
        idls = object_repository.get_all_from_labeled_objects(label)
        if not idls:
            raise ILEDelayException(f'Cannot find {key}={label} for {prop}.')
        return [idl.instance for idl in idls]

    def _update_turntables_with_agent_and_non_agent(
        self,
        scene: Scene
    ) -> Scene:
        # This config should NOT be reconciled.
        config = self.turntables_with_agent_and_non_agent
        if not config:
            return scene
        logger.trace("Updating turntables with agent and non-agent")

        # Retrieve all of the objects by their labels, or delay if necessary.
        prop = 'turntables_with_agent_and_non_agent'
        agents = self._get_by_label('agent_label', config.agent_label, prop)
        agent = random.choice(agents)
        non_agents = self._get_by_label(
            'non_agent_label', config.non_agent_label, prop
        )
        non_agent = random.choice(non_agents)
        all_turntables = []
        for turntable_label in return_list(config.turntable_labels):
            turntables = self._get_by_label(
                'turntable label', turntable_label, prop
            )
            all_turntables += turntables
        all_directional_objects = []
        for direction_label in return_list(config.direction_labels):
            directional_objects = self._get_by_label(
                'direction label', direction_label, prop
            )
            all_directional_objects += directional_objects

        # Rotate the turntable on step 1 if the agent's movement begins after
        # step 45; otherwise rotate the turntable after the agent's actions.
        rotation_step = 1
        actions = agent.get('actions')
        movements = agent.get('agentMovement')
        if actions or movements:
            begin_step = min(
                ([actions[0]['stepBegin']] if actions else []) +
                ([movements['stepBegin']] if movements else [])
            )
            end_step = actions[-1].get('stepEnd', actions[-1]['stepBegin'])
            if 0 <= begin_step <= 45:
                rotation_step = end_step + 1

        for turntable in all_turntables:
            # If the agent is above this turntable, then it should NOT rotate.
            if geometry.is_above(agent, turntable):
                if 'rotates' in turntable:
                    del turntable['rotates']
                continue
            # If the non-agent is above this turntable, then it should rotate.
            if geometry.is_above(non_agent, turntable):
                # Randomly choose one of the configured directional objects.
                directional_object = random.choice(all_directional_objects)
                # Use the position (center) of the turntable to calculate the
                # Y rotation for facing toward the directional object.
                _, ending_rotation = geometry.calculate_rotations(
                    Vector3d(**turntable['shows'][0]['position']),
                    Vector3d(**directional_object['shows'][0]['position'])
                )
                # Calculate the amount of rotation necessary.
                starting_rotation = non_agent['debug'].get(
                    # Use the mirrored rotation from the opposite_x keyword
                    # location, if possible.
                    'mirroredRotation',
                    non_agent['shows'][0]['rotation']['y']
                )
                rotation_amount = (
                    round(ending_rotation - starting_rotation, 2) % 360
                )
                # Rotate clockwise by default.
                clockwise = True
                if rotation_amount > 180:
                    # If the rotation is above 180, then adjust the amout and
                    # rotate counter-clockwise.
                    clockwise = False
                    rotation_amount = 360 - rotation_amount
                elif rotation_amount == 180:
                    # If the rotation is exactly 180, then randomly rotate
                    # either clockwise or counter-clockwise.
                    clockwise = random.choice([True, False])
                rotation_length = int(rotation_amount / 5)
                # Add the turntable's rotation.
                turntable['rotates'] = [{
                    'stepBegin': rotation_step,
                    'stepEnd': rotation_step + rotation_length - 1,
                    'vector': {
                        'x': 0,
                        'y': 5 * (1 if clockwise else -1),
                        'z': 0
                    }
                }]

        self._delayed_turntables_with_agent_and_non_agent = False
        self._delayed_turntables_with_agent_and_non_agent_reason = None
        return scene

    def _add_seeing_leads_to_knowing(self, scene: Scene):
        config = self.get_shortcut_seeing_leads_to_knowing()
        if not config:
            return scene
        logger.trace("Adding seeing leads to knowing shortcut")

        # Fixed room dimensions -- going with 10/3/10 for now
        scene.room_dimensions.x = 10
        scene.room_dimensions.y = 3
        scene.room_dimensions.z = 10

        # add platform and place performer on top
        bounds = find_bounds(scene)
        z_start = -2.65
        platform_config = StructuralPlatformConfig(
            num=1, position=VectorFloatConfig(0, 0, z_start), rotation_y=0,
            scale=VectorFloatConfig(1, 1, 1))
        scene.set_performer_start_position(
            x=0, y=platform_config.scale.y + geometry.PERFORMER_CAMERA_Y,
            z=z_start)
        scene.set_performer_start_rotation(30, 0)

        FeatureCreationService.create_feature(
            scene,
            FeatureTypes.PLATFORMS,
            platform_config,
            bounds.copy()
        )[0]

        self._create_target_goal_seeing_leads_to_knowing(scene)

        targets = scene.get_targets()
        target = random.choice(targets) if targets else None

        self._create_bins_placers_seeing_leads_to_knowing(scene, target)  # noqa

        self._agent_setup_seeing_leads_to_knowing(config, scene, target)

        return scene

    def _modify_knowledgeable_agent_rotation(self, agent: SceneObject) -> None:
        position_x = agent['shows'][0]['position']['x']
        rotation_y = agent['shows'][0]['rotation']['y']
        if rotation_y not in [0, 180]:
            raise ILEException(
                f'Knowledgeable agent pair Y rotation should be 0 or 180, but '
                f'was {rotation_y}'
            )
        # Modify the starting Y rotation by 180 degrees.
        rotation_y = (rotation_y + 180) % 360
        agent['shows'][0]['rotation']['y'] = rotation_y
        # The agent rotates 180 degrees during the first 12 steps.
        y = (1 if rotation_y == 0 else -1) * (15 if position_x < 0 else -15)
        if 'rotates' not in agent:
            agent['rotates'] = []
        agent['rotates'].insert(0, {
            'stepBegin': 1,
            'stepEnd': 12,
            'vector': {
                'x': 0,
                'y': y,
                'z': 0
            }
        })

    def _add_knowledgeable_agent_pair(self, scene: Scene):
        config = self.get_knowledgeable_agent_pair()
        if not config:
            return scene
        logger.trace("Adding knowledgeable agent pair")

        if (random.randint(0, 1) == 0):
            knowledgeable_agent_position = config.position_1
            non_knowledgeable_agent_position = config.position_2
        else:
            knowledgeable_agent_position = config.position_2
            non_knowledgeable_agent_position = config.position_1

        knowledgeable_agent_config = AgentConfig(
            num=1,
            labels='knowledgeable_agent',
            position=knowledgeable_agent_position,
            # We will modify this rotation later (see the comment below).
            # Keep it as this value to ensure the pointing rotation is correct.
            rotation_y=180,
            pointing=AgentPointingConfig(
                object_label=self.knowledgeable_agent_pair.target_labels,
                step_begin=config.pointing_step,
                walk_distance=None
            )
        )
        non_target_label = ""
        if (self.knowledgeable_agent_pair.non_target_labels is not None):
            non_target_label = self.knowledgeable_agent_pair.non_target_labels
            if (len(non_target_label) > 1):
                non_target_label = non_target_label[
                    random.randint(0, len(non_target_label)) - 1]

        non_knowledgeable_agent_config = AgentConfig(
            num=1,
            labels='non_knowledgeable_agent',
            position=non_knowledgeable_agent_position,
            # We will modify this rotation later (see the comment below).
            # Keep it as this value to ensure the pointing rotation is correct.
            rotation_y=0,
            pointing=AgentPointingConfig(
                object_label=non_target_label,
                step_begin=config.pointing_step,
                walk_distance=None
            )
        )

        try:
            agent = FeatureCreationService.create_feature(
                scene,
                FeatureTypes.AGENT,
                knowledgeable_agent_config,
                scene.find_bounds()
            )[0]
            self._modify_knowledgeable_agent_rotation(agent)
        except ILEDelayException:
            self._delayed_knowledgeable_agent_pair.append(
                knowledgeable_agent_config)

        try:
            agent = FeatureCreationService.create_feature(
                scene,
                FeatureTypes.AGENT,
                non_knowledgeable_agent_config,
                scene.find_bounds()
            )[0]
            self._modify_knowledgeable_agent_rotation(agent)
        except ILEDelayException:
            self._delayed_knowledgeable_agent_pair.append(
                non_knowledgeable_agent_config)

        return scene

    def _create_bins_placers_seeing_leads_to_knowing(
            self, scene: Scene, target: SceneObject):
        # bin/bucket setup
        bin_shape_choices = ['cup_2_static', 'cup_3_static', 'cup_6_static']
        bin_shape = random.choice(bin_shape_choices)
        bin_y_scale = 3.75 if bin_shape == 'cup_6_static' else 2.75
        bin_scale = VectorFloatConfig(x=3, y=bin_y_scale, z=3)
        bin_mat = random.choice(
            materials.METAL_MATERIALS + materials.PLASTIC_MATERIALS +
            materials.WOOD_MATERIALS
        ).material

        bin_positions = [
            {'label': 'bin_1', 'position': VectorFloatConfig(
                x=BIN_LEFT_X_POS, y=0, z=BIN_REAR_Z_POS)},
            {'label': 'bin_2', 'position': VectorFloatConfig(
                x=BIN_LEFT_X_POS, y=0, z=BIN_FRONT_Z_POS)},
            {'label': 'bin_3', 'position': VectorFloatConfig(
                x=BIN_RIGHT_X_POS, y=0, z=BIN_REAR_Z_POS)},
            {'label': 'bin_4', 'position': VectorFloatConfig(
                x=BIN_RIGHT_X_POS, y=0, z=BIN_FRONT_Z_POS)}
        ]

        # randomly choose destination bucket for target
        target_bucket = random.choice(bin_positions)

        # create bins and placers
        for bin_pos in bin_positions:
            bucket_config = InteractableObjectConfig(
                material=bin_mat,
                scale=bin_scale,
                shape=bin_shape,
                position=bin_pos['position'],
                rotation=VectorFloatConfig(x=0, y=0, z=0),
                labels=bin_pos['label']
            )

            FeatureCreationService.create_feature(
                scene, FeatureTypes.INTERACTABLE, bucket_config,
                find_bounds(scene))[0]

            end_placer_height = 0.05

            # if target should be in this bucket, move target to
            # corresponding placer
            if (bin_pos == target_bucket):
                relative_bin = RelativePositionConfig(
                    label=bin_pos['label']
                )

                placer_temp = StructuralPlacerConfig(
                    activation_step=PLACER_ACTIVATION_STEP,
                    deactivation_step=PLACER_DEACTIVATION_STEP,
                    end_height=end_placer_height,
                    position_relative=relative_bin,
                    placed_object_labels='target',
                    placed_object_rotation=0)

                FeatureCreationService.create_feature(
                    scene,
                    FeatureTypes.PLACERS,
                    placer_temp,
                    find_bounds(scene)
                )
            else:
                target_placer_y_pos = scene.room_dimensions.y - target['debug']['positionY']  # noqa

                non_target_placer = create_placer(
                    placed_object_position={
                        'x': bin_pos['position'].x,
                        'y': target_placer_y_pos,
                        'z': bin_pos['position'].z,
                    },
                    placed_object_dimensions=target['debug']['dimensions'],
                    placed_object_offset_y=target['debug']['positionY'],
                    activation_step=PLACER_ACTIVATION_STEP,
                    deactivation_step=PLACER_DEACTIVATION_STEP,
                    end_height=end_placer_height,
                    max_height=scene.room_dimensions.y,
                    last_step=scene.goal.last_step
                )

                scene.objects.append(non_target_placer)

    def _create_target_goal_seeing_leads_to_knowing(self, scene: Scene):
        # Note that soccer ball scale is slightly smaller than usual
        # for this type of task
        target_def = create_soccer_ball(size=0.75)
        origin_pos = {
            'position': {
                'x': 0, 'y': 0, 'z': 0},
            'rotation': {
                'x': 0, 'y': 0, 'z': 0}
        }
        target_inst = instances.instantiate_object(target_def, origin_pos)

        target_idl = InstanceDefinitionLocationTuple(
            target_inst, target_def, origin_pos
        )

        obj_repo = ObjectRepository.get_instance()
        obj_repo.add_to_labeled_objects(target_idl, 'target')
        scene.objects.append(target_inst)
        total_steps = 105

        scene.goal = Goal(
            metadata={
                'target': {
                    'id': target_inst['id']
                }
            },
            category='passive',
            answer={
                'choice': 'plausible'
            },
            last_step=total_steps,
            action_list=([['Pass']] * total_steps),
            description=''
        )

    def _agent_setup_seeing_leads_to_knowing(
            self, config: SeeingLeadsToKnowingConfig,
            scene: Scene, target: SceneObject):
        """
        Agent Setup
        1. Enter from left or right
        2. Walk to middle of buckets
        3. Idle until after placers fall and ball is dropped in bucket
        4. Walk to a bucket, possibly rotating before hand if correct bucket
           is behind performer
        """
        agent_x_start_left = -2
        agent_x_start_right = 2

        if (config.target_behind_agent):
            agent_x_start = (
                agent_x_start_left
                if target['shows'][0]['position']['x'] == BIN_LEFT_X_POS
                else agent_x_start_right
            )
        else:
            agent_x_start = (
                agent_x_start_left
                if target['shows'][0]['position']['x'] == BIN_RIGHT_X_POS
                else agent_x_start_right
            )

        agent_start_position = Vector3d(x=agent_x_start, y=0, z=0)

        walk_animation = "TPM_walk"
        movement_points = []
        movement_points.append(
            Vector3d(
                x=0,
                y=0,
                z=0
            )
        )

        actions = []
        agent_idle_begin = PLACER_ACTIVATION_STEP + 1
        agent_idle_end = PLACER_DEACTIVATION_STEP + 11
        agent_idle = AgentActionConfig(
            step_begin=agent_idle_begin,
            step_end=agent_idle_end,
            is_loop_animation=True,
            id='TPM_idle1'
        )
        actions.append(agent_idle)

        # If target is in front of agent, walk towards it. Otherwise, pick a
        # random bucket to walk towards behind the agent.
        is_target_behind_agent = (config.target_behind_agent or
                                  ((agent_x_start * target['shows'][0]['position']['x']) > 0))  # noqa

        if (is_target_behind_agent):
            movement_points.append(
                VectorFloatConfig(
                    x=target['shows'][0]['position']['x'],
                    z=choose_random([BIN_FRONT_Z_POS, BIN_REAR_Z_POS])
                )
            )
        else:
            movement_points.append(
                VectorFloatConfig(
                    x=target['shows'][0]['position']['x'],
                    z=target['shows'][0]['position']['z']
                )
            )

        movement = AgentMovementConfig(
            animation=walk_animation,
            step_begin=1,
            points=movement_points,
            repeat=False
        )
        agent_config = AgentConfig(
            position=agent_start_position,
            rotation_y=90 if agent_x_start == agent_x_start_left else 270,
            actions=actions,
            movement=movement
        )

        FeatureCreationService.create_feature(
            scene, FeatureTypes.AGENT, agent_config, find_bounds(scene))[0]

    def _add_imitation_task(self, scene: Scene):
        """
        Shortcut function to add all of the required scene elements for
        an imitation task. Three containers on either side of the performer
        """
        config: ImitationTaskConfig = self.get_shortcut_imitation_task()
        if not config:
            return scene
        if config.trigger_order is None:
            config.trigger_order = choose_random(
                [order.value for order in ImitationTriggerOrder])
        if config.containers_on_right_side is None:
            config.containers_on_right_side = choose_random([True, False])
        if config.kidnap_option is None:
            config.kidnap_option = choose_random(
                [option.value for option in ImitationKidnapOptions])

        rotation_to_use = None
        relative_rotation = False
        if config.global_container_rotation is not None or \
                config.relative_container_rotation is None:
            config.global_container_rotation = \
                choose_random(
                    IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL if
                    config.global_container_rotation is None else
                    config.global_container_rotation)
            rotation_to_use = config.global_container_rotation
            relative_rotation = False
            if config.global_container_rotation not in \
                    IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL:
                raise ILEException(
                    "Imitation Task Container Global Rotation "
                    f"({config.global_container_rotation}) must "
                    "be equal to a vale in "
                    f"{IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL} "
                )
        else:
            config.relative_container_rotation = choose_random(
                config.relative_container_rotation)
            rotation_to_use = config.relative_container_rotation
            relative_rotation = True
            if rotation_to_use not in \
                    (IMITATION_CONTAINER_TELEPORT_ROTATIONS_RIGHT_SIDE if
                        config.containers_on_right_side else
                        IMITATION_CONTAINER_TELEPORT_ROTATIONS_LEFT_SIDE):
                raise ILEException(
                    "Imitation Task Container Relative Rotation "
                    f"({config.relative_container_rotation}) must "
                    "be a value allowed on their container start side. "
                    "RIGHT SIDE: "
                    f"{IMITATION_CONTAINER_TELEPORT_ROTATIONS_RIGHT_SIDE}"
                    ", LEFT SIDE: "
                    f"{IMITATION_CONTAINER_TELEPORT_ROTATIONS_LEFT_SIDE}."
                )

        goal_template = GoalConfig(
            category=tags.SCENE.IMITATION,
            target=InteractableObjectConfig(
                position=Vector3d(x=0, y=0, z=4),
                shape='soccer_ball',
                scale=1))
        GoalServices.attempt_to_add_goal(scene, goal_template)
        return add_imitation_task(
            scene, config.trigger_order, config.containers_on_right_side,
            config.kidnap_option, containers_teleport_rotation=rotation_to_use,
            relative_rotation=relative_rotation)

    def get_num_delayed_actions(self) -> int:
        count = 0
        count += 1 if self._delayed_perf_pos else 0
        count += 1 if self._delayed_turntables_with_agent_and_non_agent else 0
        count += 1 if self._delayed_knowledgeable_agent_pair else 0
        return count

    def run_delayed_actions(self, scene: Scene) -> Scene:
        if self._delayed_perf_pos:
            try:
                self._position_performer_on_platform(scene)
            except Exception as e:
                self._delayed_perf_pos_reason = e
        if self._delayed_turntables_with_agent_and_non_agent:
            try:
                self._update_turntables_with_agent_and_non_agent(scene)
            except ILEDelayException as e:
                self._delayed_turntables_with_agent_and_non_agent_reason = e
        for index in range(0, len(self._delayed_knowledgeable_agent_pair)):
            try:
                agent = FeatureCreationService.create_feature(
                    scene,
                    FeatureTypes.AGENT,
                    self._delayed_knowledgeable_agent_pair[index],
                    scene.find_bounds()
                )[0]
                if agent is not None:
                    self._delayed_knowledgeable_agent_pair.pop(index)
                    index = 0
                    self._modify_knowledgeable_agent_rotation(agent)
            except Exception as e:
                msg = str(e) + ": " + \
                    str(self._delayed_knowledgeable_agent_pair[0].labels)
                self._delayed_knowledgeable_agent_pair_reason = msg
        return scene

    def get_delayed_action_error_strings(self) -> List[str]:
        errors = []
        if self._delayed_perf_pos_reason:
            errors += [str(self._delayed_perf_pos_reason)]
        if self._delayed_turntables_with_agent_and_non_agent_reason:
            errors += [str(
                self._delayed_turntables_with_agent_and_non_agent_reason
            )]
        if self._delayed_knowledgeable_agent_pair_reason:
            errors += [str(
                self._delayed_knowledgeable_agent_pair_reason
            )]
        return errors

    def _add_placers_with_decoys(self, scene: Scene) -> Scene:
        config = self.get_placers_with_decoy()
        if not config:
            return scene

        activation_step_1 = 0
        activation_step_2 = 0
        if self.placers_with_decoy.activation_step is None or \
                len(self.placers_with_decoy.activation_step) < 2:
            raise ILEException("Must be an array with at least two values")
        else:
            while (activation_step_1 == activation_step_2):
                activation_step_1 = random.randint(
                    0, len(self.placers_with_decoy.activation_step) - 1)
                activation_step_2 = random.randint(
                    0, len(self.placers_with_decoy.activation_step) - 1)
            activation_step_1 = self.placers_with_decoy.activation_step[activation_step_1]  # noqa: E501
            activation_step_2 = self.placers_with_decoy.activation_step[activation_step_2]  # noqa: E501

        x_position_1 = 0
        x_position_2 = 0
        if self.placers_with_decoy.object_end_position_x is None or \
                len(self.placers_with_decoy.object_end_position_x) < 2:
            raise ILEException("Must be an array with at least two values")
        else:
            while (x_position_1 == x_position_2):
                x_position_1 = random.randint(
                    0, len(self.placers_with_decoy.object_end_position_x) - 1)
                x_position_2 = random.randint(
                    0, len(self.placers_with_decoy.object_end_position_x) - 1)
            x_position_1 = self.placers_with_decoy.object_end_position_x[x_position_1]  # noqa: E501
            x_position_2 = self.placers_with_decoy.object_end_position_x[x_position_2]  # noqa: E501

        decoy_start_position = copy.deepcopy(
            self.placers_with_decoy.placed_object_position)
        decoy_start_position.y = decoy_start_position.y + \
            (self.placers_with_decoy.decoy_y_modifier or 0)

        placer_1_config = StructuralPlacerConfig(
            num=1,
            move_object=True,
            activation_step=activation_step_1,
            # The Y and Z are no longer needed, so just use dummy values here.
            move_object_end_position=VectorFloatConfig(
                x=x_position_1, y=0, z=0),
            labels=self.placers_with_decoy.labels,
            move_object_y=self.placers_with_decoy.move_object_y,
            move_object_z=self.placers_with_decoy.move_object_z,
            # This placer will actually move the configured object.
            placed_object_labels=self.placers_with_decoy.placed_object_labels,
            placed_object_position=self.placers_with_decoy.placed_object_position,  # noqa: E501
            placed_object_rotation=self.placers_with_decoy.placed_object_rotation  # noqa: E501
        )
        placer_2_config = StructuralPlacerConfig(
            num=1,
            move_object=True,
            activation_step=activation_step_2,
            move_object_end_position=VectorFloatConfig(
                x=x_position_2, y=0, z=0),
            labels=self.placers_with_decoy.labels,
            move_object_y=self.placers_with_decoy.move_object_y,
            move_object_z=self.placers_with_decoy.move_object_z,
            # This placer will be the decoy.
            placed_object_position=decoy_start_position,
            empty_placer=True
        )

        FeatureCreationService.create_feature(
            scene, FeatureTypes.PLACERS, placer_1_config, [])[0]
        FeatureCreationService.create_feature(
            scene, FeatureTypes.PLACERS, placer_2_config, [])[0]

        return scene
