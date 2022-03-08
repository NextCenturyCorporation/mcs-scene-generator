import copy
import logging
import math
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union

from machine_common_sense.config_manager import Vector3d
from machine_common_sense.logging_config import TRACE

from generator import (
    ALL_LARGE_BLOCK_TOOLS,
    MAX_TRIES,
    ObjectBounds,
    geometry,
    instances,
    materials,
    mechanisms,
    occluders,
    specific_objects,
    structures,
)
from ideal_learning_env.global_settings_component import (
    ROOM_MIN_XZ,
    ROOM_MIN_Y,
)
from ideal_learning_env.goal_services import TARGET_LABEL
from ideal_learning_env.interactable_object_config import (
    InteractableObjectConfig,
    KeywordLocationConfig,
)
from ideal_learning_env.object_services import (
    InstanceDefinitionLocationTuple,
    KeywordLocation,
    ObjectDefinition,
    ObjectRepository,
    add_random_placement_tag,
    reconcile_template,
)

from .choosers import (
    choose_material_tuple_from_material,
    choose_position,
    choose_random,
    choose_rotation,
)
from .defs import ILEException
from .numerics import (
    MinMaxFloat,
    MinMaxInt,
    VectorFloatConfig,
    VectorIntConfig,
)

logger = logging.getLogger(__name__)

# Magic numbers used to create ranges for size, location, scale etc for objects
PLATFORM_SCALE_MIN = 0.5
PLATFORM_SCALE_MAX = 3
RAMP_WIDTH_PERCENT_MIN = 0.05
RAMP_WIDTH_PERCENT_MAX = 0.5
RAMP_LENGTH_PERCENT_MIN = 0.05
RAMP_LENGTH_PERCENT_MAX = 1
WALL_WIDTH_PERCENT_MIN = 0.05
WALL_WIDTH_PERCENT_MAX = 0.5
RAMP_ANGLE_MIN = 15
RAMP_ANGLE_MAX = 45
L_OCCLUDER_SCALE_MIN = 0.5
L_OCCLUDER_SCALE_MAX = 2
DROPPER_THROWER_BUFFER = 0.2
DEFAULT_PROJECTILE_SCALE = MinMaxFloat(0.2, 2)
# Ranges for Occluders when values are not specified
DEFAULT_MOVING_OCCLUDER_HEIGHT_MIN = 1
DEFAULT_MOVING_OCCLUDER_HEIGHT_MAX = occluders.OCCLUDER_HEIGHT_TALL
DEFAULT_MOVING_OCCLUDER_WIDTH_MIN = occluders.OCCLUDER_MIN_SCALE_X
DEFAULT_MOVING_OCCLUDER_WIDTH_MAX = 3
DEFAULT_MOVING_OCCLUDER_THICKNESS_MIN = occluders.OCCLUDER_THICKNESS
DEFAULT_MOVING_OCCLUDER_THICKNESS_MAX = occluders.OCCLUDER_THICKNESS
DEFAULT_MOVING_OCCLUDER_REPEAT_MIN = 1
DEFAULT_MOVING_OCCLUDER_REPEAT_MAX = 20
DEFAULT_OCCLUDER_ROTATION_MIN = 0
DEFAULT_OCCLUDER_ROTATION_MAX = 359
DEFAULT_OCCLUDING_WALL_HEIGHT = MinMaxFloat(0.5, 2)
DEFAULT_OCCLUDING_WALL_THICKNESS = MinMaxFloat(0.1, 0.5)
DEFAULT_OCCLUDING_WALL_WIDTH = MinMaxFloat(0.5, 2)

# multiply target's scale by these values to make
# sure target is sufficiently occluded.
DEFAULT_OCCLUDING_WALL_HEIGHT_MULTIPLIER = 3.0
DEFAULT_OCCLUDING_WALL_WIDTH_MULTIPLIER = 2.0

DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MIN = 0.2
# Agents can wall over 0.1 height walls but not 0.15
DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_Y_MIN = 0.15
DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MAX = 0.5

# Height of 0.9 blocks agent, but doesn't look like it should visually
OCCLUDING_WALL_HOLE_MAX_HEIGHT = 0.8
OCCLUDING_WALL_WIDTH_BUFFER = 0.6

ATTACHED_RAMP_MIN_WIDTH = .5
ATTACHED_RAMP_MAX_WIDTH = 1.5
ATTACHED_RAMP_MAX_LENGTH = 3
ATTACHED_RAMP_MIN_LENGTH = .5
TOP_PLATFORM_POSITION_MIN = 0.3

# These are arbitrary but they need to be high enough that a ramp can get up
# the top platform without being greater than 45 degress.
BOTTOM_PLATFORM_SCALE_BUFFER_MIN = geometry.PERFORMER_WIDTH
BOTTOM_PLATFORM_SCALE_BUFFER_MAX = 5

# used to determine where ramps can fit next to platforms.  When on the floor,
# we don't have a good way to determine this (particularly when rotated) so we
# use an arbitrarily large number and let the bounds checking determine if
# locations are valid later.
DEFAULT_AVAIABLE_LENGTHS = (10, 10, 10, 10)
RAMP_ROTATIONS = (90, 180, -90, 0)

ALL_THROWABLE_SHAPES = list(set([
    definition.type for definition in
    specific_objects.get_throwable_definition_dataset(True).definitions()
]))


def log_structural_template_object(
    label: str,
    key: str,
    value: Any,
    templates: Optional[List] = None
) -> None:
    config_string = (
        f'\nCONFIG = {vars(templates[0]) if templates[0] else "None"}'
        if templates else ''
    )
    reconciled_string = (
        f'\nRECONCILED = {vars(templates[1] if templates[1] else "None")}'
        if templates and len(templates) > 1 else ''
    )
    logger.trace(
        f'Added {label}: {key.upper()} = {value}'
        f'{config_string}'
        f'{reconciled_string}'
    )


class WallSide(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    FRONT = "front"
    BACK = "back"


class OccluderOrigin(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    FRONT = "front"
    BACK = "back"
    TOP = "top"


class OccludingWallType(str, Enum):
    OCCLUDES = "occludes"
    THIN = "thin"
    SHORT = "short"
    HOLE = "hole"


class StructuralTypes(Enum):
    DOORS = auto()
    DROPPERS = auto()
    FLOOR_MATERIALS = auto()
    HOLES = auto()
    L_OCCLUDERS = auto()
    LAVA = auto()
    MOVING_OCCLUDERS = auto()
    OCCLUDING_WALLS = auto()
    PLACERS = auto()
    PLATFORMS = auto()
    RAMPS = auto()
    THROWERS = auto()
    WALLS = auto()
    TOOLS = auto()


@dataclass
class BaseStructuralObjectsConfig():
    """Base class that should used for all structural objects."""
    num: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = 0
    labels: Union[str, List[str]] = None


@dataclass
class PositionableStructuralObjectsConfig(BaseStructuralObjectsConfig):
    """Simple class used for user-positionable structural objects."""
    position: Union[VectorFloatConfig, List[VectorFloatConfig]] = None
    rotation_y: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    material: Union[str, List[str]] = None


@dataclass
class StructuralWallConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural interior wall.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `height` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): The height of the wall.
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "walls"
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): The width of the wall.
    """
    width: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    height: Union[float, MinMaxFloat,
                  List[Union[float, MinMaxFloat]]] = None


@dataclass
class StructuralPlatformLipsConfig():
    """
    Defines the platform's lips with front, back,
    left, and right configurations.

    - `front` (bool) : Positive Z axis
    - `back` (bool) : Negative Z axis
    - `left` (bool) : Negative X axis
    - `right` (bool) : Positive X axis
    """
    front: bool = None
    back: bool = None
    left: bool = None
    right: bool = None


@dataclass
class StructuralPlatformConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural platform.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "platforms"
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Scale of the platform
    - `lips` ([StructuralPlatformLipsConfig]
    (#StructuralPlatformLipsConfig), or list of
    StructuralPlatformLipsConfig): The platform's lips. Default: None
    - `attached_ramps` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): Number of ramps that should be attached to
    this platform to allow the performer to climb up to this platform.
    Default: 0
    - `platform_underneath` (bool or list of bools): If true, add a platform
    below this platform that touches the floor on the bottom and this platform
    on the top.  This platform will fully be encased in the x/z directions by
    the platform created underneath.  Default: False
    - `platform_underneath_attached_ramps` (int, or list of ints, or
    [MinMaxInt](#MinMaxInt) dict, or list of MinMaxInt dicts): Number of ramps
    that should be attached to the platform created below this platform to
    allow the performer to climb onto that platform. Default: 0
    """
    lips: Union[StructuralPlatformLipsConfig,
                List[StructuralPlatformLipsConfig]] = None
    scale: Union[float, MinMaxFloat, List[Union[float, MinMaxFloat]],
                 VectorFloatConfig, List[VectorFloatConfig]] = None
    attached_ramps: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    platform_underneath: Union[bool, List[bool]] = None
    platform_underneath_attached_ramps: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None  # noqa


