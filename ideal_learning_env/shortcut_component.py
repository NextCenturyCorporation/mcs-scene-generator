import copy
import logging
import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Union

from machine_common_sense.config_manager import Vector3d

from generator import MAX_TRIES, ObjectBounds, Scene, geometry, materials, tags
from generator.base_objects import LARGE_BLOCK_TOOLS_TO_DIMENSIONS
from generator.mechanisms import create_placer
from generator.structures import (
    BASE_DOOR_HEIGHT,
    BASE_DOOR_WIDTH,
    create_guide_rails_around
)
from ideal_learning_env.action_service import ActionService, TeleportConfig
from ideal_learning_env.actions_component import StepBeginEnd
from ideal_learning_env.agent_service import (
    AgentActionConfig,
    AgentConfig,
    AgentMovementConfig
)
from ideal_learning_env.goal_services import GoalConfig, GoalServices
from ideal_learning_env.interactable_object_service import (
    InteractableObjectConfig,
    KeywordLocationConfig,
    create_user_configured_interactable_object
)
from ideal_learning_env.numerics import (
    MinMaxFloat,
    MinMaxInt,
    RandomizableVectorFloat3d,
    VectorFloatConfig,
    VectorIntConfig
)
from ideal_learning_env.object_services import (
    KeywordLocation,
    ObjectRepository
)
from ideal_learning_env.validators import (
    ValidateNumber,
    ValidateOptions,
    ValidateOr
)

from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import (
    ILEDelayException,
    ILEException,
    RandomizableString,
    choose_random,
    find_bounds,
    return_list
)
from .structural_object_service import (
    DOOR_MATERIAL_RESTRICTIONS,
    FeatureCreationService,
    FeatureTypes,
    FloorAreaConfig,
    PartitionFloorConfig,
    StructuralDoorConfig,
    StructuralPlatformConfig,
    ToolConfig
)

logger = logging.getLogger(__name__)


DOOR_OCCLUDER_MIN_ROOM_Y = 5

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

MIN_LAVA_ISLAND_LONG_ROOM_DIMENSION_LENGTH = 13
MIN_LAVA_ISLAND_SHORT_ROOM_DIMENSION_LENGTH = 7

# Min lava with island width should be 5
MAX_LAVA_WITH_ISLAND_WIDTH = 9
MIN_LAVA_WITH_ISLAND_WIDTH_HOOKED_TOOL = 3
MAX_LAVA_WITH_ISLAND_WIDTH_HOOKED_TOOL = 7

HOOKED_TOOL_BUFFER = 2
MAX_TOOL_LENGTH = 9

TOOL_RECTANGULAR = 'rectangular'
TOOL_HOOKED = 'hooked'

TOOL_LENGTH_TOO_SHORT = 1
MIN_TOOL_CHOICE_X_DIMENSION = 20


class ImprobableToolOption(str, Enum):
    NO_TOOL = 'no_tool'
    TOO_SHORT_TOOL = 'too_short'


TARGET_CONTAINER_LABEL = 'target_container'


@dataclass
class LavaTargetToolConfig():
    """
    Defines details of the shortcut_lava_target_tool shortcut.  This shortcut
    creates a room with a target object on an island surrounded by lava. There
    will also be a block tool to facilitate acquiring the goal object.
    - `front_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles of lava in front of the island.  Must produce value
    between 2 and 6 for rectangular tools, 1 to 3 for hooked tools.
    Default: Random based on room size and island size
    - `guide_rails` (bool, or list of bools): If True, guide rails will be
    generated to guide the tool in the direction it is oriented.  If a target
    exists, the guide rails will extend to the target.  This option cannot be
    used with `tool_rotation`. Default: False
    - `island_size` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): The width and length of the island inside the
    lava.  Must produce value from 1 to 5 for rectangular tools, 1 to 3
    for hooked tools.
    Default: Random based on room size
    - `left_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles of lava left of the island.  Must produce value
    between 2 and 6 for rectangular tools, but will be ignored for hooked
    tools, since the lava should extend to the wall in that case.
    Default: Random based on room size and island size
    - `random_performer_position` (bool, or list of bools): If True, the
    performer will be randomly placed in the room. They will not be placed in
    the lava or the island   Default: False
    - `random_target_position` (bool, or list of bools): If True, the
    target object will be positioned randomly in the room, rather than being
    positioned on the island surrounded by lava. Default: False
    - `rear_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles of lava behind of the island.  Must produce value
    between 2 and 6 for rectangular tools, 1 to 3 for hooked tools.
    Default: Random based on room size, island size, and other lava widths.
    - `right_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles right of the island.  Must produce value
    between 2 and 6 for rectangular tools, but will be ignored for hooked
    tools, since the lava should extend to the wall in that case.
    Default: Random based on room size and island size
    - `random_performer_position` (bool, or list of bools): If True, the
    performer will be randomly placed in the room. They will not be placed in
    the lava or the island   Default: False
    - `tool_rotation` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    Angle that tool should be rotated out of alignment with target.
    This option cannot be used with `guide_rails`.  Default: 0
    - `distance_between_performer_and_tool` (float, or list of floats,
    or [MinMaxFloat](#MinMaxFloat): The distance away the performer is from the
    tool at start. The performer will be at random point around a rectangular
    perimeter surrounding the tool. This option cannot be used with
    `random_performer_position`.  Default: None
    - `tool_type` (str, or list of strs): The type of tool to generate, either
    `rectangular` or `hooked`. Note that if `hooked` tools are chosen and lava
    widths are not specified, the room will default to having an island size
    of 1, with lava extending all the way to the walls in both the left and
    right directions. The front and rear lava in the default hooked tool case
    will each have a size of 1. Default: `rectangular`

    """
    island_size: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    front_lava_width: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    rear_lava_width: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    left_lava_width: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    right_lava_width: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    guide_rails: Union[bool, List[bool]] = False
    tool_rotation: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = 0
    random_performer_position: Union[bool, List[bool]] = False
    random_target_position: Union[bool, List[bool]] = False
    distance_between_performer_and_tool: Union[
        float, MinMaxFloat, List[Union[float, MinMaxFloat]]
    ] = None
    tool_type: RandomizableString = TOOL_RECTANGULAR


