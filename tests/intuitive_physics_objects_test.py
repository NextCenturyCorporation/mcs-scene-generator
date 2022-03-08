import pytest

from generator import (
    DefinitionDataset,
    ObjectDefinition,
    intuitive_physics_objects,
    tags,
)

SIDEWAYS_SHAPES = [
    'car_1', 'racecar_red', 'train_1', 'trolley_1', 'bus_1', 'car_2', 'cart_2',
    'dog_on_wheels', 'truck_1', 'truck_2'
]


def test_getters_reuse_immutable_dataset():
    dataset_1 = intuitive_physics_objects.get_fall_down_definition_dataset(
        unshuffled=True
    )
    dataset_2 = intuitive_physics_objects.get_fall_down_definition_dataset(
        unshuffled=True
    )
    assert dataset_1 is dataset_2
    assert isinstance(dataset_1, DefinitionDataset)


def test_does_have_definitions():
    dataset = intuitive_physics_objects.get_fall_down_definition_dataset(
        unshuffled=True
    )
    definitions = dataset.definitions()
    assert len(definitions) > 0
    for definition in definitions:
        assert isinstance(definition, ObjectDefinition)

    dataset = intuitive_physics_objects.get_fall_down_opposite_colors_definition_dataset(  # noqa: E501
        unshuffled=True
    )
    definitions = dataset.definitions()
    assert len(definitions) > 0
    for definition in definitions:
        assert isinstance(definition, ObjectDefinition)

    dataset = intuitive_physics_objects.get_move_across_definition_dataset(
        unshuffled=True
    )
    definitions = dataset.definitions()
    assert len(definitions) > 0
    for definition in definitions:
        assert isinstance(definition, ObjectDefinition)

    dataset = intuitive_physics_objects.get_move_across_opposite_colors_definition_dataset(  # noqa: E501
        unshuffled=True
    )
    definitions = dataset.definitions()
    assert len(definitions) > 0
    for definition in definitions:
        assert isinstance(definition, ObjectDefinition)


def test_does_have_sideways_definitions():
    dataset = intuitive_physics_objects.get_move_across_definition_dataset(
        unshuffled=True
    )
    definitions = dataset.definitions()
    assert len(definitions) > 0
    for definition in definitions:
        if definition.type in SIDEWAYS_SHAPES:
            assert definition.rotation.y == 90
        else:
            assert definition.rotation.y == 0


@pytest.mark.slow
def test_intuitive_physics_move_across_all_objects_untrained_shapes():
    dataset = intuitive_physics_objects.get_move_across_definition_dataset(
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SHAPE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_shape(
            definition_1,
            only_diagonal_size=True
        )
        assert len(filtered_dataset.definitions()) >= 2


@pytest.mark.slow
def test_intuitive_physics_fall_down_all_objects_untrained_shapes():
    dataset = intuitive_physics_objects.get_fall_down_definition_dataset(
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SHAPE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_shape(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        assert len(filtered_dataset.definitions()) >= 2


def test_intuitive_physics_move_across_basic_objects_untrained_shapes():
    dataset = intuitive_physics_objects.get_move_across_basic_shape_definition_dataset(  # noqa: E501
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SHAPE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_shape(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        assert len(filtered_dataset.definitions()) >= 2


def test_intuitive_physics_fall_down_basic_objects_untrained_shapes():
    dataset = intuitive_physics_objects.get_fall_down_basic_shape_definition_dataset(  # noqa: E501
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SHAPE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_shape(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        assert len(filtered_dataset.definitions()) >= 2


def test_intuitive_physics_move_across_complex_objects_untrained_shapes():
    dataset = intuitive_physics_objects.get_move_across_complex_shape_definition_dataset(  # noqa: E501
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SHAPE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_shape(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        assert len(filtered_dataset.definitions()) >= 2


def test_intuitive_physics_fall_down_complex_objects_untrained_shapes():
    dataset = intuitive_physics_objects.get_fall_down_complex_shape_definition_dataset(  # noqa: E501
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SHAPE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_shape(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        # We want at least two possible untrained objects.
        assert len(filtered_dataset.definitions()) >= 2


def test_intuitive_physics_move_across_all_objects_untrained_sizes():
    dataset = intuitive_physics_objects.get_move_across_definition_dataset(
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SIZE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_size(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        # We want at least two possible untrained objects.
        assert len(filtered_dataset.definitions()) >= 2


def test_intuitive_physics_fall_down_all_objects_untrained_sizes():
    dataset = intuitive_physics_objects.get_fall_down_definition_dataset(
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SIZE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_size(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        # We want at least two possible untrained objects.
        assert len(filtered_dataset.definitions()) >= 2


def test_intuitive_physics_move_across_basic_objects_untrained_sizes():
    dataset = intuitive_physics_objects.get_move_across_basic_shape_definition_dataset(  # noqa: E501
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SIZE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_size(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        # We want at least two possible untrained objects.
        assert len(filtered_dataset.definitions()) >= 2


def test_intuitive_physics_fall_down_basic_objects_untrained_sizes():
    dataset = intuitive_physics_objects.get_fall_down_basic_shape_definition_dataset(  # noqa: E501
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SIZE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_size(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        # We want at least two possible untrained objects.
        assert len(filtered_dataset.definitions()) >= 2


def test_intuitive_physics_move_across_complex_objects_untrained_sizes():
    dataset = intuitive_physics_objects.get_move_across_complex_shape_definition_dataset(  # noqa: E501
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SIZE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_size(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        # We want at least two possible untrained objects.
        assert len(filtered_dataset.definitions()) >= 2


def test_intuitive_physics_fall_down_complex_objects_untrained_sizes():
    dataset = intuitive_physics_objects.get_fall_down_complex_shape_definition_dataset(  # noqa: E501
        unshuffled=True
    )
    trained_dataset = dataset.filter_on_trained()
    untrained_dataset = dataset.filter_on_untrained(
        tags.SCENE.UNTRAINED_SIZE
    )

    for definition_1 in trained_dataset.definitions(unshuffled=True):
        filtered_dataset = untrained_dataset.filter_on_similar_except_size(
            definition_1,
            only_diagonal_size=True
        )
        print(f'{definition_1.type} {definition_1.scale}')
        # We want at least two possible untrained objects.
        assert len(filtered_dataset.definitions()) >= 2
