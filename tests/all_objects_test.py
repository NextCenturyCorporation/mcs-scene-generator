import math

import pytest

from generator import (
    definitions,
    gravity_support_objects,
    intuitive_physics_objects,
    occluders,
    specific_objects
)


@pytest.mark.slow
def test_all_objects_have_expected_properties():
    for dataset in [
        specific_objects.get_interactable_definition_dataset(unshuffled=True),
        gravity_support_objects.get_asymmetric_target_definition_dataset(
            unshuffled=True
        ),
        gravity_support_objects.get_symmetric_target_definition_dataset(
            unshuffled=True
        ),
        intuitive_physics_objects.get_fall_down_definition_dataset(
            unshuffled=True
        ),
        intuitive_physics_objects.get_move_across_definition_dataset(
            unshuffled=True
        ),
        definitions.create_dataset([[
            gravity_support_objects.get_visible_support_object_definition()
        ]], unshuffled=True)
    ]:
        for object_definition in dataset.definitions(unshuffled=True):
            print(f'{object_definition.type}')
            assert object_definition.type
            assert object_definition.size
            assert object_definition.shape
            assert object_definition.mass
            assert object_definition.attributes is not None
            assert object_definition.dimensions
            if 'structure' not in object_definition.attributes:
                assert object_definition.materialCategory is not None
                assert object_definition.salientMaterials
                if len(object_definition.materialCategory) == 0:
                    assert object_definition.color
            if object_definition.massMultiplier:
                if object_definition.massMultiplier < 1:
                    print('[ERROR] Mass multiplier < 1 will cause '
                          'intermittent errors in other parts of the code')
                    assert False


def test_intuitive_physics_all_objects_diagonal_size():
    for dataset in [
        gravity_support_objects.get_asymmetric_target_definition_dataset(
            unshuffled=True
        ),
        gravity_support_objects.get_symmetric_target_definition_dataset(
            unshuffled=True
        ),
        intuitive_physics_objects.get_fall_down_definition_dataset(
            unshuffled=True
        ),
        intuitive_physics_objects.get_move_across_definition_dataset(
            unshuffled=True
        )
    ]:
        for definition in dataset.definitions(unshuffled=True):
            print(f'{definition}\n========================================')
            # If diagonal size is too big, it will cause an occassional issue
            # with implausible event calculations in intuitive physics scenes.
            assert math.sqrt(
                definition.dimensions.x**2 +
                definition.dimensions.z**2
            ) <= (
                occluders.OCCLUDER_MAX_SCALE_X + occluders.OCCLUDER_BUFFER +
                definitions.MAX_SIZE_DIFF
            )
