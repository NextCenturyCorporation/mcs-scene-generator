
from ideal_learning_env.goal_services import GoalConfig, GoalServices
from ideal_learning_env.interactable_object_service import (
    InteractableObjectConfig,
)
from ideal_learning_env.numerics import VectorFloatConfig

from .ile_helper import prior_scene


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
    target_id = scene.goal['metadata']['target']['id']
    assert target_id
    assert scene.goal['category'] == 'retrieval'
    objs = scene.objects
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
