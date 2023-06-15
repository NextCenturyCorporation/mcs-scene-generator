import math

import pytest
from machine_common_sense.config_manager import Vector3d

from generator import base_objects, instances, materials, tools
from ideal_learning_env import (
    ILEException,
    ILESharedConfiguration,
    InstanceDefinitionLocationTuple,
    InteractableObjectConfig,
    KeywordLocation,
    KeywordLocationConfig,
    MinMaxFloat,
    ObjectRepository,
    VectorFloatConfig,
    VectorIntConfig
)
from ideal_learning_env.interactable_object_service import (
    InteractableObjectCreationService,
    TargetCreationService,
    ToolConfig,
    ToolCreationService
)
from ideal_learning_env.object_services import DEBUG_FINAL_POSITION_KEY

from .ile_helper import (
    prior_scene,
    prior_scene_custom_size,
    prior_scene_with_target
)


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()
    # Exclude shapes that will automatically generate additional objects.
    ILESharedConfiguration.get_instance().set_excluded_shapes(
        ['lid', 'separate_container']
    )

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


def test_interactable_object_service_create_instance_rotate_x_cylinder():
    config = InteractableObjectConfig(
        position=VectorFloatConfig(1, 0, 2),
        scale=3,
        shape='cylinder',
        rotate_cylinders=True
    )
    srv = InteractableObjectCreationService()

    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.material
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'cylinder'
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 1.5, 'z': 2}
    assert instance['shows'][0]['rotation']['x'] == 90
    assert instance['shows'][0]['rotation']['y'] in [
        0, 45, 90, 135, 180, 225, 270, 315
    ]
    assert instance['shows'][0]['rotation']['z'] == 0
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 1.5, 'z': 3}

    assert len(instance['materials']) > 0
    assert (
        instance['materials'][0] in materials.ALL_UNRESTRICTED_MATERIAL_STRINGS
    )
    assert instance['materials'][0] == reconciled.material


def test_interactable_object_service_create_instance_rotate_x_cylinder_override():  # noqa: E501
    config = InteractableObjectConfig(
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='cylinder',
        rotate_cylinders=True
    )
    srv = InteractableObjectCreationService()

    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    assert reconciled.material
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'cylinder'
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 1.5, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 90, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 1.5, 'z': 3}

    assert len(instance['materials']) > 0
    assert (
        instance['materials'][0] in materials.ALL_UNRESTRICTED_MATERIAL_STRINGS
    )
    assert instance['materials'][0] == reconciled.material


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


def test_interactable_object_service_create_instance_with_dimensions():
    config = InteractableObjectConfig(
        dimensions=VectorFloatConfig(0.1, 0.33, 0.5),
        shape='block_blank_wood_cube'
    )

    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert instance['type'] == 'block_blank_wood_cube'
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 3.3, 'z': 5}
    assert instance['debug']['dimensions'] == {'x': 0.1, 'y': 0.33, 'z': 0.5}


def test_interactable_object_service_create_instance_with_one_dimension():
    config = InteractableObjectConfig(
        dimensions=VectorFloatConfig(0, 0.33, 0),
        shape='block_blank_wood_cube'
    )

    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert instance['type'] == 'block_blank_wood_cube'
    assert instance['shows'][0]['scale'] == {'x': 3.3, 'y': 3.3, 'z': 3.3}
    assert instance['debug']['dimensions'] == {'x': 0.33, 'y': 0.33, 'z': 0.33}


