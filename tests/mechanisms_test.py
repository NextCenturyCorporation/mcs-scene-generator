import copy

import pytest
from machine_common_sense.config_manager import Vector3d

from generator import base_objects, instances, mechanisms

BALL_DEFINITION = base_objects.create_soccer_ball()
# 0.42, 0.34, 0.13
DUCK_DEFINITION = base_objects.create_specific_definition_from_base(
    type='duck_on_wheels',
    color=['yellow'],
    materials=['UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1'],  # noqa: E501
    salient_materials=None,
    scale=2
)
CYLINDER_DEFINITION = base_objects.create_specific_definition_from_base(
    type='cylinder',
    color=['yellow'],
    materials=['UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1'],  # noqa: E501
    salient_materials=None,
    scale=1
)
# Adjust the duck definition's Y rotation so it's facing left by default.
DUCK_DEFINITION.rotation.y = 180


def test_create_dropping_device():
    device = mechanisms.create_dropping_device(
        1,
        2,
        3,
        vars(BALL_DEFINITION.dimensions),
        100,
        is_round=True
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
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2.86, 'z': 2}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.28, 'z': 0.28}
    device_bounds = device['shows'][0]['boundingBox']
    assert vars(device_bounds.box_xz[0]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 2.14}
    )
    assert vars(device_bounds.box_xz[1]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 1.86}
    )
    assert vars(device_bounds.box_xz[2]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 1.86}
    )
    assert vars(device_bounds.box_xz[3]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 2.14}
    )
    assert device_bounds.max_y == 3
    assert device_bounds.min_y == pytest.approx(2.72)


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
    assert device['mass'] == 16
    assert device['materials'] == ['Custom/Materials/Grey']
    assert device['debug']['color'] == ['grey']
    assert device['debug']['info'] == [
        'grey', 'dropper', 'device', 'grey dropper', 'grey device'
    ]
    assert device['states'] == ([['held']] * 100)

    assert len(device['shows']) == 1
    assert device['shows'][0]['stepBegin'] == 0
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2.785, 'z': 2}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert device['shows'][0]['scale'] == {'x': 0.55, 'y': 0.43, 'z': 0.55}
    device_bounds = device['shows'][0]['boundingBox']
    assert vars(device_bounds.box_xz[0]) == pytest.approx(
        {'x': 1.275, 'y': 0, 'z': 2.275}
    )
    assert vars(device_bounds.box_xz[1]) == pytest.approx(
        {'x': 1.275, 'y': 0, 'z': 1.725}
    )
    assert vars(device_bounds.box_xz[2]) == pytest.approx(
        {'x': 0.725, 'y': 0, 'z': 1.725}
    )
    assert vars(device_bounds.box_xz[3]) == pytest.approx(
        {'x': 0.725, 'y': 0, 'z': 2.275}
    )
    assert device_bounds.max_y == pytest.approx(3)
    assert device_bounds.min_y == pytest.approx(2.57)


def test_create_dropping_device_with_step():
    device = mechanisms.create_dropping_device(
        1,
        2,
        3,
        vars(BALL_DEFINITION.dimensions),
        100,
        25,
        'custom_id',
        is_round=True
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
    assert device['shows'][0]['position'] == {'x': 1, 'y': 2.86, 'z': 2}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.28, 'z': 0.28}
    device_bounds = device['shows'][0]['boundingBox']
    assert vars(device_bounds.box_xz[0]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 2.14}
    )
    assert vars(device_bounds.box_xz[1]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 1.86}
    )
    assert vars(device_bounds.box_xz[2]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 1.86}
    )
    assert vars(device_bounds.box_xz[3]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 2.14}
    )
    assert device_bounds.max_y == 3
    assert device_bounds.min_y == pytest.approx(2.72)


