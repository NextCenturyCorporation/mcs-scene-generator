import copy

import pytest
from machine_common_sense.config_manager import Goal, Vector3d

from generator import (
    MaterialTuple,
    ObjectBounds,
    Scene,
    exceptions,
    geometry,
    materials
)
from hypercube import hypercubes
from hypercube.agent_scene_pair_json_converter import (
    AGENT_OBJECT_CONFIG_LIST,
    AGENT_OBJECT_MATERIAL_LIST,
    GOAL_OBJECT_MATERIAL_LIST,
    OBJECT_DIMENSIONS,
    AgentConfig,
    ObjectConfig,
    ObjectConfigWithMaterial,
    OccluderMode,
    TrueObjectBounds,
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
    _create_occluder_object,
    _create_paddle_object,
    _create_scene,
    _create_show,
    _create_static_wall_object_list,
    _create_trial_frame_list,
    _create_wall_object_list,
    _fix_key_location,
    _identify_trial_index_starting_step,
    _make_true_bounds,
    _move_agent_adjacent_to_goal,
    _move_agent_past_lock_location,
    _remove_extraneous_object_show,
    _remove_intersecting_agent_steps,
    _reposition_agents_away_from_paddle,
    _retrieve_unit_size
)

UNIT_SIZE = [0.025, 0.025]


def create_ellipsoidal_bounds(center_x, center_z, radius_x, radius_z):
    # Just use an arbitrary round shape, Y dimension, rotation, and standing Y.
    return _make_true_bounds(
        'cylinder',
        dimensions={'x': radius_x * 2, 'y': 1, 'z': radius_z * 2},
        offset=None,
        position={'x': center_x, 'y': 0, 'z': center_z},
        rotation={'x': 0, 'y': 0, 'z': 0},
        standing_y=0
    )


def create_simple_bounds(x1, x2, z1, z2, y=0):
    rect = [(x2, z2), (x2, z1), (x1, z1), (x1, z2)]
    bounds = ObjectBounds(
        box_xz=[Vector3d(x=x, y=0, z=z) for x, z in rect],
        max_y=y,
        min_y=0
    )
    return TrueObjectBounds(bounds=bounds, true_poly=bounds.polygon_xz)


def create_test_agent_moving_diagonally(trial_2=False):
    bounds_a = create_simple_bounds(-2.5, -2.25, -2.5, -2.25, y=0.25)
    bounds_b = create_simple_bounds(-2.25, -2.0, -2.25, -2.0, y=0.25)
    bounds_c = create_simple_bounds(-2.0, -1.75, -2.0, -1.75, y=0.25)
    bounds_d = create_simple_bounds(-1.75, -1.5, -1.75, -1.5, y=0.25)
    bounds_e = create_simple_bounds(-1.5, -1.25, -1.5, -1.25, y=0.25)
    bounds_f = create_simple_bounds(-1.25, -1.0, -1.25, -1.0, y=0.25)
    bounds_g = create_simple_bounds(-1.0, -0.75, -1.0, -0.75, y=0.25)
    bounds_h = create_simple_bounds(-0.75, -0.5, -0.75, -0.5, y=0.25)
    bounds_i = create_simple_bounds(-0.5, -0.25, -0.5, -0.25, y=0.25)
    bounds_j = create_simple_bounds(-0.25, 0, -0.25, 0, y=0.25)
    bounds_k = create_simple_bounds(0, 0.25, 0, 0.25, y=0.25)
    bounds_l = create_simple_bounds(0.25, 0.5, 0.25, 0.5, y=0.25)
    bounds_m = create_simple_bounds(0.5, 0.75, 0.5, 0.75, y=0.25)
    bounds_n = create_simple_bounds(0.75, 1.0, 0.75, 1.0, y=0.25)
    bounds_o = create_simple_bounds(1.0, 1.25, 1.0, 1.25, y=0.25)
    bounds_p = create_simple_bounds(1.25, 1.5, 1.25, 1.5, y=0.25)
    bounds_q = create_simple_bounds(1.5, 1.75, 1.5, 1.75, y=0.25)
    bounds_r = create_simple_bounds(1.75, 2.0, 1.75, 2.0, y=0.25)
    position_a = {'x': -2.375, 'y': 0.125, 'z': -2.375}
    position_b = {'x': -2.125, 'y': 0.125, 'z': -2.125}
    position_c = {'x': -1.875, 'y': 0.125, 'z': -1.875}
    position_d = {'x': -1.625, 'y': 0.125, 'z': -1.625}
    position_e = {'x': -1.375, 'y': 0.125, 'z': -1.375}
    position_f = {'x': -1.125, 'y': 0.125, 'z': -1.125}
    position_g = {'x': -0.875, 'y': 0.125, 'z': -0.875}
    position_h = {'x': -0.625, 'y': 0.125, 'z': -0.625}
    position_i = {'x': -0.375, 'y': 0.125, 'z': -0.375}
    position_j = {'x': -0.125, 'y': 0.125, 'z': -0.125}
    position_k = {'x': 0.125, 'y': 0.125, 'z': 0.125}
    position_l = {'x': 0.375, 'y': 0.125, 'z': 0.375}
    position_m = {'x': 0.625, 'y': 0.125, 'z': 0.625}
    position_n = {'x': 0.875, 'y': 0.125, 'z': 0.875}
    position_o = {'x': 1.125, 'y': 0.125, 'z': 1.125}
    position_p = {'x': 1.375, 'y': 0.125, 'z': 1.375}
    position_q = {'x': 1.625, 'y': 0.125, 'z': 1.625}
    position_r = {'x': 1.875, 'y': 0.125, 'z': 1.875}
    agent = {
        'id': 'agent_1',
        'type': 'sphere',
        'debug': {
            'boundsAtStep': [
                bounds_a, bounds_a, bounds_a, bounds_a, bounds_a,
                bounds_b, bounds_c, bounds_d, bounds_e, bounds_f,
                bounds_g, bounds_h, bounds_i, bounds_j, bounds_k,
                bounds_l, bounds_m, bounds_n, bounds_o, bounds_p,
                bounds_q, bounds_r, bounds_r, bounds_r, bounds_r
            ],
            'dimensions': {'x': 0.25, 'y': 0.25, 'z': 0.25},
            'positionY': 0.125,
            'trialToSteps': {
                0: (0, 24)
            }
        },
        'shows': [{
            'stepBegin': 0,
            'position': position_a,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_a
        }, {
            'stepBegin': 5,
            'position': position_b,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_b
        }, {
            'stepBegin': 6,
            'position': position_c,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_c
        }, {
            'stepBegin': 7,
            'position': position_d,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_d
        }, {
            'stepBegin': 8,
            'position': position_e,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_e
        }, {
            'stepBegin': 9,
            'position': position_f,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_f
        }, {
            'stepBegin': 10,
            'position': position_g,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_g
        }, {
            'stepBegin': 11,
            'position': position_h,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_h
        }, {
            'stepBegin': 12,
            'position': position_i,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_i
        }, {
            'stepBegin': 13,
            'position': position_j,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_j
        }, {
            'stepBegin': 14,
            'position': position_k,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_k
        }, {
            'stepBegin': 15,
            'position': position_l,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_l
        }, {
            'stepBegin': 16,
            'position': position_m,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_m
        }, {
            'stepBegin': 17,
            'position': position_n,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_n
        }, {
            'stepBegin': 18,
            'position': position_o,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_o
        }, {
            'stepBegin': 19,
            'position': position_p,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_p
        }, {
            'stepBegin': 20,
            'position': position_q,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_q
        }, {
            'stepBegin': 21,
            'position': position_r,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_r
        }]
    }
    if trial_2:
        bounds_2a = create_simple_bounds(2.5, 2.25, 2.5, 2.25, y=0.25)
        bounds_2b = create_simple_bounds(2.25, 2.0, 2.25, 2.0, y=0.25)
        bounds_2c = create_simple_bounds(2.0, 1.75, 2.0, 1.75, y=0.25)
        bounds_2d = create_simple_bounds(1.75, 1.5, 1.75, 1.5, y=0.25)
        bounds_2e = create_simple_bounds(1.5, 1.25, 1.5, 1.25, y=0.25)
        bounds_2f = create_simple_bounds(1.25, 1.0, 1.25, 1.0, y=0.25)
        bounds_2g = create_simple_bounds(1.0, 0.75, 1.0, 0.75, y=0.25)
        bounds_2h = create_simple_bounds(0.75, 0.5, 0.75, 0.5, y=0.25)
        bounds_2i = create_simple_bounds(0.5, 0.25, 0.5, 0.25, y=0.25)
        bounds_2j = create_simple_bounds(0.25, 0, 0.25, 0, y=0.25)
        bounds_2k = create_simple_bounds(0, -0.25, 0, -0.25, y=0.25)
        bounds_2l = create_simple_bounds(-0.25, -0.5, -0.25, -0.5, y=0.25)
        bounds_2m = create_simple_bounds(-0.5, -0.75, -0.5, -0.75, y=0.25)
        bounds_2n = create_simple_bounds(-0.75, -1.0, -0.75, -1.0, y=0.25)
        bounds_2o = create_simple_bounds(-1.0, -1.25, -1.0, -1.25, y=0.25)
        bounds_2p = create_simple_bounds(-1.25, -1.5, -1.25, -1.5, y=0.25)
        bounds_2q = create_simple_bounds(-1.5, -1.75, -1.5, -1.75, y=0.25)
        bounds_2r = create_simple_bounds(-1.75, -2.0, -1.75, -2.0, y=0.25)
        position_2a = {'x': 2.375, 'y': 0.125, 'z': 2.375}
        position_2b = {'x': 2.125, 'y': 0.125, 'z': 2.125}
        position_2c = {'x': 1.875, 'y': 0.125, 'z': 1.875}
        position_2d = {'x': 1.625, 'y': 0.125, 'z': 1.625}
        position_2e = {'x': 1.375, 'y': 0.125, 'z': 1.375}
        position_2f = {'x': 1.125, 'y': 0.125, 'z': 1.125}
        position_2g = {'x': 0.875, 'y': 0.125, 'z': 0.875}
        position_2h = {'x': 0.625, 'y': 0.125, 'z': 0.625}
        position_2i = {'x': 0.375, 'y': 0.125, 'z': 0.375}
        position_2j = {'x': 0.125, 'y': 0.125, 'z': 0.125}
        position_2k = {'x': -0.125, 'y': 0.125, 'z': -0.125}
        position_2l = {'x': -0.375, 'y': 0.125, 'z': -0.375}
        position_2m = {'x': -0.625, 'y': 0.125, 'z': -0.625}
        position_2n = {'x': -0.875, 'y': 0.125, 'z': -0.875}
        position_2o = {'x': -1.125, 'y': 0.125, 'z': -1.125}
        position_2p = {'x': -1.375, 'y': 0.125, 'z': -1.375}
        position_2q = {'x': -1.625, 'y': 0.125, 'z': -1.625}
        position_2r = {'x': -1.875, 'y': 0.125, 'z': -1.875}
        agent['debug']['boundsAtStep'].extend([
            bounds_2a, bounds_2a, bounds_2a, bounds_2a, bounds_2a,
            bounds_2b, bounds_2c, bounds_2d, bounds_2e, bounds_2f,
            bounds_2g, bounds_2h, bounds_2i, bounds_2j, bounds_2k,
            bounds_2l, bounds_2m, bounds_2n, bounds_2o, bounds_2p,
            bounds_2q, bounds_2r, bounds_2r, bounds_2r, bounds_2r
        ])
        agent['debug']['trialToSteps'][1] = (25, 49)
        agent['shows'].extend([{
            'stepBegin': 25,
            'position': position_2a,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2a
        }, {
            'stepBegin': 30,
            'position': position_2b,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2b
        }, {
            'stepBegin': 31,
            'position': position_2c,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2c
        }, {
            'stepBegin': 32,
            'position': position_2d,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2d
        }, {
            'stepBegin': 33,
            'position': position_2e,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2e
        }, {
            'stepBegin': 34,
            'position': position_2f,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2f
        }, {
            'stepBegin': 35,
            'position': position_2g,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2g
        }, {
            'stepBegin': 36,
            'position': position_2h,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2h
        }, {
            'stepBegin': 37,
            'position': position_2i,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2i
        }, {
            'stepBegin': 38,
            'position': position_2j,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2j
        }, {
            'stepBegin': 39,
            'position': position_2k,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2k
        }, {
            'stepBegin': 40,
            'position': position_2l,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2l
        }, {
            'stepBegin': 41,
            'position': position_2m,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2m
        }, {
            'stepBegin': 42,
            'position': position_2n,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2n
        }, {
            'stepBegin': 43,
            'position': position_2o,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2o
        }, {
            'stepBegin': 44,
            'position': position_2p,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2p
        }, {
            'stepBegin': 45,
            'position': position_2q,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2q
        }, {
            'stepBegin': 46,
            'position': position_2r,
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': bounds_2r
        }])
    return agent


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
    assert key_object['physics']
    assert not key_object.get('structure')
    assert key_object['debug']['info'] == [
        'maroon', 'red', 'triangle', 'maroon red triangle'
    ]
    assert key_object['debug']['configHeight'] == [0.05, 0.35]
    assert key_object['debug']['configSize'] == [0.1, 0.35]
    verify_key_show(key_object)


def verify_key_show(key_object):
    assert len(key_object['shows']) >= 1
    for index, show in enumerate(key_object['shows']):
        assert show['rotation']['x'] == 0
        assert show['rotation']['z'] == 90
        if index == 0:
            assert show['scale']['x'] == 0.1
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
        'lime', 'green', 'lock_wall', 'lime green lock_wall'
    ]
    assert lock_object['debug']['configHeight'] == [0.05, 0.1]
    assert lock_object['debug']['configSize'] == [0.495, 0.495]

    assert len(lock_object['shows']) == 1
    assert lock_object['shows'][0]['rotation']['x'] == 0
    assert lock_object['shows'][0]['rotation']['z'] == 0
    assert lock_object['shows'][0]['scale']['x'] == 0.495
    assert lock_object['shows'][0]['scale']['y'] == 0.1
    assert lock_object['shows'][0]['scale']['z'] == 0.495


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
    verify_show(wall_object_list[0], 0, 0, -1.75, 0.05, -1.75)
    verify_show(wall_object_list[1], 0, 0, -1.75, 0.05, 1.75)
    verify_show(wall_object_list[2], 0, 0, 1.75, 0.05, -1.75)
    verify_show(wall_object_list[3], 0, 0, 1.75, 0.05, 1.75)
    verify_show(wall_object_list[4], 0, 0, 0, 0.05, 0)

    for wall_object in wall_object_list:
        assert wall_object['id'].startswith('fuse_wall_')
        assert wall_object['type'] == 'cube'
        assert wall_object['materials'] == ['Custom/Materials/Lime']
        assert wall_object['kinematic']
        assert wall_object['structure']
        assert wall_object['debug']['info'] == [
            'lime', 'green', 'cube', 'lime green cube'
        ]
        assert wall_object['debug']['configHeight'] == [0.05, 0.1]
        assert wall_object['debug']['configSize'] == [0.495, 0.495]

        assert len(wall_object['shows']) == 1
        assert wall_object['shows'][0]['scale']['x'] == 0.495
        assert wall_object['shows'][0]['scale']['y'] == 0.1
        assert wall_object['shows'][0]['scale']['z'] == 0.495

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
    verify_show(wall_object_list[5], 0, 7, -1.25, 0.05, -1.25)
    verify_show(wall_object_list[6], 0, 7, 1.25, 0.05, 1.25)
    verify_show(wall_object_list[7], 0, 7, 0, 0.05, 0)
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


