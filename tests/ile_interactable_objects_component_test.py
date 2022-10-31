import pytest

from generator import FULL_TYPE_LIST, definitions, geometry, materials
from ideal_learning_env import (
    ILEException,
    ILESharedConfiguration,
    InteractableObjectConfig,
    MinMaxInt,
    ObjectRepository,
    RandomInteractableObjectsComponent,
    RandomKeywordObjectsComponent,
    SpecificInteractableObjectsComponent
)
from ideal_learning_env.numerics import VectorFloatConfig

from .ile_helper import (
    prior_scene,
    prior_scene_custom_size,
    prior_scene_custom_start,
    prior_scene_with_target,
    prior_scene_with_targets,
    prior_scene_with_wall
)


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


def test_specific_objects_defaults():
    component = SpecificInteractableObjectsComponent({})
    assert component.specific_interactable_objects is None

    scene = component.update_ile_scene(prior_scene())
    objs = scene.objects
    assert isinstance(objs, list)
    for obj in objs:
        assert obj['debug']['random_position']


def test_specific_objects_single():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {}
    })
    print(component)
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig)
    sio = component.specific_interactable_objects
    assert sio.material is None
    assert sio.num == 1
    assert sio.shape is None
    assert sio.scale is None
    assert sio.rotation is None
    assert sio.position is None

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 1
    assert scene.objects[0]['debug']['random_position']


def test_specific_objects_on_lava_fail():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "position": {
                "x": 2,
                "y": 0,
                "z": 2
            }
        }
    })
    scene = prior_scene()
    scene.lava = [{'x': 2, 'z': 2}]
    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_specific_objects_on_holes_fail():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "position": {
                "x": 1,
                "y": 0,
                "z": -3
            }
        }
    })
    scene = prior_scene()
    scene.holes = [{'x': 1, 'z': -3}]
    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_specific_objects_array_single():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{}]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 1
    obj = component.specific_interactable_objects[0]
    assert obj.num == 1
    assert obj.material is None
    assert obj.position is None
    assert obj.rotation is None
    assert obj.scale is None
    assert obj.shape is None

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 1
    obj = scene.objects[0]
    assert 'id' in obj
    assert 'mass' in obj
    assert 'type' in obj
    assert obj['type'] in FULL_TYPE_LIST
    assert 'materials' in obj
    assert isinstance(obj['materials'], list)
    if len(obj['materials']) > 0:
        assert (
            obj['materials'][0] in materials.ALL_CONFIGURABLE_MATERIAL_STRINGS
        )
    show = obj['shows'][0]
    # The soccer_ball has scale restrictions so test them specifically.
    if obj['type'] == 'soccer_ball':
        assert 1 <= show['scale']['x'] == show['scale']['z'] <= 3
    else:
        assert show['scale']['x'] == show['scale']['z'] == 1
    original_rotation = obj['debug']['originalRotation']['y']
    assert 0 <= (show['rotation']['y'] - original_rotation) <= 360
    assert -10 <= show['position']['x'] < 10
    assert -10 <= show['position']['z'] < 10
    assert len(scene.objects) == 1
    assert scene.objects[0]['debug']['random_position']


def test_specific_objects_array_single_num_range():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": {
                "min": 2,
                "max": 4
            }
        }]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 1
    obj = component.specific_interactable_objects[0]
    assert obj.num.min == 2
    assert obj.num.max == 4
    assert obj.material is None
    assert obj.position is None
    assert obj.rotation is None
    assert obj.scale is None
    assert obj.shape is None

    scene = component.update_ile_scene(prior_scene_custom_size(25, 25))

    assert isinstance(scene.objects, list)
    assert 2 <= len(scene.objects) <= 4
    for obj in scene.objects:
        assert 'id' in obj
        assert 'mass' in obj
        assert 'type' in obj
        assert obj['type'] in FULL_TYPE_LIST
        assert 'materials' in obj
        assert isinstance(obj['materials'], list)
        if len(obj['materials']) > 0:
            assert (
                obj['materials'][0] in
                materials.ALL_CONFIGURABLE_MATERIAL_STRINGS
            )
        show = obj['shows'][0]
        # The soccer_ball has scale restrictions so test them specifically.
        if obj['type'] == 'soccer_ball':
            assert 1 <= show['scale']['x'] == show['scale']['z'] <= 3
        else:
            assert show['scale']['x'] == show['scale']['z'] == 1
        original_rotation = obj['debug']['originalRotation']['y']
        assert 0 <= (show['rotation']['y'] - original_rotation) <= 360
        assert -25 <= show['position']['x'] < 25
        assert -25 <= show['position']['z'] < 25
        assert obj['debug']['random_position']


def test_specific_objects_array_single_mat_list_mixed():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 5,
            "material": [
                "PLASTIC_MATERIALS",
                "AI2-THOR/Materials/Metals/Brass 1"
            ]
        }]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 1
    obj = component.specific_interactable_objects[0]
    assert obj.num == 5
    assert isinstance(obj.material, list)

    scene = component.update_ile_scene(prior_scene())

    material_options = ["AI2-THOR/Materials/Metals/Brass 1"]

    for mat_color in materials.PLASTIC_MATERIALS:
        material_options.append(mat_color[0])

    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 5
    for obj in scene.objects:
        assert 'materials' in obj
        assert isinstance(obj['materials'], list)
        assert obj['debug']['random_position']
        for mat in obj['materials']:
            assert mat in material_options


