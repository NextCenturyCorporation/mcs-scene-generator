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
    get_dataset
)

# Common material options used by all intuitive physics objects.
# Add some extra mass to all intuitive physics objects.
INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST: List[ChosenMaterial] = [
    ChosenMaterial.INTUITIVE_PHYSICS_BLOCK,
    ChosenMaterial.INTUITIVE_PHYSICS_PLASTIC,
    ChosenMaterial.INTUITIVE_PHYSICS_WOOD
]


TRAINED_SIZE_MULTIPLIER_LIST = [
    0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85
]
# Novel sizes currently for Eval 5.
NOVEL_SIZE_MULTIPLIER_LIST = [0.35, 0.9]


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
    ('bobcat', base_objects._TOY_BOBCAT_SIZE),
    ('bus_1', base_objects._TOY_BUS_1_SIZE),
    ('car_1', base_objects._TOY_SEDAN_SIZE),
    ('car_2', base_objects._TOY_CAR_2_SIZE),
    ('car_3', base_objects._TOY_CAR_3_SIZE),
    ('car_4', base_objects._TOY_CAR_4_SIZE),
    ('car_5', base_objects._TOY_CAR_5_SIZE),
    ('car_6', base_objects._TOY_CAR_6_SIZE),
    ('cart_2', base_objects._CART_2_SIZE),
    ('dog_on_wheels', base_objects._DOG_ON_WHEELS_SIZE),
    ('dog_on_wheels_2', base_objects._DOG_ON_WHEELS_2_SIZE),
    ('duck_on_wheels', base_objects._DUCK_ON_WHEELS_SIZE),
    ('duck_on_wheels_2', base_objects._DUCK_ON_WHEELS_2_SIZE),
    ('firetruck', base_objects._TOY_FIRETRUCK_SIZE),
    ('jeep', base_objects._TOY_JEEP_SIZE),
    ('military_truck', base_objects._TOY_MILITARY_TRUCK_SIZE),
    ('power_shovel', base_objects._TOY_POWER_SHOVEL_SIZE),
    ('racecar_red', base_objects._TOY_RACECAR_SIZE),
    ('racecar_2', base_objects._TOY_RACECAR_2_SIZE),
    ('racecar_3', base_objects._TOY_RACECAR_3_SIZE),
    ('road_scraper', base_objects._TOY_ROAD_SCRAPER_SIZE),
    ('roller', base_objects._TOY_ROLLER_SIZE),
    ('skateboard', base_objects._SKATEBOARD_SIZE),
    ('tank_1', base_objects._TOY_TANK_1_SIZE),
    ('tank_2', base_objects._TOY_TANK_2_SIZE),
    ('tank_3', base_objects._TOY_TANK_3_SIZE),
    ('taxi', base_objects._TOY_TAXI_SIZE),
    ('toddler_ride_on_car', base_objects._TODDLER_RIDE_ON_CAR_SIZE),
    ('train_1', base_objects._TOY_TRAIN_1_SIZE),
    ('train_2', base_objects._TOY_TRAIN_2_SIZE),
    ('train_3', base_objects._TOY_TRAIN_3_SIZE),
    ('train_4', base_objects._TOY_TRAIN_4_SIZE),
    ('train_5', base_objects._TOY_TRAIN_5_SIZE),
    ('train_6', base_objects._TOY_TRAIN_6_SIZE),
    ('trike', base_objects._TOY_TRIKE_SIZE),
    ('trolley_1', base_objects._TOY_TROLLEY_SIZE),
    ('truck_1', base_objects._TOY_TRUCK_1_SIZE),
    ('truck_2', base_objects._TOY_TRUCK_2_SIZE),
    ('truck_3', base_objects._TOY_TRUCK_3_SIZE),
    ('truck_4', base_objects._TOY_TRUCK_4_SIZE),
    ('truck_5', base_objects._TOY_TRUCK_5_SIZE),
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
_CYLINDER_SIDEWAYS = copy.deepcopy(_CYLINDER)
_CYLINDER_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_CYLINDER_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_CYLINDER_NOVEL_SIZE)
_CYLINDER_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


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
        Vector3d(x=multiplier, y=multiplier / 2.0, z=multiplier)
        for multiplier in TRAINED_SIZE_MULTIPLIER_LIST
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RECT_PRISM_NOVEL_SIZE = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[
        Vector3d(x=multiplier, y=multiplier / 2.0, z=multiplier)
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
_TUBE_NARROW_SIDEWAYS = copy.deepcopy(_TUBE_NARROW)
_TUBE_NARROW_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_TUBE_NARROW_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_TUBE_NARROW_NOVEL_SIZE)
_TUBE_NARROW_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


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
_TUBE_WIDE_SIDEWAYS = copy.deepcopy(_TUBE_WIDE)
_TUBE_WIDE_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_TUBE_WIDE_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_TUBE_WIDE_NOVEL_SIZE)
_TUBE_WIDE_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


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


