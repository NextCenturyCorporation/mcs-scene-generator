import copy

from machine_common_sense.config_manager import Goal, Vector3d

from generator import ObjectBounds, Scene, SceneObject
from generator.scene_saver import (
    _convert_non_serializable_data,
    _strip_debug_data,
    _strip_debug_misleading_data,
    _strip_debug_object_data,
    _truncate_floats_in_dict,
    _truncate_floats_in_list,
    find_next_filename
)


def create_test_object():
    return SceneObject({
        'id': 'thing1',
        'type': 'thing_1',
        'debug': {
            'info': ['a', 'b', 'c', 'd'],
            'goalString': 'abcd',
            'materialCategory': ['wood'],
            'dimensions': {'x': 13, 'z': 42},
            'offset': {'x': 13, 'z': 42},
            'enclosedAreas': [{}],
            'openAreas': [{}],
            'movement': {},
            'isParentOf': [],
            'untrainedCategory': True,
            'untrainedColor': True,
            'untrainedCombination': False,
            'untrainedShape': True,
            'untrainedSize': True,
            'color': ['black', 'white'],
            'shape': 'shape',
            'size': 'small',
            'weight': 'light',
            'role': 'target',
            'isTarget': True,
            'boundsAtStep': [],
            'configHeight': [],
            'configSize': []
        },
        'shows': [{
            'stepBegin': 0,
            'boundingBox': ObjectBounds(box_xz=[
                Vector3d(x=2, y=0, z=3), Vector3d(x=2.5, y=0, z=3),
                Vector3d(x=2.5, y=0, z=3.5), Vector3d(x=2, y=0, z=3.5)
            ], max_y=1, min_y=0)
        }]
    })


def test_find_next_filename():
    filename, index = find_next_filename('', 1, '01')
    assert filename == '1'
    assert index == 1

    filename, index = find_next_filename('', 2, '01')
    assert filename == '2'
    assert index == 2

    filename, index = find_next_filename('tests/file', 1, '01')
    assert filename == 'tests/file1'
    assert index == 1

    filename, index = find_next_filename('tests/file', 2, '01')
    assert filename == 'tests/file3'
    assert index == 3

    filename, index = find_next_filename('tests/file', 1, '02')
    assert filename == 'tests/file01'
    assert index == 1

    filename, index = find_next_filename('tests/file', 2, '02')
    assert filename == 'tests/file03'
    assert index == 3

    filename, index = find_next_filename('tests/file', 1, '01', suffix='.txt')
    assert filename == 'tests/file2'
    assert index == 2

    filename, index = find_next_filename(
        'tests/file',
        1,
        '01',
        suffix='_debug.json'
    )
    assert filename == 'tests/file2'
    assert index == 2


def test_convert_non_serializable_data():
    scene = Scene(objects=[create_test_object()])
    expected_object = create_test_object().data
    expected_object['shows'][0]['boundingBox'] = [
        {'x': 2, 'y': 0, 'z': 3},
        {'x': 2.5, 'y': 0, 'z': 3},
        {'x': 2.5, 'y': 0, 'z': 3.5},
        {'x': 2, 'y': 0, 'z': 3.5},
        {'x': 2, 'y': 1, 'z': 3},
        {'x': 2.5, 'y': 1, 'z': 3},
        {'x': 2.5, 'y': 1, 'z': 3.5},
        {'x': 2, 'y': 1, 'z': 3.5}
    ]
    del expected_object['debug']['boundsAtStep']
    _convert_non_serializable_data(scene)
    assert scene == Scene(objects=[expected_object])


def test_strip_debug_data():
    scene = Scene(
        debug={
            'floorColors': ['grey'],
            'wallColors': ['blue']
        },
        objects=[create_test_object()],
        goal=Goal(
            category='test',
            domains_info={
                'domainsTag': True
            },
            objects_info={
                'objectsTag': True
            },
            scene_info={
                'sceneTag': True
            },
            metadata={
                'target': {
                    'id': 'golden_idol',
                    'info': ['gold', 'idol']
                }
            }
        )
    ).to_dict()
    expected = Scene(
        debug=None,
        objects=[SceneObject({
            'id': 'thing1',
            'type': 'thing_1',
            'shows': [{
                'stepBegin': 0
            }]
        })],
        goal=Goal(
            category='test',
            metadata={
                'target': {
                    'id': 'golden_idol'
                }
            }
        )
    ).to_dict()
    actual = _strip_debug_data(scene)
    assert actual == expected


