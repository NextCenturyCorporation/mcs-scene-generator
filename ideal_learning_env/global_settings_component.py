import copy
import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from machine_common_sense.config_manager import RoomMaterials, Vector3d

from generator import MaterialTuple, geometry, materials, tags
from generator.scene import Scene, get_step_limit_from_dimensions

from .choosers import (
    choose_material_tuple_from_material,
    choose_position,
    choose_random,
    choose_rotation
)
from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import (
    ROOM_MAX_XZ,
    ROOM_MAX_Y,
    ROOM_MIN_XZ,
    ROOM_MIN_Y,
    ILEConfigurationException,
    ILEDelayException,
    ILEException,
    ILESharedConfiguration,
    RandomizableBool,
    RandomizableString,
    find_bounds,
    return_list
)
from .goal_services import GoalConfig, GoalServices
from .numerics import (
    MinMaxFloat,
    MinMaxInt,
    RandomizableFloat,
    RandomizableVectorFloat3d,
    RandomizableVectorInt3d,
    VectorFloatConfig,
    VectorIntConfig
)
from .object_services import (
    KeywordLocation,
    KeywordLocationConfig,
    ObjectRepository
)
from .validators import ValidateNoNullProp, ValidateNumber, ValidateOptions

logger = logging.getLogger(__name__)

# Limit the possible random room dimensions to more typical choices.
ROOM_RANDOM_XZ = MinMaxInt(5, 25)
ROOM_RANDOM_Y = MinMaxInt(3, 8)

TRAPEZOIDAL_WALL_LEFT = {
    "id": "wall_left_override",
    "type": "cube",
    "mass": 1000,
    "materials": [],
    "kinematic": True,
    "physics": True,
    "structure": True,
    "debug": {},
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": -4,
            "y": 3,
            "z": 0
        },
        "rotation": {
            "x": 0,
            "y": 15,
            "z": 0
        },
        "scale": {
            "x": 0.5,
            "y": 6,
            "z": 18
        }
    }]
}
TRAPEZOIDAL_WALL_RIGHT = {
    "id": "wall_right_override",
    "type": "cube",
    "mass": 1000,
    "materials": [],
    "kinematic": True,
    "physics": True,
    "structure": True,
    "debug": {},
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 4,
            "y": 3,
            "z": 0
        },
        "rotation": {
            "x": 0,
            "y": -15,
            "z": 0
        },
        "scale": {
            "x": 0.5,
            "y": 6,
            "z": 18
        }
    }]
}


@dataclass
class PerformerStartsNearConfig():
    """
    Defines details of performer_starts_near which places the performer near an
    object of a given label at a specified distance away.
    - `label` (string or list of strings):
    Label of the object the performer will be placed near. Required.
    - `distance` (float, or [MinMaxFloat](#MinMaxFloat) dict, or list of
    floats and/or MinMaxFloat dicts): Distance between the performer agent and
    the object. If set to `0`, will try all distances between `0.5` and the
    bounds of the room. If set to a MinMaxFloat with a `max` of `0` or greater
    than the room bounds, will try all distances between the configured `min`
    and the bounds of the room. If set to a MinMaxFloat with a `min` of `0`,
    will try all distances between the configured `max` and `0.5`.
    Default: 0.5

    Example:
    ```
    label: container
    distance: 0.5
    ```
    """
    label: RandomizableString = None
    distance: RandomizableFloat = 0.5


