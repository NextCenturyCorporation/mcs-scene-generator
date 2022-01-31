import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

from machine_common_sense.config_manager import Vector3d

from generator import MaterialTuple, geometry, materials

from .choosers import (
    choose_material_tuple_from_material,
    choose_position,
    choose_random,
    choose_rotation,
)
from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import ILEDelayException, ILESharedConfiguration, find_bounds
from .interactable_object_config import InteractableObjectConfig
from .numerics import VectorFloatConfig, VectorIntConfig
from .object_services import TARGET_LABEL
from .validators import ValidateNoNullProp, ValidateNumber, ValidateOptions

logger = logging.getLogger(__name__)

# MCS-553 Increase the max room size from 15 once we are able to properly
# render the depth data at that distance in Unity.
ROOM_MAX_XZ = 15
ROOM_MIN_XZ = 2
ROOM_MAX_Y = 10
ROOM_MIN_Y = 2


@dataclass
class GoalConfig():
    """A dict with str `category` and optional `target`, `target_1`, and
    `target_2` properties that represents the goal and target object(s) in each
    scene. The `target*` properties are only needed if required for the
    specific category of goal. Each `target*` property is either an
    InteractableObjectConfig dict or list of InteractableObjectConfig dicts.
    For each list, one dict will be randomly chosen within the list in each
    new scene.  All goal target objects will be assigned the 'target' label.

    Example:
    ```
    category: retrieval
    target:
        shape: soccer_ball
        scale:
          min: 1.0
          max: 3.0
    ```
    """

    category: str = None
    target: Union[
        InteractableObjectConfig,
        List[InteractableObjectConfig]
    ] = None
    target_1: Union[
        InteractableObjectConfig,
        List[InteractableObjectConfig]
    ] = None
    target_2: Union[
        InteractableObjectConfig,
        List[InteractableObjectConfig]
    ] = None