def test_strip_debug_misleading_data():
    obj = create_test_object()
    expected = copy.deepcopy(obj.data)
    expected['debug']['movement'] = {
        'deepExit': {
            'key': 'value'
        },
        'deepStop': {
            'key': 'value'
        },
        'moveExit': {
            'key': 'value'
        },
        'moveStop': {
            'key': 'value'
        },
        'tossExit': {
            'key': 'value'
        },
        'tossStop': {
            'key': 'value'
        }
    }
    obj['debug']['movement'] = {
        'deepExit': {
            'xDistanceByStep': [1],
            'yDistanceByStep': [2],
            'zDistanceByStep': [3],
            'key': 'value'
        },
        'deepStop': {
            'xDistanceByStep': [1],
            'yDistanceByStep': [2],
            'zDistanceByStep': [3],
            'key': 'value'
        },
        'moveExit': {
            'xDistanceByStep': [1],
            'yDistanceByStep': [2],
            'zDistanceByStep': [3],
            'key': 'value'
        },
        'moveStop': {
            'xDistanceByStep': [1],
            'yDistanceByStep': [2],
            'zDistanceByStep': [3],
            'key': 'value'
        },
        'tossExit': {
            'xDistanceByStep': [1],
            'yDistanceByStep': [2],
            'zDistanceByStep': [3],
            'key': 'value'
        },
        'tossStop': {
            'xDistanceByStep': [1],
            'yDistanceByStep': [2],
            'zDistanceByStep': [3],
            'key': 'value'
        }
    }
    _strip_debug_misleading_data(Scene(objects=[obj]))
    assert obj == expected


def test_strip_debug_object_data():
    obj = create_test_object()
    expected = {
        'id': 'thing1',
        'type': 'thing_1',
        'shows': [{
            'stepBegin': 0
        }]
    }
    _strip_debug_object_data(obj)
    assert obj == expected


def test_truncate_floats_in_dict():
    data = {'x': 1, 'y': 0.5, 'z': 987654321.123456789, 'tag': 'foobar'}
    _truncate_floats_in_dict(data)
    assert data['x'] == 1
    assert data['y'] == 0.5
    assert data['z'] == 987654321.1235
    assert data['tag'] == 'foobar'


def test_truncate_floats_in_dict_recursively():
    nested_data = {'x': 1, 'y': 0.5, 'z': 987654321.123456789, 'tag': 'foobar'}
    data = {'number': 0.987654321, 'nested': nested_data}
    _truncate_floats_in_dict(data)
    assert data['number'] == 0.9877
    assert data['nested']['x'] == 1
    assert data['nested']['y'] == 0.5
    assert data['nested']['z'] == 987654321.1235
    assert data['nested']['tag'] == 'foobar'


def test_truncate_floats_in_list():
    data = [1, 0.5, 987654321.123456789, 'foobar']
    _truncate_floats_in_list(data)
    assert data[0] == 1
    assert data[1] == 0.5
    assert data[2] == 987654321.1235
    assert data[3] == 'foobar'


def test_truncate_floats_in_list_recursively():
    nested_data = [1, 0.5, 987654321.123456789, 'foobar']
    data = [0.987654321, nested_data]
    _truncate_floats_in_list(data)
    assert data[0] == 0.9877
    assert data[1][0] == 1
    assert data[1][1] == 0.5
    assert data[1][2] == 987654321.1235
    assert data[1][3] == 'foobar'


def test_truncate_floats_advanced():
    nested_a = [1.11111111]
    nested_b = {'number': 2.22222222, 'nested': nested_a}
    nested_c = [3.33333333, nested_b]
    nested_d = {'number': 4.44444444, 'nested': nested_c}
    nested_e = {'number': 5.55555555}
    nested_f = [6.66666666, nested_e]
    nested_g = {'number': 7.77777777, 'nested': nested_f}
    nested_h = [8.88888888, nested_g]
    data = [nested_d, nested_h]
    _truncate_floats_in_list(data)
    assert nested_a == [1.1111]
    assert nested_b == {'number': 2.2222, 'nested': [1.1111]}
    assert nested_c == [3.3333, {'number': 2.2222, 'nested': [1.1111]}]
    assert nested_d == {
        'number': 4.4444,
        'nested': [3.3333, {'number': 2.2222, 'nested': [1.1111]}]
    }
    assert nested_e == {'number': 5.5556}
    assert nested_f == [6.6667, {'number': 5.5556}]
    assert nested_g == {
        'number': 7.7778,
        'nested': [6.6667, {'number': 5.5556}]
    }
    assert nested_h == [
        8.8889,
        {'number': 7.7778, 'nested': [6.6667, {'number': 5.5556}]}
    ]
