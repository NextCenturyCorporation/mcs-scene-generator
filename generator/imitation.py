import random
from enum import Enum
from typing import Any, Dict, List

from machine_common_sense.config_manager import Vector3d

from generator import MAX_TRIES, Scene, geometry, materials
from generator.agents import (
    AGENT_TYPES,
    add_agent_movement,
    create_agent,
    get_random_agent_settings
)
from generator.base_objects import create_specific_definition_from_base
from generator.instances import instantiate_object
from generator.mechanisms import create_placer
from generator.objects import SceneObject

IMITATION_TASK_CONTAINER_SCALE = 1
IMITATION_TASK_TARGET_SEPARATION = 0.6
IMITATION_AGENT_START_X = 0.3
IMITATION_AGENT_END_X = 0.4
IMITATION_CONTAINER_START_X = 0.9
IMITATION_CONTAINER_SEPARATION = 1

"""
The rotations here work by referencing the world global rotation
and relative clockwise rotations.
Global means that the world rotation in unity will be the exact value.
LEFT_SIDE and RIGHT_SIDE is the relative clockwise from start shift.

LEFT_SIDE:
Start            End
[3]->            [3]
[2] Rotate 45  [2] ↘
[1]->        [1] ↘

RIGHT_SIDE:
End              Start
  ↖ [3]        <-[3]
↖ [2]  Rotate 45 [2]
[1]            <-[1]

GLOBAL:
Start          End
   ↖ [3]        [1] ↗
 ↖ [2] Rotate 45  [2] ↗
[1]                 [3]
"""
IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL = [45, 135, 180, 225, 315]
IMITATION_CONTAINER_TELEPORT_ROTATIONS_LEFT_SIDE = [45, 90, 135, 225, 315]
IMITATION_CONTAINER_TELEPORT_ROTATIONS_RIGHT_SIDE = [45, 135, 225, 270, 315]

IMITATION_CONTAINER_TELEPORT_X_POS_RANGE = [
    (-0.25, 0.85), (-1, 1.5), (-1.5, -0.5), (-2.5, 0), (0, 2.5)]
IMITATION_CONTAINER_TELEPORT_MIN_Z_POS = 1


class ImitationTriggerOrder(str, Enum):
    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"
    LEFT_MIDDLE = "left_middle"
    LEFT_RIGHT = "left_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_RIGHT = "middle_right"
    RIGHT_MIDDLE = "right_middle"
    RIGHT_LEFT = "right_left"


class ImitationKidnapOptions(str, Enum):
    AGENT_ONLY = "agent_only"
    CONTAINERS = "containers"
    PERFORMER = "performer"


def _create_imitation_container(
        position: Vector3d, rotation_y, material) -> SceneObject:

    container_definition = create_specific_definition_from_base(
        type="chest_1",
        color=material[1],
        materials=[material[0]],
        salient_materials=["wood"],
        scale=IMITATION_TASK_CONTAINER_SCALE
    )
    location = {
        'position': vars(position),
        'rotation': {'x': 0, 'y': rotation_y, 'z': 0}
    }
    container = instantiate_object(container_definition, location)
    return container


def get_three_unique_materials():
    container_colors_used = []
    material_list = []
    material_choices = materials.CUSTOM_WOOD_MATERIALS
    for i in range(3):
        for _ in range(MAX_TRIES):
            try_new_color = False
            material = random.choice(material_choices)
            colors = material[1]
            for color in colors:
                if color in container_colors_used:
                    try_new_color = True
                    break
            if try_new_color:
                continue
            for color in colors:
                container_colors_used.append(color)
            material_list.append(material)
            break
    return material_list


def _setup_three_containers_for_imitation_task(
        scene: Scene, containers_on_right_side, color_override) -> List:
    containers = []
    left_container_start_pos_z = \
        1 if containers_on_right_side else -1
    separation_between_containers = IMITATION_CONTAINER_SEPARATION * (
        -1 if containers_on_right_side else 1)
    # Positive to negative z axis, positive is left, negative is right
    container_range = range(left_container_start_pos_z,
                            -left_container_start_pos_z * 2,
                            separation_between_containers)
    three_materials = color_override if color_override else \
        get_three_unique_materials()
    material_index = 0
    for container_index in container_range:
        pos_z = container_index
        rotation_y = -90 if containers_on_right_side else 90
        pos = Vector3d(
            x=(IMITATION_CONTAINER_START_X if
               containers_on_right_side else -IMITATION_CONTAINER_START_X),
            y=0, z=pos_z)
        chest = _create_imitation_container(
            pos, rotation_y, three_materials[material_index])
        scene.objects.append(chest)
        container_index = scene.objects[-1]
        containers.append(container_index)
        material_index += 1
    return containers, separation_between_containers


