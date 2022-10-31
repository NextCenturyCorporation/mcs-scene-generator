import copy
import math
from enum import Enum, auto
from typing import Any, Dict, List

from .definitions import ObjectDefinition
from .geometry import create_bounds, move_to_location
from .materials import MaterialTuple
from .structures import finalize_structural_object

DEVICE_MATERIAL = MaterialTuple('Custom/Materials/Grey', ['grey'])
HELD = 'held'
RELEASED = 'released'
THROWING_DEVICE_TUBE_SIZE_MULTIPLIER = 1.5
TUBE_SIZE_MULTIPLIER = 1.25

PLACER_ACTIVE_STATUS = ['active']
PLACER_INACTIVE_STATUS = ['inactive']
PLACER_HEIGHT_BUFFER = 0.005
PLACER_MOVE_AMOUNT = 0.25
PLACER_SCALE_MAX = 0.25
PLACER_SCALE_MIN = 0.05
PLACER_SIZE_MULT = 0.2
PLACER_WAIT_STEP = 5

DEVICE_TEMPLATE = {
    'id': 'device_',
    'type': 'tube_wide',
    'mass': 10,
    'materials': ['Custom/Materials/Grey'],
    'kinematic': True,
    'structure': True,
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
    }],
    'debug': {
        'color': ['grey'],
        'info': []
    }
}

PLACER_MOVEMENT_TEMPLATE = {
    'stepBegin': 0,
    'stepEnd': 0,
    'vector': {
        'x': 0,
        'y': -PLACER_MOVE_AMOUNT,
        'z': 0
    }
}

PLACER_TEMPLATE = {
    'id': 'pole_',
    'type': 'cylinder',
    'mass': 10,
    'materials': ['Custom/Materials/Magenta'],
    'kinematic': True,
    'structure': True,
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
            'x': 0,
            'y': 0,
            'z': 0
        }
    }],
    'moves': [],
    'changeMaterials': [{
        'stepBegin': 0,
        'materials': ['Custom/Materials/Cyan']
    }],
    'debug': {
        'color': ['magenta', 'cyan'],
        'info': [],
        'role': 'structural',
        'shape': ['placer'],
        'size': 'medium'
    }
}

CYLINDRICAL_SHAPES = [
    'cylinder', 'double_cone', 'dumbbell_1', 'dumbbell_2',
    'rollable_1', 'rollable_2', 'rollable_3', 'rollable_4',
    'tie_fighter', 'tube_narrow', 'tube_wide'
]


class MechanismDirection(Enum):
    X_POSITIVE = auto()
    X_NEGATIVE = auto()
    Z_POSITIVE = auto()
    Z_NEGATIVE = auto()


def _calculate_tube_scale(
    dimension: float,
    multiplier: float = TUBE_SIZE_MULTIPLIER
) -> float:
    return round(dimension * multiplier, 2)


def _set_placer_or_placed_object_movement(
    instance: Dict[str, Any],
    move_distance: float,
    activation_step: int,
    is_placer: bool = False,
    deactivation_step: int = None
) -> int:
    """Add the placer/placed object movement of the given Y distance starting
    at the given activation step to the given object instance."""
    instance['moves'] = [copy.deepcopy(PLACER_MOVEMENT_TEMPLATE)]

    # Calculate the Y distance in steps. If it doesn't divide evenly, round
    # DOWN to nearest int (the placed object will fall the rest of the way).
    total_steps = math.floor(move_distance / PLACER_MOVE_AMOUNT)

    # The stepEnd is inclusive, so subtract 1 from the total steps.
    stop_step = activation_step + total_steps - 1
    if deactivation_step is None or deactivation_step < stop_step:
        deactivation_step = stop_step + 1 + PLACER_WAIT_STEP

    # Move the object the given distance across the corresponding steps.
    instance['moves'][0]['stepBegin'] = activation_step
    instance['moves'][0]['stepEnd'] = stop_step

    # If the moving object is the placer, make it rise again afterward.
    if is_placer:
        instance['moves'].append(copy.deepcopy(PLACER_MOVEMENT_TEMPLATE))
        instance['moves'][1]['vector']['y'] *= -1
        # Wait additional time between deactivation and moving upward.
        instance['moves'][1]['stepBegin'] = (
            deactivation_step + PLACER_WAIT_STEP
        )
        instance['moves'][1]['stepEnd'] = (
            instance['moves'][1]['stepBegin'] + total_steps - 1
        )

    return deactivation_step


