import pytest
from machine_common_sense.config_manager import Vector3d

from generator import (
    MaterialTuple,
    ObjectBounds,
    exceptions,
    geometry,
    materials,
)
from hypercube import hypercubes
from hypercube.agent_scene_pair_json_converter import (
    AGENT_OBJECT_MATERIAL_LIST,
    GOAL_OBJECT_MATERIAL_LIST,
    ObjectConfig,
    ObjectConfigWithMaterial,
    _append_each_show_to_object,
    _choose_config_list,
    _create_action_list,
    _create_agent_object_list,
    _create_fuse_wall_object_list,
    _create_goal_object_list,
    _create_home_object,
    _create_key_object,
    _create_lock_wall_object_list,
    _create_object,
    _create_scene,
    _create_show,
    _create_static_wall_object_list,
    _create_trial_frame_list,
    _create_wall_object_list,
    _fix_key_location,
    _identify_trial_index_starting_step,
    _move_agent_past_lock_location,
    _remove_extraneous_object_show,
    _remove_intersecting_agent_steps,
    _retrieve_unit_size,
)

UNIT_SIZE = [0.025, 0.025]


def create_bounds(x1, x2, z1, z2):
    return ObjectBounds(box_xz=[
        Vector3d(x=x, y=0, z=z) for x, z in [(x1, z1), (x1, z2),
                                             (x2, z2), (x2, z1)]
    ], max_y=0, min_y=0)


def verify_bounds(mcs_object, step, x1, x2, z1, z2):
    bounds_at_step = mcs_object['debug']['boundsAtStep'][step].box_xz
    assert bounds_at_step[0].x == pytest.approx(x1)
    assert bounds_at_step[0].z == pytest.approx(z1)
    assert bounds_at_step[1].x == pytest.approx(x1)
    assert bounds_at_step[1].z == pytest.approx(z2)
    assert bounds_at_step[2].x == pytest.approx(x2)
    assert bounds_at_step[2].z == pytest.approx(z2)
    assert bounds_at_step[3].x == pytest.approx(x2)
    assert bounds_at_step[3].z == pytest.approx(z1)


def verify_key_properties(key_object):
    assert key_object['id'].startswith('key_')
    assert key_object['type'] == 'triangle'
    assert key_object['materials'] == ['Custom/Materials/Maroon']
    assert key_object['kinematic']
    assert not key_object.get('structure')
    assert key_object['debug']['info'] == [
        'maroon', 'triangle', 'maroon triangle'
    ]
    assert key_object['debug']['configHeight'] == [0.06, 0.35]
    assert key_object['debug']['configSize'] == [0.12, 0.35]
    verify_key_show(key_object)


def verify_key_show(key_object):
    assert len(key_object['shows']) >= 1
    for index, show in enumerate(key_object['shows']):
        assert show['rotation']['x'] == 0
        assert show['rotation']['z'] == 90
        if index == 0:
            assert show['scale']['x'] == 0.12
            assert show['scale']['y'] == 0.35
            assert show['scale']['z'] == 0.35
        else:
            assert 'scale' not in show


def verify_lock_properties(lock_object):
    assert lock_object['id'].startswith('lock_')
    assert lock_object['type'] == 'lock_wall'
    assert lock_object['materials'] == ['Custom/Materials/Lime']
    assert lock_object['kinematic']
    assert lock_object['structure']
    assert lock_object['debug']['info'] == [
        'lime', 'lock_wall', 'lime lock_wall'
    ]
    assert lock_object['debug']['configHeight'] == [0.06, 0.12]
    assert lock_object['debug']['configSize'] == [0.5, 0.5]

    assert len(lock_object['shows']) == 1
    assert lock_object['shows'][0]['rotation']['x'] == 0
    assert lock_object['shows'][0]['rotation']['z'] == 0
    assert lock_object['shows'][0]['scale']['x'] == 0.5
    assert lock_object['shows'][0]['scale']['y'] == 0.12
    assert lock_object['shows'][0]['scale']['z'] == 0.5


def verify_show(mcs_object, index, step, x, y, z):
    assert mcs_object['shows'][index]['stepBegin'] == step
    assert mcs_object['shows'][index]['position']['x'] == x
    assert mcs_object['shows'][index]['position']['y'] == y
    assert mcs_object['shows'][index]['position']['z'] == z
    if index > 0:
        assert 'scale' not in mcs_object['shows'][index]


def append_json_border_wall(json_list):
    # Add each border wall to verify that they won't be in the output list.
    for i in range(0, 200, 20):
        json_list.extend([
            [[0, i], [20, 20]],
            [[i, 0], [20, 20]],
            [[180, i], [20, 20]],
            [[i, 180], [20, 20]]
        ])
    return json_list


def create_wall_json_list(ignore_border=False):
    json_list = [
        [[20, 20], [20, 20]],
        [[20, 160], [20, 20]],
        [[160, 20], [20, 20]],
        [[160, 160], [20, 20]],
        [[90, 90], [20, 20]]
    ]
    return json_list if ignore_border else append_json_border_wall(json_list)


def create_wall_json_list_variation_2(ignore_border=False):
    json_list = [
        [[40, 40], [20, 20]],
        [[140, 140], [20, 20]],
        [[90, 90], [20, 20]]
    ]
    return json_list if ignore_border else append_json_border_wall(json_list)


def verify_fuse_wall_list_trial_1(wall_object_list):
    verify_show(wall_object_list[0], 0, 0, -1.75, 0.06, -1.75)
    verify_show(wall_object_list[1], 0, 0, -1.75, 0.06, 1.75)
    verify_show(wall_object_list[2], 0, 0, 1.75, 0.06, -1.75)
    verify_show(wall_object_list[3], 0, 0, 1.75, 0.06, 1.75)
    verify_show(wall_object_list[4], 0, 0, 0, 0.06, 0)

    for wall_object in wall_object_list:
        assert wall_object['id'].startswith('fuse_wall_')
        assert wall_object['type'] == 'cube'
        assert wall_object['materials'] == ['Custom/Materials/Lime']
        assert wall_object['kinematic']
        assert wall_object['structure']
        assert wall_object['debug']['info'] == ['lime', 'cube', 'lime cube']
        assert wall_object['debug']['configHeight'] == [0.06, 0.12]
        assert wall_object['debug']['configSize'] == [0.5, 0.5]

        assert len(wall_object['shows']) == 1
        assert wall_object['shows'][0]['scale']['x'] == 0.5
        assert wall_object['shows'][0]['scale']['y'] == 0.12
        assert wall_object['shows'][0]['scale']['z'] == 0.5

        assert len(wall_object['hides']) == 1

    assert wall_object_list[0]['hides'][0]['stepBegin'] == 4
    assert wall_object_list[1]['hides'][0]['stepBegin'] == 4
    assert wall_object_list[2]['hides'][0]['stepBegin'] == 3
    assert wall_object_list[3]['hides'][0]['stepBegin'] == 3
    assert wall_object_list[4]['hides'][0]['stepBegin'] == 2


def verify_border_wall_list(wall_object_list):
    assert len(wall_object_list) == 4
    verify_show(wall_object_list[0], 0, 0, 0, 0.0625, 2.25)
    verify_show(wall_object_list[1], 0, 0, 0, 0.0625, -2.25)
    verify_show(wall_object_list[2], 0, 0, -2.25, 0.0625, 0)
    verify_show(wall_object_list[3], 0, 0, 2.25, 0.0625, 0)
    verify_static_wall_list_properties(wall_object_list[0:1], scale_x=5)
    verify_static_wall_list_properties(wall_object_list[1:2], scale_x=5)
    verify_static_wall_list_properties(wall_object_list[2:3], scale_z=4)
    verify_static_wall_list_properties(wall_object_list[3:4], scale_z=4)


def verify_fuse_wall_list_trial_2(wall_object_list):
    verify_show(wall_object_list[5], 0, 7, -1.25, 0.06, -1.25)
    verify_show(wall_object_list[6], 0, 7, 1.25, 0.06, 1.25)
    verify_show(wall_object_list[7], 0, 7, 0, 0.06, 0)
    assert wall_object_list[5]['hides'][0]['stepBegin'] == 10
    assert wall_object_list[6]['hides'][0]['stepBegin'] == 9
    assert wall_object_list[7]['hides'][0]['stepBegin'] == 8


def verify_static_wall_list(
    wall_object_list,
    hidden_step=-1,
    list_length=5,
    show_step=0
):
    assert len(wall_object_list) == list_length
    verify_show(wall_object_list[0], 0, show_step, -1.75, 0.0625, -1.75)
    verify_show(wall_object_list[1], 0, show_step, -1.75, 0.0625, 1.75)
    verify_show(wall_object_list[2], 0, show_step, 1.75, 0.0625, -1.75)
    verify_show(wall_object_list[3], 0, show_step, 1.75, 0.0625, 1.75)
    if list_length > 4:
        verify_show(wall_object_list[4], 0, 0, 0, 0.0625, 0)
    if list_length > 5:
        print(
            f'Please add a new static wall object list verification test case '
            f'here: list_length={list_length}'
        )
        assert False
    verify_static_wall_list_properties(wall_object_list, hidden_step)


def verify_static_wall_list_properties(
    wall_object_list,
    hidden_step=-1,
    scale_x=0.5,
    scale_z=0.5
):
    for _, wall_object in enumerate(wall_object_list):
        assert wall_object['id'].startswith('wall_')
        assert wall_object['type'] == 'cube'
        assert wall_object['materials'] == ['Custom/Materials/Black']
        assert wall_object['kinematic']
        assert wall_object['structure']
        assert wall_object['debug']['info'] == ['black', 'cube', 'black cube']
        if 'configHeight' in wall_object['debug']:
            assert wall_object['debug']['configHeight'] == [0.0625, 0.125]
        if 'configSize' in wall_object['debug']:
            assert wall_object['debug']['configSize'] == [0.5, 0.5]

        assert len(wall_object['shows']) == 1
        assert wall_object['shows'][0]['scale']['x'] == scale_x
        assert wall_object['shows'][0]['scale']['y'] == 0.125
        assert wall_object['shows'][0]['scale']['z'] == scale_z

        if hidden_step >= 0:
            assert wall_object['hides'][0]['stepBegin'] == hidden_step
        else:
            assert 'hides' not in wall_object


def test_materials():
    agent_materials = [material[0] for material in AGENT_OBJECT_MATERIAL_LIST]
    goal_materials = [material[0] for material in GOAL_OBJECT_MATERIAL_LIST]
    for material in (agent_materials + goal_materials):
        assert material in materials.ADJACENT_SETS

    # Multi-agent scenes must have one or more goal object colors for any
    # possible combination of agent colors.
    # Assume such scenes will only ever have one or two goal objects.
    for agent_material_1 in agent_materials:
        for agent_material_2 in agent_materials:
            if agent_material_1 == agent_material_2:
                continue
            used_materials = (
                [agent_material_1] +
                materials.ADJACENT_SETS[agent_material_1] +
                [agent_material_2] +
                materials.ADJACENT_SETS[agent_material_2]
            )
            filtered_goal_materials = [
                material for material in goal_materials
                if material not in used_materials
            ]
            assert len(filtered_goal_materials) > 1

    # Multiple object scenes must have one or more agent colors for any
    # possible combination of goal object colors.
    # Assume such scenes will only ever have one agent.
    for goal_material_1 in goal_materials:
        for goal_material_2 in goal_materials:
            if goal_material_1 == goal_material_2:
                continue
            used_materials = (
                [goal_material_1] + materials.ADJACENT_SETS[goal_material_1] +
                [goal_material_2] + materials.ADJACENT_SETS[goal_material_2]
            )
            filtered_agent_materials = [
                material for material in agent_materials
                if material not in used_materials
            ]
            assert len(filtered_agent_materials)