def _setup_target_and_placer_imitation_task(
        scene: Scene, containers_on_right_side, containers):
    # move target to end of container
    scene.objects.append(scene.objects.pop(0))
    target = scene.objects[-1]
    target['shows'][0]['position']['y'] = \
        scene.room_dimensions.y + target['debug']['dimensions']['y'] * 2
    placer = create_placer(
        target['shows'][0]['position'], target['debug']['dimensions'],
        target['debug']['positionY'], 0, 0, scene.room_dimensions.y
    )
    placer['triggeredBy'] = True
    scene.objects.append(placer)

    target['triggeredBy'] = True
    target['kinematic'] = True
    target['moves'] = [placer['moves'][0]]
    target['togglePhysics'] = [
        {'stepBegin': placer['changeMaterials'][0]['stepBegin']}]
    target['shows'][0]['position']['x'] = \
        containers[0]['shows'][0]['position']['x']
    placer['shows'][0]['position']['x'] = \
        target['shows'][0]['position']['x']

    # position in front of the left containers if containers on left
    # position in front of the right containers if containers on right
    target_separation = IMITATION_TASK_TARGET_SEPARATION
    container_to_put_in_front_of_index = \
        -1 if containers_on_right_side else 0
    target['shows'][0]['position']['z'] = (
        containers[container_to_put_in_front_of_index
                   ]['shows'][0]['position']['z'] - target_separation)
    placer['shows'][0]['position']['z'] = \
        target['shows'][0]['position']['z']
    return target, placer


def _setup_trigger_order_for_imitation_task(trigger_order, containers):
    trigger_order_ids = []
    solo_options = ['left', 'middle', 'right']
    left_options = ['left_middle', 'left_right']
    middle_options = ['middle_left', 'middle_right']
    right_options = ['right_middle', 'right_left']
    containers_to_open_indexes = []
    if trigger_order in solo_options:
        container_index = solo_options.index(trigger_order)
        trigger_order_ids.append(containers[container_index]['id'])
        containers_to_open_indexes.append(container_index)
    elif trigger_order in left_options:
        trigger_order_ids.append(containers[0]['id'])
        container_index = left_options.index(trigger_order)
        trigger_order_ids.append(
            containers[1 if container_index == 0 else 2]['id'])
        containers_to_open_indexes.append(0)
        containers_to_open_indexes.append(1 if container_index == 0 else 2)
    elif trigger_order in middle_options:
        trigger_order_ids.append(containers[1]['id'])
        container_index = middle_options.index(trigger_order)
        trigger_order_ids.append(
            containers[0 if container_index == 0 else 2]['id'])
        containers_to_open_indexes.append(1)
        containers_to_open_indexes.append(0 if container_index == 0 else 2)
    elif trigger_order in right_options:
        trigger_order_ids.append(containers[2]['id'])
        container_index = right_options.index(trigger_order)
        trigger_order_ids.append(
            containers[1 if container_index == 0 else 0]['id'])
        containers_to_open_indexes.append(2)
        containers_to_open_indexes.append(1 if container_index == 0 else 0)
    return trigger_order_ids, containers_to_open_indexes


