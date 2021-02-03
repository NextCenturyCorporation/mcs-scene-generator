import random
import materials
import objects
from util import finalize_object_definition, instantiate_object, \
    random_real, move_to_location, retrieve_complete_definition_list, \
    retrieve_trained_definition_list, retrieve_untrained_definition_list, \
    is_similar_except_in_color, is_similar_except_in_shape, \
    is_similar_except_in_size, choose_distractor_definition


ALL_DEFINITIONS = [
    definition for definition_list in retrieve_complete_definition_list(
        objects.get(objects.ObjectDefinitionList.ALL)
    ) for definition in definition_list
]


PACIFIER = {
    "type": "pacifier",
    "color": "blue",
    "shape": "pacifier",
    "size": "tiny",
    "salientMaterials": ["plastic"],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.07,
        "y": 0.04,
        "z": 0.05
    },
    "mass": 0.125,
    "offset": {
        "x": 0,
        "y": 0.02,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


def test_random_real():
    n = random_real(0, 1, 0.1)
    assert 0 <= n <= 1
    # need to multiply by 10 and mod by 1 instead of 0.1 to avoid weird
    # roundoff
    assert n * 10 % 1 < 1e-8


def test_finalize_object_definition():
    dimensions = {'x': 1, 'y': 1, 'z': 1}
    mass = 12.34
    material_category = ['plastic']
    salient_materials = ['plastic', 'hollow']
    object_def = {
        'type': 'type1',
        'mass': 56.78,
        'chooseMaterial': [{
            'materialCategory': material_category,
            'salientMaterials': salient_materials
        }],
        'chooseSize': [{
            'dimensions': dimensions,
            'mass': mass
        }]
    }
    obj = finalize_object_definition(object_def)
    assert obj['dimensions'] == dimensions
    assert obj['mass'] == mass
    assert obj['materialCategory'] == material_category
    assert obj['salientMaterials'] == salient_materials


def test_instantiate_object():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'attributes': ['foo', 'bar'],
        'scale': {'x': 1, 'y': 1, 'z': 1}
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert isinstance(obj['id'], str)
    assert obj['type'] == 'sofa_1'
    assert obj['dimensions'] == object_def['dimensions']
    assert obj['goalString'] == 'huge massive sofa'
    assert obj['info'] == [
        'huge', 'massive', 'sofa', 'huge massive', 'huge sofa', 'massive sofa',
        'huge massive sofa'
    ]
    assert obj['mass'] == 12.34
    assert obj['untrainedCategory'] is False
    assert obj['untrainedColor'] is False
    assert obj['untrainedCombination'] is False
    assert obj['untrainedShape'] is False
    assert obj['untrainedSize'] is False
    assert obj['shape'] == ['sofa']
    assert obj['size'] == 'huge'
    assert obj['weight'] == 'massive'
    assert obj['foo'] is True
    assert obj['bar'] is True
    assert obj['shows'][0]['stepBegin'] == 0
    assert obj['shows'][0]['position'] == object_location['position']
    assert obj['shows'][0]['rotation'] == object_location['rotation']
    assert obj['shows'][0]['scale'] == object_def['scale']


def test_instantiate_object_choose():
    object_def = {
        'type': 'sofa_1',
        'chooseSize': [{
            'untrainedShape': True,
            'shape': 'sofa',
            'size': 'medium',
            'attributes': ['moveable'],
            'dimensions': {'x': 0.5, 'y': 0.25, 'z': 0.25},
            'mass': 12.34,
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }, {
            'shape': 'sofa',
            'size': 'huge',
            'attributes': [],
            'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
            'mass': 56.78,
            'scale': {'x': 1, 'y': 1, 'z': 1}
        }]
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['size'] == 'medium' or obj['size'] == 'huge'
    if obj['size'] == 'medium':
        assert obj['moveable']
        assert obj['untrainedShape']
        assert obj['info'] == [
            'medium', 'heavy', 'sofa', 'medium heavy', 'medium sofa',
            'heavy sofa', 'medium heavy sofa', 'untrained shape',
            'untrained medium heavy sofa'
        ]
        assert obj['goalString'] == 'medium heavy sofa'
        assert obj['dimensions'] == {'x': 0.5, 'y': 0.25, 'z': 0.25}
        assert obj['mass'] == 12.34
        assert obj['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}
    if obj['size'] == 'huge':
        assert 'moveable' not in obj
        assert not obj['untrainedShape']
        assert obj['info'] == [
            'huge', 'massive', 'sofa', 'huge massive', 'huge sofa',
            'massive sofa', 'huge massive sofa'
        ]
        assert obj['goalString'] == 'huge massive sofa'
        assert obj['dimensions'] == {'x': 1, 'y': 0.5, 'z': 0.5}
        assert obj['mass'] == 56.78
        assert obj['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_instantiate_object_heavy_moveable():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'attributes': ['moveable'],
        'scale': {'x': 1, 'y': 1, 'z': 1}
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['goalString'] == 'huge heavy sofa'
    assert obj['info'] == [
        'huge', 'heavy', 'sofa', 'huge heavy', 'huge sofa', 'heavy sofa',
        'huge heavy sofa'
    ]
    assert obj['moveable'] is True


def test_instantiate_object_light_pickupable():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'attributes': ['moveable', 'pickupable'],
        'scale': {'x': 1, 'y': 1, 'z': 1}
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['goalString'] == 'huge light sofa'
    assert obj['info'] == [
        'huge', 'light', 'sofa', 'huge light', 'huge sofa', 'light sofa',
        'huge light sofa'
    ]
    assert obj['moveable'] is True
    assert obj['pickupable'] is True


def test_instantiate_object_offset():
    offset = {
        'x': random.random(),
        'z': random.random()
    }
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
        'attributes': [],
        'offset': offset
    }
    x = random.random()
    z = random.random()
    object_location = {
        'position': {
            'x': x,
            'y': 0.0,
            'z': z
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    position = obj['shows'][0]['position']
    assert position['x'] == x - offset['x']
    assert position['z'] == z - offset['z']


def test_instantiate_object_rotation():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
        'attributes': [],
        'rotation': {'x': 1, 'y': 2, 'z': 3}
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 30.0,
            'y': 60.0,
            'z': 90.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['shows'][0]['rotation'] == {'x': 31.0, 'y': 62.0, 'z': 93.0}


def test_instantiate_object_materials():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
        'attributes': [],
        'materialCategory': ['test']
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['materials'] == ['test_material']
    assert obj['color'] == ['blue', 'yellow']
    assert obj['goalString'] == 'huge massive blue yellow sofa'
    assert obj['info'] == [
        'huge', 'massive', 'blue', 'yellow', 'sofa', 'blue yellow',
        'huge massive', 'huge blue yellow', 'huge sofa', 'massive blue yellow',
        'massive sofa', 'blue yellow sofa', 'huge massive blue yellow sofa'
    ]


def test_instantiate_object_multiple_materials():
    materials.TEST1_MATERIALS = [('test_material_1', ['blue'])]
    materials.TEST2_MATERIALS = [('test_material_2', ['yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
        'attributes': [],
        'materialCategory': ['test1', 'test2']
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['materials'] == ['test_material_1', 'test_material_2']
    assert obj['color'] == ['blue', 'yellow']
    assert obj['goalString'] == 'huge massive blue yellow sofa'
    assert obj['info'] == [
        'huge', 'massive', 'blue', 'yellow', 'sofa', 'blue yellow',
        'huge massive', 'huge blue yellow', 'huge sofa', 'massive blue yellow',
        'massive sofa', 'blue yellow sofa', 'huge massive blue yellow sofa'
    ]


def test_instantiate_object_salient_materials():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
        'attributes': [],
        'salientMaterials': ['fabric', 'wood']
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['salientMaterials'] == ['fabric', 'wood']
    assert obj['goalString'] == 'huge massive fabric wood sofa'
    assert obj['info'] == [
        'huge', 'massive', 'fabric', 'wood', 'sofa', 'fabric wood',
        'huge massive', 'huge fabric wood', 'huge sofa', 'massive fabric wood',
        'massive sofa', 'fabric wood sofa', 'huge massive fabric wood sofa'
    ]


def test_instantiate_object_size():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
        'attributes': [],
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    size_mapping = {
        'pickupable': 'light',
        'moveable': 'heavy',
        'anythingelse': 'massive'
    }
    for attribute in size_mapping:
        size = size_mapping[attribute]
        object_def['attributes'] = [attribute]
        obj = instantiate_object(object_def, object_location)
        assert size in obj['info']


def test_instantiate_object_untrained_category():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'untrainedCategory': True,
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'materialCategory': ['test']
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['goalString'] == 'huge massive blue yellow sofa'
    assert obj['info'] == [
        'huge', 'massive', 'blue', 'yellow', 'sofa', 'blue yellow',
        'huge massive', 'huge blue yellow', 'huge sofa', 'massive blue yellow',
        'massive sofa', 'blue yellow sofa', 'huge massive blue yellow sofa',
        'untrained category', 'untrained huge massive blue yellow sofa'
    ]


def test_instantiate_object_untrained_color():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'untrainedColor': True,
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'materialCategory': ['test']
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['goalString'] == 'huge massive blue yellow sofa'
    assert obj['info'] == [
        'huge', 'massive', 'blue', 'yellow', 'sofa', 'blue yellow',
        'huge massive', 'huge blue yellow', 'huge sofa', 'massive blue yellow',
        'massive sofa', 'blue yellow sofa', 'huge massive blue yellow sofa',
        'untrained color', 'untrained huge massive blue yellow sofa'
    ]


def test_instantiate_object_untrained_combination():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'untrainedCombination': True,
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'materialCategory': ['test']
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['goalString'] == 'huge massive blue yellow sofa'
    assert obj['info'] == [
        'huge', 'massive', 'blue', 'yellow', 'sofa', 'blue yellow',
        'huge massive', 'huge blue yellow', 'huge sofa', 'massive blue yellow',
        'massive sofa', 'blue yellow sofa', 'huge massive blue yellow sofa',
        'untrained combination', 'untrained huge massive blue yellow sofa'
    ]


def test_instantiate_object_untrained_shape():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'untrainedShape': True,
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'materialCategory': ['test']
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['goalString'] == 'huge massive blue yellow sofa'
    assert obj['info'] == [
        'huge', 'massive', 'blue', 'yellow', 'sofa', 'blue yellow',
        'huge massive', 'huge blue yellow', 'huge sofa', 'massive blue yellow',
        'massive sofa', 'blue yellow sofa', 'huge massive blue yellow sofa',
        'untrained shape', 'untrained huge massive blue yellow sofa'
    ]


def test_instantiate_object_untrained_size():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'untrainedSize': True,
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'materialCategory': ['test']
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['goalString'] == 'huge massive blue yellow sofa'
    assert obj['info'] == [
        'huge', 'massive', 'blue', 'yellow', 'sofa', 'blue yellow',
        'huge massive', 'huge blue yellow', 'huge sofa', 'massive blue yellow',
        'massive sofa', 'blue yellow sofa', 'huge massive blue yellow sofa',
        'untrained size', 'untrained huge massive blue yellow sofa'
    ]


def test_move_to_location():
    instance = {
        'shows': [
            {
                'position': {'x': -1, 'y': 0, 'z': -1},
                'rotation': {'x': 0, 'y': 90, 'z': 0}
            }
        ]
    }
    bounds = [{'x': 3, 'z': 3}, {'x': 3, 'z': 1},
              {'x': 1, 'z': 1}, {'x': 1, 'z': 3}]
    location = {
        'position': {
            'x': 2, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}

    actual = move_to_location(instance, location, bounds, {})
    assert actual == instance
    assert instance['shows'][0]['position'] == {'x': 2, 'y': 0, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['boundingBox'] == [
        {'x': 3, 'z': 3},
        {'x': 3, 'z': 1},
        {'x': 1, 'z': 1},
        {'x': 1, 'z': 3}
    ]

    previous = {'offset': {'x': 0.2, 'z': -0.4}}

    actual = move_to_location(instance, location, bounds, previous)
    assert actual == instance
    assert instance['shows'][0]['position'] == {'x': 2.2, 'y': 0, 'z': 1.6}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['boundingBox'] == [
        {'x': 3, 'z': 3},
        {'x': 3, 'z': 1},
        {'x': 1, 'z': 1},
        {'x': 1, 'z': 3}
    ]

    instance['offset'] = {'x': 0.1, 'z': -0.5}

    actual = move_to_location(instance, location, bounds, {})
    assert actual == instance
    assert instance['shows'][0]['position'] == {'x': 1.9, 'y': 0, 'z': 2.5}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['boundingBox'] == [
        {'x': 3, 'z': 3},
        {'x': 3, 'z': 1},
        {'x': 1, 'z': 1},
        {'x': 1, 'z': 3}
    ]

    actual = move_to_location(instance, location, bounds, previous)
    assert actual == instance
    assert instance['shows'][0]['position'] == {'x': 2.1, 'y': 0, 'z': 2.1}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['boundingBox'] == [
        {'x': 3, 'z': 3},
        {'x': 3, 'z': 1},
        {'x': 1, 'z': 1},
        {'x': 1, 'z': 3}
    ]


def test_retrieve_complete_definition_list():
    list_1 = [{'type': 'ball', 'mass': 1}]
    actual_1 = retrieve_complete_definition_list([list_1])[0]
    assert len(actual_1) == 1

    list_2 = [{'type': 'ball', 'chooseSize': [{'mass': 1}, {'mass': 2}]}]
    actual_2 = retrieve_complete_definition_list([list_2])[0]
    assert len(actual_2) == 2

    list_3 = [
        {'type': 'sofa'},
        {'type': 'ball', 'chooseSize': [{'mass': 1}, {'mass': 2}]}
    ]
    actual_3 = retrieve_complete_definition_list([list_3])[0]
    assert len(actual_3) == 3

    list_4 = [
        {'type': 'sofa', 'chooseSize': [{'mass': 1}, {'mass': 3}]},
        {'type': 'ball', 'chooseSize': [{'mass': 1}, {'mass': 2}]}
    ]
    actual_4 = retrieve_complete_definition_list([list_4])[0]
    assert len(actual_4) == 4

    list_5 = [{'chooseType': [{'type': 'sphere'}, {'type': 'cube'}]}]
    actual_5 = retrieve_complete_definition_list([list_5])[0]
    assert len(actual_5) == 2

    list_6 = [
        {'type': 'sofa'},
        {'chooseType': [{'type': 'sphere'}, {'type': 'cube'}]}
    ]
    actual_6 = retrieve_complete_definition_list([list_6])[0]
    assert len(actual_6) == 3

    list_7 = [
        {'chooseType': [{'type': 'ball'}, {'type': 'sofa'}]},
        {'chooseType': [{'type': 'sphere'}, {'type': 'cube'}]}
    ]
    actual_7 = retrieve_complete_definition_list([list_7])[0]
    assert len(actual_7) == 4

    list_8 = [{
        'chooseMaterial': [
            {'materialCategory': ['metal']},
            {'materialCategory': ['plastic']}
        ],
        'chooseSize': [{'mass': 1}, {'mass': 2}],
        'chooseType': [{'type': 'ball'}, {'type': 'sofa'}]
    }]
    actual_8 = retrieve_complete_definition_list([list_8])[0]
    assert len(actual_8) == 8


def test_retrieve_complete_definition_list_nested_list():
    list_1 = [
        [{'chooseType': [{'type': 'ball'}, {'type': 'sofa'}]}],
        [{'chooseType': [{'type': 'sphere'}, {'type': 'cube'}]}]
    ]
    actual_1 = retrieve_complete_definition_list(list_1)
    assert len(actual_1) == 2
    assert len(actual_1[0]) == 2
    assert len(actual_1[1]) == 2

    type_list_a = [item['type'] for item in actual_1[0]]
    type_list_b = [item['type'] for item in actual_1[1]]
    assert (
        (
            'ball' in type_list_a and 'sofa' in type_list_a and
            'sphere' in type_list_b and 'cube' in type_list_b
        ) or (
            'ball' in type_list_b and 'sofa' in type_list_b and
            'sphere' in type_list_a and 'cube' in type_list_a
        )
    )


def test_retrieve_complete_definition_list_choose_material():
    definition_list = [{
        'type': 'metal_thing',
        'chooseMaterial': [{'materialCategory': ['metal']}]
    }, {
        'type': 'plastic_thing',
        'chooseMaterial': [{'materialCategory': ['plastic']}]
    }, {
        'type': 'rubber_thing',
        'chooseMaterial': [{'materialCategory': ['rubber']}]
    }, {
        'type': 'wood_thing',
        'chooseMaterial': [{'materialCategory': ['wood']}]
    }, {
        'type': 'other_thing',
        'chooseMaterial': [
            {'materialCategory': ['metal']},
            {'materialCategory': ['plastic']},
            {'materialCategory': ['rubber']},
            {'materialCategory': ['wood']}
        ]
    }]

    actual_1 = retrieve_complete_definition_list([definition_list])[0]
    assert len(actual_1) == 8

    metal = [item for item in actual_1 if item['type'] == 'metal_thing']
    assert len(metal) == 1
    assert metal[0]['materialCategory'] == ['metal']
    assert 'materials' not in metal[0]

    plastic = [item for item in actual_1 if item['type'] == 'plastic_thing']
    assert len(plastic) == 1
    assert plastic[0]['materialCategory'] == ['plastic']
    assert 'materials' not in plastic[0]

    rubber = [item for item in actual_1 if item['type'] == 'rubber_thing']
    assert len(rubber) == 1
    assert rubber[0]['materialCategory'] == ['rubber']
    assert 'materials' not in rubber[0]

    wood = [item for item in actual_1 if item['type'] == 'wood_thing']
    assert len(wood) == 1
    assert wood[0]['materialCategory'] == ['wood']
    assert 'materials' not in wood[0]

    other_material_list = ['metal', 'plastic', 'rubber', 'wood']

    other = [item for item in actual_1 if item['type'] == 'other_thing']
    assert len(other) == 4

    assert other[0]['materialCategory'][0] in other_material_list
    other_material_list.remove(other[0]['materialCategory'][0])
    assert 'materials' not in other[0]

    assert other[1]['materialCategory'][0] in other_material_list
    other_material_list.remove(other[1]['materialCategory'][0])
    assert 'materials' not in other[1]

    assert other[2]['materialCategory'][0] in other_material_list
    other_material_list.remove(other[2]['materialCategory'][0])
    assert 'materials' not in other[2]

    assert other[3]['materialCategory'][0] in other_material_list
    other_material_list.remove(other[3]['materialCategory'][0])
    assert 'materials' not in other[3]


def test_retrieve_trained_definition_list():
    definition_list = [{
        'type': 'a'
    }, {
        'type': 'b',
        'untrainedCategory': True
    }, {
        'type': 'c',
        'untrainedColor': True
    }, {
        'type': 'd',
        'untrainedCombination': True
    }, {
        'type': 'e',
        'untrainedShape': True
    }, {
        'type': 'f',
        'untrainedSize': True
    }, {
        'type': 'g',
        'untrainedCategory': True,
        'untrainedColor': True,
        'untrainedCombination': True,
        'untrainedShape': True,
        'untrainedSize': True
    }, {
        'type': 'h'
    }]

    actual_1 = retrieve_trained_definition_list([definition_list])[0]
    assert len(actual_1) == 2
    assert actual_1[0]['type'] == 'a'
    assert actual_1[1]['type'] == 'h'


def test_retrieve_untrained_definition_list():
    definition_list = [{
        'type': 'a'
    }, {
        'type': 'b',
        'untrainedCategory': True
    }, {
        'type': 'c',
        'untrainedColor': True
    }, {
        'type': 'd',
        'untrainedCombination': True
    }, {
        'type': 'e',
        'untrainedShape': True
    }, {
        'type': 'f',
        'untrainedSize': True
    }, {
        'type': 'g',
        'untrainedCategory': True,
        'untrainedColor': True,
        'untrainedCombination': True,
        'untrainedShape': True,
        'untrainedSize': True
    }, {
        'type': 'h'
    }]

    actual_1 = retrieve_untrained_definition_list([definition_list],
                                                  'untrainedShape')[0]
    assert len(actual_1) == 1
    assert actual_1[0]['type'] == 'e'

    actual_2 = retrieve_untrained_definition_list([definition_list],
                                                  'untrainedSize')[0]
    assert len(actual_2) == 1
    assert actual_2[0]['type'] == 'f'


def test_retrieve_trained_definition_list_all_objects():
    assert len(retrieve_trained_definition_list(objects.get(
        objects.ObjectDefinitionList.ALL)
    )) > 0


def test_retrieve_trained_definition_list_container_objects():
    assert len(retrieve_trained_definition_list(objects.get(
        objects.ObjectDefinitionList.CONTAINERS)
    )) > 0


def test_retrieve_trained_definition_list_obstacle_objects():
    assert len(retrieve_trained_definition_list(
        objects.get(objects.ObjectDefinitionList.OBSTACLES)
    )) > 0


def test_retrieve_trained_definition_list_occluder_objects():
    assert len(retrieve_trained_definition_list(
        objects.get(objects.ObjectDefinitionList.OCCLUDERS)
    )) > 0


def test_retrieve_untrained_definition_list_all_objects():
    assert len(retrieve_untrained_definition_list(
        objects.get(objects.ObjectDefinitionList.ALL),
        'untrainedShape'
    )) > 0


def test_retrieve_untrained_definition_list_container_objects():
    assert len(retrieve_untrained_definition_list(
        objects.get(objects.ObjectDefinitionList.CONTAINERS),
        'untrainedShape'
    )) > 0


def test_retrieve_untrained_definition_list_obstacle_objects():
    assert len(retrieve_untrained_definition_list(
        objects.get(objects.ObjectDefinitionList.OBSTACLES),
        'untrainedShape'
    )) > 0


def test_retrieve_untrained_definition_list_occluder_objects():
    assert len(retrieve_untrained_definition_list(
        objects.get(objects.ObjectDefinitionList.OCCLUDERS),
        'untrainedShape'
    )) > 0


def test_is_similar_except_in_color():
    definition_1 = {
        'type': 'a',
        'materialCategory': ['x'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_2 = {
        'type': 'a',
        'materialCategory': ['y'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_3 = {
        'type': 'a',
        'materialCategory': ['x', 'y'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_4 = {
        'type': 'b',
        'materialCategory': ['y'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_5 = {
        'type': 'a',
        'materialCategory': ['y'],
        'dimensions': {'x': 2, 'y': 1, 'z': 1}
    }
    definition_6 = {
        'type': 'a',
        'materialCategory': ['y'],
        'dimensions': {'x': 0.5, 'y': 1, 'z': 1}
    }
    definition_7 = {
        'type': 'a',
        'materialCategory': ['y'],
        'dimensions': {'x': 1.05, 'y': 1, 'z': 1}
    }
    definition_8 = {
        'type': 'a',
        'materialCategory': ['y'],
        'dimensions': {'x': 0.95, 'y': 1, 'z': 1}
    }
    assert is_similar_except_in_color(definition_1, definition_2)
    assert is_similar_except_in_color(definition_1, definition_3)
    assert not is_similar_except_in_color(definition_1, definition_4)
    assert not is_similar_except_in_color(definition_1, definition_5)
    assert not is_similar_except_in_color(definition_1, definition_6)
    assert is_similar_except_in_color(definition_1, definition_7)
    assert is_similar_except_in_color(definition_1, definition_8)


def test_is_similar_except_in_shape():
    definition_1 = {
        'type': 'a',
        'materialCategory': ['x'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_2 = {
        'type': 'b',
        'materialCategory': ['x'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_3 = {
        'type': 'b',
        'materialCategory': ['y'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_4 = {
        'type': 'b',
        'materialCategory': ['x', 'y'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_5 = {
        'type': 'b',
        'materialCategory': ['x'],
        'dimensions': {'x': 2, 'y': 1, 'z': 1}
    }
    definition_6 = {
        'type': 'b',
        'materialCategory': ['x'],
        'dimensions': {'x': 0.5, 'y': 1, 'z': 1}
    }
    definition_7 = {
        'type': 'b',
        'materialCategory': ['x'],
        'dimensions': {'x': 1.05, 'y': 1, 'z': 1}
    }
    definition_8 = {
        'type': 'b',
        'materialCategory': ['x'],
        'dimensions': {'x': 0.95, 'y': 1, 'z': 1}
    }
    assert is_similar_except_in_shape(definition_1, definition_2)
    assert not is_similar_except_in_shape(definition_1, definition_3)
    assert not is_similar_except_in_shape(definition_1, definition_4)
    assert not is_similar_except_in_shape(definition_1, definition_5)
    assert not is_similar_except_in_shape(definition_1, definition_6)
    assert is_similar_except_in_shape(definition_1, definition_7)
    assert is_similar_except_in_shape(definition_1, definition_8)


def test_is_similar_except_in_size():
    definition_1 = {
        'type': 'a',
        'materialCategory': ['x'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_2 = {
        'type': 'b',
        'materialCategory': ['x'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_3 = {
        'type': 'a',
        'materialCategory': ['y'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_4 = {
        'type': 'a',
        'materialCategory': ['x', 'y'],
        'dimensions': {'x': 1, 'y': 1, 'z': 1}
    }
    definition_5 = {
        'type': 'a',
        'materialCategory': ['x'],
        'dimensions': {'x': 2, 'y': 1, 'z': 1}
    }
    definition_6 = {
        'type': 'a',
        'materialCategory': ['x'],
        'dimensions': {'x': 0.5, 'y': 1, 'z': 1}
    }
    definition_7 = {
        'type': 'a',
        'materialCategory': ['x'],
        'dimensions': {'x': 1.05, 'y': 1, 'z': 1}
    }
    definition_8 = {
        'type': 'a',
        'materialCategory': ['x'],
        'dimensions': {'x': 0.95, 'y': 1, 'z': 1}
    }
    assert not is_similar_except_in_size(definition_1, definition_2)
    assert not is_similar_except_in_size(definition_1, definition_3)
    assert not is_similar_except_in_size(definition_1, definition_4)
    assert is_similar_except_in_size(definition_1, definition_5)
    assert is_similar_except_in_size(definition_1, definition_6)
    assert not is_similar_except_in_size(definition_1, definition_7)
    assert not is_similar_except_in_size(definition_1, definition_8)


def test_is_similar_except_in_color_all_objects():
    for definition_1 in ALL_DEFINITIONS:
        for definition_2 in ALL_DEFINITIONS:
            if definition_1 != definition_2:
                x_size_1 = definition_1['dimensions']['x']
                x_size_2 = definition_2['dimensions']['x']
                y_size_1 = definition_1['dimensions']['y']
                y_size_2 = definition_2['dimensions']['y']
                z_size_1 = definition_1['dimensions']['z']
                z_size_2 = definition_2['dimensions']['z']
                expected = (
                    definition_1['type'] == definition_2['type'] and
                    definition_1['materialCategory'] !=
                    definition_2['materialCategory'] and
                    (x_size_1 + 0.05) >= x_size_2 and
                    (x_size_1 - 0.05) <= x_size_2 and
                    (y_size_1 + 0.05) >= y_size_2 and
                    (y_size_1 - 0.05) <= y_size_2 and
                    (z_size_1 + 0.05) >= z_size_2 and
                    (z_size_1 - 0.05) <= z_size_2
                )
                actual = is_similar_except_in_color(definition_1, definition_2)
                if actual != expected:
                    print(f'ONE={definition_1}')
                    print(f'TWO={definition_2}')
                assert actual == expected


def test_is_similar_except_in_shape_all_objects():
    for definition_1 in ALL_DEFINITIONS:
        for definition_2 in ALL_DEFINITIONS:
            if definition_1 != definition_2:
                x_size_1 = definition_1['dimensions']['x']
                x_size_2 = definition_2['dimensions']['x']
                y_size_1 = definition_1['dimensions']['y']
                y_size_2 = definition_2['dimensions']['y']
                z_size_1 = definition_1['dimensions']['z']
                z_size_2 = definition_2['dimensions']['z']
                expected = (
                    definition_1['type'] != definition_2['type'] and
                    definition_1['materialCategory'] ==
                    definition_2['materialCategory'] and
                    (x_size_1 + 0.05) >= x_size_2 and
                    (x_size_1 - 0.05) <= x_size_2 and
                    (y_size_1 + 0.05) >= y_size_2 and
                    (y_size_1 - 0.05) <= y_size_2 and
                    (z_size_1 + 0.05) >= z_size_2 and
                    (z_size_1 - 0.05) <= z_size_2
                )
                actual = is_similar_except_in_shape(definition_1, definition_2)
                if actual != expected:
                    print(f'ONE={definition_1}')
                    print(f'TWO={definition_2}')
                assert actual == expected


def test_is_similar_except_in_size_all_objects():
    for definition_1 in ALL_DEFINITIONS:
        for definition_2 in ALL_DEFINITIONS:
            if definition_1 != definition_2:
                x_size_1 = definition_1['dimensions']['x']
                x_size_2 = definition_2['dimensions']['x']
                y_size_1 = definition_1['dimensions']['y']
                y_size_2 = definition_2['dimensions']['y']
                z_size_1 = definition_1['dimensions']['z']
                z_size_2 = definition_2['dimensions']['z']
                expected = (
                    definition_1['type'] == definition_2['type'] and
                    definition_1['materialCategory'] ==
                    definition_2['materialCategory'] and
                    (
                        (x_size_1 + 0.05) < x_size_2 or
                        (x_size_1 - 0.05) > x_size_2 or
                        (y_size_1 + 0.05) < y_size_2 or
                        (y_size_1 - 0.05) > y_size_2 or
                        (z_size_1 + 0.05) < z_size_2 or
                        (z_size_1 - 0.05) > z_size_2
                    )
                )
                actual = is_similar_except_in_size(definition_1, definition_2)
                if actual != expected:
                    print(f'ONE={definition_1}')
                    print(f'TWO={definition_2}')
                assert actual == expected


def test_similarity_pacifier():
    # Not similar because materialCategory is not defined.
    assert not is_similar_except_in_color(PACIFIER, PACIFIER)
    assert not is_similar_except_in_shape(PACIFIER, PACIFIER)
    assert not is_similar_except_in_size(PACIFIER, PACIFIER)


def test_choose_distractor_definition():
    for definition in ALL_DEFINITIONS:
        assert choose_distractor_definition([definition])