def test_append_each_show_to_object():
    mcs_object = {
        'type': 'cube',
        'debug': {
            'boundsAtStep': [],
            'configHeight': [0.25, 0.5],
            'configSize': [0.4, 0.4]
        },
        'shows': []
    }

    trial = [{
        'test_property': [[[5, 5], 5]]
    }, {
        'test_property': [[[95, 95], 5]]
    }, {
        'test_property': [[[185, 185], 5]]
    }, {
        'test_property': [[[95, 95], 5]]
    }]
    result = _append_each_show_to_object(
        mcs_object,
        trial,
        1,
        'test_property',
        UNIT_SIZE
    )
    assert result == mcs_object
    assert len(result['debug']['boundsAtStep']) == 5
    verify_bounds(result, 0, -2.05, -2.45, -2.05, -2.45)
    verify_bounds(result, 1, 0.2, -0.2, 0.2, -0.2)
    verify_bounds(result, 2, 2.45, 2.05, 2.45, 2.05)
    verify_bounds(result, 3, 0.2, -0.2, 0.2, -0.2)
    verify_bounds(result, 4, 0.2, -0.2, 0.2, -0.2)
    assert len(result['shows']) == 4
    assert result['shows'][0]['stepBegin'] == 1
    assert result['shows'][0]['position'] == {
        'x': -2.25, 'y': 0.25, 'z': -2.25
    }
    assert result['shows'][0]['scale'] == {'x': 0.4, 'y': 0.5, 'z': 0.4}
    assert result['shows'][0]['boundingBox']
    assert result['shows'][1]['stepBegin'] == 2
    assert result['shows'][1]['position'] == {'x': 0, 'y': 0.25, 'z': 0}
    assert 'scale' not in result['shows'][1]
    assert result['shows'][1]['boundingBox']
    assert result['shows'][2]['stepBegin'] == 3
    assert result['shows'][2]['position'] == {
        'x': 2.25, 'y': 0.25, 'z': 2.25
    }
    assert 'scale' not in result['shows'][2]
    assert result['shows'][2]['boundingBox']
    assert result['shows'][3]['stepBegin'] == 4
    assert result['shows'][3]['position'] == {'x': 0, 'y': 0.25, 'z': 0}
    assert 'scale' not in result['shows'][3]
    assert result['shows'][3]['boundingBox']


def test_append_each_show_to_object_agent():
    mcs_object = {
        'type': 'cube',
        'debug': {
            'boundsAtStep': [],
            'configHeight': [0.25, 0.5],
            'configSize': [0.4, 0.4]
        },
        'shows': []
    }

    # The 'agent' property does not have nested lists.
    trial = [{
        'agent': [[5, 5], 5]
    }, {
        'agent': [[95, 95], 5]
    }, {
        'agent': [[185, 185], 5]
    }, {
        'agent': [[95, 95], 5]
    }]
    result = _append_each_show_to_object(
        mcs_object,
        trial,
        1,
        'agent',
        UNIT_SIZE
    )
    assert result == mcs_object
    assert len(result['debug']['boundsAtStep']) == 5
    verify_bounds(result, 0, -2.05, -2.45, -2.05, -2.45)
    verify_bounds(result, 1, 0.2, -0.2, 0.2, -0.2)
    verify_bounds(result, 2, 2.45, 2.05, 2.45, 2.05)
    verify_bounds(result, 3, 0.2, -0.2, 0.2, -0.2)
    verify_bounds(result, 4, 0.2, -0.2, 0.2, -0.2)
    assert len(result['shows']) == 4
    assert result['shows'][0]['stepBegin'] == 1
    assert result['shows'][0]['position'] == {
        'x': -2.25, 'y': 0.25, 'z': -2.25
    }
    assert result['shows'][0]['scale'] == {'x': 0.4, 'y': 0.5, 'z': 0.4}
    assert result['shows'][0]['boundingBox']
    assert result['shows'][1]['stepBegin'] == 2
    assert result['shows'][1]['position'] == {'x': 0, 'y': 0.25, 'z': 0}
    assert 'scale' not in result['shows'][1]
    assert result['shows'][1]['boundingBox']
    assert result['shows'][2]['stepBegin'] == 3
    assert result['shows'][2]['position'] == {
        'x': 2.25, 'y': 0.25, 'z': 2.25
    }
    assert 'scale' not in result['shows'][2]
    assert result['shows'][2]['boundingBox']
    assert result['shows'][3]['stepBegin'] == 4
    assert result['shows'][3]['position'] == {'x': 0, 'y': 0.25, 'z': 0}
    assert 'scale' not in result['shows'][3]
    assert result['shows'][3]['boundingBox']


def test_choose_config_list_with_agent():
    config_object_type_list = ['a', 'b', 'c', 'd']
    config_list = [
        ObjectConfig(object_type, index, index, index, index)
        for index, object_type in enumerate(config_object_type_list)
    ]
    material_list = [
        ('Custom/Materials/Cyan', ['cyan']),
        ('Custom/Materials/Grey', ['grey']),
        ('Custom/Materials/Magenta', ['magenta']),
        ('Custom/Materials/Yellow', ['yellow'])
    ]

    trial_list = [[{
        'agent': []
    }]]
    chosen_config_list = _choose_config_list(
        trial_list,
        config_list,
        [None, None],
        material_list,
        'agent',
        [],
        []
    )
    assert len(chosen_config_list) == 2
    assert chosen_config_list[0].object_type in config_object_type_list
    assert chosen_config_list[0].material in material_list


def test_choose_config_list_with_agent_in_instrumental_action_task():
    config_object_type_list = ['cone', 'pyramid', 'a', 'b']
    config_list = [
        ObjectConfig(object_type, index, index, index, index)
        for index, object_type in enumerate(config_object_type_list)
    ]
    material_list = [
        ('Custom/Materials/Cyan', ['cyan']),
        ('Custom/Materials/Grey', ['grey']),
        ('Custom/Materials/Magenta', ['magenta']),
        ('Custom/Materials/Yellow', ['yellow'])
    ]

    trial_list = [[{
        'agent': [],
        'key': True
    }]]
    chosen_config_list = _choose_config_list(
        trial_list,
        config_list,
        [None, None],
        material_list,
        'agent',
        [],
        []
    )
    assert len(chosen_config_list) == 2
    assert chosen_config_list[0].object_type != 'cone'
    assert chosen_config_list[0].object_type != 'pyramid'
    assert chosen_config_list[0].material in material_list


def test_choose_config_list_with_objects():
    config_object_type_list = ['a', 'b', 'c', 'd']
    config_list = [
        ObjectConfig(object_type, index, index, index, index)
        for index, object_type in enumerate(config_object_type_list)
    ]
    material_list = [
        ('Custom/Materials/Cyan', ['cyan']),
        ('Custom/Materials/Grey', ['grey']),
        ('Custom/Materials/Magenta', ['magenta']),
        ('Custom/Materials/Yellow', ['yellow'])
    ]

    trial_list_a = [[{
        'objects': [[], []]
    }]]
    chosen_config_list_a = _choose_config_list(
        trial_list_a,
        config_list,
        [None, None],
        material_list,
        'objects',
        [],
        []
    )
    assert len(chosen_config_list_a) == 2
    assert chosen_config_list_a[0].object_type in config_object_type_list
    assert chosen_config_list_a[1].object_type in config_object_type_list
    assert (
        chosen_config_list_a[0].object_type !=
        chosen_config_list_a[1].object_type
    )
    assert chosen_config_list_a[0].material in material_list
    assert chosen_config_list_a[1].material in material_list
    assert (
        chosen_config_list_a[0].material != chosen_config_list_a[1].material
    )

    trial_list_b = [[{
        'objects': [[]]
    }]]
    chosen_config_list_b = _choose_config_list(
        trial_list_b,
        config_list,
        [None],
        material_list,
        'objects',
        [],
        []
    )
    assert len(chosen_config_list_b) == 1
    assert chosen_config_list_b[0].object_type in config_object_type_list
    assert chosen_config_list_b[0].material in material_list


def test_choose_config_list_no_materials_near_to_used_materials():
    mock_config_object_type_list = ['a', 'b', 'c', 'd']
    mock_config_list = [
        ObjectConfig(object_type, index, index, index, index)
        for index, object_type in enumerate(mock_config_object_type_list)
    ]
    material_list = [
        ('Custom/Materials/Azure', ['azure']),
        ('Custom/Materials/Navy', ['navy']),
        ('Custom/Materials/Red', ['red']),
        ('Custom/Materials/Violet', ['violet'])
    ]

    trial_list = [[{
        'objects': [[]]
    }]]
    chosen_config_list = _choose_config_list(
        trial_list,
        mock_config_list,
        [None, None],
        material_list,
        'objects',
        [],
        ['Custom/Materials/Blue']
    )
    assert len(chosen_config_list) == 1
    assert chosen_config_list[0].material[0] == 'Custom/Materials/Red'


def test_choose_config_list_no_materials_near_to_used_materials_multiple():
    mock_config_object_type_list = ['a', 'b', 'c', 'd']
    mock_config_list = [
        ObjectConfig(object_type, index, index, index, index)
        for index, object_type in enumerate(mock_config_object_type_list)
    ]
    material_list = [
        ('Custom/Materials/Azure', ['azure']),
        ('Custom/Materials/Navy', ['navy']),
        ('Custom/Materials/Red', ['red']),
        ('Custom/Materials/Violet', ['violet'])
    ]

    trial_list = [[{
        'objects': [[], []]
    }]]
    with pytest.raises(exceptions.SceneException):
        _choose_config_list(
            trial_list,
            mock_config_list,
            [None, None],
            material_list,
            'objects',
            [],
            ['Custom/Materials/Blue']
        )


def test_choose_config_list_no_types_same_as_used_types():
    mock_config_object_type_list = ['a', 'b', 'c', 'd']
    mock_config_list = [
        ObjectConfig(object_type, index, index, index, index)
        for index, object_type in enumerate(mock_config_object_type_list)
    ]
    material_list = [
        ('Custom/Materials/Cyan', ['cyan']),
        ('Custom/Materials/Grey', ['grey']),
        ('Custom/Materials/Magenta', ['magenta']),
        ('Custom/Materials/Yellow', ['yellow'])
    ]

    trial_list = [[{
        'objects': [[]]
    }]]
    chosen_config_list = _choose_config_list(
        trial_list,
        mock_config_list,
        [None, None],
        material_list,
        'objects',
        ['a', 'b', 'd'],
        []
    )
    assert len(chosen_config_list) == 1
    assert chosen_config_list[0].object_type == 'c'


def test_choose_config_list_no_types_same_as_used_types_multiple():
    mock_config_object_type_list = ['a', 'b', 'c', 'd']
    mock_config_list = [
        ObjectConfig(object_type, index, index, index, index)
        for index, object_type in enumerate(mock_config_object_type_list)
    ]
    material_list = [
        ('Custom/Materials/Cyan', ['cyan']),
        ('Custom/Materials/Grey', ['grey']),
        ('Custom/Materials/Magenta', ['magenta']),
        ('Custom/Materials/Yellow', ['yellow'])
    ]

    trial_list = [[{
        'objects': [[], []]
    }]]
    with pytest.raises(exceptions.SceneException):
        _choose_config_list(
            trial_list,
            mock_config_list,
            [None, None],
            material_list,
            'objects',
            ['a', 'b', 'd'],
            []
        )


def test_create_action_list():
    trial_list_a = [[{}], [{}], [{}]]
    action_list_a = _create_action_list(trial_list_a)
    assert action_list_a == [
        ['Pass'], ['EndHabituation'],
        ['Pass'], ['EndHabituation'],
        ['Pass']
    ]

    trial_list_b = [[{}, {}, {}], [{}, {}], [{}]]
    action_list_b = _create_action_list(trial_list_b)
    assert action_list_b == [
        ['Pass'], ['Pass'], ['Pass'], ['EndHabituation'],
        ['Pass'], ['Pass'], ['EndHabituation'],
        ['Pass']
    ]


