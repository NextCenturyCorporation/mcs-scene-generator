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


@pytest.mark.slow
def test_does_have_definitions():
    dataset = specific_objects.get_interactable_definition_dataset()
    definitions = dataset.definitions()
    assert len(definitions) > 0
    assert isinstance(definitions[0], ObjectDefinition)
    trained_dataset = dataset.filter_on_trained()
    assert len(trained_dataset.definitions()) > 0
    untrained_dataset = dataset.filter_on_untrained('untrainedShape')
    assert len(untrained_dataset.definitions()) > 0

    dataset = specific_objects.get_container_definition_dataset()
    definitions = dataset.definitions()
    assert len(definitions) > 0
    assert isinstance(definitions[0], ObjectDefinition)
    trained_dataset = dataset.filter_on_trained()
    assert len(trained_dataset.definitions()) > 0
    untrained_dataset = dataset.filter_on_untrained('untrainedShape')
    assert len(untrained_dataset.definitions()) > 0

    dataset = specific_objects.get_container_open_topped_definition_dataset()
    definitions = dataset.definitions()
    assert len(definitions) > 0
    assert isinstance(definitions[0], ObjectDefinition)
    trained_dataset = dataset.filter_on_trained()
    assert len(trained_dataset.definitions()) > 0
    # Not necessary in Eval 4 tasks
    # untrained_dataset = dataset.filter_on_untrained('untrainedShape')
    # assert len(untrained_dataset.definitions()) > 0

    dataset = specific_objects.get_obstacle_definition_dataset()
    definitions = dataset.definitions()
    assert len(definitions) > 0
    assert isinstance(definitions[0], ObjectDefinition)
    trained_dataset = dataset.filter_on_trained()
    assert len(trained_dataset.definitions()) > 0
    untrained_dataset = dataset.filter_on_untrained('untrainedShape')
    assert len(untrained_dataset.definitions()) > 0

    dataset = specific_objects.get_occluder_definition_dataset()
    definitions = dataset.definitions()
    assert len(definitions) > 0
    assert isinstance(definitions[0], ObjectDefinition)
    trained_dataset = dataset.filter_on_trained()
    assert len(trained_dataset.definitions()) > 0
    untrained_dataset = dataset.filter_on_untrained('untrainedShape')
    assert len(untrained_dataset.definitions()) > 0

    dataset = specific_objects.get_pickupable_definition_dataset()
    definitions = dataset.definitions()
    assert len(definitions) > 0
    assert isinstance(definitions[0], ObjectDefinition)
    trained_dataset = dataset.filter_on_trained()
    assert len(trained_dataset.definitions()) > 0
    # Not necessary in Eval 4 tasks
    # untrained_dataset = dataset.filter_on_untrained('untrainedShape')
    # assert len(untrained_dataset.definitions()) > 0

    dataset = specific_objects.get_non_pickupable_definition_dataset()
    definitions = dataset.definitions()
    assert len(definitions) > 0
    assert isinstance(definitions[0], ObjectDefinition)
    trained_dataset = dataset.filter_on_trained()
    assert len(trained_dataset.definitions()) > 0
    # Not necessary in Eval 4 tasks
    # untrained_dataset = dataset.filter_on_untrained('untrainedShape')
    # assert len(untrained_dataset.definitions()) > 0


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
