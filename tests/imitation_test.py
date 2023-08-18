from machine_common_sense.config_manager import Vector3d

from generator import base_objects, instances
from generator.geometry import (
    ORIGIN_LOCATION,
    PERFORMER_WIDTH,
    calculate_rotations,
    get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector
)
from generator.imitation import (
    IMITATION_AGENT_END_X,
    IMITATION_AGENT_START_X,
    IMITATION_CONTAINER_SEPARATION,
    IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL,
    IMITATION_CONTAINER_TELEPORT_X_POS_RANGE,
    IMITATION_TASK_TARGET_SEPARATION,
    add_imitation_task
)
from generator.scene import Scene


def test_shortcut_imitation_left_side_teleport_containers_left_right():  # noqa
    scene = Scene()
    target_definition = base_objects.create_soccer_ball()
    target = instances.instantiate_object(target_definition, ORIGIN_LOCATION)
    scene.objects.append(target)
    scene = add_imitation_task(scene, 'left_right', False, 'containers')

    assert len(scene.goal.triggered_by_target_sequence) == 2
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[0]['id']
    # right container
    assert scene.goal.triggered_by_target_sequence[1] == scene.objects[2]['id']
    # action list
    kidnapp_step = scene.debug['endHabituationStep']
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config
    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0
    assert scene.debug['endHabituationStep'] == kidnapp_step

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[0]['shows']
    teleport_rotation = containers[0]['shows'][1]['rotation']['y']
    first_container_teleport_position = containers[0]['shows'][1]['position']
    start_x = first_container_teleport_position['x']
    start_z = first_container_teleport_position['z']
    teleport_positions = []
    teleport_positions.append((start_x, start_z))
    for _ in range(1, 3):
        x, z = \
            get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
                teleport_rotation, -IMITATION_CONTAINER_SEPARATION, 0)
        start_x += x
        start_z += z
        teleport_positions.append((start_x, start_z))
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == (i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == 90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1

        teleport = containers[i]['shows'][1]
        assert teleport['position']['x'] == teleport_positions[i][0]
        assert teleport['position']['z'] == teleport_positions[i][1]
        assert teleport['rotation']['y'] in IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL  # noqa
        assert teleport['rotation']['y'] == teleport_rotation
        assert containers[i]['shows'][1]['stepBegin'] == kidnapp_step
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[0]['openClose'][0]['step'] == 22
    assert containers[0]['openClose'][0]['open'] is True
    assert containers[0]['openClose'][1]['step'] == kidnapp_step
    assert containers[0]['openClose'][1]['open'] is False
    assert containers[1].get('openClose') is None  # middle container
    assert containers[2]['openClose'][0]['step'] == 97
    assert containers[2]['openClose'][0]['open'] is True
    assert containers[2]['openClose'][1]['step'] == kidnapp_step
    assert containers[2]['openClose'][1]['open'] is False
    # left container is in view after rotation, it tells us if the other
    # containers are in view because they are in a straight line
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert min_max[0] <= scene.objects[0]['shows'][1]['position']['x'] \
        <= min_max[1]
    agent_stand_behind_buffer = 1
    assert 0 <= scene.objects[0]['shows'][1]['position']['z'] <= \
        scene.room_dimensions.z / 2 - agent_stand_behind_buffer

    # target
    x, z = \
        get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
            teleport_rotation, -IMITATION_TASK_TARGET_SEPARATION, 0)
    x = first_container_teleport_position['x'] - x
    z = first_container_teleport_position['z'] - z
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == x
    assert target['shows'][1]['position']['z'] == z
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == x
    assert placer['shows'][1]['position']['z'] == z
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 27
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == IMITATION_AGENT_START_X
    assert start['position']['z'] == -1  # left chest
    assert start['rotation']['y'] == -90  # face right
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    assert teleport['rotation']['y'] == 180  # face performer
    # behind containers
    separation = 1
    max_container_z = \
        max(containers, key=lambda c: c['shows'][1]['position']['z'])[
            'shows'][1]['position']['z']
    assert teleport['position']['z'] == max_container_z + separation
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        containers[0]['shows'][1]['rotation']['y'])
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert (
        teleport['position']['x'] == min_max[0] - separation or
        teleport['position']['x'] == min_max[1] + separation)
    assert len(agent['rotates']) == 1
    assert agent['rotates'][0]['stepBegin'] == 83
    # left rotation because agent is walking torward perfromer
    assert agent['rotates'][0]['vector']['y'] == -9
    # opening containers sequence
    animations = agent['actions']
    assert len(animations) == 3
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    assert animations[1]['id'] == 'TPM_turnL45'
    assert animations[1]['stepBegin'] == 83
    assert animations[1]['stepEnd'] == 93
    assert animations[2]['id'] == 'TPE_jump'
    assert animations[2]['stepBegin'] == 93
    assert animations[2]['stepEnd'] == 103
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 3
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] ==
            movement['sequence'][2]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] ==
            movement['sequence'][2]['endPoint']['x'] == -IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == -1.0  # left
    assert movement['sequence'][1]['endPoint']['z'] == 1.0  # right
    assert movement['sequence'][2]['endPoint']['z'] == 0.85  # face performer


