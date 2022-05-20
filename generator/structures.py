import copy
import math
import uuid
from typing import Any, Dict, List

from machine_common_sense.config_manager import Vector3d
from shapely import affinity

from .base_objects import (
    ALL_LARGE_BLOCK_TOOLS,
    LARGE_BLOCK_TOOLS_TO_DIMENSIONS,
)
from .geometry import PERFORMER_HEIGHT, ObjectBounds, create_bounds
from .materials import MaterialTuple

ANGLE_BRACE_TEMPLATE = {
    'id': 'angle_brace_',
    'type': 'letter_l_narrow',
    'debug': {
        'color': [],
        'info': []
    },
    'mass': 10,
    'materials': [],
    'kinematic': True,
    'structure': True,
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': 0.5,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}


L_OCCLUDER_TEMPLATE = [{
    'id': 'occluder_front_',
    'type': 'cube',
    'debug': {
        'color': [],
        'info': []
    },
    'mass': 1000,
    'materials': [],
    'kinematic': True,
    'structure': True,
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': 0.5,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}, {
    'id': 'occluder_side_',
    'type': 'cube',
    'debug': {
        'color': [],
        'info': []
    },
    'mass': 1000,
    'materials': [],
    'kinematic': True,
    'structure': True,
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': 0.5,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}]


INTERIOR_WALL_TEMPLATE = {
    'id': 'wall_',
    'type': 'cube',
    'debug': {
        'color': [],
        'info': []
    },
    'mass': 1000,
    'materials': [],
    'kinematic': True,
    'structure': True,
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': 0.5,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}


PLATFORM_TEMPLATE = {
    'id': 'platform_',
    'type': 'cube',
    'debug': {
        'color': [],
        'info': []
    },
    'mass': 1000,
    'materials': [],
    'kinematic': True,
    'structure': True,
    'lips': {
        'front': False,
        'back': False,
        'left': False,
        'right': False,
    },
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': 0.5,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}


RAMP_TEMPLATE = {
    'id': 'ramp_',
    'type': 'triangle',
    'debug': {
        'color': [],
        'info': []
    },
    'mass': 1000,
    'materials': [],
    'kinematic': True,
    'structure': True,
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': 0.5,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}

DOOR_TEMPLATE = {
    'id': 'door_',
    'type': 'door_4',
    'debug': {
        'color': [],
        'info': []
    },
    'mass': 100,
    'materials': [],
    'kinematic': True,
    'openable': True,
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}

TOOL_HEIGHT = 0.3
TOOL_TEMPLATE = {
    'id': 'tool_',
    'type': None,
    'debug': {
        'color': ['grey', 'black'],
        'info': []
    },
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': TOOL_HEIGHT / 2.0,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}

GUIDE_RAIL_DEFAULT_POSITION_Y = 0.1
GUIDE_RAIL_TEMPLATE = {
    'id': 'guide_rail_',
    'type': 'cube',
    'debug': {
        'color': [],
        'info': []
    },
    'mass': None,  # Set in finalize_structural_object
    'materials': [],  # Set to randomly chosen material
    'kinematic': True,
    'structure': True,
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,  # Set to necessary position
            'y': GUIDE_RAIL_DEFAULT_POSITION_Y,
            'z': 0  # Set to necessary position
        },
        'rotation': {
            'x': 0,
            'y': 0,  # Set to necessary rotation
            'z': 0
        },
        'scale': {
            'x': 0.2,
            'y': 0.2,
            'z': 1  # Set to necessary length
        }
    }]
}

# door constants
BASE_DOOR_HEIGHT = 2.0
BASE_DOOR_WIDTH = 0.85
BASE_WALL_WITH_DOOR_WIDTH = 1.0
BASE_SIDE_WALL_POSITION = 0.21
BASE_SIDE_WALL_SCALE = 0.08

# guide rail constants
RAIL_CENTER_TO_EDGE = 0.2


def _calculate_info(colors: List[str], labels: List[str]) -> List[str]:
    combos = []
    for label in labels:
        for color in colors:
            combos.append(f'{color} {label}')
        if len(colors) > 1:
            combos.append(f'{" ".join(colors)} {label}')
    return colors + labels + combos


def _calculate_mass(dimensions: Dict[str, float]) -> float:
    """Calculate and return a significantly large mass for a structure."""
    # This calculation is arbitrary and can be modified if needed.
    return max(
        round(dimensions['x'] * dimensions['y'] * dimensions['z'] * 125),
        1
    )


def create_angle_brace(
    position_x: float,
    position_z: float,
    rotation_y: int,
    width: float,
    height: float,
    thickness: float,
    material_tuple: MaterialTuple,
    position_y_modifier: float = 0,
    rotation_x: int = 0,
    rotation_z: int = 0,
    bounds: ObjectBounds = None
) -> Dict[str, Any]:
    """Create and return an instance of an L-shaped angle brace. Please note
    that its side is twice as long as its bottom, and that it's facing to the
    right (positive X axis) by default."""
    angle_brace = copy.deepcopy(ANGLE_BRACE_TEMPLATE)
    angle_brace['id'] += str(uuid.uuid4())
    angle_brace['shows'][0]['position'] = {
        'x': position_x,
        'y': position_y_modifier + (height / 2.0),
        'z': position_z
    }
    angle_brace['shows'][0]['rotation'] = {
        'x': rotation_x,
        'y': rotation_y,
        'z': rotation_z
    }
    angle_brace['shows'][0]['scale'] = {
        'x': width,
        'y': height,
        'z': thickness
    }
    return finalize_structural_object(
        [angle_brace],
        material_tuple,
        ['angle_brace'],
        bounds
    )[0]


def create_interior_wall(
    position_x: float,
    position_z: float,
    rotation_y: float,
    width: float,
    height: float,
    material_tuple: MaterialTuple,
    position_y_modifier: float = 0,
    thickness: float = 0.1,
    bounds: ObjectBounds = None
) -> Dict[str, Any]:
    """Create and return an instance of an interior room wall."""
    wall = copy.deepcopy(INTERIOR_WALL_TEMPLATE)
    wall['id'] += str(uuid.uuid4())
    wall['shows'][0]['position'] = {
        'x': position_x,
        'y': position_y_modifier + (height / 2.0),
        'z': position_z
    }
    wall['shows'][0]['rotation'] = {
        'x': 0,
        'y': rotation_y,
        'z': 0
    }
    wall['shows'][0]['scale'] = {
        'x': width,
        'y': height,
        'z': thickness
    }
    return finalize_structural_object(
        [wall],
        material_tuple,
        ['wall'],
        bounds
    )[0]


def create_l_occluder(
    position_x: float,
    position_z: float,
    rotation_y: float,
    scale_front_x: float,
    scale_front_z: float,
    scale_side_x: float,
    scale_side_z: float,
    scale_y: float,
    material_tuple: MaterialTuple,
    position_y_modifier: float = 0,
    flip: bool = False
) -> List[Dict[str, Any]]:
    """Create and return an instance of an L-shaped occluder. If flip is True,
    the side part of the L will be on the left side (like a backwards L)."""
    occluder = copy.deepcopy(L_OCCLUDER_TEMPLATE)
    front = occluder[0]
    side = occluder[1]

    front['shows'][0]['scale'] = {
        'x': scale_front_x,
        'y': scale_y,
        'z': scale_front_z
    }
    front['shows'][0]['position'] = {
        'x': position_x,
        'y': position_y_modifier + (scale_y / 2.0),
        'z': position_z
    }
    front['shows'][0]['rotation'] = {
        'x': 0,
        'y': rotation_y,
        'z': 0
    }

    side['shows'][0]['scale'] = {
        'x': scale_side_x,
        'y': scale_y,
        'z': scale_side_z
    }
    side['shows'][0]['position'] = {
        'x': position_x + (
            (scale_side_x / 2.0) - (scale_front_x / 2.0)
        ) * (-1 if flip else 1),
        'y': position_y_modifier + (scale_y / 2.0),
        'z': (position_z + (scale_side_z / 2.0) + (scale_front_z / 2.0))
    }

    if rotation_y:
        # To rotate the side part of the L-shaped occluder:
        # 1st, create its bounds using its current position and no rotation.
        side_bounds = create_bounds(
            dimensions=side['shows'][0]['scale'],
            offset={'x': 0, 'y': 0, 'z': 0},
            position=side['shows'][0]['position'],
            rotation=side['shows'][0]['rotation'],
            standing_y=(side['shows'][0]['scale']['y'] / 2.0)
        )
        # 2nd, rotate its polygon using the front's center as the origin.
        rotated_polygon = affinity.rotate(
            side_bounds.polygon_xz,
            # In shapely, positive rotation values are counter-clockwise.
            -rotation_y,
            origin=(
                front['shows'][0]['position']['x'],
                front['shows'][0]['position']['z']
            )
        )
        # 3rd, update its position using the rotated polygon's center.
        center_coords = rotated_polygon.centroid.coords[0]
        side['shows'][0]['position']['x'] = center_coords[0]
        side['shows'][0]['position']['z'] = center_coords[1]
        # 4th, finally, update its rotation to the correct value.
        side['shows'][0]['rotation'] = {
            'x': 0,
            'y': rotation_y,
            'z': 0
        }

    return finalize_structural_object(occluder, material_tuple, ['occluder'])


def create_platform(
    position_x: float,
    position_z: float,
    rotation_y: float,
    scale_x: float,
    scale_y: float,
    scale_z: float,
    room_dimension_y: int,
    material_tuple: MaterialTuple,
    lips: dict = None,
    position_y_modifier: float = 0,
    bounds: ObjectBounds = None,
    auto_adjust_platform: bool = False
) -> Dict[str, Any]:
    """Create and return an instance of a platform."""
    platform = copy.deepcopy(PLATFORM_TEMPLATE)

    buffer = PERFORMER_HEIGHT
    if auto_adjust_platform:
        if position_y_modifier > 0:
            top_of_platform = position_y_modifier + scale_y
            if top_of_platform > room_dimension_y - buffer:
                top_of_platform = room_dimension_y - buffer
                bottom_of_platform = position_y_modifier
                fixed_y = (top_of_platform + bottom_of_platform) / 2
                fixed_scale = (top_of_platform - fixed_y) * 2
                position_y_modifier = fixed_y - fixed_scale / 2
                scale_y = fixed_scale
        elif scale_y > room_dimension_y - buffer:
            scale_y = room_dimension_y - buffer
    lips = platform['lips'] if lips is None else lips if isinstance(
        lips, dict) else lips.__dict__
    platform['lips'] = {
        'front': lips['front'],
        'back': lips['back'],
        'left': lips['left'],
        'right': lips['right'],
    }
    if lips.get('gaps'):
        platform['lips']['gaps'] = lips['gaps']
    platform['shows'][0]['position'] = {
        'x': position_x,
        'y': position_y_modifier + (scale_y / 2.0),
        'z': position_z
    }
    platform['shows'][0]['rotation'] = {
        'x': 0,
        'y': rotation_y,
        'z': 0
    }
    platform['shows'][0]['scale'] = {
        'x': scale_x,
        'y': scale_y,
        'z': scale_z
    }
    return finalize_structural_object(
        [platform],
        material_tuple,
        ['platform'],
        bounds
    )[0]


def create_ramp(
    angle: float,
    position_x: float,
    position_z: float,
    rotation_y: float,
    width: float,
    length: float,
    material_tuple: MaterialTuple,
    position_y_modifier: float = 0,
    bounds: ObjectBounds = None
) -> Dict[str, Any]:
    """Create and return an instance of a ramp. Its height is derived from the
    given angle and length.  Length is the length along the ground in a single
    dimension.  The angle must be in degress up from the ground."""
    height = length * (math.tan(math.radians(angle)))
    ramp = copy.deepcopy(RAMP_TEMPLATE)
    ramp['shows'][0]['position'] = {
        'x': position_x,
        'y': position_y_modifier + (height / 2.0),
        'z': position_z
    }
    ramp['shows'][0]['rotation'] = {
        'x': 0,
        'y': rotation_y,
        'z': 0
    }
    ramp['shows'][0]['scale'] = {
        'x': width,
        'y': height,
        'z': length
    }
    return finalize_structural_object(
        [ramp],
        material_tuple,
        ['ramp', f'ramp_{angle}_degree'],
        bounds,
        override_scale={
            'x': ramp['shows'][0]['scale']['x'],
            'y': ramp['shows'][0]['scale']['y'],
            'z': ramp['shows'][0]['scale']['z']
        }
    )[0]


def create_door(
    position_x: float,
    position_y: float,
    position_z: float,
    rotation_y: float,
    material_tuple: MaterialTuple,
    wall_material_tuple: MaterialTuple,
    wall_scale_x: float,
    wall_scale_y: float,
    bounds: ObjectBounds = None,
    add_walls: bool = True,
) -> List[Dict[str, Any]]:
    """Create and return an instance of an interior door."""
    if rotation_y not in [0, 90, 180, 270]:
        raise Exception("Doors rotation must be either 0, 90, 180, or 270")

    # if we ever want to alter the scale of the door, we need to update wall
    # calculations.
    scale_x = 1
    scale_y = 1
    scale_z = 1
    # The wall_x_scale must be at least 1 (the door itself is a little under 1
    # wide and we want to have walls on both sides of it).
    wall_scale_x = max(BASE_WALL_WITH_DOOR_WIDTH, wall_scale_x)
    # The wall_y_scale must be at least 2 (since doors are 2 units tall)
    wall_scale_y = max(BASE_DOOR_HEIGHT, wall_scale_y)

    # Calculate the properties for the top and side wall sections
    top_wall_scale_x = wall_scale_x
    top_wall_scale_y = (wall_scale_y - BASE_DOOR_HEIGHT)
    top_wall_position_y = position_y + \
        BASE_DOOR_HEIGHT + (top_wall_scale_y / 2.0)
    side_wall_scale_x = ((wall_scale_x - 1) * 0.5) + BASE_SIDE_WALL_SCALE
    side_wall_position_offset = (wall_scale_x * 0.25) + BASE_SIDE_WALL_POSITION

    # The X and Z positions of the side wall sections will depend on the Y
    # rotation
    side_wall_position_x = (
        side_wall_position_offset if rotation_y in {0, 180} else 0
    )

    side_wall_position_z = (
        side_wall_position_offset if rotation_y in {90, 270} else 0
    )

    if add_walls:
        door_wall_objects = _get_door_wall_objects(
            position_x=position_x,
            position_y=position_y,
            position_z=position_z,
            rotation_y=rotation_y,
            top_wall_position_y=top_wall_position_y,
            side_wall_position_x=side_wall_position_x,
            side_wall_position_z=side_wall_position_z,
            top_wall_scale_x=top_wall_scale_x,
            top_wall_scale_y=top_wall_scale_y,
            side_wall_scale_x=side_wall_scale_x)

    door = copy.deepcopy(DOOR_TEMPLATE)
    door['shows'][0]['position'] = {
        'x': position_x,
        'y': position_y,
        'z': position_z
    }
    door['shows'][0]['rotation'] = {
        'x': 0,
        'y': rotation_y,
        'z': 0
    }
    door['shows'][0]['scale'] = {
        'x': scale_x,
        'y': scale_y,
        'z': scale_z
    }
    objs = finalize_structural_object(
        [door],
        material_tuple,
        ['door'],
        bounds,
        override_scale={
            'x': BASE_DOOR_WIDTH * scale_x,
            'y': BASE_DOOR_HEIGHT * scale_y,
            # Ensure that both sides of the door's opening are big enough to
            # walk through, and that they're spaced away from other walls.
            'z': BASE_DOOR_WIDTH * scale_z * 2
        },
        override_offset={'x': 0, 'y': 1, 'z': 0},
        override_standing_y=0
    )
    walls = []
    if add_walls:
        walls = finalize_structural_object(
            door_wall_objects,
            wall_material_tuple,
            ['door_wall'],
            bounds
        )
    return objs + walls


def create_door_occluder(room_dimensions: Vector3d,
                         door_start_drop_step: int,
                         door_mat: MaterialTuple,
                         wall_mat: MaterialTuple,
                         middle_height: float,
                         middle_width: float,
                         position_z: float = 0):
    door_gap = room_dimensions.y - middle_height - 2.25
    side_wall_x = (room_dimensions.x - middle_width) / 2
    side_pos_x = room_dimensions.x / 2 - side_wall_x / 2
    add_y = room_dimensions.y
    doors_objs = []
    door_x = [0, -side_pos_x, side_pos_x]
    door_y = [middle_height, 0, 0]
    wall_scale_x = [middle_width, side_wall_x, side_wall_x]
    wall_scale_y = [
        room_dimensions.y -
        middle_height - door_gap,
        room_dimensions.y - door_gap,
        room_dimensions.y - door_gap]
    door_end_drop_step = door_start_drop_step + add_y * 4 - 1
    for i in range(3):
        new_objs = create_door(
            position_x=door_x[i],
            position_y=door_y[i] + add_y,
            position_z=position_z,
            rotation_y=0,
            material_tuple=door_mat,
            wall_scale_x=wall_scale_x[i],
            wall_scale_y=wall_scale_y[i],
            wall_material_tuple=wall_mat)
        for new_obj in new_objs:
            new_obj['moves'] = [{
                "stepBegin": door_start_drop_step,
                "stepEnd": door_end_drop_step,
                "vector": {
                    "x": 0,
                    "y": -0.25,
                    "z": 0
                }
            }]
        doors_objs += new_objs
    center_door = doors_objs[0]
    left_door = doors_objs[4]
    right_door = doors_objs[8]
    return (doors_objs, int(door_end_drop_step),
            center_door, left_door, right_door)


def _get_door_wall_objects(
    position_x: float,
    position_y: float,
    position_z: float,
    rotation_y: float,
    top_wall_position_y: float,
    side_wall_position_x: float,
    side_wall_position_z: float,
    top_wall_scale_x: float,
    top_wall_scale_y: float,
    side_wall_scale_x: float,
    wall_material_str: str = "Custom/Materials/GreyDrywallMCS",
):
    # Create the wall sections and the door object
    objs = []
    # only add top wall if the scale is greater than 0
    if top_wall_scale_x > 0 and top_wall_scale_y > 0:
        objs.append({
            "id": "wall_top",
            "type": "cube",
            "mass": 10,
            "materials": [wall_material_str],
            'debug': {
                'color': [],
                'info': []
            },
            "kinematic": True,
            "structure": True,
            "shows": [
                {
                    "stepBegin": 0,
                    "position": {
                        "x": position_x,
                        "y": top_wall_position_y,
                        "z": position_z
                    },
                    "rotation": {
                        "x": 0,
                        "y": rotation_y,
                        "z": 0
                    },
                    "scale": {
                        "x": top_wall_scale_x,
                        "y": top_wall_scale_y,
                        "z": 0.1
                    }
                }
            ]
        })
    if side_wall_scale_x > 0:
        objs += [{
            "id": "wall_left",
            "type": "cube",
            "mass": 10,
            "materials": [wall_material_str],
            'debug': {
                    'color': [],
                    'info': []
            },
            "kinematic": True,
            "structure": True,
            "shows": [
                {
                    "stepBegin": 0,
                    "position": {
                        "x": position_x - side_wall_position_x,
                        "y": 1 + position_y,
                        "z": position_z - side_wall_position_z
                    },
                    "rotation": {
                        "x": 0,
                        "y": rotation_y,
                        "z": 0
                    },
                    "scale": {
                        "x": side_wall_scale_x,
                        "y": 2,
                        "z": 0.1
                    }
                }
            ]
        },
            {
            "id": "wall_right",
            "type": "cube",
            "mass": 10,
            "materials": [wall_material_str],
            'debug': {
                'color': [],
                'info': []
            },
            "kinematic": True,
            "structure": True,
            "shows": [
                {
                    "stepBegin": 0,
                    "position": {
                        "x": position_x + side_wall_position_x,
                        "y": 1 + position_y,
                        "z": position_z + side_wall_position_z
                    },
                    "rotation": {
                        "x": 0,
                        "y": rotation_y,
                        "z": 0
                    },
                    "scale": {
                        "x": side_wall_scale_x,
                        "y": 2,
                        "z": 0.1
                    }
                }
            ]
        }
        ]
    return objs


def create_guide_rails_around(
        position_x: float,
        position_z: float,
        rotation_y: float,
        length: float,
        width: float,
        material_tuple: MaterialTuple,
        position_y: float = GUIDE_RAIL_DEFAULT_POSITION_Y,
        bounds: ObjectBounds = None):
    """Provide a rectangle to put rails on the sides.  The rectangle will be
    centered on the position, rotated by the rotation_y and have size of
    length and width."""
    if rotation_y not in [0, 90, 180, 270]:
        raise Exception("Guide rails only implemented at rotations of 0, 90, "
                        "180, and 270.")
    if rotation_y % 180 == 0:
        x1 = position_x + width / 2.0 + RAIL_CENTER_TO_EDGE
        x2 = position_x - width / 2.0 - RAIL_CENTER_TO_EDGE
        z1 = position_z
        z2 = position_z
    else:
        x1 = position_x
        x2 = position_x
        z1 = position_z + width / 2.0 + RAIL_CENTER_TO_EDGE
        z2 = position_z - width / 2.0 - RAIL_CENTER_TO_EDGE
    rail1 = create_guide_rail(
        x1,
        z1,
        rotation_y=rotation_y,
        length=length,
        position_y=position_y,
        material_tuple=material_tuple,
        bounds=bounds)
    rail2 = create_guide_rail(
        x2,
        z2,
        rotation_y=rotation_y,
        length=length,
        position_y=position_y,
        material_tuple=material_tuple,
        bounds=bounds)
    return [rail1, rail2]


def create_guide_rail(
        position_x: float,
        position_z: float,
        rotation_y: float,
        length: float,
        material_tuple: MaterialTuple,
        position_y: float = GUIDE_RAIL_DEFAULT_POSITION_Y,
        bounds: ObjectBounds = None):
    rail = copy.deepcopy(GUIDE_RAIL_TEMPLATE)
    rail['shows'][0]['position']['x'] = position_x
    rail['shows'][0]['position']['y'] = position_y
    rail['shows'][0]['position']['z'] = position_z
    rail['shows'][0]['rotation']['y'] = rotation_y
    rail['shows'][0]['scale']['z'] = length
    rail = finalize_structural_object(
        [rail],
        material_tuple,
        ['guide_rail'],
        bounds
    )[0]
    return rail


def create_tool(
    # TODO MCS-1206 Move into a separate file for interactable objects
    object_type: str,
    position_x: float,
    position_z: float,
    rotation_y: float,
    bounds: ObjectBounds = None
) -> Dict[str, Any]:
    """Create and return an instance of a tool."""
    tool = copy.deepcopy(TOOL_TEMPLATE)
    tool['type'] = object_type
    tool['shows'][0]['position']['x'] = position_x
    tool['shows'][0]['position']['z'] = position_z
    tool['shows'][0]['rotation']['y'] = rotation_y
    dimensions = LARGE_BLOCK_TOOLS_TO_DIMENSIONS.get(object_type)
    if not dimensions:
        raise Exception(f'Tool object type must be in {ALL_LARGE_BLOCK_TOOLS}')
    tool = finalize_structural_object(
        [tool],
        # Use the tool's default materials set by the Unity prefab.
        None,
        ['tool'],
        bounds,
        override_scale={
            'x': dimensions[0],
            'y': TOOL_HEIGHT,
            'z': dimensions[1]
        },
        override_standing_y=(TOOL_HEIGHT / 2.0)
    )[0]
    # Use the tool's default mass set in the Unity object registry file.
    del tool['mass']
    return tool


def finalize_structural_object(
    instance_list: List[Dict[str, Any]],
    material_tuple: MaterialTuple = None,
    name_list: List[str] = None,
    bounds: ObjectBounds = None,
    override_scale: Dict[str, float] = None,
    override_offset: Dict[str, float] = None,
    override_standing_y: float = None
) -> List[Dict[str, Any]]:
    """Finalize and return each of the instances of structural objects."""
    common_id = str(uuid.uuid4())
    for instance in instance_list:
        scale = override_scale or instance['shows'][0]['scale']
        instance['id'] += common_id
        instance['shows'][0]['boundingBox'] = bounds or create_bounds(
            dimensions=scale,
            offset=override_offset or {'x': 0, 'y': 0, 'z': 0},
            position=instance['shows'][0]['position'],
            rotation=instance['shows'][0]['rotation'],
            standing_y=(
                scale['y'] / 2.0 if override_standing_y is None
                else override_standing_y
            )
        )
        instance['debug']['dimensions'] = instance['shows'][0]['scale'].copy()
        instance['mass'] = _calculate_mass(instance['debug']['dimensions'])
        if material_tuple:
            instance['materials'] = [material_tuple.material]
            instance['debug']['color'] = material_tuple.color
        instance['debug']['info'] = _calculate_info(
            instance['debug']['color'],
            name_list or []
        )
    return instance_list
