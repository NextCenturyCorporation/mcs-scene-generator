from generator import (
    DefinitionDataset,
    ObjectDefinition,
    gravity_support_objects,
)


def test_getters_reuse_immutable_dataset():
    dataset_1 = (
        gravity_support_objects.get_symmetric_target_definition_dataset(
            unshuffled=True
        )
    )
    dataset_2 = (
        gravity_support_objects.get_symmetric_target_definition_dataset(
            unshuffled=True
        )
    )
    assert dataset_1 is dataset_2
    assert isinstance(dataset_1, DefinitionDataset)


def test_does_have_definitions():
    dataset = gravity_support_objects.get_asymmetric_target_definition_dataset(
        unshuffled=True
    )
    definitions = dataset.definitions()
    assert len(definitions) > 0
    for definition in definitions:
        assert isinstance(definition, ObjectDefinition)

    dataset = gravity_support_objects.get_symmetric_target_definition_dataset(
        unshuffled=True
    )
    definitions = dataset.definitions()
    assert len(definitions) > 0
    for definition in definitions:
        assert isinstance(definition, ObjectDefinition)

    output = gravity_support_objects.get_visible_support_object_definition()
    assert isinstance(output, ObjectDefinition)


def test_create_pole_template():
    pole = gravity_support_objects.create_pole_template(1)
    assert pole['shows'][0]['stepBegin'] == 1
    assert pole['moves'][0]['stepBegin'] == 1

    pole = gravity_support_objects.create_pole_template(100)
    assert pole['shows'][0]['stepBegin'] == 100
    assert pole['moves'][0]['stepBegin'] == 100
