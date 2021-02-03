import numpy
from numpy.testing import assert_array_almost_equal_nulp
import pytest
from shapely.geometry import Point

import optimal_path


def test_dilate_and_unify_object_bounds():
    bounds = [
        {'x': -1.0, 'z': -1.0},
        {'x': -1.0, 'z': 1.0},
        {'x': 1.0, 'z': 1.0},
        {'x': 1.0, 'z': -1.0}
    ]

    output = optimal_path._dilate_and_unify_object_bounds(
        [bounds],
        0.5,
        Point(0, -4),
        Point(0, 4)
    )
    assert_array_almost_equal_nulp(numpy.array(output), numpy.array([[
        (-1.0, -1.5), (-1.5, -1.0), (-1.5, 1.0), (-1.0, 1.5), (1.0, 1.5),
        (1.5, 1.0), (1.5, -1.0), (1.0, -1.5)
    ]]))

    output = optimal_path._dilate_and_unify_object_bounds(
        [bounds],
        1,
        Point(0, -4),
        Point(0, 4)
    )
    assert_array_almost_equal_nulp(numpy.array(output), numpy.array([[
        (-1.0, -2), (-2, -1.0), (-2, 1.0), (-1.0, 2), (1.0, 2),
        (2, 1.0), (2, -1.0), (1.0, -2)
    ]]))

    # Will not dilate if source is inside bounds.
    output = optimal_path._dilate_and_unify_object_bounds(
        [bounds],
        0.5,
        Point(0, -1.25),
        Point(0, 4)
    )
    assert_array_almost_equal_nulp(numpy.array(output), numpy.array([[
        (-1.0, -1.0), (-1.0, 1.0), (1.0, 1.0), (1.0, -1.0)
    ]]))

    # Will not dilate if target is inside bounds.
    output = optimal_path._dilate_and_unify_object_bounds(
        [bounds],
        0.5,
        Point(0, -4),
        Point(0, 1.25)
    )
    assert_array_almost_equal_nulp(numpy.array(output), numpy.array([[
        (-1.0, -1.0), (-1.0, 1.0), (1.0, 1.0), (1.0, -1.0)
    ]]))


def test_dilate_and_unify_object_bounds_multiple_poly():
    bounds_1 = [
        {'x': -1.0, 'z': -1.0},
        {'x': -1.0, 'z': 1.0},
        {'x': 1.0, 'z': 1.0},
        {'x': 1.0, 'z': -1.0}
    ]
    bounds_2 = [
        {'x': -4.0, 'z': -1.0},
        {'x': -4.0, 'z': 1.0},
        {'x': -3.0, 'z': 1.0},
        {'x': -3.0, 'z': -1.0}
    ]
    bounds_3 = [
        {'x': 3.0, 'z': -1.0},
        {'x': 3.0, 'z': 1.0},
        {'x': 4.0, 'z': 1.0},
        {'x': 4.0, 'z': -1.0}
    ]

    output = optimal_path._dilate_and_unify_object_bounds(
        [bounds_1, bounds_2, bounds_3],
        0.5,
        Point(0, -4),
        Point(0, 4)
    )
    assert len(output) == 3
    assert_array_almost_equal_nulp(numpy.array(output[0]), numpy.array([
        (-4.0, -1.5), (-4.5, -1.0), (-4.5, 1.0), (-4.0, 1.5), (-3.0, 1.5),
        (-2.5, 1.0), (-2.5, -1.0), (-3.0, -1.5)
    ]))
    assert_array_almost_equal_nulp(numpy.array(output[1]), numpy.array([
        (3.0, -1.5), (2.5, -1.0), (2.5, 1.0), (3.0, 1.5), (4.0, 1.5),
        (4.5, 1.0), (4.5, -1.0), (4.0, -1.5)
    ]))
    assert_array_almost_equal_nulp(numpy.array(output[2]), numpy.array([
        (-1.0, -1.5), (-1.5, -1.0), (-1.5, 1.0), (-1.0, 1.5), (1.0, 1.5),
        (1.5, 1.0), (1.5, -1.0), (1.0, -1.5)
    ]))

    bounds_4 = [
        {'x': 1.0, 'z': -1.0},
        {'x': 1.0, 'z': 1.0},
        {'x': 3.0, 'z': 1.0},
        {'x': 3.0, 'z': -1.0}
    ]

    output = optimal_path._dilate_and_unify_object_bounds(
        [bounds_1, bounds_2, bounds_3, bounds_4],
        0.5,
        Point(0, -4),
        Point(0, 4)
    )
    assert len(output) == 2
    assert_array_almost_equal_nulp(numpy.array(output[0]), numpy.array([
        (-1.0, -1.5), (-1.5, -1.0), (-1.5, 1.0), (-1.0, 1.5), (1.0, 1.5),
        (3.0, 1.5), (4.0, 1.5), (4.5, 1.0), (4.5, -1.0), (4.0, -1.5),
        (3.0, -1.5), (1.0, -1.5)
    ]))
    assert_array_almost_equal_nulp(numpy.array(output[1]), numpy.array([
        (-4.0, -1.5), (-4.5, -1.0), (-4.5, 1.0), (-4.0, 1.5), (-3.0, 1.5),
        (-2.5, 1.0), (-2.5, -1.0), (-3.0, -1.5)
    ]))


