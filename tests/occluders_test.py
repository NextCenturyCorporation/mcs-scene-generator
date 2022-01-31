import pytest

from generator.geometry import ObjectBounds
from generator.materials import MaterialTuple
from generator.occluders import (
    DEFAULT_INTUITIVE_PHYSICS_ROOM_DIMENSIONS,
    OCCLUDER_HEIGHT,
    calculate_separation_distance,
    create_occluder,
    find_rotate_step_length,
    generate_occluder_position,
    generate_sideways_pole_position_x,
)

TEST_MATERIAL_POLE = MaterialTuple('test_material_pole', ['brown'])
TEST_MATERIAL_WALL = MaterialTuple('test_material_wall', ['white'])

DEFAULT_ROOM_Y = DEFAULT_INTUITIVE_PHYSICS_ROOM_DIMENSIONS['y']


def verify_bounds(
    bounds: ObjectBounds,
    position_x: float,
    position_y: float,
    position_z: float,
    scale_x: float,
    scale_y: float,
    scale_z: float
):
    points = [{
        'x': position_x - (scale_x / 2.0),
        'y': 0,
        'z': position_z - (scale_z / 2.0)
    }, {
        'x': position_x - (scale_x / 2.0),
        'y': 0,
        'z': position_z + (scale_z / 2.0)
    }, {
        'x': position_x + (scale_x / 2.0),
        'y': 0,
        'z': position_z + (scale_z / 2.0)
    }, {
        'x': position_x + (scale_x / 2.0),
        'y': 0,
        'z': position_z - (scale_z / 2.0)
    }]
    actual_points = [vars(actual) for actual in bounds.box_xz]
    previous_points = points
    for actual in actual_points:
        next_points = []
        for expected in previous_points:
            if actual != pytest.approx(expected):
                next_points.append(expected)
        previous_points = next_points
    if len(previous_points):
        pytest.fail(
            f'BOUNDS MISMATCH:\nEXPECTED={points}\nACTUAL={actual_points}'
        )
    assert bounds.max_y == position_y + (scale_y / 2.0)
    assert bounds.min_y == 0


def verify_pole(
    pole: dict,
    position_x: float,
    position_y: float = ((DEFAULT_ROOM_Y * 0.5) + (OCCLUDER_HEIGHT * 0.5)),
    position_z: float = 1,
    rotation_y: float = 0,
    scale_x: float = 0.095,
    scale_y: float = ((DEFAULT_ROOM_Y - OCCLUDER_HEIGHT) * 0.5),
    scale_z: float = 0.095,
    move_2_step_begin: int = 21,
    move_3_step_begin: int = 186,
    no_last_step: bool = False,
    repeat: int = None
):
    assert pole['type'] == 'cylinder'
    assert pole['materials'] == [TEST_MATERIAL_POLE[0]]
    assert pole['debug']['info'] == TEST_MATERIAL_POLE[1]

    assert pole['shows'][0]['position']['x'] == position_x
    assert pole['shows'][0]['position']['y'] == position_y
    assert pole['shows'][0]['position']['z'] == position_z
    assert pole['shows'][0]['rotation']['x'] == 0
    assert pole['shows'][0]['rotation']['y'] == rotation_y
    assert pole['shows'][0]['rotation']['z'] == 0
    assert pole['shows'][0]['scale']['x'] == scale_x
    assert pole['shows'][0]['scale']['y'] == scale_y
    assert pole['shows'][0]['scale']['z'] == scale_z
    verify_bounds(
        pole['shows'][0]['boundingBox'],
        position_x,
        position_y,
        position_z,
        scale_x,
        scale_y * 2,
        scale_z
    )

    assert len(pole['moves']) == (2 if no_last_step else 3)
    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == move_2_step_begin
    assert pole['moves'][1]['stepEnd'] == move_2_step_begin + 5
    if not no_last_step:
        assert pole['moves'][2]['stepBegin'] == move_3_step_begin
        assert pole['moves'][2]['stepEnd'] == move_3_step_begin + 5

    assert 'rotates' not in pole