def test_create_placer():
    placer = mechanisms.create_placer(
        {'x': 1, 'y': 3, 'z': -1},
        {'x': 1, 'y': 1, 'z': 1},
        0,
        10,
        0,
        4
    )

    assert placer['id'].startswith('placer_')
    assert placer['kinematic'] is True
    assert placer['structure'] is True
    assert placer['type'] == 'cylinder'
    assert placer['mass'] == 10
    assert placer['materials'] == ['Custom/Materials/Magenta']
    assert placer['debug']['color'] == ['magenta', 'cyan']
    assert placer['debug']['info'] == [
        'magenta', 'cyan', 'placer', 'magenta placer', 'cyan placer',
        'magenta cyan placer'
    ]
    assert placer['debug']['shape'] == ['placer']

    assert len(placer['shows']) == 1
    assert placer['shows'][0]['stepBegin'] == 0
    assert placer['shows'][0]['position'] == {'x': 1, 'y': 6.0, 'z': -1}
    assert placer['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placer['shows'][0]['scale'] == {'x': 0.2, 'y': 2, 'z': 0.2}
    placer_bounds = placer['shows'][0]['boundingBox']
    assert vars(placer_bounds.box_xz[0]) == {'x': 1.1, 'y': 0, 'z': -0.9}
    assert vars(placer_bounds.box_xz[1]) == {'x': 1.1, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[2]) == {'x': 0.9, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[3]) == {'x': 0.9, 'y': 0, 'z': -0.9}
    assert placer_bounds.max_y == 7
    assert placer_bounds.min_y == 5

    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 10
    assert placer['moves'][0]['stepEnd'] == 21
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 32
    assert placer['moves'][1]['stepEnd'] == 42
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert placer['materials'] == ['Custom/Materials/Magenta']
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 27
    assert placer['changeMaterials'][0]['materials'] == ['Custom/Materials/Cyan']  # noqa: E501
    assert placer['states'] == ([['active']] * 26) + [['inactive']]


def test_create_placer_with_deactivation_step():
    placer = mechanisms.create_placer(
        {'x': 1, 'y': 3, 'z': -1},
        {'x': 1, 'y': 1, 'z': 1},
        0,
        10,
        0,
        4,
        deactivation_step=100
    )

    assert placer['id'].startswith('placer_')
    assert placer['kinematic'] is True
    assert placer['structure'] is True
    assert placer['type'] == 'cylinder'
    assert placer['mass'] == 10
    assert placer['materials'] == ['Custom/Materials/Magenta']
    assert placer['debug']['color'] == ['magenta', 'cyan']
    assert placer['debug']['info'] == [
        'magenta', 'cyan', 'placer', 'magenta placer', 'cyan placer',
        'magenta cyan placer'
    ]
    assert placer['debug']['shape'] == ['placer']

    assert len(placer['shows']) == 1
    assert placer['shows'][0]['stepBegin'] == 0
    assert placer['shows'][0]['position'] == {'x': 1, 'y': 6.0, 'z': -1}
    assert placer['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placer['shows'][0]['scale'] == {'x': 0.2, 'y': 2, 'z': 0.2}
    placer_bounds = placer['shows'][0]['boundingBox']
    assert vars(placer_bounds.box_xz[0]) == {'x': 1.1, 'y': 0, 'z': -0.9}
    assert vars(placer_bounds.box_xz[1]) == {'x': 1.1, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[2]) == {'x': 0.9, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[3]) == {'x': 0.9, 'y': 0, 'z': -0.9}
    assert placer_bounds.max_y == 7
    assert placer_bounds.min_y == 5

    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 10
    assert placer['moves'][0]['stepEnd'] == 21
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 105
    assert placer['moves'][1]['stepEnd'] == 115
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert placer['materials'] == ['Custom/Materials/Magenta']
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 100
    assert placer['changeMaterials'][0]['materials'] == ['Custom/Materials/Cyan']  # noqa: E501
    assert placer['states'] == ([['active']] * 99) + [['inactive']]


def test_create_placer_with_position_y_offset():
    placer = mechanisms.create_placer(
        {'x': 1, 'y': 3.5, 'z': -1},
        {'x': 1, 'y': 1, 'z': 1},
        0.5,
        10,
        0,
        4
    )

    assert placer['id'].startswith('placer_')
    assert placer['kinematic'] is True
    assert placer['structure'] is True
    assert placer['type'] == 'cylinder'
    assert placer['mass'] == 10
    assert placer['materials'] == ['Custom/Materials/Magenta']
    assert placer['debug']['color'] == ['magenta', 'cyan']
    assert placer['debug']['info'] == [
        'magenta', 'cyan', 'placer', 'magenta placer', 'cyan placer',
        'magenta cyan placer'
    ]
    assert placer['debug']['shape'] == ['placer']

    assert len(placer['shows']) == 1
    assert placer['shows'][0]['stepBegin'] == 0
    assert placer['shows'][0]['position'] == {'x': 1, 'y': 6.0, 'z': -1}
    assert placer['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placer['shows'][0]['scale'] == {'x': 0.2, 'y': 2, 'z': 0.2}
    placer_bounds = placer['shows'][0]['boundingBox']
    assert vars(placer_bounds.box_xz[0]) == {'x': 1.1, 'y': 0, 'z': -0.9}
    assert vars(placer_bounds.box_xz[1]) == {'x': 1.1, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[2]) == {'x': 0.9, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[3]) == {'x': 0.9, 'y': 0, 'z': -0.9}
    assert placer_bounds.max_y == 7
    assert placer_bounds.min_y == 5

    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 10
    assert placer['moves'][0]['stepEnd'] == 21
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 32
    assert placer['moves'][1]['stepEnd'] == 42
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert placer['materials'] == ['Custom/Materials/Magenta']
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 27
    assert placer['changeMaterials'][0]['materials'] == ['Custom/Materials/Cyan']  # noqa: E501
    assert placer['states'] == ([['active']] * 26) + [['inactive']]


def test_create_placer_with_placer_offset():
    placer = mechanisms.create_placer(
        {'x': 1, 'y': 3, 'z': -1},
        {'x': 1, 'y': 1, 'z': 1},
        0,
        10,
        0,
        4,
        placed_object_placer_offset_y=0.05
    )

    assert placer['id'].startswith('placer_')
    assert placer['kinematic'] is True
    assert placer['structure'] is True
    assert placer['type'] == 'cylinder'
    assert placer['mass'] == 10
    assert placer['materials'] == ['Custom/Materials/Magenta']
    assert placer['debug']['color'] == ['magenta', 'cyan']
    assert placer['debug']['info'] == [
        'magenta', 'cyan', 'placer', 'magenta placer', 'cyan placer',
        'magenta cyan placer'
    ]
    assert placer['debug']['shape'] == ['placer']

    assert len(placer['shows']) == 1
    assert placer['shows'][0]['stepBegin'] == 0
    assert placer['shows'][0]['position'] == {'x': 1, 'y': 5.95, 'z': -1}
    assert placer['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placer['shows'][0]['scale'] == {'x': 0.2, 'y': 2, 'z': 0.2}
    placer_bounds = placer['shows'][0]['boundingBox']
    assert vars(placer_bounds.box_xz[0]) == {'x': 1.1, 'y': 0, 'z': -0.9}
    assert vars(placer_bounds.box_xz[1]) == {'x': 1.1, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[2]) == {'x': 0.9, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[3]) == {'x': 0.9, 'y': 0, 'z': -0.9}
    assert placer_bounds.max_y == 6.95
    assert placer_bounds.min_y == 4.95

    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 10
    assert placer['moves'][0]['stepEnd'] == 21
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 32
    assert placer['moves'][1]['stepEnd'] == 42
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert placer['materials'] == ['Custom/Materials/Magenta']
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 27
    assert placer['changeMaterials'][0]['materials'] == ['Custom/Materials/Cyan']  # noqa: E501
    assert placer['states'] == ([['active']] * 26) + [['inactive']]


def test_create_placer_with_last_step():
    placer = mechanisms.create_placer(
        {'x': 1, 'y': 3, 'z': -1},
        {'x': 1, 'y': 1, 'z': 1},
        0,
        10,
        0,
        4,
        last_step=100
    )

    assert placer['id'].startswith('placer_')
    assert placer['kinematic'] is True
    assert placer['structure'] is True
    assert placer['type'] == 'cylinder'
    assert placer['mass'] == 10
    assert placer['materials'] == ['Custom/Materials/Magenta']
    assert placer['debug']['color'] == ['magenta', 'cyan']
    assert placer['debug']['info'] == [
        'magenta', 'cyan', 'placer', 'magenta placer', 'cyan placer',
        'magenta cyan placer'
    ]
    assert placer['debug']['shape'] == ['placer']

    assert len(placer['shows']) == 1
    assert placer['shows'][0]['stepBegin'] == 0
    assert placer['shows'][0]['position'] == {'x': 1, 'y': 6.0, 'z': -1}
    assert placer['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placer['shows'][0]['scale'] == {'x': 0.2, 'y': 2, 'z': 0.2}
    placer_bounds = placer['shows'][0]['boundingBox']
    assert vars(placer_bounds.box_xz[0]) == {'x': 1.1, 'y': 0, 'z': -0.9}
    assert vars(placer_bounds.box_xz[1]) == {'x': 1.1, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[2]) == {'x': 0.9, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[3]) == {'x': 0.9, 'y': 0, 'z': -0.9}
    assert placer_bounds.max_y == 7
    assert placer_bounds.min_y == 5

    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 10
    assert placer['moves'][0]['stepEnd'] == 21
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 32
    assert placer['moves'][1]['stepEnd'] == 42
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert placer['materials'] == ['Custom/Materials/Magenta']
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 27
    assert placer['changeMaterials'][0]['materials'] == ['Custom/Materials/Cyan']  # noqa: E501
    assert placer['states'] == ([['active']] * 26) + ([['inactive']] * 73)


def test_create_placer_pickup_object():
    placer = mechanisms.create_placer(
        placed_object_position={'x': 1, 'y': 3, 'z': -1},
        placed_object_dimensions={'x': 1, 'y': 1, 'z': 1},
        placed_object_offset_y=0,
        activation_step=10,
        end_height=0,
        max_height=4,
        is_pickup_obj=True,
        is_move_obj=False
    )

    assert placer['id'].startswith('placer_')
    assert placer['kinematic'] is True
    assert placer['structure'] is True
    assert placer['type'] == 'cylinder'
    assert placer['mass'] == 10
    assert placer['materials'] == ['Custom/Materials/Cyan']
    assert placer['debug']['color'] == ['magenta', 'cyan']
    assert placer['debug']['info'] == [
        'magenta', 'cyan', 'placer', 'magenta placer', 'cyan placer',
        'magenta cyan placer'
    ]
    assert placer['debug']['shape'] == ['placer']

    assert len(placer['shows']) == 1
    assert placer['shows'][0]['stepBegin'] == 0
    assert placer['shows'][0]['position'] == {'x': 1, 'y': 9.75, 'z': -1}
    assert placer['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placer['shows'][0]['scale'] == {'x': 0.2, 'y': 2, 'z': 0.2}
    placer_bounds = placer['shows'][0]['boundingBox']
    assert vars(placer_bounds.box_xz[0]) == {'x': 1.1, 'y': 0, 'z': -0.9}
    assert vars(placer_bounds.box_xz[1]) == {'x': 1.1, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[2]) == {'x': 0.9, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[3]) == {'x': 0.9, 'y': 0, 'z': -0.9}
    assert placer_bounds.max_y == 10.75
    assert placer_bounds.min_y == 8.75

    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 10
    assert placer['moves'][0]['stepEnd'] == 24
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 35
    assert placer['moves'][1]['stepEnd'] == 48
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert placer['materials'] == ['Custom/Materials/Cyan']
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 30
    assert placer['changeMaterials'][0]['materials'] == ['Custom/Materials/Magenta']  # noqa: E501
    assert placer['states'] == ([['inactive']] * 29) + ([['active']])


def test_create_placer_move_object():
    placer = mechanisms.create_placer(
        placed_object_position={'x': 1, 'y': 3, 'z': -1},
        placed_object_dimensions={'x': 1, 'y': 1, 'z': 1},
        placed_object_offset_y=0,
        activation_step=10,
        end_height=0,
        max_height=4,
        is_pickup_obj=False,
        is_move_obj=True,
        move_object_end_position=Vector3d(x=-1, y=3, z=-1),
        move_object_y=0,
        move_object_z=2
    )

    assert placer['id'].startswith('placer_')
    assert placer['kinematic'] is True
    assert placer['structure'] is True
    assert placer['type'] == 'cylinder'
    assert placer['mass'] == 10
    assert placer['materials'] == ['Custom/Materials/Cyan']
    assert placer['debug']['color'] == ['magenta', 'cyan']
    assert placer['debug']['info'] == [
        'magenta', 'cyan', 'placer', 'magenta placer', 'cyan placer',
        'magenta cyan placer'
    ]
    assert placer['debug']['shape'] == ['placer']

    assert len(placer['shows']) == 1
    assert placer['shows'][0]['stepBegin'] == 0
    assert placer['shows'][0]['position'] == {'x': 1, 'y': 9.75, 'z': -1}
    assert placer['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placer['shows'][0]['scale'] == {'x': 0.2, 'y': 2, 'z': 0.2}
    placer_bounds = placer['shows'][0]['boundingBox']
    assert vars(placer_bounds.box_xz[0]) == {'x': 1.1, 'y': 0, 'z': -0.9}
    assert vars(placer_bounds.box_xz[1]) == {'x': 1.1, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[2]) == {'x': 0.9, 'y': 0, 'z': -1.1}
    assert vars(placer_bounds.box_xz[3]) == {'x': 0.9, 'y': 0, 'z': -0.9}
    assert placer_bounds.max_y == 10.75
    assert placer_bounds.min_y == 8.75

    assert len(placer['moves']) == 5

    assert placer['moves'][0]['stepBegin'] == 10
    assert placer['moves'][0]['stepEnd'] == 24
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 30
    assert placer['moves'][1]['stepEnd'] == 37
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0, 'z': -0.25}
    assert placer['moves'][2]['stepBegin'] == 38
    assert placer['moves'][2]['stepEnd'] == 45
    assert placer['moves'][2]['vector'] == {'x': -0.25, 'y': 0, 'z': 0}
    assert placer['moves'][3]['stepBegin'] == 46
    assert placer['moves'][3]['stepEnd'] == 53
    assert placer['moves'][3]['vector'] == {'x': 0, 'y': 0, 'z': 0.25}
    assert placer['moves'][4]['stepBegin'] == 58
    assert placer['moves'][4]['stepEnd'] == 72
    assert placer['moves'][4]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert placer['materials'] == ['Custom/Materials/Cyan']
    assert len(placer['changeMaterials']) == 2
    assert placer['changeMaterials'][0]['stepBegin'] == 26
    assert placer['changeMaterials'][0]['materials'] == ['Custom/Materials/Magenta']  # noqa: E501
    assert placer['changeMaterials'][1]['stepBegin'] == 55
    assert placer['changeMaterials'][1]['materials'] == ['Custom/Materials/Cyan']  # noqa: E501
    assert placer['states'] == ([['inactive']] * 26) + \
        ([['active']] * 29) + ([['inactive']] * 14)


def test_create_throwing_device():
    device = mechanisms.create_throwing_device(
        1,
        2,
        3,
        0,
        0,
        vars(BALL_DEFINITION.dimensions),
        100,
        is_round=True
    )

    assert device['id'].startswith('throwing_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 3
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
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.28, 'z': 0.28}
    device_bounds = device['shows'][0]['boundingBox']
    assert vars(device_bounds.box_xz[0]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 3.14}
    )
    assert vars(device_bounds.box_xz[1]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 2.86}
    )
    assert vars(device_bounds.box_xz[2]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 2.86}
    )
    assert vars(device_bounds.box_xz[3]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 3.14}
    )
    assert device_bounds.max_y == pytest.approx(2.14)
    assert device_bounds.min_y == pytest.approx(1.86)


def test_create_throwing_device_too_low():
    device = mechanisms.create_throwing_device(
        1,
        0,
        3,
        0,
        0,
        vars(BALL_DEFINITION.dimensions),
        100,
        is_round=True
    )

    assert device['id'].startswith('throwing_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 3
    assert device['materials'] == ['Custom/Materials/Grey']
    assert device['debug']['color'] == ['grey']
    assert device['debug']['info'] == [
        'grey', 'thrower', 'device', 'grey thrower', 'grey device'
    ]
    assert device['states'] == ([['held']] * 100)

    assert len(device['shows']) == 1
    assert device['shows'][0]['stepBegin'] == 0
    assert device['shows'][0]['position'] == {'x': 1, 'y': 0.14, 'z': 3}
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 90}
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.28, 'z': 0.28}
    device_bounds = device['shows'][0]['boundingBox']
    assert vars(device_bounds.box_xz[0]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 3.14}
    )
    assert vars(device_bounds.box_xz[1]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 2.86}
    )
    assert vars(device_bounds.box_xz[2]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 2.86}
    )
    assert vars(device_bounds.box_xz[3]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 3.14}
    )
    assert device_bounds.max_y == pytest.approx(0.28)
    assert device_bounds.min_y == pytest.approx(0)