def test_create_agent_object_list():
    trial_list = [[{
        'agent': [[25, 25], 5, 'agent_1']
    }, {
        'agent': [[30, 30], 5, 'agent_1']
    }, {
        'agent': [[35, 35], 5, 'agent_1']
    }], [{
        'agent': [[95, 95], 5, 'agent_1']
    }, {
        'agent': [[95, 100], 5, 'agent_1']
    }, {
        'agent': [[95, 105], 5, 'agent_1']
    }, {
        'agent': [[95, 110], 5, 'agent_1']
    }], [{
        'agent': [[165, 165], 5, 'agent_1']
    }, {
        'agent': [[160, 165], 5, 'agent_1']
    }, {
        'agent': [[155, 165], 5, 'agent_1']
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 1, 2, 3, 4),
            MaterialTuple('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    agent_object_list = _create_agent_object_list(
        trial_list,
        object_config_with_material_list,
        UNIT_SIZE
    )

    assert len(agent_object_list) == 1
    agent_object = agent_object_list[0]

    assert agent_object['id'].startswith('agent_')
    assert agent_object['type'] == 'cube'
    assert agent_object['materials'] == ['test_material']
    assert agent_object['kinematic']
    assert not agent_object.get('structure')
    assert agent_object['debug']['info'] == [
        'test_color_a', 'test_color_b', 'cube',
        'test_color_a test_color_b cube'
    ]
    assert agent_object['debug']['configHeight'] == [0.25, 0.5]
    assert agent_object['debug']['configSize'] == [0.25, 0.25]

    assert len(agent_object['shows']) == 10
    verify_show(agent_object, 0, 0, -1.75, 0.25, -1.75)
    assert agent_object['shows'][0]['scale']['x'] == 0.25
    assert agent_object['shows'][0]['scale']['y'] == 0.5
    assert agent_object['shows'][0]['scale']['z'] == 0.25

    verify_show(agent_object, 1, 1, -1.625, 0.25, -1.625)
    verify_show(agent_object, 2, 2, -1.5, 0.25, -1.5)
    verify_show(agent_object, 3, 4, 0, 0.25, 0)
    verify_show(agent_object, 4, 5, 0, 0.25, 0.125)
    verify_show(agent_object, 5, 6, 0, 0.25, 0.25)
    verify_show(agent_object, 6, 7, 0, 0.25, 0.375)
    verify_show(agent_object, 7, 9, 1.75, 0.25, 1.75)
    verify_show(agent_object, 8, 10, 1.625, 0.25, 1.75)
    verify_show(agent_object, 9, 11, 1.5, 0.25, 1.75)

    assert len(agent_object['debug']['boundsAtStep']) == 13
    verify_bounds(agent_object, 0, -1.625, -1.875, -1.625, -1.875)
    verify_bounds(agent_object, 1, -1.5, -1.75, -1.5, -1.75)
    verify_bounds(agent_object, 2, -1.375, -1.625, -1.375, -1.625)
    verify_bounds(agent_object, 3, -1.375, -1.625, -1.375, -1.625)
    verify_bounds(agent_object, 4, 0.125, -0.125, 0.125, -0.125)
    verify_bounds(agent_object, 5, 0.125, -0.125, 0.25, 0)
    verify_bounds(agent_object, 6, 0.125, -0.125, 0.375, 0.125)
    verify_bounds(agent_object, 7, 0.125, -0.125, 0.5, 0.25)
    verify_bounds(agent_object, 8, 0.125, -0.125, 0.5, 0.25)
    verify_bounds(agent_object, 9, 1.875, 1.625, 1.875, 1.625)
    verify_bounds(agent_object, 10, 1.75, 1.5, 1.875, 1.625)
    verify_bounds(agent_object, 11, 1.625, 1.375, 1.875, 1.625)
    verify_bounds(agent_object, 12, 1.625, 1.375, 1.875, 1.625)


def test_create_fuse_wall_object_list():
    fuse_wall_json_list = create_wall_json_list()
    trial_list = [[
        {'fuse_walls': fuse_wall_json_list},
        {'fuse_walls': fuse_wall_json_list},
        {'fuse_walls': fuse_wall_json_list[:4]},
        {'fuse_walls': fuse_wall_json_list[:2]},
        {'fuse_walls': []},
        {'fuse_walls': []}
    ]]

    wall_object_list = _create_fuse_wall_object_list(trial_list, UNIT_SIZE)
    assert len(wall_object_list) == 5
    verify_fuse_wall_list_trial_1(wall_object_list)


def test_create_fuse_wall_object_list_multiple_trials():
    fuse_wall_json_list_1 = create_wall_json_list(True)
    fuse_wall_json_list_2 = create_wall_json_list_variation_2(True)
    trial_list = [[
        {'fuse_walls': fuse_wall_json_list_1},
        {'fuse_walls': fuse_wall_json_list_1},
        {'fuse_walls': fuse_wall_json_list_1[:4]},
        {'fuse_walls': fuse_wall_json_list_1[:2]},
        {'fuse_walls': []},
        {'fuse_walls': []}
    ], [
        {'fuse_walls': fuse_wall_json_list_2},
        {'fuse_walls': fuse_wall_json_list_2[:2]},
        {'fuse_walls': fuse_wall_json_list_2[:1]},
        {'fuse_walls': []}
    ]]

    wall_object_list = _create_fuse_wall_object_list(trial_list, UNIT_SIZE)
    assert len(wall_object_list) == 8
    verify_fuse_wall_list_trial_1(wall_object_list)
    verify_fuse_wall_list_trial_2(wall_object_list)


def test_create_goal_object_list_single_object():
    trial_list = [[{
        'objects': [
            [[25, 25], 5, 'obj_1']
        ]
    }], [{
        'objects': [
            [[95, 95], 5, 'obj_1']
        ]
    }], [{
        'objects': [
            [[165, 165], 5, 'obj_1']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 1, 2, 3, 4),
            MaterialTuple('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=10, y=0, z=10), Vector3d(x=10, y=0, z=12),
        Vector3d(x=12, y=0, z=12), Vector3d(x=12, y=0, z=10)
    ], max_y=0, min_y=0)

    goal_object_list = _create_goal_object_list(
        trial_list,
        object_config_with_material_list,
        mock_agent_start_bounds,
        'filename',
        UNIT_SIZE
    )

    assert len(goal_object_list) == 1
    goal_object_1 = goal_object_list[0]

    assert goal_object_1['id'].startswith('object_')
    assert goal_object_1['type'] == 'cube'
    assert goal_object_1['materials'] == ['test_material']
    assert goal_object_1['kinematic']
    assert not goal_object_1.get('structure')
    assert goal_object_1['debug']['info'] == [
        'test_color_a', 'test_color_b', 'cube',
        'test_color_a test_color_b cube'
    ]
    assert goal_object_1['debug']['configHeight'] == [0.25, 0.5]
    assert goal_object_1['debug']['configSize'] == [0.25, 0.25]

    assert len(goal_object_1['shows']) == 3
    verify_show(goal_object_1, 0, 0, -1.75, 0.25, -1.75)
    assert goal_object_1['shows'][0]['scale']['x'] == 0.25
    assert goal_object_1['shows'][0]['scale']['y'] == 0.5
    assert goal_object_1['shows'][0]['scale']['z'] == 0.25

    verify_show(goal_object_1, 1, 2, 0, 0.25, 0)
    verify_show(goal_object_1, 2, 4, 1.75, 0.25, 1.75)

    assert len(goal_object_1['debug']['boundsAtStep']) == 6
    verify_bounds(goal_object_1, 0, -1.625, -1.875, -1.625, -1.875)
    verify_bounds(goal_object_1, 1, -1.625, -1.875, -1.625, -1.875)
    verify_bounds(goal_object_1, 2, 0.125, -0.125, 0.125, -0.125)
    verify_bounds(goal_object_1, 3, 0.125, -0.125, 0.125, -0.125)
    verify_bounds(goal_object_1, 4, 1.875, 1.625, 1.875, 1.625)
    verify_bounds(goal_object_1, 5, 1.875, 1.625, 1.875, 1.625)


def test_create_goal_object_list_multiple_object():
    trial_list = [[{
        'objects': [
            [[25, 165], 5, 'obj_1'],
            [[160, 20], 10, 'obj_2']
        ]
    }], [{
        'objects': [
            [[90, 100], 5, 'obj_1'],
            [[95, 85], 10, 'obj_2']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 1, 2, 3, 4),
            MaterialTuple('test_material_1', ['test_color_a', 'test_color_b'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('sphere', 5, 6, 7, 8),
            MaterialTuple('test_material_2', ['test_color_c'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=10, y=0, z=10), Vector3d(x=10, y=0, z=12),
        Vector3d(x=12, y=0, z=12), Vector3d(x=12, y=0, z=10)
    ], max_y=0, min_y=0)

    goal_object_list = _create_goal_object_list(
        trial_list,
        object_config_with_material_list,
        mock_agent_start_bounds,
        'filename',
        UNIT_SIZE
    )

    assert len(goal_object_list) == 2
    goal_object_1 = goal_object_list[0]
    goal_object_2 = goal_object_list[1]

    assert goal_object_1['id'].startswith('object_')
    assert goal_object_1['type'] == 'cube'
    assert goal_object_1['materials'] == ['test_material_1']
    assert goal_object_1['kinematic']
    assert not goal_object_1.get('structure')
    assert goal_object_1['debug']['info'] == [
        'test_color_a', 'test_color_b', 'cube',
        'test_color_a test_color_b cube'
    ]
    assert goal_object_1['debug']['configHeight'] == [0.25, 0.5]
    assert goal_object_1['debug']['configSize'] == [0.25, 0.25]

    assert len(goal_object_1['shows']) == 2
    verify_show(goal_object_1, 0, 0, -1.75, 0.25, 1.75)
    assert goal_object_1['shows'][0]['scale']['x'] == 0.25
    assert goal_object_1['shows'][0]['scale']['y'] == 0.5
    assert goal_object_1['shows'][0]['scale']['z'] == 0.25
    verify_show(goal_object_1, 1, 2, -0.125, 0.25, 0.125)

    assert len(goal_object_1['debug']['boundsAtStep']) == 4
    verify_bounds(goal_object_1, 0, -1.625, -1.875, 1.875, 1.625)
    verify_bounds(goal_object_1, 1, -1.625, -1.875, 1.875, 1.625)
    verify_bounds(goal_object_1, 2, 0, -0.25, 0.25, 0)
    verify_bounds(goal_object_1, 3, 0, -0.25, 0.25, 0)

    assert goal_object_2['id'].startswith('object_')
    assert goal_object_2['type'] == 'sphere'
    assert goal_object_2['materials'] == ['test_material_2']
    assert goal_object_2['kinematic']
    assert not goal_object_2.get('structure')
    assert goal_object_2['debug']['info'] == [
        'test_color_c', 'sphere', 'test_color_c sphere'
    ]
    assert goal_object_2['debug']['configHeight'] == [1.5, 3]
    assert goal_object_2['debug']['configSize'] == [2.5, 2.5]

    assert len(goal_object_2['shows']) == 2
    verify_show(goal_object_2, 0, 0, 1.75, 1.5, -1.75)
    assert goal_object_2['shows'][0]['scale']['x'] == 2.5
    assert goal_object_2['shows'][0]['scale']['y'] == 3
    assert goal_object_2['shows'][0]['scale']['z'] == 2.5
    verify_show(goal_object_2, 1, 2, 0.125, 1.5, -0.125)

    assert len(goal_object_2['debug']['boundsAtStep']) == 4
    verify_bounds(goal_object_2, 0, 3, 0.5, -0.5, -3)
    verify_bounds(goal_object_2, 1, 3, 0.5, -0.5, -3)
    verify_bounds(goal_object_2, 2, 1.375, -1.125, 1.125, -1.375)
    verify_bounds(goal_object_2, 3, 1.375, -1.125, 1.125, -1.375)


def test_create_goal_object_list_multiple_object_swap_icon():
    trial_list = [[{
        'objects': [
            [[25, 165], 5, 'obj_1'],
            [[160, 20], 10, 'obj_2']
        ]
    }], [{
        'objects': [
            [[90, 100], 5, 'obj_2'],
            [[95, 85], 10, 'obj_1']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 1, 2, 3, 4),
            MaterialTuple('test_material_1', ['test_color_a', 'test_color_b'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('sphere', 5, 6, 7, 8),
            MaterialTuple('test_material_2', ['test_color_c'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=10, y=0, z=10), Vector3d(x=10, y=0, z=12),
        Vector3d(x=12, y=0, z=12), Vector3d(x=12, y=0, z=10)
    ], max_y=0, min_y=0)

    goal_object_list = _create_goal_object_list(
        trial_list,
        object_config_with_material_list,
        mock_agent_start_bounds,
        'filename',
        UNIT_SIZE
    )

    assert len(goal_object_list) == 2
    goal_object_1 = goal_object_list[0]
    goal_object_2 = goal_object_list[1]

    assert goal_object_1['id'].startswith('object_')
    assert goal_object_1['type'] == 'cube'
    assert goal_object_1['materials'] == ['test_material_1']
    assert goal_object_1['kinematic']
    assert not goal_object_1.get('structure')
    assert goal_object_1['debug']['info'] == [
        'test_color_a', 'test_color_b', 'cube',
        'test_color_a test_color_b cube'
    ]
    assert goal_object_1['debug']['configHeight'] == [0.25, 0.5]
    assert goal_object_1['debug']['configSize'] == [0.25, 0.25]

    assert len(goal_object_1['shows']) == 2
    verify_show(goal_object_1, 0, 0, -1.75, 0.25, 1.75)
    assert goal_object_1['shows'][0]['scale']['x'] == 0.25
    assert goal_object_1['shows'][0]['scale']['y'] == 0.5
    assert goal_object_1['shows'][0]['scale']['z'] == 0.25
    verify_show(goal_object_1, 1, 2, 0.125, 0.25, -0.125)

    assert len(goal_object_1['debug']['boundsAtStep']) == 4
    verify_bounds(goal_object_1, 0, -1.625, -1.875, 1.875, 1.625)
    verify_bounds(goal_object_1, 1, -1.625, -1.875, 1.875, 1.625)
    verify_bounds(goal_object_1, 2, 0.25, 0, 0, -0.25)
    verify_bounds(goal_object_1, 3, 0.25, 0, 0, -0.25)

    assert goal_object_2['id'].startswith('object_')
    assert goal_object_2['type'] == 'sphere'
    assert goal_object_2['materials'] == ['test_material_2']
    assert goal_object_2['kinematic']
    assert not goal_object_2.get('structure')
    assert goal_object_2['debug']['info'] == [
        'test_color_c', 'sphere', 'test_color_c sphere'
    ]
    assert goal_object_2['debug']['configHeight'] == [1.5, 3]
    assert goal_object_2['debug']['configSize'] == [2.5, 2.5]

    assert len(goal_object_2['shows']) == 2
    verify_show(goal_object_2, 0, 0, 1.75, 1.5, -1.75)
    assert goal_object_2['shows'][0]['scale']['x'] == 2.5
    assert goal_object_2['shows'][0]['scale']['y'] == 3
    assert goal_object_2['shows'][0]['scale']['z'] == 2.5
    verify_show(goal_object_2, 1, 2, -0.125, 1.5, 0.125)

    assert len(goal_object_2['debug']['boundsAtStep']) == 4
    verify_bounds(goal_object_2, 0, 3, 0.5, -0.5, -3)
    verify_bounds(goal_object_2, 1, 3, 0.5, -0.5, -3)
    verify_bounds(goal_object_2, 2, 1.125, -1.375, 1.375, -1.125)
    verify_bounds(goal_object_2, 3, 1.125, -1.375, 1.375, -1.125)


def test_create_goal_object_list_single_object_on_home():
    trial_list = [[{
        'objects': [
            [[20, 20], 5, 'obj_1']
        ]
    }], [{
        'objects': [
            [[90, 90], 5, 'obj_1']
        ]
    }], [{
        'objects': [
            [[160, 160], 5, 'obj_1']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 0.125, 0.25, 0.25, 0.25),
            MaterialTuple('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=-0.25, y=0, z=-0.25), Vector3d(x=-0.25, y=0, z=0.25),
        Vector3d(x=0.25, y=0, z=0.25), Vector3d(x=0.25, y=0, z=-0.25)
    ], max_y=0, min_y=0)

    with pytest.raises(exceptions.SceneException):
        _create_goal_object_list(
            trial_list,
            object_config_with_material_list,
            agent_start_bounds,
            'filename',
            UNIT_SIZE
        )


def test_create_goal_object_list_multiple_object_on_home():
    trial_list = [[{
        'objects': [
            [[20, 20], 5, 'obj_1'],
            [[100, 100], 5, 'obj_2']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 0.125, 0.25, 0.25, 0.25),
            MaterialTuple('test_material_1', ['test_color_a', 'test_color_b'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('sphere', 0.125, 0.25, 0.25, 0.25),
            MaterialTuple('test_material_2', ['test_color_c'])
        )
    ]

    agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=-0.25, y=0, z=-0.25), Vector3d(x=-0.25, y=0, z=0.25),
        Vector3d(x=0.25, y=0, z=0.25), Vector3d(x=0.25, y=0, z=-0.25)
    ], max_y=0, min_y=0)

    with pytest.raises(exceptions.SceneException):
        _create_goal_object_list(
            trial_list,
            object_config_with_material_list,
            agent_start_bounds,
            'filename',
            UNIT_SIZE
        )


def test_create_home_object():
    trial_list = [[{
        'home': [[95, 95], 5]
    }]]

    home_object = _create_home_object(trial_list, UNIT_SIZE)

    assert home_object['id'].startswith('home_')
    assert home_object['type'] == 'cube'
    assert home_object['materials'] == ['Custom/Materials/Magenta']
    assert home_object['kinematic']
    assert home_object['structure']
    assert home_object['debug']['info'] == ['magenta', 'cube', 'magenta cube']
    assert home_object['debug']['configHeight'] == [0.01, 0.02]
    assert home_object['debug']['configSize'] == [0.5, 0.5]

    assert len(home_object['shows']) == 1
    verify_show(home_object, 0, 0, 0, 0.01, 0)
    assert home_object['shows'][0]['scale']['x'] == 0.5
    assert home_object['shows'][0]['scale']['y'] == 0.02
    assert home_object['shows'][0]['scale']['z'] == 0.5


def test_create_home_object_uses_first_frame_of_first_trial():
    trial_list = [[{
        'home': [[20, 160], 10]
    }, {
        'home': [[40, 140], 10]
    }], [{
        'home': [[60, 120], 10]
    }]]

    home_object = _create_home_object(trial_list, UNIT_SIZE)

    assert home_object['id'].startswith('home_')
    assert home_object['type'] == 'cube'
    assert home_object['materials'] == ['Custom/Materials/Magenta']
    assert home_object['kinematic']
    assert home_object['structure']
    assert home_object['debug']['info'] == ['magenta', 'cube', 'magenta cube']
    assert home_object['debug']['configHeight'] == [0.01, 0.02]
    assert home_object['debug']['configSize'] == [0.5, 0.5]

    assert len(home_object['shows']) == 1
    verify_show(home_object, 0, 0, -1.75, 0.01, 1.75)
    assert home_object['shows'][0]['scale']['x'] == 0.5
    assert home_object['shows'][0]['scale']['y'] == 0.02
    assert home_object['shows'][0]['scale']['z'] == 0.5


def test_create_key_object():
    # negative_x
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle0.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)
    assert len(key_object['shows']) == 1
    verify_key_properties(key_object)
    verify_show(key_object, 0, 0, 0.25, 0.06, 0)
    assert key_object['shows'][0]['rotation']['y'] == -135

    # negative_z
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle90.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)
    assert len(key_object['shows']) == 1
    verify_key_properties(key_object)
    verify_show(key_object, 0, 0, 0, 0.06, 0.25)
    assert key_object['shows'][0]['rotation']['y'] == 135

    # positive_x
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle180.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)
    assert len(key_object['shows']) == 1
    verify_key_properties(key_object)
    verify_show(key_object, 0, 0, -0.25, 0.06, 0)
    assert key_object['shows'][0]['rotation']['y'] == 45

    # positive_z
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle270.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)
    assert len(key_object['shows']) == 1
    verify_key_properties(key_object)
    verify_show(key_object, 0, 0, 0, 0.06, -0.25)
    assert key_object['shows'][0]['rotation']['y'] == -45


def test_create_key_object_move_in_one_trial():
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 85], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 80], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 75], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 70], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 65], 10, 'triangle0.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)

    assert len(key_object['shows']) == 10
    verify_key_properties(key_object)

    for i in range(5):
        verify_show(key_object, i, i, 0.25, 0.06, 0)

    verify_show(key_object, 5, 5, 0.25, 0.56, -0.125)
    verify_show(key_object, 6, 6, 0.25, 0.56, -0.25)
    verify_show(key_object, 7, 7, 0.25, 0.56, -0.375)
    verify_show(key_object, 8, 8, 0.25, 0.56, -0.5)
    verify_show(key_object, 9, 9, 0.25, 0.56, -0.625)

    for i in range(10):
        assert key_object['shows'][0]['rotation']['y'] == -135


def test_create_key_object_rotate_in_one_trial():
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 85], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 80], 10, 'triangle90.png']]
    }, {
        'key': [[[90, 75], 10, 'triangle90.png']]
    }, {
        'key': [[[90, 70], 10, 'triangle180.png']]
    }, {
        'key': [[[90, 65], 10, 'triangle180.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)

    assert len(key_object['shows']) == 10
    verify_key_properties(key_object)

    for i in range(5):
        verify_show(key_object, i, i, 0.25, 0.06, 0)

    verify_show(key_object, 5, 5, 0.25, 0.56, -0.125)
    verify_show(key_object, 6, 6, 0, 0.56, -0.25 + 0.25)
    verify_show(key_object, 7, 7, 0, 0.56, -0.375 + 0.25)
    verify_show(key_object, 8, 8, -0.25, 0.56, -0.5)
    verify_show(key_object, 9, 9, -0.25, 0.56, -0.625)

    for i in range(6):
        assert key_object['shows'][i]['rotation']['y'] == -135

    for i in range(6, 8):
        assert key_object['shows'][i]['rotation']['y'] == 135

    for i in range(8, 10):
        assert key_object['shows'][i]['rotation']['y'] == 45


def test_create_key_object_move_in_multiple_trials():
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 85], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 80], 10, 'triangle0.png']]
    }], [{
        'key': [[[160, 20], 10, 'triangle0.png']]
    }, {
        'key': [[[155, 20], 10, 'triangle0.png']]
    }], [{
        'key': [[[20, 160], 10, 'triangle90.png']]
    }, {
        'key': [[[20, 160], 10, 'triangle90.png']]
    }, {
        'key': [[[25, 160], 10, 'triangle90.png']]
    }, {
        'key': [[[30, 160], 10, 'triangle90.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)

    assert len(key_object['shows']) == 10
    verify_key_properties(key_object)

    verify_show(key_object, 0, 0, 0.25, 0.06, 0)
    verify_show(key_object, 1, 1, 0.25, 0.06, 0)
    verify_show(key_object, 2, 2, 0.25, 0.56, -0.125)
    verify_show(key_object, 3, 3, 0.25, 0.56, -0.25)
    verify_show(key_object, 4, 5, 2, 0.06, -1.75)
    verify_show(key_object, 5, 6, 1.875, 0.56, -1.75)
    verify_show(key_object, 6, 8, -1.75, 0.06, 2)
    verify_show(key_object, 7, 9, -1.75, 0.06, 2)
    verify_show(key_object, 8, 10, -1.625, 0.56, 2)
    verify_show(key_object, 9, 11, -1.5, 0.56, 2)

    for i in range(6):
        assert key_object['shows'][i]['rotation']['x'] == 0
        assert key_object['shows'][i]['rotation']['y'] == -135
        assert key_object['shows'][i]['rotation']['z'] == 90

    for i in range(6, 10):
        assert key_object['shows'][i]['rotation']['x'] == 0
        assert key_object['shows'][i]['rotation']['y'] == 135
        assert key_object['shows'][i]['rotation']['z'] == 90


def test_create_key_object_if_property_is_pin():
    trial_list = [[{
        'pin': [[[90, 90], 10, 'triangle0.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)
    assert len(key_object['shows']) == 1
    verify_key_properties(key_object)
    verify_show(key_object, 0, 0, 0.25, 0.06, 0)
    assert key_object['shows'][0]['rotation']['y'] == -135


def test_create_key_object_no_key_some_trials():
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle0.png']]
    }, {
        'key': [[[90, 90], 10, 'triangle0.png']]
    }], [{}, {}, {}, {}], [{
        'key': [[[20, 160], 10, 'triangle90.png']]
    }, {
        'key': [[[20, 160], 10, 'triangle90.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)

    assert len(key_object['shows']) == 4
    verify_key_properties(key_object)

    verify_show(key_object, 0, 0, 0.25, 0.06, 0)
    verify_show(key_object, 1, 1, 0.25, 0.06, 0)
    verify_show(key_object, 2, 8, -1.75, 0.06, 2)
    verify_show(key_object, 3, 9, -1.75, 0.06, 2)

    for i in range(2):
        assert key_object['shows'][i]['rotation']['x'] == 0
        assert key_object['shows'][i]['rotation']['y'] == -135
        assert key_object['shows'][i]['rotation']['z'] == 90

    for i in range(2, 4):
        assert key_object['shows'][i]['rotation']['x'] == 0
        assert key_object['shows'][i]['rotation']['y'] == 135
        assert key_object['shows'][i]['rotation']['z'] == 90


def test_create_lock_wall_object_list():
    trial_list = [[{
        'lock': [[[90, 90], 10, 'slot0.png']]
    }]]
    lock_object_list = _create_lock_wall_object_list(trial_list, {}, UNIT_SIZE)
    assert len(lock_object_list) == 1
    verify_lock_properties(lock_object_list[0])
    verify_show(lock_object_list[0], 0, 0, 0, 0.06, 0)
    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 90

    trial_list = [[{
        'lock': [[[90, 90], 10, 'slot90.png']]
    }]]
    lock_object_list = _create_lock_wall_object_list(trial_list, {}, UNIT_SIZE)
    assert len(lock_object_list) == 1
    verify_lock_properties(lock_object_list[0])
    verify_show(lock_object_list[0], 0, 0, 0, 0.06, 0)
    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 0

    trial_list = [[{
        'lock': [[[90, 90], 10, 'slot180.png']]
    }]]
    lock_object_list = _create_lock_wall_object_list(trial_list, {}, UNIT_SIZE)
    assert len(lock_object_list) == 1
    verify_lock_properties(lock_object_list[0])
    verify_show(lock_object_list[0], 0, 0, 0, 0.06, 0)
    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 270

    trial_list = [[{
        'lock': [[[90, 90], 10, 'slot270.png']]
    }]]
    lock_object_list = _create_lock_wall_object_list(trial_list, {}, UNIT_SIZE)
    assert len(lock_object_list) == 1
    verify_lock_properties(lock_object_list[0])
    verify_show(lock_object_list[0], 0, 0, 0, 0.06, 0)
    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 180


def test_create_lock_wall_object_list_hide_unlocked():
    trial_list = [[
        {'lock': [[[90, 90], 10, 'slot0.png']]},
        {'lock': [[[90, 90], 10, 'slot0.png']]},
        {'lock': []},
        {'lock': []}
    ]]
    key_object = {'hides': []}
    lock_object_list = _create_lock_wall_object_list(
        trial_list,
        key_object,
        UNIT_SIZE
    )
    assert len(lock_object_list) == 1

    verify_lock_properties(lock_object_list[0])
    verify_show(lock_object_list[0], 0, 0, 0, 0.06, 0)
    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 90

    assert len(lock_object_list[0]['hides']) == 1
    assert lock_object_list[0]['hides'][0]['stepBegin'] == 2

    assert len(key_object['hides']) == 1
    assert key_object['hides'][0]['stepBegin'] == 2


def test_create_lock_wall_object_list_multiple_trials():
    trial_list = [[{
        'lock': [[[90, 90], 10, 'slot0.png']]
    }], [{
        'lock': [[[90, 90], 10, 'slot0.png']]
    }], [{
        'lock': [[[90, 90], 10, 'slot90.png']]
    }], [{
        'lock': [[[20, 20], 10, 'slot90.png']]
    }], [{
        'lock': [[[160, 160], 10, 'slot180.png']]
    }], [{
        'lock': [[[90, 90], 10, 'slot0.png']]
    }]]
    lock_object_list = _create_lock_wall_object_list(trial_list, {}, UNIT_SIZE)
    assert len(lock_object_list) == 6

    for lock_object in lock_object_list:
        verify_lock_properties(lock_object)

    verify_show(lock_object_list[0], 0, 0, 0, 0.06, 0)
    verify_show(lock_object_list[1], 0, 2, 0, 0.06, 0)
    verify_show(lock_object_list[2], 0, 4, 0, 0.06, 0)
    verify_show(lock_object_list[3], 0, 6, -1.75, 0.06, -1.75)
    verify_show(lock_object_list[4], 0, 8, 1.75, 0.06, 1.75)
    verify_show(lock_object_list[5], 0, 10, 0, 0.06, 0)

    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 90
    assert lock_object_list[1]['shows'][0]['rotation']['y'] == 90
    assert lock_object_list[2]['shows'][0]['rotation']['y'] == 0
    assert lock_object_list[3]['shows'][0]['rotation']['y'] == 0
    assert lock_object_list[4]['shows'][0]['rotation']['y'] == 270
    assert lock_object_list[5]['shows'][0]['rotation']['y'] == 90


def test_create_lock_wall_object_list_multiple_trials_hide_unlocked():
    trial_list = [[
        {'lock': [[[90, 90], 10, 'slot0.png']]},
        {'lock': [[[90, 90], 10, 'slot0.png']]},
        {'lock': [[[90, 90], 10, 'slot0.png']]},
        {'lock': []}
    ], [
        {'lock': [[[90, 90], 10, 'slot0.png']]},
        {'lock': []},
        {'lock': []},
        {'lock': []}
    ]]
    key_object = {'hides': []}
    lock_object_list = _create_lock_wall_object_list(
        trial_list,
        key_object,
        UNIT_SIZE
    )
    assert len(lock_object_list) == 2

    for lock_object in lock_object_list:
        verify_lock_properties(lock_object)
        assert len(lock_object['hides']) == 1

    verify_show(lock_object_list[0], 0, 0, 0, 0.06, 0)
    verify_show(lock_object_list[1], 0, 5, 0, 0.06, 0)

    assert lock_object_list[0]['hides'][0]['stepBegin'] == 3
    assert lock_object_list[1]['hides'][0]['stepBegin'] == 6

    assert len(key_object['hides']) == 2
    assert key_object['hides'][0]['stepBegin'] == 3
    assert key_object['hides'][1]['stepBegin'] == 6


def test_create_lock_wall_object_list_if_property_is_key():
    trial_list = [[{
        'key': [[[90, 90], 10, 'slot0.png']]
    }]]
    lock_object_list = _create_lock_wall_object_list(trial_list, {}, UNIT_SIZE)
    assert len(lock_object_list) == 1
    verify_lock_properties(lock_object_list[0])
    verify_show(lock_object_list[0], 0, 0, 0, 0.06, 0)
    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 90


def test_create_lock_wall_object_list_final_trial_no_lock():
    trial_list = [[{
        'lock': [[[90, 90], 10, 'slot0.png']]
    }], [{
        'lock': [[[20, 20], 10, 'slot90.png']]
    }], [{
        'lock': [[[160, 160], 10, 'slot180.png']]
    }], [{}]]
    lock_object_list = _create_lock_wall_object_list(trial_list, {}, UNIT_SIZE)
    assert len(lock_object_list) == 3

    for lock_object in lock_object_list:
        verify_lock_properties(lock_object)

    verify_show(lock_object_list[0], 0, 0, 0, 0.06, 0)
    verify_show(lock_object_list[1], 0, 2, -1.75, 0.06, -1.75)
    verify_show(lock_object_list[2], 0, 4, 1.75, 0.06, 1.75)

    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 90
    assert lock_object_list[1]['shows'][0]['rotation']['y'] == 0
    assert lock_object_list[2]['shows'][0]['rotation']['y'] == 270


def test_create_object():
    mcs_object = _create_object(
        'id_',
        'cube',
        MaterialTuple('test_material', ['test_color_a', 'test_color_b']),
        [1, 2],
        [3, 4],
        [25, 50],
        [10, 20],
        UNIT_SIZE
    )

    assert mcs_object['id'].startswith('id_')
    assert mcs_object['type'] == 'cube'
    assert mcs_object['materials'] == ['test_material']
    assert mcs_object['debug']['info'] == [
        'test_color_a', 'test_color_b', 'cube',
        'test_color_a test_color_b cube'
    ]
    assert mcs_object['debug']['configHeight'] == [1, 2]
    assert mcs_object['debug']['configSize'] == [3, 4]

    assert len(mcs_object['shows']) == 1
    verify_show(mcs_object, 0, 0, -1.75, 1, -1)
    assert mcs_object['shows'][0]['scale']['x'] == 3
    assert mcs_object['shows'][0]['scale']['y'] == 2
    assert mcs_object['shows'][0]['scale']['z'] == 4

    assert len(mcs_object['debug']['boundsAtStep']) == 1
    verify_bounds(mcs_object, 0, -0.25, -3.25, 1, -3)


def test_create_scene():
    body_template = {'objects': [], 'debug': {}}
    goal_template = hypercubes.initialize_goal(
        {'category': 'mock', 'domainsInfo': {}, 'sceneInfo': {}}
    )

    agent_object_config_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 0.1, 0.2, 0.3, 0.4),
            MaterialTuple('test_material', ['test_color'])
        )
    ]
    goal_object_config_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 0.1, 0.2, 0.3, 0.4),
            MaterialTuple('test_material', ['test_color'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 0.1, 0.2, 0.3, 0.4),
            MaterialTuple('test_material', ['test_color'])
        )
    ]

    trial_list = [[{
        'agent': [[25, 25], 5, 'agent_1'],
        'home': [[25, 25], 5],
        'objects': [
            [[25, 45], 5, 'obj_1'],
            [[95, 95], 5, 'obj_2']
        ],
        'size': [200, 200],
        'walls': [
            [[60, 60], [20, 20]],
            [[60, 120], [20, 20]],
            [[120, 60], [20, 20]],
            [[120, 120], [20, 20]]
        ]
    }, {
        'agent': [[25, 25], 5, 'agent_1']
    }, {
        'agent': [[25, 30], 5, 'agent_1']
    }, {
        'agent': [[25, 35], 5, 'agent_1']
    }, {
        'agent': [[25, 35], 5, 'agent_1']
    }], [{
        'agent': [[25, 25], 5, 'agent_1'],
        'objects': [
            [[45, 25], 5, 'obj_1'],
            [[165, 165], 5, 'obj_2']
        ],
        'walls': [
            [[60, 60], [20, 20]],
            [[60, 120], [20, 20]],
            [[120, 60], [20, 20]],
            [[120, 120], [20, 20]]
        ]
    }, {
        'agent': [[25, 25], 5, 'agent_1']
    }, {
        'agent': [[30, 25], 5, 'agent_1']
    }, {
        'agent': [[35, 25], 5, 'agent_1']
    }, {
        'agent': [[35, 25], 5, 'agent_1']
    }]]

    for is_expected in [True, False]:
        print(f'Testing is_expected={is_expected}')
        scene = _create_scene(
            body_template,
            goal_template,
            agent_object_config_list,
            goal_object_config_list,
            trial_list,
            'filename',
            is_expected
        )

        assert scene['isometric']
        assert scene['goal']['answer']['choice'] == (
            'expected' if is_expected else 'unexpected'
        )
        assert scene['goal']['action_list'] == [
            ['Pass'], ['Pass'], ['Pass'], ['Pass'], ['Pass'],
            ['EndHabituation'],
            ['Pass'], ['Pass'], ['Pass'], ['Pass'], ['Pass']
        ]
        assert scene['goal']['habituation_total'] == 1
        assert scene['goal']['last_step'] == 11

        assert len(scene['objects']) == 13
        agent_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['debug']['role'] == 'agent'
        ]
        assert len(agent_object_list) == 1
        home_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['debug']['role'] == 'home'
        ]
        assert len(home_object_list) == 1
        non_target_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['debug']['role'] == 'non target'
        ]
        assert len(non_target_object_list) == 1
        target_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['debug']['role'] == 'target'
        ]
        assert len(target_object_list) == 1
        platform_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['debug']['role'] == 'structural'
        ]
        assert len(platform_object_list) == 1
        wall_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['debug']['role'] == 'wall'
        ]
        assert len(wall_object_list) == 8


