from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, NamedTuple, Tuple, Union

from machine_common_sense.config_manager import Vector3d

from .definitions import ChosenMaterial, ObjectDefinition, SizeChoice
from .exceptions import SceneException
from .materials import (
    ALL_MATERIAL_TUPLES,
    BLOCK_BLANK_MATERIALS,
    BLOCK_LETTER_MATERIALS,
    BLOCK_NUMBER_MATERIALS,
    METAL_MATERIALS,
    PLASTIC_MATERIALS,
    RUBBER_MATERIALS,
    SOFA_1_MATERIALS,
    SOFA_2_MATERIALS,
    SOFA_3_MATERIALS,
    SOFA_CHAIR_1_MATERIALS,
    WOOD_MATERIALS,
)


@dataclass
class ObjectInteractableArea():
    dimensions: Vector3d
    position: Vector3d
    area_id: str = ''

    def to_dict(
        self,
        x_multiplier: float = 1,
        y_multiplier: float = 1,
        z_multiplier: float = 1
    ) -> Dict[str, Any]:
        # TODO MCS-697 Consider removing this behavior (just use the class)
        return {
            'id': self.area_id,
            'dimensions': {
                'x': round(self.dimensions.x * x_multiplier, 4),
                'y': round(self.dimensions.y * y_multiplier, 4),
                'z': round(self.dimensions.z * z_multiplier, 4)
            },
            'position': {
                'x': round(self.position.x * x_multiplier, 4),
                'y': round(self.position.y * y_multiplier, 4),
                'z': round(self.position.z * z_multiplier, 4)
            }
        }


@dataclass
class ObjectSidewaysSize():
    dimensions: Vector3d
    offset: Vector3d
    positionY: float
    rotation: Vector3d
    switch_x_with_y: bool = False
    switch_x_with_z: bool = False
    switch_y_with_z: bool = False


def _is_of_size(dims: Vector3d, size: float) -> bool:
    # Either: each dimension is less than size; OR: all dimensions multiplied
    # together are less than size^3 AND each dimension is less than 2*size.
    # This calculation is arbitrary and can be modified if needed.
    return (dims.x < size and dims.y < size and dims.z < size) or (
        ((dims.x * dims.y * dims.z) < size**3) and
        dims.x < (2 * size) and dims.y < (2 * size) and dims.z < (2 * size)
    )


def _choose_size_text(dimensions: Vector3d) -> str:
    if _is_of_size(dimensions, 0.25):
        return 'tiny'
    if _is_of_size(dimensions, 0.5):
        return 'small'
    if _is_of_size(dimensions, 1):
        return 'medium'
    if _is_of_size(dimensions, 1.5):
        return 'large'
    return 'huge'


@dataclass
class ObjectBaseSize():
    dimensions: Vector3d
    mass: float
    offset: Vector3d
    positionY: float
    enclosed_area_list: ObjectInteractableArea = None
    open_area_list: List[ObjectInteractableArea] = None
    sideways: ObjectSidewaysSize = None

    def make(self, size_multiplier: Union[float, Vector3d]) -> SizeChoice:
        is_vector = isinstance(size_multiplier, Vector3d)
        x_multiplier = size_multiplier.x if is_vector else size_multiplier
        y_multiplier = size_multiplier.y if is_vector else size_multiplier
        z_multiplier = size_multiplier.z if is_vector else size_multiplier
        # Set the sideways object size multipliers.
        x_sideways = x_multiplier
        y_sideways = y_multiplier
        z_sideways = z_multiplier
        if self.sideways and self.sideways.switch_x_with_y:
            x_sideways = y_multiplier
            y_sideways = x_multiplier
        if self.sideways and self.sideways.switch_x_with_z:
            x_sideways = z_multiplier
            z_sideways = x_multiplier
        if self.sideways and self.sideways.switch_y_with_z:
            y_sideways = z_multiplier
            z_sideways = y_multiplier
        dimensions = Vector3d(
            self.dimensions.x * x_multiplier,
            self.dimensions.y * y_multiplier,
            self.dimensions.z * z_multiplier
        )
        enclosedAreas = [area.to_dict(
            x_multiplier,
            y_multiplier,
            z_multiplier
        ) for area in (self.enclosed_area_list or [])]
        mass = round((
            self.mass * (x_multiplier + y_multiplier + z_multiplier) / 3.0
        ), 4)
        offset = Vector3d(
            self.offset.x * x_multiplier,
            self.offset.y * y_multiplier,
            self.offset.z * z_multiplier
        )
        openAreas = [area.to_dict(
            x_multiplier,
            y_multiplier,
            z_multiplier
        ) for area in (self.open_area_list or [])]
        positionY = (self.positionY * y_multiplier)
        scale = Vector3d(x_multiplier, y_multiplier, z_multiplier)
        sideways = {
            'dimensions': Vector3d(
                self.sideways.dimensions.x * x_sideways,
                self.sideways.dimensions.y * y_sideways,
                self.sideways.dimensions.z * z_sideways
            ),
            'offset': Vector3d(
                self.sideways.offset.x * x_sideways,
                self.sideways.offset.y * y_sideways,
                self.sideways.offset.z * z_sideways
            ),
            'positionY': self.sideways.positionY * y_sideways,
            'rotation': Vector3d(
                self.sideways.rotation.x,
                self.sideways.rotation.y,
                self.sideways.rotation.z
            )
        } if self.sideways else None
        size = _choose_size_text(dimensions)
        return SizeChoice(
            dimensions=dimensions,
            enclosedAreas=enclosedAreas,
            mass=mass,
            offset=offset,
            openAreas=openAreas,
            positionY=positionY,
            scale=scale,
            sideways=sideways,
            size=size
        )


@dataclass
class _FunctionArgs():
    chosen_material_list: List[ChosenMaterial]
    size_multiplier_list: List[Union[float, Vector3d]]
    type: str


