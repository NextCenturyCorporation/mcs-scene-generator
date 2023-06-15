import pytest

from generator import SceneException, geometry
from ideal_learning_env import (
    ILEDelayException,
    ILEException,
    InstanceDefinitionLocationTuple,
    MaterialRestrictions,
    ObjectRepository
)
from ideal_learning_env.object_services import (
    calculate_rotated_position,
    get_step_after_movement,
    get_step_after_movement_or_start
)

from .ile_helper import prior_scene


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()

    # Run test
    yield

    # Cleanup
    ObjectRepository.get_instance().clear()


def test_object_repository_clear():
    repo = ObjectRepository.get_instance()
    fake = InstanceDefinitionLocationTuple({'id': 'fake'}, {}, {})
    repo.add_to_labeled_objects(fake, "label")

    assert repo.get_one_from_labeled_objects("label") == fake
    assert len(repo._labeled_object_store) == 1
    assert repo.get_one_from_labeled_objects("fake") == fake
    assert len(repo._labeled_object_store) == 1
    repo.clear()
    assert repo.get_one_from_labeled_objects("label") is None
    assert len(repo._labeled_object_store) == 0
    assert repo.get_one_from_labeled_objects("fake") is None
    assert len(repo._id_object_store) == 0


def test_object_repository_add_none_tuple():
    repo = ObjectRepository.get_instance()
    assert len(repo._labeled_object_store) == 0
    repo.add_to_labeled_objects(None, "label")
    assert len(repo._labeled_object_store) == 0
    assert repo.get_one_from_labeled_objects("label") is None


def test_object_repository_add_none_label():
    repo = ObjectRepository.get_instance()
    fake = InstanceDefinitionLocationTuple({'id': 'fake'}, {}, {})
    assert len(repo._labeled_object_store) == 0
    repo.add_to_labeled_objects(fake, None)
    assert len(repo._labeled_object_store) == 0


def test_object_repository_add_array():
    repo = ObjectRepository.get_instance()
    fake = InstanceDefinitionLocationTuple({'id': 'fake'}, {}, {})
    repo.add_to_labeled_objects(fake, ["label", "label2"])

    assert repo.get_one_from_labeled_objects("label") == fake
    assert repo.get_one_from_labeled_objects("label2") == fake
    assert repo.get_one_from_labeled_objects("label3") is None
    assert len(repo._labeled_object_store) == 2

    assert repo.get_one_from_labeled_objects("fake") == fake


def test_object_repository_get_single():
    repo = ObjectRepository.get_instance()
    fake = InstanceDefinitionLocationTuple({'id': 'fake'}, {}, {})
    fake2 = InstanceDefinitionLocationTuple({"id": "12345"}, {}, {})
    repo.add_to_labeled_objects(fake, ["label", "label2"])
    repo.add_to_labeled_objects(fake2, ["label3", "label2"])
    assert len(repo._labeled_object_store) == 3
    assert repo.get_one_from_labeled_objects("label") == fake
    assert repo.get_one_from_labeled_objects("label2") in [fake, fake2]
    assert repo.get_one_from_labeled_objects("label3") == fake2
    assert repo.get_one_from_labeled_objects("label4") is None


def test_object_repository_get_multiple():
    repo = ObjectRepository.get_instance()
    fake = InstanceDefinitionLocationTuple({'id': 'fake'}, {}, {})
    fake2 = InstanceDefinitionLocationTuple({"id": "12345"}, {}, {})
    repo.add_to_labeled_objects(fake, ["label", "label2"])
    repo.add_to_labeled_objects(fake2, ["label3", "label2"])
    assert len(repo._labeled_object_store) == 3
    assert repo.get_all_from_labeled_objects("label") == [fake]
    assert repo.get_all_from_labeled_objects("label2") == [fake, fake2]
    assert repo.get_all_from_labeled_objects("label3") == [fake2]
    assert repo.get_all_from_labeled_objects("label4") is None


