import math

import pytest
import shapely

from generator import DefinitionDataset, geometry, specific_objects
from generator.separating_axis_theorem import sat_entry

DEFAULT_ROOM_X_MAX = (geometry.DEFAULT_ROOM_DIMENSIONS['x'] / 2.0)
DEFAULT_ROOM_Z_MAX = (geometry.DEFAULT_ROOM_DIMENSIONS['z'] / 2.0)
DEFAULT_ROOM_X_MIN = -DEFAULT_ROOM_X_MAX
DEFAULT_ROOM_Z_MIN = -DEFAULT_ROOM_Z_MAX


DATASET = specific_objects.get_interactable_definition_dataset(unshuffled=True)
ALL_DEFINITIONS = [
    # Just use the first variation (color) of each object for faster testing.
    definition_variations[0]
    for definition_selections in DATASET._definition_groups
    for definition_variations in definition_selections
]
# Reassign the dataset to use the filtered definition list for faster testing.
DATASET = DefinitionDataset([[ALL_DEFINITIONS]])


# Use the sofa because it should obstruct any pickupable object.
LARGEST_OBJECT = [
    item for item in ALL_DEFINITIONS if item.type == 'sofa_1' and
    vars(item.scale) == {'x': 1, 'y': 1, 'z': 1}
][0]


# Use the pacifier because it shouldn't obstruct any pickupable object.
SMALLEST_OBJECT = [
    item for item in ALL_DEFINITIONS if item.type == 'pacifier' and
    vars(item.scale) == {'x': 1, 'y': 1, 'z': 1}
][0]