def wrap_create_bounds(dimensions, offset, position, rotation, standing_y):
    bounds = geometry.create_bounds(
        dimensions=dimensions,
        offset=offset,
        position=position,
        rotation=rotation,
        standing_y=standing_y
    )
    return TrueObjectBounds(bounds=bounds, true_poly=bounds.polygon_xz)


def test_blobs():
    assert len(AGENT_OBJECT_CONFIG_LIST) > 1
    for config in AGENT_OBJECT_CONFIG_LIST:
        dimensions = OBJECT_DIMENSIONS[config.object_type]
        assert round(dimensions.x * config.scale_xz, 4) <= 1.0
        assert round(dimensions.z * config.scale_xz, 4) <= 1.0


def test_materials():
    # Multi-goal scenes must have one or more goal object colors for any
    # possible combination of agent colors.
    # Assume such scenes will only ever have one agent.
    for agent_material in AGENT_OBJECT_MATERIAL_LIST:
        goal_1_materials = materials.filter_used_colors(
            GOAL_OBJECT_MATERIAL_LIST,
            [agent_material]
        )
        for goal_1_material in goal_1_materials:
            goal_2_materials = materials.filter_used_colors(
                GOAL_OBJECT_MATERIAL_LIST,
                [agent_material, goal_1_material]
            )
            assert len(goal_2_materials) > 1
            for goal_2_material in goal_2_materials:
                goal_3_materials = materials.filter_used_colors(
                    GOAL_OBJECT_MATERIAL_LIST,
                    [agent_material, goal_1_material, goal_2_material]
                )
                assert len(goal_3_materials) >= 1

    # Multi-agent scenes must have one or more goal object colors for any
    # possible combination of agent colors.
    # Assume such scenes will only ever have one or two goal objects.
    for agent_1_material in AGENT_OBJECT_MATERIAL_LIST:
        agent_2_materials = materials.filter_used_colors(
            AGENT_OBJECT_MATERIAL_LIST,
            [agent_1_material]
        )
        for agent_2_material in agent_2_materials:
            goal_1_materials = materials.filter_used_colors(
                GOAL_OBJECT_MATERIAL_LIST,
                [agent_1_material, agent_2_material]
            )
            for goal_1_material in goal_1_materials:
                goal_2_materials = materials.filter_used_colors(
                    GOAL_OBJECT_MATERIAL_LIST,
                    [agent_1_material, agent_2_material, goal_1_material]
                )
                assert len(goal_2_materials) >= 1


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


def test_append_each_show_to_object_imitated_agent():
    object_1 = {
        'type': 'cube',
        'debug': {
            'boundsAtStep': [],
            'configHeight': [0.25, 0.5],
            'configSize': [0.4, 0.4]
        },
        'shows': []
    }
    object_2 = {
        'type': 'sphere',
        'debug': {
            'boundsAtStep': [],
            'configHeight': [0.25, 0.5],
            'configSize': [0.6, 0.6]
        },
        'shows': []
    }

    trial = [{
        'other_agents': [[[5, 5], 5], [[95, 95], 5]]
    }, {
        'other_agents': [[[95, 95], 5], [[185, 185], 5]]
    }]

    result_1 = _append_each_show_to_object(
        object_1,
        trial,
        1,
        'other_agents',
        UNIT_SIZE,
        json_index=0
    )
    assert result_1 == object_1
    assert len(result_1['debug']['boundsAtStep']) == 3
    verify_bounds(result_1, 0, -2.05, -2.45, -2.05, -2.45)
    verify_bounds(result_1, 1, 0.2, -0.2, 0.2, -0.2)
    verify_bounds(result_1, 2, 0.2, -0.2, 0.2, -0.2)
    assert len(result_1['shows']) == 2
    assert result_1['shows'][0]['stepBegin'] == 1
    assert result_1['shows'][0]['position'] == {
        'x': -2.25, 'y': 0.25, 'z': -2.25
    }
    assert result_1['shows'][0]['scale'] == {'x': 0.4, 'y': 0.5, 'z': 0.4}
    assert result_1['shows'][0]['boundingBox']
    assert result_1['shows'][1]['stepBegin'] == 2
    assert result_1['shows'][1]['position'] == {'x': 0, 'y': 0.25, 'z': 0}
    assert 'scale' not in result_1['shows'][1]
    assert result_1['shows'][1]['boundingBox']

    result_2 = _append_each_show_to_object(
        object_2,
        trial,
        1,
        'other_agents',
        UNIT_SIZE,
        json_index=1
    )
    assert result_2 == object_2
    assert len(result_2['debug']['boundsAtStep']) == 3
    verify_bounds(result_2, 0, 0.3, -0.3, 0.3, -0.3)
    verify_bounds(result_2, 1, 2.55, 1.95, 2.55, 1.95)
    assert len(result_2['shows']) == 2
    assert result_2['shows'][0]['stepBegin'] == 1
    assert result_2['shows'][0]['position'] == {'x': 0, 'y': 0.25, 'z': 0}
    assert result_2['shows'][0]['scale'] == {'x': 0.6, 'y': 0.5, 'z': 0.6}
    assert result_2['shows'][0]['boundingBox']
    assert result_2['shows'][1]['stepBegin'] == 2
    assert result_2['shows'][1]['position'] == {
        'x': 2.25, 'y': 0.25, 'z': 2.25
    }
    assert 'scale' not in result_2['shows'][1]
    assert result_2['shows'][1]['boundingBox']


def test_append_each_show_to_object_paddle():
    mcs_object = {
        'type': 'cube',
        'debug': {
            'boundsAtStep': [],
            'configHeight': [0.5, 1.0],
            'configSize': [0.25, 1.0]
        },
        'shows': []
    }

    # The 'agent' property does not have nested lists.
    trial = [{
        'paddle': [[100, 100], [10, 40], 15]
    }, {
        'paddle': [[100, 100], [10, 40], 20]
    }, {
        'paddle': [[100, 100], [10, 40], 25]
    }, {
        'paddle': [[100, 100], [10, 40], 30]
    }]
    result = _append_each_show_to_object(
        mcs_object,
        trial,
        1,
        'paddle',
        UNIT_SIZE
    )
    assert result == mcs_object
    bounds_at_step = result['debug']['boundsAtStep']
    assert len(bounds_at_step) == 5
    for index, bounds in enumerate(bounds_at_step):
        assert bounds
        if index < (len(bounds_at_step) - 2):
            assert bounds != bounds_at_step[index + 1]
    assert len(result['shows']) == 4
    assert result['shows'][0]['stepBegin'] == 1
    assert result['shows'][0]['position'] == {'x': 0, 'y': 0.5, 'z': 0}
    assert result['shows'][0]['rotation'] == {'x': 0, 'y': 345, 'z': 0}
    assert result['shows'][0]['scale'] == {'x': 0.25, 'y': 1.0, 'z': 1.0}
    assert result['shows'][0]['boundingBox'] == bounds_at_step[0]
    assert result['shows'][1]['stepBegin'] == 2
    assert result['shows'][1]['position'] == {'x': 0, 'y': 0.5, 'z': 0}
    assert result['shows'][1]['rotation'] == {'x': 0, 'y': 340, 'z': 0}
    assert 'scale' not in result['shows'][1]
    assert result['shows'][1]['boundingBox'] == bounds_at_step[1]
    assert result['shows'][2]['stepBegin'] == 3
    assert result['shows'][2]['position'] == {'x': 0, 'y': 0.5, 'z': 0}
    assert result['shows'][2]['rotation'] == {'x': 0, 'y': 335, 'z': 0}
    assert 'scale' not in result['shows'][2]
    assert result['shows'][2]['boundingBox'] == bounds_at_step[2]
    assert result['shows'][3]['stepBegin'] == 4
    assert result['shows'][3]['position'] == {'x': 0, 'y': 0.5, 'z': 0}
    assert result['shows'][3]['rotation'] == {'x': 0, 'y': 330, 'z': 0}
    assert 'scale' not in result['shows'][3]
    assert result['shows'][3]['boundingBox'] == bounds_at_step[3]


def test_choose_config_list_with_agent():
    config_object_type_list = ['blob_a', 'blob_b', 'blob_c', 'blob_d']
    config_list = [
        ObjectConfig(object_type, index, index)
        for index, object_type in enumerate(config_object_type_list)
    ]
    material_list = [
        MaterialTuple('Custom/Materials/Cyan', ['cyan']),
        MaterialTuple('Custom/Materials/Grey', ['grey']),
        MaterialTuple('Custom/Materials/Magenta', ['magenta']),
        MaterialTuple('Custom/Materials/Yellow', ['yellow'])
    ]

    trial_list = [[{
        'agent': []
    }]]
    chosen_config_list = _choose_config_list(
        trial_list,
        config_list,
        [None, None, None],
        material_list,
        'agent',
        [],
        []
    )
    assert len(chosen_config_list) == 2
    assert chosen_config_list[0].object_type in config_object_type_list
    assert chosen_config_list[0].material in material_list


