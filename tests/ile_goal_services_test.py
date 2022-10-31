import pytest

from ideal_learning_env.goal_services import GoalConfig, GoalServices
from ideal_learning_env.interactable_object_service import (
    InteractableObjectConfig
)
from ideal_learning_env.numerics import VectorFloatConfig

from .ile_helper import prior_scene


def test_attempt_goal_retrieval():
    scene = prior_scene()
    goal_template = GoalConfig(
        category='retrieval',
        target=InteractableObjectConfig(
            shape='soccer_ball',
            scale=1.3,
            position=VectorFloatConfig(1, 0, 3),
            rotation=VectorFloatConfig(0, 135, 0),
        )
    )
    GoalServices.attempt_to_add_goal(scene, goal_template)
    assert scene.goal['category'] == 'retrieval'
    assert scene.goal['description'] == 'Find and pick up the small light ' + \
        'black white rubber ball.'
    assert scene.goal['metadata']['target']
    assert scene.goal['metadata']['target']['id']
    objs = scene.objects
    assert len(objs) == 1
    assert objs[0]['id'] == scene.goal['metadata']['target']['id']
    assert objs[0]['type'] == 'soccer_ball'
    assert objs[0]['pickupable']
    assert objs[0]['moveable']
    show = objs[0]['shows'][0]
    assert show['position'] == pytest.approx({'x': 1.0, 'y': 0.143, 'z': 3.0})
    assert show['scale'] == {'x': 1.3, 'y': 1.3, 'z': 1.3}
    assert show['rotation']['y'] == 135


def test_attempt_goal_retrieval_ignore_num():
    scene = prior_scene()
    goal_template = GoalConfig(
        category='retrieval',
        target=InteractableObjectConfig(num=2, scale=1.5, shape='soccer_ball')
    )
    GoalServices.attempt_to_add_goal(scene, goal_template)
    assert scene.goal['category'] == 'retrieval'
    assert scene.goal['description'] == 'Find and pick up the small light ' + \
        'black white rubber ball.'
    assert scene.goal['metadata']['target']
    assert scene.goal['metadata']['target']['id']
    objs = scene.objects
    assert len(objs) == 1
    assert objs[0]['id'] == scene.goal['metadata']['target']['id']
    assert objs[0]['type'] == 'soccer_ball'


def test_attempt_goal_retrieval_no_category():
    scene = prior_scene()
    goal_template = GoalConfig(
        target=InteractableObjectConfig(scale=1, shape='soccer_ball')
    )
    GoalServices.attempt_to_add_goal(scene, goal_template)
    assert scene.goal['category'] == 'retrieval'
    assert scene.goal['description'] == 'Find and pick up the tiny light ' + \
        'black white rubber ball.'
    assert scene.goal['metadata']['target']
    assert scene.goal['metadata']['target']['id']
    objs = scene.objects
    assert len(objs) == 1
    assert objs[0]['id'] == scene.goal['metadata']['target']['id']
    assert objs[0]['type'] == 'soccer_ball'


def test_attempt_goal_multi_retrieval():
    scene = prior_scene()
    goal_template = GoalConfig(
        category='multi retrieval',
        targets=[
            InteractableObjectConfig(scale=1, shape='soccer_ball')
        ]
    )
    GoalServices.attempt_to_add_goal(scene, goal_template)
    assert scene.goal['category'] == 'multi retrieval'
    assert scene.goal['description'] == 'Find and pick up as many objects ' + \
        'as possible of type: tiny light black white rubber ball.'
    assert len(scene.goal['metadata']['targets']) == 1
    assert scene.goal['metadata']['targets'][0]['id']
    objs = scene.objects
    assert len(objs) == 1
    assert objs[0]['id'] == scene.goal['metadata']['targets'][0]['id']
    assert objs[0]['type'] == 'soccer_ball'


def test_attempt_goal_multi_retrieval_with_num():
    scene = prior_scene()
    goal_template = GoalConfig(
        category='multi retrieval',
        targets=[
            InteractableObjectConfig(num=2, scale=1, shape='soccer_ball')
        ]
    )
    GoalServices.attempt_to_add_goal(scene, goal_template)
    assert scene.goal['category'] == 'multi retrieval'
    assert scene.goal['description'] == 'Find and pick up as many objects ' + \
        'as possible of type: tiny light black white rubber ball.'
    assert len(scene.goal['metadata']['targets']) == 2
    assert scene.goal['metadata']['targets'][0]['id']
    assert scene.goal['metadata']['targets'][1]['id']
    objs = scene.objects
    assert len(objs) == 2
    assert objs[0]['id'] == scene.goal['metadata']['targets'][0]['id']
    assert objs[0]['type'] == 'soccer_ball'
    assert objs[1]['id'] == scene.goal['metadata']['targets'][1]['id']
    assert objs[1]['type'] == 'soccer_ball'


def test_attempt_goal_multi_retrieval_multiple_shapes():
    scene = prior_scene()
    goal_template = GoalConfig(
        category='multi retrieval',
        targets=[
            InteractableObjectConfig(
                scale=2,
                shape='soccer_ball',
                labels='t_1'
            ),
            InteractableObjectConfig(shape='soccer_ball', identical_to='t_1'),
            InteractableObjectConfig(scale=1, shape='trophy')
        ]
    )
    GoalServices.attempt_to_add_goal(scene, goal_template)
    assert scene.goal['category'] == 'multi retrieval'
    assert scene.goal['description'] == 'Find and pick up as many objects ' + \
        'as possible of type: small light black white rubber ball; ' + \
        'and tiny light grey metal trophy.'
    assert len(scene.goal['metadata']['targets']) == 3
    assert scene.goal['metadata']['targets'][0]['id']
    assert scene.goal['metadata']['targets'][1]['id']
    assert scene.goal['metadata']['targets'][2]['id']
    objs = scene.objects
    assert len(objs) == 3
    assert objs[0]['id'] == scene.goal['metadata']['targets'][0]['id']
    assert objs[0]['type'] == 'soccer_ball'
    assert objs[1]['id'] == scene.goal['metadata']['targets'][1]['id']
    assert objs[1]['id'] != objs[0]['id']
    assert objs[1]['type'] == 'soccer_ball'
    assert objs[1]['shows'][0]['scale'] == objs[0]['shows'][0]['scale']
    assert objs[2]['id'] == scene.goal['metadata']['targets'][2]['id']
    assert objs[2]['type'] == 'trophy'
    assert objs[2]['id'] != objs[0]['id']
    assert objs[2]['id'] != objs[1]['id']
