from generator.intuitive_physics_util import (
    find_off_screen_position_diagonal_away,
    find_off_screen_position_diagonal_toward,
    find_position_behind_occluder_diagonal_away,
    find_position_behind_occluder_diagonal_toward,
    retrieve_off_screen_position_x,
    retrieve_off_screen_position_y
)


def test_retrieve_off_screen_position_x():
    assert retrieve_off_screen_position_x(1.6) == 4.16
    assert retrieve_off_screen_position_x(2) == 4.4
    assert retrieve_off_screen_position_x(3) == 5
    assert retrieve_off_screen_position_x(4) == 5.6
    assert retrieve_off_screen_position_x(5) == 6.2
    assert retrieve_off_screen_position_x(5.6) == 6.56

    assert retrieve_off_screen_position_x(-4.5) == 0.5
    assert retrieve_off_screen_position_x(-4) == 0.8
    assert retrieve_off_screen_position_x(-3) == 1.4
    assert retrieve_off_screen_position_x(-2) == 2
    assert retrieve_off_screen_position_x(-1) == 2.6
    assert retrieve_off_screen_position_x(0) == 3.2
    assert retrieve_off_screen_position_x(1) == 3.8

    assert retrieve_off_screen_position_x(6) == 6.8
    assert retrieve_off_screen_position_x(7) == 7.4
    assert retrieve_off_screen_position_x(8) == 8.0
    assert retrieve_off_screen_position_x(9) == 8.6
    assert retrieve_off_screen_position_x(10) == 9.2


def test_retrieve_off_screen_position_y():
    assert retrieve_off_screen_position_y(1.6) == 4.94
    assert retrieve_off_screen_position_y(2) == 5.1
    assert retrieve_off_screen_position_y(3) == 5.5
    assert retrieve_off_screen_position_y(4) == 5.9
    assert retrieve_off_screen_position_y(5) == 6.3
    assert retrieve_off_screen_position_y(5.6) == 6.54

    assert retrieve_off_screen_position_y(-4.5) == 2.5
    assert retrieve_off_screen_position_y(-4) == 2.7
    assert retrieve_off_screen_position_y(-3) == 3.1
    assert retrieve_off_screen_position_y(-2) == 3.5
    assert retrieve_off_screen_position_y(-1) == 3.9
    assert retrieve_off_screen_position_y(0) == 4.3
    assert retrieve_off_screen_position_y(1) == 4.7

    assert retrieve_off_screen_position_y(6) == 6.7
    assert retrieve_off_screen_position_y(7) == 7.1
    assert retrieve_off_screen_position_y(8) == 7.5
    assert retrieve_off_screen_position_y(9) == 7.9
    assert retrieve_off_screen_position_y(10) == 8.3


def test_find_off_screen_position_diagonal_away():
    out = find_off_screen_position_diagonal_away(4.16, 1.6, 0)
    assert out == (-4.16, 1.6)
    out = find_off_screen_position_diagonal_away(6.56, 5.6, 0)
    assert out == (-6.56, 5.6)
    out = find_off_screen_position_diagonal_away(-4.16, 1.6, 0)
    assert out == (4.16, 1.6)
    out = find_off_screen_position_diagonal_away(-6.56, 5.6, 0)
    assert out == (6.56, 5.6)

    out = find_off_screen_position_diagonal_away(4.16, 1.6, 10)
    assert out == (-5.15, 3.24)
    out = find_off_screen_position_diagonal_away(-4.16, 1.6, 10)
    assert out == (5.15, 3.24)
    out = find_off_screen_position_diagonal_away(4.4, 2, 10)
    assert out == (-5.45, 3.74)
    out = find_off_screen_position_diagonal_away(5, 3, 10)
    assert out == (-6.19, 4.97)

    out = find_off_screen_position_diagonal_away(4.16, 1.6, 20)
    assert out == (-6.49, 5.48)
    out = find_off_screen_position_diagonal_away(-4.16, 1.6, 20)
    assert out == (6.49, 5.48)
    out = find_off_screen_position_diagonal_away(4.4, 2, 20)
    assert out == (-6.86, 6.1)
    out = find_off_screen_position_diagonal_away(5, 3, 20)
    assert out == (-7.8, 7.66)