def test_choose_config_list_with_agent_in_instrumental_action_task():
    config_object_type_list = ['cone', 'pyramid', 'blob_a', 'blob_b', 'blob_c']
    config_list = [
        ObjectConfig(object_type, index, index)
        for index, object_type in enumerate(config_object_type_list)
    ]
    material_list = [
        MaterialTuple('Custom/Materials/Cyan', ['cyan']),
        MaterialTuple('Custom/Materials/Grey', ['grey']),
        MaterialTuple('Custom/Materials/Magenta', ['magenta']),
        MaterialTuple('Custom/Materials/Yellow', ['yellow'])
    ]

    trial_list = [[{
        'agent': [],
        'key': True
    }]]
    chosen_config_list = _choose_config_list(
        trial_list,
        config_list,
        [None, None, None],
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
    config_object_type_list = ['cube', 'cylinder', 'hash', 'sphere']
    config_list = [
        ObjectConfig(object_type, index, index)
        for index, object_type in enumerate(config_object_type_list)
    ]
    material_list = [
        MaterialTuple('Custom/Materials/Cyan', ['cyan']),
        MaterialTuple('Custom/Materials/Grey', ['grey']),
        MaterialTuple('Custom/Materials/Magenta', ['magenta']),
        MaterialTuple('Custom/Materials/Yellow', ['yellow'])
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


def test_choose_config_list_no_types_same_as_used_types():
    mock_config_object_type_list = ['cube', 'cylinder', 'hash', 'sphere']
    mock_config_list = [
        ObjectConfig(object_type, index, index)
        for index, object_type in enumerate(mock_config_object_type_list)
    ]
    material_list = [
        MaterialTuple('Custom/Materials/Cyan', ['cyan']),
        MaterialTuple('Custom/Materials/Grey', ['grey']),
        MaterialTuple('Custom/Materials/Magenta', ['magenta']),
        MaterialTuple('Custom/Materials/Yellow', ['yellow'])
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
        ['cube', 'cylinder', 'hash'],
        []
    )
    assert len(chosen_config_list) == 1
    assert chosen_config_list[0].object_type == 'sphere'


def test_choose_config_list_no_types_same_as_used_types_multiple():
    mock_config_object_type_list = ['cube', 'cylinder', 'hash', 'sphere']
    mock_config_list = [
        ObjectConfig(object_type, index, index)
        for index, object_type in enumerate(mock_config_object_type_list)
    ]
    material_list = [
        MaterialTuple('Custom/Materials/Cyan', ['cyan']),
        MaterialTuple('Custom/Materials/Grey', ['grey']),
        MaterialTuple('Custom/Materials/Magenta', ['magenta']),
        MaterialTuple('Custom/Materials/Yellow', ['yellow'])
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
            ['cube', 'cylinder', 'hash'],
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
            AgentConfig('cube', 1, rotation_y=0),
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
    assert agent_object['physics']
    assert not agent_object.get('structure')
    assert agent_object['debug']['info'] == [
        'test_color_a', 'test_color_b', 'cube',
        'test_color_a test_color_b cube'
    ]
    assert agent_object['debug']['configHeight'] == [0.125, 0.25]
    assert agent_object['debug']['configSize'] == [0.25, 0.25]

    assert len(agent_object.get('hides', [])) == 0
    assert len(agent_object['shows']) == 10
    verify_show(agent_object, 0, 0, -1.75, 0.125, -1.75)
    assert agent_object['shows'][0]['rotation']['y'] == 0
    assert agent_object['shows'][0]['scale']['x'] == 0.25
    assert agent_object['shows'][0]['scale']['y'] == 0.25
    assert agent_object['shows'][0]['scale']['z'] == 0.25

    verify_show(agent_object, 1, 1, -1.625, 0.125, -1.625)
    verify_show(agent_object, 2, 2, -1.5, 0.125, -1.5)
    verify_show(agent_object, 3, 4, 0, 0.125, 0)
    verify_show(agent_object, 4, 5, 0, 0.125, 0.125)
    verify_show(agent_object, 5, 6, 0, 0.125, 0.25)
    verify_show(agent_object, 6, 7, 0, 0.125, 0.375)
    verify_show(agent_object, 7, 9, 1.75, 0.125, 1.75)
    verify_show(agent_object, 8, 10, 1.625, 0.125, 1.75)
    verify_show(agent_object, 9, 11, 1.5, 0.125, 1.75)

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


def test_create_agent_object_list_rotation_y():
    trial_list = [[{
        'agent': [[25, 25], 5, 'agent_1']
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            AgentConfig('cube', 1),
            MaterialTuple('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    # Test the randomly chosen Y rotation multiple times.
    for _ in range(10):
        agent_object_list = _create_agent_object_list(
            trial_list,
            object_config_with_material_list,
            UNIT_SIZE
        )
        assert len(agent_object_list) == 1
        agent_object = agent_object_list[0]
        rotation_y = agent_object['shows'][0]['rotation']['y']
        assert rotation_y in [0, 90, 180, 270]
        for show in agent_object['shows']:
            assert show['rotation']['y'] == rotation_y


def test_create_agent_object_list_hide_in_some_trials():
    trial_list = [[{
        'agent': [[25, 25], 5, 'agent_1']
    }], [{
        'agent': [[95, 95], 5, 'agent_1']
    }], [{
        'agent': [[95, 95], 5, 'agent_2']
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            AgentConfig('cube', 1),
            MaterialTuple('test_material_1', ['test_color_a'])
        ),
        ObjectConfigWithMaterial(
            AgentConfig('sphere', 1),
            MaterialTuple('test_material_2', ['test_color_b'])
        )
    ]

    agent_object_list = _create_agent_object_list(
        trial_list,
        object_config_with_material_list,
        UNIT_SIZE
    )

    assert len(agent_object_list) == 2
    agent_object_1 = agent_object_list[0]
    agent_object_2 = agent_object_list[1]

    assert agent_object_1['id'].startswith('agent_')
    assert agent_object_1['type'] == 'cube'
    assert agent_object_1['materials'] == ['test_material_1']
    assert agent_object_1['kinematic']
    assert agent_object_1['physics']
    assert not agent_object_1.get('structure')
    assert agent_object_1['debug']['configHeight'] == [0.125, 0.25]
    assert agent_object_1['debug']['configSize'] == [0.25, 0.25]

    assert len(agent_object_1['hides']) == 1
    assert agent_object_1['hides'][0]['stepBegin'] == 4
    assert len(agent_object_1['shows']) == 2
    verify_show(agent_object_1, 0, 0, -1.75, 0.125, -1.75)
    assert agent_object_1['shows'][0]['rotation']['y'] == 0
    assert agent_object_1['shows'][0]['scale']['x'] == 0.25
    assert agent_object_1['shows'][0]['scale']['y'] == 0.25
    assert agent_object_1['shows'][0]['scale']['z'] == 0.25
    verify_show(agent_object_1, 1, 2, 0, 0.125, 0)

    assert len(agent_object_1['debug']['boundsAtStep']) == 6
    verify_bounds(agent_object_1, 0, -1.625, -1.875, -1.625, -1.875)
    verify_bounds(agent_object_1, 1, -1.625, -1.875, -1.625, -1.875)
    verify_bounds(agent_object_1, 2, 0.125, -0.125, 0.125, -0.125)
    verify_bounds(agent_object_1, 3, 0.125, -0.125, 0.125, -0.125)
    assert agent_object_1['debug']['boundsAtStep'][4] is None
    assert agent_object_1['debug']['boundsAtStep'][5] is None

    assert agent_object_2['id'].startswith('agent_')
    assert agent_object_2['type'] == 'sphere'
    assert agent_object_2['materials'] == ['test_material_2']
    assert agent_object_2['kinematic']
    assert agent_object_2['physics']
    assert not agent_object_2.get('structure')
    assert agent_object_2['debug']['configHeight'] == [0.125, 0.25]
    assert agent_object_2['debug']['configSize'] == [0.25, 0.25]

    assert len(agent_object_2['hides']) == 2
    assert agent_object_2['hides'][0]['stepBegin'] == 0
    assert agent_object_2['hides'][1]['stepBegin'] == 2
    assert len(agent_object_2['shows']) == 1
    verify_show(agent_object_2, 0, 4, 0, 0.125, 0)
    assert agent_object_2['shows'][0]['rotation']['y'] == 0
    assert agent_object_2['shows'][0]['scale']['x'] == 0.25
    assert agent_object_2['shows'][0]['scale']['y'] == 0.25
    assert agent_object_2['shows'][0]['scale']['z'] == 0.25

    assert len(agent_object_2['debug']['boundsAtStep']) == 6
    assert agent_object_2['debug']['boundsAtStep'][0] is None
    assert agent_object_2['debug']['boundsAtStep'][1] is None
    assert agent_object_2['debug']['boundsAtStep'][2] is None
    assert agent_object_2['debug']['boundsAtStep'][3] is None
    verify_bounds(agent_object_2, 4, 0.125, -0.125, 0.125, -0.125)
    verify_bounds(agent_object_2, 5, 0.125, -0.125, 0.125, -0.125)


def test_create_agent_object_list_imitated_agents():
    trial_list = [[{
        'agent': [[25, 25], 5, 'agent_1'],
        'other_agents': [
            [[30, 30], 5, 'agent_2'],
            [[35, 35], 5, 'agent_3']
        ]
    }], [{
        'agent': [[95, 95], 5, 'agent_1'],
        'other_agents': [
            [[95, 105], 5, 'agent_2'],
            [[165, 165], 5, 'agent_3']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            AgentConfig('cube', 1),
            MaterialTuple('test_material_1', ['test_color_a'])
        ),
        ObjectConfigWithMaterial(
            AgentConfig('sphere', 1),
            MaterialTuple('test_material_2', ['test_color_b'])
        ),
        ObjectConfigWithMaterial(
            AgentConfig('tube_wide', 1),
            MaterialTuple('test_material_3', ['test_color_c'])
        )
    ]

    agent_object_list = _create_agent_object_list(
        trial_list,
        object_config_with_material_list,
        UNIT_SIZE
    )

    assert len(agent_object_list) == 3
    agent_object_1 = agent_object_list[0]
    agent_object_2 = agent_object_list[1]
    agent_object_3 = agent_object_list[2]

    assert agent_object_1['id'].startswith('agent_')
    assert agent_object_1['type'] == 'cube'
    assert agent_object_1['materials'] == ['test_material_1']
    assert agent_object_1['kinematic']
    assert agent_object_1['physics']
    assert not agent_object_1.get('structure')
    assert agent_object_1['debug']['configHeight'] == [0.125, 0.25]
    assert agent_object_1['debug']['configSize'] == [0.25, 0.25]

    assert len(agent_object_1.get('hides', [])) == 0
    assert len(agent_object_1['shows']) == 2
    verify_show(agent_object_1, 0, 0, -1.75, 0.125, -1.75)
    assert agent_object_1['shows'][0]['rotation']['y'] == 0
    assert agent_object_1['shows'][0]['scale']['x'] == 0.25
    assert agent_object_1['shows'][0]['scale']['y'] == 0.25
    assert agent_object_1['shows'][0]['scale']['z'] == 0.25
    verify_show(agent_object_1, 1, 2, 0, 0.125, 0)

    assert len(agent_object_1['debug']['boundsAtStep']) == 4
    verify_bounds(agent_object_1, 0, -1.625, -1.875, -1.625, -1.875)
    verify_bounds(agent_object_1, 1, -1.625, -1.875, -1.625, -1.875)
    verify_bounds(agent_object_1, 2, 0.125, -0.125, 0.125, -0.125)
    verify_bounds(agent_object_1, 3, 0.125, -0.125, 0.125, -0.125)

    assert agent_object_2['id'].startswith('other_agents_')
    assert agent_object_2['type'] == 'sphere'
    assert agent_object_2['materials'] == ['test_material_2']
    assert agent_object_2['kinematic']
    assert agent_object_2['physics']
    assert not agent_object_2.get('structure')
    assert agent_object_2['debug']['configHeight'] == [0.125, 0.25]
    assert agent_object_2['debug']['configSize'] == [0.25, 0.25]

    assert len(agent_object_2.get('hides', [])) == 0
    assert len(agent_object_2['shows']) == 2
    verify_show(agent_object_2, 0, 0, -1.625, 0.125, -1.625)
    assert agent_object_2['shows'][0]['rotation']['y'] == 0
    assert agent_object_2['shows'][0]['scale']['x'] == 0.25
    assert agent_object_2['shows'][0]['scale']['y'] == 0.25
    assert agent_object_2['shows'][0]['scale']['z'] == 0.25
    verify_show(agent_object_2, 1, 2, 0, 0.125, 0.25)

    assert len(agent_object_2['debug']['boundsAtStep']) == 4
    verify_bounds(agent_object_2, 0, -1.5, -1.75, -1.5, -1.75)
    verify_bounds(agent_object_2, 1, -1.5, -1.75, -1.5, -1.75)
    verify_bounds(agent_object_2, 2, 0.125, -0.125, 0.375, 0.125)
    verify_bounds(agent_object_2, 3, 0.125, -0.125, 0.375, 0.125)

    assert agent_object_3['id'].startswith('other_agents_')
    assert agent_object_3['type'] == 'tube_wide'
    assert agent_object_3['materials'] == ['test_material_3']
    assert agent_object_3['kinematic']
    assert agent_object_3['physics']
    assert not agent_object_3.get('structure')
    assert agent_object_3['debug']['configHeight'] == [0.125, 0.25]
    assert agent_object_3['debug']['configSize'] == [0.25, 0.25]

    assert len(agent_object_3.get('hides', [])) == 0
    assert len(agent_object_3['shows']) == 2
    verify_show(agent_object_3, 0, 0, -1.5, 0.125, -1.5)
    assert agent_object_3['shows'][0]['rotation']['y'] == 0
    assert agent_object_3['shows'][0]['scale']['x'] == 0.25
    assert agent_object_3['shows'][0]['scale']['y'] == 0.25
    assert agent_object_3['shows'][0]['scale']['z'] == 0.25
    verify_show(agent_object_3, 1, 2, 1.75, 0.125, 1.75)

    assert len(agent_object_3['debug']['boundsAtStep']) == 4
    verify_bounds(agent_object_3, 0, -1.375, -1.625, -1.375, -1.625)
    verify_bounds(agent_object_3, 1, -1.375, -1.625, -1.375, -1.625)
    verify_bounds(agent_object_3, 2, 1.875, 1.625, 1.875, 1.625)
    verify_bounds(agent_object_3, 3, 1.875, 1.625, 1.875, 1.625)


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
            [[25, 25], 5, 'obj_1', 'purple']
        ]
    }], [{
        'objects': [
            [[95, 95], 5, 'obj_1', 'purple']
        ]
    }], [{
        'objects': [
            [[165, 165], 5, 'obj_1', 'purple']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 1, 2),
            MaterialTuple('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=10, y=0, z=10), Vector3d(x=10, y=0, z=12),
        Vector3d(x=12, y=0, z=12), Vector3d(x=12, y=0, z=10)
    ], max_y=0, min_y=0)
    mock_agent_start_bounds = TrueObjectBounds(
        bounds=mock_agent_start_bounds,
        true_poly=mock_agent_start_bounds.polygon_xz
    )

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
    assert goal_object_1['physics']
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
            [[25, 165], 5, 'obj_1', 'yellow'],
            [[160, 20], 10, 'obj_2', 'purple']
        ]
    }], [{
        'objects': [
            [[90, 100], 5, 'obj_1', 'yellow'],
            [[95, 85], 10, 'obj_2', 'purple']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 1, 2),
            MaterialTuple('test_material_1', ['test_color_a', 'test_color_b'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('sphere', 5, 6),
            MaterialTuple('test_material_2', ['test_color_c'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=10, y=0, z=10), Vector3d(x=10, y=0, z=12),
        Vector3d(x=12, y=0, z=12), Vector3d(x=12, y=0, z=10)
    ], max_y=0, min_y=0)
    mock_agent_start_bounds = TrueObjectBounds(
        bounds=mock_agent_start_bounds,
        true_poly=mock_agent_start_bounds.polygon_xz
    )

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
    assert goal_object_1['physics']
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
    assert goal_object_2['physics']
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
            [[25, 165], 5, 'obj_1', 'yellow'],
            [[160, 20], 10, 'obj_2', 'purple']
        ]
    }], [{
        'objects': [
            [[90, 100], 5, 'obj_2', 'purple'],
            [[95, 85], 10, 'obj_1', 'yellow']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 1, 2),
            MaterialTuple('test_material_1', ['test_color_a', 'test_color_b'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('sphere', 5, 6),
            MaterialTuple('test_material_2', ['test_color_c'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=10, y=0, z=10), Vector3d(x=10, y=0, z=12),
        Vector3d(x=12, y=0, z=12), Vector3d(x=12, y=0, z=10)
    ], max_y=0, min_y=0)
    mock_agent_start_bounds = TrueObjectBounds(
        bounds=mock_agent_start_bounds,
        true_poly=mock_agent_start_bounds.polygon_xz
    )

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
    assert goal_object_1['physics']
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
    assert goal_object_2['physics']
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
            [[20, 20], 5, 'obj_1', 'purple']
        ]
    }], [{
        'objects': [
            [[90, 90], 5, 'obj_1', 'purple']
        ]
    }], [{
        'objects': [
            [[160, 160], 5, 'obj_1', 'purple']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 0.125, 0.25),
            MaterialTuple('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=-0.25, y=0, z=-0.25), Vector3d(x=-0.25, y=0, z=0.25),
        Vector3d(x=0.25, y=0, z=0.25), Vector3d(x=0.25, y=0, z=-0.25)
    ], max_y=0, min_y=0)
    agent_start_bounds = TrueObjectBounds(
        bounds=agent_start_bounds,
        true_poly=agent_start_bounds.polygon_xz
    )

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
            [[20, 20], 5, 'obj_1', 'yellow'],
            [[100, 100], 5, 'obj_2', 'purple']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 0.125, 0.25),
            MaterialTuple('test_material_1', ['test_color_a', 'test_color_b'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('sphere', 0.125, 0.25),
            MaterialTuple('test_material_2', ['test_color_c'])
        )
    ]

    agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=-0.25, y=0, z=-0.25), Vector3d(x=-0.25, y=0, z=0.25),
        Vector3d(x=0.25, y=0, z=0.25), Vector3d(x=0.25, y=0, z=-0.25)
    ], max_y=0, min_y=0)
    agent_start_bounds = TrueObjectBounds(
        bounds=agent_start_bounds,
        true_poly=agent_start_bounds.polygon_xz
    )

    with pytest.raises(exceptions.SceneException):
        _create_goal_object_list(
            trial_list,
            object_config_with_material_list,
            agent_start_bounds,
            'filename',
            UNIT_SIZE
        )


def test_create_goal_object_list_object_hide_in_final_trial():
    trial_list = [[{
        'objects': [
            [[25, 25], 5, 'obj_1', 'purple']
        ]
    }], [{
        'objects': [
            [[95, 95], 5, 'obj_1', 'purple']
        ]
    }], [{
        'objects': []
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 1, 2),
            MaterialTuple('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=10, y=0, z=10), Vector3d(x=10, y=0, z=12),
        Vector3d(x=12, y=0, z=12), Vector3d(x=12, y=0, z=10)
    ], max_y=0, min_y=0)
    mock_agent_start_bounds = TrueObjectBounds(
        bounds=mock_agent_start_bounds,
        true_poly=mock_agent_start_bounds.polygon_xz
    )

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
    assert goal_object_1['physics']
    assert not goal_object_1.get('structure')
    assert goal_object_1['debug']['info'] == [
        'test_color_a', 'test_color_b', 'cube',
        'test_color_a test_color_b cube'
    ]
    assert goal_object_1['debug']['configHeight'] == [0.25, 0.5]
    assert goal_object_1['debug']['configSize'] == [0.25, 0.25]

    assert len(goal_object_1['shows']) == 2
    verify_show(goal_object_1, 0, 0, -1.75, 0.25, -1.75)
    assert goal_object_1['shows'][0]['scale']['x'] == 0.25
    assert goal_object_1['shows'][0]['scale']['y'] == 0.5
    assert goal_object_1['shows'][0]['scale']['z'] == 0.25

    verify_show(goal_object_1, 1, 2, 0, 0.25, 0)

    assert len(goal_object_1['debug']['boundsAtStep']) == 6
    verify_bounds(goal_object_1, 0, -1.625, -1.875, -1.625, -1.875)
    verify_bounds(goal_object_1, 1, -1.625, -1.875, -1.625, -1.875)
    verify_bounds(goal_object_1, 2, 0.125, -0.125, 0.125, -0.125)
    verify_bounds(goal_object_1, 3, 0.125, -0.125, 0.125, -0.125)
    assert goal_object_1['debug']['boundsAtStep'][4] is None
    assert goal_object_1['debug']['boundsAtStep'][5] is None

    assert len(goal_object_1['hides']) == 1
    assert goal_object_1['hides'][0]['stepBegin'] == 4


def test_create_goal_object_list_object_show_in_final_trial():
    trial_list = [[{
        'objects': []
    }], [{
        'objects': []
    }], [{
        'objects': [
            [[165, 165], 5, 'obj_1', 'purple']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 1, 2),
            MaterialTuple('test_material', ['test_color_a', 'test_color_b'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=10, y=0, z=10), Vector3d(x=10, y=0, z=12),
        Vector3d(x=12, y=0, z=12), Vector3d(x=12, y=0, z=10)
    ], max_y=0, min_y=0)
    mock_agent_start_bounds = TrueObjectBounds(
        bounds=mock_agent_start_bounds,
        true_poly=mock_agent_start_bounds.polygon_xz
    )

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
    assert goal_object_1['physics']
    assert not goal_object_1.get('structure')
    assert goal_object_1['debug']['info'] == [
        'test_color_a', 'test_color_b', 'cube',
        'test_color_a test_color_b cube'
    ]
    assert goal_object_1['debug']['configHeight'] == [0.25, 0.5]
    assert goal_object_1['debug']['configSize'] == [0.25, 0.25]

    assert len(goal_object_1['shows']) == 1
    verify_show(goal_object_1, 0, 4, 1.75, 0.25, 1.75)
    assert goal_object_1['shows'][0]['scale']['x'] == 0.25
    assert goal_object_1['shows'][0]['scale']['y'] == 0.5
    assert goal_object_1['shows'][0]['scale']['z'] == 0.25

    assert len(goal_object_1['debug']['boundsAtStep']) == 6
    assert goal_object_1['debug']['boundsAtStep'][0] is None
    assert goal_object_1['debug']['boundsAtStep'][1] is None
    assert goal_object_1['debug']['boundsAtStep'][2] is None
    assert goal_object_1['debug']['boundsAtStep'][3] is None
    verify_bounds(goal_object_1, 4, 1.875, 1.625, 1.875, 1.625)
    verify_bounds(goal_object_1, 5, 1.875, 1.625, 1.875, 1.625)


def test_create_goal_object_list_agent_touches():
    trial_list = [[{
        'objects': [
            [[25, 165], 5, 'obj_1', 'yellow'],
            [[160, 20], 10, 'obj_2', 'purple']
        ]
    }, {
        'objects': [
            [[25, 165], 5, 'obj_1', 'yellow'],
            [[160, 20], 10, 'obj_2', 'purple']
        ]
    }, {
        'objects': [
            [[90, 100], 5, 'obj_1', 'red'],
            [[95, 85], 10, 'obj_2', 'red']
        ]
    }], [{
        'objects': [
            [[90, 100], 5, 'obj_1', 'yellow'],
            [[95, 85], 10, 'obj_2', 'purple']
        ]
    }, {
        'objects': [
            [[90, 100], 5, 'obj_1', 'yellow'],
            [[95, 85], 10, 'obj_2', 'purple']
        ]
    }, {
        'objects': [
            [[90, 100], 5, 'obj_1', 'yellow'],
            [[95, 85], 10, 'obj_2', 'purple']
        ]
    }, {
        'objects': [
            [[90, 100], 5, 'obj_1', 'yellow'],
            [[95, 85], 10, 'obj_2', 'purple']
        ]
    }, {
        'objects': [
            [[90, 100], 5, 'obj_1', 'red'],
            [[95, 85], 10, 'obj_2', 'red']
        ]
    }]]

    object_config_with_material_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 1, 2),
            MaterialTuple('test_material_1', ['test_color_a', 'test_color_b'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('sphere', 5, 6),
            MaterialTuple('test_material_2', ['test_color_c'])
        )
    ]

    # We're not testing this right now, so just use a silly value.
    mock_agent_start_bounds = ObjectBounds(box_xz=[
        Vector3d(x=10, y=0, z=10), Vector3d(x=10, y=0, z=12),
        Vector3d(x=12, y=0, z=12), Vector3d(x=12, y=0, z=10)
    ], max_y=0, min_y=0)
    mock_agent_start_bounds = TrueObjectBounds(
        bounds=mock_agent_start_bounds,
        true_poly=mock_agent_start_bounds.polygon_xz
    )

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
    assert goal_object_1['debug']['agentTouches'] == {0: [2], 1: [8]}
    assert goal_object_2['debug']['agentTouches'] == {0: [2], 1: [8]}


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
    assert home_object['debug']['info'] == [
        'magenta', 'purple', 'red', 'cube', 'magenta purple red cube'
    ]
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
    assert home_object['debug']['info'] == [
        'magenta', 'purple', 'red', 'cube', 'magenta purple red cube'
    ]
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
    verify_show(key_object, 0, 0, 0.25, 0.05, 0)
    assert key_object['shows'][0]['rotation']['y'] == -135

    # negative_z
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle90.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)
    assert len(key_object['shows']) == 1
    verify_key_properties(key_object)
    verify_show(key_object, 0, 0, 0, 0.05, 0.25)
    assert key_object['shows'][0]['rotation']['y'] == 135

    # positive_x
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle180.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)
    assert len(key_object['shows']) == 1
    verify_key_properties(key_object)
    verify_show(key_object, 0, 0, -0.25, 0.05, 0)
    assert key_object['shows'][0]['rotation']['y'] == 45

    # positive_z
    trial_list = [[{
        'key': [[[90, 90], 10, 'triangle270.png']]
    }]]

    key_object = _create_key_object(trial_list, UNIT_SIZE, 0.5)
    assert len(key_object['shows']) == 1
    verify_key_properties(key_object)
    verify_show(key_object, 0, 0, 0, 0.05, -0.25)
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
        verify_show(key_object, i, i, 0.25, 0.05, 0)

    verify_show(key_object, 5, 5, 0.25, 0.55, -0.125)
    verify_show(key_object, 6, 6, 0.25, 0.55, -0.25)
    verify_show(key_object, 7, 7, 0.25, 0.55, -0.375)
    verify_show(key_object, 8, 8, 0.25, 0.55, -0.5)
    verify_show(key_object, 9, 9, 0.25, 0.55, -0.625)

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
        verify_show(key_object, i, i, 0.25, 0.05, 0)

    verify_show(key_object, 5, 5, 0.25, 0.55, -0.125)
    verify_show(key_object, 6, 6, 0, 0.55, -0.25 + 0.25)
    verify_show(key_object, 7, 7, 0, 0.55, -0.375 + 0.25)
    verify_show(key_object, 8, 8, -0.25, 0.55, -0.5)
    verify_show(key_object, 9, 9, -0.25, 0.55, -0.625)

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

    verify_show(key_object, 0, 0, 0.25, 0.05, 0)
    verify_show(key_object, 1, 1, 0.25, 0.05, 0)
    verify_show(key_object, 2, 2, 0.25, 0.55, -0.125)
    verify_show(key_object, 3, 3, 0.25, 0.55, -0.25)
    verify_show(key_object, 4, 5, 2, 0.05, -1.75)
    verify_show(key_object, 5, 6, 1.875, 0.55, -1.75)
    verify_show(key_object, 6, 8, -1.75, 0.05, 2)
    verify_show(key_object, 7, 9, -1.75, 0.05, 2)
    verify_show(key_object, 8, 10, -1.625, 0.55, 2)
    verify_show(key_object, 9, 11, -1.5, 0.55, 2)

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
    verify_show(key_object, 0, 0, 0.25, 0.05, 0)
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

    verify_show(key_object, 0, 0, 0.25, 0.05, 0)
    verify_show(key_object, 1, 1, 0.25, 0.05, 0)
    verify_show(key_object, 2, 8, -1.75, 0.05, 2)
    verify_show(key_object, 3, 9, -1.75, 0.05, 2)

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
    verify_show(lock_object_list[0], 0, 0, 0, 0.05, 0)
    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 90

    trial_list = [[{
        'lock': [[[90, 90], 10, 'slot90.png']]
    }]]
    lock_object_list = _create_lock_wall_object_list(trial_list, {}, UNIT_SIZE)
    assert len(lock_object_list) == 1
    verify_lock_properties(lock_object_list[0])
    verify_show(lock_object_list[0], 0, 0, 0, 0.05, 0)
    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 0

    trial_list = [[{
        'lock': [[[90, 90], 10, 'slot180.png']]
    }]]
    lock_object_list = _create_lock_wall_object_list(trial_list, {}, UNIT_SIZE)
    assert len(lock_object_list) == 1
    verify_lock_properties(lock_object_list[0])
    verify_show(lock_object_list[0], 0, 0, 0, 0.05, 0)
    assert lock_object_list[0]['shows'][0]['rotation']['y'] == 270

    trial_list = [[{
        'lock': [[[90, 90], 10, 'slot270.png']]
    }]]
    lock_object_list = _create_lock_wall_object_list(trial_list, {}, UNIT_SIZE)
    assert len(lock_object_list) == 1
    verify_lock_properties(lock_object_list[0])
    verify_show(lock_object_list[0], 0, 0, 0, 0.05, 0)
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
    verify_show(lock_object_list[0], 0, 0, 0, 0.05, 0)
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

    verify_show(lock_object_list[0], 0, 0, 0, 0.05, 0)
    verify_show(lock_object_list[1], 0, 2, 0, 0.05, 0)
    verify_show(lock_object_list[2], 0, 4, 0, 0.05, 0)
    verify_show(lock_object_list[3], 0, 6, -1.75, 0.05, -1.75)
    verify_show(lock_object_list[4], 0, 8, 1.75, 0.05, 1.75)
    verify_show(lock_object_list[5], 0, 10, 0, 0.05, 0)

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

    verify_show(lock_object_list[0], 0, 0, 0, 0.05, 0)
    verify_show(lock_object_list[1], 0, 5, 0, 0.05, 0)

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
    verify_show(lock_object_list[0], 0, 0, 0, 0.05, 0)
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

    verify_show(lock_object_list[0], 0, 0, 0, 0.05, 0)
    verify_show(lock_object_list[1], 0, 2, -1.75, 0.05, -1.75)
    verify_show(lock_object_list[2], 0, 4, 1.75, 0.05, 1.75)

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


def test_create_occluder_evaluation():
    trial_list = [[{}], [{}]]
    agent_object = {
        'debug': {
            'boundsAtStep': (
                [create_simple_bounds(-0.6, -0.4, -0.6, -0.4, y=0)] * 40 +
                [create_simple_bounds(-0.5, -0.3, -0.5, -0.3, y=0)]
            ),
            'dimensions': {'x': 0.3, 'y': 0.5, 'z': 0.3}
        },
        'shows': [{
            'stepBegin': 0,
            'position': {'x': -0.5, 'y': 0, 'z': -0.5},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.3, 'y': 0.5, 'z': 0.3},
                offset=None,
                position={'x': -0.5, 'y': 0, 'z': -0.5},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 2,
            'position': {'x': -0.5, 'y': 0, 'z': -0.5},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.3, 'y': 0.5, 'z': 0.3},
                offset=None,
                position={'x': -0.5, 'y': 0, 'z': -0.5},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 41,
            'position': {'x': -0.4, 'y': 0, 'z': -0.4},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.3, 'y': 0.5, 'z': 0.3},
                offset=None,
                position={'x': -0.4, 'y': 0, 'z': -0.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }]
    }
    paddle_object = {
        'shows': [{
            'stepBegin': index,
            'position': {'x': -1.5, 'y': 0, 'z': -1},
            'rotation': {'x': 0, 'y': rotation, 'z': 0},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.25, 'y': 0.5, 'z': 1},
                offset=None,
                position={'x': -1.5, 'y': 0, 'z': -1},
                rotation={'x': 0, 'y': rotation, 'z': 0},
                standing_y=0
            )
        } for index, rotation in enumerate(range(360, 5, -5))]
    }

    occluder_object = _create_occluder_object(
        trial_list,
        agent_object,
        paddle_object,
        [],
        OccluderMode.EVAL,
        UNIT_SIZE
    )

    assert occluder_object['id'].startswith('occluder_')
    assert occluder_object['type'] == 'cube'
    assert occluder_object['materials'] == ['Custom/Materials/White']
    assert occluder_object['kinematic']
    assert occluder_object['structure']

    assert len(occluder_object['shows']) == 2
    verify_show(occluder_object, 0, 0, -3.25, 0.75, -1.45)
    assert occluder_object['shows'][0]['rotation']['y'] == 0
    assert occluder_object['shows'][0]['scale']['x'] == 0.25
    assert occluder_object['shows'][0]['scale']['y'] == 1.5
    assert occluder_object['shows'][0]['scale']['z'] == 1.05
    verify_show(occluder_object, 1, 2, 0.225, 0.75, -1.225)
    assert occluder_object['shows'][1]['rotation']['y'] == 45


