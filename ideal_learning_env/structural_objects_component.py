import logging
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Union

from machine_common_sense.config_manager import Vector3d

from generator import geometry, materials, structures, util

from .choosers import choose_material_tuple_from_material, choose_random
from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import TRACE, ILEException, find_bounds
from .numerics import MinMaxFloat, MinMaxInt, VectorFloatConfig
from .validators import ValidateNumber, ValidateOptions

logger = logging.getLogger(__name__)

# Magic numbers used to create ranges for size, location, scale etc for objects
RAMP_WIDTH_PERCENT_MIN = 0.05
RAMP_WIDTH_PERCENT_MAX = 0.5
RAMP_LENGTH_PERCENT_MIN = 0.05
RAMP_LENGTH_PERCENT_MAX = 1
WALL_WIDTH_PERCENT_MIN = 0.05
WALL_WIDTH_PERCENT_MAX = 0.5
RAMP_ANGLE_MIN = 15
RAMP_ANGLE_MAX = 45
STRUCTURE_SCALE_MIN = 0.1
STRUCTURE_SCALE_MAX = 3


@dataclass
class RandomStructuralObjectConfig():
    """A dict that configures the number of structural objects that will be
    added to each scene. Each dict can have the following optional properties:
    - `type` (string, or list of strings): A type or a list of types that are
    options for this group.  The options include the following:
        - `l_occluders`: Random L-shaped occluders
        - `platforms`: Random platforms
        - `ramps`: Random ramps
        - `walls` Random interior room walls
    Default: All types
    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt)): The number of
    structural objects that should be generated in this group.  Each object is
    one of the type choices.
    """

    type: Union[str, List[str]] = None
    num: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = 0


@dataclass
class BaseStructuralObjectsConfig():
    """Base class used for specific structural objects"""
    num: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = 0
    position: Union[VectorFloatConfig, List[VectorFloatConfig]] = None
    rotation_y: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    material: Union[str, List[str]] = None


@dataclass
class StructuralWallConfig(BaseStructuralObjectsConfig):
    """
    Defines details of a structural interior wall.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): The width of the wall.
    - `height` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): The height of the wall.
    """
    width: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    height: Union[float, MinMaxFloat,
                  List[Union[float, MinMaxFloat]]] = None


@dataclass
class StructuralPlatformConfig(BaseStructuralObjectsConfig):
    """
    Defines details of a structural platform.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Scale of the platform
    """
    scale: Union[float, MinMaxFloat, List[Union[float, MinMaxFloat]],
                 VectorFloatConfig, List[VectorFloatConfig]] = None


@dataclass
class StructuralRampConfig(BaseStructuralObjectsConfig):
    """
    Defines details of a structural ramp.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `angle` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Angle of the ramp upward from the floor
    - `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Width of the ramp
    - `length` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Length of the ramp
    """
    angle: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    width: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    length: Union[float, MinMaxFloat,
                  List[Union[float, MinMaxFloat]]] = None


@dataclass
class StructuralLOccluderConfig(BaseStructuralObjectsConfig):
    """
    Defines details of a structural L-shaped occluder.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `scale_front_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale in the x direction of the front
    part of the occluder
    - `scale_front_z` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale in the z direction of the front
    part of the occluder
    - `scale_side_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale in the x direction of the side
    part of the occluder
    - `scale_side_z` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale in the z direction of the side
    part of the occluder
    - `scale_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale in the y direction for the
    entire occluder
    """
    scale_front_x: Union[float, MinMaxFloat,
                         List[Union[float, MinMaxFloat]]] = None
    scale_front_z: Union[float, MinMaxFloat,
                         List[Union[float, MinMaxFloat]]] = None
    scale_side_x: Union[float, MinMaxFloat,
                        List[Union[float, MinMaxFloat]]] = None
    scale_side_z: Union[float, MinMaxFloat,
                        List[Union[float, MinMaxFloat]]] = None
    scale_y: Union[float, MinMaxFloat,
                   List[Union[float, MinMaxFloat]]] = None


