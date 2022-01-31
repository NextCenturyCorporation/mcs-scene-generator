import math

import pytest

from generator import geometry, materials
from ideal_learning_env import (
    GlobalSettingsComponent,
    GoalConfig,
    ILEException,
    ILESharedConfiguration,
    InteractableObjectConfig,
    SpecificInteractableObjectsComponent,
    VectorFloatConfig,
    VectorIntConfig,
)
from ideal_learning_env.object_services import ObjectRepository


def create_new_scene():
    return {'debug': {}, 'goal': {}, 'objects': []}


@pytest.fixture(autouse=True)
def run_before_test():
    ObjectRepository.get_instance().clear()


def test_global_settings():
    component = GlobalSettingsComponent({})
    assert component.ceiling_material is None
    assert component.excluded_shapes is None
    assert component.floor_material is None
    assert component.goal is None
    assert component.last_step is None
    assert component.performer_start_position is None
    assert component.performer_start_rotation is None
    assert component.room_dimensions is None
    assert component.room_shape is None
    assert component.wall_back_material is None
    assert component.wall_front_material is None
    assert component.wall_left_material is None
    assert component.wall_right_material is None

    scene = component.update_ile_scene(create_new_scene())
    assert isinstance(scene['ceilingMaterial'], str)
    assert ILESharedConfiguration.get_instance().get_excluded_shapes() == []
    assert isinstance(scene['floorMaterial'], str)
    assert scene['goal'].get('last_step') is None
    assert scene['goal'].get('category') is None
    assert scene['goal'].get('metadata') is None
    dimensions = scene['roomDimensions']
    assert dimensions['x'] >= 2 and dimensions['x'] <= 15
    assert dimensions['y'] >= 2 and dimensions['y'] <= 10
    assert dimensions['z'] >= 2 and dimensions['z'] <= 15
    assert math.sqrt(dimensions['x']**2 + dimensions['z']**2) <= 15
    position = scene['performerStart']['position']
    assert (
        position['x'] > -(dimensions['x'] / 2.0) and
        position['x'] < (dimensions['x'] / 2.0)
    )
    assert position['y'] == 0
    assert (
        position['z'] > -(dimensions['z'] / 2.0) and
        position['z'] < (dimensions['z'] / 2.0)
    )
    rotation = scene['performerStart']['rotation']
    assert rotation['x'] == 0
    assert rotation['y'] >= 0 and rotation['y'] <= 360
    assert rotation['z'] == 0
    wall_material = scene['roomMaterials']['back']
    assert isinstance(wall_material, str)
    assert scene['roomMaterials']['front'] == wall_material
    assert scene['roomMaterials']['left'] == wall_material
    assert scene['roomMaterials']['right'] == wall_material
    assert scene['debug']['ceilingColors']
    assert scene['debug']['floorColors']
    assert scene['debug']['wallColors']


def test_global_settings_partial_start_position():
    component = GlobalSettingsComponent({"performer_start_position": {"y": 0}})
    assert component.performer_start_position == VectorFloatConfig(
        None, 0, None)
    scene = component.update_ile_scene(create_new_scene())
    position = scene['performerStart']['position']

    half_width = geometry.PERFORMER_WIDTH / 2.0
    dim = scene['roomDimensions']
    ext_x = dim['x'] / 2.0 - half_width
    ext_z = dim['z'] / 2.0 - half_width
    assert -ext_x <= position['x'] <= ext_x
    assert position['y'] == 0
    assert -ext_z <= position['z'] <= ext_z