_APPLE_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.111, 0.12, 0.122),
    mass=0.5,
    offset=Vector3d(0, 0.005, 0),
    positionY=0.03
)
_APPLE_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.117, 0.121, 0.116),
    mass=0.5,
    offset=Vector3d(0, 0.002, 0),
    positionY=0.03
)
# Coincidentally, all of the blocks have the same base size.
_BLOCK_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.1, 0.1, 0.1),
    mass=0.333,
    offset=Vector3d(0, 0.05, 0),
    positionY=0
)
_BOOKCASE_1_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1, 1, 0.5),
    mass=6,
    offset=Vector3d(0, 0.5, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 0.04, 0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 0.52, 0)
        )
    ]
)
_BOOKCASE_2_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1, 1.5, 0.5),
    mass=12,
    offset=Vector3d(0, 0.75, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 0.04, 0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 0.52, 0)
        ),
        ObjectInteractableArea(
            area_id='shelf_2',
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 1.02, 0)
        )
    ]
)
_BOOKCASE_3_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1, 2, 0.5),
    mass=18,
    offset=Vector3d(0, 1, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 0.04, 0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 0.52, 0)
        ),
        ObjectInteractableArea(
            area_id='shelf_2',
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 1.02, 0)
            # Performer agent is too short to reach these areas effectively.
            # ),
            # ObjectInteractableArea(
            #     area_id='shelf_3',
            #     dimensions=Vector3d(0.5, 0, 0.25),
            #     position=Vector3d(0, 1.52, 0)
        )
    ]
)
_BOOKCASE_4_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1, 2.5, 0.5),
    mass=24,
    offset=Vector3d(0, 1, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 0.04, 0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 0.52, 0)
        ),
        ObjectInteractableArea(
            area_id='shelf_2',
            dimensions=Vector3d(0.5, 0, 0.25),
            position=Vector3d(0, 1.02, 0)
            # Performer agent is too short to reach these areas effectively.
            # ),
            # ObjectInteractableArea(
            #     area_id='shelf_3',
            #     dimensions=Vector3d(0.5, 0, 0.25),
            #     position=Vector3d(0, 1.52, 0)
            # ),
            # ObjectInteractableArea(
            #     area_id='shelf_4',
            #     dimensions=Vector3d(0.5, 0, 0.25),
            #     position=Vector3d(0, 2.02, 0)
        )
    ]
)
_BOWL_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.175, 0.116, 0.171),
    mass=0.5,
    offset=Vector3d(0, 0.055, 0),
    positionY=0.005
)
_BOWL_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.209, 0.059, 0.206),
    mass=0.5,
    offset=Vector3d(0, 0.027, 0),
    positionY=0.005
)
_BOWL_6_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.198, 0.109, 0.201),
    mass=0.5,
    offset=Vector3d(0, 0.052, 0),
    positionY=0.005
)
_CAKE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.22, 0.22, 0.22),
    mass=1,
    offset=Vector3d(0, 0.05, 0),
    positionY=0.005
)
_CART_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.725, 1.29, 0.55),
    mass=4,
    offset=Vector3d(0, 0.645, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.38, 0, 0.38),
            position=Vector3d(0, 0.34, 0)
        )
    ]
)
_CASE_1_SUITCASE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.71, 0.19, 0.42),
    mass=5,
    offset=Vector3d(0, 0.095, 0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.69, 0.175, 0.4),
            position=Vector3d(0, 0.0925, 0)
        )
    ]
)
_CASE_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.81, 0.21, 0.56),
    mass=5,
    offset=Vector3d(0, 0.105, 0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.79, 0.17, 0.53),
            position=Vector3d(0, 0.105, 0)
        )
    ]
)
_CHAIR_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.54, 1.04, 0.46),
    mass=4,
    offset=Vector3d(0, 0.51, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.38, 0, 0.38),
            position=Vector3d(0.01, 0.5, -0.02)
        )
    ]
)
_CHAIR_2_STOOL_CIRCLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.3, 0.75, 0.3),
    mass=4,
    offset=Vector3d(0, 0.375, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.2, 0, 0.2),
            position=Vector3d(0, 0.75, 0)
        )
    ]
)
_CHAIR_3_STOOL_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.42, 0.8, 0.63),
    mass=4,
    offset=Vector3d(0, 0.4, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.3, 0, 0.6),
            position=Vector3d(0, 1.3, 0)
        )
    ]
)
_CHAIR_4_OFFICE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.54, 0.88, 0.44),
    mass=4,
    offset=Vector3d(0, 0.44, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.32, 0, 0.32),
            position=Vector3d(-0.01, 1.06, 0.015)
        )
    ]
)
_CHEST_1_CUBOID_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.83, 0.42, 0.55),
    mass=5,
    offset=Vector3d(0, 0.205, 0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.77, 0.33, 0.49),
            position=Vector3d(0, 0.195, 0)
        )
    ]
)
_CHEST_2_SEMICYLINDER_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.52, 0.42, 0.31),
    mass=5,
    offset=Vector3d(0, 0.165, 0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.44, 0.25, 0.31),
            position=Vector3d(0, 0.165, 0)
        )
    ]
)
_CHEST_3_CUBOID_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.46, 0.26, 0.32),
    mass=5,
    offset=Vector3d(0, 0.13, 0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.35, 0.12, 0.21),
            position=Vector3d(0, 0.09, 0)
        )
    ]
)
_CHEST_8_SEMICYLINDER_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.42, 0.32, 0.36),
    mass=5,
    offset=Vector3d(0, 0.16, 0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.36, 0.135, 0.28),
            position=Vector3d(0, 0.09, 0)
        )
    ]
)
_CRAYON_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.01, 0.085, 0.01),
    mass=0.125,
    offset=Vector3d(0, 0.0425, 0),
    positionY=0.005
)
_CRIB_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.65, 0.9, 1.25),
    mass=10,
    offset=Vector3d(0, 0.45, 0),
    positionY=0,
)
_CUP_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.105, 0.135, 0.104),
    mass=0.5,
    offset=Vector3d(0, 0.064, 0),
    positionY=0.005
)
_CUP_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.123, 0.149, 0.126),
    mass=0.5,
    offset=Vector3d(0, 0.072, 0),
    positionY=0.005
)
_CUP_6_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.106, 0.098, 0.106),
    mass=0.5,
    offset=Vector3d(0, 0.046, 0),
    positionY=0.005
)
_DOG_ON_WHEELS_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.355, 0.134, 0.071),
    mass=2,
    offset=Vector3d(0, 0.067, 0),
    positionY=0.005
)
_DUCK_ON_WHEELS_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.21, 0.17, 0.065),
    mass=1,
    offset=Vector3d(0, 0.085, 0),
    positionY=0.005
)
_FOAM_FLOOR_TILES_SIZE = ObjectBaseSize(
    dimensions=Vector3d(9, 0.01, 9),
    mass=2,
    offset=Vector3d(0, 0.01, 0),
    positionY=0.01
)
_PACIFIER_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.07, 0.04, 0.05),
    mass=0.125,
    offset=Vector3d(0, 0.02, 0),
    positionY=0.005
)
_PLATE_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.208, 0.117, 0.222),
    mass=0.5,
    offset=Vector3d(0, 0.057, 0),
    positionY=0.005
)
_PLATE_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.304, 0.208, 0.305),
    mass=0.5,
    offset=Vector3d(0, 0.098, 0),
    positionY=0.005
)
_PLATE_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.202, 0.113, 0.206),
    mass=0.5,
    offset=Vector3d(0, 0.053, 0),
    positionY=0.005
)
_PRIMITIVE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1, 1, 1),
    mass=1,
    offset=Vector3d(0, 0.5, 0),
    positionY=0.5
)
_PRIMITIVE_TALL_NARROW_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.5, 1, 0.5),
    mass=1,
    offset=Vector3d(0, 0.5, 0),
    positionY=0.5
)
_PRIMITIVE_WIDE_TALL_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1, 2, 1),
    mass=1,
    offset=Vector3d(0, 1, 0),
    positionY=1
)
_SHELF_1_CUBBY_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.78, 0.77, 0.4),
    mass=3,
    offset=Vector3d(0, 0.385, 0),
    positionY=0,
    open_area_list=[
        # Remove the top of the shelf from this object because it's not
        # reachable by the performer agent at larger scales.
        # ObjectInteractableArea(
        #     dimensions=Vector3d(0.77, 0, 0.39),
        #     position=Vector3d(0, 0.78, 0)
        # ),
        ObjectInteractableArea(
            dimensions=Vector3d(0.38, 0.33, 0.33),
            position=Vector3d(0.175, 0.56, 0),
            area_id='top_right_shelf'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(0.38, 0.33, 0.33),
            position=Vector3d(-0.175, 0.56, 0),
            area_id='top_left_shelf'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(0.38, 0.33, 0.33),
            position=Vector3d(0.175, 0.21, 0),
            area_id='bottom_right_shelf'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(0.38, 0.33, 0.33),
            position=Vector3d(-0.175, 0.21, 0),
            area_id='bottom_left_shelf'
        )
    ]
)
_SHELF_2_TABLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.93, 0.73, 1.02),
    mass=4,
    offset=Vector3d(0, 0.355, 0),
    positionY=0,
    open_area_list=[
        # Remove the top of the shelf from this object because it's not
        # reachable by the performer agent at larger scales.
        # ObjectInteractableArea(
        #     dimensions=Vector3d(0.92, 0, 1.01),
        #     position=Vector3d(0, 0.73, 0)
        # ),
        ObjectInteractableArea(
            dimensions=Vector3d(0.65, 0.22, 0.87),
            position=Vector3d(0, 0.52, 0),
            area_id='middle_shelf'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(0.8, 0.235, 0.95),
            position=Vector3d(0, 0.225, 0),
            area_id='lower_shelf'
        )
    ]
)
_SOCCER_BALL_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.22, 0.22, 0.22),
    mass=1,
    offset=Vector3d(0, 0.11, 0),
    positionY=0.11
)
_SOFA_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(2.64, 1.15, 1.23),
    mass=45,
    offset=Vector3d(0, 0.575, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(1.95, 0, 0.6),
            position=Vector3d(0, 0.62, 0.24)
        )
    ]
)
_SOFA_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(2.55, 1.25, 0.95),
    mass=45,
    offset=Vector3d(0, 0.625, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(1.95, 0, 0.625),
            position=Vector3d(0, 0.59, 0.15)
        )
    ]
)
_SOFA_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(2.4, 1.25, 0.95),
    mass=45,
    offset=Vector3d(0, 0.625, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(1.95, 0, 0.625),
            position=Vector3d(0, 0.59, 0.15)
        )
    ]
)
_SOFA_CHAIR_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1.43, 1.15, 1.23),
    mass=30,
    offset=Vector3d(0, 0.575, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.77, 0, 0.6),
            position=Vector3d(0, 0.62, 0.24)
        )
    ]
)
_SOFA_CHAIR_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1.425, 1.25, 0.95),
    mass=30,
    offset=Vector3d(0, 0.625, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.975, 0, 0.65),
            position=Vector3d(0, 0.59, 0.15)
        )
    ]
)
_SOFA_CHAIR_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1.425, 1.25, 0.95),
    mass=30,
    offset=Vector3d(0, 0.625, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.975, 0, 0.65),
            position=Vector3d(0, 0.59, 0.15)
        )
    ]
)
_TABLE_1_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.69, 0.88, 1.63),
    mass=3,
    offset=Vector3d(0, 0.44, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.68, 0, 1.62),
            position=Vector3d(0.065, 0.88, -0.07)
        )
    ]
)
_TABLE_2_CIRCLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.67, 0.74, 0.67),
    mass=1,
    offset=Vector3d(0, 0.37, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.5, 0, 0.5),
            position=Vector3d(0, 0.74, 0)
        )
    ]
)
_TABLE_3_CIRCLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.573, 1.018, 0.557),
    mass=0.5,
    offset=Vector3d(0, 0.509, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.4, 0, 0.4),
            position=Vector3d(0, 0.84, 0)
        )
    ]
)
_TABLE_4_SEMICIRCLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.62, 0.62, 1.17),
    mass=4,
    offset=Vector3d(0, 0.31, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.45, 0, 0.8),
            position=Vector3d(0, 0.62, 0)
        )
    ]
)
_TABLE_5_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1.2, 0.7, 0.9),
    mass=8,
    offset=Vector3d(0, 0.35, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(1.2, 0, 0.9),
            position=Vector3d(0, 0.7, 0)
        )
    ]
)
_TABLE_7_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1.02, 0.45, 0.65),
    mass=3,
    offset=Vector3d(0, 0.22, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(1.02, 0, 0.65),
            position=Vector3d(0, 0.45, 0)
        )
    ]
)
_TABLE_8_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.65, 0.45, 1.02),
    mass=6,
    offset=Vector3d(0, 0.22, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(0.65, 0, 1.02),
            position=Vector3d(0, 0.45, 0)
        )
    ]
)
_TABLE_11_AND_12_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1, 0.5, 1),
    mass=12,
    offset=Vector3d(0, 0.5, 0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(1, 0, 1),
            position=Vector3d(0, 0.5, 0)
        )
    ]
)
_TOY_RACECAR_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.07, 0.06, 0.15),
    mass=0.5,
    offset=Vector3d(0, 0.03, 0),
    positionY=0.005
)
_TOY_SEDAN_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.075, 0.065, 0.14),
    mass=0.5,
    offset=Vector3d(0, 0.0325, 0),
    positionY=0.005
)
_TOY_TRAIN_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.16, 0.2, 0.23),
    mass=1,
    offset=Vector3d(0, 0.1, 0),
    positionY=0.005
)
_TOY_TROLLEY_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.16, 0.2, 0.23),
    mass=1,
    offset=Vector3d(0, 0.1, 0),
    positionY=0.005
)
_TOY_TRUCK_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.2, 0.18, 0.25),
    mass=1,
    offset=Vector3d(0, 0.09, 0),
    positionY=0.005
)
_TROPHY_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.19, 0.3, 0.14),
    mass=1,
    offset=Vector3d(0, 0.15, 0),
    positionY=0.005,
    sideways=ObjectSidewaysSize(
        dimensions=Vector3d(0.19, 0.14, 0.3),
        offset=Vector3d(0, 0, 0.15),
        positionY=0.075,
        rotation=Vector3d(90, 0, 0),
        switch_y_with_z=True
    )
)
_TURTLE_ON_WHEELS_SIZE = ObjectBaseSize(
    dimensions=Vector3d(0.24, 0.14, 0.085),
    mass=1,
    offset=Vector3d(0, 0.07, 0),
    positionY=0.005
)
_TV_SIZE = ObjectBaseSize(
    dimensions=Vector3d(1.234, 0.896, 0.256),
    mass=5,
    offset=Vector3d(0, 0.5, 0),
    positionY=0.5,
)