def test_create_show():
    show = _create_show(
        1234,
        'blob_01',
        [1, 2],
        [3, 4],
        [25, 50],
        [10, 20],
        UNIT_SIZE
    )

    assert show['stepBegin'] == 1234
    assert show['position']['x'] == -1.75
    assert show['position']['y'] == 1
    assert show['position']['z'] == -1
    assert show['scale']['x'] == 3
    assert show['scale']['y'] == 2
    assert show['scale']['z'] == 4
    assert show['boundingBox'].box_xz == [
        Vector3d(x=-1.36, y=0, z=-0.28),
        Vector3d(x=-1.36, y=0, z=-1.72),
        Vector3d(x=-2.14, y=0, z=-1.72),
        Vector3d(x=-2.14, y=0, z=-0.28)
    ]
    assert show['boundingBox'].max_y == pytest.approx(1.8)
    assert show['boundingBox'].min_y == pytest.approx(0.2)


def test_create_static_wall_object_list():
    trial_list = [[{
        'walls': create_wall_json_list()
    }]]
    wall_object_list = _create_static_wall_object_list(trial_list, UNIT_SIZE)
    assert len(wall_object_list) == 5
    verify_static_wall_list(wall_object_list)


def test_create_static_wall_object_list_remove_wall():
    trial_list = [[{
        'walls': create_wall_json_list(True)
    }], [{
        'walls': create_wall_json_list(True)[:-1]
    }]]

    wall_object_list = _create_static_wall_object_list(trial_list, UNIT_SIZE)
    assert len(wall_object_list) == 9
    verify_static_wall_list(wall_object_list[:5], hidden_step=2)
    verify_static_wall_list(wall_object_list[5:], list_length=4, show_step=2)


