import random
from typing import Any, List, Optional, Tuple, Type, Union

from machine_common_sense.config_manager import Vector3d

from generator import (
    MAX_TRIES,
    MaterialTuple,
    base_objects,
    geometry,
    materials,
)

from .defs import ILEException, ILESharedConfiguration
from .defs import choose_random as _choose_random
from .numerics import MinMaxFloat, VectorFloatConfig, VectorIntConfig

SOCCER_BALL_SCALE_MAX = 3
SOCCER_BALL_SCALE_MIN = 1


def choose_random(data: Any, data_type: Type = None) -> Any:
    """Return the data, if it's a single choice; a single element from the
    data, if it's a list; or a value within a numeric range, if it's a MinMax.
    The given type is used to handle specific edge cases."""

    # The choose_random function needs to be defined in defs, because it's used
    # by the classes in numerics, so defining it here instead would cause a
    # circular dependency. However, not having it here (in the "choosers" file)
    # also seemed odd, so I defined this wrapper function. Hopefully this is
    # less confusing, and not more (if the latter, we can just delete this).
    return _choose_random(data, data_type)


def choose_counts(
    data: List[Any],
    count_attribute: str = 'num',
    default_count: int = 1
) -> List[Tuple[Any, int]]:
    """Return the given data list, but each item in the list is now a tuple
    containing the original item and a count randomly chosen from its 'num'
    attribute."""
    return [(item, choose_random((
        item if isinstance(item, dict) else vars(item)
    ).get(count_attribute, default_count))) for item in data]


def choose_position(
    position: Union[VectorFloatConfig, List[VectorFloatConfig]],
    object_x: float = None,
    object_z: float = None,
    room_x: float = None,
    room_y: float = None,
    room_z: float = None
) -> Vector3d:
    """Choose and return a random position for the given position config or,
    if it is null, a random object position within the room bounds."""
    if position is None:
        position = VectorFloatConfig()
    position = position if isinstance(position, list) else [position]
    constrained_positions = []
    for pos in position:
        constrained_x = pos.x
        constrained_y = pos.y if pos.y is not None else 0
        constrained_z = pos.z
        if room_x is not None:
            constrained_x = _constrain_position_x_z(pos.x, object_x, room_x)
        if room_y is not None:
            constrained_y = _constrain_position_y(pos.y, room_y)
        if room_z is not None:
            constrained_z = _constrain_position_x_z(pos.z, object_z, room_z)
        constrained_position = VectorFloatConfig(
            constrained_x, constrained_y, constrained_z)
        constrained_positions.append(constrained_position)
    return choose_random(constrained_positions)


def _get_min_max_room_dimensions(room_dim, object_dim):
    width = object_dim / 2.0
    min = -(room_dim / 2.0) + width
    max = (room_dim / 2.0) - width
    return min, max


def _constrain_position_x_z(
        position: Union[float, MinMaxFloat, List[float]] = None,
        object_dim: float = None,
        room_dim: float = None):
    constrained_position = position
    if position is None:
        min, max = _get_min_max_room_dimensions(room_dim, object_dim)
        constrained_position = MinMaxFloat(min, max)
    elif isinstance(position, float) or isinstance(position, int):
        minimum = -(room_dim / 2.0) + (object_dim / 2.0)
        maximum = (room_dim / 2.0) - (object_dim / 2.0)
        if position < minimum or position > maximum:
            raise ILEException(
                f'Failed to find a valid position {position} '
                f'with room dimension: {room_dim}'
            )
        constrained_position = position
    elif isinstance(position, MinMaxFloat):
        constrained_position = \
            _constrain_min_max_pos_to_room_dimensions_x_z(
                position,
                object_dim,
                room_dim
            )
    elif isinstance(position, List):
        original_list = position
        constrained_position = []
        for pos in position:
            is_valid = \
                _constrain_float_list_to_room_dimension_x_z(
                    pos, object_dim, room_dim)
            if is_valid:
                constrained_position.append(pos)
        if len(constrained_position) == 0:
            raise ILEException(
                f'Failed to find a valid position in list: '
                f'{original_list} with room dimension: {room_dim}'
            )
    return constrained_position