@dataclass
class StructuralRampConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural ramp.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `angle` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Angle of the ramp upward from the floor
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "ramps"
    - `length` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Length of the ramp along the floor.  This
    is the 'adjacent' side and not the hypotenuse.
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Width of the ramp
    - `platform_underneath` (bool or list of bools): If true, add a platform
    below this ramp that touches the floor on the bottom and the bottom of
    this ramp on the top.  This ramp will fully be encased in the x/z
    directions by the platform created underneath.  Default: False
    - `platform_underneath_attached_ramps` (int, or list of ints, or
    [MinMaxInt](#MinMaxInt) dict, or list of MinMaxInt dicts): Number of ramps
    that should be attached to the platform created below this ramp to
    allow the performer to climb onto that platform.  Default: 0
    """
    angle: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    width: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    length: Union[float, MinMaxFloat,
                  List[Union[float, MinMaxFloat]]] = None
    platform_underneath: Union[bool, List[bool]] = None
    platform_underneath_attached_ramps: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None  # noqa


@dataclass
class StructuralLOccluderConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural L-shaped occluder.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `backwards` (bool, or list of bools): Whether to create a backwards L.
    Default: [true, false]
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "l_occluders"
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
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
    backwards: Union[bool, List[bool]] = None
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


@dataclass
class StructuralDropperConfig(BaseStructuralObjectsConfig):
    """
    Defines details of a structural dropper and its dropped projectile.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `drop_step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): The step of the simulation in which the
    projectile should be dropped.
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "droppers"
    - `position_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Position in the x direction of the of
    the ceiling where the dropper should be placed.
    - `position_z` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Position in the z direction of the of
    the ceiling where the dropper should be placed.
    - `projectile_labels` (string, or list of strings): A label for an existing
    object in your ILE configuration that will be used as this device's
    projectile, or new label(s) to associate with a new projectile object.
    Other configuration options may use this label to reference this object or
    a group of objects. Labels are not unique, and when multiple objects share
    labels, the ILE may choose one available object or all of them, depending
    on the specific option. The ILE will ignore any objects that have keyword
    locations or are used by other droppers/placers/throwers.
    - `projectile_material` (string, or list of strings): The projectiles's
    material or material type.
    - `projectile_scale` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Scale of
    the projectile.  Default is a value between 0.2 and 2.
    - `projectile_shape` (string, or list of strings): The shape or type of
    the projectile.
    """
    position_x: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    position_z: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    drop_step: Union[int, MinMaxInt,
                     List[Union[int, MinMaxInt]]] = None
    projectile_shape: Union[str, List[str]] = None
    projectile_material: Union[str, List[str]] = None
    projectile_scale: Union[float, MinMaxFloat,
                            List[Union[float, MinMaxFloat]],
                            VectorFloatConfig, List[VectorFloatConfig]] = None
    projectile_labels: Union[str, List[str]] = None


@dataclass
class StructuralThrowerConfig(BaseStructuralObjectsConfig):
    """
    Defines details of a structural dropper and its thrown projectile.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "throwers"
    - `height` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): The
    height on the wall that the thrower will be placed.
    - `position_wall` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): The
    position along the wall that the thrower will be placed.
    - `projectile_labels` (string, or list of strings): A label for an existing
    object in your ILE configuration that will be used as this device's
    projectile, or new label(s) to associate with a new projectile object.
    Other configuration options may use this label to reference this object or
    a group of objects. Labels are not unique, and when multiple objects share
    labels, the ILE may choose one available object or all of them, depending
    on the specific option. The ILE will ignore any objects that have keyword
    locations or are used by other droppers/placers/throwers.
    - `projectile_material` (string, or list of strings): The projectiles's
    material or material type.
    - `projectile_scale` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Scale of
    the projectile.  Default is a value between 0.2 and 2.
    - `projectile_shape` (string, or list of strings): The shape or type of
    the projectile.
    - `rotation` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): The angle
    in which the thrower will be rotated to point upwards.  This value should
    be between 0 and 15.
    - `throw_force` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Force of
    the throw put on the projectile.  This value will be multiplied by the
    mass of the projectile.  Values between 500 and 1500 are typical.
    - `throw_step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): The step of the simulation in which the
    projectile should be thrown.
    - `wall` (string, or list of strings): Which wall the thrower should be
    placed on.  Options are: left, right, front, back.
    """
    wall: Union[str, List[str]] = None
    position_wall: Union[float, MinMaxFloat,
                         List[Union[float, MinMaxFloat]]] = None
    height: Union[float, MinMaxFloat,
                  List[Union[float, MinMaxFloat]]] = None
    rotation: Union[float, MinMaxFloat,
                    List[Union[float, MinMaxFloat]]] = None
    throw_step: Union[int, MinMaxInt,
                      List[Union[int, MinMaxInt]]] = None
    throw_force: Union[float, MinMaxFloat,
                       List[Union[float, MinMaxFloat]]] = None
    projectile_shape: Union[str, List[str]] = None
    projectile_material: Union[str, List[str]] = None
    projectile_scale: Union[float, MinMaxFloat,
                            List[Union[float, MinMaxFloat]],
                            VectorFloatConfig, List[VectorFloatConfig]] = None
    projectile_labels: Union[str, List[str]] = None


@dataclass
class StructuralMovingOccluderConfig(BaseStructuralObjectsConfig):
    """
    Defines details of a structural moving occluder.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `occluder_height` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Height (Y
    scale) of the occluder wall.  Default is between .25 and 2.5.
    - `occluder_thickness` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Thickness
    (Z scale) of the occluder wall.  Default is between .02 and 0.5.
    - `occluder_width` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Width (X
    scale) of the occluder wall.  Default is between .25 and 4.
    - `origin` (string, or list of strings): Location that the occluder's pole
    will originate from.  Options are `top`, `front`, `back`, `left`, `right`.
    Default is weighted such that `top` occurs 50% of the time and the sides
    are each 12.5%.  Users can weight options by included them more than once
    in an array.  For example, the default can be represented as:
    ```
    ['top', 'top', 'top', 'top', 'front', 'back', 'left', 'right']
    ```
    - `pole_material` (string, or list of strings): Material of the occluder
    pole (cylinder)
    - `position_x` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): X
    position of the center of the occluder
    - `position_z` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Z
    position of the center of the occluder
    - `repeat_interval` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): if `repeat_movement` is true, the number of
    steps to wait before repeating the full movement.  Default is between 1
    and 20.
    - `repeat_movement` (bool, or list of bools): If true, repeat the
    occluder's full movement and rotation indefinitely, using `repeat_interval`
    as the number of steps to wait. Default: [true, false]
    - `reverse_direction` (bool, or list of bools): Reverse the rotation
    direction of a sideways wall by rotating the wall 180 degrees. Only used if
    `origin` is set to a wall and not `top`. Default: [true, false]
    - `rotation_y` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): Y rotation of a non-sideways occluder wall;
    only used if any `origin` is set to `top`.  Default is 0 to 359.
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "moving_occluders"
    - `wall_material` (string, or list of strings): Material of the occluder
    wall (cube)
    """

    wall_material: Union[str, List[str]] = None
    pole_material: Union[str, List[str]] = None
    position_x: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    position_z: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    origin: Union[str, List[str]] = None
    occluder_height: Union[float, MinMaxFloat,
                           List[Union[float, MinMaxFloat]]] = None
    occluder_width: Union[float, MinMaxFloat,
                          List[Union[float, MinMaxFloat]]] = None
    occluder_thickness: Union[float, MinMaxFloat,
                              List[Union[float, MinMaxFloat]]] = None
    repeat_movement: Union[bool, List[bool]] = None
    repeat_interval: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    reverse_direction: Union[bool, List[bool]] = None
    rotation_y: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None


@dataclass
class FloorAreaConfig(BaseStructuralObjectsConfig):
    """Defines an area of the floor of the room.  Note: Coordinates must be
    integers. Areas are always size 1x1 centered on the given X/Z coordinate.
    Adjacent areas are combined.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of areas to be used with these parameters
    - `position_x` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): X position of the area.
    - `position_z` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): Z position of the area.
    """
    position_x: Union[int, MinMaxInt,
                      List[Union[int, MinMaxInt]]] = None
    position_z: Union[int, MinMaxInt,
                      List[Union[int, MinMaxInt]]] = None


@dataclass
class FloorMaterialConfig(FloorAreaConfig):
    """Defines details of a specific material on a specific location of the
    floor.  Be careful if num is greater than 1, be sure there are
    possibilities such that enough floor areas can be generated.
    Note: Coordinates must be integers. Areas are always size 1x1 centered on
    the given X/Z coordinate. Adjacent areas are combined.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of areas to be used with these parameters
    - `material` (string, or list of strings): The floor's material or
    material type.
    - `position_x` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): X position of the area.
    - `position_z` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): Z position of the area.
    """
    material: Union[str, List[str]] = None


@dataclass
class StructuralOccludingWallConfig(PositionableStructuralObjectsConfig):
    """
     - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of walls to be created with these parameters
    - `keyword_location`: ([KeywordLocationConfig](#KeywordLocationConfig)):
    Used to identify one of the qualitative locations specified by keywords.
    This field should not be set when `position` or `rotation` are also set.
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "occluding_walls"
    - `material` (string, or list of strings): The wall's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The wall's position in the scene.  Will be
    overrided by keyword location.
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The wall's rotation in the scene.
    Will be overrided by keyword location.
    - `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Scale of the wall.  Default is scaled to
    target size.  This will override the scale provided by the `type` field.
    - `type` (string, or list of strings): describes the type of occluding
    wall. Types include:
      `occludes` - occludes the target or object.
      `short` - wide enough, but not tall enough to occlude the target.
      `thin` - tall enough, but not wide enough to occlude the target.
      `hole` - wall with a hole that reveals the target.
    Default: ['occludes', 'occludes', 'occludes', 'short', 'thin', 'hole']
    """
    type: Union[str, List[str]] = None
    scale: Union[float, MinMaxFloat, List[Union[float, MinMaxFloat]],
                 VectorFloatConfig, List[VectorFloatConfig]] = None
    keyword_location: Union[KeywordLocationConfig,
                            List[KeywordLocationConfig]] = None


@dataclass
class StructuralPlacerConfig(BaseStructuralObjectsConfig):
    """Defines details for an instance of a placer (cylinder) descending from the
    ceiling on the given activation step to place an object with the given
    position.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of areas to be used with these parameters
    - `activation_step`: (int, or list of ints, or [MinMaxInt](#MinMaxInt)
    dict): Step on which placer should begin downward movement. Default:
    between 0 and 10
    - `end_height`: (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict): Height at which the placer should release its held object. Default:
    0 (so the held object is in contact with the floor)
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "placers"
    - `placed_object_labels` (string, or list of strings): A label for an
    existing object in your configuration that will be used as this device's
    placed object, or new label(s) to associate with a new placed object.
    Other configuration options may use this label to reference this object or
    a group of objects. Labels are not unique, and when multiple objects share
    labels, the ILE may choose one available object or all of them, depending
    on the specific option. The ILE will ignore any objects that have keyword
    locations or are used by other droppers/placers/throwers.
    - `placed_object_material` (string, or list of strings): The material
    (color/texture) to use on the placed object in each scene. For a list, a
    new material will be randomly chosen for each scene. Default: random
    - `placed_object_position`: ([VectorFloatConfig](#VectorFloatConfig) dict,
    or list of VectorFloatConfig dicts): The placed object's position in the
    scene
    - `placed_object_rotation`: (int, or list of ints, or
    [MinMaxInt](#MinMaxInt) dict, or list of MinMaxInt dicts): The placed
    object's rotation on the y axis.
    - `placed_object_scale`: (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Placed
    object's scale.  Default is a value between 0.2 and 2.
    - `placed_object_shape` (string, or list of strings): The shape (object
    type) of the placed object. For a list, a new shape will be randomly
    chosen for each scene. Default: random
    """

    num: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = 0
    activation_step: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    end_height: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    placed_object_position: Union[VectorFloatConfig,
                                  List[VectorFloatConfig]] = None
    placed_object_scale: Union[float, MinMaxFloat,
                               VectorFloatConfig,
                               List[Union[float, MinMaxFloat,
                                          VectorFloatConfig]]] = None
    placed_object_rotation: Union[int, MinMaxInt,
                                  List[Union[int, MinMaxInt]]] = None
    placed_object_shape: Union[str, List[str]] = None
    placed_object_material: Union[str, List[str]] = None
    placed_object_labels: Union[str, List[str]] = None


@dataclass
class StructuralDoorConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural door that can be opened and closed.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "doors"
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene.
    For doors, must be 0, 90, 180, or 270
    - `wall_material` (string, or list of strings): The material for the wall
    around the door.
    - `wall_scale_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale of the walls around the door in
    the x direction.  Default: A random value between 2 and the size of the
    room in the direction parallel with the door and wall.
    - `wall_scale_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale of the walls around the door in
    the y direction.  The door will be 2 units high, so this scale must be
    greater than 2 for the top wall to appear.  Default: A random value between
    2 and the height of the room.
    """
    wall_material: Union[str, List[str]] = None
    wall_scale_x: Union[float, MinMaxFloat,
                        List[Union[float, MinMaxFloat]]] = None
    wall_scale_y: Union[float, MinMaxFloat,
                        List[Union[float, MinMaxFloat]]] = None


# TODO MCS-1206 Move into the interactable object component
@dataclass
class ToolConfig(BaseStructuralObjectsConfig):
    """
    Defines details of a tool object.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "platforms"
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `shape` (string, or list of strings): The shape (object type) of this
    object in each scene. For a list, a new shape will be randomly chosen for
    each scene. Must be a valid [tool shape](#Lists). Default: random
    - `guide_rails` (bool, or list of bools): If True, guide rails will be
    generated to guide the tool in the direction it is oriented.  If a target
    exists, the guide rails will extend to the target.  Default: random
    """
    position: Union[VectorFloatConfig, List[VectorFloatConfig]] = None
    rotation_y: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    shape: Union[str, List[str]] = None
    guide_rails: Union[bool, List[bool]] = False


DEFAULT_TEMPLATE_DROPPER = StructuralDropperConfig(
    num=0,
    drop_step=MinMaxInt(0, 10),
    projectile_shape=ALL_THROWABLE_SHAPES
)

DEFAULT_TEMPLATE_THROWER = StructuralThrowerConfig(
    num=0,
    wall=[
        WallSide.FRONT.value,
        WallSide.BACK.value,
        WallSide.LEFT.value,
        WallSide.RIGHT.value],
    throw_step=MinMaxInt(0, 10),
    throw_force=MinMaxInt(500, 1000),
    rotation=MinMaxInt(0, 15),
    projectile_shape=ALL_THROWABLE_SHAPES
)

DEFAULT_TEMPLATE_MOVING_OCCLUDER = StructuralMovingOccluderConfig(
    num=0,
    origin=['top', 'top', 'top', 'top',
            'right', 'left', 'front', 'back'],
    reverse_direction=[True, False],
    occluder_height=MinMaxFloat(
        DEFAULT_MOVING_OCCLUDER_HEIGHT_MIN,
        DEFAULT_MOVING_OCCLUDER_HEIGHT_MAX),
    occluder_thickness=MinMaxFloat(
        DEFAULT_MOVING_OCCLUDER_THICKNESS_MIN,
        DEFAULT_MOVING_OCCLUDER_THICKNESS_MAX),
    occluder_width=MinMaxFloat(
        DEFAULT_MOVING_OCCLUDER_WIDTH_MIN,
        DEFAULT_MOVING_OCCLUDER_WIDTH_MAX),
    rotation_y=MinMaxFloat(
        DEFAULT_OCCLUDER_ROTATION_MIN, DEFAULT_OCCLUDER_ROTATION_MAX),
    repeat_movement=[True, False],
    repeat_interval=MinMaxInt(DEFAULT_MOVING_OCCLUDER_REPEAT_MIN,
                              DEFAULT_MOVING_OCCLUDER_REPEAT_MAX))
DEFAULT_TEMPLATE_PLATFORM = StructuralPlatformConfig(
    num=0,
    lips=StructuralPlatformLipsConfig(False, False, False, False),
    position=VectorFloatConfig(None, None, None),
    scale=MinMaxFloat(PLATFORM_SCALE_MIN, PLATFORM_SCALE_MAX),
    attached_ramps=0, platform_underneath=False,
    platform_underneath_attached_ramps=0)
DEFAULT_TEMPLATE_WALL = StructuralWallConfig(
    num=0, position=VectorFloatConfig(None, None, None))
DEFAULT_TEMPLATE_RAMP = StructuralRampConfig(
    num=0, position=VectorFloatConfig(None, None, None),
    angle=MinMaxFloat(RAMP_ANGLE_MIN, RAMP_ANGLE_MAX))
DEFAULT_TEMPLATE_L_OCCLUDER = StructuralLOccluderConfig(
    num=0, position=VectorFloatConfig(None, None, None),
    scale_front_x=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX),
    scale_front_z=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX),
    scale_side_x=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX),
    scale_side_z=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX),
    scale_y=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX),
    backwards=[True, False])

