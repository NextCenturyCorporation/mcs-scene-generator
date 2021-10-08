import pytest

from ideal_learning_env.actions_component import ActionRestrictionsComponent
from ideal_learning_env.defs import ILEConfigurationException, ILEException


def prior_scene(last_step: int = None):
    scene = {
        'debug': {},
        'goal': {},
        'performerStart':
        {
            'position':
            {'x': 0, 'y': 0, 'z': 0}
        },
        'roomDimensions': {'x': 10, 'y': 3, 'z': 10}
    }
    if last_step:
        scene['goal']['last_step'] = last_step
    return scene


def test_action_restrictions_defaults():
    component = ActionRestrictionsComponent({})
    assert component.passive_scene is None
    assert component.freezes is None
    assert component.teleports is None

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    assert not hasattr(goal, 'action_list')


def test_action_restrictions_passive():
    component = ActionRestrictionsComponent({
        'passive_scene': True
    })
    assert isinstance(component.passive_scene, bool)
    assert component.passive_scene
    last_step = 100
    scene = component.update_ile_scene(prior_scene(last_step))
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == last_step
    for inner in al:
        assert isinstance(inner, list)
        assert len(inner) == 1
        assert inner[0] == 'Pass'


def test_action_restrictions_freeze_start():
    start_step = 2
    component = ActionRestrictionsComponent({
        'freezes': [
            {
                'begin': start_step
            }]
    })
    fzs = component.get_freezes()
    assert isinstance(fzs, list)
    assert fzs[0].begin == start_step
    assert fzs[0].end is None

    scene = component.update_ile_scene(prior_scene(100))
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == 100
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        # Minux 1 for ordinal to index fix.
        if idx >= start_step - 1:
            assert len(inner) == 1
            assert inner[0] == 'Pass'
        else:
            assert len(inner) == 0


def test_action_restrictions_freeze_start_end():
    start_step = 4
    end_step = 8
    component = ActionRestrictionsComponent({
        'freezes': [
            {
                'begin': start_step,
                'end': end_step
            }]
    })
    fzs = component.get_freezes()
    assert isinstance(fzs, list)
    assert fzs[0].begin == start_step
    assert fzs[0].end == end_step

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == end_step - 1
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        if start_step - 1 <= idx < end_step - 1:
            assert len(inner) == 1
            assert inner[0] == 'Pass'
        else:
            assert len(inner) == 0


def test_action_restrictions_freeze_choice():
    component = ActionRestrictionsComponent({
        'freezes': [[
            {
                'begin': 1,
                'end': 2
            },
            {
                'begin': 3,
                'end': 4
            },
            {
                'begin': 5,
                'end': 6
            }
        ]]
    })
    fzs = component.get_freezes()
    assert isinstance(fzs, list)
    choice = [1, 3, 5].index(fzs[0].begin)
    # Choice is the index of the choice used so we can test consistency
    start = [1, 3, 5][choice]
    end = [2, 4, 6][choice]
    assert fzs[0].begin == start
    assert fzs[0].end == end

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    choice = [1, 3, 5].index(len(al))
    start = [1, 3, 5][choice]
    end = [2, 4, 6][choice]

    assert len(al) == start
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        if start - 1 <= idx < end - 1:
            assert len(inner) == 1
            assert inner[0] == 'Pass'
        else:
            assert len(inner) == 0


def test_action_restrictions_freeze_ok_overlap():
    start_step = 4
    mid = 6
    end_step = 8
    component = ActionRestrictionsComponent({
        'freezes': [
            {
                'begin': start_step,
                'end': mid
            }, {
                'begin': mid,
                'end': end_step
            }]
    })
    fzs = component.get_freezes()
    assert isinstance(fzs, list)
    assert fzs[0].begin == start_step
    assert fzs[0].end == mid
    assert fzs[1].begin == mid
    assert fzs[1].end == end_step

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == end_step - 1
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        if start_step - 1 <= idx < end_step - 1:
            assert len(inner) == 1
            assert inner[0] == 'Pass'
        else:
            assert len(inner) == 0


