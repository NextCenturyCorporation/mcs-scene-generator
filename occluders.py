import copy
from typing import Any, Dict, List, Tuple
import util
import uuid


OCCLUDER_HEIGHT = 1.5
OCCLUDER_POSITION_Z = 1

OCCLUDER_MIN_SCALE_X = 0.5
OCCLUDER_MAX_SCALE_X = 1.4
OCCLUDER_SEPARATION_X = 0.5
OCCLUDER_BUFFER = 0.1

# The max X position so an occluder is seen within the camera's view.
OCCLUDER_MAX_X = 3
OCCLUDER_DEFAULT_MAX_X = OCCLUDER_MAX_X - (OCCLUDER_MIN_SCALE_X / 2)

# Each occluder will take 6 steps to move and rotate.
OCCLUDER_MOVEMENT_TIME = 6


_OCCLUDER_INSTANCE_NORMAL = [{
    "id": "occluder_wall_",
    "shape": ["wall"],
    "size": "huge",
    "type": "cube",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": OCCLUDER_HEIGHT / 2.0,
            "z": OCCLUDER_POSITION_Z
        },
        "scale": {
            "x": 1,
            "y": OCCLUDER_HEIGHT,
            "z": 0.1
        }
    }],
    "moves": [{
        "stepBegin": 1,
        "stepEnd": 6,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }, {
        "stepBegin": 7,
        "stepEnd": 12,
        "vector": {
            "x": 0,
            "y": -0.25,
            "z": 0
        }
    }, {
        "stepBegin": 85,
        "stepEnd": 90,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }],
    "rotates": [{
        "stepBegin": 1,
        "stepEnd": 2,
        "vector": {
            "x": 0,
            "y": 45,
            "z": 0
        }
    }, {
        "stepBegin": 11,
        "stepEnd": 12,
        "vector": {
            "x": 0,
            "y": -45,
            "z": 0
        }
    }, {
        "stepBegin": 89,
        "stepEnd": 90,
        "vector": {
            "x": 0,
            "y": 45,
            "z": 0
        }
    }]
}, {
    "id": "occluder_pole_",
    "shape": ["pole"],
    "size": "medium",
    "type": "cylinder",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 3.25,
            "z": OCCLUDER_POSITION_Z
        },
        "scale": {
            "x": 0.095,
            "y": 2,
            "z": 0.095
        }
    }],
    "moves": [{
        "stepBegin": 1,
        "stepEnd": 6,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }, {
        "stepBegin": 7,
        "stepEnd": 12,
        "vector": {
            "x": 0,
            "y": -0.25,
            "z": 0
        }
    }, {
        "stepBegin": 85,
        "stepEnd": 90,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }]
}]


_OCCLUDER_INSTANCE_SIDEWAYS = [{
    "id": "occluder_wall_",
    "shape": ["wall"],
    "size": "huge",
    "type": "cube",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": OCCLUDER_HEIGHT / 2.0,
            "z": OCCLUDER_POSITION_Z
        },
        "scale": {
            "x": 1,
            "y": OCCLUDER_HEIGHT,
            "z": 0.1
        }
    }],
    "moves": [{
        "stepBegin": 1,
        "stepEnd": 4,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }, {
        "stepBegin": 9,
        "stepEnd": 12,
        "vector": {
            "x": 0,
            "y": -0.25,
            "z": 0
        }
    }, {
        "stepBegin": 55,
        "stepEnd": 58,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }],
    "rotates": [{
        "stepBegin": 5,
        "stepEnd": 6,
        "vector": {
            "x": 45,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": 7,
        "stepEnd": 8,
        "vector": {
            "x": -45,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": 59,
        "stepEnd": 60,
        "vector": {
            "x": 45,
            "y": 0,
            "z": 0
        }
    }]
}, {
    "id": "occluder_pole_",
    "shape": ["pole"],
    "size": "medium",
    "type": "cylinder",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": OCCLUDER_HEIGHT / 2.0,
            "z": OCCLUDER_POSITION_Z
        },
        "rotation": {
            "x": 0,
            "y": 0,
            "z": 90
        },
        "scale": {
            "x": 0.095,
            "y": 3,
            "z": 0.095
        }
    }],
    "moves": [{
        "stepBegin": 1,
        "stepEnd": 4,
        "vector": {
            "x": 0.25,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": 9,
        "stepEnd": 12,
        "vector": {
            "x": -0.25,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": 55,
        "stepEnd": 58,
        "vector": {
            "x": 0.25,
            "y": 0,
            "z": 0
        }
    }]
}]


def calculate_separation_distance(
    x_position_1: float,
    x_size_1: float,
    x_position_2: float,
    x_size_2: float
) -> bool:
    """Return the distance separating the two occluders (or one object and
    one occluder) with the given X positions and X sizes. A negative
    distance means that the two objects are too close to one another."""
    distance = abs(x_position_1 - x_position_2)
    separation = (x_size_1 + x_size_2) / 2.0
    return distance - (separation + OCCLUDER_SEPARATION_X)


