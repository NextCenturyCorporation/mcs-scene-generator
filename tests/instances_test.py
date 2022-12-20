import random

from machine_common_sense.config_manager import Vector3d

from generator import ObjectDefinition, base_objects
from generator.instances import (
    get_earliest_active_step,
    get_last_move_or_rotate_step,
    instantiate_object
)


def test_instantiate_object():
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        attributes=['foo', 'bar'],
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1}),
        shape=['sofa'],
        size='huge'
    )
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
    assert obj['debug']['dimensions'] == vars(object_def.dimensions)
    assert obj['debug']['goalString'] == 'huge massive blue sofa'
    assert obj['debug']['info'] == [
        'huge', 'massive', 'blue', 'sofa', 'huge massive', 'huge blue',
        'huge sofa', 'massive blue', 'massive sofa', 'blue sofa',
        'huge massive blue sofa'
    ]
    assert obj['mass'] == 12.34
    assert obj['debug']['untrainedCategory'] is False
    assert obj['debug']['untrainedColor'] is False
    assert obj['debug']['untrainedCombination'] is False
    assert obj['debug']['untrainedShape'] is False
    assert obj['debug']['untrainedSize'] is False
    assert obj['debug']['shape'] == ['sofa']
    assert obj['debug']['size'] == 'huge'
    assert obj['debug']['weight'] == 'massive'
    assert obj['foo'] is True
    assert obj['bar'] is True
    assert obj['shows'][0]['stepBegin'] == 0
    assert obj['shows'][0]['position'] == object_location['position']
    assert obj['shows'][0]['rotation'] == object_location['rotation']
    assert obj['shows'][0]['scale'] == vars(object_def.scale)


def test_instantiate_object_heavy_moveable():
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        shape=['sofa'],
        size='huge',
        attributes=['moveable'],
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
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
    assert obj['debug']['goalString'] == 'huge heavy blue sofa'
    assert obj['debug']['info'] == [
        'huge', 'heavy', 'blue', 'sofa', 'huge heavy', 'huge blue',
        'huge sofa', 'heavy blue', 'heavy sofa', 'blue sofa',
        'huge heavy blue sofa'
    ]
    assert obj['moveable'] is True


def test_instantiate_object_light_pickupable():
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        shape=['sofa'],
        size='huge',
        attributes=['moveable', 'pickupable'],
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
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
    assert obj['debug']['goalString'] == 'huge light blue sofa'
    assert obj['debug']['info'] == [
        'huge', 'light', 'blue', 'sofa', 'huge light', 'huge blue',
        'huge sofa', 'light blue', 'light sofa', 'blue sofa',
        'huge light blue sofa'
    ]
    assert obj['moveable'] is True
    assert obj['pickupable'] is True


def test_instantiate_object_offset():
    offset = {
        'x': random.random(),
        'z': random.random()
    }
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        shape=['sofa'],
        size='huge',
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1}),
        attributes=[],
        offset=Vector3d(**offset)
    )
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
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        shape=['sofa'],
        size='huge',
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1}),
        attributes=[],
        rotation=Vector3d(**{'x': 1, 'y': 2, 'z': 3})
    )
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


def test_instantiate_object_salient_materials():
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        salientMaterials=['fabric', 'wood'],
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        shape=['sofa'],
        size='huge',
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1}),
        attributes=[]
    )
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
    assert obj['debug']['goalString'] == 'huge massive blue fabric wood sofa'
    assert obj['debug']['info'] == [
        'huge', 'massive', 'blue', 'fabric', 'wood', 'sofa', 'fabric wood',
        'huge massive', 'huge fabric wood', 'huge blue', 'huge sofa',
        'massive fabric wood', 'massive blue', 'massive sofa',
        'fabric wood blue', 'fabric wood sofa', 'blue sofa',
        'huge massive blue fabric wood sofa'
    ]


def test_instantiate_object_size():
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        shape=['sofa'],
        size='huge',
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1}),
        attributes=[]
    )
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
        object_def.attributes = [attribute]
        obj = instantiate_object(object_def, object_location)
        assert size in obj['debug']['info']


def test_instantiate_object_untrained_category():
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        untrainedCategory=True,
        shape=['sofa'],
        size='huge',
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1}),
        attributes=[]
    )
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
    assert obj['debug']['goalString'] == 'huge massive blue sofa'
    assert obj['debug']['info'] == [
        'huge', 'massive', 'blue', 'sofa',
        'huge massive', 'huge blue', 'huge sofa', 'massive blue',
        'massive sofa', 'blue sofa', 'huge massive blue sofa',
        'untrained category', 'untrained huge massive blue sofa'
    ]


def test_instantiate_object_untrained_color():
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        untrainedColor=True,
        shape=['sofa'],
        size='huge',
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1}),
        attributes=[]
    )
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
    assert obj['debug']['goalString'] == 'huge massive blue sofa'
    assert obj['debug']['info'] == [
        'huge', 'massive', 'blue', 'sofa',
        'huge massive', 'huge blue', 'huge sofa', 'massive blue',
        'massive sofa', 'blue sofa', 'huge massive blue sofa',
        'untrained color', 'untrained huge massive blue sofa'
    ]


