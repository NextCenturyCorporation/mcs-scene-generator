import random

import pytest
from machine_common_sense.config_manager import Goal

from ideal_learning_env.action_service import (
    ActionService,
    SidestepsConfig,
    StepBeginEnd,
    TeleportConfig
)
from ideal_learning_env.defs import ILEException

from .ile_helper import (
    create_agent_scene,
    create_placers_turntables_scene,
    create_random_agent_placer_turntable_scene,
    create_specific_agent_placer_turntable_scene,
    create_test_obj_scene
)


def test_action_freezes_empty_array():
    goal = Goal()
    ActionService.add_freezes(goal, [])
    assert goal.action_list == []


def test_action_freezes_single():
    goal = Goal()
    steps = [StepBeginEnd(1, 3)]
    ActionService.add_freezes(goal, steps)
    assert goal.action_list == [['Pass'], ['Pass']]


def test_action_freezes_multiple():
    goal = Goal()
    steps = [StepBeginEnd(2, 3), StepBeginEnd(5, 6)]
    ActionService.add_freezes(goal, steps)
    assert goal.action_list == [[], ['Pass'], [], [], ['Pass']]


def test_action_freezes_bad_step():
    goal = Goal()
    steps = [StepBeginEnd(3, 1)]
    with pytest.raises(ILEException):
        ActionService.add_freezes(goal, steps)


def test_action_freezes_overlap():
    goal = Goal()
    steps = [StepBeginEnd(1, 3), StepBeginEnd(2, 4)]
    with pytest.raises(ILEException):
        ActionService.add_freezes(goal, steps)


def test_action_teleports_empty_array():
    goal = Goal()
    ActionService.add_teleports(goal, [], False)
    assert goal.action_list == []


def test_action_teleports_single():
    goal = Goal()
    teleports = [TeleportConfig(2, 3, 4, 90)]
    ActionService.add_teleports(goal, teleports, False)
    al = goal.action_list
    assert al
    assert len(al) == 2
    action = al[1]
    assert action == ['EndHabituation,xPosition=3,zPosition=4,yRotation=90']


def test_action_teleports_multiple():
    goal = Goal()
    teleports = [TeleportConfig(1, -2, 1, 180), TeleportConfig(3, 2, -1, 270)]
    ActionService.add_teleports(goal, teleports, False)
    al = goal.action_list
    assert al
    assert len(al) == 3
    action = al[0]
    assert action == ['EndHabituation,xPosition=-2,zPosition=1,yRotation=180']
    action = al[2]
    assert action == ['EndHabituation,xPosition=2,zPosition=-1,yRotation=270']


def test_action_teleports_multiple_out_of_order():
    goal = Goal()
    teleports = [TeleportConfig(3, -2, 1, 180), TeleportConfig(1, 2, -1, 270)]
    ActionService.add_teleports(goal, teleports, False)
    al = goal.action_list
    assert al
    assert len(al) == 3
    action = al[0]
    assert action == ['EndHabituation,xPosition=2,zPosition=-1,yRotation=270']
    action = al[2]
    assert action == ['EndHabituation,xPosition=-2,zPosition=1,yRotation=180']