def test_create_occluder_training():
    trial_list = [[{}], [{}]]
    agent_object = {
        'debug': {
            'boundsAtStep': (
                [create_simple_bounds(-0.6, -0.4, -0.6, -0.4, y=0)] * 40 +
                [create_simple_bounds(-0.5, -0.3, -0.5, -0.3, y=0)]
            ),
            'dimensions': {'x': 0.3, 'y': 0.5, 'z': 0.3}
        },
        'shows': [{
            'stepBegin': 0,
            'position': {'x': -0.5, 'y': 0, 'z': -0.5},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.3, 'y': 0.5, 'z': 0.3},
                offset=None,
                position={'x': -0.5, 'y': 0, 'z': -0.5},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 2,
            'position': {'x': -0.5, 'y': 0, 'z': -0.5},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.3, 'y': 0.5, 'z': 0.3},
                offset=None,
                position={'x': -0.5, 'y': 0, 'z': -0.5},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 41,
            'position': {'x': -0.4, 'y': 0, 'z': -0.4},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.3, 'y': 0.5, 'z': 0.3},
                offset=None,
                position={'x': -0.4, 'y': 0, 'z': -0.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }]
    }
    paddle_object = {
        'debug': {},
        'shows': [{
            'stepBegin': index,
            'position': {'x': -1.5, 'y': 0, 'z': -1},
            'rotation': {'x': 0, 'y': rotation, 'z': 0},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.25, 'y': 0.5, 'z': 1},
                offset=None,
                position={'x': -1.5, 'y': 0, 'z': -1},
                rotation={'x': 0, 'y': rotation, 'z': 0},
                standing_y=0
            )
        } for index, rotation in enumerate(range(360, 5, -5))]
    }
    paddle_object['debug']['boundsAtStep'] = [
        show['boundingBox'] for show in paddle_object['shows']
    ]

    positions = []
    for _ in range(100):
        occluder_object = _create_occluder_object(
            trial_list,
            agent_object,
            paddle_object,
            [],
            OccluderMode.TRAINING,
            UNIT_SIZE
        )

        assert occluder_object['id'].startswith('occluder_')
        assert occluder_object['type'] == 'cube'
        assert occluder_object['materials'] == ['Custom/Materials/White']
        assert occluder_object['kinematic']
        assert occluder_object['structure']

        assert len(occluder_object['shows']) == 2
        verify_show(occluder_object, 0, 0, -3.25, 0.75, -1.45)
        assert occluder_object['shows'][0]['rotation']['y'] == 0
        assert occluder_object['shows'][0]['scale']['x'] == 0.25
        assert occluder_object['shows'][0]['scale']['y'] == 1.5
        assert occluder_object['shows'][0]['scale']['z'] == 1.05

        assert occluder_object['shows'][1]['stepBegin'] == 2
        occluder_position = occluder_object['shows'][1]['position']
        if occluder_position not in positions:
            positions.append(occluder_position)
        assert -2 < occluder_position['x'] < 2
        assert occluder_position['y'] == 0.75
        assert -2 < occluder_position['z'] < 2
        assert occluder_object['shows'][1]['rotation']['y'] == 45
        assert 'scale' not in occluder_object['shows'][1]

    # Verify there are a lot of random positions.
    assert len(positions) > 1