def _constrain_position_y(
        position: Union[float, MinMaxFloat, List[float]] = None,
        room_dim: float = None):
    max_y = room_dim - geometry.PERFORMER_HEIGHT
    constrained_y = position
    if position is None:
        constrained_y = 0
    elif isinstance(position, float) or isinstance(position, int):
        if not 0 <= position <= max_y:
            raise ILEException(
                f'Failed to find a valid position y with: '
                f'{position} with room dimension: {room_dim}'
            )
    elif isinstance(position, MinMaxFloat):
        constrained_y = _constrain_min_max_y_to_room_height(position, max_y)
    elif isinstance(position, List):
        original_list = position
        constrained_y = []
        for y in position:
            is_valid = \
                _constrain_float_list_y_to_room_height(y, max_y)
            if is_valid:
                constrained_y.append(y)
        if len(constrained_y) == 0:
            raise ILEException(
                f'Failed to find a valid position in list: '
                f'{original_list} with room dimension: {room_dim}'
            )
    return constrained_y


def _constrain_min_max_y_to_room_height(
    pos: MinMaxFloat = None,
    max_y: float = None
) -> MinMaxFloat:
    constrained_min = max_y if pos.min > max_y \
        else 0 if pos.min < 0 else pos.min
    constrained_max = max_y if pos.max > max_y \
        else 0 if pos.max < 0 else pos.max
    return MinMaxFloat(constrained_min, constrained_max)


def _constrain_float_list_y_to_room_height(
    pos: float = None,
    max_y: float = None,
) -> float:
    constrained_pos = max_y if pos > max_y else 0 if pos < 0 else pos
    return constrained_pos


def _constrain_float_list_to_room_dimension_x_z(
    pos: float = None,
    object_dim: float = None,
    room_dim: float = None
) -> float:
    min, max = _get_min_max_room_dimensions(room_dim, object_dim)
    is_valid_pos = min < pos < max
    return is_valid_pos


def _constrain_min_max_pos_to_room_dimensions_x_z(
    pos: MinMaxFloat = None,
    object_dim: float = None,
    room_dim: float = None
) -> MinMaxFloat:
    min, max = _get_min_max_room_dimensions(room_dim, object_dim)
    constrained_max = max if pos.max > max \
        else min if pos.max < min else pos.max
    constrained_min = max if pos.min > max \
        else min if pos.min < min else pos.min
    return MinMaxFloat(constrained_min, constrained_max)


def choose_rotation(
    rotation: Union[VectorIntConfig, List[VectorIntConfig]]
) -> Vector3d:
    """Choose and return a random rotation for the given rotation config or,
    if it is null, a random object rotation."""
    if rotation is None:
        rotation = VectorIntConfig()
    rotation = rotation if isinstance(rotation, list) else [rotation]
    for rot in rotation:
        if rot.x is None:
            rot.x = 0
        if rot.z is None:
            rot.z = 0
        if rot.y is None:
            rot.y = list(geometry.VALID_ROTATIONS)
    return choose_random(rotation)


def choose_material_tuple_from_material(
    material_or_color: Union[str, List[str]]
) -> MaterialTuple:
    """Return a MaterialTuple chosen randomly from the given materials that can
    either be specific materials or names of lists in materials.py."""
    material_or_color = (
        material_or_color if isinstance(material_or_color, List) else
        [material_or_color]
    )
    mat = choose_random(material_or_color)
    if hasattr(materials, str(mat)):
        return random.choice(getattr(materials, mat))
    colors = materials.find_colors(mat, [])
    return MaterialTuple(mat, colors)


