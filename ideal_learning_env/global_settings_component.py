import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

from machine_common_sense.config_manager import PhysicsConfig, Vector3d

from generator import MaterialTuple, util
from generator.materials import CEILING_AND_WALL_GROUPINGS, FLOOR_MATERIALS

from .choosers import choose_position, choose_random, choose_rotation
from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import find_bounds
from .interactable_object_config import InteractableObjectConfig
from .numerics import VectorFloatConfig, VectorIntConfig
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
    new scene.

    Example:
    ```
    category: retrieval
    target:
        shape: soccer_ball
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

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug('Running global settings component...')

        # TODO MCS-696 Once we define a Scene class, we can probably give it
        # the Python classes rather than calling vars() on them.
        scene['roomDimensions'] = vars(self.get_room_dimensions())
        logger.debug(f'Setting room dimensions = {scene["roomDimensions"]}')
        scene['performerStart'] = {
            'position': vars(self.get_performer_start_position(
                scene['roomDimensions']
            )),
            'rotation': vars(self.get_performer_start_rotation())
        }
        logger.debug(f'Setting performer start = {scene["performerStart"]}')

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
        logger.debug(
            f'Setting room materials...\nCEILING={scene["ceilingMaterial"]}'
            f'FLOOR={scene["floorMaterial"]}\nWALL={scene["roomMaterials"]}'
        )

        last_step = self.get_last_step()
        if last_step:
            scene['goal']['last_step'] = last_step
            logger.debug(f'Setting last step = {last_step}')
        goal_category, goal_metadata, target_list = self.get_goal_data(scene)
        if goal_category:
            scene['goal']['category'] = goal_category
            scene['goal']['metadata'] = goal_metadata
            logger.debug(
                f'Setting goal category = "{goal_category}" with metadata = '
                f'{goal_metadata} and {len(target_list)} target(s)'
            )
        for target in target_list:
            scene['objects'].append(target)
        return scene

    def get_ceiling_material(self) -> MaterialTuple:
        return choose_random(self.ceiling_material or [
            material_tuple for nested_list in CEILING_AND_WALL_GROUPINGS
            for material_tuple in nested_list
        ], MaterialTuple)

    @ile_config_setter()
    def set_ceiling_material(self, data: Any) -> None:
        self.ceiling_material = data

    def get_floor_material(self) -> MaterialTuple:
        return choose_random(
            self.floor_material or FLOOR_MATERIALS,
            MaterialTuple
        )

    @ile_config_setter()
    def set_floor_material(self, data: Any) -> None:
        self.floor_material = data

    # If not null, each nested property (except enable) must be a number.
    @ile_config_setter(validator=ValidateNumber(props=[
        'angularDrag', 'bounciness', 'drag', 'dynamicFriction' 'staticFriction'
    ], min_value=0, max_value=1))

    def get_goal_data(self, scene: Dict[str, Any]) -> Tuple[
        str,
        Dict[str, Any],
        List[Dict[str, Any]]
    ]:
        if not self.goal:
            return None, None, []

        # Choose a random goal category (and target if needed) from the config.
        choice: GoalConfig = choose_random(self.goal)
        goal_metadata = {}
        bounds_list = find_bounds(scene['objects'])
        target_list = []

        # Create the target(s) and add ID(s) to the goal's metadata.
        for prop in ['target', 'target_1', 'target_2']:
            config: InteractableObjectConfig = getattr(choice, prop)
            if config:
                instance = config.create_instance(
                    scene['roomDimensions'],
                    scene['performerStart'],
                    bounds_list
                )
                goal_metadata[prop] = {
                    'id': instance['id']
                }
                target_list.append(instance)
                logger.debug(
                    f'Creating goal "{prop}" from config = {vars(config)}'
                )

        return choice.category, goal_metadata, target_list

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
            util.PERFORMER_WIDTH,
            util.PERFORMER_WIDTH,
            room_dimensions['x'],
            room_dimensions['z']
        )

    # If not null, the X and Z properties are required.
    @ile_config_setter(validator=ValidateNoNullProp(props=['x', 'z']))
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

    @ile_config_setter()
    def set_wall_back_material(self, data: Any) -> None:
        self.wall_back_material = data

    @ile_config_setter()
    def set_wall_front_material(self, data: Any) -> None:
        self.wall_front_material = data

    @ile_config_setter()
    def set_wall_left_material(self, data: Any) -> None:
        self.wall_left_material = data

    @ile_config_setter()
    def set_wall_right_material(self, data: Any) -> None:
        self.wall_right_material = data

    def get_wall_material_data(self) -> Dict[str, MaterialTuple]:
        # All walls should use the same default material, so choose it now.
        material_choice = random.choice(random.choice(
            CEILING_AND_WALL_GROUPINGS
        ))
        return {
            'back': choose_random(
                self.wall_back_material or material_choice,
                MaterialTuple
            ),
            'front': choose_random(
                self.wall_front_material or material_choice,
                MaterialTuple
            ),
            'left': choose_random(
                self.wall_left_material or material_choice,
                MaterialTuple
            ),
            'right': choose_random(
                self.wall_right_material or material_choice,
                MaterialTuple
            )
        }