def test_collision():
    a = {'x': 1, 'y': 0, 'z': 1}
    b = {'x': 1, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': -1}
    d = {'x': -1, 'y': 0, 'z': 1}

    rect = [a, b, c, d]
    p0 = {'x': 0, 'y': 0, 'z': 0}
    p1 = {'x': 11, 'y': 0, 'z': 11}

    assert geometry.collision(rect, p0) is True
    assert geometry.collision(rect, p1) is False


def test_rect_intersection():
    A = [{'x': 0, 'y': 0, 'z': 0}, {'x': 1, 'y': 0, 'z': 0},
         {'x': 1, 'y': 0, 'z': 1}, {'x': 0, 'y': 0, 'z': 1}]
    B = [{'x': .25, 'y': 0, 'z': .25}, {'x': .75, 'y': 0, 'z': .25},
         {'x': .75, 'y': 0, 'z': .75},
         {'x': .25, 'y': 0, 'z': .75}]
    C = [{'x': .8, 'y': 0, 'z': 1.2}, {'x': 1.1, 'y': 0, 'z': 1.8},
         {'x': 2, 'y': 0, 'z': 1.5},
         {'x': 1.1, 'y': 0, 'z': .3}]
    D = [{'x': 1, 'y': 0, 'z': 0}, {'x': 2, 'y': 0, 'z': 1.5},
         {'x': 3, 'y': 0, 'z': 0}, {'x': 2, 'y': 0, 'z': -1.5}]
    # A intersects B,C,D. B ints A , C ints A & D, D ints A C
    # Testing transitivity as well
    assert sat_entry(A, B) is True
    assert sat_entry(A, D) is True
    assert sat_entry(C, B) is False
    assert sat_entry(D, C) is True
    assert sat_entry(B, C) is False
    assert sat_entry(A, C) is True
    assert sat_entry(C, A) is True


def test_rect_within_room():
    valid_1 = {'x': 0, 'z': 0}
    valid_2 = {'x': 5, 'z': 5}
    valid_3 = {'x': 5, 'z': -5}
    valid_4 = {'x': -5, 'z': -5}
    valid_5 = {'x': -5, 'z': 5}
    valid_6 = {'x': 0.1, 'z': 0.1}
    invalid_1 = {'x': 5.1, 'z': 0}
    invalid_2 = {'x': -5.1, 'z': 0}
    invalid_3 = {'x': 0, 'z': 5.1}
    invalid_4 = {'x': 0, 'z': -5.1}
    assert geometry.rect_within_room([
        valid_1, valid_2, valid_3, valid_4, valid_5, valid_6
    ], geometry.DEFAULT_ROOM_DIMENSIONS)
    assert geometry.rect_within_room([
        valid_1, valid_2, valid_3, valid_4, valid_5, valid_6, invalid_1
    ], geometry.DEFAULT_ROOM_DIMENSIONS) is False
    assert geometry.rect_within_room([
        valid_1, valid_2, valid_3, valid_4, valid_5, valid_6, invalid_2
    ], geometry.DEFAULT_ROOM_DIMENSIONS) is False
    assert geometry.rect_within_room([
        valid_1, valid_2, valid_3, valid_4, valid_5, valid_6, invalid_3
    ], geometry.DEFAULT_ROOM_DIMENSIONS) is False
    assert geometry.rect_within_room([
        valid_1, valid_2, valid_3, valid_4, valid_5, valid_6, invalid_4
    ], geometry.DEFAULT_ROOM_DIMENSIONS) is False
    assert geometry.rect_within_room([
        invalid_1, invalid_2, invalid_3, invalid_4
    ], geometry.DEFAULT_ROOM_DIMENSIONS) is False


def test_mcs_157():
    bounding_box = [
        {
            "x": -1.0257359312880716,
            "y": 0,
            "z": -6.05350288425444
        },
        {
            "x": -2.7935028842544405,
            "y": 0,
            "z": -4.285735931288071
        },
        {
            "x": -1.8742640687119283,
            "y": 0,
            "z": -3.3664971157455597
        },
        {
            "x": -0.10649711574555965,
            "y": 0,
            "z": -5.1342640687119285
        }
    ]
    assert geometry.rect_within_room(
        bounding_box,
        geometry.DEFAULT_ROOM_DIMENSIONS
    ) is False


def test_calc_obj_coords_identity():

    a = {'x': 2, 'y': 0, 'z': 2}
    b = {'x': 2, 'y': 0, 'z': -2}
    c = {'x': -2, 'y': 0, 'z': -2}
    d = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=0,
                                                          position_z=0,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=0,
                                                          offset_z=0,
                                                          rotation=0)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, None, {'x': 0, 'z': 0}, {'y': 0})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotate90():

    d = {'x': 2, 'y': 0, 'z': 2}
    a = {'x': 2, 'y': 0, 'z': -2}
    b = {'x': -2, 'y': 0, 'z': -2}
    c = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=0,
                                                          position_z=0,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=0,
                                                          offset_z=0,
                                                          rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, None, {'x': 0, 'z': 0}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotate180():

    c = {'x': 2, 'y': 0, 'z': 2}
    d = {'x': 2, 'y': 0, 'z': -2}
    a = {'x': -2, 'y': 0, 'z': -2}
    b = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=0,
                                                          position_z=0,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=0,
                                                          offset_z=0,
                                                          rotation=180)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, None, {'x': 0, 'z': 0}, {'y': 180})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotate270():

    b = {'x': 2, 'y': 0, 'z': 2}
    c = {'x': 2, 'y': 0, 'z': -2}
    d = {'x': -2, 'y': 0, 'z': -2}
    a = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=0,
                                                          position_z=0,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=0,
                                                          offset_z=0,
                                                          rotation=270)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, None, {'x': 0, 'z': 0}, {'y': 270})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_nonorigin_identity():

    a = {'x': 3, 'y': 0, 'z': 3}
    b = {'x': 3, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': -1}
    d = {'x': -1, 'y': 0, 'z': 3}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=1,
                                                          position_z=1,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=0,
                                                          offset_z=0,
                                                          rotation=0)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, None, {'x': 1, 'z': 1}, {'y': 0})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_nonorigin_rotate90():

    d = {'x': 3, 'y': 0, 'z': 3}
    a = {'x': 3, 'y': 0, 'z': -1}
    b = {'x': -1, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': 3}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=1,
                                                          position_z=1,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=0,
                                                          offset_z=0,
                                                          rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, None, {'x': 1, 'z': 1}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_identity_offset():

    a = {'x': 3, 'y': 0, 'z': 3}
    b = {'x': 3, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': -1}
    d = {'x': -1, 'y': 0, 'z': 3}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=0,
                                                          position_z=0,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=1,
                                                          offset_z=1,
                                                          rotation=0)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 0, 'z': 0}, {'y': 0})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotation90_offset():

    d = {'x': 3, 'y': 0, 'z': 1}
    a = {'x': 3, 'y': 0, 'z': -3}
    b = {'x': -1, 'y': 0, 'z': -3}
    c = {'x': -1, 'y': 0, 'z': 1}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=0,
                                                          position_z=0,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=1,
                                                          offset_z=1,
                                                          rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 0, 'z': 0}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotation90_offset_position_x():

    d = {'x': 10, 'y': 0, 'z': 1}
    a = {'x': 10, 'y': 0, 'z': -3}
    b = {'x': 6, 'y': 0, 'z': -3}
    c = {'x': 6, 'y': 0, 'z': 1}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=7,
                                                          position_z=0,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=1,
                                                          offset_z=1,
                                                          rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 7, 'z': 0}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotation90_offset_position_z():

    d = {'x': 3, 'y': 0, 'z': 8}
    a = {'x': 3, 'y': 0, 'z': 4}
    b = {'x': -1, 'y': 0, 'z': 4}
    c = {'x': -1, 'y': 0, 'z': 8}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=0,
                                                          position_z=7,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=1,
                                                          offset_z=1,
                                                          rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 0, 'z': 7}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotation90_offset_position_xz():

    d = {'x': 10, 'y': 0, 'z': 8}
    a = {'x': 10, 'y': 0, 'z': 4}
    b = {'x': 6, 'y': 0, 'z': 4}
    c = {'x': 6, 'y': 0, 'z': 8}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=7,
                                                          position_z=7,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=1,
                                                          offset_z=1,
                                                          rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 7, 'z': 7}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotation45_offset_position_xz():

    d = {'x': 8.41421, 'y': 0, 'z': 9.82843}
    a = {'x': 11.24264, 'y': 0, 'z': 7}
    b = {'x': 8.41421, 'y': 0, 'z': 4.17157}
    c = {'x': 5.58579, 'y': 0, 'z': 7}
    new_a, new_b, new_c, new_d = geometry.calc_obj_coords(position_x=7,
                                                          position_z=7,
                                                          delta_x=2,
                                                          delta_z=2,
                                                          offset_x=1,
                                                          offset_z=1,
                                                          rotation=45)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = geometry.generate_object_bounds(
        {'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 7, 'z': 7}, {'y': 45})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_object_collision():
    r1 = geometry.calc_obj_coords(-1.97, 1.75, .55, .445, -.01, .445, 315)
    r2 = geometry.calc_obj_coords(-3.04, .85, 1.75, .05, 0, 0, 315)
    assert sat_entry(r1, r2)
    r3 = geometry.calc_obj_coords(.04, .85, 1.75, .05, 0, 0, 315)
    assert not sat_entry(r1, r3)


def test_get_visible_segment():
    actual = geometry._get_visible_segment(
        {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 0}},
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    expected = shapely.geometry.LineString(
        [[0, geometry.MIN_FORWARD_VISIBILITY_DISTANCE],
         [0, DEFAULT_ROOM_Z_MAX]]
    )
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = geometry._get_visible_segment(
        {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 45}},
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    expected = shapely.geometry.LineString(
        [
            [
                math.sqrt(2) / 2.0 * geometry.MIN_FORWARD_VISIBILITY_DISTANCE,
                math.sqrt(2) / 2.0 * geometry.MIN_FORWARD_VISIBILITY_DISTANCE
            ],
            [DEFAULT_ROOM_X_MAX, DEFAULT_ROOM_Z_MAX]
        ]
    )
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = geometry._get_visible_segment(
        {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 90}},
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    expected = shapely.geometry.LineString(
        [[geometry.MIN_FORWARD_VISIBILITY_DISTANCE, 0],
         [DEFAULT_ROOM_X_MAX, 0]]
    )
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = geometry._get_visible_segment(
        {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 135}},
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    expected = shapely.geometry.LineString(
        [
            [
                math.sqrt(2) / 2.0 * geometry.MIN_FORWARD_VISIBILITY_DISTANCE,
                -math.sqrt(2) / 2.0 * geometry.MIN_FORWARD_VISIBILITY_DISTANCE
            ],
            [DEFAULT_ROOM_X_MAX, -DEFAULT_ROOM_Z_MAX]
        ]
    )
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)

    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = geometry._get_visible_segment(
        {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 180}},
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    expected = shapely.geometry.LineString(
        [[0, -geometry.MIN_FORWARD_VISIBILITY_DISTANCE],
         [0, -DEFAULT_ROOM_Z_MAX]]
    )
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = geometry._get_visible_segment(
        {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 225}},
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    expected = shapely.geometry.LineString(
        [
            [
                -math.sqrt(2) / 2.0 * geometry.MIN_FORWARD_VISIBILITY_DISTANCE,
                -math.sqrt(2) / 2.0 * geometry.MIN_FORWARD_VISIBILITY_DISTANCE
            ],
            [-DEFAULT_ROOM_X_MAX, -DEFAULT_ROOM_Z_MAX]
        ]
    )
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = geometry._get_visible_segment(
        {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 270}},
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    expected = shapely.geometry.LineString(
        [[-geometry.MIN_FORWARD_VISIBILITY_DISTANCE, 0],
         [-DEFAULT_ROOM_X_MAX, 0]]
    )
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = geometry._get_visible_segment(
        {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 315}},
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    expected = shapely.geometry.LineString(
        [
            [
                -math.sqrt(2) / 2.0 * geometry.MIN_FORWARD_VISIBILITY_DISTANCE,
                math.sqrt(2) / 2.0 * geometry.MIN_FORWARD_VISIBILITY_DISTANCE
            ],
            [-DEFAULT_ROOM_X_MAX, DEFAULT_ROOM_Z_MAX]
        ]
    )
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])