def test_specific_objects_single_shape():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "num": 7,
            "shape": "crayon_blue"
        }
    })
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig)
    obj = component.specific_interactable_objects
    assert obj.num == 7
    assert isinstance(obj.shape, str)
    assert obj.shape == "crayon_blue"

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 7
    for obj in scene.objects:
        assert obj['debug']['random_position']
        assert 'type' in obj
        assert isinstance(obj['type'], str)
        assert obj['type'] == "crayon_blue"


def test_specific_objects_excluded_type():
    ILESharedConfiguration.get_instance().set_excluded_shapes(['ball'])
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "num": 1
        }
    })
    # Test a bunch of times to make sure.
    for _ in range(100):
        scene = component.update_ile_scene(prior_scene())
        assert scene.objects[0]['type'] != 'ball'


def test_specific_objects_specific_type_is_excluded():
    ILESharedConfiguration.get_instance().set_excluded_shapes(['ball'])
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "num": 1,
            "shape": "ball"
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert scene.objects[0]['type'] == 'ball'


def test_specific_objects_not_random_position():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "shape": "turtle_on_wheels",
            "num": 1,
            "position": {
                "x": 2,
                "y": 0,
                "z": 2
            }
        }, {
            "shape": "table_2",
            "num": 1,
            "position": {
                "x": -3,
                "y": 0,
                "z": -3
            }
        }]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 2
    obj = component.specific_interactable_objects[0]
    assert obj.num == 1
    assert obj.position == VectorFloatConfig(2, 0, 2)
    obj = component.specific_interactable_objects[1]
    assert obj.num == 1
    assert obj.position == VectorFloatConfig(-3, 0, -3)

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 2
    objs = scene.objects
    obj = objs[0]
    pos = obj['shows'][0]['position']
    assert pos['x'] == 2
    assert pos['z'] == 2
    assert not obj['debug']['random_position']

    obj = objs[1]
    pos = obj['shows'][0]['position']
    assert pos['x'] == -3
    # Used to fail when object was wardrobe which has an offset
    assert pos['z'] == -3
    assert not obj['debug']['random_position']


def test_specific_objects_position_relative_to_x():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "num": 1,
            "shape": "turtle_on_wheels",
            "position": {
                "x": 3,
                "y": 0,
                "z": 4
            },
            "position_relative": {
                "label": "test_wall",
                "use_x": True
            }
        }
    })
    config = component.specific_interactable_objects
    assert config.num == 1
    assert config.shape == 'turtle_on_wheels'
    assert config.position == VectorFloatConfig(3, 0, 4)
    assert config.position_relative.label == 'test_wall'
    assert config.position_relative.use_x is True

    scene = component.update_ile_scene(prior_scene_with_wall())
    assert len(scene.objects) == 2

    wall = scene.objects[0]
    assert wall['id'] == 'occluding_wall'
    assert wall['type'] == 'cube'
    assert wall['shows'][0]['position']['x'] == -2
    assert wall['shows'][0]['position']['z'] == 1

    turtle = scene.objects[1]
    assert turtle['type'] == 'turtle_on_wheels'
    assert turtle['shows'][0]['position']['x'] == -2
    assert turtle['shows'][0]['position']['z'] == 4
    assert not turtle['debug']['random_position']


def test_specific_objects_position_relative_to_z():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "num": 1,
            "shape": "turtle_on_wheels",
            "position": {
                "x": 3,
                "y": 0,
                "z": 4
            },
            "position_relative": {
                "label": "test_wall",
                "use_z": True
            }
        }
    })
    config = component.specific_interactable_objects
    assert config.num == 1
    assert config.shape == 'turtle_on_wheels'
    assert config.position == VectorFloatConfig(3, 0, 4)
    assert config.position_relative.label == 'test_wall'
    assert config.position_relative.use_z is True

    scene = component.update_ile_scene(prior_scene_with_wall())
    assert len(scene.objects) == 2

    wall = scene.objects[0]
    assert wall['id'] == 'occluding_wall'
    assert wall['type'] == 'cube'
    assert wall['shows'][0]['position']['x'] == -2
    assert wall['shows'][0]['position']['z'] == 1

    turtle = scene.objects[1]
    assert turtle['type'] == 'turtle_on_wheels'
    assert turtle['shows'][0]['position']['x'] == 3
    assert turtle['shows'][0]['position']['z'] == 1
    assert not turtle['debug']['random_position']


def test_specific_objects_position_relative_with_adjustment():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "num": 1,
            "shape": "turtle_on_wheels",
            "position_relative": {
                "add_x": 0.12,
                "add_z": -0.34,
                "label": "test_wall",
                "use_x": True,
                "use_z": True
            }
        }
    })
    config = component.specific_interactable_objects
    assert config.num == 1
    assert config.shape == 'turtle_on_wheels'
    assert config.position_relative.add_x == 0.12
    assert config.position_relative.add_z == -0.34
    assert config.position_relative.label == 'test_wall'
    assert config.position_relative.use_x is True
    assert config.position_relative.use_z is True

    scene = component.update_ile_scene(prior_scene_with_wall())
    assert len(scene.objects) == 2

    wall = scene.objects[0]
    assert wall['id'] == 'occluding_wall'
    assert wall['type'] == 'cube'
    assert wall['shows'][0]['position']['x'] == -2
    assert wall['shows'][0]['position']['z'] == 1

    turtle = scene.objects[1]
    assert turtle['type'] == 'turtle_on_wheels'
    assert turtle['shows'][0]['position']['x'] == pytest.approx(-1.88)
    assert turtle['shows'][0]['position']['z'] == pytest.approx(0.66)
    assert not turtle['debug']['random_position']