def create_dropping_device(
    position_x: float,
    position_z: float,
    room_dimensions_y: float,
    object_dimensions: Dict[str, float],
    last_step: int = None,
    dropping_step: int = None,
    id_modifier: str = None,
    is_round: bool = False
) -> Dict[str, Any]:
    """Create and return an instance of a dropping device (tube) to drop the
    object with the given dimensions. The device will always face down."""
    device = copy.deepcopy(DEVICE_TEMPLATE)
    device['id'] = (
        f'dropping_device_{(id_modifier + "_") if id_modifier else ""}'
    )
    tube_scale_length = _calculate_tube_scale(object_dimensions['y'])
    tube_scale_radius = _calculate_tube_scale(
        object_dimensions['x'] if is_round else
        math.hypot(object_dimensions['x'], object_dimensions['z'])
    )
    device['shows'][0]['scale'] = {
        'x': tube_scale_radius,
        'y': tube_scale_length,
        'z': tube_scale_radius
    }
    half_y = (device['shows'][0]['scale']['y'] / 2.0)
    device['shows'][0]['position'] = {
        'x': position_x,
        'y': room_dimensions_y - half_y,
        'z': position_z
    }
    if dropping_step is not None:
        last_step_fallback = dropping_step if last_step is None else last_step
        device['states'] = (
            ([[HELD]] * (dropping_step - 1)) +
            ([[RELEASED]] * (last_step_fallback - dropping_step + 1))
        )
    else:
        device['states'] = ([[HELD]] * (1 if last_step is None else last_step))
    device = finalize_structural_object(
        [device],
        DEVICE_MATERIAL,
        ['dropper', 'device']
    )[0]
    return device


def create_placer(
    placed_object_position: Dict[str, float],
    placed_object_dimensions: Dict[str, float],
    placed_object_offset_y: float,
    activation_step: int,
    end_height: float,
    max_height: float,
    id_modifier: str = None,
    last_step: int = None,
    placed_object_placer_offset_y: float = None,
    deactivation_step: int = None
) -> List[ObjectDefinition]:
    """Create and return an instance of a placer (cylinder) descending from the
    ceiling at the given max height on the given activation step to place an
    object with the given position and dimensions at the given end height.

    - placed_object_position: Placed object's position (probably in the air).
    - placed_object_dimensions: Placed object's dimensions.
    - placed_object_offset_y: Placed object's positionY, indicating whether its
                              Y position is its bottom or center.
    - activation_step: Step on which placer should begin downward movement.
    - end_height: Height at which placed object's bottom should stop.
    - max_height: Height of room's ceiling.
    - id_modifier: String to append to placer's ID. Default: none
    - last_step: Scene's last step, used to record inactive state.
    - placed_object_placer_offset_y: Placed object's placerOffsetY.
    - deactivation_step: Step on which held object should be released.
                         Default: At end of object's downward movement
    """

    object_bottom = placed_object_position['y'] - placed_object_offset_y
    object_top = object_bottom + placed_object_dimensions['y'] - (
        placed_object_placer_offset_y or 0
    )

    placer = copy.deepcopy(PLACER_TEMPLATE)
    placer['id'] = f'placer_{(id_modifier + "_") if id_modifier else ""}'

    # Set placer X/Z scale to be fraction of placed object X/Z dimensions.
    object_scale_x = round(placed_object_dimensions['x'] * PLACER_SIZE_MULT, 2)
    object_scale_z = round(placed_object_dimensions['z'] * PLACER_SIZE_MULT, 2)
    placer_scale = min(
        max([object_scale_x, object_scale_z, PLACER_SCALE_MIN]),
        PLACER_SCALE_MAX
    )
    placer['shows'][0]['scale']['x'] = placer_scale
    placer['shows'][0]['scale']['z'] = placer_scale

    # Set placer Y scale to go from max height to end height.
    placer['shows'][0]['scale']['y'] = ((max_height - end_height) / 2.0)

    # Set placer position after setting scale.
    placer['shows'][0]['position']['x'] = placed_object_position['x']
    placer['shows'][0]['position']['z'] = placed_object_position['z']
    placer['shows'][0]['position']['y'] = (
        object_top + placer['shows'][0]['scale']['y']
    )

    # Calculate the Y distance between the object's bottom and the end height.
    move_distance = object_bottom - end_height

    # Set the scripted downward and upward movement on the placer.
    deactivation_step = _set_placer_or_placed_object_movement(
        placer,
        move_distance,
        activation_step,
        is_placer=True,
        deactivation_step=deactivation_step
    )

    # The placer must change its color once it starts to move upward.
    placer['changeMaterials'][0]['stepBegin'] = deactivation_step

    # The placer must record its states.
    placer['states'] = (
        ([PLACER_ACTIVE_STATUS] * (deactivation_step - 1)) +
        ([PLACER_INACTIVE_STATUS] * (
            (last_step - deactivation_step) if last_step else 1
        ))
    )

    placer = finalize_structural_object([placer], None, ['placer'])[0]
    return placer