DEFAULT_TEMPLATE_HOLES_LAVA = FloorAreaConfig(0)

DEFAULT_TEMPLATE_FLOOR_MATERIALS = FloorMaterialConfig(0)

DEFAULT_OCCLUDING_WALL = StructuralOccludingWallConfig(
    num=0,
    type=['occludes', 'occludes', 'occludes', 'short', 'thin', 'hole'],
    keyword_location=None,
    scale=None, rotation_y=MinMaxFloat(
        DEFAULT_OCCLUDER_ROTATION_MIN, DEFAULT_OCCLUDER_ROTATION_MAX),
    material=[mat[0] for mat in materials.WALL_MATERIALS],
    position=VectorFloatConfig(None, None, None))


DEFAULT_TEMPLATE_PLACER = StructuralPlacerConfig(
    0,
    placed_object_position=None,
    placed_object_rotation=MinMaxInt(0, 359),
    placed_object_scale=DEFAULT_PROJECTILE_SCALE,
    placed_object_shape=ALL_THROWABLE_SHAPES,
    activation_step=MinMaxInt(0, 10),
    end_height=0)

DOOR_MATERIAL_RESTRICTIONS = [mat[0] for mat in (materials.METAL_MATERIALS +
                                                 materials.PLASTIC_MATERIALS +
                                                 materials.WOOD_MATERIALS)]

DEFAULT_TEMPLATE_DOOR = StructuralDoorConfig(
    num=0, position=VectorFloatConfig(None, None, None),
    rotation_y=[0, 90, 180, 270],
    material=DOOR_MATERIAL_RESTRICTIONS,
    wall_material=materials.WALL_MATERIALS,
    wall_scale_x=None, wall_scale_y=None)

DEFAULT_TEMPLATE_TOOL = ToolConfig(
    num=0, position=VectorFloatConfig(None, None, None),
    rotation_y=MinMaxInt(0, 359),
    shape=ALL_LARGE_BLOCK_TOOLS.copy()
)


def add_structural_object_with_retries_or_throw(
        scene: dict, bounds: List[ObjectBounds], retries: int, template,
        structural_type: StructuralTypes):
    """Attempts to take a scene and a bounds and add an structural object of a
    given type.  If a template is provided, then the template will be used for
    the values provided.

    If there are more attempts than retries without success, an ILEException
    will be thrown.
    """
    template_str = vars(template) if template else "None"
    logger.trace(
        f"Attempting to create "
        f"{structural_type.name.lower().replace('_', ' ')} from template: "
        f"{template_str}"
    )
    if structural_type in [
            StructuralTypes.WALLS, StructuralTypes.L_OCCLUDERS,
            StructuralTypes.PLATFORMS, StructuralTypes.RAMPS]:
        _add_ramp_platform_occluder_wall(
            scene, bounds, retries, template, structural_type)
    elif structural_type == StructuralTypes.DROPPERS:
        _add_dropper(scene,
                     bounds,
                     retries,
                     template)
    elif structural_type == StructuralTypes.THROWERS:
        _add_thrower(scene,
                     bounds,
                     retries,
                     template)
    elif structural_type == StructuralTypes.MOVING_OCCLUDERS:
        _add_moving_occluder(scene, bounds, retries, template)
    elif (
        structural_type == StructuralTypes.HOLES or
        structural_type == StructuralTypes.LAVA
    ):
        performer_start_position = scene['performerStart']['position']
        _add_holes_or_lava_with_retries_or_throw(
            (scene['roomDimensions']['x'], scene['roomDimensions']['z']),
            (performer_start_position['x'], performer_start_position['z']),
            template,
            scene['holes'] if structural_type == StructuralTypes.HOLES else
            scene['lava'],
            bounds,
            'holes' if structural_type == StructuralTypes.HOLES else 'lava'
        )
    elif structural_type == StructuralTypes.FLOOR_MATERIALS:
        _add_floor_material_loc_with_retries_or_throw(
            (scene['roomDimensions']['x'], scene['roomDimensions']['z']),
            template,
            scene['floorTextures']
        )
    elif structural_type == StructuralTypes.OCCLUDING_WALLS:
        _add_occluding_wall(scene, bounds, retries, template)
    elif structural_type == StructuralTypes.PLACERS:
        _add_placer(scene, bounds, retries, template)
    elif structural_type == StructuralTypes.DOORS:
        _add_door_with_retries_or_throw(scene, bounds, retries, template)
    elif structural_type == StructuralTypes.TOOLS:
        _add_tool_with_retries_or_throw(scene, bounds, retries, template)


