import copy

from generator import base_objects, mechanisms

BALL_DEFINITION = base_objects.create_soccer_ball()
# 0.42, 0.34, 0.13
DUCK_DEFINITION = base_objects.create_specific_definition_from_base(
    type='duck_on_wheels',
    color=['yellow'],
    materials=['UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1'],  # noqa: E501
    salient_materials=None,
    scale=2
)
# Adjust the duck definition's Y rotation so it's facing left by default.
DUCK_DEFINITION.rotation.y = 180


def test_create_dropping_device():
    device = mechanisms.create_dropping_device(
        1,
        2,
        3,
        vars(BALL_DEFINITION.dimensions),
        100
    )

    assert device['id'].startswith('dropping_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 3
    assert device['materials'] == ['Custom/Materials/Grey']
    assert device['debug']['color'] == ['grey']
    assert device['debug']['info'] == [
        'grey', 'dropper', 'device', 'grey dropper', 'grey device'
    ]
    assert device['states'] == ([['held']] * 100)

    assert len(device['shows']) == 1
    assert device['shows'][0]['stepBegin'] == 0
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2.85, 'z': 2}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.3, 'z': 0.28}
    assert len(device['shows'][0]['boundingBox']) == 4


def test_create_dropping_device_weird_shape():
    device = mechanisms.create_dropping_device(
        1,
        2,
        3,
        vars(DUCK_DEFINITION.dimensions),
        100
    )

    assert device['id'].startswith('dropping_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 17
    assert device['materials'] == ['Custom/Materials/Grey']
    assert device['debug']['color'] == ['grey']
    assert device['debug']['info'] == [
        'grey', 'dropper', 'device', 'grey dropper', 'grey device'
    ]
    assert device['states'] == ([['held']] * 100)

    assert len(device['shows']) == 1
    assert device['shows'][0]['stepBegin'] == 0
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2.765, 'z': 2}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert device['shows'][0]['scale'] == {'x': 0.53, 'y': 0.47, 'z': 0.53}
    assert len(device['shows'][0]['boundingBox']) == 4


def test_create_dropping_device_with_step():
    device = mechanisms.create_dropping_device(
        1,
        2,
        3,
        vars(BALL_DEFINITION.dimensions),
        100,
        25,
        'custom_id'
    )

    assert device['id'].startswith('dropping_device_custom_id_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 3
    assert device['materials'] == ['Custom/Materials/Grey']
    assert device['debug']['color'] == ['grey']
    assert device['debug']['info'] == [
        'grey', 'dropper', 'device', 'grey dropper', 'grey device'
    ]
    assert device['states'] == (([['held']] * 24) + ([['released']] * 76))

    assert len(device['shows']) == 1
    assert device['shows'][0]['stepBegin'] == 0
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2.85, 'z': 2}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.3, 'z': 0.28}
    assert len(device['shows'][0]['boundingBox']) == 4


def test_create_throwing_device():
    device = mechanisms.create_throwing_device(
        1,
        2,
        3,
        0,
        0,
        vars(BALL_DEFINITION.dimensions),
        100
    )

    assert device['id'].startswith('throwing_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 4
    assert device['materials'] == ['Custom/Materials/Grey']
    assert device['debug']['color'] == ['grey']
    assert device['debug']['info'] == [
        'grey', 'thrower', 'device', 'grey thrower', 'grey device'
    ]
    assert device['states'] == ([['held']] * 100)

    assert len(device['shows']) == 1
    assert device['shows'][0]['stepBegin'] == 0
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 90}
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.4, 'z': 0.28}
    assert len(device['shows'][0]['boundingBox']) == 4


def test_create_throwing_device_weird_shape():
    device = mechanisms.create_throwing_device(
        1,
        2,
        3,
        0,
        0,
        vars(DUCK_DEFINITION.dimensions),
        100
    )

    assert device['id'].startswith('throwing_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 22
    assert device['materials'] == ['Custom/Materials/Grey']
    assert device['debug']['color'] == ['grey']
    assert device['debug']['info'] == [
        'grey', 'thrower', 'device', 'grey thrower', 'grey device'
    ]
    assert device['states'] == ([['held']] * 100)

    assert len(device['shows']) == 1
    assert device['shows'][0]['stepBegin'] == 0
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 90}
    assert device['shows'][0]['scale'] == {'x': 0.53, 'y': 0.62, 'z': 0.53}
    assert len(device['shows'][0]['boundingBox']) == 4


