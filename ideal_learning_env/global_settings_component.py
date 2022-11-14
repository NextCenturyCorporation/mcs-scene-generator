import copy
import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from machine_common_sense.config_manager import Vector3d

from generator import MaterialTuple, geometry, materials, tags
from generator.scene import Scene, get_step_limit_from_dimensions
from ideal_learning_env.interactable_object_service import (
    KeywordLocationConfig
)
from ideal_learning_env.numerics import MinMaxFloat, MinMaxInt

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
    find_bounds
)
from .goal_services import GoalConfig, GoalServices
from .numerics import RandomizableFloat, VectorFloatConfig, VectorIntConfig
from .object_services import KeywordLocation, ObjectRepository
from .validators import ValidateNoNullProp, ValidateNumber, ValidateOptions

logger = logging.getLogger(__name__)

# Limit the possible random room dimensions to more typical choices.
ROOM_RANDOM_XZ = MinMaxInt(5, 30)
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
    Label of the object the performer will be placed near.  Default: None
    - `distance` (float or list of floats):
    Distance the performer will be from the object.  Default: 0.1

    Example:
    ```
    label: container
    distance: 0.1
    ```
    """
    label: Union[str, List[str]] = None
    distance: RandomizableFloat = 0.1


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

    ceiling_material: Union[str, List[str]] = None
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

    excluded_shapes: Union[str, List[str]] = None
    """
    (string, or list of strings): Zero or more object shapes (types) to exclude
    from being randomly generated. Objects with the listed shapes can still be
    generated using specifically set configuration options, like the `type`
    property in the `goal.target` and `specific_interactable_objects` options.
    Useful if you want to avoid randomly generating additional objects of the
    same shape as a configured goal target. Default: None

    Simple Example:
    ```
    excluded_shapes: null
    ```

    Advanced Example:
    ```
    excluded_shapes: "soccer_ball"
    ```
    """

    floor_material: Union[str, List[str]] = None
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

    goal: Union[GoalConfig, List[GoalConfig]] = None
    """
    ([GoalConfig](#GoalConfig) dict): The goal category and target(s) in each
    scene, if any. Default: None

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
    overwrite 'auto_last_step' if set.  Default: none
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

    performer_look_at: Union[str, List[str]] = None
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
        distance: 0.1
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

    performer_start_rotation: Union[
        VectorIntConfig,
        List[VectorIntConfig]
    ] = None
    """
    ([VectorIntConfig](#VectorIntConfig) dict, or list of VectorIntConfig
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

    room_dimensions: Union[VectorIntConfig, List[VectorIntConfig]] = None
    """
    ([VectorIntConfig](#VectorIntConfig) dict, or list of VectorIntConfig
    dicts): The total dimensions for the room, or list of dimensions, from
    which one is chosen at random for each scene. Rooms are always rectangular
    or square. The X and Z must each be within [2, 100] and the Y must be
    within [2, 10]. The room's bounds will be [-X/2, X/2] and [-Z/2, Z/2].
    Default: random X from 5 to 30, random Y from 3 to 8, random Z from 5 to 30

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
    Default: None

    Simple Example:
    ```
    room_shape: null
    ```

    Advanced Example:
    ```
    room_shape: square
    ```
    """

    side_wall_opposite_colors: Union[bool, List[bool]] = None
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

    trapezoidal_room: Union[bool, List[bool]] = None
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

    wall_back_material: Union[str, List[str]] = None
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

    wall_front_material: Union[str, List[str]] = None
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

    wall_left_material: Union[str, List[str]] = None
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

    wall_material: Union[str, List[str]] = None
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

    wall_right_material: Union[str, List[str]] = None
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
            self.set_performer_start_rotation(VectorIntConfig(0, 0, 0))
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

        excluded_shapes = self.get_excluded_shapes()
        ILESharedConfiguration.get_instance().set_excluded_shapes(
            excluded_shapes
        )
        logger.trace(f'Setting excluded shapes = {excluded_shapes}')

        scene.room_dimensions = self.get_room_dimensions()
        logger.trace(f'Setting room dimensions = {scene.room_dimensions}')

        self._delayed_position_label = None
        self._delayed_position_distance = None
        if self.performer_starts_near:
            random_perf_starts_near = self.get_performer_distance()
            self._delayed_position_label = random_perf_starts_near.label
            self._delayed_position_distance = choose_random(
                random_perf_starts_near.distance
            )
            self._set_position_by_distance(scene)
        else:
            start_pos = self.get_performer_start_position(
                scene.room_dimensions)
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
        scene.room_materials = dict([
            (key, value.material) for key, value in wall_material_data.items()
        ])
        scene.restrict_open_doors = self.get_restrict_open_doors()
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
            wall_left['materials'] = [scene.room_materials['left']]
            wall_right['materials'] = [scene.room_materials['right']]
            scene.objects.extend([wall_left, wall_right])

        last_step = self.get_last_step()
        if not last_step and self.get_auto_last_step():
            last_step = get_step_limit_from_dimensions(
                room_x=scene.room_dimensions.x,
                room_z=scene.room_dimensions.z)
        if last_step:
            scene.goal['last_step'] = last_step
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
            (x, z) = geometry.get_position_distance_away_from_obj(
                scene.room_dimensions, target,
                self._delayed_position_distance,
                find_bounds(scene))
            scene.set_performer_start_position(x=x, y=None, z=z)
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
        return (
            choose_random(self.ceiling_material, MaterialTuple)
            if self.ceiling_material else
            random.choice(materials.CEILING_MATERIALS)
        )

    @ile_config_setter(validator=ValidateOptions(
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_ceiling_material(self, data: Any) -> None:
        self.ceiling_material = data

    def get_excluded_shapes(self) -> List[str]:
        return (
            self.excluded_shapes if isinstance(self.excluded_shapes, list) else
            [self.excluded_shapes]
        ) if self.excluded_shapes else []

    @ile_config_setter()
    def set_excluded_shapes(self, data: Any) -> None:
        self.excluded_shapes = data

    def get_floor_material(self) -> MaterialTuple:
        return choose_random(
            self.floor_material or materials.FLOOR_MATERIALS,
            MaterialTuple
        )

    @ile_config_setter(validator=ValidateOptions(
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_floor_material(self, data: Any) -> None:
        self.floor_material = data

    def get_goal(self):
        return self.goal

    @ile_config_setter(validator=ValidateOptions(props=['category'], options=[
        tags.SCENE.RETRIEVAL, tags.SCENE.MULTI_RETRIEVAL, tags.SCENE.PASSIVE
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
        return choose_random(self.performer_starts_near)

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
        self.performer_start_rotation = VectorIntConfig(
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

    def get_restrict_open_doors(
            self) -> bool:
        if self.restrict_open_doors is None:
            return False

        return self.restrict_open_doors

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
            material_choice = random.choice(materials.OPPOSITE_MATERIALS)
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

    def run_delayed_actions(self, scene: Dict[str, Any]) -> Dict[str, Any]:
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
            reasons.append(str(self._delayed_rotation_reason))
        if self._delayed_rotation_label and self._delayed_rotation_reason:
            reasons.append(str(self._delayed_rotation_reason))
        return reasons
