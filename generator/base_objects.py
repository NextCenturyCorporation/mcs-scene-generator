from __future__ import annotations

import copy
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, NamedTuple, Tuple, Union

from machine_common_sense.config_manager import Vector3d
from shapely import geometry

from .definitions import ChosenMaterial, ObjectDefinition, SizeChoice
from .exceptions import SceneException
from .materials import (
    ALL_PRIMITIVE_MATERIAL_TUPLES,
    ALL_UNRESTRICTED_MATERIAL_STRINGS,
    ALL_UNRESTRICTED_MATERIAL_TUPLES,
    ARMCHAIR_THORKEA_MATERIALS,
    BLOCK_BLANK_MATERIALS,
    BLOCK_LETTER_MATERIALS,
    BLOCK_NUMBER_MATERIALS,
    LEATHER_ARMCHAIR_MATERIALS,
    METAL_MATERIALS,
    PLASTIC_MATERIALS,
    RUBBER_MATERIALS,
    SOFA_1_MATERIALS,
    SOFA_2_MATERIALS,
    SOFA_3_MATERIALS,
    SOFA_8_MATERIALS,
    SOFA_9_MATERIALS,
    SOFA_CHAIR_1_MATERIALS,
    SOFA_CHAIR_8_MATERIALS,
    SOFA_THORKEA_MATERIALS,
    TOOL_MATERIALS,
    WOOD_MATERIALS,
    MaterialTuple
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
    placer_offset_x: List[float] = None
    placer_offset_y: List[float] = None
    placer_offset_z: List[float] = None

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
            x=self.dimensions.x * x_multiplier,
            y=self.dimensions.y * y_multiplier,
            z=self.dimensions.z * z_multiplier
        )
        enclosedAreas = [area.to_dict(
            x_multiplier,
            y_multiplier,
            z_multiplier
        ) for area in (self.enclosed_area_list or [])]
        mass = round((
            self.mass * (x_multiplier + y_multiplier + z_multiplier) / 3.0
        ), 4) if self.mass else None
        offset = Vector3d(
            x=self.offset.x * x_multiplier,
            y=self.offset.y * y_multiplier,
            z=self.offset.z * z_multiplier
        )
        openAreas = [area.to_dict(
            x_multiplier,
            y_multiplier,
            z_multiplier
        ) for area in (self.open_area_list or [])]
        placer_offset_x = [
            (offset_x * x_multiplier) for offset_x in
            (self.placer_offset_x or [0])
        ]
        placer_offset_y = [
            (offset_y * y_multiplier) for offset_y in
            (self.placer_offset_y or [0])
        ]
        placer_offset_z = [
            (offset_z * z_multiplier) for offset_z in
            (self.placer_offset_z or [0])
        ]
        positionY = (self.positionY * y_multiplier)
        scale = Vector3d(x=x_multiplier, y=y_multiplier, z=z_multiplier)
        sideways = {
            'dimensions': Vector3d(
                x=self.sideways.dimensions.x * x_sideways,
                y=self.sideways.dimensions.y * y_sideways,
                z=self.sideways.dimensions.z * z_sideways
            ),
            'offset': Vector3d(
                x=self.sideways.offset.x * x_sideways,
                y=self.sideways.offset.y * y_sideways,
                z=self.sideways.offset.z * z_sideways
            ),
            'positionY': self.sideways.positionY * y_sideways,
            'rotation': Vector3d(
                x=self.sideways.rotation.x,
                y=self.sideways.rotation.y,
                z=self.sideways.rotation.z
            )
        } if self.sideways else None
        size = _choose_size_text(dimensions)
        return SizeChoice(
            dimensions=dimensions,
            enclosedAreas=enclosedAreas,
            mass=mass,
            offset=offset,
            openAreas=openAreas,
            placerOffsetX=placer_offset_x,
            placerOffsetY=placer_offset_y,
            placerOffsetZ=placer_offset_z,
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


_ANTIQUE_ARMCHAIR_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.35, y=0.45, z=0.33),
    mass=5,
    offset=Vector3d(x=0, y=0.225, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.22, y=0, z=0.2),
            position=Vector3d(x=0, y=0.775, z=0.06),
        )
    ]
)
_ANTIQUE_ARMCHAIR_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=1.7, z=1.4),
    mass=10,
    offset=Vector3d(x=0, y=0.85, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.94, y=0, z=0.94),
            position=Vector3d(x=0, y=0.72, z=0.14),
        )
    ]
)
_ANTIQUE_ARMCHAIR_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.3, y=1.7, z=1.6),
    mass=10,
    offset=Vector3d(x=0, y=0.85, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.02, y=0, z=1.12),
            position=Vector3d(x=0, y=0.7, z=0.2),
        )
    ]
)
_ANTIQUE_CHAIR_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.76, y=1.26, z=0.64),
    mass=10,
    offset=Vector3d(x=0, y=0.63, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.52, y=0, z=0.4),
            position=Vector3d(x=0, y=1.08, z=0.08),
        )
    ]
)
_ANTIQUE_CHAIR_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.8, y=1.72, z=1),
    mass=5,
    offset=Vector3d(x=0, y=0.86, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.64, y=0, z=0.64),
            position=Vector3d(x=0, y=0.88, z=0.12),
        )
    ]
)
_ANTIQUE_CHAIR_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.84, y=1.72, z=0.84),
    mass=5,
    offset=Vector3d(x=0, y=0.86, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.64, y=0, z=0.68),
            position=Vector3d(x=0, y=0.8, z=0.1),
        )
    ]
)
_ANTIQUE_SOFA_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2, y=1.4, z=0.68),
    mass=20,
    offset=Vector3d(x=0, y=0.7, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.7, y=0, z=0.4),
            position=Vector3d(x=0, y=1.1, z=0.1),
        )
    ]
)
_ANTIQUE_TABLE_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.77, y=0.48, z=0.77),
    mass=5,
    offset=Vector3d(x=0, y=0.24, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.72, y=0, z=0.72),
            position=Vector3d(x=0, y=0.98, z=0),
        )
    ]
)
_APPLE_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.111, y=0.12, z=0.122),
    mass=0.5,
    offset=Vector3d(x=0, y=0.005, z=0),
    placer_offset_y=[0.04],
    positionY=0.03
)
_APPLE_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.117, y=0.121, z=0.116),
    mass=0.5,
    offset=Vector3d(x=0, y=0.002, z=0),
    placer_offset_y=[0.04],
    positionY=0.03
)
_BARREL_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.86, y=0.8, z=0.86),
    mass=10,
    offset=Vector3d(x=0, y=0.4, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.48, y=0.48, z=0.48),
            position=Vector3d(x=0, y=0.52, z=0)
        )
    ]
)
_BARREL_2_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.73, y=0.93, z=0.73),
    dimensions=Vector3d(x=0.73, y=0.93, z=0.95),
    mass=10,
    offset=Vector3d(x=0, y=0.465, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.38, y=0.66, z=0.38),
            position=Vector3d(x=0, y=0.41, z=0)
        )
    ]
)
_BARREL_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.73, y=0.93, z=0.73),
    mass=10,
    offset=Vector3d(x=0, y=0.465, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.38, y=0.6, z=0.38),
            position=Vector3d(x=0, y=0.38, z=0)
        )
    ]
)
_BARREL_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.73, y=0.82, z=0.73),
    mass=10,
    offset=Vector3d(x=0, y=0.41, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.38, y=0.64, z=0.38),
            position=Vector3d(x=0, y=0.41, z=0)
        )
    ]
)
_BED_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.299, y=1.015, z=2.108),
    mass=20,
    offset=Vector3d(x=0, y=0.508, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.15, y=0, z=1.93),
            position=Vector3d(x=0, y=0.56, z=0)
        )
    ]
)
_BED_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.536, y=1.096, z=2.429),
    mass=25,
    offset=Vector3d(x=0, y=0.546, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.43, y=0, z=2.27),
            position=Vector3d(x=0, y=0.82, z=0)
        )
    ]
)
_BED_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.475, y=0.726, z=2.113),
    mass=25,
    offset=Vector3d(x=0, y=0.367, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.33, y=0, z=1.98),
            position=Vector3d(x=0, y=0.52, z=0)
        )
    ]
)
_BED_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.947, y=1.751, z=2.275),
    mass=30,
    offset=Vector3d(x=0, y=0.875, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.78, y=0, z=2.14),
            position=Vector3d(x=0, y=0.85, z=0)
        )
    ]
)
_BED_5_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.261, y=1.044, z=2.371),
    mass=20,
    offset=Vector3d(x=0, y=0.511, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.19, y=0, z=2.19),
            position=Vector3d(x=0, y=0.85, z=0)
        )
    ]
)
_BED_6_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.15, y=2.2, z=2.534),
    mass=30,
    offset=Vector3d(x=0, y=1.1, z=0),
    positionY=0
)
_BED_7_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.08, y=1.23, z=2.02),
    mass=20,
    offset=Vector3d(x=0, y=0.615, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.87, y=0, z=1.78),
            position=Vector3d(x=0, y=0.458, z=0)
        )
    ]
)
_BED_8_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.88, y=0.7, z=1.7),
    mass=20,
    offset=Vector3d(x=0, y=0.35, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.7, y=0, z=1.55),
            position=Vector3d(x=0, y=0.384, z=0)
        )
    ]
)
_BED_9_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1, z=2),
    mass=20,
    offset=Vector3d(x=0, y=0.5, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.85, y=0, z=1.85),
            position=Vector3d(x=0, y=0.396, z=0)
        )
    ]
)
_BED_10_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.25, y=0.94, z=2.17),
    mass=20,
    offset=Vector3d(x=0, y=0.47, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.04, y=0, z=1.92),
            position=Vector3d(x=0, y=0.558, z=0)
        )
    ]
)
_BED_11_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2, y=1.45, z=3.2),
    mass=50,
    offset=Vector3d(x=0, y=0.725, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.9, y=0, z=2.8),
            position=Vector3d(x=0, y=1.1, z=-0.145)
        )
    ]
)
_BED_12_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2, y=2.2, z=3.2),
    mass=50,
    offset=Vector3d(x=0, y=1.1, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.9, y=0, z=2.8),
            position=Vector3d(x=0, y=1.1, z=-0.145)
        )
    ]
)
_BIN_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.5, y=0.38, z=0.34),
    mass=5,
    offset=Vector3d(x=0, y=0.19, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.383, y=0.338, z=0.218),
            position=Vector3d(x=0, y=0.203, z=0)
        )
    ]
)
_BIN_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.44, y=0.46, z=0.28),
    mass=5,
    offset=Vector3d(x=0, y=0.23, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.33, y=0.382, z=0.188),
            position=Vector3d(x=0, y=0.24, z=0)
        )
    ]
)
_BLOCK_BLANK_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.1, y=0.1, z=0.1),
    mass=0.333,
    offset=Vector3d(x=0, y=0.05, z=0),
    positionY=0.05
)
_BLOCK_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.1, y=0.1, z=0.1),
    mass=0.333,
    offset=Vector3d(x=0, y=0.05, z=0),
    positionY=0
)
_BOOKCASE_1_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1, z=0.5),
    mass=6,
    offset=Vector3d(x=0, y=0.5, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=0.04, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=0.52, z=0)
        )
    ]
)
_BOOKCASE_2_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1.5, z=0.5),
    mass=12,
    offset=Vector3d(x=0, y=0.75, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=0.04, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=0.52, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_2',
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=1.02, z=0)
        )
    ]
)
_BOOKCASE_3_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=2, z=0.5),
    mass=18,
    offset=Vector3d(x=0, y=1, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=0.04, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=0.52, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_2',
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=1.02, z=0)
        )
    ]
)
_BOOKCASE_4_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=2.5, z=0.5),
    mass=24,
    offset=Vector3d(x=0, y=1, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=0.04, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=0.52, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_2',
            dimensions=Vector3d(x=0.5, y=0, z=0.25),
            position=Vector3d(x=0, y=1.02, z=0)
        )
    ]
)
_BOWL_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.175, y=0.116, z=0.171),
    mass=0.5,
    offset=Vector3d(x=0, y=0.055, z=0),
    placer_offset_y=[0.07],
    positionY=0.005,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.138, y=0.2, z=0.138),
            position=Vector3d(x=0, y=0.102, z=0)
        )
    ]
)
_BOWL_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.209, y=0.059, z=0.206),
    mass=0.5,
    offset=Vector3d(x=0, y=0.027, z=0),
    placer_offset_y=[0.02],
    positionY=0.005,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.18, y=0.1, z=0.18),
            position=Vector3d(x=0, y=0.052, z=0)
        )
    ]
)
_BOWL_6_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.19, y=0.1, z=0.19),
    mass=0.5,
    offset=Vector3d(x=0, y=0.052, z=0),
    placer_offset_y=[0.06],
    positionY=0.005,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.07, y=.18, z=0.07),
            position=Vector3d(x=0, y=0.092, z=0)
        )
    ]
)
_CAKE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.22, y=0.22, z=0.22),
    mass=1,
    offset=Vector3d(x=0, y=0.05, z=0),
    positionY=0.005
)
_CART_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.725, y=1.29, z=0.55),
    mass=4,
    offset=Vector3d(x=0, y=0.645, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.38, y=0, z=0.38),
            position=Vector3d(x=0, y=0.34, z=0)
        )
    ]
)
_CASE_1_SUITCASE_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.71, y=0.19, z=0.42),
    dimensions=Vector3d(x=0.71, y=0.19, z=0.54),
    mass=5,
    offset=Vector3d(x=0, y=0.095, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.69, y=0.175, z=0.4),
            position=Vector3d(x=0, y=0.0925, z=0)
        )
    ]
)
_CASE_2_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.78, y=0.16, z=0.48),
    dimensions=Vector3d(x=0.78, y=0.16, z=0.58),
    mass=5,
    offset=Vector3d(x=0, y=0.08, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.7, y=0.135, z=0.4),
            position=Vector3d(x=0, y=0.0775, z=0)
        )
    ]
)
_CASE_3_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.81, y=0.21, z=0.56),
    dimensions=Vector3d(x=0.81, y=0.21, z=0.78),
    mass=5,
    offset=Vector3d(x=0, y=0.105, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.79, y=0.17, z=0.53),
            position=Vector3d(x=0, y=0.105, z=0)
        )
    ]
)
_CASE_4_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=1.68, y=1.12, z=1.12),
    dimensions=Vector3d(x=1.68, y=1.12, z=1.98),
    mass=8,
    offset=Vector3d(x=0, y=0.56, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.54, y=1.02, z=0.96),
            position=Vector3d(x=0, y=0.56, z=0)
        )
    ]
)
_CASE_5_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=1.18, y=0.94, z=0.94),
    dimensions=Vector3d(x=1.18, y=0.94, z=1.94),
    mass=8,
    offset=Vector3d(x=0, y=0.47, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.1, y=0.56, z=0.78),
            position=Vector3d(x=0, y=0.34, z=-0.01)
        )
    ]
)
_CASE_6_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.195, y=0.042, z=0.1),
    dimensions=Vector3d(x=0.195, y=0.042, z=0.144),
    mass=8,
    offset=Vector3d(x=0, y=0.021, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.185, y=0.034, z=0.085),
            position=Vector3d(x=0, y=0.021, z=-0.002)
        )
    ]
)
_CASE_7_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.195, y=0.036, z=0.1),
    dimensions=Vector3d(x=0.195, y=0.036, z=0.134),
    mass=8,
    offset=Vector3d(x=0, y=0.018, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.185, y=0.028, z=0.085),
            position=Vector3d(x=0, y=0.017, z=-0.002)
        )
    ]
)
_CART_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.42, y=0.7, z=0.51),
    mass=2,
    offset=Vector3d(x=0, y=0.35, z=0),
    placer_offset_y=[0.6],
    positionY=0.005
)
_CHAIR_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.54, y=1.04, z=0.46),
    mass=4,
    offset=Vector3d(x=0, y=0.51, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.38, y=0, z=0.38),
            position=Vector3d(x=0.01, y=0.5, z=-0.02)
        )
    ]
)
_CHAIR_2_STOOL_CIRCLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.3, y=0.75, z=0.3),
    mass=4,
    offset=Vector3d(x=0, y=0.375, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.2, y=0, z=0.2),
            position=Vector3d(x=0, y=0.75, z=0)
        )
    ]
)
_CHAIR_3_STOOL_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.42, y=0.8, z=0.63),
    mass=4,
    offset=Vector3d(x=0, y=0.4, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.3, y=0, z=0.6),
            position=Vector3d(x=0, y=1.3, z=0)
        )
    ]
)
_CHAIR_4_OFFICE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.54, y=0.88, z=0.44),
    mass=4,
    offset=Vector3d(x=0, y=0.44, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.32, y=0, z=0.32),
            position=Vector3d(x=-0.01, y=1.06, z=0.015)
        )
    ]
)
_CHAIR_5_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.489, y=0.864, z=0.577),
    mass=4,
    offset=Vector3d(x=0, y=0.416, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.378, y=0, z=0.448),
            position=Vector3d(x=0, y=0.383, z=0.04)
        )
    ]
)
_CHAIR_6_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.513, y=0.984, z=0.539),
    mass=4,
    offset=Vector3d(x=0, y=0.492, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.414, y=0, z=0.392),
            position=Vector3d(x=0, y=0.492, z=0.047)
        )
    ]
)
_CHAIR_7_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.447, y=0.891, z=0.443),
    mass=4,
    offset=Vector3d(x=0, y=0.446, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.413, y=0, z=0.309),
            position=Vector3d(x=0, y=0.425, z=0.049)
        )
    ]
)
_CHAIR_8_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.549, y=0.781, z=0.537),
    mass=4,
    offset=Vector3d(x=0, y=0.391, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0, z=0.395),
            position=Vector3d(x=0, y=0.389, z=0.059)
        )
    ]
)
_CHAIR_9_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.49, y=0.95, z=0.52),
    mass=4,
    offset=Vector3d(x=0, y=0.475, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.4, y=0, z=0.375),
            position=Vector3d(x=0, y=0.4632, z=0.55),
        )
    ]
)
_CHAIR_10_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.48, y=0.91, z=0.54),
    mass=4,
    offset=Vector3d(x=0, y=0.455, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.42, y=0, z=0.375),
            position=Vector3d(x=0, y=0.4502, z=0.061)
        )
    ]
)
_CHAIR_11_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.72, y=1.38, z=0.78),
    mass=8,
    offset=Vector3d(x=0, y=0.69, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.26, y=0, z=0.52),
            position=Vector3d(x=0, y=0.6, z=0.52)
        )
    ]
)
_CHAIR_12_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.6, y=0.84, z=0.76),
    mass=4,
    offset=Vector3d(x=0, y=0.42, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0, z=0.48),
            position=Vector3d(x=0, y=0.43, z=0.02)
        )
    ]
)
_CHAIR_13_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.42, y=0.74, z=0.4),
    mass=6,
    offset=Vector3d(x=0, y=0.37, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.34, y=0, z=0.3),
            position=Vector3d(x=0, y=0.74, z=0.04)
        )
    ]
)
_CHAIR_14_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.5, y=0.8, z=0.5),
    mass=6,
    offset=Vector3d(x=0, y=0.4, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.4, y=0, z=0.4),
            position=Vector3d(x=0, y=0.75, z=0)
        )
    ]
)
_CHAIR_15_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.42, y=0.94, z=0.4),
    mass=6,
    offset=Vector3d(x=0, y=0.47, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.34, y=0, z=0.3),
            position=Vector3d(x=0, y=0.74, z=0.04)
        )
    ]
)
_CHAIR_16_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.5, y=0.92, z=0.5),
    mass=6,
    offset=Vector3d(x=0, y=0.46, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.4, y=0, z=0.4),
            position=Vector3d(x=0, y=0.75, z=0)
        )
    ]
)
_CHANGING_TABLE_SIZE = ObjectBaseSize(
    # These are the closed dimensions and offset, if we ever need them.
    # dimensions=Vector3d(x=1.1, y=0.96, z=0.58),
    # offset=Vector3d(x=0, y=0.48, z=0),
    dimensions=Vector3d(x=1.1, y=0.96, z=0.89),
    mass=50,
    offset=Vector3d(x=0, y=0.48, z=0.155),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.68, y=0.22, z=0.41),
            position=Vector3d(x=0.165, y=0.47, z=-0.03),
            area_id='_drawer_top'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.68, y=0.2, z=0.41),
            position=Vector3d(x=0.175, y=0.19, z=-0.03),
            area_id='_drawer_bottom'
        )
    ],
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.05, y=0.2, z=0.44),
            position=Vector3d(x=0, y=0.725, z=-0.05),
            area_id='_shelf_top'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.32, y=0.25, z=0.44),
            position=Vector3d(x=-0.365, y=0.475, z=-0.05),
            area_id='_shelf_middle'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.32, y=0.25, z=0.44),
            position=Vector3d(x=-0.365, y=0.2, z=-0.05),
            area_id='_shelf_bottom'
        )
    ]
)
_CHEST_1_CUBOID_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.83, y=0.42, z=0.55),
    mass=5,
    offset=Vector3d(x=0, y=0.205, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.77, y=0.33, z=0.49),
            position=Vector3d(x=0, y=0.195, z=0)
        )
    ]
)
_CHEST_2_SEMICYLINDER_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.52, y=0.42, z=0.38),
    dimensions=Vector3d(x=0.52, y=0.42, z=0.72),
    mass=5,
    offset=Vector3d(x=0, y=0.21, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.44, y=0.25, z=0.31),
            position=Vector3d(x=0, y=0.165, z=0)
        )
    ]
)
_CHEST_3_CUBOID_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.46, y=0.26, z=0.32),
    dimensions=Vector3d(x=0.46, y=0.26, z=0.52),
    mass=5,
    offset=Vector3d(x=0, y=0.13, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.35, y=0.12, z=0.21),
            position=Vector3d(x=0, y=0.09, z=0)
        )
    ]
)
_CHEST_4_ROUNDED_LID_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.72, y=0.35, z=0.34),
    dimensions=Vector3d(x=0.72, y=0.35, z=0.6),
    mass=5,
    offset=Vector3d(x=0, y=0.175, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.64, y=0.24, z=0.24),
            position=Vector3d(x=0, y=0.16, z=0)
        )
    ]
)
_CHEST_5_ROUNDED_LID_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.46, y=0.28, z=0.42),
    dimensions=Vector3d(x=0.46, y=0.28, z=0.52),
    mass=5,
    offset=Vector3d(x=0, y=0.14, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.34, y=0.23, z=0.28),
            position=Vector3d(x=0, y=0.135, z=-0.01)
        )
    ]
)
_CHEST_6_TRAPEZOID_LID_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.5, y=0.36, z=0.38),
    dimensions=Vector3d(x=0.5, y=0.36, z=0.74),
    mass=5,
    offset=Vector3d(x=0, y=0.18, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.37, y=0.21, z=0.245),
            position=Vector3d(x=0, y=0.15, z=-0.01)
        )
    ]
)
_CHEST_7_PIRATE_TREASURE_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.59, y=0.49, z=0.42),
    dimensions=Vector3d(x=0.59, y=0.49, z=0.78),
    mass=5,
    offset=Vector3d(x=0, y=0.245, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.38, y=0.34, z=0.26),
            position=Vector3d(x=0, y=0.185, z=0)
        )
    ]
)
_CHEST_8_SEMICYLINDER_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.42, y=0.32, z=0.36),
    dimensions=Vector3d(x=0.42, y=0.32, z=0.68),
    mass=5,
    offset=Vector3d(x=0, y=0.16, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.36, y=0.135, z=0.28),
            position=Vector3d(x=0, y=0.09, z=0)
        )
    ]
)
_CHEST_9_TRAPEZOID_LID_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.84, y=0.41, z=0.42),
    dimensions=Vector3d(x=0.84, y=0.41, z=0.68),
    mass=5,
    offset=Vector3d(x=0, y=0.205, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.77, y=0.28, z=0.38),
            position=Vector3d(x=0, y=0.16, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_01_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=0.6, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.3, z=0),
    placer_offset_x=[0.4, -0.4],
    placer_offset_y=[0.4, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_02_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.5, z=0),
    placer_offset_x=[0.4, -0.4],
    placer_offset_y=[0.8, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_03_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.5, z=0),
    placer_offset_x=[0.4, -0.4],
    placer_offset_y=[0.4, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_04_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=0.6, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.3, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0.4, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_05_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=1, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.5, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0.8, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_06_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=1, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.5, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0.4, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_07_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=0.8, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.4, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0.4, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.605, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_08_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=1.2, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.6, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0.8, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.605, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_09_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=1.2, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.6, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0.4, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.605, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_10_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.2, y=0.4, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.2, z=0),
    placer_offset_x=[0.5, -0.5],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0.1, y=0.605, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_11_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.2, y=0.8, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.4, z=0),
    placer_offset_x=[0.5, -0.5],
    placer_offset_y=[0.4, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0.1, y=0.605, z=0)
        )
    ]
)
_CONTAINER_ASYMMETRIC_12_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.2, y=1.2, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.6, z=0),
    placer_offset_x=[0.5, -0.5],
    placer_offset_y=[0.8, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0.1, y=0.605, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_01_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=0.2, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.1, z=0),
    placer_offset_x=[0.4, -0.4],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_02_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=0.6, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.3, z=0),
    placer_offset_x=[0.4, -0.4],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_03_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.5, z=0),
    placer_offset_x=[0.4, -0.4],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_04_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=0.2, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.1, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_05_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=0.2, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.1, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_06_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=0.6, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.3, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_07_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=1, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.5, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.405, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_08_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=0.4, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.2, z=0),
    placer_offset_x=[0.4, -0.4],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.605, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_09_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=0.4, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.2, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.605, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_10_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=0.4, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.2, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.605, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_11_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=0.8, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.4, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.605, z=0)
        )
    ]
)
_CONTAINER_SYMMETRIC_12_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.4, y=1.2, z=1),
    mass=10,
    offset=Vector3d(x=0, y=0.6, z=0),
    placer_offset_x=[0.6, -0.6],
    placer_offset_y=[0, 0],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.6, y=0.6, z=0.8),
            position=Vector3d(x=0, y=0.605, z=0)
        )
    ]
)
_CRATE_1_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.8, y=0.8, z=0.8),
    dimensions=Vector3d(x=0.8, y=0.8, z=0.98),
    mass=5,
    offset=Vector3d(x=0, y=0.4, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.61, y=0.6, z=0.61),
            position=Vector3d(x=0, y=0.4, z=0)
        )
    ]
)
_CRATE_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.72, y=0.64, z=0.72),
    mass=5,
    offset=Vector3d(x=0, y=0.32, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.39, y=0.52, z=0.39),
            position=Vector3d(x=0, y=0.31, z=0)
        )
    ]
)
_CRATE_3_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.8, y=0.8, z=0.8),
    dimensions=Vector3d(x=0.8, y=0.8, z=0.98),
    mass=5,
    offset=Vector3d(x=0, y=0.4, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.61, y=0.6, z=0.61),
            position=Vector3d(x=0, y=0.4, z=0)
        )
    ]
)
_CRATE_4_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.76, y=0.74, z=0.76),
    dimensions=Vector3d(x=0.76, y=0.74, z=0.88),
    mass=5,
    offset=Vector3d(x=0, y=0.37, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.46, y=0.56, z=0.46),
            position=Vector3d(x=0, y=0.36, z=0)
        )
    ]
)
_CRATE_OPEN_TOPPED_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.8, y=0.8, z=0.8),
    mass=5,
    offset=Vector3d(x=0, y=0.4, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.61, y=0.6, z=0.61),
            position=Vector3d(x=0, y=0.4, z=0)
        )
    ]
)
_CRATE_OPEN_TOPPED_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.72, y=0.64, z=0.72),
    mass=5,
    offset=Vector3d(x=0, y=0.32, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.39, y=0.52, z=0.39),
            position=Vector3d(x=0, y=0.31, z=0)
        )
    ]
)
_CRAYON_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.01, y=0.085, z=0.01),
    mass=0.125,
    offset=Vector3d(x=0, y=0.0425, z=0),
    positionY=0.005
)
_CRIB_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.65, y=0.9, z=1.25),
    mass=10,
    offset=Vector3d(x=0, y=0.45, z=0),
    positionY=0,
)
_CUP_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.105, y=0.135, z=0.104),
    mass=0.5,
    offset=Vector3d(x=0, y=0.064, z=0),
    placer_offset_y=[0.04],
    positionY=0.005,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.05, y=.18, z=0.05),
            position=Vector3d(x=0, y=0.092, z=0)
        )
    ]
)
_CUP_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.123, y=0.149, z=0.126),
    mass=0.5,
    offset=Vector3d(x=0, y=0.072, z=0),
    placer_offset_y=[0.04],
    positionY=0.005,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.04, y=2, z=0.04),
            position=Vector3d(x=0, y=0.12, z=0)
        )
    ]
)
_CUP_6_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.106, y=0.098, z=0.106),
    mass=0.5,
    offset=Vector3d(x=0, y=0.046, z=0),
    placer_offset_y=[0.04],
    positionY=0.005,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.05, y=.14, z=0.05),
            position=Vector3d(x=0, y=0.09, z=0)
        )
    ]
)
_DESK_1_AND_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1, z=1),
    mass=15,
    offset=Vector3d(x=0, y=0.5, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0, z=1),
            position=Vector3d(x=0, y=1, z=0)
        )
    ]
)
_DESK_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.5, y=1, z=1.5),
    mass=18,
    offset=Vector3d(x=0, y=0.5, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0, z=1),
            position=Vector3d(x=0, y=1, z=0)
        )
    ]
)
_DESK_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=2, z=1),
    mass=24,
    offset=Vector3d(x=0, y=1, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0, z=1),
            position=Vector3d(x=0, y=1, z=0)
        )
    ]
)
_DOG_ON_WHEELS_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.355, y=0.134, z=0.071),
    mass=2,
    offset=Vector3d(x=0, y=0.067, z=0),
    placer_offset_y=[0.03],
    positionY=0.005
)
_DOG_ON_WHEELS_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.5, y=1.12, z=1.44),
    mass=4,
    offset=Vector3d(x=0, y=0.56, z=0),
    placer_offset_y=[0.35],
    positionY=0.005
)
_DOUBLE_BOOKCASE_1_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2, y=1, z=0.5),
    mass=12,
    offset=Vector3d(x=0, y=0.5, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=0.04, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=0.52, z=0)
        )
    ]
)
_DOUBLE_BOOKCASE_2_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2, y=1.5, z=0.5),
    mass=24,
    offset=Vector3d(x=0, y=0.75, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=0.04, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=0.52, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_2',
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=1.02, z=0)
        )
    ]
)
_DOUBLE_BOOKCASE_3_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2, y=2, z=0.5),
    mass=36,
    offset=Vector3d(x=0, y=1, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=0.04, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=0.52, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_2',
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=1.02, z=0)
        )
    ]
)
_DOUBLE_BOOKCASE_4_SHELF_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2, y=2.5, z=0.5),
    mass=48,
    offset=Vector3d(x=0, y=1, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=0.04, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_1',
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=0.52, z=0)
        ),
        ObjectInteractableArea(
            area_id='shelf_2',
            dimensions=Vector3d(x=0.9, y=0, z=0.45),
            position=Vector3d(x=0, y=1.02, z=0)
        )
    ]
)
_DUCK_ON_WHEELS_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.21, y=0.17, z=0.065),
    mass=1,
    offset=Vector3d(x=0, y=0.085, z=0),
    placer_offset_y=[0.01],
    positionY=0.005
)
_DUCK_ON_WHEELS_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.224, y=0.176, z=0.06),
    mass=1,
    offset=Vector3d(x=0, y=0.088, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_FOAM_FLOOR_TILES_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=9, y=0.01, z=9),
    mass=2,
    offset=Vector3d(x=0, y=0.01, z=0),
    positionY=0.01
)
_LID_SQUARE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=0.08, z=1),
    mass=0.25,
    offset=Vector3d(x=0, y=0, z=0),
    positionY=0,
    placer_offset_y=[0.04],
)
_MILITARY_CASE_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.66, y=0.82, z=0.62),
    mass=5,
    offset=Vector3d(x=0, y=0.41, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.56, y=0.7, z=0.52),
            position=Vector3d(x=0, y=0.37, z=0)
        )
    ]
)
_MILITARY_CASE_2_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.8, y=0.44, z=0.5),
    dimensions=Vector3d(x=0.8, y=0.44, z=0.7),
    mass=5,
    offset=Vector3d(x=0, y=0.22, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.72, y=0.26, z=0.36),
            position=Vector3d(x=0, y=0.16, z=0)
        )
    ]
)
_MILITARY_CASE_3_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=1.26, y=0.54, z=0.54),
    dimensions=Vector3d(x=1.26, y=0.54, z=0.76),
    mass=5,
    offset=Vector3d(x=0, y=0.27, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.14, y=0.38, z=0.44),
            position=Vector3d(x=0, y=0.21, z=0)
        )
    ]
)
_MILITARY_CASE_4_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.86, y=0.32, z=0.58),
    dimensions=Vector3d(x=0.86, y=0.32, z=0.68),
    mass=5,
    offset=Vector3d(x=0, y=0.16, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.76, y=0.24, z=0.48),
            position=Vector3d(x=0, y=0.14, z=0)
        )
    ]
)
_PACIFIER_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.07, y=0.04, z=0.05),
    mass=0.125,
    offset=Vector3d(x=0, y=0.02, z=0),
    positionY=0.005
)
_PLATE_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.208, y=0.117, z=0.222),
    mass=0.5,
    offset=Vector3d(x=0, y=0.057, z=0),
    placer_offset_y=[0.1],
    positionY=0.005
)
_PLATE_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.304, y=0.208, z=0.305),
    mass=0.5,
    offset=Vector3d(x=0, y=0.098, z=0),
    placer_offset_y=[0.19],
    positionY=0.005
)
_PLATE_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.202, y=0.113, z=0.206),
    mass=0.5,
    offset=Vector3d(x=0, y=0.053, z=0),
    placer_offset_y=[0.1],
    positionY=0.005
)
_PRIMITIVE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1, z=1),
    mass=1,
    offset=Vector3d(x=0, y=0.5, z=0),
    positionY=0.5
)
_PRIMITIVE_ON_GROUND_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1, z=1),
    mass=1,
    offset=Vector3d(x=0, y=0.5, z=0),
    positionY=0
)
_PRIMITIVE_TALL_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=2, z=1),
    mass=1,
    offset=Vector3d(x=0, y=1, z=0),
    positionY=1
)
_PRIMITIVE_TALL_NARROW_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.5, y=1, z=0.5),
    mass=1,
    offset=Vector3d(x=0, y=0.5, z=0),
    # Will be multiplied by the object's X or Z dimension (so it's really 0.2)
    placer_offset_x=[0.4],
    positionY=0.5
)
_PRIMITIVE_TRIANGLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1, z=1),
    mass=1,
    offset=Vector3d(x=0, y=0.5, z=0),
    placer_offset_x=[-0.45],
    positionY=0.5
)
_PRIMITIVE_WIDE_TALL_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=2, z=1),
    mass=1,
    offset=Vector3d(x=0, y=1, z=0),
    positionY=1
)
_SEPARATE_CONTAINER_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=1, z=1),
    # Must be heavy/sturdy enough to hold a soccer ball
    mass=10,
    offset=Vector3d(x=0, y=0, z=0),
    # Ideal for shell game
    placer_offset_z=[-0.4],
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.9, y=0.96, z=0.9),
            position=Vector3d(x=0, y=0.04, z=0)
        )
    ]
)
_SKATEBOARD_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.24, y=0.17, z=0.76),
    mass=2,
    offset=Vector3d(x=0, y=0.085, z=0),
    placer_offset_y=[0.04],
    positionY=0.005
)
_SHELF_1_CUBBY_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.78, y=0.77, z=0.4),
    mass=3,
    offset=Vector3d(x=0, y=0.385, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.77, y=0, z=0.39),
            position=Vector3d(x=0, y=0.78, z=0)
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.38, y=0.33, z=0.33),
            position=Vector3d(x=0.175, y=0.56, z=0),
            area_id='top_right_shelf'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.38, y=0.33, z=0.33),
            position=Vector3d(x=-0.175, y=0.56, z=0),
            area_id='top_left_shelf'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.38, y=0.33, z=0.33),
            position=Vector3d(x=0.175, y=0.21, z=0),
            area_id='bottom_right_shelf'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.38, y=0.33, z=0.33),
            position=Vector3d(x=-0.175, y=0.21, z=0),
            area_id='bottom_left_shelf'
        )
    ]
)
_SHELF_2_TABLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.93, y=0.73, z=1.02),
    mass=4,
    offset=Vector3d(x=0, y=0.355, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.92, y=0, z=1.01),
            position=Vector3d(x=0, y=0.73, z=0)
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.65, y=0.22, z=0.87),
            position=Vector3d(x=0, y=0.52, z=0),
            area_id='middle_shelf'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.8, y=0.235, z=0.95),
            position=Vector3d(x=0, y=0.225, z=0),
            area_id='lower_shelf'
        )
    ]
)
_SOCCER_BALL_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.22, y=0.22, z=0.22),
    mass=1,
    offset=Vector3d(x=0, y=0.11, z=0),
    positionY=0.11
)
_SOFA_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2.64, y=1.15, z=1.23),
    mass=45,
    offset=Vector3d(x=0, y=0.575, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.95, y=0, z=0.6),
            position=Vector3d(x=0, y=0.62, z=0.24)
        )
    ]
)
_SOFA_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2.55, y=1.25, z=0.95),
    mass=45,
    offset=Vector3d(x=0, y=0.625, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.95, y=0, z=0.625),
            position=Vector3d(x=0, y=0.59, z=0.15)
        )
    ]
)
_SOFA_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2.4, y=1.25, z=0.95),
    mass=45,
    offset=Vector3d(x=0, y=0.625, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.95, y=0, z=0.625),
            position=Vector3d(x=0, y=0.59, z=0.15)
        )
    ]
)
_SOFA_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.594, y=0.837, z=1.007),
    mass=30,
    offset=Vector3d(x=0, y=0.419, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.214, y=0, z=0.552),
            position=Vector3d(x=0, y=0.422, z=0.049)
        )
    ]
)
_SOFA_5_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.862, y=0.902, z=1),
    mass=30,
    offset=Vector3d(x=0, y=0.451, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.444, y=0, z=0.639),
            position=Vector3d(x=0, y=0.496, z=0.126)
        )
    ]
)
_SOFA_6_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.692, y=0.723, z=0.916),
    mass=30,
    offset=Vector3d(x=0, y=0.361, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.097, y=0, z=0.787),
            position=Vector3d(x=0, y=0.388, z=0.057)
        )
    ]
)
_SOFA_7_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.607, y=0.848, z=0.933),
    mass=30,
    offset=Vector3d(x=0, y=0.424, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.294, y=0, z=0.762),
            position=Vector3d(x=0, y=0.459, z=0.05)
        )
    ]
)
_SOFA_8_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2.78, y=0.86, z=1.1),
    mass=30,
    offset=Vector3d(x=0, y=0.43, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=2.1, y=0, z=0.78),
            position=Vector3d(x=0, y=0.5, z=-0.16)
        )
    ]
)
_SOFA_9_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2.54, y=1.62, z=1.52),
    mass=30,
    offset=Vector3d(x=0, y=0.81, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=2.1, y=0, z=0.86),
            position=Vector3d(x=0, y=0.8, z=0.29)
        )
    ]
)
_SOFA_11_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=3.3, y=1.7, z=1.5),
    mass=30,
    offset=Vector3d(x=0, y=0.85, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=2, y=0, z=0.86),
            position=Vector3d(x=0, y=0.7, z=0.18)
        )
    ]
)
_SOFA_12_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.8, y=1.08, z=2.22),
    mass=30,
    offset=Vector3d(x=0, y=0.54, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.8, y=0, z=1.66),
            position=Vector3d(x=0, y=0.55, z=0.26)
        )
    ]
)
_SOFA_CHAIR_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.43, y=1.15, z=1.23),
    mass=30,
    offset=Vector3d(x=0, y=0.575, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.77, y=0, z=0.6),
            position=Vector3d(x=0, y=0.62, z=0.24)
        )
    ]
)
_SOFA_CHAIR_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.425, y=1.25, z=0.95),
    mass=30,
    offset=Vector3d(x=0, y=0.625, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.975, y=0, z=0.65),
            position=Vector3d(x=0, y=0.59, z=0.15)
        )
    ]
)
_SOFA_CHAIR_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.425, y=1.25, z=0.95),
    mass=30,
    offset=Vector3d(x=0, y=0.625, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.975, y=0, z=0.65),
            position=Vector3d(x=0, y=0.59, z=0.15)
        )
    ]
)
_SOFA_CHAIR_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=0.857, z=0.873),
    mass=20,
    offset=Vector3d(x=0, y=0.429, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0, z=0.736),
            position=Vector3d(x=0, y=0.393, z=0.064)
        )
    ]
)
_SOFA_CHAIR_5_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.957, y=0.915, z=1),
    mass=20,
    offset=Vector3d(x=0, y=0.458, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.708, y=0, z=0.655),
            position=Vector3d(x=0, y=0.423, z=0.132)
        )
    ]
)
_SOFA_CHAIR_6_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.667, y=0.637, z=0.667),
    mass=20,
    offset=Vector3d(x=0, y=0.318, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0, z=0.446),
            position=Vector3d(x=0, y=0.27, z=0.006)
        )
    ]
)
_SOFA_CHAIR_7_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.691, y=0.681, z=0.634),
    mass=20,
    offset=Vector3d(x=0, y=0.335, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.449, y=0, z=0.325),
            position=Vector3d(x=0, y=0.324, z=0.087)
        )
    ]
)
_SOFA_CHAIR_8_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2.18, y=1.24, z=1.6),
    mass=20,
    offset=Vector3d(x=0, y=0.62, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.2, y=0, z=1.1),
            position=Vector3d(x=0, y=0.68, z=-0.24)
        )
    ]
)
_SOFA_CHAIR_9_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.38, y=1.46, z=1.36),
    mass=20,
    offset=Vector3d(x=0, y=0.73, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.02, y=0, z=0.72),
            position=Vector3d(x=0, y=0.72, z=0.25)
        )
    ]
)
_TABLE_1_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.69, y=0.88, z=1.63),
    mass=3,
    offset=Vector3d(x=0, y=0.44, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.68, y=0, z=1.62),
            position=Vector3d(x=0.065, y=0.88, z=-0.07)
        )
    ]
)
_TABLE_2_CIRCLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.67, y=0.74, z=0.67),
    mass=1,
    offset=Vector3d(x=0, y=0.37, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0, z=0.5),
            position=Vector3d(x=0, y=0.74, z=0)
        )
    ]
)
_TABLE_3_CIRCLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.573, y=1.018, z=0.557),
    mass=0.5,
    offset=Vector3d(x=0, y=0.509, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.4, y=0, z=0.4),
            position=Vector3d(x=0, y=0.84, z=0)
        )
    ]
)
_TABLE_4_SEMICIRCLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.62, y=0.62, z=1.17),
    mass=4,
    offset=Vector3d(x=0, y=0.31, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.45, y=0, z=0.8),
            position=Vector3d(x=0, y=0.62, z=0)
        )
    ]
)
_TABLE_5_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.2, y=0.7, z=0.9),
    mass=8,
    offset=Vector3d(x=0, y=0.35, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.2, y=0, z=0.9),
            position=Vector3d(x=0, y=0.7, z=0)
        )
    ]
)
_TABLE_7_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.02, y=0.45, z=0.65),
    mass=3,
    offset=Vector3d(x=0, y=0.22, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.02, y=0, z=0.65),
            position=Vector3d(x=0, y=0.45, z=0)
        )
    ]
)
_TABLE_8_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.65, y=0.45, z=1.02),
    mass=6,
    offset=Vector3d(x=0, y=0.22, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.65, y=0, z=1.02),
            position=Vector3d(x=0, y=0.45, z=0)
        )
    ]
)
_TABLE_11_AND_12_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1, y=0.5, z=1),
    mass=12,
    offset=Vector3d(x=0, y=0.5, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1, y=0, z=1),
            position=Vector3d(x=0, y=0.5, z=0)
        )
    ]
)
_TABLE_13_SMALL_CIRCLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.579, y=0.622, z=0.587),
    mass=6,
    offset=Vector3d(x=0, y=0.311, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.3, y=0, z=0.3),
            position=Vector3d(x=0, y=0.52, z=0)
        )
    ]
)
_TABLE_14_SMALL_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.534, y=0.59, z=0.526),
    mass=6,
    offset=Vector3d(x=0, y=0.295, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0, z=0.5),
            position=Vector3d(x=0, y=0.485, z=0)
        )
    ]
)
_TABLE_15_RECT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.334, y=0.901, z=0.791),
    mass=15,
    offset=Vector3d(x=0, y=0.451, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.3, y=0, z=0.749),
            position=Vector3d(x=0, y=0.739, z=0.02)
        )
    ]
)
_TABLE_16_CIRCLE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.058, y=0.833, z=1.054),
    mass=15,
    offset=Vector3d(x=0, y=0.417, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.75, y=0, z=0.75),
            position=Vector3d(x=0, y=0.7, z=0)
        )
    ]
)
_TABLE_17_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.164, y=0.82, z=0.747),
    mass=15,
    offset=Vector3d(x=0, y=0.41, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.13, y=0, z=0.72),
            position=Vector3d(x=0, y=0.7056, z=0)
        )
    ]
)
_TABLE_18_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.568, y=0.905, z=0.872),
    mass=15,
    offset=Vector3d(x=0, y=0.452, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.52, y=0, z=0.84),
            position=Vector3d(x=0, y=0.7409, z=0)
        )
    ]
)
_TABLE_19_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.921, y=0.542, z=0.491),
    mass=10,
    offset=Vector3d(x=0, y=0.271, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.9, y=0, z=0.46),
            position=Vector3d(x=0, y=0.4518, z=0)
        )
    ]
)
_TABLE_20_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.96, y=0.64, z=0.93),
    mass=10,
    offset=Vector3d(x=0, y=0.32, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.65, y=0, z=0.65),
            position=Vector3d(x=0, y=0.479, z=0)
        )
    ]
)
_TABLE_21_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.286, y=0.913, z=0.822),
    mass=10,
    offset=Vector3d(x=0, y=0.456, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.2, y=0, z=0.76),
            position=Vector3d(x=0, y=0.69, z=0)
        )
    ]
)
_TABLE_22_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.431, y=0.652, z=0.695),
    mass=15,
    offset=Vector3d(x=0, y=0.326, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.4, y=0, z=0.6),
            position=Vector3d(x=0, y=0.41, z=0)
        )
    ]
)
_TABLE_25_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.65, y=0.68, z=0.75),
    mass=15,
    offset=Vector3d(x=0, y=0.34, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.64, y=0, z=0.64),
            position=Vector3d(x=0, y=0.68, z=0)
        )
    ]
)
_TABLE_26_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.65, y=0.68, z=0.75),
    mass=15,
    offset=Vector3d(x=0, y=0.34, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.65, y=0, z=0.75),
            position=Vector3d(x=0, y=0.68, z=0)
        )
    ]
)
_TABLE_27_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.2, y=0.7, z=1.2),
    mass=5,
    offset=Vector3d(x=0, y=0.35, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.84, y=0, z=0.84),
            position=Vector3d(x=0, y=0.7, z=0)
        )
    ]
)
_TABLE_28_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=2, y=0.82, z=2),
    mass=25,
    offset=Vector3d(x=0, y=0.41, z=0),
    positionY=0,
    open_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=1.4, y=0, z=1.4),
            position=Vector3d(x=0, y=0.82, z=0)
        )
    ]
)
_TOOLBOX_1_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.51, y=0.29, z=0.21),
    dimensions=Vector3d(x=0.51, y=0.29, z=0.48),
    mass=5,
    offset=Vector3d(x=0, y=0.145, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.5, y=0.19, z=0.19),
            position=Vector3d(x=0, y=0.1, z=0)
        )
    ]
)
_TOOLBOX_2_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.58, y=0.33, z=0.32),
    dimensions=Vector3d(x=0.58, y=0.33, z=0.44),
    mass=5,
    offset=Vector3d(x=0, y=0.165, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.51, y=0.3, z=0.27),
            position=Vector3d(x=0, y=0.165, z=0)
        )
    ]
)
_TOOLBOX_3_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.15, y=0.1, z=0.106),
    dimensions=Vector3d(x=0.15, y=0.1, z=0.136),
    mass=5,
    offset=Vector3d(x=0, y=0.05, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.13, y=0.092, z=0.08),
            position=Vector3d(x=0, y=0.05, z=0)
        )
    ]
)
_TOOLBOX_4_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.13, y=0.036, z=0.09),
    dimensions=Vector3d(x=0.13, y=0.036, z=0.116),
    mass=5,
    offset=Vector3d(x=0, y=0.018, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.12, y=0.032, z=0.07),
            position=Vector3d(x=0, y=0.018, z=0)
        )
    ]
)
_TOOLBOX_5_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.25, y=0.1, z=0.1),
    dimensions=Vector3d(x=0.25, y=0.1, z=0.14),
    mass=5,
    offset=Vector3d(x=0, y=0.05, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.23, y=0.07, z=0.09),
            position=Vector3d(x=0, y=0.04, z=0)
        )
    ]
)
_TOOLBOX_6_SIZE = ObjectBaseSize(
    # These are the closed dimensions, if we ever need them.
    # dimensions=Vector3d(x=0.22, y=0.108, z=0.142),
    dimensions=Vector3d(x=0.22, y=0.108, z=0.192),
    mass=5,
    offset=Vector3d(x=0, y=0.054, z=0),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.195, y=0.08, z=0.12),
            position=Vector3d(x=0, y=0.045, z=0)
        )
    ]
)
_TOY_BOBCAT_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.13, y=0.061, z=0.038),
    mass=0.5,
    offset=Vector3d(x=0, y=0.0305, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_BUS_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.28, y=0.28, z=0.52),
    mass=1,
    offset=Vector3d(x=0, y=0.14, z=0),
    positionY=0.005
)
_TOY_CAR_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.25, y=0.2, z=0.41),
    mass=1,
    offset=Vector3d(x=0, y=0.1, z=0),
    placer_offset_y=[0.01],
    positionY=0.005
)
_TOY_CAR_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.134, y=0.052, z=0.036),
    mass=0.5,
    offset=Vector3d(x=0, y=0.026, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_CAR_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.13, y=0.052, z=0.036),
    mass=0.5,
    offset=Vector3d(x=0, y=0.026, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_CAR_5_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.9, y=0.36, z=0.42),
    mass=1.5,
    offset=Vector3d(x=0, y=0.18, z=0),
    # TODO
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_JEEP_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.06, y=0.057, z=0.098),
    mass=0.5,
    offset=Vector3d(x=0, y=0.0285, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_POWER_SHOVEL_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.18, y=0.08, z=0.042),
    mass=0.5,
    offset=Vector3d(x=0, y=0.04, z=0),
    # TODO
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_RACECAR_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.07, y=0.06, z=0.15),
    mass=0.5,
    offset=Vector3d(x=0, y=0.03, z=0),
    positionY=0.005
)
_TOY_ROAD_SCRAPER_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.136, y=0.066, z=0.038),
    mass=0.5,
    offset=Vector3d(x=0, y=0.033, z=0),
    # TODO
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_ROLLER_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.102, y=0.062, z=0.047),
    mass=0.5,
    offset=Vector3d(x=0, y=0.031, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_SEDAN_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.075, y=0.065, z=0.14),
    mass=0.5,
    offset=Vector3d(x=0, y=0.0325, z=0),
    positionY=0.005
)
_TOY_TANK_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.09, y=0.065, z=0.24),
    mass=0.5,
    offset=Vector3d(x=0, y=0.0325, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_TANK_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.065, y=0.067, z=0.17),
    mass=0.5,
    offset=Vector3d(x=0, y=0.0335, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_TANK_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.21, y=0.12, z=0.094),
    mass=1,
    offset=Vector3d(x=0, y=0.06, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_TRAIN_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.16, y=0.2, z=0.23),
    mass=1,
    offset=Vector3d(x=0, y=0.1, z=0),
    positionY=0.005
)
_TOY_TRAIN_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.09, y=0.064, z=0.036),
    mass=1,
    offset=Vector3d(x=0, y=0.032, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_TRAIN_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.4, y=0.26, z=0.22),
    mass=1.5,
    offset=Vector3d(x=0, y=0.13, z=0),
    # TODO
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_TRIKE_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.04, y=0.074, z=0.112),
    mass=0.5,
    offset=Vector3d(x=0, y=0.037, z=0),
    # TODO
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_TROLLEY_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.16, y=0.2, z=0.23),
    mass=1,
    offset=Vector3d(x=0, y=0.1, z=0),
    placer_offset_y=[0.12],
    positionY=0.005
)
_TOY_TRUCK_1_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.2, y=0.2, z=0.25),
    mass=1,
    offset=Vector3d(x=0, y=0.1, z=0),
    positionY=0.1
)
_TOY_TRUCK_2_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.14, y=0.2, z=0.28),
    mass=1,
    offset=Vector3d(x=0, y=0.1, z=0),
    positionY=0.005
)
_TOY_TRUCK_3_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.33, y=0.345, z=0.61),
    mass=1,
    offset=Vector3d(x=0, y=0.1725, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_TRUCK_4_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.25, y=0.26, z=0.4),
    mass=1,
    offset=Vector3d(x=0, y=0.13, z=0),
    placer_offset_y=[0],
    positionY=0.005
)
_TOY_TRUCK_5_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.19, y=0.072, z=0.04),
    mass=0.5,
    offset=Vector3d(x=0, y=0.036, z=0),
    positionY=0.005
)
_TROPHY_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.19, y=0.3, z=0.14),
    mass=1,
    offset=Vector3d(x=0, y=0.15, z=0),
    placer_offset_y=[0.05],
    positionY=0.005,
    sideways=ObjectSidewaysSize(
        dimensions=Vector3d(x=0.19, y=0.14, z=0.3),
        offset=Vector3d(x=0, y=0, z=0.15),
        positionY=0.075,
        rotation=Vector3d(x=90, y=0, z=0),
        switch_y_with_z=True
    )
)
_TURTLE_ON_WHEELS_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=0.24, y=0.14, z=0.085),
    mass=1,
    offset=Vector3d(x=0, y=0.07, z=0),
    positionY=0.005
)
_TV_SIZE = ObjectBaseSize(
    dimensions=Vector3d(x=1.234, y=0.896, z=0.256),
    mass=5,
    offset=Vector3d(x=0, y=0.5, z=0),
    positionY=0.5,
)
_WARDROBE_SIZE = ObjectBaseSize(
    # These are the closed dimensions and offset, if we ever need them.
    # dimensions=Vector3d(x=1.07, y=2.1, z=0.49),
    # offset=Vector3d(x=0, y=1.05, z=0),
    dimensions=Vector3d(x=1.07, y=2.1, z=1),
    mass=100,
    offset=Vector3d(x=0, y=1.05, z=0.17),
    positionY=0,
    enclosed_area_list=[
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.49, y=0.24, z=0.46),
            position=Vector3d(x=-0.255, y=0.665, z=0.005),
            area_id='_bottom_shelf_left'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.445, y=0.16, z=0.425),
            position=Vector3d(x=-0.265, y=0.42, z=0.015),
            area_id='_lower_drawer_top_left'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.445, y=0.16, z=0.425),
            position=Vector3d(x=0.265, y=0.42, z=0.015),
            area_id='_lower_drawer_top_right'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.445, y=0.16, z=0.425),
            position=Vector3d(x=-0.265, y=0.21, z=0.015),
            area_id='_lower_drawer_bottom_left'
        ),
        ObjectInteractableArea(
            dimensions=Vector3d(x=0.445, y=0.16, z=0.425),
            position=Vector3d(x=0.265, y=0.21, z=0.015),
            area_id='_lower_drawer_bottom_right'
        ),
    ]
)