def verify_pole_sideways(
    pole: dict,
    position_x: float,
    position_y: float = (OCCLUDER_HEIGHT * 0.5),
    position_z: float = 1,
    rotation_y: float = 0,
    scale_x: float = 0.095,
    scale_y: float = 4,
    scale_z: float = 0.095,
    move_2_step_begin: int = 21,
    move_3_step_begin: int = 186,
    no_last_step: bool = False,
    repeat: int = None
):
    assert pole['type'] == 'cylinder'
    assert pole['materials'] == [TEST_MATERIAL_POLE[0]]
    assert pole['debug']['info'] == TEST_MATERIAL_POLE[1]

    assert pole['shows'][0]['position']['x'] == position_x
    assert pole['shows'][0]['position']['y'] == position_y
    assert pole['shows'][0]['position']['z'] == position_z
    assert pole['shows'][0]['rotation']['x'] == 0
    assert pole['shows'][0]['rotation']['y'] == rotation_y
    assert pole['shows'][0]['rotation']['z'] == 90
    assert pole['shows'][0]['scale']['x'] == scale_x
    assert pole['shows'][0]['scale']['y'] == scale_y
    assert pole['shows'][0]['scale']['z'] == scale_z
    if rotation_y % 90 == 0:
        verify_bounds(
            pole['shows'][0]['boundingBox'],
            position_x,
            position_y,
            position_z,
            (scale_y * 2) if rotation_y % 180 == 0 else scale_z,
            scale_x,
            scale_z if rotation_y % 180 == 0 else (scale_y * 2)
        )

    assert len(pole['moves']) == (2 if no_last_step else 3)
    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == move_2_step_begin
    assert pole['moves'][1]['stepEnd'] == move_2_step_begin + 5
    if not no_last_step:
        assert pole['moves'][2]['stepBegin'] == move_3_step_begin
        assert pole['moves'][2]['stepEnd'] == move_3_step_begin + 5

    assert 'rotates' not in pole


def verify_wall(
    wall: dict,
    position_x: float,
    position_y: float = (OCCLUDER_HEIGHT * 0.5),
    position_z: float = 1,
    rotation_y: float = 0,
    scale_x: float = 1,
    scale_y: float = OCCLUDER_HEIGHT,
    scale_z: float = 0.1,
    move_2_step_begin: int = 21,
    move_3_step_begin: int = 186,
    no_last_step: bool = False,
    sideways: bool = False,
    repeat: int = None
):
    assert wall['type'] == 'cube'
    assert wall['materials'] == [TEST_MATERIAL_WALL[0]]
    assert wall['debug']['info'] == TEST_MATERIAL_WALL[1]

    assert wall['shows'][0]['position']['x'] == position_x
    assert wall['shows'][0]['position']['y'] == position_y
    assert wall['shows'][0]['position']['z'] == position_z
    assert wall['shows'][0]['rotation']['x'] == 0
    assert wall['shows'][0]['rotation']['y'] == rotation_y
    assert wall['shows'][0]['rotation']['z'] == 0
    assert wall['shows'][0]['scale']['x'] == scale_x
    assert wall['shows'][0]['scale']['y'] == scale_y
    assert wall['shows'][0]['scale']['z'] == scale_z
    if rotation_y % 90 == 0:
        verify_bounds(
            wall['shows'][0]['boundingBox'],
            position_x,
            position_y,
            position_z,
            scale_x if rotation_y % 180 == 0 else scale_z,
            scale_y,
            scale_z if rotation_y % 180 == 0 else scale_x
        )

    move_2_step_end = move_2_step_begin + 5
    move_3_step_end = move_3_step_begin + 5

    assert len(wall['moves']) == (2 if no_last_step else 3)
    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == move_2_step_begin
    assert wall['moves'][1]['stepEnd'] == move_2_step_end

    rotate_length = find_rotate_step_length(scale_x) - 1
    rotate_amount = int(90.0 / (rotate_length + 1)) * (
        1 if (sideways or position_x < 0) else -1
    )

    assert len(wall['rotates']) == (2 if no_last_step else 3)
    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 7 + rotate_length
    assert wall['rotates'][1]['stepBegin'] == (
        move_2_step_begin - 1 - rotate_length
    )
    assert wall['rotates'][1]['stepEnd'] == move_2_step_begin - 1

    prop = 'x' if sideways else 'y'
    assert wall['rotates'][0]['vector'][prop] == rotate_amount
    assert wall['rotates'][1]['vector'][prop] == rotate_amount * -1

    if not no_last_step:
        assert wall['moves'][2]['stepBegin'] == move_3_step_begin
        assert wall['moves'][2]['stepEnd'] == move_3_step_end
        assert wall['rotates'][2]['stepBegin'] == move_3_step_end + 1
        assert wall['rotates'][2]['stepEnd'] == (
            move_3_step_end + 1 + rotate_length
        )
        assert wall['rotates'][2]['vector'][prop] == rotate_amount

    if repeat is not None:
        assert wall['moves'][0]['repeat']
        assert wall['moves'][1]['repeat']
        move_interval = (move_2_step_end - 5 + repeat)
        assert wall['moves'][0]['stepWait'] == move_interval
        assert wall['moves'][1]['stepWait'] == move_interval
        assert wall['rotates'][0]['repeat']
        assert wall['rotates'][1]['repeat']
        rotate_interval = (move_2_step_end - rotate_length + repeat)
        assert wall['rotates'][0]['stepWait'] == rotate_interval
        assert wall['rotates'][1]['stepWait'] == rotate_interval


