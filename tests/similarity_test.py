import copy

import pytest
from machine_common_sense.config_manager import Vector3d

from generator import (
    DefinitionDataset,
    ObjectDefinition,
    base_objects,
    specific_objects,
)
from generator.definitions import (
    create_dataset,
    do_materials_match,
    get_similar_definition,
    is_similar_except_in_color,
    is_similar_except_in_shape,
    is_similar_except_in_size,
)

DATASET = specific_objects.get_interactable_definition_dataset(unshuffled=True)
ALL_DEFINITIONS = [
    # Just use a few variations (colors) of each object for faster testing.
    definition_variations[:2]
    for definition_selections in DATASET._definition_groups
    for definition_variations in definition_selections
]
# Reassign the dataset to use the filtered definition list for faster testing.
DATASET = DefinitionDataset([ALL_DEFINITIONS])
DEFINITIONS = DATASET.definitions(unshuffled=True)


# TODO MCS-1012 Add new shapes/textures that are similar to these objects.
SIMILARITY_EXCEPTIONS = [
    'sofa_4', 'sofa_5', 'sofa_6', 'sofa_7',
    'sofa_chair_4', 'sofa_chair_5', 'sofa_chair_6', 'sofa_chair_7'
]


def test_do_materials_match():
    assert do_materials_match(['a'], ['a'], [], [])
    assert not do_materials_match(['a'], ['b'], [], [])
    assert not do_materials_match(['a', 'b'], ['b'], [], [])
    assert not do_materials_match(['a'], ['a', 'b'], [], [])
    assert do_materials_match(['a', 'b'], ['a', 'b'], [], [])
    assert not do_materials_match(['ab'], ['a', 'b'], [], [])

    assert not do_materials_match(['a'], ['b'], ['a'], ['b'])
    assert not do_materials_match(['a'], ['b'], ['b'], ['a'])


def test_do_materials_match_one_material_list():
    assert not do_materials_match(['a'], [], [], [])
    assert not do_materials_match(['a'], [], ['x'], [])
    assert not do_materials_match(['a'], [], [], ['x'])
    assert do_materials_match(['a'], [], ['x'], ['x'])
    assert not do_materials_match(['a'], [], ['x'], ['y'])
    assert do_materials_match(['a'], [], ['x', 'y'], ['y'])
    assert do_materials_match(['a'], [], ['x'], ['x', 'y'])
    assert do_materials_match(['a'], [], ['x', 'y'], ['x', 'y'])

    assert not do_materials_match([], ['b'], [], [])
    assert not do_materials_match([], ['b'], ['x'], [])
    assert not do_materials_match([], ['b'], [], ['x'])
    assert do_materials_match([], ['b'], ['x'], ['x'])
    assert not do_materials_match([], ['b'], ['x'], ['y'])
    assert do_materials_match([], ['b'], ['x', 'y'], ['y'])
    assert do_materials_match([], ['b'], ['x'], ['x', 'y'])
    assert do_materials_match([], ['b'], ['x', 'y'], ['x', 'y'])


def test_do_materials_match_no_material_lists():
    assert not do_materials_match([], [], ['x'], [])
    assert not do_materials_match([], [], [], ['x'])
    assert do_materials_match([], [], ['x'], ['x'])
    assert not do_materials_match([], [], ['x'], ['y'])
    assert do_materials_match([], [], ['x', 'y'], ['y'])
    assert do_materials_match([], [], ['x'], ['x', 'y'])
    assert do_materials_match([], [], ['x', 'y'], ['x', 'y'])
    assert not do_materials_match([], [], ['xy'], ['x', 'y'])