def _create_apple_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='apple_1',
        attributes=['moveable', 'pickupable'],
        color=['red'],
        materialCategory=[],
        salientMaterials=['food'],
        shape=['apple'],
        chooseSizeList=[
            _APPLE_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_apple_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='apple_2',
        attributes=['moveable', 'pickupable'],
        color=['green'],
        materialCategory=[],
        salientMaterials=['food'],
        shape=['apple'],
        chooseSizeList=[
            _APPLE_2_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_ball(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='ball',
        attributes=['moveable', 'pickupable'],
        shape=['ball'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _PRIMITIVE_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_block_blank_cube(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='block_blank_wood_cube',
        attributes=['moveable', 'pickupable'],
        occluder=True,
        shape=['blank block', 'cube'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BLOCK_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_block_blank_cylinder(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='block_blank_wood_cylinder',
        attributes=['moveable', 'pickupable'],
        occluder=True,
        shape=['blank block', 'cube'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BLOCK_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_block_letter(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        # Note: please ignore the "blue letter c" in the type: the object's
        # chosen material will change this design.
        type='block_blue_letter_c',
        attributes=['moveable', 'pickupable'],
        massMultiplier=2,
        materialCategory=['block_letter'],
        occluder=True,
        salientMaterials=['wood'],
        shape=['letter block', 'cube'],
        chooseSizeList=[
            _BLOCK_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_block_number(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        # Note: please ignore the "yellow number 1" in the type: the object's
        # chosen material will change this design.
        type='block_yellow_number_1',
        attributes=['moveable', 'pickupable'],
        massMultiplier=2,
        materialCategory=['block_number'],
        occluder=True,
        salientMaterials=['wood'],
        shape=['number block', 'cube'],
        stackTarget=True,
        chooseSizeList=[
            _BLOCK_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bookcase_1_shelf(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bookcase_1_shelf',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOOKCASE_1_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_bookcase_2_shelf(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bookcase_2_shelf',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOOKCASE_2_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_bookcase_3_shelf(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bookcase_3_shelf',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOOKCASE_3_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_bookcase_4_shelf(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bookcase_4_shelf',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOOKCASE_4_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_bookcase_1_shelf_sideless(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bookcase_1_shelf_sideless',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOOKCASE_1_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_bookcase_2_shelf_sideless(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bookcase_2_shelf_sideless',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOOKCASE_2_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_bookcase_3_shelf_sideless(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bookcase_3_shelf_sideless',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOOKCASE_3_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_bookcase_4_shelf_sideless(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bookcase_4_shelf_sideless',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOOKCASE_4_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_bowl_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bowl_3',
        attributes=['moveable', 'pickupable', 'receptacle'],
        shape=['bowl'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOWL_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bowl_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bowl_4',
        attributes=['moveable', 'pickupable', 'receptacle'],
        shape=['bowl'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOWL_4_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bowl_6(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bowl_6',
        attributes=['moveable', 'pickupable', 'receptacle'],
        shape=['bowl'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOWL_6_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_cake(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='cake',
        attributes=['moveable', 'pickupable'],
        color=['brown'],
        materials=[],
        salientMaterials=['food'],
        shape=['cake'],
        chooseSizeList=[
            _CAKE_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_cart(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='cart_1',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['cart'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CART_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_case_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='case_1',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CASE_1_SUITCASE_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_case_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='case_3',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CASE_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_chair_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_1',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_chair_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_2',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['stool'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_2_STOOL_CIRCLE_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_3',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['stool'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_3_STOOL_RECT_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_4',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_4_OFFICE_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chest_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chest_1',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['chest'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHEST_1_CUBOID_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chest_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chest_2',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['chest'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHEST_2_SEMICYLINDER_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chest_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chest_3',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['chest'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHEST_3_CUBOID_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chest_8(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chest_8',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['chest'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHEST_8_SEMICYLINDER_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_crayon(args: _FunctionArgs) -> ObjectDefinition:
    color = args.type.replace('crayon_', '')
    return ObjectDefinition(
        # The type should be in the format of 'crayon_<color>'
        type=args.type,
        attributes=['moveable', 'pickupable'],
        color=((['red'] if color == 'pink' else []) + [color]),
        materials=[],
        salientMaterials=['wax'],
        shape=['crayon'],
        chooseSizeList=[
            _CRAYON_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_crib(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='crib',
        attributes=[],
        obstacle=True,
        shape=['crib'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CRIB_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_cup_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='cup_2',
        attributes=['moveable', 'pickupable', 'receptacle'],
        shape=['cup'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CUP_2_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_cup_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='cup_3',
        attributes=['moveable', 'pickupable', 'receptacle'],
        shape=['cup'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CUP_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_cup_6(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='cup_6',
        attributes=['moveable', 'pickupable', 'receptacle'],
        shape=['cup'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CUP_6_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_dog_on_wheels(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='dog_on_wheels',
        attributes=['moveable', 'pickupable'],
        shape=['dog'],
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _DOG_ON_WHEELS_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_duck_on_wheels(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='duck_on_wheels',
        attributes=['moveable', 'pickupable'],
        shape=['duck'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DUCK_ON_WHEELS_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_foam_floor_tiles(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='foam_floor_tiles',
        attributes=['physics'],
        color=['blue', 'green', 'pink', 'purple', 'red', 'yellow'],
        materials=[],
        salientMaterials=['plastic'],
        shape=['foam floor tiles'],
        chooseSizeList=[
            _FOAM_FLOOR_TILES_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_letter_l_narrow_tall(args: _FunctionArgs) -> ObjectDefinition:
    definition = ObjectDefinition(
        type='letter_l_narrow',
        attributes=['physics'],
        shape=['letter l'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _PRIMITIVE_TALL_NARROW_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )
    definition.poleOffsetX = -0.2
    definition.poly = [
        {'x': 0.25, 'z': -0.5},
        {'x': -0.25, 'z': -0.5},
        {'x': -0.25, 'z': 0.5},
        {'x': -0.15, 'z': 0.5},
        {'x': -0.15, 'z': -0.4},
        {'x': 0.25, 'z': -0.4}
    ]
    return definition


def _create_letter_l_wide(args: _FunctionArgs) -> ObjectDefinition:
    definition = _create_primitive_non_cylinder(args)
    definition.poly = [
        {'x': 0.5, 'z': -0.5},
        {'x': -0.5, 'z': -0.5},
        {'x': -0.5, 'z': 0.5},
        {'x': 0, 'z': 0.5},
        {'x': 0, 'z': 0},
        {'x': 0.5, 'z': 0}
    ]
    return definition


def _create_letter_l_wide_tall(args: _FunctionArgs) -> ObjectDefinition:
    definition = ObjectDefinition(
        type=args.type,
        attributes=['physics'],
        shape=[args.type.replace('_', ' ')],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _PRIMITIVE_WIDE_TALL_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )
    definition.poly = [
        {'x': 0.5, 'z': -1.0},
        {'x': -0.5, 'z': -1.0},
        {'x': -0.5, 'z': 1.0},
        {'x': 0, 'z': 1.0},
        {'x': 0, 'z': -0.5},
        {'x': 0.5, 'z': -0.5}
    ]
    return definition


def _create_pacifier(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='pacifier',
        attributes=['moveable', 'pickupable'],
        color=['blue'],
        materials=[],
        salientMaterials=['plastic'],
        shape=['pacifier'],
        chooseSizeList=[
            _PACIFIER_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_plate_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='plate_1',
        attributes=['moveable', 'pickupable', 'receptacle'],
        shape=['plate'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _PLATE_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_plate_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='plate_3',
        attributes=['moveable', 'pickupable', 'receptacle'],
        shape=['plate'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _PLATE_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_plate_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='plate_4',
        attributes=['moveable', 'pickupable', 'receptacle'],
        shape=['plate'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _PLATE_4_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_primitive_cylinder(args: _FunctionArgs) -> ObjectDefinition:
    size_list = [
        _PRIMITIVE_SIZE.make(size) for size in args.size_multiplier_list
    ]
    for size in size_list:
        # Halve the Y scale here, but not its dimensions or other properties,
        # because Unity will automatically double a cylinder's height.
        size.scale.y *= 0.5
    return ObjectDefinition(
        type='cylinder',
        attributes=['physics'],
        shape=['cylinder'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=size_list
    )


# Size data for non-cylinder primitive objects (cones, cubes, spheres, etc.)
def _create_primitive_non_cylinder(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type=args.type,
        attributes=['physics'],
        shape=[args.type.replace('_', ' ')],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _PRIMITIVE_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_soccer_ball(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='soccer_ball',
        attributes=['moveable', 'pickupable'],
        color=['white', 'black'],
        materials=[],
        salientMaterials=['rubber'],
        shape=['ball'],
        chooseSizeList=[
            _SOCCER_BALL_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_shelf_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='shelf_1',
        attributes=['receptacle'],
        obstacle=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _SHELF_1_CUBBY_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_shelf_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='shelf_2',
        attributes=['receptacle'],
        obstacle=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _SHELF_2_TABLE_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_sofa_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_1',
        attributes=['receptacle'],
        materialCategory=['sofa_1'],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_2',
        attributes=['receptacle'],
        materialCategory=['sofa_2'],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_2_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_3',
        attributes=['receptacle'],
        materialCategory=['sofa_3'],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_chair_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_chair_1',
        attributes=['receptacle'],
        # This material must be sofa_chair_1, but the rest are just sofa_X
        materialCategory=['sofa_chair_1'],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_CHAIR_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_chair_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_chair_2',
        attributes=['receptacle'],
        materialCategory=['sofa_2'],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_CHAIR_2_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_chair_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_chair_3',
        attributes=['receptacle'],
        materialCategory=['sofa_3'],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_CHAIR_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_table_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_1',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TABLE_1_RECT_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_table_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_2',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_2_CIRCLE_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_3',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TABLE_3_CIRCLE_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_4',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TABLE_4_SEMICIRCLE_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_5(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_5',
        attributes=['receptacle'],
        occluder=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TABLE_5_RECT_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_7(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_7',
        attributes=['receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TABLE_7_RECT_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_8(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_8',
        attributes=['receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TABLE_8_RECT_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_11(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_11',
        attributes=['receptacle'],
        occluder=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_11_AND_12_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_12(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_12',
        attributes=['receptacle'],
        occluder=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_11_AND_12_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_toy_racecar(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='racecar_red',
        attributes=['moveable', 'pickupable'],
        shape=['car'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_RACECAR_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_toy_sedan(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='car_1',
        attributes=['moveable', 'pickupable'],
        shape=['car'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_SEDAN_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_train(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='train_1',
        attributes=['moveable', 'pickupable'],
        shape=['train'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TRAIN_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_trolley(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='trolley_1',
        attributes=['moveable', 'pickupable'],
        shape=['trolley'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TROLLEY_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_truck(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='truck_1',
        attributes=['moveable', 'pickupable'],
        shape=['truck'],
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TOY_TRUCK_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_trophy(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='trophy',
        attributes=['moveable', 'pickupable'],
        color=['grey'],
        materials=[],
        salientMaterials=['metal'],
        shape=['trophy'],
        chooseSizeList=[
            _TROPHY_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_turtle_on_wheels(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='turtle_on_wheels',
        attributes=['moveable', 'pickupable'],
        shape=['turtle'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TURTLE_ON_WHEELS_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_tv(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='tv_2',
        attributes=[],
        color=['grey', 'black'],
        materials=[],
        occluder=True,
        salientMaterials=['plastic'],
        shape=['television'],
        chooseSizeList=[
            _TV_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


class TypeDetailsTuple(NamedTuple):
    definition_function: Callable[[_FunctionArgs], ObjectDefinition]
    material_restrictions: List[Tuple[str, List[str]]]


"""Given a type, returns details that include a function to create and any
    material restrictions.  If materials restrictions is None, the shape can
    be any material."""
_TYPES_TO_DETAILS: Dict[str, TypeDetailsTuple] = {
    # primitives
    'circle_frustum': TypeDetailsTuple(
        _create_primitive_non_cylinder,
        None
    ), 'cone': TypeDetailsTuple(
        _create_primitive_non_cylinder,
        None
    ), 'cube': TypeDetailsTuple(
        _create_primitive_non_cylinder,
        None
    ), 'cylinder': TypeDetailsTuple(
        _create_primitive_cylinder,
        None
    ), 'letter_l_narrow': TypeDetailsTuple(
        _create_letter_l_narrow_tall,
        None
    ), 'letter_l_wide': TypeDetailsTuple(
        _create_letter_l_wide,
        None
    ), 'letter_l_wide_tall': TypeDetailsTuple(
        _create_letter_l_wide_tall,
        None
    ), 'pyramid': TypeDetailsTuple(
        _create_primitive_non_cylinder,
        None
    ), 'sphere': TypeDetailsTuple(
        _create_primitive_non_cylinder,
        None
    ), 'square_frustum': TypeDetailsTuple(
        _create_primitive_non_cylinder,
        None
    ), 'triangle': TypeDetailsTuple(
        _create_primitive_non_cylinder,
        None
    ), 'tube_narrow': TypeDetailsTuple(
        _create_primitive_non_cylinder,
        None
    ), 'tube_wide': TypeDetailsTuple(
        _create_primitive_non_cylinder,
        None
        # non-primitives
    ), 'apple_1': TypeDetailsTuple(
        _create_apple_1,
        None
    ), 'apple_2': TypeDetailsTuple(
        _create_apple_2,
        None
    ), 'ball': TypeDetailsTuple(
        _create_ball,
        (BLOCK_BLANK_MATERIALS + METAL_MATERIALS +
         PLASTIC_MATERIALS + RUBBER_MATERIALS + WOOD_MATERIALS)
    ), 'block_blank_blue_cube': TypeDetailsTuple(
        _create_block_blank_cube,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'block_blank_red_cube': TypeDetailsTuple(
        _create_block_blank_cube,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'block_blank_wood_cube': TypeDetailsTuple(
        _create_block_blank_cube,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'block_blank_yellow_cube': TypeDetailsTuple(
        _create_block_blank_cube,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'block_blank_blue_cylinder': TypeDetailsTuple(
        _create_block_blank_cylinder,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'block_blank_red_cylinder': TypeDetailsTuple(
        _create_block_blank_cylinder,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'block_blank_wood_cylinder': TypeDetailsTuple(
        _create_block_blank_cylinder,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'block_blank_yellow_cylinder': TypeDetailsTuple(
        _create_block_blank_cylinder,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'block_blue_letter_a': TypeDetailsTuple(
        _create_block_letter,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_blue_letter_b': TypeDetailsTuple(
        _create_block_letter,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_blue_letter_c': TypeDetailsTuple(
        _create_block_letter,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_blue_letter_d': TypeDetailsTuple(
        _create_block_letter,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_blue_letter_m': TypeDetailsTuple(
        _create_block_letter,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_blue_letter_s': TypeDetailsTuple(
        _create_block_letter,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_yellow_number_1': TypeDetailsTuple(
        _create_block_number,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_yellow_number_2': TypeDetailsTuple(
        _create_block_number,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_yellow_number_3': TypeDetailsTuple(
        _create_block_number,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_yellow_number_4': TypeDetailsTuple(
        _create_block_number,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_yellow_number_5': TypeDetailsTuple(
        _create_block_number,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'block_yellow_number_6': TypeDetailsTuple(
        _create_block_number,
        BLOCK_LETTER_MATERIALS + BLOCK_NUMBER_MATERIALS
    ), 'bookcase_1_shelf': TypeDetailsTuple(
        _create_bookcase_1_shelf,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'bookcase_2_shelf': TypeDetailsTuple(
        _create_bookcase_2_shelf,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'bookcase_3_shelf': TypeDetailsTuple(
        _create_bookcase_3_shelf,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'bookcase_4_shelf': TypeDetailsTuple(
        _create_bookcase_4_shelf,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'bookcase_1_shelf_sideless': TypeDetailsTuple(
        _create_bookcase_1_shelf_sideless,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'bookcase_2_shelf_sideless': TypeDetailsTuple(
        _create_bookcase_2_shelf_sideless,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'bookcase_3_shelf_sideless': TypeDetailsTuple(
        _create_bookcase_3_shelf_sideless,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'bookcase_4_shelf_sideless': TypeDetailsTuple(
        _create_bookcase_4_shelf_sideless,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'bowl_3': TypeDetailsTuple(
        _create_bowl_3,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'bowl_4': TypeDetailsTuple(
        _create_bowl_4,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'bowl_6': TypeDetailsTuple(
        _create_bowl_6,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'cake': TypeDetailsTuple(
        _create_cake,
        None
    ), 'car_1': TypeDetailsTuple(
        _create_toy_sedan,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'cart_1': TypeDetailsTuple(
        _create_cart,
        METAL_MATERIALS
    ), 'case_1': TypeDetailsTuple(
        _create_case_1,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'case_3': TypeDetailsTuple(
        _create_case_3,
        None
    ), 'chair_1': TypeDetailsTuple(
        _create_chair_1,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_2': TypeDetailsTuple(
        _create_chair_2,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_3': TypeDetailsTuple(
        _create_chair_3,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_4': TypeDetailsTuple(
        _create_chair_4,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_1': TypeDetailsTuple(
        _create_chest_1,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_2': TypeDetailsTuple(
        _create_chest_2,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_3': TypeDetailsTuple(
        _create_chest_3,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_8': TypeDetailsTuple(
        _create_chest_8,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'crayon_black': TypeDetailsTuple(
        _create_crayon,
        None
    ), 'crayon_blue': TypeDetailsTuple(
        _create_crayon,
        None
    ), 'crayon_green': TypeDetailsTuple(
        _create_crayon,
        None
    ), 'crayon_pink': TypeDetailsTuple(
        _create_crayon,
        None
    ), 'crayon_red': TypeDetailsTuple(
        _create_crayon,
        None
    ), 'crayon_yellow': TypeDetailsTuple(
        _create_crayon,
        None
    ), 'crib': TypeDetailsTuple(
        _create_crib,
        WOOD_MATERIALS
    ), 'cup_2': TypeDetailsTuple(
        _create_cup_2,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'cup_3': TypeDetailsTuple(
        _create_cup_3,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'cup_6': TypeDetailsTuple(
        _create_cup_6,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'dog_on_wheels': TypeDetailsTuple(
        _create_dog_on_wheels,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'duck_on_wheels': TypeDetailsTuple(
        _create_duck_on_wheels,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'foam_floor_tiles': TypeDetailsTuple(
        _create_foam_floor_tiles,
        None
    ), 'pacifier': TypeDetailsTuple(
        _create_pacifier,
        None
    ), 'plate_1': TypeDetailsTuple(
        _create_plate_1,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'plate_3': TypeDetailsTuple(
        _create_plate_3,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'plate_4': TypeDetailsTuple(
        _create_plate_4,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'racecar_red': TypeDetailsTuple(
        _create_toy_racecar,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'shelf_1': TypeDetailsTuple(
        _create_shelf_1,
        None
    ), 'shelf_2': TypeDetailsTuple(
        _create_shelf_2,
        None
    ), 'soccer_ball': TypeDetailsTuple(
        _create_soccer_ball,
        None
    ), 'sofa_1': TypeDetailsTuple(
        _create_sofa_1,
        SOFA_1_MATERIALS
    ), 'sofa_2': TypeDetailsTuple(
        _create_sofa_2,
        SOFA_2_MATERIALS
    ), 'sofa_3': TypeDetailsTuple(
        _create_sofa_3,
        SOFA_3_MATERIALS
    ), 'sofa_chair_1': TypeDetailsTuple(
        _create_sofa_chair_1,
        SOFA_CHAIR_1_MATERIALS
    ), 'sofa_chair_2': TypeDetailsTuple(
        _create_sofa_chair_2,
        SOFA_2_MATERIALS
    ), 'sofa_chair_3': TypeDetailsTuple(
        _create_sofa_chair_3,
        SOFA_3_MATERIALS
    ), 'suitcase_1': TypeDetailsTuple(
        _create_case_1,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'table_1': TypeDetailsTuple(
        _create_table_1,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_2': TypeDetailsTuple(
        _create_table_2,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_3': TypeDetailsTuple(
        _create_table_3,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_4': TypeDetailsTuple(
        _create_table_4,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_5': TypeDetailsTuple(
        _create_table_5,
        METAL_MATERIALS + WOOD_MATERIALS
    ), 'table_7': TypeDetailsTuple(
        _create_table_7,
        METAL_MATERIALS + WOOD_MATERIALS
    ), 'table_8': TypeDetailsTuple(
        _create_table_8,
        METAL_MATERIALS + WOOD_MATERIALS
    ), 'table_11': TypeDetailsTuple(
        _create_table_11,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_12': TypeDetailsTuple(
        _create_table_12,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'train_1': TypeDetailsTuple(
        _create_toy_train,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'trolley_1': TypeDetailsTuple(
        _create_toy_trolley,
        None
    ), 'trophy': TypeDetailsTuple(
        _create_trophy,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'truck_1': TypeDetailsTuple(
        _create_toy_truck,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'turtle_on_wheels': TypeDetailsTuple(
        _create_turtle_on_wheels,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'tv_2': TypeDetailsTuple(
        _create_tv, None
    )
    # TODO MCS-906 missing: changing_table, wardrobe, gift_box_1,
    # cube_hollow_narrow, cube_hollow_wide, hash, letter_x, lock_wall
}


_MATERIAL_TO_VALID_TYPE = {"_all_types": []}
for key, details in _TYPES_TO_DETAILS.items():
    mat_restr = details.material_restrictions
    if mat_restr is not None:
        for material in mat_restr:
            type_list = _MATERIAL_TO_VALID_TYPE.get(material[0])
            if type_list is None:
                type_list = []
                _MATERIAL_TO_VALID_TYPE[material[0]] = type_list
            type_list.append(key)
    else:
        _MATERIAL_TO_VALID_TYPE["_all_types"].append(key)


def get_type_from_material(material: str) -> str:
    """Given a material string, return a type/shape or None if a valid
    type/shape cannot be found."""
    type_list = (
        _MATERIAL_TO_VALID_TYPE.get(material, []) +
        _MATERIAL_TO_VALID_TYPE["_all_types"])
    # not empty or None
    if type_list:
        shape = random.choice(type_list)
    else:
        shape = random.choice(FULL_TYPE_LIST)
    if is_valid_shape_material(shape, material):
        return shape
    else:
        return None


def get_material_restriction(shape: str) -> List[str]:
    """Return the list of materials that are valid for the given shape.
    If no restrictions are present, return all materials"""
    if shape in _TYPES_TO_DETAILS:
        details = _TYPES_TO_DETAILS[shape]
        if details is None or details.material_restrictions is None:
            return ALL_MATERIAL_TUPLES
        else:
            return details.material_restrictions
    return []


def has_material_restriction(shape: str) -> bool:
    """Returns whether the given shape has a material restriction or not"""
    return shape in _TYPES_TO_DETAILS and _TYPES_TO_DETAILS[shape] is not None


def is_valid_shape_material(
        shape: str, material: Union[str, Tuple[str, List[str]]]) -> bool:
    """returns whether shape and material combination are valid"""
    if shape in _TYPES_TO_DETAILS:
        if _TYPES_TO_DETAILS[shape] is None:
            return True
        restrictions = _TYPES_TO_DETAILS[shape].material_restrictions
        if restrictions is None:
            return True
        if not isinstance(material, Tuple):
            return any(material == mat_tuple[0] for mat_tuple in restrictions)
        if material not in restrictions:
            return False
    return True


# List of all currently supported object types (shapes).
FULL_TYPE_LIST: List[str] = list(_TYPES_TO_DETAILS.keys())


def create_specific_definition_from_base(
    type: str,
    color: List[str],
    materials: List[str],
    salient_materials: List[str],
    scale: Union[float, Vector3d],
    mass_override: float = None
) -> ObjectDefinition:
    """Create and return a definition for the given type that has the given
    options."""
    definition_function = _TYPES_TO_DETAILS.get(type).definition_function
    if not definition_function:
        raise SceneException(f'Object type not found: {type}')

    definition = definition_function(_FunctionArgs(
        chosen_material_list=[],
        # Use the scale as the size multipler here so that other properties
        # like dimensions and offset are also affected accordingly.
        size_multiplier_list=[scale],
        type=type
    ))
    # Set the color and materials here. Don't use materialCategory.
    # If the color or materials are not None, assume that they must always be
    # set to specific values and cannot be customized.
    if definition.color is None:
        definition.color = color
    if definition.materials is None:
        definition.materials = materials
    if definition.salientMaterials is None:
        definition.salientMaterials = salient_materials
    # Override the mass here if needed.
    if mass_override:
        definition.mass = mass_override
    return definition


def create_variable_definition_from_base(
    type: str,
    size_multiplier_list: List[Union[float, Vector3d]],
    chosen_material_list: List[ChosenMaterial] = None,
    attributes_overrides: List[str] = None
) -> ObjectDefinition:
    """Create and return a definition for the given type that varies with the
    given material and size options."""
    type_details = _TYPES_TO_DETAILS.get(type)
    definition_function = None
    if not type_details:
        raise SceneException(f'Object type not found: {type}')
    definition_function = type_details.definition_function

    definition = definition_function(_FunctionArgs(
        chosen_material_list=(chosen_material_list or []),
        size_multiplier_list=size_multiplier_list,
        type=type
    ))
    # Override the attributes here if needed.
    if attributes_overrides is not None:
        definition.attributes = attributes_overrides.copy()
    return definition


def create_soccer_ball(size: float = 1) -> ObjectDefinition:
    """Returns a deep copy of the soccer ball (Eval 4 interactive target)."""
    return _create_soccer_ball(_FunctionArgs(
        chosen_material_list=[],
        size_multiplier_list=[size],
        type='soccer_ball'
    ))