def create_throwing_device(
    position_x: float,
    position_y: float,
    position_z: float,
    rotation_y: float,
    rotation_z: float,
    object_dimensions: Dict[str, float],
    last_step: int = None,
    throwing_step: int = None,
    id_modifier: str = None,
    object_rotation_y: float = None,
    is_round: bool = False
) -> Dict[str, Any]:
    """Create and return an instance of a throwing device (tube) to throw the
    object with the given dimensions. The device will always face left by
    default, but can also face right, forward, or backward."""
    device = copy.deepcopy(DEVICE_TEMPLATE)
    device['id'] = (
        f'throwing_device_{(id_modifier + "_") if id_modifier else ""}'
    )
    width_axis = 'x'
    length_axis = 'z'
    if object_rotation_y is not None and object_rotation_y % 180 == 0:
        width_axis = 'z'
        length_axis = 'x'
    tube_scale_length = _calculate_tube_scale(object_dimensions[length_axis])
    tube_scale_radius = _calculate_tube_scale(
        object_dimensions[width_axis] if is_round else
        math.hypot(object_dimensions[width_axis], object_dimensions['y'])
    )
    device['shows'][0]['scale'] = {
        'x': tube_scale_radius,
        'y': tube_scale_length,
        'z': tube_scale_radius
    }
    device['shows'][0]['rotation'] = {
        'x': 0,
        'y': rotation_y,
        # Add 90 to the Z rotation because the tube must start horizontal.
        'z': 90 + rotation_z
    }
    device['shows'][0]['position'] = {
        'x': position_x,
        # Device should not be positioned in or below the floor.
        'y': max(position_y, tube_scale_radius / 2.0),
        'z': position_z
    }
    if throwing_step is not None:
        last_step_fallback = throwing_step if last_step is None else last_step
        device['states'] = (
            ([[HELD]] * (throwing_step - 1)) +
            ([[RELEASED]] * (last_step_fallback - throwing_step + 1))
        )
    else:
        device['states'] = ([[HELD]] * (1 if last_step is None else last_step))
    return finalize_structural_object(
        [device],
        DEVICE_MATERIAL,
        ['thrower', 'device'],
        override_scale={
            # Switch the X and Y scale since the device is mostly horizontal.
            'x': device['shows'][0]['scale']['y'],
            'y': device['shows'][0]['scale']['x'],
            'z': device['shows'][0]['scale']['z'],
        }
    )[0]


def rotate_x_for_cylinders_in_droppers_throwers(
        instance: Dict[str, Any]) -> float:
    """For cylinder shaped projectiles in droppers and throwers,
    rotate 90 degrees along x-axis."""
    x_rot = 0
    if(instance['type'] in CYLINDRICAL_SHAPES):
        x_rot = 90

    return x_rot