def test_shortcut_imitation_right_side_teleport_containers_left_right():  # noqa
    scene = Scene()
    target_definition = base_objects.create_soccer_ball()
    target = instances.instantiate_object(target_definition, ORIGIN_LOCATION)
    scene.objects.append(target)
    scene = add_imitation_task(scene, 'left_right', True, 'containers')

    assert len(scene.goal.triggered_by_target_sequence) == 2
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[0]['id']
    # right container
    assert scene.goal.triggered_by_target_sequence[1] == scene.objects[2]['id']
    # action list
    kidnapp_step = scene.debug['endHabituationStep']
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config
    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0
    assert scene.debug['endHabituationStep'] == kidnapp_step

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[-1]['shows']
    teleport_rotation = containers[0]['shows'][1]['rotation']['y']
    first_container_teleport_position = containers[0]['shows'][1]['position']
    start_x = first_container_teleport_position['x']
    start_z = first_container_teleport_position['z']
    teleport_positions = []
    teleport_positions.append((start_x, start_z))
    for _ in range(1, 3):
        x, z = \
            get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
                teleport_rotation, IMITATION_CONTAINER_SEPARATION, 0)
        start_x -= x
        start_z -= z
        teleport_positions.append((start_x, start_z))
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == -(i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == -90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1

        teleport = containers[i]['shows'][1]
        assert round(
            teleport['position']['x'], 3) == round(
            teleport_positions[i][0], 3)
        assert round(
            teleport['position']['z'], 3) == round(
            teleport_positions[i][1], 3)
        assert teleport['rotation']['y'] in IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL  # noqa
        assert teleport['rotation']['y'] == teleport_rotation
        assert containers[i]['shows'][1]['stepBegin'] == kidnapp_step
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[0]['openClose'][0]['step'] == 22
    assert containers[0]['openClose'][0]['open'] is True
    assert containers[0]['openClose'][1]['step'] == kidnapp_step
    assert containers[0]['openClose'][1]['open'] is False
    assert containers[1].get('openClose') is None  # middle container
    assert containers[2]['openClose'][0]['step'] == 96
    assert containers[2]['openClose'][0]['open'] is True
    assert containers[2]['openClose'][1]['step'] == kidnapp_step
    assert containers[2]['openClose'][1]['open'] is False
    # left container is in view after rotation, it tells us if the other
    # containers are in view because they are in a straight line
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert min_max[0] <= scene.objects[0]['shows'][1]['position']['x'] \
        <= min_max[1]
    agent_stand_behind_buffer = 1
    assert 0 <= scene.objects[0]['shows'][1]['position']['z'] <= \
        scene.room_dimensions.z / 2 - agent_stand_behind_buffer

    # target
    x, z = \
        get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
            teleport_rotation, IMITATION_TASK_TARGET_SEPARATION, 0)
    x = end_container[1]['position']['x'] - x
    z = end_container[1]['position']['z'] - z
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == x
    assert target['shows'][1]['position']['z'] == z
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == x
    assert placer['shows'][1]['position']['z'] == z
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 27
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == -IMITATION_AGENT_START_X
    assert start['position']['z'] == 1  # left chest
    assert start['rotation']['y'] == 90  # face right
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    assert teleport['rotation']['y'] == 180  # face performer
    # behind containers
    separation = 1
    max_container_z = \
        max(containers, key=lambda c: c['shows'][1]['position']['z'])[
            'shows'][1]['position']['z']
    assert teleport['position']['z'] == max_container_z + separation
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert (
        teleport['position']['x'] == min_max[0] - separation or
        teleport['position']['x'] == min_max[1] + separation)
    assert len(agent['rotates']) == 1
    assert agent['rotates'][0]['stepBegin'] == 82
    # left rotation because agent is walking torward perfromer
    assert agent['rotates'][0]['vector']['y'] == -9
    # opening containers sequence
    animations = agent['actions']
    assert len(animations) == 3
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    assert animations[1]['id'] == 'TPM_turnL45'
    assert animations[1]['stepBegin'] == 82
    assert animations[1]['stepEnd'] == 92
    assert animations[2]['id'] == 'TPE_jump'
    assert animations[2]['stepBegin'] == 92
    assert animations[2]['stepEnd'] == 102
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 3
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] ==
            movement['sequence'][2]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] ==
            movement['sequence'][2]['endPoint']['x'] == IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == 1.0  # left
    assert movement['sequence'][1]['endPoint']['z'] == -1.0  # right
    assert movement['sequence'][2]['endPoint']['z'] == -1.15  # face performer