def test_create_occluder_none():
    trial_list = [[{}], [{}]]
    agent_object = {
        'debug': {
            'boundsAtStep': (
                [create_simple_bounds(-0.6, -0.4, -0.6, -0.4, y=0)] * 40 +
                [create_simple_bounds(-0.5, -0.3, -0.5, -0.3, y=0)]
            ),
            'dimensions': {'x': 0.3, 'y': 0.5, 'z': 0.3}
        },
        'shows': [{
            'stepBegin': 0,
            'position': {'x': -0.5, 'y': 0, 'z': -0.5},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.3, 'y': 0.5, 'z': 0.3},
                offset=None,
                position={'x': -0.5, 'y': 0, 'z': -0.5},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 2,
            'position': {'x': -0.5, 'y': 0, 'z': -0.5},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.3, 'y': 0.5, 'z': 0.3},
                offset=None,
                position={'x': -0.5, 'y': 0, 'z': -0.5},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 41,
            'position': {'x': -0.4, 'y': 0, 'z': -0.4},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.3, 'y': 0.5, 'z': 0.3},
                offset=None,
                position={'x': -0.4, 'y': 0, 'z': -0.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }]
    }
    paddle_object = {
        'shows': [{
            'stepBegin': index,
            'position': {'x': -1.5, 'y': 0, 'z': -1},
            'rotation': {'x': 0, 'y': rotation, 'z': 0},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.25, 'y': 0.5, 'z': 1},
                offset=None,
                position={'x': -1.5, 'y': 0, 'z': -1},
                rotation={'x': 0, 'y': rotation, 'z': 0},
                standing_y=0
            )
        } for index, rotation in enumerate(range(360, 5, -5))]
    }

    occluder_object = _create_occluder_object(
        trial_list,
        agent_object,
        paddle_object,
        [],
        OccluderMode.NONE,
        UNIT_SIZE
    )
    assert occluder_object is None


def test_create_paddle():
    trial_list = [[
        {'paddle': [[20, 20], [10, 40], 30]},
        {'paddle': [[20, 20], [10, 40], 35]},
        {'paddle': [[20, 20], [10, 40], 40]},
        {'paddle': [[20, 20], [10, 40], 45]},
    ], [
        {'paddle': [[100, 100], [10, 40], 300]},
        {'paddle': [[100, 100], [10, 40], 305]},
        {'paddle': [[100, 100], [10, 40], 310]},
        {'paddle': [[100, 100], [10, 40], 315]}
    ]]

    paddle_object = _create_paddle_object(trial_list, UNIT_SIZE)

    assert paddle_object['id'].startswith('paddle_')
    assert paddle_object['type'] == 'cube'
    assert paddle_object['materials'] == ['Custom/Materials/Black']
    assert paddle_object['kinematic']
    assert paddle_object['debug']['configHeight'] == [0.25, 0.5]
    assert paddle_object['debug']['configSize'] == [0.25, 1.0]

    assert len(paddle_object['shows']) == 8
    assert paddle_object['shows'][0]['scale']['x'] == 0.25
    assert paddle_object['shows'][0]['scale']['y'] == 0.5
    assert paddle_object['shows'][0]['scale']['z'] == 1.0
    verify_show(paddle_object, 0, 0, -2.0, 0.25, -2.0)
    verify_show(paddle_object, 1, 1, -2.0, 0.25, -2.0)
    verify_show(paddle_object, 2, 2, -2.0, 0.25, -2.0)
    verify_show(paddle_object, 3, 3, -2.0, 0.25, -2.0)
    assert paddle_object['shows'][0]['rotation']['y'] == 330
    assert paddle_object['shows'][1]['rotation']['y'] == 325
    assert paddle_object['shows'][2]['rotation']['y'] == 320
    assert paddle_object['shows'][3]['rotation']['y'] == 315
    verify_show(paddle_object, 4, 5, 0, 0.25, 0)
    verify_show(paddle_object, 5, 6, 0, 0.25, 0)
    verify_show(paddle_object, 6, 7, 0, 0.25, 0)
    verify_show(paddle_object, 7, 8, 0, 0.25, 0)
    assert paddle_object['shows'][4]['rotation']['y'] == 60
    assert paddle_object['shows'][5]['rotation']['y'] == 55
    assert paddle_object['shows'][6]['rotation']['y'] == 50
    assert paddle_object['shows'][7]['rotation']['y'] == 45


def test_create_scene():
    starter_scene = Scene()
    goal_template = hypercubes.initialize_goal(
        Goal(category='mock', domains_info={}, scene_info={})
    )

    agent_object_config_list = [
        ObjectConfigWithMaterial(
            AgentConfig('cube', 0.1, rotation_y=0),
            MaterialTuple('test_material', ['test_color'])
        )
    ]
    goal_object_config_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 0.1, 0.2),
            MaterialTuple('test_material', ['test_color'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 0.1, 0.2),
            MaterialTuple('test_material', ['test_color'])
        )
    ]

    trial_list = [[{
        'agent': [[25, 25], 5, 'agent_1'],
        'home': [[25, 25], 5],
        'objects': [
            [[25, 45], 5, 'obj_1', 'yellow'],
            [[95, 95], 5, 'obj_2', 'purple']
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
            [[45, 25], 5, 'obj_1', 'yellow'],
            [[165, 165], 5, 'obj_2', 'purple']
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
            starter_scene,
            goal_template,
            agent_object_config_list,
            goal_object_config_list,
            trial_list,
            'filename',
            MaterialTuple('test_material', ['test_color']),
            is_expected
        )

        assert scene.isometric
        assert scene.goal.answer['choice'] == (
            'expected' if is_expected else 'unexpected'
        )
        assert scene.goal.action_list == [
            ['Pass'], ['Pass'], ['Pass'], ['Pass'], ['Pass'],
            ['EndHabituation'],
            ['Pass'], ['Pass'], ['Pass'], ['Pass'], ['Pass']
        ]
        assert scene.goal.habituation_total == 1
        assert scene.goal.last_step == 11

        assert len(scene.objects) == 13
        agent_object_list = [
            mcs_object for mcs_object in scene.objects
            if mcs_object['debug']['role'] == 'agent'
        ]
        assert len(agent_object_list) == 1
        home_object_list = [
            mcs_object for mcs_object in scene.objects
            if mcs_object['debug']['role'] == 'home'
        ]
        assert len(home_object_list) == 1
        non_target_object_list = [
            mcs_object for mcs_object in scene.objects
            if mcs_object['debug']['role'] == 'non target'
        ]
        assert len(non_target_object_list) == 1
        target_object_list = [
            mcs_object for mcs_object in scene.objects
            if mcs_object['debug']['role'] == 'target'
        ]
        assert len(target_object_list) == 1
        platform_object_list = [
            mcs_object for mcs_object in scene.objects
            if mcs_object['debug']['role'] == 'structural'
        ]
        assert len(platform_object_list) == 1
        wall_object_list = [
            mcs_object for mcs_object in scene.objects
            if mcs_object['debug']['role'] == 'wall'
        ]
        assert len(wall_object_list) == 8


def test_create_scene_with_paddle():
    starter_scene = Scene()
    goal_template = hypercubes.initialize_goal(
        Goal(category='mock', domains_info={}, scene_info={})
    )

    agent_object_config_list = [
        ObjectConfigWithMaterial(
            AgentConfig('cube', 1, rotation_y=0),
            MaterialTuple('test_material', ['test_color'])
        )
    ]
    goal_object_config_list = [
        ObjectConfigWithMaterial(
            ObjectConfig('cube', 0.707, 1, rotation_y=45),
            MaterialTuple('test_material', ['test_color'])
        ),
        ObjectConfigWithMaterial(
            ObjectConfig('sphere', 1, 1),
            MaterialTuple('test_material', ['test_color'])
        )
    ]

    trial_list = [[{
        'agent': [[25, 25], 5, 'agent_1'],
        'home': [[25, 25], 5],
        'objects': [
            [[25, 45], 5, 'obj_1', 'yellow'],
            [[95, 95], 5, 'obj_2', 'purple']
        ],
        'paddle': [[160, 160], [10, 40], 120],
        'size': [200, 200],
        'walls': [
            [[60, 60], [20, 20]],
            [[60, 120], [20, 20]],
            [[120, 60], [20, 20]],
            [[120, 120], [20, 20]]
        ]
    }, {
        'agent': [[25, 25], 5, 'agent_1'],
        'paddle': [[160, 160], [10, 40], 125]
    }, {
        'agent': [[25, 30], 5, 'agent_1'],
        'paddle': [[160, 160], [10, 40], 130]
    }, {
        'agent': [[25, 35], 5, 'agent_1'],
        'paddle': [[160, 160], [10, 40], 135]
    }, {
        'agent': [[25, 35], 5, 'agent_1'],
        'paddle': [[160, 160], [10, 40], 140]
    }], [{
        'agent': [[25, 25], 5, 'agent_1'],
        'objects': [
            [[45, 25], 5, 'obj_1', 'yellow'],
            [[165, 165], 5, 'obj_2', 'purple']
        ],
        'paddle': [[160, 160], [10, 40], 120],
        'walls': [
            [[60, 60], [20, 20]],
            [[60, 120], [20, 20]],
            [[120, 60], [20, 20]],
            [[120, 120], [20, 20]]
        ]
    }, {
        'agent': [[25, 25], 5, 'agent_1'],
        'paddle': [[160, 160], [10, 40], 125]
    }, {
        'agent': [[30, 25], 5, 'agent_1'],
        'paddle': [[160, 160], [10, 40], 130]
    }, {
        'agent': [[35, 25], 5, 'agent_1'],
        'paddle': [[160, 160], [10, 40], 135]
    }, {
        'agent': [[35, 25], 5, 'agent_1'],
        'paddle': [[160, 160], [10, 40], 140]
    }]]

    # Valid scene.
    scene = _create_scene(
        starter_scene,
        goal_template,
        agent_object_config_list,
        goal_object_config_list,
        trial_list,
        'filename',
        MaterialTuple('test_material', ['test_color']),
        True
    )
    assert scene
    paddle_object_list = [
        mcs_object for mcs_object in scene.objects
        if mcs_object['debug']['role'] == 'paddle'
    ]
    assert len(paddle_object_list) == 1

    # Still a valid scene.
    for frame in trial_list[-1]:
        # Move the paddle to be near the agent, but not overlap it.
        frame['paddle'][0] = [18, 18]
    scene = _create_scene(
        starter_scene,
        goal_template,
        agent_object_config_list,
        goal_object_config_list,
        trial_list,
        'filename',
        MaterialTuple('test_material', ['test_color']),
        True
    )
    assert scene

    # Invalid scene.
    for frame in trial_list[-1]:
        # Move the paddle to overlap with the agent.
        frame['paddle'][0] = [19, 19]
    with pytest.raises(exceptions.SceneException):
        _create_scene(
            starter_scene,
            goal_template,
            agent_object_config_list,
            goal_object_config_list,
            trial_list,
            'filename',
            MaterialTuple('test_material', ['test_color']),
            True
        )


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
        Vector3d(x=-1.36, y=0, z=-0.4),
        Vector3d(x=-1.36, y=0, z=-1.6),
        Vector3d(x=-2.14, y=0, z=-1.6),
        Vector3d(x=-2.14, y=0, z=-0.4)
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
    converted_trial = _create_trial_frame_list(trial, 0)
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

    converted_trial = _create_trial_frame_list(trial, 0)
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


def test_create_trial_frame_list_imitated_agents():
    trial = [
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 13]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 14]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 15]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 16]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 15]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 14]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 13]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[31, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[41, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[51, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[61, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[51, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[41, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[31, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 3]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 4]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 5]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 6]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 5]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 4]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 3]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]}
    ]
    converted_trial = _create_trial_frame_list(trial, 0)
    assert converted_trial == [
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 13]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 15]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 15]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 13]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[41, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[61, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[41, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 3]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 5]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 5]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 3]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]},
        {'agent': [[1, 2]], 'other_agents': [[[11, 12]], [[21, 22]]]}
    ]


def test_create_trial_frame_list_paddle():
    trial = [
        {'agent': [[10, 10]], 'paddle': [[150, 150], i]} for i in range(180)
    ]
    for i in range(0, 60):
        trial[i + 60]['agent'][0][0] += i + 1
        trial[i + 120]['agent'][0][0] += 60

    converted_trial = _create_trial_frame_list(trial, 0)

    assert converted_trial == [
        {'agent': [[10, 10]], 'paddle': [[150, 150], 0]},
        {'agent': [[10, 10]], 'paddle': [[150, 150], 1]},
    ] + [
        {'agent': [[10, 10]], 'paddle': [[150, 150], i]}
        for i in range(3, 60, 2)
    ] + [
        {'agent': [[10 + i + 1, 10]], 'paddle': [[150, 150], 60 + i]}
        for i in range(1, 60, 2)
    ] + [
        {'agent': [[70, 10]], 'paddle': [[150, 150], 120 + i]}
        for i in range(1, 10, 2)
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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
        'scale': {'x': 0.1, 'y': 0.35, 'z': 0.35}
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


def test_move_agent_adjacent_to_goal():
    agent = create_test_agent_moving_diagonally()
    original = copy.deepcopy(agent['shows'])
    goal_bounds_1 = create_simple_bounds(3.1, 2.1, 3.1, 2.1)
    goal_object_1 = {
        'id': 'goal_1',
        'type': 'tube_wide',
        'changeMaterials': [],
        'debug': {
            'boundsAtStep': [goal_bounds_1] * 25
        },
        'materials': ['Custom/Materials/Orange'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2.55, 'y': 0, 'z': 2.55},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_1
        }]
    }
    # Number of frames in each trial is always one less than number of bounds.
    trial_list = [[{}] * 24]

    _move_agent_adjacent_to_goal(agent, [goal_object_1], trial_list)

    assert len(agent['shows']) == 18
    for i in range(0, 17):
        assert agent['shows'][i] == original[i]
    assert agent['shows'][17]['stepBegin'] == 21
    expected_position = {'x': 1.975, 'y': 0.125, 'z': 1.975}
    assert agent['shows'][17]['position'] == expected_position
    assert agent['shows'][17]['boundingBox'] != original[17]['boundingBox']
    bounds_at_step = agent['debug']['boundsAtStep']
    assert bounds_at_step[21] != original[17]['boundingBox']
    assert bounds_at_step[22] == bounds_at_step[21]
    assert bounds_at_step[23] == bounds_at_step[21]
    for show in agent['shows']:
        step = show['stepBegin']
        assert bounds_at_step[step] == show['boundingBox']
    assert goal_object_1['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 25,
        'materials': ['Custom/Materials/Orange']
    }]


