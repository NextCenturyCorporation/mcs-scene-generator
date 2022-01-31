import copy
import math
import uuid
from typing import Any, Dict, List

from shapely import affinity

from .geometry import ObjectBounds, create_bounds
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
    'structure': True,
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
    """Create and return an instance of an L-shaped occluder."""
    occluder = copy.deepcopy(L_OCCLUDER_TEMPLATE)
    front = occluder[0]
    side = occluder[1]

    front['shows'][0]['scale'] = {
        'x': scale_front_x,
        'y': scale_y,
        'z': scale_front_z
    }
    front['shows'][0]['position'] = {
        'x': position_x * (-1 if flip else 1),
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
        'x': (
            (position_x + (scale_side_x / 2.0) - (scale_front_x / 2.0))
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
    material_tuple: MaterialTuple,
    position_y_modifier: float = 0,
    bounds: ObjectBounds = None
) -> Dict[str, Any]:
    """Create and return an instance of a platform."""
    platform = copy.deepcopy(PLATFORM_TEMPLATE)
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
    position_z: float,
    rotation_y: float,
    scale_x: float,
    scale_y: float,
    scale_z: float,
    material_tuple: MaterialTuple,
    bounds: ObjectBounds = None
) -> Dict[str, Any]:
    """Create and return an instance of an interior door."""

    door = copy.deepcopy(DOOR_TEMPLATE)
    door['id'] += str(uuid.uuid4())
    door['shows'][0]['position'] = {
        'x': position_x,
        'y': 0,
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
    return finalize_structural_object(
        [door],
        material_tuple,
        ['door'],
        bounds
    )[0]


def finalize_structural_object(
    instance_list: List[Dict[str, Any]],
    material_tuple: MaterialTuple = None,
    name_list: List[str] = None,
    bounds: ObjectBounds = None,
    override_scale: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """Finalize and return each of the instances of structural objects."""
    common_id = str(uuid.uuid4())
    for instance in instance_list:
        scale = override_scale or instance['shows'][0]['scale']
        instance['id'] += common_id
        instance['shows'][0]['boundingBox'] = bounds or create_bounds(
            dimensions=scale,
            offset={'x': 0, 'y': 0, 'z': 0},
            position=instance['shows'][0]['position'],
            rotation=instance['shows'][0]['rotation'],
            standing_y=(scale['y'] / 2.0)
        )
        instance['debug']['dimensions'] = instance['shows'][0]['scale'].copy()
        instance['mass'] = _calculate_mass(instance['debug']['dimensions'])
        if material_tuple:
            instance['materials'] = [material_tuple.material]
            instance['debug']['color'] = material_tuple.color
            instance['debug']['info'] = _calculate_info(
                material_tuple.color,
                name_list or []
            )
    return instance_list