def test_create_occluder_normal_positive_x():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(wall, position_x=1)
    verify_pole(pole, position_x=1)


def test_create_occluder_normal_negative_x():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=-1,
        occluder_width=1,
        last_step=200
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(wall, position_x=-1)
    verify_pole(pole, position_x=-1)


def test_create_occluder_narrow():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=0.5,
        last_step=200
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        scale_x=0.5,
        move_2_step_begin=17,
        move_3_step_begin=188
    )
    verify_pole(
        pole,
        position_x=1,
        move_2_step_begin=17,
        move_3_step_begin=188
    )


def test_create_occluder_wide():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1.5,
        last_step=200
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        scale_x=1.5,
        move_2_step_begin=23,
        move_3_step_begin=185
    )
    verify_pole(
        pole,
        position_x=1,
        move_2_step_begin=23,
        move_3_step_begin=185
    )


def test_create_occluder_very_wide():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=4,
        last_step=200
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        scale_x=4,
        move_2_step_begin=71,
        move_3_step_begin=161
    )
    verify_pole(
        pole,
        position_x=1,
        move_2_step_begin=71,
        move_3_step_begin=161
    )


def test_create_occluder_with_modified_last_step():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=160
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        scale_x=1,
        move_2_step_begin=21,
        move_3_step_begin=146
    )
    verify_pole(
        pole,
        position_x=1,
        move_2_step_begin=21,
        move_3_step_begin=146
    )


def test_create_occluder_sideways_left_positive_x():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        sideways_left=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=-3.5,
        scale_y=4
    )


def test_create_occluder_sideways_left_positive_x_wide_wall():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=2,
        last_step=200,
        sideways_left=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        scale_x=2,
        move_2_step_begin=29,
        move_3_step_begin=182,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=-3.75,
        scale_y=3.75,
        move_2_step_begin=29,
        move_3_step_begin=182
    )


def test_create_occluder_sideways_left_negative_x():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=-1,
        occluder_width=1,
        last_step=200,
        sideways_left=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=-1,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=-4.5,
        scale_y=3
    )


def test_create_occluder_sideways_left_negative_x_wide_wall():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=-1,
        occluder_width=2,
        last_step=200,
        sideways_left=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=-1,
        scale_x=2,
        move_2_step_begin=29,
        move_3_step_begin=182,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=-4.75,
        scale_y=2.75,
        move_2_step_begin=29,
        move_3_step_begin=182
    )


def test_create_occluder_sideways_right_positive_x():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        sideways_right=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=4.5,
        scale_y=3
    )


def test_create_occluder_sideways_right_positive_x_wide_wall():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=2,
        last_step=200,
        sideways_right=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        scale_x=2,
        move_2_step_begin=29,
        move_3_step_begin=182,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=4.75,
        scale_y=2.75,
        move_2_step_begin=29,
        move_3_step_begin=182
    )


def test_create_occluder_sideways_right_negative_x():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=-1,
        occluder_width=1,
        last_step=200,
        sideways_right=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=-1,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=3.5,
        scale_y=4
    )


def test_create_occluder_sideways_right_negative_x_wide_wall():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=-1,
        occluder_width=2,
        last_step=200,
        sideways_right=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=-1,
        scale_x=2,
        move_2_step_begin=29,
        move_3_step_begin=182,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=3.75,
        scale_y=3.75,
        move_2_step_begin=29,
        move_3_step_begin=182
    )


def test_create_occluder_no_last_step():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        no_last_step=True
    )
    verify_pole(
        pole,
        position_x=1,
        no_last_step=True
    )


def test_create_occluder_custom_height_thickness_and_z_position():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        occluder_height=3,
        occluder_thickness=0.5,
        z_position=-2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_y=1.5,
        position_z=-2,
        scale_y=3,
        scale_z=0.5
    )
    verify_pole(
        pole,
        position_x=1,
        position_y=3.5,
        position_z=-2,
        scale_x=0.495,
        scale_y=0.5,
        scale_z=0.495
    )


