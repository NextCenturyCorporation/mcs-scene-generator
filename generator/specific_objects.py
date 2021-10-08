from __future__ import annotations

import copy
from typing import List, Union

from machine_common_sense.config_manager import Vector3d

from .base_objects import (
    create_soccer_ball,
    create_variable_definition_from_base,
)
from .definitions import (
    ChosenMaterial,
    DefinitionDataset,
    ObjectDefinition,
    get_dataset,
)


def multiply(one: Vector3d, two: Vector3d) -> Vector3d:
    return Vector3d(one.x * two.x, one.y * two.y, one.z * two.z)


_BALL_PLASTIC = create_variable_definition_from_base(
    type='ball',
    size_multiplier_list=[0.05, 0.1, 0.25, 0.5],
    chosen_material_list=[ChosenMaterial.PLASTIC_HOLLOW, ChosenMaterial.RUBBER]
)
_BALL_NON_PLASTIC = create_variable_definition_from_base(
    type='ball',
    size_multiplier_list=[0.025, 0.05, 0.1, 0.25],
    chosen_material_list=[
        ChosenMaterial.BLOCK_WOOD,
        ChosenMaterial.METAL,
        ChosenMaterial.WOOD
    ]
)


_BLOCK_BLANK_CUBE = create_variable_definition_from_base(
    type='block_blank_wood_cube',
    size_multiplier_list=[1, Vector3d(1, 2, 1), Vector3d(2, 1, 2)],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)
_BLOCK_BLANK_CYLINDER = create_variable_definition_from_base(
    type='block_blank_wood_cylinder',
    size_multiplier_list=[1, Vector3d(1, 2, 1), Vector3d(2, 1, 2)],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)
_BLOCK_LETTER = create_variable_definition_from_base(
    # Note: please ignore the "blue letter c" in the type: the object's
    # chosen material will change this design.
    type='block_blue_letter_c',
    size_multiplier_list=[1]
)
_BLOCK_NUMBER = create_variable_definition_from_base(
    # Note: please ignore the "yellow number 1" in the type: the object's
    # chosen material will change this design.
    type='block_yellow_number_1',
    size_multiplier_list=[1]
)


