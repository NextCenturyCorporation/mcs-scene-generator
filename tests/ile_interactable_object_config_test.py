import math

import pytest

from generator import base_objects, materials
from ideal_learning_env import (
    InteractableObjectConfig,
    VectorFloatConfig,
    find_bounds,
)
from ideal_learning_env.defs import ILEException
from ideal_learning_env.interactable_object_config import (
    KeywordLocationConfig,
    ObjectRepository,
)
from ideal_learning_env.object_services import KeywordLocation


@pytest.fixture(autouse=True)
def run_before_test():
    ObjectRepository.get_instance().clear()


def test_find_bounds():
    assert find_bounds([]) == []
    assert find_bounds([
        {'shows': [{'boundingBox': ['a', 'b']}]}
    ]) == [['a', 'b']]
    assert find_bounds([
        {'shows': [{'boundingBox': ['a', 'b']}]},
        {'shows': [{'boundingBox': ['c', 'd']}]}
    ]) == [['a', 'b'], ['c', 'd']]
    assert find_bounds([
        {'shows': [{'boundingBox': ['a', 'b']}]},
        {'shows': [{'boundingBox': ['c', 'd']}]},
        {'shows': [{'boundingBox': ['a', 'd']}]},
    ]) == [['a', 'b'], ['c', 'd'], ['a', 'd']]


def test_interactable_object_config_create_instance_random_material():
    config = InteractableObjectConfig(
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'ball'
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3}

    assert len(instance['materials']) > 0
    assert instance['materials'][0] in materials.ALL_MATERIAL_STRINGS


def test_interactable_object_config_create_instance_random_position():
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/BlackPlastic',
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'ball'
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/BlackPlastic']
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3}

    assert -3.5 <= instance['shows'][0]['position']['x'] <= 3.5
    assert instance['shows'][0]['position']['y'] == 0
    assert -3.5 <= instance['shows'][0]['position']['z'] <= 3.5


def test_interactable_object_config_create_instance_random_rotation():
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/BlackPlastic',
        position=VectorFloatConfig(1, 0, 2),
        scale=3,
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'ball'
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/BlackPlastic']
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 2}
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3}

    assert instance['shows'][0]['rotation']['x'] == 0
    assert instance['shows'][0]['rotation']['y'] in [
        0, 45, 90, 135, 180, 225, 270, 315
    ]
    assert instance['shows'][0]['rotation']['z'] == 0


def test_interactable_object_config_create_instance_random_scale():
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Wood/DarkWoodSmooth2',
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'ball'
    assert instance['materials'] == ['AI2-THOR/Materials/Wood/DarkWoodSmooth2']
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_config_create_instance_random_shape():
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['materials'] == [
        'AI2-THOR/Materials/Metals/BrushedAluminum_Blue']
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3}

    assert instance['type'] in base_objects.FULL_TYPE_LIST


def test_interactable_object_config_create_instance_specific():
    config = InteractableObjectConfig(
        material='UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1',  # noqa
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'ball'
    assert instance['materials'] == [
        'UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1']  # noqa
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3}


def test_interactable_object_config_create_instance_specific_invalid_shape_material():  # noqa
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Fabrics/Carpet2',
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='ball'
    )
    with pytest.raises(ILEException):
        config.create_instance(
            {'x': 10, 'y': 3, 'z': 10},
            {'position': {'x': 0, 'y': 0, 'z': 0},
             'rotation': {'x': 0, 'y': 0, 'z': 0}},
            []
        )


def test_interactable_object_config_create_instance_specific_list():
    config = InteractableObjectConfig(
        material=[
            'UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1',  # noqa
            'UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1'],  # noqa
        position=[VectorFloatConfig(1, 0, 2), VectorFloatConfig(-1, 0, -2)],
        rotation=[VectorFloatConfig(0, 90, 0), VectorFloatConfig(0, 180, 0)],
        scale=[3, VectorFloatConfig(3.25, 3.5, 3.75)],
        shape=['ball', 'block_blank_wood_cube']
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] in ['ball', 'block_blank_wood_cube']
    assert instance['materials'] in [
        ['UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1'],  # noqa
        ['UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1']  # noqa
    ]
    assert (
        instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 2} or
        instance['shows'][0]['position'] == {'x': -1, 'y': 0, 'z': -2}
    )
    assert (
        instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0} or
        instance['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    )
    assert (
        instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3} or
        instance['shows'][0]['scale'] == {'x': 3.25, 'y': 3.5, 'z': 3.75}
    )