def test_action_restrictions_freeze_gap():
    start_step = 2
    mid1 = 4
    mid2 = 8
    end_step = 12
    component = ActionRestrictionsComponent({
        'freezes': [
            {
                'begin': start_step,
                'end': mid1
            }, {
                'begin': mid2,
                'end': end_step
            }]
    })
    fzs = component.get_freezes()
    assert isinstance(fzs, list)
    assert fzs[0].begin == start_step
    assert fzs[0].end == mid1
    assert fzs[1].begin == mid2
    assert fzs[1].end == end_step

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == end_step - 1
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        if start_step - 1 <= idx < mid1 - 1 or mid2 - 1 <= idx < end_step - 1:
            assert len(inner) == 1
            assert inner[0] == 'Pass'
        else:
            assert len(inner) == 0


def test_action_restrictions_freeze_bad_overlap():
    start_step = 2
    mid = 6
    end_step = 10
    component = ActionRestrictionsComponent({
        'freezes': [
            {
                'begin': start_step,
                'end': mid + 1
            }, {
                'begin': mid - 1,
                'end': end_step
            }]
    })
    fzs = component.get_freezes()
    assert isinstance(fzs, list)
    assert fzs[0].begin == start_step
    assert fzs[0].end == mid + 1
    assert fzs[1].begin == mid - 1
    assert fzs[1].end == end_step

    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene())


def test_action_restrictions_freeze_just_end():
    end_step = 3
    component = ActionRestrictionsComponent({
        'freezes': [
            {
                'end': end_step
            }]
    })
    fzs = component.get_freezes()
    assert isinstance(fzs, list)
    assert fzs[0].begin is None
    assert fzs[0].end == end_step

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == end_step - 1
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        # minux 2 is 1 for ordinal to index and 1 for exclusiveness of end
        if idx <= end_step - 2:
            assert len(inner) == 1
            assert inner[0] == 'Pass'
        else:
            assert len(inner) == 0


def test_action_restrictions_freeze_missing_start_and_end():
    component = ActionRestrictionsComponent({
        'freezes': [
            {}]
    })
    fzs = component.get_freezes()
    assert isinstance(fzs, list)
    assert fzs[0].begin is None
    assert fzs[0].end is None

    with pytest.raises(ILEConfigurationException):
        component.update_ile_scene(prior_scene())


def test_action_restrictions_freeze_empty_list():
    component = ActionRestrictionsComponent({
        'freezes': [
        ]
    })
    fzs = component.get_freezes()
    assert isinstance(fzs, list)
    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    assert not hasattr(goal, 'action_list')


def test_action_restriction_teleport_missing_step():
    with pytest.raises(ILEException):
        ActionRestrictionsComponent({
            'teleports': [{
                'position_x': 1,
                'position_z': 2,
                'rotation_y': 30
            }]
        })


def test_action_restriction_teleport_missing_pos_x():
    step = 8
    component = ActionRestrictionsComponent({
        'teleports': [{
            'step': step,
            'position_z': 2,
            'rotation_y': 30
        }]
    })

    tps = component.get_teleports()
    assert isinstance(tps, list)
    assert tps[0].step == step
    assert tps[0].position_x is None
    assert tps[0].position_z == 2
    assert tps[0].rotation_y == 30

    with pytest.raises(ILEConfigurationException):
        component.update_ile_scene(prior_scene())


def test_action_restriction_teleport_missing_pos_z():
    step = 8
    component = ActionRestrictionsComponent({
        'teleports': [{
            'step': step,
            'position_x': 2,
            'rotation_y': 30
        }]
    })

    tps = component.get_teleports()
    assert isinstance(tps, list)
    assert tps[0].step == step
    assert tps[0].position_z is None
    assert tps[0].position_x == 2
    assert tps[0].rotation_y == 30

    with pytest.raises(ILEConfigurationException):
        component.update_ile_scene(prior_scene())


