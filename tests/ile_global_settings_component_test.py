import math

import pytest
from machine_common_sense.config_manager import PerformerStart, Vector3d
from numpy import arange
from shapely.geometry import Point, Polygon

from generator import geometry, materials
from generator.base_objects import create_soccer_ball
from generator.geometry import PERFORMER_HALF_WIDTH
from generator.instances import instantiate_object
from generator.scene import Scene
from ideal_learning_env import (
    GlobalSettingsComponent,
    GoalConfig,
    ILEException,
    ILESharedConfiguration,
    InteractableObjectConfig,
    KeywordLocationConfig,
    SpecificInteractableObjectsComponent,
    VectorFloatConfig,
    VectorIntConfig
)
from ideal_learning_env.defs import ILEConfigurationException
from ideal_learning_env.numerics import MinMaxFloat, MinMaxInt
from ideal_learning_env.object_services import ObjectRepository
from tests.ile_helper import (
    add_object_with_position_to_repo,
    prior_scene,
    prior_scene_custom_start,
    prior_scene_with_target
)


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
    assert component.occluder_gap is None
    assert component.occluder_gap_viewport is None
    assert component.passive_physics_floor is None
    assert component.passive_physics_scene is None
    assert component.performer_start_position is None
    assert component.performer_start_rotation is None
    assert component.restrict_open_doors is None
    assert component.restrict_open_objects is None
    assert component.room_dimensions is None
    assert component.room_shape is None
    assert component.side_wall_opposite_colors is None
    assert component.trapezoidal_room is None
    assert component.wall_back_material is None
    assert component.wall_front_material is None
    assert component.wall_left_material is None
    assert component.wall_material is None
    assert component.wall_right_material is None

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene.ceiling_material, str)
    assert ILESharedConfiguration.get_instance().get_excluded_shapes() == []
    assert ILESharedConfiguration.get_instance().get_occluder_gap() is None
    assert ILESharedConfiguration.get_instance().get_occluder_gap_viewport() \
        is None
    assert isinstance(scene.floor_material, str)
    assert scene.floor_properties is None
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
    assert scene.restrict_open_objects is False
    assert not scene.intuitive_physics
    assert not scene.objects


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


def test_global_settings_start_position_keyword():
    component = GlobalSettingsComponent(
        {"performer_start_position": {"keyword": "along_wall",
                                      "relative_object_label": "back_wall"},
         "room_dimensions": {"x": 4, "y": 3, "z": 14}})
    assert component.performer_start_position == KeywordLocationConfig(
        keyword="along_wall", relative_object_label="back_wall")
    scene = component.update_ile_scene(prior_scene())
    pos = scene.performer_start.position
    assert pos.z == pytest.approx(6.72, 2)
    assert -1.75 < pos.x < 1.75


def test_global_settings_start_position_keyword_no_label():
    component = GlobalSettingsComponent(
        {"performer_start_position": {"keyword": "along_wall"},
         "room_dimensions": {"x": 10, "y": 3, "z": 10}})
    assert component.performer_start_position == KeywordLocationConfig(
        keyword="along_wall")
    scene = component.update_ile_scene(prior_scene())
    pos = scene.performer_start.position
    assert (abs(pos.z) == pytest.approx(4.72, 2) or
            abs(pos.x) == pytest.approx(4.72, 2))


def test_global_settings_start_position_keyword_fail():
    component = GlobalSettingsComponent(
        {"performer_start_position": {"keyword": "between"}})
    with pytest.raises(ILEConfigurationException):
        component.update_ile_scene(prior_scene())