def test_object_repository_remove():
    repo = ObjectRepository.get_instance()
    assert len(repo._labeled_object_store) == 0

    idl_1 = InstanceDefinitionLocationTuple({'id': 'object_1'}, {}, {})
    idl_2 = InstanceDefinitionLocationTuple({'id': 'object_2'}, {}, {})
    repo.add_to_labeled_objects(idl_1, ['label_a', 'label_b'])
    repo.add_to_labeled_objects(idl_2, ['label_a'])
    assert repo.get_all_from_labeled_objects('label_a') == [idl_1, idl_2]
    assert repo.get_all_from_labeled_objects('label_b') == [idl_1]

    repo.remove_from_labeled_objects('object_1', 'label_a')
    assert repo.get_all_from_labeled_objects('label_a') == [idl_2]
    assert repo.get_all_from_labeled_objects('label_b') == [idl_1]

    repo.remove_from_labeled_objects('object_1', 'label_b')
    assert repo.get_all_from_labeled_objects('label_a') == [idl_2]
    assert repo.get_all_from_labeled_objects('label_b') == []

    repo.remove_from_labeled_objects('object_2', 'label_a')
    assert repo.get_all_from_labeled_objects('label_a') == []
    assert repo.get_all_from_labeled_objects('label_b') == []

    repo.remove_from_labeled_objects('object_2', 'label_b')
    assert repo.get_all_from_labeled_objects('label_a') == []
    assert repo.get_all_from_labeled_objects('label_b') == []

    repo.remove_from_labeled_objects('object_2', 'label_c')
    assert repo.get_all_from_labeled_objects('label_c') is None


def test_object_repository_singleton():
    repo1 = ObjectRepository.get_instance()
    repo2 = ObjectRepository.get_instance()
    assert repo1 == repo2


def test_object_repository_singleton_error():
    ObjectRepository.get_instance()
    with pytest.raises(Exception):
        ObjectRepository()


def test_material_restrictions_valid():
    MaterialRestrictions.valid_shape_material_or_raise(
        'car_1',
        'UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/gray_1x1')  # noqa
    MaterialRestrictions.valid_shape_material_or_raise(
        'cup_6',
        'AI2-THOR/Materials/Metals/HammeredMetal_AlbedoTransparency 1')
    MaterialRestrictions.valid_shape_material_or_raise(
        'bookcase_1_shelf',
        "UnityAssetStore/Kindergarten_Interior/Models/Materials/color 4")
    MaterialRestrictions.valid_shape_material_or_raise(
        'cube', "AI2-THOR/Materials/Ceramics/WhiteCountertop")
    MaterialRestrictions.valid_shape_material_or_raise(
        'wardrobe', 'AI2-THOR/Materials/Wood/BedroomFloor1')
    MaterialRestrictions.valid_shape_material_or_raise(
        'crayon_yellow', None)


def test_material_restrictions_invalid():
    with pytest.raises(ILEException):
        MaterialRestrictions.valid_shape_material_or_raise(
            'car_1', "AI2-THOR/Materials/Ceramics/WhiteCountertop")

    with pytest.raises(ILEException):
        MaterialRestrictions.valid_shape_material_or_raise(
            'cart_1', "AI2-THOR/Materials/Wood/DarkWood2")


