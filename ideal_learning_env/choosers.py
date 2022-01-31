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

from .defs import ILEException
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


def choose_position(
    position: Union[VectorFloatConfig, List[VectorFloatConfig]],
    object_x: float = None,
    object_z: float = None,
    room_x: float = None,
    room_z: float = None
) -> Vector3d:
    """Choose and return a random position for the given position config or,
    if it is null, a random object position within the room bounds."""
    if position is None:
        position = VectorFloatConfig()
    position = position if isinstance(position, list) else [position]
    for pos in position:
        if pos.x is None:
            pos.x = MinMaxFloat(
                -(room_x / 2.0) + (object_x / 2.0),
                (room_x / 2.0) - (object_x / 2.0)
            )
        if pos.y is None:
            pos.y = 0
        if pos.z is None:
            pos.z = MinMaxFloat(
                -(room_z / 2.0) + (object_z / 2.0),
                (room_z / 2.0) - (object_z / 2.0)
            )
    return choose_random(position)


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
    # Cases:
    #   Both are none - choose shape randomly and then pick a valid material
    #   Only shape is none - choose material, then find valid shape
    #   Only material is none - choose shape, then pick valid material
    #       (similar to both are none)
    #   Neither are none - Choose shape, find material that fits?
    if material_or_color is None:
        # Case 1 and 3 above
        shape = choose_random(shape_list or base_objects.FULL_TYPE_LIST)
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
        shape = base_objects.get_type_from_material(mat[0])
        if shape is None:
            raise ILEException(f"Failed to find shape for material={mat}")
        return (shape, mat)
    else:
        # Case 4
        shape = choose_random(shape_list)
        if base_objects.has_material_restriction(shape):
            material_restriction = \
                base_objects.get_material_restriction_strings(
                    shape)
            if not material_restriction:
                return (shape, None)
            # Can we find a way to figure this out without guess and check?
            # The color option somewhat creates an issue
            for _ in range(MAX_TRIES):
                mat = choose_material_tuple_from_material(material_or_color)
                if mat[0] in material_restriction:
                    return (shape, mat)
            raise ILEException(
                f"failed to create valid shape/material combination for"
                f" shape={shape}")
        else:
            mat = choose_material_tuple_from_material(material_or_color)
        return (shape, mat)