def test_interactable_object_service_create_instance_with_sideways_dimension():
    config = InteractableObjectConfig(
        dimensions=VectorFloatConfig(0.1, 0.33, 0.5),
        shape='trolley_1'
    )

    srv = InteractableObjectCreationService()
    scene = prior_scene()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert instance['type'] == 'trolley_1'
    assert instance['shows'][0]['scale'] == pytest.approx(
        {'x': 3.125, 'y': 1.65, 'z': 0.434783}
    )
    assert instance['debug']['dimensions'] == {'x': 0.1, 'y': 0.33, 'z': 0.5}


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
        position=VectorFloatConfig(2, 0, 1),
        rotation=VectorFloatConfig(0, 0, 0),
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
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
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
    assert instance['shows'][0]['position']['y'] == 0.5
    assert (
        instance['shows'][0]['position']['x'] == pytest.approx(3.1) and
        instance['shows'][0]['position']['z'] == pytest.approx(1.0)
    ) or (
        instance['shows'][0]['position']['x'] == pytest.approx(0.9) and
        instance['shows'][0]['position']['z'] == pytest.approx(1.0)
    ) or (
        instance['shows'][0]['position']['x'] == pytest.approx(2.0) and
        instance['shows'][0]['position']['z'] == pytest.approx(2.1)
    ) or (
        instance['shows'][0]['position']['x'] == pytest.approx(2.0) and
        instance['shows'][0]['position']['z'] == pytest.approx(-0.1)
    )
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert relative_instance['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_adjacent_with_rotation():  # noqa: E501
    rel_config = InteractableObjectConfig(
        position=VectorFloatConfig(2, 0, 1),
        rotation=VectorFloatConfig(0, 45, 0),
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
        relative_object_label="rel_label"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        rotation=VectorFloatConfig(0, 45, 0),
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['shows'][0]['position']['y'] == 0.5
    assert (
        instance['shows'][0]['position']['x'] == pytest.approx(3.514214) and
        instance['shows'][0]['position']['z'] == pytest.approx(1.0)
    ) or (
        instance['shows'][0]['position']['x'] == pytest.approx(0.485786) and
        instance['shows'][0]['position']['z'] == pytest.approx(1.0)
    ) or (
        instance['shows'][0]['position']['x'] == pytest.approx(2.0) and
        instance['shows'][0]['position']['z'] == pytest.approx(2.514214)
    ) or (
        instance['shows'][0]['position']['x'] == pytest.approx(2.0) and
        instance['shows'][0]['position']['z'] == pytest.approx(-0.514214)
    )
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 45, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert relative_instance['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_adjacent_with_distance():  # noqa: E501
    rel_config = InteractableObjectConfig(
        position=VectorFloatConfig(2, 0, 1),
        rotation=VectorFloatConfig(0, 0, 0),
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
        adjacent_distance=VectorFloatConfig(-3, 0, -4),
        relative_object_label="rel_label"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['shows'][0]['position']['y'] == 0.5
    assert (
        instance['shows'][0]['position']['x'] == pytest.approx(-2.0) and
        instance['shows'][0]['position']['z'] == pytest.approx(-4.0)
    )
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert relative_instance['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_adjacent_with_distance_list():  # noqa: E501
    rel_config = InteractableObjectConfig(
        position=VectorFloatConfig(2, 0, 1),
        rotation=VectorFloatConfig(0, 0, 0),
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
        adjacent_distance=[
            VectorFloatConfig(-3, 0, 0),
            VectorFloatConfig(0, 0, -4)
        ],
        relative_object_label="rel_label"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['shows'][0]['position']['y'] == 0.5
    assert (
        instance['shows'][0]['position']['x'] == pytest.approx(-2.0) and
        instance['shows'][0]['position']['z'] == pytest.approx(1.0)
    ) or (
        instance['shows'][0]['position']['x'] == pytest.approx(2.0) and
        instance['shows'][0]['position']['z'] == pytest.approx(-4.0)
    )
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert relative_instance['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_adjacent_failed():
    rel_config = InteractableObjectConfig(
        position=VectorFloatConfig(2, 0, 1),
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball',
        labels="rel_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    srv.add_to_scene(scene, rel_config, [])
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_OBJECT,
        adjacent_distance=VectorFloatConfig(10, 0, 10),
        relative_object_label="rel_label"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    with pytest.raises(ILEException):
        srv.create_feature_from_specific_values(
            scene=scene,
            reconciled=reconciled,
            source_template=config
        )


def test_interactable_object_service_create_keyword_adjacent_corner():
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER)
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball'
    )
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['y'] == 0.5
    x_pos = instance['shows'][0]['position']['x']
    z_pos = instance['shows'][0]['position']['z']
    assert (
        abs(x_pos) == pytest.approx(4.45, 0.1) and
        abs(z_pos) == pytest.approx(4.45, 0.1)
    )
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_adjacent_corner_with_label():  # noqa: E501
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER, relative_object_label="back_right")
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball'
    )
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['y'] == 0.5
    x_pos = instance['shows'][0]['position']['x']
    z_pos = instance['shows'][0]['position']['z']
    assert (
        x_pos == pytest.approx(4.45, 0.1) and
        z_pos == pytest.approx(-4.45, 0.1)
    )
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_adjacent_corner_with_label_and_distance():  # noqa: E501
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        relative_object_label="front_right",
        adjacent_distance=VectorFloatConfig(2, 0, 1.5))
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball'
    )
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['y'] == 0.5
    x_pos = instance['shows'][0]['position']['x']
    z_pos = instance['shows'][0]['position']['z']
    assert (
        x_pos == pytest.approx(2.5, 0.1) and
        z_pos == pytest.approx(3.0, 0.1)
    )
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_adjacent_corner_with_distance():  # noqa: E501
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        adjacent_distance=VectorFloatConfig(1.5, 0, 2.0))
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball'
    )
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['y'] == 0.5
    x_pos = instance['shows'][0]['position']['x']
    z_pos = instance['shows'][0]['position']['z']
    assert (
        abs(x_pos) == pytest.approx(3.0, 0.1) and
        abs(z_pos) == pytest.approx(2.5, 0.1)
    )
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_adjacent_corner_with_distance_list():  # noqa: E501
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        adjacent_distance=[
            VectorFloatConfig(3, 0, 0),
            VectorFloatConfig(0, 0, 4)
        ]
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball'
    )
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['y'] == 0.5
    x_pos = instance['shows'][0]['position']['x']
    z_pos = instance['shows'][0]['position']['z']
    assert ((
        abs(x_pos) == pytest.approx(1.5, 0.1) and
        abs(z_pos) == pytest.approx(4.5, 0.1)
    ) or
        (
        abs(x_pos) == pytest.approx(4.5, 0.1) and
        abs(z_pos) == pytest.approx(0.5, 0.1)
    ))
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_adjacent_corner_failed():
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        adjacent_distance=VectorFloatConfig(10, 0, 10),
        relative_object_label="back_left"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball'
    )
    reconciled = srv.reconcile(scene, config)
    with pytest.raises(ILEException):
        srv.create_feature_from_specific_values(
            scene=scene,
            reconciled=reconciled,
            source_template=config
        )


def test_interactable_object_service_surrounded_by_lava():
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        adjacent_distance=VectorFloatConfig(2, 0, 2),
        relative_object_label="back_left"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=0.5,
        shape='ball',
        surrounded_by_lava=True,
        surrounding_lava_size=2
    )
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['y'] == 0.25
    x_pos = instance['shows'][0]['position']['x']
    z_pos = instance['shows'][0]['position']['z']
    assert (
        x_pos == pytest.approx(-3.0, 0.1) and
        z_pos == pytest.approx(-3.0, 0.1)
    )

    assert instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    # Make sure lava isn't officially added until add_to_scene is called
    assert not scene.lava
    assert instance['debug']['surroundingLava']
    assert len(instance['debug']['surroundingLava']) == 24
    for square in instance['debug']['surroundingLava']:
        assert square['x'] in [-5, -4, -3, -2, -1]
        assert square['z'] in [-5, -4, -3, -2, -1]
        assert not (square['x'] == -3 and square['z'] == -3)

    instances, _ = srv.add_to_scene(
        scene=scene, source_template=config, bounds=[])

    instance = instances[0]
    assert scene.lava
    assert len(scene.lava) == 24
    # check that 'surroundingLava' array was deleted
    # after lava was placed
    assert 'surroundingLava' not in instance['debug']

    for square in scene.lava:
        assert square.x in [-5, -4, -3, -2, -1]
        assert square.z in [-5, -4, -3, -2, -1]
        assert not (square.x == -3 and square.z == -3)