def test_global_settings_configured():
    component = GlobalSettingsComponent({
        'ceiling_material': 'Custom/Materials/GreyDrywallMCS',
        'excluded_shapes': ['ball', 'pacifier'],
        'floor_material': 'Custom/Materials/GreyCarpetMCS',
        'goal': {
            'category': 'retrieval',
            'target': {
                'shape': 'soccer_ball'
            }
        },
        'last_step': 1000,
        'performer_start_position': {'x': -1, 'y': 0, 'z': 1},
        'performer_start_rotation': {'x': -10, 'y': 90, 'z': 0},
        'room_dimensions': {'x': 5, 'y': 3, 'z': 10},
        'room_shape': 'square',
        'wall_back_material': 'Custom/Materials/WhiteDrywallMCS',
        'wall_front_material': 'Custom/Materials/BlueDrywallMCS',
        'wall_left_material': 'Custom/Materials/GreenDrywallMCS',
        'wall_right_material': 'Custom/Materials/RedDrywallMCS'
    })
    assert component.ceiling_material == 'Custom/Materials/GreyDrywallMCS'
    assert component.excluded_shapes == ['ball', 'pacifier']
    assert component.floor_material == 'Custom/Materials/GreyCarpetMCS'
    assert component.goal == GoalConfig(
        category='retrieval',
        target=InteractableObjectConfig(shape='soccer_ball')
    )
    assert component.last_step == 1000
    assert component.performer_start_position == VectorFloatConfig(-1, 0, 1)
    assert component.performer_start_rotation == VectorIntConfig(-10, 90, 0)
    assert component.room_dimensions == VectorIntConfig(5, 3, 10)
    assert component.room_shape == 'square'
    assert component.wall_back_material == 'Custom/Materials/WhiteDrywallMCS'
    assert component.wall_front_material == 'Custom/Materials/BlueDrywallMCS'
    assert component.wall_left_material == 'Custom/Materials/GreenDrywallMCS'
    assert component.wall_right_material == 'Custom/Materials/RedDrywallMCS'

    scene = component.update_ile_scene(create_new_scene())
    assert scene['ceilingMaterial'] == 'Custom/Materials/GreyDrywallMCS'
    assert ILESharedConfiguration.get_instance().get_excluded_shapes() == [
        'ball', 'pacifier'
    ]
    assert scene['floorMaterial'] == 'Custom/Materials/GreyCarpetMCS'
    assert scene['goal']['category'] == 'retrieval'
    assert scene['goal']['description'] == (
        'Find and pick up the tiny light black white rubber ball'
    )
    assert scene['goal']['last_step'] == 1000
    assert scene['goal']['metadata']['target']['id']
    assert scene['performerStart'] == {
        'position': {'x': -1, 'y': 0, 'z': 1},
        'rotation': {'x': -10, 'y': 90, 'z': 0}
    }
    assert scene['roomDimensions'] == {'x': 5, 'y': 3, 'z': 10}
    assert scene['roomMaterials'] == {
        'back': 'Custom/Materials/WhiteDrywallMCS',
        'front': 'Custom/Materials/BlueDrywallMCS',
        'left': 'Custom/Materials/GreenDrywallMCS',
        'right': 'Custom/Materials/RedDrywallMCS'
    }

    # Cleanup
    ILESharedConfiguration.get_instance().set_excluded_shapes([])


def test_global_settings_fail_ceiling_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'ceiling_material': ''
        })


def test_global_settings_fail_floor_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'floor_material': ''
        })


def test_global_settings_fail_goal():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'goal': {}
        })


def test_global_settings_fail_goal_no_category():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'goal': {
                'target': {
                    'shape': 'soccer_ball'
                }
            }
        })


def test_global_settings_fail_last_step_negative():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'last_step': -1
        })


def test_global_settings_fail_last_step_zero():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'last_step': 0
        })


def test_global_settings_fail_performer_start_rotation_y_is_none():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'performer_start_rotation': {
                'x': 0,
                'y': None,
                'z': 0
            }
        })


def test_global_settings_fail_room_dimensions_x_above_max():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_dimensions': {
                'x': 16,
                'y': 2,
                'z': 2
            }
        })


def test_global_settings_fail_room_dimensions_x_below_min():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_dimensions': {
                'x': 1,
                'y': 2,
                'z': 2
            }
        })


def test_global_settings_fail_room_dimensions_x_is_none():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_dimensions': {
                'x': None,
                'y': 2,
                'z': 2
            }
        })


def test_global_settings_fail_room_dimensions_y_above_max():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_dimensions': {
                'x': 2,
                'y': 11,
                'z': 2
            }
        })


def test_global_settings_fail_room_dimensions_y_below_min():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_dimensions': {
                'x': 2,
                'y': 1,
                'z': 2
            }
        })


