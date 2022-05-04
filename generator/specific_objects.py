from __future__ import annotations

import copy
from typing import List, Union

from machine_common_sense.config_manager import Vector3d

from .base_objects import create_variable_definition_from_base
from .definitions import (
    ChosenMaterial,
    DefinitionDataset,
    ImmutableObjectDefinition,
    ObjectDefinition,
    get_dataset,
)
from .structures import DOOR_TEMPLATE


def multiply(one: Vector3d, two: Vector3d) -> Vector3d:
    return Vector3d(x=one.x * two.x, y=one.y * two.y, z=one.z * two.z)


_BALL_SOCCER = create_variable_definition_from_base(
    type='soccer_ball',
    size_multiplier_list=[1, 1.5, 2],
    chosen_material_list=[]
)
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
    size_multiplier_list=[1, Vector3d(x=1, y=2, z=1), Vector3d(x=2, y=1, z=2)],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)
_BLOCK_BLANK_CYLINDER = create_variable_definition_from_base(
    type='block_blank_wood_cylinder',
    size_multiplier_list=[1, Vector3d(x=1, y=2, z=1), Vector3d(x=2, y=1, z=2)],
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


_CART_2 = create_variable_definition_from_base(
    type='cart_2',
    size_multiplier_list=[0.5, 1, 1.5, 2],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.PLASTIC]
)