def test_interactable_object_service_larger_object_surrounded_by_lava():
    srv = InteractableObjectCreationService()
    scene = prior_scene()

    # move performer out of the way of object and lava so there are no errors
    scene.performer_start.position.x = 3
    scene.performer_start.position.z = 3

    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        adjacent_distance=VectorFloatConfig(3, 0, 3),
        relative_object_label="back_left"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=2.0,
        shape='ball',
        surrounded_by_lava=True,
        surrounding_lava_size=1
    )
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['y'] == 1.0
    x_pos = instance['shows'][0]['position']['x']
    z_pos = instance['shows'][0]['position']['z']

    assert (
        x_pos == pytest.approx(-1.0, 0.1) and
        z_pos == pytest.approx(-1.0, 0.1)
    )

    assert instance['shows'][0]['scale'] == {'x': 2.0, 'y': 2.0, 'z': 2.0}

    assert not scene.lava
    assert instance['debug']['surroundingLava']
    assert len(instance['debug']['surroundingLava']) == 16
    for square in instance['debug']['surroundingLava']:
        assert square['x'] in [-3, -2, -1, 0, 1]
        assert square['z'] in [-3, -2, -1, 0, 1]
        assert not (square['x'] == -2 and square['z'] == -2)
        assert not (square['x'] == -2 and square['z'] == -1)
        assert not (square['x'] == -2 and square['z'] == 0)
        assert not (square['x'] == -1 and square['z'] == -2)
        assert not (square['x'] == -1 and square['z'] == -1)
        assert not (square['x'] == -1 and square['z'] == 0)
        assert not (square['x'] == 0 and square['z'] == -2)
        assert not (square['x'] == 0 and square['z'] == -1)
        assert not (square['x'] == 0 and square['z'] == 0)

    instances, _ = srv.add_to_scene(
        scene=scene, source_template=config, bounds=[])

    instance = instances[0]
    assert scene.lava
    assert len(scene.lava) == 16
    assert 'surroundingLava' not in instance['debug']

    for square in scene.lava:
        assert square.x in [-3, -2, -1, 0, 1]
        assert square.z in [-3, -2, -1, 0, 1]
        assert not (square.x == -2 and square.z == -2)
        assert not (square.x == -2 and square.z == -1)
        assert not (square.x == -2 and square.z == 0)
        assert not (square.x == -1 and square.z == -2)
        assert not (square.x == -1 and square.z == -1)
        assert not (square.x == -1 and square.z == 0)
        assert not (square.x == 0 and square.z == -2)
        assert not (square.x == 0 and square.z == -1)
        assert not (square.x == 0 and square.z == 0)


def test_interactable_object_service_surrounded_by_lava_fail_perf_start():
    srv = InteractableObjectCreationService()
    scene = prior_scene()

    # should overlap with performer_start, so should fail
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        adjacent_distance=VectorFloatConfig(3, 0, 3),
        relative_object_label="back_left"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=2.0,
        shape='ball',
        surrounded_by_lava=True,
        surrounding_lava_size=1
    )
    reconciled = srv.reconcile(scene, config)

    with pytest.raises(ILEException):
        srv.create_feature_from_specific_values(
            scene=scene,
            reconciled=reconciled,
            source_template=config
        )


def test_interactable_object_service_surrounded_by_lava_fail_object_overlap():
    srv = InteractableObjectCreationService()
    # target will overlap with new keyword object, should throw error
    scene = prior_scene_with_target()

    # move performer out of the way of objects
    scene.performer_start.position.x = 3
    scene.performer_start.position.z = 3

    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        adjacent_distance=VectorFloatConfig(3, 0, 2),
        relative_object_label="front_left"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=2.0,
        shape='ball',
        surrounded_by_lava=True,
        surrounding_lava_size=1
    )
    reconciled = srv.reconcile(scene, config)

    with pytest.raises(ILEException):
        srv.create_feature_from_specific_values(
            scene=scene,
            reconciled=reconciled,
            source_template=config
        )
        srv.add_to_scene(
            scene=scene, source_template=config, bounds=[])


def test_interactable_object_service_surrounded_by_lava_default_lava_size():
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        adjacent_distance=VectorFloatConfig(2, 0, 2),
        relative_object_label="back_left"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=0.5,
        shape='ball',
        surrounded_by_lava=True
    )
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['y'] == 0.25
    x_pos = instance['shows'][0]['position']['x']
    z_pos = instance['shows'][0]['position']['z']
    assert (
        x_pos == pytest.approx(-3.0, 0.1) and
        z_pos == pytest.approx(-3.0, 0.1)
    )

    assert instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    assert not scene.lava
    assert instance['debug']['surroundingLava']
    assert len(instance['debug']['surroundingLava']) == 8
    for square in scene.lava:
        assert square['x'] in [-4, -3, -2]
        assert square['z'] in [-4, -3, -2]
        assert not (square['x'] == -3 and square['z'] == -3)

    instances, _ = srv.add_to_scene(
        scene=scene, source_template=config, bounds=[])

    instance = instances[0]
    assert scene.lava
    assert len(scene.lava) == 8

    assert 'surroundingLava' not in instance['debug']
    for square in scene.lava:
        assert square.x in [-4, -3, -2]
        assert square.z in [-4, -3, -2]
        assert not (square.x == -3 and square.z == -3)