def test_create_throwing_device_weird_shape():
    device = mechanisms.create_throwing_device(
        1,
        2,
        3,
        0,
        0,
        vars(DUCK_DEFINITION.dimensions),
        100,
        object_rotation_y=DUCK_DEFINITION.rotation.y
    )

    assert device['id'].startswith('throwing_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 14
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
    assert device['shows'][0]['scale'] == {'x': 0.46, 'y': 0.53, 'z': 0.46}
    device_bounds = device['shows'][0]['boundingBox']
    assert vars(device_bounds.box_xz[0]) == pytest.approx(
        {'x': 1.265, 'y': 0, 'z': 3.23}
    )
    assert vars(device_bounds.box_xz[1]) == pytest.approx(
        {'x': 1.265, 'y': 0, 'z': 2.77}
    )
    assert vars(device_bounds.box_xz[2]) == pytest.approx(
        {'x': 0.735, 'y': 0, 'z': 2.77}
    )
    assert vars(device_bounds.box_xz[3]) == pytest.approx(
        {'x': 0.735, 'y': 0, 'z': 3.23}
    )
    assert device_bounds.max_y == pytest.approx(2.23)
    assert device_bounds.min_y == pytest.approx(1.77)


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
        'custom_id',
        is_round=True
    )

    assert device['id'].startswith('throwing_device_custom_id_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 3
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
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.28, 'z': 0.28}
    device_bounds = device['shows'][0]['boundingBox']
    assert vars(device_bounds.box_xz[0]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 3.14}
    )
    assert vars(device_bounds.box_xz[1]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 2.86}
    )
    assert vars(device_bounds.box_xz[2]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 2.86}
    )
    assert vars(device_bounds.box_xz[3]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 3.14}
    )
    assert device_bounds.max_y == pytest.approx(2.14)
    assert device_bounds.min_y == pytest.approx(1.86)