class GlobalSettingsComponent(ILEComponent):
    """Manages the global settings of an ILE scene (the config properties that
    affect the whole scene)."""

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
    steps, from which one is chosen at random for each scene. Default: none
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

    performer_start_position: Union[
        VectorFloatConfig,
        List[VectorFloatConfig]
    ] = None
    """
    ([VectorFloatConfig](#VectorFloatConfig) dict, or list of VectorFloatConfig
    dicts): The starting position of the performer agent, or a list of
    positions, from which one is chosen at random for each scene. The
    (optional) `y` is used to position on top of structural objects like
    platforms. Default: random within the room

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

    room_dimensions: Union[VectorIntConfig, List[VectorIntConfig]] = None
    """
    ([VectorIntConfig](#VectorIntConfig) dict, or list of VectorIntConfig
    dicts): The total dimensions for the room, or list of dimensions, from
    which one is chosen at random for each scene. Rooms are always rectangular
    or square. The X and Z must each be within [2, 15] and the Y must be within
    [2, 10]. The room's bounds will be [-X/2, X/2] and [-Z/2, Z/2].
    Default: random

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

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring global settings for the scene...')

        excluded_shapes = self.get_excluded_shapes()
        ILESharedConfiguration.get_instance().set_excluded_shapes(
            excluded_shapes
        )
        logger.trace(f'Setting excluded shapes = {excluded_shapes}')

        # TODO MCS-696 Once we define a Scene class, we can probably give it
        # the Python classes rather than calling vars() on them.
        scene['roomDimensions'] = vars(self.get_room_dimensions())
        logger.trace(f'Setting room dimensions = {scene["roomDimensions"]}')
        scene['performerStart'] = {
            'position': vars(self.get_performer_start_position(
                scene['roomDimensions']
            )),
            'rotation': vars(self.get_performer_start_rotation())
        }
        logger.trace(f'Setting performer start = {scene["performerStart"]}')

        ceiling_material_tuple = self.get_ceiling_material()
        scene['ceilingMaterial'] = ceiling_material_tuple.material
        scene['debug']['ceilingColors'] = ceiling_material_tuple.color
        floor_material_tuple = self.get_floor_material()
        scene['floorMaterial'] = floor_material_tuple.material
        scene['debug']['floorColors'] = floor_material_tuple.color
        wall_material_data = self.get_wall_material_data()
        scene['roomMaterials'] = dict([
            (key, value.material) for key, value in wall_material_data.items()
        ])
        scene['debug']['wallColors'] = list(set([
            color for value in wall_material_data.values()
            for color in value.color
        ]))
        logger.trace(
            f'Setting room materials...\nCEILING={scene["ceilingMaterial"]}'
            f'\nFLOOR={scene["floorMaterial"]}\nWALL={scene["roomMaterials"]}'
        )

        last_step = self.get_last_step()
        if last_step:
            scene['goal']['last_step'] = last_step
            logger.trace(f'Setting last step = {last_step}')

        self._attempt_goal(scene)
        return scene

    def _attempt_goal(self, scene):
        try:
            goal_data, target_list = self.get_goal_data(scene)
            if goal_data:
                scene['goal']['category'] = goal_data['category']
                scene['goal']['description'] = goal_data['description']
                scene['goal']['metadata'] = goal_data['metadata']
                logger.trace(
                    f'Setting {scene["goal"]["category"]} goal with '
                    f'{len(target_list)} target(s): {scene["goal"]}'
                )
            for target in target_list:
                scene['objects'].append(target)
            self._delayed_goal = False
        except ILEDelayException as e:
            logger.trace("Goal failed and needs delay.", exc_info=e)
            self._delayed_goal = True

    def get_ceiling_material(self) -> MaterialTuple:
        return (
            choose_random(self.ceiling_material, MaterialTuple)
            if self.ceiling_material else
            random.choice(random.choice(materials.CEILING_AND_WALL_GROUPINGS))
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

    def get_goal_data(self, scene: Dict[str, Any]) -> Tuple[
        Dict[str, Any],
        List[Dict[str, Any]]
    ]:
        if not self.goal:
            return None, []

        # Choose a random goal category (and target if needed) from the config.
        choice: GoalConfig = choose_random(self.goal)
        goal_metadata = {}
        bounds_list = find_bounds(scene)
        target_list = []

        # Create the target(s) and add ID(s) to the goal's metadata.
        for prop in ['target', 'target_1', 'target_2']:
            config: InteractableObjectConfig = getattr(choice, prop)
            if config:
                labels = getattr(config, 'labels') or []
                labels = labels if isinstance(labels, list) else [labels]
                if TARGET_LABEL not in labels:
                    labels.append(TARGET_LABEL)
                setattr(config, 'labels', labels)
                instance = config.create_instance(
                    scene['roomDimensions'],
                    scene['performerStart'],
                    bounds_list
                )
                goal_metadata[prop] = {
                    'id': instance['id']
                }
                target_list.append(instance)
                logger.trace(
                    f'Creating goal "{prop}" from config = {vars(config)}'
                )

        description = None
        if choice.category.lower() == 'retrieval' and len(target_list):
            description = (
                f'Find and pick up the {target_list[0]["debug"]["goalString"]}'
            )

        return {
            'category': choice.category.lower(),
            'description': description,
            'metadata': goal_metadata
        }, target_list

    # If not null, category is required.
    @ile_config_setter(validator=ValidateNoNullProp(props=['category']))
    def set_goal(self, data: Any) -> None:
        self.goal = data

    def get_last_step(self) -> int:
        return self.last_step

    # If not null, it must be a number.
    @ile_config_setter(validator=ValidateNumber(min_value=1))
    def set_last_step(self, data: Any) -> None:
        self.last_step = data

    def get_performer_start_position(
        self,
        room_dimensions: Dict[str, int]
    ) -> Vector3d:
        return choose_position(
            self.performer_start_position,
            geometry.PERFORMER_WIDTH,
            geometry.PERFORMER_WIDTH,
            room_dimensions['x'],
            room_dimensions['z']
        )

    # allow partial setting of start position.  I.E.  only setting X
    @ile_config_setter(validator=ValidateNumber(
        props=['x', 'y', 'z'], null_ok=True))
    def set_performer_start_position(self, data: Any) -> None:
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

    def get_room_dimensions(self) -> VectorIntConfig:
        if self.room_dimensions:
            return choose_random(self.room_dimensions)
        good = False
        while not good:
            x = random.randint(ROOM_MIN_XZ, ROOM_MAX_XZ)
            z = (
                x if self.room_shape == 'square' else
                random.randint(ROOM_MIN_XZ, ROOM_MAX_XZ)
            )
            good = True
            # Enforce the max for the diagonal distance too.
            if math.sqrt(x**2 + z**2) > ROOM_MAX_XZ:
                good = False
            if self.room_shape == 'rectangle' and x == z:
                good = False
        return VectorIntConfig(x, random.randint(ROOM_MIN_Y, ROOM_MAX_Y), z)

    # If not null, all X/Y/Z properties are required.
    @ile_config_setter(validator=ValidateNumber(
        props=['x', 'z'],
        min_value=ROOM_MIN_XZ,
        max_value=ROOM_MAX_XZ)
    )
    @ile_config_setter(validator=ValidateNumber(
        props=['y'],
        min_value=ROOM_MIN_Y,
        max_value=ROOM_MAX_Y)
    )
    def set_room_dimensions(self, data: Any) -> None:
        self.room_dimensions = data

    @ile_config_setter(validator=ValidateOptions(
        options=['rectangle', 'square']
    ))
    def set_room_shape(self, data: Any) -> None:
        self.room_shape = data

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
    def set_wall_right_material(self, data: Any) -> None:
        self.wall_right_material = data

    def get_wall_material_data(self) -> Dict[str, MaterialTuple]:
        # All walls should use the same default material, so choose it now.
        material_choice = random.choice(random.choice(
            materials.CEILING_AND_WALL_GROUPINGS
        ))
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

    def get_num_delayed_actions(self) -> int:
        return 1 if self._delayed_goal else 0

    def run_delayed_actions(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        if self._delayed_goal:
            self._attempt_goal(scene)
        return scene
