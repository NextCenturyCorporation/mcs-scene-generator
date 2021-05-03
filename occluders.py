import copy
from typing import Any, Dict, List, Tuple
import util
import uuid


# Default occluder height of 1.8 enables seeing a falling object for 8+ frames.
OCCLUDER_HEIGHT = 1.8
OCCLUDER_HEIGHT_TALL = 3
OCCLUDER_POSITION_Z = 1

OCCLUDER_MIN_SCALE_X = 0.5
OCCLUDER_MAX_SCALE_X = 1.4
OCCLUDER_SEPARATION_X = 0.5
OCCLUDER_BUFFER = 0.1

# The max X position so an occluder is seen within the camera's view.
OCCLUDER_MAX_X = 3
OCCLUDER_DEFAULT_MAX_X = OCCLUDER_MAX_X - (OCCLUDER_MIN_SCALE_X / 2)

# Each occluder will take up to 40 steps to move, rotate, and wait before it
# can move again.
OCCLUDER_MOVEMENT_TIME = 40

MOVE_STEP_LENGTH = 6
MOVE_AMOUNT_UP = 1.5 / MOVE_STEP_LENGTH
ROTATE_STEP_WAIT = 4


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
        "stepEnd": MOVE_STEP_LENGTH,
        "vector": {
            "x": 0,
            "y": MOVE_AMOUNT_UP,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": 0,
            "y": -MOVE_AMOUNT_UP,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": 0,
            "y": MOVE_AMOUNT_UP,
            "z": 0
        }
    }],
    "rotates": [{
        "stepBegin": MOVE_STEP_LENGTH + 1,
        "stepEnd": None,
        "vector": {
            "x": 0,
            "y": None,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": 0,
            "y": None,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": 0,
            "y": None,
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
        "stepEnd": MOVE_STEP_LENGTH,
        "vector": {
            "x": 0,
            "y": MOVE_AMOUNT_UP,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": 0,
            "y": -MOVE_AMOUNT_UP,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": 0,
            "y": MOVE_AMOUNT_UP,
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
        "stepEnd": MOVE_STEP_LENGTH,
        "vector": {
            "x": 0,
            "y": MOVE_AMOUNT_UP,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": 0,
            "y": -MOVE_AMOUNT_UP,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": 0,
            "y": MOVE_AMOUNT_UP,
            "z": 0
        }
    }],
    "rotates": [{
        "stepBegin": MOVE_STEP_LENGTH + 1,
        "stepEnd": None,
        "vector": {
            "x": None,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": 7,
        "stepEnd": 8,
        "vector": {
            "x": None,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": 59,
        "stepEnd": 60,
        "vector": {
            "x": None,
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
        "stepEnd": MOVE_STEP_LENGTH,
        "vector": {
            "x": MOVE_AMOUNT_UP,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": -MOVE_AMOUNT_UP,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": MOVE_AMOUNT_UP,
            "y": 0,
            "z": 0
        }
    }]
}]


WALL = 0
POLE = 1


def adjust_movement_and_rotation_to_scale(
    occluder: List[Dict[str, Any]],
    sideways: bool,
    last_step: int,
    x_scale_override: float = None
) -> None:
    """Adjust the move and rotate properties of the given occluder based on its
    given X scale and the other input."""
    x_position = occluder[WALL]['shows'][0]['position']['x']
    x_scale = (
        x_scale_override if x_scale_override
        else occluder[WALL]['shows'][0]['scale']['x']
    )

    # Rotation step length based on occluder's X scale.
    rotate_length = find_rotate_step_length(x_scale)
    rotate_amount = 90.0 / rotate_length
    rotate_prop = 'x' if sideways else 'y'

    # Note: Subtract 1 from each stepEnd because the property's inclusive.

    # Rotate occluder wall by 90 degrees after a short delay.
    occluder[WALL]['rotates'][0]['stepEnd'] = MOVE_STEP_LENGTH + rotate_length
    occluder[WALL]['rotates'][0]['vector'][rotate_prop] = rotate_amount

    # Rotate occluder wall back after a short pause.
    occluder[WALL]['rotates'][1]['stepBegin'] = (
        MOVE_STEP_LENGTH + rotate_length + ROTATE_STEP_WAIT + 1
    )
    occluder[WALL]['rotates'][1]['stepEnd'] = (
        MOVE_STEP_LENGTH + (2 * rotate_length) + ROTATE_STEP_WAIT
    )
    occluder[WALL]['rotates'][1]['vector'][rotate_prop] = -rotate_amount

    # Move occluder back down after its first rotation.
    move_down_step_begin = occluder[WALL]['rotates'][1]['stepEnd'] + 1
    move_down_step_end = move_down_step_begin + MOVE_STEP_LENGTH - 1
    occluder[WALL]['moves'][1]['stepBegin'] = move_down_step_begin
    occluder[WALL]['moves'][1]['stepEnd'] = move_down_step_end
    occluder[POLE]['moves'][1]['stepBegin'] = move_down_step_begin
    occluder[POLE]['moves'][1]['stepEnd'] = move_down_step_end

    # Move occluder back up at end of scene before its final rotate.
    move_up_step_begin = (
        last_step - rotate_length - MOVE_STEP_LENGTH - ROTATE_STEP_WAIT + 1
    )
    move_up_step_end = move_up_step_begin + MOVE_STEP_LENGTH - 1
    occluder[WALL]['moves'][2]['stepBegin'] = move_up_step_begin
    occluder[WALL]['moves'][2]['stepEnd'] = move_up_step_end
    occluder[POLE]['moves'][2]['stepBegin'] = move_up_step_begin
    occluder[POLE]['moves'][2]['stepEnd'] = move_up_step_end

    # Rotate occluder wall by 90 degrees at end of scene after its final move.
    occluder[WALL]['rotates'][2]['stepBegin'] = move_up_step_end + 1
    occluder[WALL]['rotates'][2]['stepEnd'] = last_step - ROTATE_STEP_WAIT
    occluder[WALL]['rotates'][2]['vector'][rotate_prop] = rotate_amount

    if (not sideways) and (x_position > 0):
        # Rotate counterclockwise if occluder is on the right (positive) side.
        for rotate in occluder[WALL]['rotates']:
            rotate['vector']['y'] *= -1


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
    sideways_left: bool,
    sideways_right: bool,
    occluder_height: float,
    last_step: int
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Create an occluder as a pair of separate wall and pole objects."""

    if sideways_left or sideways_right:
        occluder = copy.deepcopy(_OCCLUDER_INSTANCE_SIDEWAYS)
        occluder[POLE]['shows'][0]['position']['y'] = occluder_height / 2.0
    else:
        occluder = copy.deepcopy(_OCCLUDER_INSTANCE_NORMAL)

    occluder[WALL]['shows'][0]['position']['y'] = occluder_height / 2.0
    occluder[WALL]['shows'][0]['scale']['y'] = occluder_height

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
        # Adjust the pole position for the sideways occluder.
        occluder[POLE]['shows'][0]['position']['x'] = (
            generate_occluder_pole_position_x(
                x_position,
                x_scale,
                sideways_left
            )
        )

    adjust_movement_and_rotation_to_scale(
        occluder,
        sideways_left or sideways_right,
        last_step
    )

    return occluder


def find_rotate_step_length(x_size: float) -> int:
    # Values chosen somewhat arbitrarily. All values evenly divide into 90,
    # because (I believe) the rotation amount (in degrees) must be an int.
    # TODO Consider refactoring to use a single equation in the future.
    if x_size <= 0.5:
        return 3
    if x_size <= 1:
        return 5
    if x_size <= 1.5:
        return 6
    # Larger values needed for hypercubes with "stop" movement.
    if x_size <= 2:
        return 9
    if x_size <= 2.5:
        return 10
    if x_size <= 3:
        return 15
    if x_size <= 3.5:
        return 18
    return 30


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