def test_specific_objects_position_relative_to_x_by_view_angle():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "num": 1,
            "shape": "turtle_on_wheels",
            "position": {
                "z": 2
            },
            "position_relative": {
                "label": "test_wall",
                "use_x": True,
                "view_angle_x": True
            }
        }
    })
    config = component.specific_interactable_objects
    assert config.num == 1
    assert config.shape == 'turtle_on_wheels'
    assert config.position == VectorFloatConfig(None, None, 2)
    assert config.position_relative.label == 'test_wall'
    assert config.position_relative.use_x is True
    assert config.position_relative.view_angle_x is True

    scene = component.update_ile_scene(prior_scene_with_wall(start_z=-4))
    assert len(scene.objects) == 2

    wall = scene.objects[0]
    assert wall['id'] == 'occluding_wall'
    assert wall['type'] == 'cube'
    assert wall['shows'][0]['position']['x'] == -2
    assert wall['shows'][0]['position']['z'] == 1

    turtle = scene.objects[1]
    assert turtle['type'] == 'turtle_on_wheels'
    assert turtle['shows'][0]['position']['x'] == pytest.approx(-2.4)
    assert turtle['shows'][0]['position']['z'] == 2
    assert not turtle['debug']['random_position']


def test_specific_objects_position_relative_to_multiple():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "shape": "ball",
            "labels": "test_ball",
            "position": {
                "x": 3,
                "y": 0,
                "z": 4
            }
        }, {
            "num": 1,
            "shape": "turtle_on_wheels",
            "position_relative": [{
                "label": "test_wall",
                "use_x": True
            }, {
                "label": "test_ball",
                "use_z": True
            }]
        }]
    })
    config = component.specific_interactable_objects
    assert config[0].num == 1
    assert config[0].shape == 'ball'
    assert config[0].labels == 'test_ball'
    assert config[0].position == VectorFloatConfig(3, 0, 4)
    assert config[1].num == 1
    assert config[1].shape == 'turtle_on_wheels'
    assert config[1].position_relative[0].label == 'test_wall'
    assert config[1].position_relative[0].use_x is True
    assert config[1].position_relative[1].label == 'test_ball'
    assert config[1].position_relative[1].use_z is True

    scene = component.update_ile_scene(prior_scene_with_wall())
    assert len(scene.objects) == 3

    wall = scene.objects[0]
    assert wall['id'] == 'occluding_wall'
    assert wall['type'] == 'cube'
    assert wall['shows'][0]['position']['x'] == -2
    assert wall['shows'][0]['position']['z'] == 1

    ball = scene.objects[1]
    assert ball['type'] == 'ball'
    assert ball['shows'][0]['position']['x'] == 3
    assert ball['shows'][0]['position']['z'] == 4

    turtle = scene.objects[2]
    assert turtle['type'] == 'turtle_on_wheels'
    assert turtle['shows'][0]['position']['x'] == -2
    assert turtle['shows'][0]['position']['z'] == 4
    assert not turtle['debug']['random_position']


def test_specific_objects_position_relative_to_multiple_override():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "shape": "ball",
            "labels": "test_ball",
            "position": {
                "x": 3,
                "y": 0,
                "z": 4
            }
        }, {
            "num": 1,
            "shape": "turtle_on_wheels",
            "position": {
                "z": 0
            },
            "position_relative": [{
                "label": "test_wall",
                "use_x": True
            }, {
                "label": "test_ball",
                "use_x": True
            }]
        }]
    })
    config = component.specific_interactable_objects
    assert config[0].num == 1
    assert config[0].shape == 'ball'
    assert config[0].labels == 'test_ball'
    assert config[0].position == VectorFloatConfig(3, 0, 4)
    assert config[1].num == 1
    assert config[1].shape == 'turtle_on_wheels'
    assert config[1].position == VectorFloatConfig(None, None, 0)
    assert config[1].position_relative[0].label == 'test_wall'
    assert config[1].position_relative[0].use_x is True
    assert config[1].position_relative[1].label == 'test_ball'
    assert config[1].position_relative[1].use_x is True

    scene = component.update_ile_scene(prior_scene_with_wall())
    assert len(scene.objects) == 3

    wall = scene.objects[0]
    assert wall['id'] == 'occluding_wall'
    assert wall['type'] == 'cube'
    assert wall['shows'][0]['position']['x'] == -2
    assert wall['shows'][0]['position']['z'] == 1

    ball = scene.objects[1]
    assert ball['type'] == 'ball'
    assert ball['shows'][0]['position']['x'] == 3
    assert ball['shows'][0]['position']['z'] == 4

    turtle = scene.objects[2]
    assert turtle['type'] == 'turtle_on_wheels'
    assert turtle['shows'][0]['position']['x'] == 3
    assert turtle['shows'][0]['position']['z'] == 0
    assert not turtle['debug']['random_position']


