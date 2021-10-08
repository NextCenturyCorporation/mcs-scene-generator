import copy

from generator.scene_saver import (
    _strip_debug_data,
    _strip_debug_misleading_data,
    _strip_debug_object_data,
    find_next_filename,
)


def create_test_object():
    return {
        'id': 'thing1',
        'type': 'thing_1',
        'debug': {
            'info': ['a', 'b', 'c', 'd'],
            'goalString': 'abcd',
            'materialCategory': ['wood'],
            'dimensions': {'x': 13, 'z': 42},
            'offset': {'x': 13, 'z': 42},
            'closedDimensions': {'x': 13, 'z': 42},
            'closedOffset': {'x': 13, 'z': 42},
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
            'boundingBox': 'dummy'
        }]
    }


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


def test_strip_debug_data():
    scene = {
        'debug': {
            'floorColors': ['grey'],
            'wallColors': ['blue']
        },
        'objects': [create_test_object()],
        'goal': {
            'category': 'test',
            'domainsInfo': {
                'domainsTag': True
            },
            'objectsInfo': {
                'objectsTag': True
            },
            'sceneInfo': {
                'sceneTag': True
            },
            'metadata': {
                'target': {
                    'id': 'golden_idol',
                    'info': ['gold', 'idol']
                }
            }
        }
    }
    expected = {
        'objects': [{
            'id': 'thing1',
            'type': 'thing_1',
            'shows': [{
                'stepBegin': 0
            }]
        }],
        'goal': {
            'category': 'test',
            'metadata': {
                'target': {
                    'id': 'golden_idol'
                }
            }
        }
    }
    _strip_debug_data(scene)
    assert scene == expected


def test_strip_debug_misleading_data():
    obj = create_test_object()
    expected = copy.deepcopy(obj)
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
    _strip_debug_misleading_data({'objects': [obj]})
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