def test_dilate_target_bounds():
    output = optimal_path._dilate_target_bounds([
        {'x': -1.0, 'z': -1.0},
        {'x': -1.0, 'z': 1.0},
        {'x': 1.0, 'z': 1.0},
        {'x': 1.0, 'z': -1.0}
    ])
    assert_array_almost_equal_nulp(numpy.array(output), numpy.array([
        (1.0, -1.99), (0, -1.99), (-1.0, -1.99),
        (-1.99, -1.0), (-1.99, 0), (-1.99, 1.0),
        (-1.0, 1.99), (0, 1.99), (1.0, 1.99),
        (1.99, 1.0), (1.99, 0), (1.99, -1.0)
    ]))


def test_find_target_or_parent_dict():
    output = optimal_path._find_target_or_parent_dict({
        'id': 'id_0',
        'type': 'trophy'
    }, [{
        'id': 'id_1',
        'type': 'ball'
    }, {
        'id': 'id_2',
        'type': 'duck'
    }, {
        'id': 'id_3',
        'type': 'sofa'
    }, {
        'id': 'id_4',
        'type': 'suitcase'
    }])
    assert output == {'id': 'id_0', 'type': 'trophy'}


def test_find_target_or_parent_dict_with_parent():
    output = optimal_path._find_target_or_parent_dict({
        'id': 'id_0',
        'type': 'trophy',
        'locationParent': 'id_4'
    }, [{
        'id': 'id_1',
        'type': 'ball'
    }, {
        'id': 'id_2',
        'type': 'duck'
    }, {
        'id': 'id_3',
        'type': 'sofa'
    }, {
        'id': 'id_4',
        'type': 'suitcase'
    }])
    assert output == {'id': 'id_4', 'type': 'suitcase'}


def test_remove_duplicate_paths():
    path_1 = optimal_path.ShortestPath([{
        'action': 'MoveAhead',
        'params': {}
    }, {
        'action': 'MoveAhead',
        'params': {}
    }], None, None)
    path_2 = optimal_path.ShortestPath([{
        'action': 'MoveAhead',
        'params': {}
    }, {
        'action': 'PickupObject',
        'params': {'objectId': 'a'}
    }], None, None)
    path_3 = optimal_path.ShortestPath([{
        'action': 'MoveAhead',
        'params': {}
    }, {
        'action': 'PickupObject',
        'params': {'objectId': 'b'}
    }], None, None)
    path_4 = optimal_path.ShortestPath([{
        'action': 'MoveAhead',
        'params': {}
    }, {
        'action': 'MoveAhead',
        'params': {}
    }, {
        'action': 'PickupObject',
        'params': {'objectId': 'a'}
    }], None, None)

    output = optimal_path._remove_duplicate_paths([
        path_1, path_2, path_3, path_4, path_1, path_2, path_3, path_4
    ])
    assert len(output) == 4
    assert output[0].action_list[0]['action'] == 'MoveAhead'
    assert output[0].action_list[1]['action'] == 'MoveAhead'
    assert output[1].action_list[0]['action'] == 'MoveAhead'
    assert output[1].action_list[1]['action'] == 'PickupObject'
    assert output[1].action_list[1]['params']['objectId'] == 'a'
    assert output[2].action_list[0]['action'] == 'MoveAhead'
    assert output[2].action_list[1]['action'] == 'PickupObject'
    assert output[2].action_list[1]['params']['objectId'] == 'b'
    assert output[3].action_list[0]['action'] == 'MoveAhead'
    assert output[3].action_list[1]['action'] == 'MoveAhead'
    assert output[3].action_list[2]['action'] == 'PickupObject'
    assert output[3].action_list[2]['params']['objectId'] == 'a'