def test_specific_objects_array_multiple_scale():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "scale": 1.5
        }, {
            "num": 3,
            "scale": {
                "x": 2,
                "y": [0.5, 1.3],
                "z": {
                    "min": 0,
                    "max": 0.5
                }
            }
        }]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 2
    obj = component.specific_interactable_objects[0]
    assert obj.num == 1
    assert obj.scale == 1.5
    obj = component.specific_interactable_objects[1]
    assert obj.num == 3
    s = obj.scale
    assert s.x == 2
    assert s.y == [0.5, 1.3]
    assert s.z.min == 0
    assert s.z.max == 0.5

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 4
    objs = scene.objects
    obj = objs[0]
    s = obj['shows'][0]['scale']
    is_cylinder = (
        obj['type'] in ['cylinder', 'hex_cylinder', 'decagon_cylinder']
    )
    print(f'type={obj["type"]}')
    assert isinstance(s, dict)
    assert s['x'] == 1.5
    assert (s['y'] * (1 if not is_cylinder else 2)) == 1.5
    assert s['z'] == 1.5
    for i in range(3):
        obj = objs[i + 1]
        s = obj['shows'][0]['scale']
        is_cylinder = (
            obj['type'] in ['cylinder', 'hex_cylinder', 'decagon_cylinder']
        )
        print(f'type={obj["type"]}')
        # The soccer_ball has scale restrictions, so just ignore it.
        if obj['type'] != 'soccer_ball':
            assert s['x'] == 2
            assert (s['y'] * (1 if not is_cylinder else 2)) in [0.5, 1.3]
            assert 0 <= s['z'] <= 0.5
        assert obj['debug']['random_position']


def test_specific_objects_array_multiple_position_rotation():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "position": {
                "x": 1.5
            }
        }, {
            "num": 3,
            "position": {
                "x": 2,
                "y": .1,
                "z": {
                    "min": -5,
                    "max": 3.2
                }
            },
            "rotation": {
                "y": {
                    "min": 40,
                    "max": 279
                }
            }
        }]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 2
    obj = component.specific_interactable_objects[0]
    assert obj.num == 1
    assert obj.position.x == 1.5
    obj = component.specific_interactable_objects[1]
    assert obj.num == 3
    p = obj.position
    assert p.x == 2
    assert p.y == 0.1
    assert p.z.min == -5
    assert p.z.max == 3.2

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 4
    objs = scene.objects
    obj = objs[0]
    show = obj['shows'][0]
    assert 'position' in show
    p = show['position']
    assert isinstance(p, dict)
    assert p['x'] == 1.5
    assert p['y'] >= 0
    assert -5 <= p['z'] <= 5
    for i in range(3):
        obj = objs[i + 1]
        p = obj['shows'][0]['position']
        assert p['x'] == 2
        assert p['y'] >= 0.1
        assert -5 <= p['z'] <= 3.2
        r = obj['shows'][0]['rotation']
        plus = obj['debug']['originalRotation']['y']
        assert (40 + plus) <= r['y'] <= (279 + plus)
    for obj in objs:
        assert obj['debug']['random_position']


def test_specific_objects_array_multiple():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{}, {}]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 2
    for obj in component.specific_interactable_objects:
        assert obj.num == 1
        assert obj.material is None
        assert obj.position is None
        assert obj.rotation is None
        assert obj.scale is None
        assert obj.shape is None

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 2
    for obj in scene.objects:
        assert 'id' in obj
        assert 'mass' in obj
        assert 'type' in obj
        assert obj['type'] in FULL_TYPE_LIST
        assert 'materials' in obj
        print(obj['materials'])
        assert isinstance(obj['materials'], list)
        for mat in obj['materials']:
            assert mat in materials.ALL_CONFIGURABLE_MATERIAL_STRINGS
        show = obj['shows'][0]
        # The soccer_ball has scale restrictions so test them specifically.
        if obj['type'] == 'soccer_ball':
            assert 1 <= show['scale']['x'] == show['scale']['z'] <= 3
        else:
            assert show['scale']['x'] == show['scale']['z'] == 1
        original_rotation = obj['debug']['originalRotation']['y']
        assert 0 <= (show['rotation']['y'] - original_rotation) <= 360
        assert -10 <= show['position']['x'] < 10
        assert -10 <= show['position']['z'] < 10
        assert obj['debug']['random_position']


def test_specific_objects_num_targets_minus_zero_with_single_target():
    component = SpecificInteractableObjectsComponent({
        'specific_interactable_objects': {
            'num_targets_minus': 0,
            'shape': 'duck_on_wheels'
        }
    })
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig
    )
    config = component.specific_interactable_objects
    assert config.num_targets_minus == 0
    assert config.shape == 'duck_on_wheels'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 2
    assert scene.objects[0]['type'] == 'soccer_ball'
    assert scene.objects[1]['type'] == 'duck_on_wheels'


def test_specific_objects_num_targets_minus_one_with_single_target():
    component = SpecificInteractableObjectsComponent({
        'specific_interactable_objects': {
            'num_targets_minus': 1,
            'shape': 'duck_on_wheels'
        }
    })
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig
    )
    config = component.specific_interactable_objects
    assert config.num_targets_minus == 1
    assert config.shape == 'duck_on_wheels'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 1
    assert scene.objects[0]['type'] == 'soccer_ball'


def test_specific_objects_num_targets_minus_two_with_single_target():
    component = SpecificInteractableObjectsComponent({
        'specific_interactable_objects': {
            'num_targets_minus': 2,
            'shape': 'duck_on_wheels'
        }
    })
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig
    )
    config = component.specific_interactable_objects
    assert config.num_targets_minus == 2
    assert config.shape == 'duck_on_wheels'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 1
    assert scene.objects[0]['type'] == 'soccer_ball'


