from __future__ import annotations

import copy
import math
from typing import List, Union

from machine_common_sense.config_manager import Vector3d

from . import base_objects
from .base_objects import ObjectBaseSize, create_variable_definition_from_base
from .definitions import (
    ChosenMaterial,
    DefinitionDataset,
    ObjectDefinition,
    get_dataset,
)

# Common material options used by all intuitive physics objects.
# Add some extra mass to all intuitive physics objects.
INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST: List[ChosenMaterial] = [
    ChosenMaterial.INTUITIVE_PHYSICS_BLOCK,
    ChosenMaterial.INTUITIVE_PHYSICS_PLASTIC,
    ChosenMaterial.INTUITIVE_PHYSICS_WOOD
]


TRAINED_SIZE_MULTIPLIER_LIST = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75]
NOVEL_SIZE_MULTIPLIER_LIST = [0.4, 0.85]


def generate_size_multiplier_list(
    object_size: ObjectBaseSize,
    novel: bool = False
) -> List[float]:
    """The intuitive physics hypercubes use objects with similar diagonal sizes
    so make sure each object type has a similar array of sizes."""
    output = []
    for multiplier in (
        NOVEL_SIZE_MULTIPLIER_LIST if novel else TRAINED_SIZE_MULTIPLIER_LIST
    ):
        diagonal = math.hypot(multiplier, multiplier)
        x_size = object_size.dimensions.x
        z_size = object_size.dimensions.z
        adjusted_diagonal = math.sqrt(diagonal**2 / (x_size**2 + z_size**2))
        output.append(round(adjusted_diagonal, 2))
    return output


_INTUITIVE_PHYSICS_COMPLEX_OBJECTS = [
    ('bus_1', base_objects._TOY_BUS_1_SIZE),
    ('car_1', base_objects._TOY_SEDAN_SIZE),
    ('car_2', base_objects._TOY_CAR_2_SIZE),
    ('cart_2', base_objects._CART_2_SIZE),
    ('dog_on_wheels', base_objects._DOG_ON_WHEELS_SIZE),
    ('duck_on_wheels', base_objects._DUCK_ON_WHEELS_SIZE),
    ('racecar_red', base_objects._TOY_RACECAR_SIZE),
    ('train_1', base_objects._TOY_TRAIN_SIZE),
    ('trolley_1', base_objects._TOY_TROLLEY_SIZE),
    ('truck_1', base_objects._TOY_TRUCK_1_SIZE),
    ('truck_2', base_objects._TOY_TRUCK_2_SIZE),
    ('turtle_on_wheels', base_objects._TURTLE_ON_WHEELS_SIZE),
]
_COMPLEX_TYPES_TO_SIZES = dict([
    (object_type, generate_size_multiplier_list(object_size))
    for object_type, object_size in _INTUITIVE_PHYSICS_COMPLEX_OBJECTS
])
_NOVEL_COMPLEX_TYPES_TO_SIZES = dict([
    (object_type, generate_size_multiplier_list(object_size, novel=True))
    for object_type, object_size in _INTUITIVE_PHYSICS_COMPLEX_OBJECTS
])


def turn_sideways(definition: ObjectDefinition) -> ObjectDefinition:
    """Set the Y rotation to 90 in the given definition and switch its X and Z
    dimensions."""
    definition.rotation = Vector3d(0, 90, 0)
    for size in definition.chooseSizeList:
        size.dimensions = Vector3d(
            size.dimensions.z,
            size.dimensions.y,
            size.dimensions.x
        )
    return definition


