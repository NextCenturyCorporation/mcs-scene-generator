import pytest
from machine_common_sense.config_manager import Vector3d

from generator import (
    ALL_LARGE_BLOCK_TOOLS,
    MaterialTuple,
    ObjectBounds,
    structures,
)


def test_create_interior_wall():
    wall = structures.create_interior_wall(
        position_x=1,
        position_z=2,
        rotation_y=0,
        width=4,
        height=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert isinstance(wall['id'], str)
    assert wall['kinematic'] is True
    assert wall['structure'] is True
    assert wall['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert wall['mass'] == 250
    assert wall['materials'] == ['test_material']
    assert wall['debug']['color'] == ['black', 'white']
    assert wall['debug']['info'] == [
        'black', 'white', 'wall', 'black wall', 'white wall',
        'black white wall'
    ]

    assert len(wall['shows']) == 1
    assert wall['shows'][0]['stepBegin'] == 0
    assert wall['shows'][0]['position'] == {'x': 1, 'y': 2.5, 'z': 2}
    assert wall['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert wall['shows'][0]['scale'] == {'x': 4, 'y': 5, 'z': 0.1}
    assert len(wall['shows'][0]['boundingBox'].box_xz) == 4
    wall_bounds = wall['shows'][0]['boundingBox']
    assert vars(wall_bounds.box_xz[0]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': 2.05}
    )
    assert vars(wall_bounds.box_xz[1]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': 1.95}
    )
    assert vars(wall_bounds.box_xz[2]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': 1.95}
    )
    assert vars(wall_bounds.box_xz[3]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': 2.05}
    )
    assert wall_bounds.max_y == 5
    assert wall_bounds.min_y == 0


def test_create_interior_wall_optional_parameters():
    bounds = ObjectBounds(box_xz=[
        Vector3d(**{'x': 0.11, 'y': 0.12, 'z': 0.13}),
        Vector3d(**{'x': 0.21, 'y': 0.22, 'z': 0.23}),
        Vector3d(**{'x': 0.31, 'y': 0.32, 'z': 0.33}),
        Vector3d(**{'x': 0.41, 'y': 0.42, 'z': 0.43})
    ], max_y=0, min_y=0)
    wall = structures.create_interior_wall(
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        height=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        thickness=6,
        position_y_modifier=10,
        bounds=bounds
    )

    assert isinstance(wall['id'], str)
    assert wall['kinematic'] is True
    assert wall['structure'] is True
    assert wall['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert wall['mass'] == 15000
    assert wall['materials'] == ['test_material']
    assert wall['debug']['color'] == ['black', 'white']
    assert wall['debug']['info'] == [
        'black', 'white', 'wall', 'black wall', 'white wall',
        'black white wall'
    ]

    assert len(wall['shows']) == 1
    assert wall['shows'][0]['stepBegin'] == 0
    assert wall['shows'][0]['position'] == {'x': 1, 'y': 12.5, 'z': 2}
    assert wall['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert wall['shows'][0]['scale'] == {'x': 4, 'y': 5, 'z': 6}
    assert wall['shows'][0]['boundingBox'] == bounds


def test_create_l_occluder():
    occluder = structures.create_l_occluder(
        position_x=1,
        position_z=2,
        rotation_y=0,
        scale_front_x=2.5,
        scale_front_z=0.5,
        scale_side_x=1.5,
        scale_side_z=3.5,
        scale_y=4.5,
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert len(occluder) == 2
    front = occluder[0]
    side = occluder[1]

    assert isinstance(front['id'], str)
    assert front['kinematic'] is True
    assert front['structure'] is True
    assert front['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert front['mass'] == 703
    assert front['materials'] == ['test_material']
    assert front['debug']['color'] == ['black', 'white']
    assert front['debug']['info'] == [
        'black', 'white', 'occluder', 'black occluder', 'white occluder',
        'black white occluder'
    ]

    assert len(front['shows']) == 1
    assert front['shows'][0]['stepBegin'] == 0
    assert front['shows'][0]['position'] == {'x': 1, 'y': 2.25, 'z': 2}
    assert front['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert front['shows'][0]['scale'] == {'x': 2.5, 'y': 4.5, 'z': 0.5}
    front_bounds = front['shows'][0]['boundingBox']
    assert vars(front_bounds.box_xz[0]) == pytest.approx(
        {'x': 2.25, 'y': 0, 'z': 2.25}
    )
    assert vars(front_bounds.box_xz[1]) == pytest.approx(
        {'x': 2.25, 'y': 0, 'z': 1.75}
    )
    assert vars(front_bounds.box_xz[2]) == pytest.approx(
        {'x': -0.25, 'y': 0, 'z': 1.75}
    )
    assert vars(front_bounds.box_xz[3]) == pytest.approx(
        {'x': -0.25, 'y': 0, 'z': 2.25}
    )
    assert front_bounds.max_y == 4.5
    assert front_bounds.min_y == 0

    assert isinstance(side['id'], str)
    assert side['kinematic'] is True
    assert side['structure'] is True
    assert side['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert side['mass'] == 2953
    assert side['materials'] == ['test_material']
    assert side['debug']['color'] == ['black', 'white']
    assert side['debug']['info'] == [
        'black', 'white', 'occluder', 'black occluder', 'white occluder',
        'black white occluder'
    ]

    assert len(side['shows']) == 1
    assert side['shows'][0]['stepBegin'] == 0
    assert side['shows'][0]['position'] == {'x': 0.5, 'y': 2.25, 'z': 4}
    assert side['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert side['shows'][0]['scale'] == {'x': 1.5, 'y': 4.5, 'z': 3.5}
    assert len(side['shows'][0]['boundingBox'].box_xz) == 4
    side_bounds = side['shows'][0]['boundingBox']
    assert vars(side_bounds.box_xz[0]) == pytest.approx(
        {'x': 1.25, 'y': 0, 'z': 5.75}
    )
    assert vars(side_bounds.box_xz[1]) == pytest.approx(
        {'x': 1.25, 'y': 0, 'z': 2.25}
    )
    assert vars(side_bounds.box_xz[2]) == pytest.approx(
        {'x': -0.25, 'y': 0, 'z': 2.25}
    )
    assert vars(side_bounds.box_xz[3]) == pytest.approx(
        {'x': -0.25, 'y': 0, 'z': 5.75}
    )
    assert side_bounds.max_y == 4.5
    assert side_bounds.min_y == 0


def test_create_l_occluder_optional_parameters():
    occluder = structures.create_l_occluder(
        position_x=-1,
        position_z=2,
        rotation_y=0,
        scale_front_x=2.5,
        scale_front_z=0.5,
        scale_side_x=1.5,
        scale_side_z=3.5,
        scale_y=4.5,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        position_y_modifier=10,
        flip=True
    )

    assert len(occluder) == 2
    front = occluder[0]
    side = occluder[1]

    assert isinstance(front['id'], str)
    assert front['kinematic'] is True
    assert front['structure'] is True
    assert front['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert front['mass'] == 703
    assert front['materials'] == ['test_material']
    assert front['debug']['color'] == ['black', 'white']
    assert front['debug']['info'] == [
        'black', 'white', 'occluder', 'black occluder', 'white occluder',
        'black white occluder'
    ]

    assert len(front['shows']) == 1
    assert front['shows'][0]['stepBegin'] == 0
    assert front['shows'][0]['position'] == {'x': -1, 'y': 12.25, 'z': 2}
    assert front['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert front['shows'][0]['scale'] == {'x': 2.5, 'y': 4.5, 'z': 0.5}
    assert len(front['shows'][0]['boundingBox'].box_xz) == 4
    front_bounds = front['shows'][0]['boundingBox']
    assert vars(front_bounds.box_xz[0]) == pytest.approx(
        {'x': 0.25, 'y': 0, 'z': 2.25}
    )
    assert vars(front_bounds.box_xz[1]) == pytest.approx(
        {'x': 0.25, 'y': 0, 'z': 1.75}
    )
    assert vars(front_bounds.box_xz[2]) == pytest.approx(
        {'x': -2.25, 'y': 0, 'z': 1.75}
    )
    assert vars(front_bounds.box_xz[3]) == pytest.approx(
        {'x': -2.25, 'y': 0, 'z': 2.25}
    )
    assert front_bounds.max_y == 14.5
    assert front_bounds.min_y == 10

    assert isinstance(side['id'], str)
    assert side['kinematic'] is True
    assert side['structure'] is True
    assert side['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert side['mass'] == 2953
    assert side['materials'] == ['test_material']
    assert side['debug']['color'] == ['black', 'white']
    assert side['debug']['info'] == [
        'black', 'white', 'occluder', 'black occluder', 'white occluder',
        'black white occluder'
    ]

    assert len(side['shows']) == 1
    assert side['shows'][0]['stepBegin'] == 0
    assert side['shows'][0]['position'] == {'x': -0.5, 'y': 12.25, 'z': 4}
    assert side['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert side['shows'][0]['scale'] == {'x': 1.5, 'y': 4.5, 'z': 3.5}
    assert len(side['shows'][0]['boundingBox'].box_xz) == 4
    side_bounds = side['shows'][0]['boundingBox']
    assert vars(side_bounds.box_xz[0]) == pytest.approx(
        {'x': 0.25, 'y': 0, 'z': 5.75}
    )
    assert vars(side_bounds.box_xz[1]) == pytest.approx(
        {'x': 0.25, 'y': 0, 'z': 2.25}
    )
    assert vars(side_bounds.box_xz[2]) == pytest.approx(
        {'x': -1.25, 'y': 0, 'z': 2.25}
    )
    assert vars(side_bounds.box_xz[3]) == pytest.approx(
        {'x': -1.25, 'y': 0, 'z': 5.75}
    )
    assert side_bounds.max_y == 14.5
    assert side_bounds.min_y == 10


def test_create_l_occluder_with_rotation():
    occluder = structures.create_l_occluder(
        position_x=2,
        position_z=2,
        rotation_y=45,
        scale_front_x=3,
        scale_front_z=1,
        scale_side_x=1,
        scale_side_z=1,
        scale_y=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert len(occluder) == 2
    front = occluder[0]
    side = occluder[1]

    assert len(front['shows']) == 1
    assert front['shows'][0]['stepBegin'] == 0
    assert front['shows'][0]['position'] == {'x': 2, 'y': 2.5, 'z': 2}
    assert front['shows'][0]['rotation'] == {'x': 0, 'y': 45, 'z': 0}
    assert front['shows'][0]['scale'] == {'x': 3, 'y': 5, 'z': 1}
    front_bounds = front['shows'][0]['boundingBox']
    assert vars(front_bounds.box_xz[0]) == pytest.approx(
        {'x': 3.414214, 'y': 0, 'z': 1.292893}
    )
    assert vars(front_bounds.box_xz[1]) == pytest.approx(
        {'x': 2.707107, 'y': 0, 'z': 0.585786}
    )
    assert vars(front_bounds.box_xz[2]) == pytest.approx(
        {'x': 0.585786, 'y': 0, 'z': 2.707107}
    )
    assert vars(front_bounds.box_xz[3]) == pytest.approx(
        {'x': 1.292893, 'y': 0, 'z': 3.414214}
    )
    assert front_bounds.max_y == 5
    assert front_bounds.min_y == 0

    assert len(side['shows']) == 1
    assert side['shows'][0]['stepBegin'] == 0
    assert side['shows'][0]['position'] == pytest.approx(
        {'x': 2, 'y': 2.5, 'z': 3.414214}
    )
    assert side['shows'][0]['rotation'] == {'x': 0, 'y': 45, 'z': 0}
    assert side['shows'][0]['scale'] == {'x': 1, 'y': 5, 'z': 1}
    assert len(side['shows'][0]['boundingBox'].box_xz) == 4
    side_bounds = side['shows'][0]['boundingBox']
    assert vars(side_bounds.box_xz[0]) == pytest.approx(
        {'x': 2.707107, 'y': 0, 'z': 3.414214}
    )
    assert vars(side_bounds.box_xz[1]) == pytest.approx(
        {'x': 2, 'y': 0, 'z': 2.707107}
    )
    assert vars(side_bounds.box_xz[2]) == pytest.approx(
        {'x': 1.292893, 'y': 0, 'z': 3.414214}
    )
    assert vars(side_bounds.box_xz[3]) == pytest.approx(
        {'x': 2, 'y': 0, 'z': 4.12132}
    )
    assert side_bounds.max_y == 5
    assert side_bounds.min_y == 0


def test_create_platform():
    platform = structures.create_platform(
        position_x=1,
        position_z=2,
        rotation_y=0,
        scale_x=4,
        scale_y=5,
        scale_z=6,
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert isinstance(platform['id'], str)
    assert platform['kinematic'] is True
    assert platform['structure'] is True
    assert platform['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert platform['mass'] == 15000
    assert platform['materials'] == ['test_material']
    assert platform['debug']['color'] == ['black', 'white']
    assert platform['debug']['info'] == [
        'black', 'white', 'platform', 'black platform', 'white platform',
        'black white platform'
    ]

    assert len(platform['shows']) == 1
    assert platform['shows'][0]['stepBegin'] == 0
    assert platform['shows'][0]['position'] == {'x': 1, 'y': 2.5, 'z': 2}
    assert platform['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert platform['shows'][0]['scale'] == {'x': 4, 'y': 5, 'z': 6}
    platform_bounds = platform['shows'][0]['boundingBox']
    assert vars(platform_bounds.box_xz[0]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': 5}
    )
    assert vars(platform_bounds.box_xz[1]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': -1}
    )
    assert vars(platform_bounds.box_xz[2]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': -1}
    )
    assert vars(platform_bounds.box_xz[3]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': 5}
    )
    assert platform_bounds.max_y == 5
    assert platform_bounds.min_y == 0
    assert platform['lips']['front'] is False
    assert platform['lips']['back'] is False
    assert platform['lips']['left'] is False
    assert platform['lips']['right'] is False


def test_create_platform_with_lips():
    platform = structures.create_platform(
        position_x=1,
        position_z=2,
        rotation_y=0,
        scale_x=4,
        scale_y=5,
        scale_z=6,
        lips={
            'front': True,
            'back': True,
            'left': False,
            'right': False
        },
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert isinstance(platform['id'], str)
    assert platform['kinematic'] is True
    assert platform['structure'] is True
    assert platform['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert platform['mass'] == 15000
    assert platform['materials'] == ['test_material']
    assert platform['debug']['color'] == ['black', 'white']
    assert platform['debug']['info'] == [
        'black', 'white', 'platform', 'black platform', 'white platform',
        'black white platform'
    ]

    assert len(platform['shows']) == 1
    assert platform['shows'][0]['stepBegin'] == 0
    assert platform['shows'][0]['position'] == {'x': 1, 'y': 2.5, 'z': 2}
    assert platform['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert platform['shows'][0]['scale'] == {'x': 4, 'y': 5, 'z': 6}
    platform_bounds = platform['shows'][0]['boundingBox']
    assert vars(platform_bounds.box_xz[0]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': 5}
    )
    assert vars(platform_bounds.box_xz[1]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': -1}
    )
    assert vars(platform_bounds.box_xz[2]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': -1}
    )
    assert vars(platform_bounds.box_xz[3]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': 5}
    )
    assert platform_bounds.max_y == 5
    assert platform_bounds.min_y == 0

    assert platform['lips']['front'] is True
    assert platform['lips']['back'] is True
    assert platform['lips']['left'] is False
    assert platform['lips']['right'] is False


def test_create_platform_optional_parameters():
    bounds = ObjectBounds(box_xz=[
        Vector3d(**{'x': 0.11, 'y': 0.12, 'z': 0.13}),
        Vector3d(**{'x': 0.21, 'y': 0.22, 'z': 0.23}),
        Vector3d(**{'x': 0.31, 'y': 0.32, 'z': 0.33}),
        Vector3d(**{'x': 0.41, 'y': 0.42, 'z': 0.43})
    ], max_y=0, min_y=0)
    platform = structures.create_platform(
        position_x=1,
        position_z=2,
        rotation_y=3,
        scale_x=4,
        scale_y=5,
        scale_z=6,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        position_y_modifier=10,
        bounds=bounds
    )

    assert isinstance(platform['id'], str)
    assert platform['kinematic'] is True
    assert platform['structure'] is True
    assert platform['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert platform['mass'] == 15000
    assert platform['materials'] == ['test_material']
    assert platform['debug']['color'] == ['black', 'white']
    assert platform['debug']['info'] == [
        'black', 'white', 'platform', 'black platform', 'white platform',
        'black white platform'
    ]

    assert len(platform['shows']) == 1
    assert platform['shows'][0]['stepBegin'] == 0
    assert platform['shows'][0]['position'] == {'x': 1, 'y': 12.5, 'z': 2}
    assert platform['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert platform['shows'][0]['scale'] == {'x': 4, 'y': 5, 'z': 6}
    assert platform['shows'][0]['boundingBox'] == bounds


def test_create_ramp_15_degree():
    ramp = structures.create_ramp(
        angle=15,
        position_x=1,
        position_z=2,
        rotation_y=0,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'triangle'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 3349
    assert ramp['materials'] == ['test_material']
    assert ramp['debug']['color'] == ['black', 'white']
    assert ramp['debug']['info'] == [
        'black', 'white', 'ramp', 'ramp_15_degree', 'black ramp', 'white ramp',
        'black white ramp', 'black ramp_15_degree', 'white ramp_15_degree',
        'black white ramp_15_degree'
    ]

    assert len(ramp['shows']) == 1
    assert ramp['shows'][0]['stepBegin'] == 0
    assert ramp['shows'][0]['position']['x'] == 1
    assert ramp['shows'][0]['position']['y'] == pytest.approx(0.66987298)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(1.339745)
    assert ramp['shows'][0]['scale']['z'] == 5
    ramp_bounds = ramp['shows'][0]['boundingBox']
    assert vars(ramp_bounds.box_xz[0]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': 4.5}
    )
    assert vars(ramp_bounds.box_xz[1]) == pytest.approx(
        {'x': 2.999999, 'y': 0, 'z': -0.5}
    )

    assert vars(ramp_bounds.box_xz[2]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': -0.5}
    )
    assert vars(ramp_bounds.box_xz[3]) == pytest.approx(
        {'x': -0.99999999, 'y': 0, 'z': 4.5}
    )
    assert ramp_bounds.max_y == pytest.approx(1.33974596)
    assert ramp_bounds.min_y == pytest.approx(0.0)


def test_create_ramp_15_degree_optional_parameters():
    bounds = ObjectBounds(box_xz=[
        Vector3d(**{'x': 0.11, 'y': 0.12, 'z': 0.13}),
        Vector3d(**{'x': 0.21, 'y': 0.22, 'z': 0.23}),
        Vector3d(**{'x': 0.31, 'y': 0.32, 'z': 0.33}),
        Vector3d(**{'x': 0.41, 'y': 0.42, 'z': 0.43})
    ], max_y=0, min_y=0)
    ramp = structures.create_ramp(
        angle=15,
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        position_y_modifier=10,
        bounds=bounds
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'triangle'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 3349
    assert ramp['materials'] == ['test_material']
    assert ramp['debug']['color'] == ['black', 'white']
    assert ramp['debug']['info'] == [
        'black', 'white', 'ramp', 'ramp_15_degree', 'black ramp', 'white ramp',
        'black white ramp', 'black ramp_15_degree', 'white ramp_15_degree',
        'black white ramp_15_degree'
    ]

    assert len(ramp['shows']) == 1
    assert ramp['shows'][0]['stepBegin'] == 0
    assert ramp['shows'][0]['position']['x'] == 1
    assert ramp['shows'][0]['position']['y'] == pytest.approx(10.66987298)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(1.33974596)
    assert ramp['shows'][0]['scale']['z'] == 5
    assert ramp['shows'][0]['boundingBox'] == bounds


def test_create_ramp_30_degree():
    ramp = structures.create_ramp(
        angle=30,
        position_x=1,
        position_z=2,
        rotation_y=0,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'triangle'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 7217
    assert ramp['materials'] == ['test_material']
    assert ramp['debug']['color'] == ['black', 'white']
    assert ramp['debug']['info'] == [
        'black', 'white', 'ramp', 'ramp_30_degree', 'black ramp', 'white ramp',
        'black white ramp', 'black ramp_30_degree', 'white ramp_30_degree',
        'black white ramp_30_degree'
    ]

    assert len(ramp['shows']) == 1
    assert ramp['shows'][0]['stepBegin'] == 0
    assert ramp['shows'][0]['position']['x'] == 1
    assert ramp['shows'][0]['position']['y'] == pytest.approx(1.44337567)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(2.8867513459)
    assert ramp['shows'][0]['scale']['z'] == 5
    ramp_bounds = ramp['shows'][0]['boundingBox']
    assert vars(ramp_bounds.box_xz[0]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': 4.5}
    )
    assert vars(ramp_bounds.box_xz[1]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': -0.5}
    )
    assert vars(ramp_bounds.box_xz[2]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': -0.5}
    )
    assert vars(ramp_bounds.box_xz[3]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': 4.5}
    )
    assert ramp_bounds.max_y == pytest.approx(2.8867513459)
    assert ramp_bounds.min_y == pytest.approx(0.0)


def test_create_ramp_30_degree_optional_parameters():
    bounds = ObjectBounds(box_xz=[
        Vector3d(**{'x': 0.11, 'y': 0.12, 'z': 0.13}),
        Vector3d(**{'x': 0.21, 'y': 0.22, 'z': 0.23}),
        Vector3d(**{'x': 0.31, 'y': 0.32, 'z': 0.33}),
        Vector3d(**{'x': 0.41, 'y': 0.42, 'z': 0.43})
    ], max_y=0, min_y=0)
    ramp = structures.create_ramp(
        angle=30,
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        position_y_modifier=10,
        bounds=bounds
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'triangle'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 7217
    assert ramp['materials'] == ['test_material']
    assert ramp['debug']['color'] == ['black', 'white']
    assert ramp['debug']['info'] == [
        'black', 'white', 'ramp', 'ramp_30_degree', 'black ramp', 'white ramp',
        'black white ramp', 'black ramp_30_degree', 'white ramp_30_degree',
        'black white ramp_30_degree'
    ]

    assert len(ramp['shows']) == 1
    assert ramp['shows'][0]['stepBegin'] == 0
    assert ramp['shows'][0]['position']['x'] == 1
    assert ramp['shows'][0]['position']['y'] == pytest.approx(11.44337567)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(2.8867513)
    assert ramp['shows'][0]['scale']['z'] == 5
    assert ramp['shows'][0]['boundingBox'] == bounds


def test_create_ramp_45_degree():
    ramp = structures.create_ramp(
        angle=45,
        position_x=1,
        position_z=2,
        rotation_y=0,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'triangle'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 12500
    assert ramp['materials'] == ['test_material']
    assert ramp['debug']['color'] == ['black', 'white']
    assert ramp['debug']['info'] == [
        'black', 'white', 'ramp', 'ramp_45_degree', 'black ramp', 'white ramp',
        'black white ramp', 'black ramp_45_degree', 'white ramp_45_degree',
        'black white ramp_45_degree'
    ]

    assert len(ramp['shows']) == 1
    assert ramp['shows'][0]['stepBegin'] == 0
    assert ramp['shows'][0]['position']['x'] == 1
    assert ramp['shows'][0]['position']['y'] == pytest.approx(2.5)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(5)
    assert ramp['shows'][0]['scale']['z'] == 5
    ramp_bounds = ramp['shows'][0]['boundingBox']
    assert vars(ramp_bounds.box_xz[0]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': 4.5}
    )
    assert vars(ramp_bounds.box_xz[1]) == pytest.approx(
        {'x': 3, 'y': 0, 'z': -0.5}
    )
    assert vars(ramp_bounds.box_xz[2]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': -0.5}
    )
    assert vars(ramp_bounds.box_xz[3]) == pytest.approx(
        {'x': -1, 'y': 0, 'z': 4.5}
    )
    assert ramp_bounds.max_y == pytest.approx(5)
    assert ramp_bounds.min_y == pytest.approx(0.0)


def test_create_ramp_45_degree_optional_parameters():
    bounds = ObjectBounds(box_xz=[
        Vector3d(**{'x': 0.11, 'y': 0.12, 'z': 0.13}),
        Vector3d(**{'x': 0.21, 'y': 0.22, 'z': 0.23}),
        Vector3d(**{'x': 0.31, 'y': 0.32, 'z': 0.33}),
        Vector3d(**{'x': 0.41, 'y': 0.42, 'z': 0.43})
    ], max_y=0, min_y=0)
    ramp = structures.create_ramp(
        angle=45,
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        position_y_modifier=10,
        bounds=bounds
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'triangle'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 12500
    assert ramp['materials'] == ['test_material']
    assert ramp['debug']['color'] == ['black', 'white']
    assert ramp['debug']['info'] == [
        'black', 'white', 'ramp', 'ramp_45_degree', 'black ramp', 'white ramp',
        'black white ramp', 'black ramp_45_degree', 'white ramp_45_degree',
        'black white ramp_45_degree'
    ]

    assert len(ramp['shows']) == 1
    assert ramp['shows'][0]['stepBegin'] == 0
    assert ramp['shows'][0]['position']['x'] == 1
    assert ramp['shows'][0]['position']['y'] == pytest.approx(12.5)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(5)
    assert ramp['shows'][0]['scale']['z'] == 5
    assert ramp['shows'][0]['boundingBox'] == bounds


def test_create_door():
    door_objs = structures.create_door(
        position_x=1,
        position_y=0,
        position_z=3,
        rotation_y=180,
        wall_scale_x=3.2,
        wall_scale_y=2.5,
        material_tuple=MaterialTuple("test_material", ["brown", "blue"]),
        wall_material_tuple=MaterialTuple("wall_material", ["green", "red"])
    )

    door = door_objs[0]

    assert isinstance(door['id'], str)
    assert door['kinematic']
    assert not door.get('structure')
    assert door['type'] == 'door_4'
    assert door['materials'] == ['test_material']
    assert door['debug']['color'] == ['brown', 'blue']
    assert door['debug']['info'] == [
        'brown', 'blue', 'door', 'brown door', 'blue door', 'brown blue door'
    ]
    assert len(door['shows']) == 1
    assert door['shows'][0]['stepBegin'] == 0
    assert door['shows'][0]['position']['x'] == 1
    assert door['shows'][0]['position']['y'] == 0
    assert door['shows'][0]['position']['z'] == 3
    assert door['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    assert door['shows'][0]['scale']['x'] == 1
    assert door['shows'][0]['scale']['y'] == 1
    assert door['shows'][0]['scale']['z'] == 1
    bb = door['shows'][0]['boundingBox']
    assert bb.max_y == 2
    assert bb.min_y == 0
    bb0 = vars(bb.box_xz[0])
    bb1 = vars(bb.box_xz[1])
    bb2 = vars(bb.box_xz[2])
    bb3 = vars(bb.box_xz[3])
    assert bb0['x'] == pytest.approx(0.575, 0.01)
    assert bb0['y'] == 0
    assert bb0['z'] == pytest.approx(2.15, 0.01)
    assert bb1['x'] == pytest.approx(0.575, 0.01)
    assert bb1['y'] == 0
    assert bb1['z'] == pytest.approx(3.85, 0.01)
    assert bb2['x'] == pytest.approx(1.425, 0.01)
    assert bb2['y'] == 0
    assert bb2['z'] == pytest.approx(3.85, 0.01)
    assert bb3['x'] == pytest.approx(1.425, 0.01)
    assert bb3['y'] == 0
    assert bb3['z'] == pytest.approx(2.15, 0.01)

    top_wall = door_objs[1]
    assert isinstance(top_wall['id'], str)
    assert top_wall['kinematic']
    assert top_wall['structure']
    assert top_wall['type'] == 'cube'
    assert top_wall['materials'] == ['wall_material']
    assert top_wall['debug']['color'] == ['green', 'red']
    assert top_wall['shows'][0]['stepBegin'] == 0
    assert top_wall['shows'][0]['position']['x'] == 1
    assert top_wall['shows'][0]['position']['y'] == 2.25
    assert top_wall['shows'][0]['position']['z'] == 3
    assert top_wall['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    assert top_wall['shows'][0]['scale']['x'] == 3.2
    assert top_wall['shows'][0]['scale']['y'] == 0.5
    assert top_wall['shows'][0]['scale']['z'] == 0.1

    left_wall = door_objs[2]
    assert isinstance(left_wall['id'], str)
    assert left_wall['kinematic']
    assert left_wall['structure']
    assert left_wall['type'] == 'cube'
    assert left_wall['materials'] == ['wall_material']
    assert left_wall['debug']['color'] == ['green', 'red']
    assert left_wall['shows'][0]['stepBegin'] == 0
    assert left_wall['shows'][0]['position']['x'] == pytest.approx(-0.01)
    assert left_wall['shows'][0]['position']['y'] == 1
    assert left_wall['shows'][0]['position']['z'] == 3
    assert left_wall['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    assert left_wall['shows'][0]['scale']['x'] == pytest.approx(1.18)
    assert left_wall['shows'][0]['scale']['y'] == 2
    assert left_wall['shows'][0]['scale']['z'] == 0.1

    right_wall = door_objs[3]
    assert isinstance(right_wall['id'], str)
    assert right_wall['kinematic']
    assert right_wall['structure']
    assert right_wall['type'] == 'cube'
    assert right_wall['materials'] == ['wall_material']
    assert right_wall['debug']['color'] == ['green', 'red']
    assert right_wall['shows'][0]['stepBegin'] == 0
    assert right_wall['shows'][0]['position']['x'] == pytest.approx(2.01)
    assert right_wall['shows'][0]['position']['y'] == 1
    assert right_wall['shows'][0]['position']['z'] == 3
    assert right_wall['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    assert right_wall['shows'][0]['scale']['x'] == pytest.approx(1.18)
    assert right_wall['shows'][0]['scale']['y'] == 2
    assert right_wall['shows'][0]['scale']['z'] == 0.1


def test_create_guide_rail():
    mat = MaterialTuple("AI2-THOR/Materials/Wood/BedroomFloor1", ["brown"])
    rail = structures.create_guide_rail(1, 2, 90, 4, mat)
    assert rail['id'].startswith('guide_rail')
    assert rail['type'] == 'cube'
    assert rail['structure']
    assert rail['kinematic']
    show = rail['shows'][0]
    pos = show['position']
    scale = show['scale']
    assert pos == {'x': 1, 'y': 0, 'z': 2}
    assert show['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert scale == {'x': 0.2, 'y': 0.2, 'z': 4}
    assert rail['materials'] == [mat[0]]


def test_create_guilde_rail_around():
    mat = MaterialTuple("AI2-THOR/Materials/Walls/BrownDrywall", ["brown"])
    rails = structures.create_guide_rails_around(3, 1, 180, 3, 2, mat)
    rail1 = rails[0]
    rail2 = rails[1]

    assert rail1['id'].startswith('guide_rail')
    assert rail1['type'] == 'cube'
    assert rail1['structure']
    assert rail1['kinematic']
    show = rail1['shows'][0]
    pos = show['position']
    scale = show['scale']
    assert pos == {'x': 4.2, 'y': 0, 'z': 1}
    assert show['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    assert scale == {'x': 0.2, 'y': 0.2, 'z': 3}

    assert rail2['id'].startswith('guide_rail')
    assert rail2['type'] == 'cube'
    assert rail2['structure']
    assert rail2['kinematic']
    show = rail2['shows'][0]
    pos = show['position']
    scale = show['scale']
    assert pos == {'x': 1.8, 'y': 0, 'z': 1}
    assert show['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    assert scale == {'x': 0.2, 'y': 0.2, 'z': 3}
    assert rail1['materials'] == rail2['materials'] == [mat[0]]


def test_create_tool():
    tool_type = 'tool_rect_1_00_x_4_00'
    assert tool_type in ALL_LARGE_BLOCK_TOOLS
    tool = structures.create_tool(
        object_type=tool_type,
        position_x=1,
        position_z=2,
        rotation_y=180
    )

    assert tool['id'].startswith('tool_')
    assert tool['type'] == tool_type
    assert not tool.get('kinematic')
    assert not tool.get('structure')
    assert tool.get('moveable', True)
    assert 'mass' not in tool
    assert 'materials' not in tool
    assert tool['debug']['color'] == ['grey', 'black']
    assert tool['debug']['info'] == [
        'grey', 'black', 'tool', 'grey tool', 'black tool',
        'grey black tool'
    ]

    assert len(tool['shows']) == 1
    assert tool['shows'][0]['stepBegin'] == 0
    assert tool['shows'][0]['position'] == {'x': 1, 'y': 0.15, 'z': 2}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    tool_bounds = tool['shows'][0]['boundingBox']
    assert vars(tool_bounds.box_xz[0]) == pytest.approx(
        {'x': 0.5, 'y': 0, 'z': 0}
    )
    assert vars(tool_bounds.box_xz[1]) == pytest.approx(
        {'x': 0.5, 'y': 0, 'z': 4}
    )
    assert vars(tool_bounds.box_xz[2]) == pytest.approx(
        {'x': 1.5, 'y': 0, 'z': 4}
    )
    assert vars(tool_bounds.box_xz[3]) == pytest.approx(
        {'x': 1.5, 'y': 0, 'z': 0}
    )
    assert tool_bounds.max_y == 0.3
    assert tool_bounds.min_y == 0