def turn_around(definition: ObjectDefinition) -> ObjectDefinition:
    """Set the Y rotation to 90 in the given definition and switch its X and Z
    dimensions."""
    definition.rotation = Vector3d(x=0, y=180, z=0)
    return definition


def turn_sideways(definition: ObjectDefinition) -> ObjectDefinition:
    """Set the Y rotation to 90 in the given definition and switch its X and Z
    dimensions."""
    definition.rotation = Vector3d(x=0, y=90, z=0)
    if definition.dimensions:
        definition.dimensions = Vector3d(
            x=definition.dimensions.z,
            y=definition.dimensions.y,
            z=definition.dimensions.x
        )
    for size in definition.chooseSizeList:
        size.dimensions = Vector3d(
            x=size.dimensions.z,
            y=size.dimensions.y,
            z=size.dimensions.x
        )
    return definition


def _create_antique_armchair_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='antique_armchair_1',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        materialCategory=['leather_armchair'],
        salientMaterials=['leather'],
        shape=['sofa chair'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _ANTIQUE_ARMCHAIR_1_SIZE.make(size)
            for size in args.size_multiplier_list
        ]
    )


def _create_antique_armchair_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='antique_armchair_2',
        untrainedShape=True,
        attributes=['moveable', 'receptacle'],
        color=['blue', 'purple', 'yellow'],
        occluder=True,
        materialCategory=[],
        salientMaterials=['fabric', 'wood'],
        shape=['sofa chair'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _ANTIQUE_ARMCHAIR_2_SIZE.make(size)
            for size in args.size_multiplier_list
        ]
    )


