import copy
import logging
import math
import random
from collections import namedtuple
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from machine_common_sense.config_manager import Vector3d

from generator import MAX_TRIES, ObjectBounds, Scene, geometry, materials
from generator.base_objects import LARGE_BLOCK_TOOLS_TO_DIMENSIONS
from generator.structures import (
    BASE_DOOR_HEIGHT,
    BASE_DOOR_WIDTH,
    create_guide_rails_around,
)
from ideal_learning_env.action_service import ActionService
from ideal_learning_env.actions_component import StepBeginEnd
from ideal_learning_env.agent_service import (
    DEFAULT_TEMPLATE_AGENT_MOVEMENT,
    AgentConfig,
    AgentCreationService,
)
from ideal_learning_env.goal_services import GoalConfig, GoalServices
from ideal_learning_env.interactable_object_service import (
    InteractableObjectConfig,
    KeywordLocationConfig,
)
from ideal_learning_env.numerics import (
    MinMaxFloat,
    MinMaxInt,
    RandomizableVectorFloat3d,
    VectorFloatConfig,
    VectorIntConfig,
)
from ideal_learning_env.object_services import (
    KeywordLocation,
    ObjectRepository,
)
from ideal_learning_env.validators import (
    ValidateNumber,
    ValidateOptions,
    ValidateOr,
)

from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import ILEException, choose_random, find_bounds
from .structural_object_service import (
    DOOR_MATERIAL_RESTRICTIONS,
    FeatureCreationService,
    FeatureTypes,
    FloorAreaConfig,
    PartitionFloorConfig,
    StructuralDoorConfig,
    StructuralPlatformConfig,
    ToolConfig,
)

logger = logging.getLogger(__name__)


DOOR_OCCLUDER_MIN_ROOM_Y = 5

EXTENSION_LENGTH_MIN = 0.5
EXTENSION_WIDTH = 1

MAX_LAVA_ISLAND_SIZE = 3
MIN_LAVA_ISLAND_SIZE = 1
MAX_LAVA_WIDTH = 6
MIN_LAVA_WIDTH = 2
MIN_LAVA_ISLAND_ROOM_LONG_LENGTH = 13
MIN_LAVA_ISLAND_ROOM_SHORT_LENGTH = 7


