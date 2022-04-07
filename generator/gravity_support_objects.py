import copy
from typing import List, Union

from machine_common_sense.config_manager import Vector3d
from shapely import geometry

from .base_objects import create_variable_definition_from_base
from .definitions import (
    ChosenMaterial,
    DefinitionDataset,
    ObjectDefinition,
    finalize_object_definition,
    get_dataset,
)
from .intuitive_physics_objects import (
    INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST,
)

_VISIBLE_SUPPORT = create_variable_definition_from_base(
    type='cube',
    attributes_overrides=['kinematic', 'structure'],
    size_multiplier_list=[
        Vector3d(x=0.6, y=0.6, z=1),
        Vector3d(x=0.7, y=0.6, z=1),
        Vector3d(x=0.8, y=0.6, z=1),
        Vector3d(x=0.9, y=0.6, z=1),
        Vector3d(x=1, y=0.6, z=1),
        Vector3d(x=0.6, y=0.7, z=1),
        Vector3d(x=0.7, y=0.7, z=1),
        Vector3d(x=0.8, y=0.7, z=1),
        Vector3d(x=0.9, y=0.7, z=1),
        Vector3d(x=1, y=0.7, z=1),
        Vector3d(x=0.6, y=0.8, z=1),
        Vector3d(x=0.7, y=0.8, z=1),
        Vector3d(x=0.8, y=0.8, z=1),
        Vector3d(x=0.9, y=0.8, z=1),
        Vector3d(x=1, y=0.8, z=1),
        Vector3d(x=0.6, y=0.9, z=1),
        Vector3d(x=0.7, y=0.9, z=1),
        Vector3d(x=0.8, y=0.9, z=1),
        Vector3d(x=0.9, y=0.9, z=1),
        Vector3d(x=1, y=0.9, z=1),
        Vector3d(x=0.6, y=1, z=1),
        Vector3d(x=0.7, y=1, z=1),
        Vector3d(x=0.8, y=1, z=1),
        Vector3d(x=0.9, y=1, z=1),
        Vector3d(x=1, y=1, z=1),
        Vector3d(x=0.6, y=1.1, z=1),
        Vector3d(x=0.7, y=1.1, z=1),
        Vector3d(x=0.8, y=1.1, z=1),
        Vector3d(x=0.9, y=1.1, z=1),
        Vector3d(x=1, y=1.1, z=1),
        Vector3d(x=0.6, y=1.2, z=1),
        Vector3d(x=0.7, y=1.2, z=1),
        Vector3d(x=0.8, y=1.2, z=1),
        Vector3d(x=0.9, y=1.2, z=1),
        Vector3d(x=1, y=1.2, z=1),
        Vector3d(x=0.6, y=1.3, z=1),
        Vector3d(x=0.7, y=1.3, z=1),
        Vector3d(x=0.8, y=1.3, z=1),
        Vector3d(x=0.9, y=1.3, z=1),
        Vector3d(x=1, y=1.3, z=1),
        Vector3d(x=0.6, y=1.4, z=1),
        Vector3d(x=0.7, y=1.4, z=1),
        Vector3d(x=0.8, y=1.4, z=1),
        Vector3d(x=0.9, y=1.4, z=1),
        Vector3d(x=1, y=1.4, z=1),
        Vector3d(x=0.6, y=1.5, z=1),
        Vector3d(x=0.7, y=1.5, z=1),
        Vector3d(x=0.8, y=1.5, z=1),
        Vector3d(x=0.9, y=1.5, z=1),
        Vector3d(x=1, y=1.5, z=1)
    ],
    # This object's materials and salientMaterials will be set manually.
    chosen_material_list=[ChosenMaterial.NONE]
)
_VISIBLE_SUPPORT.massMultiplier = 100


