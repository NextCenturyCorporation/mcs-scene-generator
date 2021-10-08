import random
from typing import Any, List, Tuple, Type, Union

from machine_common_sense.config_manager import Vector3d

from generator import base_objects, geometry, materials, util

from .defs import ILEException
from .defs import choose_random as _choose_random
from .numerics import MinMaxFloat, VectorFloatConfig, VectorIntConfig


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
    return choose_random(position or VectorFloatConfig(MinMaxFloat(
        -(room_x / 2.0) + (object_x / 2.0),
        (room_x / 2.0) - (object_x / 2.0)
    ), 0, MinMaxFloat(
        -(room_z / 2.0) + (object_z / 2.0),
        (room_z / 2.0) - (object_z / 2.0)
    )))


def choose_rotation(
    rotation: Union[VectorIntConfig, List[VectorIntConfig]]
) -> Vector3d:
    """Choose and return a random rotation for the given rotation config or,
    if it is null, a random object rotation."""
    return choose_random(
        rotation or VectorIntConfig(0, list(geometry.VALID_ROTATIONS), 0)
    )


def choose_material_tuple_from_material(
        material_or_color: Union[str, List[str]] = None,
        shape: str = None) -> Tuple[str, List[str]]:
    '''Choose material tuple either for random if parameter is None or match
    the material or color string'''
    if (material_or_color is None):
        material_or_color = base_objects.get_material_restriction(shape)
    material_or_color = material_or_color if isinstance(
        material_or_color, List) else [material_or_color]
    mat = choose_random(material_or_color or materials.ALL_MATERIAL_STRINGS)
    if hasattr(materials, mat):
        mat = random.choice(getattr(materials, mat))
    else:
        colors = materials.find_colors(mat, None)
        mat = (mat, colors)
    return mat


def choose_shape_material(
        shape_list: Union[str, List[str]] = None,
        material_or_color=None) -> Tuple[str, Tuple[str, List[str]]]:
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
        material_or_color = choose_random(
            base_objects.get_material_restriction(shape))
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
            mat_restrict = base_objects.get_material_restriction(shape)
            # Can we find a way to figure this out without guess and check?
            # The color option somewhat creates an issue
            for _ in range(util.MAX_TRIES):
                mat = choose_material_tuple_from_material(material_or_color)
                if mat in mat_restrict:
                    return (shape, mat)
            raise ILEException(
                f"failed to create valid shape/material combination for"
                f" shape={shape}")
        else:
            mat = choose_material_tuple_from_material(material_or_color)
        return (shape, mat)
