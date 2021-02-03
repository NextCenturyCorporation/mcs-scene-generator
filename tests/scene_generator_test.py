from scene_generator import SceneGenerator


def find_object(id, obj_list):
    for obj in obj_list:
        if obj['id'] == id:
            return obj
    return None


def create_test_object():
    return {
        'id': 'thing1',
        'info': ['a', 'b', 'c', 'd'],
        'goalString': 'abcd',
        'materialCategory': ['wood'],
        'dimensions': {'x': 13, 'z': 42},
        'offset': {'x': 13, 'z': 42},
        'closedDimensions': {'x': 13, 'z': 42},
        'closedOffset': {'x': 13, 'z': 42},
        'enclosedAreas': [{}],
        'openAreas': [{}],
        'speed': {},
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
        'configSize': [],
        'shows': [{
            'stepBegin': 0,
            'boundingBox': 'dummy'
        }]
    }


def test_strip_debug_object_data():
    obj = create_test_object()
    expected = {
        'id': 'thing1',
        'shows': [{
            'stepBegin': 0
        }]
    }
    scene_generator = SceneGenerator([])
    scene_generator.strip_debug_object_data(obj)
    assert obj == expected


def test_strip_debug_data():
    scene = {
        'wallColors': ['blue'],
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
    scene_generator = SceneGenerator([])
    scene_generator.strip_debug_data(scene)
    assert scene == expected