def test_get_visible_segment_with_position():
    actual = geometry._get_visible_segment(
        {'position': {'x': 1, 'y': 0, 'z': 1}, 'rotation': {'y': 45}},
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    expected = shapely.geometry.LineString(
        [
            [
                math.sqrt(2) / 2.0 *
                geometry.MIN_FORWARD_VISIBILITY_DISTANCE + 1,
                math.sqrt(2) / 2.0 *
                geometry.MIN_FORWARD_VISIBILITY_DISTANCE + 1
            ],
            [DEFAULT_ROOM_X_MAX, DEFAULT_ROOM_Z_MAX]
        ]
    )
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = geometry._get_visible_segment(
        {'position': {'x': -5, 'y': 0, 'z': -5}, 'rotation': {'y': 45}},
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    expected = shapely.geometry.LineString(
        [
            [
                math.sqrt(2) / 2.0 *
                geometry.MIN_FORWARD_VISIBILITY_DISTANCE - 5,
                math.sqrt(2) / 2.0 *
                geometry.MIN_FORWARD_VISIBILITY_DISTANCE - 5
            ],
            [DEFAULT_ROOM_X_MAX, DEFAULT_ROOM_Z_MAX]
        ]
    )
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    assert (
        geometry._get_visible_segment(
            {'position': {'x': 4.5, 'y': 0, 'z': 0}, 'rotation': {'y': 45}},
            geometry.DEFAULT_ROOM_DIMENSIONS
        )
        is None
    )
    assert (
        geometry._get_visible_segment(
            {'position': {'x': 0, 'y': 0, 'z': 4.5}, 'rotation': {'y': 45}},
            geometry.DEFAULT_ROOM_DIMENSIONS
        )
        is None
    )
    assert (
        geometry._get_visible_segment(
            {'position': {'x': 4.5, 'y': 0, 'z': 4.5}, 'rotation': {'y': 45}},
            geometry.DEFAULT_ROOM_DIMENSIONS
        )
        is None
    )
    assert (
        geometry._get_visible_segment(
            {'position': {'x': 5, 'y': 0, 'z': 0}, 'rotation': {'y': 45}},
            geometry.DEFAULT_ROOM_DIMENSIONS
        )
        is None
    )


def test_get_position_in_front_of_performer():
    performer_start = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'y': 0}}

    for target_definition in ALL_DEFINITIONS:
        target_half_size_x = (target_definition.dimensions.x / 2.0)
        target_half_size_z = (target_definition.dimensions.z / 2.0)

        performer_start['rotation']['y'] = 0
        positive_z = geometry.get_location_in_front_of_performer(
            performer_start, target_definition)
        assert 0 <= positive_z['position']['z']
        assert positive_z['position']['z'] <= DEFAULT_ROOM_Z_MAX
        assert -target_half_size_x <= positive_z['position']['x']
        assert positive_z['position']['x'] <= target_half_size_x
        assert geometry.get_bounding_polygon(positive_z).intersection(
            shapely.geometry.LineString([[0, 1], [0, DEFAULT_ROOM_Z_MAX]]))

        performer_start['rotation']['y'] = 90
        positive_x = geometry.get_location_in_front_of_performer(
            performer_start, target_definition)
        assert 0 <= positive_x['position']['x']
        assert positive_x['position']['x'] <= DEFAULT_ROOM_X_MAX
        assert -target_half_size_z <= positive_x['position']['z']
        assert positive_x['position']['z'] <= target_half_size_z
        assert geometry.get_bounding_polygon(positive_x).intersection(
            shapely.geometry.LineString([[1, 0], [DEFAULT_ROOM_X_MAX, 0]]))

        performer_start['rotation']['y'] = 180
        negative_z = geometry.get_location_in_front_of_performer(
            performer_start, target_definition)
        assert DEFAULT_ROOM_Z_MIN <= negative_z['position']['z']
        assert negative_z['position']['z'] <= 0
        assert -target_half_size_x <= negative_z['position']['x']
        assert negative_z['position']['x'] <= target_half_size_x
        assert geometry.get_bounding_polygon(negative_z).intersection(
            shapely.geometry.LineString([[0, -1], [0, -DEFAULT_ROOM_Z_MAX]]))

        performer_start['rotation']['y'] = 270
        negative_x = geometry.get_location_in_front_of_performer(
            performer_start, target_definition)
        assert DEFAULT_ROOM_X_MIN <= negative_x['position']['x']
        assert negative_x['position']['x'] <= 0
        assert -target_half_size_z <= negative_x['position']['z']
        assert negative_x['position']['z'] <= target_half_size_z
        assert geometry.get_bounding_polygon(negative_x).intersection(
            shapely.geometry.LineString([[-1, 0], [-DEFAULT_ROOM_X_MAX, 0]]))


def test_get_position_in_front_of_performer_next_to_room_wall():
    performer_start = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'y': 0}}

    for target_definition in ALL_DEFINITIONS:
        performer_start['position']['z'] = DEFAULT_ROOM_Z_MAX
        location = geometry.get_location_in_front_of_performer(
            performer_start, target_definition)
        assert location is None