@dataclass
class LavaTargetToolConfig():
    """
    Defines details of the shortcut_lava_target_tool shortcut.  This shortcut
    creates a room with a target object on an island surrounded by lava. There
    will also be a block tool to facilitate acquiring the goal object.
    - `front_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles of lava in front of the island.  Must produce value
    between 2 and 6. Default: Random based on room size and island size
    - `guide_rails` (bool, or list of bools): If True, guide rails will be
    generated to guide the tool in the direction it is oriented.  If a target
    exists, the guide rails will extend to the target.  This option cannot be
    used with `tool_rotation`. Default: False
    - `island_size` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): The width and lenght of the island inside the
    lava.  Must produce value from 1 to 3.
    Default: Random based on room size
    - `random_performer_position` (bool, or list of bools): If True, the
    performer will be randomly placed in the room. They will not be placed in
    the lava or the island   Default: False
    - `random_target_position` (bool, or list of bools): If True, the
    target object will be positioned randomly in the room, rather than being
    positioned on the island surrounded by lava. Default: False
    - `rear_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles of lava behind of the island.  Must produce value
    between 2 and 6. Default: Random based on room size, island size, and
    other lava widths.
    - `tool_rotation` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    Angle that too should be rotated out of alignment with target.
    This option cannot be used with `guide_rails`.  Default: 0
    """
    island_size: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    front_lava_width: Union[int, MinMaxInt,
                            List[Union[int, MinMaxInt]]] = None
    rear_lava_width: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    guide_rails: Union[bool, List[bool]] = False
    tool_rotation: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = 0
    random_performer_position: Union[bool, List[bool]] = False
    random_target_position: Union[bool, List[bool]] = False


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
    Defines details of the shortcut_agent_with_target shortcut.  This shortcut
    creates a room with an agent holding a target soccer ball.  The agent's
    position can be specified.
    - `agent_position` ([VectorFloatConfig](#VectorFloatConfig) or list of
    [VectorFloatConfig](#VectorFloatConfig)): Determines the position of the
    agent.  Default: Random
    - `movement_bounds` (list of [VectorFloatConfig](#VectorFloatConfig))
    points to generate a polygon that bounds the agents random movement.
    If the polygon has an area of 0, no movement will occur.  Polygons with
    only 1 or 2 points will have an area of 0 and therefore will have no
    movement.  Default: entire room
    """

    agent_position: RandomizableVectorFloat3d = None
    movement_bounds: List[RandomizableVectorFloat3d] = None


@dataclass
class BisectingPlatformConfig():
    """
    Defines details of the shortcut_bisecting_platform shortcut.  This shortcut
    creates a platform that bisects the room, where the performer will start.
    On default, a blocking wall is on that platform, forcing the performer
    to choose a side to drop off of the platform, but this can be disabled.
    - `has_blocking_wall` (bool): Enables the blocking wall so that the
    performer has to stop and choose a side of the room. Default: True
    """
    has_blocking_wall: bool = True


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
    One dimension of the room must be 13 or greater.  The other dimension must
    be 7 or greater.  By default, the target is a soccer ball with scale
    between 1 and 3. The tool is a pushable tool object with a length equal
    to the span from the front of the lava over the island to the back of the
    lava.  It will have a width of either 0.5, 0.75, 1.0. Default: False

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
      guide_rails: [True, False]
    ```
    """

    shortcut_agent_with_target: Union[bool,
                                      AgentTargetConfig,
                                      List[Union[bool,
                                                 AgentTargetConfig]]] = False
    """
    (bool or [AgentTargetConfig](#AgentTargetConfig)):
    Creates a room with an agent holding a target soccer ball.  The agent's
    position can be specified.

    Simple Example:
    ```
    shortcut_agent_with_target: False
    ```

    Advanced Example:
    ```
    shortcut_agent_with_target:
      agent_position:
        x:
          min: 1
          max: 3
        y: 0
        z: [2, 3]
      movement_bounds:
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

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self._delayed_perf_pos = False
        self._delayed_perf_pos_reason = None

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

    @ile_config_setter()
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

    def get_shortcut_agent_with_target(
            self) -> Union[bool, AgentTargetConfig]:
        if not self.shortcut_agent_with_target:
            return False
        template = copy.deepcopy(self.shortcut_agent_with_target)
        if isinstance(self.shortcut_agent_with_target, List):
            template = random.choice(template)
        if template is True:
            template = AgentTargetConfig()
        bounds = template.movement_bounds or []
        template.movement_bounds = None
        # choose random fails with an empty array and we want to process the
        # array manually anyway, so we've saved the value.
        config = choose_random(template)
        config.movement_bounds = [
            choose_random(point) for point in bounds]
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

        return scene

    def _add_bisecting_platform(self, scene: Scene, room_dim: Vector3d):
        if not self.get_shortcut_bisecting_platform():
            return scene

        logger.trace("Adding bisecting platform shortcut")
        config = self.get_shortcut_bisecting_platform()
        self._do_add_bisecting_platform(scene, room_dim,
                                        config.has_blocking_wall)

        return scene

    def _do_add_bisecting_platform(
            self, scene: Scene, room_dim: Vector3d,
            blocking_wall: bool = False,
            platform_height=1):

        # Second platform is the wall to prevent performer from moving too
        # far before getting off the platform.  Since walls go to the
        # ceiling and platforms all start on the floor, we overlap this
        # platform.

        bounds = find_bounds(scene)
        performer_z = -room_dim.z / 2.0
        platform = StructuralPlatformConfig(
            num=1, position=VectorFloatConfig(0, 0, 0), rotation_y=0,
            scale=VectorFloatConfig(1, platform_height, room_dim.z))
        blocking_wall_platform = StructuralPlatformConfig(
            num=1, position=VectorFloatConfig(0, 0, performer_z + 1.5),
            rotation_y=0,
            scale=VectorFloatConfig(0.99, platform_height + 0.25, 0.1))
        scene.set_performer_start_position(
            x=0, y=platform.scale.y, z=(performer_z) + 0.5)
        scene.set_performer_start_rotation(0)

        struct_type = FeatureTypes.PLATFORMS
        FeatureCreationService.create_feature(
            scene, struct_type, platform, bounds)
        if blocking_wall:
            FeatureCreationService.create_feature(
                # Ignore the platform's bounds
                scene, struct_type, blocking_wall_platform, bounds[:-1])
        return bounds

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
            scene.set_performer_start_rotation(random.randint(-90, 90))

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

    LavaSizes = namedtuple('LavaIslandSizes', (
        'island_size',
        'front_lava_width',
        'rear_lava_width',
        'short_lava_width'))

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

        for _ in range(MAX_TRIES):
            try:
                self.remove_target_on_error = False
                bounds = find_bounds(scene)
                # Test room size and determine sizes
                long_length = max(room_dim.x, room_dim.z)
                short_length = min(room_dim.x, room_dim.z)
                long_key, short_key = (('z', 'x') if long_length ==
                                       room_dim.z else ('x', 'z'))

                # place performer
                start = scene.performer_start.position
                setattr(start, long_key, - (long_length / 2.0 - 0.5))
                scene.performer_start.rotation.y = (
                    0 if long_key == 'z' else 90)

                sizes = self._compute_lava_sizes(
                    long_length, short_length, long_key, short_key, config)

                setattr(
                    start,
                    short_key,
                    0 if sizes.island_size %
                    2 == 1 else 0.5)

                tool_length = (
                    sizes.rear_lava_width +
                    sizes.front_lava_width +
                    sizes.island_size)

                # if size 13, edge is whole tiles at 6, buffer should be 6,
                # if size 14, dges is half tile at 7, buffer should be 6
                long_buffer_coord = math.floor(long_length / 2.0 - 0.5)
                long_far_island_coord = (
                    long_buffer_coord - sizes.rear_lava_width - 1)
                long_near_island_coord = (
                    long_far_island_coord - sizes.island_size + 1)
                short_left_island_coord = - \
                    math.floor((sizes.island_size - 1) / 2)
                short_right_island_coord = math.ceil(
                    (sizes.island_size - 1) / 2.0)

                # Find or create the target and position it on the island
                if not config.random_target_position:
                    self._add_target_to_lava_island(
                        scene,
                        long_key,
                        short_key,
                        sizes.island_size,
                        long_far_island_coord,
                        long_near_island_coord
                    )
                    target = scene.objects[-1]

                # Encircle island with lava
                self._add_lava_around_island(
                    scene, bounds, long_key, sizes.front_lava_width,
                    sizes.rear_lava_width, sizes.short_lava_width,
                    long_far_island_coord, long_near_island_coord,
                    short_left_island_coord, short_right_island_coord)

                # Add the island to the bounds list so that no additional
                # objects will be randomly positioned there in the future.
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

                # Add block tool
                self._add_tool(
                    scene,
                    bounds + [island_bounds],
                    sizes.island_size,
                    long_key,
                    short_key,
                    sizes.front_lava_width,
                    tool_length,
                    long_near_island_coord,
                    config.tool_rotation)
                tool = scene.objects[-1]

                if config.guide_rails:
                    self._add_guide_rails(scene, long_key, short_key,
                                          tool_length, target, tool)

                # Create the target and position it randomly, if needed
                if config.random_target_position:
                    target = scene.get_target_object()
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
                    self._randomize_performer_position(
                        scene,
                        long_key, short_key, long_near_island_coord,
                        long_far_island_coord, sizes)
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

    def _add_guide_rails(self, scene, long_key,
                         short_key, tool_length, target, tool):
        tool_pos = tool['shows'][0]['position']
        rot = tool['shows'][0]['rotation']['y']
        target_pos = target['shows'][0]['position']
        center = VectorIntConfig(y=tool_pos['y'])
        setattr(center, short_key, target_pos[short_key])
        c = ((
            target_pos[long_key] + tool_pos[long_key] -
            tool_length / 2.0) / 2.0)
        setattr(center, long_key, c)
        length = (target_pos[long_key] - tool_pos[long_key] +
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
                                      long_far_island_coord, sizes: LavaSizes):
        no_go_long_min = long_near_island_coord - sizes.front_lava_width - 0.5
        no_go_long_max = long_far_island_coord + sizes.rear_lava_width + 0.5

        # for island size 1, 2, 3; island bounds are :
        # min is -0.5, -0.5, -1.5
        # max is 0.5, 1.5, 1.5
        no_go_short_min = math.floor(-sizes.island_size / 2.0) + \
            0.5 - sizes.short_lava_width
        no_go_short_max = math.floor(
            sizes.island_size / 2.0) + 0.5 + sizes.short_lava_width

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
            self, scene: Scene, long_key, short_key, island_size,
            long_far_island_coord, long_near_island_coord):
        target = scene.get_target_object()

        # put target in middle of island
        pos = VectorFloatConfig()
        pos.y = 0
        # if even island size, shift in positive direction
        short_coord = 0 if island_size % 2 == 1 else 0.5
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
            category="retrieval",
            target=InteractableObjectConfig(
                shape='soccer_ball',
                position=position,
                scale=MinMaxFloat(1.0, 3.0)))
        goal_specific: GoalConfig = choose_random(goal_template)
        GoalServices.attempt_to_add_goal(scene, goal_specific)

    def _add_tool(self, scene, bounds, island_size, long_key, short_key,
                  front_lava_width, tool_length, long_near_island_coord,
                  tool_rotation=False):
        tool_shape = self._get_tool_shape(tool_length)
        tool_rot = 0 if long_key == 'z' else 90
        if tool_rotation:
            tool_rot += tool_rotation
        tool_pos = VectorFloatConfig(y=0)
        long_tool_pos = (long_near_island_coord -
                         front_lava_width - 1 - tool_length / 2.0 - 0.5)
        short_coord = 0 if island_size % 2 == 1 else 0.5
        setattr(tool_pos, short_key, short_coord)
        setattr(tool_pos, long_key, long_tool_pos)
        tool_template = ToolConfig(
            num=1,
            position=tool_pos,
            rotation_y=tool_rot,
            shape=tool_shape)
        FeatureCreationService.create_feature(
            scene, FeatureTypes.TOOLS, tool_template, bounds)

    def _compute_lava_sizes(
            self, long_length, short_length, long_key, short_key,
            config: LavaTargetToolConfig):
        buffer = 1.5
        if config.island_size:
            island_size = config.island_size
        else:
            local_max = math.floor(
                long_length / 2.0 - buffer - 2 * MIN_LAVA_WIDTH)
            if local_max < 1:
                raise ILEException(
                    f"Not enough space in the long ({long_key}) direction "
                    f"with size {long_length}.  This dimension must be "
                    f"atleast {MIN_LAVA_ISLAND_ROOM_LONG_LENGTH}.")
            island_size = random.randint(
                MIN_LAVA_ISLAND_SIZE, min(local_max, MAX_LAVA_ISLAND_SIZE))

        if config.front_lava_width:
            front_lava_width = config.front_lava_width
        else:
            # max length with 1 on either end for performer, length of
            # Tool that can span the whole the whole lava and island with
            # min lava on other end.
            local_max = math.floor(long_length / 2.0 - island_size -
                                   MIN_LAVA_WIDTH - buffer)
            front_lava_width = random.randint(
                MIN_LAVA_WIDTH,
                min(MAX_LAVA_WIDTH, local_max))

        local_max = math.floor(
            long_length / 2.0 - island_size -
            front_lava_width - buffer)
        if local_max < 2:
            raise ILEException(
                f"Not enough space in the long ({long_key}) direction "
                f"with current choices. Need to retry: "
                f"Island size = {island_size} "
                f"Front lava width = {front_lava_width}"
                f"Long length = {long_length}")
        if config.rear_lava_width:
            if (config.rear_lava_width > MAX_LAVA_WIDTH or
                    config.rear_lava_width < MIN_LAVA_WIDTH):
                raise ILEException(
                    "Unable to create lava island with configuration")
            rear_lava_width = config.rear_lava_width
        else:
            rear_lava_width = random.randint(
                MIN_LAVA_WIDTH,
                min(MAX_LAVA_WIDTH, local_max))

        # keep this uniform on both sides for now
        short_lava_width_max = math.floor(
            (short_length - island_size - buffer) / 2.0)
        local_max = min(short_lava_width_max, MAX_LAVA_WIDTH)
        if local_max < 2:
            raise ILEException(
                f"Not enough space in short ({short_key}) direction "
                f"with size {short_length} and island size "
                f"{island_size}. This dimension must be atleast "
                f"{MIN_LAVA_ISLAND_ROOM_SHORT_LENGTH}.")
        short_lava_width = random.randint(MIN_LAVA_WIDTH, local_max)
        return self.LavaSizes(island_size, front_lava_width,
                              rear_lava_width, short_lava_width)

    def _add_lava_around_island(
            self, scene, bounds, long_key, front_lava_width,
            rear_lava_width, short_lava_width,
            long_far_island_coord, long_near_island_coord,
            short_left_island_coord, short_right_island_coord):
        try:
            long_range = range(
                long_near_island_coord - front_lava_width,
                long_near_island_coord)
            short_range = range(short_left_island_coord - short_lava_width,
                                short_right_island_coord + short_lava_width +
                                1)
            self._add_lava_range(
                scene, bounds, long_key, long_range, short_range)

            long_range = range(long_far_island_coord + 1,
                               long_far_island_coord + rear_lava_width + 1,
                               )
            self._add_lava_range(
                scene, bounds, long_key, long_range, short_range)

            long_range = range(
                long_near_island_coord,
                long_far_island_coord + 1)
            short_range = range(short_left_island_coord -
                                short_lava_width,
                                short_left_island_coord)

            self._add_lava_range(
                scene, bounds, long_key, long_range, short_range)

            short_range = range(
                short_right_island_coord + 1,
                short_right_island_coord + 1 + short_lava_width)
            self._add_lava_range(
                scene, bounds, long_key, long_range, short_range)
        except Exception as e:
            scene.lava = []
            # sourcery recommends the 'from e'
            raise e from e

    def _add_lava_range(self, scene, bounds, long_key,
                        long_range, short_range):
        logger.trace(f"Adding lava with ranges {long_range} {short_range}")
        for long in long_range:
            for short in short_range:
                (x, z) = (long, short) if long_key == 'x' else (short, long)
                logger.trace(f"Adding lava at {x},{z}")
                lava = FloorAreaConfig(
                    num=1, position_x=x, position_z=z)
                FeatureCreationService.create_feature(
                    scene, FeatureTypes.LAVA, lava, bounds
                )

    def _get_tool_shape(self, tool_length):
        tools = [
            tool
            for tool, (_, length) in LARGE_BLOCK_TOOLS_TO_DIMENSIONS.items()
            if length == tool_length
        ]
        return random.choice(tools)

    def _add_agent_holds_target(self, scene: Scene):
        config: AgentTargetConfig = self.get_shortcut_agent_with_target()
        if not config:
            return scene
        logger.trace("Adding agent with target shortcut")
        target = scene.get_target_object()

        bounds = find_bounds(scene)
        agentConfig = AgentConfig(position=config.agent_position)

        agents = FeatureCreationService.create_feature(
            scene, FeatureTypes.AGENT, agentConfig, bounds)
        agent = agents[0]

        agent_keyword_loc = KeywordLocationConfig(
            keyword=KeywordLocation.ASSOCIATED_WITH_AGENT,
            relative_object_label=agent['id'])
        if target:
            KeywordLocation.associate_with_agent(
                agent_keyword_loc, target)
        else:
            rot = VectorIntConfig(0, choose_random(MinMaxInt(0, 359)), 0)
            goal_template = GoalConfig(
                category="retrieval",
                target=InteractableObjectConfig(
                    shape='soccer_ball',
                    keyword_location=agent_keyword_loc,
                    scale=VectorFloatConfig(1, 1, 1),
                    rotation=rot))
            GoalServices.attempt_to_add_goal(scene, goal_template)
        movement_template = choose_random(DEFAULT_TEMPLATE_AGENT_MOVEMENT)
        movement_template.bounds = config.movement_bounds
        AgentCreationService.add_random_agent_movement(
            scene, agent, movement_template)
        return scene

    def get_num_delayed_actions(self) -> int:
        return 1 if self._delayed_perf_pos else 0

    def run_delayed_actions(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        if self._delayed_perf_pos:
            try:
                self._position_performer_on_platform(scene)
            except Exception as e:
                self._delayed_perf_pos_reason = e
        return scene

    def get_delayed_action_error_strings(self) -> List[str]:
        return [str(self._delayed_perf_pos_reason)
                ] if self._delayed_perf_pos_reason else []