def test_get_step_after_movement():
    repo = ObjectRepository.get_instance()

    object_1 = {'id': 'object_1'}
    object_2 = {
        'id': 'object_2',
        'moves': [{
            'stepBegin': 1,
            'stepEnd': 10
        }]
    }
    object_3 = {
        'id': 'object_3',
        'moves': [{
            'stepBegin': 21,
            'stepEnd': 60
        }]
    }
    object_4 = {
        'id': 'object_4',
        'moves': [{
            'stepBegin': 31,
            'stepEnd': 40
        }]
    }
    object_5 = {
        'id': 'object_5',
        'rotates': [{
            'stepBegin': 1,
            'stepEnd': 10
        }]
    }
    object_6 = {
        'id': 'object_6',
        'rotates': [{
            'stepBegin': 21,
            'stepEnd': 60
        }]
    }

    idl_1 = InstanceDefinitionLocationTuple(object_1, {}, {})
    idl_2 = InstanceDefinitionLocationTuple(object_2, {}, {})
    idl_3 = InstanceDefinitionLocationTuple(object_3, {}, {})
    idl_4 = InstanceDefinitionLocationTuple(object_4, {}, {})
    idl_5 = InstanceDefinitionLocationTuple(object_5, {}, {})
    idl_6 = InstanceDefinitionLocationTuple(object_6, {}, {})

    repo.add_to_labeled_objects(idl_1, ['label_1'])
    repo.add_to_labeled_objects(idl_2, ['label_2'])
    repo.add_to_labeled_objects(idl_3, ['label_3'])
    repo.add_to_labeled_objects(idl_4, ['label_4'])
    repo.add_to_labeled_objects(idl_5, ['label_5_6'])
    repo.add_to_labeled_objects(idl_6, ['label_5_6'])

    assert get_step_after_movement([]) == 1
    assert get_step_after_movement(['label_1']) == 1
    assert get_step_after_movement(['label_2']) == 11
    assert get_step_after_movement(['label_3']) == 61
    assert get_step_after_movement(['label_4']) == 41
    assert get_step_after_movement(['label_2', 'label_3']) == 61
    assert get_step_after_movement(['label_2', 'label_4']) == 41
    assert get_step_after_movement(['label_3', 'label_4']) == 61
    assert get_step_after_movement(['label_2', 'label_3', 'label_4']) == 61
    assert get_step_after_movement(['label_5_6']) == 61


def test_get_step_after_movement_delay():
    with pytest.raises(ILEDelayException):
        # Error because no objects with this label are in the ObjectRepository
        get_step_after_movement(['label_1'])


def test_get_step_after_movement_or_start():
    repo = ObjectRepository.get_instance()

    object_1 = {'id': 'object_1'}
    object_2 = {
        'id': 'object_2',
        'moves': [{
            'stepBegin': 1,
            'stepEnd': 10
        }]
    }
    object_3 = {
        'id': 'object_3',
        'moves': [{
            'stepBegin': 21,
            'stepEnd': 60
        }]
    }
    object_4 = {
        'id': 'object_4',
        'moves': [{
            'stepBegin': 31,
            'stepEnd': 40
        }]
    }
    object_5 = {
        'id': 'object_5',
        'rotates': [{
            'stepBegin': 1,
            'stepEnd': 10
        }]
    }
    object_6 = {
        'id': 'object_6',
        'rotates': [{
            'stepBegin': 21,
            'stepEnd': 60
        }]
    }

    idl_1 = InstanceDefinitionLocationTuple(object_1, {}, {})
    idl_2 = InstanceDefinitionLocationTuple(object_2, {}, {})
    idl_3 = InstanceDefinitionLocationTuple(object_3, {}, {})
    idl_4 = InstanceDefinitionLocationTuple(object_4, {}, {})
    idl_5 = InstanceDefinitionLocationTuple(object_5, {}, {})
    idl_6 = InstanceDefinitionLocationTuple(object_6, {}, {})

    repo.add_to_labeled_objects(idl_1, ['label_1'])
    repo.add_to_labeled_objects(idl_2, ['label_2'])
    repo.add_to_labeled_objects(idl_3, ['label_3'])
    repo.add_to_labeled_objects(idl_4, ['label_4'])
    repo.add_to_labeled_objects(idl_5, ['label_5_6'])
    repo.add_to_labeled_objects(idl_6, ['label_5_6'])

    assert get_step_after_movement_or_start([]) == 1
    assert get_step_after_movement_or_start(['label_1']) == 1
    assert get_step_after_movement_or_start(['label_2']) == 11
    assert get_step_after_movement_or_start(['label_3']) == 1
    assert get_step_after_movement_or_start(['label_4']) == 1
    assert get_step_after_movement_or_start(['label_2', 'label_3']) == 61
    assert get_step_after_movement_or_start(['label_2', 'label_4']) == 41
    assert get_step_after_movement_or_start(['label_3', 'label_4']) == 1
    assert get_step_after_movement_or_start(
        ['label_2', 'label_3', 'label_4']
    ) == 61
    assert get_step_after_movement_or_start(['label_5_6']) == 61


