import copy
import uuid
from typing import Any, Dict, List, Tuple

from .util import MAX_TRIES, MIN_RANDOM_INTERVAL, random_real

# Default occluder height of 1.8 enables seeing a falling object for 8+ frames.
OCCLUDER_HEIGHT = 1.8
OCCLUDER_HEIGHT_TALL = 3
OCCLUDER_POSITION_Z = 1
OCCLUDER_THICKNESS = 0.1

OCCLUDER_MIN_SCALE_X = 0.5
OCCLUDER_MAX_SCALE_X = 1.4
OCCLUDER_SEPARATION_X = 0.5
OCCLUDER_BUFFER = 0.1

# The max X position so an occluder is seen within the camera's view.
# ONLY INTENDED FOR USE IN INTUITIVE PHYSICS HYPERCUBES.
OCCLUDER_MAX_X = 3
OCCLUDER_DEFAULT_MAX_X = OCCLUDER_MAX_X - (OCCLUDER_MIN_SCALE_X / 2)

# Each occluder will take up to 40 steps to move, rotate, and wait before it
# can move again.
OCCLUDER_MOVEMENT_TIME = 40

POLE_RADIUS_OFFSET = 0.005

MOVE_STEP_LENGTH = 6
MOVE_AMOUNT_UP = 1.5 / MOVE_STEP_LENGTH
ROTATE_STEP_WAIT = 4

# TODO Where to put this?
DEFAULT_INTUITIVE_PHYSICS_ROOM_DIMENSIONS = {'x': 15, 'y': 4, 'z': 10}