_DOG_ON_WHEELS = create_variable_definition_from_base(
    type='dog_on_wheels',
    size_multiplier_list=[1, 1.5, 2, 2.5],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_DUCK_ON_WHEELS = create_variable_definition_from_base(
    type='duck_on_wheels',
    size_multiplier_list=[1, 1.5, 2, 2.5],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TOY_BUS = create_variable_definition_from_base(
    type='bus_1',
    size_multiplier_list=[0.5, 1, 1.5],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TOY_CAR_2 = create_variable_definition_from_base(
    type='car_2',
    size_multiplier_list=[1, 1.5, 2],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TOY_RACECAR = create_variable_definition_from_base(
    type='racecar_red',
    size_multiplier_list=[1, 1.5, 2, 2.5],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TOY_SEDAN = create_variable_definition_from_base(
    type='car_1',
    size_multiplier_list=[1, 1.5, 2, 2.5],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TOY_TRAIN = create_variable_definition_from_base(
    type='train_1',
    size_multiplier_list=[1, 1.5, 2, 2.5],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TOY_TROLLEY = create_variable_definition_from_base(
    type='trolley_1',
    size_multiplier_list=[1, 1.5, 2, 2.5],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TOY_TRUCK_1 = create_variable_definition_from_base(
    type='truck_1',
    size_multiplier_list=[1, 1.5, 2, 2.5],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TOY_TRUCK_2 = create_variable_definition_from_base(
    type='truck_2',
    size_multiplier_list=[1, 1.5, 2, 2.5],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_TURTLE_ON_WHEELS = create_variable_definition_from_base(
    type='turtle_on_wheels',
    size_multiplier_list=[1, 1.5, 2, 2.5],
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


_BED_1_OCCLUDER = create_variable_definition_from_base(
    type='bed_1',
    size_multiplier_list=[1],
    chosen_material_list=[ChosenMaterial.WOOD]
)


_BED_2_OCCLUDER = create_variable_definition_from_base(
    type='bed_2',
    size_multiplier_list=[1],
    chosen_material_list=[ChosenMaterial.WOOD]
)


_BED_3_OCCLUDER = create_variable_definition_from_base(
    type='bed_3',
    size_multiplier_list=[1],
    chosen_material_list=[ChosenMaterial.WOOD]
)


_BED_4_OCCLUDER = create_variable_definition_from_base(
    type='bed_4',
    size_multiplier_list=[1],
    chosen_material_list=[ChosenMaterial.WOOD]
)


_BED_5_OBSTACLE = create_variable_definition_from_base(
    type='bed_5',
    size_multiplier_list=[1],
    chosen_material_list=[ChosenMaterial.WOOD]
)


_BED_6_OBSTACLE = create_variable_definition_from_base(
    type='bed_6',
    size_multiplier_list=[1],
    chosen_material_list=[ChosenMaterial.WOOD]
)


_BOOKCASE = ObjectDefinition(
    chooseTypeList=[
        create_variable_definition_from_base(
            type='bookcase_1_shelf',
            size_multiplier_list=[1],
        ),
        create_variable_definition_from_base(
            type='bookcase_1_shelf',
            size_multiplier_list=[Vector3d(x=0.5, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_1_shelf',
            size_multiplier_list=[Vector3d(x=2, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf',
            size_multiplier_list=[Vector3d(x=0.5, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf',
            size_multiplier_list=[Vector3d(x=2, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf',
            size_multiplier_list=[Vector3d(x=0.5, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf',
            size_multiplier_list=[Vector3d(x=2, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf',
            size_multiplier_list=[Vector3d(x=0.5, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf',
            size_multiplier_list=[Vector3d(x=2, y=1, z=1)]
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
            size_multiplier_list=[Vector3d(x=0.5, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_1_shelf_sideless',
            size_multiplier_list=[Vector3d(x=2, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf_sideless',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf_sideless',
            size_multiplier_list=[Vector3d(x=0.5, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_2_shelf_sideless',
            size_multiplier_list=[Vector3d(x=2, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf_sideless',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf_sideless',
            size_multiplier_list=[Vector3d(x=0.5, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_3_shelf_sideless',
            size_multiplier_list=[Vector3d(x=2, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf_sideless',
            size_multiplier_list=[1]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf_sideless',
            size_multiplier_list=[Vector3d(x=0.5, y=1, z=1)]
        ),
        create_variable_definition_from_base(
            type='bookcase_4_shelf_sideless',
            size_multiplier_list=[Vector3d(x=2, y=1, z=1)]
        )
    ],
    chooseMaterialList=[
        ChosenMaterial.METAL.copy(),
        ChosenMaterial.PLASTIC.copy(),
        ChosenMaterial.WOOD.copy()
    ]
)


_CART_1 = create_variable_definition_from_base(
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
        Vector3d(x=0.25, y=0.5, z=0.25),
        Vector3d(x=0.5, y=0.5, z=0.5),
        Vector3d(x=0.75, y=0.5, z=0.75)
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
        Vector3d(x=0.75, y=0.75, z=0.75),
        Vector3d(x=1, y=0.75, z=1),
        Vector3d(x=1, y=1, z=1)
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
        Vector3d(x=0.5, y=0.5, z=0.5),
        Vector3d(x=0.667, y=0.667, z=0.667),
        Vector3d(x=0.75, y=0.75, z=0.75)
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
        Vector3d(x=0.7, y=0.7, z=0.7),
        Vector3d(x=0.9, y=0.9, z=0.9),
        Vector3d(x=1.1, y=1.1, z=1.1)
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.PLASTIC]
)


_CHAIR_5 = create_variable_definition_from_base(
    type='chair_5',
    size_multiplier_list=[1],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHAIR_6 = create_variable_definition_from_base(
    type='chair_6',
    size_multiplier_list=[1],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHAIR_7 = create_variable_definition_from_base(
    type='chair_7',
    size_multiplier_list=[1],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHAIR_8 = create_variable_definition_from_base(
    type='chair_8',
    size_multiplier_list=[1],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_BLOCK_BLANK_CUBE_NOT_PICKUPABLE = create_variable_definition_from_base(
    type='block_blank_wood_cube',
    attributes_overrides=['moveable'],
    size_multiplier_list=[2, Vector3d(x=2, y=4, z=2), Vector3d(x=4, y=2, z=4)],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)
_BLOCK_BLANK_CYLINDER_NOT_PICKUPABLE = create_variable_definition_from_base(
    type='block_blank_wood_cylinder',
    attributes_overrides=['moveable'],
    size_multiplier_list=[2, Vector3d(x=2, y=4, z=2), Vector3d(x=4, y=2, z=4)],
    chosen_material_list=[ChosenMaterial.BLOCK_WOOD, ChosenMaterial.WOOD]
)


_CRIB = create_variable_definition_from_base(
    type='crib',
    size_multiplier_list=[1],
    chosen_material_list=[ChosenMaterial.WOOD]
)


# Set the default X to 1.175 so the table's shape is an exact 1:2 ratio.
_TABLE_1_RECT_VECTOR = Vector3d(x=1.175, y=1, z=1)
_TABLE_1_RECT_BABY_SCALED = create_variable_definition_from_base(
    type='table_1',
    attributes_overrides=['pickupable', 'receptacle'],
    size_multiplier_list=[
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(x=0.5, y=0.5, z=0.5)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(x=0.5, y=0.333, z=0.5)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(x=0.5, y=0.5, z=0.25)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(x=0.5, y=0.333, z=0.25))
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)
_TABLE_1_RECT_ACCESSIBLE = create_variable_definition_from_base(
    type='table_1',
    size_multiplier_list=[
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(x=1, y=0.5, z=0.5)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(x=1, y=0.5, z=1)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(x=2, y=0.5, z=1)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(x=1, y=1, z=0.5)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(x=1, y=1, z=1)),
        multiply(_TABLE_1_RECT_VECTOR, Vector3d(x=2, y=1, z=1))
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


_TABLE_2_CIRCLE_BABY_SCALED = create_variable_definition_from_base(
    type='table_2',
    attributes_overrides=['pickupable', 'receptacle'],
    size_multiplier_list=[
        Vector3d(x=0.333, y=0.333, z=0.333),
        Vector3d(x=0.5, y=0.333, z=0.5)
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
        Vector3d(x=0.5, y=0.5, z=0.5),
        Vector3d(x=1, y=0.5, z=1),
        Vector3d(x=0.75, y=0.75, z=0.75),
        Vector3d(x=1.5, y=0.75, z=1.5),
        Vector3d(x=1, y=1, z=1),
        Vector3d(x=2, y=1, z=2)
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
    size_multiplier_list=[
        Vector3d(x=0.5, y=0.5, z=0.5), Vector3d(x=1, y=0.5, z=1)],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)
_TABLE_3_CIRCLE_ACCESSIBLE = create_variable_definition_from_base(
    type='table_3',
    size_multiplier_list=[
        Vector3d(x=1.5, y=0.5, z=1.5),
        Vector3d(x=2, y=0.5, z=2),
        Vector3d(x=1, y=1, z=1),
        Vector3d(x=1.5, y=1, z=1.5),
        Vector3d(x=2, y=1, z=2),
        Vector3d(x=2.5, y=1, z=2.5)
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


_TABLE_4_SEMICIRCLE_ACCESSIBLE = create_variable_definition_from_base(
    type='table_4',
    size_multiplier_list=[
        Vector3d(x=0.75, y=0.75, z=0.75),
        Vector3d(x=1, y=0.75, z=1),
        Vector3d(x=1.25, y=0.75, z=1.25),
        Vector3d(x=1.5, y=0.75, z=1.5),
        Vector3d(x=1, y=1, z=1),
        Vector3d(x=1.25, y=1, z=1.25),
        Vector3d(x=1.5, y=1, z=1.5),
        Vector3d(x=2, y=1, z=2)
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


# Set the default Z to 0.667 so the table's shape is an exact 2:1 ratio.
_TABLE_5_RECT_VECTOR = Vector3d(x=1, y=1, z=0.667)
_TABLE_5_RECT_ACCESSIBLE = create_variable_definition_from_base(
    type='table_5',
    size_multiplier_list=[
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(x=0.25, y=0.5, z=0.5)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(x=0.5, y=0.5, z=0.5)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(x=0.5, y=0.5, z=1)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(x=1, y=0.5, z=1)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(x=0.25, y=1, z=0.5)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(x=0.5, y=1, z=0.5)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(x=0.5, y=1, z=1)),
        multiply(_TABLE_5_RECT_VECTOR, Vector3d(x=1, y=1, z=1))
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


# Set the default X and Z so the table's shape is an exact 2:1 ratio.
_TABLE_7_RECT_VECTOR = Vector3d(x=0.98, y=1, z=0.769)
_TABLE_7_RECT_ACCESSIBLE = create_variable_definition_from_base(
    type='table_7',
    size_multiplier_list=[
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(x=0.5, y=1, z=1)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(x=1, y=1, z=1)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(x=1, y=1, z=2)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(x=2, y=1, z=2)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(x=0.5, y=2, z=1)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(x=1, y=2, z=1)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(x=1, y=2, z=2)),
        multiply(_TABLE_7_RECT_VECTOR, Vector3d(x=2, y=2, z=2))
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


# Set the default X and Z so the table's shape is an exact 1:2 ratio.
_TABLE_8_RECT_VECTOR = Vector3d(x=0.769, y=1, z=0.98)
_TABLE_8_RECT_ACCESSIBLE = create_variable_definition_from_base(
    type='table_8',
    size_multiplier_list=[
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(x=1, y=1, z=0.5)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(x=1, y=1, z=1)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(x=2, y=1, z=1)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(x=2, y=1, z=2)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(x=1, y=2, z=0.5)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(x=1, y=2, z=1)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(x=2, y=2, z=1)),
        multiply(_TABLE_8_RECT_VECTOR, Vector3d(x=2, y=2, z=2))
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


_TABLE_11_T_LEGS = create_variable_definition_from_base(
    type='table_11',
    size_multiplier_list=[
        Vector3d(x=0.5, y=0.5, z=0.5),
        Vector3d(x=0.5, y=1, z=0.5),
        Vector3d(x=1, y=0.5, z=1),
        Vector3d(x=1, y=1, z=1),
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
        Vector3d(x=0.5, y=0.5, z=0.5),
        Vector3d(x=0.5, y=1, z=0.5),
        Vector3d(x=1, y=0.5, z=1),
        Vector3d(x=1, y=1, z=1),
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_TABLE_13_SMALL_CIRCLE = create_variable_definition_from_base(
    type='table_13',
    size_multiplier_list=[1, Vector3d(
        x=2, y=1, z=2), 2, Vector3d(x=3, y=2, z=3)],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_TABLE_14_SMALL_RECT = create_variable_definition_from_base(
    type='table_14',
    size_multiplier_list=[
        1,
        Vector3d(x=2, y=1, z=1),
        Vector3d(x=1, y=1, z=2),
        2,
        Vector3d(x=3, y=2, z=2),
        Vector3d(x=2, y=2, z=3)
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_TABLE_15_RECT = create_variable_definition_from_base(
    type='table_15',
    size_multiplier_list=[
        0.75,
        Vector3d(x=1, y=0.75, z=0.75),
        Vector3d(x=0.75, y=0.75, z=1),
        1,
        Vector3d(x=1.25, y=1, z=1),
        Vector3d(x=1, y=1, z=1.25),
        1.25,
        Vector3d(x=1, y=1.25, z=1.25),
        Vector3d(x=1.25, y=1.25, z=1)
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_TABLE_16_CIRCLE = create_variable_definition_from_base(
    type='table_16',
    size_multiplier_list=[
        0.75,
        Vector3d(x=1, y=0.75, z=1),
        1,
        Vector3d(x=1.25, y=1, z=1.25),
        1.25,
        Vector3d(x=1, y=1.25, z=1)
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
    size_multiplier_list=[
        Vector3d(x=0.5, y=1, z=0.5), Vector3d(x=1, y=1, z=1)],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)
_SHELF_2_TABLE_RECT = create_variable_definition_from_base(
    type='shelf_2',
    size_multiplier_list=[
        Vector3d(x=1, y=2, z=0.5),
        Vector3d(x=2, y=2, z=0.5),
        Vector3d(x=2, y=3, z=0.5),
        Vector3d(x=3, y=3, z=0.5)
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)


_SHELF_1_CUBBY_BABY_SCALED = create_variable_definition_from_base(
    type='shelf_1',
    attributes_overrides=['pickupable', 'receptacle'],
    size_multiplier_list=[
        Vector3d(x=0.5, y=0.5, z=0.5), Vector3d(x=0.75, y=0.75, z=0.75)],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
)
_SHELF_1_CUBBY = create_variable_definition_from_base(
    type='shelf_1',
    size_multiplier_list=[
        Vector3d(x=1, y=1, z=1),
        Vector3d(x=1.5, y=1.5, z=1),
        Vector3d(x=1.5, y=1.5, z=1.5),
        Vector3d(x=2, y=2, z=1),
        Vector3d(x=2, y=2, z=1.5),
        Vector3d(x=2, y=2, z=2)
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
    size_multiplier_list=[
        Vector3d(x=0.75, y=1, z=1), 1, Vector3d(x=1.25, y=1, z=1)]
)


_SOFA_2 = create_variable_definition_from_base(
    type='sofa_2',
    size_multiplier_list=[
        Vector3d(x=0.75, y=1, z=1), 1, Vector3d(x=1.25, y=1, z=1)]
)


_SOFA_3 = create_variable_definition_from_base(
    type='sofa_3',
    size_multiplier_list=[
        Vector3d(x=0.75, y=1, z=1), 1, Vector3d(x=1.25, y=1, z=1)]
)


_SOFA_4 = create_variable_definition_from_base(
    type='sofa_4',
    size_multiplier_list=[1]
)


_SOFA_5 = create_variable_definition_from_base(
    type='sofa_5',
    size_multiplier_list=[1]
)


_SOFA_6 = create_variable_definition_from_base(
    type='sofa_6',
    size_multiplier_list=[1]
)


_SOFA_7 = create_variable_definition_from_base(
    type='sofa_7',
    size_multiplier_list=[1]
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


_SOFA_CHAIR_4 = create_variable_definition_from_base(
    type='sofa_chair_4',
    size_multiplier_list=[1]
)


_SOFA_CHAIR_5 = create_variable_definition_from_base(
    type='sofa_chair_5',
    size_multiplier_list=[1]
)


_SOFA_CHAIR_6 = create_variable_definition_from_base(
    type='sofa_chair_6',
    size_multiplier_list=[1]
)


_SOFA_CHAIR_7 = create_variable_definition_from_base(
    type='sofa_chair_7',
    size_multiplier_list=[1]
)


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


_CASE_2 = create_variable_definition_from_base(
    type='case_2',
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


_CHEST_4_ROUNDED_LID = create_variable_definition_from_base(
    type='chest_4',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.6, 0.8,
        # Big enough to fit a soccer ball inside
        1.2, 1.4, 1.6
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHEST_5_ROUNDED_LID = create_variable_definition_from_base(
    type='chest_5',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.6, 0.8,
        # Big enough to fit a soccer ball inside
        1.2, 1.4, 1.6
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHEST_6_TRAPEZOID_LID = create_variable_definition_from_base(
    type='chest_6',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.6, 0.8,
        # Big enough to fit a soccer ball inside
        1.2, 1.4, 1.6
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_CHEST_7_PIRATE_TREASURE = create_variable_definition_from_base(
    type='chest_7',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.4, 0.6,
        # Big enough to fit a soccer ball inside
        1, 1.2, 1.4
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


_CHEST_9_TRAPEZOID_LID = create_variable_definition_from_base(
    type='chest_9',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.4, 0.6,
        # Big enough to fit a soccer ball inside
        1.2, 1.4, 1.6
    ],
    chosen_material_list=[
        ChosenMaterial.METAL,
        ChosenMaterial.PLASTIC,
        ChosenMaterial.WOOD
    ]
)


_TOOLBOX_1 = create_variable_definition_from_base(
    type='toolbox_1',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.8, 1,
        # Big enough to fit a soccer ball inside
        1.4, 1.6, 1.8
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.PLASTIC]
)


_TOOLBOX_2 = create_variable_definition_from_base(
    type='toolbox_2',
    size_multiplier_list=[
        # Too little to fit a soccer ball inside
        0.4, 0.6,
        # Big enough to fit a soccer ball inside
        1, 1.2, 1.4
    ],
    chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.PLASTIC]
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


_PICKUPABLE_BALLS = [
    _BALL_SOCCER,
    _BALL_PLASTIC,
    _BALL_NON_PLASTIC
]
_PICKUPABLE_BLOCKS = [
    _BLOCK_BLANK_CUBE,
    _BLOCK_BLANK_CYLINDER,
    _BLOCK_LETTER,
    _BLOCK_NUMBER
]
_PICKUPABLE_FURNITURE = [
    _CHAIR_1_BABY_SCALED,
    _CHAIR_2_STOOL_CIRCLE_BABY_SCALED,
    _TABLE_1_RECT_BABY_SCALED,
    _TABLE_3_CIRCLE_BABY_SCALED,
    _SHELF_1_CUBBY_BABY_SCALED
]
_PICKUPABLE_MISC = [
    _APPLE,
    _BOWL,
    _CUP,
    _PLATE,
    _CRAYON,
    _PACIFIER
]
_PICKUPABLE_TOYS = [
    _DOG_ON_WHEELS,
    _DUCK_ON_WHEELS,
    _TOY_BUS,
    _TOY_CAR_2,
    _TOY_RACECAR,
    _TOY_SEDAN,
    _TOY_TRAIN,
    _TOY_TROLLEY,
    _TOY_TRUCK_1,
    _TOY_TRUCK_2,
    _TURTLE_ON_WHEELS
]


_ROLLABLES = [_PICKUPABLE_BALLS + _PICKUPABLE_TOYS]


_PICKUPABLES = [
    _PICKUPABLE_BALLS,
    _PICKUPABLE_BLOCKS,
    _PICKUPABLE_FURNITURE,
    _PICKUPABLE_MISC,
    _PICKUPABLE_TOYS
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
        _CART_1,
        _CART_2,
        _CRIB,
        _TV
    ],
    # Eval 4 novel objects
    [_BED_1_OCCLUDER, _BED_2_OCCLUDER, _BED_3_OCCLUDER, _BED_4_OCCLUDER],
    [_BED_5_OBSTACLE, _BED_5_OBSTACLE],
    [_CHAIR_5, _CHAIR_6, _CHAIR_7, _CHAIR_8],
    [_SOFA_4, _SOFA_5, _SOFA_6, _SOFA_7],
    [_SOFA_CHAIR_4, _SOFA_CHAIR_5, _SOFA_CHAIR_6, _SOFA_CHAIR_7],
    [
        _TABLE_13_SMALL_CIRCLE,
        _TABLE_14_SMALL_RECT,
        _TABLE_15_RECT,
        _TABLE_16_CIRCLE
    ],
    # Don't use containers here as possible occluders or context objects
]


_CONTAINERS_OPENABLE = [
    _CASE_1_SUITCASE,
    _CASE_3,
    _CHEST_1_CUBOID,
    _CHEST_2_SEMICYLINDER,
    _CHEST_3_CUBOID,
    _CHEST_8_SEMICYLINDER,
    # Eval 4 novel containers
    _CASE_2,
    _CHEST_4_ROUNDED_LID,
    _CHEST_5_ROUNDED_LID,
    _CHEST_6_TRAPEZOID_LID,
    _CHEST_7_PIRATE_TREASURE,
    _CHEST_9_TRAPEZOID_LID,
    _TOOLBOX_1,
    _TOOLBOX_2
]


_CONTAINERS_BINS = [
    # Each definition has multiple available sizes: the first is the smallest
    # size that can fit the soccer ball, and the rest are bigger sizes.
    create_variable_definition_from_base(
        type='bowl_3',
        size_multiplier_list=[
            Vector3d(x=3, y=3, z=3), Vector3d(x=3.5, y=3.5, z=3.5)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ),
    create_variable_definition_from_base(
        type='bowl_4',
        size_multiplier_list=[
            Vector3d(x=2.5, y=5, z=2.5), Vector3d(x=3, y=6, z=3)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ),
    create_variable_definition_from_base(
        type='bowl_6',
        size_multiplier_list=[
            Vector3d(x=3, y=4, z=3), Vector3d(x=3.5, y=4.5, z=3.5)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ),
    create_variable_definition_from_base(
        type='cup_2',
        size_multiplier_list=[
            Vector3d(x=4, y=2.5, z=4), Vector3d(x=4.5, y=3, z=4.5)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ),
    create_variable_definition_from_base(
        type='cup_3',
        size_multiplier_list=[
            Vector3d(x=4, y=2.5, z=4), Vector3d(x=4.5, y=3, z=4.5)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ),
    create_variable_definition_from_base(
        type='cup_6',
        size_multiplier_list=[
            Vector3d(x=4, y=3, z=4), Vector3d(x=4, y=3.5, z=4)],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    )
]


_CONTAINERS_ASYMMETRIC = [
    create_variable_definition_from_base(
        type=f'container_asymmetric_{suffix}',
        size_multiplier_list=[1],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ) for suffix in [
        '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'
    ]
]


_CONTAINERS_SYMMETRIC = [
    create_variable_definition_from_base(
        type=f'container_symmetric_{suffix}',
        size_multiplier_list=[1],
        chosen_material_list=[
            ChosenMaterial.METAL,
            ChosenMaterial.PLASTIC,
            ChosenMaterial.WOOD
        ]
    ) for suffix in [
        '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'
    ]
]


_CONTAINERS_OPEN_TOPPED = [
    # Same chance each type.
    _CONTAINERS_ASYMMETRIC, _CONTAINERS_BINS, _CONTAINERS_SYMMETRIC
]


_CONTAINERS = [
    # Same chance openable versus open-topped.
    _CONTAINERS_OPENABLE,
    [
        definition for definition_list in _CONTAINERS_OPEN_TOPPED
        for definition in definition_list
    ]
]


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


_ALL_NON_CONTAINERS = _PICKUPABLES + _NOT_PICKUPABLES


# Map each rollable object type (shape) to each size (scale) option.
ROLLABLE_TYPES_TO_SIZES = {}
for definition_list in _ROLLABLES:
    for definition in definition_list:
        if definition.type not in ROLLABLE_TYPES_TO_SIZES:
            ROLLABLE_TYPES_TO_SIZES[definition.type] = []
        if definition.scale:
            ROLLABLE_TYPES_TO_SIZES[definition.type].append(definition.scale)
        ROLLABLE_TYPES_TO_SIZES[definition.type].extend([
            option.scale for option in definition.chooseSizeList
        ])
# Map each symmetric/asymmetric container object type to each size option.
CONTAINER_TYPES_TO_SIZES = {}
for definition_list in [_CONTAINERS_SYMMETRIC] + [_CONTAINERS_ASYMMETRIC]:
    for definition in definition_list:
        if definition.type not in CONTAINER_TYPES_TO_SIZES:
            CONTAINER_TYPES_TO_SIZES[definition.type] = []
        if definition.scale:
            CONTAINER_TYPES_TO_SIZES[definition.type].append(definition.scale)
        CONTAINER_TYPES_TO_SIZES[definition.type].extend([
            option.scale for option in definition.chooseSizeList
        ])


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


def get_container_asymmetric_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all open topped asymmetric container
    definitions."""
    return get_dataset(
        [_get('CONTAINERS_ASYMMETRIC')],
        'CONTAINERS_ASYMMETRIC',
        unshuffled=unshuffled
    )


def get_container_bin_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all open topped bin container
    definitions."""
    return get_dataset(
        [_get('CONTAINERS_BINS')],
        'CONTAINERS_BINS',
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


def get_container_openable_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all openable/closable container
    definitions."""
    return get_dataset(
        [_get('CONTAINERS_OPENABLE')],
        'CONTAINERS_OPENABLE',
        unshuffled=unshuffled
    )


def get_container_symmetric_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all open topped symmetric container
    definitions."""
    return get_dataset(
        [_get('CONTAINERS_SYMMETRIC')],
        'CONTAINERS_SYMMETRIC',
        unshuffled=unshuffled
    )


def get_interactable_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all non-container interactable
    definitions. Intentionally excludes containers due to use cases with
    Eval 3 retrieval hypercubes."""
    return get_dataset(
        _get('ALL_NON_CONTAINERS'),
        'ALL_NON_CONTAINERS',
        unshuffled=unshuffled
    )


def get_rollable_definition_dataset(
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Returns an immutable dataset of all rollable interactable
    definitions."""
    return get_dataset(_get('ROLLABLES'), 'ROLLABLES', unshuffled=unshuffled)


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


DISTRACTOR_DATASET = None


def choose_distractor_definition(
    shapes_list: List[List[str]]
) -> ObjectDefinition:
    """Choose and return a distractor definition for the given objects."""
    # Use the final shape, since it should always be the most descriptive.
    invalid_shape_list = [shapes[-1] for shapes in shapes_list]

    # Save the distractor dataset for future use once it's made.
    global DISTRACTOR_DATASET
    if not DISTRACTOR_DATASET:
        # Distractors should always be both trained and pickupable.
        DISTRACTOR_DATASET = (
            get_pickupable_definition_dataset().filter_on_trained()
        )

    def _filter_data_callback(definition: ImmutableObjectDefinition) -> bool:
        # Distractors cannot have the same shape as an existing object from the
        # given list so we don't unintentionally generate a new confusor.
        return definition.shape[-1] not in invalid_shape_list

    dataset = DISTRACTOR_DATASET.filter_on_custom(_filter_data_callback)
    return dataset.choose_random_definition()


LOCKABLE_SHAPES = None


def get_lockable_shapes():
    """Generate and return a list of all the lockable shapes"""
    global LOCKABLE_SHAPES
    if not LOCKABLE_SHAPES:
        LOCKABLE_SHAPES = []
        all_containers = _get("CONTAINERS")
        for outer in all_containers:
            for inner in outer:
                if inner and inner.type:
                    LOCKABLE_SHAPES.append(inner.type)
    return LOCKABLE_SHAPES + [DOOR_TEMPLATE['type']]
