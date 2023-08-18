import copy
import math
from enum import Enum, auto
from typing import Dict, List

from .definitions import ObjectDefinition
from .geometry import create_bounds, move_to_location
from .materials import MaterialTuple
from .objects import SceneObject
from .structures import finalize_structural_object

DEVICE_MATERIAL = MaterialTuple('Custom/Materials/Grey', ['grey'])
HELD = 'held'
RELEASED = 'released'
THROWING_DEVICE_TUBE_SIZE_MULTIPLIER = 1.5
TUBE_SIZE_MULTIPLIER = 1.25

PLACER_ACTIVE_STATUS = ['active']
PLACER_EXT_AMT = 0.25
PLACER_INACTIVE_STATUS = ['inactive']
PLACER_HEIGHT_BUFFER = 0.005
PLACER_MOVE_AMOUNT = 0.25
PLACER_SCALE_MAX = 0.25
PLACER_SCALE_MIN = 0.05
PLACER_SIZE_MULT = 0.2
PLACER_WAIT_STEP = 5
MOVE_OBJ_OFFSET = 1.5


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

OBJECT_MOVEMENT_TEMPLATE = {
    'stepBegin': 0,
    'stepEnd': 0,
    'vector': {
        'x': 0,
        'y': 0,
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
    'rollable_5', 'rollable_6', 'rollable_7', 'rollable_8',
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
    instance: SceneObject,
    move_distance: float,
    activation_step: int,
    is_placer: bool = False,
    deactivation_step: int = None,
    is_pickup_obj: bool = False
) -> int:
    """Add the placer/placed object movement of the given Y distance starting
    at the given activation step to the given object instance."""

    if is_pickup_obj:
        instance['moves'] = [copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE)]
        instance['moves'][0]['vector']['y'] = PLACER_MOVE_AMOUNT
    else:
        instance['moves'] = [copy.deepcopy(PLACER_MOVEMENT_TEMPLATE)]

    # Calculate the Y distance in steps. If it doesn't divide evenly, round
    # DOWN to nearest int (the placed object will fall the rest of the way).
    # Subtract 1 because the step range is inclusive.
    total_steps = math.floor(move_distance / PLACER_MOVE_AMOUNT) - 1

    stop_step = activation_step + total_steps

    if deactivation_step is None or deactivation_step < stop_step:
        deactivation_step = stop_step + 1 + PLACER_WAIT_STEP

    # Move the object the given distance across the corresponding steps.
    if is_pickup_obj:
        instance['moves'][0]['stepBegin'] = deactivation_step + \
            PLACER_WAIT_STEP
        instance['moves'][0]['stepEnd'] = (
            instance['moves'][0]['stepBegin'] + total_steps
        )
    else:
        instance['moves'][0]['stepBegin'] = activation_step
        instance['moves'][0]['stepEnd'] = stop_step

    # If the moving object is the placer, make it move again afterward in the
    # opposite direction.
    if is_placer:
        instance['moves'].append(copy.deepcopy(PLACER_MOVEMENT_TEMPLATE))
        instance['moves'][1]['vector']['y'] *= -1
        instance['moves'][1]['stepBegin'] = (
            deactivation_step + PLACER_WAIT_STEP
        )
        instance['moves'][1]['stepEnd'] = (
            instance['moves'][1]['stepBegin'] + total_steps
        )
    return deactivation_step