def test_create_throwing_device_with_y_rotation():
    device = mechanisms.create_throwing_device(
        1,
        2,
        3,
        30,
        0,
        vars(BALL_DEFINITION.dimensions),
        100,
        is_round=True
    )

    assert device['id'].startswith('throwing_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 3
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
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.28, 'z': 0.28}
    device_bounds = device['shows'][0]['boundingBox']
    assert vars(device_bounds.box_xz[0]) == pytest.approx(
        {'x': 1.191244, 'y': 0, 'z': 3.051244}
    )
    assert vars(device_bounds.box_xz[1]) == pytest.approx(
        {'x': 1.051244, 'y': 0, 'z': 2.808756}
    )
    assert vars(device_bounds.box_xz[2]) == pytest.approx(
        {'x': 0.808756, 'y': 0, 'z': 2.948756}
    )
    assert vars(device_bounds.box_xz[3]) == pytest.approx(
        {'x': 0.948756, 'y': 0, 'z': 3.191244}
    )
    assert device_bounds.max_y == pytest.approx(2.14)
    assert device_bounds.min_y == pytest.approx(1.86)


def test_create_throwing_device_with_z_rotation():
    device = mechanisms.create_throwing_device(
        1,
        2,
        3,
        0,
        30,
        vars(BALL_DEFINITION.dimensions),
        100,
        is_round=True
    )

    assert device['id'].startswith('throwing_device_')
    assert device['kinematic'] is True
    assert device['structure'] is True
    assert device['type'] == 'tube_wide'
    assert device['mass'] == 3
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
    assert device['shows'][0]['scale'] == {'x': 0.28, 'y': 0.28, 'z': 0.28}
    device_bounds = device['shows'][0]['boundingBox']
    assert vars(device_bounds.box_xz[0]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 3.14}
    )
    assert vars(device_bounds.box_xz[1]) == pytest.approx(
        {'x': 1.14, 'y': 0, 'z': 2.86}
    )
    assert vars(device_bounds.box_xz[2]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 2.86}
    )
    assert vars(device_bounds.box_xz[3]) == pytest.approx(
        {'x': 0.86, 'y': 0, 'z': 3.14}
    )
    assert device_bounds.max_y == pytest.approx(2.14)
    assert device_bounds.min_y == pytest.approx(1.86)