def test_get_step_after_movement_or_start_delay():
    with pytest.raises(ILEDelayException):
        # Error because no objects with this label are in the ObjectRepository
        get_step_after_movement_or_start(['label_1'])


def test_calculate_rotated_position():
    container_position = {'x': 1, 'y': 0.5, 'z': 0}
    container_dimensions = {'x': 1, 'y': 1, 'z': 1}
    mock_container = {
        'id': 'container_1234',
        'debug': {
            'dimensions': container_dimensions,
            'isRotatedBy': 'turntable_5678',
            'positionY': 0
        },
        'shows': [{
            'boundingBox': geometry.create_bounds(
                container_dimensions,
                None,
                container_position,
                {'x': 0, 'y': 0, 'z': 0},
                0
            ),
            'position': container_position
        }]
    }
    mock_turntable = {
        'id': 'turntable_5678',
        'rotates': [{
            'stepBegin': 1,
            'stepEnd': None,
            'vector': {'x': 0, 'y': 5, 'z': 0}
        }],
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0}
        }]
    }
    scene = prior_scene()
    scene.objects.append(mock_turntable)

    # Test: clockwise rotation, varying degrees.
    for step_end, expected_x, expected_z in [
        (9, 0.70710678, -0.70710678), (18, 0, -1),
        (27, -0.70710678, -0.70710678), (36, -1, 0),
        (45, -0.70710678, 0.70710678), (54, 0, 1),
        (63, 0.70710678, 0.70710678), (72, 1, 0)
    ]:
        mock_turntable['rotates'][0]['stepEnd'] = step_end
        actual = calculate_rotated_position(
            scene,
            step_end + 10,
            mock_container
        )
        expected = {'x': expected_x, 'y': 0.5, 'z': expected_z}
        if actual != pytest.approx(expected):
            print(f'{step_end=} {expected_x=} {expected_z=}')
        assert actual == pytest.approx(expected)

    # Adjustments for next test...
    mock_turntable['rotates'][0]['vector']['y'] = -5

    # Test: counterclockwise rotation, varying degrees.
    for step_end, expected_x, expected_z in [
        (9, 0.70710678, 0.70710678), (18, 0, 1),
        (27, -0.70710678, 0.70710678), (36, -1, 0),
        (45, -0.70710678, -0.70710678), (54, 0, -1),
        (63, 0.70710678, -0.70710678), (72, 1, 0)
    ]:
        mock_turntable['rotates'][0]['stepEnd'] = step_end
        actual = calculate_rotated_position(
            scene,
            step_end + 10,
            mock_container
        )
        expected = {'x': expected_x, 'y': 0.5, 'z': expected_z}
        if actual != pytest.approx(expected):
            print(f'{step_end=} {expected_x=} {expected_z=}')
        assert actual == pytest.approx(expected)

    # Adjustments for next test...
    container_position = {'x': 2, 'y': 0.5, 'z': 1}
    mock_container['shows'][0]['position'] = container_position
    mock_container['shows'][0]['boundingBox'] = geometry.create_bounds(
        container_dimensions,
        None,
        container_position,
        {'x': 0, 'y': 0, 'z': 0},
        0
    )
    mock_turntable['shows'][0]['position'] = {'x': 1, 'y': 0, 'z': 1}
    mock_turntable['rotates'][0]['vector']['y'] = 5

    # Test: non-zero turntable position.
    for step_end, expected_x, expected_z in [
        (9, 1.70710678, 0.29289322), (18, 1, 0),
        (27, 0.29289322, 0.29289322), (36, 0, 1),
        (45, 0.29289322, 1.70710678), (54, 1, 2),
        (63, 1.70710678, 1.70710678), (72, 2, 1)
    ]:
        mock_turntable['rotates'][0]['stepEnd'] = step_end
        actual = calculate_rotated_position(
            scene,
            step_end + 10,
            mock_container
        )
        expected = {'x': expected_x, 'y': 0.5, 'z': expected_z}
        if actual != pytest.approx(expected):
            print(f'{step_end=} {expected_x=} {expected_z=}')
        assert actual == pytest.approx(expected)


