import math

import pytest
from machine_common_sense.config_manager import PerformerStart, Vector3d

from generator import geometry, materials
from generator.scene import Scene
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
from tests.ile_helper import prior_scene, prior_scene_custom_start


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()

    # Run test
    yield

    # Cleanup
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
    assert component.restrict_open_doors is None
    assert component.room_dimensions is None
    assert component.room_shape is None
    assert component.wall_back_material is None
    assert component.wall_front_material is None
    assert component.wall_left_material is None
    assert component.wall_right_material is None

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene.ceiling_material, str)
    assert ILESharedConfiguration.get_instance().get_excluded_shapes() == []
    assert isinstance(scene.floor_material, str)
    assert scene.goal.get('last_step') is None
    assert scene.goal.get('category') is None
    assert scene.goal.get('metadata') == {}
    dimensions = scene.room_dimensions
    assert dimensions.x >= 2 and dimensions.x <= 100
    assert dimensions.y >= 2 and dimensions.y <= 10
    assert dimensions.z >= 2 and dimensions.z <= 100
    assert math.sqrt(dimensions.x**2 + dimensions.z**2) <= 150
    position = scene.performer_start.position
    assert (
        position.x > -(dimensions.x / 2.0) and
        position.x < (dimensions.x / 2.0)
    )
    assert position.y == 0
    assert (
        position.z > -(dimensions.z / 2.0) and
        position.z < (dimensions.z / 2.0)
    )
    rotation = scene.performer_start.rotation
    assert rotation.x == 0
    assert rotation.y >= 0 and rotation.y <= 360
    assert rotation.z == 0
    wall_material = scene.room_materials['back']
    assert isinstance(wall_material, str)
    assert scene.room_materials['front'] == wall_material
    assert scene.room_materials['left'] == wall_material
    assert scene.room_materials['right'] == wall_material
    assert scene.debug['ceilingColors']
    assert scene.debug['floorColors']
    assert scene.debug['wallColors']
    assert scene.restrict_open_doors is False