def test_global_settings_start_position_restrictions():
    scene = prior_scene()
    component = GlobalSettingsComponent({
        "performer_start_position": {
            "x": MinMaxFloat(-4.75, 4.75),
            "y": 5.75,
            "z": [-4.75, -2, 0, 2, 4.75]
        },
        "room_dimensions": {
            "x": MinMaxInt(5, 10),
            "y": 7,
            "z": [5, 10]
        }
    })
    scene = component.update_ile_scene(scene)
    position = scene.performer_start.position
    assert -4.75 <= position.x <= 4.75
    assert position.y == 5.75
    assert position.z in [-2, 0, 2]

    component = GlobalSettingsComponent({
        "performer_start_position": {
            "x": MinMaxFloat(-5, 0)
        },
        "room_dimensions": {
            "x": MinMaxInt(5, 10)
        }
    })
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = GlobalSettingsComponent({
        "performer_start_position": {
            "x": MinMaxFloat(0, 5)
        },
        "room_dimensions": {
            "x": MinMaxInt(5, 10)
        }
    })
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = GlobalSettingsComponent({
        "performer_start_position": {
            "y": 7
        },
        "room_dimensions": {
            "y": 7
        }
    })
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = GlobalSettingsComponent({
        "performer_start_position": {
            "z": [-5, 0, 2.5]
        },
        "room_dimensions": {
            "z": [5, 10]
        }
    })
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = GlobalSettingsComponent({
        "performer_start_position": {
            "z": [0, 2.5, 5]
        },
        "room_dimensions": {
            "z": [5, 10]
        }
    })
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)