def test_interactable_object_service_surrounded_by_lava_lava_size_list():
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        adjacent_distance=VectorFloatConfig(2, 0, 2),
        relative_object_label="back_left"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=0.5,
        shape='ball',
        surrounded_by_lava=True,
        surrounding_lava_size=[1, 2]
    )
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['y'] == 0.25
    x_pos = instance['shows'][0]['position']['x']
    z_pos = instance['shows'][0]['position']['z']

    assert (
        x_pos == pytest.approx(-3.0, 1) and
        z_pos == pytest.approx(-3.0, 1)
    )

    assert instance['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}

    assert not scene.lava
    assert instance['debug']['surroundingLava']
    assert len(instance['debug']['surroundingLava']) in [8, 24]

    instances, _ = srv.add_to_scene(
        scene=scene, source_template=config, bounds=[])

    instance = instances[0]
    assert scene.lava
    assert len(scene.lava) in [8, 24]
    assert 'surroundingLava' not in instance['debug']


def test_interactable_object_service_surrounded_by_lava_default_false():
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    klc = KeywordLocationConfig(
        KeywordLocation.ADJACENT_TO_CORNER,
        adjacent_distance=VectorFloatConfig(2, 0, 2),
        relative_object_label="back_left"
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        rotation=VectorFloatConfig(0, 0, 0),
        scale=1,
        shape='ball',
        surrounded_by_lava=False
    )
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'ball'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['materials'] == [
        'AI2-THOR/Materials/Plastics/OrangePlastic']
    assert instance['shows'][0]['position']['y'] == 0.5
    x_pos = instance['shows'][0]['position']['x']
    z_pos = instance['shows'][0]['position']['z']
    assert (
        x_pos == pytest.approx(-2.5, 0.1) and
        z_pos == pytest.approx(-2.5, 0.1)
    )

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert not scene.lava
    assert 'surroundingLava' not in instance['debug']

    srv.add_to_scene(
        scene=scene, source_template=config, bounds=[])

    assert not scene.lava


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


def test_interactable_object_service_create_keyword_location_in_placer_ctr():
    container_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Wood/WhiteWood',
        position=VectorFloatConfig(-2, 0, -2),
        scale=1,
        shape='container_asymmetric_01',
        labels="container_label"
    )

    srv = InteractableObjectCreationService()
    scene = prior_scene()
    container, _ = srv.add_to_scene(scene, container_config, [])
    container = container[0]
    klc = KeywordLocationConfig(
        KeywordLocation.IN_CONTAINER,
        container_label="container_label")
    config = InteractableObjectConfig(
        material='Custom/Materials/Black',
        keyword_location=klc,
        scale=1,
        shape='crayon_blue'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)

    container['moves'] = [{
        "stepBegin": 1,
        "stepEnd": 16,
        "vector": {
            "x": 0,
            "y": -0.25,
            "z": 0
        }
    }]
    container['kinematic'] = True
    container['togglePhysics'] = [{"stepBegin": 60}]
    container['debug']['positionedBy'] = "mechanism"

    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)

    assert instance['type'] == 'crayon_blue'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['shows'][0]['position']['x'] == 0
    assert instance['shows'][0]['position']['z'] == 0
    assert instance['locationParent'] == container['id']

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    # make sure object inside container match container physics
    assert instance['moves'] == container['moves']
    assert instance['togglePhysics'] == container['togglePhysics']
    assert instance['kinematic'] == container['kinematic']

    assert container['debug'][DEBUG_FINAL_POSITION_KEY]