def test_shortcut_imitation_left_side_teleport_containers_right_middle():
    scene = Scene()
    target_definition = base_objects.create_soccer_ball()
    target = instances.instantiate_object(target_definition, ORIGIN_LOCATION)
    scene.objects.append(target)
    scene = add_imitation_task(scene, 'right_middle', False, 'containers')

    assert len(scene.goal.triggered_by_target_sequence) == 2
    # right container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[2]['id']
    # middle container
    assert scene.goal.triggered_by_target_sequence[1] == scene.objects[1]['id']
    # action list
    kidnapp_step = scene.debug['endHabituationStep']
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config
    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0
    assert scene.debug['endHabituationStep'] == kidnapp_step

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[0]['shows']
    teleport_rotation = containers[0]['shows'][1]['rotation']['y']
    first_container_teleport_position = containers[0]['shows'][1]['position']
    start_x = first_container_teleport_position['x']
    start_z = first_container_teleport_position['z']
    teleport_positions = []
    teleport_positions.append((start_x, start_z))
    for _ in range(1, 3):
        x, z = \
            get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
                teleport_rotation, -IMITATION_CONTAINER_SEPARATION, 0)
        start_x += x
        start_z += z
        teleport_positions.append((start_x, start_z))
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == (i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == 90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1

        teleport = containers[i]['shows'][1]
        assert teleport['position']['x'] == teleport_positions[i][0]
        assert teleport['position']['z'] == teleport_positions[i][1]
        assert teleport['rotation']['y'] in IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL  # noqa
        assert teleport['rotation']['y'] == teleport_rotation
        assert containers[i]['shows'][1]['stepBegin'] == kidnapp_step
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[2]['openClose'][0]['step'] == 22
    assert containers[2]['openClose'][0]['open'] is True
    assert containers[2]['openClose'][1]['step'] == kidnapp_step
    assert containers[2]['openClose'][1]['open'] is False
    assert containers[0].get('openClose') is None  # left container
    assert containers[1]['openClose'][0]['step'] == 71
    assert containers[1]['openClose'][0]['open'] is True
    assert containers[1]['openClose'][1]['step'] == kidnapp_step
    assert containers[1]['openClose'][1]['open'] is False
    # left container is in view after rotation, it tells us if the other
    # containers are in view because they are in a straight line
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert min_max[0] <= scene.objects[0]['shows'][1]['position']['x'] \
        <= min_max[1]
    agent_stand_behind_buffer = 1
    assert 0 <= scene.objects[0]['shows'][1]['position']['z'] <= \
        scene.room_dimensions.z / 2 - agent_stand_behind_buffer

    # target
    x, z = \
        get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
            teleport_rotation, -IMITATION_TASK_TARGET_SEPARATION, 0)
    x = first_container_teleport_position['x'] - x
    z = first_container_teleport_position['z'] - z
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == x
    assert target['shows'][1]['position']['z'] == z
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == x
    assert placer['shows'][1]['position']['z'] == z
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 27
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == IMITATION_AGENT_START_X
    assert start['position']['z'] == 1  # right chest
    assert start['rotation']['y'] == -90  # face left
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    assert teleport['rotation']['y'] == 180  # face performer
    # behind containers
    separation = 1
    max_container_z = \
        max(containers, key=lambda c: c['shows'][1]['position']['z'])[
            'shows'][1]['position']['z']
    assert teleport['position']['z'] == max_container_z + separation
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert (
        teleport['position']['x'] == min_max[0] - separation or
        teleport['position']['x'] == min_max[1] + separation)
    assert len(agent['rotates']) == 1
    assert agent['rotates'][0]['stepBegin'] == 57
    # left rotation because agent is walking torward perfromer
    assert agent['rotates'][0]['vector']['y'] == 9
    # opening containers sequence
    animations = agent['actions']
    assert len(animations) == 3
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    assert animations[1]['id'] == 'TPM_turnR45'
    assert animations[1]['stepBegin'] == 57
    assert animations[1]['stepEnd'] == 67
    assert animations[2]['id'] == 'TPE_jump'
    assert animations[2]['stepBegin'] == 67
    assert animations[2]['stepEnd'] == 77
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 3
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] ==
            movement['sequence'][2]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] ==
            movement['sequence'][2]['endPoint']['x'] == -IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == 1.0  # right
    assert movement['sequence'][1]['endPoint']['z'] == 0.0  # middle
    assert movement['sequence'][2]['endPoint']['z'] == -0.15  # face performer