def _get_structural_object(
    structural_type: StructuralTypes,
    scene: Dict[str, Any],
    source_template=None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Creates a structural object of the given type using any available
    parameters from the template if provided"""
    room_dim = scene.get('roomDimensions', {})
    def_dim = geometry.DEFAULT_ROOM_DIMENSIONS
    room_width = room_dim.get('x', def_dim['x'])
    room_length = room_dim.get('z', def_dim['y'])
    room_height = room_dim.get('y', def_dim['z'])
    min_room_dim = min(room_width, room_length)
    max_room_dim = max(room_width, room_length)
    templates = {
        StructuralTypes.PLATFORMS: DEFAULT_TEMPLATE_PLATFORM,
        StructuralTypes.WALLS: DEFAULT_TEMPLATE_WALL,
        StructuralTypes.RAMPS: DEFAULT_TEMPLATE_RAMP,
        StructuralTypes.L_OCCLUDERS: DEFAULT_TEMPLATE_L_OCCLUDER}
    def_temp = templates[structural_type]
    template = reconcile_template(def_temp, source_template)
    x = (
        MinMaxFloat(-room_width / 2.0, room_width / 2.0).convert_value()
        if template.position.x is None else template.position.x
    )
    z = (
        MinMaxFloat(-room_length / 2.0, room_length / 2.0).convert_value()
        if template.position.z is None else template.position.z
    )
    rot = (geometry.random_rotation()
           if template.rotation_y is None else template.rotation_y)
    mat = (
        choose_material_tuple_from_material(template.material)
        if template.material else
        random.choice(random.choice(materials.CEILING_AND_WALL_GROUPINGS))
    )
    args = {
        'position_x': x,
        'position_z': z,
        'rotation_y': rot,
        'material_tuple': mat
    }

    if template.position.y == 0 and template.platform_underneath:
        # this assumes we never want to put these structures in holes
        raise ILEException("Cannot put platform underneith structural "
                           "object with y position less than 0")

    plat_under = getattr(template, 'platform_underneath', None)

    if template.position.y is None:
        if plat_under:
            # what should the default be?
            template.position.y = MinMaxFloat(
                TOP_PLATFORM_POSITION_MIN,
                room_height - geometry.PERFORMER_HEIGHT).convert_value()
        else:
            template.position.y = 0

    if template.position.y:
        args['position_y_modifier'] = template.position.y

    if structural_type == StructuralTypes.WALLS:
        _setup_wall_args(template, room_height, max_room_dim, args)
        logger.trace(f'Creating interior wall:\nINPUT = {args}')
        new_obj, reconciled_template = structures.create_interior_wall(
            **args), template
    if structural_type == StructuralTypes.PLATFORMS:
        _setup_platform_args(template, room_height, args)
        logger.trace(f'Creating platform:\nINPUT = {args}')
        new_obj, reconciled_template = structures.create_platform(
            **args), template
    if structural_type == StructuralTypes.RAMPS:
        _setup_ramp_args(template, min_room_dim, room_height, args)
        logger.trace(f'Creating ramp:\nINPUT = {args}')
        new_obj, reconciled_template = structures.create_ramp(**args), template
    if structural_type == StructuralTypes.L_OCCLUDERS:
        _setup_l_occluder_args(template, room_height, args)
        logger.trace(f'Creating l occluder:\nINPUT = {args}')
        new_obj, reconciled_template = structures.create_l_occluder(
            **args), template
    add_random_placement_tag(new_obj, source_template)
    new_objs = new_obj if isinstance(new_obj, list) else [new_obj]
    for obj in new_objs:
        extra_labels = (
            source_template.labels
            if source_template and source_template.labels
            else [])
        extra_labels = extra_labels if isinstance(
            extra_labels, list) else [extra_labels]
        obj['debug']['labels'] = (
            [structural_type.name.lower()] + (extra_labels))
    if plat_under or getattr(
            template, 'attached_ramps', None):
        # if we ever try to attach to l_occluders, this won't work
        new_obj = _add_platform_attached_objects(scene, template, new_obj)
    return new_obj, reconciled_template


def _add_platform_attached_objects(
        scene,
        orig_template: Union[StructuralPlatformConfig,
                             StructuralRampConfig],
        obj: dict):
    # Ideally, we've position everything and then rotate everything around a
    # single axis.  Doing this is harder with some of the utlity functions
    # available and can limit retries since objects may be moved outside the
    # room late.  Therefore, we create and place each additional object and
    # then rotate it around the original objects position.  To create some
    # objects, we need information from objects from a pre-rotation state.
    # We simply return and store these states when needed.

    # bounds to test ramps to make sure they don't hit each other.  We'll
    # check all objects against all other objects when finished.
    local_bounds = []
    objs = [obj]
    new_platform = None
    top_pos = rotation_point = obj['shows'][0]['position']
    top_scale = obj['shows'][0]['scale']
    mat = obj['materials'][0]
    rotation_y = obj['shows'][0]['rotation']['y']
    below_pre_rot_pos = None

    if getattr(orig_template, 'platform_underneath', None):
        new_platform, below_pre_rot_pos = _add_platform_below(
            scene, obj, rotation_point, orig_template)
        objs += [new_platform]
        below_scale = new_platform['shows'][0]['scale']
    if getattr(orig_template, 'attached_ramps', None):
        # These values are just large to tell the system they have
        # essentially unlimited space for ramps when we don't know.
        # We can't determine exactly how much space when the base flooring
        # isn't rotated the same (I.E. the floor)
        available_lengths = DEFAULT_AVAIABLE_LENGTHS
        if below_pre_rot_pos:
            available_lengths = _get_space_around_platform(
                top_pos=top_pos,
                top_scale=top_scale,
                bottom_pos=below_pre_rot_pos,
                bottom_scale=below_scale)

        # Attach ramps
        gaps = []
        for i in range(orig_template.attached_ramps):
            logger.trace(
                f"Attempting to attach ramp {i}/"
                f"{orig_template.attached_ramps} to platform.")
            gap = _add_valid_ramp_with_retries(
                scene, objs, bounds=local_bounds,
                pre_rot_pos=top_pos,
                scale=top_scale,
                rotation_y=rotation_y,
                rotation_point=rotation_point,
                material=mat,
                max_angle=45,
                available_lengths=available_lengths)
            gaps.append(gap)
        _add_gaps_to_object(gaps, obj)

    if getattr(orig_template, 'platform_underneath_attached_ramps',
               None) and new_platform:
        gaps = []
        for i in range(orig_template.platform_underneath_attached_ramps):
            logger.trace(
                f"Attempting to attach ramp {i}/"
                f"{orig_template.platform_underneath_attached_ramps} to "
                f"underneath platform.")
            new_mat = new_platform['materials'][0]
            gap = _add_valid_ramp_with_retries(
                scene, objs, bounds=local_bounds,
                pre_rot_pos=below_pre_rot_pos,
                scale=below_scale,
                rotation_y=rotation_y,
                rotation_point=rotation_point,
                material=new_mat,
                max_angle=45,
                available_lengths=DEFAULT_AVAIABLE_LENGTHS)
            gaps.append(gap)
        _add_gaps_to_object(gaps, new_platform)
    return objs


def _add_gaps_to_object(gaps_list, obj):
    all_gaps = {}
    lips_cfg = obj['lips']
    for gap in gaps_list:
        side = gap['side']
        if not lips_cfg[side]:
            continue
        gaps = all_gaps.get(side, [])
        gap = copy.deepcopy(gap)
        gap.pop('side')
        gaps.append(gap)
        gaps = sorted(gaps, key=lambda item: item['low'])
        all_gaps[side] = gaps
    if all_gaps:
        obj['lips']['gaps'] = all_gaps


def _add_platform_below(scene, obj, rotation_point, top_template):
    show = obj['shows'][0]
    scale = show['scale']
    pos = show['position']
    min_y = show['boundingBox'].min_y
    for _ in range(MAX_TRIES):
        # some assumptions:
        # rotation between platforms is fixed

        max_room_dim = max(
            scene['roomDimensions']['x'],
            scene['roomDimensions']['z'])
        x0, z0, scale_x, scale_z = _get_under_platform_position_scale(
            scale, pos, max_room_dim)

        # rotation around arbitrary center is:
        # x1 = (x0 -xc) cos(theta) - (z0 -zc)sin(theta) + xc
        # z1 = (x0 -xc) sin(theat) + (z0 -zc)cos(theta) + zc
        # rotate position around obj position
        r_point_x = rotation_point['x']
        r_point_z = rotation_point['z']
        radians = math.radians(obj['shows'][0]['rotation']['y'])
        x = (x0 - r_point_x) * math.cos(radians) - \
            (z0 - r_point_z) * math.sin(radians) + r_point_x
        z = -(x0 - r_point_x) * math.sin(radians) - \
            (z0 - r_point_z) * math.cos(radians) + r_point_z

        new_template = StructuralPlatformConfig(
            num=1,
            position=VectorFloatConfig(x, 0, z),
            rotation_y=show['rotation']['y'],
            scale=VectorFloatConfig(
                scale_x,
                min_y,
                scale_z),
            lips=top_template.lips,
            labels=top_template.labels)
        new_platform, _ = _get_structural_object(
            StructuralTypes.PLATFORMS, scene, new_template)
        new_platform['debug']['random_position'] = True
        return new_platform, {'x': x0, 'y': min_y * 0.5, 'z': z0}

    raise ILEException("Failed to add platform under existing platform.")


def _get_under_platform_position_scale(top_scale, top_position, max_room_dim):
    # How do we want to determine the position and scale of the platform below?
    # This has a range which is determined based on the top objects scale.
    # We then choose a random position where the top object entirely fits on
    # the bottom platform.

    # top_scale['y'] is the ramp length at 45 degrees (max angle)
    scale_min_buffer = max(
        top_scale['y'] +
        BOTTOM_PLATFORM_SCALE_BUFFER_MIN,
        top_scale['y'] * 2)
    scale_max_buffer = min(
        max_room_dim - geometry.PERFORMER_WIDTH -
        min(top_scale['x'], top_scale['z']),
        top_scale['y'] +
        BOTTOM_PLATFORM_SCALE_BUFFER_MAX)
    scale_x = MinMaxFloat(
        # Note: top_scale
        top_scale['x'] + scale_min_buffer,
        top_scale['x'] + scale_max_buffer
    ).convert_value()
    scale_z = MinMaxFloat(
        top_scale['z'] + scale_min_buffer,
        top_scale['z'] + scale_max_buffer
    ).convert_value()

    top_pos_x = _get_pre_rotate_under_position(
        top_scale, top_position, scale_x, 'x')
    top_pos_z = _get_pre_rotate_under_position(
        top_scale, top_position, scale_z, 'z')

    return top_pos_x, top_pos_z, scale_x, scale_z


def _get_pre_rotate_under_position(
        top_scale, top_position, bot_scale, key):
    """determine the range of positions in one dimension for a platform under
    another platform or ramp to ensure the top (original) object is
    entirely contained in the bottom in this one dimension.
    """
    pos_min = top_position[key] + top_scale[key] * 0.5 - bot_scale * 0.5
    pos_max = top_position[key] - top_scale[key] * 0.5 + bot_scale * 0.5
    return random.uniform(pos_min, pos_max)


def _add_valid_ramp_with_retries(
        scene, objs, bounds,
        pre_rot_pos, scale, rotation_y,
        rotation_point, material,
        max_angle, available_lengths):
    """ Returns gap location"""
    for i in range(MAX_TRIES):
        logger.trace(f"attempting to find ramp, try #{i}")
        ramp, gap = _get_attached_ramp(
            scene,
            pre_rot_pos=pre_rot_pos, scale=scale,
            rotation_y=rotation_y,
            rotation_point=rotation_point,
            material=material,
            available_lengths=available_lengths,
            max_angle=max_angle)
        if _validate_all_locations_and_update_bounds(
                [ramp], scene, bounds):
            objs.append(ramp)
            return gap
    raise ILEException("Unable to find valid location to attach ramp to "
                       "platform.  This is usually due too many ramps for the"
                       "amount of space.")


def _get_attached_ramp(scene: dict, pre_rot_pos: dict, scale: dict,
                       rotation_y, rotation_point, material, available_lengths,
                       max_angle=89,
                       ):
    ppx = pre_rot_pos['x']
    ppy = pre_rot_pos['y']
    ppz = pre_rot_pos['z']
    psx = scale['x']
    psy = scale['y']
    psz = scale['z']

    r_point_x = rotation_point['x']
    r_point_z = rotation_point['z']

    performer_buffer = geometry.PERFORMER_HALF_WIDTH * 2
    # then randomize which edge we choose first
    edge_choices = [0, 1, 2, 3]
    random.shuffle(edge_choices)

    # get how much room we have for a ramp in this edge if on top of
    # another platform
    # default to a high number.  Ignore the space check if platform is on
    # floor.

    valid_edge = False
    # verify there is enough space for a ramp
    for edge in edge_choices:
        max_ramp_length = min(
            available_lengths[edge] -
            performer_buffer,
            ATTACHED_RAMP_MAX_LENGTH)
        min_ramp_length = psy / math.tan(math.radians(max_angle))
        min_ramp_length = max(min_ramp_length, ATTACHED_RAMP_MIN_LENGTH)
        # what angle do we need to get to the necessary height given the max
        # length.
        angle_needed = math.degrees(math.atan(psy / (max_ramp_length)))
        # make sure ramp isn't wider than platform
        ramp_width_max = min(
            ATTACHED_RAMP_MAX_WIDTH,
            psz if edge %
            2 == 0 else psx)
        if (angle_needed <= max_angle and angle_needed >=
                0 and max_ramp_length > min_ramp_length and
                ramp_width_max >= ATTACHED_RAMP_MIN_WIDTH):
            scale = VectorFloatConfig(
                MinMaxFloat(ATTACHED_RAMP_MIN_WIDTH, ramp_width_max),
                psy,
                MinMaxFloat(min_ramp_length, max_ramp_length))
            scale = choose_random(scale)
            valid_edge = True
            break

    if not valid_edge:
        raise ILEException(
            f"Unable to add ramp to given platform with angle less than "
            f"{max_angle}")

    rsx = scale.x
    rsz = scale.z
    rot = rotation_y

    # need to rotate ramps when all is done so they go from the platform down.
    rot_add = RAMP_ROTATIONS[edge]

    rpy = ppy - 0.5 * psy

    length = rsz
    r_angle = math.degrees(math.atan(psy / rsz))

    # determing the position of the ramp is somewhat complicated.
    # The steps are:
    #  Determine position as if there is no rotation.
    #  Rotate the position around the center (position) of the platform

    # x limit when x of ramp is outside the platform relative to platform
    # origin
    x_limit_out = psx * 0.5 + 0.5 * rsz
    # x limit when x of ramp is inside the platform relative to platform origin
    x_limit_in = psx * 0.5 - 0.5 * rsx
    # same with z
    z_limit_out = psz * 0.5 + 0.5 * rsz
    z_limit_in = psz * 0.5 - 0.5 * rsx

    # position ranges as if platform has no rotation.  Each
    # index corresponds to one edge of the platform.
    non_rot_x_min = [-x_limit_out, -x_limit_in, x_limit_out, -x_limit_in]
    non_rot_x_max = [-x_limit_out, x_limit_in, x_limit_out, x_limit_in]
    non_rot_z_min = [-z_limit_in, -z_limit_out, -z_limit_in, z_limit_out]
    non_rot_z_max = [z_limit_in, -z_limit_out, z_limit_in, z_limit_out]

    # rotation around arbitrary center is:
    # x1 = (x0 -xc) cos(theta) - (z0 -zc)sin(theta) + xc
    # z1 = (x0 -xc) sin(theat) + (z0 -zc)cos(theta) + zc
    rel_x0 = random.uniform(non_rot_x_min[edge], non_rot_x_max[edge])
    rel_z0 = random.uniform(non_rot_z_min[edge], non_rot_z_max[edge])

    if edge % 2 == 0:
        # on left or right, we need to determine range in z
        # ramp width is always x so always use rsx
        gap = _get_lip_gap(rel_z0, rsx, ppz, psz, edge)
    else:
        # on front or back, we need to determine range in x
        gap = _get_lip_gap(rel_x0, rsx, ppx, psx, edge)

    x0 = rel_x0 + ppx
    z0 = rel_z0 + ppz

    radians = math.radians(rot)
    rpx = (x0 - r_point_x) * math.cos(radians) - \
        (z0 - r_point_z) * math.sin(radians) + r_point_x
    rpz = -(x0 - r_point_x) * math.sin(radians) - \
        (z0 - r_point_z) * math.cos(radians) + r_point_z

    pos = VectorFloatConfig(rpx, rpy, rpz)

    rot = (rot + rot_add) % 360
    new_template = StructuralRampConfig(
        num=1, position=pos, rotation_y=rot, angle=r_angle,
        length=length, width=rsx, material=material)
    new_ramp, _ = _get_structural_object(
        StructuralTypes.RAMPS, scene, new_template)
    new_ramp['debug']['random_position'] = True
    return new_ramp, gap


def _get_lip_gap(ramp_pos, ramp_scale, plat_pos, plat_scale, edge):
    # ramp_pos is relative to the platform.  To get the actual position, we
    # would add plat_pos as we do in the function where this is called.
    # However that should get factored out so we don't need it.
    # edge 0 = -x left, 1=-z back, 2=+x right, 3=+z front
    gap = {'side': ['left', 'back', 'right', 'front'][edge]}
    gap['high'] = (ramp_pos + ramp_scale * 0.5 +
                   plat_scale * 0.5) / plat_scale
    gap['low'] = (ramp_pos - ramp_scale * 0.5 + plat_scale * 0.5) / plat_scale
    # I'm not sure why I need to reverse the direction here.
    if edge % 2 == 0:
        temp = 1 - gap['high']
        gap['high'] = 1 - gap['low']
        gap['low'] = temp
    return gap


def _get_space_around_platform(
        top_pos: dict, top_scale: dict, bottom_pos: dict, bottom_scale: dict):
    """All values must be pre-rotation and both objects must have the same
    rotation applied.
    """
    # delta pos
    dposx = bottom_pos['x'] - top_pos['x']
    dposz = bottom_pos['z'] - top_pos['z']
    # delta scale
    dscalex = bottom_scale['x'] - top_scale['x']
    dscalez = bottom_scale['z'] - top_scale['z']

    x_positive = dposx + dscalex / 2
    x_negative = -dposx + dscalex / 2

    z_positive = dposz + dscalez / 2
    z_negative = -dposz + dscalez / 2
    logger.debug(f" Area around platform for ramps: "
                 f"{[x_negative, z_negative, x_positive, z_positive]}")
    return [x_negative, z_negative, x_positive, z_positive]


def _setup_wall_args(template: StructuralWallConfig, room_height: int,
                     max_room_dim: int, args: dict):
    """Applies extra arguments needed for a wall from the template if
    available."""
    width = MinMaxFloat(
        max_room_dim * WALL_WIDTH_PERCENT_MIN,
        max_room_dim * WALL_WIDTH_PERCENT_MAX)
    args['width'] = getattr(template, 'width', None) or width.convert_value()
    # Wall height always equals room height.
    args['height'] = room_height
    # Wall rotation should not be diagonal unless specifically configured so.
    args['rotation_y'] = (
        random.choice([0, 90, 180, 270]) if template.rotation_y is None else
        template.rotation_y
    )


def _setup_l_occluder_args(
    template: StructuralLOccluderConfig,
    room_height: float,
    args: dict
) -> None:
    """Applies extra arguments needed for an l occluder from the template if
    available."""
    args['flip'] = template.backwards
    args['scale_front_x'] = template.scale_front_x
    args['scale_front_z'] = template.scale_front_z
    args['scale_side_x'] = template.scale_side_x
    args['scale_side_z'] = template.scale_side_z
    # Restrict max height to room height.
    args['scale_y'] = min(template.scale_y, room_height)


def _setup_ramp_args(
    template: StructuralRampConfig,
    min_room_dim: float,
    room_height: float,
    args: dict
) -> None:
    """Applies extra arguments needed for a ramp from the template if
    available."""
    ramp_angle = template.angle
    # Find the ramp's maximum possible length using the ramp's angle and the
    # room's height.
    max_length = (
        (room_height - geometry.PERFORMER_HEIGHT) /
        math.tan(math.radians(ramp_angle))
    )
    ramp_width = getattr(template, 'width', None) or MinMaxFloat(
        min_room_dim * RAMP_WIDTH_PERCENT_MIN,
        min_room_dim * RAMP_WIDTH_PERCENT_MAX
    ).convert_value()
    ramp_length = getattr(template, 'length', None) or MinMaxFloat(
        min_room_dim * RAMP_LENGTH_PERCENT_MIN,
        min(min_room_dim * RAMP_LENGTH_PERCENT_MAX, max_length)
    ).convert_value()
    args['angle'] = ramp_angle
    args['width'] = ramp_width
    # If the ramp's length was configured, restrict it to the max length.
    args['length'] = min(ramp_length, max_length)


def _setup_platform_args(
    template: StructuralPlatformConfig,
    room_height: float,
    args: dict
) -> None:
    """Applies extra arguments needed for a platform from the template if
    available."""
    args['lips'] = template.lips
    if isinstance(template.scale, Vector3d):
        args['scale_x'] = template.scale.x
        # Restrict max height to room height.
        args['scale_y'] = min(template.scale.y, room_height)
        args['scale_z'] = template.scale.z
    else:
        args['scale_x'] = template.scale
        # Restrict max height to room height.
        args['scale_y'] = min(template.scale, room_height)
        args['scale_z'] = template.scale


def _validate_all_locations_and_update_bounds(
    objects: Union[list, dict],
    scene: Dict[str, Any],
    bounds: List[ObjectBounds]
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


def _add_holes_or_lava_with_retries_or_throw(
    room_dimensions: Tuple[float, float],
    performer_start: Tuple[float, float],
    src_template: FloorAreaConfig,
    existing: List[Dict[str, float]],
    bounds: List[ObjectBounds],
    label: str
) -> None:
    xmax = math.floor(room_dimensions[0] / 2)
    zmax = math.floor(room_dimensions[1] / 2)
    default_template = DEFAULT_TEMPLATE_HOLES_LAVA
    errors = set({})
    perf_x = performer_start[0]
    perf_z = performer_start[1]
    perf_x = round(perf_x)
    perf_z = round(perf_z)
    restrict_under_user = (
        src_template is None or src_template.position_x is None or
        src_template.position_z is None)

    for _ in range(MAX_TRIES):
        error, floor_loc, template = _get_floor_location(
            src_template, xmax, zmax, default_template)
        if (restrict_under_user and
                floor_loc['x'] == perf_x and floor_loc['z'] == perf_z):
            error = ("Random location of {label} put under performer start at"
                     f" ({perf_x}, {perf_z}). ")
        if error is None:
            if floor_loc not in existing:
                existing.append(floor_loc)
                bounds.append(geometry.generate_floor_area_bounds(
                    floor_loc['x'],
                    floor_loc['z']
                ))
                log_structural_template_object(
                    label,
                    label,
                    existing[-1],
                    [src_template, template]
                )
                return
            else:
                errors.add("Unable to find valid location. ")
        else:
            errors.add(error)
    raise ILEException(f"Failed to create {label}. Errors={''.join(errors)}")


def _get_floor_location(src_template, xmax: int,
                        zmax: int, default_template):
    error = None
    template = reconcile_template(default_template, src_template)
    x = template.position_x
    x = x if x is not None else random.randint(-xmax, xmax)
    z = template.position_z
    z = z if z is not None else random.randint(-zmax, zmax)
    if x < -xmax or x > xmax:
        error = f"x location of hole is out of bounds x={x}. "
    if z < -zmax or z > zmax:
        error = f"z location of hole is out of bounds z={z}. "
    floor_loc = {'x': x, 'z': z}
    return error, floor_loc, template


def _add_floor_material_loc_with_retries_or_throw(
    room_dimensions: Tuple[float, float],
    src_template: FloorMaterialConfig,
    existing: List[Dict[str, Any]]
) -> None:
    default_template = DEFAULT_TEMPLATE_FLOOR_MATERIALS
    errors = set({})
    xmax = math.floor(room_dimensions[0] / 2)
    zmax = math.floor(room_dimensions[1] / 2)
    for _ in range(MAX_TRIES):
        error, floor_loc, template = _get_floor_location(
            src_template, xmax, zmax, default_template)
        if error is None:
            mat = template.material
            mat = mat[0] if isinstance(mat, tuple) else mat
            mat = (
                choose_material_tuple_from_material(mat) if mat else
                random.choice(materials.FLOOR_MATERIALS)
            )
            valid = True
            for floor_texture in existing:
                if floor_loc in floor_texture['positions']:
                    valid = False
                    break
            if valid:
                found = False
                for floor_texture in existing:
                    if mat.material == floor_texture['material']:
                        floor_texture['positions'].append(floor_loc)
                        found = True
                        break
                if not found:
                    existing.append(
                        {'material': mat.material, 'positions': [floor_loc]}
                    )
                log_structural_template_object(
                    'floor textures',
                    mat.material,
                    floor_loc,
                    [src_template, template]
                )
                return
            else:
                errors.add("Unable to find valid location. ")
        else:
            errors.add(error)
    raise ILEException(
        f"Failed to create floor material.  Errors={''.join(errors)}")


def _add_dropper(
        scene: dict, bounds: List[ObjectBounds], retries: int,
        source_template: StructuralDropperConfig):
    buffer = DROPPER_THROWER_BUFFER
    for _ in range(retries):
        template = reconcile_template(
            DEFAULT_TEMPLATE_DROPPER,
            source_template)
        room_dim = scene['roomDimensions']
        target, exists = _get_projectile_idl(
            template,
            room_dim,
            scene['performerStart'],
            bounds
        )
        pos_x = (random.uniform(-room_dim['x'] /
                                2.0 + buffer, room_dim['x'] / 2.0 - buffer)
                 if template.position_x is None else template.position_x)
        pos_z = (random.uniform(-room_dim['z'] /
                                2.0 + buffer, room_dim['z'] / 2.0 - buffer)
                 if template.position_z is None else template.position_z)
        projectile_dimensions = vars(target.definition.dimensions)
        args = {
            'position_x': pos_x,
            'position_z': pos_z,
            'room_dimensions_y': room_dim['y'],
            'object_dimensions': projectile_dimensions,
            'last_step': scene.get('last_step'),
            'dropping_step': template.drop_step,
            'is_round': ('ball' in target.definition.shape)
        }
        logger.trace(f'Creating dropper:\nINPUT = {args}')
        obj = mechanisms.create_dropping_device(**args)
        if obj:
            bounding_box = obj['shows'][0]['boundingBox']
            valid = geometry.validate_location_rect(
                bounding_box,
                scene['performerStart']['position'],
                bounds,
                room_dim)
            if valid:
                scene['objects'].append(obj)
                _save_to_object_repository(
                    obj,
                    StructuralTypes.DROPPERS,
                    template.labels
                )
                log_structural_template_object(
                    'dropper',
                    'id',
                    obj['id'],
                    [source_template, template]
                )
                args = {
                    'instance': target.instance,
                    'dropping_device': obj,
                    'dropping_step': template.drop_step
                }
                logger.trace(f'Positioning dropper object:\nINPUT = {args}')
                mechanisms.drop_object(**args)
                if not exists:
                    scene['objects'].append(target.instance)
                    log_structural_template_object(
                        'dropper object',
                        'id',
                        target.instance['id']
                    )
                else:
                    for i in range(len(scene['objects'])):
                        if scene['objects'][i]['id'] == target.instance['id']:
                            scene['objects'][i] = target.instance
                bounds.append(bounding_box)
                return
    raise ILEException("Failed to create dropper.")


def _add_thrower(
        scene: dict, bounds: List[ObjectBounds], retries: int,
        source_template: StructuralThrowerConfig):
    for _ in range(retries):
        template = reconcile_template(
            DEFAULT_TEMPLATE_THROWER,
            source_template)
        room_dim = scene['roomDimensions']
        # Don't want to validate against the walls since the throwers
        # intentionally intersect with walls.
        room_dimensions_extended = {
            'x': room_dim['x'] + 2,
            'y': room_dim['y'],
            'z': room_dim['z'] + 2
        }
        target, exists = _get_projectile_idl(
            template,
            room_dimensions_extended,
            scene['performerStart'],
            bounds
        )
        projectile_dimensions = vars(target.definition.dimensions)
        max_scale = max(projectile_dimensions['x'], projectile_dimensions['z'])
        wall = template.wall
        pos_x, pos_y, pos_z, rot_y = _compute_thrower_position_rotation(
            room_dim, max_scale, wall, template)

        args = {
            'position_x': pos_x,
            'position_y': pos_y,
            'position_z': pos_z,
            'rotation_y': rot_y,
            'rotation_z': template.rotation,
            'object_dimensions': projectile_dimensions,
            'object_rotation_y': target.definition.rotation.y,
            'last_step': scene.get('last_step'),
            'throwing_step': template.throw_step,
            'is_round': ('ball' in target.definition.shape)
        }
        logger.trace(f'Creating thrower:\nINPUT = {args}')
        obj = mechanisms.create_throwing_device(**args)
        if obj:
            bounding_box = obj['shows'][0]['boundingBox']
            valid = geometry.validate_location_rect(
                bounding_box,
                scene['performerStart']['position'],
                bounds,
                room_dimensions_extended
            )
            if valid:
                scene['objects'].append(obj)
                _save_to_object_repository(
                    obj,
                    StructuralTypes.THROWERS,
                    template.labels
                )
                log_structural_template_object(
                    'thrower',
                    'id',
                    obj['id'],
                    [source_template, template]
                )
                force = template.throw_force
                force *= target.definition.mass
                args = {
                    'instance': target.instance,
                    'throwing_device': obj,
                    'throwing_force': force,
                    'throwing_step': template.throw_step
                }
                logger.trace(f'Positioning thrower object:\nINPUT = {args}')
                mechanisms.throw_object(**args)
                if not exists:
                    scene['objects'].append(target.instance)
                    log_structural_template_object(
                        'thrower object',
                        'id',
                        target.instance['id']
                    )
                else:
                    for i in range(len(scene['objects'])):
                        if scene['objects'][i]['id'] == target.instance['id']:
                            scene['objects'][i] = target.instance
                bounds.append(bounding_box)
                return
    raise ILEException("Failed to create thrower.")


def _add_moving_occluder(scene: dict, bounds: List[ObjectBounds], retries: int,
                         source_template: StructuralMovingOccluderConfig):
    # Moving occluders has a lot of "dependent" defaults which can't be put in
    # the default object itself.
    room_dim = scene.get(
        'roomDimensions',
        geometry.DEFAULT_ROOM_DIMENSIONS)

    for _ in range(retries):

        template = reconcile_template(
            DEFAULT_TEMPLATE_MOVING_OCCLUDER,
            source_template)
        template.wall_material = (
            choose_material_tuple_from_material(template.wall_material)
            if template.wall_material else
            random.choice(random.choice(materials.CEILING_AND_WALL_GROUPINGS))
        )
        template.pole_material = (
            choose_material_tuple_from_material(template.pole_material)
            if template.pole_material else
            random.choice(materials.METAL_MATERIALS)
        )
        max_size = max(template.occluder_thickness, template.occluder_width)
        limit_x = room_dim['x'] - max_size
        limit_z = room_dim['z'] - max_size
        template.position_x = (
            template.position_x if template.position_x is not None
            else random.uniform(-limit_x, limit_x))
        template.position_z = (
            template.position_z if template.position_z is not None
            else random.uniform(-limit_z, limit_z))

        limit_x = room_dim['x'] - max_size
        limit_z = room_dim['z'] - max_size
        template.position_x = (
            template.position_x if template.position_x is not None
            else random.uniform(-limit_x, limit_x))
        template.position_z = (
            template.position_z if template.position_z is not None
            else random.uniform(-limit_z, limit_z))
        # Disable repeat if boolean is off
        template.repeat_interval = (
            template.repeat_interval if template.repeat_movement else None)

        # Restrict max height to room height.
        template.occluder_height = min(template.occluder_height, room_dim['y'])

        obj = occluders.create_occluder(
            wall_material=template.wall_material,
            pole_material=template.pole_material,
            x_position=template.position_x,
            occluder_width=template.occluder_width,
            occluder_height=template.occluder_height,
            occluder_thickness=template.occluder_thickness,
            repeat_movement=template.repeat_interval,
            reverse_direction=template.reverse_direction,
            room_dimensions=room_dim,
            sideways_back=template.origin == OccluderOrigin.BACK,
            sideways_front=template.origin == OccluderOrigin.FRONT,
            sideways_left=template.origin == OccluderOrigin.LEFT,
            sideways_right=template.origin == OccluderOrigin.RIGHT,
            y_rotation=template.rotation_y,
            z_position=template.position_z)
        if obj:
            bb1 = _get_bounding_box_moving_occluder(obj[0])
            bb2 = obj[1]['shows'][0]['boundingBox']
            valid1 = geometry.validate_location_rect(
                bb1,
                scene['performerStart']['position'],
                bounds, room_dim
            )
            valid2 = geometry.validate_location_rect(
                bb2,
                scene['performerStart']['position'],
                bounds, room_dim
            )
            if valid1 and valid2:
                add_random_placement_tag(obj, source_template)
                obj[0]['shows'][0]['boundingBox'] = bb1
                obj[1]['shows'][0]['boundingBox'] = bb2
                scene['objects'].append(obj[0])
                scene['objects'].append(obj[1])
                bounds.append(bb1)
                bounds.append(bb2)
                _save_to_object_repository(
                    # Only save the first part of the occluder (the "wall").
                    obj[0],
                    StructuralTypes.MOVING_OCCLUDERS,
                    template.labels
                )
                log_structural_template_object(
                    'moving occluder',
                    'ids',
                    [part['id'] for part in obj],
                    [source_template, template]
                )
                return
    raise ILEException("Failed to create occluder")


def _get_occluding_wall_scale(
    template: StructuralOccludingWallConfig,
    target: InstanceDefinitionLocationTuple,
    room_height: float
) -> Vector3d:
    scale = template.scale
    dim = None
    if scale is None and target:
        try:
            # Try and fall back to definition
            temp_dim = target.instance['debug']['dimensions']
            dim = Vector3d(temp_dim['x'], temp_dim['y'], temp_dim['z'])
        except Exception:
            dim = target.definition.dimensions
        scale = Vector3d(
            max(dim.x, dim.z) * DEFAULT_OCCLUDING_WALL_WIDTH_MULTIPLIER,
            dim.y * DEFAULT_OCCLUDING_WALL_HEIGHT_MULTIPLIER,
            choose_random(DEFAULT_OCCLUDING_WALL_THICKNESS)
        )
        if template.type == OccludingWallType.THIN:
            scale.x = (min(dim.x,
                           dim.z) *
                       random.uniform(
                DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MIN,
                DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MAX))
        elif template.type == OccludingWallType.SHORT:
            scale.y = dim.y * random.uniform(
                DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MIN,
                DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MAX)
            scale.y = max(
                scale.y, DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_Y_MIN)
        elif template.type == OccludingWallType.HOLE:
            width = max(dim.x, dim.z)
            scale.x = width + OCCLUDING_WALL_WIDTH_BUFFER
            scale.y = dim.y + min(OCCLUDING_WALL_HOLE_MAX_HEIGHT, dim.y)
    elif scale:
        if isinstance(scale, (int, float)):
            scale = Vector3d(scale, scale, scale)
        if scale.x == 0:
            scale.x = choose_random(DEFAULT_OCCLUDING_WALL_WIDTH)
        if scale.y == 0:
            scale.y = choose_random(DEFAULT_OCCLUDING_WALL_HEIGHT)
        if scale.z == 0:
            scale.z = choose_random(DEFAULT_OCCLUDING_WALL_THICKNESS)
    elif scale is None:
        scale = Vector3d(
            choose_random(DEFAULT_OCCLUDING_WALL_WIDTH),
            choose_random(DEFAULT_OCCLUDING_WALL_HEIGHT),
            choose_random(DEFAULT_OCCLUDING_WALL_THICKNESS)
        )
    # Restrict max height to room height.
    scale.y = min(scale.y, room_height)
    return (scale, dim)


def _get_occluding_wall_definition(
        template: StructuralOccludingWallConfig,
        scale: Vector3d) -> ObjectDefinition:
    return ObjectDefinition(
        type='cube',
        attributes=['structure', 'kinematic'],
        color=template.material[1],
        scale=scale,
        dimensions=scale,
        materials=[template.material[0]],
        materialCategory=[],
        salientMaterials=[],
        shape=['cube'],
        size='huge'
    )


def _add_occluding_wall(scene: dict, bounds: List[ObjectBounds], retries: int,
                        source_template: StructuralOccludingWallConfig):

    obj_repo = ObjectRepository.get_instance()
    room_dim = scene.get('roomDimensions', geometry.DEFAULT_ROOM_DIMENSIONS)

    random_position = (
        source_template is None or source_template.position is None or
        not isinstance(source_template.position.x, (float, int)) or
        not isinstance(source_template.position.z, (float, int)))
    for _ in range(retries):
        target = None
        template = reconcile_template(
            DEFAULT_OCCLUDING_WALL,
            source_template)
        template.material = (
            choose_material_tuple_from_material(template.material)
            if template.material else
            random.choice(random.choice(materials.CEILING_AND_WALL_GROUPINGS))
        )

        # Add a default keyword_location using the target label if this wall
        # doesn't already have a keyword_location, and if at least one target
        # hasn't already been positioned via keyword_location.
        if (
            template.keyword_location is None and
            template.position.x is None and
            template.position.y is None and
            template.position.z is None and
            any([(not idl.instance['debug'].get('positionedBy')) for idl in (
                obj_repo.get_all_from_labeled_objects(TARGET_LABEL)
                if obj_repo.has_label(TARGET_LABEL) else []
            )])
        ):
            template.keyword_location = KeywordLocationConfig(keyword=(
                'between' if template.type == OccludingWallType.THIN else
                'occlude'
            ), relative_object_label=TARGET_LABEL)

        # For thin occluding walls, replace an 'occlude' keyword_location with
        # 'between' because using 'occlude' doesn't make sense for thin walls!
        # This also helps configuring randomly generating occluding walls.
        if (
            template.keyword_location and
            template.keyword_location.keyword == 'occlude' and
            template.type == OccludingWallType.THIN
        ):
            template.keyword_location.keyword = 'between'

        # Find the relative object to use, if any.
        if (
            template.keyword_location and
            template.keyword_location.relative_object_label
        ):
            label = template.keyword_location.relative_object_label
            target = obj_repo.get_one_from_labeled_objects(label)

        # Adjust the wall's scale using the target's dimensions, if any.
        scale, target_dimensions = _get_occluding_wall_scale(
            template,
            target,
            room_dim['y']
        )

        defn = _get_occluding_wall_definition(template, scale)
        if (template.keyword_location is not None):
            # setup keyword location
            idl = KeywordLocation.get_keyword_location_object_tuple(
                template.keyword_location, defn, scene['performerStart'],
                bounds, room_dim)
            # Intentionally adding original to bounds even if we later split it
            # up.  They will occupy the same bounding box.
            bounds.append(idl.instance['shows'][0]['boundingBox'])
            idl.instance['id'] = f"{template.type}-{idl.instance['id']}"
            _modify_for_hole_and_add(
                scene, template.type, idl.instance, target_dimensions,
                random_position)
            _save_to_object_repository(
                idl.instance,
                StructuralTypes.OCCLUDING_WALLS,
                template.labels
            )
            log_structural_template_object(
                'occluding wall',
                'id',
                idl.instance['id'],
                [source_template, template]
            )
            return
        else:
            # setup x, z location
            defn.scale = scale
            max_size = math.sqrt(math.pow(scale.x, 2) +
                                 math.pow(scale.z, 2))
            limit_x = room_dim['x'] - max_size
            limit_z = room_dim['z'] - max_size

            x = (
                MinMaxFloat(-limit_x, limit_x).convert_value()
                if template.position.x is None else template.position.x
            )
            z = (
                MinMaxFloat(-limit_z, limit_z).convert_value()
                if template.position.z is None else template.position.z
            )
            location = {
                'position': {
                    'x': x,
                    'y': scale.y / 2.0,
                    'z': z
                },
                'rotation': {
                    'x': 0,
                    'y': template.rotation_y,
                    'z': 0
                }
            }
            inst = instances.instantiate_object(defn, location)
            inst = structures.finalize_structural_object([inst])[0]
            inst['id'] = f"{template.type}-{inst['id']}"
            add_random_placement_tag(inst, source_template)
            bb = inst['shows'][0]['boundingBox']
            valid = geometry.validate_location_rect(
                bb,
                scene['performerStart']['position'],
                bounds, room_dim
            )
            if valid:
                bounds.append(bb)
                _modify_for_hole_and_add(
                    scene, template.type, inst, target_dimensions,
                    random_position)
                _save_to_object_repository(
                    inst,
                    StructuralTypes.OCCLUDING_WALLS,
                    template.labels
                )
                log_structural_template_object(
                    'occluding wall',
                    'id',
                    inst['id'],
                    [source_template, template]
                )
                return
    raise ILEException("Failed to create occluding wall")


def _modify_for_hole_and_add(
        scene, type, base, target_dimensions, random_position):
    show = base['shows'][0]
    if type == OccludingWallType.HOLE:
        # boost position by half of each section.  each section is half
        # the height
        show['position']['y'] = show['scale']['y'] / 4.0
        # copy instance and create new instances.
        l_col, r_col, top = _convert_base_occluding_wall_to_holed_wall(
            base, target_dimensions)
        walls = structures.finalize_structural_object(
            [l_col, r_col, top])

        for obj in walls:
            obj['debug']['random_position'] = random_position
        scene['objects'].append(walls[0])
        scene['objects'].append(walls[1])
        scene['objects'].append(walls[2])

    else:
        show['position']['y'] = show['scale']['y'] / 2.0
        obj = structures.finalize_structural_object([base])[0]
        obj['debug']['random_position'] = random_position
        scene['objects'].append(obj)


def _convert_base_occluding_wall_to_holed_wall(
        base: dict, target_dim: Vector3d):
    l_col = copy.deepcopy(base)
    r_col = copy.deepcopy(base)
    top = copy.deepcopy(base)

    rot = base['shows'][0]['rotation']['y']
    l_pos = l_col['shows'][0]['position']
    l_scale = l_col['shows'][0]['scale']
    r_pos = r_col['shows'][0]['position']
    r_scale = r_col['shows'][0]['scale']
    t_pos = top['shows'][0]['position']
    t_scale = top['shows'][0]['scale']

    if t_scale['y'] / 2 > OCCLUDING_WALL_HOLE_MAX_HEIGHT:
        hole_height = OCCLUDING_WALL_HOLE_MAX_HEIGHT
    else:
        hole_height = t_scale['y'] / 2

    l_scale['x'] = OCCLUDING_WALL_WIDTH_BUFFER / 2.0
    r_scale['x'] = OCCLUDING_WALL_WIDTH_BUFFER / 2.0
    l_scale['y'] = hole_height
    r_scale['y'] = hole_height
    t_scale['y'] -= hole_height
    r_pos['y'] = hole_height / 2.0
    l_pos['y'] = hole_height / 2.0
    t_pos['y'] = hole_height + (t_scale['y'] / 2.0)
    sin = math.sin(math.radians(rot))
    cos = math.cos(math.radians(rot))
    shift = t_scale['x'] - l_scale['x']
    shift /= 2.0

    l_pos['x'] -= shift * cos
    l_pos['z'] += shift * sin
    r_pos['x'] += shift * cos
    r_pos['z'] -= shift * sin

    # scale x/3, y/2, z, shifted -x/3 (note rotation)
    # scale x/3, y/2, z, shifted -x/3 (note rotation)
    # scale x, y/2, z, shifted y
    l_col['id'] = f"l_col-{l_col['id']}"
    r_col['id'] = f"r_col-{r_col['id']}"
    top['id'] = f"top-{top['id']}"
    return l_col, r_col, top


def _add_placer(scene: dict, bounds: List[ObjectBounds], retries: int,
                source_template: StructuralPlacerConfig):
    room_dim = scene.get('roomDimensions', geometry.DEFAULT_ROOM_DIMENSIONS)
    perf_start = scene.get("performerStart")
    for _ in range(retries):
        template = reconcile_template(
            DEFAULT_TEMPLATE_PLACER,
            source_template)
        labels = (source_template.placed_object_labels if source_template is
                  not None else None)
        idl = None
        if labels:
            idl = _get_existing_held_object_idl(labels)
        if idl:
            geometry.move_to_location(idl.instance, {
                'position': vars(choose_position(
                    template.placed_object_position,
                    idl.definition.dimensions.x,
                    idl.definition.dimensions.z,
                    room_dim['x'],
                    room_dim['z']
                )),
                'rotation': vars(choose_rotation(
                    VectorIntConfig(0, template.placed_object_rotation, 0)
                ))
            })
        else:
            obj_cfg = InteractableObjectConfig(
                num=1,
                position=template.placed_object_position,
                rotation=VectorIntConfig(
                    0, template.placed_object_rotation, 0),
                scale=template.placed_object_scale,
                shape=template.placed_object_shape,
                material=template.placed_object_material,
                labels=labels)

            idl = obj_cfg.create_instance_definition_location_tuple(
                room_dim, perf_start, bounds)
            idl.instance['debug']['positionedBy'] = 'mechanism'
            scene['objects'].append(idl.instance)
            bounds.append(idl.instance['shows'][0]['boundingBox'])
            log_structural_template_object(
                'placer object',
                'id',
                idl.instance['id']
            )

        start_height = room_dim['y']
        max_height = room_dim['y']
        last_step = scene.get("last_step")
        instance = idl.instance
        defn = idl.definition

        args = {
            'instance': instance,
            'activation_step': template.activation_step,
            'start_height': start_height,
            'end_height': template.end_height
        }
        logger.trace(f'Positioning placer object:\nINPUT = {args}')
        mechanisms.place_object(**args)

        args = {
            'placed_object_position': instance['shows'][0]['position'],
            'placed_object_dimensions': instance['debug']['dimensions'],
            'placed_object_offset_y': instance['debug']['positionY'],
            'activation_step': template.activation_step,
            'end_height': template.end_height,
            'max_height': max_height,
            'id_modifier': None,
            'last_step': last_step,
            'placed_object_pole_offset_y': defn.poleOffsetY
        }
        logger.trace(f'Creating placer:\nINPUT = {args}')
        obj = mechanisms.create_placer(**args)

        scene['objects'].append(obj)
        bounds.append(obj['shows'][0]['boundingBox'])
        _save_to_object_repository(
            obj,
            StructuralTypes.PLACERS,
            template.labels
        )
        log_structural_template_object(
            'placer',
            'id',
            obj['id'],
            [source_template, template]
        )
        return


def _add_door_with_retries_or_throw(
        scene: dict, bounds: List[ObjectBounds], retries: int,
        source_template: StructuralDoorConfig):
    room_dim = scene.get('roomDimensions', {})
    def_dim = geometry.DEFAULT_ROOM_DIMENSIONS
    room_width = room_dim.get('x', def_dim['x'])
    room_length = room_dim.get('z', def_dim['y'])

    # When getting values here, we don't want to corrupt the template so we
    # store in local values now.  This allows retries or delayed actions to
    # use the original template as intended.
    for _ in range(retries):
        template = reconcile_template(
            DEFAULT_TEMPLATE_DOOR,
            source_template)
        mat = (
            choose_material_tuple_from_material(template.material)
            if template.material else random.choice(random.choice([
                materials.METAL_MATERIALS,
                materials.PLASTIC_MATERIALS,
                materials.WOOD_MATERIALS,
            ]))
        )
        # Convert tuple back to string
        wall_mat = template.wall_material
        wall_mat = wall_mat[0] if isinstance(
            wall_mat, materials.MaterialTuple) else wall_mat
        wall_mat = (
            choose_material_tuple_from_material(wall_mat)
            if template.wall_material else random.choice(random.choice([
                materials.METAL_MATERIALS,
                materials.PLASTIC_MATERIALS,
                materials.WOOD_MATERIALS,
            ]))
        )
        x = choose_random(
            MinMaxFloat(-room_width / 2.0, room_width / 2.0)
            if template.position.x is None else template.position.x
        )
        y = 0 if template.position.y is None else template.position.y
        z = choose_random(
            MinMaxFloat(-room_length / 2.0, room_length / 2.0)
            if template.position.z is None else template.position.z
        )
        # need to determine random now
        rot = choose_random(template.rotation_y)
        default_wall_scale_x = MinMaxInt(
            ROOM_MIN_XZ,
            room_dim['x'] if rot in [0, 180] else room_dim['z']
        )
        wall_scale_x = choose_random(
            default_wall_scale_x
            if template.wall_scale_x is None else
            template.wall_scale_x)

        wall_scale_y = choose_random(
            MinMaxInt(ROOM_MIN_Y, room_dim['y'])
            if template.wall_scale_y is None else
            template.wall_scale_y)

        args = {
            'position_x': x,
            'position_y': y,
            'position_z': z,
            'rotation_y': rot,
            'material_tuple': mat,
            'wall_scale_x': wall_scale_x,
            'wall_scale_y': wall_scale_y,
            'wall_material_tuple': wall_mat

        }
        logger.trace(f'Creating door:\nINPUT = {args}')
        door_objs = structures.create_door(**args)

        if _validate_all_locations_and_update_bounds(door_objs, scene, bounds):
            for door in door_objs:
                add_random_placement_tag(door, source_template)
                scene['objects'].append(door)
            _save_to_object_repository(
                door_objs[0],
                StructuralTypes.DOORS,
                template.labels
            )
            log_structural_template_object(
                'door',
                'id',
                door_objs[0]['id'],
                [source_template, template]
            )
            return
    raise ILEException("Failed to create door")


def _add_tool_with_retries_or_throw(
        scene: dict, bounds: List[ObjectBounds], retries: int,
        source_template: ToolConfig):
    room_dim = scene.get('roomDimensions', {})
    def_dim = geometry.DEFAULT_ROOM_DIMENSIONS
    room_width = room_dim.get('x', def_dim['x'])
    room_length = room_dim.get('z', def_dim['y'])

    for _ in range(retries):
        template = reconcile_template(DEFAULT_TEMPLATE_TOOL, source_template)
        template.position.x = (
            MinMaxFloat(-room_width / 2.0, room_width / 2.0).convert_value()
            if template.position.x is None else template.position.x
        )
        template.position.z = (
            MinMaxFloat(-room_length / 2.0, room_length / 2.0).convert_value()
            if template.position.z is None else template.position.z
        )
        args = {
            'object_type': template.shape,
            'position_x': template.position.x,
            'position_z': template.position.z,
            'rotation_y': template.rotation_y
        }
        logger.trace(f'Creating tool:\nINPUT = {args}')
        obj = structures.create_tool(**args)
        if _validate_all_locations_and_update_bounds([obj], scene, bounds):
            scene['objects'].append(obj)
            _save_to_object_repository(
                obj,
                StructuralTypes.TOOLS,
                template.labels
            )
            log_structural_template_object(
                'tool',
                'id',
                obj['id'],
                [source_template, template]
            )
            return
    raise ILEException(f'Failed to create tool shape={source_template.shape}')


def _get_existing_held_object_idl(
    labels: Union[str, List[str]]
) -> Optional[InstanceDefinitionLocationTuple]:
    object_repository = ObjectRepository.get_instance()
    shuffled_labels = (
        labels if isinstance(labels, list) else [labels]
    ) if labels else []
    random.shuffle(shuffled_labels)
    idl_count = 0
    for label in shuffled_labels:
        if not object_repository.has_label(label):
            continue
        idls = object_repository.get_all_from_labeled_objects(label).copy()
        idl_count += len(idls)
        random.shuffle(idls)
        for idl in idls:
            # Verify that this object has not already been given a final
            # position by another mechanism or keyword location.
            if idl.instance['debug'].get('positionedBy'):
                continue
            idl.instance['debug']['positionedBy'] = 'mechanism'
            return idl
    # If a target object does not exist or was already used by another
    # mechanism, do not generate a new one; just raise an error.
    if labels == TARGET_LABEL or labels == [TARGET_LABEL]:
        error_message = (
            f'all {idl_count} matching object(s) were already used with other '
            f'mechanisms or positioned with keyword locations'
        ) if idl_count else 'no matching object(s) were previously generated'
        raise ILEException(
            f'Failed to find an available object with the "{TARGET_LABEL}" '
            f'label for a dropper/placer/thrower because {error_message}.'
        )
    return None


def _get_projectile_idl(
    template: Union[StructuralDropperConfig, StructuralThrowerConfig],
    room_dimensions: Dict[str, float],
    performer_start: Dict[str, Dict[str, float]],
    bounds_list: List[ObjectBounds]
) -> Tuple[InstanceDefinitionLocationTuple, bool]:
    labels = template.projectile_labels if template else None
    if labels:
        idl = _get_existing_held_object_idl(labels)
        if idl:
            return idl, True

    use_random = template is None or (template.projectile_shape is None and
                                      template.projectile_material is None and
                                      template.projectile_scale is None)
    if use_random:
        proj = InteractableObjectConfig(labels=labels)
    else:
        scale = template.projectile_scale or DEFAULT_PROJECTILE_SCALE
        proj = InteractableObjectConfig(
            labels=(
                [label for label in labels if label != TARGET_LABEL]
                if isinstance(labels, list) else labels
            ),
            material=template.projectile_material,
            shape=template.projectile_shape,
            scale=scale
        )

    idl = proj.create_instance_definition_location_tuple(
        room_dimensions,
        performer_start,
        bounds_list
    )
    idl.instance['debug']['positionedBy'] = 'mechanism'
    return idl, False


def _get_bounding_box_moving_occluder(obj: Dict[str, Any]) -> ObjectBounds:
    show = obj['shows'][0]
    scale = show['scale']
    max_scale = max(scale['x'], scale['z'])
    # Use max scale in both dimensions for bounding box of moving occluders.
    # This allows us to rotate without colliding.  This works for ILE, but
    # kind of creates an incorrect value for bounding box, thus it is here
    # and not in occluders.py
    return geometry.create_bounds(
        dimensions={'x': max_scale, 'y': scale['y'], 'z': max_scale},
        offset={'x': 0, 'y': 0, 'z': 0},
        position=show['position'],
        rotation=show['rotation'],
        standing_y=(scale['y'] / 2.0)
    )


def _compute_thrower_position_rotation(
        room_dim, max_scale, wall, template: StructuralThrowerConfig = None):
    twidth = getattr(template, 'position_wall', None)
    theight = getattr(template, 'height', None)
    buffer = max_scale
    wall_rot = {
        WallSide.LEFT.value: 0,
        WallSide.RIGHT: 180,
        WallSide.FRONT: 90,
        WallSide.BACK: 270}
    if (wall in [WallSide.FRONT, WallSide.BACK]):
        if twidth is not None:
            pos_x = twidth
        else:
            pos_x = twidth = random.uniform(-room_dim['x'] /
                                            2.0 + buffer, room_dim['x'] /
                                            2.0 - buffer)
        pos_z = (room_dim['z'] - max_scale) / \
            2.0 if wall == WallSide.FRONT else -(
                room_dim['z'] - max_scale) / 2.0
    if (wall in [WallSide.RIGHT, WallSide.LEFT]):
        if twidth is not None:
            pos_z = twidth
        else:
            pos_z = twidth or random.uniform(-room_dim['z'] /
                                             2.0 + buffer, room_dim['z'] /
                                             2.0 - buffer)
        pos_x = -(room_dim['x'] - max_scale) / \
            2.0 if wall == WallSide.LEFT else (room_dim['x'] - max_scale) / 2.0

    if theight is not None:
        pos_y = theight
    else:
        pos_y = random.uniform(buffer, room_dim['y'] - buffer)

    rot_y = wall_rot.get(wall)
    return pos_x, pos_y, pos_z, rot_y


def _add_ramp_platform_occluder_wall(
        scene: dict, bounds: List[ObjectBounds], retries: int, template: dict,
        structural_type: StructuralTypes):
    for try_num in range(retries):
        new_obj, reconciled_template = _get_structural_object(
            structural_type,
            scene,
            template
        )
        if not isinstance(new_obj, list):
            new_obj = [new_obj]
        valid = False
        if _validate_all_locations_and_update_bounds(new_obj, scene, bounds):
            valid = True
            if structural_type == StructuralTypes.WALLS:
                valid = (not is_wall_too_close(new_obj[0]))
        if valid:
            break
        else:
            # Checks if enabled for TRACE logging.
            # TODO Just use "logging.TRACE" once MCS v0.5.1 is released.
            if logger.isEnabledFor(TRACE):
                logger.trace(
                    f'Failed validating location of {structural_type.name} on '
                    f'try {try_num + 1} of {retries}.'
                    f'\nEXISTING BOUNDS = {bounds}'
                    f'\nFAILED OBJECT = {new_obj}'
                )
            else:
                logger.debug(
                    f'Failed validating location of {structural_type.name} on '
                    f'try {try_num + 1} of {retries}.'
                )
            new_obj = None
    if new_obj is not None:
        for obj in new_obj:
            scene['objects'].append(obj)
            _save_to_object_repository(
                obj,
                structural_type,
                reconciled_template.labels
            )
        log_structural_template_object(
            structural_type.name.lower().replace('_', ' '),
            'ids' if len(new_obj) > 1 else 'id',
            [part['id'] for part in new_obj] if len(new_obj) > 1 else
            new_obj[0]['id'],
            [template, reconciled_template]
        )
    else:
        msg = (
            f"Failed to create structural object of {structural_type.name} "
            f"after {retries} tries. Try reducing the number of objects, "
            f"using smaller objects, or using a larger room."
        )
        logger.debug(msg)
        raise ILEException(msg)


def _save_to_object_repository(
    obj: Dict[str, Any],
    structural_type: StructuralTypes,
    labels: List[str]
) -> None:
    # debug labels are labels going into the debug key.
    # We use the debug key because we need to generate the labels before we
    # are sure they object will be added to the scene.
    debug_labels = obj.get('debug', {}).get('labels')
    if debug_labels is not None:
        labels_list = debug_labels.copy()
    else:
        labels_list = (
            labels.copy() if isinstance(labels, list) else ([labels] or [])
        )
        if structural_type.name.lower() not in labels_list:
            labels_list.append(structural_type.name.lower())
    show = obj['shows'][0]
    location = {
        'position': copy.deepcopy(show['position']),
        'rotation': copy.deepcopy(show['rotation']),
        'boundingBox': copy.deepcopy(show['boundingBox']),
    }
    obj_repo = ObjectRepository.get_instance()
    obj_tuple = InstanceDefinitionLocationTuple(obj, None, location)
    obj_repo.add_to_labeled_objects(obj_tuple, labels=labels_list)


def is_wall_too_close(new_wall: Dict[str, Any]) -> bool:
    """Return if the given wall object is too close to any existing parallel
    walls in the object repository."""
    new_wall_rotation = new_wall['shows'][0]['rotation']
    # Only run this check if the wall is perfectly horizontal or vertical.
    # TODO Should we check all existing walls that are parallel to this wall,
    #      regardless of starting rotation? We'd need to update the math.
    if new_wall_rotation['y'] % 90 != 0:
        return False
    new_wall_is_horizontal = (new_wall_rotation['y'] % 180 == 0)
    new_wall_position = new_wall['shows'][0]['position']
    new_wall_scale = new_wall['shows'][0]['scale']
    new_wall_thickness_halved = (new_wall_scale['z'] / 2.0)
    new_wall_width_halved = (new_wall_scale['x'] / 2.0)
    object_repository = ObjectRepository.get_instance()
    walls = object_repository.get_all_from_labeled_objects('walls') or []
    for old_wall in walls:
        old_wall_position = old_wall.instance['shows'][0]['position']
        old_wall_rotation = old_wall.instance['shows'][0]['rotation']
        # Only check this wall if it's perfectly horizontal or vertical.
        if old_wall_rotation['y'] % 90 != 0:
            continue
        old_wall_is_horizontal = (old_wall_rotation['y'] % 180 == 0)
        if old_wall_is_horizontal == new_wall_is_horizontal:
            major_axis = 'z' if old_wall_is_horizontal else 'x'
            minor_axis = 'x' if old_wall_is_horizontal else 'z'
            old_wall_scale = old_wall.instance['shows'][0]['scale']
            old_wall_thickness_halved = (old_wall_scale['z'] / 2.0)
            old_wall_width_halved = (old_wall_scale['x'] / 2.0)
            distance_adjacent = (abs(
                new_wall_position[minor_axis] - old_wall_position[minor_axis]
            ) - old_wall_width_halved - new_wall_width_halved)
            if distance_adjacent > 0:
                continue
            distance_across = (abs(
                new_wall_position[major_axis] - old_wall_position[major_axis]
            ) - old_wall_thickness_halved - new_wall_thickness_halved)
            if distance_across < geometry.PERFORMER_WIDTH:
                return True
    return False
