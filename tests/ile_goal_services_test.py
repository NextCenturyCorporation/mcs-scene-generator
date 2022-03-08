
from machine_common_sense.config_manager import Vector3d

from generator.geometry import ObjectBounds
from ideal_learning_env.goal_services import (
    GoalConfig,
    GoalServices,
    get_target_object,
)
from ideal_learning_env.interactable_object_config import (
    InteractableObjectConfig,
)
from ideal_learning_env.numerics import VectorFloatConfig


def prior_scene():
    return {
        'debug': {},
        'goal': {},
        'performerStart':
        {
            'position':
            {'x': 0, 'y': 0, 'z': 0}
        },
        'roomDimensions': {'x': 10, 'y': 3, 'z': 10}
    }


def prior_scene_with_target():
    scene = prior_scene()
    target_object = {
        'id': '743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f',
        'type': 'soccer_ball',
        'mass': 1.0,
        'salientMaterials': ['rubber'],
        'debug':
            {'dimensions':
                {'x': 0.22,
                 'y': 0.22,
                 'z': 0.22},
             'info': [
                    'tiny', 'light', 'black', 'white', 'rubber', 'ball',
                    'black white', 'tiny light', 'tiny rubber',
                    'tiny black white', 'tiny ball', 'light rubber',
                    'light black white', 'light ball',
                    'rubber black white', 'rubber ball', 'black white ball',
                    'tiny light black white rubber ball'],
             'positionY': 0.11, 'role': '', 'shape': ['ball'],
             'size': 'tiny', 'untrainedCategory': False,
             'untrainedColor': False, 'untrainedCombination': False,
             'untrainedShape': False, 'untrainedSize': False, 'offset':
             {'x': 0, 'y': 0.11, 'z': 0}, 'materialCategory': [], 'color':
             ['black', 'white'], 'weight': 'light', 'goalString':
             'tiny light black white rubber ball', 'salientMaterials':
             ['rubber'], 'enclosedAreas': []}, 'moveable': True,
        'pickupable': True, 'shows': [
                 {'rotation': {'x': 0, 'y': 45, 'z': 0},
                  'position': {'x': -1.03, 'y': 0.11, 'z': 4.08},
                  'boundingBox': ObjectBounds(box_xz=[
                      Vector3d(**{'x': -0.8744, 'y': 0, 'z': 4.08}),
                      Vector3d(**{'x': -1.03, 'y': 0, 'z': 3.9244}),
                      Vector3d(**{'x': -1.1856, 'y': 0, 'z': 4.08}),
                      Vector3d(**{'x': -1.03, 'y': 0, 'z': 4.2356})
                  ], max_y=0, min_y=0),
                  'stepBegin': 0, 'scale': {'x': 1, 'y': 1, 'z': 1}}],
        'materials': []}

    scene["objects"] = [target_object]
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
    return scene


def test_attempt_goal():
    scene = prior_scene()
    goal_template = GoalConfig(
        category='retrieval',
        target=InteractableObjectConfig(
            shape='ball',
            scale=1.3,
            position=VectorFloatConfig(1, 0, 3),
            rotation=VectorFloatConfig(0, 135, 0),
        )
    )
    GoalServices.attempt_to_add_goal(scene, goal_template)
    target_id = scene['goal']['metadata']['target']['id']
    assert target_id
    assert scene['goal']['category'] == 'retrieval'
    objs = scene['objects']
    assert len(objs) == 1
    target = objs[0]
    assert target['id'] == target_id
    assert target['type'] == 'ball'
    assert target['pickupable']
    assert target['moveable']
    show = target['shows'][0]
    assert show['position'] == {'x': 1.0, 'y': 0.65, 'z': 3.0}
    assert show['scale'] == {'x': 1.3, 'y': 1.3, 'z': 1.3}
    assert show['rotation']['y'] == 135


def test_get_target_object_None():
    scene = prior_scene()
    assert get_target_object(scene) is None


def test_get_target_object_with_target():
    scene = prior_scene_with_target()
    obj = get_target_object(scene)
    assert obj['type'] == 'soccer_ball'
    assert obj['id'] == '743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f'
    assert obj['moveable']
    assert obj['pickupable']
    show = obj['shows'][0]
    assert show['rotation'] == {'x': 0, 'y': 45, 'z': 0}
    assert show['position'] == {'x': -1.03, 'y': 0.11, 'z': 4.08}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}
