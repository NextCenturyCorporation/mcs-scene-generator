import logging
import math
import random
from collections import namedtuple
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from generator import MAX_TRIES, geometry, materials
from generator.base_objects import LARGE_BLOCK_TOOLS_TO_DIMENSIONS
from generator.structures import create_guide_rails_around
from ideal_learning_env.action_generator import add_freezes
from ideal_learning_env.actions_component import StepBeginEnd
from ideal_learning_env.goal_services import (
    GoalConfig,
    GoalServices,
    get_target_object,
)
from ideal_learning_env.interactable_object_config import (
    InteractableObjectConfig,
)
from ideal_learning_env.numerics import (
    MinMaxFloat,
    MinMaxInt,
    VectorFloatConfig,
    VectorIntConfig,
)
from ideal_learning_env.object_services import ObjectRepository
from ideal_learning_env.validators import ValidateNumber, ValidateOptions

from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import ILEException, choose_random, find_bounds
from .structural_object_generator import (
    DOOR_MATERIAL_RESTRICTIONS,
    FloorMaterialConfig,
    StructuralDoorConfig,
    StructuralPlatformConfig,
    StructuralRampConfig,
    StructuralTypes,
    ToolConfig,
    add_structural_object_with_retries_or_throw,
)

logger = logging.getLogger(__name__)

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
    creates a room with a goal object on an island surrounded by lava. There
    will also be a block tool to facilitate acquiring the goal object.
    - `island_size` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): The width and lenght of the island inside the
    lava.  Must produce value from 1 to 3.
    Default: Random based on room size
    - `front_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles of lava in front of the island.  Must produce value
    between 2 and 6. Default: Random based on room size and island size
    - `rear_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    The number of tiles of lava behind of the island.  Must produce value
    between 2 and 6. Default: Random based on room size, island size, and
    other lava widths.
    - `guide_rails` (bool, or list of bools): If True, guide rails will be
    generated to guide the tool in the direction it is oriented.  If a target
    exists, the guide rails will extend to the target.  This option cannot be
    used with `tool_rotation`. Default: False
    - `tool_rotation` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
    Angle that too should be rotated out of alignment with target.
    This option cannot be used with `guide_rails`.  Default: 0
    - `random_performer_position` (bool, or list of bools): If True, the
    performer will be randomly placed in the room. They will not be placed in
    the lava or the island   Default: False
    """
    island_size: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    front_lava_width: Union[int, MinMaxInt,
                            List[Union[int, MinMaxInt]]] = None
    rear_lava_width: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    guide_rails: Union[bool, List[bool]] = False
    tool_rotation: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = 0
    random_performer_position: Union[bool, List[bool]] = False


@dataclass
class TripleDoorConfig():
    """
    Defines details of the triple door shortcut.  This short cut contains a
    platform that bisects the room.  A wall with 3 doors (a.k.a. door occluder,
    or "door-cluder" or "doorcluder") will bisect the room
    in the perpendicular direction.

    - `start_drop_step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): Step number to start dropping the bisecting
    wall with doors.  If None or less than 1, the wall will start in position.
    Default: None
    - `add_lips` (bool, or list of bools): If true, lips will be added on the
    platform beyond the doors and wall such that the performer will be forced
    to go through the corresponding door to enter the area behind it.
    Default: True
    - `add_freeze` (bool, or list of bools): If true and 'start_drop_step is'
    greater than 0, the user will be frozen (forced to Pass) until the wall and
    doors are in position.  If the 'start_drop_step' is None or less than 1,
    this value has no effect.  Default: True
    - `restrict_open_doors` (bool, or list of bools): If true, the performer
    will only be able to open one door.  Using this feature and 'add_lips'
    will result in a forced choice by the performer.  Default: True
    - `door_material` (string, or list of strings): The material or material
    type for the doors.
    - `wall_material` (string, or list of strings): The material or material
    type for the wall.
    """
    start_drop_step: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    add_lips: Union[bool, List[bool]] = True
    add_freeze: Union[bool, List[bool]] = True
    restrict_open_doors: Union[bool, List[bool]] = True
    door_material: Union[str, List[str]] = None
    wall_material: Union[str, List[str]] = None


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

    shortcut_bisecting_platform: bool = False
    """
    (bool): Creates a platform bisecting the room.  The performer starts on one
    end with a wall in front of them such that the performer is forced to make
    a choice on which side they want to drop off and they cannot get back to
    the other side.  Default: False

    Simple Example:
    ```
    shortcut_bisecting_platform: False
    ```

    Advanced Example:
    ```
    shortcut_bisecting_platform: True
    ```
    """

    shortcut_triple_door_choice: Union[bool, TripleDoorConfig] = False
    """
    (bool or [TripleDoorConfig](#TripleDoorConfig)):
    Creates a platform bisecting the room with a wall with 3 doors
    (a.k.a. door occluder, or "door-cluder" or "doorcluder").
    The performer starts on one end such that the performer is forced to make
    a choice on which door they want to open.  By default, the doors will be
    restricted so only one can be opened.  Default: False

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

    shortcut_ramp_to_platform: bool = False
    """
    (bool): Creates a ramp with a platform connected to it such that a
    performer can climb the ramp up to the platform. Will automatically add the
    "platform_next_to_ramp" label to the platform and the
    "ramp_next_to_platform" label to the ramp.  Default: False

    Simple Example:
    ```
    shortcut_ramp_to_platform: False
    ```

    Advanced Example:
    ```
    shortcut_ramp_to_platform: True
    ```
    """

    shortcut_start_on_platform: bool = False
    """
    (bool): Ensures that the performer will start on top of a platform. In
    order for this to work, `structural_platforms` needs to be specified
    using the label `start_structure`.

    Default: False

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
    performer will start in the center (non-lava) part.

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
    lava.  It will have a width of either 0.5, 0.75, 1.0.

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

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self._delayed_perf_pos = False

    def set_shortcut_bisecting_platform(self, data: Any) -> None:
        self.shortcut_bisecting_platform = data

    def get_shortcut_bisecting_platform(
            self) -> bool:
        return self.shortcut_bisecting_platform

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

    def set_shortcut_ramp_to_platform(self, data: Any) -> None:
        self.shortcut_ramp_to_platform = data

    def get_shortcut_ramp_to_platform(
            self) -> bool:
        return self.shortcut_ramp_to_platform

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

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring shortcut options for the scene...')
        room_dim = scene['roomDimensions']

        scene = self._add_bisecting_platform(scene, room_dim)
        scene = self._add_triple_door_shortcut(scene, room_dim)
        scene = self._add_ramp_to_platform(scene, room_dim)
        scene = self._delay_performer_placement(scene, room_dim)
        scene = self._add_lava_shortcut(scene, room_dim)
        scene = self._add_tool_lava_goal(scene, room_dim)

        return scene

    def _add_bisecting_platform(self, scene, room_dim):
        if self.get_shortcut_bisecting_platform():
            logger.trace("Adding bisecting platform shortcut")
            self._do_add_bisecting_platform(scene, room_dim, True)

        return scene

    def _do_add_bisecting_platform(
            self, scene, room_dim, blocking_wall: bool = False,
            platform_height=1):
        scene['objects'] = scene.get('objects', [])

        # Second platform is the wall to prevent performer from moving too
        # far before getting off the platform.  Since walls go to the
        # ceiling and platforms all start on the floor, we overlap this
        # platform.

        bounds = find_bounds(scene)
        performer_z = -room_dim['z'] / 2.0
        platform = StructuralPlatformConfig(
            num=1, position=VectorFloatConfig(0, 0, 0), rotation_y=0,
            scale=VectorFloatConfig(1, platform_height, room_dim['z']))
        blocking_wall_platform = StructuralPlatformConfig(
            num=1, position=VectorFloatConfig(0, 0, performer_z + 1.5),
            rotation_y=0,
            scale=VectorFloatConfig(0.99, platform_height + 0.25, 0.1))
        scene['performerStart']['position'] = {
            'x': 0,
            'y': platform.scale.y,
            'z': (performer_z) + 0.5
        }
        scene['performerStart']['rotation']['y'] = 0

        struct_type = StructuralTypes.PLATFORMS
        add_structural_object_with_retries_or_throw(
            scene, bounds, MAX_TRIES, platform, struct_type)
        if blocking_wall:
            add_structural_object_with_retries_or_throw(
                # Ignore the platform's bounds
                scene, bounds[:-1], MAX_TRIES, blocking_wall_platform,
                struct_type)
        return bounds

    def _add_triple_door_shortcut(self, scene, room_dim):
        if config := self.get_shortcut_triple_door_choice():
            logger.trace("Adding triple door occluding choice shortcut")
            self._do_add_triple_door_shortcut(
                scene, room_dim, config=config)
        return scene

    def _do_add_triple_door_shortcut(
            self, scene, room_dim, config: TripleDoorConfig):
        if config is None:
            config = TripleDoorConfig()
        dropping = (
            config.start_drop_step is not None and config.start_drop_step > 0)
        add_y = room_dim['y'] if dropping else 0
        bounds = self._do_add_bisecting_platform(scene, room_dim, False, 2)
        if config.add_lips:
            plat = scene['objects'][-1]
            plat['lips']['left'] = True
            plat['lips']['right'] = True
            plat['lips']['gaps'] = {
                'left': [{'high': 0.5, 'low': 0}],
                'right': [{'high': 0.5, 'low': 0}]}
        rot_y = 0
        door_center_template = StructuralDoorConfig(
            num=1, position=VectorFloatConfig(
                0, 2 + add_y, 0), rotation_y=rot_y, wall_scale_x=1,
            wall_scale_y=2.25, material=config.door_material,
            wall_material=config.wall_material)

        door_index = len(scene.get('objects', 0))

        add_structural_object_with_retries_or_throw(
            scene, bounds, MAX_TRIES, door_center_template,
            StructuralTypes.DOORS)
        wall = scene['objects'][-1]
        wall_mat = wall['materials'][0]
        door = scene['objects'][door_index]
        door_mat = door['materials'][0]
        side_wall_scale_x = room_dim['x'] / 2.0 - 0.5
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

        add_structural_object_with_retries_or_throw(
            scene, [], MAX_TRIES, door_right_template,
            StructuralTypes.DOORS)
        add_structural_object_with_retries_or_throw(
            scene, [], MAX_TRIES, door_left_template,
            StructuralTypes.DOORS)

        if dropping:
            self._add_door_drops(scene, config.start_drop_step,
                                 add_y, door_index)
            if config.add_freeze:
                goal = scene.get('goal', {})
                step_end = config.start_drop_step + add_y * 4
                freezes = [StepBeginEnd(1, step_end)]
                add_freezes(goal, freezes)
        scene['restrictOpenDoors'] = config.restrict_open_doors

    def _add_door_drops(self, scene, start_drop_step, add_y, door_index):
        for i in range(door_index, len(scene['objects'])):
            obj = scene['objects'][i]
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

    def _add_lava_shortcut(self, scene, room_dim):
        if self.get_shortcut_lava_room():
            logger.trace("Adding lava shortcut")
            scene['lava'] = scene.get('lava', [])
            scene['objects'] = scene.get('objects', [])

            bounds = find_bounds(scene)

            struct_type = StructuralTypes.LAVA

            # position performer in the center non-lava part,
            # in the back of the room, facing forward.
            scene['performerStart']['position'] = {
                'x': 0,
                'y': scene['performerStart']['position']['y'],
                'z': -1 * (room_dim['z'] / 2.0) + 0.5
            }

            scene['performerStart']['rotation']['y'] = random.randint(-90, 90)

            step = 1

            # find the width along the x axis of
            # each lava section, and the min/max values
            # along the x axis
            x_lava_width = math.floor(room_dim['x'] / 3.0)
            x_max = room_dim['x'] / 2.0
            x_min = math.ceil(x_max - x_lava_width)
            x_values = range(x_min, math.floor(x_max) + step)

            # need to create lava all along the z axis
            z_max = int(room_dim['z'] / 2.0)
            z_min = -1 * z_max
            z_values = range(z_min, z_max + step)

            for z in z_values:
                for x in x_values:
                    lava_neg_x = FloorMaterialConfig(
                        num=1, position_x=-x, position_z=z)
                    lava_pos_x = FloorMaterialConfig(
                        num=1, position_x=x, position_z=z)

                    add_structural_object_with_retries_or_throw(
                        scene, bounds, MAX_TRIES, lava_neg_x, struct_type)

                    add_structural_object_with_retries_or_throw(
                        scene, bounds, MAX_TRIES, lava_pos_x, struct_type)

        return scene

    def _delay_performer_placement(self, scene, room_dim):
        if not self.get_shortcut_start_on_platform():
            return scene

        self._delayed_perf_pos = True
        logger.trace("Delaying start on platform shortcut")
        scene['objects'] = scene.get('objects', [])

        # Place performer outside of room until their
        # start platform is created
        scene['performerStart']['position'] = {
            'x': room_dim['x'],
            'y': 0,
            'z': room_dim['z']
        }

        return scene

    def _position_performer_on_platform(self, scene):
        logger.trace("Adding start on platform shortcut")
        obj_repo = ObjectRepository.get_instance()

        bounds = find_bounds(scene)

        struct = obj_repo.get_one_from_labeled_objects(
            self.LABEL_START_PLATFORM
        )

        if struct is None:
            return

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

        valid = False
        perf_pos = {}

        for _ in range(MAX_TRIES):
            perf_pos = {
                'x': round(random.uniform(min_x, max_x), 3),
                'y': struct_scale['y'],
                'z': round(random.uniform(min_z, max_z), 3)
            }

            new_perf_bounds = geometry.create_bounds(
                dimensions={
                    "x": geometry.PERFORMER_WIDTH,
                    "y": geometry.PERFORMER_HEIGHT,
                    "z": geometry.PERFORMER_WIDTH
                },
                offset=None,
                position=perf_pos,
                rotation=scene['performerStart']['rotation'],
                standing_y=0
            )

            valid = geometry.validate_location_rect(
                location_bounds=new_perf_bounds,
                performer_start_position=scene['performerStart']['position'],
                bounds_list=bounds,
                room_dimensions=scene['roomDimensions']
            )

            if valid:
                break

        if valid:
            scene['performerStart']['position'] = perf_pos
            self._delayed_perf_pos = False
        else:
            raise ILEException(
                "Attempt to position performer on chosen " +
                "platform failed.")

    def _add_ramp_to_platform(self, scene, room_dim):
        last_exception = None
        if not self.shortcut_ramp_to_platform:
            return scene
        logger.trace("Adding ramp to platform shortcut")
        scene['objects'] = scene.get('objects', [])
        num_prev_objs = len(scene['objects'])
        for _ in range(MAX_TRIES):
            try:
                bounds = find_bounds(scene)
                # need 2 copies of bounds since the two objects will overlap
                # intentionally and adding the ramp will alter the first copy
                bounds2 = find_bounds(scene)
                angle = random.randint(
                    self.RAMP_ANGLE_MIN, self.RAMP_ANGLE_MAX)
                radians = math.radians(angle)

                min_length = (
                    self.RAMP_TO_PLATFORM_MIN_HEIGHT) / math.tan(radians)
                max_length = (
                    (room_dim['y'] -
                     self.RAMP_TO_PLATFORM_MIN_DIST_TO_CEILING) /
                    math.tan(radians))

                ramp_config = StructuralRampConfig(
                    num=1,
                    angle=angle,
                    length=MinMaxFloat(min_length, max_length),
                    labels=['ramp_next_to_platform']
                )
                add_structural_object_with_retries_or_throw(
                    scene,
                    bounds,
                    MAX_TRIES,
                    ramp_config,
                    StructuralTypes.RAMPS)

                objs = scene['objects']
                ramp = objs[-1]
                show = ramp['shows'][0]
                # Figure out ramp rotation
                ramp_rot_y = show['rotation']['y']

                rpos = show['position']
                rscale = show['scale']
                ramp_width = rscale['x']

                platform_z = random.uniform(
                    self.RAMP_TO_PLATFORM_PLATFORM_LENGTH_MIN,
                    self.RAMP_TO_PLATFORM_PLATFORM_LENGTH_MAX)

                ramp_length = rscale['z']
                height = rscale['y']

                z_inc = (ramp_length + platform_z) / 2.0 * \
                    math.cos(math.radians(ramp_rot_y))
                x_inc = (ramp_length + platform_z) / 2.0 * \
                    math.sin(math.radians(ramp_rot_y))

                platform_scale = VectorFloatConfig(
                    ramp_width, height, platform_z)

                # Figure out position such that platform will be against
                # ramp
                platform_position = VectorFloatConfig(
                    rpos['x'] + x_inc, rpos['y'], rpos['z'] + z_inc)

                platform_config = StructuralPlatformConfig(
                    num=1,
                    material=ramp['materials'],
                    position=platform_position,
                    rotation_y=ramp_rot_y,
                    scale=platform_scale,
                    labels=['platform_next_to_ramp']
                )
                add_structural_object_with_retries_or_throw(
                    scene,
                    bounds2,
                    MAX_TRIES,
                    platform_config,
                    StructuralTypes.PLATFORMS)

                return scene
            except BaseException as e:
                last_exception = e
                logger.debug(
                    "failed to create ramp to platform to",
                    exc_info=last_exception,
                )
                # remove added objects on failure
                num_extra = len(scene['objects']) - num_prev_objs
                if num_extra > 0:
                    scene['objects'].pop(-1)
        raise ILEException(
            "Failed to create ramp to platform") from last_exception

    LavaSizes = namedtuple('LavaIslandSizes', (
        'island_size',
        'front_lava_width',
        'rear_lava_width',
        'short_lava_width'))

    def _add_tool_lava_goal(self, scene, room_dim):

        last_exception = None
        config = self.get_shortcut_lava_target_tool()
        if not config:
            return scene
        logger.trace("Adding tool to goal shortcut")
        scene['objects'] = scene.get('objects', [])
        scene['lava'] = scene.get('lava', [])
        num_prev_objs = len(scene['objects'])
        num_prev_lava = len(scene['lava'])

        if config.guide_rails and config.tool_rotation:
            raise ILEException(
                "Unable to use 'guide_rails' and 'tool_rotation' from "
                "shortcut_lava_target_tool at the same time")

        for _ in range(MAX_TRIES):
            try:
                self.remove_target_on_error = False
                bounds = find_bounds(scene)
                # Test room size and determine sizes
                long_length = max(room_dim['x'], room_dim['z'])
                short_length = min(room_dim['x'], room_dim['z'])
                long_key, short_key = (('z', 'x') if long_length ==
                                       room_dim['z'] else ('x', 'z'))

                # place performer
                start = scene['performerStart']['position']
                start[long_key] = - (long_length / 2.0 - 0.5)
                scene['performerStart']['rotation']['y'] = (
                    0 if long_key == 'z' else 90)

                sizes = self._compute_lava_sizes(
                    long_length, short_length, long_key, short_key, config)

                start[short_key] = 0 if sizes.island_size % 2 == 1 else 0.5

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

                # Find/Create target
                self._add_target_to_lava_island(
                    scene,
                    long_key,
                    short_key,
                    sizes.island_size,
                    long_far_island_coord,
                    long_near_island_coord)
                target = scene['objects'][-1]

                # Encircle target with lava
                self._add_lava_around_island(
                    scene, bounds, long_key, sizes.front_lava_width,
                    sizes.rear_lava_width, sizes.short_lava_width,
                    long_far_island_coord, long_near_island_coord,
                    short_left_island_coord, short_right_island_coord)

                # Add block tool
                self._add_tool(
                    scene,
                    bounds,
                    sizes.island_size,
                    long_key,
                    short_key,
                    sizes.front_lava_width,
                    tool_length,
                    long_near_island_coord,
                    config.tool_rotation)
                tool = scene['objects'][-1]

                if config.guide_rails:
                    self._add_guide_rails(scene, long_key, short_key,
                                          tool_length, target, tool)

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
                scene['objects'] = scene['objects'][:num_prev_objs]
                scene['lava'] = scene['lava'][:num_prev_lava]
                if self.remove_target_on_error:
                    meta = scene.get('goal', {}).get('metadata', {})
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
            rotation_y=rot, position_y=center.y,
            length=length, width=width, material_tuple=mat,
            bounds=[])
        scene['objects'] += rails

    def _get_guide_rail_material_tuple(
            self, scene: dict) -> materials.MaterialTuple:
        invalid_mats = {scene.get("ceilingMaterial", ""),
                        scene.get("floorMaterial", ""),
                        scene.get("wallMaterial", "")}
        room_mats = scene.get("roomMaterials", {})
        for mat in room_mats.values():
            invalid_mats.add(mat)
        valid = False
        while (not valid):
            mat = random.choice(
                random.choice(materials.CEILING_AND_WALL_GROUPINGS)
            )
            valid = mat[0] not in invalid_mats
        return mat

    def _randomize_performer_position(self, scene,
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
        long_extent = scene['roomDimensions'][long_key] / 2.0 - 0.5
        short_extent = scene['roomDimensions'][short_key] / 2.0 - 0.5
        template = VectorFloatConfig(y=0)
        setattr(template, long_key, MinMaxFloat(-long_extent, long_extent))
        setattr(template, short_key, MinMaxFloat(-short_extent, short_extent))

        for _ in range(MAX_TRIES):
            pos = choose_random(template)
            if (no_go_long_min <= getattr(pos, long_key) <= no_go_long_max and
                    no_go_short_min <= getattr(
                    pos, short_key) <= no_go_short_max):
                continue
            for obj in scene['objects']:
                if not geometry.validate_location_rect(
                        obj['shows'][0]['boundingBox'], vars(pos), [],
                        scene['roomDimensions']):
                    continue
            scene['performerStart']['position']['x'] = pos.x
            scene['performerStart']['position']['z'] = pos.z
            return
        raise ILEException("Failed to find random performer location")

    def _add_target_to_lava_island(
            self, scene, long_key, short_key, island_size,
            long_far_island_coord, long_near_island_coord):
        target = get_target_object(scene)

        # put target in middle of island
        pos = VectorFloatConfig()
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
            self.remove_target_on_error = True
            goal_template = GoalConfig(
                category="retrieval",
                target=InteractableObjectConfig(
                    shape='soccer_ball',
                    position=pos,
                    scale=MinMaxFloat(1.0, 3.0)))
            GoalServices.attempt_to_add_goal(scene, goal_template)
            target = get_target_object(scene)

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
        add_structural_object_with_retries_or_throw(
            scene, bounds, MAX_TRIES, tool_template, StructuralTypes.TOOLS)

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
            scene['lava'] = []
            # sourcery recommends the 'from e'
            raise e from e

    def _add_lava_range(self, scene, bounds, long_key,
                        long_range, short_range):
        logger.trace(f"Adding lava with ranges {long_range} {short_range}")
        for long in long_range:
            for short in short_range:
                (x, z) = (long, short) if long_key == 'x' else (short, long)
                logger.trace(f"Adding lava at {x},{z}")
                lava = FloorMaterialConfig(
                    num=1, position_x=x, position_z=z)
                add_structural_object_with_retries_or_throw(
                    scene, bounds, MAX_TRIES, lava,
                    StructuralTypes.LAVA)

    def _get_tool_shape(self, tool_length):
        tools = [
            tool
            for tool, (_, length) in LARGE_BLOCK_TOOLS_TO_DIMENSIONS.items()
            if length == tool_length
        ]
        return random.choice(tools)

    def get_num_delayed_actions(self) -> int:
        return 1 if self._delayed_perf_pos else 0

    def run_delayed_actions(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        if self._delayed_perf_pos:
            self._position_performer_on_platform(scene)
        return scene