def test_interactable_object_config_create_keyword_location_front():
    klc = KeywordLocationConfig(
        KeywordLocation.FRONT_OF_PERFORMER)
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Metals/WhiteMetal',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'ball'
    assert instance['materials'] == ['AI2-THOR/Materials/Metals/WhiteMetal']
    assert instance['shows'][0]['position']['x'] == 0
    assert instance['shows'][0]['position']['y'] == 0.5
    assert instance['shows'][0]['position']['z'] > 0

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_config_create_keyword_location_back():
    klc = KeywordLocationConfig(
        KeywordLocation.BACK_OF_PERFORMER)
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Metals/GenericStainlessSteel',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'ball'
    assert instance['materials'] == [
        'AI2-THOR/Materials/Metals/GenericStainlessSteel']
    assert -5 < instance['shows'][0]['position']['x'] < 5
    assert instance['shows'][0]['position']['y'] == 0.5
    assert instance['shows'][0]['position']['z'] < 0

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_config_create_keyword_location_between():
    rel_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        position=VectorFloatConfig(4, 0, 2),
        scale=1,
        shape='ball',
        labels="rel_label"
    )
    rel_config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    klc = KeywordLocationConfig(
        KeywordLocation.BETWEEN_PERFORMER_OBJECT,
        relative_object_label="rel_label")
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'ball'
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert 0 < instance['shows'][0]['position']['x'] < 4
    assert instance['shows'][0]['position']['y'] == 0.5
    assert 0 < instance['shows'][0]['position']['z'] < 2

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_config_create_keyword_location_behind():
    rel_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        position=VectorFloatConfig(0, 0, 2),
        scale=1,
        shape='ball',
        labels="rel_label"
    )
    rel_config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    klc = KeywordLocationConfig(
        KeywordLocation.BEHIND_OBJECT_FROM_PERFORMER,
        relative_object_label="rel_label")
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'ball'
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['x'] == 0
    assert instance['shows'][0]['position']['y'] == 0.5
    assert instance['shows'][0]['position']['z'] > 2

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_config_create_keyword_location_adjacent():
    rel_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        position=VectorFloatConfig(3, 0, 3),
        scale=1,
        shape='ball',
        labels="rel_label"
    )
    rel_config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_OBJECT,
        relative_object_label="rel_label")
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'ball'
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert 1.5 < instance['shows'][0]['position']['x'] < 4.5
    assert instance['shows'][0]['position']['y'] == 0.5
    assert 1.5 < instance['shows'][0]['position']['z'] < 4.5

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_config_create_keyword_location_in():
    chest_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/WhitePlastic',
        position=VectorFloatConfig(-2, 0, -2),
        scale=1,
        shape='chest_3',
        labels="chest_label"
    )
    chest = chest_config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    klc = KeywordLocationConfig(
        KeywordLocation.IN_CONTAINER,
        container_label="chest_label")
    config = InteractableObjectConfig(
        material='Custom/Materials/Black',
        keyword_location=klc,
        scale=1,
        shape='crayon_blue'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'crayon_blue'
    assert instance['shows'][0]['position']['x'] == 0
    assert instance['shows'][0]['position']['z'] == 0
    assert instance['locationParent'] == chest['id']

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_config_create_keyword_location_in_with():
    rel_config = InteractableObjectConfig(
        scale=1,
        shape='crayon_blue',
        labels="rel_label"
    )
    rel_inst = rel_config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    chest_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/WhitePlastic',
        position=VectorFloatConfig(-2, 0, -2),
        scale=1,
        shape='chest_3',
        labels="chest_label"
    )
    chest = chest_config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    klc = KeywordLocationConfig(
        KeywordLocation.IN_CONTAINER_WITH_OBJECT,
        container_label="chest_label",
        relative_object_label="rel_label")
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/WhitePlastic',
        keyword_location=klc,
        scale=1,
        shape='crayon_blue'
    )
    instance = config.create_instance(
        {'x': 10, 'y': 3, 'z': 10},
        {'position': {'x': 0, 'y': 0, 'z': 0},
         'rotation': {'x': 0, 'y': 0, 'z': 0}},
        []
    )
    assert instance['type'] == 'crayon_blue'
    assert instance['shows'][0]['position']['x'] == -0.005
    assert math.isclose(instance['shows'][0]['position']['y'], 0.035)
    assert instance['shows'][0]['position']['z'] == 0
    assert instance['locationParent'] == chest['id']
    assert rel_inst['locationParent'] == chest['id']

    assert rel_inst['shows'][0]['position']['x'] == 0.005
    assert math.isclose(rel_inst['shows'][0]['position']['y'], 0.035)
    assert rel_inst['shows'][0]['position']['z'] == 0

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