def test_calculate_rotated_position_return_none():
    container_position = {'x': 1, 'y': 0.5, 'z': 0}
    container_dimensions = {'x': 1, 'y': 1, 'z': 1}
    mock_container = {
        'id': 'container_1234',
        'debug': {
            'dimensions': container_dimensions,
            'isRotatedBy': None,
            'positionY': 0
        },
        'shows': [{
            'boundingBox': geometry.create_bounds(
                container_dimensions,
                None,
                container_position,
                {'x': 0, 'y': 0, 'z': 0},
                0
            ),
            'position': container_position
        }]
    }
    scene = prior_scene()

    # Test: container does not have isRotatedBy property.
    actual = calculate_rotated_position(
        scene,
        20,
        mock_container
    )
    assert actual is None

    mock_container['debug']['isRotatedBy'] = 'turntable_5678'
    mock_turntable = {
        'id': 'turntable_5678',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0}
        }]
    }
    scene.objects.append(mock_turntable)

    # Test: turntable does not rotate.
    actual = calculate_rotated_position(
        scene,
        20,
        mock_container
    )
    assert actual is None

    mock_turntable['rotates'] = [{
        'stepBegin': 1,
        'stepEnd': 9,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }]

    # Test: container starts with lid already on placed it (lid_step_begin=0).
    actual = calculate_rotated_position(
        scene,
        0,
        mock_container
    )
    assert actual is None

    mock_turntable['rotates'] = [{
        'stepBegin': 21,
        'stepEnd': 29,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }]

    # Test: container lid is placed before turntable starts rotating.
    actual = calculate_rotated_position(
        scene,
        1,
        mock_container
    )
    assert actual is None


def test_calculate_rotated_position_error_placed_during_rotation():
    container_position = {'x': 1, 'y': 0.5, 'z': 0}
    container_dimensions = {'x': 1, 'y': 1, 'z': 1}
    mock_container = {
        'id': 'container_1234',
        'debug': {
            'dimensions': container_dimensions,
            'isRotatedBy': 'turntable_5678',
            'positionY': 0
        },
        'shows': [{
            'boundingBox': geometry.create_bounds(
                container_dimensions,
                None,
                container_position,
                {'x': 0, 'y': 0, 'z': 0},
                0
            ),
            'position': container_position
        }]
    }
    mock_turntable = {
        'id': 'turntable_5678',
        'rotates': [{
            'stepBegin': 2,
            'stepEnd': 100,
            'vector': {'x': 0, 'y': 5, 'z': 0}
        }],
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0}
        }]
    }
    scene = prior_scene()
    scene.objects.append(mock_turntable)

    # Test: container lid is placed as turntable is rotating.
    with pytest.raises(SceneException):
        calculate_rotated_position(
            scene,
            1,
            mock_container
        )