def _filter_scale_soccer_ball(
    scale: Union[float, MinMaxFloat, VectorFloatConfig]
) -> bool:
    if not scale:
        return False
    # Soccer balls are restricted to only specific scales.
    if isinstance(scale, (int, float)):
        return SOCCER_BALL_SCALE_MIN <= scale <= SOCCER_BALL_SCALE_MAX
    if isinstance(scale, MinMaxFloat):
        return (
            SOCCER_BALL_SCALE_MIN <= scale.min <= SOCCER_BALL_SCALE_MAX and
            SOCCER_BALL_SCALE_MIN <= scale.max <= SOCCER_BALL_SCALE_MAX
        )
    # Soccer balls must have the same X/Y/Z scales.
    if isinstance(scale, VectorFloatConfig):
        return not (
            scale.x != scale.y or scale.x != scale.z or scale.y != scale.z or
            SOCCER_BALL_SCALE_MIN > scale.x > SOCCER_BALL_SCALE_MAX
        )
    if isinstance(scale, Vector3d):
        return not (
            scale.x != scale.y or scale.x != scale.z or scale.y != scale.z or
            SOCCER_BALL_SCALE_MIN > scale.x > SOCCER_BALL_SCALE_MAX
        )
    return False


def choose_scale(
    scale: Union[
        float, MinMaxFloat, VectorFloatConfig,
        List[Union[float, MinMaxFloat, VectorFloatConfig]]
    ],
    shape: str
) -> float:
    """Return a randomly chosen scale for the given shape using the given
    scale options."""
    # Default scale is 1 if scale is None or 0.
    choices = scale or 1
    # Rules for soccer balls, which have specific restrictions due to their
    # importance as the target object in interactive evaluation scenes.
    if shape == 'soccer_ball':
        # If no choices are valid, scale is randomized from defaults.
        choices = list(filter(
            _filter_scale_soccer_ball,
            scale if isinstance(scale, list) else [scale]
        )) or MinMaxFloat(SOCCER_BALL_SCALE_MIN, SOCCER_BALL_SCALE_MAX)
    return choose_random(choices)


def choose_shape_material(
    shape_list: Union[str, List[str]] = None,
    material_or_color: Union[str, List[str]] = None
) -> Optional[Tuple[str, MaterialTuple]]:
    """Takes choices for shape and material_or_color and returns a valid
    combination or throws and exception.  Throwing an exception will mean
    there is a possible shape without a possible material and thus will not be
    retryable."""
    shared_config = ILESharedConfiguration.get_instance()
    excluded_shapes = shared_config.get_excluded_shapes()
    # Cases:
    #   Both are none - choose shape randomly and then pick a valid material
    #   Only shape is none - choose material, then find valid shape
    #   Only material is none - choose shape, then pick valid material
    #       (similar to both are none)
    #   Neither are none - Choose shape, find material that fits?
    if material_or_color is None:
        # Case 1 and 3 above
        if shape_list:
            shape = choose_random(shape_list)
        else:
            for _ in range(MAX_TRIES):
                shape = choose_random(base_objects.FULL_TYPE_LIST)
                if shape not in excluded_shapes:
                    break
                shape = None
            if not shape:
                raise ILEException(
                    f'Failed to find a valid shape with excluded shapes: '
                    f'{excluded_shapes}'
                )
        material_restriction = base_objects.get_material_restriction_tuples(
            shape)
        material_or_color = (
            choose_random(material_restriction) if material_restriction else
            None
        )
        return (shape, material_or_color)
    elif shape_list is None:
        # Case 2 above
        mat = choose_material_tuple_from_material(material_or_color)
        for _ in range(MAX_TRIES):
            shape = base_objects.get_type_from_material(mat[0])
            if shape not in excluded_shapes:
                break
            shape = None
        if shape is None:
            raise ILEException(
                f'Failed to find a valid shape for material {mat} with '
                f'excluded shapes: {excluded_shapes}'
            )
        return (shape, mat)
    else:
        # Case 4
        shape = choose_random(shape_list)
        if base_objects.has_material_restriction(shape):
            material_restriction = \
                base_objects.get_material_restriction_strings(shape)
            if not material_restriction:
                return (shape, None)
            # Can we find a way to figure this out without guess and check?
            # The color option somewhat creates an issue
            for _ in range(MAX_TRIES):
                mat = choose_material_tuple_from_material(material_or_color)
                if mat[0] in material_restriction:
                    return (shape, mat)
            raise ILEException(
                f'Failed to find a valid shape and material combination for '
                f'shape {shape} and {len(material_restriction)} materials'
            )
        mat = choose_material_tuple_from_material(material_or_color)
        return (shape, mat)