def test_shortcut_imitation_right_side_teleport_containers_right_middle():
    scene = Scene()
    target_definition = base_objects.create_soccer_ball()
    target = instances.instantiate_object(target_definition, ORIGIN_LOCATION)
    scene.objects.append(target)
    scene = add_imitation_task(scene, 'right_middle', True, 'containers')

    assert len(scene.goal.triggered_by_target_sequence) == 2
    # right container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[2]['id']
    # middle container
    assert scene.goal.triggered_by_target_sequence[1] == scene.objects[1]['id']
    # action list
    kidnapp_step = scene.debug['endHabituationStep']
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config
    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0
    assert scene.debug['endHabituationStep'] == kidnapp_step

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[-1]['shows']
    teleport_rotation = containers[0]['shows'][1]['rotation']['y']
    first_container_teleport_position = containers[0]['shows'][1]['position']
    start_x = first_container_teleport_position['x']
    start_z = first_container_teleport_position['z']
    teleport_positions = []
    teleport_positions.append((start_x, start_z))
    for _ in range(1, 3):
        x, z = \
            get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
                teleport_rotation, IMITATION_CONTAINER_SEPARATION, 0)
        start_x -= x
        start_z -= z
        teleport_positions.append((start_x, start_z))
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == -(i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == -90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1

        teleport = containers[i]['shows'][1]
        assert round(
            teleport['position']['x'], 3) == round(
            teleport_positions[i][0], 3)
        assert round(
            teleport['position']['z'], 3) == round(
            teleport_positions[i][1], 3)
        assert teleport['rotation']['y'] in IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL  # noqa
        assert teleport['rotation']['y'] == teleport_rotation
        assert containers[i]['shows'][1]['stepBegin'] == kidnapp_step
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[2]['openClose'][0]['step'] == 22
    assert containers[2]['openClose'][0]['open'] is True
    assert containers[2]['openClose'][1]['step'] == kidnapp_step
    assert containers[2]['openClose'][1]['open'] is False
    assert containers[0].get('openClose') is None  # left container
    assert containers[1]['openClose'][0]['step'] == 71
    assert containers[1]['openClose'][0]['open'] is True
    assert containers[1]['openClose'][1]['step'] == kidnapp_step
    assert containers[1]['openClose'][1]['open'] is False
    # left container is in view after rotation, it tells us if the other
    # containers are in view because they are in a straight line
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert min_max[0] <= scene.objects[0]['shows'][1]['position']['x'] \
        <= min_max[1]
    agent_stand_behind_buffer = 1
    assert 0 <= scene.objects[0]['shows'][1]['position']['z'] <= \
        scene.room_dimensions.z / 2 - agent_stand_behind_buffer

    # target
    x, z = \
        get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
            teleport_rotation, IMITATION_TASK_TARGET_SEPARATION, 0)
    x = end_container[1]['position']['x'] - x
    z = end_container[1]['position']['z'] - z
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == x
    assert target['shows'][1]['position']['z'] == z
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == x
    assert placer['shows'][1]['position']['z'] == z
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 27
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == -IMITATION_AGENT_START_X
    assert start['position']['z'] == -1  # left chest
    assert start['rotation']['y'] == 90  # face right
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    assert teleport['rotation']['y'] == 180  # face performer
    # behind containers
    separation = 1
    max_container_z = \
        max(containers, key=lambda c: c['shows'][1]['position']['z'])[
            'shows'][1]['position']['z']
    assert teleport['position']['z'] == max_container_z + separation
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert (
        teleport['position']['x'] == min_max[0] - separation or
        teleport['position']['x'] == min_max[1] + separation)
    assert len(agent['rotates']) == 1
    assert agent['rotates'][0]['stepBegin'] == 57
    # left rotation because agent is walking torward perfromer
    assert agent['rotates'][0]['vector']['y'] == 9
    # opening containers sequence
    animations = agent['actions']
    assert len(animations) == 3
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    assert animations[1]['id'] == 'TPM_turnR45'
    assert animations[1]['stepBegin'] == 57
    assert animations[1]['stepEnd'] == 67
    assert animations[2]['id'] == 'TPE_jump'
    assert animations[2]['stepBegin'] == 67
    assert animations[2]['stepEnd'] == 77
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 3
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] ==
            movement['sequence'][2]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] ==
            movement['sequence'][2]['endPoint']['x'] == IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == -1.0  # right
    assert movement['sequence'][1]['endPoint']['z'] == 0.0  # middle
    assert movement['sequence'][2]['endPoint']['z'] == -0.15  # face performer