def test_get_position_in_back_of_performer():
    performer_start = {
        'position': {'x': 0, 'y': 0, 'z': 0},
        'rotation': {'y': 0}
    }

    for target_definition in ALL_DEFINITIONS:
        target_half_x = (target_definition.dimensions.x / 2.0)
        target_half_z = (target_definition.dimensions.z / 2.0)
        min_x = DEFAULT_ROOM_X_MIN + target_half_x - 0.05
        max_x = DEFAULT_ROOM_X_MAX - target_half_x + 0.05
        min_z = DEFAULT_ROOM_Z_MIN + target_half_z - 0.05
        max_z = DEFAULT_ROOM_Z_MAX - target_half_z + 0.05
        rear = shapely.geometry.box(
            -(DEFAULT_ROOM_X_MAX - DEFAULT_ROOM_X_MIN),
            -(DEFAULT_ROOM_Z_MAX - DEFAULT_ROOM_Z_MIN),
            (DEFAULT_ROOM_X_MAX - DEFAULT_ROOM_X_MIN),
            -target_half_z
        )
        room = shapely.geometry.box(min_x, min_z, max_x, max_z)

        performer_start['rotation']['y'] = 0
        rear_poly = shapely.affinity.rotate(rear, 0, origin=(0, 0))
        rear_poly = rear_poly.intersection(room)
        negative_z = geometry.get_location_in_back_of_performer(
            performer_start, target_definition)
        assert shapely.geometry.Point(
            negative_z['position']['x'],
            negative_z['position']['z']
        ).within(rear_poly)
        assert -target_half_z >= negative_z['position']['z']
        assert negative_z['position']['z'] >= min_z
        assert max_x >= negative_z['position']['x']
        assert negative_z['position']['x'] >= min_x

        performer_start['rotation']['y'] = 45
        rear_poly = shapely.affinity.rotate(rear, -45, origin=(0, 0))
        rear_poly = rear_poly.intersection(room)
        location = geometry.get_location_in_back_of_performer(
            performer_start, target_definition)
        assert shapely.geometry.Point(
            location['position']['x'],
            location['position']['z']
        ).within(rear_poly)

        performer_start['rotation']['y'] = 90
        rear_poly = shapely.affinity.rotate(rear, -90, origin=(0, 0))
        rear_poly = rear_poly.intersection(room)
        negative_x = geometry.get_location_in_back_of_performer(
            performer_start, target_definition)
        assert shapely.geometry.Point(
            negative_x['position']['x'],
            negative_x['position']['z']
        ).within(rear_poly)
        assert -target_half_x >= negative_x['position']['x']
        assert negative_x['position']['x'] >= min_x
        assert max_z >= negative_x['position']['z']
        assert negative_x['position']['z'] >= min_z

        performer_start['rotation']['y'] = 135
        rear_poly = shapely.affinity.rotate(rear, -135, origin=(0, 0))
        rear_poly = rear_poly.intersection(room)
        location = geometry.get_location_in_back_of_performer(
            performer_start, target_definition)
        assert shapely.geometry.Point(
            location['position']['x'],
            location['position']['z']
        ).within(rear_poly)

        performer_start['rotation']['y'] = 180
        rear_poly = shapely.affinity.rotate(rear, -180, origin=(0, 0))
        rear_poly = rear_poly.intersection(room)
        positive_z = geometry.get_location_in_back_of_performer(
            performer_start, target_definition)
        assert shapely.geometry.Point(
            positive_z['position']['x'],
            positive_z['position']['z']
        ).within(rear_poly)
        assert max_z >= positive_z['position']['z']
        assert positive_z['position']['z'] >= target_half_z
        assert max_x >= positive_z['position']['x']
        assert positive_z['position']['x'] >= min_x

        performer_start['rotation']['y'] = 225
        rear_poly = shapely.affinity.rotate(rear, -225, origin=(0, 0))
        rear_poly = rear_poly.intersection(room)
        location = geometry.get_location_in_back_of_performer(
            performer_start, target_definition)
        assert shapely.geometry.Point(
            location['position']['x'],
            location['position']['z']
        ).within(rear_poly)

        performer_start['rotation']['y'] = 270
        rear_poly = shapely.affinity.rotate(rear, -270, origin=(0, 0))
        rear_poly = rear_poly.intersection(room)
        positive_x = geometry.get_location_in_back_of_performer(
            performer_start, target_definition)
        assert shapely.geometry.Point(
            positive_x['position']['x'],
            positive_x['position']['z']
        ).within(rear_poly)
        assert max_x >= positive_x['position']['x']
        assert positive_x['position']['x'] >= target_half_x
        assert max_z >= positive_x['position']['z']
        assert positive_x['position']['z'] >= min_z

        performer_start['rotation']['y'] = 315
        rear_poly = shapely.affinity.rotate(rear, -315, origin=(0, 0))
        rear_poly = rear_poly.intersection(room)
        location = geometry.get_location_in_back_of_performer(
            performer_start, target_definition)
        assert shapely.geometry.Point(
            location['position']['x'],
            location['position']['z']
        ).within(rear_poly)


def test_get_position_in_back_of_performer_next_to_room_wall():
    performer_start = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'y': 0}}

    for target_definition in ALL_DEFINITIONS:
        performer_start['position']['z'] = DEFAULT_ROOM_Z_MIN
        location = geometry.get_location_in_back_of_performer(
            performer_start, target_definition)
        assert location is None