def test_instantiate_object_untrained_combination():
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        untrainedCombination=True,
        shape=['sofa'],
        size='huge',
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1}),
        attributes=[]
    )
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
    assert obj['debug']['goalString'] == 'huge massive blue sofa'
    assert obj['debug']['info'] == [
        'huge', 'massive', 'blue', 'sofa',
        'huge massive', 'huge blue', 'huge sofa', 'massive blue',
        'massive sofa', 'blue sofa', 'huge massive blue sofa',
        'untrained combination', 'untrained huge massive blue sofa'
    ]


def test_instantiate_object_untrained_shape():
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        untrainedShape=True,
        shape=['sofa'],
        size='huge',
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1}),
        attributes=[]
    )
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
    assert obj['debug']['goalString'] == 'huge massive blue sofa'
    assert obj['debug']['info'] == [
        'huge', 'massive', 'blue', 'sofa',
        'huge massive', 'huge blue', 'huge sofa', 'massive blue',
        'massive sofa', 'blue sofa', 'huge massive blue sofa',
        'untrained shape', 'untrained huge massive blue sofa'
    ]


def test_instantiate_object_untrained_size():
    object_def = ObjectDefinition(
        color=['blue'],
        materials=['blue_material'],
        type='sofa_1',
        mass=12.34,
        dimensions=Vector3d(**{'x': 1, 'y': 0.5, 'z': 0.5}),
        untrainedSize=True,
        shape=['sofa'],
        size='huge',
        scale=Vector3d(**{'x': 1, 'y': 1, 'z': 1}),
        attributes=[]
    )
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
    assert obj['debug']['goalString'] == 'huge massive blue sofa'
    assert obj['debug']['info'] == [
        'huge', 'massive', 'blue', 'sofa',
        'huge massive', 'huge blue', 'huge sofa', 'massive blue',
        'massive sofa', 'blue sofa', 'huge massive blue sofa',
        'untrained size', 'untrained huge massive blue sofa'
    ]


def test_instantiate_soccer_ball():
    definition = base_objects.create_soccer_ball()
    location = {
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
    instance = instantiate_object(definition, location)
    assert instance
    assert instance['type'] == 'soccer_ball'
    assert instance['mass'] == 1
    assert instance['debug']['dimensions'] == vars(definition.dimensions)
    assert instance['debug']['goalString'] == (
        'tiny light black white rubber ball'
    )
    assert instance['debug']['info'] == [
        'tiny', 'light', 'black', 'white', 'rubber', 'ball', 'black white',
        'tiny light', 'tiny rubber', 'tiny black white', 'tiny ball',
        'light rubber', 'light black white', 'light ball',
        'rubber black white', 'rubber ball', 'black white ball',
        'tiny light black white rubber ball'
    ]
    assert instance['debug']['untrainedCategory'] is False
    assert instance['debug']['untrainedColor'] is False
    assert instance['debug']['untrainedCombination'] is False
    assert instance['debug']['untrainedShape'] is False
    assert instance['debug']['untrainedSize'] is False
    assert instance['debug']['shape'] == ['ball']
    assert instance['debug']['size'] == 'tiny'
    assert instance['debug']['weight'] == 'light'
    assert instance['shows'][0]['stepBegin'] == 0
    assert instance['shows'][0]['position'] == location['position']
    assert instance['shows'][0]['rotation'] == location['rotation']
    assert instance['shows'][0]['scale'] == vars(definition.scale)


def test_get_earliest_active_step():
    assert -1 == get_earliest_active_step({})
    assert -1 == get_earliest_active_step({
        'forces': [],
        'moves': [],
        'rotates': [],
        'torques': []
    })
    assert 2 == get_earliest_active_step({'forces': [{'stepBegin': 2}]})
    assert 3 == get_earliest_active_step({'moves': [{'stepBegin': 3}]})
    assert 4 == get_earliest_active_step({'rotates': [{'stepBegin': 4}]})
    assert 5 == get_earliest_active_step({'torques': [{'stepBegin': 5}]})
    assert 10 == get_earliest_active_step({
        'moves': [{'stepBegin': 10}, {'stepBegin': 15}]
    })
    assert 20 == get_earliest_active_step({
        'moves': [{'stepBegin': 25}],
        'rotates': [{'stepBegin': 20}]
    })


def test_get_last_move_or_rotate_step():
    assert -1 == get_last_move_or_rotate_step({})
    assert -1 == get_last_move_or_rotate_step({
        'moves': [],
        'rotates': [],
    })
    assert 2 == get_last_move_or_rotate_step({'moves': [{'stepEnd': 2}]})
    assert 3 == get_last_move_or_rotate_step({'rotates': [{'stepEnd': 3}]})
    assert 15 == get_last_move_or_rotate_step({
        'moves': [{'stepEnd': 10}, {'stepEnd': 15}]
    })
    assert 25 == get_last_move_or_rotate_step({
        'moves': [{'stepEnd': 20}],
        'rotates': [{'stepEnd': 25}]
    })