def test_global_settings_partial_start_position():
    component = GlobalSettingsComponent({"performer_start_position": {"y": 0}})
    assert component.performer_start_position == VectorFloatConfig(
        None, 0, None)
    scene = component.update_ile_scene(prior_scene())
    position = scene.performer_start.position

    half_width = geometry.PERFORMER_WIDTH / 2.0
    dim = scene.room_dimensions
    ext_x = dim.x / 2.0 - half_width
    ext_z = dim.z / 2.0 - half_width
    assert -ext_x <= position.x <= ext_x
    assert position.y == 0
    assert -ext_z <= position.z <= ext_z


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
        'restrict_open_doors': True,
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
    assert component.restrict_open_doors
    assert component.room_dimensions == VectorIntConfig(5, 3, 10)
    assert component.room_shape == 'square'
    assert component.wall_back_material == 'Custom/Materials/WhiteDrywallMCS'
    assert component.wall_front_material == 'Custom/Materials/BlueDrywallMCS'
    assert component.wall_left_material == 'Custom/Materials/GreenDrywallMCS'
    assert component.wall_right_material == 'Custom/Materials/RedDrywallMCS'

    scene = component.update_ile_scene(prior_scene())
    assert scene.ceiling_material == 'Custom/Materials/GreyDrywallMCS'
    assert ILESharedConfiguration.get_instance().get_excluded_shapes() == [
        'ball', 'pacifier'
    ]
    assert scene.floor_material == 'Custom/Materials/GreyCarpetMCS'
    assert scene.goal['category'] == 'retrieval'
    assert scene.goal['description'] in [
        'Find and pick up the tiny light black white rubber ball',
        'Find and pick up the medium light black white rubber ball',
        'Find and pick up the small light black white rubber ball'
    ]
    assert scene.goal['last_step'] == 1000
    assert scene.goal['metadata']['target']['id']
    assert scene.performer_start == PerformerStart(
        position=Vector3d(x=-1, y=0, z=1), rotation=Vector3d(x=-10, y=90, z=0))

    assert scene.restrict_open_doors is True
    assert scene.room_dimensions == Vector3d(x=5, y=3, z=10)
    assert scene.room_materials == {
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
                'x': 101,
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


def test_global_settings_room_dimensions_x_is_none():
    component = GlobalSettingsComponent({
        'room_dimensions': {
            'x': None,
            'y': 2,
            'z': 2
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert 2 <= scene.room_dimensions.x <= 100
    assert scene.room_dimensions.y == 2
    assert scene.room_dimensions.z == 2


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


def test_global_settings_room_dimensions_y_is_none():
    component = GlobalSettingsComponent({
        'room_dimensions': {
            'x': 2,
            'y': None,
            'z': 2
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert scene.room_dimensions.x == 2
    assert 2 <= scene.room_dimensions.y <= 10
    assert scene.room_dimensions.z == 2


def test_global_settings_fail_room_dimensions_z_above_max():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'room_dimensions': {
                'x': 2,
                'y': 2,
                'z': 101
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


def test_global_settings_room_dimensions_z_is_none():
    component = GlobalSettingsComponent({
        'room_dimensions': {
            'x': 2,
            'y': 2,
            'z': None
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert scene.room_dimensions.x == 2
    assert scene.room_dimensions.y == 2
    assert 2 <= scene.room_dimensions.z <= 100


def test_global_settings_room_dimensions_min_max():
    component = GlobalSettingsComponent({
        'room_dimensions': {
            'x': 2,
            'y': 2,
            'z': {'min': 3, 'max': 8}
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert scene.room_dimensions.x == 2
    assert scene.room_dimensions.y == 2
    assert 3 <= scene.room_dimensions.z <= 8


def test_global_settings_room_dimensions_array():
    component = GlobalSettingsComponent({
        'room_dimensions': {
            'x': [4, 8],
            'y': 2,
            'z': 4
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert scene.room_dimensions.x in [4, 8]
    assert scene.room_dimensions.y == 2
    assert scene.room_dimensions.z == 4


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
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.position == Vector3d(x=-1, y=0, z=1)


def test_global_settings_performer_start_rotation_x_and_z_are_none():
    component = GlobalSettingsComponent({
        'performer_start_rotation': {
            'x': None,
            'y': -90,
            'z': None
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.rotation == Vector3d(x=0, y=-90, z=0)


def test_global_settings_room_shape_rectangle():
    # Test on many different random iterations.
    for _ in list(range(10)):
        component = GlobalSettingsComponent({
            'room_shape': 'rectangle'
        })
        scene = component.update_ile_scene(prior_scene())
        dimensions = scene.room_dimensions
        assert dimensions.x != dimensions.z


def test_global_settings_room_shape_square():
    # Test on many different random iterations.
    for _ in list(range(10)):
        component = GlobalSettingsComponent({
            'room_shape': 'square'
        })
        scene = component.update_ile_scene(Scene())
        dimensions = scene.room_dimensions
        assert dimensions.x == dimensions.z


def test_target_delayed():
    label = "after_object"
    scene = prior_scene_custom_start(4, 4)

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
            "labels": label,
            "shape": 'chest_4',
            "position": {
                'x': 0,
                'y': 0,
                'z': 0
            }
        }
    }

    component = GlobalSettingsComponent(data)

    scene = component.update_ile_scene(scene)
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 0
    assert component.get_num_delayed_actions() == 1

    object_comp = SpecificInteractableObjectsComponent(data)
    scene = object_comp.update_ile_scene(scene)
    assert len(objects) == 1

    scene = component.run_delayed_actions(scene)
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 2
    component.get_num_delayed_actions() == 0
    assert objects[1]['type'] == "soccer_ball"


def test_global_settings_ceiling_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'ceiling_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_floor_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'floor_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_wall_back_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_back_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_wall_front_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_front_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_wall_left_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_left_material': materials.SOFA_1_MATERIALS[0].material
        })


def test_global_settings_wall_right_material_fail_restricted_material():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'wall_right_material': materials.SOFA_1_MATERIALS[0].material
        })
