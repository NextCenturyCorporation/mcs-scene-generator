import math

import pytest
from machine_common_sense.config_manager import Vector3d

from generator import base_objects, materials
from ideal_learning_env import (
    ILEException,
    ILESharedConfiguration,
    InteractableObjectConfig,
    KeywordLocation,
    KeywordLocationConfig,
    ObjectRepository,
    VectorFloatConfig,
)
from ideal_learning_env.interactable_object_service import (
    InteractableObjectCreationService,
)
from ideal_learning_env.object_services import DEBUG_FINAL_POSITION_KEY

from .ile_helper import prior_scene, prior_scene_custom_size


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()
    ILESharedConfiguration.get_instance().set_excluded_shapes([])

    # Run test
    yield

    # Cleanup
    ObjectRepository.get_instance().clear()
    ILESharedConfiguration.get_instance().set_excluded_shapes([])


def test_interactable_object_service_create_instance_random_material():
    config = InteractableObjectConfig(
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='ball',
    )
    srv = InteractableObjectCreationService()

    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.material
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 1.5, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3}

    assert len(instance['materials']) > 0
    assert (
        instance['materials'][0] in materials.ALL_UNRESTRICTED_MATERIAL_STRINGS
    )
    assert instance['materials'][0] == reconciled.material


def test_interactable_object_service_create_instance_random_position():
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/BlackPlastic',
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='ball'
    )
    srv = InteractableObjectCreationService()

    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.position
    assert -3.5 <= reconciled.position.x <= 3.5
    assert reconciled.position.y == 0
    assert -3.5 <= reconciled.position.z <= 3.5


def test_interactable_object_service_create_instance_random_rotation():
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/BlackPlastic',
        position=VectorFloatConfig(1, 0, 2),
        scale=3,
        shape='ball'
    )
    srv = InteractableObjectCreationService()

    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.rotation is not None
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/BlackPlastic']
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 1.5, 'z': 2}
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3}

    assert instance['shows'][0]['rotation']['x'] == 0
    assert instance['shows'][0]['rotation']['y'] in [
        0, 45, 90, 135, 180, 225, 270, 315
    ]
    assert instance['shows'][0]['rotation']['z'] == 0


def test_interactable_object_service_create_instance_random_scale():
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Wood/DarkWoodSmooth2',
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        shape='ball'
    )
    srv = InteractableObjectCreationService()

    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.scale
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['materials'] == ['AI2-THOR/Materials/Wood/DarkWoodSmooth2']
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 0.5, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_instance_random_shape():
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.shape
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['materials'] == [
        'AI2-THOR/Materials/Metals/BrushedAluminum_Blue']
    assert instance['shows'][0]['position']['x'] == 1
    assert instance['shows'][0]['position']['z'] == 2
    assert instance['shows'][0]['rotation'] == {
        'x': 0,
        'y': 90 + instance['debug']['originalRotation']['y'],
        'z': 0
    }

    assert instance['shows'][0]['scale']['x'] == 3
    assert instance['shows'][0]['scale']['z'] == 3

    assert instance['type'] in base_objects.FULL_TYPE_LIST


def test_interactable_object_service_create_instance_random_shape_excluded():
    ILESharedConfiguration.get_instance().set_excluded_shapes(['ball'])
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
        position=VectorFloatConfig(5.1, 0, 5.2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene_custom_size(25, 25)
    reconciled = srv.reconcile(scene, config)
    assert reconciled.shape
    assert reconciled.shape != 'ball'
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['materials'] == [
        'AI2-THOR/Materials/Metals/BrushedAluminum_Blue']
    assert instance['shows'][0]['position']['x'] == 5.1
    assert instance['shows'][0]['position']['z'] == 5.2
    assert instance['shows'][0]['rotation'] == {
        'x': 0,
        'y': 90 + instance['debug']['originalRotation']['y'],
        'z': 0
    }

    assert instance['shows'][0]['scale']['x'] == 3
    assert instance['shows'][0]['scale']['z'] == 3

    assert instance['type'] in base_objects.FULL_TYPE_LIST
    # The type/shape "ball" is an excluded type
    assert instance['type'] != 'ball'


def test_interactable_object_service_create_instance_specific():
    config = InteractableObjectConfig(
        material='UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1',  # noqa
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='ball'
    )

    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['materials'] == [
        'UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1']  # noqa
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 1.5, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3}