class StructuralTypes(Enum):
    WALLS = auto()
    L_OCCLUDERS = auto()
    PLATFORMS = auto()
    RAMPS = auto()


def validate_all_locations_and_update_bounds(
    objects: Union[list, dict],
    scene: Dict[str, Any],
    bounds: List[List[Dict[str, float]]]
) -> bool:
    '''Returns true if objects don't intersect with existing bounds or
    false otherwise.  If true, will also add new object bounds to bounds
    object.'''

    starting_pos = scene['performerStart']['position']
    for object in objects:
        bb = object.get('shows')[0].get('boundingBox')
        if not geometry.validate_location_rect(
            bb,
            starting_pos,
            bounds,
            scene['roomDimensions']
        ):
            return False
    for object in objects:
        bb = object['shows'][0]['boundingBox']
        bounds.append(bb)
    return True


def add_structural_object_with_retries_or_throw(
        scene: dict, bounds: dict, retries: int, template: dict,
        structural_type: StructuralTypes, i: int):
    """Attempts to take a scene and a bounds and add an structural object of a
    given type.  If a template is provided, then the template will be used for
    the values provided.

    If there are more attempts than retries without success, an ILEException
    will be thrown.
    """
    for try_num in range(retries):
        new_obj = get_structural_object(
            structural_type, scene, template)
        if not isinstance(new_obj, list):
            new_obj = [new_obj]
        if validate_all_locations_and_update_bounds(
                new_obj, scene, bounds):
            logger.log(
                TRACE,
                f"created object of {structural_type} #{i} on try "
                f"{try_num} of {retries}.  Object = {new_obj}"
            )
            break
        else:
            logger.debug('Validation failed; retrying creation...')
            new_obj = None
    if new_obj is not None:
        for object in new_obj:
            scene['objects'].append(object)
    else:
        msg = f"Failed to create structural object of {structural_type} "
        msg += f"after {retries}.  Try using fewer objects"
        logger.warning(msg)
        raise ILEException(msg)


def get_structural_object(structural_type: StructuralTypes,
                          scene, template=None) -> Dict[str, Any]:
    """Creates a structural object of the given type using any available
    parameters from the template if provided"""
    room_dim = scene.get('roomDimensions', {})
    def_dim = geometry.DEFAULT_ROOM_DIMENSIONS
    room_width = room_dim.get('x', def_dim['x'])
    room_length = room_dim.get('z', def_dim['y'])
    room_height = room_dim.get('y', def_dim['z'])
    min_room_dim = min(room_width, room_length)
    max_room_dim = max(room_width, room_length)

    tpos = getattr(template, 'position', {})
    tx = getattr(tpos, 'x', None)
    tz = getattr(tpos, 'z', None)
    trot = getattr(template, 'rotation_y', None)
    x = (
        MinMaxFloat(-room_width / 2.0, room_width / 2.0).convert_value()
        if tx is None else tx
    )
    z = (
        MinMaxFloat(-room_length / 2.0, room_length / 2.0).convert_value()
        if tz is None else tz
    )
    rot = geometry.random_rotation() if trot is None else trot
    tmat = getattr(template, 'material', None)
    mat = choose_material_tuple_from_material(tmat)
    # Is this necessary?
    if mat is None:
        mat = random.choice(materials.ALL_MATERIAL_TUPLES)
    # TODO MCS-813 Conversion won't be needed
    mat = materials.MaterialTuple(mat[0], mat[1])
    args = {
        'position_x': x,
        'position_z': z,
        'rotation_y': rot,
        'material_tuple': mat
    }

    scale = MinMaxFloat(STRUCTURE_SCALE_MIN, STRUCTURE_SCALE_MAX)
    if structural_type == StructuralTypes.WALLS:
        setup_wall_args(template, room_height, max_room_dim, args)
        logger.debug(
            f'Creating INTERIOR WALL:\nTEMPLATE = '
            f'{vars(template) if template else {}}\nARGS = {args}'
        )
        return structures.create_interior_wall(**args)
    if structural_type == StructuralTypes.PLATFORMS:
        setup_platform_args(template, args, scale)
        logger.debug(
            f'Creating PLATFORM:\nTEMPLATE = '
            f'{vars(template) if template else {}}\nARGS = {args}'
        )
        return structures.create_platform(**args)
    if structural_type == StructuralTypes.RAMPS:
        setup_ramp_args(template, min_room_dim, args)
        logger.debug(
            f'Creating RAMP:\nTEMPLATE = '
            f'{vars(template) if template else {}}\nARGS = {args}'
        )
        return structures.create_ramp(**args)
    if structural_type == StructuralTypes.L_OCCLUDERS:
        setup_l_occluder_args(template, args, scale)
        logger.debug(
            f'Creating L-OCCLUDER:\nTEMPLATE = '
            f'{vars(template) if template else {}}\nARGS = {args}'
        )
    return structures.create_l_occluder(**args)


