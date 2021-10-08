import copy
from enum import Enum, auto
from typing import Any, Dict

from .definitions import ObjectDefinition
from .materials import MaterialTuple
from .structures import finalize_structural_object
from .util import instantiate_object

DEVICE_MATERIAL = MaterialTuple('Custom/Materials/Grey', ['grey'])
HELD = 'held'
RELEASED = 'released'
TUBE_SIZE_MULTIPLIER = 1.25

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

DROPPING_DEVICE_Y_SCALE_MULTIPLIER = 1.1
THROWING_DEVICE_Y_SCALE_MULTIPLIER = 1.45


class MechanismDirection(Enum):
    X_POSITIVE = auto()
    X_NEGATIVE = auto()
    Z_POSITIVE = auto()
    Z_NEGATIVE = auto()


def _calculate_tube_scale(dimension: float, multiplier: float = 1) -> float:
    return round(dimension * TUBE_SIZE_MULTIPLIER * multiplier, 2)


def create_dropping_device(
    position_x: float,
    position_z: float,
    room_dimensions_y: float,
    object_dimensions: Dict[str, float],
    last_step: int,
    dropping_step: int = None,
    id_modifier: str = None
) -> Dict[str, Any]:
    """Create and return an instance of a dropping device (tube) to drop the
    object with the given dimensions. The device will always face down."""
    device = copy.deepcopy(DEVICE_TEMPLATE)
    device['id'] = (
        f'dropping_device_{(id_modifier + "_") if id_modifier else ""}'
    )
    scale_x = _calculate_tube_scale(object_dimensions['x'])
    scale_y = _calculate_tube_scale(
        object_dimensions['y'],
        DROPPING_DEVICE_Y_SCALE_MULTIPLIER
    )
    scale_z = _calculate_tube_scale(object_dimensions['z'])
    device['shows'][0]['scale'] = {
        'x': max(scale_x, scale_z),
        'y': scale_y,
        'z': max(scale_x, scale_z)
    }
    half_y = (device['shows'][0]['scale']['y'] / 2.0)
    device['shows'][0]['position'] = {
        'x': position_x,
        'y': room_dimensions_y - half_y,
        'z': position_z
    }
    if dropping_step is not None:
        device['states'] = (
            ([[HELD]] * (dropping_step - 1)) +
            ([[RELEASED]] * (last_step - dropping_step + 1))
        )
    else:
        device['states'] = ([[HELD]] * last_step)
    return finalize_structural_object(
        [device],
        DEVICE_MATERIAL,
        ['dropper', 'device']
    )[0]


def create_throwing_device(
    position_x: float,
    position_y: float,
    position_z: float,
    rotation_y: float,
    rotation_z: float,
    object_dimensions: Dict[str, float],
    last_step: int,
    throwing_step: int = None,
    id_modifier: str = None
) -> Dict[str, Any]:
    """Create and return an instance of a throwing device (tube) to throw the
    object with the given dimensions. The device will always face left by
    default, but can also face right, forward, or backward."""
    device = copy.deepcopy(DEVICE_TEMPLATE)
    device['id'] = (
        f'throwing_device_{(id_modifier + "_") if id_modifier else ""}'
    )
    scale_x = _calculate_tube_scale(object_dimensions['x'])
    scale_y = _calculate_tube_scale(
        object_dimensions['y'],
        THROWING_DEVICE_Y_SCALE_MULTIPLIER
    )
    scale_z = _calculate_tube_scale(object_dimensions['z'])
    device['shows'][0]['scale'] = {
        'x': max(scale_x, scale_z),
        'y': scale_y,
        'z': max(scale_x, scale_z)
    }
    device['shows'][0]['rotation'] = {
        'x': 0,
        'y': rotation_y,
        # Add 90 to the Z rotation because the tube must start horizontal.
        'z': 90 + rotation_z
    }
    device['shows'][0]['position'] = {
        'x': position_x,
        'y': position_y,
        'z': position_z
    }
    if throwing_step is not None:
        device['states'] = (
            ([[HELD]] * (throwing_step - 1)) +
            ([[RELEASED]] * (last_step - throwing_step + 1))
        )
    else:
        device['states'] = ([[HELD]] * last_step)
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


def drop_object(
    definition: ObjectDefinition,
    dropping_device: Dict[str, Any],
    dropping_step: int
) -> Dict[str, Any]:
    """Create and return an instance of the given object definition that will
    be dropped by the given device at the given step."""
    # Assign the object's location using its chosen corner.
    location = {
        'position': dropping_device['shows'][0]['position'].copy()
    }
    instance = instantiate_object(definition, location)
    # The object starts immobile...
    instance['kinematic'] = True
    # ...and then it falls.
    instance['togglePhysics'] = [{
        'stepBegin': dropping_step
    }]
    return instance


def throw_object(
    definition: ObjectDefinition,
    throwing_device: Dict[str, Any],
    throwing_force: int,
    throwing_step: int,
    position_x_modifier: float = 0,
    position_y_modifier: float = 0,
    position_z_modifier: float = 0,
    rotation_z: int = 0
) -> Dict[str, Any]:
    """Create and return an instance of the given object definition that will
    be thrown by the given device with the given force at the given step.
    Assume the given object definition will face left by default; if not,
    please adjust the definition's Y rotation before calling this function."""
    # Assign the object's location using its throwing device.
    location = {
        'position': {
            'x': (
                throwing_device['shows'][0]['position']['x'] +
                position_x_modifier
            ),
            'y': (
                throwing_device['shows'][0]['position']['y'] +
                position_y_modifier
            ),
            'z': (
                throwing_device['shows'][0]['position']['z'] +
                position_z_modifier
            )
        },
        'rotation': {
            'x': 0,
            'y': throwing_device['shows'][0]['rotation']['y'],
            'z': rotation_z
        }
    }
    instance = instantiate_object(definition, location)
    # Add the force to the object.
    instance['forces'] = [{
        'relative': True,
        'stepBegin': throwing_step,
        'stepEnd': throwing_step,
        'vector': {
            'x': throwing_force,
            'y': 0,
            'z': 0
        }
    }]
    return instance
