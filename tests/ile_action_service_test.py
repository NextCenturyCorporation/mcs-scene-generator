import pytest

from ideal_learning_env.action_service import (
    ActionService,
    StepBeginEnd,
    TeleportConfig
)
from ideal_learning_env.defs import ILEException


def test_action_freezes_empty_array():
    goal = {}
    ActionService.add_freezes(goal, [])
    assert goal['action_list'] == []


def test_action_freezes_single():
    goal = {}
    steps = [StepBeginEnd(1, 3)]
    ActionService.add_freezes(goal, steps)
    assert goal['action_list'] == [['Pass'], ['Pass']]


def test_action_freezes_multiple():
    goal = {}
    steps = [StepBeginEnd(2, 3), StepBeginEnd(5, 6)]
    ActionService.add_freezes(goal, steps)
    assert goal['action_list'] == [[], ['Pass'], [], [], ['Pass']]


def test_action_freezes_bad_step():
    goal = {}
    steps = [StepBeginEnd(3, 1)]
    with pytest.raises(ILEException):
        ActionService.add_freezes(goal, steps)


def test_action_freezes_overlap():
    goal = {}
    steps = [StepBeginEnd(1, 3), StepBeginEnd(2, 4)]
    with pytest.raises(ILEException):
        ActionService.add_freezes(goal, steps)


def test_action_teleports_empty_array():
    goal = {}
    ActionService.add_teleports(goal, [], False)
    assert goal['action_list'] == []


def test_action_teleports_single():
    goal = {}
    teleports = [TeleportConfig(2, 3, 4, 90)]
    ActionService.add_teleports(goal, teleports, False)
    al = goal['action_list']
    assert al
    assert len(al) == 2
    action = al[1]
    assert action == ['EndHabituation,xPosition=3,zPosition=4,yRotation=90']


def test_action_teleports_multiple():
    goal = {}
    teleports = [TeleportConfig(1, -2, 1, 180), TeleportConfig(3, 2, -1, 270)]
    ActionService.add_teleports(goal, teleports, False)
    al = goal['action_list']
    assert al
    assert len(al) == 3
    action = al[0]
    assert action == ['EndHabituation,xPosition=-2,zPosition=1,yRotation=180']
    action = al[2]
    assert action == ['EndHabituation,xPosition=2,zPosition=-1,yRotation=270']


def test_action_teleports_multiple_out_of_order():
    goal = {}
    teleports = [TeleportConfig(3, -2, 1, 180), TeleportConfig(1, 2, -1, 270)]
    ActionService.add_teleports(goal, teleports, False)
    al = goal['action_list']
    assert al
    assert len(al) == 3
    action = al[0]
    assert action == ['EndHabituation,xPosition=2,zPosition=-1,yRotation=270']
    action = al[2]
    assert action == ['EndHabituation,xPosition=-2,zPosition=1,yRotation=180']


def test_action_teleports_look_at_center_facing_front():
    goal = {}
    teleports = [TeleportConfig(1, 0, -7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=0,zPosition=-7.5,yRotation=0']

    goal = {}
    teleports = [TeleportConfig(1, 0.25, -7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=0.25,zPosition=-7.5,yRotation=0']

    goal = {}
    teleports = [TeleportConfig(1, -0.25, -7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=-0.25,zPosition=-7.5,yRotation=0']


def test_action_teleports_look_at_center_facing_back():
    goal = {}
    teleports = [TeleportConfig(1, 0, 7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=0,zPosition=7.5,yRotation=180']

    goal = {}
    teleports = [TeleportConfig(1, 0.25, 7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=0.25,zPosition=7.5,yRotation=180']

    goal = {}
    teleports = [TeleportConfig(1, -0.25, 7.5, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert (
        cmd == ['EndHabituation,xPosition=-0.25,zPosition=7.5,yRotation=180']
    )


def test_action_teleports_look_at_center_facing_left():
    goal = {}
    teleports = [TeleportConfig(1, 7.5, 0, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=7.5,zPosition=0,yRotation=270']

    goal = {}
    teleports = [TeleportConfig(1, 7.5, 0.25, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=7.5,zPosition=0.25,yRotation=270']

    goal = {}
    teleports = [TeleportConfig(1, 7.5, -0.25, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert (
        cmd == ['EndHabituation,xPosition=7.5,zPosition=-0.25,yRotation=270']
    )


def test_action_teleports_look_at_center_facing_right():
    goal = {}
    teleports = [TeleportConfig(1, -7.5, 0, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=-7.5,zPosition=0,yRotation=90']

    goal = {}
    teleports = [TeleportConfig(1, -7.5, 0.25, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=-7.5,zPosition=0.25,yRotation=90']

    goal = {}
    teleports = [TeleportConfig(1, -7.5, -0.25, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert (
        cmd == ['EndHabituation,xPosition=-7.5,zPosition=-0.25,yRotation=90']
    )


def test_action_teleports_look_at_center_rounds_to_tens():
    goal = {}
    teleports = [TeleportConfig(1, 2, 2, None, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=2,zPosition=2,yRotation=220']


def test_action_teleports_look_at_center_ignores_rotation_y():
    goal = {}
    teleports = [TeleportConfig(1, 0, 7.5, 90, look_at_center=True)]
    ActionService.add_teleports(goal, teleports, False)
    assert len(goal['action_list']) == 1
    cmd = goal['action_list'][0]
    assert cmd == ['EndHabituation,xPosition=0,zPosition=7.5,yRotation=180']


def test_action_circles_empty_array():
    goal = {}
    ActionService.add_circles(goal, [])
    assert goal['action_list'] == []


def test_action_circles_single():
    goal = {}
    ActionService.add_circles(goal, [1])
    circle = ['RotateRight']
    assert goal['action_list'] == [circle] * 36


def test_action_circles_multiple():
    goal = {}
    ActionService.add_circles(goal, [1, 101])
    circle = ['RotateRight']
    assert goal['action_list'] == [circle] * 36 + [[]] * 64 + [circle] * 36


def test_action_swivels_empty_array():
    goal = {}
    ActionService.add_swivels(goal, [])
    assert goal['action_list'] == []


def test_action_swivels_single():
    goal = {}
    steps = [StepBeginEnd(3, 5)]
    ActionService.add_swivels(goal, steps)
    swivel = ['LookDown', 'LookUp', 'RotateLeft', 'RotateRight']
    assert goal['action_list'] == [[], [], swivel, swivel]


def test_action_swivels_multiple():
    goal = {}
    steps = [StepBeginEnd(1, 2), StepBeginEnd(4, 6)]
    ActionService.add_swivels(goal, steps)
    swivel = ['LookDown', 'LookUp', 'RotateLeft', 'RotateRight']
    assert goal['action_list'] == [swivel, [], [], swivel, swivel]


def test_action_swivels_bad_step():
    goal = {}
    steps = [StepBeginEnd(5, 2)]
    with pytest.raises(ILEException):
        ActionService.add_swivels(goal, steps)


def test_action_swivels_overlap():
    goal = {}
    steps = [StepBeginEnd(3, 5), StepBeginEnd(4, 7)]
    with pytest.raises(ILEException):
        ActionService.add_swivels(goal, steps)
