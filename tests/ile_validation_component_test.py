import pytest
from machine_common_sense.config_manager import Vector3d

from generator import ObjectBounds, specific_objects
from ideal_learning_env.defs import ILEConfigurationException, ILEException
from ideal_learning_env.goal_services import TARGET_LABEL
from ideal_learning_env.object_services import (
    InstanceDefinitionLocationTuple,
    ObjectRepository,
)
from ideal_learning_env.validation_component import ValidPathComponent


def prior_scene(start_x=0, start_z=0):
    return {'debug': {}, 'goal': {}, 'performerStart':
            {'position':
             {'x': start_x, 'y': 0, 'z': start_z},
             'rotation': {'x': 0, 'y': 0, 'z': 0}},
            'roomDimensions': {'x': 10, 'y': 3, 'z': 10}}


def prior_scene_custom_size(x, z):
    return {'debug': {}, 'goal': {}, 'performerStart':
            {'position':
             {'x': 0, 'y': 0, 'z': 0}},
            'roomDimensions': {'x': x, 'y': 3, 'z': z}}


def prior_scene_with_target(start_x=0, start_z=0):
    scene = prior_scene(start_x, start_z)
    target_inst = {
        'id': '743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f',
        'type': 'soccer_ball',
        'mass': 1.0,
        'salientMaterials': ['rubber'],
        'debug': {
            'dimensions': {'x': 0.22, 'y': 0.22, 'z': 0.22},
            'positionY': 0.11,
            'shape': ['ball'],
            'offset': {'x': 0, 'y': 0.11, 'z': 0},
            'materialCategory': [],
            'color': ['black', 'white']
        },
        'moveable': True,
        'pickupable': True,
        'shows': [{
            'rotation': {'x': 0, 'y': 45, 'z': 0},
            'position': {'x': -1.03, 'y': 0.11, 'z': 4.08},
            'boundingBox': ObjectBounds(box_xz=[
                Vector3d(**{'x': -0.8744, 'y': 0, 'z': 4.08}),
                Vector3d(**{'x': -1.03, 'y': 0, 'z': 3.9244}),
                Vector3d(**{'x': -1.1856, 'y': 0, 'z': 4.08}),
                Vector3d(**{'x': -1.03, 'y': 0, 'z': 4.2356})
            ], max_y=0.22, min_y=0),
            'stepBegin': 0,
            'scale': {'x': 1, 'y': 1, 'z': 1}
        }],
        'materials': []
    }

    scene["objects"] = [target_inst]
    goal = {
        "metadata": {
            "target": {
                "id": "743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f"
            }
        },
        "last_step": 1000,
        "category": "retrieval"
    }
    scene["goal"] = goal
    target_defn = specific_objects.create_soccer_ball()
    target_loc = target_inst['shows'][0]
    t = InstanceDefinitionLocationTuple(target_inst, target_defn, target_loc)
    ObjectRepository.get_instance().clear()
    ObjectRepository.get_instance().add_to_labeled_objects(t, TARGET_LABEL)
    return scene


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()

    # Run test
    yield

    # Cleanup
    ObjectRepository.get_instance().clear()


def test_valid_path_off_by_defaults():
    component = ValidPathComponent({})
    assert component.check_valid_path is None
    assert component.get_check_valid_path() is False

    component.update_ile_scene(prior_scene())
    assert component.last_distance is None
    assert component.last_path is None
    # Just don't raise.


def test_valid_path_no_obstacles():
    component = ValidPathComponent({'check_valid_path': True})
    assert component.check_valid_path
    assert component.get_check_valid_path()

    component.update_ile_scene(prior_scene_with_target())
    assert component.last_distance == pytest.approx(4.2, 0.1)
    # second path entry is location of target
    assert component.last_path == [(0, 0), (-1.03, 4.08)]
    # Just don't raise.


def test_valid_path_no_target():
    component = ValidPathComponent({'check_valid_path': True})
    assert component.check_valid_path
    assert component.get_check_valid_path()

    with pytest.raises(ILEConfigurationException):
        component.update_ile_scene(prior_scene())


def test_valid_path_blocked_by_holes():
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target()
    scene['holes'] = scene.get('holes', [])
    # create blocked by holes
    holes = scene.get('holes')
    for i in range(11):
        holes.append({'x': i - 5, 'z': 2})

    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_valid_path_blocked_by_lava():
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target()

    # create blocked by lava
    scene['lava'] = [{'x': i - 5, 'z': 2} for i in range(11)]

    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_valid_path_blocked_by_platforms():
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target()
    scene['objects'] = scene.get('objects', [])
    # create blocked by holes
    objs = scene.get('objects')
    [
        {
            "x": 4.9,
            "y": 0.0,
            "z": 2.4386
        },
        {
            "x": 4.9,
            "y": 0.0,
            "z": 1.5614
        },
        {
            "x": -4.9,
            "y": 0.0,
            "z": 1.5614
        },
        {
            "x": -4.9,
            "y": 0.0,
            "z": 2.4386
        },
        {
            "x": 4.9,
            "y": 0.5,
            "z": 2.4386
        },
        {
            "x": 4.9,
            "y": 0.5,
            "z": 1.5614
        },
        {
            "x": -4.9,
            "y": 0.5,
            "z": 1.5614
        },
        {
            "x": -4.9,
            "y": 0.5,
            "z": 2.4386
        }
    ]

    bb = ObjectBounds([Vector3d(4.9, 0, 2.4386), Vector3d(4.9, 0, -2.4386),
                       Vector3d(-4.9, 0, -2.4386), Vector3d(-4.9, 0, 2.4386)],
                      max_y=2.0, min_y=0.0)

    platform = {
        "id": "platform_8c30bd12-0f0f-494f-a127-de362a54e79d",
        "type": "cube",
        "debug": {
            "color": [
              "red"
            ],
            "info": [
                "red",
                "platform",
                "red platform"
            ],
            "dimensions": {
                "x": 9.8,
                "y": 0.5,
                "z": 0.8772
            },
            "random_position": False
        },
        "mass": 537,
        "materials": [
            "UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1"],
        "kinematic": True,
        "structure": True,
        "shows": [
            {
                "stepBegin": 0,
                "position": {
                    "x": 0,
                    "y": 0.25,
                    "z": 2
                },
                "rotation": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
                "scale": {
                    "x": 9.8,
                    "y": 0.5,
                    "z": 0.8772
                },
                "boundingBox": bb
            }
        ]
    }
    objs.append(platform)

    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_valid_path_with_lava_and_holes():
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target(-3, -3)
    scene['holes'] = scene.get('holes', [])
    # create blocked by holes
    holes = scene.get('holes')
    for i in range(8):
        holes.append({'x': i - 5, 'z': 3})

    scene['lava'] = [{'x': i - 3, 'z': 0} for i in range(8)]

    component.update_ile_scene(scene)
    assert component.last_distance == pytest.approx(15, 0.1)
