import copy
import uuid
from typing import List, Union

from machine_common_sense.config_manager import Vector3d

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

POLE_MOVE_AMOUNT = 0.1
POLE_WAIT_TIME = 1


_VISIBLE_SUPPORT = create_variable_definition_from_base(
    type='cube',
    attributes_overrides=['kinematic', 'structure'],
    size_multiplier_list=[
        Vector3d(0.6, 0.6, 1),
        Vector3d(0.7, 0.6, 1),
        Vector3d(0.8, 0.6, 1),
        Vector3d(0.9, 0.6, 1),
        Vector3d(1, 0.6, 1),
        Vector3d(0.6, 0.7, 1),
        Vector3d(0.7, 0.7, 1),
        Vector3d(0.8, 0.7, 1),
        Vector3d(0.9, 0.7, 1),
        Vector3d(1, 0.7, 1),
        Vector3d(0.6, 0.8, 1),
        Vector3d(0.7, 0.8, 1),
        Vector3d(0.8, 0.8, 1),
        Vector3d(0.9, 0.8, 1),
        Vector3d(1, 0.8, 1),
        Vector3d(0.6, 0.9, 1),
        Vector3d(0.7, 0.9, 1),
        Vector3d(0.8, 0.9, 1),
        Vector3d(0.9, 0.9, 1),
        Vector3d(1, 0.9, 1),
        Vector3d(0.6, 1, 1),
        Vector3d(0.7, 1, 1),
        Vector3d(0.8, 1, 1),
        Vector3d(0.9, 1, 1),
        Vector3d(1, 1, 1),
        Vector3d(0.6, 1.1, 1),
        Vector3d(0.7, 1.1, 1),
        Vector3d(0.8, 1.1, 1),
        Vector3d(0.9, 1.1, 1),
        Vector3d(1, 1.1, 1),
        Vector3d(0.6, 1.2, 1),
        Vector3d(0.7, 1.2, 1),
        Vector3d(0.8, 1.2, 1),
        Vector3d(0.9, 1.2, 1),
        Vector3d(1, 1.2, 1),
        Vector3d(0.6, 1.3, 1),
        Vector3d(0.7, 1.3, 1),
        Vector3d(0.8, 1.3, 1),
        Vector3d(0.9, 1.3, 1),
        Vector3d(1, 1.3, 1),
        Vector3d(0.6, 1.4, 1),
        Vector3d(0.7, 1.4, 1),
        Vector3d(0.8, 1.4, 1),
        Vector3d(0.9, 1.4, 1),
        Vector3d(1, 1.4, 1),
        Vector3d(0.6, 1.5, 1),
        Vector3d(0.7, 1.5, 1),
        Vector3d(0.8, 1.5, 1),
        Vector3d(0.9, 1.5, 1),
        Vector3d(1, 1.5, 1)
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
_TRIANGLE_90_45_45_ISOSCELES.rotation = Vector3d(0, -90, 0)
_TRIANGLE_90_45_45_ISOSCELES.prettyName = 'triangle_isosceles'
_TRIANGLE_90_45_45_ISOSCELES.poleOffsetX = -0.45
_TRIANGLE_90_45_45_ISOSCELES.poly = [
    {'x': 0.5, 'z': -0.5},
    {'x': -0.5, 'z': -0.5},
    {'x': -0.5, 'z': 0.5}
]


_TRIANGLE_90_60_30_TALL = create_variable_definition_from_base(
    type='triangle',
    size_multiplier_list=[
        Vector3d(0.5, 1, 0.5),
        Vector3d(0.6, 1.2, 0.6),
        Vector3d(0.7, 1.4, 0.7),
        Vector3d(0.8, 1.6, 0.8),
        Vector3d(0.9, 1.8, 0.9),
        Vector3d(1, 2, 1)
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRIANGLE_90_60_30_TALL.rotation = Vector3d(0, -90, 0)
_TRIANGLE_90_60_30_TALL.prettyName = 'triangle_tall'
_TRIANGLE_90_60_30_TALL.poleOffsetX = -0.45
_TRIANGLE_90_60_30_TALL.poly = [
    {'x': 0.5, 'z': -0.5},
    {'x': -0.5, 'z': -0.5},
    {'x': -0.5, 'z': 0.5}
]


_TRIANGLE_90_60_30_WIDE = create_variable_definition_from_base(
    type='triangle',
    size_multiplier_list=[
        Vector3d(0.5, 0.25, 0.5),
        Vector3d(0.6, 0.3, 0.6),
        Vector3d(0.7, 0.35, 0.7),
        Vector3d(0.8, 0.4, 0.8),
        Vector3d(0.9, 0.45, 0.9),
        Vector3d(1, 0.5, 1)
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_TRIANGLE_90_60_30_WIDE.rotation = Vector3d(0, -90, 0)
_TRIANGLE_90_60_30_WIDE.prettyName = 'triangle_wide'
_TRIANGLE_90_60_30_WIDE.poleOffsetX = -0.45
_TRIANGLE_90_60_30_WIDE.poly = [
    {'x': 0.5, 'z': -0.5},
    {'x': -0.5, 'z': -0.5},
    {'x': -0.5, 'z': 0.5}
]


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
        Vector3d(0.5, 0.5 * 0.55, 0.5),
        Vector3d(0.5, 0.5 * 0.6, 0.5),
        Vector3d(0.5, 0.5 * 0.65, 0.5),
        Vector3d(0.5, 0.5 * 0.7, 0.5),
        Vector3d(0.5, 0.5 * 0.75, 0.5),
        Vector3d(0.5, 0.5 * 0.8, 0.5),
        Vector3d(0.5, 0.5 * 0.85, 0.5),
        Vector3d(0.5, 0.5 * 0.9, 0.5),
        Vector3d(0.5, 0.5 * 0.95, 0.5),
        Vector3d(0.5, 0.5 * 1, 0.5),
        Vector3d(0.6, 0.5 * 0.65, 0.6),
        Vector3d(0.6, 0.5 * 0.7, 0.6),
        Vector3d(0.6, 0.5 * 0.75, 0.6),
        Vector3d(0.6, 0.5 * 0.8, 0.6),
        Vector3d(0.6, 0.5 * 0.85, 0.6),
        Vector3d(0.6, 0.5 * 0.9, 0.6),
        Vector3d(0.6, 0.5 * 0.95, 0.6),
        Vector3d(0.6, 0.5 * 1, 0.6),
        Vector3d(0.7, 0.5 * 0.75, 0.7),
        Vector3d(0.7, 0.5 * 0.8, 0.7),
        Vector3d(0.7, 0.5 * 0.85, 0.7),
        Vector3d(0.7, 0.5 * 0.9, 0.7),
        Vector3d(0.7, 0.5 * 0.95, 0.7),
        Vector3d(0.7, 0.5 * 1, 0.7),
        Vector3d(0.8, 0.5 * 0.85, 0.8),
        Vector3d(0.8, 0.5 * 0.9, 0.8),
        Vector3d(0.8, 0.5 * 0.95, 0.8),
        Vector3d(0.8, 0.5 * 1, 0.8),
        Vector3d(0.9, 0.5 * 0.95, 0.9),
        Vector3d(0.9, 0.5 * 1, 0.9)
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RECTANGULAR_PRISM_THIN.prettyName = 'rect_thin'


_RECTANGULAR_PRISM_WIDE = create_variable_definition_from_base(
    type='cube',
    size_multiplier_list=[
        Vector3d(0.5, 0.5 * 0.25, 0.5),
        Vector3d(0.5, 0.5 * 0.3, 0.5),
        Vector3d(0.5, 0.5 * 0.35, 0.5),
        Vector3d(0.5, 0.5 * 0.4, 0.5),
        Vector3d(0.5, 0.5 * 0.45, 0.5),
        Vector3d(0.6, 0.5 * 0.3, 0.6),
        Vector3d(0.6, 0.5 * 0.35, 0.6),
        Vector3d(0.6, 0.5 * 0.4, 0.6),
        Vector3d(0.6, 0.5 * 0.45, 0.6),
        Vector3d(0.6, 0.5 * 0.5, 0.6),
        Vector3d(0.6, 0.5 * 0.55, 0.6),
        Vector3d(0.7, 0.5 * 0.35, 0.7),
        Vector3d(0.7, 0.5 * 0.4, 0.7),
        Vector3d(0.7, 0.5 * 0.45, 0.7),
        Vector3d(0.7, 0.5 * 0.5, 0.7),
        Vector3d(0.7, 0.5 * 0.55, 0.7),
        Vector3d(0.7, 0.5 * 0.6, 0.7),
        Vector3d(0.7, 0.5 * 0.65, 0.7),
        Vector3d(0.8, 0.5 * 0.4, 0.8),
        Vector3d(0.8, 0.5 * 0.45, 0.8),
        Vector3d(0.8, 0.5 * 0.5, 0.8),
        Vector3d(0.8, 0.5 * 0.55, 0.8),
        Vector3d(0.8, 0.5 * 0.6, 0.8),
        Vector3d(0.8, 0.5 * 0.65, 0.8),
        Vector3d(0.8, 0.5 * 0.7, 0.8),
        Vector3d(0.8, 0.5 * 0.75, 0.8),
        Vector3d(0.9, 0.5 * 0.45, 0.9),
        Vector3d(0.9, 0.5 * 0.5, 0.9),
        Vector3d(0.9, 0.5 * 0.55, 0.9),
        Vector3d(0.9, 0.5 * 0.6, 0.9),
        Vector3d(0.9, 0.5 * 0.65, 0.9),
        Vector3d(0.9, 0.5 * 0.7, 0.9),
        Vector3d(0.9, 0.5 * 0.75, 0.9),
        Vector3d(0.9, 0.5 * 0.8, 0.9),
        Vector3d(0.9, 0.5 * 0.85, 0.9),
        Vector3d(1, 0.5 * 0.5, 1),
        Vector3d(1, 0.5 * 0.55, 1),
        Vector3d(1, 0.5 * 0.6, 1),
        Vector3d(1, 0.5 * 0.65, 1),
        Vector3d(1, 0.5 * 0.7, 1),
        Vector3d(1, 0.5 * 0.75, 1),
        Vector3d(1, 0.5 * 0.8, 1),
        Vector3d(1, 0.5 * 0.85, 1),
        Vector3d(1, 0.5 * 0.9, 1),
        Vector3d(1, 0.5 * 0.95, 1)
    ],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)
_RECTANGULAR_PRISM_WIDE.prettyName = 'rect_wide'


_SQUARE_FRUSTUM = create_variable_definition_from_base(
    type='square_frustum',
    size_multiplier_list=[0.5, 0.6, 0.7, 0.8, 0.9, 1],
    chosen_material_list=INTUITIVE_PHYSICS_OBJECT_CHOSEN_MATERIAL_LIST
)


_POLE = {
    "id": "pole_",
    "type": "cylinder",
    "debug": {
        "color": ["magenta", "cyan"],
        "dimensions": {
            "x": 0.2,
            "y": 10,
            "z": 0.2
        },
        "info": [],
        "role": "structural",
        "shape": ["pole"],
        "size": "medium"
    },
    "kinematic": True,
    "structure": True,
    "mass": 50,
    "materials": ["Custom/Materials/Magenta"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 5,
            "z": 0
        },
        "scale": {
            "x": 0.2,
            "y": 5,
            "z": 0.2
        }
    }],
    "moves": [{
        "stepBegin": 0,
        "stepEnd": 0,
        "vector": {
            "x": 0,
            "y": POLE_MOVE_AMOUNT,
            "z": 0
        }
    }, {
        "stepBegin": 0,
        "stepEnd": 0,
        "vector": {
            "x": 0,
            "y": -POLE_MOVE_AMOUNT,
            "z": 0
        }
    }],
    "changeMaterials": [{
        "stepBegin": 0,
        "materials": ["Custom/Materials/Cyan"]
    }]
}


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


def create_pole_template(show_step: int) -> List[ObjectDefinition]:
    pole = _get('POLE')
    pole['id'] = pole['id'] + str(uuid.uuid4())
    pole['shows'][0]['stepBegin'] = show_step
    pole['moves'][0]['stepBegin'] = show_step
    return pole


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