def test_specific_objects_num_targets_minus_zero_with_multiple_targets():
    component = SpecificInteractableObjectsComponent({
        'specific_interactable_objects': {
            'num_targets_minus': 0,
            'shape': 'duck_on_wheels'
        }
    })
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig
    )
    config = component.specific_interactable_objects
    assert config.num_targets_minus == 0
    assert config.shape == 'duck_on_wheels'

    scene = component.update_ile_scene(prior_scene_with_targets())
    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 4
    assert scene.objects[0]['type'] == 'soccer_ball'
    assert scene.objects[1]['type'] == 'soccer_ball'
    assert scene.objects[2]['type'] == 'duck_on_wheels'
    assert scene.objects[3]['type'] == 'duck_on_wheels'


def test_specific_objects_num_targets_minus_one_with_multiple_targets():
    component = SpecificInteractableObjectsComponent({
        'specific_interactable_objects': {
            'num_targets_minus': 1,
            'shape': 'duck_on_wheels'
        }
    })
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig
    )
    config = component.specific_interactable_objects
    assert config.num_targets_minus == 1
    assert config.shape == 'duck_on_wheels'

    scene = component.update_ile_scene(prior_scene_with_targets())
    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 3
    assert scene.objects[0]['type'] == 'soccer_ball'
    assert scene.objects[1]['type'] == 'soccer_ball'
    assert scene.objects[2]['type'] == 'duck_on_wheels'


def test_specific_objects_num_targets_minus_two_with_multiple_targets():
    component = SpecificInteractableObjectsComponent({
        'specific_interactable_objects': {
            'num_targets_minus': 2,
            'shape': 'duck_on_wheels'
        }
    })
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig
    )
    config = component.specific_interactable_objects
    assert config.num_targets_minus == 2
    assert config.shape == 'duck_on_wheels'

    scene = component.update_ile_scene(prior_scene_with_targets())
    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 2
    assert scene.objects[0]['type'] == 'soccer_ball'
    assert scene.objects[1]['type'] == 'soccer_ball'


def test_random_interactable_objects_config_component():
    component = RandomInteractableObjectsComponent({})
    assert component.num_random_interactable_objects is None

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) < 31


def test_random_interactable_objects_config_component_configured():
    component = RandomInteractableObjectsComponent({
        'num_random_interactable_objects': 5
    })
    assert component.num_random_interactable_objects == 5

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 5
    for obj in objs:
        assert obj['debug']['random_position']


def test_random_interactable_objects_config_component_excluded_type():
    ILESharedConfiguration.get_instance().set_excluded_shapes(['ball'])
    component = RandomInteractableObjectsComponent({
        'num_random_interactable_objects': 1
    })
    # Test a bunch of times to make sure.
    for _ in range(100):
        scene = component.update_ile_scene(prior_scene())
        assert scene.objects[0]['type'] != 'ball'


def test_random_interactable_objects_config_component_excluded_type_fail():
    ILESharedConfiguration.get_instance().set_excluded_shapes(FULL_TYPE_LIST)
    component = RandomInteractableObjectsComponent({
        'num_random_interactable_objects': 1
    })
    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene())


def test_random_interactable_objects_config_component_configured_min_max():
    component = RandomInteractableObjectsComponent({
        'num_random_interactable_objects': MinMaxInt(1, 4)
    })
    assert component.num_random_interactable_objects == MinMaxInt(1, 4)

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert 1 <= len(objs) <= 4


def test_random_interactable_objects_config_component_fail():
    with pytest.raises(ILEException):
        RandomInteractableObjectsComponent({
            'num_random_interactable_objects': ''
        })


def test_random_interactable_objects_config_component_overlap():
    component = RandomInteractableObjectsComponent({
        'num_random_interactable_objects': 10
    })
    assert component.num_random_interactable_objects == 10

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    for obj_1 in objs:
        bounds = [
            obj_2['shows'][0]['boundingBox']
            for obj_2 in objs
            if obj_1['id'] != obj_2['id']
        ]
        assert obj_1['debug']['random_position']
        assert geometry.validate_location_rect(
            obj_1['shows'][0]['boundingBox'],
            vars(scene.performer_start.position),
            bounds,
            vars(scene.room_dimensions)
        )


@pytest.mark.slow
def test_random_keyword_objects_types_none():
    component = RandomKeywordObjectsComponent({})
    assert component.keyword_objects is None

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert 2 <= len(objs) <= 14
    for obj in objs:
        assert obj['debug']['random_position']


def test_random_keyword_objects_types_containers():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'containers',
            'num': 4,
        }
    })
    assert component.keyword_objects.keyword == 'containers'
    assert component.keyword_objects.num == 4

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 4
    for obj in objs:
        assert obj['receptacle']
        assert obj['debug']['random_position']

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 4 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS))


def test_random_keyword_objects_types_containers_excluded_type():
    ILESharedConfiguration.get_instance().set_excluded_shapes(['chest_1'])
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'containers',
            'num': 1
        }
    })

    # Test a bunch of times to make sure.
    for _ in range(100):
        scene = component.update_ile_scene(prior_scene())
        assert scene.objects[0]['type'] != 'chest_1'


def test_random_keyword_objects_types_containers_contain_without_target():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'containers_can_contain_target',
            'num': 4
        }]
    })
    assert (component.keyword_objects[0].keyword ==
            'containers_can_contain_target')
    assert component.keyword_objects[0].num == 4
    assert component._delayed_actions == []

    component.update_ile_scene(prior_scene())
    assert len(component._delayed_actions) == 4


