import math
import random
from typing import Tuple

from .geometry import occluder_x_to_object_x

MAX_Z = 10
MIN_Z = -4.5
MAX_TARGET_Y = 6.5
MIN_TARGET_Z = 1.6
# In Evals 3 and 4, this was 4.4, but in Eval 5 we made the room deeper, and
# the "deep" movement sometimes starts at this depth.
MAX_TARGET_Z = 5.6
MAX_TARGET_Z_STRAIGHT_ACROSS = 4.4

STEP_Z = 0.05
MIN_OFFSCREEN_X = 0.5
STEP_OFFSCREEN_X = 0.03 / STEP_Z
MIN_OFFSCREEN_Y = 2.5
STEP_OFFSCREEN_Y = 0.02 / STEP_Z

# See generator/movements.py
NON_COLLISION_SPEEDS = list(range(650, 710, 10))
NON_COLLISION_ANGLED_SPEEDS = list(range(600, 850, 25))
COLLISION_SPEEDS = list(range(800, 910, 10))
TOSS_SPEEDS = [300, 350, 400, 450]


def choose_position_z(
    min_z: float = MIN_TARGET_Z,
    max_z: float = MAX_TARGET_Z
) -> float:
    """Return a pseudo-random Z position for a target/non-target object."""
    max_steps = int(round((max_z - min_z) / STEP_Z))
    return min_z + (random.randint(0, max_steps) * STEP_Z)


def retrieve_off_screen_position_x(position_z: float) -> float:
    """Return the off-screen object X position for the given Z position."""
    result = MIN_OFFSCREEN_X + ((position_z - MIN_Z) * STEP_OFFSCREEN_X)
    return round(result, 4)


def retrieve_off_screen_position_y(position_z: float) -> float:
    """Return the off-screen object Y position for the given Z position."""
    result = MIN_OFFSCREEN_Y + ((position_z - MIN_Z) * STEP_OFFSCREEN_Y)
    return round(result, 4)


def _find_off_screen_position_diagonal(
    start_x: float,
    start_z: float,
    angle: float,
    toward: bool
) -> Tuple[float, float]:

    if angle == 0:
        return -start_x, start_z

    if toward:
        # Begin with a travel distance of start_x (so the X position is 0). End
        # with a travel distance of 2*start_x (so the X position is -start_x).
        # Since the object is moving toward the performer agent, the offscreen
        # X position cannot be greater than -start_x.
        min_x = abs(start_x)
        max_x = 2 * abs(start_x)
    else:
        # Begin with a travel distance of 2*start_x (so the X position is
        # -start_x). End with a travel distance for the back room wall. Since
        # the object is moving away from the performer agent, the offscreen
        # X position must be greater than -start_x.
        min_x = 2 * abs(start_x)
        max_x = retrieve_off_screen_position_x(MAX_Z) + abs(start_x)

    # Loop over each possible X distance in increments of 0.01
    for distance_x in [
        round(i / 100, 2) for i in
        range(int(min_x * 100), int(max_x * 100))
    ]:
        # Calculate the X position.
        possible_x = round(distance_x - abs(start_x), 4)
        # Calculate the Z distance corresponding to the current X distance.
        distance_z = (-1 if toward else 1) * round(
            distance_x * math.sin(math.radians(angle)) /
            math.sin(math.radians(90 - angle)),
            4
        )
        # Calculate the Z position.
        possible_z = round(start_z + distance_z, 2)
        # Identify the offscreen X position at the new Z position.
        required_x = retrieve_off_screen_position_x(possible_z)
        # See if the current X position meets the minimum necessary X position.
        if required_x <= possible_x:
            return possible_x * (-1 if start_x > 0 else 1), possible_z

    return None, None


def find_off_screen_position_diagonal_away(
    start_x: float,
    start_z: float,
    angle: float
) -> Tuple[float, float]:
    """Return the X/Z position at which an object will move offscreen assuming
    that object starts at the given X/Z position and moves at the given angle
    AWAY FROM the performer agent."""

    return _find_off_screen_position_diagonal(start_x, start_z, angle, False)


def find_off_screen_position_diagonal_toward(
    start_x: float,
    start_z: float,
    angle: float
) -> Tuple[float, float]:
    """Return the X/Z position at which an object will move offscreen assuming
    that object starts at the given X/Z position and moves at the given angle
    TOWARD the performer agent."""

    return _find_off_screen_position_diagonal(start_x, start_z, angle, True)


def _find_position_behind_occluder_diagonal(
    occluder_x: float,
    occluder_z: float,
    start_x: float,
    start_z: float,
    angle: float,
    toward: bool
) -> Tuple[float, float]:

    if angle == 0:
        end_x = occluder_x_to_object_x(
            occluder_x,
            occluder_z,
            start_z,
            0,
            -4.5
        )
        return end_x, start_z

    if toward:
        # Begin with a travel distance of 0. End with a travel distance so that
        # the object's Z position is adjacent to the occluder.
        max_z = int(start_z - occluder_z)
    else:
        # Begin with a travel distance of 0. End with a travel distance so that
        # the object's Z position is adjacent to the back room wall.
        max_z = int(MAX_Z - start_z)

    # Loop over each possible Z distance in increments of 0.01
    for distance_z in [round(i / 100, 2) for i in range(0, max_z * 100)]:
        # Calculate the X position corresponding to the current Z distance.
        possible_x = round(start_x + (1 if start_x < 0 else -1) * (
            distance_z * math.sin(math.radians(90 - angle)) /
            math.sin(math.radians(angle))
        ), 4)
        # Calculate the Z position.
        possible_z = round(start_z + (distance_z * (-1 if toward else 1)), 2)
        # Identify the required X position at the current Z position for the
        # object to be successfully hidden behind the occluder.
        required_x = occluder_x_to_object_x(
            occluder_x,
            occluder_z,
            possible_z,
            0,
            -4.5
        )
        # See if the current X position is approx. the necessary X position.
        if math.isclose(required_x, possible_x, rel_tol=0.1, abs_tol=0.1):
            return possible_x, round(possible_z, 2)

    return None, None


def find_position_behind_occluder_diagonal_away(
    occluder_x: float,
    occluder_z: float,
    start_x: float,
    start_z: float,
    angle: float
) -> Tuple[float, float]:
    """Return the X/Z position at which an object will move behind an occluder
    with the given X/Z position assuming that object starts at the given X/Z
    position and moves at the given angle AWAY FROM the performer agent."""

    return _find_position_behind_occluder_diagonal(
        occluder_x,
        occluder_z,
        start_x,
        start_z,
        angle,
        False
    )


def find_position_behind_occluder_diagonal_toward(
    occluder_x: float,
    occluder_z: float,
    start_x: float,
    start_z: float,
    angle: float
) -> Tuple[float, float]:
    """Return the X/Z position at which an object will move behind an occluder
    with the given X/Z position assuming that object starts at the given X/Z
    position and moves at the given angle TOWARD the performer agent."""

    return _find_position_behind_occluder_diagonal(
        occluder_x,
        occluder_z,
        start_x,
        start_z,
        angle,
        True
    )
