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
from ideal_learning_env.interactable_object_config import (
    InteractableObjectConfig,
    KeywordLocationConfig,
)
from ideal_learning_env.object_services import (
    TARGET_LABEL,
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
DROPPER_THROWER_SCALE_MULTIPLIER = 1.5
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
    """
    scale: Union[float, MinMaxFloat, List[Union[float, MinMaxFloat]],
                 VectorFloatConfig, List[VectorFloatConfig]] = None


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
    or list of MinMaxFloat dicts): Length of the ramp
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Width of the ramp
    """
    angle: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    width: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    length: Union[float, MinMaxFloat,
                  List[Union[float, MinMaxFloat]]] = None


@dataclass
class StructuralLOccluderConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural L-shaped occluder.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
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
    - `repeat_movement` (boolean): If true, repeat the occluder's full
    movement and rotation indefinitely, using `repeat_interval` as the number
    of steps to wait.
    - `reverse_direction` (bool): Reverse the rotation direction of a sideways
    wall by rotating the wall 180 degrees.  Only used if `origin` is set to a
    wall and not `top`
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
    repeat_movement: bool = None
    repeat_interval: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    reverse_direction: bool = None
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
    wall.
    The types include:
      `occludes` - occludes the target or object.
      `short` - wide enough, but not tall enough to occlude the target.
      `thin` - tall enough, but not wide enough to occlude the target.
      `hole` - wall with a hole that reveals the target.
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
    dict): Step on which placer should begin downward movement.
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
    activation_step: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
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
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Scale of the door
    """
    scale: Union[float, MinMaxFloat, List[Union[float, MinMaxFloat]],
                 VectorFloatConfig, List[VectorFloatConfig]] = None


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
    num=0, position=VectorFloatConfig(None, None, None),
    scale=MinMaxFloat(PLATFORM_SCALE_MIN, PLATFORM_SCALE_MAX))
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
    scale_y=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX))

DEFAULT_TEMPLATE_HOLES = FloorAreaConfig(0)

DEFAULT_TEMPLATE_FLOOR_MATERIALS = FloorMaterialConfig(0)

DEFAULT_OCCLUDING_WALL = StructuralOccludingWallConfig(
    num=0, type=[e.value for e in OccludingWallType],
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
    activation_step=MinMaxInt(0, 10))

DOOR_MATERIAL_RESTRICTIONS = [mat[0] for mat in (materials.METAL_MATERIALS +
                                                 materials.PLASTIC_MATERIALS +
                                                 materials.WOOD_MATERIALS)]

DEFAULT_TEMPLATE_DOOR = StructuralDoorConfig(
    num=0, position=VectorFloatConfig(None, None, None),
    rotation_y=MinMaxInt(0, 359),
    scale=1, material=DOOR_MATERIAL_RESTRICTIONS)


def add_structural_object_with_retries_or_throw(
        scene: dict, bounds: List[ObjectBounds], retries: int, template,
        structural_type: StructuralTypes, i: int,
        existing_holes: Tuple[int, int], mat_to_loc,
        existing_floor_materials: Tuple[int, int]):
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
            scene, bounds, retries, template, structural_type, i)
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
    elif structural_type == StructuralTypes.HOLES:
        _add_holes_with_retries_or_throw(
            scene, template, existing_holes, bounds)
    elif (
        structural_type == StructuralTypes.FLOOR_MATERIALS or
        structural_type == StructuralTypes.LAVA
    ):
        # Ensure that the lava template always uses the lava material.
        # Especially important when lava is made via random_structural_objects.
        if structural_type == StructuralTypes.LAVA:
            if not template:
                template = FloorMaterialConfig()
            template.material = materials.LAVA_MATERIALS[0].material
        mat, mat_loc = _get_floor_material_loc_with_retries_or_throw(
            scene, template, existing_floor_materials)
        mat = mat[0]
        loc_list = mat_to_loc.get(mat, [])
        loc_list.append(mat_loc)
        mat_to_loc[mat] = loc_list
        # For a lava material, add its bounds to the list.
        if mat in [item.material for item in materials.LAVA_MATERIALS]:
            bounds.append(geometry.generate_floor_area_bounds(
                mat_loc['x'],
                mat_loc['z']
            ))
        log_structural_template_object(
            structural_type.name.lower().replace('_', ' '),
            mat,
            mat_to_loc[mat],
            [template]
        )
    elif structural_type == StructuralTypes.OCCLUDING_WALLS:
        _add_occluding_wall(scene, bounds, retries, template)
    elif structural_type == StructuralTypes.PLACERS:
        _add_placer(scene, bounds, retries, template)
    elif structural_type == StructuralTypes.DOORS:
        _add_door_with_retries_or_throw(scene, bounds, retries, template)


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
    return new_obj, reconciled_template


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


def _add_holes_with_retries_or_throw(
    scene: Dict[str, Any],
    src_template: FloorAreaConfig,
    existing: List[Tuple[int, int]],
    bounds: List[ObjectBounds]
) -> None:
    room_dim = scene['roomDimensions']
    xmax = math.floor(room_dim['x'] / 2)
    zmax = math.floor(room_dim['z'] / 2)
    default_template = DEFAULT_TEMPLATE_HOLES
    errors = set({})
    performer_pos = scene['performerStart']['position']
    perf_x = performer_pos['x']
    perf_z = performer_pos['z']
    perf_x = round(perf_x)
    perf_z = round(perf_z)
    restrict_under_user = (
        src_template is None or src_template.position_x is None or
        src_template.position_z is None)

    for _ in range(MAX_TRIES):
        error, hole_loc, _ = _get_floor_location(
            src_template, xmax, zmax, default_template)
        if (restrict_under_user and
                hole_loc[0] == perf_x and hole_loc[1] == perf_z):
            error = ("Random location of hole put under performer start at"
                     f" ({perf_x}, {perf_z}). ")
        if error is None:
            if hole_loc not in existing:
                existing.append(hole_loc)
                scene['holes'].append({'x': hole_loc[0], 'z': hole_loc[1]})
                bounds.append(geometry.generate_floor_area_bounds(
                    hole_loc[0],
                    hole_loc[1]
                ))
                log_structural_template_object(
                    'holes',
                    'holes',
                    scene['holes'][-1],
                    [src_template]
                )
                return
            else:
                errors.add("Unable to find valid location. ")
        else:
            errors.add(error)
    raise ILEException(
        f"Failed to create holes.  Errors={''.join(errors)}")


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
    floor_loc = (x, z)
    return error, floor_loc, template


def _get_floor_material_loc_with_retries_or_throw(
    scene, src_template: FloorMaterialConfig,
        existing: List[Tuple[int, int]]):
    default_template = DEFAULT_TEMPLATE_FLOOR_MATERIALS
    errors = set({})
    room_dim = scene['roomDimensions']
    xmax = math.floor(room_dim['x'] / 2)
    zmax = math.floor(room_dim['z'] / 2)
    for _ in range(MAX_TRIES):
        error, mat_loc, template = _get_floor_location(
            src_template, xmax, zmax, default_template)
        if error is None:
            mat = template.material
            mat = mat[0] if isinstance(mat, tuple) else mat
            mat = (
                choose_material_tuple_from_material(mat) if mat else
                random.choice(materials.FLOOR_MATERIALS)
            )
            if mat_loc not in existing:
                existing.append(mat_loc)
                return (mat, {'x': mat_loc[0], 'z': mat_loc[1]})
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
        projectile_dimensions['x'] *= DROPPER_THROWER_SCALE_MULTIPLIER
        projectile_dimensions['y'] *= DROPPER_THROWER_SCALE_MULTIPLIER
        projectile_dimensions['z'] *= DROPPER_THROWER_SCALE_MULTIPLIER
        args = {
            'position_x': pos_x,
            'position_z': pos_z,
            'room_dimensions_y': room_dim['y'],
            'object_dimensions': projectile_dimensions,
            'last_step': scene.get('last_step'),
            'dropping_step': template.drop_step
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
        projectile_dimensions['x'] *= DROPPER_THROWER_SCALE_MULTIPLIER
        projectile_dimensions['y'] *= DROPPER_THROWER_SCALE_MULTIPLIER
        projectile_dimensions['z'] *= DROPPER_THROWER_SCALE_MULTIPLIER
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
            'last_step': scene.get('last_step'),
            'throwing_step': template.throw_step
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
        end_height = 0
        max_height = room_dim['y']
        last_step = scene.get("last_step")
        instance = idl.instance
        defn = idl.definition

        args = {
            'instance': instance,
            'activation_step': template.activation_step,
            'start_height': start_height,
            'end_height': end_height
        }
        logger.trace(f'Positioning placer object:\nINPUT = {args}')
        mechanisms.place_object(**args)

        args = {
            'placed_object_position': instance['shows'][0]['position'],
            'placed_object_scale': instance['shows'][0]['scale'],
            'placed_object_dimensions': instance['debug']['dimensions'],
            'placed_object_offset_y': instance['debug']['positionY'],
            'activation_step': template.activation_step,
            'end_height': end_height,
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

    for try_num in range(retries):
        template = reconcile_template(
            DEFAULT_TEMPLATE_DOOR,
            source_template)
        template.material = (
            choose_material_tuple_from_material(template.material)
            if template.material else random.choice(random.choice([
                materials.METAL_MATERIALS,
                materials.PLASTIC_MATERIALS,
                materials.WOOD_MATERIALS,
            ]))
        )
        template.position.x = (
            MinMaxFloat(-room_width / 2.0, room_width / 2.0).convert_value()
            if template.position.x is None else template.position.x
        )
        template.position.z = (
            MinMaxFloat(-room_length / 2.0, room_length / 2.0).convert_value()
            if template.position.z is None else template.position.z
        )
        scale = template.scale
        scale = scale if isinstance(
            scale, Vector3d) else Vector3d(
            scale, scale, scale)
        # Restrict max height to room height.
        # Door objects are twice as tall as their Y scale.
        scale.y = min(scale.y, room_dim['y'] / 2.0)
        mat = template.material
        args = {
            'position_x': template.position.x,
            'position_z': template.position.z,
            'rotation_y': template.rotation_y,
            'scale_x': scale.x,
            'scale_y': scale.y,
            'scale_z': scale.z,
            'material_tuple': mat
        }
        logger.trace(f'Creating door:\nINPUT = {args}')
        door = structures.create_door(**args)

        if _validate_all_locations_and_update_bounds([door], scene, bounds):
            add_random_placement_tag(door, source_template)
            scene['objects'].append(door)
            _save_to_object_repository(
                door,
                StructuralTypes.DOORS,
                template.labels
            )
            log_structural_template_object(
                'door',
                'id',
                door['id'],
                [source_template, template]
            )
            return
    raise ILEException("Failed to create door")


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
        structural_type: StructuralTypes, i: int):
    for try_num in range(retries):
        new_obj, reconciled_template = _get_structural_object(
            structural_type,
            scene,
            template
        )
        if not isinstance(new_obj, list):
            new_obj = [new_obj]
        if _validate_all_locations_and_update_bounds(new_obj, scene, bounds):
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