def test_global_settings_configured():
    component = GlobalSettingsComponent({
        'ceiling_material': 'Custom/Materials/GreyDrywallMCS',
        'excluded_shapes': ['ball', 'pacifier'],
        'floor_material': 'Custom/Materials/GreyCarpetMCS',
        'goal': {
            'category': 'retrieval',
            'target': {
                'shape': 'soccer_ball'
            },
        },
        'last_step': 1000,
        'occluder_gap': 1.0,
        'occluder_gap_viewport': 1.0,
        'performer_start_position': {'x': -1, 'y': 0, 'z': 1},
        'performer_start_rotation': {'x': -10, 'y': 90, 'z': 0},
        'restrict_open_doors': True,
        'restrict_open_objects': True,
        'room_dimensions': {'x': 5, 'y': 3, 'z': 10},
        'room_shape': 'square',
        'wall_back_material': 'Custom/Materials/WhiteDrywallMCS',
        'wall_front_material': 'Custom/Materials/BlueDrywallMCS',
        'wall_left_material': 'Custom/Materials/GreenDrywallMCS',
        'wall_material': 'Custom/Materials/YellowDrywallMCS',
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
    assert component.occluder_gap == 1.0
    assert component.occluder_gap_viewport == 1.0
    assert component.performer_start_position == VectorFloatConfig(-1, 0, 1)
    assert component.performer_start_rotation == VectorIntConfig(-10, 90, 0)
    assert component.restrict_open_doors
    assert component.restrict_open_objects
    assert component.room_dimensions == VectorIntConfig(5, 3, 10)
    assert component.room_shape == 'square'
    assert component.wall_back_material == 'Custom/Materials/WhiteDrywallMCS'
    assert component.wall_front_material == 'Custom/Materials/BlueDrywallMCS'
    assert component.wall_left_material == 'Custom/Materials/GreenDrywallMCS'
    assert component.wall_material == 'Custom/Materials/YellowDrywallMCS'
    assert component.wall_right_material == 'Custom/Materials/RedDrywallMCS'

    scene = component.update_ile_scene(prior_scene())
    assert scene.ceiling_material == 'Custom/Materials/GreyDrywallMCS'
    assert ILESharedConfiguration.get_instance().get_excluded_shapes() == [
        'ball', 'pacifier'
    ]
    assert scene.floor_material == 'Custom/Materials/GreyCarpetMCS'
    assert scene.floor_properties is None
    assert scene.goal['category'] == 'retrieval'
    assert scene.goal['description'] in [
        'Find and pick up the tiny light black white rubber ball.',
        'Find and pick up the medium light black white rubber ball.',
        'Find and pick up the small light black white rubber ball.'
    ]
    assert scene.goal['last_step'] == 1000
    assert scene.goal['metadata']['target']['id']
    assert ILESharedConfiguration.get_instance().get_occluder_gap() == 1.0
    assert ILESharedConfiguration.get_instance().get_occluder_gap_viewport() \
        == 1.0
    assert scene.performer_start == PerformerStart(
        position=Vector3d(x=-1, y=0, z=1), rotation=Vector3d(x=-10, y=90, z=0))
    assert scene.restrict_open_doors is True
    assert scene.restrict_open_objects is True
    assert scene.room_dimensions == Vector3d(x=5, y=3, z=10)
    assert scene.room_materials == {
        'back': 'Custom/Materials/WhiteDrywallMCS',
        'front': 'Custom/Materials/BlueDrywallMCS',
        'left': 'Custom/Materials/GreenDrywallMCS',
        'right': 'Custom/Materials/RedDrywallMCS'
    }
    assert not scene.intuitive_physics
    assert len(scene.objects) == 1
    assert scene.objects[0]['type'] == 'soccer_ball'

    # Cleanup
    ILESharedConfiguration.get_instance().set_excluded_shapes([])
    ILESharedConfiguration.get_instance().set_occluder_gap(None)
    ILESharedConfiguration.get_instance().set_occluder_gap_viewport(None)


def test_global_settings_passive_physics_scene():
    component = GlobalSettingsComponent({
        'ceiling_material': 'Custom/Materials/GreyDrywallMCS',
        'excluded_shapes': ['ball', 'pacifier'],
        'floor_material': 'Custom/Materials/GreyCarpetMCS',
        # Expect this to be overridden after calling update_ile_scene
        'goal': {
            'category': 'retrieval',
            'target': {
                'shape': 'soccer_ball'
            }
        },
        'last_step': 1000,
        'occluder_gap': 1.0,
        'occluder_gap_viewport': 1.0,
        'passive_physics_scene': True,
        # Expect this to be overridden after calling update_ile_scene
        'performer_start_position': {'x': -1, 'y': 0, 'z': 1},
        # Expect this to be overridden after calling update_ile_scene
        'performer_start_rotation': {'x': -10, 'y': 90, 'z': 0},
        # Expect this to be overridden after calling update_ile_scene
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
    assert component.occluder_gap == 1.0
    assert component.occluder_gap_viewport == 1.0
    assert component.passive_physics_scene is True
    assert component.performer_start_position == VectorFloatConfig(-1, 0, 1)
    assert component.performer_start_rotation == VectorIntConfig(-10, 90, 0)
    assert component.room_dimensions == VectorIntConfig(5, 3, 10)
    assert component.room_shape == 'square'
    assert component.wall_back_material == 'Custom/Materials/WhiteDrywallMCS'
    assert component.wall_front_material == 'Custom/Materials/BlueDrywallMCS'
    assert component.wall_left_material == 'Custom/Materials/GreenDrywallMCS'
    assert component.wall_right_material == 'Custom/Materials/RedDrywallMCS'

    scene = component.update_ile_scene(prior_scene())
    assert scene.intuitive_physics
    assert scene.version == 3
    assert scene.ceiling_material == 'Custom/Materials/GreyDrywallMCS'
    assert ILESharedConfiguration.get_instance().get_excluded_shapes() == [
        'ball', 'pacifier'
    ]
    assert ILESharedConfiguration.get_instance().get_occluder_gap() == 1.0
    assert ILESharedConfiguration.get_instance().get_occluder_gap_viewport() \
        == 1.0
    assert scene.floor_material == 'Custom/Materials/GreyCarpetMCS'
    assert scene.floor_properties['enable'] is True
    assert scene.floor_properties['angularDrag'] == 0.5
    assert scene.floor_properties['bounciness'] == 0
    assert scene.floor_properties['drag'] == 0
    assert scene.floor_properties['dynamicFriction'] == 0.1
    assert scene.floor_properties['staticFriction'] == 0.1
    assert scene.goal['category'] == 'intuitive physics'
    assert scene.goal['description'] == ''
    assert scene.goal['last_step'] == 1000
    assert scene.goal['metadata'] == {}
    assert scene.performer_start == PerformerStart(
        position=Vector3d(x=0, y=0, z=-4.5),
        rotation=Vector3d(x=0, y=0, z=0)
    )
    assert scene.room_dimensions == Vector3d(x=20, y=10, z=20)
    assert scene.room_materials == {
        'back': 'Custom/Materials/WhiteDrywallMCS',
        'front': 'Custom/Materials/BlueDrywallMCS',
        'left': 'Custom/Materials/GreenDrywallMCS',
        'right': 'Custom/Materials/RedDrywallMCS'
    }

    # Cleanup
    ILESharedConfiguration.get_instance().set_excluded_shapes([])
    ILESharedConfiguration.get_instance().set_occluder_gap(None)
    ILESharedConfiguration.get_instance().set_occluder_gap_viewport(None)


def test_global_settings_side_wall_opposite_colors():
    component = GlobalSettingsComponent({
        'side_wall_opposite_colors': True
    })
    assert component.side_wall_opposite_colors

    scene = component.update_ile_scene(prior_scene())
    options = [item.material for item in materials.OPPOSITE_MATERIALS]
    wall_material = scene.room_materials['back']
    assert wall_material in options
    opposite_material = materials.OPPOSITE_SETS[wall_material].material
    assert scene.room_materials['front'] == wall_material
    assert (
        scene.room_materials['left'] == wall_material and
        scene.room_materials['right'] == opposite_material
    ) or (
        scene.room_materials['right'] == wall_material and
        scene.room_materials['left'] == opposite_material
    )


def test_global_settings_trapezoidal_room():
    component = GlobalSettingsComponent({
        'ceiling_material': 'Custom/Materials/GreyDrywallMCS',
        'floor_material': 'Custom/Materials/GreyCarpetMCS',
        'goal': {
            'category': 'retrieval',
            'target': {
                'shape': 'soccer_ball'
            }
        },
        'room_dimensions': {'x': 12, 'y': 3, 'z': 16},
        'trapezoidal_room': True,
        'wall_back_material': 'Custom/Materials/WhiteDrywallMCS',
        'wall_front_material': 'Custom/Materials/BlueDrywallMCS',
        'wall_left_material': 'Custom/Materials/GreenDrywallMCS',
        'wall_right_material': 'Custom/Materials/RedDrywallMCS'
    })
    assert component.ceiling_material == 'Custom/Materials/GreyDrywallMCS'
    assert component.floor_material == 'Custom/Materials/GreyCarpetMCS'
    assert component.goal == GoalConfig(
        category='retrieval',
        target=InteractableObjectConfig(shape='soccer_ball')
    )
    assert component.room_dimensions == VectorIntConfig(12, 3, 16)
    assert component.trapezoidal_room
    assert component.wall_back_material == 'Custom/Materials/WhiteDrywallMCS'
    assert component.wall_front_material == 'Custom/Materials/BlueDrywallMCS'
    assert component.wall_left_material == 'Custom/Materials/GreenDrywallMCS'
    assert component.wall_right_material == 'Custom/Materials/RedDrywallMCS'

    scene = component.update_ile_scene(prior_scene())
    assert scene.ceiling_material == 'Custom/Materials/GreyDrywallMCS'
    assert scene.floor_material == 'Custom/Materials/GreyCarpetMCS'
    assert scene.floor_properties is None
    assert scene.goal['category'] == 'retrieval'
    assert scene.goal['description'] in [
        'Find and pick up the tiny light black white rubber ball.',
        'Find and pick up the medium light black white rubber ball.',
        'Find and pick up the small light black white rubber ball.'
    ]
    assert scene.goal['metadata']['target']['id']
    assert scene.room_dimensions == Vector3d(x=12, y=3, z=16)
    assert scene.room_materials == {
        'back': 'Custom/Materials/WhiteDrywallMCS',
        'front': 'Custom/Materials/BlueDrywallMCS',
        'left': 'Custom/Materials/GreenDrywallMCS',
        'right': 'Custom/Materials/RedDrywallMCS'
    }
    assert not scene.intuitive_physics
    assert len(scene.objects) == 3
    wall_left = scene.objects[0]
    wall_right = scene.objects[1]
    target = scene.objects[2]
    assert target['type'] == 'soccer_ball'
    assert wall_left['type'] == 'cube'
    assert wall_left['id'] == 'wall_left_override'
    assert wall_left['materials'] == ['Custom/Materials/GreenDrywallMCS']
    assert wall_right['type'] == 'cube'
    assert wall_right['id'] == 'wall_right_override'
    assert wall_right['materials'] == ['Custom/Materials/RedDrywallMCS']


def test_global_settings_wall_material():
    component = GlobalSettingsComponent({
        'wall_material': "Custom/Materials/BrownDrywallMCS"
    })
    assert component.wall_material == "Custom/Materials/BrownDrywallMCS"

    scene = component.update_ile_scene(prior_scene())
    assert scene.room_materials['back'] == "Custom/Materials/BrownDrywallMCS"
    assert scene.room_materials['front'] == "Custom/Materials/BrownDrywallMCS"
    assert scene.room_materials['left'] == "Custom/Materials/BrownDrywallMCS"
    assert scene.room_materials['right'] == "Custom/Materials/BrownDrywallMCS"


def test_auto_last_step():
    component = GlobalSettingsComponent({
        'auto_last_step': True,
        'room_dimensions': {'x': 5, 'y': 3, 'z': 10},
    })
    scene: Scene = component.update_ile_scene(prior_scene())
    assert scene.goal['last_step'] == 2000


def test_last_step_both_methods():
    component = GlobalSettingsComponent({
        'auto_last_step': True,
        'last_step': 987,
        'room_dimensions': {'x': 5, 'y': 3, 'z': 10},
    })
    scene: Scene = component.update_ile_scene(prior_scene())
    assert scene.goal['last_step'] == 987


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


def test_global_settings_fail_goal_category_invalid():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'goal': {
                'category': 'invalid'
            }
        })


def test_global_settings_fail_goal_category_intuitive_physics():
    with pytest.raises(ILEException):
        GlobalSettingsComponent({
            'goal': {
                'category': 'intuitive physics'
            }
        })


def test_global_settings_fail_goal_category_retrieval():
    with pytest.raises(ILEConfigurationException):
        GlobalSettingsComponent({
            'goal': {
                'category': 'retrieval'
            }
        })


def test_global_settings_fail_goal_category_multi_retrieval():
    with pytest.raises(ILEConfigurationException):
        GlobalSettingsComponent({
            'goal': {
                'category': 'multi retrieval'
            }
        })


def test_global_settings_goal_no_category():
    # Should not raise exception
    component = GlobalSettingsComponent({
        'goal': {
            'target': {
                'shape': 'soccer_ball'
            }
        }
    })
    assert component.goal.category == 'retrieval'


def test_global_settings_goal_no_category_multi_retrieval():
    # Should not raise exception
    component = GlobalSettingsComponent({
        'goal': {
            'targets': [{
                'shape': 'soccer_ball'
            }]
        }
    })
    assert component.goal.category == 'multi retrieval'


def test_global_settings_goal_passive():
    # Should not raise exception
    component = GlobalSettingsComponent({
        'goal': {
            'category': 'passive'
        }
    })
    assert component.goal.category == 'passive'


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


def test_global_settings_fail_trapezoidal_room_unsupported_dimensions():
    component = GlobalSettingsComponent({
        'room_dimensions': {'x': 10, 'y': 3, 'z': 10},
        'trapezoidal_room': True
    })
    assert component.room_dimensions == VectorIntConfig(10, 3, 10)
    assert component.trapezoidal_room
    with pytest.raises(ILEConfigurationException):
        component.update_ile_scene(prior_scene())


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


def test_global_settings_performer_look_at_target():
    component = GlobalSettingsComponent({
        'performer_start_position': {
            'x': 4,
            'z': -4
        },
        'performer_start_rotation': {
            'x': 0,
            'y': 0
        },
        'performer_look_at': 'target',
        'room_dimensions': {
            'x': 10,
            'y': 10,
            'z': 10
        }
    })
    scene = component.update_ile_scene(
        prior_scene_with_target(add_to_repo=True))
    assert scene.performer_start.rotation.x == 0
    assert scene.performer_start.rotation.y == 330
    assert scene.performer_start.rotation.z == 0


def test_global_settings_performer_look_at_target_around_the_world():
    component = GlobalSettingsComponent({
        'performer_start_position': {
            'x': 1,
            'z': -1
        },
        'performer_start_rotation': {
            'x': 0,
            'y': 0
        },
        'performer_look_at': 'test_obj'
    })

    ObjectRepository.get_instance().clear()
    add_object_with_position_to_repo("test_obj", 1, 0.5, 1)
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.rotation.y == 0
    assert scene.performer_start.rotation.z == 0

    ObjectRepository.get_instance().clear()
    add_object_with_position_to_repo("test_obj", 3, 0.5, 1)
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.rotation.y == 40
    assert scene.performer_start.rotation.z == 0

    ObjectRepository.get_instance().clear()
    add_object_with_position_to_repo("test_obj", 3, 0.5, -1)
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.rotation.y == 90
    assert scene.performer_start.rotation.z == 0

    ObjectRepository.get_instance().clear()
    add_object_with_position_to_repo("test_obj", 3, 0.5, -3)
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.rotation.y == 140
    assert scene.performer_start.rotation.z == 0

    ObjectRepository.get_instance().clear()
    add_object_with_position_to_repo("test_obj", 1, 0.5, -3)
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.rotation.y == 180
    assert scene.performer_start.rotation.z == 0

    ObjectRepository.get_instance().clear()
    add_object_with_position_to_repo("test_obj", -1, 0.5, -3)
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.rotation.y == 220
    assert scene.performer_start.rotation.z == 0

    ObjectRepository.get_instance().clear()
    add_object_with_position_to_repo("test_obj", -1, 0.5, -1)
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.rotation.y == 270
    assert scene.performer_start.rotation.z == 0

    ObjectRepository.get_instance().clear()
    add_object_with_position_to_repo("test_obj", -1, 0.5, 1)
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.rotation.y == 320
    assert scene.performer_start.rotation.z == 0

    ObjectRepository.get_instance().clear()
    add_object_with_position_to_repo("test_obj", 4, 0.5, -4)
    scene = component.update_ile_scene(prior_scene())
    assert scene.performer_start.rotation.x == 0
    assert scene.performer_start.rotation.y == 140
    assert scene.performer_start.rotation.z == 0


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


@pytest.mark.slow
def test_global_settings_performer_starts_near():
    for distance_away in arange(0.1, 2.1, 0.1):
        for _ in range(10):
            distance_away = round(distance_away, 1)
            ObjectRepository.get_instance().clear()
            data = {
                "specific_interactable_objects": [{
                    'num': 1,
                    'shape': 'chest_1',
                    'labels': 'container'
                }],
                'performer_starts_near': {
                    'label': 'container',
                    'distance': distance_away
                }
            }

            component = GlobalSettingsComponent(data)
            assert component.performer_starts_near
            assert component.performer_starts_near.label
            assert component.performer_starts_near.distance >= 0
            assert component.performer_starts_near.distance == distance_away
            scene = component.update_ile_scene(
                prior_scene_custom_start(10, 10))
            assert component.get_num_delayed_actions() == 1

            object_comp = SpecificInteractableObjectsComponent(data)
            scene = object_comp.update_ile_scene(scene)
            assert len(scene.objects) == 1

            scene = component.run_delayed_actions(scene)
            component.get_num_delayed_actions() == 0

            performer_start = Point(
                scene.performer_start.position.x,
                scene.performer_start.position.z)
            object = scene.objects[0]
            bb_boxes = object['shows'][0]['boundingBox'].box_xz
            top_right = Point(bb_boxes[0].x, bb_boxes[0].z)
            bottom_right = Point(bb_boxes[1].x, bb_boxes[1].z)
            bottom_left = Point(bb_boxes[2].x, bb_boxes[2].z)
            top_left = Point(bb_boxes[3].x, bb_boxes[3].z)
            object_polygon = Polygon(
                [top_right, bottom_right, bottom_left, top_left])
            distance = round(performer_start.distance(object_polygon), 2)
            expected_distance = round(distance_away + PERFORMER_HALF_WIDTH, 2)
            assert distance == expected_distance


def test_global_settings_adjacent_targets_without_error():
    component = GlobalSettingsComponent({
        'goal': {
            'category': 'multi retrieval',
            'targets': [{
                'num': 1,
                'shape': 'soccer_ball',
                'scale': 1,
                'position': {'x': 2, 'y': 0, 'z': 2},
                'rotation': {'x': 0, 'y': 0, 'z': 0},
                'labels': 'target_1'
            }, {
                'num': 8,
                'shape': 'soccer_ball',
                'scale': 1,
                'keyword_location': {
                    'keyword': 'adjacent',
                    'relative_object_label': 'target_1',
                    'adjacent_distance': [
                        {'x': 0, 'z': 0.1},
                        {'x': 0.1, 'z': 0.1},
                        {'x': 0.1, 'z': 0},
                        {'x': 0.1, 'z': -0.1},
                        {'x': 0, 'z': -0.1},
                        {'x': -0.1, 'z': -0.1},
                        {'x': -0.1, 'z': 0},
                        {'x': -0.1, 'z': 0.1}
                    ]
                }
            }]
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert len(scene.objects) == 9
    target_1 = scene.objects[0]
    assert target_1['type'] == 'soccer_ball'
    assert target_1['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    position_1 = target_1['shows'][0]['position']
    assert position_1 == {'x': 2, 'y': 0.11, 'z': 2}
    rotation_1 = target_1['shows'][0]['rotation']
    assert rotation_1 == {'x': 0, 'y': 0, 'z': 0}
    diff_x = 0.32
    diff_z = 0.32
    for target_i in scene.objects[1:]:
        assert target_i['type'] == 'soccer_ball'
        assert target_i['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
        position_i = target_i['shows'][0]['position']
        rotation_i = target_i['shows'][0]['rotation']
        assert (
            position_i['x'] == pytest.approx(position_1['x'] - diff_x) or
            position_i['x'] == pytest.approx(position_1['x']) or
            position_i['x'] == pytest.approx(position_1['x'] + diff_x)
        )
        assert (
            position_i['z'] == pytest.approx(position_1['z'] - diff_z) or
            position_i['z'] == pytest.approx(position_1['z']) or
            position_i['z'] == pytest.approx(position_1['z'] + diff_z)
        )
        assert rotation_i == rotation_1


def test_global_settings_identical_targets_without_error():
    component = GlobalSettingsComponent({
        'goal': {
            'category': 'multi retrieval',
            'targets': [{
                'num': 1,
                'shape': 'soccer_ball',
                'scale': 2,
                'labels': 'target_1'
            }, {
                'num': 4,
                'identical_to': 'target_1'
            }]
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert len(scene.objects) == 5
    target_1 = scene.objects[0]
    scale_1 = target_1['shows'][0]['scale']
    assert target_1['type'] == 'soccer_ball'
    assert target_1['shows'][0]['scale'] == {'x': 2, 'y': 2, 'z': 2}
    for target_i in scene.objects[1:]:
        scale_i = target_i['shows'][0]['scale']
        assert target_1['type'] == target_i['type']
        assert scale_1 == scale_i


def test_global_settings_forced_choice_multi_retrieval_target_left():
    scene = prior_scene()
    ball_1 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': -1, 'y': 0.11, 'z': 2}}
    )
    scene.objects = [ball_1]
    component = GlobalSettingsComponent({
        'forced_choice_multi_retrieval_target': 'soccer_ball'
    })
    scene = component.update_ile_scene(scene)
    assert scene.goal == {'metadata': {}}
    scene = component.run_actions_at_end_of_scene_generation(scene)
    assert len(scene.objects) == 1
    assert scene.goal['category'] == 'multi retrieval'
    assert scene.goal['description']
    assert scene.goal['metadata'] == {'targets': [
        {'id': scene.objects[0]['id']}
    ]}


def test_global_settings_forced_choice_multi_retrieval_target_right():
    scene = prior_scene()
    ball_1 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': 1, 'y': 0.11, 'z': 2}}
    )
    ball_2 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': -1, 'y': 0.11, 'z': 2}}
    )
    ball_3 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': 2, 'y': 0.11, 'z': -1}}
    )
    scene.objects = [ball_1, ball_2, ball_3]
    component = GlobalSettingsComponent({
        'forced_choice_multi_retrieval_target': 'soccer_ball'
    })
    scene = component.update_ile_scene(scene)
    assert scene.goal == {'metadata': {}}
    scene = component.run_actions_at_end_of_scene_generation(scene)
    assert len(scene.objects) == 3
    assert scene.goal['category'] == 'multi retrieval'
    assert scene.goal['description']
    assert scene.goal['metadata'] == {'targets': [
        {'id': scene.objects[0]['id']},
        {'id': scene.objects[2]['id']}
    ]}


def test_global_settings_forced_choice_multi_retrieval_target_pickup():
    scene = prior_scene()
    ball_1 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': 1, 'y': 0.11, 'z': 2}}
    )
    ball_2 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': -1, 'y': 0.11, 'z': 2}}
    )
    ball_3 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': 2, 'y': 0.11, 'z': -1}}
    )
    ball_1['moves'] = [{'vector': {'y': 0.25}}]
    ball_3['moves'] = [{'vector': {'y': -0.25}}, {'vector': {'y': 0.25}}]
    scene.objects = [ball_1, ball_2, ball_3]
    component = GlobalSettingsComponent({
        'forced_choice_multi_retrieval_target': 'soccer_ball'
    })
    scene = component.update_ile_scene(scene)
    assert scene.goal == {'metadata': {}}
    scene = component.run_actions_at_end_of_scene_generation(scene)
    assert len(scene.objects) == 3
    assert scene.goal['category'] == 'multi retrieval'
    assert scene.goal['description']
    assert scene.goal['metadata'] == {'targets': [
        {'id': scene.objects[1]['id']}
    ]}


def test_global_settings_forced_choice_multi_retrieval_target_equal():
    scene = prior_scene()
    ball_1 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': 1, 'y': 0.11, 'z': 2}}
    )
    ball_2 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': -1, 'y': 0.11, 'z': 2}}
    )
    scene.objects = [ball_1, ball_2]
    component = GlobalSettingsComponent({
        'forced_choice_multi_retrieval_target': 'soccer_ball'
    })
    with pytest.raises(ILEException):
        component.run_actions_at_end_of_scene_generation(scene)