def setup_wall_args(template: StructuralWallConfig, room_height: int,
                    max_room_dim: int, args: dict):
    """Applies extra arguments needed for a wall from the template if
    available."""
    width = MinMaxFloat(
        max_room_dim * WALL_WIDTH_PERCENT_MIN,
        max_room_dim * WALL_WIDTH_PERCENT_MAX)
    args['width'] = getattr(template, 'width', None) or width.convert_value()
    # Wall height always equals room height.
    args['height'] = room_height


def setup_l_occluder_args(
        template: StructuralLOccluderConfig, args: dict, scale):
    """Applies extra arguments needed for an l occluder from the template if
    available."""
    args['scale_front_x'] = getattr(
        template, 'scale_front_x', None) or scale.convert_value()
    args['scale_front_z'] = getattr(
        template, 'scale_front_z', None) or scale.convert_value()
    args['scale_side_x'] = getattr(
        template, 'scale_side_x', None) or scale.convert_value()
    args['scale_side_z'] = getattr(
        template, 'scale_side_z', None) or scale.convert_value()
    args['scale_y'] = getattr(
        template, 'scale_y', None) or scale.convert_value()


def setup_ramp_args(template: StructuralRampConfig,
                    min_room_dim: int, args: dict):
    """Applies extra arguments needed for a ramp from the template if
    available."""
    width = MinMaxFloat(
        min_room_dim * RAMP_WIDTH_PERCENT_MIN,
        min_room_dim * RAMP_WIDTH_PERCENT_MAX)
    length = MinMaxFloat(
        min_room_dim * RAMP_LENGTH_PERCENT_MIN,
        min_room_dim * RAMP_LENGTH_PERCENT_MAX)
    angle = MinMaxFloat(RAMP_ANGLE_MIN, RAMP_ANGLE_MAX)
    args['angle'] = getattr(
        template, 'angle', None) or angle.convert_value()
    args['width'] = getattr(
        template, 'width', None) or width.convert_value()
    args['length'] = getattr(
        template, 'length', None) or length.convert_value()


def setup_platform_args(template: StructuralPlatformConfig,
                        args: dict, scale: MinMaxFloat):
    """Applies extra arguments needed for a platform from the template if
    available."""
    tscale = getattr(template, 'scale', None)
    if tscale:
        if isinstance(tscale, Vector3d):
            args['scale_x'] = tscale.x
            args['scale_y'] = tscale.y
            args['scale_z'] = tscale.z
        else:
            # must be a single float
            args['scale_x'] = tscale
            args['scale_y'] = tscale
            args['scale_z'] = tscale
    else:
        args['scale_x'] = scale.convert_value()
        args['scale_y'] = scale.convert_value()
        args['scale_z'] = scale.convert_value()