@dataclass
class LavaIslandSizes():
    # internal class for storing lava widths and island sizes
    island_size: int = 0
    front: int = 0
    rear: int = 0
    left: int = 0
    right: int = 0


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
    - `wall_material` (string, or list of strings): The material or material
    type for the wall.
    """
    start_drop_step: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    add_lips: Union[bool, List[bool]] = True
    add_freeze: Union[bool, List[bool]] = True
    restrict_open_doors: Union[bool, List[bool]] = True
    door_material: Union[str, List[str]] = None
    wall_material: Union[str, List[str]] = None
    add_extension: Union[bool, List[bool]] = False
    extension_length: Union[
        float, MinMaxFloat, List[Union[float, MinMaxFloat]]
    ] = None
    extension_position: Union[
        float, MinMaxFloat, List[Union[float, MinMaxFloat]]
    ] = None
    bigger_far_end: Union[bool, List[bool]] = False


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
    movement: Union[bool, List[bool]] = None


@dataclass
class BisectingPlatformConfig():
    """
    Defines details of the shortcut_bisecting_platform shortcut.  This shortcut
    creates a platform that bisects the room, where the performer will start.
    On default, a blocking wall is on that platform, forcing the performer
    to choose a side to drop off of the platform, but this can be disabled.
    - `has_blocking_wall` (bool): Enables the blocking wall so that the
    performer has to stop and choose a side of the room. Default: True
    - `has_long_blocking_wall` (bool): Enables the long blocking wall used in
    Spatial Reorientation tasks. Overrides `has_blocking_wall`. Default: False
    - `is_short` (bool): Makes the platform short (a Y scale of 0.5 rather
    than 1). Default: False
    - `is_thin` (bool): Makes the platform thin (an X scale of 0.5 rather
    than 1). Default: False
    - `other_platforms` ([StructuralPlatformConfig](#StructuralPlatformConfig)
    dict, or list of StructuralPlatformConfig dicts): Configurations to
    generate other platforms that may intersect with the bisecting platform.
    Default: None
    """
    has_blocking_wall: bool = True
    has_long_blocking_wall: bool = False
    is_short: bool = False
    is_thin: bool = False
    other_platforms: Union[
        StructuralPlatformConfig,
        List[StructuralPlatformConfig]
    ] = None


class ImitationTriggerOrder(str, Enum):
    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"
    LEFT_MIDDLE = "left_middle"
    LEFT_RIGHT = "left_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_RIGHT = "middle_right"
    RIGHT_MIDDLE = "right_middle"
    RIGHT_LEFT = "right_left"


class ImitationKidnapOptions(str, Enum):
    AGENT_ONLY = "agent_only"
    CONTAINERS = "containers"
    CONTAINERS_ROTATE = "containers_rotate"
    PERFORMER = "performer"


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
    2) containers: The containers are teleported but still in view. The
    containers are still aligned with their start rotation. The imitation agent
    is teleported away from the containers but in view.
    3) containers_rotate: The containers are teleported but still in view. The
    containers are rotated 90 degrees to be perpendicular to how they started.
    The imitation agent is teleported away from the containers but in view.
    4) performer: The performer is teleported to a random part of the room
    but looks at the center of the room where the containers still are.
    The imitation agent is teleported away from the containers but in view.

    Default: random
    """
    trigger_order: Union[str, List[str]] = None
    containers_on_right_side: Union[bool, List[bool]] = None
    kidnap_option: Union[str, List[str]] = None


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
    turntable_labels: Union[str, List[str]]
    direction_labels: Union[str, List[str]]


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

    For hooked tools, different min/max rules apply. See
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

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self._delayed_perf_pos = False
        self._delayed_perf_pos_reason = None
        self._delayed_turntables_with_agent_and_non_agent = False
        self._delayed_turntables_with_agent_and_non_agent_reason = None

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
        config = choose_random(config)
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

    def get_shortcut_lava_target_tool(
            self) -> Union[bool, LavaTargetToolConfig]:
        if self.shortcut_lava_target_tool is False:
            return False
        config = self.shortcut_lava_target_tool
        if self.shortcut_lava_target_tool is True:
            config = LavaTargetToolConfig()
        config = choose_random(config)
        return config

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
        props=['kidnap_options'],
        options=(
            ImitationKidnapOptions.AGENT_ONLY,
            ImitationKidnapOptions.CONTAINERS,
            ImitationKidnapOptions.CONTAINERS_ROTATE,
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

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring shortcut options for the scene...')
        room_dim = scene.room_dimensions

        scene = self._add_bisecting_platform(scene, room_dim)
        scene = self._add_triple_door_shortcut(scene, room_dim)
        scene = self._delay_performer_placement(scene, room_dim)
        scene = self._add_lava_shortcut(scene, room_dim)
        scene = self._add_tool_lava_goal(scene, room_dim)
        scene = self._add_agent_holds_target(scene)
        scene = self._add_imitation_task(scene)
        scene = self._add_lava_tool_choice_goal(scene, room_dim)
        try:
            scene = self._update_turntables_with_agent_and_non_agent(scene)
        except ILEDelayException as e:
            self._delayed_turntables_with_agent_and_non_agent = True
            self._delayed_turntables_with_agent_and_non_agent_reason = e

        return scene

    def _add_bisecting_platform(self, scene: Scene, room_dim: Vector3d):
        if not self.get_shortcut_bisecting_platform():
            return scene

        logger.trace("Adding bisecting platform shortcut")
        config = self.get_shortcut_bisecting_platform()
        self._do_add_bisecting_platform(
            scene,
            room_dim,
            blocking_wall=config.has_blocking_wall,
            platform_height=(0.5 if config.is_short else 1),
            long_blocking_wall=config.has_long_blocking_wall,
            is_thin=config.is_thin,
            other_platforms=(
                config.other_platforms
                if isinstance(config.other_platforms, list)
                else [config.other_platforms]
            ) if config.other_platforms else []
        )

        return scene

    def _do_add_bisecting_platform(
        self,
        scene: Scene,
        room_dim: Vector3d,
        blocking_wall: bool = False,
        platform_height: float = 1,
        long_blocking_wall: bool = False,
        is_thin: bool = False,
        other_platforms: List[StructuralPlatformConfig] = None
    ) -> None:

        # Second platform is the wall to prevent performer from moving too
        # far before getting off the platform.  Since walls go to the
        # ceiling and platforms all start on the floor, we overlap this
        # platform.

        bounds = find_bounds(scene)
        performer_z = -room_dim.z / 2.0
        scale_x = 0.5 if is_thin else 1
        platform_config = StructuralPlatformConfig(
            num=1, position=VectorFloatConfig(0, 0, 0), rotation_y=0,
            scale=VectorFloatConfig(scale_x, platform_height, room_dim.z))

        # Create the blocking wall.
        position_z = 0 if long_blocking_wall else (performer_z + 1.5)
        blocking_wall_config = StructuralPlatformConfig(
            num=1,
            material=materials.BLACK.material,
            position=VectorFloatConfig(0, 0, position_z),
            rotation_y=0,
            scale=VectorFloatConfig(
                scale_x - 0.01,
                platform_height + 0.25,
                (scene.room_dimensions.z - 3) if long_blocking_wall else 0.1
            )
        )

        scene.set_performer_start_position(
            x=0, y=platform_config.scale.y, z=(performer_z) + 0.5)
        # Start looking down if the room is short.
        rotation_x = (10 if scene.room_dimensions.z < 10 else 0)
        scene.set_performer_start_rotation(rotation_x, 0)

        platform_instance = FeatureCreationService.create_feature(
            scene,
            FeatureTypes.PLATFORMS,
            platform_config,
            # Use a copy of the bounds list here because we want to ignore the
            # bounds of the new platform within this function.
            bounds.copy()
        )[0]

        if blocking_wall or long_blocking_wall:
            FeatureCreationService.create_feature(
                scene,
                FeatureTypes.PLATFORMS,
                blocking_wall_config,
                bounds.copy()
            )

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

    def _add_platform_extension(
        self,
        scene: Scene,
        platform: Dict[str, Any],
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
                0, 2 + add_y, 0), rotation_y=rot_y, wall_scale_x=1,
            wall_scale_y=2.25, material=config.door_material,
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

        # Note: 4.25 is from height of platform, height of door, plus what we
        # added to the center door top so all top walls line up.
        door_right_template = StructuralDoorConfig(
            num=1, position=VectorFloatConfig(
                side_wall_position_x, add_y, 0), rotation_y=rot_y,
            wall_scale_x=side_wall_scale_x,
            wall_scale_y=4.25, wall_material=wall_mat, material=door_mat)
        door_left_template = StructuralDoorConfig(
            num=1, position=VectorFloatConfig(
                -side_wall_position_x, add_y, 0), rotation_y=rot_y,
            wall_scale_x=side_wall_scale_x,
            wall_scale_y=4.25, wall_material=wall_mat, material=door_mat)

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
                goal = scene.goal or {}
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
        config = self.get_shortcut_lava_target_tool()
        if not config:
            return scene
        logger.trace("Adding tool to goal shortcut")
        num_prev_objs = len(scene.objects)
        num_prev_lava = len(scene.lava)

        if config.guide_rails and config.tool_rotation:
            raise ILEException(
                "Unable to use 'guide_rails' and 'tool_rotation' from "
                "shortcut_lava_target_tool at the same time")

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

                if config.tool_type == TOOL_HOOKED:
                    tool_length = random.randint(
                        tool_length + HOOKED_TOOL_BUFFER, MAX_TOOL_LENGTH)

                # if size 13, edge is whole tiles at 6, buffer should be 6,
                # if size 14, edge is half tile at 7, buffer should be 6

                # buffer here not used for hooked tools
                far_island_buffer = (
                    1 if config.tool_type != TOOL_HOOKED else 0)
                # additional buffer of lava needed for hooked tool scenes
                # with even sized long dimension
                rear_lava_buffer = (
                    1 if config.tool_type == TOOL_HOOKED and long_length %
                    2 == 0 else 0)

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
                tool_shape = self._get_tool_shape(
                    tool_length, config.tool_type)
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
                    config.tool_type,
                    tool_shape,
                    config.tool_rotation)
                tool = scene.objects[-1]

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

                if (config.distance_between_performer_and_tool is not None and
                        config.random_performer_position):
                    raise ILEException(
                        "Cannot have distance_between_performer_and_tool "
                        "and random_performer_position"
                    )
                if config.random_performer_position:
                    self._randomize_performer_position(
                        scene,
                        long_key, short_key, long_near_island_coord,
                        long_far_island_coord, sizes)
                elif config.distance_between_performer_and_tool is not None:
                    if tool['type'].startswith('tool_hooked'):
                        (x, z) = geometry.get_position_distance_away_from_hooked_tool(  # noqa
                            scene.room_dimensions, tool,
                            config.distance_between_performer_and_tool,
                            bounds + [island_bounds])
                    else:
                        (x, z) = geometry.get_position_distance_away_from_obj(
                            scene.room_dimensions, tool,
                            config.distance_between_performer_and_tool,
                            bounds + [island_bounds])
                    scene.set_performer_start_position(x=x, y=None, z=z)
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
                    meta = (scene.goal or {}).get('metadata', {})
                    if 'target' in meta:
                        meta.pop('target')
                config = self.get_shortcut_lava_target_tool()

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
                    TOOL_RECTANGULAR)
                (_, left, right) = self._get_island_and_lava_size_by_dimension(
                    short_length,
                    island_size,
                    left_right_width,
                    left_right_width,
                    False,
                    "left_lava_width",
                    "right_lava_width",
                    TOOL_RECTANGULAR)

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
                scene.goal['action_list'] = ([['RotateRight']] * 36)

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
                    meta = (scene.goal or {}).get('metadata', {})
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
        if(valid_tool):
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
        if(valid_tool):
            tool_shape = self._get_tool_shape(tool_length, TOOL_RECTANGULAR)
        else:
            # if improbable_option set to no_tool, nothing left to do, return
            if(config.improbable_option == ImprobableToolOption.NO_TOOL):
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
            TOOL_RECTANGULAR,
            tool_shape,
            False)

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
        if TOOL_HOOKED in tool['type']:
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
        room_mats = scene.room_materials or {}
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
                  tool_rotation=False):
        bounds_to_check = bounds
        tool_rot = 0 if long_key == 'z' else 90
        if tool_rotation:
            tool_rot += tool_rotation
        tool_pos = VectorFloatConfig(y=0)
        long_tool_pos = (long_near_island_coord -
                         front_lava_width - tool_length / 2.0 - 0.5)

        if(tool_type == TOOL_HOOKED):
            bounds_to_check = []
            tool_width = LARGE_BLOCK_TOOLS_TO_DIMENSIONS[tool_shape][0]
            tool_buffer = 1.0 - (tool_width / 3.0)

            # make sure tool is placed directly behind island
            rear_buffer = 1.0
            lava_front_to_behind_island = (
                front_lava_width +
                island_size + rear_buffer)
            tool_pos_increment = lava_front_to_behind_island - tool_buffer
            long_tool_pos = long_tool_pos + tool_pos_increment
            short_coord = short_coord + (tool_buffer / 2.0)

        setattr(tool_pos, short_key, short_coord)
        setattr(tool_pos, long_key, long_tool_pos)
        tool_template = ToolConfig(
            num=1,
            position=tool_pos,
            rotation_y=tool_rot,
            shape=tool_shape)
        FeatureCreationService.create_feature(
            scene, FeatureTypes.TOOLS, tool_template, bounds_to_check)
        # helps with distance_between_performer_and_tool calculations for
        # hooked bounding box shapes
        if tool_type == TOOL_HOOKED:
            tool = scene.objects[-1]
            tool['debug']['tool_thickness'] = tool_width / 3.0
            tool['debug']['length'] = tool_length

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
            if tool_type == TOOL_HOOKED else MIN_LAVA_WIDTH)
        buffer = 1.5 if long_side else \
            (3 if dimension_length % 2 == 0 else 1.5)
        total_max_width_in_dimension = math.floor(
            (dimension_length / (2 if long_side else 1)) - buffer)
        total_max_width_in_dimension = min(
            MAX_LAVA_WITH_ISLAND_WIDTH,
            total_max_width_in_dimension)

        if long_side and tool_type == TOOL_HOOKED:
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
            island_size = (1 if tool_type == TOOL_HOOKED else random.randint(
                MIN_LAVA_ISLAND_SIZE, max_island_size))

        total_accumulated_size += island_size

        # for the left and right lava sides in hooked tool scenes,
        # make sure lava extends to the wall
        if(not long_side and tool_type == TOOL_HOOKED):
            side_size = math.ceil((dimension_length - island_size) / 2.0)
            return island_size, side_size, side_size
        # Side 1
        side_two = side_two if side_two else min_lava_width
        max_side_one_width = (
            total_max_width_in_dimension - total_accumulated_size - side_two)

        if(tool_type == TOOL_HOOKED and (side_two or side_one)):
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

        if(tool_type == TOOL_HOOKED and (side_two or side_one)):
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

    def _get_tool_shape(self, tool_length, tool_type):
        tools = [
            tool
            for tool, (_, length) in LARGE_BLOCK_TOOLS_TO_DIMENSIONS.items()
            if (length == tool_length and
                ((TOOL_HOOKED in tool and tool_type == TOOL_HOOKED) or
                    ("rect" in tool and length != 1 and
                     tool_type == TOOL_RECTANGULAR)))
        ]
        return random.choice(tools)

    # Using only tools with a length of 1 for now
    def _get_too_small_tool(self):
        tools = [
            tool
            for tool, (_, length) in LARGE_BLOCK_TOOLS_TO_DIMENSIONS.items()
            if tool.startswith('tool_rect') and length == TOOL_LENGTH_TOO_SHORT
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

    def _get_or_add_soccer_ball_target(self, scene: Scene) -> Dict[str, Any]:
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
                rotation_amount = (ending_rotation - starting_rotation) % 360
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

    def _setup_containers_for_imitation_task(
            self, scene: Scene,
            config: ImitationTaskConfig) -> List:
        containers = []
        left_container_start_pos_z = \
            1 if config.containers_on_right_side else -1
        separation_between_containers = \
            -1 if config.containers_on_right_side else 1
        # Positive to negative z axis, positive is left, negative is right
        container_range = range(left_container_start_pos_z,
                                -left_container_start_pos_z * 2,
                                separation_between_containers)
        container_colors_used = []
        material_choices = materials._CUSTOM_WOOD_MATERIALS
        for container_index in container_range:
            pos_z = container_index
            scale = 0.55
            rotation_y = -90 if config.containers_on_right_side else 90
            for _ in range(MAX_TRIES):
                try_new_color = False
                material = random.choice(material_choices)
                colors = material[1]
                for color in colors:
                    if color in container_colors_used:
                        try_new_color = True
                        break
                if try_new_color:
                    continue
                for color in colors:
                    container_colors_used.append(color)
                break
            container_template = InteractableObjectConfig(
                position=Vector3d(
                    x=0.9 if config.containers_on_right_side else -0.9,
                    y=0,
                    z=pos_z),
                rotation=Vector3d(y=rotation_y),
                scale=Vector3d(
                    x=scale,
                    y=1,
                    z=scale),
                shape='chest_1',
                num=1,
                material=material[0]
            )
            FeatureCreationService.create_feature(
                scene, FeatureTypes.INTERACTABLE,
                container_template, find_bounds(scene))
            container_index = scene.objects[-1]
            containers.append(container_index)
        return containers, separation_between_containers

    def _setup_target_and_placer_imitation_task(self, scene: Scene,
                                                config: ImitationTaskConfig,
                                                containers):
        self.remove_target_on_error = True
        goal_template = GoalConfig(
            category=tags.SCENE.IMITATION,
            target=InteractableObjectConfig(
                position=Vector3d(x=0, y=0, z=0),
                shape='soccer_ball',
                scale=1))
        GoalServices.attempt_to_add_goal(scene, goal_template)

        target = scene.objects[-1]
        target['shows'][0]['position']['y'] = \
            scene.room_dimensions.y + target['debug']['dimensions']['y'] * 2
        placer = create_placer(
            target['shows'][0]['position'], target['debug']['dimensions'],
            target['debug']['positionY'], 0, 0, scene.room_dimensions.y
        )
        placer['triggeredBy'] = True
        scene.objects.append(placer)

        target['triggeredBy'] = True
        target['kinematic'] = True
        target['moves'] = [placer['moves'][0]]
        target['togglePhysics'] = [
            {'stepBegin': placer['changeMaterials'][0]['stepBegin']}]
        target['shows'][0]['position']['x'] = \
            containers[0]['shows'][0]['position']['x']
        placer['shows'][0]['position']['x'] = \
            target['shows'][0]['position']['x']

        # position in front of the left containers if containers on left
        # position in front of the right containers if containers on right
        target_separation = 0.5
        container_to_put_in_front_of_index = \
            -1 if config.containers_on_right_side else 0
        target['shows'][0]['position']['z'] = (
            containers[container_to_put_in_front_of_index
                       ]['shows'][0]['position']['z'] - target_separation)
        placer['shows'][0]['position']['z'] = \
            target['shows'][0]['position']['z']
        return target, placer

    def _setup_trigger_order_for_imitation_task(self, scene: Scene,
                                                config: ImitationTaskConfig,
                                                containers):
        trigger_order_ids = []
        solo_options = ['left', 'middle', 'right']
        left_options = ['left_middle', 'left_right']
        middle_options = ['middle_left', 'middle_right']
        right_options = ['right_middle', 'right_left']
        containers_to_open_indexes = []
        if config.trigger_order in solo_options:
            container_index = solo_options.index(config.trigger_order)
            trigger_order_ids.append(containers[container_index]['id'])
            containers_to_open_indexes.append(container_index)
        elif config.trigger_order in left_options:
            trigger_order_ids.append(containers[0]['id'])
            container_index = left_options.index(config.trigger_order)
            trigger_order_ids.append(
                containers[1 if container_index == 0 else 2]['id'])
            containers_to_open_indexes.append(0)
            containers_to_open_indexes.append(1 if container_index == 0 else 2)
        elif config.trigger_order in middle_options:
            trigger_order_ids.append(containers[1]['id'])
            container_index = middle_options.index(config.trigger_order)
            trigger_order_ids.append(
                containers[0 if container_index == 0 else 2]['id'])
            containers_to_open_indexes.append(1)
            containers_to_open_indexes.append(0 if container_index == 0 else 2)
        elif config.trigger_order in right_options:
            trigger_order_ids.append(containers[2]['id'])
            container_index = right_options.index(config.trigger_order)
            trigger_order_ids.append(
                containers[1 if container_index == 0 else 0]['id'])
            containers_to_open_indexes.append(2)
            containers_to_open_indexes.append(1 if container_index == 0 else 0)
        return trigger_order_ids, containers_to_open_indexes

    def _setup_agent_for_imitation_task(
        self, scene: Scene, config: ImitationTaskConfig, containers,
            containers_to_open_indexes):
        """
        Agent Setup
        1. Enter in front of starting chest
        2. Walk to chest
        3. Open (if only open one chest then end here and face performer)
        4. Walk to other chest
        5. Rotate to face chest
        6. Open the chest
        7. Face performer
        """
        step_begin_open_first_chest = 18
        step_end_open_first_chest = 28
        open_animation = "TPE_jump"
        turn_left_animation = "TPM_turnL45"
        turn_right_animation = "TPM_turnR45"
        walk_animation = "TPM_walk"

        movement_points = []
        number_of_containers = 0
        start_turning_step = None
        rotates = None
        for container_index in containers_to_open_indexes:
            movement_points.append(
                Vector3d(
                    x=0.5 if config.containers_on_right_side else -0.5,
                    y=0,
                    z=containers[container_index]['shows'][0]['position']['z']
                )
            )
            number_of_containers += 1
            if number_of_containers > 1:
                """
                Example of chest on the right:
                Rotate left because the agent walks toward the performer.
                Start
                  |     c opened
                  |     c
                Agent > c open this

                Performer
                """
                containers_on_right_side_agent_moving_toward_performer = (
                    config.containers_on_right_side and
                    container_index > containers_to_open_indexes[0])
                containers_on_left_side_agent_moving_away_from_performer = (
                    not config.containers_on_right_side and
                    container_index > containers_to_open_indexes[0])
                # negative is left turn, positive is right turn
                direction = (
                    -1 if
                    containers_on_right_side_agent_moving_toward_performer or
                    containers_on_left_side_agent_moving_away_from_performer
                    else 1)
                is_adjacent_container = (
                    container_index == containers_to_open_indexes[0] + 1 or
                    container_index == containers_to_open_indexes[0] - 1)
                # for some reason the left side needs one extra step
                extra_step = (
                    1 if
                    containers_on_left_side_agent_moving_away_from_performer
                    else 0)
                # With an origin point of the start container z position,
                # 57 and 82 are the number of steps required to reach the
                # adjacent or far container z position and be centered in
                # front of it
                start_turning_step = 57 + extra_step if \
                    is_adjacent_container else 82 + extra_step
                rotation_per_step = 9 * direction
                rotates = {
                    "stepBegin": start_turning_step,
                    "stepEnd": start_turning_step + 10,
                    "vector": {
                        "x": 0,
                        "y": rotation_per_step,
                        "z": 0
                    }
                }

        # End position facing the performer
        end_point_z = movement_points[-1].z - 0.15
        movement_points.append(
            Vector3d(
                x=0.5 if config.containers_on_right_side else -0.5,
                y=0,
                z=end_point_z))
        movement = AgentMovementConfig(
            animation=walk_animation,
            step_begin=1,
            points=movement_points,
            repeat=False
        )

        # Animations
        actions = []
        # The steps that each container is opened
        open_steps = []
        first_open = AgentActionConfig(
            step_begin=step_begin_open_first_chest,
            step_end=step_end_open_first_chest,
            is_loop_animation=False,
            id=open_animation
        )
        actions.append(first_open)
        open_steps.append(step_begin_open_first_chest)

        # Check if we are opening more than one chest
        # A turning animation is required to face the second chest
        if start_turning_step is not None:
            turn = AgentActionConfig(
                step_begin=start_turning_step,
                step_end=start_turning_step + 10,
                is_loop_animation=False,
                id=(turn_left_animation if rotates['vector']['y'] < 1
                    else turn_right_animation)
            )
            second_open = AgentActionConfig(
                step_begin=start_turning_step + 10,
                step_end=start_turning_step + 20,
                is_loop_animation=False,
                id=open_animation
            )
            actions.append(turn)
            actions.append(second_open)
            open_steps.append(start_turning_step + 10)

        # Config the agent in front of the first chest to open
        start_position = Vector3d(
            x=-0.2 if config.containers_on_right_side else 0.2, y=0,
            z=(containers[containers_to_open_indexes[0]]
                         ['shows'][0]['position']['z']))
        rotation_y = 90 if config.containers_on_right_side else -90
        agentConfig = AgentConfig(
            position=start_position,
            rotation_y=rotation_y,
            actions=actions,
            movement=movement
        )
        agent = FeatureCreationService.create_feature(
            scene, FeatureTypes.AGENT, agentConfig, [])[0]
        if rotates:
            agent['rotates'] = [rotates]

        # Open containers with animation timing
        i = 0
        for container_index in containers_to_open_indexes:
            containers[container_index]['openClose'] = [{
                'step': open_steps[i] + 4,
                'open': True
            }]
            i += 1

        return agent, open_steps

    def _change_container_and_agent_positions_during_kidnap(
            self, scene: Scene, config: ImitationTaskConfig, containers,
            separation_between_containers, kidnap_step, target,
            placer, agent):
        # Need to slightly shift depending on the start side since
        # the performer is offset to stay in the performers view
        buffer_for_all_containers_to_fit = 2
        buffer_for_agent_to_stand_behind = 1
        rotate_90 = (random.choice([True, False]) if
                     config.kidnap_option
                     is None else config.kidnap_option ==
                     ImitationKidnapOptions.CONTAINERS_ROTATE)
        if not rotate_90:
            start_x = round(random.uniform(-2.5, 2.5), 2)
            if not config.containers_on_right_side:
                start_z = round(random.uniform(
                    0,
                    scene.room_dimensions.z / 2 -
                    buffer_for_all_containers_to_fit -
                    buffer_for_agent_to_stand_behind), 2)
            else:
                start_z = round(random.uniform(
                    2,
                    scene.room_dimensions.z / 2 -
                    buffer_for_agent_to_stand_behind), 2)
        else:
            start_x = round(random.uniform(-2.5, 0.5), 2)
            start_z = round(random.uniform(
                0,
                scene.room_dimensions.z /
                2 -
                buffer_for_agent_to_stand_behind), 2)
        for container in containers:
            container['shows'].append({
                'stepBegin': kidnap_step,
                'position': {
                    'x': start_x,
                    'y': 0,
                    'z': start_z
                },
                'rotation': {
                    'y': (
                        180 if rotate_90
                        else container['shows'][0]['rotation']['y'])
                }
            })
            if not rotate_90:
                start_z += separation_between_containers
            else:
                start_x += abs(separation_between_containers)

        end_container = containers[
            -1 if config.containers_on_right_side else 0]

        # target and placer need to shift too
        target_separation = 0.5
        if rotate_90:
            target['shows'][1]['position']['x'] = (
                end_container['shows'][1]['position']['x'] +
                (target_separation *
                 (1 if config.containers_on_right_side else -1)))
            target['shows'][1]['position']['z'] = \
                end_container['shows'][1]['position']['z']
        else:
            target['shows'][1]['position']['x'] = \
                end_container['shows'][1]['position']['x']
            target['shows'][1]['position']['z'] = \
                end_container['shows'][1]['position']['z'] - target_separation
        placer['shows'][1]['position']['x'] = \
            target['shows'][1]['position']['x']
        placer['shows'][1]['position']['z'] = \
            target['shows'][1]['position']['z']

        # Place the agent behind
        end_container_pos = \
            containers[0 if config.containers_on_right_side
                       else -1]['shows'][1]['position']['z']
        separation = 1
        agent_z = end_container_pos + separation
        agent_x = random.choice(
            [containers[0]['shows'][1]['position']['x'] - separation,
                containers[-1]['shows'][1]['position']['x'] + separation])
        agent['shows'].append({
            'stepBegin': kidnap_step,
            'position': {
                'x': agent_x,
                'y': 0,
                'z': agent_z
            },
            'rotation': {
                'y': 180
            }
        })

        teleport_pos_x = scene.performer_start.position.x
        teleport_pos_z = scene.performer_start.position.z
        teleport_rot_y = scene.performer_start.rotation.y
        ActionService.add_teleports(
            scene.goal, [
                TeleportConfig(
                    step=kidnap_step, position_x=teleport_pos_x,
                    position_z=teleport_pos_z, rotation_y=teleport_rot_y)],
            False)

    def _teleport_performer_for_imitation_task(
            self, scene: Scene, agent,
            kidnap_step):
        # pick an x and z not in the center x of the room
        # so the teleport is substantial
        shift = 2.5
        x1 = round(random.uniform(
            -scene.room_dimensions.x / 2 + geometry.PERFORMER_WIDTH,
            -shift), 2)
        x2 = round(random.uniform(
            shift, scene.room_dimensions.x / 2 - geometry.PERFORMER_WIDTH),
            2)
        teleport_pos_x = random.choice([x1, x2])
        z1 = round(random.uniform(
            -scene.room_dimensions.z / 2 + geometry.PERFORMER_WIDTH,
            -shift), 2)
        z2 = round(random.uniform(
            shift, scene.room_dimensions.z / 2 - geometry.PERFORMER_WIDTH),
            2)
        teleport_pos_z = random.choice([z1, z2])
        ActionService.add_teleports(
            scene.goal, [
                TeleportConfig(
                    step=kidnap_step, position_x=teleport_pos_x,
                    position_z=teleport_pos_z, look_at_center=True)],
            False)
        end_habituation_string = scene.goal['action_list'][-1][0]
        teleport_rot_y_index = end_habituation_string.rfind('=')
        teleport_rot_y = int(
            end_habituation_string[teleport_rot_y_index + 1:])

        agent_z = random.choice([-2, 2])
        agent['shows'].append({
            'stepBegin': kidnap_step,
            # Put the agent still close the containers
            'position': {
                'x': random.uniform(-2, 2),
                'y': 0,
                'z': agent_z
            },
            'rotation': {
                'y': 180 if agent_z > 0 else 0
            }
        })
        scene.debug['endHabituationStep'] = kidnap_step
        scene.debug['endHabituationTeleportPositionX'] = teleport_pos_x
        scene.debug['endHabituationTeleportPositionZ'] = teleport_pos_z
        scene.debug['endHabituationTeleportRotationY'] = teleport_rot_y

    def _kidnap_performer_for_imitation_task(
        self, scene: Scene, config: ImitationTaskConfig, target, placer,
            agent, last_open_step, containers, containers_to_open_indexes,
            separation_between_containers):
        kidnap_step = last_open_step + placer['moves'][-1]['stepEnd'] + 10
        ActionService.add_freezes(scene.goal, [StepBeginEnd(1, kidnap_step)])

        placer_first_position = placer['shows'][0]['position']
        placer['shows'].append({
            'stepBegin': kidnap_step,
            'position': {
                'x': placer_first_position['x'],
                'y': placer_first_position['y'],
                'z': placer_first_position['z']
            }
        })
        target_first_position = target['shows'][0]['position']
        target['shows'].append({
            'stepBegin': kidnap_step,
            'position': {
                'x': target_first_position['x'],
                'y': target_first_position['y'],
                'z': target_first_position['z']
            }
        })

        # Close containers
        for container_index in containers_to_open_indexes:
            containers[container_index]['openClose'].append({
                'step': kidnap_step,
                'open': False
            })

        scene.debug['endHabituationStep'] = kidnap_step
        scene.debug['endHabituationTeleportPositionX'] = \
            scene.performer_start.position.x
        scene.debug['endHabituationTeleportPositionZ'] = \
            scene.performer_start.position.z
        scene.debug['endHabituationTeleportRotationY'] = \
            scene.performer_start.rotation.y
        # If we do NOT need to teleport anything, teleport the agent only
        if config.kidnap_option == ImitationKidnapOptions.AGENT_ONLY:
            agent['shows'].append({
                'stepBegin': kidnap_step,
                'position': {
                    'x': random.uniform(-2, 2),
                    'y': 0,
                    'z': 2
                },
                'rotation': {
                    'y': 180
                }
            })
            ActionService.add_teleports(
                scene.goal, [
                    TeleportConfig(
                        step=kidnap_step,
                        position_x=scene.performer_start.position.x,
                        position_z=scene.performer_start.position.z,
                        rotation_y=scene.performer_start.rotation.y)],
                False)
        # If we need to teleport the containers
        elif (config.kidnap_option == ImitationKidnapOptions.CONTAINERS or
              config.kidnap_option == ImitationKidnapOptions.CONTAINERS_ROTATE
              ):
            self._change_container_and_agent_positions_during_kidnap(
                scene, config, containers, separation_between_containers,
                kidnap_step, target, placer, agent)
        # If we need to teleport the performer
        else:
            self._teleport_performer_for_imitation_task(
                scene, agent, kidnap_step)

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
            config.kidnap_options = choose_random(
                [option.value for option in ImitationKidnapOptions])

        scene.performer_start.position.x = 0
        scene.performer_start.position.z = -3.75
        scene.performer_start.rotation.y = 0
        # Make a rectangular room
        base_dimension = random.randint(8, 10)
        rectangle_dimension = base_dimension * 2
        rectangle_direction = random.randint(0, 1)
        scene.room_dimensions.x = \
            base_dimension if rectangle_direction == 0 else rectangle_dimension
        scene.room_dimensions.y = 3
        scene.room_dimensions.z = \
            rectangle_dimension if rectangle_direction == 0 else base_dimension

        containers, separation_between_containers = \
            self._setup_containers_for_imitation_task(scene, config)

        target, placer = self._setup_target_and_placer_imitation_task(
            scene, config, containers)

        trigger_order_ids, containers_to_open_indexes = \
            self._setup_trigger_order_for_imitation_task(
                scene, config, containers)

        scene.goal['triggeredByTargetSequence'] = trigger_order_ids

        agent, open_steps = self._setup_agent_for_imitation_task(
            scene, config, containers, containers_to_open_indexes)

        # Now Kidnap the performer!!! ヽ(°o°)ﾉ
        self._kidnap_performer_for_imitation_task(
            scene, config, target, placer, agent, open_steps[-1], containers,
            containers_to_open_indexes, separation_between_containers)

        return scene

    def get_num_delayed_actions(self) -> int:
        count = 0
        count += 1 if self._delayed_perf_pos else 0
        count += 1 if self._delayed_turntables_with_agent_and_non_agent else 0
        return count

    def run_delayed_actions(self, scene: Dict[str, Any]) -> Dict[str, Any]:
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
        return scene

    def get_delayed_action_error_strings(self) -> List[str]:
        errors = []
        if self._delayed_perf_pos_reason:
            errors += [str(self._delayed_perf_pos_reason)]
        if self._delayed_turntables_with_agent_and_non_agent_reason:
            errors += [str(
                self._delayed_turntables_with_agent_and_non_agent_reason
            )]
        return errors