def test_action_teleports_look_at_center_facing_front():
    goal = Goal()
    teleports = [TeleportConfig(1, 0, -7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=0,zPosition=-7.5,yRotation=0']

    goal = Goal()
    teleports = [TeleportConfig(1, 0.25, -7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=0.25,zPosition=-7.5,yRotation=0']

    goal = Goal()
    teleports = [TeleportConfig(1, -0.25, -7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=-0.25,zPosition=-7.5,yRotation=0']


def test_action_teleports_look_at_center_facing_back():
    goal = Goal()
    teleports = [TeleportConfig(1, 0, 7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=0,zPosition=7.5,yRotation=180']

    goal = Goal()
    teleports = [TeleportConfig(1, 0.25, 7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=0.25,zPosition=7.5,yRotation=180']

    goal = Goal()
    teleports = [TeleportConfig(1, -0.25, 7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert (
        cmd == ['EndHabituation,xPosition=-0.25,zPosition=7.5,yRotation=180']
    )


def test_action_teleports_look_at_center_facing_left():
    goal = Goal()
    teleports = [TeleportConfig(1, 7.5, 0, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=7.5,zPosition=0,yRotation=270']

    goal = Goal()
    teleports = [TeleportConfig(1, 7.5, 0.25, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=7.5,zPosition=0.25,yRotation=270']

    goal = Goal()
    teleports = [TeleportConfig(1, 7.5, -0.25, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert (
        cmd == ['EndHabituation,xPosition=7.5,zPosition=-0.25,yRotation=270']
    )


def test_action_teleports_look_at_center_facing_right():
    goal = Goal()
    teleports = [TeleportConfig(1, -7.5, 0, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=-7.5,zPosition=0,yRotation=90']

    goal = Goal()
    teleports = [TeleportConfig(1, -7.5, 0.25, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=-7.5,zPosition=0.25,yRotation=90']

    goal = Goal()
    teleports = [TeleportConfig(1, -7.5, -0.25, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert (
        cmd == ['EndHabituation,xPosition=-7.5,zPosition=-0.25,yRotation=90']
    )


def test_action_teleports_look_at_center_rounds_to_tens():
    goal = Goal()
    teleports = [TeleportConfig(1, 2, 2, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=2,zPosition=2,yRotation=220']


def test_action_teleports_look_at_center_ignores_rotation_y():
    goal = Goal()
    teleports = [TeleportConfig(1, 0, 7.5, 90, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal.action_list) == 1
    cmd = goal.action_list[0]
    assert cmd == ['EndHabituation,xPosition=0,zPosition=7.5,yRotation=180']


def test_action_circles_empty_array():
    goal = Goal()
    ActionService.add_circles(goal, [])
    assert goal.action_list == []


def test_action_circles_single():
    goal = Goal()
    ActionService.add_circles(goal, [1])
    circle = ['RotateRight']
    assert goal.action_list == [circle] * 36


def test_action_circles_multiple():
    goal = Goal()
    ActionService.add_circles(goal, [1, 101])
    circle = ['RotateRight']
    assert goal.action_list == [circle] * 36 + [[]] * 64 + [circle] * 36


def test_action_swivels_empty_array():
    goal = Goal()
    ActionService.add_swivels(goal, [])
    assert goal.action_list == []


def test_action_swivels_single():
    goal = Goal()
    steps = [StepBeginEnd(3, 5)]
    ActionService.add_swivels(goal, steps)
    swivel = ['LookDown', 'LookUp', 'RotateLeft', 'RotateRight']
    assert goal.action_list == [[], [], swivel, swivel]


def test_action_swivels_multiple():
    goal = Goal()
    steps = [StepBeginEnd(1, 2), StepBeginEnd(4, 6)]
    ActionService.add_swivels(goal, steps)
    swivel = ['LookDown', 'LookUp', 'RotateLeft', 'RotateRight']
    assert goal.action_list == [swivel, [], [], swivel, swivel]


def test_action_swivels_bad_step():
    goal = Goal()
    steps = [StepBeginEnd(5, 2)]
    with pytest.raises(ILEException):
        ActionService.add_swivels(goal, steps)


def test_action_swivels_overlap():
    goal = Goal()
    steps = [StepBeginEnd(3, 5), StepBeginEnd(4, 7)]
    with pytest.raises(ILEException):
        ActionService.add_swivels(goal, steps)


def test_action_sidesteps_empty_array():
    goal = Goal()
    ActionService.add_sidesteps(goal, [], create_test_obj_scene(0, 3))
    assert goal.action_list == []


def test_action_sidesteps_single_minimum_distance():
    # Predetermined sidesteps action lists that are known to work after
    # being tested and graphed
    positive_90_right_movement = (
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 15 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 3
    )

    negative_90_left_movement = (
        [['MoveLeft']] * 8 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 15 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 8 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 3
    )

    positive_180_right_movement = (
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 15 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 6 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 6 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 12 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 12 +
        [['RotateLeft']] * 1
    )

    negative_180_left_movement = (
        [['MoveLeft']] * 8 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 15 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 8 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 6 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 6 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 12 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 12
    )

    positive_270_right_movement = (
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 15 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 6 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 6 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 12 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 11 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 7 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 4 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 7 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 4 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 7 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 11 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateRight']] * 1
    )

    negative_270_left_movement = (
        [['MoveLeft']] * 8 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 15 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 8 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 6 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 6 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 12 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 11 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 7 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 4 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 7 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 4 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 7 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 11 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateLeft']] * 1
    )

    positive_360_right_movement = (
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 15 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 6 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 6 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 12 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 11 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 7 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 4 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 7 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 4 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 7 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 11 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 13 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 10 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 9 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2
    )
    negative_360_left_movement = (
        [['MoveLeft']] * 8 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 15 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 8 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 6 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 6 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 12 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 11 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 7 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 4 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 7 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 4 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 7 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 11 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 13 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 10 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 9 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 8 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2
    )
    minimum_distance = 3

    # Try +x, -x, +z, -z. They should all be the same.
    # Test all degree options [90, 180, 270, 360, -90, -180, -270, -360]
    for i in range(100):
        for i in range(4):
            # Setup scene and object
            x = minimum_distance if i == 0 else -minimum_distance if \
                i == 1 else 0
            z = minimum_distance if i == 2 else -minimum_distance if \
                i == 3 else 0
            scene = create_test_obj_scene(x, z)

            # +90 Degrees
            goal = Goal()
            steps = [
                SidestepsConfig(
                    begin=1,
                    object_label='object',
                    degrees=90)]
            ActionService.add_sidesteps(goal, steps, scene)
            assert goal.action_list == positive_90_right_movement

            # -90 Degrees
            goal = Goal()
            steps = [
                SidestepsConfig(
                    begin=1,
                    object_label='object',
                    degrees=-90)]
            ActionService.add_sidesteps(goal, steps, scene)
            assert goal.action_list == negative_90_left_movement

            # +180 Degrees
            goal = Goal()
            steps = [
                SidestepsConfig(
                    begin=1,
                    object_label='object',
                    degrees=180)]
            ActionService.add_sidesteps(goal, steps, scene)
            assert goal.action_list == positive_180_right_movement

            # -180 Degrees
            goal = Goal()
            steps = [
                SidestepsConfig(
                    begin=1,
                    object_label='object',
                    degrees=-180)]
            ActionService.add_sidesteps(goal, steps, scene)
            assert goal.action_list == negative_180_left_movement

            # 270 Degrees
            goal = Goal()
            steps = [
                SidestepsConfig(
                    begin=1,
                    object_label='object',
                    degrees=270)]
            ActionService.add_sidesteps(goal, steps, scene)
            assert goal.action_list == positive_270_right_movement

            # -270 Degrees
            goal = Goal()
            steps = [
                SidestepsConfig(
                    begin=1,
                    object_label='object',
                    degrees=-270)]
            ActionService.add_sidesteps(goal, steps, scene)
            assert goal.action_list == negative_270_left_movement

            # +360 Degrees
            goal = Goal()
            steps = [
                SidestepsConfig(
                    begin=1,
                    object_label='object',
                    degrees=360)]
            ActionService.add_sidesteps(goal, steps, scene)
            assert goal.action_list == positive_360_right_movement

            # -360 Degrees
            goal = Goal()
            steps = [
                SidestepsConfig(
                    begin=1,
                    object_label='object',
                    degrees=-360)]
            ActionService.add_sidesteps(goal, steps, scene)
            assert goal.action_list == negative_360_left_movement


def test_action_sidesteps_multiple():
    # Setup scene and object
    scene = create_test_obj_scene(0, 3)
    goal = Goal()
    steps = [
        SidestepsConfig(
            begin=1,
            object_label='object',
            degrees=90),
        SidestepsConfig(
            begin=59,
            object_label='object',
            degrees=-90)]
    ActionService.add_sidesteps(goal, steps, scene)
    assert goal.action_list == (
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 15 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 11 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 15 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 3 +
        [['MoveLeft']] * 9 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 15 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 9 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 3
    )


def test_action_sidesteps_begin_later():
    # Setup scene and object
    scene = create_test_obj_scene(0, 3)
    goal = Goal()
    steps = [
        SidestepsConfig(
            begin=10,
            object_label='object',
            degrees=90),
        SidestepsConfig(
            begin=100,
            object_label='object',
            degrees=-90)]
    ActionService.add_sidesteps(goal, steps, scene)
    assert goal.action_list == (
        [[]] * 9 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 15 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 3 +
        [[]] * 32 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 15 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 2 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 8 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 5 +
        [['RotateLeft']] * 1 +
        [['MoveRight']] * 3 +
        [['MoveLeft']] * 9 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 15 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 2 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 9 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 5 +
        [['RotateRight']] * 1 +
        [['MoveLeft']] * 3
    )


def test_action_sidesteps_overlap_freeze_error():
    scene = create_test_obj_scene(0, 3)
    goal = Goal()
    steps = [StepBeginEnd(1, 3)]
    ActionService.add_freezes(goal, steps)
    assert goal.action_list == [['Pass'], ['Pass']]
    steps = [SidestepsConfig(begin=1, object_label='object', degrees=90)]
    with pytest.raises(ILEException):
        ActionService.add_sidesteps(goal, steps, scene)
    steps = [SidestepsConfig(begin=1, object_label='object', degrees=-90)]
    with pytest.raises(ILEException):
        ActionService.add_sidesteps(goal, steps, scene)


def test_action_sidesteps_overlap_error():
    scene = create_test_obj_scene(0, 3)
    goal = Goal()
    steps = [
        SidestepsConfig(
            begin=1,
            object_label='object',
            degrees=90),
        SidestepsConfig(
            begin=58,
            object_label='object',
            degrees=-90)]
    with pytest.raises(ILEException):
        ActionService.add_sidesteps(goal, steps, scene)


def test_action_sidesteps_too_short_distance_error():
    scene = create_test_obj_scene(0, 2.9)
    goal = Goal()
    steps = [
        SidestepsConfig(
            begin=1,
            object_label='object',
            degrees=90)]
    with pytest.raises(ILEException):
        ActionService.add_sidesteps(goal, steps, scene)


def test_action_sidesteps_wrong_labels_error():
    scene = create_test_obj_scene(0, 3)
    goal = Goal()
    steps = [
        SidestepsConfig(
            begin=1,
            object_label='object',
            degrees=90),
        SidestepsConfig(
            begin=100,
            object_label='not_object',
            degrees=-90)]
    with pytest.raises(ILEException):
        ActionService.add_sidesteps(goal, steps, scene)


def test_action_sidesteps_bad_angle():
    scene = create_test_obj_scene(0, 3)
    goal = Goal()
    steps = [
        SidestepsConfig(
            begin=1,
            object_label='object',
            degrees=91)]
    with pytest.raises(ILEException):
        ActionService.add_sidesteps(goal, steps, scene)
    goal = Goal()
    steps = [
        SidestepsConfig(
            begin=1,
            object_label='object',
            degrees=-91)]
    with pytest.raises(ILEException):
        ActionService.add_sidesteps(goal, steps, scene)


def test_action_sidesteps_no_degrees():
    scene = create_test_obj_scene(0, 3)
    goal = Goal()
    steps = [
        SidestepsConfig(
            begin=1,
            object_label='object')
    ]
    ActionService.add_sidesteps(goal, steps, scene)
    for action in goal.action_list:
        assert action in [
            ["MoveRight"],
            ["MoveLeft"],
            ["RotateRight"],
            ["RotateLeft"]
        ]


def test_action_freeze_while_moving_empty_array():
    goal = Goal()
    ActionService.add_freeze_while_moving(goal, [])
    assert goal.action_list == []


def test_action_freeze_while_moving_moves_rotates():
    scene = create_placers_turntables_scene(20, 1)
    goal = Goal()
    freeze_while_moving = ['placers', 'turntables']
    ActionService.add_freeze_while_moving(goal, freeze_while_moving)
    moves = \
        max(scene.objects[1:-1],
            key=lambda x: 0 if not x.get('moves') else
            x['moves'][-1]['stepEnd'])['moves'][-1]['stepEnd']
    assert len(goal.action_list) == moves

    scene = create_placers_turntables_scene(1, 20)
    goal = Goal()
    freeze_while_moving = ['placers', 'turntables']
    ActionService.add_freeze_while_moving(goal, freeze_while_moving)
    assert \
        len(goal.action_list) == scene.objects[-1]['rotates'][-1]['stepEnd']


def test_action_freeze_while_moving_actions():
    scene = create_agent_scene()
    goal = Goal()
    freeze_while_moving = ['agent']
    ActionService.add_freeze_while_moving(goal, freeze_while_moving)
    actions = scene.objects[0]['actions']
    actions_max_step_end = \
        max(item['stepEnd'] for item in actions if not item.get(
            'isLoopAnimation', False))
    assert len(goal.action_list) == actions_max_step_end


def test_action_freeze_while_moving_actions_multiple_agents():
    number_of_agents = random.randint(2, 10)
    scene = create_agent_scene(number_of_agents)
    goal = Goal()
    freeze_while_moving = ['agent']
    ActionService.add_freeze_while_moving(goal, freeze_while_moving)
    action_lists = [agent['actions'] for agent in scene.objects]
    actions_max_step_end = max(
        item['stepEnd'] for action_list in action_lists
        for item in action_list if not item.get('isLoopAnimation', False))
    assert len(goal.action_list) == actions_max_step_end


def test_action_freeze_while_moving_agents_placers_and_turntables_random():
    scene = create_random_agent_placer_turntable_scene()
    goal = Goal()
    freeze_while_moving = ['agent', 'placers', 'turntables']
    ActionService.add_freeze_while_moving(goal, freeze_while_moving)

    action_lists = [
        obj.get('actions') for obj in scene.objects if
        obj.get('actions') is not None]
    moves_lists = [
        obj.get('moves') for obj in scene.objects if
        obj.get('moves') is not None]
    rotates_lists = [
        obj.get('rotates') for obj in scene.objects if
        obj.get('rotates') is not None]  # noqa

    actions_max_step_end = max(
        item['stepEnd'] for action_list in action_lists
        for item in action_list if not item.get('isLoopAnimation', False))
    moves_max_step_end = max(
        move['stepEnd'] for moves in moves_lists for move in moves)
    rotates_max_step_end = max(
        rotate['stepEnd'] for rotates in rotates_lists for rotate in rotates)

    assert len(
        goal.action_list) == max(
        actions_max_step_end,
        moves_max_step_end,
        rotates_max_step_end)


def test_action_freeze_while_moving_agents_placers_and_turntables_agents():
    scene = create_specific_agent_placer_turntable_scene(
        agent_start=100, placer_start=50, turntable_start=10)
    goal = Goal()
    freeze_while_moving = ['agent', 'placers', 'turntables']
    ActionService.add_freeze_while_moving(goal, freeze_while_moving)
    action_lists = [
        obj.get('actions') for obj in scene.objects if
        obj.get('actions') is not None]
    actions_max_step_end = max(
        item['stepEnd'] for action_list in action_lists
        for item in action_list if not item.get('isLoopAnimation', False))
    assert len(goal.action_list) == actions_max_step_end


def test_action_freeze_while_moving_agents_placers_and_turntables_placers():
    scene = create_specific_agent_placer_turntable_scene(
        agent_start=10, placer_start=100, turntable_start=50)
    goal = Goal()
    freeze_while_moving = ['agent', 'placers', 'turntables']
    ActionService.add_freeze_while_moving(goal, freeze_while_moving)
    moves_lists = [obj.get('moves')
                   for obj in scene.objects if obj.get('moves') is not None]
    moves_max_step_end = max(
        move['stepEnd'] for moves in moves_lists for move in moves)
    assert len(goal.action_list) == moves_max_step_end


def test_action_freeze_while_moving_agents_placers_and_turntables_turntables():
    scene = create_specific_agent_placer_turntable_scene(
        agent_start=10, placer_start=50, turntable_start=100)
    goal = Goal()
    freeze_while_moving = ['agent', 'placers', 'turntables']
    ActionService.add_freeze_while_moving(goal, freeze_while_moving)
    rotates_lists = [
        obj.get('rotates') for obj in scene.objects if
        obj.get('rotates') is not None]
    rotates_max_step_end = max(
        rotate['stepEnd'] for rotates in rotates_lists for rotate in rotates)
    assert len(goal.action_list) == rotates_max_step_end