def _setup_agent_for_imitation_task(
        scene: Scene, containers_on_right_side, containers,
        containers_to_open_indexes, agent_settings_override,
        agent_type_override):
    """
    Agent Setup
    1. Enter in front of starting chest
    2. Walk to chest
    3. Open (if only open one chest then end here and face performer)
    4. Walk to other chest
    5. Rotate to face chest
    6. Open the chest
    7. Face performer
    """
    step_begin_open_first_chest = 18
    step_end_open_first_chest = 28
    open_animation = "TPE_jump"
    turn_left_animation = "TPM_turnL45"
    turn_right_animation = "TPM_turnR45"

    movement_points = []
    number_of_containers = 0
    start_turning_step = None
    rotates = None
    for container_index in containers_to_open_indexes:
        end_point_x = IMITATION_AGENT_END_X if containers_on_right_side else \
            -IMITATION_AGENT_END_X
        end_point_z = containers[container_index]['shows'][0]['position']['z']
        movement_points.append((end_point_x, end_point_z))
        number_of_containers += 1
        if number_of_containers > 1:
            """
            Example of chest on the right:
            Rotate left because the agent walks toward the performer.
            Start
                |     c opened
                |     c
            Agent >   c open this

            Performer
            """
            containers_on_right_side_agent_moving_toward_performer = (
                containers_on_right_side and
                container_index > containers_to_open_indexes[0])
            containers_on_left_side_agent_moving_away_from_performer = (
                not containers_on_right_side and
                container_index > containers_to_open_indexes[0])
            # negative is left turn, positive is right turn
            direction = (
                -1 if
                containers_on_right_side_agent_moving_toward_performer or
                containers_on_left_side_agent_moving_away_from_performer
                else 1)
            is_adjacent_container = (
                container_index == containers_to_open_indexes[0] + 1 or
                container_index == containers_to_open_indexes[0] - 1)
            # for some reason the left side needs one extra step
            extra_step = (
                1 if
                containers_on_left_side_agent_moving_away_from_performer
                else 0)
            # With an origin point of the start container z position,
            # 57 and 82 are the number of steps required to reach the
            # adjacent or far container z position and be centered in
            # front of it
            start_turning_step = 57 + extra_step if \
                is_adjacent_container else 82 + extra_step
            rotation_per_step = 9 * direction
            rotates = {
                "stepBegin": start_turning_step,
                "stepEnd": start_turning_step + 10,
                "vector": {
                    "x": 0,
                    "y": rotation_per_step,
                    "z": 0
                }
            }

    # End position facing the performer
    end_point_x = IMITATION_AGENT_END_X if containers_on_right_side else \
        -IMITATION_AGENT_END_X
    end_point_z = movement_points[-1][1] - 0.15
    movement_points.append((end_point_x, end_point_z))

    # Animations
    actions = []
    # The steps that each container is opened
    open_steps = []
    first_open = {
        'stepBegin': step_begin_open_first_chest,
        'stepEnd': step_end_open_first_chest,
        'isLoopAnimation': False,
        'id': open_animation
    }
    actions.append(first_open)
    open_steps.append(step_begin_open_first_chest)

    # Check if we are opening more than one chest
    # A turning animation is required to face the second chest
    if start_turning_step is not None:
        turn = {
            'stepBegin': start_turning_step,
            'stepEnd': start_turning_step + 10,
            'isLoopAnimation': False,
            'id': (turn_left_animation if rotates['vector']['y'] < 1 else
                   turn_right_animation)
        }
        second_open = {
            'stepBegin': start_turning_step + 10,
            'stepEnd': start_turning_step + 20,
            'isLoopAnimation': False,
            'id': open_animation
        }
        actions.append(turn)
        actions.append(second_open)
        open_steps.append(start_turning_step + 10)

    # Config the agent in front of the first chest to open
    start_position = Vector3d(
        x=(-IMITATION_AGENT_START_X if
            containers_on_right_side else
            IMITATION_AGENT_START_X), y=0,
        z=(containers[containers_to_open_indexes[0]]
           ['shows'][0]['position']['z']))
    rotation_y = 90 if containers_on_right_side else -90

    type = agent_type_override if agent_type_override else \
        random.choice(AGENT_TYPES)
    settings = agent_settings_override if agent_settings_override else \
        get_random_agent_settings(type)
    agent = create_agent(
        type, start_position.x, start_position.z, rotation_y, settings)
    agent['actions'] = actions

    if rotates:
        agent['rotates'] = [rotates]
    add_agent_movement(agent=agent, step_begin=1, points=movement_points)

    # Open containers with animation timing
    i = 0
    for container_index in containers_to_open_indexes:
        containers[container_index]['openClose'] = [{
            'step': open_steps[i] + 4,
            'open': True
        }]
        i += 1

    scene.objects.append(agent)
    return agent, open_steps