def test_action_restriction_teleport_missing_rot_y():
    step = 8
    component = ActionRestrictionsComponent({
        'teleports': [{
            'step': step,
            'position_x': 2,
            'position_z': 3
        }]
    })

    tps = component.get_teleports()
    assert isinstance(tps, list)
    assert tps[0].step == step
    assert tps[0].position_z == 3
    assert tps[0].position_x == 2
    assert tps[0].rotation_y is None

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == step
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        # minux 2 is 1 for ordinal to index and 1 for exclusiveness of end
        if idx == step - 1:
            assert len(inner) == 1
            assert inner[0] == "EndHabituation,xPosition=2,zPosition=3"
        else:
            assert len(inner) == 0


def test_action_restriction_teleport():
    step = 3

    component = ActionRestrictionsComponent({
        'teleports': [{
            'step': step,
            'position_x': 1,
            'position_z': 2,
            'rotation_y': 45
        }]
    })

    tps = component.get_teleports()
    assert isinstance(tps, list)
    assert tps[0].step == step
    assert tps[0].position_x == 1
    assert tps[0].position_z == 2
    assert tps[0].rotation_y == 45

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == step
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        if step - 1 == idx:
            teleport_pos = 'EndHabituation,xPosition=1,zPosition=2,yRotation=45'  # noqa: E501
            assert len(inner) == 1
            assert inner[0] == teleport_pos
        else:
            assert len(inner) == 0


def test_action_restriction_teleport_choice():
    component = ActionRestrictionsComponent({
        'teleports': [[{
            'step': 3,
            'position_x': 1,
            'position_z': 2,
            'rotation_y': 45
        }, {
            'step': 6,
            'position_x': 2,
            'position_z': 4,
            'rotation_y': 90
        }]]
    })

    tps = component.get_teleports()
    assert isinstance(tps, list)
    assert tps[0].step in [3, 6]
    assert tps[0].position_x in [1, 2]
    assert tps[0].position_z in [2, 4]
    assert tps[0].rotation_y in [45, 90]

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) in [3, 6]
    num_end_hab = 0
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        if idx in [2, 5] and len(inner) == 1:
            teleport_pos = [
                'EndHabituation,xPosition=1,zPosition=2,yRotation=45',
                'EndHabituation,xPosition=2,zPosition=4,yRotation=90'
            ]
            num_end_hab += 1
            assert inner[0] in teleport_pos
        else:
            assert len(inner) == 0
    assert num_end_hab == 1


def test_action_restriction_teleport_multi():
    step1 = 3
    step2 = 5
    step3 = 9

    component = ActionRestrictionsComponent({
        'teleports': [{
            'step': step1,
            'position_x': 1,
            'position_z': 2,
            'rotation_y': 45
        }, {
            'step': step2,
            'rotation_y': 90
        }, {
            'step': step3,
            'position_x': -3,
            'position_z': -1
        }]
    })

    tps = component.get_teleports()
    assert isinstance(tps, list)
    assert tps[0].step == step1
    assert tps[0].position_x == 1
    assert tps[0].position_z == 2
    assert tps[0].rotation_y == 45

    assert tps[1].step == step2
    assert tps[1].position_x is None
    assert tps[1].position_z is None
    assert tps[1].rotation_y == 90

    assert tps[2].step == step3
    assert tps[2].position_x == -3
    assert tps[2].position_z == -1
    assert tps[2].rotation_y is None

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == step3
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        if step1 - 1 == idx:
            teleport_pos = 'EndHabituation,xPosition=1,zPosition=2,yRotation=45'  # noqa: E501
            assert len(inner) == 1
            assert inner[0] == teleport_pos
        elif step2 - 1 == idx:
            teleport_pos = 'EndHabituation,yRotation=90'
            assert len(inner) == 1
            assert inner[0] == teleport_pos
        elif step3 - 1 == idx:
            teleport_pos = 'EndHabituation,xPosition=-3,zPosition=-1'  # noqa: E501
            assert len(inner) == 1
            assert inner[0] == teleport_pos
        else:
            assert len(inner) == 0