def test_create_static_wall_object_list_change_in_some_trials():
    trial_list = [[{
        'walls': [
            [[20, 20], [20, 20]],
            [[20, 160], [20, 20]],
            [[160, 20], [20, 20]],
            [[160, 160], [20, 20]],
            [[80, 80], [20, 20]]
        ]
    }], [{
        'walls': [
            [[40, 40], [20, 20]],
            [[40, 140], [20, 20]],
            [[140, 40], [20, 20]],
            [[140, 140], [20, 20]],
            [[80, 80], [20, 20]],
            [[100, 100], [20, 20]]
        ]
    }], [{
        'walls': [
            [[120, 20], [20, 20]],
            [[20, 20], [20, 20]],
            [[120, 120], [20, 20]],
            [[20, 120], [20, 20]]
        ]
    }]]
    wall_object_list = _create_static_wall_object_list(trial_list, UNIT_SIZE)
    assert len(wall_object_list) == 15
    verify_show(wall_object_list[0], 0, 0, -1.75, 0.0625, -1.75)
    verify_show(wall_object_list[1], 0, 0, -1.75, 0.0625, 1.75)
    verify_show(wall_object_list[2], 0, 0, 1.75, 0.0625, -1.75)
    verify_show(wall_object_list[3], 0, 0, 1.75, 0.0625, 1.75)
    verify_show(wall_object_list[4], 0, 0, -0.25, 0.0625, -0.25)
    verify_show(wall_object_list[5], 0, 2, -1.25, 0.0625, -1.25)
    verify_show(wall_object_list[6], 0, 2, -1.25, 0.0625, 1.25)
    verify_show(wall_object_list[7], 0, 2, 1.25, 0.0625, -1.25)
    verify_show(wall_object_list[8], 0, 2, 1.25, 0.0625, 1.25)
    verify_show(wall_object_list[9], 0, 2, -0.25, 0.0625, -0.25)
    verify_show(wall_object_list[10], 0, 2, 0.25, 0.0625, 0.25)
    verify_show(wall_object_list[11], 0, 4, 0.75, 0.0625, -1.75)
    verify_show(wall_object_list[12], 0, 4, -1.75, 0.0625, -1.75)
    verify_show(wall_object_list[13], 0, 4, 0.75, 0.0625, 0.75)
    verify_show(wall_object_list[14], 0, 4, -1.75, 0.0625, 0.75)
    verify_static_wall_list_properties(wall_object_list[:5], hidden_step=2)
    verify_static_wall_list_properties(wall_object_list[5:11], hidden_step=4)
    verify_static_wall_list_properties(wall_object_list[11:])