def test_create_occluder_repeat_movement():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        repeat_movement=10
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        no_last_step=True,
        repeat=10
    )
    verify_pole(
        pole,
        position_x=1,
        no_last_step=True,
        repeat=10
    )


def test_create_occluder_repeat_movement_with_very_wide_wall():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=4,
        last_step=200,
        repeat_movement=10
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        scale_x=4,
        move_2_step_begin=71,
        no_last_step=True,
        repeat=10
    )
    verify_pole(
        pole,
        position_x=1,
        move_2_step_begin=71,
        no_last_step=True,
        repeat=10
    )


def test_create_occluder_room_dimensions():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        room_dimensions={'x': 10, 'y': 6, 'z': 8}
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1
    )
    verify_pole(
        pole,
        position_x=1,
        position_y=3.9,
        scale_y=2.1
    )


def test_create_occluder_y_rotation():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        y_rotation=45
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        rotation_y=45
    )
    verify_pole(
        pole,
        position_x=1
    )


def test_create_occluder_sideways_back_positive_z():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        sideways_back=True,
        z_position=2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=2,
        rotation_y=90,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=-1.75,
        rotation_y=90,
        scale_y=3.25
    )


def test_create_occluder_sideways_back_positive_z_wide_wall():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=2,
        last_step=200,
        sideways_back=True,
        z_position=2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=2,
        scale_x=2,
        rotation_y=90,
        move_2_step_begin=29,
        move_3_step_begin=182,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=-2,
        rotation_y=90,
        scale_y=3,
        move_2_step_begin=29,
        move_3_step_begin=182
    )


def test_create_occluder_sideways_back_negative_z():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        sideways_back=True,
        z_position=-2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=-2,
        rotation_y=90,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=-3.75,
        rotation_y=90,
        scale_y=1.25
    )


def test_create_occluder_sideways_back_negative_z_wide_wall():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=2,
        last_step=200,
        sideways_back=True,
        z_position=-2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=-2,
        scale_x=2,
        rotation_y=90,
        move_2_step_begin=29,
        move_3_step_begin=182,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=-4,
        rotation_y=90,
        scale_y=1,
        move_2_step_begin=29,
        move_3_step_begin=182
    )


def test_create_occluder_sideways_front_positive_z():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        sideways_front=True,
        z_position=2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=2,
        rotation_y=90,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=3.75,
        rotation_y=90,
        scale_y=1.25
    )


def test_create_occluder_sideways_front_positive_z_wide_wall():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=2,
        last_step=200,
        sideways_front=True,
        z_position=2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=2,
        rotation_y=90,
        scale_x=2,
        move_2_step_begin=29,
        move_3_step_begin=182,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=4,
        rotation_y=90,
        scale_y=1,
        move_2_step_begin=29,
        move_3_step_begin=182
    )


def test_create_occluder_sideways_front_negative_z():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        sideways_front=True,
        z_position=-2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=-2,
        rotation_y=90,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=1.75,
        rotation_y=90,
        scale_y=3.25
    )


def test_create_occluder_sideways_front_negative_z_wide_wall():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=2,
        last_step=200,
        sideways_front=True,
        z_position=-2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=-2,
        rotation_y=90,
        scale_x=2,
        move_2_step_begin=29,
        move_3_step_begin=182,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=2,
        rotation_y=90,
        scale_y=3,
        move_2_step_begin=29,
        move_3_step_begin=182
    )


def test_create_occluder_sideways_back_reverse_direction():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        reverse_direction=True,
        sideways_back=True,
        z_position=2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=2,
        rotation_y=-90,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=-1.75,
        rotation_y=90,
        scale_y=3.25
    )


def test_create_occluder_sideways_back_with_modified_room_dimensions():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        room_dimensions={'x': 10, 'y': 3, 'z': 14},
        sideways_back=True,
        z_position=2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=2,
        rotation_y=90,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=-2.75,
        rotation_y=90,
        scale_y=4.25
    )


def test_create_occluder_sideways_front_reverse_direction():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        reverse_direction=True,
        sideways_front=True,
        z_position=2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=2,
        rotation_y=-90,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=3.75,
        rotation_y=90,
        scale_y=1.25
    )