def test_drop_object():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3}
        }]
    }
    target = instances.instantiate_object(
        copy.deepcopy(BALL_DEFINITION),
        {'position': {'x': 0, 'y': 0, 'z': 0}}
    )
    target = mechanisms.drop_object(
        target,
        mock_device,
        25
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['togglePhysics'] == [{'stepBegin': 25}]
    assert target['kinematic'] is True

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    target_bounds = target['shows'][0]['boundingBox']
    assert vars(target_bounds.box_xz[0]) == {'x': 1.11, 'y': 0, 'z': 3.11}
    assert vars(target_bounds.box_xz[1]) == {'x': 1.11, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[2]) == {'x': 0.89, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[3]) == {'x': 0.89, 'y': 0, 'z': 3.11}
    assert target_bounds.max_y == 2.11
    assert target_bounds.min_y == 1.89


def test_drop_object_cylinder():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3}
        }]
    }
    target = instances.instantiate_object(
        copy.deepcopy(CYLINDER_DEFINITION),
        {'position': {'x': 0, 'y': 0, 'z': 0}}
    )
    target = mechanisms.drop_object(
        target,
        mock_device,
        25
    )
    assert target['type'] == CYLINDER_DEFINITION.type
    assert target['togglePhysics'] == [{'stepBegin': 25}]
    assert target['kinematic'] is True

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 90, 'y': 0, 'z': 0}
    target_bounds = target['shows'][0]['boundingBox']
    assert vars(target_bounds.box_xz[0]) == {
        'x': pytest.approx(1.5), 'y': 0, 'z': 3.5}
    assert vars(target_bounds.box_xz[1]) == {
        'x': pytest.approx(1.5), 'y': 0, 'z': 2.5}
    assert vars(target_bounds.box_xz[2]) == {
        'x': pytest.approx(0.5), 'y': 0, 'z': 2.5}
    assert vars(target_bounds.box_xz[3]) == {
        'x': pytest.approx(0.5), 'y': 0, 'z': 3.5}
    assert target_bounds.max_y == 2.5
    assert target_bounds.min_y == 1.5