def test_generate_shortest_path_position_list_trivial():
    environment = optimal_path._generate_pathfinding_environment([])
    assert environment
    position_list = optimal_path._generate_shortest_path_position_list(
        (0, 0),
        (0, 4.5),
        environment
    )
    assert position_list == [(0, 0), (0, 4.5)]


def test_generate_shortest_path_position_list_basic():
    bounds_1 = [
        {'x': -1.0, 'z': 0.5}, {'x': -1.0, 'z': 1.0}, {'x': 0.5, 'z': 1.0},
        {'x': 0.5, 'z': 0.5}
    ]
    environment = optimal_path._generate_pathfinding_environment(
        [bounds_1]
    )
    assert environment
    position_list = optimal_path._generate_shortest_path_position_list(
        (0, 0),
        (0, 4.5),
        environment
    )
    assert_array_almost_equal_nulp(numpy.array(position_list), numpy.array([
        (0, 0), (0.5, 0.22), (0.78, 0.5), (0.78, 1.0), (0, 4.5)
    ]))


def test_generate_shortest_path_position_list_complex():
    bounds_1 = [
        {'x': -1.0, 'z': 0.5}, {'x': -1.0, 'z': 0.75}, {'x': 0.5, 'z': 0.75},
        {'x': 0.5, 'z': 0.5}
    ]
    bounds_2 = [
        {'x': -0.5, 'z': 1.5}, {'x': -0.5, 'z': 1.75}, {'x': 4.44, 'z': 1.75},
        {'x': 4.44, 'z': 1.5}
    ]
    bounds_3 = [
        {'x': -4.44, 'z': 2.5}, {'x': -4.44, 'z': 2.75}, {'x': 0.5, 'z': 2.75},
        {'x': 0.5, 'z': 2.5}
    ]
    bounds_4 = [
        {'x': -0.5, 'z': 3.5}, {'x': -0.5, 'z': 3.75}, {'x': 1.0, 'z': 3.75},
        {'x': 1.0, 'z': 3.5}
    ]
    environment = optimal_path._generate_pathfinding_environment(
        [bounds_1, bounds_2, bounds_3, bounds_4]
    )
    assert environment
    position_list = optimal_path._generate_shortest_path_position_list(
        (0, 0),
        (0, 4.5),
        environment
    )
    assert_array_almost_equal_nulp(numpy.array(position_list), numpy.array([
        (0, 0), (-1.0, 0.22), (-1.28, 0.5), (-1.28, 0.75), (-0.78, 1.75),
        (-0.5, 2.03), (0.5, 2.22), (0.78, 2.5), (1.28, 3.5), (1.28, 3.75),
        (1.0, 4.03), (0, 4.5)
    ]))


def test_generate_shortest_path_position_list_squeeze():
    bounds_1 = [
        {'x': -4.44, 'z': 0.5}, {'x': -4.44, 'z': 1.0}, {'x': -0.25, 'z': 1.0},
        {'x': -0.25, 'z': 0.5}
    ]
    bounds_2 = [
        {'x': 0.25, 'z': 0.5}, {'x': 0.25, 'z': 1.0}, {'x': 1.0, 'z': 1.0},
        {'x': 1.0, 'z': 0.5}
    ]
    bounds_3 = [
        {'x': 2.0, 'z': 0.5}, {'x': 2.0, 'z': 1.0}, {'x': 4.44, 'z': 1.0},
        {'x': 4.44, 'z': 0.5}
    ]
    environment = optimal_path._generate_pathfinding_environment(
        [bounds_1, bounds_2, bounds_3]
    )
    assert environment
    position_list = optimal_path._generate_shortest_path_position_list(
        (0, 0),
        (0, 4.5),
        environment
    )
    assert_array_almost_equal_nulp(numpy.array(position_list), numpy.array([
        (0, 0), (1.0, 0.22), (1.28, 0.5), (1.28, 1.0), (0, 4.5)
    ]))


