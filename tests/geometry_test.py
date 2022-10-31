import math

import pytest
import shapely
from machine_common_sense.config_manager import Vector3d

from generator import (
    DefinitionDataset,
    ObjectBounds,
    geometry,
    specific_objects
)
from generator.base_objects import create_soccer_ball
from generator.geometry import calculate_rotations
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
# Reassign the dataset to just have one variation (color) for faster testing.
DATASET = DefinitionDataset([
    [[variations[0]] for variations in selections]
    for selections in DATASET._definition_groups
])


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


def test_object_bounds():
    box_xz = [
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ]
    bounds = ObjectBounds(box_xz=box_xz, max_y=4, min_y=3)
    assert bounds.box_xz == box_xz
    assert bounds.polygon_xz
    assert bounds.max_y == 4
    assert bounds.min_y == 3


def test_expand_by():
    box_xz = [
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ]
    bounds = ObjectBounds(box_xz=box_xz, max_y=4, min_y=3)
    bounds.expand_by(3)
    assert bounds.box_xz == [
        Vector3d(x=-2, y=0, z=-2), Vector3d(x=-2, y=0, z=5),
        Vector3d(x=5, y=0, z=5), Vector3d(x=5, y=0, z=-2)
    ]
    assert bounds.polygon_xz
    assert bounds.max_y == 4
    assert bounds.min_y == 3


def test_expand_by_diagonal_fraction():
    box_xz = [
        Vector3d(x=0.2, y=0, z=0.6), Vector3d(x=0.4, y=0, z=0.8),
        Vector3d(x=0.8, y=0, z=0.4), Vector3d(x=0.6, y=0, z=0.2)
    ]
    bounds = ObjectBounds(box_xz=box_xz, max_y=4, min_y=3)
    bounds.expand_by(0.1)
    expected = [
        Vector3d(x=0.059, y=0, z=0.6), Vector3d(x=0.4, y=0, z=0.941),
        Vector3d(x=0.941, y=0, z=0.4), Vector3d(x=0.6, y=0, z=0.059)
    ]
    for index, point in enumerate(expected):
        assert point.x == round(bounds.box_xz[index].x, 3)
        assert point.y == 0
        assert point.z == round(bounds.box_xz[index].z, 3)
    assert bounds.polygon_xz
    assert bounds.max_y == 4
    assert bounds.min_y == 3


def test_expand_by_diagonal_negative():
    box_xz = [
        Vector3d(x=-1.5, y=0, z=-1), Vector3d(x=-1, y=0, z=-1.5),
        Vector3d(x=-0.5, y=0, z=-1), Vector3d(x=-1, y=0, z=-0.5)
    ]
    bounds = ObjectBounds(box_xz=box_xz, max_y=4, min_y=3)
    bounds.expand_by(1)
    expected = [
        Vector3d(x=-2.914, y=0, z=-1.0), Vector3d(x=-1.0, y=0, z=0.914),
        Vector3d(x=0.914, y=0, z=-1.0), Vector3d(x=-1.0, y=0, z=-2.914)
    ]
    for index, point in enumerate(expected):
        assert point.x == round(bounds.box_xz[index].x, 3)
        assert point.y == 0
        assert point.z == round(bounds.box_xz[index].z, 3)
    assert bounds.polygon_xz
    assert bounds.max_y == 4
    assert bounds.min_y == 3


def test_extend_bottom_to_ground():
    box_xz = [
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ]
    bounds = ObjectBounds(box_xz=box_xz, max_y=4, min_y=3)
    bounds.extend_bottom_to_ground()
    assert bounds.box_xz == box_xz
    assert bounds.polygon_xz
    assert bounds.max_y == 4
    assert bounds.min_y == 0


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


def test_is_within_room():
    valid_1 = Vector3d(**{'x': 0, 'y': 0, 'z': 0})
    valid_2 = Vector3d(**{'x': 5, 'y': 0, 'z': 5})
    valid_3 = Vector3d(**{'x': 5, 'y': 0, 'z': -5})
    valid_4 = Vector3d(**{'x': -5, 'y': 0, 'z': -5})
    valid_5 = Vector3d(**{'x': -5, 'y': 0, 'z': 5})
    valid_6 = Vector3d(**{'x': 0.1, 'y': 0, 'z': 0.1})
    invalid_1 = Vector3d(**{'x': 5.1, 'y': 0, 'z': 0})
    invalid_2 = Vector3d(**{'x': -5.1, 'y': 0, 'z': 0})
    invalid_3 = Vector3d(**{'x': 0, 'y': 0, 'z': 5.1})
    invalid_4 = Vector3d(**{'x': 0, 'y': 0, 'z': -5.1})
    assert ObjectBounds(box_xz=[
        valid_1, valid_2, valid_3, valid_4, valid_5, valid_6
    ], max_y=1, min_y=0).is_within_room(geometry.DEFAULT_ROOM_DIMENSIONS)
    assert not ObjectBounds(box_xz=[
        valid_1, valid_2, valid_3, valid_4, valid_5, valid_6, invalid_1
    ], max_y=1, min_y=0).is_within_room(geometry.DEFAULT_ROOM_DIMENSIONS)
    assert not ObjectBounds(box_xz=[
        valid_1, valid_2, valid_3, valid_4, valid_5, valid_6, invalid_2
    ], max_y=1, min_y=0).is_within_room(geometry.DEFAULT_ROOM_DIMENSIONS)
    assert not ObjectBounds(box_xz=[
        valid_1, valid_2, valid_3, valid_4, valid_5, valid_6, invalid_3
    ], max_y=1, min_y=0).is_within_room(geometry.DEFAULT_ROOM_DIMENSIONS)
    assert not ObjectBounds(box_xz=[
        valid_1, valid_2, valid_3, valid_4, valid_5, valid_6, invalid_4
    ], max_y=1, min_y=0).is_within_room(geometry.DEFAULT_ROOM_DIMENSIONS)
    assert not ObjectBounds(box_xz=[
        invalid_1, invalid_2, invalid_3, invalid_4
    ], max_y=1, min_y=0).is_within_room(geometry.DEFAULT_ROOM_DIMENSIONS)


def test_mcs_157():
    bounds = ObjectBounds(box_xz=[
        Vector3d(**{
            "x": -1.0257359312880716,
            "y": 0,
            "z": -6.05350288425444
        }),
        Vector3d(**{
            "x": -2.7935028842544405,
            "y": 0,
            "z": -4.285735931288071
        }),
        Vector3d(**{
            "x": -1.8742640687119283,
            "y": 0,
            "z": -3.3664971157455597
        }),
        Vector3d(**{
            "x": -0.10649711574555965,
            "y": 0,
            "z": -5.1342640687119285
        })
    ], max_y=1, min_y=0)
    assert bounds.is_within_room(geometry.DEFAULT_ROOM_DIMENSIONS) is False