def test_find_off_screen_position_diagonal_toward():
    out = find_off_screen_position_diagonal_toward(4.16, 1.6, 0)
    assert out == (-4.16, 1.6)
    out = find_off_screen_position_diagonal_toward(6.56, 5.6, 0)
    assert out == (-6.56, 5.6)
    out = find_off_screen_position_diagonal_toward(-4.16, 1.6, 0)
    assert out == (4.16, 1.6)
    out = find_off_screen_position_diagonal_toward(-6.56, 5.6, 0)
    assert out == (6.56, 5.6)

    out = find_off_screen_position_diagonal_toward(6.56, 5.6, 10)
    assert out == (-5.31, 3.51)
    out = find_off_screen_position_diagonal_toward(-6.56, 5.6, 10)
    assert out == (5.31, 3.51)
    out = find_off_screen_position_diagonal_toward(6.2, 5, 10)
    assert out == (-5.02, 3.02)
    out = find_off_screen_position_diagonal_toward(5.6, 4, 10)
    assert out == (-4.53, 2.21)

    out = find_off_screen_position_diagonal_toward(6.56, 5.6, 20)
    assert out == (-4.21, 1.68)
    out = find_off_screen_position_diagonal_toward(-6.56, 5.6, 20)
    assert out == (4.21, 1.68)
    out = find_off_screen_position_diagonal_toward(6.2, 5, 20)
    assert out == (-3.98, 1.29)
    out = find_off_screen_position_diagonal_toward(5.6, 4, 20)
    assert out == (-3.6, 0.65)


def test_find_position_behind_occluder_diagonal_away():
    out = find_position_behind_occluder_diagonal_away(0, 1, 4.16, 1.6, 0)
    assert out == (0, 1.6)
    out = find_position_behind_occluder_diagonal_away(0, 1, 6.56, 5.6, 0)
    assert out == (0, 5.6)
    out = find_position_behind_occluder_diagonal_away(2, 1, 4.16, 1.6, 0)
    assert out == (2.2182, 1.6)
    out = find_position_behind_occluder_diagonal_away(2, 1, -4.16, 1.6, 0)
    assert out == (2.2182, 1.6)
    out = find_position_behind_occluder_diagonal_away(2, 1, 6.56, 5.6, 0)
    assert out == (3.6727, 5.6)
    out = find_position_behind_occluder_diagonal_away(2, 1, -6.56, 5.6, 0)
    assert out == (3.6727, 5.6)
    out = find_position_behind_occluder_diagonal_away(-2, 1, 4.16, 1.6, 0)
    assert out == (-2.2182, 1.6)
    out = find_position_behind_occluder_diagonal_away(-2, 1, -4.16, 1.6, 0)
    assert out == (-2.2182, 1.6)
    out = find_position_behind_occluder_diagonal_away(-2, 1, 6.56, 5.6, 0)
    assert out == (-3.6727, 5.6)
    out = find_position_behind_occluder_diagonal_away(-2, 1, -6.56, 5.6, 0)
    assert out == (-3.6727, 5.6)

    out = find_position_behind_occluder_diagonal_away(0, 1, 4.16, 1.6, 10)
    assert out == (0.0767, 2.32)
    out = find_position_behind_occluder_diagonal_away(0, 1, -4.16, 1.6, 10)
    assert out == (-0.0767, 2.32)
    out = find_position_behind_occluder_diagonal_away(0, 1, 5, 3, 10)
    assert out == (0.066, 3.87)
    out = find_position_behind_occluder_diagonal_away(0, 1, -5, 3, 10)
    assert out == (-0.066, 3.87)

    out = find_position_behind_occluder_diagonal_away(2, 1, 4.16, 1.6, 10)
    assert out == (2.572, 1.88)
    out = find_position_behind_occluder_diagonal_away(2, 1, -4.16, 1.6, 10)
    assert out == (2.4187, 2.76)
    out = find_position_behind_occluder_diagonal_away(2, 1, 5, 3, 10)
    assert out == (3.1285, 3.33)
    out = find_position_behind_occluder_diagonal_away(2, 1, -5, 3, 10)
    assert out == (2.9398, 4.4)

    out = find_position_behind_occluder_diagonal_away(-2, 1, 4.16, 1.6, 10)
    assert out == (-2.4187, 2.76)
    out = find_position_behind_occluder_diagonal_away(-2, 1, -4.16, 1.6, 10)
    assert out == (-2.572, 1.88)
    out = find_position_behind_occluder_diagonal_away(-2, 1, 5, 3, 10)
    assert out == (-2.9398, 4.4)
    out = find_position_behind_occluder_diagonal_away(-2, 1, -5, 3, 10)
    assert out == (-3.1285, 3.33)

    out = find_position_behind_occluder_diagonal_away(0, 1, 4.16, 1.6, 20)
    assert out == (0.0937, 3.08)
    out = find_position_behind_occluder_diagonal_away(0, 1, -4.16, 1.6, 20)
    assert out == (-0.0937, 3.08)
    out = find_position_behind_occluder_diagonal_away(2, 1, 4.16, 1.6, 20)
    assert out == (2.6764, 2.14)
    out = find_position_behind_occluder_diagonal_away(2, 1, -4.16, 1.6, 20)
    assert out == (2.8461, 4.15)
    out = find_position_behind_occluder_diagonal_away(-2, 1, 4.16, 1.6, 20)
    assert out == (-2.8461, 4.15)
    out = find_position_behind_occluder_diagonal_away(-2, 1, -4.16, 1.6, 20)
    assert out == (-2.6764, 2.14)
    out = find_position_behind_occluder_diagonal_away(2, 1, 5, 3, 20)
    assert out == (3.2691, 3.63)
    out = find_position_behind_occluder_diagonal_away(-2, 1, -5, 3, 20)
    assert out == (-3.2691, 3.63)