def test_random_keyword_objects_types_containers_contain_target():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'containers_can_contain_target',
            'num': 2
        }]
    })
    assert (component.keyword_objects[0].keyword ==
            'containers_can_contain_target')
    assert component.keyword_objects[0].num == 2

    scene = component.update_ile_scene(prior_scene_with_target())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 3
    for i, obj in enumerate(objs):
        if i != 0:
            assert obj['receptacle']
            assert obj['debug']['random_position']

    assert 2 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 2 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS))
    assert 2 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS_CAN_CONTAIN_TARGET))  # noqa


def test_random_keyword_objects_types_containers_min_max():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'containers',
            'num': {
                'min': 1,
                'max': 3
            }
        }]
    })
    assert component.keyword_objects[0].keyword == 'containers'
    assert component.keyword_objects[0].num.min == 1
    assert component.keyword_objects[0].num.max == 3

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert 1 <= len(objs) <= 3
    for obj in objs:
        assert obj['receptacle']
        assert obj['debug']['random_position']

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 1 <= len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS)) <= 3


def test_random_keyword_objects_types_asymmetric_containers():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'asymmetric_containers',
            'num': 6,
        }
    })
    assert component.keyword_objects.keyword == 'asymmetric_containers'
    assert component.keyword_objects.num == 6

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 6
    for obj in objs:
        assert obj['type'].startswith('container_asymmetric_')
        assert obj['receptacle']
        assert obj['debug']['random_position']
        assert not obj.get('openable', False)

    object_repository = ObjectRepository.get_instance()
    assert 1 == len(object_repository._labeled_object_store)
    assert 6 == len(object_repository.get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_ASYMMETRIC_CONTAINERS
    ))


def test_random_keyword_objects_types_bin_containers():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'bins',
            'num': 6,
        }
    })
    assert component.keyword_objects.keyword == 'bins'
    assert component.keyword_objects.num == 6

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 6
    for obj in objs:
        assert (
            obj['type'].startswith('bowl_') or obj['type'].startswith('cup_')
        )
        assert obj['receptacle']
        assert obj['debug']['random_position']
        assert not obj.get('openable', False)

    object_repository = ObjectRepository.get_instance()
    assert 1 == len(object_repository._labeled_object_store)
    assert 6 == len(object_repository.get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_BINS
    ))


def test_random_keyword_objects_types_open_topped_containers():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'open_topped_containers',
            'num': 6,
        }
    })
    assert component.keyword_objects.keyword == 'open_topped_containers'
    assert component.keyword_objects.num == 6

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 6
    for obj in objs:
        assert (
            obj['type'].startswith('bowl_') or
            obj['type'].startswith('cup_') or
            obj['type'].startswith('container_asymmetric_') or
            obj['type'].startswith('container_symmetric_')
        )
        assert obj['receptacle']
        assert obj['debug']['random_position']
        assert not obj.get('openable', False)

    object_repository = ObjectRepository.get_instance()
    assert 1 == len(object_repository._labeled_object_store)
    assert 6 == len(object_repository.get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_OPEN_TOPPED_CONTAINERS
    ))


def test_random_keyword_objects_types_symmetric_containers():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'symmetric_containers',
            'num': 6,
        }
    })
    assert component.keyword_objects.keyword == 'symmetric_containers'
    assert component.keyword_objects.num == 6

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 6
    for obj in objs:
        assert obj['type'].startswith('container_symmetric_')
        assert obj['receptacle']
        assert obj['debug']['random_position']
        assert not obj.get('openable', False)

    object_repository = ObjectRepository.get_instance()
    assert 1 == len(object_repository._labeled_object_store)
    assert 6 == len(object_repository.get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_SYMMETRIC_CONTAINERS
    ))


@pytest.mark.slow
def test_random_keyword_objects_types_confusors():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'confusors',
            'num': {
                'min': 2,
                'max': 4
            }
        }]
    })
    assert component.keyword_objects[0].keyword == 'confusors'
    assert component.keyword_objects[0].num.min == 2
    assert component.keyword_objects[0].num.max == 4

    scene = component.update_ile_scene(prior_scene_with_target())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert 3 <= len(objs) <= 5
    goal = None
    for idx, obj in enumerate(objs):
        if idx == 0:
            # assume this is the goal
            assert obj['type'] == 'soccer_ball'
            goal = obj
            continue
        assert obj['moveable']
        sim_color = definitions.is_similar_except_in_color(obj, goal)
        sim_shape = definitions.is_similar_except_in_shape(obj, goal)
        sim_size = definitions.is_similar_except_in_size(obj, goal)
        assert sim_color or sim_shape or sim_size
        assert obj['debug']['random_position']

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 2 <= len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONFUSORS)) <= 4


@pytest.mark.slow
def test_random_keyword_objects_types_obstacles():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'obstacles',
            'num': 2
        }]
    })
    assert component.keyword_objects[0].keyword == 'obstacles'
    assert component.keyword_objects[0].num == 2

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 2
    for obj in objs:
        assert obj['debug']['random_position']

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 1 <= len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_OBSTACLES)) <= 2


@pytest.mark.slow
def test_random_keyword_objects_types_obstacles_excluded_type():
    ILESharedConfiguration.get_instance().set_excluded_shapes(['chair_1'])
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'obstacles',
            'num': 1
        }
    })

    # Test a bunch of times to make sure.
    for _ in range(100):
        scene = component.update_ile_scene(prior_scene())
        assert scene.objects[0]['type'] != 'chair_1'