def test_are_adjacent():
    dimensions = {'x': 2, 'y': 2, 'z': 2}

    center = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    center['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, center['position'], center['rotation'])

    good_1 = {
        'position': {
            'x': 2, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_1['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, good_1['position'], good_1['rotation'])
    assert geometry.are_adjacent(center, good_1)

    good_2 = {
        'position': {
            'x': -2,
            'y': 0,
            'z': 0},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    good_2['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, good_2['position'], good_2['rotation'])
    assert geometry.are_adjacent(center, good_2)

    good_3 = {
        'position': {
            'x': 0, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_3['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, good_3['position'], good_3['rotation'])
    assert geometry.are_adjacent(center, good_3)

    good_4 = {
        'position': {
            'x': 0,
            'y': 0,
            'z': -2},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    good_4['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, good_4['position'], good_4['rotation'])
    assert geometry.are_adjacent(center, good_4)

    good_5 = {
        'position': {
            'x': 2, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_5['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, good_5['position'], good_5['rotation'])
    assert geometry.are_adjacent(center, good_5)

    good_6 = {
        'position': {
            'x': 2,
            'y': 0,
            'z': -2},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    good_6['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, good_6['position'], good_6['rotation'])
    assert geometry.are_adjacent(center, good_6)

    good_7 = {
        'position': {
            'x': -2,
            'y': 0,
            'z': 2},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    good_7['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, good_7['position'], good_7['rotation'])
    assert geometry.are_adjacent(center, good_7)

    good_8 = {
        'position': {
            'x': -2,
            'y': 0,
            'z': -2},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    good_8['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, good_8['position'], good_8['rotation'])
    assert geometry.are_adjacent(center, good_8)

    bad_1 = {
        'position': {
            'x': 3, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_1['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, bad_1['position'], bad_1['rotation'])
    assert not geometry.are_adjacent(center, bad_1)

    bad_2 = {
        'position': {
            'x': -3,
            'y': 0,
            'z': 0},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    bad_2['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, bad_2['position'], bad_2['rotation'])
    assert not geometry.are_adjacent(center, bad_2)

    bad_3 = {
        'position': {
            'x': 0, 'y': 0, 'z': 3}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_3['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, bad_3['position'], bad_3['rotation'])
    assert not geometry.are_adjacent(center, bad_3)

    bad_4 = {
        'position': {
            'x': 0,
            'y': 0,
            'z': -3},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    bad_4['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, bad_4['position'], bad_4['rotation'])
    assert not geometry.are_adjacent(center, bad_4)

    bad_5 = {
        'position': {
            'x': 2.5, 'y': 0, 'z': 2.5}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_5['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, bad_5['position'], bad_5['rotation'])
    assert not geometry.are_adjacent(center, bad_5)

    bad_6 = {
        'position': {
            'x': 2.5,
            'y': 0,
            'z': -2.5},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    bad_6['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, bad_6['position'], bad_6['rotation'])
    assert not geometry.are_adjacent(center, bad_6)

    bad_7 = {
        'position': {
            'x': -2.5,
            'y': 0,
            'z': 2.5},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    bad_7['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, bad_7['position'], bad_7['rotation'])
    assert not geometry.are_adjacent(center, bad_7)

    bad_8 = {
        'position': {
            'x': -2.5,
            'y': 0,
            'z': -2.5},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    bad_8['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, bad_8['position'], bad_8['rotation'])
    assert not geometry.are_adjacent(center, bad_8)


def test_are_adjacent_with_offset():
    dimensions = {'x': 2, 'y': 2, 'z': 2}
    offset = {'x': -1, 'y': 0, 'z': 1}

    center = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    center['boundingBox'] = geometry.generate_object_bounds(
        dimensions, None, center['position'], center['rotation'])

    good_1 = {
        'position': {
            'x': 3, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_1['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, good_1['position'], good_1['rotation'])
    assert geometry.are_adjacent(center, good_1)

    good_2 = {
        'position': {
            'x': -1,
            'y': 0,
            'z': 0},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    good_2['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, good_2['position'], good_2['rotation'])
    assert geometry.are_adjacent(center, good_2)

    good_3 = {
        'position': {
            'x': 0, 'y': 0, 'z': 1}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_3['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, good_3['position'], good_3['rotation'])
    assert geometry.are_adjacent(center, good_3)

    good_4 = {
        'position': {
            'x': 0,
            'y': 0,
            'z': -3},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    good_4['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, good_4['position'], good_4['rotation'])
    assert geometry.are_adjacent(center, good_4)

    good_5 = {
        'position': {
            'x': 3, 'y': 0, 'z': 1}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_5['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, good_5['position'], good_5['rotation'])
    assert geometry.are_adjacent(center, good_5)

    good_6 = {
        'position': {
            'x': 3,
            'y': 0,
            'z': -3},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    good_6['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, good_6['position'], good_6['rotation'])
    assert geometry.are_adjacent(center, good_6)

    good_7 = {
        'position': {
            'x': -1,
            'y': 0,
            'z': 1},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    good_7['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, good_7['position'], good_7['rotation'])
    assert geometry.are_adjacent(center, good_7)

    good_8 = {
        'position': {
            'x': -1,
            'y': 0,
            'z': -3},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    good_8['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, good_8['position'], good_8['rotation'])
    assert geometry.are_adjacent(center, good_8)

    bad_1 = {
        'position': {
            'x': 4, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_1['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, bad_1['position'], bad_1['rotation'])
    assert not geometry.are_adjacent(center, bad_1)

    bad_2 = {
        'position': {
            'x': -2,
            'y': 0,
            'z': 0},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    bad_2['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, bad_2['position'], bad_2['rotation'])
    assert not geometry.are_adjacent(center, bad_2)

    bad_3 = {
        'position': {
            'x': 0, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_3['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, bad_3['position'], bad_3['rotation'])
    assert not geometry.are_adjacent(center, bad_3)

    bad_4 = {
        'position': {
            'x': 0,
            'y': 0,
            'z': -4},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    bad_4['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, bad_4['position'], bad_4['rotation'])
    assert not geometry.are_adjacent(center, bad_4)

    bad_5 = {
        'position': {
            'x': 3.5, 'y': 0, 'z': 1.5}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_5['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, bad_5['position'], bad_5['rotation'])
    assert not geometry.are_adjacent(center, bad_5)

    bad_6 = {
        'position': {
            'x': 3.5,
            'y': 0,
            'z': -3.5},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    bad_6['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, bad_6['position'], bad_6['rotation'])
    assert not geometry.are_adjacent(center, bad_6)

    bad_7 = {
        'position': {
            'x': -1.5,
            'y': 0,
            'z': 1.5},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    bad_7['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, bad_7['position'], bad_7['rotation'])
    assert not geometry.are_adjacent(center, bad_7)

    bad_8 = {
        'position': {
            'x': -1.5,
            'y': 0,
            'z': -3.5},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    bad_8['boundingBox'] = geometry.generate_object_bounds(
        dimensions, offset, bad_8['position'], bad_8['rotation'])
    assert not geometry.are_adjacent(center, bad_8)


def test_generate_location_in_line_with_object():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': 0, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_location = {
            # Ensure object X equals performer start X in this test.
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )
        object_1_poly = geometry.get_bounding_polygon(object_1_location)
        object_1_offset = vars(object_1_definition.offset)

        for object_2_definition in [LARGEST_OBJECT, SMALLEST_OBJECT]:
            object_2_offset = vars(object_2_definition.offset)
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                []
            )
            assert location
            object_2_poly = geometry.get_bounding_polygon(location)
            # Location is close to 1st object.
            assert object_2_poly.distance(object_1_poly) < 0.105
            # Location is in the room and does not overlap with 1st object.
            assert geometry.validate_location_rect(
                location['boundingBox'],
                performer_start['position'],
                [object_1_location['boundingBox']],
                geometry.DEFAULT_ROOM_DIMENSIONS
            )
            # Location is orthogonal on the Z axis to 1st object.
            assert (
                object_1_location['position']['x'] + object_1_offset['x'] ==
                pytest.approx(location['position']['x'] + object_2_offset['x'])
            )
            # Location is anywhere in front of 1st object.
            assert (
                object_1_location['position']['z'] + object_1_offset['z'] >
                location['position']['z'] + object_2_offset['z']
            )
            assert geometry.does_partly_obstruct_target(
                performer_start['position'],
                object_1_location,
                object_2_poly
            )


def test_generate_location_in_line_with_object_too_close():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': 0, 'y': 0, 'z': 0},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_half_z = (
            object_1_definition.dimensions.z / 2.0
        )
        object_1_location = {
            # Ensure object is directly in front of performer start location.
            'position': {'x': 0, 'y': 0, 'z': object_1_half_z},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )

        for object_2_definition in [LARGEST_OBJECT, SMALLEST_OBJECT]:
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                []
            )
            assert not location


def test_generate_location_in_line_with_object_too_close_diagonal():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': 0, 'y': 0, 'z': 0},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_half_x = (
            object_1_definition.dimensions.x / 2.0
        )
        object_1_half_z = (
            object_1_definition.dimensions.z / 2.0
        )
        object_1_location = {
            # Ensure object is directly in front of performer start location.
            'position': {'x': object_1_half_x, 'y': 0, 'z': object_1_half_z},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )

        for object_2_definition in [LARGEST_OBJECT, SMALLEST_OBJECT]:
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                []
            )
            assert not location


def test_generate_location_in_line_with_object_diagonal():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': -4.5, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_location = {
            # Ensure object location is diagonal in this test.
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )
        object_1_poly = geometry.get_bounding_polygon(object_1_location)
        object_1_offset = vars(object_1_definition.offset)

        for object_2_definition in [LARGEST_OBJECT, SMALLEST_OBJECT]:
            object_2_offset = vars(object_2_definition.offset)
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                []
            )
            assert location
            object_2_poly = geometry.get_bounding_polygon(location)
            # Location is close to 1st object.
            assert object_2_poly.distance(object_1_poly) < 0.105
            # Location is in the room and does not overlap with 1st object.
            assert geometry.validate_location_rect(
                location['boundingBox'],
                performer_start['position'],
                [object_1_location['boundingBox']],
                geometry.DEFAULT_ROOM_DIMENSIONS
            )
            # Location is on the diagonal line from the performer start.
            assert (
                round(location['position']['x'] + object_2_offset['x'], 5) ==
                round(location['position']['z'] + object_2_offset['z'], 5)
            )
            # Location is anywhere in front of 1st object.
            assert (
                object_1_location['position']['x'] + object_1_offset['x'] >
                location['position']['x'] + object_2_offset['x']
            )
            assert (
                object_1_location['position']['z'] + object_1_offset['z'] >
                location['position']['z'] + object_2_offset['z']
            )
            assert geometry.does_partly_obstruct_target(
                performer_start['position'],
                object_1_location,
                object_2_poly
            )


def test_generate_location_in_line_with_object_adjacent():
    # Set the performer start out-of-the-way.
    performer_start = {
        'position': {'x': -4.5, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_location = {
            # Ensure object X equals performer start X in this test.
            'position': {'x': -4.5, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )
        object_1_poly = geometry.get_bounding_polygon(object_1_location)
        object_1_offset = vars(object_1_definition.offset)

        for object_2_definition in [LARGEST_OBJECT, SMALLEST_OBJECT]:
            object_2_offset = vars(object_2_definition.offset)
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                [],
                adjacent=True
            )
            assert location
            object_2_poly = geometry.get_bounding_polygon(location)
            # Location is close to 1st object.
            assert object_2_poly.distance(object_1_poly) < 0.105
            # Location is in the room and does not overlap with 1st object.
            assert geometry.validate_location_rect(
                location['boundingBox'],
                performer_start['position'],
                [object_1_location['boundingBox']],
                geometry.DEFAULT_ROOM_DIMENSIONS
            )
            # Location is orthogonal on the X axis to 1st object.
            assert (
                object_1_location['position']['x'] + object_1_offset['x'] !=
                location['position']['x'] + object_2_offset['x']
            )
            assert (
                object_1_location['position']['z'] + object_1_offset['z'] ==
                pytest.approx(location['position']['z'] + object_2_offset['z'])
            )


def test_generate_location_in_line_with_object_adjacent_diagonal():
    # Set the performer start out-of-the-way.
    performer_start = {
        'position': {'x': -4.5, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_location = {
            # Ensure object location is diagonal in this test.
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )
        object_1_poly = geometry.get_bounding_polygon(object_1_location)
        object_1_offset = vars(object_1_definition.offset)

        for object_2_definition in [LARGEST_OBJECT, SMALLEST_OBJECT]:
            object_2_offset = vars(object_2_definition.offset)
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                [],
                adjacent=True
            )
            assert location
            object_2_poly = geometry.get_bounding_polygon(location)
            # Location is close to 1st object.
            assert object_2_poly.distance(object_1_poly) < 0.105
            # Location is in the room and does not overlap with 1st object.
            assert geometry.validate_location_rect(
                location['boundingBox'],
                performer_start['position'],
                [object_1_location['boundingBox']],
                geometry.DEFAULT_ROOM_DIMENSIONS
            )
            # Location is on the perpendicular line from the performer start.
            assert (
                -round(location['position']['x'] + object_2_offset['x'], 5) ==
                round(location['position']['z'] + object_2_offset['z'], 5)
            )
            assert (
                object_1_location['position']['x'] + object_1_offset['x'] !=
                location['position']['x'] + object_2_offset['x']
            )
            assert (
                object_1_location['position']['z'] + object_1_offset['z'] !=
                location['position']['z'] + object_2_offset['z']
            )


def test_generate_location_in_line_with_object_behind():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': 0, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_location = {
            # Ensure object X equals performer start X in this test.
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )
        object_1_poly = geometry.get_bounding_polygon(object_1_location)
        object_1_offset = vars(object_1_definition.offset)

        for object_2_definition in [LARGEST_OBJECT, SMALLEST_OBJECT]:
            object_2_offset = vars(object_2_definition.offset)
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                [],
                behind=True
            )
            assert location
            object_2_poly = geometry.get_bounding_polygon(location)
            # Location is close to 1st object.
            assert object_2_poly.distance(object_1_poly) < 0.105
            # Location is in the room and does not overlap with 1st object.
            assert geometry.validate_location_rect(
                location['boundingBox'],
                performer_start['position'],
                [object_1_location['boundingBox']],
                geometry.DEFAULT_ROOM_DIMENSIONS
            )
            # Location is orthogonal on the Z axis to 1st object.
            assert (
                object_1_location['position']['x'] + object_1_offset['x'] ==
                pytest.approx(location['position']['x'] + object_2_offset['x'])
            )
            # Location is anywhere in back of 1st object.
            assert (
                object_1_location['position']['z'] + object_1_offset['z'] <
                location['position']['z'] + object_2_offset['z']
            )
            assert geometry.does_partly_obstruct_target(
                performer_start['position'],
                location,
                object_1_poly
            )


def test_generate_location_in_line_with_object_behind_diagonal():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': -4.5, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_location = {
            # Ensure object location is diagonal in this test.
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )
        object_1_poly = geometry.get_bounding_polygon(object_1_location)
        object_1_offset = vars(object_1_definition.offset)

        for object_2_definition in [LARGEST_OBJECT, SMALLEST_OBJECT]:
            object_2_offset = vars(object_2_definition.offset)
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                [],
                behind=True
            )
            assert location
            object_2_poly = geometry.get_bounding_polygon(location)
            # Location is close to 1st object.
            assert object_2_poly.distance(object_1_poly) < 0.105
            # Location is in the room and does not overlap with 1st object.
            assert geometry.validate_location_rect(
                location['boundingBox'],
                performer_start['position'],
                [object_1_location['boundingBox']],
                geometry.DEFAULT_ROOM_DIMENSIONS
            )
            # Location is on the diagonal line from the performer start.
            assert (
                round(location['position']['x'] + object_2_offset['x'], 5) ==
                round(location['position']['z'] + object_2_offset['z'], 5)
            )
            # Location is anywhere in back of 1st object.
            assert (
                object_1_location['position']['x'] + object_1_offset['x'] <
                location['position']['x'] + object_2_offset['x']
            )
            assert (
                object_1_location['position']['z'] + object_1_offset['z'] <
                location['position']['z'] + object_2_offset['z']
            )
            assert geometry.does_partly_obstruct_target(
                performer_start['position'],
                location,
                object_1_poly
            )


def test_generate_location_in_line_with_object_obstruct():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': 0, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_location = {
            # Ensure object X equals performer start X in this test.
            'position': {'x': 0, 'y': 0, 'z': 4.5},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )
        object_1_offset = vars(object_1_definition.offset)

        for object_2_definition in [LARGEST_OBJECT]:
            object_2_offset = vars(object_2_definition.offset)
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                [],
                obstruct=True
            )
            assert location
            object_2_poly = geometry.get_bounding_polygon(location)
            # Location is in the room and does not overlap with 1st object.
            assert geometry.validate_location_rect(
                location['boundingBox'],
                performer_start['position'],
                [object_1_location['boundingBox']],
                geometry.DEFAULT_ROOM_DIMENSIONS
            )
            # Location is orthogonal on the Z axis to 1st object.
            assert (
                object_1_location['position']['x'] + object_1_offset['x'] ==
                pytest.approx(location['position']['x'] + object_2_offset['x'])
            )
            # Location is in front of 1st object and obstructs it.
            assert (
                object_1_location['position']['z'] + object_1_offset['z'] >
                location['position']['z'] + object_2_offset['z']
            )
            assert geometry.does_fully_obstruct_target(
                performer_start['position'],
                object_1_location,
                object_2_poly
            )


def test_generate_location_in_line_with_object_obstruct_diagonal():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': -4.5, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_location = {
            # Ensure object location is diagonal in this test.
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )
        object_1_offset = vars(object_1_definition.offset)

        for object_2_definition in [LARGEST_OBJECT]:
            object_2_offset = vars(object_2_definition.offset)
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                [],
                obstruct=True
            )
            assert location
            object_2_poly = geometry.get_bounding_polygon(location)
            # Location is in the room and does not overlap with 1st object.
            assert geometry.validate_location_rect(
                location['boundingBox'],
                performer_start['position'],
                [object_1_location['boundingBox']],
                geometry.DEFAULT_ROOM_DIMENSIONS
            )
            # Location is on the diagonal line from the performer start.
            assert (
                round(location['position']['x'] + object_2_offset['x'], 5) ==
                round(location['position']['z'] + object_2_offset['z'], 5)
            )
            # Location is in front of 1st object and obstructs it.
            assert (
                object_1_location['position']['x'] + object_1_offset['x'] >
                location['position']['x'] + object_2_offset['x']
            )
            assert (
                object_1_location['position']['z'] + object_1_offset['z'] >
                location['position']['z'] + object_2_offset['z']
            )
            assert geometry.does_fully_obstruct_target(
                performer_start['position'],
                object_1_location,
                object_2_poly
            )


def test_generate_location_in_line_with_object_unreachable():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': 0, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_location = {
            # Ensure object X equals performer start X in this test.
            'position': {'x': 0, 'y': 0, 'z': 4.5},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )
        object_1_poly = geometry.get_bounding_polygon(object_1_location)
        object_1_offset = vars(object_1_definition.offset)

        for object_2_definition in [LARGEST_OBJECT, SMALLEST_OBJECT]:
            object_2_offset = vars(object_2_definition.offset)
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                [],
                unreachable=True
            )
            assert location
            object_2_poly = geometry.get_bounding_polygon(location)
            # Location is far enough away from 1st object.
            assert (
                object_2_poly.distance(object_1_poly) + max(
                    object_2_definition.dimensions.x / 2.0,
                    object_2_definition.dimensions.z / 2.0,
                ) > 1
            )
            # Location is in the room and does not overlap with 1st object.
            assert geometry.validate_location_rect(
                location['boundingBox'],
                performer_start['position'],
                [object_1_location['boundingBox']],
                geometry.DEFAULT_ROOM_DIMENSIONS
            )
            # Location is orthogonal on the Z axis to 1st object.
            assert (
                object_1_location['position']['x'] + object_1_offset['x'] ==
                pytest.approx(location['position']['x'] + object_2_offset['x'])
            )
            # Location is anywhere in front of 1st object.
            assert (
                object_1_location['position']['z'] + object_1_offset['z'] >
                location['position']['z'] + object_2_offset['z']
            )
            assert geometry.does_partly_obstruct_target(
                performer_start['position'],
                object_1_location,
                object_2_poly
            )


def test_generate_location_in_line_with_object_unreachable_diagonal():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': -4.5, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }

    for object_1_definition in ALL_DEFINITIONS:
        object_1_location = {
            # Ensure object location is diagonal in this test.
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
        object_1_location['boundingBox'] = geometry.generate_object_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation']
        )
        object_1_poly = geometry.get_bounding_polygon(object_1_location)
        object_1_offset = vars(object_1_definition.offset)

        for object_2_definition in [LARGEST_OBJECT, SMALLEST_OBJECT]:
            object_2_offset = vars(object_2_definition.offset)
            location = geometry.generate_location_in_line_with_object(
                object_2_definition,
                object_1_definition,
                object_1_location,
                performer_start,
                [],
                unreachable=True
            )
            assert location
            object_2_poly = geometry.get_bounding_polygon(location)
            # Location is far enough away from 1st object.
            assert (
                object_2_poly.distance(object_1_poly) + max(
                    object_2_definition.dimensions.x / 2.0,
                    object_2_definition.dimensions.x / 2.0,
                ) > 1
            )
            # Location is in the room and does not overlap with 1st object.
            assert geometry.validate_location_rect(
                location['boundingBox'],
                performer_start['position'],
                [object_1_location['boundingBox']],
                geometry.DEFAULT_ROOM_DIMENSIONS
            )
            # Location is on the diagonal line from the performer start.
            assert (
                round(location['position']['x'] + object_2_offset['x'], 5) ==
                round(location['position']['z'] + object_2_offset['z'], 5)
            )
            # Location is anywhere in front of 1st object.
            assert (
                object_1_location['position']['x'] + object_1_offset['x'] >
                location['position']['x'] + object_2_offset['x']
            )
            assert (
                object_1_location['position']['z'] + object_1_offset['z'] >
                location['position']['z'] + object_2_offset['z']
            )
            assert geometry.does_partly_obstruct_target(
                performer_start['position'],
                object_1_location,
                object_2_poly
            )


def test_retrieve_obstacle_occluder_definition_list():
    for object_definition in ALL_DEFINITIONS:
        object_dimensions = vars(
            object_definition.closedDimensions or object_definition.dimensions
        )
        definition_list = geometry.retrieve_obstacle_occluder_definition_list(
            object_definition,
            DATASET,
            False
        )
        for bigger_definition_result in definition_list:
            bigger_definition, angle = bigger_definition_result
            bigger_dimensions = vars(
                bigger_definition.closedDimensions or
                bigger_definition.dimensions
            )
            assert bigger_definition.obstacle
            assert bigger_dimensions['y'] >= 0.2
            assert bigger_definition.mass > 2
            if angle == 0:
                assert bigger_dimensions['x'] >= object_dimensions['x']
            else:
                # We rotate the bigger object so compare its side to the
                # original object's front.
                assert bigger_dimensions['z'] >= object_dimensions['x']


def test_retrieve_obstacle_occluder_definition_list_is_occluder():
    for object_definition in ALL_DEFINITIONS:
        object_dimensions = vars(
            object_definition.closedDimensions or object_definition.dimensions
        )
        definition_list = geometry.retrieve_obstacle_occluder_definition_list(
            object_definition,
            DATASET,
            True
        )
        for bigger_definition_result in definition_list:
            bigger_definition, angle = bigger_definition_result
            bigger_dimensions = vars(
                bigger_definition.closedDimensions or
                bigger_definition.dimensions
            )
            assert bigger_definition.occluder
            assert bigger_dimensions['y'] >= object_dimensions['y']
            assert bigger_definition.mass > 2
            if angle == 0:
                assert bigger_dimensions['x'] >= object_dimensions['x']
            else:
                # We rotate the bigger object so compare its side to the
                # original object's front.
                assert bigger_dimensions['z'] >= object_dimensions['x']


def test_get_bounding_poly():
    # TODO
    pass


def test_rect_to_poly():
    rect = [{'x': 1, 'z': 2}, {'x': 3, 'z': 4},
            {'x': 7, 'z': 0}, {'x': 5, 'z': -2}]
    expected = shapely.geometry.Polygon([(1, 2), (3, 4), (7, 0), (5, -2)])
    actual = geometry.rect_to_poly(rect)
    assert actual.equals(expected)


def test_find_performer_rect():
    expected1 = [{'x': -0.27, 'z': -0.27}, {'x': -0.27, 'z': 0.27},
                 {'x': 0.27, 'z': 0.27}, {'x': 0.27, 'z': -0.27}]
    actual1 = geometry.find_performer_rect({'x': 0, 'y': 0, 'z': 0})
    assert actual1 == expected1

    expected2 = [{'x': 0.73, 'z': 0.73}, {'x': 0.73, 'z': 1.27},
                 {'x': 1.27, 'z': 1.27}, {'x': 1.27, 'z': 0.73}]
    actual2 = geometry.find_performer_rect({'x': 1, 'y': 1, 'z': 1})
    assert actual2 == expected2


def test_does_fully_obstruct_target():
    target_location = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    target_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 1, 'z': 1},
        None,
        target_location['position'],
        target_location['rotation']
    )
    obstructor_location = {
        'position': {
            'x': -2,
            'y': 0,
            'z': 0},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 2, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 0,
            'y': 0,
            'z': -2},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MIN}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 0, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MAX}, target_location,
        obstructor_poly)


def test_does_fully_obstruct_target_returns_false_too_small():
    target_location = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    target_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 1, 'z': 1},
        None,
        target_location['position'],
        target_location['rotation']
    )

    obstructor_location = {
        'position': {
            'x': -2,
            'y': 0,
            'z': 0},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 0.5, 'z': 0.5},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 2, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 0.5, 'z': 0.5},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 0,
            'y': 0,
            'z': -2},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 0.5, 'z': 0.5},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MIN}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 0, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 0.5, 'z': 0.5},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MAX}, target_location,
        obstructor_poly)


def test_does_fully_obstruct_target_returns_false_performer_start():
    target_location = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    target_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 1, 'z': 1},
        None,
        target_location['position'],
        target_location['rotation']
    )

    obstructor_location = {
        'position': {
            'x': -2,
            'y': 0,
            'z': 0},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MIN}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MAX}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0,
         'z': DEFAULT_ROOM_Z_MIN},
        target_location,
        obstructor_poly
    )
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0,
         'z': DEFAULT_ROOM_Z_MAX},
        target_location,
        obstructor_poly
    )

    obstructor_location = {
        'position': {
            'x': 2, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MIN}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MAX}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0,
         'z': DEFAULT_ROOM_Z_MIN},
        target_location,
        obstructor_poly
    )
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0,
         'z': DEFAULT_ROOM_Z_MAX},
        target_location,
        obstructor_poly
    )

    obstructor_location = {
        'position': {
            'x': 0,
            'y': 0,
            'z': -2},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MAX}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0,
         'z': DEFAULT_ROOM_Z_MIN},
        target_location,
        obstructor_poly
    )
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0,
         'z': DEFAULT_ROOM_Z_MIN},
        target_location,
        obstructor_poly
    )
    obstructor_location = {
        'position': {
            'x': 0, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MIN}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0,
         'z': DEFAULT_ROOM_Z_MAX},
        target_location,
        obstructor_poly
    )
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0,
         'z': DEFAULT_ROOM_Z_MAX},
        target_location,
        obstructor_poly
    )


def test_does_fully_obstruct_target_returns_false_visible_corners():
    target_location = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    target_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 1, 'z': 1},
        None,
        target_location['position'],
        target_location['rotation']
    )

    obstructor_location = {
        'position': {
            'x': -2,
            'y': 0,
            'z': 1},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': -2,
            'y': 0,
            'z': -1},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 2, 'y': 0, 'z': 1}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 2,
            'y': 0,
            'z': -1},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MAX, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 1,
            'y': 0,
            'z': -2},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MIN}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': -1,
            'y': 0,
            'z': -2},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MIN}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 1, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MAX}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': -1,
            'y': 0,
            'z': 2},
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0}}
    obstructor_location['boundingBox'] = geometry.generate_object_bounds(
        {'x': 2, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation']
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MAX}, target_location,
        obstructor_poly)


def test_validate_location_rect():
    # TODO
    pass