def _kidnap_performer_for_imitation_task(
        scene: Scene, kidnap_option, containers_on_right_side, target, placer,
        agent, last_open_step, containers, containers_to_open_indexes,
        separation_between_containers, containers_teleport_rotation=None,
        relative_rotation=True):
    kidnap_step = last_open_step + placer['moves'][-1]['stepEnd'] + 10
    freezes = [["Pass"]] * (kidnap_step - 1)
    scene.goal.action_list = freezes

    placer_first_position = placer['shows'][0]['position']
    placer['shows'].append({
        'stepBegin': kidnap_step,
        'position': {
            'x': placer_first_position['x'],
            'y': placer_first_position['y'],
            'z': placer_first_position['z']
        }
    })
    target_first_position = target['shows'][0]['position']
    target['shows'].append({
        'stepBegin': kidnap_step,
        'position': {
            'x': target_first_position['x'],
            'y': target_first_position['y'],
            'z': target_first_position['z']
        }
    })

    # Close containers
    for container_index in containers_to_open_indexes:
        containers[container_index]['openClose'].append({
            'step': kidnap_step,
            'open': False
        })

    x = scene.performer_start.position.x
    z = scene.performer_start.position.z
    y = scene.performer_start.rotation.y
    scene.debug['endHabituationStep'] = kidnap_step
    scene.debug['endHabituationTeleportPositionX'] = x
    scene.debug['endHabituationTeleportPositionZ'] = z
    scene.debug['endHabituationTeleportRotationY'] = y
    # If we do NOT need to teleport anything, teleport the agent only
    if kidnap_option == ImitationKidnapOptions.AGENT_ONLY:
        agent['shows'].append({
            'stepBegin': kidnap_step,
            'position': {
                'x': random.uniform(-2, 2),
                'y': 0,
                'z': 2
            },
            'rotation': {
                'y': 180
            }
        })
        scene.goal.action_list.append([
            f"EndHabituation,xPosition={x},zPosition={z},yRotation={y}"
        ])
    # If we need to teleport the containers
    elif kidnap_option == ImitationKidnapOptions.CONTAINERS:
        _change_container_and_agent_positions_during_kidnap(
            scene, kidnap_option, containers_on_right_side,
            containers, separation_between_containers,
            kidnap_step, target, placer, agent, containers_teleport_rotation,
            relative_rotation)
        scene.goal.action_list.append([
            f"EndHabituation,xPosition={x},zPosition={z},yRotation={y}"
        ])
    # If we need to teleport the performer
    else:
        _teleport_performer_for_imitation_task(
            scene, agent, kidnap_step)


def _change_container_and_agent_positions_during_kidnap(
        scene: Scene, kidnap_option, containers_on_right_side, containers,
        separation_between_containers, kidnap_step, target,
        placer, agent, containers_teleport_rotation=None,
        relative_rotation=True):
    # Need to slightly shift depending on the start side since
    # the performer is offset to stay in the performers view
    buffer_for_all_containers_to_fit = 2
    buffer_for_agent_to_stand_behind = 1

    rotation = (
        containers_teleport_rotation if containers_teleport_rotation else
        random.choice(IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL))
    if relative_rotation and containers_teleport_rotation:
        rotation = (containers_teleport_rotation +
                    (270 if containers_on_right_side else 90))
        rotation %= 360
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        abs(rotation))
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]

    start_x = round(random.uniform(min_max[0], min_max[1]), 2)
    start_z = round(
        random.uniform(IMITATION_CONTAINER_TELEPORT_MIN_Z_POS,
                       scene.room_dimensions.z / 2 -
                       buffer_for_all_containers_to_fit -
                       buffer_for_agent_to_stand_behind), 2)
    separation = separation_between_containers * (1 if not containers else -1)
    for container in containers:
        container['shows'].append({
            'stepBegin': kidnap_step,
            'position': {
                'x': start_x,
                'y': 0,
                'z': start_z
            },
            'rotation': {
                'y': rotation
            }
        })
        x, z = \
            geometry.get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
                rotation, separation * (-1 if containers_on_right_side else 1),
                0)
        start_x += x
        start_z += z

    # target and placer need to shift too
    x, z = \
        geometry.get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
            rotation,
            IMITATION_TASK_TARGET_SEPARATION *
            (-1 if containers_on_right_side else 1),
            0)
    end_container = -1 if containers_on_right_side else 0
    target['shows'][1]['position']['x'] = \
        containers[end_container]['shows'][1]['position']['x'] + x
    target['shows'][1]['position']['z'] = \
        containers[end_container]['shows'][1]['position']['z'] + z
    placer['shows'][1]['position']['x'] = \
        target['shows'][1]['position']['x']
    placer['shows'][1]['position']['z'] = \
        target['shows'][1]['position']['z']

    separation = 1
    max_container_z = \
        max(containers, key=lambda c: c['shows'][1]['position']['z'])
    agent_z = max_container_z['shows'][1]['position']['z'] + separation
    agent_x = random.choice([min_max[0] - separation, min_max[1] + separation])
    agent['shows'].append({
        'stepBegin': kidnap_step,
        'position': {
            'x': agent_x,
            'y': 0,
            'z': agent_z
        },
        'rotation': {
            'y': 180
        }
    })


