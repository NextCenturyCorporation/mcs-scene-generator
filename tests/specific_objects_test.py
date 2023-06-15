import pytest

from generator import DefinitionDataset, ObjectDefinition, specific_objects


def test_getters_reuse_immutable_dataset():
    dataset_1 = specific_objects.get_interactable_definition_dataset(
        unshuffled=True
    )
    dataset_2 = specific_objects.get_interactable_definition_dataset(
        unshuffled=True
    )
    assert dataset_1 is dataset_2
    assert isinstance(dataset_1, DefinitionDataset)


def validate_datasets(dataset, no_untrained_shape=False):
    definitions = dataset.definitions_unique_shape_scale()
    assert len(definitions) > 0
    assert isinstance(definitions[0], ObjectDefinition)
    trained_dataset = dataset.filter_on_trained()
    assert len(trained_dataset.definitions_unique_shape_scale()) > 0
    if not no_untrained_shape:
        untrained_dataset = dataset.filter_on_untrained('untrainedShape')
        assert len(untrained_dataset.definitions_unique_shape_scale()) > 0


@pytest.mark.slow
def test_does_have_definitions():
    dataset = specific_objects.get_interactable_definition_dataset()
    validate_datasets(dataset)

    dataset = specific_objects.get_container_definition_dataset()
    validate_datasets(dataset)

    dataset = specific_objects.get_container_asymmetric_definition_dataset()
    validate_datasets(dataset, no_untrained_shape=True)

    dataset = specific_objects.get_container_bin_definition_dataset()
    validate_datasets(dataset, no_untrained_shape=True)

    dataset = specific_objects.get_container_open_topped_definition_dataset()
    validate_datasets(dataset, no_untrained_shape=True)

    dataset = specific_objects.get_container_openable_definition_dataset()
    validate_datasets(dataset)

    dataset = specific_objects.get_container_symmetric_definition_dataset()
    validate_datasets(dataset, no_untrained_shape=True)

    dataset = specific_objects.get_obstacle_definition_dataset()
    validate_datasets(dataset)

    dataset = specific_objects.get_occluder_definition_dataset()
    validate_datasets(dataset)

    dataset = specific_objects.get_pickupable_definition_dataset()
    validate_datasets(dataset, no_untrained_shape=True)

    dataset = specific_objects.get_non_pickupable_definition_dataset()
    validate_datasets(dataset, no_untrained_shape=True)


def test_choose_distractor_definition():
    dataset = specific_objects.get_interactable_definition_dataset(
        unshuffled=True
    )
    assert len(dataset._definition_groups)
    for definition_selections in dataset._definition_groups:
        assert len(definition_selections)
        for definition_variations in definition_selections:
            assert len(definition_variations)
            # Just test the first element since testing the full list will take
            # a long time and each variation here is simply a different color.
            definition = definition_variations[0]
            assert specific_objects.choose_distractor_definition(
                [definition.shape]
            )
