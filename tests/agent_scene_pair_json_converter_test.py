import pytest

from agent_scene_pair_json_converter import _choose_config_list, \
    _choose_object_config, _create_action_list, _create_agent_object_list, \
    _create_goal_object_list, _create_home_object, _create_object, \
    _create_scene, _create_show, _create_trial_frame_list, \
    _create_wall_object_list, _identify_trial_index_starting_step, \
    _remove_extraneous_agent_shows, _remove_intersecting_agent_steps, \
    _retrieve_unit_size, ObjectConfig, ObjectConfigWithMaterial
import exceptions
import hypercubes


def create_bounds(x1, x2, z1, z2):
    return [
        {'x': x, 'z': z} for x, z in [(x1, z1), (x1, z2), (x2, z2), (x2, z1)]
    ]


def verify_bounds(mcs_object, step, x1, x2, z1, z2):
    assert mcs_object['boundsAtStep'][step][0]['x'] == pytest.approx(x1)
    assert mcs_object['boundsAtStep'][step][0]['z'] == pytest.approx(z1)
    assert mcs_object['boundsAtStep'][step][1]['x'] == pytest.approx(x1)
    assert mcs_object['boundsAtStep'][step][1]['z'] == pytest.approx(z2)
    assert mcs_object['boundsAtStep'][step][2]['x'] == pytest.approx(x2)
    assert mcs_object['boundsAtStep'][step][2]['z'] == pytest.approx(z2)
    assert mcs_object['boundsAtStep'][step][3]['x'] == pytest.approx(x2)
    assert mcs_object['boundsAtStep'][step][3]['z'] == pytest.approx(z1)


def verify_show(mcs_object, index, step, x, y, z):
    assert mcs_object['shows'][index]['stepBegin'] == step
    assert mcs_object['shows'][index]['position']['x'] == x
    assert mcs_object['shows'][index]['position']['y'] == y
    assert mcs_object['shows'][index]['position']['z'] == z
    if step > 0:
        assert 'scale' not in mcs_object['shows'][index]


def test_choose_config_list_with_agent():
    config_object_type_list = ['a', 'b', 'c', 'd']
    config_list = [
        ObjectConfig(object_type, index, index, index, index)
        for index, object_type in enumerate(config_object_type_list)
    ]
    material_list = ['e', 'f', 'g', 'h']

    trial_list = [[{
        'agent': []
    }]]
    chosen_config_list = _choose_config_list(
        trial_list,
        config_list,
        [None],
        material_list,
        'agent'
    )
    assert len(chosen_config_list) == 1
    assert chosen_config_list[0].object_type in config_object_type_list
    assert chosen_config_list[0].material in material_list


def test_choose_config_list_with_objects():
    config_object_type_list = ['a', 'b', 'c', 'd']
    config_list = [
        ObjectConfig(object_type, index, index, index, index)
        for index, object_type in enumerate(config_object_type_list)
    ]
    material_list = ['e', 'f', 'g', 'h']

    trial_list_a = [[{
        'objects': [[], []]
    }]]
    chosen_config_list_a = _choose_config_list(
        trial_list_a,
        config_list,
        [None, None],
        material_list,
        'objects'
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
        'objects'
    )
    assert len(chosen_config_list_b) == 1
    assert chosen_config_list_b[0].object_type in config_object_type_list
    assert chosen_config_list_b[0].material in material_list