def test_find_position_behind_occluder_diagonal_toward():
    out = find_position_behind_occluder_diagonal_toward(0, 1, 4.16, 1.6, 0)
    assert out == (0, 1.6)
    out = find_position_behind_occluder_diagonal_toward(0, 1, 6.56, 5.6, 0)
    assert out == (0, 5.6)
    out = find_position_behind_occluder_diagonal_toward(2, 1, 4.16, 1.6, 0)
    assert out == (2.2182, 1.6)
    out = find_position_behind_occluder_diagonal_toward(2, 1, -4.16, 1.6, 0)
    assert out == (2.2182, 1.6)
    out = find_position_behind_occluder_diagonal_toward(2, 1, 6.56, 5.6, 0)
    assert out == (3.6727, 5.6)
    out = find_position_behind_occluder_diagonal_toward(2, 1, -6.56, 5.6, 0)
    assert out == (3.6727, 5.6)
    out = find_position_behind_occluder_diagonal_toward(-2, 1, 4.16, 1.6, 0)
    assert out == (-2.2182, 1.6)
    out = find_position_behind_occluder_diagonal_toward(-2, 1, -4.16, 1.6, 0)
    assert out == (-2.2182, 1.6)
    out = find_position_behind_occluder_diagonal_toward(-2, 1, 6.56, 5.6, 0)
    assert out == (-3.6727, 5.6)
    out = find_position_behind_occluder_diagonal_toward(-2, 1, -6.56, 5.6, 0)
    assert out == (-3.6727, 5.6)

    out = find_position_behind_occluder_diagonal_toward(0, 1, 6.56, 5.6, 10)
    assert out == (0.0947, 4.46)
    out = find_position_behind_occluder_diagonal_toward(0, 1, -6.56, 5.6, 10)
    assert out == (-0.0947, 4.46)
    out = find_position_behind_occluder_diagonal_toward(0, 1, 5, 3, 10)
    assert out == (0.066, 2.13)
    out = find_position_behind_occluder_diagonal_toward(0, 1, -5, 3, 10)
    assert out == (-0.066, 2.13)

    out = find_position_behind_occluder_diagonal_toward(2, 1, 6.56, 5.6, 10)
    assert out == (3.8378, 5.12)
    out = find_position_behind_occluder_diagonal_toward(2, 1, -6.56, 5.6, 10)
    assert out == (2.7976, 3.95)
    out = find_position_behind_occluder_diagonal_toward(2, 1, 5, 3, 10)
    assert out == (2.8449, 2.62)
    out = find_position_behind_occluder_diagonal_toward(2, 1, -5, 3, 10)
    assert out == (2.0891, 1.75)

    out = find_position_behind_occluder_diagonal_toward(-2, 1, 6.56, 5.6, 10)
    assert out == (-2.7976, 3.95)
    out = find_position_behind_occluder_diagonal_toward(-2, 1, -6.56, 5.6, 10)
    assert out == (-3.8378, 5.12)
    out = find_position_behind_occluder_diagonal_toward(-2, 1, 5, 3, 10)
    assert out == (-2.0891, 1.75)
    out = find_position_behind_occluder_diagonal_toward(-2, 1, -5, 3, 10)
    assert out == (-2.8449, 2.62)

    out = find_position_behind_occluder_diagonal_toward(0, 1, 6.56, 5.6, 20)
    assert out == (0.076, 3.24)
    out = find_position_behind_occluder_diagonal_toward(0, 1, -6.56, 5.6, 20)
    assert out == (-0.076, 3.24)
    out = find_position_behind_occluder_diagonal_toward(2, 1, 6.56, 5.6, 20)
    assert out == (3.6477, 4.54)
    out = find_position_behind_occluder_diagonal_toward(2, 1, -6.56, 5.6, 20)
    assert out == (2.2594, 2.39)
    out = find_position_behind_occluder_diagonal_toward(-2, 1, 6.56, 5.6, 20)
    assert out == (-2.2594, 2.39)
    out = find_position_behind_occluder_diagonal_toward(-2, 1, -6.56, 5.6, 20)
    assert out == (-3.6477, 4.54)
    out = find_position_behind_occluder_diagonal_toward(2, 1, 5, 3, 20)
    assert out == (2.6646, 2.15)
    out = find_position_behind_occluder_diagonal_toward(-2, 1, -5, 3, 20)
    assert out == (-2.6646, 2.15)
