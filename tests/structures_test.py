import pytest

from generator import MaterialTuple, structures


def test_create_interior_wall():
    wall = structures.create_interior_wall(
        position_x=1,
        position_z=2,
        rotation_y=3,
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
    assert wall['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert wall['shows'][0]['scale'] == {'x': 4, 'y': 5, 'z': 0.1}
    assert len(wall['shows'][0]['boundingBox']) == 4


def test_create_interior_wall_optional_parameters():
    bounding_rect = [
        {'x': 0.11, 'y': 0.12, 'z': 0.13},
        {'x': 0.21, 'y': 0.22, 'z': 0.23},
        {'x': 0.31, 'y': 0.32, 'z': 0.33},
        {'x': 0.41, 'y': 0.42, 'z': 0.43}
    ]
    wall = structures.create_interior_wall(
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        height=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        thickness=6,
        position_y_modifier=10,
        bounding_rect=bounding_rect
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
    assert wall['shows'][0]['boundingBox'] == bounding_rect


def test_create_l_occluder():
    occluder = structures.create_l_occluder(
        position_x=1,
        position_z=2,
        rotation_y=3,
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
    assert front['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert front['shows'][0]['scale'] == {'x': 2.5, 'y': 4.5, 'z': 0.5}
    assert len(front['shows'][0]['boundingBox']) == 4

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
    assert side['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert side['shows'][0]['scale'] == {'x': 1.5, 'y': 4.5, 'z': 3.5}
    assert len(side['shows'][0]['boundingBox']) == 4


def test_create_l_occluder_optional_parameters():
    occluder = structures.create_l_occluder(
        position_x=1,
        position_z=2,
        rotation_y=3,
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
    assert front['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert front['shows'][0]['scale'] == {'x': 2.5, 'y': 4.5, 'z': 0.5}
    assert len(front['shows'][0]['boundingBox']) == 4

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
    assert side['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert side['shows'][0]['scale'] == {'x': 1.5, 'y': 4.5, 'z': 3.5}
    assert len(side['shows'][0]['boundingBox']) == 4


def test_create_platform():
    platform = structures.create_platform(
        position_x=1,
        position_z=2,
        rotation_y=3,
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
    assert platform['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert platform['shows'][0]['scale'] == {'x': 4, 'y': 5, 'z': 6}
    assert len(platform['shows'][0]['boundingBox']) == 4


def test_create_platform_optional_parameters():
    bounding_rect = [
        {'x': 0.11, 'y': 0.12, 'z': 0.13},
        {'x': 0.21, 'y': 0.22, 'z': 0.23},
        {'x': 0.31, 'y': 0.32, 'z': 0.33},
        {'x': 0.41, 'y': 0.42, 'z': 0.43}
    ]
    platform = structures.create_platform(
        position_x=1,
        position_z=2,
        rotation_y=3,
        scale_x=4,
        scale_y=5,
        scale_z=6,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        position_y_modifier=10,
        bounding_rect=bounding_rect
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
    assert platform['shows'][0]['boundingBox'] == bounding_rect


def test_create_ramp_15_degree():
    ramp = structures.create_ramp(
        angle=15,
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 259
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
    assert ramp['shows'][0]['position']['y'] == pytest.approx(0.61987298)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 75, 'y': 3, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(5.17638)
    assert ramp['shows'][0]['scale']['z'] == 0.1
    assert len(ramp['shows'][0]['boundingBox']) == 4


def test_create_ramp_15_degree_optional_parameters():
    bounding_rect = [
        {'x': 0.11, 'y': 0.12, 'z': 0.13},
        {'x': 0.21, 'y': 0.22, 'z': 0.23},
        {'x': 0.31, 'y': 0.32, 'z': 0.33},
        {'x': 0.41, 'y': 0.42, 'z': 0.43}
    ]
    ramp = structures.create_ramp(
        angle=15,
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        thickness=0.5,
        position_y_modifier=10,
        bounding_rect=bounding_rect
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 1294
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
    assert ramp['shows'][0]['position']['y'] == pytest.approx(10.41987298)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 75, 'y': 3, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(5.17638)
    assert ramp['shows'][0]['scale']['z'] == 0.5
    assert ramp['shows'][0]['boundingBox'] == bounding_rect


def test_create_ramp_30_degree():
    ramp = structures.create_ramp(
        angle=30,
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 289
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
    assert ramp['shows'][0]['position']['y'] == pytest.approx(1.39337567)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 60, 'y': 3, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(5.77350269)
    assert ramp['shows'][0]['scale']['z'] == 0.1
    assert len(ramp['shows'][0]['boundingBox']) == 4


def test_create_ramp_30_degree_optional_parameters():
    bounding_rect = [
        {'x': 0.11, 'y': 0.12, 'z': 0.13},
        {'x': 0.21, 'y': 0.22, 'z': 0.23},
        {'x': 0.31, 'y': 0.32, 'z': 0.33},
        {'x': 0.41, 'y': 0.42, 'z': 0.43}
    ]
    ramp = structures.create_ramp(
        angle=30,
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        thickness=0.5,
        position_y_modifier=10,
        bounding_rect=bounding_rect
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 1443
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
    assert ramp['shows'][0]['position']['y'] == pytest.approx(11.19337567)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 60, 'y': 3, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(5.77350269)
    assert ramp['shows'][0]['scale']['z'] == 0.5
    assert ramp['shows'][0]['boundingBox'] == bounding_rect


def test_create_ramp_45_degree():
    ramp = structures.create_ramp(
        angle=45,
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white'])
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 354
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
    assert ramp['shows'][0]['position']['y'] == pytest.approx(2.45)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 45, 'y': 3, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(7.07106781)
    assert ramp['shows'][0]['scale']['z'] == 0.1
    assert len(ramp['shows'][0]['boundingBox']) == 4


def test_create_ramp_45_degree_optional_parameters():
    bounding_rect = [
        {'x': 0.11, 'y': 0.12, 'z': 0.13},
        {'x': 0.21, 'y': 0.22, 'z': 0.23},
        {'x': 0.31, 'y': 0.32, 'z': 0.33},
        {'x': 0.41, 'y': 0.42, 'z': 0.43}
    ]
    ramp = structures.create_ramp(
        angle=45,
        position_x=1,
        position_z=2,
        rotation_y=3,
        width=4,
        length=5,
        material_tuple=MaterialTuple('test_material', ['black', 'white']),
        thickness=0.5,
        position_y_modifier=10,
        bounding_rect=bounding_rect
    )

    assert isinstance(ramp['id'], str)
    assert ramp['kinematic'] is True
    assert ramp['structure'] is True
    assert ramp['type'] == 'cube'
    # Expected mass from _calculate_mass function
    assert ramp['mass'] == 1768
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
    assert ramp['shows'][0]['position']['y'] == pytest.approx(12.25)
    assert ramp['shows'][0]['position']['z'] == 2
    assert ramp['shows'][0]['rotation'] == {'x': 45, 'y': 3, 'z': 0}
    assert ramp['shows'][0]['scale']['x'] == 4
    assert ramp['shows'][0]['scale']['y'] == pytest.approx(7.07106781)
    assert ramp['shows'][0]['scale']['z'] == 0.5
    assert ramp['shows'][0]['boundingBox'] == bounding_rect
