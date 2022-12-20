import pytest

from ideal_learning_env import (
    ILEDelayException,
    ILEException,
    InstanceDefinitionLocationTuple,
    MaterialRestrictions,
    ObjectRepository
)
from ideal_learning_env.object_services import (
    get_step_after_movement,
    get_step_after_movement_or_start
)


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