def test_drop_object_weird_shape():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3}
        }]
    }
    target = instances.instantiate_object(
        copy.deepcopy(DUCK_DEFINITION),
        {'position': {'x': 0, 'y': 0, 'z': 0}}
    )
    target = mechanisms.drop_object(
        target,
        mock_device,
        25,
        rotation_y=DUCK_DEFINITION.rotation.y
    )
    assert target['type'] == DUCK_DEFINITION.type
    assert target['togglePhysics'] == [{'stepBegin': 25}]
    assert target['kinematic'] is True

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 360, 'z': 0}
    target_bounds = target['shows'][0]['boundingBox']
    assert vars(target_bounds.box_xz[0]) == {'x': 1.21, 'y': 0, 'z': 3.065}
    assert vars(target_bounds.box_xz[1]) == {'x': 1.21, 'y': 0, 'z': 2.935}
    assert vars(target_bounds.box_xz[2]) == {'x': 0.79, 'y': 0, 'z': 2.935}
    assert vars(target_bounds.box_xz[3]) == {'x': 0.79, 'y': 0, 'z': 3.065}
    assert target_bounds.max_y == 2.33
    assert target_bounds.min_y == 1.99


def test_place_object():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 3, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0
        }
    }
    mechanisms.place_object(mock_instance, 10)
    assert mock_instance['kinematic']
    assert mock_instance['togglePhysics'] == [{'stepBegin': 27}]

    assert len(mock_instance['shows']) == 1
    assert mock_instance['shows'][0]['position'] == {'x': 1, 'y': 3, 'z': -1}
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(5)
    assert bounds.min_y == pytest.approx(3)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 10
    assert mock_instance['moves'][0]['stepEnd'] == 21
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_place_object_with_deactivation_step():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 3, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0
        }
    }
    mechanisms.place_object(mock_instance, 10, deactivation_step=100)
    assert mock_instance['kinematic']
    assert mock_instance['togglePhysics'] == [{'stepBegin': 100}]

    assert len(mock_instance['shows']) == 1
    assert mock_instance['shows'][0]['position'] == {'x': 1, 'y': 3, 'z': -1}
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(5)
    assert bounds.min_y == pytest.approx(3)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 10
    assert mock_instance['moves'][0]['stepEnd'] == 21
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_place_object_with_position_y_offset():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 3.5, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0.5
        }
    }
    mechanisms.place_object(mock_instance, 10)
    assert mock_instance['kinematic']
    assert mock_instance['togglePhysics'] == [{'stepBegin': 27}]

    assert len(mock_instance['shows']) == 1
    assert (
        mock_instance['shows'][0]['position'] == {'x': 1, 'y': 3.5, 'z': -1}
    )
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(5)
    assert bounds.min_y == pytest.approx(3)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 10
    assert mock_instance['moves'][0]['stepEnd'] == 21
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_place_object_with_end_height():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 3, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0
        }
    }
    mechanisms.place_object(mock_instance, 10, end_height=1)
    assert mock_instance['kinematic']
    assert mock_instance['togglePhysics'] == [{'stepBegin': 23}]

    assert len(mock_instance['shows']) == 1
    assert mock_instance['shows'][0]['position'] == {'x': 1, 'y': 3, 'z': -1}
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(5)
    assert bounds.min_y == pytest.approx(3)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 10
    assert mock_instance['moves'][0]['stepEnd'] == 17
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_place_object_with_end_height_position_y_offset():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 3.5, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0.5
        }
    }
    mechanisms.place_object(mock_instance, 10, end_height=1)
    assert mock_instance['kinematic']
    assert mock_instance['togglePhysics'] == [{'stepBegin': 23}]

    assert len(mock_instance['shows']) == 1
    assert (
        mock_instance['shows'][0]['position'] == {'x': 1, 'y': 3.5, 'z': -1}
    )
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(5)
    assert bounds.min_y == pytest.approx(3)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 10
    assert mock_instance['moves'][0]['stepEnd'] == 17
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_place_object_with_start_height():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 0, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0
        }
    }
    mechanisms.place_object(mock_instance, 10, start_height=5)
    assert mock_instance['kinematic']
    assert mock_instance['togglePhysics'] == [{'stepBegin': 26}]

    assert len(mock_instance['shows']) == 1
    assert mock_instance['shows'][0]['position'] == (
        {'x': 1, 'y': 2.75, 'z': -1}
    )
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(4.75)
    assert bounds.min_y == pytest.approx(2.75)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 10
    assert mock_instance['moves'][0]['stepEnd'] == 20
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_place_object_with_start_height_position_y_offset():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 0, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0.5
        }
    }
    mechanisms.place_object(mock_instance, 10, start_height=5)
    assert mock_instance['kinematic']
    assert mock_instance['togglePhysics'] == [{'stepBegin': 26}]

    assert len(mock_instance['shows']) == 1
    assert mock_instance['shows'][0]['position'] == (
        {'x': 1, 'y': 3.25, 'z': -1}
    )
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(4.75)
    assert bounds.min_y == pytest.approx(2.75)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 10
    assert mock_instance['moves'][0]['stepEnd'] == 20
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_place_object_position_adjustment():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 2.74, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0
        }
    }
    mechanisms.place_object(mock_instance, 10)
    assert mock_instance['kinematic']
    assert mock_instance['togglePhysics'] == [{'stepBegin': 25}]

    assert len(mock_instance['shows']) == 1
    assert mock_instance['shows'][0]['position'] == {'x': 1, 'y': 2.5, 'z': -1}
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(4.5)
    assert bounds.min_y == pytest.approx(2.5)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 10
    assert mock_instance['moves'][0]['stepEnd'] == 19
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_place_object_with_end_height_and_position_adjustment():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 2.74, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0
        }
    }
    mechanisms.place_object(mock_instance, 10, end_height=1)
    assert mock_instance['kinematic']
    assert mock_instance['togglePhysics'] == [{'stepBegin': 21}]

    assert len(mock_instance['shows']) == 1
    assert mock_instance['shows'][0]['position'] == {'x': 1, 'y': 2.5, 'z': -1}
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(4.5)
    assert bounds.min_y == pytest.approx(2.5)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 10
    assert mock_instance['moves'][0]['stepEnd'] == 15
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_place_object_with_start_height_and_position_adjustment():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 2.74, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0
        }
    }
    mechanisms.place_object(mock_instance, 10, start_height=3.74)
    assert mock_instance['kinematic']
    assert mock_instance['togglePhysics'] == [{'stepBegin': 21}]

    assert len(mock_instance['shows']) == 1
    assert mock_instance['shows'][0]['position'] == {'x': 1, 'y': 1.5, 'z': -1}
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(3.5)
    assert bounds.min_y == pytest.approx(1.5)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 10
    assert mock_instance['moves'][0]['stepEnd'] == 15
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_pickup_object():
    mock_instance = {
        'shows': [{
            'position': {'x': 1, 'y': 1, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }],
        'debug': {
            'dimensions': {'x': 2, 'y': 2, 'z': 2},
            'positionY': 0
        }
    }
    mechanisms.pickup_object(
        mock_instance,
        10,
        start_height=1,
        end_height=5,
        deactivation_step=50)
    assert mock_instance['kinematic'] is False
    assert mock_instance['togglePhysics'] == [{'stepBegin': 10}]

    assert len(mock_instance['shows']) == 1
    assert mock_instance['shows'][0]['position'] == {'x': 1, 'y': 1, 'z': -1}
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(3)
    assert bounds.min_y == pytest.approx(1)

    assert len(mock_instance['moves']) == 1
    assert mock_instance['moves'][0]['stepBegin'] == 55
    assert mock_instance['moves'][0]['stepEnd'] == 68
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}