@pytest.mark.slow
def test_random_keyword_objects_types_obstacles_with_target():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'obstacles',
            'num': 2
        }]
    })
    assert component.keyword_objects[0].keyword == 'obstacles'
    assert component.keyword_objects[0].num == 2

    scene = component.update_ile_scene(prior_scene_with_target())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 3
    assert objs[1]['debug']['random_position']
    assert objs[2]['debug']['random_position']

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 2 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_OBSTACLES))


@pytest.mark.slow
def test_random_keyword_objects_types_occluders():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'occluders',
            'num': 3
        }]
    })
    assert component.keyword_objects[0].keyword == 'occluders'
    assert component.keyword_objects[0].num == 3

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 3

    for obj in objs:
        assert obj['debug']['random_position']

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 3 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_OCCLUDERS))


def test_random_keyword_objects_types_occluders_excluded_type():
    ILESharedConfiguration.get_instance().set_excluded_shapes(['sofa_1'])
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'occluders',
            'num': 1
        }
    })

    # Test a bunch of times to make sure.
    for _ in range(100):
        scene = component.update_ile_scene(prior_scene())
        assert scene.objects[0]['type'] != 'sofa_1'


def test_random_keyword_objects_types_occluders_with_target():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'occluders',
            'num': 3
        }]
    })
    assert component.keyword_objects[0].keyword == 'occluders'
    assert component.keyword_objects[0].num == 3

    scene = component.update_ile_scene(prior_scene_with_target())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 4

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 3 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_OCCLUDERS))


def test_random_keyword_objects_types_context():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'context',
            'num': 5
        }
    })

    assert component.keyword_objects.keyword == 'context'
    assert component.keyword_objects.num == 5

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 5

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 5 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTEXT))


def test_random_keyword_objects_types_context_excluded_type():
    ILESharedConfiguration.get_instance().set_excluded_shapes(['ball'])
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'context',
            'num': 1
        }
    })

    # Test a bunch of times to make sure.
    for _ in range(100):
        scene = component.update_ile_scene(prior_scene())
        assert scene.objects[0]['type'] != 'ball'


def test_random_keyword_objects_types_occluder_front():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'containers',
            'num': 4,
            'keyword_location': {
                'keyword': 'front'
            }
        }
    })
    assert component.keyword_objects.keyword == 'containers'
    assert component.keyword_objects.num == 4

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 4
    for obj in objs:
        assert obj['receptacle']
        pos = obj['shows'][0]['position']
        assert pos['x'] == 0
        assert pos['z'] > 0
        assert obj['debug']['random_position']

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 4 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS))


def test_random_keyword_objects_types_context_in_containers():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'containers',
            'num': 1,
        }, {
            'keyword': 'context',
            'num': 1,
            'keyword_location': {
                'keyword': 'adjacent',
                'relative_object_label':
                RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS
            }}
        ]
    })
    assert component.keyword_objects[0].keyword == 'containers'
    assert component.keyword_objects[0].num == 1
    assert component.keyword_objects[1].keyword == 'context'
    assert component.keyword_objects[1].num == 1
    assert component.keyword_objects[1].keyword_location.keyword == 'adjacent'
    assert (
        component.keyword_objects[1].keyword_location.relative_object_label ==
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS
    )

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    objs = scene.objects
    assert len(objs) == 2
    assert objs[0]['receptacle']
    assert objs[0]['debug']['random_position']
    assert objs[1]['debug']['random_position']

    assert 2 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 1 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS))
    assert 1 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTEXT))


def test_random_keyword_objects_with_position():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'bins',
            'num': 1,
            'position': {'x': 0, 'y': 0, 'z': 0}
        }
    })
    assert component.keyword_objects.keyword == 'bins'
    assert component.keyword_objects.num == 1
    assert component.keyword_objects.position == (
        VectorFloatConfig(x=0, y=0, z=0)
    )

    scene = component.update_ile_scene(prior_scene_custom_start(0, -4))
    assert len(scene.objects) == 1
    assert scene.objects[0]['shows'][0]['position']['x'] == 0
    assert scene.objects[0]['shows'][0]['position']['z'] == 0


def test_random_keyword_objects_with_position_list():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'bins',
            'num': 4,
            'position': [
                {'x': 0, 'y': 0, 'z': 3},
                {'x': 3, 'y': 0, 'z': 0},
                {'x': 0, 'y': 0, 'z': -3},
                {'x': -3, 'y': 0, 'z': 0}
            ]
        }
    })
    assert component.keyword_objects.keyword == 'bins'
    assert component.keyword_objects.num == 4
    assert component.keyword_objects.position == [
        VectorFloatConfig(x=0, y=0, z=3),
        VectorFloatConfig(x=3, y=0, z=0),
        VectorFloatConfig(x=0, y=0, z=-3),
        VectorFloatConfig(x=-3, y=0, z=0)
    ]

    scene = component.update_ile_scene(prior_scene())
    assert len(scene.objects) == 4

    positions = {}
    for instance in scene.objects:
        position = instance['shows'][0]['position']
        positions[f'{position["x"]},{position["z"]}'] = True
    assert positions.get('0.0,3.0')
    assert positions.get('3.0,0.0')
    assert positions.get('0.0,-3.0')
    assert positions.get('-3.0,0.0')


def test_specific_objects_dimensions():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "shape": "chest_1",
            "dimensions": 1.0,
        }]})
    scene = component.update_ile_scene(prior_scene())
    obj = scene.objects[0]
    scale = obj['shows'][0]['scale']
    # The scale is the inverse of the dimenions listed in base_objects.py when
    # dimensions is 1.0
    assert scale['x'] == 1 / 0.83
    assert scale['y'] == 1 / 0.42
    assert scale['z'] == 1 / 0.55