def test_shortcut_imitation_left_side_teleport_performer_left():
    scene = Scene()
    target_definition = base_objects.create_soccer_ball()
    target = instances.instantiate_object(target_definition, ORIGIN_LOCATION)
    scene.objects.append(target)
    scene = add_imitation_task(scene, 'left', False, 'performer')

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert len(scene.goal.triggered_by_target_sequence) == 1
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[0]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config

    shift = 2.5
    neg_range_x = (-scene.room_dimensions.x / 2 - PERFORMER_WIDTH, -shift)
    pos_range_x = (shift, scene.room_dimensions.x / 2 - PERFORMER_WIDTH)
    neg_range_z = (-scene.room_dimensions.z / 2 - PERFORMER_WIDTH, -shift)
    pos_range_z = (shift, scene.room_dimensions.z / 2 - PERFORMER_WIDTH)
    assert (
        (neg_range_x[0] <= scene.debug['endHabituationTeleportPositionX'] <=
         neg_range_x[1]) or
        (pos_range_x[0] <= scene.debug['endHabituationTeleportPositionX'] <=
         pos_range_x[1])
    )
    assert (
        (neg_range_z[0] <= scene.debug['endHabituationTeleportPositionZ'] <=
         neg_range_z[1]) or
        (pos_range_z[0] <= scene.debug['endHabituationTeleportPositionZ'] <=
         pos_range_z[1])
    )
    _, rotation_y = calculate_rotations(
        Vector3d(
            x=scene.debug['endHabituationTeleportPositionX'],
            y=0,
            z=scene.debug['endHabituationTeleportPositionZ']),
        Vector3d(x=0, y=0, z=0)
    )
    assert scene.debug['endHabituationTeleportRotationY'] == rotation_y

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[0]['shows']
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == (i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == 90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[1].get('openClose') is None  # middle container
    assert containers[2].get('openClose') is None  # right container
    assert containers[0]['openClose'][0]['step'] == 22
    assert containers[0]['openClose'][0]['open'] is True
    assert containers[0]['openClose'][1]['step'] == kidnapp_step
    assert containers[0]['openClose'][1]['open'] is False

    # target
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 27
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == IMITATION_AGENT_START_X
    assert start['position']['z'] == -1  # left chest
    assert start['rotation']['y'] == -90  # face right
    # move agent after kidnapp
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    agent_z_choices = (-2, 2)
    agent_x_range = (-2, 2)
    assert teleport['rotation']['y'] == \
        (180 if teleport['position']['z'] > 0 else 0)
    assert teleport['position']['z'] == \
        agent_z_choices[0] or teleport['position']['z'] == agent_z_choices[1]
    assert agent_x_range[0] <= teleport['position']['x'] <= agent_x_range[1]

    # opening containers sequence
    assert agent.get('rotates') is None
    animations = agent['actions']
    assert len(animations) == 1
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 2
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] == -IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == -1  # left
    assert movement['sequence'][1]['endPoint']['z'] == -1.15  # face performer