def create_occluder(
    wall_material: Tuple[str, List[str]],
    pole_material: Tuple[str, List[str]],
    x_position: float,
    x_scale: float,
    sideways_left: bool = False,
    sideways_right: bool = False,
    occluder_height: float = OCCLUDER_HEIGHT,
    last_step: int = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Create an occluder as a pair of separate wall and pole objects."""

    if sideways_left or sideways_right:
        occluder = copy.deepcopy(_OCCLUDER_INSTANCE_SIDEWAYS)
        occluder[0]['shows'][0]['position']['y'] = occluder_height / 2.0
        occluder[0]['shows'][0]['scale']['y'] = occluder_height
        occluder[1]['shows'][0]['position']['y'] = occluder_height / 2.0
    else:
        occluder = copy.deepcopy(_OCCLUDER_INSTANCE_NORMAL)
        occluder[0]['shows'][0]['position']['y'] = occluder_height / 2.0
        occluder[0]['shows'][0]['scale']['y'] = occluder_height

    WALL = 0
    POLE = 1

    occluder_id = str(uuid.uuid4())
    occluder[WALL]['id'] = occluder[WALL]['id'] + occluder_id
    occluder[POLE]['id'] = occluder[POLE]['id'] + occluder_id

    occluder[WALL]['materials'] = [wall_material[0]]
    occluder[POLE]['materials'] = [pole_material[0]]

    occluder[WALL]['color'] = wall_material[1]
    occluder[POLE]['color'] = pole_material[1]

    # Just set the occluder's info to its color for now.
    occluder[WALL]['info'] = wall_material[1]
    occluder[POLE]['info'] = pole_material[1]

    occluder[WALL]['shows'][0]['position']['x'] = x_position
    occluder[POLE]['shows'][0]['position']['x'] = x_position

    occluder[WALL]['shows'][0]['scale']['x'] = x_scale

    if sideways_left or sideways_right:
        occluder[POLE]['shows'][0]['position']['x'] = (
            generate_occluder_pole_position_x(
                x_position,
                x_scale,
                sideways_left
            )
        )
    elif x_position > 0:
        for rot in occluder[WALL]['rotates']:
            rot['vector']['y'] *= -1

    if last_step:
        if sideways_left or sideways_right:
            occluder[POLE]['moves'][-1]['stepBegin'] = last_step - 5
            occluder[POLE]['moves'][-1]['stepEnd'] = last_step - 2
            occluder[WALL]['moves'][-1]['stepBegin'] = last_step - 5
            occluder[WALL]['moves'][-1]['stepEnd'] = last_step - 2
            occluder[WALL]['rotates'][-1]['stepBegin'] = last_step - 1
            occluder[WALL]['rotates'][-1]['stepEnd'] = last_step
        else:
            occluder[POLE]['moves'][-1]['stepBegin'] = last_step - 5
            occluder[POLE]['moves'][-1]['stepEnd'] = last_step
            occluder[WALL]['moves'][-1]['stepBegin'] = last_step - 5
            occluder[WALL]['moves'][-1]['stepEnd'] = last_step
            occluder[WALL]['rotates'][-1]['stepBegin'] = last_step - 1
            occluder[WALL]['rotates'][-1]['stepEnd'] = last_step

    return occluder


def generate_occluder_pole_position_x(
    wall_x_position: float,
    wall_x_scale: float,
    sideways_left: bool
) -> float:
    """Generate and return the X position for a sideways occluder's pole object
    using the given properties."""
    if sideways_left:
        return -3 + wall_x_position - wall_x_scale / 2
    return 3 + wall_x_position + wall_x_scale / 2


def generate_occluder_position(
    x_scale: float,
    occluder_list: List[Dict[str, Any]]
) -> float:
    """Generate and return a random X position for a new occluder with the
    given X scale that isn't too close to an existing occluder from the
    given list."""
    max_x = OCCLUDER_MAX_X - x_scale / 2.0
    max_x = int(max_x / util.MIN_RANDOM_INTERVAL) * util.MIN_RANDOM_INTERVAL

    for _ in range(util.MAX_TRIES):
        # Choose a random position.
        x_position = util.random_real(-max_x, max_x, util.MIN_RANDOM_INTERVAL)

        # Ensure the new occluder isn't too close to an existing occluder.
        too_close = False
        for occluder in occluder_list:
            too_close = calculate_separation_distance(
                occluder['shows'][0]['position']['x'],
                occluder['shows'][0]['scale']['x'],
                x_position,
                x_scale
            ) < 0
            if too_close:
                break
        if not too_close:
            return x_position

    return None