def test_create_trial_frame_list():
    trial = [
        {'agent': [[20, 20]]},
        {'agent': [[20, 20]]},
        {'agent': [[20, 20]]},
        {'agent': [[20, 20]]},
        {'agent': [[20, 20]]},
        {'agent': [[21, 20]]},
        {'agent': [[21, 21]]},
        {'agent': [[22, 21]]},
        {'agent': [[22, 22]]},
        {'agent': [[23, 22]]},
        {'agent': [[23, 23]]},
        {'agent': [[24, 23]]},
        {'agent': [[24, 24]]},
        {'agent': [[25, 24]]},
        {'agent': [[25, 25]]},
        {'agent': [[25, 25]]},
        {'agent': [[25, 25]]},
        {'agent': [[25, 25]]},
        {'agent': [[25, 25]]},
        {'agent': [[25, 25]]}
    ]
    converted_trial = _create_trial_frame_list(trial)
    assert converted_trial == [
        {'agent': [[20, 20]]},
        {'agent': [[20, 20]]},
        {'agent': [[20, 20]]},
        {'agent': [[21, 20]]},
        {'agent': [[22, 21]]},
        {'agent': [[23, 22]]},
        {'agent': [[24, 23]]},
        {'agent': [[25, 24]]},
        {'agent': [[25, 25]]},
        {'agent': [[25, 25]]},
        {'agent': [[25, 25]]}
    ]