def test_move_agent_adjacent_to_goal_too_far_away():
    agent = create_test_agent_moving_diagonally()
    original = copy.deepcopy(agent['shows'])
    goal_bounds_1 = create_simple_bounds(3.25, 2.25, 3.25, 2.25)
    goal_object_1 = {
        'id': 'goal_1',
        'type': 'tube_wide',
        'changeMaterials': [],
        'debug': {
            'boundsAtStep': [goal_bounds_1] * 25
        },
        'materials': ['Custom/Materials/Orange'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2.75, 'y': 0, 'z': 2.75},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_1
        }]
    }
    # Number of frames in each trial is always one less than number of bounds.
    trial_list = [[{}] * 24]

    _move_agent_adjacent_to_goal(agent, [goal_object_1], trial_list)

    assert len(agent['shows']) == 18
    for i in range(0, 18):
        assert agent['shows'][i] == original[i]
    for show in agent['shows']:
        step = show['stepBegin']
        assert agent['debug']['boundsAtStep'][step] == show['boundingBox']
    assert goal_object_1['changeMaterials'] == []


def test_move_agent_adjacent_to_goal_multiple_trials():
    agent = create_test_agent_moving_diagonally(trial_2=True)
    original = copy.deepcopy(agent['shows'])
    goal_bounds_1 = create_simple_bounds(2.5, 1.5, 3.1, 2.1)
    goal_bounds_2 = create_simple_bounds(-2.1, -3.1, -1.5, -2.5)
    goal_object_1 = {
        'id': 'goal_1',
        'type': 'tube_wide',
        'changeMaterials': [],
        'debug': {
            'boundsAtStep': [goal_bounds_1] * 25 + [goal_bounds_2] * 25
        },
        'materials': ['Custom/Materials/Orange'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2, 'y': 0, 'z': 2.55},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_1
        }, {
            'stepBegin': 25,
            'position': {'x': -2.55, 'y': 0, 'z': -2},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_2
        }]
    }
    # Number of frames in each trial is always one less than number of bounds.
    trial_list = [[{}] * 24, [{}] * 24]

    _move_agent_adjacent_to_goal(agent, [goal_object_1], trial_list)

    assert len(agent['shows']) == 36
    for i in list(range(0, 17)) + list(range(18, 35)):
        assert agent['shows'][i] == original[i]
    bounds_at_step = agent['debug']['boundsAtStep']
    for show in agent['shows']:
        step = show['stepBegin']
        assert bounds_at_step[step] == show['boundingBox']
    assert goal_object_1['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 25,
        'materials': ['Custom/Materials/Orange']
    }, {
        'stepBegin': 46,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 50,
        'materials': ['Custom/Materials/Orange']
    }]
    # Trial 1
    assert agent['shows'][17]['stepBegin'] == 21
    expected_position = {'x': 1.875, 'y': 0.125, 'z': 1.975}
    assert agent['shows'][17]['position'] == expected_position
    assert agent['shows'][17]['boundingBox'] != original[17]['boundingBox']
    assert bounds_at_step[21] != original[17]['boundingBox']
    assert bounds_at_step[22] == bounds_at_step[21]
    assert bounds_at_step[23] == bounds_at_step[21]
    # Trial 2
    assert agent['shows'][35]['stepBegin'] == 46
    expected_position = {'x': -1.975, 'y': 0.125, 'z': -1.875}
    assert agent['shows'][35]['position'] == expected_position
    assert agent['shows'][35]['boundingBox'] != original[35]['boundingBox']
    assert bounds_at_step[46] != original[35]['boundingBox']
    assert bounds_at_step[47] == bounds_at_step[46]
    assert bounds_at_step[48] == bounds_at_step[46]


def test_move_agent_adjacent_to_goal_multiple_objects():
    agent = create_test_agent_moving_diagonally()
    original = copy.deepcopy(agent['shows'])
    goal_bounds_1 = create_simple_bounds(3.1, 2.1, 3.1, 2.1)
    goal_bounds_2 = create_simple_bounds(3.1, 2.1, 0.5, -0.5)
    goal_object_1 = {
        'id': 'goal_1',
        'type': 'tube_wide',
        'changeMaterials': [],
        'debug': {
            'boundsAtStep': [goal_bounds_1] * 25
        },
        'materials': ['Custom/Materials/Orange'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2.55, 'y': 0, 'z': 2.55},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_1
        }]
    }
    goal_object_2 = {
        'id': 'goal_2',
        'type': 'cube_hollow_wide',
        'changeMaterials': [],
        'debug': {
            'boundsAtStep': [goal_bounds_2] * 25
        },
        'materials': ['Custom/Materials/Grey'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2.55, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_2
        }]
    }
    goal_object_list = [goal_object_1, goal_object_2]
    # Number of frames in each trial is always one less than number of bounds.
    trial_list = [[{}] * 24]

    _move_agent_adjacent_to_goal(agent, goal_object_list, trial_list)

    assert len(agent['shows']) == 18
    for i in range(0, 17):
        assert agent['shows'][i] == original[i]
    assert agent['shows'][17]['stepBegin'] == 21
    expected_position = {'x': 1.975, 'y': 0.125, 'z': 1.975}
    assert agent['shows'][17]['position'] == expected_position
    assert agent['shows'][17]['boundingBox'] != original[17]['boundingBox']
    bounds_at_step = agent['debug']['boundsAtStep']
    assert bounds_at_step[21] != original[17]['boundingBox']
    assert bounds_at_step[22] == bounds_at_step[21]
    assert bounds_at_step[23] == bounds_at_step[21]
    for show in agent['shows']:
        step = show['stepBegin']
        assert bounds_at_step[step] == show['boundingBox']
    assert goal_object_1['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 25,
        'materials': ['Custom/Materials/Orange']
    }]
    assert goal_object_2['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 25,
        'materials': ['Custom/Materials/Grey']
    }]


def test_move_agent_adjacent_to_goal_small_overlap():
    agent = create_test_agent_moving_diagonally()
    original = copy.deepcopy(agent['shows'])
    goal_bounds_1 = create_simple_bounds(2.9, 1.9, 2.9, 1.9)
    goal_object_1 = {
        'id': 'goal_1',
        'type': 'tube_wide',
        'changeMaterials': [],
        'debug': {
            'boundsAtStep': [goal_bounds_1] * 25
        },
        'materials': ['Custom/Materials/Orange'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2.45, 'y': 0, 'z': 2.45},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_1
        }]
    }
    # Number of frames in each trial is always one less than number of bounds.
    trial_list = [[{}] * 24]

    _move_agent_adjacent_to_goal(agent, [goal_object_1], trial_list)

    # Minor overlap is OK; if not, other parts of the code will likely raise
    # an exception.
    assert len(agent['shows']) == 18
    for i in range(0, 18):
        assert agent['shows'][i] == original[i]
    for show in agent['shows']:
        step = show['stepBegin']
        assert agent['debug']['boundsAtStep'][step] == show['boundingBox']
    assert goal_object_1['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 25,
        'materials': ['Custom/Materials/Orange']
    }]


def test_move_agent_adjacent_to_goal_toward_then_away():
    agent = create_test_agent_moving_diagonally()
    agent['debug']['boundsAtStep'] = agent['debug']['boundsAtStep'][:-3]
    extras = list(reversed(copy.deepcopy(agent['shows'][:-1])))
    for i in range(0, 17):
        extras[i]['stepBegin'] = 22 + i
        agent['debug']['boundsAtStep'].append(extras[i]['boundingBox'])
    agent['shows'].extend(extras)
    agent['debug']['boundsAtStep'].extend([extras[-1]['boundingBox']] * 3)
    agent['debug']['trialToSteps'][0] = (0, 41)
    original = copy.deepcopy(agent['shows'])
    goal_bounds_1 = create_simple_bounds(3.1, 2.1, 3.1, 2.1)
    goal_object_1 = {
        'id': 'goal_1',
        'type': 'tube_wide',
        'changeMaterials': [],
        'debug': {
            'boundsAtStep': [goal_bounds_1] * 42
        },
        'materials': ['Custom/Materials/Orange'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2.55, 'y': 0, 'z': 2.55},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_1
        }]
    }
    # Number of frames in each trial is always one less than number of bounds.
    trial_list = [[{}] * 41]

    _move_agent_adjacent_to_goal(agent, [goal_object_1], trial_list)

    assert len(agent['shows']) == 35
    for i in list(range(0, 17)) + list(range(18, 35)):
        assert agent['shows'][i] == original[i]
    assert agent['shows'][17]['stepBegin'] == 21
    expected_position = {'x': 1.975, 'y': 0.125, 'z': 1.975}
    assert agent['shows'][17]['position'] == expected_position
    assert agent['shows'][17]['boundingBox'] != original[17]['boundingBox']
    bounds_at_step = agent['debug']['boundsAtStep']
    assert bounds_at_step[21] != original[17]['boundingBox']
    for show in agent['shows']:
        step = show['stepBegin']
        assert bounds_at_step[step] == show['boundingBox']
    assert goal_object_1['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 42,
        'materials': ['Custom/Materials/Orange']
    }]


def test_move_agent_adjacent_to_goal_agent_touches():
    agent = create_test_agent_moving_diagonally()
    original = copy.deepcopy(agent['shows'])
    goal_bounds_1 = create_simple_bounds(3.1, 2.1, 3.1, 2.1)
    goal_object_1 = {
        'id': 'goal_1',
        'type': 'tube_wide',
        'changeMaterials': [],
        'debug': {
            'agentTouches': {
                0: [21]
            },
            'boundsAtStep': [goal_bounds_1] * 25
        },
        'materials': ['Custom/Materials/Orange'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2.55, 'y': 0, 'z': 2.55},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_1
        }]
    }
    # Number of frames in each trial is always one less than number of bounds.
    trial_list = [[{}] * 24]

    _move_agent_adjacent_to_goal(agent, [goal_object_1], trial_list)

    assert len(agent['shows']) == 18
    for i in range(0, 17):
        assert agent['shows'][i] == original[i]
    assert agent['shows'][17]['stepBegin'] == 21
    expected_position = {'x': 1.975, 'y': 0.125, 'z': 1.975}
    assert agent['shows'][17]['position'] == expected_position
    assert agent['shows'][17]['boundingBox'] != original[17]['boundingBox']
    bounds_at_step = agent['debug']['boundsAtStep']
    assert bounds_at_step[21] != original[17]['boundingBox']
    assert bounds_at_step[22] == bounds_at_step[21]
    assert bounds_at_step[23] == bounds_at_step[21]
    for show in agent['shows']:
        step = show['stepBegin']
        assert bounds_at_step[step] == show['boundingBox']
    assert goal_object_1['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 25,
        'materials': ['Custom/Materials/Orange']
    }]


def test_move_agent_adjacent_to_goal_agent_touches_multiple_touches():
    agent = create_test_agent_moving_diagonally()
    agent['debug']['boundsAtStep'] = agent['debug']['boundsAtStep'][:-3]
    extras = (
        list(reversed(copy.deepcopy(agent['shows'][:-1]))) +
        list(copy.deepcopy(agent['shows'][1:]))
    )
    for i in range(0, 34):
        extras[i]['stepBegin'] = 22 + i
        agent['debug']['boundsAtStep'].append(extras[i]['boundingBox'])
    agent['shows'].extend(extras)
    agent['debug']['boundsAtStep'].extend([extras[-1]['boundingBox']] * 3)
    agent['debug']['trialToSteps'][0] = (0, 58)
    original = copy.deepcopy(agent['shows'])
    goal_bounds_1 = create_simple_bounds(3.1, 2.1, 3.1, 2.1)
    goal_object_1 = {
        'id': 'goal_1',
        'type': 'tube_wide',
        'changeMaterials': [],
        'debug': {
            'agentTouches': {
                0: [21, 55]
            },
            'boundsAtStep': [goal_bounds_1] * 59
        },
        'materials': ['Custom/Materials/Orange'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2.55, 'y': 0, 'z': 2.55},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_1
        }]
    }
    # Number of frames in each trial is always one less than number of bounds.
    trial_list = [[{}] * 58]

    _move_agent_adjacent_to_goal(agent, [goal_object_1], trial_list)

    assert len(agent['shows']) == 52
    for i in list(range(0, 17)) + list(range(18, 51)):
        assert agent['shows'][i] == original[i]
    assert agent['shows'][17]['stepBegin'] == 21
    expected_position = {'x': 1.975, 'y': 0.125, 'z': 1.975}
    assert agent['shows'][17]['position'] == expected_position
    assert agent['shows'][17]['boundingBox'] != original[17]['boundingBox']
    bounds_at_step = agent['debug']['boundsAtStep']
    assert bounds_at_step[21] != original[17]['boundingBox']
    assert agent['shows'][51]['stepBegin'] == 55
    expected_position = {'x': 1.975, 'y': 0.125, 'z': 1.975}
    assert agent['shows'][51]['position'] == expected_position
    assert agent['shows'][51]['boundingBox'] != original[47]['boundingBox']
    bounds_at_step = agent['debug']['boundsAtStep']
    assert bounds_at_step[55] != original[51]['boundingBox']
    for show in agent['shows']:
        step = show['stepBegin']
        assert bounds_at_step[step] == show['boundingBox']
    assert goal_object_1['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 55,
        'materials': ['Custom/Materials/Orange']
    }, {
        'stepBegin': 59,
        'materials': ['Custom/Materials/Orange']
    }]