def drop_object(
    instance: Dict[str, Any],
    dropping_device: Dict[str, Any],
    dropping_step: int,
    rotation_y: int = 0
) -> Dict[str, Any]:
    """Modify and return the given object instance that will be dropped by the
    given device at the given step."""
    # Assign the object's location using its chosen corner.

    x_rot = rotate_x_for_cylinders_in_droppers_throwers(instance)

    location = {
        'position': dropping_device['shows'][0]['position'].copy(),
        'rotation': {'x': x_rot, 'y': rotation_y, 'z': 0}
    }
    move_to_location(instance, location)
    # The object starts immobile...
    instance['kinematic'] = True
    # ...and then it falls.
    instance['togglePhysics'] = [{
        'stepBegin': dropping_step
    }]
    return instance


def place_object(
    instance: Dict[str, Any],
    activation_step: int,
    start_height: float = None,
    end_height: float = 0,
    deactivation_step: int = None
) -> Dict[str, Any]:
    """Modify and return the given object instance so its top is positioned at
    the given height, will move downward with a placer (instantiated later) at
    the given step like they're attached together, and is then placed when its
    bottom is at the given height.

    - instance: Instantiated object to place.
    - activation_step: Step on which object should begin downward movement.
    - start_height: Y coordinate at which top of object should be positioned.
                    If none, just use given instance's Y position.
    - end_height: Y coordinate at which bottom of object should be placed.
                  Default: 0
    - deactivation_step: Step on which held object should be released.
                         Default: At end of object's downward movement
    """
    # Change the object's Y position so its top is at the given start height.
    if start_height is not None:
        instance['shows'][0]['position']['y'] = (
            start_height - instance['debug']['dimensions']['y'] +
            instance['debug']['positionY'] - PLACER_HEIGHT_BUFFER
        )
    object_bottom = (
        instance['shows'][0]['position']['y'] - instance['debug']['positionY']
    )
    # Calculate the Y distance between the object's bottom and the end height.
    move_distance = object_bottom - end_height
    # Set the scripted downward movement on the object.
    deactivation_step = _set_placer_or_placed_object_movement(
        instance,
        move_distance,
        activation_step,
        deactivation_step=deactivation_step
    )
    # Update the object's bounds.
    instance['shows'][0]['boundingBox'] = create_bounds(
        dimensions=instance['debug']['dimensions'],
        offset=instance['debug'].get('offset'),
        position=instance['shows'][0]['position'],
        rotation=instance['shows'][0]['rotation'],
        standing_y=instance['debug']['positionY']
    )
    # The object starts immobile...
    instance['kinematic'] = True
    # ...and then is placed, so enable gravity physics.
    instance['togglePhysics'] = [{
        'stepBegin': deactivation_step
    }]
    return instance


def throw_object(
    instance: Dict[str, Any],
    throwing_device: Dict[str, Any],
    throwing_force: int,
    throwing_step: int,
    position_x_modifier: float = 0,
    position_y_modifier: float = 0,
    position_z_modifier: float = 0,
    rotation_y: int = 0,
    rotation_z: int = 0,
    impulse: bool = True
) -> Dict[str, Any]:
    """Modify and return the given object instance that will be thrown by the
    given device with the given force at the given step. The rotation_y should
    be the rotation needed to turn the object to face toward the left."""
    # Assign the object's location using its throwing device.

    x_rot = rotate_x_for_cylinders_in_droppers_throwers(instance)

    location = {
        'position': {
            'x': (
                throwing_device['shows'][0]['position']['x'] +
                position_x_modifier
            ),
            'y': (
                throwing_device['shows'][0]['position']['y'] +
                position_y_modifier -
                (instance['debug']['dimensions']['y'] / 2.0) +
                instance['debug']['positionY']
            ),
            'z': (
                throwing_device['shows'][0]['position']['z'] +
                position_z_modifier
            )
        },
        'rotation': {
            'x': x_rot,
            'y': throwing_device['shows'][0]['rotation']['y'] + rotation_y,
            'z': rotation_z
        }
    }
    move_to_location(instance, location)
    original_rotation = instance['debug'].get('originalRotation', {})
    swap_axes = (original_rotation.get('y', 0) % 180 == 90)
    # Add the force to the object.
    instance['forces'] = [{
        'impulse': impulse,
        'relative': True,
        'stepBegin': throwing_step,
        'stepEnd': throwing_step,
        'vector': {
            'x': 0 if swap_axes else throwing_force,
            'y': 0,
            'z': throwing_force if swap_axes else 0
        }
    }]
    return instance