def _set_placer_or_placed_object_shellgame_movement(
    instance: SceneObject,
    move_object_end_position: float,
    activation_step: int,
    is_placer: bool = False,
    move_distance: int = None,
    move_object_y: float = None,
    move_object_z: float = None
) -> int:
    """Add the placer/placed object shellgame movement starting
    at the given activation step to the given object instance."""

    # How high to left the object if move_object_raise
    if move_object_y is not None:
        if move_object_y > 0:
            move_object_raise_height = move_object_y \
                if move_object_y is not None \
                else MOVE_OBJ_OFFSET
        else:
            move_object_raise_height = 0
    else:
        move_object_raise_height = 0

    # How far down the Z-axis the object moves
    offset_step_z = move_object_z if move_object_z is not None \
        else MOVE_OBJ_OFFSET

    move_distance_x = abs(
        instance['shows'][0]['position']['x'] - move_object_end_position)

    move_distance_y = move_object_raise_height

    direction_x = 1 if instance['shows'][0]['position']['x'] < \
        move_object_end_position else -1

    # Calculate the distances in steps. If it doesn't divide evenly, round
    # DOWN to nearest int.
    total_steps_y = math.floor(move_distance_y / PLACER_MOVE_AMOUNT)
    total_steps_x = math.floor(move_distance_x / PLACER_MOVE_AMOUNT)
    total_steps_z = math.floor(offset_step_z / PLACER_MOVE_AMOUNT)
    # Steps for the placer to move down at the start.
    # Subtract 1 because the step range is inclusive.
    total_steps_placer_y = math.floor(move_distance / PLACER_MOVE_AMOUNT) - 1
    # The first movement after the placer activates must add the wait step.
    must_wait = True
    # Backwards compatibility: use only half the wait step to activate or
    # deactivate the placer.
    half_wait_step = math.floor(PLACER_WAIT_STEP / 2)

    # Placer Comes Down
    if is_placer:
        instance['moves'] = [copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE)]
        moves_idx = len(instance['moves']) - 1
        instance['materials'] = ['Custom/Materials/Cyan']
        instance['moves'][moves_idx]['stepBegin'] = activation_step
        instance['moves'][moves_idx]['stepEnd'] = \
            instance['moves'][moves_idx]['stepBegin'] + total_steps_placer_y
        instance['moves'][moves_idx]['vector']['y'] = -PLACER_MOVE_AMOUNT

        # Placer is now active - magenta
        chg_mat_idx = len(instance['changeMaterials']) - 1
        instance['changeMaterials'][chg_mat_idx]['materials'] = [
            'Custom/Materials/Magenta']
        instance['changeMaterials'][chg_mat_idx]['stepBegin'] = \
            instance['moves'][moves_idx]['stepEnd'] + \
            half_wait_step
        instance['states'] = [PLACER_INACTIVE_STATUS] * \
            instance['changeMaterials'][chg_mat_idx]['stepBegin']

    # move the object up if move_object_y
    if move_object_raise_height > 0:
        if instance.get('moves') is None:
            instance['moves'] = [copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE)]
            moves_idx = len(instance['moves']) - 1
            instance['moves'][moves_idx]['stepBegin'] = \
                activation_step + total_steps_placer_y + PLACER_WAIT_STEP
            instance['moves'][moves_idx]['stepEnd'] = \
                instance['moves'][moves_idx]['stepBegin'] + \
                total_steps_y - 1
            instance['moves'][moves_idx]['vector']['y'] = PLACER_MOVE_AMOUNT
        else:
            instance['moves'].append(
                copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE))
            moves_idx = len(instance['moves']) - 1
            instance['moves'][moves_idx]['stepBegin'] = \
                instance['moves'][moves_idx - 1]['stepEnd'] + \
                PLACER_WAIT_STEP
            instance['moves'][moves_idx]['stepEnd'] = \
                instance['moves'][moves_idx]['stepBegin'] + \
                total_steps_y - 1
            instance['moves'][moves_idx]['vector']['y'] = PLACER_MOVE_AMOUNT
        must_wait = False

    # Move the object forward
    if total_steps_z != 0:
        if instance.get('moves') is None:
            # Object
            instance['moves'] = [copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE)]
            moves_idx = len(instance['moves']) - 1
            instance['moves'][moves_idx]['stepBegin'] = \
                activation_step + total_steps_placer_y + \
                (PLACER_WAIT_STEP if must_wait else 1)
            instance['moves'][moves_idx]['stepEnd'] = \
                instance['moves'][moves_idx]['stepBegin'] + \
                abs(total_steps_z) - 1
            instance['moves'][moves_idx]['vector']['z'] = -PLACER_MOVE_AMOUNT
        else:
            instance['moves'].append(copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE))
            moves_idx = len(instance['moves']) - 1
            instance['moves'][moves_idx]['stepBegin'] = \
                instance['moves'][moves_idx - 1]['stepEnd'] + \
                (PLACER_WAIT_STEP if must_wait else 1)
            instance['moves'][moves_idx]['stepEnd'] = \
                instance['moves'][moves_idx]['stepBegin'] + \
                abs(total_steps_z) - 1
            instance['moves'][moves_idx]['vector']['z'] = -PLACER_MOVE_AMOUNT
        must_wait = False

    # X-Axis Movement
    if instance.get('moves') is None:
        instance['moves'] = [copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE)]
        moves_idx = len(instance['moves']) - 1
        instance['moves'][moves_idx]['stepBegin'] = \
            activation_step + total_steps_placer_y + \
            (PLACER_WAIT_STEP if must_wait else 1)
        instance['moves'][moves_idx]['stepEnd'] = \
            instance['moves'][moves_idx]['stepBegin'] + \
            total_steps_x - 1
        instance['moves'][moves_idx]['vector']['x'] = direction_x * \
            PLACER_MOVE_AMOUNT
    else:
        instance['moves'].append(copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE))
        moves_idx = len(instance['moves']) - 1
        instance['moves'][moves_idx]['stepBegin'] = \
            instance['moves'][moves_idx - 1]['stepEnd'] + \
            (PLACER_WAIT_STEP if must_wait else 1)
        instance['moves'][moves_idx]['stepEnd'] = \
            instance['moves'][moves_idx]['stepBegin'] + \
            total_steps_x - 1
        instance['moves'][moves_idx]['vector']['x'] = direction_x * \
            PLACER_MOVE_AMOUNT

    must_wait = False

    # Move the object backward
    if total_steps_z != 0:
        instance['moves'].append(copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE))
        moves_idx = len(instance['moves']) - 1
        instance['moves'][moves_idx]['stepBegin'] = \
            instance['moves'][moves_idx - 1]['stepEnd'] + 1
        instance['moves'][moves_idx]['stepEnd'] = \
            instance['moves'][moves_idx]['stepBegin'] + abs(total_steps_z) - 1
        instance['moves'][moves_idx]['vector']['z'] = PLACER_MOVE_AMOUNT

    # move the object down
    if move_object_raise_height > 0:
        instance['moves'].append(copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE))
        moves_idx = len(instance['moves']) - 1
        instance['moves'][moves_idx]['stepBegin'] = \
            instance['moves'][moves_idx - 1]['stepEnd'] + 1
        instance['moves'][moves_idx]['stepEnd'] = \
            instance['moves'][moves_idx]['stepBegin'] + total_steps_y - 1
        instance['moves'][moves_idx]['vector']['y'] = -PLACER_MOVE_AMOUNT

    deactivation_step = instance['moves'][moves_idx]['stepEnd'] + \
        half_wait_step

    # Placer is now inactive - cyan / move the placer back up
    if is_placer:
        instance['changeMaterials'].append({
            'stepBegin': (
                instance['moves'][moves_idx]['stepEnd'] + half_wait_step
            ),
            'materials': ['Custom/Materials/Cyan']
        })

        instance['states'] += [PLACER_ACTIVE_STATUS] * \
            (instance['moves'][moves_idx]['stepEnd'] + half_wait_step -
             instance['changeMaterials'][chg_mat_idx]['stepBegin'])

        instance['moves'].append(copy.deepcopy(OBJECT_MOVEMENT_TEMPLATE))
        moves_idx = len(instance['moves']) - 1
        instance['moves'][moves_idx]['stepBegin'] = \
            instance['moves'][moves_idx - 1]['stepEnd'] + PLACER_WAIT_STEP
        instance['moves'][moves_idx]['stepEnd'] =  \
            instance['moves'][moves_idx]['stepBegin'] + total_steps_placer_y
        instance['moves'][moves_idx]['vector']['y'] = PLACER_MOVE_AMOUNT

        instance['states'] += [PLACER_INACTIVE_STATUS] * \
            (instance['moves'][moves_idx]['stepEnd'] -
             instance['moves'][moves_idx]['stepBegin'])

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
) -> SceneObject:
    """Create and return an instance of a dropping device (tube) to drop the
    object with the given dimensions. The device will always face down."""
    device = SceneObject(copy.deepcopy(DEVICE_TEMPLATE))
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
    deactivation_step: int = None,
    is_pickup_obj: bool = False,
    is_move_obj: bool = False,
    move_object_end_position: float = None,
    move_object_y: float = None,
    move_object_z: float = None,
) -> List[ObjectDefinition]:
    """Create and return an instance of a placer (cylinder) descending from the
    ceiling at the given max height on the given activation step to place an
    object with the given position and dimensions at the given end height.

    NOTE: Call place_object, pickup_object or move_object BEFORE this function!

    - placed_object_position: Placed object's position (probably in the air).
    - placed_object_dimensions: Placed object's dimensions.
    - placed_object_offset_y: Placed object's positionY, indicating whether its
                              Y position is its bottom or center.
    - activation_step: Step on which placer should begin downward movement.
    - end_height: Height at which placed object's bottom should stop.
                  Not used if is_pickup_obj or is_move_obj.
    - max_height: Height of room's ceiling.
    - id_modifier: String to append to placer's ID. Default: none
    - last_step: Scene's last step, used to record inactive state.
    - placed_object_placer_offset_y: Placed object's placerOffsetY.
    - deactivation_step: Step on which held object should be released.
                         Default: At end of object's downward movement
    - is_pickup_obj: If object is being pickuped by the placer
        Default: False
    - is_move_obj: If object is being moved by the placer
        Default: False
    - move_object_end_position: End location of the moved object
    - move_object_y: The placer will raise the object by this value
        during the move object event.
        Default: 0
    - move_object_z: The placer will move the object this distance along
        the z-axis, slide along the x-axis and move back.
        Default: 1.5
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

    # Calculate the Y distance between the object and the end height.
    if is_pickup_obj or is_move_obj:
        move_distance = math.ceil(
            (max_height - object_top - PLACER_EXT_AMT) / PLACER_MOVE_AMOUNT
        ) * PLACER_MOVE_AMOUNT
        placer['shows'][0]['scale']['y'] = max_height / 2.0
        # Ensure the placer always starts slightly extruded from the ceiling.
        placer['shows'][0]['position']['y'] = (
            object_top + move_distance + placer['shows'][0]['scale']['y']
        )
    else:
        move_distance = object_bottom - end_height
        # Set placer Y scale to go from max height to end height.
        placer['shows'][0]['scale']['y'] = ((max_height - end_height) / 2.0)
        # Ensure the placer always starts slightly extruded from the ceiling.
        placer['shows'][0]['position']['y'] = (
            object_top + placer['shows'][0]['scale']['y']
        )

    # Set placer position after setting scale.
    placer['shows'][0]['position']['x'] = placed_object_position['x']
    placer['shows'][0]['position']['z'] = placed_object_position['z']

    # Set the scripted downward and upward movement on the placer.
    if is_move_obj:
        deactivation_step = _set_placer_or_placed_object_shellgame_movement(
            placer,
            move_object_end_position=move_object_end_position,
            activation_step=activation_step,
            is_placer=True,
            move_distance=move_distance,
            move_object_y=move_object_y,
            move_object_z=move_object_z,
        )

    else:
        deactivation_step = _set_placer_or_placed_object_movement(
            placer,
            move_distance,
            activation_step,
            is_placer=True,
            deactivation_step=deactivation_step,
            # Intentionally set to false, even if is_pickup_object=True
            is_pickup_obj=False
        )

    # The placer changes colors and must record its states.
    if is_pickup_obj:
        placer['materials'] = ['Custom/Materials/Cyan']
        placer['changeMaterials'][0]['materials'] = [
            'Custom/Materials/Magenta']
        placer['changeMaterials'][0]['stepBegin'] = deactivation_step

        placer['states'] = (
            ([PLACER_INACTIVE_STATUS] * (deactivation_step - 1)) +
            ([PLACER_ACTIVE_STATUS] * (
                (last_step - deactivation_step) if last_step else 1
            ))
        )
    elif is_move_obj:
        # changeMatertials/States is handled inside
        # _set_placer_or_placed_object_shellgame_movement
        pass
    else:
        placer['changeMaterials'][0]['stepBegin'] = deactivation_step
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
) -> SceneObject:
    """Create and return an instance of a throwing device (tube) to throw the
    object with the given dimensions. The device will always face left by
    default, but can also face right, forward, or backward."""
    device = SceneObject(copy.deepcopy(DEVICE_TEMPLATE))
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
        instance: SceneObject) -> float:
    """For cylinder shaped projectiles in droppers and throwers,
    rotate 90 degrees along x-axis."""
    x_rot = 0
    if (instance['type'] in CYLINDRICAL_SHAPES):
        x_rot = 90

    return x_rot


def drop_object(
    instance: SceneObject,
    dropping_device: SceneObject,
    dropping_step: int,
    rotation_y: int = 0
) -> SceneObject:
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
    instance: SceneObject,
    activation_step: int,
    start_height: float = None,
    end_height: float = 0,
    deactivation_step: int = None
) -> SceneObject:
    """Modify and return the given object instance so its top is positioned at
    the given height, will move downward with a placer (instantiated later) at
    the given step like they're attached together, and is then placed when its
    bottom is at the given height.

    NOTE: Call create_placer AFTER this function!

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
    # Ensure the object will be placed at exactly the end height, so it does
    # not bounce after being placed. This may mean lowering the object's
    # starting height a little.
    if not round(move_distance / PLACER_MOVE_AMOUNT, 4).is_integer():
        move_distance = (
            math.floor((object_bottom - end_height) / PLACER_MOVE_AMOUNT) *
            PLACER_MOVE_AMOUNT
        )
        object_bottom = move_distance + end_height
        instance['shows'][0]['position']['y'] = (
            object_bottom + instance['debug']['positionY']
        )
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