def test_create_throwing_device_with_step():
    device = mechanisms.create_throwing_device(
        1,
        2,
        3,
        0,
        0,
        vars(BALL_DEFINITION.dimensions),
        100,
        25,
        'custom_id'
    )

    assert device['id'].startswith('throwing_device_custom_id_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 4
    assert device['materials'] == ['Custom/Materials/Grey']
    assert device['debug']['color'] == ['grey']
    assert device['debug']['info'] == [
        'grey', 'thrower', 'device', 'grey thrower', 'grey device'
    ]
    assert device['states'] == (([['held']] * 24) + ([['released']] * 76))

    assert len(device['shows']) == 1
    assert device['shows'][0]['stepBegin'] == 0
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 90}
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.4, 'z': 0.28}
    assert len(device['shows'][0]['boundingBox']) == 4


def test_create_throwing_device_with_y_rotation():
    device = mechanisms.create_throwing_device(
        1,
        2,
        3,
        30,
        0,
        vars(BALL_DEFINITION.dimensions),
        100
    )

    assert device['id'].startswith('throwing_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 4
    assert device['materials'] == ['Custom/Materials/Grey']
    assert device['debug']['color'] == ['grey']
    assert device['debug']['info'] == [
        'grey', 'thrower', 'device', 'grey thrower', 'grey device'
    ]
    assert device['states'] == ([['held']] * 100)

    assert len(device['shows']) == 1
    assert device['shows'][0]['stepBegin'] == 0
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 30, 'z': 90}
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.4, 'z': 0.28}
    assert len(device['shows'][0]['boundingBox']) == 4


def test_create_throwing_device_with_z_rotation():
    device = mechanisms.create_throwing_device(
        1,
        2,
        3,
        0,
        30,
        vars(BALL_DEFINITION.dimensions),
        100
    )

    assert device['id'].startswith('throwing_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 4
    assert device['materials'] == ['Custom/Materials/Grey']
    assert device['debug']['color'] == ['grey']
    assert device['debug']['info'] == [
        'grey', 'thrower', 'device', 'grey thrower', 'grey device'
    ]
    assert device['states'] == ([['held']] * 100)

    assert len(device['shows']) == 1
    assert device['shows'][0]['stepBegin'] == 0
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 120}
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.4, 'z': 0.28}
    assert len(device['shows'][0]['boundingBox']) == 4


def test_drop_object():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3}
        }]
    }
    target = mechanisms.drop_object(
        copy.deepcopy(BALL_DEFINITION),
        mock_device,
        25
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['togglePhysics'] == [{'stepBegin': 25}]
    assert target['kinematic'] is True

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}


def test_drop_object_weird_shape():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3}
        }]
    }
    target = mechanisms.drop_object(
        copy.deepcopy(DUCK_DEFINITION),
        mock_device,
        25
    )
    assert target['type'] == DUCK_DEFINITION.type
    assert target['togglePhysics'] == [{'stepBegin': 25}]
    assert target['kinematic'] is True

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}


def test_throw_object():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 90},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = mechanisms.throw_object(
        copy.deepcopy(BALL_DEFINITION),
        mock_device,
        345,
        25
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['forces'] == [{
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}


def test_throw_object_downward():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 90},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = mechanisms.throw_object(
        copy.deepcopy(BALL_DEFINITION),
        mock_device,
        345,
        25,
        rotation_z=-5
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['forces'] == [{
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': -5}


def test_throw_object_downward_from_device_with_upward_z_rotation():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 60},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = mechanisms.throw_object(
        copy.deepcopy(BALL_DEFINITION),
        mock_device,
        345,
        25,
        rotation_z=-5
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['forces'] == [{
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': -5}


def test_throw_object_weird_shape():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 90},
            'scale': {'x': 0.53, 'y': 0.62, 'z': 0.53}
        }]
    }
    target = mechanisms.throw_object(
        copy.deepcopy(DUCK_DEFINITION),
        mock_device,
        345,
        25
    )
    assert target['type'] == DUCK_DEFINITION.type
    assert target['forces'] == [{
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}


def test_throw_object_with_y_rotation():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 90, 'z': 90},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = mechanisms.throw_object(
        copy.deepcopy(BALL_DEFINITION),
        mock_device,
        345,
        25
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['forces'] == [{
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}


def test_throw_object_from_device_with_upward_z_rotation():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 60},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = mechanisms.throw_object(
        copy.deepcopy(BALL_DEFINITION),
        mock_device,
        345,
        25
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['forces'] == [{
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