def test_shortcut_imitation_right_side_teleport_performer_right():
    scene = Scene()
    target_definition = base_objects.create_soccer_ball()
    target = instances.instantiate_object(target_definition, ORIGIN_LOCATION)
    scene.objects.append(target)
    scene = add_imitation_task(scene, 'right', True, 'performer')

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert len(scene.goal.triggered_by_target_sequence) == 1
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[2]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config

    shift = 2.5
    neg_range_x = (-scene.room_dimensions.x / 2 - PERFORMER_WIDTH, -shift)
    pos_range_x = (shift, scene.room_dimensions.x / 2 - PERFORMER_WIDTH)
    neg_range_z = (-scene.room_dimensions.z / 2 - PERFORMER_WIDTH, -shift)
    pos_range_z = (shift, scene.room_dimensions.z / 2 - PERFORMER_WIDTH)
    assert (
        (neg_range_x[0] <= scene.debug['endHabituationTeleportPositionX'] <=
         neg_range_x[1]) or
        (pos_range_x[0] <= scene.debug['endHabituationTeleportPositionX'] <=
         pos_range_x[1])
    )
    assert (
        (neg_range_z[0] <= scene.debug['endHabituationTeleportPositionZ'] <=
         neg_range_z[1]) or
        (pos_range_z[0] <= scene.debug['endHabituationTeleportPositionZ'] <=
         pos_range_z[1])
    )
    _, rotation_y = calculate_rotations(
        Vector3d(
            x=scene.debug['endHabituationTeleportPositionX'],
            y=0,
            z=scene.debug['endHabituationTeleportPositionZ']),
        Vector3d(x=0, y=0, z=0)
    )
    assert scene.debug['endHabituationTeleportRotationY'] == rotation_y

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[-1]['shows']
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == -(i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == -90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[0].get('openClose') is None  # left container
    assert containers[1].get('openClose') is None  # middle container
    assert containers[2]['openClose'][0]['step'] == 22
    assert containers[2]['openClose'][0]['open'] is True
    assert containers[2]['openClose'][1]['step'] == kidnapp_step
    assert containers[2]['openClose'][1]['open'] is False

    # target
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 27
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == -IMITATION_AGENT_START_X
    assert start['position']['z'] == -1  # right chest
    assert start['rotation']['y'] == 90  # face right
    # move agent after kidnapp
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    agent_z_choices = (-2, 2)
    agent_x_range = (-2, 2)
    assert teleport['rotation']['y'] == \
        (180 if teleport['position']['z'] > 0 else 0)
    assert teleport['position']['z'] == \
        agent_z_choices[0] or teleport['position']['z'] == agent_z_choices[1]
    assert agent_x_range[0] <= teleport['position']['x'] <= agent_x_range[1]

    # opening containers sequence
    assert agent.get('rotates') is None
    animations = agent['actions']
    assert len(animations) == 1


def test_shortcut_imitation_left_side_middle_agent_only():
    scene = Scene()
    target_definition = base_objects.create_soccer_ball()
    target = instances.instantiate_object(target_definition, ORIGIN_LOCATION)
    scene.objects.append(target)
    scene = add_imitation_task(scene, 'middle', False, 'agent_only')

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert len(scene.goal.triggered_by_target_sequence) == 1
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[1]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config

    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[0]['shows']
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == (i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == 90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[0].get('openClose') is None  # left container
    assert containers[2].get('openClose') is None  # right container
    assert containers[1]['openClose'][0]['step'] == 22
    assert containers[1]['openClose'][0]['open'] is True
    assert containers[1]['openClose'][1]['step'] == kidnapp_step
    assert containers[1]['openClose'][1]['open'] is False

    # target
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 27
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == IMITATION_AGENT_START_X
    assert start['position']['z'] == 0  # middle chest
    assert start['rotation']['y'] == -90  # face left
    # move agent after kidnapp
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    agent_x_range = (-2, 2)
    assert teleport['rotation']['y'] == 180
    assert teleport['position']['z'] == 2
    assert agent_x_range[0] <= teleport['position']['x'] <= agent_x_range[1]

    # opening containers sequence
    assert agent.get('rotates') is None
    animations = agent['actions']
    assert len(animations) == 1
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 2
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] == -IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == 0  # middle
    assert movement['sequence'][1]['endPoint']['z'] == -0.15  # face performer


def test_shortcut_imitation_right_side_teleport_containers_middle_left_agent_only():  # noqa
    scene = Scene()
    target_definition = base_objects.create_soccer_ball()
    target = instances.instantiate_object(target_definition, ORIGIN_LOCATION)
    scene.objects.append(target)
    scene = add_imitation_task(scene, 'middle_left', True, 'agent_only')

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert len(scene.goal.triggered_by_target_sequence) == 2
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[1]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config
    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0
    assert scene.debug['endHabituationStep'] == kidnapp_step

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[-1]['shows']
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == -(i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == -90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[2].get('openClose') is None  # left container
    assert containers[1]['openClose'][0]['step'] == 22
    assert containers[1]['openClose'][0]['open'] is True
    assert containers[1]['openClose'][1]['step'] == kidnapp_step
    assert containers[1]['openClose'][1]['open'] is False
    assert containers[0]['openClose'][0]['step'] == 71
    assert containers[0]['openClose'][0]['open'] is True
    assert containers[0]['openClose'][1]['step'] == kidnapp_step
    assert containers[0]['openClose'][1]['open'] is False

    # target
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 27
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == -IMITATION_AGENT_START_X
    assert start['position']['z'] == 0  # middle chest
    assert start['rotation']['y'] == 90  # face right
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    assert teleport['rotation']['y'] == 180  # face performer
    # behind containers
    # of to the right or the left since the containers were rotate 90
    assert -2 <= teleport['position']['x'] <= 2
    assert teleport['position']['z'] == 2
    assert len(agent['rotates']) == 1
    assert agent['rotates'][0]['stepBegin'] == 57
    # right rotation because agent is walking torward perfromer
    assert agent['rotates'][0]['vector']['y'] == 9
    # opening containers sequence
    animations = agent['actions']
    assert len(animations) == 3
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    assert animations[1]['id'] == 'TPM_turnR45'
    assert animations[1]['stepBegin'] == 57
    assert animations[1]['stepEnd'] == 67
    assert animations[2]['id'] == 'TPE_jump'
    assert animations[2]['stepBegin'] == 67
    assert animations[2]['stepEnd'] == 77
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 3
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] ==
            movement['sequence'][2]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] ==
            movement['sequence'][2]['endPoint']['x'] == IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == 0  # middle
    assert movement['sequence'][1]['endPoint']['z'] == 1  # left
    assert movement['sequence'][2]['endPoint']['z'] == 0.85  # face performer