def test_global_settings_fail_room_dimensions_y_is_none():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_dimensions': {
                'x': 2,
                'y': None,
                'z': 2
            }
        })


def test_global_settings_fail_room_dimensions_z_above_max():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_dimensions': {
                'x': 2,
                'y': 2,
                'z': 16
            }
        })


def test_global_settings_fail_room_dimensions_z_below_min():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_dimensions': {
                'x': 2,
                'y': 2,
                'z': 1
            }
        })


def test_global_settings_fail_room_dimensions_z_is_none():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_dimensions': {
                'x': 2,
                'y': 2,
                'z': None
            }
        })


def test_global_settings_fail_room_shape():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_shape': ''
        })


def test_global_settings_fail_wall_back_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_back_material': ''
        })


def test_global_settings_fail_wall_front_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_front_material': ''
        })


def test_global_settings_fail_wall_left_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_left_material': ''
        })


def test_global_settings_fail_wall_right_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_right_material': ''
        })


def test_global_settings_performer_start_position_y_is_none():
    component = GlobalSettingsComponent({
        'performer_start_position': {
            'x': -1,
            'y': None,
            'z': 1
        }
    })
    scene = component.update_ile_scene(create_new_scene())
    assert scene['performerStart']['position'] == {
        'x': -1,
        'y': 0,
        'z': 1
    }


def test_global_settings_performer_start_rotation_x_and_z_are_none():
    component = GlobalSettingsComponent({
        'performer_start_rotation': {
            'x': None,
            'y': -90,
            'z': None
        }
    })
    scene = component.update_ile_scene(create_new_scene())
    assert scene['performerStart']['rotation'] == {
        'x': 0,
        'y': -90,
        'z': 0
    }


def test_global_settings_room_shape_rectangle():
    # Test on many different random iterations.
    for _ in list(range(10)):
        component = GlobalSettingsComponent({
            'room_shape': 'rectangle'
        })
        scene = component.update_ile_scene(create_new_scene())
        dimensions = scene['roomDimensions']
        assert dimensions['x'] != dimensions['z']


def test_global_settings_room_shape_square():
    # Test on many different random iterations.
    for _ in list(range(10)):
        component = GlobalSettingsComponent({
            'room_shape': 'square'
        })
        scene = component.update_ile_scene(create_new_scene())
        dimensions = scene['roomDimensions']
        assert dimensions['x'] == dimensions['z']


def test_target_delayed():
    label = "after_object"
    scene = create_new_scene()

    data = {
        "goal": {
            "category": "retrieval",
            "target": {
                "shape": "soccer_ball",
                "keyword_location": {
                        "keyword": "adjacent",
                        "relative_object_label": label
                }
            }
        },
        "specific_interactable_objects": {
            "num": 1,
            "labels": label
        }
    }

    component = GlobalSettingsComponent(data)

    scene = component.update_ile_scene(scene)
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 0
    assert component.get_num_delayed_actions() == 1

    object_comp = SpecificInteractableObjectsComponent(data)
    scene = object_comp.update_ile_scene(scene)
    assert len(objects) == 1

    scene = component.run_delayed_actions(scene)
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 2
    component.get_num_delayed_actions() == 0
    assert objects[1]['type'] == "soccer_ball"


def test_global_settings_ceiling_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'ceiling_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_ceiling_material_fail_lava_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'ceiling_material': materials.LAVA_MATERIALS[0].material
        })


def test_global_settings_floor_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'floor_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_floor_material_fail_lava_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'floor_material': materials.LAVA_MATERIALS[0].material
        })


def test_global_settings_wall_back_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_back_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_wall_back_material_fail_lava_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_back_material': materials.LAVA_MATERIALS[0].material
        })


def test_global_settings_wall_front_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_front_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_wall_front_material_fail_lava_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_front_material': materials.LAVA_MATERIALS[0].material
        })


def test_global_settings_wall_left_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_left_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_wall_left_material_fail_lava_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_left_material': materials.LAVA_MATERIALS[0].material
        })


def test_global_settings_wall_right_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_right_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_wall_right_material_fail_lava_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_right_material': materials.LAVA_MATERIALS[0].material
        })