def test_choose_object_config():
    config_object_type_list = ['a', 'b', 'c', 'd']
    config_list = [
        ObjectConfig(object_type, index, index, index, index)
        for index, object_type in enumerate(config_object_type_list)
    ]
    material_list = ['e', 'f', 'g', 'h']
    used_config_index_list = []
    used_material_index_list = []

    config_a = _choose_object_config(
        config_list,
        material_list,
        used_config_index_list,
        used_material_index_list
    )
    assert len(used_config_index_list) == 1
    assert len(used_material_index_list) == 1
    assert config_a.object_type == config_object_type_list[
        used_config_index_list[0]
    ]
    assert config_a.material == material_list[used_material_index_list[0]]

    config_b = _choose_object_config(
        config_list,
        material_list,
        used_config_index_list,
        used_material_index_list
    )
    assert len(used_config_index_list) == 2
    assert len(used_material_index_list) == 2
    assert used_config_index_list[0] != used_config_index_list[1]
    assert used_material_index_list[0] != used_material_index_list[1]
    assert config_b.object_type == config_object_type_list[
        used_config_index_list[1]
    ]
    assert config_b.material == material_list[used_material_index_list[1]]


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
        'agent': [[25, 25], 5]
    }, {
        'agent': [[30, 30], 5]
    }, {
        'agent': [[35, 35], 5]
    }], [{
        'agent': [[95, 95], 5]
    }, {
        'agent': [[95, 100], 5]
    }, {
        'agent': [[95, 105], 5]
    }, {
        'agent': [[95, 110], 5]
    }], [{
        'agent': [[165, 165], 5]
    }, {
        'agent': [[160, 165], 5]
    }, {
        'agent': [[155, 165], 5]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('test_type', 1, 2, 3, 4),
            ('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    agent_object_list = _create_agent_object_list(
        trial_list,
        object_config_with_material_list,
        [0.025, 0.025]
    )

    assert len(agent_object_list) == 1
    agent_object = agent_object_list[0]

    assert agent_object['id'].startswith('agent_')
    assert agent_object['type'] == 'test_type'
    assert agent_object['materials'] == ['test_material']
    assert agent_object['info'] == [
        'test_color_a', 'test_color_b', 'test_type',
        'test_color_a test_color_b test_type'
    ]
    assert agent_object['configHeight'] == [1, 3]
    assert agent_object['configSize'] == [2, 4]

    assert len(agent_object['shows']) == 10
    verify_show(agent_object, 0, 0, -1.75, 1, -1.75)
    assert agent_object['shows'][0]['scale']['x'] == 2
    assert agent_object['shows'][0]['scale']['y'] == 3
    assert agent_object['shows'][0]['scale']['z'] == 4

    verify_show(agent_object, 1, 1, -1.625, 1, -1.625)
    verify_show(agent_object, 2, 2, -1.5, 1, -1.5)
    verify_show(agent_object, 3, 4, 0, 1, 0)
    verify_show(agent_object, 4, 5, 0, 1, 0.125)
    verify_show(agent_object, 5, 6, 0, 1, 0.25)
    verify_show(agent_object, 6, 7, 0, 1, 0.375)
    verify_show(agent_object, 7, 9, 1.75, 1, 1.75)
    verify_show(agent_object, 8, 10, 1.625, 1, 1.75)
    verify_show(agent_object, 9, 11, 1.5, 1, 1.75)

    assert len(agent_object['boundsAtStep']) == 13
    verify_bounds(agent_object, 0, -0.75, -2.75, 0.25, -3.75)
    verify_bounds(agent_object, 1, -0.625, -2.625, 0.375, -3.625)
    verify_bounds(agent_object, 2, -0.5, -2.5, 0.5, -3.5)
    verify_bounds(agent_object, 3, -0.5, -2.5, 0.5, -3.5)
    verify_bounds(agent_object, 4, 1, -1, 2, -2)
    verify_bounds(agent_object, 5, 1, -1, 2.125, -1.875)
    verify_bounds(agent_object, 6, 1, -1, 2.25, -1.75)
    verify_bounds(agent_object, 7, 1, -1, 2.375, -1.625)
    verify_bounds(agent_object, 8, 1, -1, 2.375, -1.625)
    verify_bounds(agent_object, 9, 2.75, 0.75, 3.75, -0.25)
    verify_bounds(agent_object, 10, 2.625, 0.625, 3.75, -0.25)
    verify_bounds(agent_object, 11, 2.5, 0.5, 3.75, -0.25)
    verify_bounds(agent_object, 12, 2.5, 0.5, 3.75, -0.25)


def test_create_goal_object_list_single_object():
    trial_list = [[{
        'objects': [
            [[25, 25], 5]
        ]
    }], [{
        'objects': [
            [[95, 95], 5]
        ]
    }], [{
        'objects': [
            [[165, 165], 5]
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('test_type', 1, 2, 3, 4),
            ('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = [
        {'x': 10, 'z': 10}, {'x': 10, 'z': 12},
        {'x': 12, 'z': 12}, {'x': 12, 'z': 10}
    ]

    goal_object_list = _create_goal_object_list(
        trial_list,
        object_config_with_material_list,
        mock_agent_start_bounds,
        'filename',
        [0.025, 0.025]
    )

    assert len(goal_object_list) == 1
    goal_object_1 = goal_object_list[0]

    assert goal_object_1['id'].startswith('object_')
    assert goal_object_1['type'] == 'test_type'
    assert goal_object_1['materials'] == ['test_material']
    assert goal_object_1['info'] == [
        'test_color_a', 'test_color_b', 'test_type',
        'test_color_a test_color_b test_type'
    ]
    assert goal_object_1['configHeight'] == [1, 3]
    assert goal_object_1['configSize'] == [2, 4]

    assert len(goal_object_1['shows']) == 3
    verify_show(goal_object_1, 0, 0, -1.75, 1, -1.75)
    assert goal_object_1['shows'][0]['scale']['x'] == 2
    assert goal_object_1['shows'][0]['scale']['y'] == 3
    assert goal_object_1['shows'][0]['scale']['z'] == 4

    verify_show(goal_object_1, 1, 2, 0, 1, 0)
    verify_show(goal_object_1, 2, 4, 1.75, 1, 1.75)

    assert len(goal_object_1['boundsAtStep']) == 6
    verify_bounds(goal_object_1, 0, -0.75, -2.75, 0.25, -3.75)
    verify_bounds(goal_object_1, 1, -0.75, -2.75, 0.25, -3.75)
    verify_bounds(goal_object_1, 2, 1, -1, 2, -2)
    verify_bounds(goal_object_1, 3, 1, -1, 2, -2)
    verify_bounds(goal_object_1, 4, 2.75, 0.75, 3.75, -0.25)
    verify_bounds(goal_object_1, 5, 2.75, 0.75, 3.75, -0.25)


def test_create_goal_object_list_multiple_object():
    trial_list = [[{
        'objects': [
            [[25, 165], 5],
            [[160, 20], 10]
        ]
    }], [{
        'objects': [
            [[90, 100], 5],
            [[95, 85], 10]
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('test_type_1', 1, 2, 3, 4),
            ('test_material_1', ['test_color_a', 'test_color_b'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('test_type_2', 5, 6, 7, 8),
            ('test_material_2', ['test_color_c'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = [
        {'x': 10, 'z': 10}, {'x': 10, 'z': 12},
        {'x': 12, 'z': 12}, {'x': 12, 'z': 10}
    ]

    goal_object_list = _create_goal_object_list(
        trial_list,
        object_config_with_material_list,
        mock_agent_start_bounds,
        'filename',
        [0.025, 0.025]
    )

    assert len(goal_object_list) == 2
    goal_object_1 = goal_object_list[0]
    goal_object_2 = goal_object_list[1]

    assert goal_object_1['id'].startswith('object_')
    assert goal_object_1['type'] == 'test_type_1'
    assert goal_object_1['materials'] == ['test_material_1']
    assert goal_object_1['info'] == [
        'test_color_a', 'test_color_b', 'test_type_1',
        'test_color_a test_color_b test_type_1'
    ]
    assert goal_object_1['configHeight'] == [1, 3]
    assert goal_object_1['configSize'] == [2, 4]

    assert len(goal_object_1['shows']) == 2
    verify_show(goal_object_1, 0, 0, -1.75, 1, 1.75)
    assert goal_object_1['shows'][0]['scale']['x'] == 2
    assert goal_object_1['shows'][0]['scale']['y'] == 3
    assert goal_object_1['shows'][0]['scale']['z'] == 4
    verify_show(goal_object_1, 1, 2, -0.125, 1, 0.125)

    assert len(goal_object_1['boundsAtStep']) == 4
    verify_bounds(goal_object_1, 0, -0.75, -2.75, 3.75, -0.25)
    verify_bounds(goal_object_1, 1, -0.75, -2.75, 3.75, -0.25)
    verify_bounds(goal_object_1, 2, 0.875, -1.125, 2.125, -1.875)
    verify_bounds(goal_object_1, 3, 0.875, -1.125, 2.125, -1.875)

    assert goal_object_2['id'].startswith('object_')
    assert goal_object_2['type'] == 'test_type_2'
    assert goal_object_2['materials'] == ['test_material_2']
    assert goal_object_2['info'] == [
        'test_color_c', 'test_type_2', 'test_color_c test_type_2'
    ]
    assert goal_object_2['configHeight'] == [5, 7]
    assert goal_object_2['configSize'] == [6, 8]

    assert len(goal_object_2['shows']) == 2
    verify_show(goal_object_2, 0, 0, 1.75, 5, -1.75)
    assert goal_object_2['shows'][0]['scale']['x'] == 6
    assert goal_object_2['shows'][0]['scale']['y'] == 7
    assert goal_object_2['shows'][0]['scale']['z'] == 8
    verify_show(goal_object_2, 1, 2, 0.125, 5, -0.125)

    assert len(goal_object_2['boundsAtStep']) == 4
    verify_bounds(goal_object_2, 0, 4.75, -1.25, 2.25, -5.75)
    verify_bounds(goal_object_2, 1, 4.75, -1.25, 2.25, -5.75)
    verify_bounds(goal_object_2, 2, 3.125, -2.875, 3.875, -4.125)
    verify_bounds(goal_object_2, 3, 3.125, -2.875, 3.875, -4.125)


def test_create_goal_object_list_single_object_on_home():
    trial_list = [[{
        'objects': [
            [[20, 20], 5]
        ]
    }], [{
        'objects': [
            [[90, 90], 5]
        ]
    }], [{
        'objects': [
            [[160, 160], 5]
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('test_type', 0.125, 0.25, 0.25, 0.25),
            ('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    agent_start_bounds = [
        {'x': -0.25, 'z': -0.25}, {'x': -0.25, 'z': 0.25},
        {'x': 0.25, 'z': 0.25}, {'x': 0.25, 'z': -0.25}
    ]

    with pytest.raises(exceptions.SceneException):
        _create_goal_object_list(
            trial_list,
            object_config_with_material_list,
            agent_start_bounds,
            'filename',
            [0.025, 0.025]
        )


def test_create_goal_object_list_multiple_object_on_home():
    trial_list = [[{
        'objects': [
            [[20, 20], 5],
            [[100, 100], 5]
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('test_type_1', 0.125, 0.25, 0.25, 0.25),
            ('test_material_1', ['test_color_a', 'test_color_b'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('test_type_2', 0.125, 0.25, 0.25, 0.25),
            ('test_material_2', ['test_color_c'])
        )
    ]

    agent_start_bounds = [
        {'x': -0.25, 'z': -0.25}, {'x': -0.25, 'z': 0.25},
        {'x': 0.25, 'z': 0.25}, {'x': 0.25, 'z': -0.25}
    ]

    with pytest.raises(exceptions.SceneException):
        _create_goal_object_list(
            trial_list,
            object_config_with_material_list,
            agent_start_bounds,
            'filename',
            [0.025, 0.025]
        )


def test_create_home_object():
    trial_list = [[{
        'home': [[95, 95], 5]
    }]]

    home_object = _create_home_object(trial_list, [0.025, 0.025])

    assert home_object['id'].startswith('home_')
    assert home_object['type'] == 'cube'
    assert home_object['materials'] == ['Custom/Materials/Magenta']
    assert home_object['info'] == ['magenta', 'cube', 'magenta cube']
    assert home_object['configHeight'] == [0.000625, 0.00125]
    assert home_object['configSize'] == [0.5, 0.5]

    assert len(home_object['shows']) == 1
    verify_show(home_object, 0, 0, 0, 0.000625, 0)
    assert home_object['shows'][0]['scale']['x'] == 0.5
    assert home_object['shows'][0]['scale']['y'] == 0.00125
    assert home_object['shows'][0]['scale']['z'] == 0.5


def test_create_home_object_uses_first_frame_of_first_trial():
    trial_list = [[{
        'home': [[20, 160], 10]
    }, {
        'home': [[40, 140], 10]
    }], [{
        'home': [[60, 120], 10]
    }]]

    home_object = _create_home_object(trial_list, [0.025, 0.025])

    assert home_object['id'].startswith('home_')
    assert home_object['type'] == 'cube'
    assert home_object['materials'] == ['Custom/Materials/Magenta']
    assert home_object['info'] == ['magenta', 'cube', 'magenta cube']
    assert home_object['configHeight'] == [0.000625, 0.00125]
    assert home_object['configSize'] == [0.5, 0.5]

    assert len(home_object['shows']) == 1
    verify_show(home_object, 0, 0, -1.75, 0.000625, 1.75)
    assert home_object['shows'][0]['scale']['x'] == 0.5
    assert home_object['shows'][0]['scale']['y'] == 0.00125
    assert home_object['shows'][0]['scale']['z'] == 0.5


def test_create_object():
    mcs_object = _create_object(
        'id_',
        'test_type',
        ('test_material', ['test_color_a', 'test_color_b']),
        [1, 2],
        [3, 4],
        [25, 50],
        [10, 20],
        [0.025, 0.025]
    )

    assert mcs_object['id'].startswith('id_')
    assert mcs_object['type'] == 'test_type'
    assert mcs_object['materials'] == ['test_material']
    assert mcs_object['info'] == [
        'test_color_a', 'test_color_b', 'test_type',
        'test_color_a test_color_b test_type'
    ]
    assert mcs_object['configHeight'] == [1, 2]
    assert mcs_object['configSize'] == [3, 4]

    assert len(mcs_object['shows']) == 1
    verify_show(mcs_object, 0, 0, -1.75, 1, -1)
    assert mcs_object['shows'][0]['scale']['x'] == 3
    assert mcs_object['shows'][0]['scale']['y'] == 2
    assert mcs_object['shows'][0]['scale']['z'] == 4

    assert len(mcs_object['boundsAtStep']) == 1
    verify_bounds(mcs_object, 0, -0.25, -3.25, 1, -3)


def test_create_scene():
    body_template = {'objects': []}
    goal_template = hypercubes.initialize_goal(
        {'category': 'mock', 'domainsInfo': {}, 'sceneInfo': {}}
    )

    agent_object_config_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('test_type', 0.1, 0.2, 0.3, 0.4),
            ('test_material', ['test_color'])
        )
    ]
    goal_object_config_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('test_type', 0.1, 0.2, 0.3, 0.4),
            ('test_material', ['test_color'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('test_type', 0.1, 0.2, 0.3, 0.4),
            ('test_material', ['test_color'])
        )
    ]

    trial_list = [[{
        'agent': [[25, 25], 5],
        'home': [[25, 25], 5],
        'objects': [
            [[25, 45], 5],
            [[95, 95], 5]
        ],
        'size': [200, 200],
        'walls': [
            [[60, 60], [20, 20]],
            [[60, 120], [20, 20]],
            [[120, 60], [20, 20]],
            [[120, 120], [20, 20]]
        ]
    }, {
        'agent': [[25, 25], 5],
    }, {
        'agent': [[25, 30], 5]
    }, {
        'agent': [[25, 35], 5]
    }, {
        'agent': [[25, 35], 5]
    }], [{
        'agent': [[25, 25], 5],
        'objects': [
            [[45, 25], 5],
            [[165, 165], 5]
        ],
        'walls': [
            [[60, 60], [20, 20]],
            [[60, 120], [20, 20]],
            [[120, 60], [20, 20]],
            [[120, 120], [20, 20]]
        ]
    }, {
        'agent': [[25, 25], 5],
    }, {
        'agent': [[30, 25], 5]
    }, {
        'agent': [[35, 25], 5]
    }, {
        'agent': [[35, 25], 5]
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
        assert scene['floorMaterial'] == 'Custom/Materials/White'
        assert scene['wallMaterial'] == 'Custom/Materials/Black'
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

        assert len(scene['objects']) == 8
        agent_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['role'] == 'agent'
        ]
        assert len(agent_object_list) == 1
        home_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['role'] == 'home'
        ]
        assert len(home_object_list) == 1
        non_target_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['role'] == 'non target'
        ]
        assert len(non_target_object_list) == 1
        target_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['role'] == 'target'
        ]
        assert len(target_object_list) == 1
        wall_object_list = [
            mcs_object for mcs_object in scene['objects']
            if mcs_object['role'] == 'wall'
        ]
        assert len(wall_object_list) == 4


def test_create_show():
    show = _create_show(
        1234,
        [1, 2],
        [3, 4],
        [25, 50],
        [10, 20],
        [0.025, 0.025]
    )

    assert show['stepBegin'] == 1234
    assert show['position']['x'] == -1.75
    assert show['position']['y'] == 1
    assert show['position']['z'] == -1
    assert show['scale']['x'] == 3
    assert show['scale']['y'] == 2
    assert show['scale']['z'] == 4


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


def test_create_wall_object_list():
    trial_list = [[{
        'walls': [
            [[20, 20], [20, 20]],
            [[20, 160], [20, 20]],
            [[160, 20], [20, 20]],
            [[160, 160], [20, 20]],
            [[90, 90], [20, 20]]
        ]
    }]]

    # Add each border wall.
    for i in range(0, 200, 20):
        trial_list[0][0]['walls'].extend([
            [[0, i], [20, 20]],
            [[i, 0], [20, 20]],
            [[180, i], [20, 20]],
            [[i, 180], [20, 20]]
        ])

    wall_object_list = _create_wall_object_list(trial_list, [0.025, 0.025])

    assert len(wall_object_list) == 5
    verify_show(wall_object_list[0], 0, 0, -1.75, 0.0625, -1.75)
    verify_show(wall_object_list[1], 0, 0, -1.75, 0.0625, 1.75)
    verify_show(wall_object_list[2], 0, 0, 1.75, 0.0625, -1.75)
    verify_show(wall_object_list[3], 0, 0, 1.75, 0.0625, 1.75)
    verify_show(wall_object_list[4], 0, 0, 0, 0.0625, 0)

    for wall_object in wall_object_list:
        assert wall_object['id'].startswith('wall_')
        assert wall_object['type'] == 'cube'
        assert wall_object['materials'] == ['Custom/Materials/Black']
        assert wall_object['info'] == ['black', 'cube', 'black cube']
        assert wall_object['configHeight'] == [0.0625, 0.125]
        assert wall_object['configSize'] == [0.5, 0.5]

        assert len(wall_object['shows']) == 1
        assert wall_object['shows'][0]['scale']['x'] == 0.5
        assert wall_object['shows'][0]['scale']['y'] == 0.125
        assert wall_object['shows'][0]['scale']['z'] == 0.5

        assert 'hides' not in wall_object


def test_create_wall_object_list_remove_wall():
    trial_list = [[{
        'walls': [
            [[20, 20], [20, 20]],
            [[20, 160], [20, 20]],
            [[160, 20], [20, 20]],
            [[160, 160], [20, 20]],
            [[90, 90], [20, 20]]
        ]
    }], [{
        'walls': [
            [[20, 20], [20, 20]],
            [[20, 160], [20, 20]],
            [[160, 20], [20, 20]],
            [[160, 160], [20, 20]]
        ]
    }]]

    wall_object_list = _create_wall_object_list(trial_list, [0.025, 0.025])

    assert len(wall_object_list) == 5
    assert wall_object_list[0]['shows'][0]['position']['x'] == -1.75
    assert wall_object_list[0]['shows'][0]['position']['z'] == -1.75
    assert wall_object_list[1]['shows'][0]['position']['x'] == -1.75
    assert wall_object_list[1]['shows'][0]['position']['z'] == 1.75
    assert wall_object_list[2]['shows'][0]['position']['x'] == 1.75
    assert wall_object_list[2]['shows'][0]['position']['z'] == -1.75
    assert wall_object_list[3]['shows'][0]['position']['x'] == 1.75
    assert wall_object_list[3]['shows'][0]['position']['z'] == 1.75
    assert wall_object_list[4]['shows'][0]['position']['x'] == 0
    assert wall_object_list[4]['shows'][0]['position']['z'] == 0

    for wall_object in wall_object_list:
        assert wall_object['id'].startswith('wall_')
        assert wall_object['type'] == 'cube'
        assert wall_object['materials'] == ['Custom/Materials/Black']
        assert wall_object['info'] == ['black', 'cube', 'black cube']
        assert wall_object['configHeight'] == [0.0625, 0.125]
        assert wall_object['configSize'] == [0.5, 0.5]

        assert len(wall_object['shows']) == 1
        assert wall_object['shows'][0]['stepBegin'] == 0
        assert wall_object['shows'][0]['position']['y'] == 0.0625
        assert wall_object['shows'][0]['scale']['x'] == 0.5
        assert wall_object['shows'][0]['scale']['y'] == 0.125
        assert wall_object['shows'][0]['scale']['z'] == 0.5

    assert 'hides' not in wall_object_list[0]
    assert 'hides' not in wall_object_list[1]
    assert 'hides' not in wall_object_list[2]
    assert 'hides' not in wall_object_list[3]
    assert wall_object_list[4]['hides'][0]['stepBegin'] == 2


def test_identify_target_object():
    # TODO
    pass


def test_identify_trial_index_starting_step():
    trial_list_a = [[{}], [{}], [{}]]
    assert _identify_trial_index_starting_step(0, trial_list_a) == 0
    assert _identify_trial_index_starting_step(1, trial_list_a) == 2
    assert _identify_trial_index_starting_step(2, trial_list_a) == 4

    trial_list_b = [[{}, {}, {}], [{}, {}], [{}]]
    assert _identify_trial_index_starting_step(0, trial_list_b) == 0
    assert _identify_trial_index_starting_step(1, trial_list_b) == 4
    assert _identify_trial_index_starting_step(2, trial_list_b) == 7


def test_remove_extraneous_agent_shows_single_step():
    agent_object_list = [{
        'shows': [
            {'position': {'x': 0, 'z': 0}}
        ]
    }]

    _remove_extraneous_agent_shows(agent_object_list)

    assert len(agent_object_list[0]['shows']) == 1


def test_remove_extraneous_agent_shows_no_extraneous():
    agent_object_list = [{
        'shows': [
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': 1, 'z': 0}},
            {'position': {'x': 1, 'z': 1}},
            {'position': {'x': 0, 'z': 1}},
            {'position': {'x': 0, 'z': 0}}
        ]
    }]

    _remove_extraneous_agent_shows(agent_object_list)

    assert len(agent_object_list[0]['shows']) == 5


def test_remove_extraneous_agent_shows_multiple_extraneous():
    agent_object_list = [{
        'shows': [
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': 1, 'z': 1}},
            {'position': {'x': 1, 'z': 1}},
            {'position': {'x': 1, 'z': 1}},
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': -1, 'z': -1}},
            {'position': {'x': -1, 'z': -1}},
            {'position': {'x': -1, 'z': -1}}
        ]
    }]

    _remove_extraneous_agent_shows(agent_object_list)

    assert len(agent_object_list[0]['shows']) == 4
    assert agent_object_list[0]['shows'][0]['position']['x'] == 0
    assert agent_object_list[0]['shows'][0]['position']['z'] == 0
    assert agent_object_list[0]['shows'][1]['position']['x'] == 1
    assert agent_object_list[0]['shows'][1]['position']['z'] == 1
    assert agent_object_list[0]['shows'][2]['position']['x'] == 0
    assert agent_object_list[0]['shows'][2]['position']['z'] == 0
    assert agent_object_list[0]['shows'][3]['position']['x'] == -1
    assert agent_object_list[0]['shows'][3]['position']['z'] == -1


def test_remove_extraneous_agent_shows_multiple_agents():
    agent_object_list = [{
        'shows': [
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': -1, 'z': -1}},
            {'position': {'x': -1, 'z': -1}},
            {'position': {'x': -1, 'z': -1}}
        ]
    }, {
        'shows': [
            {'position': {'x': 1, 'z': 1}},
            {'position': {'x': 1, 'z': 1}},
            {'position': {'x': 1, 'z': 1}},
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': 0, 'z': 0}},
            {'position': {'x': 0, 'z': 0}}
        ]
    }]

    _remove_extraneous_agent_shows(agent_object_list)

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


def test_remove_intersecting_agent_steps_with_no_intersection():
    agent_object_list = [{
        'boundsAtStep': [
            create_bounds(1, -1, 1, -1),
            create_bounds(1, -1, 1, -1),
            create_bounds(1, -1, 1, -1),
            create_bounds(2, 0, 2, 0),
            create_bounds(3, 1, 3, 1),
            create_bounds(4, 2, 4, 2),
            create_bounds(4, 2, 4, 2),
            create_bounds(4, 2, 4, 2)
        ],
        'shows': [
            {'stepBegin': 0},
            {'stepBegin': 3},
            {'stepBegin': 4},
            {'stepBegin': 5}
        ]
    }]

    goal_object_list = [{
        'boundsAtStep': [create_bounds(6.1, 4.1, 6.1, 4.1)] * 8
    }]

    _remove_intersecting_agent_steps(agent_object_list, goal_object_list)

    assert len(agent_object_list[0]['shows']) == 4


def test_remove_intersecting_agent_steps_with_intersection():
    agent_object_list = [{
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
        ],
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
        'boundsAtStep': [create_bounds(3.9, 2.9, 3.9, 2.9)] * 14
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
        ],
        'shows': [
            {'stepBegin': 0},
            {'stepBegin': 3},
            {'stepBegin': 4},
            {'stepBegin': 7},
            {'stepBegin': 10},
            {'stepBegin': 11}
        ]
    }, {
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
        ],
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
        'boundsAtStep': [create_bounds(3.9, 2.9, 3.9, 2.9)] * 14
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
        ],
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
        'boundsAtStep': [create_bounds(2.9, 1.9, 3.9, 2.9)] * 14
    }, {
        'boundsAtStep': [create_bounds(-3.9, -2.9, -2.9, -1.9)] * 14
    }]

    _remove_intersecting_agent_steps(agent_object_list, goal_object_list)

    assert len(agent_object_list[0]['shows']) == 4
    assert agent_object_list[0]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[0]['shows'][1]['stepBegin'] == 3
    assert agent_object_list[0]['shows'][2]['stepBegin'] == 7
    assert agent_object_list[0]['shows'][3]['stepBegin'] == 10


def test_retrieve_unit_size():
    assert _retrieve_unit_size([[{'size': [200, 200]}]]) == [0.025, 0.025]
    assert _retrieve_unit_size([[{'size': [100, 400]}]]) == [0.05, 0.0125]