_SEDAN = create_variable_definition_from_base(
    type='car_1',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['car_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SEDAN_NOVEL_SIZE = create_variable_definition_from_base(
    type='car_1',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['car_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SEDAN_NOVEL_SIZE.untrainedSize = True


_RACECAR = create_variable_definition_from_base(
    type='racecar_red',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['racecar_red'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RACECAR_NOVEL_SIZE = create_variable_definition_from_base(
    type='racecar_red',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['racecar_red'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RACECAR_NOVEL_SIZE.untrainedSize = True


_TRAIN_1 = create_variable_definition_from_base(
    type='train_1',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['train_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_1_NOVEL_SIZE = create_variable_definition_from_base(
    type='train_1',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['train_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_1_NOVEL_SIZE.untrainedSize = True


_TROLLEY = create_variable_definition_from_base(
    type='trolley_1',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['trolley_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TROLLEY_NOVEL_SIZE = create_variable_definition_from_base(
    type='trolley_1',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['trolley_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TROLLEY_NOVEL_SIZE.untrainedSize = True


# EVAL 4 NOVEL OBJECTS


_DUMBBELL_1 = create_variable_definition_from_base(
    type='dumbbell_1',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUMBBELL_1_NOVEL_SIZE = create_variable_definition_from_base(
    type='dumbbell_1',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUMBBELL_1_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_DUMBBELL_1_SIDEWAYS = copy.deepcopy(_DUMBBELL_1)
_DUMBBELL_1_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_DUMBBELL_1_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_DUMBBELL_1_NOVEL_SIZE)
_DUMBBELL_1_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_DUMBBELL_2 = create_variable_definition_from_base(
    type='dumbbell_2',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUMBBELL_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='dumbbell_2',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUMBBELL_2_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_DUMBBELL_2_SIDEWAYS = copy.deepcopy(_DUMBBELL_2)
_DUMBBELL_2_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_DUMBBELL_2_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_DUMBBELL_2_NOVEL_SIZE)
_DUMBBELL_2_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_TIE_FIGHTER = create_variable_definition_from_base(
    type='tie_fighter',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TIE_FIGHTER_NOVEL_SIZE = create_variable_definition_from_base(
    type='tie_fighter',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TIE_FIGHTER_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_TIE_FIGHTER_SIDEWAYS = copy.deepcopy(_TIE_FIGHTER)
_TIE_FIGHTER_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_TIE_FIGHTER_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_TIE_FIGHTER_NOVEL_SIZE)
_TIE_FIGHTER_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_BUS_1 = create_variable_definition_from_base(
    type='bus_1',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['bus_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_BUS_1_NOVEL_SIZE = create_variable_definition_from_base(
    type='bus_1',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['bus_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_BUS_1_NOVEL_SIZE.untrainedSize = True


_CAR_2 = create_variable_definition_from_base(
    type='car_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['car_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CAR_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='car_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['car_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CAR_2_NOVEL_SIZE.untrainedSize = True


_CART_2 = create_variable_definition_from_base(
    type='cart_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['cart_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CART_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='cart_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['cart_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CART_2_NOVEL_SIZE.untrainedSize = True


_DOG = create_variable_definition_from_base(
    type='dog_on_wheels',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['dog_on_wheels'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DOG_NOVEL_SIZE = create_variable_definition_from_base(
    type='dog_on_wheels',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['dog_on_wheels'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DOG_NOVEL_SIZE.untrainedSize = True


_TRUCK_2 = create_variable_definition_from_base(
    type='truck_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['truck_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRUCK_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='truck_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['truck_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRUCK_2_NOVEL_SIZE.untrainedSize = True


# EVAL 5 NOVEL OBJECTS


_ROLLABLE_1 = create_variable_definition_from_base(
    type='rollable_1',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_1_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_1',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_1_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_1_SIDEWAYS = copy.deepcopy(_ROLLABLE_1)
_ROLLABLE_1_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_1_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_1_NOVEL_SIZE)
_ROLLABLE_1_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_ROLLABLE_2 = create_variable_definition_from_base(
    type='rollable_2',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_2',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_2_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_2_SIDEWAYS = copy.deepcopy(_ROLLABLE_2)
_ROLLABLE_2_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_2_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_2_NOVEL_SIZE)
_ROLLABLE_2_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_ROLLABLE_3 = create_variable_definition_from_base(
    type='rollable_3',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_3_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_3',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_3_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_3_SIDEWAYS = copy.deepcopy(_ROLLABLE_3)
_ROLLABLE_3_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_3_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_3_NOVEL_SIZE)
_ROLLABLE_3_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_ROLLABLE_4 = create_variable_definition_from_base(
    type='rollable_4',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_4_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_4',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_4_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_4_SIDEWAYS = copy.deepcopy(_ROLLABLE_4)
_ROLLABLE_4_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_4_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_4_NOVEL_SIZE)
_ROLLABLE_4_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_BOBCAT = create_variable_definition_from_base(
    type='bobcat',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['bobcat'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_BOBCAT_NOVEL_SIZE = create_variable_definition_from_base(
    type='bobcat',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['bobcat'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_BOBCAT_NOVEL_SIZE.untrainedSize = True


_CAR_3 = create_variable_definition_from_base(
    type='car_3',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['car_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CAR_3_NOVEL_SIZE = create_variable_definition_from_base(
    type='car_3',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['car_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CAR_3_NOVEL_SIZE.untrainedSize = True


_DOG_2 = create_variable_definition_from_base(
    type='dog_on_wheels_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['dog_on_wheels_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DOG_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='dog_on_wheels_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['dog_on_wheels_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DOG_2_NOVEL_SIZE.untrainedSize = True


_DUCK_2 = create_variable_definition_from_base(
    type='duck_on_wheels_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['duck_on_wheels_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUCK_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='duck_on_wheels_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['duck_on_wheels_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUCK_2_NOVEL_SIZE.untrainedSize = True


_JEEP = create_variable_definition_from_base(
    type='jeep',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['jeep'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_JEEP_NOVEL_SIZE = create_variable_definition_from_base(
    type='jeep',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['jeep'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_JEEP_NOVEL_SIZE.untrainedSize = True


_ROLLER = create_variable_definition_from_base(
    type='roller',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['roller'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLER_NOVEL_SIZE = create_variable_definition_from_base(
    type='roller',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['roller'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLER_NOVEL_SIZE.untrainedSize = True


_SKATEBOARD = create_variable_definition_from_base(
    type='skateboard',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['skateboard'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SKATEBOARD_NOVEL_SIZE = create_variable_definition_from_base(
    type='skateboard',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['skateboard'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SKATEBOARD_NOVEL_SIZE.untrainedSize = True


_TANK_1 = create_variable_definition_from_base(
    type='tank_1',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['tank_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TANK_1_NOVEL_SIZE = create_variable_definition_from_base(
    type='tank_1',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['tank_1'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TANK_1_NOVEL_SIZE.untrainedSize = True


_TANK_2 = create_variable_definition_from_base(
    type='tank_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['tank_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TANK_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='tank_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['tank_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TANK_2_NOVEL_SIZE.untrainedSize = True


_TRAIN_2 = create_variable_definition_from_base(
    type='train_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['train_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='train_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['train_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_2_NOVEL_SIZE.untrainedSize = True


_TRUCK_3 = create_variable_definition_from_base(
    type='truck_3',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['truck_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRUCK_3_NOVEL_SIZE = create_variable_definition_from_base(
    type='truck_3',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['truck_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRUCK_3_NOVEL_SIZE.untrainedSize = True


_TRUCK_4 = create_variable_definition_from_base(
    type='truck_4',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['truck_4'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRUCK_4_NOVEL_SIZE = create_variable_definition_from_base(
    type='truck_4',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['truck_4'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRUCK_4_NOVEL_SIZE.untrainedSize = True


# EVAL 6 NOVEL OBJECTS


_ROLLABLE_5 = create_variable_definition_from_base(
    type='rollable_5',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_5_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_5',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_5_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_5_SIDEWAYS = copy.deepcopy(_ROLLABLE_5)
_ROLLABLE_5_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_5_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_5_NOVEL_SIZE)
_ROLLABLE_5_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_ROLLABLE_6 = create_variable_definition_from_base(
    type='rollable_6',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_6_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_6',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_6_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_6_SIDEWAYS = copy.deepcopy(_ROLLABLE_6)
_ROLLABLE_6_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_6_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_6_NOVEL_SIZE)
_ROLLABLE_6_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_ROLLABLE_7 = create_variable_definition_from_base(
    type='rollable_7',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_7_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_7',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_7_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_7_SIDEWAYS = copy.deepcopy(_ROLLABLE_7)
_ROLLABLE_7_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_7_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_7_NOVEL_SIZE)
_ROLLABLE_7_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_ROLLABLE_8 = create_variable_definition_from_base(
    type='rollable_8',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_8_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_8',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_8_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_8_SIDEWAYS = copy.deepcopy(_ROLLABLE_8)
_ROLLABLE_8_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_8_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_8_NOVEL_SIZE)
_ROLLABLE_8_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_CAR_4 = create_variable_definition_from_base(
    type='car_4',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['car_4'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CAR_4_NOVEL_SIZE = create_variable_definition_from_base(
    type='car_4',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['car_4'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CAR_4_NOVEL_SIZE.untrainedSize = True


_CAR_5 = create_variable_definition_from_base(
    type='car_5',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['car_5'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CAR_5_NOVEL_SIZE = create_variable_definition_from_base(
    type='car_5',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['car_5'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CAR_5_NOVEL_SIZE.untrainedSize = True


_POWER_SHOVEL = create_variable_definition_from_base(
    type='power_shovel',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['power_shovel'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_POWER_SHOVEL_NOVEL_SIZE = create_variable_definition_from_base(
    type='power_shovel',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['power_shovel'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_POWER_SHOVEL_NOVEL_SIZE.untrainedSize = True


_ROAD_SCRAPER = create_variable_definition_from_base(
    type='road_scraper',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['road_scraper'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROAD_SCRAPER_NOVEL_SIZE = create_variable_definition_from_base(
    type='road_scraper',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['road_scraper'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROAD_SCRAPER_NOVEL_SIZE.untrainedSize = True


_TANK_3 = create_variable_definition_from_base(
    type='tank_3',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['tank_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TANK_3_NOVEL_SIZE = create_variable_definition_from_base(
    type='tank_3',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['tank_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TANK_3_NOVEL_SIZE.untrainedSize = True


_TANK_3 = create_variable_definition_from_base(
    type='tank_3',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['tank_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TANK_3_NOVEL_SIZE = create_variable_definition_from_base(
    type='tank_3',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['tank_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TANK_3_NOVEL_SIZE.untrainedSize = True


_TRAIN_3 = create_variable_definition_from_base(
    type='train_3',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['train_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_3_NOVEL_SIZE = create_variable_definition_from_base(
    type='train_3',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['train_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_3_NOVEL_SIZE.untrainedSize = True


_TRIKE = create_variable_definition_from_base(
    type='trike',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['trike'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRIKE_NOVEL_SIZE = create_variable_definition_from_base(
    type='trike',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['trike'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRIKE_NOVEL_SIZE.untrainedSize = True


_TRUCK_5 = create_variable_definition_from_base(
    type='truck_5',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['truck_5'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRUCK_5_NOVEL_SIZE = create_variable_definition_from_base(
    type='truck_5',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['truck_5'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRUCK_5_NOVEL_SIZE.untrainedSize = True


# EVAL 7 NOVEL OBJECTS


_ROLLABLE_9 = create_variable_definition_from_base(
    type='rollable_9',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_9.untrainedShape = True
_ROLLABLE_9_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_9',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_9_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_9_SIDEWAYS = copy.deepcopy(_ROLLABLE_9)
_ROLLABLE_9_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_9_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_9_NOVEL_SIZE)
_ROLLABLE_9_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_ROLLABLE_10 = create_variable_definition_from_base(
    type='rollable_10',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_10.untrainedShape = True
_ROLLABLE_10_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_10',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_10_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_10_SIDEWAYS = copy.deepcopy(_ROLLABLE_10)
_ROLLABLE_10_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_10_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_10_NOVEL_SIZE)
_ROLLABLE_10_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_ROLLABLE_11 = create_variable_definition_from_base(
    type='rollable_11',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_11.untrainedShape = True
_ROLLABLE_11_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_11',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_11_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_11_SIDEWAYS = copy.deepcopy(_ROLLABLE_11)
_ROLLABLE_11_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_11_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_11_NOVEL_SIZE)
_ROLLABLE_11_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_ROLLABLE_12 = create_variable_definition_from_base(
    type='rollable_12',
    size_multiplier_list=TRAINED_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_12.untrainedShape = True
_ROLLABLE_12_NOVEL_SIZE = create_variable_definition_from_base(
    type='rollable_12',
    size_multiplier_list=NOVEL_SIZE_MULTIPLIER_LIST.copy(),
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_ROLLABLE_12_NOVEL_SIZE.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_ROLLABLE_12_SIDEWAYS = copy.deepcopy(_ROLLABLE_12)
_ROLLABLE_12_SIDEWAYS.rotation = Vector3d(x=90, y=0, z=0)
_ROLLABLE_12_SIDEWAYS_NOVEL_SIZE = copy.deepcopy(_ROLLABLE_12_NOVEL_SIZE)
_ROLLABLE_12_SIDEWAYS_NOVEL_SIZE.rotation = Vector3d(x=90, y=0, z=0)


_CAR_6 = create_variable_definition_from_base(
    type='car_6',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['car_6'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CAR_6.untrainedShape = True
_CAR_6_NOVEL_SIZE = create_variable_definition_from_base(
    type='car_6',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['car_6'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CAR_6_NOVEL_SIZE.untrainedSize = True


_FIRETRUCK = create_variable_definition_from_base(
    type='firetruck',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['firetruck'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_FIRETRUCK.untrainedShape = True
_FIRETRUCK_NOVEL_SIZE = create_variable_definition_from_base(
    type='firetruck',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['firetruck'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_FIRETRUCK_NOVEL_SIZE.untrainedSize = True


_RACECAR_2 = create_variable_definition_from_base(
    type='racecar_2',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['racecar_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RACECAR_2.untrainedShape = True
_RACECAR_2_NOVEL_SIZE = create_variable_definition_from_base(
    type='racecar_2',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['racecar_2'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RACECAR_2_NOVEL_SIZE.untrainedSize = True


_RACECAR_3 = create_variable_definition_from_base(
    type='racecar_3',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['racecar_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RACECAR_3.untrainedShape = True
_RACECAR_3_NOVEL_SIZE = create_variable_definition_from_base(
    type='racecar_3',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['racecar_3'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RACECAR_3_NOVEL_SIZE.untrainedSize = True


_MILITARY_TRUCK = create_variable_definition_from_base(
    type='military_truck',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['military_truck'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_MILITARY_TRUCK.untrainedShape = True
_MILITARY_TRUCK_NOVEL_SIZE = create_variable_definition_from_base(
    type='military_truck',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['military_truck'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_MILITARY_TRUCK_NOVEL_SIZE.untrainedSize = True


_TAXI = create_variable_definition_from_base(
    type='taxi',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['taxi'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TAXI.untrainedShape = True
_TAXI_NOVEL_SIZE = create_variable_definition_from_base(
    type='taxi',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['taxi'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TAXI_NOVEL_SIZE.untrainedSize = True


_TODDLER_RIDE_ON_CAR = create_variable_definition_from_base(
    type='toddler_ride_on_car',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['toddler_ride_on_car'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TODDLER_RIDE_ON_CAR.untrainedShape = True
_TODDLER_RIDE_ON_CAR_NOVEL_SIZE = create_variable_definition_from_base(
    type='toddler_ride_on_car',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['toddler_ride_on_car'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TODDLER_RIDE_ON_CAR_NOVEL_SIZE.untrainedSize = True


_TRAIN_4 = create_variable_definition_from_base(
    type='train_4',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['train_4'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_4.untrainedShape = True
_TRAIN_4_NOVEL_SIZE = create_variable_definition_from_base(
    type='train_4',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['train_4'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_4_NOVEL_SIZE.untrainedSize = True


_TRAIN_5 = create_variable_definition_from_base(
    type='train_5',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['train_5'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_5.untrainedShape = True
_TRAIN_5_NOVEL_SIZE = create_variable_definition_from_base(
    type='train_5',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['train_5'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_5_NOVEL_SIZE.untrainedSize = True


_TRAIN_6 = create_variable_definition_from_base(
    type='train_6',
    size_multiplier_list=_COMPLEX_TYPES_TO_SIZES['train_6'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_6.untrainedShape = True
_TRAIN_6_NOVEL_SIZE = create_variable_definition_from_base(
    type='train_6',
    size_multiplier_list=_NOVEL_COMPLEX_TYPES_TO_SIZES['train_6'],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRAIN_6_NOVEL_SIZE.untrainedSize = True


# Only use rollable objects in move-across setups.
_MOVE_ACROSS_BASIC = [
    _CYLINDER_SIDEWAYS,
    _CYLINDER_SIDEWAYS_NOVEL_SIZE,
    _DUMBBELL_1_SIDEWAYS,
    _DUMBBELL_1_SIDEWAYS_NOVEL_SIZE,
    _DUMBBELL_2_SIDEWAYS,
    _DUMBBELL_2_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_1_SIDEWAYS,
    _ROLLABLE_1_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_2_SIDEWAYS,
    _ROLLABLE_2_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_3_SIDEWAYS,
    _ROLLABLE_3_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_4_SIDEWAYS,
    _ROLLABLE_4_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_5_SIDEWAYS,
    _ROLLABLE_5_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_6_SIDEWAYS,
    _ROLLABLE_6_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_7_SIDEWAYS,
    _ROLLABLE_7_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_8_SIDEWAYS,
    _ROLLABLE_8_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_9_SIDEWAYS,
    _ROLLABLE_9_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_10_SIDEWAYS,
    _ROLLABLE_10_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_11_SIDEWAYS,
    _ROLLABLE_11_SIDEWAYS_NOVEL_SIZE,
    _ROLLABLE_12_SIDEWAYS,
    _ROLLABLE_12_SIDEWAYS_NOVEL_SIZE,
    _SPHERE,
    _SPHERE_NOVEL_SIZE,
    _TIE_FIGHTER_SIDEWAYS,
    _TIE_FIGHTER_SIDEWAYS_NOVEL_SIZE,
    _TUBE_NARROW_SIDEWAYS,
    _TUBE_NARROW_SIDEWAYS_NOVEL_SIZE,
    _TUBE_WIDE_SIDEWAYS,
    _TUBE_WIDE_SIDEWAYS_NOVEL_SIZE,
]

_FALL_DOWN_BASIC = [
    # Objects copied from _MOVE_ACROSS_BASIC (not the sideways versions)
    _CYLINDER,
    _SPHERE,
    _TUBE_NARROW,
    _TUBE_WIDE,
    _CYLINDER_NOVEL_SIZE,
    _SPHERE_NOVEL_SIZE,
    _TUBE_NARROW_NOVEL_SIZE,
    _TUBE_WIDE_NOVEL_SIZE,
    _DUMBBELL_1,
    _DUMBBELL_1_NOVEL_SIZE,
    _DUMBBELL_2,
    _DUMBBELL_2_NOVEL_SIZE,
    _ROLLABLE_1,
    _ROLLABLE_1_NOVEL_SIZE,
    _ROLLABLE_2,
    _ROLLABLE_2_NOVEL_SIZE,
    _ROLLABLE_3,
    _ROLLABLE_3_NOVEL_SIZE,
    _ROLLABLE_4,
    _ROLLABLE_4_NOVEL_SIZE,
    _ROLLABLE_5,
    _ROLLABLE_5_NOVEL_SIZE,
    _ROLLABLE_6,
    _ROLLABLE_6_NOVEL_SIZE,
    _ROLLABLE_7,
    _ROLLABLE_7_NOVEL_SIZE,
    _ROLLABLE_8,
    _ROLLABLE_8_NOVEL_SIZE,
    _ROLLABLE_9,
    _ROLLABLE_9_NOVEL_SIZE,
    _ROLLABLE_10,
    _ROLLABLE_10_NOVEL_SIZE,
    _ROLLABLE_11,
    _ROLLABLE_11_NOVEL_SIZE,
    _ROLLABLE_12,
    _ROLLABLE_12_NOVEL_SIZE,
    _TIE_FIGHTER,
    _TIE_FIGHTER_NOVEL_SIZE,
    # Objects specific to _FALL_DOWN_BASIC
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
    _BOBCAT,
    _BOBCAT_NOVEL_SIZE,
    _BUS_1,
    _BUS_1_NOVEL_SIZE,
    _CAR_2,
    _CAR_2_NOVEL_SIZE,
    _CAR_3,
    _CAR_3_NOVEL_SIZE,
    _CAR_4,
    _CAR_4_NOVEL_SIZE,
    _CAR_5,
    _CAR_5_NOVEL_SIZE,
    _CAR_6,
    _CAR_6_NOVEL_SIZE,
    _CART_2,
    _CART_2_NOVEL_SIZE,
    _DOG,
    _DOG_NOVEL_SIZE,
    _DOG_2,
    _DOG_2_NOVEL_SIZE,
    _DUCK,
    _DUCK_NOVEL_SIZE,
    _DUCK_2,
    _DUCK_2_NOVEL_SIZE,
    _FIRETRUCK,
    _FIRETRUCK_NOVEL_SIZE,
    _JEEP,
    _JEEP_NOVEL_SIZE,
    _MILITARY_TRUCK,
    _MILITARY_TRUCK_NOVEL_SIZE,
    _POWER_SHOVEL,
    _POWER_SHOVEL_NOVEL_SIZE,
    _RACECAR,
    _RACECAR_NOVEL_SIZE,
    _RACECAR_2,
    _RACECAR_2_NOVEL_SIZE,
    _RACECAR_3,
    _RACECAR_3_NOVEL_SIZE,
    _ROAD_SCRAPER,
    _ROAD_SCRAPER_NOVEL_SIZE,
    _ROLLER,
    _ROLLER_NOVEL_SIZE,
    _SEDAN,
    _SEDAN_NOVEL_SIZE,
    _SKATEBOARD,
    _SKATEBOARD_NOVEL_SIZE,
    _TANK_1,
    _TANK_1_NOVEL_SIZE,
    _TANK_2,
    _TANK_2_NOVEL_SIZE,
    _TANK_3,
    _TANK_3_NOVEL_SIZE,
    _TAXI,
    _TAXI_NOVEL_SIZE,
    _TODDLER_RIDE_ON_CAR,
    _TODDLER_RIDE_ON_CAR_NOVEL_SIZE,
    _TRAIN_1,
    _TRAIN_1_NOVEL_SIZE,
    _TRAIN_2,
    _TRAIN_2_NOVEL_SIZE,
    _TRAIN_3,
    _TRAIN_3_NOVEL_SIZE,
    _TRAIN_4,
    _TRAIN_4_NOVEL_SIZE,
    _TRAIN_5,
    _TRAIN_5_NOVEL_SIZE,
    _TRAIN_6,
    _TRAIN_6_NOVEL_SIZE,
    _TRIKE,
    _TRIKE_NOVEL_SIZE,
    _TROLLEY,
    _TROLLEY_NOVEL_SIZE,
    _TRUCK_2,
    _TRUCK_2_NOVEL_SIZE,
    _TRUCK_3,
    _TRUCK_3_NOVEL_SIZE,
    _TRUCK_4,
    _TRUCK_4_NOVEL_SIZE,
    _TRUCK_5,
    _TRUCK_5_NOVEL_SIZE,
    _TURTLE,
    _TURTLE_NOVEL_SIZE,
]

_FALL_DOWN_COMPLEX = _MOVE_ACROSS_COMPLEX.copy()

_MOVE_ACROSS_ALL = _MOVE_ACROSS_BASIC + _MOVE_ACROSS_COMPLEX
_FALL_DOWN_ALL = _FALL_DOWN_BASIC + _FALL_DOWN_COMPLEX


# Map each intuitive physics object type (shape) to each size (scale) option.
FALL_DOWN_TYPES_TO_SIZES = {}
MOVE_ACROSS_TYPES_TO_SIZES = {}
for definition in _FALL_DOWN_ALL:
    if definition.type not in FALL_DOWN_TYPES_TO_SIZES:
        FALL_DOWN_TYPES_TO_SIZES[definition.type] = []
    if definition.scale:
        FALL_DOWN_TYPES_TO_SIZES[definition.type].append(definition.scale)
    FALL_DOWN_TYPES_TO_SIZES[definition.type].extend([
        option.scale for option in definition.chooseSizeList
    ])
for definition in _MOVE_ACROSS_ALL:
    if definition.type not in MOVE_ACROSS_TYPES_TO_SIZES:
        MOVE_ACROSS_TYPES_TO_SIZES[definition.type] = []
    if definition.scale:
        MOVE_ACROSS_TYPES_TO_SIZES[definition.type].append(definition.scale)
    MOVE_ACROSS_TYPES_TO_SIZES[definition.type].extend([
        option.scale for option in definition.chooseSizeList
    ])


def _get(prop: str) -> Union[ObjectDefinition, List[ObjectDefinition]]:
    """Returns a deep copy of the global property with the given name
    (normally either an object definition or an object definition list)."""
    return copy.deepcopy(globals()['_' + prop])


def _create_opposite_colors_definition_list(
    definition_list: List[ObjectDefinition]
) -> List[ObjectDefinition]:
    # Override each object definition so its colors/materials can only be
    # chosen from a specific list of opposites.
    for definition in definition_list:
        definition.assign_chosen_material(definition.chooseMaterialList[0])
        materials_count = len(definition.materialCategory)
        definition.materialCategory = (['object_opposite'] * materials_count)
    return definition_list


_MOVE_ACROSS_BASIC_SHAPE_OPPOSITE_COLORS = None
_FALL_DOWN_BASIC_SHAPE_OPPOSITE_COLORS = None
_MOVE_ACROSS_COMPLEX_SHAPE_OPPOSITE_COLORS = None
_FALL_DOWN_COMPLEX_SHAPE_OPPOSITE_COLORS = None


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


def get_fall_down_basic_shape_opposite_colors_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    global _FALL_DOWN_BASIC_SHAPE_OPPOSITE_COLORS
    if not _FALL_DOWN_BASIC_SHAPE_OPPOSITE_COLORS:
        _FALL_DOWN_BASIC_SHAPE_OPPOSITE_COLORS = (
            _create_opposite_colors_definition_list(_get('FALL_DOWN_BASIC'))
        )
    return get_dataset(
        [_get('FALL_DOWN_BASIC_SHAPE_OPPOSITE_COLORS')],
        'FALL_DOWN_BASIC_SHAPE_OPPOSITE_COLORS',
        unshuffled=unshuffled
    )


def get_fall_down_complex_shape_opposite_colors_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    global _FALL_DOWN_COMPLEX_SHAPE_OPPOSITE_COLORS
    if not _FALL_DOWN_COMPLEX_SHAPE_OPPOSITE_COLORS:
        _FALL_DOWN_COMPLEX_SHAPE_OPPOSITE_COLORS = (
            _create_opposite_colors_definition_list(_get('FALL_DOWN_COMPLEX'))
        )
    return get_dataset(
        [_get('FALL_DOWN_COMPLEX_SHAPE_OPPOSITE_COLORS')],
        'FALL_DOWN_COMPLEX_SHAPE_OPPOSITE_COLORS',
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


def get_move_across_basic_shape_opposite_colors_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    global _MOVE_ACROSS_BASIC_SHAPE_OPPOSITE_COLORS
    if not _MOVE_ACROSS_BASIC_SHAPE_OPPOSITE_COLORS:
        _MOVE_ACROSS_BASIC_SHAPE_OPPOSITE_COLORS = (
            _create_opposite_colors_definition_list(_get('MOVE_ACROSS_BASIC'))
        )
    return get_dataset(
        [_get('MOVE_ACROSS_BASIC_SHAPE_OPPOSITE_COLORS')],
        'MOVE_ACROSS_BASIC_SHAPE_OPPOSITE_COLORS',
        unshuffled=unshuffled
    )


def get_move_across_complex_shape_opposite_colors_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of the corresponding intuitive physics
    object definition list."""
    global _MOVE_ACROSS_COMPLEX_SHAPE_OPPOSITE_COLORS
    if not _MOVE_ACROSS_COMPLEX_SHAPE_OPPOSITE_COLORS:
        _MOVE_ACROSS_COMPLEX_SHAPE_OPPOSITE_COLORS = (
            _create_opposite_colors_definition_list(
                _get('MOVE_ACROSS_COMPLEX')
            )
        )
    return get_dataset(
        [_get('MOVE_ACROSS_COMPLEX_SHAPE_OPPOSITE_COLORS')],
        'MOVE_ACROSS_COMPLEX_SHAPE_OPPOSITE_COLORS',
        unshuffled=unshuffled
    )