def test_create_object_bounds_box_identity():

    a = {'x': 2, 'y': 0, 'z': 2}
    b = {'x': 2, 'y': 0, 'z': -2}
    c = {'x': -2, 'y': 0, 'z': -2}
    d = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 0, 'y': 0, 'z': 0},
        position={'x': 0, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': 0, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_rotate90():

    d = {'x': 2, 'y': 0, 'z': 2}
    a = {'x': 2, 'y': 0, 'z': -2}
    b = {'x': -2, 'y': 0, 'z': -2}
    c = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 0, 'y': 0, 'z': 0},
        position={'x': 0, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': 90, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_rotate180():

    c = {'x': 2, 'y': 0, 'z': 2}
    d = {'x': 2, 'y': 0, 'z': -2}
    a = {'x': -2, 'y': 0, 'z': -2}
    b = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 0, 'y': 0, 'z': 0},
        position={'x': 0, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': 180, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_rotate270():

    b = {'x': 2, 'y': 0, 'z': 2}
    c = {'x': 2, 'y': 0, 'z': -2}
    d = {'x': -2, 'y': 0, 'z': -2}
    a = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 0, 'y': 0, 'z': 0},
        position={'x': 0, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': 270, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_nonorigin_identity():

    a = {'x': 3, 'y': 0, 'z': 3}
    b = {'x': 3, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': -1}
    d = {'x': -1, 'y': 0, 'z': 3}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 0, 'y': 0, 'z': 0},
        position={'x': 1, 'y': 0, 'z': 1},
        rotation={'x': 0, 'y': 0, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_nonorigin_rotate90():

    d = {'x': 3, 'y': 0, 'z': 3}
    a = {'x': 3, 'y': 0, 'z': -1}
    b = {'x': -1, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': 3}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 0, 'y': 0, 'z': 0},
        position={'x': 1, 'y': 0, 'z': 1},
        rotation={'x': 0, 'y': 90, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_identity_offset():

    a = {'x': 3, 'y': 0, 'z': 3}
    b = {'x': 3, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': -1}
    d = {'x': -1, 'y': 0, 'z': 3}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 1, 'y': 0, 'z': 1},
        position={'x': 0, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': 0, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_rotation90_offset():

    d = {'x': 3, 'y': 0, 'z': 1}
    a = {'x': 3, 'y': 0, 'z': -3}
    b = {'x': -1, 'y': 0, 'z': -3}
    c = {'x': -1, 'y': 0, 'z': 1}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 1, 'y': 0, 'z': 1},
        position={'x': 0, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': 90, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_rotation90_offset_position_x():

    d = {'x': 10, 'y': 0, 'z': 1}
    a = {'x': 10, 'y': 0, 'z': -3}
    b = {'x': 6, 'y': 0, 'z': -3}
    c = {'x': 6, 'y': 0, 'z': 1}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 1, 'y': 0, 'z': 1},
        position={'x': 7, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': 90, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_rotation90_offset_position_z():

    d = {'x': 3, 'y': 0, 'z': 8}
    a = {'x': 3, 'y': 0, 'z': 4}
    b = {'x': -1, 'y': 0, 'z': 4}
    c = {'x': -1, 'y': 0, 'z': 8}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 1, 'y': 0, 'z': 1},
        position={'x': 0, 'y': 0, 'z': 7},
        rotation={'x': 0, 'y': 90, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_rotation90_offset_position_xz():

    d = {'x': 10, 'y': 0, 'z': 8}
    a = {'x': 10, 'y': 0, 'z': 4}
    b = {'x': 6, 'y': 0, 'z': 4}
    c = {'x': 6, 'y': 0, 'z': 8}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 1, 'y': 0, 'z': 1},
        position={'x': 7, 'y': 0, 'z': 7},
        rotation={'x': 0, 'y': 90, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_object_bounds_box_rotation45_offset_position_xz():

    d = {'x': 8.41421, 'y': 0, 'z': 9.82843}
    a = {'x': 11.24264, 'y': 0, 'z': 7}
    b = {'x': 8.41421, 'y': 0, 'z': 4.17157}
    c = {'x': 5.58579, 'y': 0, 'z': 7}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 4},
        offset={'x': 1, 'y': 0, 'z': 1},
        position={'x': 7, 'y': 0, 'z': 7},
        rotation={'x': 0, 'y': 45, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_bounds_rotation_more_than_360():
    a = {'x': 2.232051, 'y': 0, 'z': -0.133975}
    b = {'x': 1.232051, 'y': 0, 'z': -1.866025}
    c = {'x': -2.232051, 'y': 0, 'z': 0.133975}
    d = {'x': -1.232051, 'y': 0, 'z': 1.866025}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 2},
        offset={'x': 0, 'y': 0, 'z': 0},
        position={'x': 0, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': 390, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_create_bounds_rotation_negative():
    a = {'x': 1.232051, 'y': 0, 'z': 1.866025}
    b = {'x': 2.232051, 'y': 0, 'z': 0.133975}
    c = {'x': -1.232051, 'y': 0, 'z': -1.866025}
    d = {'x': -2.232051, 'y': 0, 'z': -0.133975}
    new_a, new_b, new_c, new_d = geometry.create_bounds(
        dimensions={'x': 4, 'y': 1, 'z': 2},
        offset={'x': 0, 'y': 0, 'z': 0},
        position={'x': 0, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': -30, 'z': 0},
        standing_y=0
    ).box_xz
    assert vars(new_a) == pytest.approx(a)
    assert vars(new_b) == pytest.approx(b)
    assert vars(new_c) == pytest.approx(c)
    assert vars(new_d) == pytest.approx(d)


def test_random_real():
    n = geometry.random_real(0, 1, 0.1)
    assert 0 <= n <= 1
    # need to multiply by 10 and mod by 1 instead of 0.1 to avoid weird
    # roundoff
    assert n * 10 % 1 < 1e-8


def test_object_collision():
    r1 = geometry.create_bounds(
        position={'x': -1.97, 'y': 0, 'z': 1.75},
        dimensions={'x': 1.1, 'y': 0, 'z': 0.89},
        offset={'x': -0.01, 'y': 0, 'z': 0.445},
        rotation={'x': 0, 'y': 315, 'z': 0},
        standing_y=0
    )
    r2 = geometry.create_bounds(
        position={'x': -3.04, 'y': 0, 'z': 0.85},
        dimensions={'x': 3.5, 'y': 0, 'z': 0.1},
        offset={'x': 0, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': 315, 'z': 0},
        standing_y=0
    )
    assert sat_entry(r1.box_xz, r2.box_xz)
    r3 = geometry.create_bounds(
        position={'x': 0.04, 'y': 0, 'z': 0.85},
        dimensions={'x': 3.5, 'y': 0, 'z': 0.1},
        offset={'x': 0, 'y': 0, 'z': 0},
        rotation={'x': 0, 'y': 315, 'z': 0},
        standing_y=0
    )
    assert not sat_entry(r1.box_xz, r3.box_xz)


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


@pytest.mark.slow
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


def test_get_location_adjacent_to_performer():
    perf_start = {
        'rotation': {'x': 0, 'y': 0, 'z': 0},
        'position': {'x': 1, 'y': 0, 'z': 2}
    }
    room_dim = {'x': 15, 'y': 3, 'z': 15}

    defn = create_soccer_ball(0.5)

    loc = geometry.get_location_adjacent_to_performer(
        performer_start=perf_start,
        room_dimensions=room_dim,
        target_definition_or_instance=defn,
        direction_rotation=0,
        distance=1)

    pos = loc['position']
    assert pos['x'] == 1
    assert pos['y'] == 0.055
    assert pos['z'] == pytest.approx(3.305)

    loc = geometry.get_location_adjacent_to_performer(
        performer_start=perf_start,
        room_dimensions=room_dim,
        target_definition_or_instance=defn,
        direction_rotation=90,
        distance=0.5)

    pos = loc['position']
    assert pos['x'] == pytest.approx(1.805)
    assert pos['z'] == pytest.approx(2)

    perf_start = {
        'rotation': {'x': 0, 'y': 60, 'z': 0},
        'position': {'x': 1, 'y': 0, 'z': 2}
    }

    loc = geometry.get_location_adjacent_to_performer(
        performer_start=perf_start,
        room_dimensions=room_dim,
        target_definition_or_instance=defn,
        direction_rotation=0,
        distance=1)

    pos = loc['position']
    assert pos['x'] == pytest.approx(2.1301631519386923)
    assert pos['z'] == pytest.approx(2.6525)

    loc = geometry.get_location_adjacent_to_performer(
        performer_start=perf_start,
        room_dimensions=room_dim,
        target_definition_or_instance=defn,
        direction_rotation=180,
        distance=0.7)

    pos = loc['position']
    assert pos['x'] == pytest.approx(0.12964446919663952)
    assert pos['z'] == pytest.approx(1.4974999999999996)

    loc = geometry.get_location_adjacent_to_performer(
        performer_start=perf_start,
        room_dimensions=room_dim,
        target_definition_or_instance=defn,
        direction_rotation=235,
        distance=0.25)

    pos = loc['position']
    assert pos['x'] == pytest.approx(0.49699917819465933)
    assert pos['z'] == pytest.approx(2.234553135266088)


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
    center['boundingBox'] = geometry.create_bounds(
        dimensions, None, center['position'], center['rotation'], 0)

    good_1 = {
        'position': {
            'x': 2, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_1['boundingBox'] = geometry.create_bounds(
        dimensions, None, good_1['position'], good_1['rotation'], 0)
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
    good_2['boundingBox'] = geometry.create_bounds(
        dimensions, None, good_2['position'], good_2['rotation'], 0)
    assert geometry.are_adjacent(center, good_2)

    good_3 = {
        'position': {
            'x': 0, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_3['boundingBox'] = geometry.create_bounds(
        dimensions, None, good_3['position'], good_3['rotation'], 0)
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
    good_4['boundingBox'] = geometry.create_bounds(
        dimensions, None, good_4['position'], good_4['rotation'], 0)
    assert geometry.are_adjacent(center, good_4)

    good_5 = {
        'position': {
            'x': 2, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_5['boundingBox'] = geometry.create_bounds(
        dimensions, None, good_5['position'], good_5['rotation'], 0)
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
    good_6['boundingBox'] = geometry.create_bounds(
        dimensions, None, good_6['position'], good_6['rotation'], 0)
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
    good_7['boundingBox'] = geometry.create_bounds(
        dimensions, None, good_7['position'], good_7['rotation'], 0)
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
    good_8['boundingBox'] = geometry.create_bounds(
        dimensions, None, good_8['position'], good_8['rotation'], 0)
    assert geometry.are_adjacent(center, good_8)

    bad_1 = {
        'position': {
            'x': 3, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_1['boundingBox'] = geometry.create_bounds(
        dimensions, None, bad_1['position'], bad_1['rotation'], 0)
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
    bad_2['boundingBox'] = geometry.create_bounds(
        dimensions, None, bad_2['position'], bad_2['rotation'], 0)
    assert not geometry.are_adjacent(center, bad_2)

    bad_3 = {
        'position': {
            'x': 0, 'y': 0, 'z': 3}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_3['boundingBox'] = geometry.create_bounds(
        dimensions, None, bad_3['position'], bad_3['rotation'], 0)
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
    bad_4['boundingBox'] = geometry.create_bounds(
        dimensions, None, bad_4['position'], bad_4['rotation'], 0)
    assert not geometry.are_adjacent(center, bad_4)

    bad_5 = {
        'position': {
            'x': 2.5, 'y': 0, 'z': 2.5}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_5['boundingBox'] = geometry.create_bounds(
        dimensions, None, bad_5['position'], bad_5['rotation'], 0)
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
    bad_6['boundingBox'] = geometry.create_bounds(
        dimensions, None, bad_6['position'], bad_6['rotation'], 0)
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
    bad_7['boundingBox'] = geometry.create_bounds(
        dimensions, None, bad_7['position'], bad_7['rotation'], 0)
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
    bad_8['boundingBox'] = geometry.create_bounds(
        dimensions, None, bad_8['position'], bad_8['rotation'], 0)
    assert not geometry.are_adjacent(center, bad_8)


def test_are_adjacent_with_offset():
    dimensions = {'x': 2, 'y': 2, 'z': 2}
    offset = {'x': -1, 'y': 0, 'z': 1}

    center = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    center['boundingBox'] = geometry.create_bounds(
        dimensions, None, center['position'], center['rotation'], 0)

    good_1 = {
        'position': {
            'x': 3, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_1['boundingBox'] = geometry.create_bounds(
        dimensions, offset, good_1['position'], good_1['rotation'], 0)
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
    good_2['boundingBox'] = geometry.create_bounds(
        dimensions, offset, good_2['position'], good_2['rotation'], 0)
    assert geometry.are_adjacent(center, good_2)

    good_3 = {
        'position': {
            'x': 0, 'y': 0, 'z': 1}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_3['boundingBox'] = geometry.create_bounds(
        dimensions, offset, good_3['position'], good_3['rotation'], 0)
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
    good_4['boundingBox'] = geometry.create_bounds(
        dimensions, offset, good_4['position'], good_4['rotation'], 0)
    assert geometry.are_adjacent(center, good_4)

    good_5 = {
        'position': {
            'x': 3, 'y': 0, 'z': 1}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    good_5['boundingBox'] = geometry.create_bounds(
        dimensions, offset, good_5['position'], good_5['rotation'], 0)
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
    good_6['boundingBox'] = geometry.create_bounds(
        dimensions, offset, good_6['position'], good_6['rotation'], 0)
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
    good_7['boundingBox'] = geometry.create_bounds(
        dimensions, offset, good_7['position'], good_7['rotation'], 0)
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
    good_8['boundingBox'] = geometry.create_bounds(
        dimensions, offset, good_8['position'], good_8['rotation'], 0)
    assert geometry.are_adjacent(center, good_8)

    bad_1 = {
        'position': {
            'x': 4, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_1['boundingBox'] = geometry.create_bounds(
        dimensions, offset, bad_1['position'], bad_1['rotation'], 0)
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
    bad_2['boundingBox'] = geometry.create_bounds(
        dimensions, offset, bad_2['position'], bad_2['rotation'], 0)
    assert not geometry.are_adjacent(center, bad_2)

    bad_3 = {
        'position': {
            'x': 0, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_3['boundingBox'] = geometry.create_bounds(
        dimensions, offset, bad_3['position'], bad_3['rotation'], 0)
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
    bad_4['boundingBox'] = geometry.create_bounds(
        dimensions, offset, bad_4['position'], bad_4['rotation'], 0)
    assert not geometry.are_adjacent(center, bad_4)

    bad_5 = {
        'position': {
            'x': 3.5, 'y': 0, 'z': 1.5}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    bad_5['boundingBox'] = geometry.create_bounds(
        dimensions, offset, bad_5['position'], bad_5['rotation'], 0)
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
    bad_6['boundingBox'] = geometry.create_bounds(
        dimensions, offset, bad_6['position'], bad_6['rotation'], 0)
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
    bad_7['boundingBox'] = geometry.create_bounds(
        dimensions, offset, bad_7['position'], bad_7['rotation'], 0)
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
    bad_8['boundingBox'] = geometry.create_bounds(
        dimensions, offset, bad_8['position'], bad_8['rotation'], 0)
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
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
            assert object_2_poly.distance(object_1_poly) < 0.505
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
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
            assert object_2_poly.distance(object_1_poly) < 0.505
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
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
            assert object_2_poly.distance(object_1_poly) < 0.505
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
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
            assert object_2_poly.distance(object_1_poly) < 0.505
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
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
            assert object_2_poly.distance(object_1_poly) < 0.505
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
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
            assert object_2_poly.distance(object_1_poly) < 0.505
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
        )
        object_1_poly = geometry.get_bounding_polygon(object_1_location)
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
            # Location is close to 1st object. (Bigger because of sofas.)
            assert object_2_poly.distance(object_1_poly) <= 1
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
        )
        object_1_poly = geometry.get_bounding_polygon(object_1_location)
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
            # Location is close to 1st object. (Bigger because of sofas.)
            assert object_2_poly.distance(object_1_poly) <= 1
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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
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


def test_generate_location_on_object():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': -4.5, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }
    obj = {
        'debug': {
            'dimensions': {'x': 0.2, 'y': 0.2, 'z': 0.2},
            'offset': {'x': 0, 'y': 0, 'z': 0},
            'positionY': 0,
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
    }

    loc = {
        'position': {'x': 3, 'y': 0, 'z': 4},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }
    static_inst = {
        'debug': {
            'dimensions': {'x': 1, 'y': 1, 'z': 1},
            'offset': {'x': 0, 'y': 0, 'z': 0},
            'positionY': 0
        },
        'shows': [loc]
    }
    static_inst = geometry.move_to_location(static_inst, loc)

    bounds_list = []
    location = geometry.generate_location_on_object(
        obj,
        static_inst,
        performer_start,
        bounds_list,
        geometry.DEFAULT_ROOM_DIMENSIONS,
        False)

    assert 2.5 < location['position']['x'] < 3.5
    assert 3.5 < location['position']['z'] < 4.5
    assert location['position']['y'] == 1


def test_generate_location_on_object_centered():
    performer_start = {
        'position': {'x': -4.5, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }
    obj = {
        'debug': {
            'dimensions': {'x': 0.2, 'y': 0.2, 'z': 0.2},
            'offset': {'x': 0, 'y': 0, 'z': 0},
            'positionY': 0,
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
    }

    loc = {
        'position': {'x': 3, 'y': 0, 'z': 4},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }
    static_inst = {
        'debug': {
            'dimensions': {'x': 1, 'y': 1, 'z': 1},
            'offset': {'x': 0, 'y': 0, 'z': 0},
            'positionY': 0
        },
        'shows': [loc]
    }
    static_inst = geometry.move_to_location(static_inst, loc)

    bounds_list = []
    location = geometry.generate_location_on_object(
        obj,
        static_inst,
        performer_start,
        bounds_list,
        geometry.DEFAULT_ROOM_DIMENSIONS,
        True)

    assert location['position']['x'] == 3
    assert location['position']['z'] == 4
    assert location['position']['y'] == 1


def test_generate_location_on_object_thats_too_tall():
    # Set the performer start in the back of the room facing inward.
    performer_start = {
        'position': {'x': -4.5, 'y': 0, 'z': -4.5},
        'rotation': {'y': 0}
    }
    obj = {
        'debug': {
            'dimensions': {'x': 0.2, 'y': 0.2, 'z': 0.2},
            'offset': {'x': 0, 'y': 0, 'z': 0},
            'positionY': 0,
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }
    }

    loc = {
        'position': {'x': 3, 'y': 0, 'z': 4},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }
    static_inst = {
        'debug': {
            'dimensions': {'x': 1, 'y': 3.5, 'z': 1},
            'offset': {'x': 0, 'y': 0, 'z': 0},
            'positionY': 0
        },
        'shows': [loc]
    }
    static_inst = geometry.move_to_location(static_inst, loc)

    bounds_list = []
    with pytest.raises(Exception):
        geometry.generate_location_on_object(
            obj,
            static_inst,
            performer_start,
            bounds_list,
            geometry.DEFAULT_ROOM_DIMENSIONS,
            False)


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
        object_1_location['boundingBox'] = geometry.create_bounds(
            vars(object_1_definition.dimensions),
            vars(object_1_definition.offset),
            object_1_location['position'],
            object_1_location['rotation'],
            0
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
    failed = False
    for object_definition in ALL_DEFINITIONS:
        # Only test the small, pickupable objects.
        if 'pickupable' not in object_definition.attributes:
            continue
        object_dimensions = vars(object_definition.dimensions)
        # Find a valid obstacle.
        output = geometry.retrieve_obstacle_occluder_definition_list(
            object_definition,
            DATASET,
            False
        )
        if not output:
            print(f'Failed: {object_definition}')
            failed = True
            continue
        # Ensure the obstacle meets the requirements.
        bigger_definition, angle = output
        bigger_dimensions = vars(bigger_definition.dimensions)
        assert bigger_definition.obstacle
        assert bigger_dimensions['y'] >= 0.2
        assert bigger_definition.mass > 2
        if angle == 0:
            assert bigger_dimensions['x'] >= object_dimensions['x']
        else:
            # We rotate the bigger object so compare its side to the
            # original object's front.
            assert bigger_dimensions['z'] >= object_dimensions['x']
    assert not failed


def test_retrieve_obstacle_occluder_definition_list_is_occluder():
    failed = False
    for object_definition in ALL_DEFINITIONS:
        # Only test the small, pickupable objects.
        if 'pickupable' not in object_definition.attributes:
            continue
        object_dimensions = vars(object_definition.dimensions)
        # Find a valid occluder.
        output = geometry.retrieve_obstacle_occluder_definition_list(
            object_definition,
            DATASET,
            True
        )
        if not output:
            print(f'Failed: {object_definition}')
            failed = True
            continue
        # Ensure the occluder meets the requirements.
        bigger_definition, angle = output
        bigger_dimensions = vars(bigger_definition.dimensions)
        assert bigger_definition.occluder
        assert bigger_dimensions['y'] >= object_dimensions['y']
        assert bigger_definition.mass > 2
        if angle == 0:
            assert bigger_dimensions['x'] >= object_dimensions['x']
        else:
            # We rotate the bigger object so compare its side to the
            # original object's front.
            assert bigger_dimensions['z'] >= object_dimensions['x']
    assert not failed


def test_get_bounding_polygon():
    bounds_a = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ], max_y=1, min_y=0)
    bounds_b = ObjectBounds(box_xz=[
        Vector3d(x=3, y=0, z=3), Vector3d(x=3, y=0, z=4),
        Vector3d(x=4, y=0, z=4), Vector3d(x=4, y=0, z=3)
    ], max_y=1, min_y=0)
    location = {'boundingBox': bounds_a}
    instance = {'shows': [{'boundingBox': bounds_b}]}
    assert geometry.get_bounding_polygon(location) == bounds_a.polygon_xz
    assert geometry.get_bounding_polygon(instance) == bounds_b.polygon_xz


def test_create_object_bounds_polygon():
    bounds = ObjectBounds(box_xz=[
        Vector3d(**{'x': 1, 'y': 0, 'z': 2}),
        Vector3d(**{'x': 3, 'y': 0, 'z': 4}),
        Vector3d(**{'x': 7, 'y': 0, 'z': 0}),
        Vector3d(**{'x': 5, 'y': 0, 'z': -2})
    ], max_y=1, min_y=0)
    expected = shapely.geometry.Polygon([(1, 2), (3, 4), (7, 0), (5, -2)])
    actual = bounds.polygon_xz
    assert actual.equals(expected)


def test_find_performer_bounds():
    expected1 = [
        {'x': -0.25, 'y': 0, 'z': -0.25}, {'x': -0.25, 'y': 0, 'z': 0.25},
        {'x': 0.25, 'y': 0, 'z': 0.25}, {'x': 0.25, 'y': 0, 'z': -0.25}
    ]
    actual1 = geometry.find_performer_bounds({'x': 0, 'y': 0, 'z': 0})
    assert vars(actual1.box_xz[0]) == expected1[0]
    assert vars(actual1.box_xz[1]) == expected1[1]
    assert vars(actual1.box_xz[2]) == expected1[2]
    assert vars(actual1.box_xz[3]) == expected1[3]
    assert actual1.max_y == 1.25
    assert actual1.min_y == 0

    expected2 = [
        {'x': 0.75, 'y': 0, 'z': 0.75}, {'x': 0.75, 'y': 0, 'z': 1.25},
        {'x': 1.25, 'y': 0, 'z': 1.25}, {'x': 1.25, 'y': 0, 'z': 0.75}
    ]
    actual2 = geometry.find_performer_bounds({'x': 1, 'y': 1, 'z': 1})
    assert vars(actual2.box_xz[0]) == expected2[0]
    assert vars(actual2.box_xz[1]) == expected2[1]
    assert vars(actual2.box_xz[2]) == expected2[2]
    assert vars(actual2.box_xz[3]) == expected2[3]
    assert actual2.max_y == 2.25
    assert actual2.min_y == 1


def test_does_fully_obstruct_target():
    target_location = {
        'position': {
            'x': 0, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    target_location['boundingBox'] = geometry.create_bounds(
        {'x': 1, 'y': 0, 'z': 1},
        None,
        target_location['position'],
        target_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 2, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MIN}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 0, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    target_location['boundingBox'] = geometry.create_bounds(
        {'x': 1, 'y': 0, 'z': 1},
        None,
        target_location['position'],
        target_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 0.5, 'y': 0, 'z': 0.5},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 2, 'y': 0, 'z': 0}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 0.5, 'y': 0, 'z': 0.5},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 0.5, 'y': 0, 'z': 0.5},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MIN}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 0, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 0.5, 'y': 0, 'z': 0.5},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    target_location['boundingBox'] = geometry.create_bounds(
        {'x': 1, 'y': 0, 'z': 1},
        None,
        target_location['position'],
        target_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    target_location['boundingBox'] = geometry.create_bounds(
        {'x': 1, 'y': 0, 'z': 1},
        None,
        target_location['position'],
        target_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': DEFAULT_ROOM_X_MIN, 'y': 0, 'z': 0}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 2, 'y': 0, 'z': 1}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MIN}, target_location,
        obstructor_poly)

    obstructor_location = {
        'position': {
            'x': 1, 'y': 0, 'z': 2}, 'rotation': {
            'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
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
    obstructor_location['boundingBox'] = geometry.create_bounds(
        {'x': 2, 'y': 0, 'z': 2},
        None,
        obstructor_location['position'],
        obstructor_location['rotation'],
        0
    )
    obstructor_poly = geometry.get_bounding_polygon(obstructor_location)
    assert not geometry.does_fully_obstruct_target(
        {'x': 0, 'y': 0, 'z': DEFAULT_ROOM_Z_MAX}, target_location,
        obstructor_poly)


def test_validate_location_rect():
    object_bounds = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ], max_y=1, min_y=0)
    assert geometry.validate_location_rect(
        object_bounds,
        {'x': 0, 'y': 0, 'z': 0},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )

    object_bounds = ObjectBounds(box_xz=[
        Vector3d(x=-3, y=0, z=-3), Vector3d(x=-3, y=0, z=-4),
        Vector3d(x=-4, y=0, z=-4), Vector3d(x=-4, y=0, z=-3)
    ], max_y=1, min_y=0)
    assert geometry.validate_location_rect(
        object_bounds,
        {'x': 0, 'y': 0, 'z': 0},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )


def test_validate_location_rect_not_inside_room():
    assert not geometry.validate_location_rect(
        ObjectBounds(box_xz=[
            Vector3d(x=4, y=0, z=4), Vector3d(x=4, y=0, z=6),
            Vector3d(x=6, y=0, z=6), Vector3d(x=6, y=0, z=4)
        ], max_y=1, min_y=0),
        {'x': 0, 'y': 0, 'z': 0},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        ObjectBounds(box_xz=[
            Vector3d(x=-4, y=0, z=-4), Vector3d(x=-4, y=0, z=-6),
            Vector3d(x=-6, y=0, z=-6), Vector3d(x=-6, y=0, z=-4)
        ], max_y=1, min_y=0),
        {'x': 0, 'y': 0, 'z': 0},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        ObjectBounds(box_xz=[
            Vector3d(x=4, y=0, z=0), Vector3d(x=4, y=0, z=2),
            Vector3d(x=6, y=0, z=2), Vector3d(x=6, y=0, z=0)
        ], max_y=1, min_y=0),
        {'x': 0, 'y': 0, 'z': 0},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        ObjectBounds(box_xz=[
            Vector3d(x=-4, y=0, z=0), Vector3d(x=-4, y=0, z=2),
            Vector3d(x=-6, y=0, z=2), Vector3d(x=-6, y=0, z=0)
        ], max_y=1, min_y=0),
        {'x': 0, 'y': 0, 'z': 0},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        ObjectBounds(box_xz=[
            Vector3d(x=0, y=0, z=4), Vector3d(x=0, y=0, z=6),
            Vector3d(x=2, y=0, z=6), Vector3d(x=2, y=0, z=4)
        ], max_y=1, min_y=0),
        {'x': 0, 'y': 0, 'z': 0},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        ObjectBounds(box_xz=[
            Vector3d(x=0, y=0, z=-4), Vector3d(x=0, y=0, z=-6),
            Vector3d(x=2, y=0, z=-6), Vector3d(x=2, y=0, z=-4)
        ], max_y=1, min_y=0),
        {'x': 0, 'y': 0, 'z': 0},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        ObjectBounds(box_xz=[
            Vector3d(x=5, y=0, z=5), Vector3d(x=5, y=0, z=6),
            Vector3d(x=6, y=0, z=6), Vector3d(x=6, y=0, z=5)
        ], max_y=1, min_y=0),
        {'x': 0, 'y': 0, 'z': 0},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        ObjectBounds(box_xz=[
            Vector3d(x=6, y=0, z=6), Vector3d(x=6, y=0, z=9),
            Vector3d(x=9, y=0, z=9), Vector3d(x=9, y=0, z=6)
        ], max_y=1, min_y=0),
        {'x': 0, 'y': 0, 'z': 0},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )


def test_validate_location_rect_overlaps_performer_agent():
    object_bounds = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ], max_y=1, min_y=0)
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': 1, 'y': 0, 'z': 1},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': 1, 'y': 0, 'z': 2},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': 2, 'y': 0, 'z': 2},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': 2, 'y': 0, 'z': 1},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': 1.5, 'y': 0, 'z': 1.5},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )

    object_bounds = ObjectBounds(box_xz=[
        Vector3d(x=-3, y=0, z=-3), Vector3d(x=-3, y=0, z=-4),
        Vector3d(x=-4, y=0, z=-4), Vector3d(x=-4, y=0, z=-3)
    ], max_y=1, min_y=0)
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': -3, 'y': 0, 'z': -3},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': -3, 'y': 0, 'z': -4},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': -4, 'y': 0, 'z': -4},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': -4, 'y': 0, 'z': -3},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': -3.5, 'y': 0, 'z': -3.5},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )


def test_validate_location_rect_with_bounds_list():
    target_bounds = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ], max_y=1, min_y=0)
    bounds_1 = ObjectBounds(box_xz=[
        Vector3d(x=3, y=0, z=3), Vector3d(x=3, y=0, z=4),
        Vector3d(x=4, y=0, z=4), Vector3d(x=4, y=0, z=3)
    ], max_y=1, min_y=0)
    bounds_2 = ObjectBounds(box_xz=[
        Vector3d(x=-1, y=0, z=-1), Vector3d(x=-1, y=0, z=-2),
        Vector3d(x=-2, y=0, z=-2), Vector3d(x=-2, y=0, z=-1)
    ], max_y=1, min_y=0)
    assert geometry.validate_location_rect(
        target_bounds,
        {'x': 0, 'y': 0, 'z': 0},
        [bounds_1, bounds_2],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )

    bounds_3 = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ], max_y=1, min_y=0)
    assert not geometry.validate_location_rect(
        target_bounds,
        {'x': 0, 'y': 0, 'z': 0},
        [bounds_1, bounds_2, bounds_3],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )

    bounds_4 = ObjectBounds(box_xz=[
        Vector3d(x=1.25, y=0, z=1.25), Vector3d(x=1.25, y=0, z=1.75),
        Vector3d(x=1.75, y=0, z=1.75), Vector3d(x=1.75, y=0, z=1.25)
    ], max_y=1, min_y=0)
    assert not geometry.validate_location_rect(
        target_bounds,
        {'x': 0, 'y': 0, 'z': 0},
        [bounds_1, bounds_2, bounds_4],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )

    bounds_5 = ObjectBounds(box_xz=[
        Vector3d(x=1.75, y=0, z=1.75), Vector3d(x=1.75, y=0, z=2.25),
        Vector3d(x=2.25, y=0, z=2.25), Vector3d(x=2.25, y=0, z=1.75)
    ], max_y=1, min_y=0)
    assert not geometry.validate_location_rect(
        target_bounds,
        {'x': 0, 'y': 0, 'z': 0},
        [bounds_1, bounds_2, bounds_5],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )

    bounds_6 = ObjectBounds(box_xz=[
        Vector3d(x=4.75, y=0, z=1.25), Vector3d(x=4.75, y=0, z=1.75),
        Vector3d(x=-4.75, y=0, z=1.75), Vector3d(x=-4.75, y=0, z=1.25)
    ], max_y=1, min_y=0)
    assert not geometry.validate_location_rect(
        target_bounds,
        {'x': 0, 'y': 0, 'z': 0},
        [bounds_1, bounds_2, bounds_6],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )


def test_validate_location_rect_performer_agent_with_y_bounds():
    object_bounds = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ], max_y=0.99, min_y=0)
    assert not geometry.validate_location_rect(
        object_bounds,
        {'x': 1.5, 'y': 0.5, 'z': 1.5},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert geometry.validate_location_rect(
        object_bounds,
        {'x': 1.5, 'y': 1, 'z': 1.5},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert geometry.validate_location_rect(
        object_bounds,
        {'x': 1.5, 'y': 1.5, 'z': 1.5},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )
    assert geometry.validate_location_rect(
        object_bounds,
        {'x': 1.5, 'y': 2, 'z': 1.5},
        [],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )


def test_validate_location_rect_with_y_bounds():
    target_bounds = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ], max_y=1.99, min_y=1.01)
    bounds_1 = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ], max_y=3, min_y=2)
    bounds_2 = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ], max_y=1, min_y=0)
    assert geometry.validate_location_rect(
        target_bounds,
        {'x': 0, 'y': 0, 'z': 0},
        [bounds_1, bounds_2],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )

    bounds_3 = ObjectBounds(box_xz=[
        Vector3d(x=3, y=0, z=3), Vector3d(x=3, y=0, z=4),
        Vector3d(x=4, y=0, z=4), Vector3d(x=4, y=0, z=3)
    ], max_y=1.75, min_y=1.25)
    assert geometry.validate_location_rect(
        target_bounds,
        {'x': 0, 'y': 0, 'z': 0},
        [bounds_1, bounds_2, bounds_3],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )

    bounds_4 = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1), Vector3d(x=1, y=0, z=2),
        Vector3d(x=2, y=0, z=2), Vector3d(x=2, y=0, z=1)
    ], max_y=1.75, min_y=1.25)
    assert not geometry.validate_location_rect(
        target_bounds,
        {'x': 0, 'y': 0, 'z': 0},
        [bounds_1, bounds_2, bounds_4],
        geometry.DEFAULT_ROOM_DIMENSIONS
    )


def test_move_to_location():
    old_location = {
        'position': {'x': -1, 'y': 0, 'z': -2},
        'rotation': {'x': 0, 'y': 90, 'z': 0}
    }
    new_location = {
        'position': {'x': 3, 'y': 0, 'z': 4},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }
    instance = {
        'debug': {
            'dimensions': {'x': 1, 'y': 1, 'z': 1},
            'offset': {'x': 0, 'y': 0, 'z': 0},
            'positionY': 0
        },
        'shows': [old_location]
    }
    actual = geometry.move_to_location(instance, new_location)
    assert actual == instance
    assert instance['shows'][0]['position'] == {'x': 3, 'y': 0, 'z': 4}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    bounds = instance['shows'][0]['boundingBox']
    assert vars(bounds.box_xz[0]) == {'x': 3.5, 'y': 0, 'z': 4.5}
    assert vars(bounds.box_xz[1]) == {'x': 3.5, 'y': 0, 'z': 3.5}
    assert vars(bounds.box_xz[2]) == {'x': 2.5, 'y': 0, 'z': 3.5}
    assert vars(bounds.box_xz[3]) == {'x': 2.5, 'y': 0, 'z': 4.5}
    assert bounds.max_y == 1
    assert bounds.min_y == 0

    old_location = {
        'position': {'x': -1, 'y': 0, 'z': -2},
        'rotation': {'x': 0, 'y': 90, 'z': 0}
    }
    new_location = {
        'position': {'x': 3, 'y': 0, 'z': 4},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }
    instance = {
        'debug': {
            'dimensions': {'x': 1, 'y': 1, 'z': 1},
            'offset': {'x': 0.2, 'y': 0, 'z': -0.4},
            'positionY': 0
        },
        'shows': [old_location]
    }
    actual = geometry.move_to_location(instance, new_location)
    assert actual == instance
    assert instance['shows'][0]['position'] == {'x': 2.8, 'y': 0, 'z': 4.4}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    bounds = instance['shows'][0]['boundingBox']
    assert vars(bounds.box_xz[0]) == pytest.approx(
        {'x': 3.5, 'y': 0, 'z': 4.5}
    )
    assert vars(bounds.box_xz[1]) == pytest.approx(
        {'x': 3.5, 'y': 0, 'z': 3.5}
    )
    assert vars(bounds.box_xz[2]) == pytest.approx(
        {'x': 2.5, 'y': 0, 'z': 3.5}
    )
    assert vars(bounds.box_xz[3]) == pytest.approx(
        {'x': 2.5, 'y': 0, 'z': 4.5}
    )
    assert bounds.max_y == 1
    assert bounds.min_y == 0


def test_generate_floor_area_bounds():
    buffer = geometry.FLOOR_FEATURE_BOUNDS_BUFFER
    bounds_1 = ObjectBounds(box_xz=[
        Vector3d(x=0.5 + buffer, y=0, z=0.5 + buffer),
        Vector3d(x=1.5 - buffer, y=0, z=0.5 + buffer),
        Vector3d(x=1.5 - buffer, y=0, z=1.5 - buffer),
        Vector3d(x=0.5 + buffer, y=0, z=1.5 - buffer)
    ], max_y=100, min_y=0)
    assert geometry.generate_floor_area_bounds(1, 1) == bounds_1

    bounds_2 = ObjectBounds(box_xz=[
        Vector3d(x=-3.5 + buffer, y=0, z=-3.5 + buffer),
        Vector3d(x=-2.5 - buffer, y=0, z=-3.5 + buffer),
        Vector3d(x=-2.5 - buffer, y=0, z=-2.5 - buffer),
        Vector3d(x=-3.5 + buffer, y=0, z=-2.5 - buffer)
    ], max_y=100, min_y=0)
    assert geometry.generate_floor_area_bounds(-3, -3) == bounds_2


def test_object_x_to_occluder_x():
    result = geometry.object_x_to_occluder_x(0, 2, 1, 0, -4)
    assert result == 0

    result = geometry.object_x_to_occluder_x(1, 2, 1, 0, -4)
    assert result == 0.8333

    result = geometry.object_x_to_occluder_x(2, 2, 1, 0, -4)
    assert result == 1.6667

    result = geometry.object_x_to_occluder_x(1, 2, 1, -1, -4)
    assert result == 0.6667

    result = geometry.object_x_to_occluder_x(1, 4, 1, 0, -4)
    assert result == 0.625

    result = geometry.object_x_to_occluder_x(1, 2, 1, 0, -6)
    assert result == 0.875

    result = geometry.object_x_to_occluder_x(3, 4, 1, 0, -4)
    assert result == 1.875

    result = geometry.object_x_to_occluder_x(1, 4, 2, 0, -4)
    assert result == 0.75

    result = geometry.object_x_to_occluder_x(11, 4, 2, 10, -4)
    assert result == 10.75

    result = geometry.object_x_to_occluder_x(-9, 4, 2, -10, -4)
    assert result == -9.25


def test_occluder_x_to_object_x():
    result = geometry.occluder_x_to_object_x(0, 1, 2, 0, -4)
    assert result == 0

    result = geometry.occluder_x_to_object_x(1, 1, 2, 0, -4)
    assert result == 1.2

    result = geometry.occluder_x_to_object_x(2, 1, 2, 0, -4)
    assert result == 2.4

    result = geometry.occluder_x_to_object_x(1, 1, 2, -1, -4)
    assert result == 1.4

    result = geometry.occluder_x_to_object_x(1, 1, 4, 0, -4)
    assert result == 1.6

    result = geometry.occluder_x_to_object_x(1, 1, 2, 0, -6)
    assert result == 1.1429

    result = geometry.occluder_x_to_object_x(3, 1, 4, 0, -4)
    assert result == 4.8

    result = geometry.occluder_x_to_object_x(1, 2, 4, 0, -4)
    assert result == 1.3333

    result = geometry.occluder_x_to_object_x(11, 1, 2, 10, -4)
    assert result == 11.2

    result = geometry.occluder_x_to_object_x(-9, 1, 2, -10, -4)
    assert result == -8.8


def test_get_along_wall_xz():
    room_dimensions = {'x': 10, 'y': 3, 'z': 30}
    dimensions = {'x': 0.4, 'y': 1, 'z': 0.6}
    wall_label = "back_wall"
    x, z = geometry.get_along_wall_xz(wall_label, room_dimensions, dimensions)
    assert z == 14.69
    assert -4.8 < x < 4.8
    wall_label = "front_wall"
    x, z = geometry.get_along_wall_xz(wall_label, room_dimensions, dimensions)
    assert z == -14.69
    assert -4.8 < x < 4.8
    wall_label = "left_wall"
    x, z = geometry.get_along_wall_xz(wall_label, room_dimensions, dimensions)
    assert x == -4.79
    assert -14.7 < z < 14.7
    wall_label = "right_wall"
    x, z = geometry.get_along_wall_xz(wall_label, room_dimensions, dimensions)
    assert x == 4.79
    assert -14.7 < z < 14.7


def test_get_along_wall_xz_fail():
    room_dimensions = {'x': 10, 'y': 3, 'z': 30}
    dimensions = {'x': 0.4, 'y': 1, 'z': 0.6}
    wall_label = "not_wall"
    with pytest.raises(Exception):
        geometry.get_along_wall_xz(wall_label, room_dimensions, dimensions)


def test_calculate_rotations_no_rounding():
    v1 = Vector3d(x=0, y=0, z=0)
    assert calculate_rotations(v1, Vector3d(x=0, y=0, z=1), True) == (37, 0)
    assert calculate_rotations(v1, Vector3d(x=0, y=0, z=2), True) == (21, 0)
    assert calculate_rotations(v1, Vector3d(x=0, y=0, z=3), True) == (14, 0)
    assert calculate_rotations(v1, Vector3d(x=0, y=1, z=1), True) == (-13, 0)
    assert calculate_rotations(v1, Vector3d(x=0, y=0.76, z=1), True) == (0, 0)
    assert calculate_rotations(v1, Vector3d(x=1, y=0, z=1), True) == (28, 45)
    assert calculate_rotations(v1, Vector3d(x=1, y=0.76, z=1), True) == (0, 45)
    assert calculate_rotations(v1, Vector3d(x=2, y=0.76, z=1), True) == (0, 63)
    assert calculate_rotations(v1, Vector3d(x=2, y=0.76, z=2), True) == (0, 45)
    assert calculate_rotations(v1, Vector3d(x=-1, y=0.76, z=1), True) == \
        (0, 315)


def test_calculate_rotations():
    v1 = Vector3d(x=0, y=0, z=0)
    assert calculate_rotations(v1, Vector3d(x=0, y=0, z=1)) == (40, 0)
    assert calculate_rotations(v1, Vector3d(x=0, y=0, z=2)) == (20, 0)
    assert calculate_rotations(v1, Vector3d(x=0, y=0, z=3)) == (10, 0)
    assert calculate_rotations(v1, Vector3d(x=0, y=1, z=1)) == (-10, 0)
    assert calculate_rotations(v1, Vector3d(x=0, y=0.76, z=1)) == (0, 0)
    assert calculate_rotations(v1, Vector3d(x=1, y=0, z=1)) == (30, 40)
    assert calculate_rotations(v1, Vector3d(x=1, y=0.76, z=1)) == (0, 40)
    assert calculate_rotations(v1, Vector3d(x=2, y=0.76, z=1)) == (0, 60)
    assert calculate_rotations(v1, Vector3d(x=2, y=0.76, z=2)) == (0, 40)
    assert calculate_rotations(v1, Vector3d(x=-1, y=0.76, z=1)) == (0, 320)
