from __future__ import annotations

import copy
from typing import List, Union

from machine_common_sense.config_manager import Vector3d

from .base_objects import create_variable_definition_from_base
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
    size_multiplier_list=[0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_CIRCLE_FRUSTUM_NOVEL = create_variable_definition_from_base(
    type='circle_frustum',
    size_multiplier_list=[0.4, 0.9],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CIRCLE_FRUSTUM_NOVEL.untrainedSize = True


_CONE = create_variable_definition_from_base(
    type='cone',
    size_multiplier_list=[0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CONE_NOVEL = create_variable_definition_from_base(
    type='cone',
    size_multiplier_list=[0.4, 0.9],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CONE_NOVEL.untrainedSize = True


_CUBE = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CUBE_NOVEL = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[0.4, 0.9],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CUBE_NOVEL.untrainedSize = True


_CYLINDER = create_variable_definition_from_base(
    type='cylinder',
    size_multiplier_list=[0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CYLINDER_NOVEL = create_variable_definition_from_base(
    type='cylinder',
    size_multiplier_list=[0.4, 0.9],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_CYLINDER_NOVEL.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_CYLINDER.rotation = Vector3d(90, 0, 0)
_CYLINDER_NOVEL.rotation = Vector3d(90, 0, 0)


_PYRAMID = create_variable_definition_from_base(
    type='pyramid',
    size_multiplier_list=[0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_PYRAMID_NOVEL = create_variable_definition_from_base(
    type='pyramid',
    size_multiplier_list=[0.4, 0.9],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_PYRAMID_NOVEL.untrainedSize = True


_RECT_PRISM = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[
        Vector3d(0.5, 0.25, 0.5),
        Vector3d(0.55, 0.275, 0.55),
        Vector3d(0.6, 0.3, 0.6),
        Vector3d(0.65, 0.325, 0.65),
        Vector3d(0.7, 0.35, 0.7),
        Vector3d(0.75, 0.375, 0.75),
        Vector3d(0.8, 0.4, 0.8)
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RECT_PRISM_NOVEL = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[
        Vector3d(0.4, 0.2, 0.4),
        Vector3d(0.9, 0.45, 0.9)
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RECT_PRISM_NOVEL.untrainedSize = True
# Override the default shape (cube).
_RECT_PRISM.shape = ['rectangular prism']
_RECT_PRISM_NOVEL.shape = ['rectangular prism']


_SPHERE = create_variable_definition_from_base(
    type='sphere',
    size_multiplier_list=[0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SPHERE_NOVEL = create_variable_definition_from_base(
    type='sphere',
    size_multiplier_list=[0.4, 0.9],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SPHERE_NOVEL.untrainedSize = True


_SQUARE_FRUSTUM = create_variable_definition_from_base(
    type='square_frustum',
    size_multiplier_list=[0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SQUARE_FRUSTUM_NOVEL = create_variable_definition_from_base(
    type='square_frustum',
    size_multiplier_list=[0.4, 0.9],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_SQUARE_FRUSTUM_NOVEL.untrainedSize = True


_TUBE_NARROW = create_variable_definition_from_base(
    type='tube_narrow',
    size_multiplier_list=[0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TUBE_NARROW_NOVEL = create_variable_definition_from_base(
    type='tube_narrow',
    size_multiplier_list=[0.4, 0.9],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TUBE_NARROW_NOVEL.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_TUBE_NARROW.rotation = Vector3d(90, 0, 0)
_TUBE_NARROW_NOVEL.rotation = Vector3d(90, 0, 0)


_TUBE_WIDE = create_variable_definition_from_base(
    type='tube_wide',
    size_multiplier_list=[0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TUBE_WIDE_NOVEL = create_variable_definition_from_base(
    type='tube_wide',
    size_multiplier_list=[0.4, 0.9],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TUBE_WIDE_NOVEL.untrainedSize = True
# Rotate the object onto its curved side so it can roll sideways.
_TUBE_WIDE.rotation = Vector3d(90, 0, 0)
_TUBE_WIDE_NOVEL.rotation = Vector3d(90, 0, 0)


_DUCK = create_variable_definition_from_base(
    type='duck_on_wheels',
    size_multiplier_list=[3.25, 3.5, 3.75, 4, 4.25, 4.5, 4.75, 5, 5.25],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUCK_NOVEL = create_variable_definition_from_base(
    type='duck_on_wheels',
    size_multiplier_list=[2.5, 5.75],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_DUCK_NOVEL.untrainedSize = True


_TURTLE = create_variable_definition_from_base(
    type='turtle_on_wheels',
    size_multiplier_list=[2.75, 3, 3.25, 3.5, 3.75, 4, 4.25, 4.5],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)

_TURTLE_NOVEL = create_variable_definition_from_base(
    type='turtle_on_wheels',
    size_multiplier_list=[2.25, 5],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TURTLE_NOVEL.untrainedSize = True


_SEDAN = turn_sideways(create_variable_definition_from_base(
    type='car_1',
    size_multiplier_list=[4.5, 5, 5.5, 6, 6.5, 7],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_SEDAN_NOVEL = turn_sideways(create_variable_definition_from_base(
    type='car_1',
    size_multiplier_list=[3.5, 8],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_SEDAN_NOVEL.untrainedSize = True


_RACECAR = turn_sideways(create_variable_definition_from_base(
    type='racecar_red',
    size_multiplier_list=[4.25, 4.75, 5.25, 5.75, 6.25, 6.75],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_RACECAR_NOVEL = turn_sideways(create_variable_definition_from_base(
    type='racecar_red',
    size_multiplier_list=[3.5, 7.75],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_RACECAR_NOVEL.untrainedSize = True


# TODO MCS-635 Fix dog_on_wheels
# _DOG = {
#     "type": "dog_on_wheels",
#     "shape": ["dog"],
#     "rotation": {
#         "x": 0,
#         # Turn the dog so its side is facing the camera.
#         "y": 90,
#         "z": 0
#     },
#     "chooseSize": [
#         1.5, # novel
#         2,
#         2.25,
#         2.5,
#         2.75,
#         3,
#         3.5, # novel
#     ],
#     "chooseMaterial": [{
#         'debug': {
#             'materialCategory': item['debug']['materialCategory'] * 2,
#         },
#         'salientMaterials': item['salientMaterials']
#     } for item in INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST],
#     "attributes": ["moveable"]
# }


_TRAIN = turn_sideways(create_variable_definition_from_base(
    type='train_1',
    size_multiplier_list=[2.5, 2.75, 3, 3.25, 3.5, 3.75, 4],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TRAIN_NOVEL = turn_sideways(create_variable_definition_from_base(
    type='train_1',
    size_multiplier_list=[2, 4.5],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TRAIN_NOVEL.untrainedSize = True


_TROLLEY = turn_sideways(create_variable_definition_from_base(
    type='trolley_1',
    size_multiplier_list=[2.5, 2.75, 3, 3.25, 3.5, 3.75, 4],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TROLLEY_NOVEL = turn_sideways(create_variable_definition_from_base(
    type='trolley_1',
    size_multiplier_list=[2, 4.5],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
))
_TROLLEY_NOVEL.untrainedSize = True


# TODO MCS-635 Fix truck_1
# _TRUCK = {
#     "type": "truck_1",
#     "shape": ["truck"],
#     "rotation": {
#         "x": 0,
#         # Turn the truck so its side is facing the camera.
#         "y": 90,
#         "z": 0
#     },
#     "chooseSize": [
#         1.75, # novel
#         2.25,
#         2.5,
#         2.75,
#         3,
#         3.25,
#         3.5,
#         4, # novel
#     ],
#     "chooseMaterial": [{
#         'debug': {
#             'materialCategory': item['debug']['materialCategory'] * 2,
#         },
#         'salientMaterials': item['salientMaterials']
#     } for item in INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST],
#     "attributes": ["moveable"]
# }


# Only use rollable objects in move-across setups.
_MOVE_ACROSS_BASIC = [
    _CYLINDER,
    _SPHERE,
    _TUBE_NARROW,
    _TUBE_WIDE,
    _CYLINDER_NOVEL,
    _SPHERE_NOVEL,
    _TUBE_NARROW_NOVEL,
    _TUBE_WIDE_NOVEL
]

_FALL_DOWN_BASIC = _MOVE_ACROSS_BASIC + [
    _CIRCLE_FRUSTUM,
    _CONE,
    _CUBE,
    _RECT_PRISM,
    _PYRAMID,
    _SQUARE_FRUSTUM,
    _CIRCLE_FRUSTUM_NOVEL,
    _CONE_NOVEL,
    _CUBE_NOVEL,
    _RECT_PRISM_NOVEL,
    _PYRAMID_NOVEL,
    _SQUARE_FRUSTUM_NOVEL
]

# Only use rollable objects in move-across setups.
_MOVE_ACROSS_COMPLEX = [
    _DUCK,
    _TURTLE,
    _RACECAR,
    _SEDAN,
    _TRAIN,
    _TROLLEY,
    _DUCK_NOVEL,
    _TURTLE_NOVEL,
    _RACECAR_NOVEL,
    _SEDAN_NOVEL,
    _TRAIN_NOVEL,
    _TROLLEY_NOVEL
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