_CIRCLE_FRUSTUM = create_variable_definition_from_base(
    type='circle_frustum',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CIRCLE_FRUSTUM_NOVEL_SIZE = create_variable_definition_from_base(
    type='circle_frustum',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CIRCLE_FRUSTUM_NOVEL_SIZE.untrainedSize = True


_CONE = create_variable_definition_from_base(
    type='cone',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CONE_NOVEL_SIZE = create_variable_definition_from_base(
    type='cone',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CONE_NOVEL_SIZE.untrainedSize = True


_CUBE = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CUBE_NOVEL_SIZE = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CUBE_NOVEL_SIZE.untrainedSize = True


_CYLINDER = create_variable_definition_from_base(
    type='cylinder',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CYLINDER_NOVEL_SIZE = create_variable_definition_from_base(
    type='cylinder',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CYLINDER_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_CYLINDER.rotation = Vector3d(90, 0, 0)
_CYLINDER_NOVEL_SIZE.rotation = Vector3d(90, 0, 0)


_PYRAMID = create_variable_definition_from_base(
    type='pyramid',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_PYRAMID_NOVEL_SIZE = create_variable_definition_from_base(
    type='pyramid',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_PYRAMID_NOVEL_SIZE.untrainedSize = True


_RECT_PRISM = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[
        Vector3d(multiplier, multiplier / 2.0, multiplier)
        for multiplier in TRAINED_SIZE_MULTIPLIER_LIST
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RECT_PRISM_NOVEL_SIZE = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[
        Vector3d(multiplier, multiplier / 2.0, multiplier)
        for multiplier in NOVEL_SIZE_MULTIPLIER_LIST
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RECT_PRISM_NOVEL_SIZE.untrainedSize = True
# Override the default shape (cube).
_RECT_PRISM.shape = ['rectangular prism']
_RECT_PRISM_NOVEL_SIZE.shape = ['rectangular prism']


_SPHERE = create_variable_definition_from_base(
    type='sphere',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SPHERE_NOVEL_SIZE = create_variable_definition_from_base(
    type='sphere',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SPHERE_NOVEL_SIZE.untrainedSize = True


_SQUARE_FRUSTUM = create_variable_definition_from_base(
    type='square_frustum',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SQUARE_FRUSTUM_NOVEL_SIZE = create_variable_definition_from_base(
    type='square_frustum',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SQUARE_FRUSTUM_NOVEL_SIZE.untrainedSize = True


_TUBE_NARROW = create_variable_definition_from_base(
    type='tube_narrow',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TUBE_NARROW_NOVEL_SIZE = create_variable_definition_from_base(
    type='tube_narrow',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TUBE_NARROW_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_TUBE_NARROW.rotation = Vector3d(90, 0, 0)
_TUBE_NARROW_NOVEL_SIZE.rotation = Vector3d(90, 0, 0)


_TUBE_WIDE = create_variable_definition_from_base(
    type='tube_wide',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TUBE_WIDE_NOVEL_SIZE = create_variable_definition_from_base(
    type='tube_wide',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TUBE_WIDE_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_TUBE_WIDE.rotation = Vector3d(90, 0, 0)
_TUBE_WIDE_NOVEL_SIZE.rotation = Vector3d(90, 0, 0)


_DUCK = create_variable_definition_from_base(
    type='duck_on_wheels',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['duck_on_wheels'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUCK_NOVEL_SIZE = create_variable_definition_from_base(
    type='duck_on_wheels',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['duck_on_wheels'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUCK_NOVEL_SIZE.untrainedSize = True


_TURTLE = create_variable_definition_from_base(
    type='turtle_on_wheels',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['turtle_on_wheels'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)

_TURTLE_NOVEL_SIZE = create_variable_definition_from_base(
    type='turtle_on_wheels',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['turtle_on_wheels'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TURTLE_NOVEL_SIZE.untrainedSize = True


_SEDAN = turn_sideways(create_variable_definition_from_base(
    type='car_1',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['car_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_SEDAN_NOVEL_SIZE = turn_sideways(create_variable_definition_from_base(
    type='car_1',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['car_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_SEDAN_NOVEL_SIZE.untrainedSize = True


_RACECAR = turn_sideways(create_variable_definition_from_base(
    type='racecar_red',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['racecar_red'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_RACECAR_NOVEL_SIZE = turn_sideways(create_variable_definition_from_base(
    type='racecar_red',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['racecar_red'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_RACECAR_NOVEL_SIZE.untrainedSize = True


_TRAIN = turn_sideways(create_variable_definition_from_base(
    type='train_1',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['train_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TRAIN_NOVEL_SIZE = turn_sideways(create_variable_definition_from_base(
    type='train_1',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['train_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TRAIN_NOVEL_SIZE.untrainedSize = True


_TROLLEY = turn_sideways(create_variable_definition_from_base(
    type='trolley_1',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['trolley_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TROLLEY_NOVEL_SIZE = turn_sideways(create_variable_definition_from_base(
    type='trolley_1',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['trolley_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TROLLEY_NOVEL_SIZE.untrainedSize = True


# EVAL 4 NOVEL OBJECTS


_DOUBLE_CONE = create_variable_definition_from_base(
    type='double_cone',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DOUBLE_CONE.untrainedShape = True
_DOUBLE_CONE_NOVEL_SIZE = create_variable_definition_from_base(
    type='double_cone',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DOUBLE_CONE_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_DOUBLE_CONE.rotation = Vector3d(90, 0, 0)
_DOUBLE_CONE_NOVEL_SIZE.rotation = Vector3d(90, 0, 0)


_DUMBBELL_1 = create_variable_definition_from_base(
    type='dumbbell_1',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUMBBELL_1.untrainedShape = True
_DUMBBELL_1_NOVEL_SIZE = create_variable_definition_from_base(
    type='dumbbell_1',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUMBBELL_1_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_DUMBBELL_1.rotation = Vector3d(90, 0, 0)
_DUMBBELL_1_NOVEL_SIZE.rotation = Vector3d(90, 0, 0)


_DUMBBELL_2 = create_variable_definition_from_base(
    type='dumbbell_2',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUMBBELL_2.untrainedShape = True
_DUMBBELL_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='dumbbell_2',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUMBBELL_2_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_DUMBBELL_2.rotation = Vector3d(90, 0, 0)
_DUMBBELL_2_NOVEL_SIZE.rotation = Vector3d(90, 0, 0)


_TIE_FIGHTER = create_variable_definition_from_base(
    type='tie_fighter',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TIE_FIGHTER.untrainedShape = True
_TIE_FIGHTER_NOVEL_SIZE = create_variable_definition_from_base(
    type='tie_fighter',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TIE_FIGHTER_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_TIE_FIGHTER.rotation = Vector3d(90, 0, 0)
_TIE_FIGHTER_NOVEL_SIZE.rotation = Vector3d(90, 0, 0)


_BUS_1 = turn_sideways(create_variable_definition_from_base(
    type='bus_1',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['bus_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_BUS_1.untrainedShape = True
_BUS_1_NOVEL_SIZE = turn_sideways(create_variable_definition_from_base(
    type='bus_1',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['bus_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_BUS_1_NOVEL_SIZE.untrainedSize = True


_CAR_2 = turn_sideways(create_variable_definition_from_base(
    type='car_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['car_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_CAR_2.untrainedShape = True
_CAR_2_NOVEL_SIZE = turn_sideways(create_variable_definition_from_base(
    type='car_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['car_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_CAR_2_NOVEL_SIZE.untrainedSize = True


_CART_2 = turn_sideways(create_variable_definition_from_base(
    type='cart_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['cart_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_CART_2.untrainedShape = True
_CART_2_NOVEL_SIZE = turn_sideways(create_variable_definition_from_base(
    type='cart_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['cart_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_CART_2_NOVEL_SIZE.untrainedSize = True


_DOG_ON_WHEELS = turn_sideways(create_variable_definition_from_base(
    type='dog_on_wheels',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['dog_on_wheels'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_DOG_ON_WHEELS.untrainedShape = True
_DOG_ON_WHEELS_NOVEL_SIZE = turn_sideways(create_variable_definition_from_base(
    type='dog_on_wheels',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['dog_on_wheels'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_DOG_ON_WHEELS_NOVEL_SIZE.untrainedSize = True


_TRUCK_1 = turn_sideways(create_variable_definition_from_base(
    type='truck_1',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['truck_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TRUCK_1.untrainedShape = True
_TRUCK_1_NOVEL_SIZE = turn_sideways(create_variable_definition_from_base(
    type='truck_1',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['truck_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TRUCK_1_NOVEL_SIZE.untrainedSize = True


_TRUCK_2 = turn_sideways(create_variable_definition_from_base(
    type='truck_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['truck_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TRUCK_2.untrainedShape = True
_TRUCK_2_NOVEL_SIZE = turn_sideways(create_variable_definition_from_base(
    type='truck_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['truck_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TRUCK_2_NOVEL_SIZE.untrainedSize = True


# Only use rollable objects in move-across setups.
_MOVE_ACROSS_BASIC = [
    _CYLINDER,
    _SPHERE,
    _TUBE_NARROW,
    _TUBE_WIDE,
    _CYLINDER_NOVEL_SIZE,
    _SPHERE_NOVEL_SIZE,
    _TUBE_NARROW_NOVEL_SIZE,
    _TUBE_WIDE_NOVEL_SIZE,
    # Eval 4 novel objects
    _DOUBLE_CONE,
    _DOUBLE_CONE_NOVEL_SIZE,
    _DUMBBELL_1,
    _DUMBBELL_1_NOVEL_SIZE,
    _DUMBBELL_2,
    _DUMBBELL_2_NOVEL_SIZE,
    _TIE_FIGHTER,
    _TIE_FIGHTER_NOVEL_SIZE,
]

_FALL_DOWN_BASIC = _MOVE_ACROSS_BASIC + [
    _CIRCLE_FRUSTUM,
    _CONE,
    _CUBE,
    _RECT_PRISM,
    _PYRAMID,
    _SQUARE_FRUSTUM,
    _CIRCLE_FRUSTUM_NOVEL_SIZE,
    _CONE_NOVEL_SIZE,
    _CUBE_NOVEL_SIZE,
    _RECT_PRISM_NOVEL_SIZE,
    _PYRAMID_NOVEL_SIZE,
    _SQUARE_FRUSTUM_NOVEL_SIZE,
]

# Only use rollable objects in move-across setups.
_MOVE_ACROSS_COMPLEX = [
    _DUCK,
    _TURTLE,
    _RACECAR,
    _SEDAN,
    _TRAIN,
    _TROLLEY,
    _DUCK_NOVEL_SIZE,
    _TURTLE_NOVEL_SIZE,
    _RACECAR_NOVEL_SIZE,
    _SEDAN_NOVEL_SIZE,
    _TRAIN_NOVEL_SIZE,
    _TROLLEY_NOVEL_SIZE,
    # Eval 4 novel objects
    _BUS_1,
    _BUS_1_NOVEL_SIZE,
    _CAR_2,
    _CAR_2_NOVEL_SIZE,
    _CART_2,
    _CART_2_NOVEL_SIZE,
    _DOG_ON_WHEELS,
    _DOG_ON_WHEELS_NOVEL_SIZE,
    _TRUCK_1,
    _TRUCK_1_NOVEL_SIZE,
    _TRUCK_2,
    _TRUCK_2_NOVEL_SIZE,
]

_FALL_DOWN_COMPLEX = _MOVE_ACROSS_COMPLEX.copy()

_MOVE_ACROSS_ALL = _MOVE_ACROSS_BASIC + _MOVE_ACROSS_COMPLEX
_FALL_DOWN_ALL = _FALL_DOWN_BASIC + _FALL_DOWN_COMPLEX


def _get(prop: str) -> Union[ObjectDefinition, List[ObjectDefinition]]:
    """Returns a deep copy of the global property with the given name
    (normally either an object definition or an object definition list)."""
    return copy.deepcopy(globals()['_' + prop])


def _adjust_definition_list_to_opposite_colors(
    definition_list: List[ObjectDefinition]
) -> List[ObjectDefinition]:
    # Override each object definition so its colors/materials can only be
    # chosen from a specific list of opposites.
    for definition in definition_list:
        definition.assign_chosen_material(definition.chooseMaterialList[0])
        materials_count = len(definition.materialCategory)
        definition.materialCategory = (['opposite'] * materials_count)
    return definition_list


_MOVE_ACROSS_OPPOSITE_COLORS = _adjust_definition_list_to_opposite_colors(
    _get('MOVE_ACROSS_ALL')
)
_FALL_DOWN_OPPOSITE_COLORS = _adjust_definition_list_to_opposite_colors(
    _get('FALL_DOWN_ALL')
)


def get_fall_down_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    return get_dataset(
        [_get('FALL_DOWN_ALL')],
        'FALL_DOWN_ALL',
        unshuffled=unshuffled
    )


def get_fall_down_basic_shape_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    return get_dataset(
        [_get('FALL_DOWN_BASIC')],
        'FALL_DOWN_BASIC',
        unshuffled=unshuffled
    )


def get_fall_down_complex_shape_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    return get_dataset(
        [_get('FALL_DOWN_COMPLEX')],
        'FALL_DOWN_COMPLEX',
        unshuffled=unshuffled
    )


def get_fall_down_opposite_colors_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    return get_dataset(
        [_get('FALL_DOWN_OPPOSITE_COLORS')],
        'FALL_DOWN_OPPOSITE_COLORS',
        unshuffled=unshuffled
    )


def get_move_across_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    return get_dataset(
        [_get('MOVE_ACROSS_ALL')],
        'MOVE_ACROSS_ALL',
        unshuffled=unshuffled
    )


def get_move_across_basic_shape_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    return get_dataset(
        [_get('MOVE_ACROSS_BASIC')],
        'MOVE_ACROSS_BASIC',
        unshuffled=unshuffled
    )


def get_move_across_complex_shape_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    return get_dataset(
        [_get('MOVE_ACROSS_COMPLEX')],
        'MOVE_ACROSS_COMPLEX',
        unshuffled=unshuffled
    )


def get_move_across_opposite_colors_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    return get_dataset(
        [_get('MOVE_ACROSS_OPPOSITE_COLORS')],
        'MOVE_ACROSS_OPPOSITE_COLORS',
        unshuffled=unshuffled
    )
