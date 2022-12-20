import copy
import uuid
from typing import Any, Dict, List, Tuple

from .geometry import (
    MAX_TRIES,
    MIN_RANDOM_INTERVAL,
    create_bounds,
    random_real
)
from .intuitive_physics_util import retrieve_off_screen_position_x
from .materials import MaterialTuple

# Default occluder height of 1.8 enables seeing a falling object for 8+ frames.
OCCLUDER_HEIGHT = 1.8
OCCLUDER_HEIGHT_TALL = 3
OCCLUDER_POSITION_Z = 1
OCCLUDER_THICKNESS = 0.1

# This buffer should handle any minor variability in the speed of rolling
# objects (in intuitive physics move across scenes) due to difference in shape.
OCCLUDER_BUFFER = 0.1
OCCLUDER_BUFFER_MULTIPLE_EXIT = 0.4 + OCCLUDER_BUFFER
OCCLUDER_BUFFER_EXIT_AND_STOP = 0.4 + OCCLUDER_BUFFER_MULTIPLE_EXIT
# An occluder must have a maximum width to hide the current largest possible
# intuitive physics object, measured diagonally, rounded up (1.4 in Eval 5).
# Remember to add the OCCLUDER_BUFFER!
OCCLUDER_MAX_SCALE_X = 1.4
OCCLUDER_MIN_SCALE_X = 0.4

# Minimum separation from between occluder and viewport
OCCLUDER_MIN_VIEWPORT_GAP = .25

# Minimum separation between two adjacent occluders.
OCCLUDER_SEPARATION_X = 0.5

