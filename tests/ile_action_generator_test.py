import pytest

from ideal_learning_env.action_generator import StepBeginEnd, add_freezes
from ideal_learning_env.defs import ILEException


def test_action_freezes_empty_array():
    goal = {}
    add_freezes(goal, [])
    assert goal['action_list'] == []


def test_action_freezes_single():
    goal = {}
    steps = [StepBeginEnd(1, 3)]
    add_freezes(goal, steps)
    assert goal['action_list'] == [['Pass'], ['Pass']]


def test_action_freezes_multiple():
    goal = {}
    steps = [StepBeginEnd(2, 3), StepBeginEnd(5, 6)]
    add_freezes(goal, steps)
    assert goal['action_list'] == [[], ['Pass'], [], [], ['Pass']]


def test_action_freezes_bad_setp():
    goal = {}
    steps = [StepBeginEnd(3, 1)]
    with pytest.raises(ILEException):
        add_freezes(goal, steps)


def test_action_freezes_overlap():
    goal = {}
    steps = [StepBeginEnd(1, 3), StepBeginEnd(2, 4)]
    with pytest.raises(ILEException):
        add_freezes(goal, steps)