def test_is_similar_except_in_color():
    definition_1 = ObjectDefinition(
        type='a',
        color=['x'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_2 = ObjectDefinition(
        type='a',
        color=['y'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_3 = ObjectDefinition(
        type='a',
        color=['x', 'y'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_4 = ObjectDefinition(
        type='b',
        color=['y'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_5 = ObjectDefinition(
        type='a',
        color=['y'],
        dimensions=Vector3d(**{'x': 2, 'y': 1, 'z': 1})
    )
    definition_6 = ObjectDefinition(
        type='a',
        color=['y'],
        dimensions=Vector3d(**{'x': 0.5, 'y': 1, 'z': 1})
    )
    definition_7 = ObjectDefinition(
        type='a',
        color=['y'],
        dimensions=Vector3d(**{'x': 1.05, 'y': 1, 'z': 1})
    )
    definition_8 = ObjectDefinition(
        type='a',
        color=['y'],
        dimensions=Vector3d(**{'x': 0.95, 'y': 1, 'z': 1})
    )
    assert is_similar_except_in_color(definition_1, definition_2)
    assert not is_similar_except_in_color(definition_1, definition_3)
    assert not is_similar_except_in_color(definition_1, definition_4)
    assert not is_similar_except_in_color(definition_1, definition_5)
    assert not is_similar_except_in_color(definition_1, definition_6)
    assert is_similar_except_in_color(definition_1, definition_7)
    assert is_similar_except_in_color(definition_1, definition_8)


def test_is_similar_except_in_material():
    definition_1 = ObjectDefinition(
        type='a',
        materials=['x'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_2 = ObjectDefinition(
        type='a',
        materials=['y'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_3 = ObjectDefinition(
        type='a',
        materials=['x', 'y'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_4 = ObjectDefinition(
        type='b',
        materials=['y'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_5 = ObjectDefinition(
        type='a',
        materials=['y'],
        dimensions=Vector3d(**{'x': 2, 'y': 1, 'z': 1})
    )
    definition_6 = ObjectDefinition(
        type='a',
        materials=['y'],
        dimensions=Vector3d(**{'x': 0.5, 'y': 1, 'z': 1})
    )
    definition_7 = ObjectDefinition(
        type='a',
        materials=['y'],
        dimensions=Vector3d(**{'x': 1.05, 'y': 1, 'z': 1})
    )
    definition_8 = ObjectDefinition(
        type='a',
        materials=['y'],
        dimensions=Vector3d(**{'x': 0.95, 'y': 1, 'z': 1})
    )
    assert is_similar_except_in_color(definition_1, definition_2)
    assert is_similar_except_in_color(definition_1, definition_3)
    assert not is_similar_except_in_color(definition_1, definition_4)
    assert not is_similar_except_in_color(definition_1, definition_5)
    assert not is_similar_except_in_color(definition_1, definition_6)
    assert is_similar_except_in_color(definition_1, definition_7)
    assert is_similar_except_in_color(definition_1, definition_8)


def test_is_similar_except_in_shape():
    definition_1 = ObjectDefinition(
        type='a',
        materials=['x'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_2 = ObjectDefinition(
        type='b',
        materials=['x'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_3 = ObjectDefinition(
        type='b',
        materials=['y'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_4 = ObjectDefinition(
        type='b',
        materials=['x', 'y'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_5 = ObjectDefinition(
        type='b',
        materials=['x'],
        dimensions=Vector3d(**{'x': 2, 'y': 1, 'z': 1})
    )
    definition_6 = ObjectDefinition(
        type='b',
        materials=['x'],
        dimensions=Vector3d(**{'x': 0.5, 'y': 1, 'z': 1})
    )
    definition_7 = ObjectDefinition(
        type='b',
        materials=['x'],
        dimensions=Vector3d(**{'x': 1.05, 'y': 1, 'z': 1})
    )
    definition_8 = ObjectDefinition(
        type='b',
        materials=['x'],
        dimensions=Vector3d(**{'x': 0.95, 'y': 1, 'z': 1})
    )
    assert is_similar_except_in_shape(definition_1, definition_2)
    assert not is_similar_except_in_shape(definition_1, definition_3)
    assert not is_similar_except_in_shape(definition_1, definition_4)
    assert not is_similar_except_in_shape(definition_1, definition_5)
    assert not is_similar_except_in_shape(definition_1, definition_6)
    assert is_similar_except_in_shape(definition_1, definition_7)
    assert is_similar_except_in_shape(definition_1, definition_8)


def test_is_similar_except_in_size():
    definition_1 = ObjectDefinition(
        type='a',
        materials=['x'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_2 = ObjectDefinition(
        type='b',
        materials=['x'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_3 = ObjectDefinition(
        type='a',
        materials=['y'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_4 = ObjectDefinition(
        type='a',
        materials=['x', 'y'],
        dimensions=Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    )
    definition_5 = ObjectDefinition(
        type='a',
        materials=['x'],
        dimensions=Vector3d(**{'x': 2, 'y': 1, 'z': 1})
    )
    definition_6 = ObjectDefinition(
        type='a',
        materials=['x'],
        dimensions=Vector3d(**{'x': 0.5, 'y': 1, 'z': 1})
    )
    definition_7 = ObjectDefinition(
        type='a',
        materials=['x'],
        dimensions=Vector3d(**{'x': 1.05, 'y': 1, 'z': 1})
    )
    definition_8 = ObjectDefinition(
        type='a',
        materials=['x'],
        dimensions=Vector3d(**{'x': 0.95, 'y': 1, 'z': 1})
    )
    assert not is_similar_except_in_size(definition_1, definition_2)
    assert not is_similar_except_in_size(definition_1, definition_3)
    assert not is_similar_except_in_size(definition_1, definition_4)
    assert is_similar_except_in_size(definition_1, definition_5)
    assert is_similar_except_in_size(definition_1, definition_6)
    assert not is_similar_except_in_size(definition_1, definition_7)
    assert not is_similar_except_in_size(definition_1, definition_8)


@pytest.mark.slow
def test_is_similar_except_in_color_all_objects():
    for definition_1 in DEFINITIONS:
        x_size_1 = definition_1.dimensions.x
        y_size_1 = definition_1.dimensions.y
        z_size_1 = definition_1.dimensions.z
        for definition_2 in DEFINITIONS:
            if definition_1 != definition_2:
                x_size_2 = definition_2.dimensions.x
                y_size_2 = definition_2.dimensions.y
                z_size_2 = definition_2.dimensions.z
                type_1 = definition_1.type
                type_2 = definition_2.type
                for type_prefix in ['apple', 'crayon']:
                    if type_1.startswith(type_prefix):
                        type_1 = type_prefix
                    if type_2.startswith(type_prefix):
                        type_2 = type_prefix
                expected = (
                    type_1 == type_2 and
                    not do_materials_match(
                        definition_1.materials or [],
                        definition_2.materials or [],
                        definition_1.color or [],
                        definition_2.color or []
                    ) and
                    (x_size_1 + 0.05) >= x_size_2 and
                    (x_size_1 - 0.05) <= x_size_2 and
                    (y_size_1 + 0.05) >= y_size_2 and
                    (y_size_1 - 0.05) <= y_size_2 and
                    (z_size_1 + 0.05) >= z_size_2 and
                    (z_size_1 - 0.05) <= z_size_2
                )
                actual = is_similar_except_in_color(definition_1, definition_2)
                if bool(actual) != expected:
                    print(f'ONE={definition_1}')
                    print(f'TWO={definition_2}')
                assert bool(actual) == expected


@pytest.mark.slow
def test_is_similar_except_in_shape_all_objects():
    for definition_1 in DEFINITIONS:
        x_size_1 = definition_1.dimensions.x
        y_size_1 = definition_1.dimensions.y
        z_size_1 = definition_1.dimensions.z
        for definition_2 in DEFINITIONS:
            if definition_1 != definition_2:
                x_size_2 = definition_2.dimensions.x
                y_size_2 = definition_2.dimensions.y
                z_size_2 = definition_2.dimensions.z
                type_1 = definition_1.type
                type_2 = definition_2.type
                for type_prefix in ['apple', 'crayon']:
                    if type_1.startswith(type_prefix):
                        type_1 = type_prefix
                    if type_2.startswith(type_prefix):
                        type_2 = type_prefix
                expected = (
                    type_1 != type_2 and
                    do_materials_match(
                        definition_1.materials or [],
                        definition_2.materials or [],
                        definition_1.color or [],
                        definition_2.color or []
                    ) and
                    (x_size_1 + 0.05) >= x_size_2 and
                    (x_size_1 - 0.05) <= x_size_2 and
                    (y_size_1 + 0.05) >= y_size_2 and
                    (y_size_1 - 0.05) <= y_size_2 and
                    (z_size_1 + 0.05) >= z_size_2 and
                    (z_size_1 - 0.05) <= z_size_2
                )
                actual = is_similar_except_in_shape(definition_1, definition_2)
                if bool(actual) != expected:
                    print(f'ONE={definition_1}')
                    print(f'TWO={definition_2}')
                assert bool(actual) == expected


@pytest.mark.slow
def test_is_similar_except_in_size_all_objects():
    for definition_1 in DEFINITIONS:
        x_size_1 = definition_1.dimensions.x
        y_size_1 = definition_1.dimensions.y
        z_size_1 = definition_1.dimensions.z
        for definition_2 in DEFINITIONS:
            if definition_1 != definition_2:
                x_size_2 = definition_2.dimensions.x
                y_size_2 = definition_2.dimensions.y
                z_size_2 = definition_2.dimensions.z
                type_1 = definition_1.type
                type_2 = definition_2.type
                for type_prefix in ['apple', 'crayon']:
                    if type_1.startswith(type_prefix):
                        type_1 = type_prefix
                    if type_2.startswith(type_prefix):
                        type_2 = type_prefix
                expected = (
                    type_1 == type_2 and
                    do_materials_match(
                        definition_1.materials or [],
                        definition_2.materials or [],
                        definition_1.color or [],
                        definition_2.color or []
                    ) and
                    (
                        (x_size_1 + 0.05) < x_size_2 or
                        (x_size_1 - 0.05) > x_size_2 or
                        (y_size_1 + 0.05) < y_size_2 or
                        (y_size_1 - 0.05) > y_size_2 or
                        (z_size_1 + 0.05) < z_size_2 or
                        (z_size_1 - 0.05) > z_size_2
                    )
                )
                actual = is_similar_except_in_size(definition_1, definition_2)
                if bool(actual) != expected:
                    print(f'ONE={definition_1}')
                    print(f'TWO={definition_2}')
                assert bool(actual) == expected


def test_similarity_soccer_ball():
    soccer_ball = base_objects.create_soccer_ball()
    soccer_ball_big = base_objects.create_soccer_ball(2)
    soccer_ball_small = base_objects.create_soccer_ball(0.5)
    assert not is_similar_except_in_color(soccer_ball, soccer_ball_big)
    assert not is_similar_except_in_color(soccer_ball, soccer_ball_small)
    assert not is_similar_except_in_shape(soccer_ball, soccer_ball_big)
    assert not is_similar_except_in_shape(soccer_ball, soccer_ball_small)
    assert is_similar_except_in_size(soccer_ball, soccer_ball_big)
    assert is_similar_except_in_size(soccer_ball, soccer_ball_small)

    big_copy = copy.deepcopy(soccer_ball_big)
    big_copy.difference = 'size'
    big_dataset = create_dataset([[soccer_ball_big]])
    assert get_similar_definition(soccer_ball, big_dataset) == big_copy
    small_copy = copy.deepcopy(soccer_ball_small)
    small_copy.difference = 'size'
    small_dataset = create_dataset([[soccer_ball_small]])
    assert get_similar_definition(soccer_ball, small_dataset) == small_copy

    black_ball = base_objects.create_specific_definition_from_base(
        type='ball',
        color=['black'],
        materials=['Custom/Materials/Black'],
        salient_materials=['rubber'],
        scale=0.25
    )
    green_ball = base_objects.create_specific_definition_from_base(
        type='ball',
        color=['green'],
        materials=['Custom/Materials/Green'],
        salient_materials=['rubber'],
        scale=0.25
    )
    white_ball = base_objects.create_specific_definition_from_base(
        type='ball',
        color=['white'],
        materials=['Custom/Materials/White'],
        salient_materials=['rubber'],
        scale=0.25
    )
    assert is_similar_except_in_shape(soccer_ball, black_ball)
    assert is_similar_except_in_shape(soccer_ball, white_ball)
    assert not is_similar_except_in_shape(soccer_ball, green_ball)

    black_copy = copy.deepcopy(black_ball)
    black_copy.difference = 'shape'
    black_dataset = create_dataset([[black_ball]])
    assert get_similar_definition(soccer_ball, black_dataset) == black_copy
    white_copy = copy.deepcopy(white_ball)
    white_copy.difference = 'shape'
    white_dataset = create_dataset([[white_ball]])
    assert get_similar_definition(soccer_ball, white_dataset) == white_copy


@pytest.mark.slow
def test_get_similar_definition():
    failed = False
    for definition in DEFINITIONS:
        if definition.type in SIMILARITY_EXCEPTIONS:
            continue
        result = get_similar_definition(definition, DATASET, unshuffled=True)
        if not result:
            print(f'NO SIMILAR DEF {definition}')
            failed = True
        else:
            result.difference = None
    assert not failed