def test_action_restriction_teleport_multi_overwrite_error():
    step = 2

    component = ActionRestrictionsComponent({
        'teleports': [{
            'step': step,
            'position_x': 1,
            'position_z': 2,
            'rotation_y': 45
        }, {
            'step': step,
            'rotation_y': 90
        }]
    })

    tps = component.get_teleports()
    assert isinstance(tps, list)
    assert tps[0].step == step
    assert tps[0].position_x == 1
    assert tps[0].position_z == 2
    assert tps[0].rotation_y == 45

    assert tps[1].step == step
    assert tps[1].position_x is None
    assert tps[1].position_z is None
    assert tps[1].rotation_y == 90

    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene())


def test_action_restriction_freeze_teleport_combined():
    tstep = 2
    start = 5
    end = 8
    component = ActionRestrictionsComponent({
        'teleports': [{
            'step': tstep,
            'position_x': 1,
            'position_z': 2,
            'rotation_y': 45
        }],
        'freezes': [
            {
                'begin': start,
                'end': end
            }
        ]
    })

    tps = component.get_teleports()
    assert isinstance(tps, list)
    assert tps[0].step == tstep
    assert tps[0].position_x == 1
    assert tps[0].position_z == 2
    assert tps[0].rotation_y == 45

    fzs = component.get_freezes()
    assert fzs[0].begin == start
    assert fzs[0].end == end

    scene = component.update_ile_scene(prior_scene())
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == max(end - 1, tstep)
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        if tstep - 1 == idx:
            teleport_pos = 'EndHabituation,xPosition=1,zPosition=2,yRotation=45'  # noqa: E501
            assert len(inner) == 1
            assert inner[0] == teleport_pos
        elif start - 1 <= idx < end:
            assert len(inner) == 1
            assert inner[0] == 'Pass'
        else:
            assert len(inner) == 0


def test_action_restriction_freeze_teleport_overwrite_error():
    step = 2

    component = ActionRestrictionsComponent({
        'teleports': [{
            'step': step,
            'position_x': 1,
            'position_z': 2,
            'rotation_y': 45
        }],
        'freezes': [
            {
                'begin': step,
                'end': step + 3
            }
        ]
    })

    tps = component.get_teleports()
    assert isinstance(tps, list)
    assert tps[0].step == step
    assert tps[0].position_x == 1
    assert tps[0].position_z == 2
    assert tps[0].rotation_y == 45

    fzs = component.get_freezes()
    assert fzs[0].begin == step
    assert fzs[0].end == step + 3

    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene())


def test_action_restriction_passive_teleport():
    step = 2

    component = ActionRestrictionsComponent({
        'passive_scene': True,
        'teleports': [{
            'step': step,
            'position_x': 1,
            'position_z': 2,
            'rotation_y': 45
        }]
    })

    tps = component.get_teleports()
    assert isinstance(tps, list)
    assert tps[0].step == step
    assert tps[0].position_x == 1
    assert tps[0].position_z == 2
    assert tps[0].rotation_y == 45

    assert component.get_passive_scene()

    scene = component.update_ile_scene(prior_scene(100))
    goal = scene['goal']
    assert isinstance(goal, dict)
    al = goal['action_list']
    assert isinstance(al, list)
    assert len(al) == 100
    for idx, inner in enumerate(al):
        assert isinstance(inner, list)
        if step - 1 == idx:
            teleport_pos = 'EndHabituation,xPosition=1,zPosition=2,yRotation=45'  # noqa: E501
            assert inner[0] == teleport_pos
        else:
            assert inner[0] == 'Pass'
        assert len(inner) == 1


def test_action_restriction_passive_freeze_error():
    step = 2

    component = ActionRestrictionsComponent({
        'passive_scene': True,
        'freezes': [
            {
                'begin': step,
                'end': step + 3
            }
        ]
    })

    assert component.get_passive_scene()

    fzs = component.get_freezes()
    assert fzs[0].begin == step
    assert fzs[0].end == step + 3

    with pytest.raises(ILEConfigurationException):
        component.update_ile_scene(prior_scene(100))