_DUCK_ON_WHEELS = create_variable_definition_from_base(
    type='duck_on_wheels',
    size_multiplier_list=[0.5, 1, 2],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TOY_RACECAR = create_variable_definition_from_base(
    type='racecar_red',
    size_multiplier_list=[0.75, 1.5, 3],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_PACIFIER = create_variable_definition_from_base(
    type='pacifier',
    size_multiplier_list=[1]
)


_CRAYON = ObjectDefinition(
    chooseTypeList=[
        create_variable_definition_from_base(
            type='crayon_black',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='crayon_blue',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='crayon_green',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='crayon_pink',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='crayon_red',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='crayon_yellow',
            size_multiplier_list=[1]
        )
    ]
)


_TURTLE_ON_WHEELS = create_variable_definition_from_base(
    type='turtle_on_wheels',
    size_multiplier_list=[0.5, 1, 2],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TOY_SEDAN = create_variable_definition_from_base(
    type='car_1',
    size_multiplier_list=[0.75, 1.5, 3],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_APPLE = ObjectDefinition(
    chooseTypeList=[
        create_variable_definition_from_base(
            type='apple_1',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='apple_2',
            size_multiplier_list=[1]
        )
    ]
)


_BOWL = ObjectDefinition(
    chooseTypeList=[
        create_variable_definition_from_base(
            type='bowl_3',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bowl_4',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bowl_6',
            size_multiplier_list=[1]
        )
    ],
    chooseMaterialList=[
        ChosenMaterial.PLASTIC.copy(),
        ChosenMaterial.WOOD.copy()
    ]
)


_CUP = ObjectDefinition(
    chooseTypeList=[
        create_variable_definition_from_base(
            type='cup_2',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='cup_3',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='cup_6',
            size_multiplier_list=[1]
        )
    ],
    chooseMaterialList=[
        ChosenMaterial.PLASTIC.copy(),
        ChosenMaterial.WOOD.copy()
    ]
)


_PLATE = ObjectDefinition(
    chooseTypeList=[
        create_variable_definition_from_base(
            type='plate_1',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='plate_3',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='plate_4',
            size_multiplier_list=[1]
        )
    ],
    chooseMaterialList=[
        ChosenMaterial.PLASTIC.copy(),
        ChosenMaterial.WOOD.copy()
    ]
)


_BOOKCASE = ObjectDefinition(
    chooseTypeList=[
        create_variable_definition_from_base(
            type='bookcase_1_shelf',
            size_multiplier_list=[1],
        ),
        create_variable_definition_from_base(
            type='bookcase_1_shelf',
            size_multiplier_list=[Vector3d(0.5, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_1_shelf',
            size_multiplier_list=[Vector3d(2, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf',
            size_multiplier_list=[Vector3d(0.5, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf',
            size_multiplier_list=[Vector3d(2, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf',
            size_multiplier_list=[Vector3d(0.5, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf',
            size_multiplier_list=[Vector3d(2, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf',
            size_multiplier_list=[Vector3d(0.5, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf',
            size_multiplier_list=[Vector3d(2, 1, 1)]
        )
    ],
    chooseMaterialList=[
        ChosenMaterial.METAL.copy(),
        ChosenMaterial.PLASTIC.copy(),
        ChosenMaterial.WOOD.copy()
    ]
)


_BOOKCASE_SIDELESS = ObjectDefinition(
    chooseTypeList=[
        create_variable_definition_from_base(
            type='bookcase_1_shelf_sideless',
            size_multiplier_list=[1],
        ),
        create_variable_definition_from_base(
            type='bookcase_1_shelf_sideless',
            size_multiplier_list=[Vector3d(0.5, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_1_shelf_sideless',
            size_multiplier_list=[Vector3d(2, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf_sideless',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf_sideless',
            size_multiplier_list=[Vector3d(0.5, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf_sideless',
            size_multiplier_list=[Vector3d(2, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf_sideless',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf_sideless',
            size_multiplier_list=[Vector3d(0.5, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf_sideless',
            size_multiplier_list=[Vector3d(2, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf_sideless',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf_sideless',
            size_multiplier_list=[Vector3d(0.5, 1, 1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf_sideless',
            size_multiplier_list=[Vector3d(2, 1, 1)]
        )
    ],
    chooseMaterialList=[
        ChosenMaterial.METAL.copy(),
        ChosenMaterial.PLASTIC.copy(),
        ChosenMaterial.WOOD.copy()
    ]
)


_CART = create_variable_definition_from_base(
    type='cart_1',
    size_multiplier_list=[0.5, 1],
    chosen_material_list=[ChosenMaterial.METAL]
)


_CHAIR_1_BABY_SCALED = create_variable_definition_from_base(
    type='chair_1',
    attributes_overrides=['pickupable', 'receptacle'],
    size_multiplier_list=[0.333, 0.5, 0.667],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)
_CHAIR_1 = create_variable_definition_from_base(
    type='chair_1',
    size_multiplier_list=[0.75, 1, 1.25],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHAIR_2_STOOL_CIRCLE_BABY_SCALED = create_variable_definition_from_base(
    type='chair_2',
    attributes_overrides=['pickupable', 'receptacle'],
    size_multiplier_list=[
        Vector3d(0.25, 0.5, 0.25),
        Vector3d(0.5, 0.5, 0.5),
        Vector3d(0.75, 0.5, 0.75)
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)
_CHAIR_2_STOOL_CIRCLE = create_variable_definition_from_base(
    type='chair_2',
    size_multiplier_list=[
        Vector3d(0.75, 0.75, 0.75),
        Vector3d(1, 0.75, 1),
        Vector3d(1, 1, 1)
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHAIR_3_STOOL_RECT = create_variable_definition_from_base(
    type='chair_3',
    size_multiplier_list=[
        Vector3d(0.5, 0.5, 0.5),
        Vector3d(0.667, 0.667, 0.667),
        Vector3d(0.75, 0.75, 0.75)
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHAIR_4_OFFICE = create_variable_definition_from_base(
    type='chair_4',
    size_multiplier_list=[
        Vector3d(0.7, 0.7, 0.7),
        Vector3d(0.9, 0.9, 0.9),
        Vector3d(1.1, 1.1, 1.1)
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.PLASTIC]
)


_BLOCK_BLANK_CUBE_NOT_PICKUPABLE = create_variable_definition_from_base(
    type='block_blank_wood_cube',
    attributes_overrides=['moveable'],
    size_multiplier_list=[2, Vector3d(2, 4, 2), Vector3d(4, 2, 4)],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)
_BLOCK_BLANK_CYLINDER_NOT_PICKUPABLE = create_variable_definition_from_base(
    type='block_blank_wood_cylinder',
    attributes_overrides=['moveable'],
    size_multiplier_list=[2, Vector3d(2, 4, 2), Vector3d(4, 2, 4)],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


# TODO Update this to use ObjectDefinition if needed in the future.
# _CHANGING_TABLE = {
#     "type": "changing_table",
#     "shape": ["changing table"],
#     "size": "huge",
#     "mass": 50,
#     "materialCategory": ["wood"],
#     "salientMaterials": ["wood"],
#     "attributes": ["receptacle", "openable", "occluder"],
#     "enclosedAreas": [{
#         # Remove the top drawer for now.
#         #        "id": "_drawer_top",
#         #        "position": {
#         #            "x": 0.165,
#         #            "y": 0.47,
#         #            "z": -0.03
#         #        },
#         #        "dimensions": {
#         #            "x": 0.68,
#         #            "y": 0.22,
#         #            "z": 0.41
#         #            }
#         #    }, {
#         "id": "_drawer_bottom",
#         "position": {
#             "x": 0.175,
#             "y": 0.19,
#             "z": -0.03
#         },
#         "dimensions": {
#             "x": 0.68,
#             "y": 0.2,
#             "z": 0.41
#         }
#     }],
#     "openAreas": [{
#         # Remove the top shelves for now.
#         #        "id": "",
#         #        "position": {
#         #            "x": 0,
#         #            "y": 0.85,
#         #            "z": 0
#         #        },
#         #        "dimensions": {
#         #            "x": 1,
#         #            "y": 0,
#         #            "z": 0.55
#         #            }
#         #    }, {
#         #        "id": "_shelf_top",
#         #        "position": {
#         #            "x": 0,
#         #            "y": 0.725,
#         #            "z": -0.05
#         #        },
#         #        "dimensions": {
#         #            "x": 1.05,
#         #            "y": 0.2,
#         #            "z": 0.44
#         #            }
#         #    }, {
#         #        "id": "_shelf_middle",
#         #        "position": {
#         #            "x": -0.365,
#         #            "y": 0.475,
#         #            "z": -0.05
#         #        },
#         #        "dimensions": {
#         #            "x": 0.32,
#         #            "y": 0.25,
#         #            "z": 0.44
#         #            }
#         #    }, {
#         "id": "_shelf_bottom",
#         "position": {
#             "x": -0.365,
#             "y": 0.2,
#             "z": -0.05
#         },
#         "dimensions": {
#             "x": 0.32,
#             "y": 0.25,
#             "z": 0.44
#         }
#     }],
#     "dimensions": {
#         "x": 1.1,
#         "y": 0.96,
#         "z": 0.89
#     },
#     "offset": {
#         "x": 0,
#         "y": 0.48,
#         "z": 0.155
#     },
#     "closedDimensions": {
#         "x": 1.1,
#         "y": 0.96,
#         "z": 0.58
#     },
#     "closedOffset": {
#         "x": 0,
#         "y": 0.48,
#         "z": 0
#     },
#     "positionY": 0,
#     "scale": {
#         "x": 1,
#         "y": 1,
#         "z": 1
#     }
# }


_CRIB = create_variable_definition_from_base(
    type='crib',
    size_multiplier_list=[1],
    chosen_material_list=[ChosenMaterial.WOOD]
)


# Set the default X to 1.175 so the table's shape is an exact 1:2 ratio.
_TABLE_1_RECT_VECTOR = Vector3d(1.175, 1, 1)
_TABLE_1_RECT_BABY_SCALED = create_variable_definition_from_base(
    type='table_1',
    attributes_overrides=['pickupable', 'receptacle'],
    size_multiplier_list=[
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(0.5, 0.5, 0.5)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(0.5, 0.333, 0.5)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(0.5, 0.5, 0.25)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(0.5, 0.333, 0.25))
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)
_TABLE_1_RECT_ACCESSIBLE = create_variable_definition_from_base(
    type='table_1',
    size_multiplier_list=[
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(1, 0.5, 0.5)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(1, 0.5, 1)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(2, 0.5, 1)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(1, 1, 0.5)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(1, 1, 1)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(2, 1, 1))
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


_TABLE_2_CIRCLE_BABY_SCALED = create_variable_definition_from_base(
    type='table_2',
    attributes_overrides=['pickupable', 'receptacle'],
    size_multiplier_list=[
        Vector3d(0.333, 0.333, 0.333),
        Vector3d(0.5, 0.333, 0.5)
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)
_TABLE_2_CIRCLE_ACCESSIBLE = create_variable_definition_from_base(
    type='table_2',
    size_multiplier_list=[
        Vector3d(0.5, 0.5, 0.5),
        Vector3d(1, 0.5, 1),
        Vector3d(0.75, 0.75, 0.75),
        Vector3d(1.5, 0.75, 1.5),
        Vector3d(1, 1, 1),
        Vector3d(2, 1, 2)
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_TABLE_3_CIRCLE_BABY_SCALED = create_variable_definition_from_base(
    type='table_3',
    attributes_overrides=['pickupable', 'receptacle'],
    size_multiplier_list=[Vector3d(0.5, 0.5, 0.5), Vector3d(1, 0.5, 1)],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)
_TABLE_3_CIRCLE_ACCESSIBLE = create_variable_definition_from_base(
    type='table_3',
    size_multiplier_list=[
        Vector3d(1.5, 0.5, 1.5),
        Vector3d(2, 0.5, 2),
        Vector3d(1, 1, 1),
        Vector3d(1.5, 1, 1.5),
        Vector3d(2, 1, 2),
        Vector3d(2.5, 1, 2.5)
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


_TABLE_4_SEMICIRCLE_ACCESSIBLE = create_variable_definition_from_base(
    type='table_4',
    size_multiplier_list=[
        Vector3d(0.75, 0.75, 0.75),
        Vector3d(1, 0.75, 1),
        Vector3d(1.25, 0.75, 1.25),
        Vector3d(1.5, 0.75, 1.5),
        Vector3d(1, 1, 1),
        Vector3d(1.25, 1, 1.25),
        Vector3d(1.5, 1, 1.5),
        Vector3d(2, 1, 2)
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


# Set the default Z to 0.667 so the table's shape is an exact 2:1 ratio.
_TABLE_5_RECT_VECTOR = Vector3d(1, 1, 0.667)
_TABLE_5_RECT_ACCESSIBLE = create_variable_definition_from_base(
    type='table_5',
    size_multiplier_list=[
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(0.25, 0.5, 0.5)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(0.5, 0.5, 0.5)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(0.5, 0.5, 1)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(1, 0.5, 1)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(0.25, 1, 0.5)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(0.5, 1, 0.5)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(0.5, 1, 1)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(1, 1, 1))
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


# Set the default X and Z so the table's shape is an exact 2:1 ratio.
_TABLE_7_RECT_VECTOR = Vector3d(0.98, 1, 0.769)
_TABLE_7_RECT_ACCESSIBLE = create_variable_definition_from_base(
    type='table_7',
    size_multiplier_list=[
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(0.5, 1, 1)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(1, 1, 1)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(1, 1, 2)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(2, 1, 2)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(0.5, 2, 1)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(1, 2, 1)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(1, 2, 2)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(2, 2, 2))
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


# Set the default X and Z so the table's shape is an exact 1:2 ratio.
_TABLE_8_RECT_VECTOR = Vector3d(0.769, 1, 0.98)
_TABLE_8_RECT_ACCESSIBLE = create_variable_definition_from_base(
    type='table_8',
    size_multiplier_list=[
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(1, 1, 0.5)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(1, 1, 1)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(2, 1, 1)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(2, 1, 2)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(1, 2, 0.5)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(1, 2, 1)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(2, 2, 1)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(2, 2, 2))
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


_TABLE_11_T_LEGS = create_variable_definition_from_base(
    type='table_11',
    size_multiplier_list=[
        Vector3d(0.5, 0.5, 0.5),
        Vector3d(0.5, 1, 0.5),
        Vector3d(1, 0.5, 1),
        Vector3d(1, 1, 1),
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)
_TABLE_12_X_LEGS = create_variable_definition_from_base(
    type='table_12',
    size_multiplier_list=[
        Vector3d(0.5, 0.5, 0.5),
        Vector3d(0.5, 1, 0.5),
        Vector3d(1, 0.5, 1),
        Vector3d(1, 1, 1),
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_TV = create_variable_definition_from_base(
    type='tv_2',
    size_multiplier_list=[0.5, 1, 1.5, 2]
)


_SHELF_2_TABLE_SQUARE = create_variable_definition_from_base(
    type='shelf_2',
    size_multiplier_list=[Vector3d(0.5, 1, 0.5), Vector3d(1, 1, 1)],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)
_SHELF_2_TABLE_RECT = create_variable_definition_from_base(
    type='shelf_2',
    size_multiplier_list=[
        Vector3d(1, 2, 0.5),
        Vector3d(2, 2, 0.5),
        Vector3d(2, 3, 0.5),
        Vector3d(3, 3, 0.5)
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


_SHELF_1_CUBBY_BABY_SCALED = create_variable_definition_from_base(
    type='shelf_1',
    attributes_overrides=['pickupable', 'receptacle'],
    size_multiplier_list=[Vector3d(0.5, 0.5, 0.5), Vector3d(0.75, 0.75, 0.75)],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)
_SHELF_1_CUBBY = create_variable_definition_from_base(
    type='shelf_1',
    size_multiplier_list=[
        Vector3d(1, 1, 1),
        Vector3d(1.5, 1.5, 1),
        Vector3d(1.5, 1.5, 1.5),
        Vector3d(2, 2, 1),
        Vector3d(2, 2, 1.5),
        Vector3d(2, 2, 2)
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


_SOFA_BABY_SCALED = ObjectDefinition(
    chooseTypeList=[
        create_variable_definition_from_base(
            type='sofa_1',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.333]
        ),
        create_variable_definition_from_base(
            type='sofa_1',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.5]
        ),
        create_variable_definition_from_base(
            type='sofa_2',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.333]
        ),
        create_variable_definition_from_base(
            type='sofa_2',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.5]
        ),
        create_variable_definition_from_base(
            type='sofa_3',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.333]
        ),
        create_variable_definition_from_base(
            type='sofa_3',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.5]
        )
    ]
)


_SOFA_1 = create_variable_definition_from_base(
    type='sofa_1',
    size_multiplier_list=[Vector3d(0.75, 1, 1), 1, Vector3d(1.25, 1, 1)]
)


_SOFA_2 = create_variable_definition_from_base(
    type='sofa_2',
    size_multiplier_list=[Vector3d(0.75, 1, 1), 1, Vector3d(1.25, 1, 1)]
)


_SOFA_3 = create_variable_definition_from_base(
    type='sofa_3',
    size_multiplier_list=[Vector3d(0.75, 1, 1), 1, Vector3d(1.25, 1, 1)]
)


_SOFA_CHAIR_BABY_SCALED = ObjectDefinition(
    chooseTypeList=[
        create_variable_definition_from_base(
            type='sofa_chair_1',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.333]
        ),
        create_variable_definition_from_base(
            type='sofa_chair_1',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.5]
        ),
        create_variable_definition_from_base(
            type='sofa_chair_2',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.333]
        ),
        create_variable_definition_from_base(
            type='sofa_chair_2',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.5]
        ),
        create_variable_definition_from_base(
            type='sofa_chair_3',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.333]
        ),
        create_variable_definition_from_base(
            type='sofa_chair_3',
            attributes_overrides=['moveable', 'receptacle'],
            size_multiplier_list=[0.5]
        )
    ]
)


_SOFA_CHAIR_1 = create_variable_definition_from_base(
    type='sofa_chair_1',
    size_multiplier_list=[1]
)


_SOFA_CHAIR_2 = create_variable_definition_from_base(
    type='sofa_chair_2',
    size_multiplier_list=[1]
)


_SOFA_CHAIR_3 = create_variable_definition_from_base(
    type='sofa_chair_3',
    size_multiplier_list=[1]
)


# TODO Update this to use ObjectDefinition if needed in the future.
# _WARDROBE = {
#     "type": "wardrobe",
#     "shape": ["wardrobe"],
#     "size": "huge",
#     "mass": 50,
#     "materialCategory": ["wood"],
#     "salientMaterials": ["wood"],
#     "attributes": ["receptacle", "openable", "occluder"],
#     "enclosedAreas": [{
#         # Remove the top drawers and shelves for now.
#         #        "id": "_middle_shelf_right",
#         #        "position": {
#         #            "x": 0.255,
#         #            "y": 1.165,
#         #            "z": 0.005
#         #        },
#         #        "dimensions": {
#         #            "x": 0.49,
#         #            "y": 1.24,
#         #            "z": 0.46
#         #        }
#         #    }, {
#         #        "id": "_middle_shelf_left",
#         #        "position": {
#         #            "x": -0.255,
#         #            "y": 1.295,
#         #            "z": 0.005
#         #        },
#         #        "dimensions": {
#         #            "x": 0.49,
#         #            "y": 0.98,
#         #            "z": 0.46
#         #        }
#         #    }, {
#         #        "id": "_bottom_shelf_left",
#         #        "position": {
#         #            "x": -0.255,
#         #            "y": 0.665,
#         #            "z": 0.005
#         #        },
#         #        "dimensions": {
#         #            "x": 0.49,
#         #            "y": 0.24,
#         #            "z": 0.46
#         #        }
#         #    }, {
#         #        "id": "_lower_drawer_top_left",
#         #        "position": {
#         #            "x": -0.265,
#         #            "y": 0.42,
#         #            "z": 0.015
#         #        },
#         #        "dimensions": {
#         #            "x": 0.445,
#         #            "y": 0.16
#         #            "z": 0.425
#         #        }
#         #    }, {
#         #        "id": "_lower_drawer_top_right",
#         #        "position": {
#         #            "x": 0.265,
#         #            "y": 0.42,
#         #            "z": 0.015
#         #        },
#         #        "dimensions": {
#         #            "x": 0.445,
#         #            "y": 0.16
#         #            "z": 0.425
#         #        }
#         #    }, {
#         "id": "_lower_drawer_bottom_left",
#         "position": {
#             "x": -0.265,
#             "y": 0.21,
#             "z": 0.015
#         },
#         "dimensions": {
#             "x": 0.445,
#             "y": 0.16,
#             "z": 0.425
#         }
#     }, {
#         "id": "_lower_drawer_bottom_right",
#         "position": {
#             "x": 0.265,
#             "y": 0.21,
#             "z": 0.015
#         },
#         "dimensions": {
#             "x": 0.445,
#             "y": 0.16,
#             "z": 0.425
#         }
#     }],
#     "dimensions": {
#         "x": 1.07,
#         "y": 2.1,
#         "z": 1
#     },
#     "offset": {
#         "x": 0,
#         "y": 1.05,
#         "z": 0.17
#     },
#     "closedDimensions": {
#         "x": 1.07,
#         "y": 2.1,
#         "z": 0.49
#     },
#     "closedOffset": {
#         "x": 0,
#         "y": 1.05,
#         "z": 0
#     },
#     "positionY": 0,
#     "scale": {
#         "x": 1,
#         "y": 1,
#         "z": 1
#     }
# }


_CASE_1_SUITCASE = create_variable_definition_from_base(
    type='case_1',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        1, 1.25, 1.5,
        # Big enough to fit a soccer ball inside
        2, 2.25, 2.5
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.PLASTIC]
)


_CASE_3 = create_variable_definition_from_base(
    type='case_3',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        1, 1.25, 1.5,
        # Big enough to fit a soccer ball inside
        2, 2.25, 2.5
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.PLASTIC]
)


_CHEST_1_CUBOID = create_variable_definition_from_base(
    type='chest_1',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.3, 0.5,
        # Big enough to fit a soccer ball inside
        0.7, 0.9, 1.1, 1.3
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHEST_2_SEMICYLINDER = create_variable_definition_from_base(
    type='chest_2',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.5, 0.75,
        # Big enough to fit a soccer ball inside
        1.25, 1.5, 1.75, 2
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHEST_3_CUBOID = create_variable_definition_from_base(
    type='chest_3',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.8, 1.2,
        # Big enough to fit a soccer ball inside
        1.6, 2, 2.4
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHEST_8_SEMICYLINDER = create_variable_definition_from_base(
    type='chest_8',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.8, 1.2,
        # Big enough to fit a soccer ball inside
        1.8, 2.4, 3
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


# TODO Update this to use ObjectDefinition if needed in the future.
# _POTTED_PLANT_LARGE = {
#     "shape": ["potted plant"],
#     "size": "large",
#     "mass": 5,
#     "materialCategory": [],
#     "salientMaterials": ["organic", "ceramic"],
#     "attributes": [],
#     "chooseType": [{
#         "type": "plant_1",
#         "color": ["green", "brown"],
#         "dimensions": {
#             "x": 0.931 * 2,
#             "y": 0.807 * 2,
#             "z": 0.894
#         },
#         "offset": {
#             "x": -0.114 * 2,
#             "y": 0.399 * 2,
#             "z": -0.118
#         },
#         "positionY": 0,
#         "scale": {
#             "x": 2,
#             "y": 2,
#             "z": 2
#         }
#     }, {
#         "type": "plant_5",
#         "color": ["green", "grey", "brown"],
#         "dimensions": {
#             "x": 0.522 * 2,
#             "y": 0.656 * 2,
#             "z": 0.62
#         },
#         "offset": {
#             "x": -0.024 * 2,
#             "y": 0.32 * 2,
#             "z": -0.018
#         },
#         "positionY": 0,
#         "scale": {
#             "x": 2,
#             "y": 2,
#             "z": 2
#         }
#     }, {
#         "type": "plant_7",
#         "color": ["green", "brown"],
#         "dimensions": {
#             "x": 0.72 * 2,
#             "y": 1.094 * 2,
#             "z": 0.755
#         },
#         "offset": {
#             "x": 0 * 2,
#             "y": 0.546 * 2,
#             "z": -0.017
#         },
#         "positionY": 0,
#         "scale": {
#             "x": 2,
#             "y": 2,
#             "z": 2
#         }
#     }, {
#         "type": "plant_9",
#         "color": ["green", "grey", "brown"],
#         "dimensions": {
#             "x": 0.679 * 2,
#             "y": 0.859 * 2,
#             "z": 0.546
#         },
#         "offset": {
#             "x": 0.037 * 2,
#             "y": 0.41 * 2,
#             "z": 0
#         },
#         "positionY": 0,
#         "scale": {
#             "x": 2,
#             "y": 2,
#             "z": 2
#         }
#     }, {
#         "type": "plant_14",
#         "color": ["red", "brown"],
#         "dimensions": {
#             "x": 0.508 * 2,
#             "y": 0.815 * 2,
#             "z": 0.623
#         },
#         "offset": {
#             "x": 0.036 * 2,
#             "y": 0.383 * 2,
#             "z": 0.033
#         },
#         "positionY": 0,
#         "scale": {
#             "x": 2,
#             "y": 2,
#             "z": 2
#         }
#     }, {
#         "type": "plant_16",
#         "color": ["green", "brown"],
#         "dimensions": {
#             "x": 0.702 * 2,
#             "y": 1.278 * 2,
#             "z": 0.813
#         },
#         "offset": {
#             "x": -0.008 * 2,
#             "y": 0.629 * 2,
#             "z": -0.012
#         },
#         "positionY": 0,
#         "scale": {
#             "x": 2,
#             "y": 2,
#             "z": 2
#         }
#     }]
# }


_PICKUPABLES = [
    # Arbitrary division: balls
    [_BALL_PLASTIC, _BALL_NON_PLASTIC, create_soccer_ball()],
    # Arbitrary division: blocks
    [_BLOCK_BLANK_CUBE, _BLOCK_BLANK_CYLINDER, _BLOCK_LETTER, _BLOCK_NUMBER],
    # Arbitrary division: toys
    [
        _TOY_SEDAN,
        _TOY_RACECAR,
        _DUCK_ON_WHEELS,
        _TURTLE_ON_WHEELS
    ],
    # Arbitrary division: misc objects
    [
        _APPLE,
        _BOWL,
        _CUP,
        _PLATE,
        _CRAYON,
        _PACIFIER
    ],
    # Arbitrary division: baby furniture
    [
        _CHAIR_1_BABY_SCALED,
        _CHAIR_2_STOOL_CIRCLE_BABY_SCALED,
        _TABLE_1_RECT_BABY_SCALED,
        _TABLE_3_CIRCLE_BABY_SCALED,
        _SHELF_1_CUBBY_BABY_SCALED
    ]
]


_NOT_PICKUPABLES = [
    # Arbitrary division: shelves
    [
        _BOOKCASE,
        _BOOKCASE_SIDELESS,
        _SHELF_1_CUBBY,
        _SHELF_2_TABLE_SQUARE,
        _SHELF_2_TABLE_RECT
    ],
    # Arbitrary division: chairs
    [_CHAIR_1, _CHAIR_2_STOOL_CIRCLE, _CHAIR_3_STOOL_RECT, _CHAIR_4_OFFICE],
    # Arbitrary division: sofas
    [_SOFA_1, _SOFA_2, _SOFA_3, _SOFA_BABY_SCALED],
    # Arbitrary division: sofa chairs
    [_SOFA_CHAIR_1, _SOFA_CHAIR_2, _SOFA_CHAIR_3, _SOFA_CHAIR_BABY_SCALED],
    # Arbitrary division: rectangular obstacle tables
    [
        _TABLE_1_RECT_ACCESSIBLE,
        _TABLE_7_RECT_ACCESSIBLE,
        _TABLE_8_RECT_ACCESSIBLE
    ],
    # Arbitrary division: (semi)circular obstacle tables
    [
        _TABLE_2_CIRCLE_ACCESSIBLE,
        _TABLE_3_CIRCLE_ACCESSIBLE,
        _TABLE_4_SEMICIRCLE_ACCESSIBLE
    ],
    # Arbitrary division: occluder tables
    [_TABLE_5_RECT_ACCESSIBLE, _TABLE_11_T_LEGS, _TABLE_12_X_LEGS],
    # Arbitrary division: random objects
    [
        _BLOCK_BLANK_CUBE_NOT_PICKUPABLE,
        _BLOCK_BLANK_CYLINDER_NOT_PICKUPABLE,
        _CART,
        _CRIB,
        _TV
    ]
    # Don't use containers here as possible occluders or context objects
]


_CONTAINERS = [
    [_CASE_1_SUITCASE],
    [_CHEST_1_CUBOID],
    [_CHEST_2_SEMICYLINDER],
    [_CASE_3],
    [_CHEST_3_CUBOID],
    [_CHEST_8_SEMICYLINDER]
]


_CONTAINERS_OPEN_TOPPED = [[
    # Each definition has multiple available sizes: the first is the smallest
    # size that can fit the soccer ball, and the rest are bigger sizes.
    create_variable_definition_from_base(
        type='bowl_3',
        size_multiplier_list=[Vector3d(3, 3, 3), Vector3d(3.5, 3.5, 3.5)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ),
    create_variable_definition_from_base(
        type='bowl_4',
        size_multiplier_list=[Vector3d(2.5, 5, 2.5), Vector3d(3, 6, 3)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ),
    create_variable_definition_from_base(
        type='bowl_6',
        size_multiplier_list=[Vector3d(3, 4, 3), Vector3d(3.5, 4.5, 3.5)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ),
    create_variable_definition_from_base(
        type='cup_2',
        size_multiplier_list=[Vector3d(4, 2.5, 4), Vector3d(4.5, 3, 4.5)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ),
    create_variable_definition_from_base(
        type='cup_3',
        size_multiplier_list=[Vector3d(4, 2.5, 4), Vector3d(4.5, 3, 4.5)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ),
    create_variable_definition_from_base(
        type='cup_6',
        size_multiplier_list=[Vector3d(4, 3, 4), Vector3d(4, 3.5, 4)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    )
]]


_OBSTACLES = list(filter(lambda filtered_list: len(filtered_list) > 0, [
    list(filter(lambda item: item.obstacle, object_list))
    for object_list in _NOT_PICKUPABLES
]))


_OCCLUDERS = list(filter(lambda filtered_list: len(filtered_list) > 0, [
    list(filter(lambda item: item.occluder, object_list))
    for object_list in _NOT_PICKUPABLES
]))


_STACK_TARGETS = list(filter(lambda filtered_list: len(filtered_list) > 0, [
    list(filter(lambda item: item.stackTarget, object_list))
    for object_list in _NOT_PICKUPABLES
]))


_ALL = _PICKUPABLES + _NOT_PICKUPABLES


def _get(prop: str) -> Union[
    ObjectDefinition,
    List[ObjectDefinition],
    List[List[ObjectDefinition]]
]:
    """Returns a deep copy of the global property with the given name
    (normally either an object definition or an object definition list)."""
    return copy.deepcopy(globals()['_' + prop])


def get_container_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all container definitions."""
    return get_dataset(
        _get('CONTAINERS'),
        'CONTAINERS',
        unshuffled=unshuffled
    )


def get_container_open_topped_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all open topped container
    definitions."""
    return get_dataset(
        _get('CONTAINERS_OPEN_TOPPED'),
        'CONTAINERS_OPEN_TOPPED',
        unshuffled=unshuffled
    )


def get_interactable_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all interactable definitions."""
    return get_dataset(_get('ALL'), 'ALL', unshuffled=unshuffled)


def get_non_pickupable_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all non-pickupable definitions."""
    return get_dataset(
        _get('NOT_PICKUPABLES'),
        'NOT_PICKUPABLES',
        unshuffled=unshuffled
    )


def get_obstacle_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all obstacle definitions."""
    return get_dataset(
        _get('OBSTACLES'),
        'OBSTACLES',
        unshuffled=unshuffled
    )


def get_occluder_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all occluder definitions."""
    return get_dataset(
        _get('OCCLUDERS'),
        'OCCLUDERS',
        unshuffled=unshuffled
    )


def get_pickupable_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all pickupable definitions."""
    return get_dataset(
        _get('PICKUPABLES'),
        'PICKUPABLES',
        unshuffled=unshuffled
    )


def get_stack_target_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all stack target definitions."""
    return get_dataset(
        _get('STACK_TARGETS'),
        'STACK_TARGETS',
        unshuffled=unshuffled
    )