def test_generate_shortest_path_position_list_almost_impossible():
    bounds_1 = [
        {'x': -5, 'z': 0.5}, {'x': -5, 'z': 1.0}, {'x': 4.43, 'z': 1.0},
        {'x': 4.43, 'z': 0.5}
    ]
    environment = optimal_path._generate_pathfinding_environment(
        [bounds_1]
    )
    assert environment
    position_list = optimal_path._generate_shortest_path_position_list(
        (0, 0),
        (0, 4.5),
        environment
    )
    assert_array_almost_equal_nulp(numpy.array(position_list), numpy.array([
        (0, 0), (4.43, 0.22), (4.71, 0.5), (4.71, 1.0), (4.43, 1.28), (0, 4.5)
    ]))


def test_generate_shortest_path_position_list_impossible():
    bounds_1 = [
        {'x': -4.45, 'z': 0.5}, {'x': -4.45, 'z': 1.0}, {'x': 4.45, 'z': 1.0},
        {'x': 4.45, 'z': 0.5}
    ]
    environment = optimal_path._generate_pathfinding_environment(
        [bounds_1]
    )
    assert environment
    position_list = optimal_path._generate_shortest_path_position_list(
        (0, 0),
        (0, 4),
        environment
    )
    assert position_list is None


def test_rotate_then_move_no_rotation_or_movement():
    # 90 degree rotation is facing north in shapely
    path = optimal_path.ShortestPath([], (0, 0), 90)
    path_list = optimal_path._rotate_then_move(path, (0, 0))
    assert len(path_list) == 1
    assert path_list[0].action_list == []
    assert path_list[0].rotation == 90
    assert path_list[0].position[0] == pytest.approx(0)
    assert path_list[0].position[1] == pytest.approx(0)


def test_rotate_then_move_only_movement():
    # 90 degree rotation is facing north in shapely
    path = optimal_path.ShortestPath([], (0, 0), 90)
    path_list = optimal_path._rotate_then_move(path, (0, 4))
    assert len(path_list) == 1
    assert path_list[0].action_list == (
        [{'action': 'MoveAhead', 'params': {}}] * 40
    )
    assert path_list[0].rotation == 90
    assert path_list[0].position[0] == pytest.approx(0)
    assert path_list[0].position[1] == pytest.approx(4)


def test_rotate_then_move_only_rotation():
    # 0 degree rotation is facing east in shapely
    path = optimal_path.ShortestPath([], (0, 0), 0)
    path_list = optimal_path._rotate_then_move(path, (0, 0.05))
    assert len(path_list) == 2
    assert path_list[0].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 9
    )
    assert path_list[0].rotation == 90
    assert path_list[0].position[0] == pytest.approx(0)
    assert path_list[0].position[1] == pytest.approx(0)
    assert path_list[1].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 9 +
        [{'action': 'MoveAhead', 'params': {}}]
    )
    assert path_list[1].rotation == 90
    assert path_list[1].position[0] == pytest.approx(0)
    assert path_list[1].position[1] == pytest.approx(0.1)


def test_rotate_then_move():
    # 180 degree rotation is facing west in shapely
    path = optimal_path.ShortestPath([], (0, 0), 180)
    path_list = optimal_path._rotate_then_move(path, (0, 4))
    assert len(path_list) == 1
    assert path_list[0].action_list == (
        [{'action': 'RotateRight', 'params': {}}] * 9 +
        [{'action': 'MoveAhead', 'params': {}}] * 40
    )
    assert path_list[0].rotation == 90
    assert path_list[0].position[0] == pytest.approx(0)
    assert path_list[0].position[1] == pytest.approx(4)