def move_object(
    instance: SceneObject,
    move_object_end_position: float,
    activation_step: int,
    room_height: float,
    move_object_y: float = None,
    move_object_z: float = None,
) -> SceneObject:
    """Modify and return the given object instance so it's moved from its
    current position to the given position via "shell game" movement.
    Assumes there will always be movement on the X axis.

    NOTE: Call create_placer AFTER this function!

    - instance: Instantiated object to place.
    - move_object_end_position: End X position of object instance.
    - activation_step: Step on which placer will begin downward movement.
    - room_height: Height of the room.
    - move_object_y: The placer will raise the object by this value
        during the move object event.
        Default: 0
    - move_object_z: The object will be moved this distance along the z-axis,
        slide along the x-axis and move back.
        Default: 1.5
    """
    object_top = (
        instance['shows'][0]['position']['y'] +
        instance['debug']['dimensions']['y'] -
        instance['debug'].get('positionY', 0)
    )
    move_distance = math.ceil(
        (room_height - object_top - PLACER_EXT_AMT) / PLACER_MOVE_AMOUNT
    ) * PLACER_MOVE_AMOUNT

    # Set the scripted sideways movement on the object.
    deactivation_step = _set_placer_or_placed_object_shellgame_movement(
        instance,
        move_object_end_position=move_object_end_position,
        activation_step=activation_step,
        is_placer=False,
        move_distance=move_distance,
        move_object_y=move_object_y,
        move_object_z=move_object_z
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
    # Wait till after pause to toggle physics
    instance['togglePhysics'] = [{
        'stepBegin': deactivation_step
    }]

    return instance


def pickup_object(
    instance: SceneObject,
    activation_step: int,
    room_height: float,
    start_height: float = 0,
    deactivation_step: int = None
) -> SceneObject:
    """Modify and return the given object instance so its bottom is positioned
    at the top of the object height, will move upward with a placer
    (instantiated later) at the given step like they're attached together,
    and is then stops when its top is at the ceiling height.

    NOTE: Call create_placer AFTER this function!

    - instance: Instantiated object to place.
    - activation_step: Step on which object should begin upward movement.
    - start_height: Y coordinate at which top of object should be positioned.
                    If none, just use given instance's Y position.
    - end_height: Y coordinate at which top of object reaches the ceiling.
                  Default: 0
    - deactivation_step: Step on which held object should be released.
                         Default: At end of object's downward movement
    """
    # Change the object's Y position so its bottom is at the given start
    # height.
    instance['shows'][0]['position']['y'] = (
        start_height + instance['debug']['positionY']
    )

    object_top = (
        instance['shows'][0]['position']['y'] +
        instance['debug']['dimensions']['y'] -
        instance['debug'].get('positionY', 0)
    )
    move_distance = math.ceil(
        (room_height - object_top - PLACER_EXT_AMT) / PLACER_MOVE_AMOUNT
    ) * PLACER_MOVE_AMOUNT

    # Set the scripted upward movement on the object.
    deactivation_step = _set_placer_or_placed_object_movement(
        instance,
        move_distance,
        activation_step,
        deactivation_step=deactivation_step,
        is_pickup_obj=True
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
    instance['kinematic'] = False
    # ...and then move's upward, so enable gravity physics.
    instance['togglePhysics'] = [{
        'stepBegin': activation_step
    }]
    return instance


def throw_object(
    instance: SceneObject,
    throwing_device: SceneObject,
    throwing_force: int,
    throwing_step: int,
    position_x_modifier: float = 0,
    position_y_modifier: float = 0,
    position_z_modifier: float = 0,
    rotation_y: int = 0,
    rotation_z: int = 0,
    impulse: bool = True
) -> SceneObject:
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