def test_interactable_object_service_create_keyword_location_in_dropper_ctr():
    container_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Wood/WhiteWood',
        position=VectorFloatConfig(-2, 0, -2),
        scale=1,
        shape='container_asymmetric_01',
        labels="container_label"
    )

    srv = InteractableObjectCreationService()
    scene = prior_scene()
    container, _ = srv.add_to_scene(scene, container_config, [])
    container = container[0]
    klc = KeywordLocationConfig(
        KeywordLocation.IN_CONTAINER,
        container_label="container_label")
    config = InteractableObjectConfig(
        material='Custom/Materials/Black',
        keyword_location=klc,
        scale=1,
        shape='crayon_blue'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)

    container['kinematic'] = True
    container['togglePhysics'] = [{"stepBegin": 60}]
    container['debug']['positionedBy'] = "mechanism"

    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)

    assert instance['type'] == 'crayon_blue'
    assert instance['debug'][DEBUG_FINAL_POSITION_KEY]
    assert instance['shows'][0]['position']['x'] == 0
    assert instance['shows'][0]['position']['z'] == 0
    assert instance['locationParent'] == container['id']

    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    # don't update physics for cases for objects within containers that
    # are held by non-placers
    assert instance.get('togglePhysics') is None
    assert instance.get('kinematic') is None
    assert instance.get('moves') is None

    assert container['debug'][DEBUG_FINAL_POSITION_KEY]


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
        rotation=VectorIntConfig(0, 0, 0),
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
    assert -2.26 < instance['shows'][0]['position']['z'] < -1.74
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
    assert instance['shows'][0]['position']['x'] == pytest.approx(-2)
    assert instance['shows'][0]['position']['z'] == pytest.approx(-2)
    assert instance['shows'][0]['position']['y'] == 0.265
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_location_relative_to_center():  # noqa: E501
    table_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/WhitePlastic',
        position=VectorFloatConfig(x=-1, y=0, z=-1),
        rotation=VectorFloatConfig(x=0, y=90, z=0),
        scale=1,
        shape='table_1',
        labels="table_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    srv.add_to_scene(scene, table_config, [])
    klc = KeywordLocationConfig(
        KeywordLocation.ON_OBJECT_CENTERED,
        relative_object_label="table_label",
        position_relative_to_start=VectorFloatConfig(x=0, y=None, z=1))

    config = InteractableObjectConfig(
        material='Custom/Materials/WhiteWoodMCS',
        keyword_location=klc,
        scale=1,
        shape='bowl_3'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene, reconciled=reconciled, source_template=config)
    assert instance['type'] == 'bowl_3'
    assert instance['shows'][0]['position']['x'] == pytest.approx(-1.7275)
    assert instance['shows'][0]['position']['z'] == pytest.approx(-1)
    assert instance['shows'][0]['position']['y'] == 0.885
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_location_opposite_x():
    rel_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        position=VectorFloatConfig(4, 0, 2),
        rotation=VectorIntConfig(0, 0, 0),
        scale=1,
        shape='ball',
        labels="rel_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    srv.add_to_scene(scene, rel_config, [])
    klc = KeywordLocationConfig(
        KeywordLocation.OPPOSITE_X,
        relative_object_label="rel_label")
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
    assert instance['shows'][0]['position']['x'] == -4
    assert instance['shows'][0]['position']['y'] == pytest.approx(0.005)
    assert instance['shows'][0]['position']['z'] == 2
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_location_opposite_x_with_rotation():  # noqa: E501
    rel_config = InteractableObjectConfig(
        position=VectorFloatConfig(4, 0, 2),
        rotation=VectorIntConfig(0, 0, 0),
        scale=1,
        shape='ball',
        labels='rel_label'
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    srv.add_to_scene(scene, rel_config, [])
    klc = KeywordLocationConfig(
        KeywordLocation.OPPOSITE_X,
        relative_object_label='rel_label'
    )
    config = InteractableObjectConfig(
        keyword_location=klc,
        rotation=VectorIntConfig(0, 45, 0),
        scale=1,
        shape='block_blank_wood_cube'
    )
    srv = InteractableObjectCreationService()
    reconciled = srv.reconcile(scene, config)
    instance = srv.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert instance['type'] == 'block_blank_wood_cube'
    assert instance['shows'][0]['position']['x'] == -4
    assert instance['shows'][0]['position']['y'] == pytest.approx(0.05)
    assert instance['shows'][0]['position']['z'] == 2
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 45, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_interactable_object_service_create_keyword_location_opposite_z():
    rel_config = InteractableObjectConfig(
        material='AI2-THOR/Materials/Plastics/OrangePlastic',
        position=VectorFloatConfig(4, 0, 2),
        rotation=VectorIntConfig(0, 0, 0),
        scale=1,
        shape='ball',
        labels="rel_label"
    )
    srv = InteractableObjectCreationService()
    scene = prior_scene()
    srv.add_to_scene(scene, rel_config, [])
    klc = KeywordLocationConfig(
        KeywordLocation.OPPOSITE_Z,
        relative_object_label="rel_label")
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
    assert instance['shows'][0]['position']['x'] == 4
    assert instance['shows'][0]['position']['y'] == pytest.approx(0.005)
    assert instance['shows'][0]['position']['z'] == -2
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_target_creation_service():
    config = InteractableObjectConfig(
        labels='test_label',
        position=VectorFloatConfig(1, 0, 2),
        rotation=VectorFloatConfig(0, 90, 0),
        scale=3,
        shape='soccer_ball'
    )
    service = TargetCreationService()
    scene = prior_scene()
    instances, _ = service.add_to_scene(
        scene=scene, source_template=config, bounds=[])
    instance = instances[0]
    assert instance['type'] == 'soccer_ball'
    assert instance['materials'] == []
    assert instance['shows'][0]['position'] == {'x': 1, 'y': 0.33, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert instance['shows'][0]['scale'] == {'x': 3, 'y': 3, 'z': 3}
    assert ObjectRepository.get_instance().has_label('target')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_tool_creation_reconcile():
    scene = prior_scene()
    srv = ToolCreationService()
    tmp = ToolConfig(1)
    r1: ToolConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert -5 < r1.position.x < 5
    assert r1.position.y == 0
    assert -5 < r1.position.z < 5
    assert 0 <= r1.rotation_y < 360
    assert r1.shape in base_objects.ALL_LARGE_BLOCK_TOOLS

    tmp2 = ToolConfig(
        num=[2, 3],
        position=VectorFloatConfig([3, 2], MinMaxFloat(0, 2), 3),
        rotation_y=[90, 180],
        shape=['tool_rect_1_00_x_9_00', 'tool_hooked_0_50_x_4_00']
    )
    srv = ToolCreationService()
    r2: ToolConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position.x in [2, 3]
    assert 0 <= r2.position.y <= 2
    assert r2.position.z == 3
    assert r2.rotation_y in [90, 180]
    assert r2.shape in ["tool_rect_1_00_x_9_00", "tool_hooked_0_50_x_4_00"]


def test_tool_creation_reconcile_by_size():
    scene = prior_scene()
    template = ToolConfig(num=1, width=0.75, length=6)
    srv = ToolCreationService()
    r1: ToolConfig = srv.reconcile(scene, template)

    assert r1.num == 1
    assert r1.shape in ['tool_rect_0_75_x_6_00', 'tool_hooked_0_75_x_6_00']

    template2 = ToolConfig(num=1, length=6)
    srv = ToolCreationService()
    r2: ToolConfig = srv.reconcile(scene, template2)

    assert r2.num == 1
    assert r2.shape in [
        'tool_rect_0_50_x_6_00',
        'tool_rect_0_75_x_6_00',
        'tool_rect_1_00_x_6_00',
        'tool_hooked_0_50_x_6_00',
        'tool_hooked_0_75_x_6_00',
        'tool_hooked_1_00_x_6_00']


def test_tool_creation_reconcile_by_size_error():
    scene = prior_scene()
    template = ToolConfig(num=1, width=0.76, length=6)
    srv = ToolCreationService()
    with pytest.raises(ILEException):
        srv.reconcile(scene, template)


def test_tool_create():
    temp = ToolConfig(
        position=VectorFloatConfig(1.1, 1.2, 1.3), rotation_y=34,
        shape='tool_rect_0_75_x_4_00', material=materials.TOOL_MATERIALS[0])
    tool = ToolCreationService().create_feature_from_specific_values(
        prior_scene(), temp, None)

    assert tool
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['materials'] == [materials.TOOL_MATERIALS[0].material]
    show = tool['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 0.15, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 1, 'y': 1, 'z': 1}


def test_tool_create_hooked():
    temp = ToolConfig(
        num=1, width=0.76, length=6,
        position=VectorFloatConfig(1.1, 1.2, 1.3), rotation_y=34,
        shape='tool_hooked_0_75_x_4_00')
    temp.material = materials.TOOL_MATERIALS[1]
    tool = ToolCreationService().create_feature_from_specific_values(
        prior_scene(), temp, None)

    assert tool
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_hooked_0_75_x_4_00'
    show = tool['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 0.15, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 1, 'y': 1, 'z': 1}


def test_tool_create_short():
    temp = ToolConfig(
        position=VectorFloatConfig(1.1, 1.2, 1.3), rotation_y=34,
        shape='tool_rect_0_75_x_1_00', material=materials.TOOL_MATERIALS[0])
    tool = ToolCreationService().create_feature_from_specific_values(
        prior_scene(), temp, None)

    assert tool
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_1_00'
    show = tool['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 0.15, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 1, 'y': 1, 'z': 1}


def test_tool_create_aligned_with_rect_tool():
    config = ToolConfig(
        align_distance=2,
        shape='tool_rect_0_75_x_4_00',
        # Should override configured position and rotation.
        position=VectorFloatConfig(1.1, 1.2, 1.3),
        rotation_y=34
    )
    service = ToolCreationService()
    scene = prior_scene()

    instance_1 = tools.create_tool('tool_rect_0_75_x_6_00', 0, 0, 0)
    assert instance_1['shows'][0]['rotation']['y'] == 0
    assert instance_1['debug'].get('originalRotation', {'y': 0})['y'] == 0
    location_1 = instance_1['shows'][0]
    scene.objects.append(instance_1)
    idl_1 = InstanceDefinitionLocationTuple(instance_1, None, location_1)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_1, 'tool_1')

    config.align_with = 'tool_1'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == 0
    assert reconciled.position.z == -7
    assert reconciled.rotation_y == 0

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {'x': 0, 'y': 0.15, 'z': -7}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    instance_2 = tools.create_tool('tool_rect_0_75_x_6_00', 0, 0, 45)
    location_2 = instance_2['shows'][0]
    scene.objects.append(instance_2)
    idl_2 = InstanceDefinitionLocationTuple(instance_2, None, location_2)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_2, 'tool_2')

    config.align_with = 'tool_2'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == -4.9497
    assert reconciled.position.z == -4.9497
    assert reconciled.rotation_y == 45

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {
        'x': -4.9497,
        'y': 0.15,
        'z': -4.9497
    }
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 45, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    instance_3 = tools.create_tool('tool_rect_0_75_x_6_00', 0, 0, 90)
    location_3 = instance_3['shows'][0]
    scene.objects.append(instance_3)
    idl_3 = InstanceDefinitionLocationTuple(instance_3, None, location_3)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_3, 'tool_3')

    config.align_with = 'tool_3'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == -7
    assert reconciled.position.z == 0
    assert reconciled.rotation_y == 90

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {'x': -7, 'y': 0.15, 'z': 0}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_tool_create_aligned_with_hooked_tool():
    config = ToolConfig(
        align_distance=2,
        shape='tool_rect_0_75_x_4_00',
        # Should override configured position and rotation.
        position=VectorFloatConfig(1.1, 1.2, 1.3),
        rotation_y=34
    )
    service = ToolCreationService()
    scene = prior_scene()

    instance_1 = tools.create_tool('tool_hooked_0_75_x_6_00', 0, 0, 0)
    assert instance_1['shows'][0]['rotation']['y'] == 0
    assert instance_1['debug'].get('originalRotation', {'y': 0})['y'] == 0
    location_1 = instance_1['shows'][0]
    scene.objects.append(instance_1)
    idl_1 = InstanceDefinitionLocationTuple(instance_1, None, location_1)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_1, 'tool_1')

    config.align_with = 'tool_1'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == 0.75
    assert reconciled.position.z == -7
    assert reconciled.rotation_y == 0

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {'x': 0.75, 'y': 0.15, 'z': -7}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    instance_2 = tools.create_tool('tool_hooked_0_75_x_6_00', 0, 0, 45)
    location_2 = instance_2['shows'][0]
    scene.objects.append(instance_2)
    idl_2 = InstanceDefinitionLocationTuple(instance_2, None, location_2)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_2, 'tool_2')

    config.align_with = 'tool_2'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == -4.4194
    assert reconciled.position.z == -5.4801
    assert reconciled.rotation_y == 45

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {
        'x': -4.4194,
        'y': 0.15,
        'z': -5.4801
    }
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 45, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    instance_3 = tools.create_tool('tool_hooked_0_75_x_6_00', 0, 0, 90)
    location_3 = instance_3['shows'][0]
    scene.objects.append(instance_3)
    idl_3 = InstanceDefinitionLocationTuple(instance_3, None, location_3)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_3, 'tool_3')

    config.align_with = 'tool_3'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == -7
    assert reconciled.position.z == -0.75
    assert reconciled.rotation_y == 90

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {'x': -7, 'y': 0.15, 'z': -0.75}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_tool_create_aligned_with_isosceles_tool():
    config = ToolConfig(
        align_distance=2,
        shape='tool_rect_0_75_x_4_00',
        # Should override configured position and rotation.
        position=VectorFloatConfig(1.1, 1.2, 1.3),
        rotation_y=34
    )
    service = ToolCreationService()
    scene = prior_scene()

    instance_1 = tools.create_tool('tool_isosceles_0_75_x_6_00', 0, 0, 0)
    assert instance_1['shows'][0]['rotation']['y'] == 0
    assert instance_1['debug'].get('originalRotation', {'y': 0})['y'] == 0
    location_1 = instance_1['shows'][0]
    scene.objects.append(instance_1)
    idl_1 = InstanceDefinitionLocationTuple(instance_1, None, location_1)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_1, 'tool_1')

    config.align_with = 'tool_1'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == 2.625
    assert reconciled.position.z == -7
    assert reconciled.rotation_y == 0

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {'x': 2.625, 'y': 0.15, 'z': -7}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    instance_2 = tools.create_tool('tool_isosceles_0_75_x_6_00', 0, 0, 45)
    location_2 = instance_2['shows'][0]
    scene.objects.append(instance_2)
    idl_2 = InstanceDefinitionLocationTuple(instance_2, None, location_2)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_2, 'tool_2')

    config.align_with = 'tool_2'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == -3.0936
    assert reconciled.position.z == -6.8059
    assert reconciled.rotation_y == 45

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {
        'x': -3.0936,
        'y': 0.15,
        'z': -6.8059
    }
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 45, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    instance_3 = tools.create_tool('tool_isosceles_0_75_x_6_00', 0, 0, 90)
    location_3 = instance_3['shows'][0]
    scene.objects.append(instance_3)
    idl_3 = InstanceDefinitionLocationTuple(instance_3, None, location_3)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_3, 'tool_3')

    config.align_with = 'tool_3'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == -7
    assert reconciled.position.z == -2.625
    assert reconciled.rotation_y == 90

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {'x': -7, 'y': 0.15, 'z': -2.625}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_tool_create_aligned_with_normal_toy():
    config = ToolConfig(
        align_distance=2,
        shape='tool_rect_0_75_x_4_00',
        # Should override configured position and rotation.
        position=VectorFloatConfig(1.1, 1.2, 1.3),
        rotation_y=34
    )
    service = ToolCreationService()
    scene = prior_scene()
    material_tuple = materials.ORANGE_PLASTIC
    definition = base_objects.create_specific_definition_from_base(
        'ball',
        material_tuple.color,
        [material_tuple.material],
        None,
        1
    )

    location_1 = {
        'position': {'x': 0, 'y': definition.positionY, 'z': 0},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }
    instance_1 = instances.instantiate_object(definition, location_1)
    assert instance_1['shows'][0]['rotation']['y'] == 0
    assert instance_1['debug']['originalRotation']['y'] == 0
    scene.objects.append(instance_1)
    idl_1 = InstanceDefinitionLocationTuple(instance_1, definition, location_1)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_1, 'toy_1')

    config.align_with = 'toy_1'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == -4.5
    assert reconciled.position.z == 0
    assert reconciled.rotation_y == 90

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {'x': -4.5, 'y': 0.15, 'z': 0}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    location_2 = {
        'position': {'x': 0, 'y': definition.positionY, 'z': 0},
        'rotation': {'x': 0, 'y': 45, 'z': 0}
    }
    instance_2 = instances.instantiate_object(definition, location_2)
    scene.objects.append(instance_2)
    idl_2 = InstanceDefinitionLocationTuple(instance_2, definition, location_2)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_2, 'toy_2')

    config.align_with = 'toy_2'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == -3.182
    assert reconciled.position.z == 3.182
    assert reconciled.rotation_y == 135

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {
        'x': -3.182,
        'y': 0.15,
        'z': 3.182
    }
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 135, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    location_3 = {
        'position': {'x': 0, 'y': definition.positionY, 'z': 0},
        'rotation': {'x': 0, 'y': 90, 'z': 0}
    }
    instance_3 = instances.instantiate_object(definition, location_3)
    scene.objects.append(instance_3)
    idl_3 = InstanceDefinitionLocationTuple(instance_3, definition, location_3)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_3, 'toy_3')

    config.align_with = 'toy_3'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == 0
    assert reconciled.position.z == 4.5
    assert reconciled.rotation_y == 180

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {'x': 0, 'y': 0.15, 'z': 4.5}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_tool_create_aligned_with_sideways_toy():
    config = ToolConfig(
        align_distance=2,
        shape='tool_rect_0_75_x_4_00',
        # Should override configured position and rotation.
        position=VectorFloatConfig(1.1, 1.2, 1.3),
        rotation_y=34
    )
    service = ToolCreationService()
    scene = prior_scene()
    material_tuple = materials.ORANGE_PLASTIC
    definition = base_objects.create_specific_definition_from_base(
        'car_1',
        material_tuple.color,
        [material_tuple.material],
        None,
        1
    )

    location_1 = {
        'position': {'x': 0, 'y': definition.positionY, 'z': 0},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }
    instance_1 = instances.instantiate_object(definition, location_1)
    assert instance_1['shows'][0]['rotation']['y'] == 90
    assert instance_1['debug']['originalRotation']['y'] == 90
    scene.objects.append(instance_1)
    idl_1 = InstanceDefinitionLocationTuple(instance_1, definition, location_1)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_1, 'toy_1')

    config.align_with = 'toy_1'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == -4.0375
    assert reconciled.position.z == 0
    assert reconciled.rotation_y == 90

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {'x': -4.0375, 'y': 0.15, 'z': 0}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    location_2 = {
        'position': {'x': 0, 'y': definition.positionY, 'z': 0},
        'rotation': {'x': 0, 'y': 45, 'z': 0}
    }
    instance_2 = instances.instantiate_object(definition, location_2)
    scene.objects.append(instance_2)
    idl_2 = InstanceDefinitionLocationTuple(instance_2, definition, location_2)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_2, 'toy_2')

    config.align_with = 'toy_2'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == -2.8549
    assert reconciled.position.z == 2.8549
    assert reconciled.rotation_y == 135

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {
        'x': -2.8549,
        'y': 0.15,
        'z': 2.8549
    }
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 135, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    location_3 = {
        'position': {'x': 0, 'y': definition.positionY, 'z': 0},
        'rotation': {'x': 0, 'y': 90, 'z': 0}
    }
    instance_3 = instances.instantiate_object(definition, location_3)
    scene.objects.append(instance_3)
    idl_3 = InstanceDefinitionLocationTuple(instance_3, definition, location_3)
    ObjectRepository.get_instance().add_to_labeled_objects(idl_3, 'toy_3')

    config.align_with = 'toy_3'
    reconciled = service.reconcile(scene, config)
    assert reconciled.position.x == 0
    assert reconciled.position.z == 4.0375
    assert reconciled.rotation_y == 180

    tool = service.create_feature_from_specific_values(
        scene=scene,
        reconciled=reconciled,
        source_template=config
    )
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    assert tool['shows'][0]['position'] == {'x': 0, 'y': 0.15, 'z': 4.0375}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_tool_create_aligned_with_error_invalid_distance():
    config = ToolConfig(
        align_distance=20,
        align_with='toy',
        shape='tool_rect_0_75_x_4_00'
    )
    service = ToolCreationService()
    scene = prior_scene()
    material_tuple = materials.ORANGE_PLASTIC
    definition = base_objects.create_specific_definition_from_base(
        'ball',
        material_tuple.color,
        [material_tuple.material],
        None,
        1
    )
    location = {
        'position': {'x': 0, 'y': definition.positionY, 'z': 0},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    }
    instance = instances.instantiate_object(definition, location)
    scene.objects.append(instance)
    idl = InstanceDefinitionLocationTuple(instance, definition, location)
    ObjectRepository.get_instance().add_to_labeled_objects(idl, 'toy')

    with pytest.raises(Exception):
        service.add_to_scene(
            scene=scene,
            source_template=config,
            bounds=[]
        )


