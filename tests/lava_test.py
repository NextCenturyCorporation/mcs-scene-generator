from machine_common_sense.config_manager import Vector2dInt

from generator import lava


def test_lava_square():
    p1 = Vector2dInt(x=0, z=0)
    p2 = Vector2dInt(x=2, z=2)
    test_pool = lava.create_square_lava_pool(p1, p2)
    assert len(test_pool) == 9

    p1 = Vector2dInt(x=0, z=0)
    p2 = Vector2dInt(x=2, z=2)
    test_pool = lava.create_square_lava_pool(p1, p2, [p1])
    assert len(test_pool) == 8


def test_lava_square_points():
    p1 = Vector2dInt(x=0, z=0)
    p2 = Vector2dInt(x=2, z=2)
    test_pool = lava.create_square_lava_pool_points(p1, p2)
    assert len(test_pool) == 9

    p1 = Vector2dInt(x=0, z=0)
    p2 = Vector2dInt(x=2, z=2)
    test_pool = lava.create_square_lava_pool_points(p1, p2, [p1])
    assert len(test_pool) == 8


def test_create_L_lava_pool():
    p1 = Vector2dInt(x=0, z=0)
    pm = Vector2dInt(x=0, z=2)
    p2 = Vector2dInt(x=2, z=2)
    test_pool = lava.create_L_lava_pool(p1, pm, p2)
    assert len(test_pool) == 5

    p1 = Vector2dInt(x=0, z=0)
    pm = Vector2dInt(x=0, z=2)
    p2 = Vector2dInt(x=4, z=2)
    test_pool = lava.create_L_lava_pool(p1, pm, p2)
    assert len(test_pool) == 7