def test_rotate_then_move_multiple_path_move():
    # 0 degree rotation is facing east in shapely
    path = optimal_path.ShortestPath([], (0, 0), 0)
    path_list = optimal_path._rotate_then_move(path, (0.94, 0))
    assert len(path_list) == 2
    assert path_list[0].action_list == (
        [{'action': 'MoveAhead', 'params': {}}] * 9
    )
    assert path_list[0].rotation == 0
    assert path_list[0].position[0] == pytest.approx(0.9)
    assert path_list[0].position[1] == pytest.approx(0)
    assert path_list[1].action_list == (
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[1].rotation == 0
    assert path_list[1].position[0] == pytest.approx(1.0)
    assert path_list[1].position[1] == pytest.approx(0)


def test_rotate_then_move_multiple_path_rotate_left():
    path = optimal_path.ShortestPath([], (0, 0), -44)
    path_list = optimal_path._rotate_then_move(path, (1, 0))
    assert len(path_list) == 2
    assert path_list[0].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 4 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[0].rotation == -4
    assert path_list[0].position[0] == pytest.approx(0.997564)
    assert path_list[0].position[1] == pytest.approx(-0.0697565)
    assert path_list[1].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 5 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[1].rotation == 6
    assert path_list[1].position[0] == pytest.approx(0.994522)
    assert path_list[1].position[1] == pytest.approx(0.1045285)


def test_rotate_then_move_multiple_path_rotate_right():
    path = optimal_path.ShortestPath([], (0, 0), 44)
    path_list = optimal_path._rotate_then_move(path, (1, 0))
    assert len(path_list) == 2
    assert path_list[0].action_list == (
        [{'action': 'RotateRight', 'params': {}}] * 4 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[0].rotation == 4
    assert path_list[0].position[0] == pytest.approx(0.997564)
    assert path_list[0].position[1] == pytest.approx(0.0697565)
    assert path_list[1].action_list == (
        [{'action': 'RotateRight', 'params': {}}] * 5 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[1].rotation == -6
    assert path_list[1].position[0] == pytest.approx(0.994522)
    assert path_list[1].position[1] == pytest.approx(-0.1045285)


def test_rotate_then_move_multiple_path_both_rotate_move():
    path = optimal_path.ShortestPath([], (0, 0), -44)
    path_list = optimal_path._rotate_then_move(path, (1.04, 0))
    assert len(path_list) == 4
    assert path_list[0].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 4 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[0].rotation == -4
    assert path_list[0].position[0] == pytest.approx(0.997564)
    assert path_list[0].position[1] == pytest.approx(-0.0697565)
    assert path_list[1].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 4 +
        [{'action': 'MoveAhead', 'params': {}}] * 11
    )
    assert path_list[1].rotation == -4
    assert path_list[1].position[0] == pytest.approx(1.09732)
    assert path_list[1].position[1] == pytest.approx(-0.0767321)
    assert path_list[2].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 5 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[2].rotation == 6
    assert path_list[2].position[0] == pytest.approx(0.994522)
    assert path_list[2].position[1] == pytest.approx(0.1045285)
    assert path_list[3].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 5 +
        [{'action': 'MoveAhead', 'params': {}}] * 11
    )
    assert path_list[3].rotation == 6
    assert path_list[3].position[0] == pytest.approx(1.093974)
    assert path_list[3].position[1] == pytest.approx(0.1149813)


def test_rotate_then_move_rotate_less():
    path = optimal_path.ShortestPath([], (0, 0), -41)
    path_list = optimal_path._rotate_then_move(path, (1, 0))
    assert len(path_list) == 3
    assert path_list[0].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 4 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[0].rotation == -1
    assert path_list[0].position[0] == pytest.approx(0.999848)
    assert path_list[0].position[1] == pytest.approx(-0.0174524)
    assert path_list[1].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 5 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[1].rotation == 9
    assert path_list[1].position[0] == pytest.approx(0.987688)
    assert path_list[1].position[1] == pytest.approx(0.1564345)
    assert path_list[2].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 3 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[2].rotation == -11
    assert path_list[2].position[0] == pytest.approx(0.981627)
    assert path_list[2].position[1] == pytest.approx(-0.190809)


def test_rotate_then_move_rotate_more():
    path = optimal_path.ShortestPath([], (0, 0), -49)
    path_list = optimal_path._rotate_then_move(path, (1, 0))
    assert len(path_list) == 3
    assert path_list[0].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 4 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[0].rotation == -9
    assert path_list[0].position[0] == pytest.approx(0.987688)
    assert path_list[0].position[1] == pytest.approx(-0.1564344)
    assert path_list[1].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 5 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[1].rotation == 1
    assert path_list[1].position[0] == pytest.approx(0.999848)
    assert path_list[1].position[1] == pytest.approx(0.0174524)
    assert path_list[2].action_list == (
        [{'action': 'RotateLeft', 'params': {}}] * 6 +
        [{'action': 'MoveAhead', 'params': {}}] * 10
    )
    assert path_list[2].rotation == 11
    assert path_list[2].position[0] == pytest.approx(0.981627)
    assert path_list[2].position[1] == pytest.approx(0.190809)
