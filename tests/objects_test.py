import math
import objects
import occluders
import tags
import util


def test_all_objects_have_expected_properties():
    for definition_list in util.retrieve_complete_definition_list(
        objects.get(objects.ObjectDefinitionList.ALL)
    ):
        for object_definition in definition_list:
            print(f'{object_definition["type"]}')
            assert 'type' in object_definition
            assert 'size' in object_definition
            assert 'shape' in object_definition
            assert 'mass' in object_definition
            assert 'attributes' in object_definition
            assert 'dimensions' in object_definition
            assert 'materialCategory' in object_definition
            assert 'salientMaterials' in object_definition
            if len(object_definition['materialCategory']) == 0:
                assert 'color' in object_definition
            assert 'info' not in object_definition
            if 'massMultiplier' in object_definition:
                if object_definition['massMultiplier'] < 1:
                    print('[ERROR] Mass multiplier < 1 will cause '
                          'intermittent errors in other parts of the code')
                    assert False


def test_get_copies_lists():
    list_1 = objects.get(objects.ObjectDefinitionList.ALL)
    list_2 = objects.get(objects.ObjectDefinitionList.ALL)
    assert not (list_1 is list_2)
    assert list_1 == list_2
    for index in range(len(list_1)):
        assert not (list_1[index] is list_2[index])


def test_does_have_definitions():
    output_list = objects.get(objects.ObjectDefinitionList.ALL)
    assert len(output_list) > 0
    for definition_list in output_list:
        assert len(definition_list) > 0

    output_list = objects.get(objects.ObjectDefinitionList.CONTAINERS)
    assert len(output_list) > 0
    for definition_list in output_list:
        assert len(definition_list) > 0

    output_list = objects.get(objects.ObjectDefinitionList.OBSTACLES)
    assert len(output_list) > 0
    for definition_list in output_list:
        assert len(definition_list) > 0

    output_list = objects.get(objects.ObjectDefinitionList.OCCLUDERS)
    assert len(output_list) > 0
    for definition_list in output_list:
        assert len(definition_list) > 0

    output_list = objects.get(objects.ObjectDefinitionList.PICKUPABLES)
    assert len(output_list) > 0
    for definition_list in output_list:
        assert len(definition_list) > 0

    output_list = objects.get(objects.ObjectDefinitionList.NOT_PICKUPABLES)
    assert len(output_list) > 0
    for definition_list in output_list:
        assert len(definition_list) > 0


def test_intuitive_physics_all_objects_diagonal_size():
    # The fall-down list should contain the move-across objects as well.
    for definition in util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(True)]
    )[0]:
        print(f'{definition}\n========================================')
        assert (
            (definition['dimensions']['x'] * math.sqrt(2)) <=
            (occluders.OCCLUDER_MAX_SCALE_X + util.MAX_SIZE_DIFFERENCE)
        )


def test_intuitive_physics_move_across_all_objects_untrained_shapes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(False)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SHAPE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_shape(definition_1, definition_2,
                                               True)
        ]
        assert len(option_list) >= 2


def test_intuitive_physics_fall_down_all_objects_untrained_shapes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(True)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SHAPE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_shape(definition_1, definition_2,
                                               True)
        ]
        assert len(option_list) >= 2


def test_intuitive_physics_move_across_basic_objects_untrained_shapes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(False, True, False)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SHAPE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_shape(definition_1, definition_2,
                                               True)
        ]
        # TODO: We want at least two possible untrained objects.
        # assert len(option_list) >= 2
        assert len(option_list) >= 1


def test_intuitive_physics_fall_down_basic_objects_untrained_shapes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(True, True, False)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SHAPE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_shape(definition_1, definition_2,
                                               True)
        ]
        # TODO: We want at least two possible untrained objects.
        # assert len(option_list) >= 2
        assert len(option_list) >= 1


def test_intuitive_physics_move_across_complex_objects_untrained_shapes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(False, False, True)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SHAPE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_shape(definition_1, definition_2,
                                               True)
        ]
        assert len(option_list) >= 2


def test_intuitive_physics_fall_down_complex_objects_untrained_shapes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(True, False, True)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SHAPE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_shape(definition_1, definition_2,
                                               True)
        ]
        # We want at least two possible untrained objects.
        assert len(option_list) >= 2


def test_intuitive_physics_move_across_all_objects_untrained_sizes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(False)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SIZE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_size(definition_1, definition_2,
                                              True)
        ]
        # We want at least two possible untrained objects.
        assert len(option_list) >= 2


def test_intuitive_physics_fall_down_all_objects_untrained_sizes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(True)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SIZE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_size(definition_1, definition_2,
                                              True)
        ]
        # We want at least two possible untrained objects.
        assert len(option_list) >= 2


def test_intuitive_physics_move_across_basic_objects_untrained_sizes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(False, True, False)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SIZE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_size(definition_1, definition_2,
                                              True)
        ]
        # We want at least two possible untrained objects.
        assert len(option_list) >= 2


def test_intuitive_physics_fall_down_basic_objects_untrained_sizes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(True, True, False)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SIZE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_size(definition_1, definition_2,
                                              True)
        ]
        # We want at least two possible untrained objects.
        assert len(option_list) >= 2


def test_intuitive_physics_move_across_complex_objects_untrained_sizes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(False, False, True)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SIZE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_size(definition_1, definition_2,
                                              True)
        ]
        # We want at least two possible untrained objects.
        assert len(option_list) >= 2


def test_intuitive_physics_fall_down_complex_objects_untrained_sizes():
    definition_list = util.retrieve_complete_definition_list(
        [objects.get_intuitive_physics(True, False, True)]
    )[0]
    trained_list = util.retrieve_trained_definition_list([definition_list])[0]
    untrained_list = util.retrieve_untrained_definition_list(
        [definition_list],
        tags.SCENE.UNTRAINED_SIZE
    )[0]

    for definition_1 in trained_list:
        option_list = [
            definition_2 for definition_2 in untrained_list
            if util.is_similar_except_in_size(definition_1, definition_2,
                                              True)
        ]
        # We want at least two possible untrained objects.
        assert len(option_list) >= 2
