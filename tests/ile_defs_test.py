import random

import pytest
from machine_common_sense.config_manager import (
    FloorTexturesConfig,
    Vector2dInt,
    Vector3d,
)

from generator import ObjectBounds, ObjectDefinition
from generator.scene import Scene
from ideal_learning_env.defs import (
    ILEException,
    ILESharedConfiguration,
    find_bounds,
    return_list,
)


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ILESharedConfiguration.get_instance().set_excluded_shapes([])

    # Run test
    yield

    # Cleanup
    ILESharedConfiguration.get_instance().set_excluded_shapes([])


def test_shared_config_singleton():
    shared_config_1 = ILESharedConfiguration.get_instance()
    shared_config_2 = ILESharedConfiguration.get_instance()
    assert shared_config_1 == shared_config_2


def test_shared_config_singleton_error():
    ILESharedConfiguration.get_instance()
    with pytest.raises(Exception):
        ILESharedConfiguration()


def test_shared_config_choose_from_included_shapes():
    expected = ObjectDefinition(type='mock')

    def callback() -> ObjectDefinition:
        return expected

    shared_config = ILESharedConfiguration.get_instance()

    actual = shared_config.choose_definition_from_included_shapes(callback)
    assert actual == expected


def test_shared_config_choose_from_included_shapes_with_multiple():
    expected_1 = ObjectDefinition(type='mock_1')
    expected_2 = ObjectDefinition(type='mock_2')

    def callback() -> ObjectDefinition:
        return random.choice([expected_1, expected_2])

    shared_config = ILESharedConfiguration.get_instance()

    actual = shared_config.choose_definition_from_included_shapes(callback)
    assert actual == expected_1 or actual == expected_2


def test_shared_config_choose_from_included_shapes_with_exclusions():
    expected = ObjectDefinition(type='mock')
    unexpected = ObjectDefinition(type='mock_excluded')

    def callback() -> ObjectDefinition:
        return random.choice([expected, unexpected])

    shared_config = ILESharedConfiguration.get_instance()
    shared_config.set_excluded_shapes(['mock_excluded'])

    actual = shared_config.choose_definition_from_included_shapes(callback)
    assert actual == expected


def test_shared_config_choose_from_included_shapes_does_fail():
    def callback() -> ObjectDefinition:
        return ObjectDefinition(type='mock_excluded')

    shared_config = ILESharedConfiguration.get_instance()
    shared_config.set_excluded_shapes(['mock_excluded'])

    with pytest.raises(ILEException):
        shared_config.choose_definition_from_included_shapes(callback)


def test_find_bounds():
    # Case 1: No objects
    scene = Scene(objects=[])
    assert find_bounds(scene) == []

    bounds_1 = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1),
        Vector3d(x=2, y=0, z=1),
        Vector3d(x=2, y=0, z=2),
        Vector3d(x=1, y=0, z=2)
    ], max_y=1, min_y=0)
    bounds_2 = ObjectBounds(box_xz=[
        Vector3d(x=-1, y=0, z=-1),
        Vector3d(x=-2, y=0, z=-1),
        Vector3d(x=-2, y=0, z=-2),
        Vector3d(x=-1, y=0, z=-2)
    ], max_y=1, min_y=0)

    # Case 2: 1 object
    scene = Scene(objects=[
        {'shows': [{'boundingBox': bounds_1}]}
    ])
    assert find_bounds(scene) == [bounds_1]

    # Case 3: 2 objects
    scene = Scene(objects=[
        {'shows': [{'boundingBox': bounds_1}]},
        {'shows': [{'boundingBox': bounds_2}]}
    ])
    assert find_bounds(scene) == [bounds_1, bounds_2]

    bounds_3 = ObjectBounds(box_xz=[
        Vector3d(x=2.5, y=0, z=2.5),
        Vector3d(x=3.5, y=0, z=2.5),
        Vector3d(x=3.5, y=0, z=3.5),
        Vector3d(x=2.5, y=0, z=3.5)
    ], max_y=100, min_y=0)
    bounds_4 = ObjectBounds(box_xz=[
        Vector3d(x=-3.5, y=0, z=-3.5),
        Vector3d(x=-2.5, y=0, z=-3.5),
        Vector3d(x=-2.5, y=0, z=-2.5),
        Vector3d(x=-3.5, y=0, z=-2.5)
    ], max_y=100, min_y=0)

    # Case 4: 1 hole
    scene = Scene(holes=[{'x': 3, 'z': 3}], objects=[])
    assert find_bounds(scene) == [bounds_3]

    # Case 5: 2 holes
    scene = Scene(holes=[{'x': 3, 'z': 3}, {'x': -3, 'z': -3}], objects=[])
    assert find_bounds(scene) == [bounds_3, bounds_4]

    # Case 6: holes and objects
    scene = Scene(holes=[{'x': 3, 'z': 3}, {'x': -3, 'z': -3}], objects=[
        {'shows': [{'boundingBox': bounds_1}]},
        {'shows': [{'boundingBox': bounds_2}]}
    ])
    assert find_bounds(scene) == [bounds_3, bounds_4, bounds_1, bounds_2]

    # Case 7: floor textures
    scene = Scene(floor_textures=[FloorTexturesConfig(
        material='blue',
        positions=[Vector2dInt(x=0, z=0)]
    )], objects=[])
    assert find_bounds(scene) == []

    # Case 8: 1 lava area
    scene = Scene(lava=[{'x': 3, 'z': 3}], objects=[])
    assert find_bounds(scene) == [bounds_3]

    # Case 9: 2 lava areas
    scene = Scene(lava=[{'x': 3, 'z': 3}, {'x': -3, 'z': -3}], objects=[])
    assert find_bounds(scene) == [bounds_3, bounds_4]

    # Case 10: lava areas and objects
    scene = Scene(lava=[{'x': 3, 'z': 3}, {'x': -3, 'z': -3}], objects=[
        {'shows': [{'boundingBox': bounds_1}]},
        {'shows': [{'boundingBox': bounds_2}]}
    ])
    assert find_bounds(scene) == [bounds_3, bounds_4, bounds_1, bounds_2]

    # Case 11: everything
    scene = Scene(floor_textures=FloorTexturesConfig(
        material='blue',
        positions=[Vector2dInt(x=0, z=0)]),
        lava=[{'x': 3, 'z': 3}], holes=[{'x': -3, 'z': -3}], objects=[
        {'shows': [{'boundingBox': bounds_1}]},
        {'shows': [{'boundingBox': bounds_2}]}
    ])
    assert find_bounds(scene) == [bounds_4, bounds_3, bounds_1, bounds_2]


def test_return_list():
    assert return_list(None) == []
    assert return_list(None, [1234]) == [1234]
    assert return_list(1234) == [1234]
    assert return_list([1234]) == [1234]