def test_move_object():
    mock_instance = {
        'shows': [{
            'position': {'x': 3, 'y': 0, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 1}
        }],
        'debug': {
            'dimensions': {'x': 1, 'y': 1, 'z': 1},
            'positionY': 0
        }
    }
    move_object_end_position = Vector3d(x=-3.0, y=0.0, z=3.0)
    move_object_y = 0
    mechanisms.move_object(
        instance=mock_instance,
        move_object_end_position=move_object_end_position,
        activation_step=10,
        start_height=0,
        end_height=5,
        deactivation_step=50,
        move_object_y=move_object_y)
    assert mock_instance['kinematic'] is True

    assert len(mock_instance['shows']) == 1
    assert mock_instance['shows'][0]['position'] == {'x': 3, 'y': 0, 'z': 3}
    assert mock_instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert mock_instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    bounds = mock_instance['shows'][0]['boundingBox']
    assert bounds.max_y == pytest.approx(1)
    assert bounds.min_y == 0

    assert len(mock_instance['moves']) == 3
    assert mock_instance['moves'][0]['stepBegin'] == 32
    assert mock_instance['moves'][0]['stepEnd'] == 37
    assert mock_instance['moves'][0]['vector'] == {'x': 0, 'y': 0, 'z': -0.25}
    assert mock_instance['moves'][1]['stepBegin'] == 38
    assert mock_instance['moves'][1]['stepEnd'] == 61
    assert mock_instance['moves'][1]['vector'] == {'x': -0.25, 'y': 0, 'z': 0}
    assert mock_instance['moves'][2]['stepBegin'] == 62
    assert mock_instance['moves'][2]['stepEnd'] == 67
    assert mock_instance['moves'][2]['vector'] == {'x': 0, 'y': 0, 'z': .25}