def test_specific_objects_dimensions_and_scale():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "shape": "soccer_ball",
            "scale": {
                "x": 1,
                "y": 3,
                "z": 0.5
            },
            "dimensions": {
                "x": 0.33,
                "y": 0.44,
                "z": 0.55
            }
        }]})
    scene = component.update_ile_scene(prior_scene())
    obj = scene.objects[0]
    scale = obj['shows'][0]['scale']
    assert scale['x'] == pytest.approx(1.5)
    assert scale['y'] == pytest.approx(2)
    assert scale['z'] == pytest.approx(2.5)


def test_interactable_objects_with_identical_to_label():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "shape": "chest_1",
            "scale": 1,
            "material": ["UnityAssetStore/Baby_Room/Models/Materials/wood 1"],
            "labels": "obj_to_copy"
        }, {
            "num": 4,
            "identical_to": "obj_to_copy"
        }]
    })

    assert isinstance(
        component.specific_interactable_objects,
        list)
    assert len(component.specific_interactable_objects) == 2

    base_obj = component.specific_interactable_objects[0]
    assert isinstance(
        base_obj,
        InteractableObjectConfig)
    assert base_obj.num == 1
    assert isinstance(base_obj.shape, str)
    assert base_obj.shape == "chest_1"
    assert base_obj.material == [
        "UnityAssetStore/Baby_Room/Models/Materials/wood 1"]
    assert base_obj.scale == 1
    assert base_obj.labels == "obj_to_copy"

    copy_template = component.specific_interactable_objects[1]
    assert isinstance(
        copy_template,
        InteractableObjectConfig)
    assert copy_template.num == 4
    assert copy_template.identical_to == "obj_to_copy"

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 5
    for obj in scene.objects:
        assert obj['debug']['random_position']
        assert 'type' in obj
        assert isinstance(obj['type'], str)
        assert obj['type'] == "chest_1"
        assert 'scale' in obj['shows'][0]
        assert obj['shows'][0]['scale'] == {"x": 1, "y": 1, "z": 1}
        assert obj['materials'] == [
            "UnityAssetStore/Baby_Room/Models/Materials/wood 1"]


def test_interactable_objects_with_identical_except_color_label():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "shape": "chest_1",
            "scale": 1,
            "material": ["UnityAssetStore/Baby_Room/Models/Materials/wood 1"],
            "labels": "obj_to_copy"
        }, {
            "num": 4,
            "identical_except_color": "obj_to_copy"
        }]
    })

    assert isinstance(
        component.specific_interactable_objects,
        list)
    assert len(component.specific_interactable_objects) == 2

    base_obj = component.specific_interactable_objects[0]
    assert isinstance(
        base_obj,
        InteractableObjectConfig)
    assert base_obj.num == 1
    assert isinstance(base_obj.shape, str)
    assert base_obj.shape == "chest_1"
    assert base_obj.material == [
        "UnityAssetStore/Baby_Room/Models/Materials/wood 1"]
    assert base_obj.scale == 1
    assert base_obj.labels == "obj_to_copy"

    copy_template = component.specific_interactable_objects[1]
    assert isinstance(
        copy_template,
        InteractableObjectConfig)
    assert copy_template.num == 4
    assert copy_template.identical_except_color == "obj_to_copy"

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene.objects, list)
    assert len(scene.objects) == 5
    for index, obj in enumerate(scene.objects):
        assert obj['debug']['random_position']
        assert 'type' in obj
        assert isinstance(obj['type'], str)
        assert obj['type'] == "chest_1"
        assert 'scale' in obj['shows'][0]
        assert obj['shows'][0]['scale'] == {"x": 1, "y": 1, "z": 1}
        if index == 0:
            assert obj['materials'] == [
                "UnityAssetStore/Baby_Room/Models/Materials/wood 1"]
        else:
            assert obj['materials'] != [
                "UnityAssetStore/Baby_Room/Models/Materials/wood 1"]


def test_specific_objects_delayed_action():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "keyword_location": {
                "keyword": "in",
                "container_label": "no_object"
            }
        }
    })
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig)
    sio = component.specific_interactable_objects
    assert sio.material is None
    assert sio.num == 1
    assert sio.shape is None
    assert sio.scale is None
    assert sio.rotation is None
    assert sio.position is None

    scene = component.update_ile_scene(prior_scene())
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 0
    component.get_num_delayed_actions() == 1


def test_specific_objects_delayed_action_adjacent():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "keyword_location": {
                "keyword": "adjacent",
                "relative_object_label": "after_object"
            }
        }, {
            "labels": "after_object"
        }]
    })

    scene = component.update_ile_scene(prior_scene())
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 1
    assert component.get_num_delayed_actions() == 1

    scene = component.run_delayed_actions(scene)
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 2
    component.get_num_delayed_actions() == 0
    #  objects[1][]


def test_specific_objects_delayed_action_in():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "shape": "crayon_blue",
            "keyword_location": {
                "keyword": "in",
                "container_label": "chest"
            }
        }, {
            "labels": "chest",
            "shape": "chest_3"
        }]
    })

    scene = component.update_ile_scene(prior_scene())
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 1
    assert component.get_num_delayed_actions() == 1

    scene = component.run_delayed_actions(scene)
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 2
    component.get_num_delayed_actions() == 0
    assert objects[1]['locationParent'] == objects[0]['id']