def test_create_trial_frame_list_instrumental_action():
    fuse_wall_json_list = [
        [[20, 40], [20, 20]],
        [[20, 60], [20, 20]],
        [[20, 80], [20, 20]],
        [[20, 100], [20, 20]],
        [[20, 120], [20, 20]],
        [[20, 140], [20, 20]],
        [[20, 160], [20, 20]],
        [[160, 20], [20, 20]],
        [[160, 40], [20, 20]],
        [[160, 60], [20, 20]],
        [[160, 80], [20, 20]],
        [[160, 100], [20, 20]],
        [[160, 120], [20, 20]],
        [[160, 140], [20, 20]]
    ]
    trial = [
        # Start the trial, prior to movement. Should skip some frames.
        {
            'agent': [[20, 20]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[20, 20]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[20, 20]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[20, 20]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        # Start the agent's movement. Should skip some frames.
        {
            'agent': [[21, 21]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[22, 22]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[23, 23]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[24, 24]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        # Pause the agent's movement. Should skip some frames.
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        # Change the key's position. Should stop skipping frames.
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        # Start removing fuse walls. Should skip some frames.
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[1:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[2:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[3:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[4:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[5:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[6:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[7:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        # Remove the lock while removing the fuse walls. Should use this frame.
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[8:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[9:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[10:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[11:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[12:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[13:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        # Resume the agent's movement. Should skip some frames.
        {
            'agent': [[26, 26]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[27, 27]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[28, 28]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[29, 29]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[30, 30]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        }
    ]

    converted_trial = _create_trial_frame_list(trial)
    assert converted_trial == [
        {
            'agent': [[20, 20]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[20, 20]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[20, 20]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[21, 21]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[23, 23]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[90, 90], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list,
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[1:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[6:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': [[[160, 160], 10, 'slot0.png']]
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[8:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': fuse_wall_json_list[9:],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[25, 25]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[27, 27]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[29, 29]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        },
        {
            'agent': [[30, 30]],
            'fuse_walls': [],
            'key': [[[40, 40], 10, 'triangle0.png']],
            'lock': []
        }
    ]


def test_create_wall_object_list():
    trial_list = [[{
        'walls': create_wall_json_list()
    }]]
    wall_object_list = _create_wall_object_list(trial_list, UNIT_SIZE)
    assert len(wall_object_list) == 9
    verify_static_wall_list(wall_object_list[:5])
    verify_border_wall_list(wall_object_list[5:])


def test_create_wall_object_list_remove_wall():
    trial_list = [[{
        'walls': create_wall_json_list(True)
    }], [{
        'walls': create_wall_json_list(True)[:-1]
    }]]

    wall_object_list = _create_wall_object_list(trial_list, UNIT_SIZE)
    assert len(wall_object_list) == 13
    verify_static_wall_list(wall_object_list[:5], hidden_step=2)
    verify_static_wall_list(wall_object_list[5:9], list_length=4, show_step=2)
    verify_border_wall_list(wall_object_list[9:])


def test_create_wall_object_list_change_in_some_trials():
    trial_list = [[{
        'walls': [
            [[20, 20], [20, 20]],
            [[20, 160], [20, 20]],
            [[160, 20], [20, 20]],
            [[160, 160], [20, 20]],
            [[80, 80], [20, 20]]
        ]
    }], [{
        'walls': [
            [[40, 40], [20, 20]],
            [[40, 140], [20, 20]],
            [[140, 40], [20, 20]],
            [[140, 140], [20, 20]],
            [[80, 80], [20, 20]],
            [[100, 100], [20, 20]]
        ]
    }], [{
        'walls': [
            [[120, 20], [20, 20]],
            [[20, 20], [20, 20]],
            [[120, 120], [20, 20]],
            [[20, 120], [20, 20]]
        ]
    }]]
    wall_object_list = _create_wall_object_list(trial_list, UNIT_SIZE)
    assert len(wall_object_list) == 19
    verify_show(wall_object_list[0], 0, 0, -1.75, 0.0625, -1.75)
    verify_show(wall_object_list[1], 0, 0, -1.75, 0.0625, 1.75)
    verify_show(wall_object_list[2], 0, 0, 1.75, 0.0625, -1.75)
    verify_show(wall_object_list[3], 0, 0, 1.75, 0.0625, 1.75)
    verify_show(wall_object_list[4], 0, 0, -0.25, 0.0625, -0.25)
    verify_show(wall_object_list[5], 0, 2, -1.25, 0.0625, -1.25)
    verify_show(wall_object_list[6], 0, 2, -1.25, 0.0625, 1.25)
    verify_show(wall_object_list[7], 0, 2, 1.25, 0.0625, -1.25)
    verify_show(wall_object_list[8], 0, 2, 1.25, 0.0625, 1.25)
    verify_show(wall_object_list[9], 0, 2, -0.25, 0.0625, -0.25)
    verify_show(wall_object_list[10], 0, 2, 0.25, 0.0625, 0.25)
    verify_show(wall_object_list[11], 0, 4, 0.75, 0.0625, -1.75)
    verify_show(wall_object_list[12], 0, 4, -1.75, 0.0625, -1.75)
    verify_show(wall_object_list[13], 0, 4, 0.75, 0.0625, 0.75)
    verify_show(wall_object_list[14], 0, 4, -1.75, 0.0625, 0.75)
    verify_static_wall_list_properties(wall_object_list[:5], hidden_step=2)
    verify_static_wall_list_properties(wall_object_list[5:11], hidden_step=4)
    verify_static_wall_list_properties(wall_object_list[11:15])
    verify_border_wall_list(wall_object_list[15:])


def test_create_wall_object_list_with_fuse():
    fuse_wall_json_list = create_wall_json_list()
    trial_list = [[
        {
            'fuse_walls': fuse_wall_json_list,
            'walls': create_wall_json_list()
        },
        {'fuse_walls': fuse_wall_json_list},
        {'fuse_walls': fuse_wall_json_list[:4]},
        {'fuse_walls': fuse_wall_json_list[:2]},
        {'fuse_walls': []},
        {'fuse_walls': []}
    ]]

    wall_object_list = _create_wall_object_list(trial_list, UNIT_SIZE)
    assert len(wall_object_list) == 14
    verify_static_wall_list(wall_object_list[:5])
    verify_border_wall_list(wall_object_list[5:9])
    verify_fuse_wall_list_trial_1(wall_object_list[9:])


def test_create_wall_object_list_with_fuse_multiple_trials():
    fuse_wall_json_list_1 = create_wall_json_list(True)
    fuse_wall_json_list_2 = create_wall_json_list_variation_2(True)
    trial_list = [[
        {
            'fuse_walls': fuse_wall_json_list_1,
            'walls': create_wall_json_list(True)
        },
        {'fuse_walls': fuse_wall_json_list_1},
        {'fuse_walls': fuse_wall_json_list_1[:4]},
        {'fuse_walls': fuse_wall_json_list_1[:2]},
        {'fuse_walls': []},
        {'fuse_walls': []}
    ], [
        {
            'fuse_walls': fuse_wall_json_list_2,
            'walls': create_wall_json_list(True)
        },
        {'fuse_walls': fuse_wall_json_list_2[:2]},
        {'fuse_walls': fuse_wall_json_list_2[:1]},
        {'fuse_walls': []}
    ]]

    wall_object_list = _create_wall_object_list(trial_list, UNIT_SIZE)
    assert len(wall_object_list) == 17
    verify_static_wall_list(wall_object_list[:5])
    verify_border_wall_list(wall_object_list[5:9])
    verify_fuse_wall_list_trial_1(wall_object_list[9:])
    verify_fuse_wall_list_trial_2(wall_object_list[9:])


def test_fix_key_location():
    # negative_x
    json_key = [[90, 90], 10, 'triangle0.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'rotation': {'x': 0, 'y': 0, 'z': 0},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }]}
    fixed_key_object = _fix_key_location(0, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 1
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 0, 0, 0.25, 0, 0)
    assert fixed_key_object['shows'][0]['rotation']['y'] == -135
    assert fixed_key_object['shows'][0]['rotationProperty'] == 'negative_x'

    # negative_z
    json_key = [[90, 90], 10, 'triangle90.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'rotation': {'x': 0, 'y': 0, 'z': 0},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }]}
    fixed_key_object = _fix_key_location(0, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 1
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 0, 0, 0, 0, 0.25)
    assert fixed_key_object['shows'][0]['rotation']['y'] == 135
    assert fixed_key_object['shows'][0]['rotationProperty'] == 'negative_z'

    # positive_x
    json_key = [[90, 90], 10, 'triangle180.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'rotation': {'x': 0, 'y': 0, 'z': 0},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }]}
    fixed_key_object = _fix_key_location(0, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 1
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 0, 0, -0.25, 0, 0)
    assert fixed_key_object['shows'][0]['rotation']['y'] == 45
    assert fixed_key_object['shows'][0]['rotationProperty'] == 'positive_x'

    # positive_z
    json_key = [[90, 90], 10, 'triangle270.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 0, 'y': 0, 'z': 0},
        'rotation': {'x': 0, 'y': 0, 'z': 0},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }]}
    fixed_key_object = _fix_key_location(0, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 1
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 0, 0, 0, 0, -0.25)
    assert fixed_key_object['shows'][0]['rotation']['y'] == -45
    assert fixed_key_object['shows'][0]['rotationProperty'] == 'positive_z'


def test_fix_key_location_nondefault_position():
    # negative_x
    json_key = [[90, 90], 10, 'triangle0.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 1, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': 0, 'z': 0},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }]}
    fixed_key_object = _fix_key_location(0, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 1
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 0, 0, 1.25, 0.1, -1)
    assert fixed_key_object['shows'][0]['rotation']['y'] == -135


def test_fix_key_location_multiple_show_no_movement():
    json_key = [[90, 90], 10, 'triangle0.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 1.25, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': -135, 'z': 90},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }, {
        'stepBegin': 1,
        'position': {'x': 1, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }]}
    fixed_key_object = _fix_key_location(0, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 2
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 0, 0, 1.25, 0.1, -1)
    assert fixed_key_object['shows'][0]['rotation']['y'] == -135
    verify_show(fixed_key_object, 1, 1, 1.25, 0.1, -1)
    assert fixed_key_object['shows'][1]['rotation']['y'] == -135


def test_fix_key_location_multiple_show_movement_during_first_trial():
    json_key = [[90, 90], 10, 'triangle0.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 1.25, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': -135, 'z': 90},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }, {
        'stepBegin': 1,
        'position': {'x': 1.25, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }]}
    fixed_key_object = _fix_key_location(0, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 2
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 0, 0, 1.25, 0.1, -1)
    assert fixed_key_object['shows'][0]['rotation']['y'] == -135
    verify_show(fixed_key_object, 1, 1, 1.5, 0.6, -1)
    assert fixed_key_object['shows'][1]['rotation']['y'] == -135


def test_fix_key_location_multiple_show_reset_between_two_trials():
    json_key = [[90, 90], 10, 'triangle0.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 1.25, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': -135, 'z': 90},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }, {
        'stepBegin': 1,
        'position': {'x': 1.25, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }]}
    fixed_key_object = _fix_key_location(1, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 2
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 0, 0, 1.25, 0.1, -1)
    assert fixed_key_object['shows'][0]['rotation']['y'] == -135
    verify_show(fixed_key_object, 1, 1, 1.5, 0.1, -1)
    assert fixed_key_object['shows'][1]['rotation']['y'] == -135


def test_fix_key_location_multiple_show_movement_during_later_trial():
    json_key = [[90, 90], 10, 'triangle0.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 1.25, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': -135, 'z': 90},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }, {
        'stepBegin': 1,
        'position': {'x': 1.25, 'y': 0.6, 'z': -1},
        'rotation': {'x': 0, 'y': -135, 'z': 90}
    }, {
        'stepBegin': 2,
        'position': {'x': 1.5, 'y': 0.6, 'z': -1},
        'rotation': {'x': 0, 'y': -135, 'z': 90}
    }, {
        'stepBegin': 3,
        'position': {'x': -0.75, 'y': 0.1, 'z': 1},
        'rotation': {'x': 0, 'y': -135, 'z': 90}
    }, {
        'stepBegin': 4,
        'position': {'x': -0.75, 'y': 0.6, 'z': 0.75},
        'rotation': {'x': 0, 'y': -135, 'z': 90}
    }, {
        'stepBegin': 5,
        'position': {'x': -1, 'y': 0.1, 'z': 0.5},
        'rotation': {'x': 0, 'y': -135, 'z': 90}
    }]}
    fixed_key_object = _fix_key_location(3, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 6
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 5, 5, -0.75, 0.6, 0.5)
    assert fixed_key_object['shows'][5]['rotation']['y'] == -135


def test_fix_key_location_multiple_show_rotate_during_first_trial():
    json_key = [[90, 90], 10, 'triangle90.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 1.25, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': -135, 'z': 90},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }, {
        'stepBegin': 1,
        'position': {'x': 1, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }]}
    fixed_key_object = _fix_key_location(0, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 2
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 0, 0, 1.25, 0.1, -1)
    assert fixed_key_object['shows'][0]['rotation']['y'] == -135
    verify_show(fixed_key_object, 1, 1, 1, 0.6, -0.75)
    assert fixed_key_object['shows'][1]['rotation']['y'] == 135


def test_fix_key_location_multiple_show_rotate_between_two_trials():
    json_key = [[90, 90], 10, 'triangle90.png']
    input_key_object = {'debug': {'agentHeight': 0.5}, 'shows': [{
        'stepBegin': 0,
        'position': {'x': 1.25, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': -135, 'z': 90},
        'scale': {'x': 0.12, 'y': 0.35, 'z': 0.35}
    }, {
        'stepBegin': 1,
        'position': {'x': 1, 'y': 0.1, 'z': -1},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }]}
    fixed_key_object = _fix_key_location(1, json_key, input_key_object)
    assert len(fixed_key_object['shows']) == 2
    verify_key_show(fixed_key_object)
    verify_show(fixed_key_object, 0, 0, 1.25, 0.1, -1)
    assert fixed_key_object['shows'][0]['rotation']['y'] == -135
    verify_show(fixed_key_object, 1, 1, 1, 0.1, -0.75)
    assert fixed_key_object['shows'][1]['rotation']['y'] == 135


def test_identify_trial_index_starting_step():
    trial_list_a = [[{}], [{}], [{}]]
    assert _identify_trial_index_starting_step(0, trial_list_a) == 0
    assert _identify_trial_index_starting_step(1, trial_list_a) == 2
    assert _identify_trial_index_starting_step(2, trial_list_a) == 4

    trial_list_b = [[{}, {}, {}], [{}, {}], [{}]]
    assert _identify_trial_index_starting_step(0, trial_list_b) == 0
    assert _identify_trial_index_starting_step(1, trial_list_b) == 4
    assert _identify_trial_index_starting_step(2, trial_list_b) == 7


def test_move_agent_past_lock_location():
    agent_object = {
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 1,
            'position': {'x': 0, 'y': 0, 'z': 0.1},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 2,
            'position': {'x': 0, 'y': 0, 'z': 0.2},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.2},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 3,
            'position': {'x': 0, 'y': 0, 'z': 0.3},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.3},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 4,
            'position': {'x': 0, 'y': 0, 'z': 0.4},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 10,
            'position': {'x': 0, 'y': 0, 'z': 0.8},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.8},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 11,
            'position': {'x': 0, 'y': 0, 'z': 0.9},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.9},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 12,
            'position': {'x': 0, 'y': 0, 'z': 1},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 13,
            'position': {'x': 0, 'y': 0, 'z': 1.1},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 14,
            'position': {'x': 0, 'y': 0, 'z': 1.2},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.2},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 15,
            'position': {'x': 0, 'y': 0, 'z': 1.3},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.3},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 16,
            'position': {'x': 0, 'y': 0, 'z': 1.4},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }]
    }
    lock_bounds = geometry.create_bounds(
        dimensions={'x': 0.5, 'y': 0.5, 'z': 0.5},
        offset=None,
        position={'x': 0, 'y': 0, 'z': 0.8},
        rotation={'x': 0, 'y': 0, 'z': 0},
        standing_y=0
    )
    lock_object = {
        'debug': {
            'boundsAtStep': ([lock_bounds] * 5) + ([None] * 12)
        },
        'hides': [{'stepBegin': 5}]
    }

    _move_agent_past_lock_location([agent_object], [lock_object])

    verify_show(agent_object, 0, 0, 0, 0, 0)
    verify_show(agent_object, 1, 1, 0, 0, 0.1)
    verify_show(agent_object, 2, 2, 0, 0, 0.2)
    verify_show(agent_object, 3, 3, 0, 0, 0.3)
    verify_show(agent_object, 4, 4, 0, 0, 0.4)
    verify_show(agent_object, 5, 10, 0, 0, 0.56)
    verify_show(agent_object, 6, 11, 0, 0, 0.72)
    verify_show(agent_object, 7, 12, 0, 0, 0.88)
    verify_show(agent_object, 8, 13, 0, 0, 1.04)
    verify_show(agent_object, 9, 14, 0, 0, 1.2)
    verify_show(agent_object, 10, 15, 0, 0, 1.3)
    verify_show(agent_object, 11, 16, 0, 0, 1.4)
    assert len(agent_object['shows']) == 12


def test_move_agent_past_lock_location_move_back():
    agent_object = {
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 1,
            'position': {'x': 0, 'y': 0, 'z': 0.1},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 2,
            'position': {'x': 0, 'y': 0, 'z': 0.2},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.2},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 3,
            'position': {'x': 0, 'y': 0, 'z': 0.3},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.3},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 4,
            'position': {'x': 0, 'y': 0, 'z': 0.4},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 10,
            'position': {'x': 0, 'y': 0, 'z': 0.8},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.8},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 11,
            'position': {'x': 0, 'y': 0, 'z': 0.7},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.7},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 12,
            'position': {'x': 0, 'y': 0, 'z': 0.6},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.6},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 13,
            'position': {'x': 0, 'y': 0, 'z': 0.5},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.5},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 14,
            'position': {'x': 0, 'y': 0, 'z': 0.4},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 15,
            'position': {'x': 0, 'y': 0, 'z': 0.3},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.3},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 16,
            'position': {'x': 0, 'y': 0, 'z': 0.2},
            'boundingBox': geometry.create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.2},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }]
    }
    lock_bounds = geometry.create_bounds(
        dimensions={'x': 0.5, 'y': 0.5, 'z': 0.5},
        offset=None,
        position={'x': 0, 'y': 0, 'z': 0.8},
        rotation={'x': 0, 'y': 0, 'z': 0},
        standing_y=0
    )
    lock_object = {
        'debug': {
            'boundsAtStep': ([lock_bounds] * 5) + ([None] * 12)
        },
        'hides': [{'stepBegin': 5}]
    }

    _move_agent_past_lock_location([agent_object], [lock_object])

    verify_show(agent_object, 0, 0, 0, 0, 0)
    verify_show(agent_object, 1, 1, 0, 0, 0.1)
    verify_show(agent_object, 2, 2, 0, 0, 0.2)
    verify_show(agent_object, 3, 3, 0, 0, 0.3)
    verify_show(agent_object, 4, 4, 0, 0, 0.4)
    verify_show(agent_object, 5, 14, 0, 0, 0.4)
    verify_show(agent_object, 6, 15, 0, 0, 0.3)
    verify_show(agent_object, 7, 16, 0, 0, 0.2)
    assert len(agent_object['shows']) == 8


def test_remove_extraneous_object_show_single_step():
    agent_object_list = [{
        'shows': [
            {'stepBegin': 0, 'position': {'x': 0, 'z': 0}}
        ]
    }]

    _remove_extraneous_object_show(agent_object_list, [[{}]])

    assert len(agent_object_list[0]['shows']) == 1


def test_remove_extraneous_object_show_no_extraneous():
    agent_object_list = [{
        'shows': [
            {'stepBegin': 0, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 1, 'position': {'x': 1, 'z': 0}},
            {'stepBegin': 2, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 3, 'position': {'x': 0, 'z': 1}},
            {'stepBegin': 4, 'position': {'x': 0, 'z': 0}}
        ]
    }]

    _remove_extraneous_object_show(agent_object_list, [[{}] * 4])

    assert len(agent_object_list[0]['shows']) == 5