def test_tool_create_with_lava_surrounding():
    scene = prior_scene()
    # move performer out of the way of tool and lava so there are no errors
    scene.performer_start.position.x = -4
    scene.performer_start.position.z = -4
    temp = ToolConfig(
        surrounded_by_lava=True,
        shape='tool_hooked_0_50_x_5_00',
        rotation_y=0,
        position=VectorFloatConfig(1, 0, 1)
    )
    temp.material = materials.TOOL_MATERIALS[1]
    tool = ToolCreationService().create_feature_from_specific_values(
        scene, temp, None)

    assert tool
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_hooked_0_50_x_5_00'
    show = tool['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1, 'y': 0.15, 'z': 1}
    assert rot == {'x': 0, 'y': 0, 'z': 0}
    assert scale == {'x': 1, 'y': 1, 'z': 1}

    # Make sure lava isn't officially added until add_to_scene is called
    assert not scene.lava
    assert tool['debug']['surroundingLava']
    assert len(tool['debug']['surroundingLava']) == 20
    for square in tool['debug']['surroundingLava']:
        assert square['x'] in [-1, 0, 1, 2, 3]
        assert square['z'] in [-2, -1, 0, 1, 2, 3, 4]
        assert not (square['x'] in [0, 1, 2] and
                    square['z'] in [-1, 0, 1, 2, 3])

    instances, _ = ToolCreationService().add_to_scene(
        scene=scene, source_template=temp, bounds=[])

    tool = instances[0]
    assert scene.lava
    assert len(scene.lava) == 20
    # check that 'surroundingLava' array was deleted
    # after lava was placed
    assert 'surroundingLava' not in tool['debug']

    for square in scene.lava:
        assert square.x in [-1, 0, 1, 2, 3]
        assert square.z in [-2, -1, 0, 1, 2, 3, 4]
        assert not (square.x in [0, 1, 2] and square.z in [-1, 0, 1, 2, 3])


def test_tool_create_with_lava_surrounding_fail_perf_start():
    scene = prior_scene()

    temp = ToolConfig(
        surrounded_by_lava=True,
        shape='tool_hooked_0_50_x_5_00',
        rotation_y=0,
        position=VectorFloatConfig(1, 0, 1)
    )
    temp.material = materials.TOOL_MATERIALS[1]

    with pytest.raises(ILEException):
        ToolCreationService().create_feature_from_specific_values(
            scene, temp, None
        )


def test_tool_create_with_lava_surrounding_fail_object_overlap():
    scene = prior_scene_with_target()

    # move performer out of the way of tool and lava so there are no errors
    scene.performer_start.position.x = -4
    scene.performer_start.position.z = -4

    temp = ToolConfig(
        surrounded_by_lava=True,
        shape='tool_hooked_0_50_x_5_00',
        rotation_y=0,
        position=VectorFloatConfig(1, 0, 1)
    )
    temp.material = materials.TOOL_MATERIALS[1]

    with pytest.raises(ILEException):
        ToolCreationService().create_feature_from_specific_values(
            scene=scene, reconciled=temp, source_template=None
        )
        ToolCreationService().add_to_scene(
            scene=scene, source_template=temp, bounds=[])