class SpecificStructuralObjectsComponent(ILEComponent):
    """Adds specific structural objects to an ILE scene.  Users can specify
    more exact values, ranges, or leave blank each type of structural object.
    When a choice is specified, each generated scene will have a different
    value generated within that choice.

    This component requires performerStart.location to be set in the scene
    prior. This is typically handles by the GlobalSettingsComponent"""

    structural_walls: Union[
        StructuralWallConfig,
        List[StructuralWallConfig]] = None
    """
    ([StructuralWallConfig](#StructuralWallConfig) dict, or list of
    [StructuralWallConfig](#StructuralWallConfig) dicts): Template(s)
    containing properties needed to create an interior wall.  Default: None

    Simple Example:
    ```
    structural_walls:
      num: 0
    ```

    Advanced Example:
    ```
    structural_walls:
        num:
          min: 1
          max: 3
        position:
          x: 1
          y: 0
          z: 2
        rotation_y: 30
        material: 'PLASTIC_MATERIALS'
        width: .5
        height: .3
    ```
    """

    structural_platforms: Union[
        StructuralPlatformConfig,
        List[StructuralPlatformConfig]] = None
    """
    ([StructuralPlatformConfig](#StructuralPlatformConfig) dict, or list of
    [StructuralPlatformConfig](#StructuralPlatformConfig) dicts): Template(s)
    containing properties needed to create a platform.  Default: None

    Simple Example:
    ```
    structural_platforms:
      num: 0
    ```

    Advanced Example:
    ```
    structural_platforms:
        num: [1, 2, 4]
        position:
          x: 1
          y: 0
          z: 2
        rotation_y: 30
        material: 'PLASTIC_MATERIALS'
        scale:
          x: 1.1
          y: [0.5, 1]
          z:
            min: 0.3
            max: 1.3
    ```
    """

    structural_l_occluders: Union[
        StructuralLOccluderConfig,
        List[StructuralLOccluderConfig]] = None
    """
    ([StructuralOccluderConfig](#StructuralOccluderConfig) dict, or list of
    [StructuralOccluderConfig](#StructuralOccluderConfig) dicts): Template(s)
    containing properties needed to create an L-shaped occluder.  Default: None

    Simple Example
    ```
    structural_l_occluders:
      num: 0
    ```

    Advanced Example:
    ```
    structural_l_occluders:
        num: 2
        position:
          x: 1
          y: 0
          z: 2
        rotation_y: 30
        material: 'AI2-THOR/Materials/Metals/Brass 1'
        scale_front_x: 0.3
        scale_front_z: [0.4, 0.5, 0.6]
        scale_side_x:
          min: 0.1
          max: 2.1
        scale_side_z: 0.6
        scale_y: 0.7
    ```
    """

    structural_ramps: Union[
        StructuralRampConfig,
        List[StructuralRampConfig]] = None
    """
    ([StructuralRampConfig](#StructuralRampConfig) dict, or list of
    [StructuralRampConfig](#StructuralRampConfig) dicts): Template(s)
    containing properties needed to create a ramp.  Default: None

    Simple Example:
    ```
    structural_ramps:
      num: 0
    ```

    Advanced Example:
    ```
    structural_ramps:
        num:
          min: 0
          max: 3
        position:
          x: 1
          y: 0
          z: 2
        rotation_y: 30
        material: 'AI2-THOR/Materials/Metals/Brass 1'
        angle: 30
        width: 0.4
        length: 0.5
    ```
    """

    def get_structural_walls(self) -> int:
        return self._get_val(self.structural_walls, StructuralWallConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(
            materials.ALL_MATERIAL_LISTS + materials.ALL_MATERIAL_STRINGS
        )
    ))
    def set_structural_walls(self, data: Any) -> None:
        self.structural_walls = data

    def get_structural_platforms(self) -> int:
        return self._get_val(self.structural_platforms,
                             StructuralPlatformConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(
            materials.ALL_MATERIAL_LISTS + materials.ALL_MATERIAL_STRINGS
        )
    ))
    def set_structural_platforms(self, data: Any) -> None:
        self.structural_platforms = data

    def get_structural_l_occluders(self) -> int:
        return self._get_val(self.structural_l_occluders,
                             StructuralLOccluderConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(
            materials.ALL_MATERIAL_LISTS + materials.ALL_MATERIAL_STRINGS
        )
    ))
    def set_structural_l_occluders(self, data: Any) -> None:
        self.structural_l_occluders = data

    def get_structural_ramps(self) -> int:
        return self._get_val(self.structural_ramps, StructuralRampConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(
            materials.ALL_MATERIAL_LISTS + materials.ALL_MATERIAL_STRINGS
        )
    ))
    def set_structural_ramps(self, data: Any) -> None:
        self.structural_ramps = data

    def _get_val(self, data, type):
        if data is None:
            return None
        return choose_random(
            [] if data is None else data, type
        )

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug('Running specific structural objects component...')

        scene['objects'] = scene.get('objects', [])
        bounds = find_bounds(scene['objects'])

        structural_type_templates = [
            (StructuralTypes.WALLS, self.get_structural_walls),
            (StructuralTypes.PLATFORMS, self.get_structural_platforms),
            (StructuralTypes.L_OCCLUDERS, self.get_structural_l_occluders),
            (StructuralTypes.RAMPS, self.get_structural_ramps)
        ]

        for s_type, s_func in structural_type_templates:
            num_template = s_func()
            if num_template:
                for i in range(num_template.num):
                    template = s_func()
                    add_structural_object_with_retries_or_throw(
                        scene, bounds, util.MAX_TRIES, template,
                        s_type, i)

        return scene