def test_create_occluder_sideways_front_with_modified_room_dimensions():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        room_dimensions={'x': 10, 'y': 3, 'z': 14},
        sideways_front=True,
        z_position=2
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        position_z=2,
        rotation_y=90,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=1,
        position_z=4.75,
        rotation_y=90,
        scale_y=2.25
    )


def test_create_occluder_sideways_left_reverse_direction():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        reverse_direction=True,
        sideways_left=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        rotation_y=180,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=-3.5,
        scale_y=4
    )


def test_create_occluder_sideways_left_with_modified_room_dimensions():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        room_dimensions={'x': 11, 'y': 3, 'z': 10},
        sideways_left=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=-2.5,
        scale_y=3
    )


def test_create_occluder_sideways_right_reverse_direction():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        reverse_direction=True,
        sideways_right=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        rotation_y=180,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=4.5,
        scale_y=3
    )


def test_create_occluder_sideways_right_with_modified_room_dimensions():
    occluder = create_occluder(
        wall_material=TEST_MATERIAL_WALL,
        pole_material=TEST_MATERIAL_POLE,
        x_position=1,
        occluder_width=1,
        last_step=200,
        room_dimensions={'x': 11, 'y': 3, 'z': 10},
        sideways_right=True
    )
    assert len(occluder) == 2
    wall, pole = occluder
    verify_wall(
        wall,
        position_x=1,
        sideways=True
    )
    verify_pole_sideways(
        pole,
        position_x=3.5,
        scale_y=2
    )


def test_calculate_separation_distance():
    assert calculate_separation_distance(0.5, 1, 2.5, 1) == pytest.approx(0.5)
    assert calculate_separation_distance(0, 1, 2.5, 1) == pytest.approx(1)
    assert calculate_separation_distance(-1, 1, -3, 1) == pytest.approx(0.5)
    assert calculate_separation_distance(-1, 1, 2, 1) == pytest.approx(1.5)
    assert calculate_separation_distance(1, 0.5, 3, 0.5) == pytest.approx(1)
    assert calculate_separation_distance(1, 1, 2.5, 1) == pytest.approx(0)
    assert calculate_separation_distance(1, 1, 2, 1) == pytest.approx(-0.5)
    assert calculate_separation_distance(1, 1, 2, 2) == pytest.approx(-1)


def test_find_rotate_step_length():
    for i in list(range(1, 51)):
        size = i / 10.0
        step_length = find_rotate_step_length(size)
        assert 2 <= step_length <= 30
        assert 90 % step_length == 0


def test_generate_occluder_position():
    assert -2.75 <= generate_occluder_position(0.5, []) <= 2.75
    assert -2.5 <= generate_occluder_position(1, []) <= 2.5

    occluder_1 = {'shows': [{'position': {'x': 2}, 'scale': {'x': 1}}]}
    assert -2.5 <= generate_occluder_position(1, [occluder_1]) <= 1

    occluder_2 = {'shows': [{'position': {'x': -2.25}, 'scale': {'x': 0.5}}]}
    assert -1.5 <= generate_occluder_position(1, [occluder_1, occluder_2]) <= 1


def test_generate_sideways_pole_position_x():
    assert generate_sideways_pole_position_x(-1, 1, False) == 2.25
    assert generate_sideways_pole_position_x(0, 1, False) == 2.75
    assert generate_sideways_pole_position_x(1, 1, False) == 3.25

    assert generate_sideways_pole_position_x(-1, 3, False) == 2.75
    assert generate_sideways_pole_position_x(0, 3, False) == 3.25
    assert generate_sideways_pole_position_x(1, 3, False) == 3.75

    assert generate_sideways_pole_position_x(-1, 1, False, 6) == 1.25
    assert generate_sideways_pole_position_x(0, 1, False, 6) == 1.75
    assert generate_sideways_pole_position_x(1, 1, False, 6) == 2.25

    assert generate_sideways_pole_position_x(-1, 1, True) == -3.25
    assert generate_sideways_pole_position_x(0, 1, True) == -2.75
    assert generate_sideways_pole_position_x(1, 1, True) == -2.25

    assert generate_sideways_pole_position_x(-1, 3, True) == -3.75
    assert generate_sideways_pole_position_x(0, 3, True) == -3.25
    assert generate_sideways_pole_position_x(1, 3, True) == -2.75

    assert generate_sideways_pole_position_x(-1, 1, True, 6) == -2.25
    assert generate_sideways_pole_position_x(0, 1, True, 6) == -1.75
    assert generate_sideways_pole_position_x(1, 1, True, 6) == -1.25