def test_move_agent_adjacent_to_goal_agent_touches_multiple_trials():
    agent = create_test_agent_moving_diagonally(trial_2=True)
    original = copy.deepcopy(agent['shows'])
    goal_bounds_1 = create_simple_bounds(2.5, 1.5, 3.1, 2.1)
    goal_bounds_2 = create_simple_bounds(-2.1, -3.1, -1.5, -2.5)
    goal_object_1 = {
        'id': 'goal_1',
        'type': 'tube_wide',
        'changeMaterials': [],
        'debug': {
            'agentTouches': {
                0: [21],
                1: [46]
            },
            'boundsAtStep': [goal_bounds_1] * 25 + [goal_bounds_2] * 25
        },
        'materials': ['Custom/Materials/Orange'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2, 'y': 0, 'z': 2.55},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_1
        }, {
            'stepBegin': 25,
            'position': {'x': -2.55, 'y': 0, 'z': -2},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_2
        }]
    }
    # Number of frames in each trial is always one less than number of bounds.
    trial_list = [[{}] * 24, [{}] * 24]

    _move_agent_adjacent_to_goal(agent, [goal_object_1], trial_list)

    assert len(agent['shows']) == 36
    for i in list(range(0, 17)) + list(range(18, 35)):
        assert agent['shows'][i] == original[i]
    bounds_at_step = agent['debug']['boundsAtStep']
    for show in agent['shows']:
        step = show['stepBegin']
        assert bounds_at_step[step] == show['boundingBox']
    assert goal_object_1['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 25,
        'materials': ['Custom/Materials/Orange']
    }, {
        'stepBegin': 46,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 50,
        'materials': ['Custom/Materials/Orange']
    }]
    # Trial 1
    assert agent['shows'][17]['stepBegin'] == 21
    expected_position = {'x': 1.875, 'y': 0.125, 'z': 1.975}
    assert agent['shows'][17]['position'] == expected_position
    assert agent['shows'][17]['boundingBox'] != original[17]['boundingBox']
    assert bounds_at_step[21] != original[17]['boundingBox']
    assert bounds_at_step[22] == bounds_at_step[21]
    assert bounds_at_step[23] == bounds_at_step[21]
    # Trial 2
    assert agent['shows'][35]['stepBegin'] == 46
    expected_position = {'x': -1.975, 'y': 0.125, 'z': -1.875}
    assert agent['shows'][35]['position'] == expected_position
    assert agent['shows'][35]['boundingBox'] != original[35]['boundingBox']
    assert bounds_at_step[46] != original[35]['boundingBox']
    assert bounds_at_step[47] == bounds_at_step[46]
    assert bounds_at_step[48] == bounds_at_step[46]


def test_move_agent_adjacent_to_goal_agent_touches_multiple_objects():
    agent = create_test_agent_moving_diagonally()
    original = copy.deepcopy(agent['shows'])
    goal_bounds_1 = create_simple_bounds(3.1, 2.1, 3.1, 2.1)
    goal_bounds_2 = create_simple_bounds(3.1, 2.1, 0.5, -0.5)
    goal_object_1 = {
        'id': 'goal_1',
        'type': 'tube_wide',
        'changeMaterials': [],
        'debug': {
            'agentTouches': {
                0: [21]
            },
            'boundsAtStep': [goal_bounds_1] * 25
        },
        'materials': ['Custom/Materials/Orange'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2.55, 'y': 0, 'z': 2.55},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_1
        }]
    }
    goal_object_2 = {
        'id': 'goal_2',
        'type': 'cube_hollow_wide',
        'changeMaterials': [],
        'debug': {
            'boundsAtStep': [goal_bounds_2] * 25
        },
        'materials': ['Custom/Materials/Grey'],
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 2.55, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': goal_bounds_2
        }]
    }
    goal_object_list = [goal_object_1, goal_object_2]
    # Number of frames in each trial is always one less than number of bounds.
    trial_list = [[{}] * 24]

    _move_agent_adjacent_to_goal(agent, goal_object_list, trial_list)

    assert len(agent['shows']) == 18
    for i in range(0, 17):
        assert agent['shows'][i] == original[i]
    assert agent['shows'][17]['stepBegin'] == 21
    expected_position = {'x': 1.975, 'y': 0.125, 'z': 1.975}
    assert agent['shows'][17]['position'] == expected_position
    assert agent['shows'][17]['boundingBox'] != original[17]['boundingBox']
    bounds_at_step = agent['debug']['boundsAtStep']
    assert bounds_at_step[21] != original[17]['boundingBox']
    assert bounds_at_step[22] == bounds_at_step[21]
    assert bounds_at_step[23] == bounds_at_step[21]
    for show in agent['shows']:
        step = show['stepBegin']
        assert bounds_at_step[step] == show['boundingBox']
    assert goal_object_1['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 25,
        'materials': ['Custom/Materials/Orange']
    }]
    assert goal_object_2['changeMaterials'] == [{
        'stepBegin': 21,
        'materials': ['Custom/Materials/Red']
    }, {
        'stepBegin': 25,
        'materials': ['Custom/Materials/Grey']
    }]