def _create_antique_armchair_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='antique_armchair_3',
        untrainedShape=True,
        attributes=['moveable', 'receptacle'],
        color=['black', 'brown', 'yellow'],
        occluder=True,
        materialCategory=[],
        salientMaterials=['fabric', 'wood'],
        shape=['sofa chair'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _ANTIQUE_ARMCHAIR_3_SIZE.make(size)
            for size in args.size_multiplier_list
        ]
    )


def _create_antique_chair_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='antique_chair_1',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _ANTIQUE_CHAIR_1_SIZE.make(size)
            for size in args.size_multiplier_list
        ]
    )


def _create_antique_chair_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='antique_chair_2',
        untrainedShape=True,
        attributes=['moveable', 'receptacle'],
        color=['black', 'brown'],
        materialCategory=[],
        obstacle=True,
        salientMaterials=['fabric', 'wood'],
        shape=['chair'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _ANTIQUE_CHAIR_2_SIZE.make(size)
            for size in args.size_multiplier_list
        ]
    )


def _create_antique_chair_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='antique_chair_3',
        untrainedShape=True,
        attributes=['moveable', 'receptacle'],
        color=['red', 'brown'],
        materialCategory=[],
        obstacle=True,
        salientMaterials=['fabric', 'wood'],
        shape=['chair'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _ANTIQUE_CHAIR_3_SIZE.make(size)
            for size in args.size_multiplier_list
        ]
    )