def test_calculate_rotated_position_error_placed_step_begin():
    # Assume our function will resolve its placer_steps to to following value:
    placer_steps = 6

    container_position = {'x': 1, 'y': 0.5, 'z': 0}
    container_dimensions = {'x': 1, 'y': 1, 'z': 1}
    mock_container = {
        'id': 'container_1234',
        'debug': {
            'dimensions': container_dimensions,
            'isRotatedBy': 'turntable_5678',
            'positionY': 0
        },
        'shows': [{
            'boundingBox': geometry.create_bounds(
                container_dimensions,
                None,
                container_position,
                {'x': 0, 'y': 0, 'z': 0},
                0
            ),
            'position': container_position
        }]
    }
    mock_turntable = {
        'id': 'turntable_5678',
        'rotates': [{
            'stepBegin': 1 + placer_steps,
            'stepEnd': 18 + placer_steps,
            'vector': {'x': 0, 'y': 5, 'z': 0}
        }],
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0}
        }]
    }
    scene = prior_scene()
    scene.objects.append(mock_turntable)

    # Test: container lid is placed on same step turntable starts rotating.
    with pytest.raises(SceneException):
        calculate_rotated_position(
            scene,
            1,
            mock_container
        )


def test_calculate_rotated_position_error_placed_step_end():
    # Assume our function will resolve its placer_steps to to following value:
    placer_steps = 6

    container_position = {'x': 1, 'y': 0.5, 'z': 0}
    container_dimensions = {'x': 1, 'y': 1, 'z': 1}
    mock_container = {
        'id': 'container_1234',
        'debug': {
            'dimensions': container_dimensions,
            'isRotatedBy': 'turntable_5678',
            'positionY': 0
        },
        'shows': [{
            'boundingBox': geometry.create_bounds(
                container_dimensions,
                None,
                container_position,
                {'x': 0, 'y': 0, 'z': 0},
                0
            ),
            'position': container_position
        }]
    }
    mock_turntable = {
        'id': 'turntable_5678',
        'rotates': [{
            'stepBegin': 1,
            'stepEnd': 18,
            'vector': {'x': 0, 'y': 5, 'z': 0}
        }],
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0}
        }]
    }
    scene = prior_scene()
    scene.objects.append(mock_turntable)

    # Test: container lid is placed on same step turntable finishes rotating.
    with pytest.raises(SceneException):
        calculate_rotated_position(
            scene,
            18 - placer_steps,
            mock_container
        )


def test_calculate_rotated_position_edge_case():
    container_position = {'x': 1, 'y': 0.5, 'z': 0}
    container_dimensions = {'x': 1, 'y': 1, 'z': 1}
    mock_container = {
        'id': 'container_1234',
        'debug': {
            'dimensions': container_dimensions,
            'isRotatedBy': 'turntable_5678',
            'positionY': 0
        },
        'shows': [{
            'boundingBox': geometry.create_bounds(
                container_dimensions,
                None,
                container_position,
                {'x': 0, 'y': 0, 'z': 0},
                0
            ),
            'position': container_position
        }]
    }
    mock_turntable = {
        'id': 'turntable_5678',
        'rotates': [{
            'stepBegin': 1,
            'stepEnd': 18,
            'vector': {'x': 0, 'y': 5, 'z': 0}
        }],
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0}
        }]
    }
    scene = prior_scene()
    scene.objects.append(mock_turntable)

    # Assume our function will resolve its placer_steps to to following value:
    placer_steps = 6

    # Test: container lid is placed on step turntable finishes rotating.
    actual = calculate_rotated_position(
        scene,
        19 - placer_steps,
        mock_container
    )
    assert actual == pytest.approx({'x': 0, 'y': 0.5, 'z': -1})

    # Test: container places its lid the step the turntable starts rotating.
    mock_turntable['rotates'][0]['stepEnd'] = placer_steps
    actual = calculate_rotated_position(
        scene,
        1,
        mock_container
    )
    assert actual == pytest.approx({'x': 0.866025, 'y': 0.5, 'z': -0.5})