_OCCLUDER_INSTANCE_NORMAL = [{
    "id": "occluder_wall_",
    "type": "cube",
    "debug": {
        "shape": ["wall"],
        "size": "huge"
    },
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 0,
            "z": 0
        },
        "rotation": {
            "x": 0,
            "y": 0,
            "z": 0
        },
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
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
    "type": "cylinder",
    "debug": {
        "shape": ["pole"],
        "size": "medium"
    },
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 3.25,
            "z": 0
        },
        "rotation": {
            "x": 0,
            "y": 0,
            "z": 0
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
    "type": "cube",
    "debug": {
        "shape": ["wall"],
        "size": "huge"
    },
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 0,
            "z": 0
        },
        "rotation": {
            "x": 0,
            "y": 0,
            "z": 0
        },
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
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
    "type": "cylinder",
    "debug": {
        "shape": ["pole"],
        "size": "medium"
    },
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 0,
            "z": 0
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
    rotate_amount = int(90.0 / rotate_length)
    rotate_prop = 'x' if sideways else 'y'

    # Note: Subtract 1 from each stepEnd because the property's inclusive.

    # Rotate the occluder wall in increments to a total of 90 degrees
    # immediately after moving up.
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

    if last_step is None:
        # Remove the final move and rotate for non-hypercube scenes.
        occluder[WALL]['moves'].pop()
        occluder[POLE]['moves'].pop()
        occluder[WALL]['rotates'].pop()

    else:
        # Move occluder back up at end of scene before its final rotate.
        move_up_step_begin = (
            last_step - rotate_length - MOVE_STEP_LENGTH - ROTATE_STEP_WAIT + 1
        )
        move_up_step_end = move_up_step_begin + MOVE_STEP_LENGTH - 1
        occluder[WALL]['moves'][2]['stepBegin'] = move_up_step_begin
        occluder[WALL]['moves'][2]['stepEnd'] = move_up_step_end
        occluder[POLE]['moves'][2]['stepBegin'] = move_up_step_begin
        occluder[POLE]['moves'][2]['stepEnd'] = move_up_step_end

        # Rotate occluder wall by 90 deg at end of scene after its final move.
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
    occluder_width: float,
    last_step: int = None,
    occluder_height: float = OCCLUDER_HEIGHT,
    occluder_thickness: float = OCCLUDER_THICKNESS,
    repeat_movement: int = None,
    reverse_direction: bool = False,
    room_dimensions: Dict[str, float] = None,
    sideways_back: bool = False,
    sideways_front: bool = False,
    sideways_left: bool = False,
    sideways_right: bool = False,
    y_rotation: int = 0,
    z_position: float = OCCLUDER_POSITION_Z
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Create and return a moving and rotating intuitive-physics-style occluder
    as a pair of wall and pole object instances. By default, the pole is
    vertical above the center of the wall. The timing of the movement and the
    rotation is currently always static. Arguments:

    - wall_material: Material of the occluder wall (cube)
    - pole_material: Material of the occluder pole (cylinder)
    - x_position: X position of the center of the occluder
    - occluder_width: Width (X scale) of the occluder wall
    - occluder_height: Height (Y scale) of the occluder wall
    - occluder_thickness: Thickness (Z scale) of the occluder wall
    - last_step: The last step for the scene; if set, it will enable one final
                 movement and rotation at the end of the scene; not used if a
                 repeat_movement is set.
                 ONLY INTENDED FOR USE IN INTUITIVE PHYSICS HYPERCUBES.
    - repeat_movement: If set, repeat the occluder's full movement and rotation
                       indefinitely, using the given value as the step wait.
    - reverse_direction: Reverse the rotation direction of a sideways wall by
                         rotating the wall 180 degrees; only used if a
                         "sideways" argument is set (for non-sideways
                         occluders, please use y_rotation)
    - room_dimensions: Room dimensions; if unset, assume the default dimensions
    - sideways_back: Rotate the wall 90 degrees and position the pole
                     horizontally on the back side (-Z)
    - sideways_front: Rotate the wall 90 degrees and position the pole
                     horizontally on the front side (+Z)
    - sideways_left: Position the pole horizontally on the left side (-X)
    - sideways_right: Position the pole horizontally on the right side (+X)
    - y_rotation: Y rotation of a non-sideways occluder wall; not used if any
                  "sideways" arguments are set
    - z_position: Z position of the center of the occluder
    """

    room = room_dimensions or DEFAULT_INTUITIVE_PHYSICS_ROOM_DIMENSIONS
    occluder_height_half = round(occluder_height / 2.0, 3)

    if sideways_left or sideways_right:
        occluder = copy.deepcopy(_OCCLUDER_INSTANCE_SIDEWAYS)
        pole_x_position = generate_sideways_pole_position_x(
            x_position,
            occluder_width,
            sideways_left,
            room['x']
        )
        occluder[POLE]['shows'][0]['position']['x'] = pole_x_position
        occluder[POLE]['shows'][0]['position']['y'] = occluder_height_half
        occluder[POLE]['shows'][0]['position']['z'] = z_position
        occluder[POLE]['shows'][0]['scale']['y'] = round(
            (room['x'] * 0.5) - abs(pole_x_position),
            3
        )
        occluder[WALL]['shows'][0]['rotation']['y'] = (
            180 if reverse_direction else 0
        )
    elif sideways_back or sideways_front:
        occluder = copy.deepcopy(_OCCLUDER_INSTANCE_SIDEWAYS)
        # Do the same as with sideways_left or sideways_right, but just swap
        # the X and Z positions, and add Y rotation.
        pole_z_position = generate_sideways_pole_position_x(
            z_position,
            occluder_width,
            sideways_back,
            room['z']
        )
        occluder[POLE]['shows'][0]['position']['x'] = x_position
        occluder[POLE]['shows'][0]['position']['y'] = occluder_height_half
        occluder[POLE]['shows'][0]['position']['z'] = pole_z_position
        occluder[POLE]['shows'][0]['scale']['y'] = round(
            (room['z'] * 0.5) - abs(pole_z_position),
            3
        )
        occluder[POLE]['shows'][0]['rotation']['y'] = 90
        occluder[WALL]['shows'][0]['rotation']['y'] = (
            -90 if reverse_direction else 90
        )
    else:
        occluder = copy.deepcopy(_OCCLUDER_INSTANCE_NORMAL)
        pole_length = round((room['y'] - occluder_height) / 2.0, 3)
        occluder[POLE]['shows'][0]['scale']['y'] = pole_length
        occluder[POLE]['shows'][0]['position']['x'] = x_position
        occluder[POLE]['shows'][0]['position']['y'] = round(
            pole_length + occluder_height,
            3
        )
        occluder[POLE]['shows'][0]['position']['z'] = z_position
        occluder[WALL]['shows'][0]['rotation']['y'] = y_rotation

    occluder[WALL]['shows'][0]['position']['x'] = x_position
    occluder[WALL]['shows'][0]['position']['y'] = occluder_height_half
    occluder[WALL]['shows'][0]['position']['z'] = z_position
    occluder[WALL]['shows'][0]['scale']['x'] = occluder_width
    occluder[WALL]['shows'][0]['scale']['y'] = occluder_height
    occluder[WALL]['shows'][0]['scale']['z'] = occluder_thickness

    pole_thickness = round(occluder_thickness - POLE_RADIUS_OFFSET, 3)
    occluder[POLE]['shows'][0]['scale']['x'] = pole_thickness
    occluder[POLE]['shows'][0]['scale']['z'] = pole_thickness

    occluder_id = str(uuid.uuid4())
    occluder[WALL]['id'] = occluder[WALL]['id'] + occluder_id
    occluder[POLE]['id'] = occluder[POLE]['id'] + occluder_id

    occluder[WALL]['materials'] = [wall_material[0]]
    occluder[POLE]['materials'] = [pole_material[0]]

    occluder[WALL]['debug']['color'] = wall_material[1]
    occluder[POLE]['debug']['color'] = pole_material[1]

    # Just set the occluder's info to its color for now.
    occluder[WALL]['debug']['info'] = wall_material[1]
    occluder[POLE]['debug']['info'] = pole_material[1]

    adjust_movement_and_rotation_to_scale(
        occluder,
        sideways_back or sideways_front or sideways_left or sideways_right,
        # Ignore the last_step behavior if the repeat_movement is not None
        last_step if repeat_movement is None else None
    )

    if repeat_movement is not None:
        # Calculate the intervals between each repeated movement/rotation, and
        # add the repeat_movement as a modifier to the step wait.
        move_interval = repeat_movement + (
            occluder[WALL]['moves'][1]['stepEnd'] -
            occluder[WALL]['moves'][0]['stepEnd'] +
            occluder[WALL]['moves'][0]['stepBegin']
        )
        rotate_interval = repeat_movement + (
            occluder[WALL]['moves'][1]['stepEnd'] -
            occluder[WALL]['rotates'][0]['stepEnd'] +
            occluder[WALL]['rotates'][0]['stepBegin']
        )
        for action_index in [0, 1]:
            # Update the rotation for both the wall and the pole.
            for object_index in [WALL, POLE]:
                move = occluder[object_index]['moves'][action_index]
                move['repeat'] = True
                move['stepWait'] = move_interval
            # Update the rotation for the wall (the pole doesn't rotate).
            rotate = occluder[WALL]['rotates'][action_index]
            rotate['repeat'] = True
            rotate['stepWait'] = rotate_interval

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


def generate_sideways_pole_position_x(
    wall_x_position: float,
    wall_x_scale: float,
    sideways_left: bool,
    room_x: int = 10
) -> float:
    """Generate and return the X position for a sideways occluder's pole object
    using the given properties."""
    return round(
        ((room_x + wall_x_scale) * 0.25 * (-1 if sideways_left else 1)) +
        (wall_x_position * 0.5),
        3
    )


def generate_occluder_position(
    x_scale: float,
    occluder_list: List[Dict[str, Any]]
) -> float:
    """Generate and return a random X position for a new occluder with the
    given X scale that isn't too close to an existing occluder from the
    given list."""
    max_x = OCCLUDER_MAX_X - x_scale / 2.0
    max_x = int(max_x / MIN_RANDOM_INTERVAL) * MIN_RANDOM_INTERVAL

    for _ in range(MAX_TRIES):
        # Choose a random position.
        x_position = random_real(-max_x, max_x, MIN_RANDOM_INTERVAL)

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