def _teleport_performer_for_imitation_task(
        scene: Scene, agent,
        kidnap_step):
    agent_z = random.choice([-2, 2])
    agent['shows'].append({
        'stepBegin': kidnap_step,
        # Put the agent still close the containers
        'position': {
            'x': random.uniform(-2, 2),
            'y': 0,
            'z': agent_z
        },
        'rotation': {
            'y': 180 if agent_z > 0 else 0
        }
    })

    # pick an x and z not in the center x of the room
    # so the teleport is substantial
    shift = 2.5
    x1 = round(random.uniform(
        -scene.room_dimensions.x / 2 + geometry.PERFORMER_WIDTH,
        -shift), 2)
    x2 = round(random.uniform(
        shift, scene.room_dimensions.x / 2 - geometry.PERFORMER_WIDTH),
        2)
    x = random.choice([x1, x2])
    z1 = round(random.uniform(
        -scene.room_dimensions.z / 2 + geometry.PERFORMER_WIDTH,
        -shift), 2)
    z2 = round(random.uniform(
        shift, scene.room_dimensions.z / 2 - geometry.PERFORMER_WIDTH),
        2)
    z = random.choice([z1, z2])
    _, y = geometry.calculate_rotations(
        Vector3d(x=x, y=0, z=z), Vector3d(x=0, y=0, z=0))

    scene.debug['endHabituationStep'] = kidnap_step
    scene.debug['endHabituationTeleportPositionX'] = x
    scene.debug['endHabituationTeleportPositionZ'] = z
    scene.debug['endHabituationTeleportRotationY'] = y
    scene.goal.action_list.append([
        f"EndHabituation,xPosition={x},zPosition={z},yRotation={y}"
    ])


def add_imitation_task(scene: Scene,
                       trigger_order: str,
                       containers_on_right_side: bool,
                       kidnap_option: str,
                       use_scene_room_dimensions: bool = False,
                       agent_settings_override: Dict[str, Any] = None,
                       agent_type_override: bool = False,
                       color_override: List = None,
                       containers_teleport_rotation: int = None,
                       relative_rotation: bool = True):
    """
    Creates an imitation task scene.
    Note: The target should already be added
    to the scene as the first and only object in the object list
    before calling this function.
    """

    # Performer start
    scene.set_performer_start(
        Vector3d(x=0, y=0, z=-3.75), Vector3d(x=0, y=0, z=0))

    # Make a rectangular room
    scene.room_dimensions.y = 2

    if not use_scene_room_dimensions:
        base_dimension = random.randint(8, 10)
        rectangle_dimension = base_dimension * 2
        rectangle_direction = random.randint(0, 1)
        scene.room_dimensions.x = \
            base_dimension if rectangle_direction == 0 else rectangle_dimension
        scene.room_dimensions.z = \
            rectangle_dimension if rectangle_direction == 0 else base_dimension

    # Containers
    containers, separation_between_containers = \
        _setup_three_containers_for_imitation_task(
            scene, containers_on_right_side, color_override)

    # Target with Placer
    target, placer = _setup_target_and_placer_imitation_task(
        scene, containers_on_right_side, containers)

    # Trigger Order
    trigger_order_ids, containers_to_open_indexes = \
        _setup_trigger_order_for_imitation_task(trigger_order, containers)
    scene.goal.triggered_by_target_sequence = trigger_order_ids

    # Agent
    agent, open_steps = _setup_agent_for_imitation_task(
        scene, containers_on_right_side, containers,
        containers_to_open_indexes, agent_settings_override,
        agent_type_override)

    # Now Kidnap the performer!!! ヽ(°o°)ﾉ
    _kidnap_performer_for_imitation_task(
        scene, kidnap_option, containers_on_right_side, target, placer, agent,
        open_steps[-1], containers, containers_to_open_indexes,
        separation_between_containers, containers_teleport_rotation,
        relative_rotation)

    # Raise the ceiling so the target and placer are visible after
    # we generated the scene
    scene.room_dimensions.y = 3
    return scene