_LETTER_L_NARROW_TALL = create_variable_definition_from_base(
    type='letter_l_narrow',
    size_multiplier_list=[1, 1.2, 1.4, 1.6, 1.8, 2],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_LETTER_L_WIDE = create_variable_definition_from_base(
    type='letter_l_wide',
    size_multiplier_list=[0.5, 0.6, 0.7, 0.8, 0.9, 1],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_LETTER_L_WIDE_TALL = create_variable_definition_from_base(
    type='letter_l_wide_tall',
    size_multiplier_list=[0.5, 0.6, 0.7, 0.8, 0.9, 1],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_TRIANGLE_90_45_45_ISOSCELES = create_variable_definition_from_base(
    type='triangle',
    size_multiplier_list=[0.5, 0.6, 0.7, 0.8, 0.9, 1],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRIANGLE_90_45_45_ISOSCELES.rotation = Vector3d(x=0, y=-90, z=0)
_TRIANGLE_90_45_45_ISOSCELES.prettyName = 'triangle_isosceles'
_TRIANGLE_90_45_45_ISOSCELES.poly = geometry.Polygon([
    (0.5, -0.5),
    (-0.5, -0.5),
    (-0.5, 0.5)
])


_TRIANGLE_90_60_30_TALL = create_variable_definition_from_base(
    type='triangle',
    size_multiplier_list=[
        Vector3d(x=0.5, y=1, z=0.5),
        Vector3d(x=0.6, y=1.2, z=0.6),
        Vector3d(x=0.7, y=1.4, z=0.7),
        Vector3d(x=0.8, y=1.6, z=0.8),
        Vector3d(x=0.9, y=1.8, z=0.9),
        Vector3d(x=1, y=2, z=1)
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRIANGLE_90_60_30_TALL.rotation = Vector3d(x=0, y=-90, z=0)
_TRIANGLE_90_60_30_TALL.prettyName = 'triangle_tall'
_TRIANGLE_90_60_30_TALL.poly = geometry.Polygon([
    (0.5, -0.5),
    (-0.5, -0.5),
    (-0.5, 0.5)
])


_TRIANGLE_90_60_30_WIDE = create_variable_definition_from_base(
    type='triangle',
    size_multiplier_list=[
        Vector3d(x=0.5, y=0.25, z=0.5),
        Vector3d(x=0.6, y=0.3, z=0.6),
        Vector3d(x=0.7, y=0.35, z=0.7),
        Vector3d(x=0.8, y=0.4, z=0.8),
        Vector3d(x=0.9, y=0.45, z=0.9),
        Vector3d(x=1, y=0.5, z=1)
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRIANGLE_90_60_30_WIDE.rotation = Vector3d(x=0, y=-90, z=0)
_TRIANGLE_90_60_30_WIDE.prettyName = 'triangle_wide'
_TRIANGLE_90_60_30_WIDE.poly = geometry.Polygon([
    (0.5, -0.5),
    (-0.5, -0.5),
    (-0.5, 0.5)
])


_CIRCLE_FRUSTUM = create_variable_definition_from_base(
    type='circle_frustum',
    size_multiplier_list=[0.5, 0.6, 0.7, 0.8, 0.9, 1],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_CONE = create_variable_definition_from_base(
    type='cone',
    size_multiplier_list=[0.5, 0.6, 0.7, 0.8, 0.9, 1],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_CUBE = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[0.5, 0.6, 0.7, 0.8, 0.9, 1],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_CYLINDER = create_variable_definition_from_base(
    type='cylinder',
    size_multiplier_list=[0.5, 0.6, 0.7, 0.8, 0.9, 1],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_PYRAMID = create_variable_definition_from_base(
    type='pyramid',
    size_multiplier_list=[0.5, 0.6, 0.7, 0.8, 0.9, 1],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_RECTANGULAR_PRISM_THIN = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[
        Vector3d(x=0.5, y=0.5 * 0.55, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.6, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.65, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.7, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.75, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.8, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.85, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.9, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.95, z=0.5),
        Vector3d(x=0.5, y=0.5 * 1, z=0.5),
        Vector3d(x=0.6, y=0.5 * 0.65, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.7, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.75, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.8, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.85, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.9, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.95, z=0.6),
        Vector3d(x=0.6, y=0.5 * 1, z=0.6),
        Vector3d(x=0.7, y=0.5 * 0.75, z=0.7),
        Vector3d(x=0.7, y=0.5 * 0.8, z=0.7),
        Vector3d(x=0.7, y=0.5 * 0.85, z=0.7),
        Vector3d(x=0.7, y=0.5 * 0.9, z=0.7),
        Vector3d(x=0.7, y=0.5 * 0.95, z=0.7),
        Vector3d(x=0.7, y=0.5 * 1, z=0.7),
        Vector3d(x=0.8, y=0.5 * 0.85, z=0.8),
        Vector3d(x=0.8, y=0.5 * 0.9, z=0.8),
        Vector3d(x=0.8, y=0.5 * 0.95, z=0.8),
        Vector3d(x=0.8, y=0.5 * 1, z=0.8),
        Vector3d(x=0.9, y=0.5 * 0.95, z=0.9),
        Vector3d(x=0.9, y=0.5 * 1, z=0.9)
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RECTANGULAR_PRISM_THIN.prettyName = 'rect_thin'


_RECTANGULAR_PRISM_WIDE = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[
        Vector3d(x=0.5, y=0.5 * 0.25, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.3, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.35, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.4, z=0.5),
        Vector3d(x=0.5, y=0.5 * 0.45, z=0.5),
        Vector3d(x=0.6, y=0.5 * 0.3, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.35, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.4, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.45, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.5, z=0.6),
        Vector3d(x=0.6, y=0.5 * 0.55, z=0.6),
        Vector3d(x=0.7, y=0.5 * 0.35, z=0.7),
        Vector3d(x=0.7, y=0.5 * 0.4, z=0.7),
        Vector3d(x=0.7, y=0.5 * 0.45, z=0.7),
        Vector3d(x=0.7, y=0.5 * 0.5, z=0.7),
        Vector3d(x=0.7, y=0.5 * 0.55, z=0.7),
        Vector3d(x=0.7, y=0.5 * 0.6, z=0.7),
        Vector3d(x=0.7, y=0.5 * 0.65, z=0.7),
        Vector3d(x=0.8, y=0.5 * 0.4, z=0.8),
        Vector3d(x=0.8, y=0.5 * 0.45, z=0.8),
        Vector3d(x=0.8, y=0.5 * 0.5, z=0.8),
        Vector3d(x=0.8, y=0.5 * 0.55, z=0.8),
        Vector3d(x=0.8, y=0.5 * 0.6, z=0.8),
        Vector3d(x=0.8, y=0.5 * 0.65, z=0.8),
        Vector3d(x=0.8, y=0.5 * 0.7, z=0.8),
        Vector3d(x=0.8, y=0.5 * 0.75, z=0.8),
        Vector3d(x=0.9, y=0.5 * 0.45, z=0.9),
        Vector3d(x=0.9, y=0.5 * 0.5, z=0.9),
        Vector3d(x=0.9, y=0.5 * 0.55, z=0.9),
        Vector3d(x=0.9, y=0.5 * 0.6, z=0.9),
        Vector3d(x=0.9, y=0.5 * 0.65, z=0.9),
        Vector3d(x=0.9, y=0.5 * 0.7, z=0.9),
        Vector3d(x=0.9, y=0.5 * 0.75, z=0.9),
        Vector3d(x=0.9, y=0.5 * 0.8, z=0.9),
        Vector3d(x=0.9, y=0.5 * 0.85, z=0.9),
        Vector3d(x=1, y=0.5 * 0.5, z=1),
        Vector3d(x=1, y=0.5 * 0.55, z=1),
        Vector3d(x=1, y=0.5 * 0.6, z=1),
        Vector3d(x=1, y=0.5 * 0.65, z=1),
        Vector3d(x=1, y=0.5 * 0.7, z=1),
        Vector3d(x=1, y=0.5 * 0.75, z=1),
        Vector3d(x=1, y=0.5 * 0.8, z=1),
        Vector3d(x=1, y=0.5 * 0.85, z=1),
        Vector3d(x=1, y=0.5 * 0.9, z=1),
        Vector3d(x=1, y=0.5 * 0.95, z=1)
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RECTANGULAR_PRISM_WIDE.prettyName = 'rect_wide'


_SQUARE_FRUSTUM = create_variable_definition_from_base(
    type='square_frustum',
    size_multiplier_list=[0.5, 0.6, 0.7, 0.8, 0.9, 1],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_ASYMMETRIC_TARGET_LIST = [
    _LETTER_L_WIDE,
    _LETTER_L_WIDE_TALL,
    _TRIANGLE_90_45_45_ISOSCELES,
    _TRIANGLE_90_60_30_TALL,
    _TRIANGLE_90_60_30_WIDE
]


_SYMMETRIC_TARGET_LIST = [
    _CIRCLE_FRUSTUM,
    _CONE,
    _CUBE,
    _CYLINDER,
    _PYRAMID,
    _RECTANGULAR_PRISM_THIN,
    _RECTANGULAR_PRISM_WIDE,
    _SQUARE_FRUSTUM
]


def _get(prop: str) -> Union[ObjectDefinition, List[ObjectDefinition]]:
    """Returns a deep copy of the global property with the given name
    (normally either an object definition or an object definition list)."""
    return copy.deepcopy(globals()['_' + prop])


def get_asymmetric_target_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all asymmetric definitions."""
    return get_dataset(
        [_get('ASYMMETRIC_TARGET_LIST')],
        'ASYMMETRIC_TARGET_LIST',
        unshuffled=unshuffled
    )


def get_symmetric_target_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all symmetric definitions."""
    return get_dataset(
        [_get('SYMMETRIC_TARGET_LIST')],
        'SYMMETRIC_TARGET_LIST',
        unshuffled=unshuffled
    )


def get_visible_support_object_definition(
    min_x: float = 0
) -> ObjectDefinition:
    """Returns a new visible support object definition with a random size for a
    target object of the given X size."""
    visible_support = _get('VISIBLE_SUPPORT')
    visible_support.chooseSizeList = [
        size for size in visible_support.chooseSizeList
        if size.dimensions.x >= min_x
    ]
    return finalize_object_definition(visible_support)