def test_remove_extraneous_object_show_multiple_extraneous():
    agent_object_list = [{
        'shows': [
            {'stepBegin': 0, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 1, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 2, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 3, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 4, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 5, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 6, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 7, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 8, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 9, 'position': {'x': -1, 'z': -1}},
            {'stepBegin': 10, 'position': {'x': -1, 'z': -1}}
        ]
    }]

    _remove_extraneous_object_show(agent_object_list, [[{}] * 10])

    assert len(agent_object_list[0]['shows']) == 4
    assert agent_object_list[0]['shows'][0]['position']['x'] == 0
    assert agent_object_list[0]['shows'][0]['position']['z'] == 0
    assert agent_object_list[0]['shows'][1]['position']['x'] == 1
    assert agent_object_list[0]['shows'][1]['position']['z'] == 1
    assert agent_object_list[0]['shows'][2]['position']['x'] == 0
    assert agent_object_list[0]['shows'][2]['position']['z'] == 0
    assert agent_object_list[0]['shows'][3]['position']['x'] == -1
    assert agent_object_list[0]['shows'][3]['position']['z'] == -1


def test_remove_extraneous_object_show_multiple_agents():
    agent_object_list = [{
        'shows': [
            {'stepBegin': 0, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 1, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 2, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 3, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 4, 'position': {'x': -1, 'z': -1}},
            {'stepBegin': 5, 'position': {'x': -1, 'z': -1}},
            {'stepBegin': 6, 'position': {'x': -1, 'z': -1}}
        ]
    }, {
        'shows': [
            {'stepBegin': 0, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 1, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 2, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 3, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 4, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 5, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 6, 'position': {'x': 0, 'z': 0}}
        ]
    }]

    _remove_extraneous_object_show(agent_object_list, [[{}] * 6])

    assert len(agent_object_list[0]['shows']) == 2
    assert agent_object_list[0]['shows'][0]['position']['x'] == 0
    assert agent_object_list[0]['shows'][0]['position']['z'] == 0
    assert agent_object_list[0]['shows'][1]['position']['x'] == -1
    assert agent_object_list[0]['shows'][1]['position']['z'] == -1

    assert len(agent_object_list[1]['shows']) == 2
    assert agent_object_list[1]['shows'][0]['position']['x'] == 1
    assert agent_object_list[1]['shows'][0]['position']['z'] == 1
    assert agent_object_list[1]['shows'][1]['position']['x'] == 0
    assert agent_object_list[1]['shows'][1]['position']['z'] == 0


def test_remove_extraneous_object_show_multiple_extraneous_across_trials():
    agent_object_list = [{
        'shows': [
            {'stepBegin': 0, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 1, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 2, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 3, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 4, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 5, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 6, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 7, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 8, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 9, 'position': {'x': -1, 'z': -1}},
            {'stepBegin': 10, 'position': {'x': -1, 'z': -1}}
        ]
    }]

    _remove_extraneous_object_show(agent_object_list, [[{}] * 7, [{}] * 3])

    assert len(agent_object_list[0]['shows']) == 5
    assert agent_object_list[0]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[0]['shows'][0]['position']['x'] == 0
    assert agent_object_list[0]['shows'][0]['position']['z'] == 0
    assert agent_object_list[0]['shows'][1]['stepBegin'] == 3
    assert agent_object_list[0]['shows'][1]['position']['x'] == 1
    assert agent_object_list[0]['shows'][1]['position']['z'] == 1
    assert agent_object_list[0]['shows'][2]['stepBegin'] == 6
    assert agent_object_list[0]['shows'][2]['position']['x'] == 0
    assert agent_object_list[0]['shows'][2]['position']['z'] == 0
    assert agent_object_list[0]['shows'][3]['stepBegin'] == 8
    assert agent_object_list[0]['shows'][3]['position']['x'] == 0
    assert agent_object_list[0]['shows'][3]['position']['z'] == 0
    assert agent_object_list[0]['shows'][4]['stepBegin'] == 9
    assert agent_object_list[0]['shows'][4]['position']['x'] == -1
    assert agent_object_list[0]['shows'][4]['position']['z'] == -1


def test_remove_extraneous_object_show_multiple_agents_across_trials():
    agent_object_list = [{
        'shows': [
            {'stepBegin': 0, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 1, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 2, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 3, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 4, 'position': {'x': -1, 'z': -1}},
            {'stepBegin': 5, 'position': {'x': -1, 'z': -1}},
            {'stepBegin': 6, 'position': {'x': -1, 'z': -1}}
        ]
    }, {
        'shows': [
            {'stepBegin': 0, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 1, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 2, 'position': {'x': 1, 'z': 1}},
            {'stepBegin': 3, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 4, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 5, 'position': {'x': 0, 'z': 0}},
            {'stepBegin': 6, 'position': {'x': 0, 'z': 0}}
        ]
    }]

    _remove_extraneous_object_show(agent_object_list, [[{}] * 3, [{}] * 3])

    assert len(agent_object_list[0]['shows']) == 2
    assert agent_object_list[0]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[0]['shows'][0]['position']['x'] == 0
    assert agent_object_list[0]['shows'][0]['position']['z'] == 0
    assert agent_object_list[0]['shows'][1]['stepBegin'] == 4
    assert agent_object_list[0]['shows'][1]['position']['x'] == -1
    assert agent_object_list[0]['shows'][1]['position']['z'] == -1

    assert len(agent_object_list[1]['shows']) == 3
    assert agent_object_list[1]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[1]['shows'][0]['position']['x'] == 1
    assert agent_object_list[1]['shows'][0]['position']['z'] == 1
    assert agent_object_list[1]['shows'][1]['stepBegin'] == 3
    assert agent_object_list[1]['shows'][1]['position']['x'] == 0
    assert agent_object_list[1]['shows'][1]['position']['z'] == 0
    assert agent_object_list[1]['shows'][2]['stepBegin'] == 4
    assert agent_object_list[1]['shows'][2]['position']['x'] == 0
    assert agent_object_list[1]['shows'][2]['position']['z'] == 0


def test_remove_intersecting_agent_steps_with_no_intersection():
    agent_object_list = [{
        'debug': {
            'boundsAtStep': [
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(2, 0, 2, 0),
                create_bounds(3, 1, 3, 1),
                create_bounds(4, 2, 4, 2),
                create_bounds(4, 2, 4, 2),
                create_bounds(4, 2, 4, 2)
            ]
        },
        'shows': [
            {'stepBegin': 0},
            {'stepBegin': 3},
            {'stepBegin': 4},
            {'stepBegin': 5}
        ]
    }]

    goal_object_list = [{
        'debug': {
            'boundsAtStep': [create_bounds(6.1, 4.1, 6.1, 4.1)] * 8
        }
    }]

    _remove_intersecting_agent_steps(agent_object_list, goal_object_list)

    assert len(agent_object_list[0]['shows']) == 4


def test_remove_intersecting_agent_steps_with_intersection():
    agent_object_list = [{
        'debug': {
            'boundsAtStep': [
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(2, 0, 2, 0),
                create_bounds(3, 1, 3, 1),
                create_bounds(3, 1, 3, 1),
                create_bounds(3, 1, 3, 1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(0, -2, 0, -2),
                create_bounds(-1, -3, -1, -3),
                create_bounds(-1, -3, -1, -3),
                create_bounds(-1, -3, -1, -3)
            ]
        },
        'shows': [
            {'stepBegin': 0},
            {'stepBegin': 3},
            {'stepBegin': 4},
            {'stepBegin': 7},
            {'stepBegin': 10},
            {'stepBegin': 11}
        ]
    }]

    goal_object_list = [{
        'debug': {
            'boundsAtStep': [create_bounds(3.9, 2.9, 3.9, 2.9)] * 14
        }
    }]

    _remove_intersecting_agent_steps(agent_object_list, goal_object_list)

    assert len(agent_object_list[0]['shows']) == 5
    assert agent_object_list[0]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[0]['shows'][1]['stepBegin'] == 3
    assert agent_object_list[0]['shows'][2]['stepBegin'] == 7
    assert agent_object_list[0]['shows'][3]['stepBegin'] == 10
    assert agent_object_list[0]['shows'][4]['stepBegin'] == 11


def test_remove_intersecting_agent_steps_with_multiple_agents():
    agent_object_list = [{
        'debug': {
            'boundsAtStep': [
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(2, 0, 2, 0),
                create_bounds(3, 1, 3, 1),
                create_bounds(3, 1, 3, 1),
                create_bounds(3, 1, 3, 1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(0, -2, 0, -2),
                create_bounds(-1, -3, -1, -3),
                create_bounds(-1, -3, -1, -3),
                create_bounds(-1, -3, -1, -3)
            ]
        },
        'shows': [
            {'stepBegin': 0},
            {'stepBegin': 3},
            {'stepBegin': 4},
            {'stepBegin': 7},
            {'stepBegin': 10},
            {'stepBegin': 11}
        ]
    }, {
        'debug': {
            'boundsAtStep': [
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(0, -2, 0, -2),
                create_bounds(-1, -3, -1, -3),
                create_bounds(-1, -3, -1, -3),
                create_bounds(-1, -3, -1, -3),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(2, 0, 2, 0),
                create_bounds(3, 1, 3, 1),
                create_bounds(3, 1, 3, 1),
                create_bounds(3, 1, 3, 1)
            ]
        },
        'shows': [
            {'stepBegin': 0},
            {'stepBegin': 3},
            {'stepBegin': 4},
            {'stepBegin': 7},
            {'stepBegin': 10},
            {'stepBegin': 11}
        ]
    }]

    goal_object_list = [{
        'debug': {
            'boundsAtStep': [create_bounds(3.9, 2.9, 3.9, 2.9)] * 14
        }
    }]

    _remove_intersecting_agent_steps(agent_object_list, goal_object_list)

    assert len(agent_object_list[0]['shows']) == 5
    assert agent_object_list[0]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[0]['shows'][1]['stepBegin'] == 3
    assert agent_object_list[0]['shows'][2]['stepBegin'] == 7
    assert agent_object_list[0]['shows'][3]['stepBegin'] == 10
    assert agent_object_list[0]['shows'][4]['stepBegin'] == 11

    assert len(agent_object_list[1]['shows']) == 5
    assert agent_object_list[1]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[1]['shows'][1]['stepBegin'] == 3
    assert agent_object_list[1]['shows'][2]['stepBegin'] == 4
    assert agent_object_list[1]['shows'][3]['stepBegin'] == 7
    assert agent_object_list[1]['shows'][4]['stepBegin'] == 10


def test_remove_intersecting_agent_steps_with_multiple_objects():
    agent_object_list = [{
        'debug': {
            'boundsAtStep': [
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(2, 0, 2, 0),
                create_bounds(3, 1, 3, 1),
                create_bounds(3, 1, 3, 1),
                create_bounds(3, 1, 3, 1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(1, -1, 1, -1),
                create_bounds(0, -2, 0, -2),
                create_bounds(-1, -3, -1, -3),
                create_bounds(-1, -3, -1, -3),
                create_bounds(-1, -3, -1, -3)
            ]
        },
        'shows': [
            {'stepBegin': 0},
            {'stepBegin': 3},
            {'stepBegin': 4},
            {'stepBegin': 7},
            {'stepBegin': 10},
            {'stepBegin': 11}
        ]
    }]

    goal_object_list = [{
        'debug': {
            'boundsAtStep': [create_bounds(2.9, 1.9, 3.9, 2.9)] * 14
        }
    }, {
        'debug': {
            'boundsAtStep': [create_bounds(-3.9, -2.9, -2.9, -1.9)] * 14
        }
    }]

    _remove_intersecting_agent_steps(agent_object_list, goal_object_list)

    assert len(agent_object_list[0]['shows']) == 4
    assert agent_object_list[0]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[0]['shows'][1]['stepBegin'] == 3
    assert agent_object_list[0]['shows'][2]['stepBegin'] == 7
    assert agent_object_list[0]['shows'][3]['stepBegin'] == 10


def test_retrieve_unit_size():
    assert _retrieve_unit_size([[{'size': [200, 200]}]]) == UNIT_SIZE
    assert _retrieve_unit_size([[{'size': [100, 400]}]]) == [0.05, 0.0125]