class RandomStructuralObjectsComponent(ILEComponent):
    """Adds random structural objects to an ILE scene.  Users can specify an
    exact number or a range.  When a range is specified, each generated scene
    will have a uniformly distributed random number be generated within that
    range, inclusively.  Alternatively, the user can specify an object with
    a number or range for each type of structural object, wall, l occluder,
    platform, ramp.

    This component requires performerStart.location to be set in the scene
    prior. This is typically handles by the GlobalSettingsComponent"""
    random_structural_objects: Union[RandomStructuralObjectConfig,
                                     List[RandomStructuralObjectConfig]] = 0
    """
    ([RandomStructuralObjectConfig](#RandomStructuralObjectConfig), or list of
    [RandomStructuralObjectConfig](#RandomStructuralObjectConfig) dict) --
    Groups of random object types and how many should be generated from the
    type options.
    Default: 2 to 4 of all types
    ```
    random_structural_objects:
      - type: ['walls','platforms','ramps','l_occluders']
        num:
          min: 2
          max: 4
    ```

    Simple Example:
    ```
    random_structural_objects: null
    ```

    Advanced Example:
    ```
    random_structural_objects:
      - type: ['walls','platforms','ramps','l_occluders']
        num:
            min: 0
            max: 2
      - type: ['walls','l_occluders']
        num: [3, 5, 7]
      - type: 'walls'
        num: 2
    ```
    """

    ALL_STRUCTURAL_OBJECT_TYPES = [
        "walls", "ramps", "l_occluders", "platforms"]
    DEFAULT_VALUE = [RandomStructuralObjectConfig(
        **{"type": ["walls", "l_occluders", "platforms", "ramps"],
           # Add moving occluders, droppers, throwers, placers, holes, and lava
           # when implemented.
           "num": MinMaxInt(2, 4)
           })]

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug('Running random structural objects component...')

        scene['objects'] = scene.get('objects', [])
        bounds = find_bounds(scene['objects'])
        templates = self.random_structural_objects
        if templates is None:
            templates = self.DEFAULT_VALUE
        templates = templates if isinstance(templates, List) else [templates]

        logger.debug(
            f'Choosing random structural objects: {templates}'
        )

        retries = util.MAX_TRIES

        for template in templates:
            num = choose_random(template.num)
            for i in range(num):
                type = choose_random(
                    template.type or self.ALL_STRUCTURAL_OBJECT_TYPES)
                structural_type = StructuralTypes[type.upper()]
                add_structural_object_with_retries_or_throw(
                    scene, bounds, retries, None, structural_type, i)

        return scene

    def get_random_structural_objects(
            self) -> List[RandomStructuralObjectConfig]:
        rso = self.random_structural_objects
        if rso is None:
            return self.DEFAULT_VALUE
        if not isinstance(rso, List):
            rso = [rso]
        return [choose_random(obj) for obj in rso]

    # If not null, each number must be an integer zero or greater.
    @ile_config_setter(validator=ValidateNumber(
        props=[
            'num'],
        min_value=0)
    )
    def set_random_structural_objects(self, data: Any) -> None:
        self.random_structural_objects = data
