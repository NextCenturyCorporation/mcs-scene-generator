from occluders import (
    OCCLUDER_HEIGHT,
    calculate_separation_distance,
    create_occluder,
    generate_occluder_position
)
import pytest
import random


def test_create_occluder_normal_positive_x():
    occluder = create_occluder(
        ['test_material_wall', ['white']],
        ['test_material_pole', ['brown']],
        1,
        1,
        False,
        False,
        OCCLUDER_HEIGHT,
        200
    )
    assert len(occluder) == 2
    wall, pole = occluder
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']

    assert pole['shows'][0]['position']['x'] == 1
    assert pole['shows'][0]['position']['y'] == 3.25
    assert wall['shows'][0]['position']['x'] == 1
    assert wall['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['scale']['y'] == OCCLUDER_HEIGHT

    assert len(pole['moves']) == 3
    assert len(wall['moves']) == 3
    assert len(wall['rotates']) == 3

    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == 21
    assert pole['moves'][1]['stepEnd'] == 26
    assert pole['moves'][2]['stepBegin'] == 186
    assert pole['moves'][2]['stepEnd'] == 191

    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == 21
    assert wall['moves'][1]['stepEnd'] == 26
    assert wall['moves'][2]['stepBegin'] == 186
    assert wall['moves'][2]['stepEnd'] == 191

    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 11
    assert wall['rotates'][0]['vector']['y'] == (90.0 / 5) * -1
    assert wall['rotates'][1]['stepBegin'] == 16
    assert wall['rotates'][1]['stepEnd'] == 20
    assert wall['rotates'][1]['vector']['y'] == (90.0 / 5)
    assert wall['rotates'][2]['stepBegin'] == 192
    assert wall['rotates'][2]['stepEnd'] == 196
    assert wall['rotates'][2]['vector']['y'] == (90.0 / 5) * -1


def test_create_occluder_normal_negative_x():
    occluder = create_occluder(
        ['test_material_wall', ['white']],
        ['test_material_pole', ['brown']],
        -1,
        1,
        False,
        False,
        OCCLUDER_HEIGHT,
        200
    )
    assert len(occluder) == 2
    wall, pole = occluder
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']

    assert pole['shows'][0]['position']['x'] == -1
    assert pole['shows'][0]['position']['y'] == 3.25
    assert wall['shows'][0]['position']['x'] == -1
    assert wall['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['scale']['y'] == OCCLUDER_HEIGHT

    assert len(pole['moves']) == 3
    assert len(wall['moves']) == 3
    assert len(wall['rotates']) == 3

    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == 21
    assert pole['moves'][1]['stepEnd'] == 26
    assert pole['moves'][2]['stepBegin'] == 186
    assert pole['moves'][2]['stepEnd'] == 191

    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == 21
    assert wall['moves'][1]['stepEnd'] == 26
    assert wall['moves'][2]['stepBegin'] == 186
    assert wall['moves'][2]['stepEnd'] == 191

    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 11
    assert wall['rotates'][0]['vector']['y'] == (90.0 / 5)
    assert wall['rotates'][1]['stepBegin'] == 16
    assert wall['rotates'][1]['stepEnd'] == 20
    assert wall['rotates'][1]['vector']['y'] == (90.0 / 5) * -1
    assert wall['rotates'][2]['stepBegin'] == 192
    assert wall['rotates'][2]['stepEnd'] == 196
    assert wall['rotates'][2]['vector']['y'] == (90.0 / 5)


def test_create_occluder_narrow():
    occluder = create_occluder(
        ['test_material_wall', ['white']],
        ['test_material_pole', ['brown']],
        -1,
        0.5,
        False,
        False,
        OCCLUDER_HEIGHT,
        200
    )
    assert len(occluder) == 2
    wall, pole = occluder
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']

    assert pole['shows'][0]['position']['x'] == -1
    assert pole['shows'][0]['position']['y'] == 3.25
    assert wall['shows'][0]['position']['x'] == -1
    assert wall['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['scale']['y'] == OCCLUDER_HEIGHT

    assert len(pole['moves']) == 3
    assert len(wall['moves']) == 3
    assert len(wall['rotates']) == 3

    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == 17
    assert pole['moves'][1]['stepEnd'] == 22
    assert pole['moves'][2]['stepBegin'] == 188
    assert pole['moves'][2]['stepEnd'] == 193

    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == 17
    assert wall['moves'][1]['stepEnd'] == 22
    assert wall['moves'][2]['stepBegin'] == 188
    assert wall['moves'][2]['stepEnd'] == 193

    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 9
    assert wall['rotates'][0]['vector']['y'] == (90.0 / 3)
    assert wall['rotates'][1]['stepBegin'] == 14
    assert wall['rotates'][1]['stepEnd'] == 16
    assert wall['rotates'][1]['vector']['y'] == (90.0 / 3) * -1
    assert wall['rotates'][2]['stepBegin'] == 194
    assert wall['rotates'][2]['stepEnd'] == 196
    assert wall['rotates'][2]['vector']['y'] == (90.0 / 3)


def test_create_occluder_wide():
    occluder = create_occluder(
        ['test_material_wall', ['white']],
        ['test_material_pole', ['brown']],
        -1,
        1.5,
        False,
        False,
        OCCLUDER_HEIGHT,
        200
    )
    assert len(occluder) == 2
    wall, pole = occluder
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']

    assert pole['shows'][0]['position']['x'] == -1
    assert pole['shows'][0]['position']['y'] == 3.25
    assert wall['shows'][0]['position']['x'] == -1
    assert wall['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['scale']['y'] == OCCLUDER_HEIGHT

    assert len(pole['moves']) == 3
    assert len(wall['moves']) == 3
    assert len(wall['rotates']) == 3

    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == 23
    assert pole['moves'][1]['stepEnd'] == 28
    assert pole['moves'][2]['stepBegin'] == 185
    assert pole['moves'][2]['stepEnd'] == 190

    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == 23
    assert wall['moves'][1]['stepEnd'] == 28
    assert wall['moves'][2]['stepBegin'] == 185
    assert wall['moves'][2]['stepEnd'] == 190

    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 12
    assert wall['rotates'][0]['vector']['y'] == (90.0 / 6)
    assert wall['rotates'][1]['stepBegin'] == 17
    assert wall['rotates'][1]['stepEnd'] == 22
    assert wall['rotates'][1]['vector']['y'] == (90.0 / 6) * -1
    assert wall['rotates'][2]['stepBegin'] == 191
    assert wall['rotates'][2]['stepEnd'] == 196
    assert wall['rotates'][2]['vector']['y'] == (90.0 / 6)


def test_create_occluder_very_wide():
    occluder = create_occluder(
        ['test_material_wall', ['white']],
        ['test_material_pole', ['brown']],
        -1,
        4,
        False,
        False,
        OCCLUDER_HEIGHT,
        200
    )
    assert len(occluder) == 2
    wall, pole = occluder
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']

    assert pole['shows'][0]['position']['x'] == -1
    assert pole['shows'][0]['position']['y'] == 3.25
    assert wall['shows'][0]['position']['x'] == -1
    assert wall['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['scale']['y'] == OCCLUDER_HEIGHT

    assert len(pole['moves']) == 3
    assert len(wall['moves']) == 3
    assert len(wall['rotates']) == 3

    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == 71
    assert pole['moves'][1]['stepEnd'] == 76
    assert pole['moves'][2]['stepBegin'] == 161
    assert pole['moves'][2]['stepEnd'] == 166

    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == 71
    assert wall['moves'][1]['stepEnd'] == 76
    assert wall['moves'][2]['stepBegin'] == 161
    assert wall['moves'][2]['stepEnd'] == 166

    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 36
    assert wall['rotates'][0]['vector']['y'] == (90.0 / 30)
    assert wall['rotates'][1]['stepBegin'] == 41
    assert wall['rotates'][1]['stepEnd'] == 70
    assert wall['rotates'][1]['vector']['y'] == (90.0 / 30) * -1
    assert wall['rotates'][2]['stepBegin'] == 167
    assert wall['rotates'][2]['stepEnd'] == 196
    assert wall['rotates'][2]['vector']['y'] == (90.0 / 30)


def test_create_occluder_with_modified_last_step():
    occluder = create_occluder(
        ['test_material_wall', ['white']],
        ['test_material_pole', ['brown']],
        -1,
        1,
        False,
        False,
        OCCLUDER_HEIGHT,
        160
    )
    assert len(occluder) == 2
    wall, pole = occluder
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']

    assert pole['shows'][0]['position']['x'] == -1
    assert pole['shows'][0]['position']['y'] == 3.25
    assert wall['shows'][0]['position']['x'] == -1
    assert wall['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['scale']['y'] == OCCLUDER_HEIGHT

    assert len(pole['moves']) == 3
    assert len(wall['moves']) == 3
    assert len(wall['rotates']) == 3

    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == 21
    assert pole['moves'][1]['stepEnd'] == 26
    assert pole['moves'][2]['stepBegin'] == 146
    assert pole['moves'][2]['stepEnd'] == 151

    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == 21
    assert wall['moves'][1]['stepEnd'] == 26
    assert wall['moves'][2]['stepBegin'] == 146
    assert wall['moves'][2]['stepEnd'] == 151

    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 11
    assert wall['rotates'][0]['vector']['y'] == (90.0 / 5)
    assert wall['rotates'][1]['stepBegin'] == 16
    assert wall['rotates'][1]['stepEnd'] == 20
    assert wall['rotates'][1]['vector']['y'] == (90.0 / 5) * -1
    assert wall['rotates'][2]['stepBegin'] == 152
    assert wall['rotates'][2]['stepEnd'] == 156
    assert wall['rotates'][2]['vector']['y'] == (90.0 / 5)


def test_create_occluder_sideways_left_positive_x():
    occluder = create_occluder(
        ['test_material_wall', ['white']],
        ['test_material_pole', ['brown']],
        1,
        1,
        True,
        False,
        OCCLUDER_HEIGHT,
        160
    )
    assert len(occluder) == 2
    wall, pole = occluder
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']

    assert pole['shows'][0]['position']['x'] == -2.5
    assert pole['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['position']['x'] == 1
    assert wall['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['scale']['y'] == OCCLUDER_HEIGHT

    assert len(pole['moves']) == 3
    assert len(wall['moves']) == 3
    assert len(wall['rotates']) == 3

    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == 21
    assert pole['moves'][1]['stepEnd'] == 26
    assert pole['moves'][2]['stepBegin'] == 146
    assert pole['moves'][2]['stepEnd'] == 151

    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == 21
    assert wall['moves'][1]['stepEnd'] == 26
    assert wall['moves'][2]['stepBegin'] == 146
    assert wall['moves'][2]['stepEnd'] == 151

    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 11
    assert wall['rotates'][0]['vector']['x'] == (90.0 / 5)
    assert wall['rotates'][1]['stepBegin'] == 16
    assert wall['rotates'][1]['stepEnd'] == 20
    assert wall['rotates'][1]['vector']['x'] == (90.0 / 5) * -1
    assert wall['rotates'][2]['stepBegin'] == 152
    assert wall['rotates'][2]['stepEnd'] == 156
    assert wall['rotates'][2]['vector']['x'] == (90.0 / 5)


def test_create_occluder_sideways_left_negative_x():
    occluder = create_occluder(
        ['test_material_wall', ['white']],
        ['test_material_pole', ['brown']],
        -1,
        1,
        True,
        False,
        OCCLUDER_HEIGHT,
        160
    )
    assert len(occluder) == 2
    wall, pole = occluder
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']

    assert pole['shows'][0]['position']['x'] == -4.5
    assert pole['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['position']['x'] == -1
    assert wall['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['scale']['y'] == OCCLUDER_HEIGHT

    assert len(pole['moves']) == 3
    assert len(wall['moves']) == 3
    assert len(wall['rotates']) == 3

    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == 21
    assert pole['moves'][1]['stepEnd'] == 26
    assert pole['moves'][2]['stepBegin'] == 146
    assert pole['moves'][2]['stepEnd'] == 151

    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == 21
    assert wall['moves'][1]['stepEnd'] == 26
    assert wall['moves'][2]['stepBegin'] == 146
    assert wall['moves'][2]['stepEnd'] == 151

    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 11
    assert wall['rotates'][0]['vector']['x'] == (90.0 / 5)
    assert wall['rotates'][1]['stepBegin'] == 16
    assert wall['rotates'][1]['stepEnd'] == 20
    assert wall['rotates'][1]['vector']['x'] == (90.0 / 5) * -1
    assert wall['rotates'][2]['stepBegin'] == 152
    assert wall['rotates'][2]['stepEnd'] == 156
    assert wall['rotates'][2]['vector']['x'] == (90.0 / 5)


def test_create_occluder_sideways_right_positive_x():
    occluder = create_occluder(
        ['test_material_wall', ['white']],
        ['test_material_pole', ['brown']],
        1,
        1,
        False,
        True,
        OCCLUDER_HEIGHT,
        160
    )
    assert len(occluder) == 2
    wall, pole = occluder
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']

    assert pole['shows'][0]['position']['x'] == 4.5
    assert pole['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['position']['x'] == 1
    assert wall['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['scale']['y'] == OCCLUDER_HEIGHT

    assert len(pole['moves']) == 3
    assert len(wall['moves']) == 3
    assert len(wall['rotates']) == 3

    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == 21
    assert pole['moves'][1]['stepEnd'] == 26
    assert pole['moves'][2]['stepBegin'] == 146
    assert pole['moves'][2]['stepEnd'] == 151

    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == 21
    assert wall['moves'][1]['stepEnd'] == 26
    assert wall['moves'][2]['stepBegin'] == 146
    assert wall['moves'][2]['stepEnd'] == 151

    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 11
    assert wall['rotates'][0]['vector']['x'] == (90.0 / 5)
    assert wall['rotates'][1]['stepBegin'] == 16
    assert wall['rotates'][1]['stepEnd'] == 20
    assert wall['rotates'][1]['vector']['x'] == (90.0 / 5) * -1
    assert wall['rotates'][2]['stepBegin'] == 152
    assert wall['rotates'][2]['stepEnd'] == 156
    assert wall['rotates'][2]['vector']['x'] == (90.0 / 5)


def test_create_occluder_sideways_right_negative_x():
    occluder = create_occluder(
        ['test_material_wall', ['white']],
        ['test_material_pole', ['brown']],
        -1,
        1,
        False,
        True,
        OCCLUDER_HEIGHT,
        160
    )
    assert len(occluder) == 2
    wall, pole = occluder
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']

    assert pole['shows'][0]['position']['x'] == 2.5
    assert pole['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['position']['x'] == -1
    assert wall['shows'][0]['position']['y'] == (OCCLUDER_HEIGHT / 2.0)
    assert wall['shows'][0]['scale']['y'] == OCCLUDER_HEIGHT

    assert len(pole['moves']) == 3
    assert len(wall['moves']) == 3
    assert len(wall['rotates']) == 3

    assert pole['moves'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepEnd'] == 6
    assert pole['moves'][1]['stepBegin'] == 21
    assert pole['moves'][1]['stepEnd'] == 26
    assert pole['moves'][2]['stepBegin'] == 146
    assert pole['moves'][2]['stepEnd'] == 151

    assert wall['moves'][0]['stepBegin'] == 1
    assert wall['moves'][0]['stepEnd'] == 6
    assert wall['moves'][1]['stepBegin'] == 21
    assert wall['moves'][1]['stepEnd'] == 26
    assert wall['moves'][2]['stepBegin'] == 146
    assert wall['moves'][2]['stepEnd'] == 151

    assert wall['rotates'][0]['stepBegin'] == 7
    assert wall['rotates'][0]['stepEnd'] == 11
    assert wall['rotates'][0]['vector']['x'] == (90.0 / 5)
    assert wall['rotates'][1]['stepBegin'] == 16
    assert wall['rotates'][1]['stepEnd'] == 20
    assert wall['rotates'][1]['vector']['x'] == (90.0 / 5) * -1
    assert wall['rotates'][2]['stepBegin'] == 152
    assert wall['rotates'][2]['stepEnd'] == 156
    assert wall['rotates'][2]['vector']['x'] == (90.0 / 5)


def test_calculate_separation_distance():
    assert calculate_separation_distance(0.5, 1, 2.5, 1) == pytest.approx(0.5)
    assert calculate_separation_distance(0, 1, 2.5, 1) == pytest.approx(1)
    assert calculate_separation_distance(-1, 1, -3, 1) == pytest.approx(0.5)
    assert calculate_separation_distance(-1, 1, 2, 1) == pytest.approx(1.5)
    assert calculate_separation_distance(1, 0.5, 3, 0.5) == pytest.approx(1)
    assert calculate_separation_distance(1, 1, 2.5, 1) == pytest.approx(0)
    assert calculate_separation_distance(1, 1, 2, 1) == pytest.approx(-0.5)
    assert calculate_separation_distance(1, 1, 2, 2) == pytest.approx(-1)


def test_generate_occluder_position():
    assert -2.75 <= generate_occluder_position(0.5, []) <= 2.75
    assert -2.5 <= generate_occluder_position(1, []) <= 2.5

    occluder_1 = {'shows': [{'position': {'x': 2}, 'scale': {'x': 1}}]}
    assert -2.5 <= generate_occluder_position(1, [occluder_1]) <= 1

    occluder_2 = {'shows': [{'position': {'x': -2.25}, 'scale': {'x': 0.5}}]}
    assert -1.5 <= generate_occluder_position(1, [occluder_1, occluder_2]) <= 1
