import pytest

from ideal_learning_env import (
    ILEException,
    InstanceDefinitionLocationTuple,
    MaterialRestrictions,
    ObjectRepository
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