# The max X position so an occluder is seen within the camera's view.
# ONLY INTENDED FOR USE IN INTUITIVE PHYSICS HYPERCUBES.
OCCLUDER_MAX_X = 2.75

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
        "stepBegin": None,
        "stepEnd": None,
        "vector": {
            "x": None,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": None,
        "stepEnd": None,
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
    wall_material: MaterialTuple,
    pole_material: MaterialTuple,
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
    z_position: float = OCCLUDER_POSITION_Z,
    move_down_only: bool = False
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
    - move_down_only: If true, occluder will start near the ceiling and move
                      down until touching the floor, and will not rotate.
    """

    room = room_dimensions or DEFAULT_INTUITIVE_PHYSICS_ROOM_DIMENSIONS
    occluder_height_half = round(occluder_height / 2.0, 3)

    # Move down only applies just to sideways occluders for now
    if sideways_left or sideways_right:
        occluder = copy.deepcopy(_OCCLUDER_INSTANCE_SIDEWAYS)
        pole_x_position = generate_sideways_pole_position_x(
            x_position,
            occluder_width,
            sideways_left,
            room['x']
        )
        occluder[POLE]['shows'][0]['position']['x'] = pole_x_position
        # make sure pole is towards the top of occluder for move_down_only
        # setting, so that the performer has room to walk underneath the pole
        occluder[POLE]['shows'][0]['position']['y'] = room['y'] - \
            OCCLUDER_BUFFER if move_down_only else occluder_height_half
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
        # make sure pole is towards the top of occluder for move_down_only
        # setting, so that the performer has room to walk underneath the pole
        occluder[POLE]['shows'][0]['position']['y'] = room['y'] - \
            OCCLUDER_BUFFER if move_down_only else occluder_height_half
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
        if(move_down_only):
            occluder[POLE]['shows'][0]['position']['y'] += (
                room['y'] - occluder_height)
        occluder[POLE]['shows'][0]['position']['z'] = z_position
        occluder[WALL]['shows'][0]['rotation']['y'] = y_rotation

    occluder[WALL]['shows'][0]['position']['x'] = x_position
    occluder[WALL]['shows'][0]['position']['y'] = (
        room['y'] - occluder_height_half if move_down_only else
        occluder_height_half)
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

    occluder[WALL]['materials'] = [wall_material.material]
    occluder[POLE]['materials'] = [pole_material.material]

    occluder[WALL]['debug']['color'] = wall_material.color
    occluder[POLE]['debug']['color'] = pole_material.color

    occluder[WALL]['debug']['dimensions'] = copy.deepcopy(
        occluder[WALL]['shows'][0]['scale']
    )
    occluder[POLE]['debug']['dimensions'] = copy.deepcopy(
        occluder[POLE]['shows'][0]['scale']
    )

    # Just set the occluder's info to its color for now.
    occluder[WALL]['debug']['info'] = wall_material.color
    occluder[POLE]['debug']['info'] = pole_material.color

    if(move_down_only):
        # remove extraneous moves/rotates for move down
        # case
        del occluder[POLE]['moves'][2]
        del occluder[POLE]['moves'][0]
        del occluder[WALL]['moves'][2]
        del occluder[WALL]['moves'][0]
        del occluder[WALL]['rotates']

        move_down_dist = (
            occluder[WALL]['shows'][0]['position']['y'] -
            occluder_height_half)
        step_end = round(move_down_dist / MOVE_AMOUNT_UP)

        occluder[POLE]['moves'][0]['stepBegin'] = 1
        occluder[WALL]['moves'][0]['stepBegin'] = 1
        occluder[POLE]['moves'][0]['stepEnd'] = step_end
        occluder[WALL]['moves'][0]['stepEnd'] = step_end
    else:
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

    is_sideways = (
        sideways_back or sideways_front or sideways_left or sideways_right
    )
    _assign_occluder_bounds(occluder[WALL], is_sideways)
    _assign_occluder_bounds(occluder[POLE], is_sideways, is_pole=True)
    return occluder


def _assign_occluder_bounds(
    occluder_part: Dict[str, Any],
    is_sideways: bool,
    is_pole: bool = False
) -> None:
    dimensions_x = occluder_part['shows'][0]['scale']['x']
    dimensions_y = occluder_part['shows'][0]['scale']['y']
    dimensions_z = occluder_part['shows'][0]['scale']['z']
    if is_pole:
        # Unity automatically doubles a cylinder's height.
        dimensions_y *= 2
        # The create_bounds function will adjust for the Y rotation but not
        # the Z, so swap the X and Y dimensions if the pole is sideways.
        if is_sideways:
            temp = dimensions_x
            dimensions_x = dimensions_y
            dimensions_y = temp
    occluder_part['shows'][0]['boundingBox'] = create_bounds(
        dimensions={
            'x': dimensions_x,
            'y': dimensions_y,
            'z': dimensions_z
        },
        offset={'x': 0, 'y': 0, 'z': 0},
        position=occluder_part['shows'][0]['position'],
        rotation=occluder_part['shows'][0]['rotation'],
        standing_y=(dimensions_y / 2.0)
    )
    # The occluder's bounding box should occupy the entire vertical space.
    occluder_part['shows'][0]['boundingBox'].extend_bottom_to_ground()


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
        x_position = random_real(-max_x, max_x)

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


def make_occluder_sideways(
    wall: Dict[str, Any],
    pole: Dict[str, Any],
    is_left: bool,
    room_x: int = DEFAULT_INTUITIVE_PHYSICS_ROOM_DIMENSIONS['x']
) -> None:
    """Changes the given occluder to its sideways orientation."""
    # Reposition the occluder pole to the side.
    pole['shows'][0]['position']['x'] = generate_sideways_pole_position_x(
        wall['shows'][0]['position']['x'],
        wall['shows'][0]['scale']['x'],
        is_left,
        room_x=room_x
    )
    pole['shows'][0]['position']['y'] = wall['shows'][0]['position']['y']
    pole['shows'][0]['rotation']['z'] = 90
    # Adjust the occluder pole scale and dimensions as needed.
    pole['shows'][0]['scale']['y'] = round(
        (room_x / 2.0) - abs(pole['shows'][0]['position']['x']),
        3
    )
    pole['debug']['dimensions'] = copy.deepcopy(pole['shows'][0]['scale'])
    # Update the occluder pole bounds.
    _assign_occluder_bounds(pole, is_sideways=True, is_pole=True)
    # Change the axis on which the occluder wall rotates.
    for index, rotate in enumerate(wall['rotates']):
        multiplier = -1 if index == 1 else 1
        rotate['vector']['x'] = multiplier * abs(rotate['vector']['y'])
        rotate['vector']['y'] = 0
    # Change the axis on which the occluder pole moves.
    for move in pole['moves']:
        move['vector']['x'] = move['vector']['y']
        move['vector']['y'] = 0


def occluder_gap_positioning(scene, gap, vp_gap, new_obj, sideways):

    #     """If gap is not None, changes the X position of the occluders' Pole
    #     and wall so that the X distance between the inner edges of the
    #     occluder walls are `gap`.
    #     if vp_gap is not None and gap is None, changes the x position of the
    #     occluders Pole and wall so that the egde of the occluder is 'vp_gap'
    #     from the edge of the viewport.
    #     if gap and vp_gap is not None, `gap` takes precedence over `vp_gap`
    #     and `vp_gap` acts like a miinimum distance check
    #     Assumptions:
    #         1. In an occluder wall/pole set, wall comes first in the list
    #         2. Occluder wall/pole has id prefix of 'occluder_wall_*` and
    #            'occluder_pole_*`
    #     Constraints:
    #         1. The viewport gap (vp_gap) only works with 1 or 2 occluders.
    #            The occluders are moved to the nearest viewport using the
    #            `vp_gap` distance.
    #     """

    view_edge_x = retrieve_off_screen_position_x(
        scene.performer_start.position.x)

    set_complete = False
    prev_wall_dim_x = None
    prev_wall_x = None

    # Make gap between occluders = gap
    if gap is not None:
        for index, key in enumerate(scene.objects):
            # handle more than two occluders
            if set_complete:  # next occluder set
                if "occluder_wall_" in scene.objects[index]['id']:
                    wall_dim_x = \
                        scene.objects[index]['debug']['dimensions']['x'] / 2
                    if prev_wall_x < \
                            scene.objects[index]['shows'][0]['position']['x']:
                        new_pos_x = \
                            prev_wall_x + prev_wall_dim_x + gap + wall_dim_x
                        scene.objects[index]['shows'][0]['position']['x'] = \
                            new_pos_x
                    else:
                        new_pos_x = \
                            prev_wall_x - prev_wall_dim_x - gap - wall_dim_x
                        scene.objects[index]['shows'][0]['position']['x'] = \
                            new_pos_x

                    prev_wall_x = new_pos_x
                    prev_wall_dim_x = wall_dim_x

                if "occluder_pole_" in scene.objects[index]['id']:
                    scene.objects[index]['shows'][0]['position']['x'] = \
                        new_pos_x
                    set_complete = False
                    continue

            if "occluder_wall_" in scene.objects[index]['id'] \
                    and not set_complete:

                # if gap and vp_gap make vp_gap a minimal check on the
                # occluder
                if vp_gap is not None:
                    wall_x = \
                        scene.objects[index]['debug']['dimensions']['x'] / 2

                    # if smaller than viewport_gap, then move it to
                    # viewport_gap
                    if scene.objects[index]['shows'][0]['position']['x'] < \
                       new_obj[1]['shows'][0]['position']['x']:
                        if scene.objects[index]['shows'][0]['position']['x'] -\
                                wall_x < (-view_edge_x + vp_gap):
                            scene.objects[index]['shows'][0]['position']['x']\
                                = -(view_edge_x) + wall_x + vp_gap
                    else:
                        if scene.objects[index]['shows'][0]['position']['x']\
                                + wall_x > (view_edge_x - vp_gap):
                            scene.objects[index]['shows'][0]['position']['x'] \
                                = view_edge_x - wall_x - vp_gap

                prev_wall_dim_x = \
                    scene.objects[index]['debug']['dimensions']['x'] / 2
                prev_wall_x = scene.objects[index]['shows'][0]['position']['x']

            if "occluder_pole_" in scene.objects[index]['id'] \
                    and not set_complete:

                if prev_wall_x > 0:
                    new_pos_x = prev_wall_x - prev_wall_dim_x - \
                        (scene.objects[index]['debug']
                         ['dimensions']['x'] / 2)
                    new_pole_x = \
                        scene.objects[index]['shows'][0]['position']['x'] + \
                        (prev_wall_x + new_pos_x)
                else:
                    new_pos_x = prev_wall_x + prev_wall_dim_x + \
                        (scene.objects[index]['debug']
                         ['dimensions']['x'] / 2)
                    new_pole_x = \
                        scene.objects[index]['shows'][0]['position']['x'] - \
                        (prev_wall_x - new_pos_x)

                if sideways:
                    scene.objects[index]['shows'][0]['position']['x'] = \
                        new_pole_x
                else:
                    scene.objects[index]['shows'][0]['position']['x'] = \
                        prev_wall_x

                set_complete = True

        if prev_wall_x is not None:
            if prev_wall_x > new_obj[0]['shows'][0]['position']['x']:
                new_pos_x = prev_wall_x - prev_wall_dim_x - gap - \
                    (new_obj[0]['debug']['dimensions']['x'] / 2)
                new_pole_x = new_obj[1]['shows'][0]['position']['x'] + \
                    (new_obj[0]['shows'][0]['position']['x'] + new_pos_x)
            else:
                new_pos_x = prev_wall_x + prev_wall_dim_x + gap + \
                    (new_obj[0]['debug']['dimensions']['x'] / 2)
                new_pole_x = new_obj[1]['shows'][0]['position']['x'] - \
                    (new_obj[0]['shows'][0]['position']['x'] - new_pos_x)

            new_obj[0]['shows'][0]['position']['x'] = new_pos_x

            if sideways:
                new_obj[1]['shows'][0]['position']['x'] = new_pole_x
            else:
                new_obj[1]['shows'][0]['position']['x'] = new_pos_x

    # Make view port gap on left/right edges = vp_gap
    if vp_gap is not None and gap is None:
        set_complete = False
        prev_wall_x = None
        prev_wall_dim_x = None
        put_left = False
        for index, key in enumerate(scene.objects):
            if "occluder_wall_" in scene.objects[index]['id'] \
                    and not set_complete:

                prev_wall_dim_x = \
                    scene.objects[index]['debug']['dimensions']['x'] / 2

                if scene.objects[index]['shows'][0]['position']['x'] < 0:
                    # put wall on left view port by `vp_gap`
                    prev_wall_x = -view_edge_x + \
                        prev_wall_dim_x + vp_gap
                    put_left = True
                else:
                    # put wall on right view port by `vp_gap`
                    prev_wall_x = view_edge_x - prev_wall_dim_x - vp_gap
                    put_left = False

                scene.objects[index]['shows'][0]['position']['x'] = prev_wall_x

            if "occluder_pole_" in scene.objects[index]['id'] \
                    and not set_complete:
                if sideways:
                    if put_left:
                        new_pos_x = prev_wall_x - prev_wall_dim_x - \
                            (scene.objects[index]['debug']['dimensions']['y'])
                    else:
                        new_pos_x = prev_wall_x + prev_wall_dim_x + \
                            (scene.objects[index]['debug']['dimensions']['y'])

                    scene.objects[index]['shows'][0]['position']['x'] = \
                        new_pos_x
                else:
                    scene.objects[index]['shows'][0]['position']['x'] = \
                        prev_wall_x
                set_complete = True

        # put second wall on right view port by `vp_gap`
        # if prev_wall_x is not None:
        if "occluder_wall_" in new_obj[0]['id']:
            # Wall is always before pole in set?
            prev_wall_dim_x = \
                new_obj[0]['debug']['dimensions']['x'] / 2

            if not put_left:
                prev_wall_x = -view_edge_x + prev_wall_dim_x + vp_gap
            else:
                prev_wall_x = view_edge_x - prev_wall_dim_x - vp_gap

            new_obj[0]['shows'][0]['position']['x'] = prev_wall_x
        if "occluder_pole_" in new_obj[1]['id']:
            if sideways:
                if not put_left:
                    new_pos_x = prev_wall_x - prev_wall_dim_x - \
                        (new_obj[1]['debug']['dimensions']['y'])
                else:
                    new_pos_x = prev_wall_x + prev_wall_dim_x + \
                        (new_obj[1]['debug']['dimensions']['y'])

                new_obj[1]['shows'][0]['position']['x'] = new_pos_x

            else:
                new_obj[1]['shows'][0]['position']['x'] = \
                    new_obj[0]['shows'][0]['position']['x']

    if not sideways:
        scene, new_obj = _occluder_min_viewport_validation(scene, new_obj)

    return scene, new_obj


def _occluder_min_viewport_validation(scene, new_obj):
    """
    Check for minimum separation between occluder and viewport
    Move it over if separation isn't larger than
    OCCLUDER_MIN_VIEWPORT_GAP. Can happen with larger random
    size occluders and gaps.
    """

    view_edge_x = retrieve_off_screen_position_x(
        scene.performer_start.position.x)

    move_occ = False
    move_occ_sign = -1

    for index, key in enumerate(scene.objects):
        if "occluder_wall_" in scene.objects[index]['id']:
            # Wall is always before pole in set?
            pos_x = scene.objects[index]['shows'][0]['position']['x']
            dim_x = scene.objects[index]['debug']['dimensions']['x'] / 2
            if pos_x - dim_x < \
                    -view_edge_x + OCCLUDER_MIN_VIEWPORT_GAP:
                move_occ = True
                move_occ_sign = 1

            if pos_x + dim_x > \
                    view_edge_x - OCCLUDER_MIN_VIEWPORT_GAP:
                move_occ = True

    pos_x = new_obj[0]['shows'][0]['position']['x']
    dim_x = new_obj[0]['debug']['dimensions']['x'] / 2
    if pos_x - dim_x < \
            -view_edge_x + OCCLUDER_MIN_VIEWPORT_GAP:
        move_occ = True
        move_occ_sign = 1

    if pos_x + dim_x > \
            view_edge_x - OCCLUDER_MIN_VIEWPORT_GAP:
        move_occ = True

    if move_occ:
        prev_edge = None

        for index, key in enumerate(scene.objects):
            if "occluder_wall_" in scene.objects[index]['id']:
                pos_x = scene.objects[index]['shows'][0]['position']['x']
                dim_x = scene.objects[index]['debug']['dimensions']['x'] / 2
                if move_occ_sign > 0:
                    if prev_edge is None:
                        prev_edge = pos_x - dim_x
                    else:
                        if (pos_x - dim_x) < prev_edge:
                            prev_edge = pos_x - dim_x
                else:
                    if prev_edge is None:
                        prev_edge = pos_x + dim_x
                    else:
                        if (pos_x + dim_x) > prev_edge:
                            prev_edge = pos_x + dim_x

        pos_x = new_obj[0]['shows'][0]['position']['x']
        dim_x = new_obj[0]['debug']['dimensions']['x'] / 2
        if move_occ_sign > 0:
            if prev_edge is None:
                prev_edge = pos_x - dim_x
            else:
                if (pos_x - dim_x) < prev_edge:
                    prev_edge = pos_x - dim_x
        else:
            if prev_edge is None:
                prev_edge = pos_x + dim_x
            else:
                if (pos_x + dim_x) > prev_edge:
                    prev_edge = pos_x + dim_x

        move_delta = (abs(prev_edge) - view_edge_x) + \
            OCCLUDER_MIN_VIEWPORT_GAP

        for index, key in enumerate(scene.objects):
            if "occluder_wall_" in scene.objects[index]['id'] or \
                    "occluder_pole_" in scene.objects[index]['id']:
                scene.objects[index]['shows'][0]['position']['x'] += \
                    move_delta * move_occ_sign

        new_obj[0]['shows'][0]['position']['x'] += move_delta * move_occ_sign
        new_obj[1]['shows'][0]['position']['x'] += move_delta * move_occ_sign

    return scene, new_obj