class GlobalSettingsComponent(ILEComponent):
    """Manages the global settings of an ILE scene (the config properties that
    affect the whole scene)."""

    auto_last_step: RandomizableBool = None
    """
    (bool, or list of bools): Determines if the last step should automatically
    be determined by room size.  The last step is calculated such that the
    performer can walk in a circle along the walls of the room approximately 5
    times.  If 'last_step' is set, that field takes
    precedence.  Default: False

    Simple Example:
    ```
    auto_last_step: False
    ```

    Advanced Example:
    ```
    auto_last_step: True
    ```
    """

    ceiling_material: RandomizableString = None
    """
    (string, or list of strings): A single material for the ceiling, or a
    list of materials for the ceiling, from which one is chosen at random for
    each scene. Default: random

    Simple Example:
    ```
    ceiling_material: null
    ```

    Advanced Example:
    ```
    ceiling_material: "Custom/Materials/GreyDrywallMCS"
    ```
    """

    excluded_colors: RandomizableString = None
    """
    (string, or list of strings): Zero or more color words to exclude from
    being randomly generated as object or room materials. Materials with the
    listed colors can still be generated using specifically set configuration
    options, like the `floor_material` and `wall_material` options, or the
    `material` property in the `specific_interactable_objects` option. Useful
    if you want to avoid generating random objects with the same color as a
    configured object. Default: no excluded colors

    Simple Example:
    ```
    excluded_colors: null
    ```

    Advanced Example:
    ```
    excluded_colors: "red"
    ```
    """

    excluded_shapes: RandomizableString = None
    """
    (string, or list of strings): Zero or more object shapes (types) to exclude
    from being randomly generated. Objects with the listed shapes can still be
    generated using specifically set configuration options, like the `type`
    property in the `goal.target` and `specific_interactable_objects` options.
    Useful if you want to avoid randomly generating additional objects of the
    same shape as a configured goal target. Default: no excluded shapes

    Simple Example:
    ```
    excluded_shapes: null
    ```

    Advanced Example:
    ```
    excluded_shapes: "soccer_ball"
    ```
    """

    floor_material: RandomizableString = None
    """
    (string, or list of strings): A single material for the floor, or a
    list of materials for the floor, from which one is chosen at random for
    each scene. Default: random

    Simple Example:
    ```
    floor_material: null
    ```

    Advanced Example:
    ```
    floor_material: "Custom/Materials/GreyCarpetMCS"
    ```
    """

    forced_choice_multi_retrieval_target: str = None
    """
    (str): Whether to set a new "multi retrieval" goal using objects of a
    specific type that already exist in the scene. Set this option to an object
    shape like `"soccer_ball"`. This option splits all matching objects into
    "left" and "right" groups based on their X positions (ignoring objects that
    are picked up by placers). All objects in the larger group will be used as
    the new goal's target(s). Overrides the configured `goal`.
    Default: not used

    Simple Example:
    ```
    forced_choice_multi_retrieval_target: null
    ```

    Advanced Example:
    ```
    forced_choice_multi_retrieval_target: 'soccer_ball'
    ```
    """

    goal: Union[GoalConfig, List[GoalConfig]] = None
    """
    ([GoalConfig](#GoalConfig) dict): The goal category and target(s) in each
    scene, if any. Default: no goal

    Simple Example:
    ```
    goal: null
    ```

    Advanced Example:
    ```
    goal:
        category: retrieval
        target:
            shape: soccer_ball
            scale:
              min: 1.0
              max: 3.0
    ```
    """

    last_step: Union[int, List[int]] = None
    """
    (int, or list of ints): The last possible action step, or list of last
    steps, from which one is chosen at random for each scene. This field will
    overwrite 'auto_last_step' if set.  Default: no last step
    (unlimited)

    Simple Example:
    ```
    last_step: null
    ```

    Advanced Example:
    ```
    last_step: 1000
    ```
    """

    occluder_gap: RandomizableFloat = None
    """
    (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict: Gap (X
    distance) between moving structual occluders. Will override
    `position_x`. Only applies when `passive_physics_scene` is True.
    Default: no restrictions

    All scenes are generated with a .5 gap between occluders.

    Simple Example:
    ```
    occluder_gap: .5
    ```

    All scenes are generated with .5 or 1.0 gap between occluders.

    Advanced Example:
    ```
    occluder_gap: [.5, 1.0]
    ```

    All scenes are generated with a gap between (inclusive) .5 and 1.0 between
    occluders.

    Advanced Example:
    ```
    occluder_gap:
        min: .5
        max: 1.0
    ```
    """

    occluder_gap_viewport: RandomizableFloat = None
    """
    (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict: Gap (X
    distance) between occluders and edge of viewport. If both are included,
    `occluder_gap` will take precedence over `occluder_gap_viewport`.
    Will override `position_x`.
    Only applies when `passive_physics_scene` is True.
    Default: no restrictions

    All scenes are generated with a .5 gap between the occluder and the
    viewport.

    Simple Example:
    ```
    occluder_gap_viewport: .5
    ```

    All scenes are generated with .5 or 1.0 gap between occluder and the
    viewport.

    Advanced Example:
    ```
    occluder_gap_viewport: [.5, 1.0]
    ```

    All scenes are generated with a gap between (inclusive) .5 and 1.0 between
    the occluder nad the edge of the viewport.

    Advanced Example:
    ```
    occluder_gap_viewport:
        min: .5
        max: 1.0
    ```
    """

    passive_physics_floor: bool = None
    """
    **Deprecated.** Please use `passive_physics_scene: true`

    (bool): Lowers the friction of the floor (making it more "slippery").
    Used in passive physics evaluation scenes. Default: False

    Simple Example:
    ```
    passive_physics_floor: False
    ```

    Advanced Example:
    ```
    passive_physics_floor: True
    ```
    """

    passive_physics_scene: bool = None
    """
    (bool): Setup each scene in exactly the same way as the "passive physics"
    scenes used in the MCS evaluations, including the camera position, room
    dimensions, floor friction, and restrictions on only "Pass" actions.
    Default: False

    Simple Example:
    ```
    passive_physics_scene: False
    ```

    Advanced Example:
    ```
    passive_physics_scene: True
    ```
    """

    performer_look_at: RandomizableString = None
    """
    (string or list of strings): If set, configures the performer to start
    looking at an object found by the label matching the string given.
    Overrides `performer_start_rotation`.
    Default: Use `performer_start_rotation`

    Simple Example:
    ```
    performer_look_at: null
    ```

    Advanced Example:
    ```
    performer_look_at: [target, agent]
    ```
    """

    performer_starts_near: Union[
        PerformerStartsNearConfig,
        List[PerformerStartsNearConfig]
    ] = None
    """
    ([PerformerStartsNearConfig](#PerformerStartsNearConfig) dict, or list
    of PerformerStartsNearConfig dicts:
    Dictates if the starting position of the performer will be near an
    object of a given `label` at a specified `distance` away.
    Use in combination with `performer_look_at` to look at the object at start.
    Overrides `performer_start_position`.
    Default: Use `performer_start_position`

    Simple Example:
    ```
    performer_starts_near: null
    ```

    Advanced Example:
    ```
    performer_starts_near:
        label: container
        distance: 0.5
    ```
    """

    performer_start_position: Union[
        VectorFloatConfig,
        List[VectorFloatConfig],
        KeywordLocationConfig
    ] = None

    """
    ([VectorFloatConfig](#VectorFloatConfig) dict, or list of VectorFloatConfig
    dicts or [KeywordLocationConfig](#KeywordLocationConfig)): The starting
    position of the performer agent, or a list of
    positions, from which one is chosen at random for each scene. The
    (optional) `y` is used to position on top of structural objects like
    platforms. Valid parameters are constrained by room dimensions.
    `x` and `z` positions must be positioned within half of the room
    dimension bounds minus an additional 0.25 to account for the performer
    width. For example: in a room where 'dimension x = 5', valid
    `x` parameters would be '4.75, MinMaxFloat(-4.75, 4.75) and
    [-4.75, 0, 4.75].' In the case of variable room dimensions that use a
    MinMaxInt or list, valid parameters are bound by the maximum room
    dimension. For example: with 'dimension `x` = MinMax(5, 7) or [5, 6, 7]
    valid x parameters would be '3.25, MinMaxFloat(-3.25, 3.25), and
    [-3.25, 0, 3.25].' For `y` start and room dimensions, the min y position
    must always be greater than 0 and the max must always be less than or equal
    to room dimension y - 1.25.' This ensures the performer does not clip
    into the ceiling. Alternatively, the performer start can be a
    [KeywordLocationConfig](#KeywordLocationConfig).  Performer only supports
    the following keyword locations: `along_wall`
    Default: random within the room

    Simple Example:
    ```
    performer_start_position: null
    ```

    Advanced Example:
    ```
    performer_start_position:
        x:
            - -1
            - -0.5
            - 0
            - 0.5
            - 1
        y: 0
        z:
            min: -1
            max: 1
    ```
    """

    performer_start_rotation: RandomizableVectorFloat3d = None
    """
    ([VectorFloatConfig](#VectorFloatConfig) dict, or list of VectorFloatConfig
    dicts): The starting rotation of the performer agent, or a list of
    rotations, from which one is chosen at random for each scene. The
    (required) `y` is left/right and (optional) `x` is up/down. Default: random

    Simple Example:
    ```
    performer_start_rotation: null
    ```

    Advanced Example:
    ```
    performer_start_rotation:
        x: 0
        y:
            - 0
            - 90
            - 180
            - 270
    ```
    """

    restrict_open_doors: bool = None
    """
    (bool): If there are multiple doors in a scene, only allow for one door to
    ever be opened.
    Default: False

    Simple Example:
    ```
    restrict_open_doors: False
    ```

    Advanced Example:
    ```
    restrict_open_doors: True
    ```
    """

    restrict_open_objects: bool = None
    """
    (bool): If there are multiple openable objects in a scene, including
    containers and doors, only allow for one to ever be opened.
    Default: False

    Simple Example:
    ```
    restrict_open_objects: False
    ```

    Advanced Example:
    ```
    restrict_open_objects: True
    ```
    """

    room_dimensions: RandomizableVectorInt3d = None
    """
    ([VectorIntConfig](#VectorIntConfig) dict, or list of VectorIntConfig
    dicts): The total dimensions for the room, or list of dimensions, from
    which one is chosen at random for each scene. Rooms are always rectangular
    or square. The X and Z must each be within [2, 100] and the Y must be
    within [2, 10]. The room's bounds will be [-X/2, X/2] and [-Z/2, Z/2].
    Default: random X from 5 to 25, random Y from 3 to 8, random Z from 5 to 25

    Simple Example:
    ```
    room_dimensions: null
    ```

    Advanced Example:
    ```
    room_dimensions:
        x: 10
        y:
            - 3
            - 4
            - 5
            - 6
        z:
            min: 5
            max: 10
    ```
    """

    room_shape: str = None
    """
    (string): Shape of the room to restrict the randomzed room dimensions if
    `room_dimensions` weren't configured. Options: `rectangle`, `square`.
    Default: Use `room_dimensions`

    Simple Example:
    ```
    room_shape: null
    ```

    Advanced Example:
    ```
    room_shape: square
    ```
    """

    side_wall_opposite_colors: RandomizableBool = None
    """
    (bool, or list of bools): Makes three of the room's walls the same color,
    and the other wall (either the left or the right) an opposite color.
    Overrides all the `wall_*_material` config options. Default: False

    Simple Example:
    ```
    side_wall_opposite_colors: False
    ```

    Advanced Example:
    ```
    side_wall_opposite_colors: True
    ```
    """

    trapezoidal_room: RandomizableBool = None
    """
    (bool, or list of bools): Makes the room trapezoidal, so the left and right
    walls will be angled inward. Currently only supported for room_dimensions
    of X=12 and Z=16. Default: False

    Simple Example:
    ```
    trapezoidal_room: False
    ```

    Advanced Example:
    ```
    trapezoidal_room: True
    ```
    """

    wall_back_material: RandomizableString = None
    """
    (string, or list of strings): The material for the back wall, or list of
    materials, from which one is chosen for each scene. Default: random

    Simple Example:
    ```
    wall_back_material: null
    ```

    Advanced Example:
    ```
    wall_back_material: "Custom/Materials/GreyDrywallMCS"
    ```
    """

    wall_front_material: RandomizableString = None
    """
    (string, or list of strings): The material for the front wall, or list of
    materials, from which one is chosen for each scene. Default: random

    Simple Example:
    ```
    wall_front_material: null
    ```

    Advanced Example:
    ```
    wall_front_material: "Custom/Materials/GreyDrywallMCS"
    ```
    """

    wall_left_material: RandomizableString = None
    """
    (string, or list of strings): The material for the left wall, or list of
    materials, from which one is chosen for each scene. Default: random

    Simple Example:
    ```
    wall_left_material: null
    ```

    Advanced Example:
    ```
    wall_left_material: "Custom/Materials/GreyDrywallMCS"
    ```
    """

    wall_material: RandomizableString = None
    """
    (string, or list of strings): The material for all room walls, or list of
    materials, from which one is chosen for each scene. Is overridden by the
    individual `wall_*_material` config options. Default: ROOM_WALL_MATERIALS

    Simple Example:
    ```
    wall_material: null
    ```

    Advanced Example:
    ```
    wall_material: "Custom/Materials/GreyDrywallMCS"
    ```
    """

    wall_right_material: RandomizableString = None
    """
    (string, or list of strings): The material for the right wall, or list of
    materials, from which one is chosen for each scene. Default: random

    Simple Example:
    ```
    wall_right_material: null
    ```

    Advanced Example:
    ```
    wall_right_material: "Custom/Materials/GreyDrywallMCS"
    ```
    """

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self._delayed_goal = False
        self._delayed_goal_reason = None

    # Override
    def update_ile_scene(self, scene: Scene) -> Scene:
        logger.info('Configuring global settings for the scene...')

        if (
            self.get_passive_physics_floor() or
            self.get_passive_physics_scene()
        ):
            logger.trace('Switching to passive physics scene setup')
            scene.intuitive_physics = True
            scene.version = 3

            # These properties aren't needed for Unity to render the scene, but
            # may be needed for other parts of the ILE scene generator to work.
            self.set_room_dimensions(VectorIntConfig(20, 10, 20))
            self.set_performer_start_position(VectorFloatConfig(0, 0, -4.5))
            self.set_performer_start_rotation(VectorFloatConfig(0, 0, 0))
            # Don't use set_goal() here because of the category validator.
            self.goal = GoalConfig(category=tags.SCENE.INTUITIVE_PHYSICS)

            # Lower the friction values, but use defaults for the others.
            # Note this is no longer needed as of v1.5, because we now set
            # `intuitive_physics`, but keeping it for backwards compatibility.
            scene.floor_properties = {
                'enable': True,
                'angularDrag': 0.5,
                'bounciness': 0,
                'drag': 0,
                'dynamicFriction': 0.1,
                'staticFriction': 0.1
            }

        shared_config = ILESharedConfiguration.get_instance()

        occluder_gap = self.get_occluder_gap()
        shared_config.set_occluder_gap(occluder_gap)

        occluder_gap_viewport = self.get_occluder_gap_viewport()
        shared_config.set_occluder_gap_viewport(occluder_gap_viewport)

        excluded_colors = return_list(self.excluded_colors, [])
        shared_config.set_excluded_colors(excluded_colors)
        if excluded_colors:
            logger.trace(f'Setting excluded colors = {excluded_colors}')

        excluded_shapes = return_list(self.excluded_shapes, [])
        shared_config.set_excluded_shapes(excluded_shapes)
        if excluded_shapes:
            logger.trace(f'Setting excluded shapes = {excluded_shapes}')

        room_size = self.get_room_dimensions()
        scene.room_dimensions = room_size
        logger.trace(f'Setting room dimensions = {scene.room_dimensions}')

        self._delayed_position_label = None
        self._delayed_position_distance = None
        if self.performer_starts_near:
            random_perf_starts_near = self.get_performer_distance()
            self._delayed_position_label = random_perf_starts_near.label
            self._delayed_position_distance = random_perf_starts_near.distance
            self._set_position_by_distance(scene)
            # Temporarily set the performer start location outside of the room
            # to avoid issues with collision checking in other ILE components.
            scene.set_performer_start(
                Vector3d(x=(room_size.x + 1), y=0, z=(room_size.z + 1)),
                Vector3d(x=0, y=0, z=0)
            )
        else:
            start_pos = self.get_performer_start_position(room_size)
            scene.set_performer_start(
                start_pos,
                self.get_performer_start_rotation())
        logger.trace(f'Setting performer start = {scene.performer_start}')
        self._delayed_rotation_label = self.get_performer_look_at()
        self._set_rotation_by_look_at(scene)

        ceiling_material_tuple = self.get_ceiling_material()
        scene.ceiling_material = ceiling_material_tuple.material
        scene.debug['ceilingColors'] = ceiling_material_tuple.color

        floor_material_tuple = self.get_floor_material()
        scene.floor_material = floor_material_tuple.material
        scene.debug['floorColors'] = floor_material_tuple.color
        wall_material_data = self.get_wall_material_data()
        scene.room_materials = RoomMaterials(
            front=wall_material_data['front'].material,
            left=wall_material_data['left'].material,
            right=wall_material_data['right'].material,
            back=wall_material_data['back'].material
        )
        scene.restrict_open_doors = self.get_restrict_open_doors()
        scene.restrict_open_objects = self.get_restrict_open_objects()
        scene.debug['wallColors'] = list(set([
            color for value in wall_material_data.values()
            for color in value.color
        ]))
        logger.trace(
            f'Setting room materials...\nCEILING={scene.ceiling_material}'
            f'\nFLOOR={scene.floor_material}\nWALL={scene.room_materials}'
        )

        trapezoidal_room = choose_random(self.trapezoidal_room)
        if trapezoidal_room:
            if scene.room_dimensions.x != 12:
                raise ILEConfigurationException(
                    f'The trapezoidal_room config option is currently only '
                    f'supported for room_dimensions of X=12, but it is X='
                    f'{scene.room_dimensions.x}'
                )
            if scene.room_dimensions.z != 16:
                raise ILEConfigurationException(
                    f'The trapezoidal_room config option is currently only '
                    f'supported for room_dimensions of Z=16, but it is Z='
                    f'{scene.room_dimensions.z}'
                )
            wall_left = copy.deepcopy(TRAPEZOIDAL_WALL_LEFT)
            wall_right = copy.deepcopy(TRAPEZOIDAL_WALL_RIGHT)
            reverse_angle = random.choice([True, False])
            if reverse_angle:
                wall_left['shows'][0]['rotation']['y'] *= -1
                wall_right['shows'][0]['rotation']['y'] *= -1
            wall_left['materials'] = [scene.room_materials.left]
            wall_right['materials'] = [scene.room_materials.right]
            scene.objects.extend([wall_left, wall_right])

        last_step = self.get_last_step()
        if not last_step and self.get_auto_last_step():
            last_step = get_step_limit_from_dimensions(
                room_x=scene.room_dimensions.x,
                room_z=scene.room_dimensions.z)
        if last_step:
            scene.goal.last_step = last_step
            logger.trace(f'Setting last step = {last_step}')
        self._attempt_goal(scene)

        return scene

    def _set_rotation_by_look_at(self, scene: Scene):
        if not self._delayed_rotation_label:
            return
        if idl := (ObjectRepository.get_instance().
                   get_one_from_labeled_objects(
                self._delayed_rotation_label)):
            self._delayed_rotation_reason = None
            # determine rotation
            perf_pos = scene.performer_start.position
            tar_pos = idl.instance['shows'][0]['position']
            tbb = idl.instance['shows'][0]['boundingBox']
            target_y = (tbb.min_y + tbb.max_y) / 2.0
            tilt, rot = geometry.calculate_rotations(
                perf_pos,
                Vector3d(x=tar_pos['x'], y=target_y, z=tar_pos['z'])
            )
            self._delayed_rotation_label = None
            scene.performer_start.rotation.y = rot
            scene.performer_start.rotation.x = tilt
        else:
            self._delayed_rotation_reason = ILEDelayException(
                f"Performer unable to set rotation due to missing object "
                f"with label '{self._delayed_rotation_label}'")

    def _set_position_by_distance(self, scene: Scene):
        if not self._delayed_position_label:
            return
        if idl := (ObjectRepository.get_instance().
                   get_one_from_labeled_objects(
                self._delayed_position_label)):
            self._delayed_position_reason = None
            target = idl.instance
            if isinstance(self._delayed_position_distance, (int, float)):
                self._delayed_position_distance = MinMaxFloat(
                    min=self._delayed_position_distance,
                    max=self._delayed_position_distance
                )
            try:
                # Identify a valid position using the current distance.
                (x, z) = geometry.get_position_distance_away_from_obj(
                    scene.room_dimensions,
                    target,
                    self._delayed_position_distance.min,
                    self._delayed_position_distance.max,
                    find_bounds(scene)
                )
            except Exception as e:
                raise ILEException(
                    f'Cannot find any valid locations for '
                    f'"performer_starts_near" with configured '
                    f'label={self._delayed_position_label} and '
                    f'distance={self._delayed_position_distance}'
                ) from e
            scene.set_performer_start_position(x=x, y=0, z=z)
            self._delayed_position_label = None
        else:
            self._delayed_position_reason = ILEDelayException(
                f"Performer unable to set position due to missing object "
                f"with label '{self._delayed_position_label}'")

    def _attempt_goal(self, scene):
        try:
            goal_template = self.goal
            GoalServices.attempt_to_add_goal(scene, goal_template)
            self._delayed_goal = False
            self._delayed_goal_reason = None
        except ILEDelayException as e:
            logger.trace("Goal failed and needs delay.", exc_info=e)
            self._delayed_goal = True
            self._delayed_goal_reason = e

    def get_ceiling_material(self) -> MaterialTuple:
        return choose_material_tuple_from_material(
            self.ceiling_material or materials.CEILING_MATERIALS
        )

    @ile_config_setter(validator=ValidateOptions(
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_ceiling_material(self, data: Any) -> None:
        self.ceiling_material = data

    @ile_config_setter()
    def set_excluded_colors(self, data: Any) -> None:
        self.excluded_colors = data

    @ile_config_setter()
    def set_excluded_shapes(self, data: Any) -> None:
        self.excluded_shapes = data

    def get_floor_material(self) -> MaterialTuple:
        return choose_material_tuple_from_material(
            self.floor_material or materials.FLOOR_MATERIALS
        )

    @ile_config_setter(validator=ValidateOptions(
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_floor_material(self, data: Any) -> None:
        self.floor_material = data

    @ile_config_setter()
    def set_forced_choice_multi_retrieval_target(self, data: Any) -> None:
        self.forced_choice_multi_retrieval_target = data

    def get_goal(self):
        return self.goal

    @ile_config_setter(validator=ValidateOptions(props=['category'], options=[
        tags.SCENE.RETRIEVAL, tags.SCENE.MULTI_RETRIEVAL,
        tags.SCENE.PASSIVE, tags.SCENE.IMITATION
    ]))
    def set_goal(self, data: Any) -> None:
        if data:
            data.category = GoalServices.validate_goal_category(data)
        self.goal = data

    def get_last_step(self) -> int:
        return self.last_step

    # If not null, it must be a number.
    @ile_config_setter(validator=ValidateNumber(min_value=1))
    def set_last_step(self, data: Any) -> None:
        self.last_step = data

    @ile_config_setter()
    def set_occluder_gap(self, data: Any) -> None:
        self.occluder_gap = data

    def get_occluder_gap(self) -> RandomizableFloat:
        return choose_random(self.occluder_gap) or None

    @ile_config_setter()
    def set_occluder_gap_viewport(self, data: Any) -> None:
        self.occluder_gap_viewport = data

    def get_occluder_gap_viewport(self) -> RandomizableFloat:
        return choose_random(self.occluder_gap_viewport) or None

    @ile_config_setter()
    def set_passive_physics_floor(self, data: Any) -> None:
        self.passive_physics_floor = data

    def get_passive_physics_floor(self) -> bool:
        return self.passive_physics_floor or False

    @ile_config_setter()
    def set_passive_physics_scene(self, data: Any) -> None:
        self.passive_physics_scene = data

    def get_passive_physics_scene(self) -> bool:
        return self.passive_physics_scene or False

    @ile_config_setter(validator=ValidateNumber(
        props=['distance'], min_value=0, null_ok=True))
    def set_performer_starts_near(self, data: Any) -> None:
        self.performer_starts_near = data

    def get_performer_distance(self) -> str:
        # Do not use choose_random for the distance. Return the source config.
        if isinstance(self.performer_starts_near, list):
            # For lists, choose a random configuration from it.
            return random.choice(self.performer_starts_near)
        return self.performer_starts_near

    def get_performer_start_position(
        self,
        room_dimensions: Dict[str, int]
    ) -> Vector3d:
        if isinstance(self.performer_starts_near, PerformerStartsNearConfig):
            pass
        elif isinstance(self.performer_start_position, KeywordLocationConfig):
            klc: KeywordLocationConfig = self.performer_start_position
            if klc.keyword != KeywordLocation.ALONG_WALL:
                raise ILEConfigurationException(
                    f"Performer start does not support keyword location "
                    f"'{klc.keyword}'")

            wall_labels = klc.relative_object_label or random.choice([
                geometry.FRONT_WALL_LABEL,
                geometry.BACK_WALL_LABEL,
                geometry.LEFT_WALL_LABEL,
                geometry.RIGHT_WALL_LABEL])
            x, z = geometry.get_along_wall_xz(
                wall_labels,
                dict(room_dimensions),
                {'x': geometry.PERFORMER_WIDTH,
                    'y': geometry.PERFORMER_HEIGHT,
                    'z': geometry.PERFORMER_WIDTH})
            return Vector3d(x=x, y=0, z=z)

        return choose_position(
            self.performer_start_position,
            geometry.PERFORMER_WIDTH,
            geometry.PERFORMER_WIDTH,
            room_dimensions.x,
            room_dimensions.y,
            room_dimensions.z
        )

    def get_performer_look_at(self) -> str:
        return choose_random(self.performer_look_at)

    @ile_config_setter()
    def set_performer_look_at(self, data: Any) -> None:
        self.performer_look_at = data

    # allow partial setting of start position.  I.E.  only setting X
    @ile_config_setter(validator=ValidateNumber(
        props=['x', 'y', 'z'], null_ok=True))
    def set_performer_start_position(self, data: Any) -> None:
        if isinstance(data, KeywordLocationConfig):
            self.performer_start_position = data
        else:
            self.performer_start_position = VectorFloatConfig(
                data.x,
                data.y or 0,
                data.z
            ) if data is not None else None

    def get_performer_start_rotation(self) -> Vector3d:
        return choose_rotation(self.performer_start_rotation)

    # If not null, the Y property is required.
    @ile_config_setter(validator=ValidateNoNullProp(props=['y']))
    def set_performer_start_rotation(self, data: Any) -> None:
        self.performer_start_rotation = VectorFloatConfig(
            data.x or 0,
            data.y,
            data.z or 0
        ) if data is not None else None

    def get_room_dimensions(self) -> Vector3d:
        has_none = False
        rd = self.room_dimensions or VectorIntConfig()
        template = VectorIntConfig(rd.x, rd.y, rd.z)
        if not template:
            template = VectorIntConfig()
        if template.x is None:
            template.x = ROOM_RANDOM_XZ
            has_none = True
        if template.y is None:
            template.y = ROOM_RANDOM_Y
            has_none = True
        if template.z is None:
            template.z = ROOM_RANDOM_XZ
            has_none = True

        has_random = (
            isinstance(template.x, (list, MinMaxInt)) or
            isinstance(template.y, (list, MinMaxInt)) or
            isinstance(template.z, (list, MinMaxInt))
        )
        if not has_none and not has_random:
            return Vector3d(x=template.x, y=template.y, z=template.z)

        # check if all configs are valid
        self._valid_performer_start(template)

        good = False
        while not good:
            dims = choose_random(template)
            x = dims.x
            z = dims.x if self.room_shape == 'square' else dims.z
            good = True
            # Enforce the max for the diagonal distance too.
            if math.sqrt(x**2 + z**2) > ROOM_MAX_XZ:
                good = False
            if self.room_shape == 'rectangle' and x == z:
                good = False
        return Vector3d(x=x, y=dims.y, z=z)

    def _valid_performer_start(self, template):
        if isinstance(self.performer_start_position, KeywordLocationConfig):
            return
        room_x = template.x
        room_y = template.y
        room_z = template.z
        perf_x = None
        perf_y = None
        perf_z = None
        start = self.performer_start_position
        if start is not None:
            perf_x = start.x
            perf_y = start.y
            perf_z = start.z

        if perf_x is not None:
            self._valid_position(room_x, perf_x)
        if perf_y is not None:
            self._valid_position(room_y, perf_y, True)
        if perf_z is not None:
            self._valid_position(room_z, perf_z)

    def _valid_position(self, room_dim, pos, is_y=False):
        if isinstance(room_dim, int):
            # if any positions are outside the one room dimension
            minimum, maximum = (0, room_dim - geometry.PERFORMER_HEIGHT) \
                if is_y else self._get_min_max_room_dimensions(room_dim)
            self._valid_pos_checks(minimum, maximum, pos)
        elif isinstance(room_dim, MinMaxInt):
            # if any positions are outside the max throw an exception
            max_min, max_max = (0, room_dim.max - geometry.PERFORMER_HEIGHT) \
                if is_y else self._get_min_max_room_dimensions(room_dim.max)
            self._valid_pos_checks(max_min, max_max, pos)
        elif isinstance(room_dim, list):
            # if any positions are outside the max throw an exception
            max_room_dim = max(room_dim)
            minimum, maximum = (0, room_dim - geometry.PERFORMER_HEIGHT) \
                if is_y else self._get_min_max_room_dimensions(max_room_dim)
            self._valid_pos_checks(minimum, maximum, pos)

    def _valid_pos_checks(self, min, max, pos):
        if isinstance(pos, float) or isinstance(pos, int):
            self._valid_position_int_or_float(min, max, pos)
        elif isinstance(pos, MinMaxFloat):
            self._valid_position_min_max_float(min, max, pos)
        elif isinstance(pos, List):
            self._valid_position_list(min, max, pos)

    def _valid_position_int_or_float(self, min, max, pos):
        self._position_is_inside_room(min, max, pos)

    def _valid_position_min_max_float(self, min, max, pos):
        max_pos_is_valid = self._position_is_inside_room(min, max, pos.max)
        min_pos_is_valid = self._position_is_inside_room(min, max, pos.min)
        return max_pos_is_valid and min_pos_is_valid

    def _valid_position_list(self, min, max, pos):
        for p in pos:
            self._position_is_inside_room(min, max, p)

    def _position_is_inside_room(self, min, max, pos):
        valid = min <= pos <= max
        room_dim = self._get_constrained_room_dimension(
            max) if min != 0 else int(max + geometry.PERFORMER_HEIGHT)
        if not valid:
            raise ILEException(
                f'Performer start position: {pos} '
                f'is not valid with room dimension: {room_dim} '
                f'where the MAX position = {max} and MIN position = {min}'
                f'Please remove this position from the performer start '
                f'config options')

    def _get_min_max_room_dimensions(self, room_dim):
        min = -(room_dim / 2.0) + geometry.PERFORMER_HALF_WIDTH
        max = (room_dim / 2.0) - geometry.PERFORMER_HALF_WIDTH
        return min, max

    def _get_constrained_room_dimension(self, room_dim):
        return int((room_dim + geometry.PERFORMER_HALF_WIDTH) * 2)

    @ile_config_setter()
    def set_restrict_open_doors(self, data: Any) -> None:
        self.restrict_open_doors = data

    def get_restrict_open_doors(self) -> bool:
        if self.restrict_open_doors is None:
            return False

        return self.restrict_open_doors

    @ile_config_setter()
    def set_restrict_open_objects(self, data: Any) -> None:
        self.restrict_open_objects = data

    def get_restrict_open_objects(self) -> bool:
        return self.restrict_open_objects or False

    # If not null, all X/Y/Z properties are required.
    @ile_config_setter(validator=ValidateNumber(
        props=['x', 'z'],
        min_value=ROOM_MIN_XZ,
        max_value=ROOM_MAX_XZ,
        null_ok=True)
    )
    @ile_config_setter(validator=ValidateNumber(
        props=['y'],
        min_value=ROOM_MIN_Y,
        max_value=ROOM_MAX_Y,
        null_ok=True)
    )
    def set_room_dimensions(self, data: Any) -> None:
        self.room_dimensions = data

    @ile_config_setter(validator=ValidateOptions(
        options=['rectangle', 'square']
    ))
    def set_room_shape(self, data: Any) -> None:
        self.room_shape = data

    @ile_config_setter()
    def set_side_wall_opposite_colors(self, data: Any) -> None:
        self.side_wall_opposite_colors = data

    @ile_config_setter()
    def set_trapezoidal_room(self, data: Any) -> None:
        self.trapezoidal_room = data

    @ile_config_setter(validator=ValidateOptions(
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_wall_back_material(self, data: Any) -> None:
        self.wall_back_material = data

    @ile_config_setter(validator=ValidateOptions(
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_wall_front_material(self, data: Any) -> None:
        self.wall_front_material = data

    @ile_config_setter(validator=ValidateOptions(
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_wall_left_material(self, data: Any) -> None:
        self.wall_left_material = data

    @ile_config_setter(validator=ValidateOptions(
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_wall_material(self, data: Any) -> None:
        self.wall_material = data

    @ile_config_setter(validator=ValidateOptions(
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_wall_right_material(self, data: Any) -> None:
        self.wall_right_material = data

    def get_wall_material_data(self) -> Dict[str, MaterialTuple]:
        if self.side_wall_opposite_colors:
            material_choice = choose_material_tuple_from_material(
                materials.WALL_OPPOSITE_MATERIALS
            )
            data = {
                'back': material_choice,
                'front': material_choice,
                'left': material_choice,
                'right': material_choice
            }
            opposite_choice = materials.OPPOSITE_SETS[material_choice.material]
            opposite_wall = random.choice(['left', 'right'])
            data[opposite_wall] = opposite_choice
            return data

        # All walls should use the same default material, so choose it now.
        material_choice = random.choice(materials.ROOM_WALL_MATERIALS)
        if self.wall_material:
            material_choice = choose_material_tuple_from_material(
                self.wall_material
            )
        back = material_choice
        if self.wall_back_material:
            back = choose_material_tuple_from_material(self.wall_back_material)
        front = material_choice
        if self.wall_front_material:
            front = choose_material_tuple_from_material(
                self.wall_front_material)
        left = material_choice
        if self.wall_left_material:
            left = choose_material_tuple_from_material(self.wall_left_material)
        right = material_choice
        if self.wall_right_material:
            right = choose_material_tuple_from_material(
                self.wall_right_material)
        return {
            'back': choose_random(back, MaterialTuple),
            'front': choose_random(front, MaterialTuple),
            'left': choose_random(left, MaterialTuple),
            'right': choose_random(right, MaterialTuple)
        }

    def get_auto_last_step(self) -> bool:
        return choose_random(self.auto_last_step)

    @ile_config_setter()
    def set_auto_last_step(self, data: Any) -> None:
        self.auto_last_step = data

    def get_num_delayed_actions(self) -> int:
        return ((1 if self._delayed_goal else 0) +
                (1 if self._delayed_position_label else 0) +
                (1 if self._delayed_rotation_label else 0))

    def run_delayed_actions(self, scene: Scene) -> Scene:
        if self._delayed_goal:
            self._attempt_goal(scene)
        if self._delayed_position_label:
            self._set_position_by_distance(scene)
        if self._delayed_rotation_label:
            self._set_rotation_by_look_at(scene)
        return scene

    def get_delayed_action_error_strings(self):
        reasons = []
        if self._delayed_goal and self._delayed_goal_reason:
            reasons.append(str(self._delayed_goal_reason))
        if self._delayed_position_label and self._delayed_position_reason:
            reasons.append(str(self._delayed_position_reason))
        if self._delayed_rotation_label and self._delayed_rotation_reason:
            reasons.append(str(self._delayed_rotation_reason))
        return reasons

    def run_actions_at_end_of_scene_generation(self, scene: Scene) -> Scene:
        if not self.forced_choice_multi_retrieval_target:
            return scene

        # Use the configured value as the target type.
        target_type = self.forced_choice_multi_retrieval_target

        # Look for all viable targets on both the left and the right.
        left_group = []
        right_group = []
        for instance in scene.objects:
            # Skip this object if it is not the target type.
            if instance['type'] != target_type:
                continue
            # Skip this object if it moves upward (assume it is picked up
            # by a placer and held out-of-reach indefinitely).
            movement = instance.get('moves')
            if movement and movement[-1]['vector']['y'] > 0:
                continue
            # Assign this object to the left or right group appropriately.
            if instance['shows'][0]['position']['x'] < 0:
                left_group.append(instance)
            if instance['shows'][0]['position']['x'] > 0:
                right_group.append(instance)
        # In the unlikely event that both groups have the same number of
        # viable targets, raise an exception and retry generating the scene.
        if len(left_group) == len(right_group):
            raise ILEException(
                f'Cannot create a forced choice multi retrieval goal with '
                f'the target type {target_type} because both the left and '
                f'the right sides have the same number of viable targets: '
                f'{len(left_group)}'
            )
        # Otherwise use the group with more viable targets.
        use_left_group = len(left_group) > len(right_group)
        targets = left_group if use_left_group else right_group
        logger.trace(
            f'Setting forced choice multi retrieval goal with '
            f'{len(targets)} {target_type} targets on the '
            f'{"left" if use_left_group else "right"} side.'
        )
        # Set the goal in the scene.
        scene.goal.category = tags.SCENE.MULTI_RETRIEVAL
        scene.goal.description = GoalServices.make_goal_description(
            scene.goal.category,
            targets
        )
        scene.goal.metadata = {
            'targets': [{'id': target['id']} for target in targets]
        }
        return scene