def _create_antique_sofa_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='antique_sofa_1',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['sofa'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _ANTIQUE_SOFA_1_SIZE.make(size)
            for size in args.size_multiplier_list
        ]
    )


def _create_antique_table_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='antique_table_1',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _ANTIQUE_TABLE_1_SIZE.make(size)
            for size in args.size_multiplier_list
        ]
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


def _create_barrel_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='barrel_1',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['barrel'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BARREL_1_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_barrel_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='barrel_2',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['barrel'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BARREL_2_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_barrel_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='barrel_3',
        untrainedShape=True,
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['barrel'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BARREL_3_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_barrel_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='barrel_4',
        untrainedShape=True,
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['barrel'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BARREL_4_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_bed_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_1',
        attributes=['receptacle'],
        occluder=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_2',
        attributes=['receptacle'],
        occluder=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_2_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_3',
        attributes=['receptacle'],
        occluder=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_4',
        attributes=['receptacle'],
        occluder=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_4_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_5(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_5',
        attributes=['receptacle'],
        obstacle=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_5_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_6(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_6',
        attributes=[],
        obstacle=True,
        shape=['bed'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_6_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_7(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_7',
        attributes=['receptacle'],
        occluder=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_7_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_8(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_8',
        attributes=['receptacle'],
        occluder=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_8_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_9(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_9',
        attributes=['receptacle'],
        occluder=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_9_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_10(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_10',
        attributes=['receptacle'],
        occluder=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_10_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_11(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_11',
        untrainedShape=True,
        attributes=['receptacle'],
        occluder=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_11_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bed_12(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bed_12',
        untrainedShape=True,
        attributes=['receptacle'],
        occluder=True,
        shape=['bed'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BED_12_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bin_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bin_1',
        attributes=['receptacle'],
        occluder=True,
        shape=['bin'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BIN_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_bin_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bin_3',
        attributes=['receptacle'],
        occluder=True,
        shape=['bin'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BIN_3_SIZE.make(size) for size in args.size_multiplier_list
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
            _BLOCK_BLANK_SIZE.make(size) for size in args.size_multiplier_list
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
            _BLOCK_BLANK_SIZE.make(size) for size in args.size_multiplier_list
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


def _create_double_bookcase_1_shelf(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='double_bookcase_1_shelf',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DOUBLE_BOOKCASE_1_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_double_bookcase_2_shelf(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='double_bookcase_2_shelf',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DOUBLE_BOOKCASE_2_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_double_bookcase_3_shelf(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='double_bookcase_3_shelf',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DOUBLE_BOOKCASE_3_SHELF_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_double_bookcase_4_shelf(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='double_bookcase_4_shelf',
        attributes=['receptacle'],
        occluder=True,
        shape=['shelf'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DOUBLE_BOOKCASE_4_SHELF_SIZE.make(size) for size in
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
    attributes = ['receptacle']
    if not args.type.endswith('static'):
        attributes.extend(['moveable', 'pickupable'])
    return ObjectDefinition(
        type=args.type,
        attributes=attributes,
        shape=['bowl'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOWL_3_SIZE.make(size) for size in args.size_multiplier_list
        ],
        massMultiplier=(3 if args.type.endswith('static') else 1)
    )


def _create_bowl_4(args: _FunctionArgs) -> ObjectDefinition:
    attributes = ['receptacle']
    if not args.type.endswith('static'):
        attributes.extend(['moveable', 'pickupable'])
    return ObjectDefinition(
        type=args.type,
        attributes=attributes,
        shape=['bowl'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOWL_4_SIZE.make(size) for size in args.size_multiplier_list
        ],
        massMultiplier=(3 if args.type.endswith('static') else 1)
    )


def _create_bowl_6(args: _FunctionArgs) -> ObjectDefinition:
    attributes = ['receptacle']
    if not args.type.endswith('static'):
        attributes.extend(['moveable', 'pickupable'])
    return ObjectDefinition(
        type=args.type,
        attributes=attributes,
        shape=['bowl'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _BOWL_6_SIZE.make(size) for size in args.size_multiplier_list
        ],
        massMultiplier=(3 if args.type.endswith('static') else 1)
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


def _create_case_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='case_2',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CASE_2_SIZE.make(size) for size in
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


def _create_case_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='case_4',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CASE_4_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_case_5(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='case_5',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CASE_5_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_case_6(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='case_6',
        untrainedShape=True,
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CASE_6_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_case_7(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='case_7',
        untrainedShape=True,
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CASE_7_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_cart_2(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='cart_2',
        attributes=['moveable', 'pickupable'],
        shape=['cart'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CART_2_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


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


def _create_chair_5(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_5',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _CHAIR_5_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_6(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_6',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _CHAIR_6_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_7(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_7',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_7_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_8(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_8',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _CHAIR_8_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_9(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_9',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_9_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_10(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_10',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_10_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_11(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_11',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_11_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_12(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_12',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_12_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_13(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_13',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_13_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_14(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_14',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_14_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_15(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_15',
        untrainedShape=True,
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_15_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chair_16(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chair_16',
        untrainedShape=True,
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['chair'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHAIR_16_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_changing_table(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='changing_table',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['changing table'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHANGING_TABLE_SIZE.make(size) for size in
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


def _create_chest_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chest_4',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['chest'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHEST_4_ROUNDED_LID_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chest_5(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chest_5',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['chest'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHEST_5_ROUNDED_LID_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chest_6(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chest_6',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['chest'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHEST_6_TRAPEZOID_LID_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_chest_7(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chest_7',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['chest'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHEST_7_PIRATE_TREASURE_SIZE.make(size) for size in
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


def _create_chest_9(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='chest_9',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['chest'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CHEST_9_TRAPEZOID_LID_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_01(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_01',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_01_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_02(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_02',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_02_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_03(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_03',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_03_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_04(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_04',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_04_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_05(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_05',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_05_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_06(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_06',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_06_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_07(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_07',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_07_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_08(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_08',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_08_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_09(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_09',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_09_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_10(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_10',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_10_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_11(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_11',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_11_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_asymmetric_12(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_asymmetric_12',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_ASYMMETRIC_12_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_01(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_01',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_01_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_02(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_02',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_02_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_03(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_03',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_03_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_04(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_04',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_04_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_05(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_05',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_05_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_06(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_06',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_06_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_07(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_07',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_07_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_08(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_08',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_08_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_09(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_09',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_09_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_10(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_10',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_10_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_11(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_11',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_11_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_container_symmetric_12(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='container_symmetric_12',
        attributes=['moveable', 'receptacle'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CONTAINER_SYMMETRIC_12_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_crate_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='crate_1',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['crate'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CRATE_1_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_crate_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='crate_2',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['crate'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CRATE_2_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_crate_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='crate_3',
        untrainedShape=True,
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['crate'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CRATE_3_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_crate_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='crate_4',
        untrainedShape=True,
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['crate'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CRATE_4_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_crate_open_topped_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='crate_open_topped_1',
        attributes=['receptacle'],
        occluder=True,
        shape=['crate'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CRATE_OPEN_TOPPED_1_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_crate_open_topped_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='crate_open_topped_2',
        attributes=['receptacle'],
        occluder=True,
        shape=['crate'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CRATE_OPEN_TOPPED_2_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_crayon(args: _FunctionArgs) -> ObjectDefinition:
    color = args.type.replace('crayon_', '')
    return ObjectDefinition(
        # The type should be in the format of 'crayon_<color>'
        type=args.type,
        attributes=['moveable', 'pickupable'],
        color=((['pink', 'red'] if color == 'pink' else []) + [color]),
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
    attributes = ['receptacle']
    if not args.type.endswith('static'):
        attributes.extend(['moveable', 'pickupable'])
    return ObjectDefinition(
        type=args.type,
        attributes=attributes,
        shape=['cup'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CUP_2_SIZE.make(size) for size in args.size_multiplier_list
        ],
        massMultiplier=(3 if args.type.endswith('static') else 1)
    )


def _create_cup_3(args: _FunctionArgs) -> ObjectDefinition:
    attributes = ['receptacle']
    if not args.type.endswith('static'):
        attributes.extend(['moveable', 'pickupable'])
    return ObjectDefinition(
        type=args.type,
        attributes=attributes,
        shape=['cup'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CUP_3_SIZE.make(size) for size in args.size_multiplier_list
        ],
        massMultiplier=(3 if args.type.endswith('static') else 1)
    )


def _create_cup_6(args: _FunctionArgs) -> ObjectDefinition:
    attributes = ['receptacle']
    if not args.type.endswith('static'):
        attributes.extend(['moveable', 'pickupable'])
    return ObjectDefinition(
        type=args.type,
        attributes=attributes,
        shape=['cup'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _CUP_6_SIZE.make(size) for size in args.size_multiplier_list
        ],
        massMultiplier=(3 if args.type.endswith('static') else 1)
    )


def _create_desk_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='desk_1',
        attributes=['moveable', 'receptacle'],
        occluder=True,
        shape=['desk'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DESK_1_AND_2_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_desk_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='desk_2',
        attributes=['moveable', 'receptacle'],
        occluder=True,
        shape=['desk'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DESK_1_AND_2_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_desk_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='desk_3',
        attributes=['moveable', 'receptacle'],
        occluder=True,
        shape=['desk'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DESK_3_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_desk_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='desk_4',
        attributes=['moveable', 'receptacle'],
        occluder=True,
        shape=['desk'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DESK_4_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_dog_on_wheels(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='dog_on_wheels',
        attributes=['moveable', 'pickupable'],
        shape=['dog'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DOG_ON_WHEELS_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    ))


def _create_dog_on_wheels_2(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='dog_on_wheels_2',
        attributes=['moveable', 'pickupable'],
        shape=['dog'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DOG_ON_WHEELS_2_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    ))


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


def _create_duck_on_wheels_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='duck_on_wheels_2',
        attributes=['moveable', 'pickupable'],
        shape=['duck'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _DUCK_ON_WHEELS_2_SIZE.make(size) for size in
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
    definition.poly = geometry.Polygon([
        (0.25, -0.5),
        (-0.25, -0.5),
        (-0.25, 0.5),
        (-0.15, 0.5),
        (-0.15, -0.4),
        (0.25, -0.4)
    ])
    return definition


def _create_letter_l_wide(args: _FunctionArgs) -> ObjectDefinition:
    definition = _create_primitive_non_cylinder(args)
    definition.poly = geometry.Polygon([
        (0.5, -0.5),
        (-0.5, -0.5),
        (-0.5, 0.5),
        (0, 0.5),
        (0, 0),
        (0.5, 0)
    ])
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
    definition.poly = geometry.Polygon([
        (0.5, -1.0),
        (-0.5, -1.0),
        (-0.5, 1.0),
        (0, 1.0),
        (0, -0.5),
        (0.5, -0.5)
    ])
    return definition


def _create_lid_square(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='lid',
        attributes=['openable'],
        shape=['lid'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _LID_SQUARE_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_military_case_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='military_case_1',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['military_case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _MILITARY_CASE_1_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_military_case_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='military_case_2',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['military_case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _MILITARY_CASE_2_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_military_case_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='military_case_3',
        untrainedShape=True,
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['military_case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _MILITARY_CASE_3_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_military_case_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='military_case_4',
        untrainedShape=True,
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['military_case'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _MILITARY_CASE_4_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


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


def _create_primitive_helper(
    args: _FunctionArgs,
    size_list: List[SizeChoice]
) -> ObjectDefinition:
    return ObjectDefinition(
        type=args.type,
        attributes=['physics'],
        shape=[' '.join([
            text for text in args.type.replace('_', ' ').split(' ')
            if not text.isnumeric()
        ])],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=size_list
    )


def _create_primitive_cylinder(args: _FunctionArgs) -> ObjectDefinition:
    size_list = [
        _PRIMITIVE_SIZE.make(size) for size in args.size_multiplier_list
    ]
    cylinder_size_list = []
    for size in size_list:
        size_copy = copy.deepcopy(size)
        # Halve the Y scale here, but not its dimensions or other properties,
        # because Unity will automatically double a cylinder's height.
        size_copy.scale.y *= 0.5
        cylinder_size_list.append(size_copy)
    return _create_primitive_helper(args, cylinder_size_list)


# Size data for non-cylinder primitive objects (cones, cubes, spheres, etc.)
def _create_primitive_non_cylinder(args: _FunctionArgs) -> ObjectDefinition:
    return _create_primitive_helper(args, [
        _PRIMITIVE_SIZE.make(size) for size in args.size_multiplier_list
    ])


def _create_primitive_on_ground(args: _FunctionArgs) -> ObjectDefinition:
    return _create_primitive_helper(args, [
        _PRIMITIVE_ON_GROUND_SIZE.make(size)
        for size in args.size_multiplier_list
    ])


def _create_primitive_tall(args: _FunctionArgs) -> ObjectDefinition:
    return _create_primitive_helper(args, [
        _PRIMITIVE_TALL_SIZE.make(size) for size in args.size_multiplier_list
    ])


def _create_primitive_triangle(args: _FunctionArgs) -> ObjectDefinition:
    return _create_primitive_helper(args, [
        _PRIMITIVE_TRIANGLE_SIZE.make(size)
        for size in args.size_multiplier_list
    ])


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


def _create_separate_container(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='separate_container',
        attributes=['receptacle', 'openable'],
        shape=['container'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _SEPARATE_CONTAINER_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_skateboard(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='skateboard',
        attributes=['moveable', 'pickupable'],
        color=['black'],
        salientMaterials=['metal', 'plastic'],
        shape=['skateboard'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _SKATEBOARD_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


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


def _create_sofa_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_4',
        attributes=['receptacle'],
        color=['grey'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_4_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_5(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_5',
        attributes=['receptacle'],
        color=['white'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_5_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_6(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_6',
        attributes=['receptacle'],
        color=['brown'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_6_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_7(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_7',
        attributes=['receptacle'],
        color=['grey'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_7_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_8(args: _FunctionArgs) -> ObjectDefinition:
    return turn_around(ObjectDefinition(
        type='sofa_8',
        attributes=['receptacle'],
        color=['grey'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_8_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_sofa_9(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_9',
        attributes=['receptacle'],
        color=['grey'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_9_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_11(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_11',
        untrainedShape=True,
        attributes=['receptacle'],
        color=['brown', 'orange', 'red'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['leather'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_11_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_12(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_12',
        untrainedShape=True,
        attributes=['receptacle'],
        color=['blue', 'green', 'grey', 'yellow'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_12_SIZE.make(size) for size in args.size_multiplier_list
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
        shape=['sofa chair'],
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
        shape=['sofa chair'],
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
        shape=['sofa chair'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_CHAIR_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_chair_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_chair_4',
        attributes=['receptacle'],
        color=['brown'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa chair'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_CHAIR_4_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_chair_5(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_chair_5',
        attributes=['receptacle'],
        color=['blue'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa chair'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_CHAIR_5_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_chair_6(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_chair_6',
        attributes=['receptacle'],
        color=['brown'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa chair'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_CHAIR_6_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_chair_7(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_chair_7',
        attributes=['receptacle'],
        color=['white'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa chair'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_CHAIR_7_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_sofa_chair_8(args: _FunctionArgs) -> ObjectDefinition:
    return turn_around(ObjectDefinition(
        type='sofa_chair_8',
        attributes=['receptacle'],
        color=['white'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa chair'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_CHAIR_8_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_sofa_chair_9(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='sofa_chair_9',
        attributes=['receptacle'],
        color=['white'],
        materialCategory=[],
        occluder=True,
        salientMaterials=['fabric'],
        shape=['sofa chair'],
        stackTarget=True,
        chooseSizeList=[
            _SOFA_CHAIR_9_SIZE.make(size) for size in args.size_multiplier_list
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
        attributes=['moveable', 'receptacle'],
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
        attributes=['moveable', 'receptacle'],
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
        attributes=['moveable', 'receptacle'],
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
        attributes=['moveable', 'receptacle'],
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
        attributes=['moveable', 'receptacle'],
        occluder=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_11_AND_12_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_13(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_13',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_13_SMALL_CIRCLE_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_14(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_14',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_14_SMALL_RECT_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_15(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_15',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TABLE_15_RECT_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_16(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_16',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_16_CIRCLE_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_17(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_17',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TABLE_17_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_18(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_18',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_18_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_19(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_19',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[
            item.copy(3) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TABLE_19_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_20(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_20',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_20_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_21(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_21',
        untrainedShape=True,
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_21_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_22(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_22',
        untrainedShape=True,
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_22_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_25(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_25',
        untrainedShape=True,
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_25_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_26(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_26',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_26_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_27(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_27',
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_27_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_table_28(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='table_28',
        untrainedShape=True,
        attributes=['moveable', 'receptacle'],
        obstacle=True,
        shape=['table'],
        stackTarget=True,
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TABLE_28_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


# Maps each tool type to its base X/Z dimensions.
LARGE_BLOCK_TOOLS_TO_DIMENSIONS = {
    'tool_hooked_0_50_x_4_00': (1.5, 4),
    'tool_hooked_0_50_x_5_00': (1.5, 5),
    'tool_hooked_0_50_x_6_00': (1.5, 6),
    'tool_hooked_0_50_x_7_00': (1.5, 7),
    'tool_hooked_0_50_x_8_00': (1.5, 8),
    'tool_hooked_0_50_x_9_00': (1.5, 9),
    'tool_hooked_0_75_x_4_00': (2.25, 4),
    'tool_hooked_0_75_x_5_00': (2.25, 5),
    'tool_hooked_0_75_x_6_00': (2.25, 6),
    'tool_hooked_0_75_x_7_00': (2.25, 7),
    'tool_hooked_0_75_x_8_00': (2.25, 8),
    'tool_hooked_0_75_x_9_00': (2.25, 9),
    'tool_hooked_1_00_x_4_00': (3, 4),
    'tool_hooked_1_00_x_5_00': (3, 5),
    'tool_hooked_1_00_x_6_00': (3, 6),
    'tool_hooked_1_00_x_7_00': (3, 7),
    'tool_hooked_1_00_x_8_00': (3, 8),
    'tool_hooked_1_00_x_9_00': (3, 9),
    'tool_isosceles_0_50_x_4_00': (4, 4),
    'tool_isosceles_0_50_x_5_00': (5, 5),
    'tool_isosceles_0_50_x_6_00': (6, 6),
    'tool_isosceles_0_50_x_7_00': (7, 7),
    'tool_isosceles_0_50_x_8_00': (8, 8),
    'tool_isosceles_0_50_x_9_00': (9, 9),
    'tool_isosceles_0_75_x_4_00': (4, 4),
    'tool_isosceles_0_75_x_5_00': (5, 5),
    'tool_isosceles_0_75_x_6_00': (6, 6),
    'tool_isosceles_0_75_x_7_00': (7, 7),
    'tool_isosceles_0_75_x_8_00': (8, 8),
    'tool_isosceles_0_75_x_9_00': (8, 9),
    'tool_isosceles_1_00_x_4_00': (4, 4),
    'tool_isosceles_1_00_x_5_00': (5, 5),
    'tool_isosceles_1_00_x_6_00': (6, 6),
    'tool_isosceles_1_00_x_7_00': (7, 7),
    'tool_isosceles_1_00_x_8_00': (8, 8),
    'tool_isosceles_1_00_x_9_00': (9, 9),
    'tool_rect_0_50_x_1_00': (0.5, 1),
    'tool_rect_0_75_x_1_00': (0.75, 1),
    'tool_rect_1_00_x_1_00': (1, 1),
    'tool_rect_0_50_x_3_00': (0.5, 3),
    'tool_rect_0_50_x_4_00': (0.5, 4),
    'tool_rect_0_50_x_5_00': (0.5, 5),
    'tool_rect_0_50_x_6_00': (0.5, 6),
    'tool_rect_0_50_x_7_00': (0.5, 7),
    'tool_rect_0_50_x_8_00': (0.5, 8),
    'tool_rect_0_50_x_9_00': (0.5, 9),
    'tool_rect_0_75_x_3_00': (0.75, 3),
    'tool_rect_0_75_x_4_00': (0.75, 4),
    'tool_rect_0_75_x_5_00': (0.75, 5),
    'tool_rect_0_75_x_6_00': (0.75, 6),
    'tool_rect_0_75_x_7_00': (0.75, 7),
    'tool_rect_0_75_x_8_00': (0.75, 8),
    'tool_rect_0_75_x_9_00': (0.75, 9),
    'tool_rect_1_00_x_3_00': (1, 3),
    'tool_rect_1_00_x_4_00': (1, 4),
    'tool_rect_1_00_x_5_00': (1, 5),
    'tool_rect_1_00_x_6_00': (1, 6),
    'tool_rect_1_00_x_7_00': (1, 7),
    'tool_rect_1_00_x_8_00': (1, 8),
    'tool_rect_1_00_x_9_00': (1, 9)
}

LARGE_BLOCK_NOVEL_TOOLS_TO_DIMENSIONS = {
    'tool_rect_0_63_x_1_00': (0.63, 1),
    'tool_rect_0_88_x_1_00': (0.88, 1),
    'tool_rect_1_13_x_1_00': (1.13, 1),
    'tool_rect_0_63_x_4_00': (0.63, 4),
    'tool_rect_0_63_x_5_00': (0.63, 5),
    'tool_rect_0_63_x_6_00': (0.63, 6),
    'tool_rect_0_63_x_7_00': (0.63, 7),
    'tool_rect_0_63_x_8_00': (0.63, 8),
    'tool_rect_0_63_x_9_00': (0.63, 9),
    'tool_rect_0_88_x_4_00': (0.88, 4),
    'tool_rect_0_88_x_5_00': (0.88, 5),
    'tool_rect_0_88_x_6_00': (0.88, 6),
    'tool_rect_0_88_x_7_00': (0.88, 7),
    'tool_rect_0_88_x_8_00': (0.88, 8),
    'tool_rect_0_88_x_9_00': (0.88, 9),
    'tool_rect_1_13_x_4_00': (1.13, 4),
    'tool_rect_1_13_x_5_00': (1.13, 5),
    'tool_rect_1_13_x_6_00': (1.13, 6),
    'tool_rect_1_13_x_7_00': (1.13, 7),
    'tool_rect_1_13_x_8_00': (1.13, 8),
    'tool_rect_1_13_x_9_00': (1.13, 9)
}


def _create_tool(args: _FunctionArgs) -> ObjectDefinition:
    dimensions = LARGE_BLOCK_TOOLS_TO_DIMENSIONS[args.type]
    base_size = ObjectBaseSize(
        dimensions=Vector3d(x=dimensions[0], y=0.6, z=dimensions[1]),
        mass=None,
        offset=Vector3d(x=0, y=0.3, z=0),
        positionY=0.3
    )
    return ObjectDefinition(
        type=args.type,
        attributes=[],
        color=['grey', 'black'],
        materials=[],
        salientMaterials=['metal'],
        shape=['tool'],
        chooseSizeList=[
            base_size.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toolbox_1(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='toolbox_1',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['toolbox'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOOLBOX_1_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_toolbox_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='toolbox_2',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['toolbox'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOOLBOX_2_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_toolbox_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='toolbox_3',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['toolbox'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOOLBOX_3_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_toolbox_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='toolbox_4',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['toolbox'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOOLBOX_4_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_toolbox_5(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='toolbox_5',
        untrainedShape=True,
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['toolbox'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOOLBOX_5_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_toolbox_6(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='toolbox_6',
        untrainedShape=True,
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['toolbox'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOOLBOX_6_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_toy_bobcat(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='bobcat',
        attributes=['moveable', 'pickupable'],
        shape=['bobcat'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_BOBCAT_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_bus_1(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='bus_1',
        attributes=['moveable', 'pickupable'],
        shape=['bus'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_BUS_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_car_2(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='car_2',
        attributes=['moveable', 'pickupable'],
        shape=['car'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_CAR_2_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_car_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='car_3',
        attributes=['moveable', 'pickupable'],
        shape=['car'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_CAR_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_car_4(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='car_4',
        untrainedShape=True,
        attributes=['moveable', 'pickupable'],
        shape=['car'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_CAR_4_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_car_5(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='car_5',
        untrainedShape=True,
        attributes=['moveable', 'pickupable'],
        shape=['car'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_CAR_5_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_jeep(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='jeep',
        attributes=['moveable', 'pickupable'],
        shape=['jeep'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_JEEP_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_power_shovel(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='power_shovel',
        untrainedShape=True,
        attributes=['moveable', 'pickupable'],
        shape=['power_shovel'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_POWER_SHOVEL_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_toy_racecar(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='racecar_red',
        attributes=['moveable', 'pickupable'],
        shape=['car'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_RACECAR_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    ))


def _create_toy_road_scraper(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='road_scraper',
        untrainedShape=True,
        attributes=['moveable', 'pickupable'],
        shape=['road_scraper'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_ROAD_SCRAPER_SIZE.make(size) for size in
            args.size_multiplier_list
        ]
    )


def _create_toy_roller(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='roller',
        attributes=['moveable', 'pickupable'],
        shape=['roller'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_ROLLER_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_sedan(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='car_1',
        attributes=['moveable', 'pickupable'],
        shape=['car'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_SEDAN_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_tank_1(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='tank_1',
        attributes=['moveable', 'pickupable'],
        shape=['tank'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TANK_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_tank_2(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='tank_2',
        attributes=['moveable', 'pickupable'],
        shape=['tank'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TANK_2_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_tank_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='tank_3',
        untrainedShape=True,
        attributes=['moveable', 'pickupable'],
        shape=['tank'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TANK_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_train_1(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='train_1',
        attributes=['moveable', 'pickupable'],
        shape=['train'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TRAIN_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_train_2(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='train_2',
        attributes=['moveable', 'pickupable'],
        shape=['train'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TRAIN_2_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_train_3(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='train_3',
        untrainedShape=True,
        attributes=['moveable', 'pickupable'],
        shape=['train'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TRAIN_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


def _create_toy_trike(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='trike',
        untrainedShape=True,
        attributes=['moveable', 'pickupable'],
        shape=['trike'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TRIKE_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_trolley(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='trolley_1',
        attributes=['moveable', 'pickupable'],
        shape=['trolley'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TROLLEY_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_truck_1(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='truck_1',
        attributes=['moveable', 'pickupable'],
        shape=['truck'],
        chooseMaterialList=[
            item.copy(2) for item in args.chosen_material_list
        ],
        chooseSizeList=[
            _TOY_TRUCK_1_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_truck_2(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='truck_2',
        attributes=['moveable', 'pickupable'],
        shape=['truck'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TRUCK_2_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_truck_3(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='truck_3',
        attributes=['moveable', 'pickupable'],
        shape=['truck'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TRUCK_3_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_truck_4(args: _FunctionArgs) -> ObjectDefinition:
    return turn_sideways(ObjectDefinition(
        type='truck_4',
        attributes=['moveable', 'pickupable'],
        shape=['truck'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TRUCK_4_SIZE.make(size) for size in args.size_multiplier_list
        ]
    ))


def _create_toy_truck_5(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='truck_5',
        untrainedShape=True,
        attributes=['moveable', 'pickupable'],
        shape=['truck'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _TOY_TRUCK_5_SIZE.make(size) for size in args.size_multiplier_list
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


def _create_wardrobe(args: _FunctionArgs) -> ObjectDefinition:
    return ObjectDefinition(
        type='wardrobe',
        attributes=['receptacle', 'openable'],
        occluder=True,
        shape=['wardrobe'],
        chooseMaterialList=[item.copy() for item in args.chosen_material_list],
        chooseSizeList=[
            _WARDROBE_SIZE.make(size) for size in args.size_multiplier_list
        ]
    )


class TypeDetailsTuple(NamedTuple):
    definition_function: Callable[[_FunctionArgs], ObjectDefinition]
    material_restrictions: List[MaterialTuple]


"""Given a type, returns details that include a function to create and any
    material restrictions.  If materials restrictions is None, the shape can
    be any material."""
_TYPES_TO_DETAILS: Dict[str, TypeDetailsTuple] = {
    'antique_armchair_1': TypeDetailsTuple(
        _create_antique_armchair_1,
        LEATHER_ARMCHAIR_MATERIALS
    ),
    'antique_armchair_2': TypeDetailsTuple(
        _create_antique_armchair_2,
        []  # No material
    ),
    'antique_armchair_3': TypeDetailsTuple(
        _create_antique_armchair_3,
        []  # No material
    ),
    'antique_chair_1': TypeDetailsTuple(
        _create_antique_chair_1,
        WOOD_MATERIALS
    ),
    'antique_chair_2': TypeDetailsTuple(
        _create_antique_chair_2,
        []  # No material
    ),
    'antique_chair_3': TypeDetailsTuple(
        _create_antique_chair_3,
        []  # No material
    ),
    'antique_sofa_1': TypeDetailsTuple(
        _create_antique_sofa_1,
        WOOD_MATERIALS
    ),
    'antique_table_1': TypeDetailsTuple(
        _create_antique_table_1,
        WOOD_MATERIALS
    ),
    'apple_1': TypeDetailsTuple(
        _create_apple_1,
        []  # No material
    ), 'apple_2': TypeDetailsTuple(
        _create_apple_2,
        []  # No material
    ), 'ball': TypeDetailsTuple(
        _create_ball,
        (BLOCK_BLANK_MATERIALS + METAL_MATERIALS +
         PLASTIC_MATERIALS + RUBBER_MATERIALS + WOOD_MATERIALS)
    ), 'barrel_1': TypeDetailsTuple(
        _create_barrel_1,
        WOOD_MATERIALS
    ), 'barrel_2': TypeDetailsTuple(
        _create_barrel_2,
        WOOD_MATERIALS
    ), 'barrel_3': TypeDetailsTuple(
        _create_barrel_3,
        WOOD_MATERIALS
    ), 'barrel_4': TypeDetailsTuple(
        _create_barrel_4,
        WOOD_MATERIALS
    ), 'bed_1': TypeDetailsTuple(
        _create_bed_1,
        WOOD_MATERIALS
    ), 'bed_2': TypeDetailsTuple(
        _create_bed_2,
        WOOD_MATERIALS
    ), 'bed_3': TypeDetailsTuple(
        _create_bed_3,
        WOOD_MATERIALS
    ), 'bed_4': TypeDetailsTuple(
        _create_bed_4,
        WOOD_MATERIALS
    ), 'bed_5': TypeDetailsTuple(
        _create_bed_5,
        WOOD_MATERIALS
    ), 'bed_6': TypeDetailsTuple(
        _create_bed_6,
        WOOD_MATERIALS
    ), 'bed_7': TypeDetailsTuple(
        _create_bed_7,
        WOOD_MATERIALS
    ), 'bed_8': TypeDetailsTuple(
        _create_bed_8,
        WOOD_MATERIALS
    ), 'bed_9': TypeDetailsTuple(
        _create_bed_9,
        WOOD_MATERIALS
    ), 'bed_10': TypeDetailsTuple(
        _create_bed_10,
        WOOD_MATERIALS
    ), 'bed_11': TypeDetailsTuple(
        _create_bed_11,
        WOOD_MATERIALS
    ), 'bed_12': TypeDetailsTuple(
        _create_bed_12,
        WOOD_MATERIALS
    ), 'bin_1': TypeDetailsTuple(
        _create_bin_1,
        PLASTIC_MATERIALS
    ), 'bin_3': TypeDetailsTuple(
        _create_bin_3,
        PLASTIC_MATERIALS
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
    ), 'bobcat': TypeDetailsTuple(
        _create_toy_bobcat,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
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
    ), 'bowl_3_static': TypeDetailsTuple(
        _create_bowl_3,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'bowl_4': TypeDetailsTuple(
        _create_bowl_4,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'bowl_4_static': TypeDetailsTuple(
        _create_bowl_4,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'bowl_6': TypeDetailsTuple(
        _create_bowl_6,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'bowl_6_static': TypeDetailsTuple(
        _create_bowl_6,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'bus_1': TypeDetailsTuple(
        _create_toy_bus_1,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'car_1': TypeDetailsTuple(
        _create_toy_sedan,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'car_2': TypeDetailsTuple(
        _create_toy_car_2,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'car_3': TypeDetailsTuple(
        _create_toy_car_3,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'car_4': TypeDetailsTuple(
        _create_toy_car_4,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'car_5': TypeDetailsTuple(
        _create_toy_car_5,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'cart_1': TypeDetailsTuple(
        _create_cart,
        METAL_MATERIALS
    ), 'case_1': TypeDetailsTuple(
        _create_case_1,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'case_2': TypeDetailsTuple(
        _create_case_2,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'case_3': TypeDetailsTuple(
        _create_case_3,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'case_4': TypeDetailsTuple(
        _create_case_4,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'case_5': TypeDetailsTuple(
        _create_case_5,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'case_6': TypeDetailsTuple(
        _create_case_6,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'case_7': TypeDetailsTuple(
        _create_case_7,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'cart_2': TypeDetailsTuple(
        _create_cart_2,
        METAL_MATERIALS + PLASTIC_MATERIALS
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
    ), 'chair_5': TypeDetailsTuple(
        _create_chair_5,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_6': TypeDetailsTuple(
        _create_chair_6,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_7': TypeDetailsTuple(
        _create_chair_7,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_8': TypeDetailsTuple(
        _create_chair_8,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_9': TypeDetailsTuple(
        _create_chair_9,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_10': TypeDetailsTuple(
        _create_chair_10,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_11': TypeDetailsTuple(
        _create_chair_11,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_12': TypeDetailsTuple(
        _create_chair_12,
        PLASTIC_MATERIALS
    ), 'chair_13': TypeDetailsTuple(
        _create_chair_13,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_14': TypeDetailsTuple(
        _create_chair_14,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'chair_15': TypeDetailsTuple(
        _create_chair_15,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chair_16': TypeDetailsTuple(
        _create_chair_16,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'changing_table': TypeDetailsTuple(
        _create_changing_table,
        WOOD_MATERIALS
    ), 'chest_1': TypeDetailsTuple(
        _create_chest_1,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_2': TypeDetailsTuple(
        _create_chest_2,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_3': TypeDetailsTuple(
        _create_chest_3,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_4': TypeDetailsTuple(
        _create_chest_4,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_5': TypeDetailsTuple(
        _create_chest_5,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_6': TypeDetailsTuple(
        _create_chest_6,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_7': TypeDetailsTuple(
        _create_chest_7,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_8': TypeDetailsTuple(
        _create_chest_8,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'chest_9': TypeDetailsTuple(
        _create_chest_9,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_01': TypeDetailsTuple(
        _create_container_asymmetric_01,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_02': TypeDetailsTuple(
        _create_container_asymmetric_02,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_03': TypeDetailsTuple(
        _create_container_asymmetric_03,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_04': TypeDetailsTuple(
        _create_container_asymmetric_04,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_05': TypeDetailsTuple(
        _create_container_asymmetric_05,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_06': TypeDetailsTuple(
        _create_container_asymmetric_06,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_07': TypeDetailsTuple(
        _create_container_asymmetric_07,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_08': TypeDetailsTuple(
        _create_container_asymmetric_08,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_09': TypeDetailsTuple(
        _create_container_asymmetric_09,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_10': TypeDetailsTuple(
        _create_container_asymmetric_10,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_11': TypeDetailsTuple(
        _create_container_asymmetric_11,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_asymmetric_12': TypeDetailsTuple(
        _create_container_asymmetric_12,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_01': TypeDetailsTuple(
        _create_container_symmetric_01,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_02': TypeDetailsTuple(
        _create_container_symmetric_02,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_03': TypeDetailsTuple(
        _create_container_symmetric_03,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_04': TypeDetailsTuple(
        _create_container_symmetric_04,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_05': TypeDetailsTuple(
        _create_container_symmetric_05,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_06': TypeDetailsTuple(
        _create_container_symmetric_06,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_07': TypeDetailsTuple(
        _create_container_symmetric_07,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_08': TypeDetailsTuple(
        _create_container_symmetric_08,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_09': TypeDetailsTuple(
        _create_container_symmetric_09,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_10': TypeDetailsTuple(
        _create_container_symmetric_10,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_11': TypeDetailsTuple(
        _create_container_symmetric_11,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'container_symmetric_12': TypeDetailsTuple(
        _create_container_symmetric_12,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'crate_1': TypeDetailsTuple(
        _create_crate_1,
        WOOD_MATERIALS
    ), 'crate_2': TypeDetailsTuple(
        _create_crate_2,
        WOOD_MATERIALS
    ), 'crate_3': TypeDetailsTuple(
        _create_crate_3,
        WOOD_MATERIALS
    ), 'crate_4': TypeDetailsTuple(
        _create_crate_4,
        WOOD_MATERIALS
    ), 'crate_open_topped_1': TypeDetailsTuple(
        _create_crate_open_topped_1,
        WOOD_MATERIALS
    ), 'crate_open_topped_2': TypeDetailsTuple(
        _create_crate_open_topped_2,
        WOOD_MATERIALS
    ), 'crayon_black': TypeDetailsTuple(
        _create_crayon,
        []  # No material
    ), 'crayon_blue': TypeDetailsTuple(
        _create_crayon,
        []  # No material
    ), 'crayon_green': TypeDetailsTuple(
        _create_crayon,
        []  # No material
    ), 'crayon_pink': TypeDetailsTuple(
        _create_crayon,
        []  # No material
    ), 'crayon_red': TypeDetailsTuple(
        _create_crayon,
        []  # No material
    ), 'crayon_yellow': TypeDetailsTuple(
        _create_crayon,
        []  # No material
    ), 'crib': TypeDetailsTuple(
        _create_crib,
        WOOD_MATERIALS
    ), 'cup_2': TypeDetailsTuple(
        _create_cup_2,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'cup_2_static': TypeDetailsTuple(
        _create_cup_2,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'cup_3': TypeDetailsTuple(
        _create_cup_3,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'cup_3_static': TypeDetailsTuple(
        _create_cup_3,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'cup_6': TypeDetailsTuple(
        _create_cup_6,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'cup_6_static': TypeDetailsTuple(
        _create_cup_6,
        METAL_MATERIALS + WOOD_MATERIALS + PLASTIC_MATERIALS
    ), 'desk_1': TypeDetailsTuple(
        _create_desk_1,
        WOOD_MATERIALS
    ), 'desk_2': TypeDetailsTuple(
        _create_desk_2,
        WOOD_MATERIALS
    ), 'desk_3': TypeDetailsTuple(
        _create_desk_3,
        WOOD_MATERIALS
    ), 'desk_4': TypeDetailsTuple(
        _create_desk_4,
        WOOD_MATERIALS
    ), 'dog_on_wheels': TypeDetailsTuple(
        _create_dog_on_wheels,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'double_bookcase_1_shelf': TypeDetailsTuple(
        _create_double_bookcase_1_shelf,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'double_bookcase_2_shelf': TypeDetailsTuple(
        _create_double_bookcase_2_shelf,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'double_bookcase_3_shelf': TypeDetailsTuple(
        _create_double_bookcase_3_shelf,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'double_bookcase_4_shelf': TypeDetailsTuple(
        _create_double_bookcase_4_shelf,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'dog_on_wheels_2': TypeDetailsTuple(
        _create_dog_on_wheels_2,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'duck_on_wheels': TypeDetailsTuple(
        _create_duck_on_wheels,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'duck_on_wheels_2': TypeDetailsTuple(
        _create_duck_on_wheels_2,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'foam_floor_tiles': TypeDetailsTuple(
        _create_foam_floor_tiles,
        []  # No material
    ), 'jeep': TypeDetailsTuple(
        _create_toy_jeep,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'lid': TypeDetailsTuple(
        _create_lid_square,
        BLOCK_BLANK_MATERIALS + METAL_MATERIALS + PLASTIC_MATERIALS +
        WOOD_MATERIALS
    ), 'military_case_1': TypeDetailsTuple(
        _create_military_case_1,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'military_case_2': TypeDetailsTuple(
        _create_military_case_2,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'military_case_3': TypeDetailsTuple(
        _create_military_case_3,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'military_case_4': TypeDetailsTuple(
        _create_military_case_4,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'pacifier': TypeDetailsTuple(
        _create_pacifier,
        []  # No material
    ), 'plate_1': TypeDetailsTuple(
        _create_plate_1,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'plate_3': TypeDetailsTuple(
        _create_plate_3,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'plate_4': TypeDetailsTuple(
        _create_plate_4,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'power_shovel': TypeDetailsTuple(
        _create_toy_power_shovel,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'racecar_red': TypeDetailsTuple(
        _create_toy_racecar,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'road_scraper': TypeDetailsTuple(
        _create_toy_road_scraper,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'roller': TypeDetailsTuple(
        _create_toy_roller,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'separate_container': TypeDetailsTuple(
        _create_separate_container,
        BLOCK_BLANK_MATERIALS + METAL_MATERIALS + PLASTIC_MATERIALS +
        WOOD_MATERIALS
    ), 'shelf_1': TypeDetailsTuple(
        _create_shelf_1,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'shelf_2': TypeDetailsTuple(
        _create_shelf_2,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'skateboard': TypeDetailsTuple(
        _create_skateboard,
        []  # No material
    ), 'soccer_ball': TypeDetailsTuple(
        _create_soccer_ball,
        []  # No material
    ), 'sofa_1': TypeDetailsTuple(
        _create_sofa_1,
        SOFA_1_MATERIALS
    ), 'sofa_2': TypeDetailsTuple(
        _create_sofa_2,
        SOFA_2_MATERIALS
    ), 'sofa_3': TypeDetailsTuple(
        _create_sofa_3,
        SOFA_3_MATERIALS
    ), 'sofa_4': TypeDetailsTuple(
        _create_sofa_4,
        SOFA_THORKEA_MATERIALS
    ), 'sofa_5': TypeDetailsTuple(
        _create_sofa_5,
        SOFA_THORKEA_MATERIALS
    ), 'sofa_6': TypeDetailsTuple(
        _create_sofa_6,
        SOFA_THORKEA_MATERIALS
    ), 'sofa_7': TypeDetailsTuple(
        _create_sofa_7,
        SOFA_THORKEA_MATERIALS
    ), 'sofa_8': TypeDetailsTuple(
        _create_sofa_8,
        SOFA_8_MATERIALS
    ), 'sofa_9': TypeDetailsTuple(
        _create_sofa_9,
        SOFA_9_MATERIALS
    ), 'sofa_11': TypeDetailsTuple(
        _create_sofa_11,
        []  # No material
    ), 'sofa_12': TypeDetailsTuple(
        _create_sofa_12,
        []  # No material
    ), 'sofa_chair_1': TypeDetailsTuple(
        _create_sofa_chair_1,
        SOFA_CHAIR_1_MATERIALS
    ), 'sofa_chair_2': TypeDetailsTuple(
        _create_sofa_chair_2,
        SOFA_2_MATERIALS
    ), 'sofa_chair_3': TypeDetailsTuple(
        _create_sofa_chair_3,
        SOFA_3_MATERIALS
    ), 'sofa_chair_4': TypeDetailsTuple(
        _create_sofa_chair_4,
        ARMCHAIR_THORKEA_MATERIALS
    ), 'sofa_chair_5': TypeDetailsTuple(
        _create_sofa_chair_5,
        ARMCHAIR_THORKEA_MATERIALS
    ), 'sofa_chair_6': TypeDetailsTuple(
        _create_sofa_chair_6,
        ARMCHAIR_THORKEA_MATERIALS
    ), 'sofa_chair_7': TypeDetailsTuple(
        _create_sofa_chair_7,
        ARMCHAIR_THORKEA_MATERIALS
    ), 'sofa_chair_8': TypeDetailsTuple(
        _create_sofa_chair_8,
        SOFA_CHAIR_8_MATERIALS
    ), 'sofa_chair_9': TypeDetailsTuple(
        _create_sofa_chair_9,
        SOFA_9_MATERIALS
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
    ), 'table_13': TypeDetailsTuple(
        _create_table_13,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_14': TypeDetailsTuple(
        _create_table_14,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_15': TypeDetailsTuple(
        _create_table_15,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_16': TypeDetailsTuple(
        _create_table_16,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_17': TypeDetailsTuple(
        _create_table_17,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_18': TypeDetailsTuple(
        _create_table_18,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_19': TypeDetailsTuple(
        _create_table_19,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_20': TypeDetailsTuple(
        _create_table_20,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_21': TypeDetailsTuple(
        _create_table_21,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_22': TypeDetailsTuple(
        _create_table_22,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_25': TypeDetailsTuple(
        _create_table_25,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_26': TypeDetailsTuple(
        _create_table_26,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'table_27': TypeDetailsTuple(
        _create_table_27,
        PLASTIC_MATERIALS
    ), 'table_28': TypeDetailsTuple(
        _create_table_28,
        METAL_MATERIALS + PLASTIC_MATERIALS + WOOD_MATERIALS
    ), 'tank_1': TypeDetailsTuple(
        _create_toy_tank_1,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'tank_2': TypeDetailsTuple(
        _create_toy_tank_2,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'tank_3': TypeDetailsTuple(
        _create_toy_tank_3,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'toolbox_1': TypeDetailsTuple(
        _create_toolbox_1,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'toolbox_2': TypeDetailsTuple(
        _create_toolbox_2,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'toolbox_3': TypeDetailsTuple(
        _create_toolbox_3,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'toolbox_4': TypeDetailsTuple(
        _create_toolbox_4,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'toolbox_5': TypeDetailsTuple(
        _create_toolbox_5,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'toolbox_6': TypeDetailsTuple(
        _create_toolbox_6,
        METAL_MATERIALS + PLASTIC_MATERIALS
    ), 'train_1': TypeDetailsTuple(
        _create_toy_train_1,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'train_2': TypeDetailsTuple(
        _create_toy_train_2,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'train_3': TypeDetailsTuple(
        _create_toy_train_3,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'trike': TypeDetailsTuple(
        _create_toy_trike,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'trolley_1': TypeDetailsTuple(
        _create_toy_trolley,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'trophy': TypeDetailsTuple(
        _create_trophy,
        []  # No material
    ), 'truck_1': TypeDetailsTuple(
        _create_toy_truck_1,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'truck_2': TypeDetailsTuple(
        _create_toy_truck_2,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'truck_3': TypeDetailsTuple(
        _create_toy_truck_3,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'truck_4': TypeDetailsTuple(
        _create_toy_truck_4,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'truck_5': TypeDetailsTuple(
        _create_toy_truck_5,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'turtle_on_wheels': TypeDetailsTuple(
        _create_turtle_on_wheels,
        BLOCK_BLANK_MATERIALS + WOOD_MATERIALS
    ), 'tv_2': TypeDetailsTuple(
        _create_tv,
        []  # No material
    ), 'wardrobe': TypeDetailsTuple(
        _create_wardrobe,
        WOOD_MATERIALS
    )
}


for tool_type in LARGE_BLOCK_TOOLS_TO_DIMENSIONS.keys():
    _TYPES_TO_DETAILS[tool_type] = TypeDetailsTuple(
        _create_tool, TOOL_MATERIALS)


_PRIMITIVE_TUPLES = [
    ('circle_frustum', _create_primitive_non_cylinder),
    ('circle_frustum_with_base', _create_primitive_tall),
    ('cone', _create_primitive_non_cylinder),
    ('cone_with_base', _create_primitive_tall),
    ('cube', _create_primitive_non_cylinder),
    ('cube_hollow_narrow', _create_primitive_on_ground),
    ('cube_hollow_wide', _create_primitive_on_ground),
    ('cylinder', _create_primitive_cylinder),
    ('decagon_cylinder', _create_primitive_cylinder),
    ('double_cone', _create_primitive_non_cylinder),
    ('dumbbell_1', _create_primitive_non_cylinder),
    ('dumbbell_2', _create_primitive_non_cylinder),
    ('hash', _create_primitive_on_ground),
    ('hex_cylinder', _create_primitive_cylinder),
    ('hex_tube_narrow', _create_primitive_non_cylinder),
    ('hex_tube_wide', _create_primitive_non_cylinder),
    ('letter_l_narrow', _create_letter_l_narrow_tall),
    ('letter_l_wide', _create_letter_l_wide),
    ('letter_l_wide_tall', _create_letter_l_wide_tall),
    ('letter_x', _create_primitive_on_ground),
    ('lock_wall', _create_primitive_non_cylinder),
    ('pyramid', _create_primitive_non_cylinder),
    ('pyramid_with_base', _create_primitive_tall),
    ('rollable_1', _create_primitive_non_cylinder),
    ('rollable_2', _create_primitive_non_cylinder),
    ('rollable_3', _create_primitive_non_cylinder),
    ('rollable_4', _create_primitive_non_cylinder),
    ('rollable_5', _create_primitive_non_cylinder),
    ('rollable_6', _create_primitive_non_cylinder),
    ('rollable_7', _create_primitive_non_cylinder),
    ('rollable_8', _create_primitive_non_cylinder),
    ('sphere', _create_primitive_non_cylinder),
    ('square_frustum', _create_primitive_non_cylinder),
    ('square_frustum_with_base', _create_primitive_tall),
    ('tie_fighter', _create_primitive_non_cylinder),
    ('triangle', _create_primitive_triangle),
    ('tube_narrow', _create_primitive_non_cylinder),
    ('tube_wide', _create_primitive_non_cylinder)
]
for primitive_type, primitive_function in _PRIMITIVE_TUPLES:
    _TYPES_TO_DETAILS[primitive_type] = TypeDetailsTuple(
        primitive_function,
        ALL_PRIMITIVE_MATERIAL_TUPLES
    )


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


def get_material_restriction_strings(shape: str) -> List[str]:
    """Return the list of materials that are valid for the given shape.
    If no restrictions are present, return all materials"""
    if shape is None:
        return ALL_UNRESTRICTED_MATERIAL_STRINGS
    if shape in _TYPES_TO_DETAILS:
        details = _TYPES_TO_DETAILS[shape]
        if details is None or details.material_restrictions is None:
            return ALL_UNRESTRICTED_MATERIAL_STRINGS
        else:
            return [mat[0] for mat in details.material_restrictions]
    return []


def get_material_restriction_tuples(shape: str) -> List[MaterialTuple]:
    """Return the list of materials that are valid for the given shape.
    If no restrictions are present, return all materials"""
    if shape is None:
        return ALL_UNRESTRICTED_MATERIAL_TUPLES
    if shape in _TYPES_TO_DETAILS:
        details = _TYPES_TO_DETAILS[shape]
        if details is None or details.material_restrictions is None:
            return ALL_UNRESTRICTED_MATERIAL_TUPLES
        else:
            return details.material_restrictions
    return []


def has_material_restriction(shape: str) -> bool:
    """Returns whether the given shape has a material restriction or not"""
    return shape in _TYPES_TO_DETAILS and _TYPES_TO_DETAILS[shape] is not None


def is_valid_shape_material(
    shape: str,
    material: Union[str, MaterialTuple]
) -> bool:
    """returns whether shape and material combination are valid"""
    if shape in _TYPES_TO_DETAILS:
        if _TYPES_TO_DETAILS[shape] is None:
            return True
        restrictions = _TYPES_TO_DETAILS[shape].material_restrictions
        if restrictions is None:
            return True
        if restrictions == []:
            return material is None
        if not isinstance(material, Tuple):
            return any(material == mat_tuple[0] for mat_tuple in restrictions)
        if material not in restrictions:
            return False
    return True


# List of all currently supported object types (shapes).
FULL_TYPE_LIST: List[str] = list(_TYPES_TO_DETAILS.keys())


ALL_LARGE_BLOCK_TOOLS: List[str] = [
    shape for shape in FULL_TYPE_LIST if shape.startswith('tool_')
]


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