def test_interactable_object_service_create_instance_locked():
    config = InteractableObjectConfig(
        shape='chest_4',
        locked=True
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.position
    assert reconciled.rotation
    assert reconciled.scale
    assert reconciled.material
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    srv._on_valid_instances(scene, reconciled, [instance], 'objects')
    assert instance['type'] == 'chest_4'
    assert instance['locked']


def test_interactable_object_service_create_instance_locked_unlockable():
    config = InteractableObjectConfig(
        shape='ball',
        locked=True
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.position
    assert reconciled.rotation
    assert reconciled.scale
    assert reconciled.material
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    srv._on_valid_instances(scene, reconciled, [instance], 'objects')
    assert instance['type'] == 'ball'
    assert instance.get('locked') is None


def test_interactable_object_service_create_instance_specific_excluded():
    ILESharedConfiguration.get_instance().set_excluded_shapes(['ball'])
    config = InteractableObjectConfig(
        material='UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1',  # noqa
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=0.6,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.shape
    assert reconciled.shape == 'ball'
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    # The type/shape "ball" is excluded , but can still be configured manually
    assert instance['type'] == 'ball'
    assert instance['materials'] == [
        'UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1']  # noqa
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 0.3, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 0.6, 'y': 0.6, 'z': 0.6}


def test_interactable_object_service_create_instance_specific_invalid_shape_material():  # noqa
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Fabrics/Carpet2',
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='ball'
    )
    with pytest.raises(ILEException):
        srv = InteractableObjectCreationService()
        scene = prior_scene()
        reconciled = srv.reconcile(scene, config)
        srv.create_feature_from_specific_values(
            scene=scene, reconciled=reconciled, source_template=config)


def test_interactable_object_service_create_instance_specific_list():
    config = InteractableObjectConfig(
        material=[
            'UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1',  # noqa
            'UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1'],  # noqa
        position=[VectorFloatConfig(1, 0, 2), VectorFloatConfig(-1, 0, -2)],
        rotation=[VectorFloatConfig(0, 90, 0), VectorFloatConfig(0, 180, 0)],
        scale=[3, VectorFloatConfig(3.25, 3.5, 3.75)],
        shape=['ball', 'block_blank_wood_cube']
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.shape in ['ball', 'block_blank_wood_cube']
    assert reconciled.material in [
            'UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1',  # noqa
            'UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1']  # noqa
    assert reconciled.position in [Vector3d(
        x=1, y=0, z=2), Vector3d(x=-1, y=0, z=-2)]
    assert reconciled.rotation in [
        Vector3d(x=0, y=90, z=0),
        Vector3d(x=0, y=180, z=0)]
    assert reconciled.scale in [
        Vector3d(x=3, y=3, z=3),
        Vector3d(x=3.25, y=3.5, z=3.75)]
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] in ['ball', 'block_blank_wood_cube']
    assert instance['materials'] in [
        ['UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1'],  # noqa
        ['UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1']  # noqa
    ]
    assert instance['shows'][0]['position']['x'] in [1, -1]
    assert pytest.approx(instance['shows'][0]['position']['y']) in [
        0, 1.5, 1.75, 0.15, 0.175]
    assert instance['shows'][0]['position']['z'] in [2, -2]
    assert (
        instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0} or
        instance['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    )
    assert (
        instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3} or
        instance['shows'][0]['scale'] == {'x': 3.25, 'y': 3.5, 'z': 3.75}
    )


def test_interactable_object_service_create_keyword_location_random():
    klc = KeywordLocationConfig(KeywordLocation.RANDOM)
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Metals/WhiteMetal',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert not instance['debug'].get('positionedBy')
    assert instance['materials'] == ['AI2-THOR/Materials/Metals/WhiteMetal']
    assert -5 < instance['shows'][0]['position']['x'] < 5
    assert instance['shows'][0]['position']['y'] == 0.5
    assert -5 < instance['shows'][0]['position']['z'] < 5
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_location_front():
    klc = KeywordLocationConfig(
        KeywordLocation.FRONT_OF_PERFORMER)
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Metals/WhiteMetal',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == ['AI2-THOR/Materials/Metals/WhiteMetal']
    assert instance['shows'][0]['position']['x'] == 0
    assert instance['shows'][0]['position']['y'] == 0.5
    assert instance['shows'][0]['position']['z'] > 0

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_location_back():
    klc = KeywordLocationConfig(
        KeywordLocation.BACK_OF_PERFORMER)
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Metals/GenericStainlessSteel',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Metals/GenericStainlessSteel']
    assert -5 < instance['shows'][0]['position']['x'] < 5
    assert instance['shows'][0]['position']['y'] == 0.5
    assert instance['shows'][0]['position']['z'] < 0

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_location_between():
    rel_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        position=VectorFloatConfig(4, 0, 2),
        scale=1,
        shape='ball',
        labels="rel_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    relative_instance, reconciled = srv.add_to_scene(scene, rel_config, [])
    relative_instance = relative_instance[0]

    klc = KeywordLocationConfig(
        KeywordLocation.BETWEEN_PERFORMER_OBJECT,
        relative_object_label="rel_label")
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert 0 < instance['shows'][0]['position']['x'] < 4
    assert instance['shows'][0]['position']['y'] == 0.5
    assert 0 < instance['shows'][0]['position']['z'] < 2

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert relative_instance['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_behind():
    rel_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        position=VectorFloatConfig(0, 0, 2),
        scale=1,
        shape='ball',
        labels="rel_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    rel_insts, _ = srv.add_to_scene(scene, rel_config, [])
    relative_instance = rel_insts[0]
    klc = KeywordLocationConfig(
        KeywordLocation.BEHIND_OBJECT_FROM_PERFORMER,
        relative_object_label="rel_label")
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['x'] == 0
    assert instance['shows'][0]['position']['y'] == 0.5
    assert instance['shows'][0]['position']['z'] > 2

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert relative_instance['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_adjacent():
    rel_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        position=VectorFloatConfig(3, 0, 3),
        scale=1,
        shape='ball',
        labels="rel_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    rel_insts, _ = srv.add_to_scene(scene, rel_config, [])
    relative_instance = rel_insts[0]
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_OBJECT,
        relative_object_label="rel_label")
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert 1.5 < instance['shows'][0]['position']['x'] < 4.5
    assert instance['shows'][0]['position']['y'] == 0.5
    assert 1.5 < instance['shows'][0]['position']['z'] < 4.5

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert relative_instance['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_in():
    chest_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/WhitePlastic',
        position=VectorFloatConfig(-2, 0, -2),
        scale=1,
        shape='chest_3',
        labels="chest_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    chest, _ = srv.add_to_scene(scene, chest_config, [])
    chest = chest[0]
    klc = KeywordLocationConfig(
        KeywordLocation.IN_CONTAINER,
        container_label="chest_label")
    config = InteractableObjectConfig(
        material='Custom/Materials/Black',
        keyword_location=klc,
        scale=1,
        shape='crayon_blue'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'crayon_blue'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['shows'][0]['position']['x'] == 0
    assert instance['shows'][0]['position']['z'] == 0
    assert instance['locationParent'] == chest['id']

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert chest['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_in_with():
    rel_config = InteractableObjectConfig(
        scale=1,
        shape='crayon_blue',
        labels="rel_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    rel_inst, _ = srv.add_to_scene(scene, rel_config, [])
    rel_inst = rel_inst[0]
    chest_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/WhitePlastic',
        position=VectorFloatConfig(-2, 0, -2),
        scale=1,
        shape='chest_3',
        labels="chest_label"
    )
    srv = InteractableObjectCreationService()
    chest, _ = srv.add_to_scene(scene, chest_config, [])
    chest = chest[0]
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
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'crayon_blue'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['shows'][0]['position']['x'] == -0.005
    assert math.isclose(instance['shows'][0]['position']['y'], 0.035)
    assert instance['shows'][0]['position']['z'] == 0
    assert instance['locationParent'] == chest['id']
    assert rel_inst['locationParent'] == chest['id']

    assert rel_inst['shows'][0]['position']['x'] == 0.005
    assert math.isclose(rel_inst['shows'][0]['position']['y'], 0.035)
    assert rel_inst['shows'][0]['position']['z'] == 0

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert rel_inst['debug']['positionedBy']
    assert rel_inst['debug'][DEBUG_FINAL_POSITION_KEY]
    assert chest['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_occlude():
    rel_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        position=VectorFloatConfig(4, 0, 2),
        scale=1,
        shape='ball',
        labels="rel_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    relative_instance, _ = srv.add_to_scene(scene, rel_config, [])
    relative_instance = relative_instance[0]
    klc = KeywordLocationConfig(
        KeywordLocation.OCCLUDE_OBJECT,
        relative_object_label="rel_label")
    config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        keyword_location=klc,
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert 0 < instance['shows'][0]['position']['x'] < 4
    assert instance['shows'][0]['position']['y'] == 0.5
    assert 0 < instance['shows'][0]['position']['z'] < 2

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert relative_instance['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_on():
    chest_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/WhitePlastic',
        position=VectorFloatConfig(-2, 0, -2),
        scale=1,
        shape='chest_3',
        labels="chest_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    srv.add_to_scene(scene, chest_config, [])
    klc = KeywordLocationConfig(
        KeywordLocation.ON_OBJECT,
        relative_object_label="chest_label")
    config = InteractableObjectConfig(
        material='Custom/Materials/Black',
        keyword_location=klc,
        scale=1,
        shape='crayon_blue'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'crayon_blue'
    assert -2.23 < instance['shows'][0]['position']['x'] < -1.77
    assert -2.23 < instance['shows'][0]['position']['z'] < -1.77
    assert instance['shows'][0]['position']['y'] == 0.265
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_location_on_center():
    chest_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/WhitePlastic',
        position=VectorFloatConfig(-2, 0, -2),
        scale=1,
        shape='chest_3',
        labels="chest_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    srv.add_to_scene(scene, chest_config, [])
    klc = KeywordLocationConfig(
        KeywordLocation.ON_OBJECT_CENTERED,
        relative_object_label="chest_label")
    config = InteractableObjectConfig(
        material='Custom/Materials/Black',
        keyword_location=klc,
        scale=1,
        shape='crayon_blue'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'crayon_blue'
    assert instance['shows'][0]['position']['x'] == -2
    assert instance['shows'][0]['position']['z'] == -2
    assert instance['shows'][0]['position']['y'] == 0.265
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