def test_move_agent_past_lock_location():
    agent_object = {
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 1,
            'position': {'x': 0, 'y': 0, 'z': 0.1},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 2,
            'position': {'x': 0, 'y': 0, 'z': 0.2},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.2},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 3,
            'position': {'x': 0, 'y': 0, 'z': 0.3},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.3},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 4,
            'position': {'x': 0, 'y': 0, 'z': 0.4},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 10,
            'position': {'x': 0, 'y': 0, 'z': 0.8},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.8},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 11,
            'position': {'x': 0, 'y': 0, 'z': 0.9},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.9},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 12,
            'position': {'x': 0, 'y': 0, 'z': 1},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 13,
            'position': {'x': 0, 'y': 0, 'z': 1.1},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 14,
            'position': {'x': 0, 'y': 0, 'z': 1.2},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.2},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 15,
            'position': {'x': 0, 'y': 0, 'z': 1.3},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.3},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 16,
            'position': {'x': 0, 'y': 0, 'z': 1.4},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }]
    }
    lock_bounds = wrap_create_bounds(
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
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 1,
            'position': {'x': 0, 'y': 0, 'z': 0.1},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 2,
            'position': {'x': 0, 'y': 0, 'z': 0.2},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.2},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 3,
            'position': {'x': 0, 'y': 0, 'z': 0.3},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.3},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 4,
            'position': {'x': 0, 'y': 0, 'z': 0.4},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 10,
            'position': {'x': 0, 'y': 0, 'z': 0.8},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.8},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 11,
            'position': {'x': 0, 'y': 0, 'z': 0.7},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.7},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 12,
            'position': {'x': 0, 'y': 0, 'z': 0.6},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.6},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 13,
            'position': {'x': 0, 'y': 0, 'z': 0.5},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.5},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 14,
            'position': {'x': 0, 'y': 0, 'z': 0.4},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 15,
            'position': {'x': 0, 'y': 0, 'z': 0.3},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.3},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 16,
            'position': {'x': 0, 'y': 0, 'z': 0.2},
            'boundingBox': wrap_create_bounds(
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.2},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }]
    }
    lock_bounds = wrap_create_bounds(
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


def test_move_agent_past_lock_location_with_ellipses():
    agent_object = {
        'shows': [{
            'stepBegin': 0,
            'position': {'x': 0, 'y': 0, 'z': 0},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 1,
            'position': {'x': 0, 'y': 0, 'z': 0.1},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 2,
            'position': {'x': 0, 'y': 0, 'z': 0.2},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.2},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 3,
            'position': {'x': 0, 'y': 0, 'z': 0.3},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.3},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 4,
            'position': {'x': 0, 'y': 0, 'z': 0.4},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 10,
            'position': {'x': 0, 'y': 0, 'z': 0.8},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.8},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 11,
            'position': {'x': 0, 'y': 0, 'z': 0.9},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 0.9},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 12,
            'position': {'x': 0, 'y': 0, 'z': 1},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 13,
            'position': {'x': 0, 'y': 0, 'z': 1.1},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.1},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 14,
            'position': {'x': 0, 'y': 0, 'z': 1.2},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.2},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 15,
            'position': {'x': 0, 'y': 0, 'z': 1.3},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.3},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }, {
            'stepBegin': 16,
            'position': {'x': 0, 'y': 0, 'z': 1.4},
            'boundingBox': _make_true_bounds(
                'blob_01',
                dimensions={'x': 0.2, 'y': 0.2, 'z': 0.2},
                offset=None,
                position={'x': 0, 'y': 0, 'z': 1.4},
                rotation={'x': 0, 'y': 0, 'z': 0},
                standing_y=0
            )
        }]
    }
    lock_bounds = _make_true_bounds(
        'lock_wall',
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


def test_remove_extraneous_object_show_single_step():
    agent_object_list = [{
        'debug': {},
        'shows': [
            {'stepBegin': 0, 'position': {'x': 0, 'z': 0}}
        ]
    }]

    _remove_extraneous_object_show(agent_object_list, [[{}]])

    assert len(agent_object_list[0]['shows']) == 1


def test_remove_extraneous_object_show_no_extraneous():
    agent_object_list = [{
        'debug': {},
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
        'debug': {},
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
        'debug': {},
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
        'debug': {},
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
        'debug': {},
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
        'debug': {},
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
        'debug': {},
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
    bounds_a = create_simple_bounds(1, -1, 1, -1)
    bounds_b = create_simple_bounds(2, 0, 2, 0)
    bounds_c = create_simple_bounds(3, 1, 3, 1)
    bounds_d = create_simple_bounds(4, 2, 4, 2)
    agent_object_list = [{
        'id': 'agent_1',
        'debug': {
            'boundsAtStep': [
                bounds_a, bounds_a, bounds_a, bounds_b, bounds_c,
                bounds_d, bounds_d, bounds_d
            ],
            'trialToSteps': {
                0: (0, 7)
            }
        },
        'shows': [
            {'stepBegin': 0, 'boundingBox': bounds_a},
            {'stepBegin': 3, 'boundingBox': bounds_b},
            {'stepBegin': 4, 'boundingBox': bounds_c},
            {'stepBegin': 5, 'boundingBox': bounds_d}
        ]
    }]

    goal_object_list = [{
        'id': 'goal_1',
        'debug': {
            'boundsAtStep': [create_simple_bounds(6.1, 4.1, 6.1, 4.1)] * 8
        }
    }]

    _remove_intersecting_agent_steps(agent_object_list, goal_object_list)

    assert len(agent_object_list[0]['shows']) == 4


def test_remove_intersecting_agent_steps_with_intersection():
    bounds_a = create_simple_bounds(1, -1, 1, -1)
    bounds_b = create_simple_bounds(2, 0, 2, 0)
    bounds_c = create_simple_bounds(3, 1, 3, 1)
    bounds_d = create_simple_bounds(1, -1, 1, -1)
    bounds_e = create_simple_bounds(0, -2, 0, -2)
    bounds_f = create_simple_bounds(-1, -3, -1, -3)
    agent_object_list = [{
        'id': 'agent_1',
        'debug': {
            'boundsAtStep': [
                bounds_a, bounds_a, bounds_a, bounds_b, bounds_c,
                bounds_c, bounds_c, bounds_d, bounds_d, bounds_d,
                bounds_e, bounds_f, bounds_f, bounds_f
            ],
            'trialToSteps': {
                0: (0, 13)
            }
        },
        'shows': [
            {'stepBegin': 0, 'boundingBox': bounds_a},
            {'stepBegin': 3, 'boundingBox': bounds_b},
            {'stepBegin': 4, 'boundingBox': bounds_c},
            {'stepBegin': 7, 'boundingBox': bounds_d},
            {'stepBegin': 10, 'boundingBox': bounds_e},
            {'stepBegin': 11, 'boundingBox': bounds_f}
        ]
    }]

    goal_object_list = [{
        'id': 'goal_1',
        'debug': {
            'boundsAtStep': [create_simple_bounds(3.9, 2.9, 3.9, 2.9)] * 14
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
    bounds_a = create_simple_bounds(1, -1, 1, -1)
    bounds_b = create_simple_bounds(2, 0, 2, 0)
    bounds_c = create_simple_bounds(3, 1, 3, 1)
    bounds_d = create_simple_bounds(1, -1, 1, -1)
    bounds_e = create_simple_bounds(0, -2, 0, -2)
    bounds_f = create_simple_bounds(-1, -3, -1, -3)
    agent_object_list = [{
        'id': 'agent_1',
        'debug': {
            'boundsAtStep': [
                bounds_a, bounds_a, bounds_a, bounds_b, bounds_c,
                bounds_c, bounds_c, bounds_d, bounds_d, bounds_d,
                bounds_e, bounds_f, bounds_f, bounds_f
            ],
            'trialToSteps': {
                0: (0, 13)
            }
        },
        'shows': [
            {'stepBegin': 0, 'boundingBox': bounds_a},
            {'stepBegin': 3, 'boundingBox': bounds_b},
            {'stepBegin': 4, 'boundingBox': bounds_c},
            {'stepBegin': 7, 'boundingBox': bounds_d},
            {'stepBegin': 10, 'boundingBox': bounds_e},
            {'stepBegin': 11, 'boundingBox': bounds_f}
        ]
    }, {
        'id': 'agent_2',
        'debug': {
            'boundsAtStep': [
                # Intentionally out-of-order
                bounds_d, bounds_d, bounds_d, bounds_e, bounds_f,
                bounds_f, bounds_f, bounds_a, bounds_a, bounds_a,
                bounds_b, bounds_c, bounds_c, bounds_c
            ],
            'trialToSteps': {
                0: (0, 13)
            }
        },
        'shows': [
            # Intentionally out-of-order
            {'stepBegin': 0, 'boundingBox': bounds_d},
            {'stepBegin': 3, 'boundingBox': bounds_e},
            {'stepBegin': 4, 'boundingBox': bounds_f},
            {'stepBegin': 7, 'boundingBox': bounds_a},
            {'stepBegin': 10, 'boundingBox': bounds_b},
            {'stepBegin': 11, 'boundingBox': bounds_c}
        ]
    }]

    goal_object_list = [{
        'id': 'goal_1',
        'debug': {
            'boundsAtStep': [create_simple_bounds(3.9, 2.9, 3.9, 2.9)] * 14
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
    bounds_a = create_simple_bounds(1, -1, 1, -1)
    bounds_b = create_simple_bounds(2, 0, 2, 0)
    bounds_c = create_simple_bounds(3, 1, 3, 1)
    bounds_d = create_simple_bounds(1, -1, 1, -1)
    bounds_e = create_simple_bounds(0, -2, 0, -2)
    bounds_f = create_simple_bounds(-1, -3, -1, -3)
    agent_object_list = [{
        'id': 'agent_1',
        'debug': {
            'boundsAtStep': [
                bounds_a, bounds_a, bounds_a, bounds_b, bounds_c,
                bounds_c, bounds_c, bounds_d, bounds_d, bounds_d,
                bounds_e, bounds_f, bounds_f, bounds_f
            ],
            'trialToSteps': {
                0: (0, 13)
            }
        },
        'shows': [
            {'stepBegin': 0, 'boundingBox': bounds_a},
            {'stepBegin': 3, 'boundingBox': bounds_b},
            {'stepBegin': 4, 'boundingBox': bounds_c},
            {'stepBegin': 7, 'boundingBox': bounds_d},
            {'stepBegin': 10, 'boundingBox': bounds_e},
            {'stepBegin': 11, 'boundingBox': bounds_f}
        ]
    }]

    goal_object_list = [{
        'id': 'goal_1',
        'debug': {
            'boundsAtStep': [create_simple_bounds(2.9, 1.9, 3.9, 2.9)] * 14
        }
    }, {
        'id': 'goal_2',
        'debug': {
            'boundsAtStep': [create_simple_bounds(-3.9, -2.9, -2.9, -1.9)] * 14
        }
    }]

    _remove_intersecting_agent_steps(agent_object_list, goal_object_list)

    assert len(agent_object_list[0]['shows']) == 4
    assert agent_object_list[0]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[0]['shows'][1]['stepBegin'] == 3
    assert agent_object_list[0]['shows'][2]['stepBegin'] == 7
    assert agent_object_list[0]['shows'][3]['stepBegin'] == 10


def test_remove_intersecting_agent_steps_with_ellipses():
    bounds_1 = create_ellipsoidal_bounds(0, 0, 0.5, 1)
    bounds_2 = create_ellipsoidal_bounds(0.5, 0.5, 0.5, 1)
    bounds_3 = create_ellipsoidal_bounds(1, 1, 0.5, 1)
    bounds_4 = create_ellipsoidal_bounds(1.5, 1.5, 0.5, 1)
    bounds_5 = create_ellipsoidal_bounds(2, 2, 0.5, 1)
    bounds_6 = bounds_5
    agent_object_list = [{
        'id': 'agent_1',
        'debug': {
            'boundsAtStep': [
                bounds_1, bounds_2, bounds_3, bounds_4, bounds_5, bounds_6
            ],
            'trialToSteps': {
                0: (0, 5)
            }
        },
        'shows': [
            {'stepBegin': 0, 'boundingBox': bounds_1},
            {'stepBegin': 1, 'boundingBox': bounds_2},
            {'stepBegin': 2, 'boundingBox': bounds_3},
            {'stepBegin': 3, 'boundingBox': bounds_4},
            {'stepBegin': 4, 'boundingBox': bounds_5}
        ]
    }]

    goal_object_list = [{
        'id': 'goal_1',
        'debug': {
            'boundsAtStep': [create_ellipsoidal_bounds(2, 2, 0.5, 1)] * 6
        }
    }]

    _remove_intersecting_agent_steps(agent_object_list, goal_object_list)

    assert len(agent_object_list[0]['shows']) == 3
    assert agent_object_list[0]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[0]['shows'][1]['stepBegin'] == 1
    assert agent_object_list[0]['shows'][2]['stepBegin'] == 2


def test_remove_intersecting_agent_steps_with_object_in_middle_of_path():
    bounds_a = create_simple_bounds(-2.5, -2.25, -2.5, -2.25)
    bounds_b = create_simple_bounds(-2.25, -2.0, -2.25, -2.0)
    bounds_c = create_simple_bounds(-2.0, -1.75, -2.0, -1.75)
    bounds_d = create_simple_bounds(-1.75, -1.5, -1.75, -1.5)
    bounds_e = create_simple_bounds(-1.5, -1.25, -1.5, -1.25)
    bounds_f = create_simple_bounds(-1.25, -1.0, -1.25, -1.0)
    bounds_g = create_simple_bounds(-1.0, -0.75, -1.0, -0.75)
    bounds_h = create_simple_bounds(-0.75, -0.5, -0.75, -0.5)
    bounds_i = create_simple_bounds(-0.5, -0.25, -0.5, -0.25)
    bounds_j = create_simple_bounds(-0.25, 0, -0.25, 0)
    bounds_k = create_simple_bounds(0, 0.25, 0, 0.25)
    bounds_l = create_simple_bounds(0.25, 0.5, 0.25, 0.5)
    bounds_m = create_simple_bounds(0.5, 0.75, 0.5, 0.75)
    bounds_n = create_simple_bounds(0.75, 1.0, 0.75, 1.0)
    bounds_o = create_simple_bounds(1.0, 1.25, 1.0, 1.25)
    bounds_p = create_simple_bounds(1.25, 1.5, 1.25, 1.5)
    bounds_q = create_simple_bounds(1.5, 1.75, 1.5, 1.75)
    bounds_r = create_simple_bounds(1.75, 2.0, 1.75, 2.0)
    agent_object_list = [{
        'id': 'agent_1',
        'debug': {
            'boundsAtStep': [
                bounds_a, bounds_a, bounds_a, bounds_a, bounds_a,
                bounds_b, bounds_c, bounds_d, bounds_e, bounds_f,
                bounds_g, bounds_h, bounds_i, bounds_j, bounds_k,
                bounds_l, bounds_m, bounds_n, bounds_o, bounds_p,
                bounds_q, bounds_r, bounds_r, bounds_r, bounds_r
            ],
            'trialToSteps': {
                0: (0, 24)
            }
        },
        'shows': [
            {'stepBegin': 0, 'boundingBox': bounds_a},
            {'stepBegin': 5, 'boundingBox': bounds_b},
            {'stepBegin': 6, 'boundingBox': bounds_c},
            {'stepBegin': 7, 'boundingBox': bounds_d},
            {'stepBegin': 8, 'boundingBox': bounds_e},
            {'stepBegin': 9, 'boundingBox': bounds_f},
            {'stepBegin': 10, 'boundingBox': bounds_g},
            {'stepBegin': 11, 'boundingBox': bounds_h},
            {'stepBegin': 12, 'boundingBox': bounds_i},
            {'stepBegin': 13, 'boundingBox': bounds_j},
            {'stepBegin': 14, 'boundingBox': bounds_k},
            {'stepBegin': 15, 'boundingBox': bounds_l},
            {'stepBegin': 16, 'boundingBox': bounds_m},
            {'stepBegin': 17, 'boundingBox': bounds_n},
            {'stepBegin': 18, 'boundingBox': bounds_o},
            {'stepBegin': 19, 'boundingBox': bounds_p},
            {'stepBegin': 20, 'boundingBox': bounds_q},
            {'stepBegin': 21, 'boundingBox': bounds_r}
        ]
    }]

    non_agent_list = [{
        'id': 'goal_1',
        'debug': {
            'boundsAtStep': [create_simple_bounds(0.5, -0.5, 0.5, -0.5)] * 25
        }
    }]

    _remove_intersecting_agent_steps(agent_object_list, non_agent_list)

    # Never show an agent intersecting another object by a significantly large
    # amount. In a real case this egregious, other parts of the code will
    # likely raise an exception before calling this function.
    assert len(agent_object_list[0]['shows']) == 14
    assert agent_object_list[0]['shows'][0]['stepBegin'] == 0
    assert agent_object_list[0]['shows'][1]['stepBegin'] == 5
    assert agent_object_list[0]['shows'][2]['stepBegin'] == 6
    assert agent_object_list[0]['shows'][3]['stepBegin'] == 7
    assert agent_object_list[0]['shows'][4]['stepBegin'] == 8
    assert agent_object_list[0]['shows'][5]['stepBegin'] == 9
    assert agent_object_list[0]['shows'][6]['stepBegin'] == 10
    assert agent_object_list[0]['shows'][7]['stepBegin'] == 11
    assert agent_object_list[0]['shows'][8]['stepBegin'] == 16
    assert agent_object_list[0]['shows'][9]['stepBegin'] == 17
    assert agent_object_list[0]['shows'][10]['stepBegin'] == 18
    assert agent_object_list[0]['shows'][11]['stepBegin'] == 19
    assert agent_object_list[0]['shows'][12]['stepBegin'] == 20
    assert agent_object_list[0]['shows'][13]['stepBegin'] == 21


def test_remove_intersecting_agent_steps_with_wall_in_middle_of_path():
    bounds_a = create_simple_bounds(-2.5, -2.25, -2.5, -2.25)
    bounds_b = create_simple_bounds(-2.25, -2.0, -2.25, -2.0)
    bounds_c = create_simple_bounds(-2.0, -1.75, -2.0, -1.75)
    bounds_d = create_simple_bounds(-1.75, -1.5, -1.75, -1.5)
    bounds_e = create_simple_bounds(-1.5, -1.25, -1.5, -1.25)
    bounds_f = create_simple_bounds(-1.25, -1.0, -1.25, -1.0)
    bounds_g = create_simple_bounds(-1.0, -0.75, -1.0, -0.75)
    bounds_h = create_simple_bounds(-0.75, -0.5, -0.75, -0.5)
    bounds_i = create_simple_bounds(-0.5, -0.25, -0.5, -0.25)
    bounds_j = create_simple_bounds(-0.25, 0, -0.25, 0)
    bounds_k = create_simple_bounds(0, 0.25, 0, 0.25)
    bounds_l = create_simple_bounds(0.25, 0.5, 0.25, 0.5)
    bounds_m = create_simple_bounds(0.5, 0.75, 0.5, 0.75)
    bounds_n = create_simple_bounds(0.75, 1.0, 0.75, 1.0)
    bounds_o = create_simple_bounds(1.0, 1.25, 1.0, 1.25)
    bounds_p = create_simple_bounds(1.25, 1.5, 1.25, 1.5)
    bounds_q = create_simple_bounds(1.5, 1.75, 1.5, 1.75)
    bounds_r = create_simple_bounds(1.75, 2.0, 1.75, 2.0)
    agent_object_list = [{
        'id': 'agent_1',
        'debug': {
            'boundsAtStep': [
                bounds_a, bounds_a, bounds_a, bounds_a, bounds_a,
                bounds_b, bounds_c, bounds_d, bounds_e, bounds_f,
                bounds_g, bounds_h, bounds_i, bounds_j, bounds_k,
                bounds_l, bounds_m, bounds_n, bounds_o, bounds_p,
                bounds_q, bounds_r, bounds_r, bounds_r, bounds_r
            ],
            'trialToSteps': {
                0: (0, 24)
            }
        },
        'shows': [
            {'stepBegin': 0, 'boundingBox': bounds_a},
            {'stepBegin': 5, 'boundingBox': bounds_b},
            {'stepBegin': 6, 'boundingBox': bounds_c},
            {'stepBegin': 7, 'boundingBox': bounds_d},
            {'stepBegin': 8, 'boundingBox': bounds_e},
            {'stepBegin': 9, 'boundingBox': bounds_f},
            {'stepBegin': 10, 'boundingBox': bounds_g},
            {'stepBegin': 11, 'boundingBox': bounds_h},
            {'stepBegin': 12, 'boundingBox': bounds_i},
            {'stepBegin': 13, 'boundingBox': bounds_j},
            {'stepBegin': 14, 'boundingBox': bounds_k},
            {'stepBegin': 15, 'boundingBox': bounds_l},
            {'stepBegin': 16, 'boundingBox': bounds_m},
            {'stepBegin': 17, 'boundingBox': bounds_n},
            {'stepBegin': 18, 'boundingBox': bounds_o},
            {'stepBegin': 19, 'boundingBox': bounds_p},
            {'stepBegin': 20, 'boundingBox': bounds_q},
            {'stepBegin': 21, 'boundingBox': bounds_r}
        ]
    }]
    original = copy.deepcopy(agent_object_list[0]['shows'])

    non_agent_list = [{
        'id': 'wall_1',
        'debug': {
            'boundsAtStep': [create_simple_bounds(0.5, -0.5, 0.5, -0.5)] * 25
        }
    }]

    _remove_intersecting_agent_steps(agent_object_list, non_agent_list)

    # It's OK to show an agent intersecting with a wall in the middle of its
    # path. In a real case this egregious, other parts of the code will
    # likely raise an exception before calling this function. Normally the
    # agent may just clip the wall a little.
    assert original == agent_object_list[0]['shows']


def test_reposition_agents_away_from_paddle_unnecessary_no_intersection():
    agent = create_test_agent_moving_diagonally()
    original = copy.deepcopy(agent['shows'])

    paddle_bounds_a = create_simple_bounds(-3.2, -2.7, 1.5, 3.5)
    paddle_bounds_b = create_simple_bounds(-3.95, -1.95, 1.5, 3.5)
    paddle = {
        'id': 'paddle',
        'debug': {
            'boundsAtStep': ([paddle_bounds_a] + ([paddle_bounds_b] * 9)) * 3
        },
        'shows': [{'stepBegin': i} for i in range(0, 25)]
    }

    _reposition_agents_away_from_paddle([agent], paddle)

    assert len(agent['shows']) == 18
    for i in range(0, 18):
        assert agent['shows'][i] == original[i]


def test_reposition_agents_away_from_paddle_necessary():
    agent = create_test_agent_moving_diagonally()
    original = copy.deepcopy(agent['shows'])

    paddle_bounds_a = create_simple_bounds(-3.2, -2.7, -3.5, -1.5)
    paddle_bounds_b = create_simple_bounds(-3.95, -1.95, -3.5, -1.5)
    paddle = {
        'id': 'paddle',
        'debug': {
            'boundsAtStep': ([paddle_bounds_a] + ([paddle_bounds_b] * 9)) * 3
        },
        'shows': [{'stepBegin': i} for i in range(0, 25)]
    }

    _reposition_agents_away_from_paddle([agent], paddle)

    assert len(agent['shows']) == 18
    assert agent['shows'][0]['stepBegin'] == 0
    expected_position = {'x': -1.875, 'y': 0.125, 'z': -1.875}
    assert agent['shows'][0]['position'] == expected_position
    assert agent['shows'][1]['stepBegin'] == 5
    assert agent['shows'][1]['position'] == expected_position
    assert agent['shows'][2]['stepBegin'] == 6
    assert agent['shows'][2]['position'] == expected_position
    for i in range(3, 18):
        assert agent['shows'][i] == original[i]


def test_reposition_agents_away_from_paddle_unnecessary_intersection_midway():
    agent = create_test_agent_moving_diagonally()
    original = copy.deepcopy(agent['shows'])

    paddle_bounds_a = create_simple_bounds(-0.25, 0.25, 1, 1)
    paddle_bounds_b = create_simple_bounds(-1, 1, -1, 1)
    paddle = {
        'id': 'paddle',
        'debug': {
            'boundsAtStep': ([paddle_bounds_a] + ([paddle_bounds_b] * 9)) * 3
        },
        'shows': [{'stepBegin': i} for i in range(0, 25)]
    }

    _reposition_agents_away_from_paddle([agent], paddle)

    # Never remove steps from an agent's path due to the paddle after the agent
    # starts moving. In a real case this egregious, other parts of the code
    # will likely raise an exception before calling this function.
    assert len(agent['shows']) == 18
    for i in range(0, 18):
        assert agent['shows'][i] == original[i]


def test_reposition_agents_away_from_paddle_no_paddle():
    agent = create_test_agent_moving_diagonally()
    original = copy.deepcopy(agent['shows'])

    _reposition_agents_away_from_paddle([agent], None)

    assert len(agent['shows']) == 18
    for i in range(0, 18):
        assert agent['shows'][i] == original[i]


def test_retrieve_unit_size():
    assert _retrieve_unit_size([[{'size': [200, 200]}]]) == UNIT_SIZE
    assert _retrieve_unit_size([[{'size': [100, 400]}]]) == [0.05, 0.0125]