def test_throw_object():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 90},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = instances.instantiate_object(
        copy.deepcopy(BALL_DEFINITION),
        {'position': {'x': 0, 'y': 0, 'z': 0}}
    )
    target = mechanisms.throw_object(
        target,
        mock_device,
        345,
        25
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['forces'] == [{
        'impulse': True,
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]
    assert target.get('maxAngularVelocity') is None

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    target_bounds = target['shows'][0]['boundingBox']
    assert vars(target_bounds.box_xz[0]) == {'x': 1.11, 'y': 0, 'z': 3.11}
    assert vars(target_bounds.box_xz[1]) == {'x': 1.11, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[2]) == {'x': 0.89, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[3]) == {'x': 0.89, 'y': 0, 'z': 3.11}
    assert target_bounds.max_y == 2.11
    assert target_bounds.min_y == 1.89


def test_throw_object_cylinder():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 90},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = instances.instantiate_object(
        copy.deepcopy(CYLINDER_DEFINITION),
        {'position': {'x': 0, 'y': 0, 'z': 0}}
    )
    target = mechanisms.throw_object(
        target,
        mock_device,
        345,
        25
    )
    assert target['type'] == CYLINDER_DEFINITION.type
    assert target['forces'] == [{
        'impulse': True,
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]
    assert target.get('maxAngularVelocity') is None

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 90, 'y': 0, 'z': 0}
    target_bounds = target['shows'][0]['boundingBox']
    assert vars(target_bounds.box_xz[0]) == {
        'x': pytest.approx(1.5), 'y': 0, 'z': 3.5}
    assert vars(target_bounds.box_xz[1]) == {
        'x': pytest.approx(1.5), 'y': 0, 'z': 2.5}
    assert vars(target_bounds.box_xz[2]) == {
        'x': pytest.approx(0.5), 'y': 0, 'z': 2.5}
    assert vars(target_bounds.box_xz[3]) == {
        'x': pytest.approx(0.5), 'y': 0, 'z': 3.5}
    assert target_bounds.max_y == 2.5
    assert target_bounds.min_y == 1.5


def test_throw_object_downward():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 90},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = instances.instantiate_object(
        copy.deepcopy(BALL_DEFINITION),
        {'position': {'x': 0, 'y': 0, 'z': 0}}
    )
    target = mechanisms.throw_object(
        target,
        mock_device,
        345,
        25,
        rotation_z=-5
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['forces'] == [{
        'impulse': True,
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]
    assert target.get('maxAngularVelocity') is None

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': -5}
    target_bounds = target['shows'][0]['boundingBox']
    assert vars(target_bounds.box_xz[0]) == {'x': 1.11, 'y': 0, 'z': 3.11}
    assert vars(target_bounds.box_xz[1]) == {'x': 1.11, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[2]) == {'x': 0.89, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[3]) == {'x': 0.89, 'y': 0, 'z': 3.11}
    assert target_bounds.max_y == 2.11
    assert target_bounds.min_y == 1.89


def test_throw_object_downward_from_device_with_upward_z_rotation():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 60},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = instances.instantiate_object(
        copy.deepcopy(BALL_DEFINITION),
        {'position': {'x': 0, 'y': 0, 'z': 0}}
    )
    target = mechanisms.throw_object(
        target,
        mock_device,
        345,
        25,
        rotation_z=-5
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['forces'] == [{
        'impulse': True,
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]
    assert target.get('maxAngularVelocity') is None

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': -5}
    target_bounds = target['shows'][0]['boundingBox']
    assert vars(target_bounds.box_xz[0]) == {'x': 1.11, 'y': 0, 'z': 3.11}
    assert vars(target_bounds.box_xz[1]) == {'x': 1.11, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[2]) == {'x': 0.89, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[3]) == {'x': 0.89, 'y': 0, 'z': 3.11}
    assert target_bounds.max_y == 2.11
    assert target_bounds.min_y == 1.89


def test_throw_object_weird_shape():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 90},
            'scale': {'x': 0.53, 'y': 0.62, 'z': 0.53}
        }]
    }
    target = instances.instantiate_object(
        copy.deepcopy(DUCK_DEFINITION),
        {'position': {'x': 0, 'y': 0, 'z': 0}}
    )
    target = mechanisms.throw_object(
        target,
        mock_device,
        345,
        25,
        rotation_y=DUCK_DEFINITION.rotation.y
    )
    assert target['type'] == DUCK_DEFINITION.type
    assert target['forces'] == [{
        'impulse': True,
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]
    assert target.get('maxAngularVelocity') is None

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 1.84, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 360, 'z': 0}
    target_bounds = target['shows'][0]['boundingBox']
    assert vars(target_bounds.box_xz[0]) == {'x': 1.21, 'y': 0, 'z': 3.065}
    assert vars(target_bounds.box_xz[1]) == {'x': 1.21, 'y': 0, 'z': 2.935}
    assert vars(target_bounds.box_xz[2]) == {'x': 0.79, 'y': 0, 'z': 2.935}
    assert vars(target_bounds.box_xz[3]) == {'x': 0.79, 'y': 0, 'z': 3.065}
    assert target_bounds.max_y == 2.17
    assert target_bounds.min_y == 1.83


def test_throw_object_with_y_rotation():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 90, 'z': 90},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = instances.instantiate_object(
        copy.deepcopy(BALL_DEFINITION),
        {'position': {'x': 0, 'y': 0, 'z': 0}}
    )
    target = mechanisms.throw_object(
        target,
        mock_device,
        345,
        25
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['forces'] == [{
        'impulse': True,
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]
    assert target.get('maxAngularVelocity') is None

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    target_bounds = target['shows'][0]['boundingBox']
    assert vars(target_bounds.box_xz[0]) == {'x': 1.11, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[1]) == {'x': 0.89, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[2]) == {'x': 0.89, 'y': 0, 'z': 3.11}
    assert vars(target_bounds.box_xz[3]) == {'x': 1.11, 'y': 0, 'z': 3.11}
    assert target_bounds.max_y == 2.11
    assert target_bounds.min_y == 1.89


def test_throw_object_from_device_with_upward_z_rotation():
    mock_device = {
        'shows': [{
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 60},
            'scale': {'x': 0.28, 'y': 0.4, 'z': 0.28}
        }]
    }
    target = instances.instantiate_object(
        copy.deepcopy(BALL_DEFINITION),
        {'position': {'x': 0, 'y': 0, 'z': 0}}
    )
    target = mechanisms.throw_object(
        target,
        mock_device,
        345,
        25
    )
    assert target['type'] == BALL_DEFINITION.type
    assert target['forces'] == [{
        'impulse': True,
        'relative': True,
        'stepBegin': 25,
        'stepEnd': 25,
        'vector': {'x': 345, 'y': 0, 'z': 0}
    }]
    assert target.get('maxAngularVelocity') is None

    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    target_bounds = target['shows'][0]['boundingBox']
    assert vars(target_bounds.box_xz[0]) == {'x': 1.11, 'y': 0, 'z': 3.11}
    assert vars(target_bounds.box_xz[1]) == {'x': 1.11, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[2]) == {'x': 0.89, 'y': 0, 'z': 2.89}
    assert vars(target_bounds.box_xz[3]) == {'x': 0.89, 'y': 0, 'z': 3.11}
    assert target_bounds.max_y == 2.11
    assert target_bounds.min_y == 1.89
