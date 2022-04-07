import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

from generator import ObjectBounds, Scene
from ideal_learning_env.defs import TARGET_LABEL, find_bounds
from ideal_learning_env.feature_creation_service import (
    FeatureCreationService,
    FeatureTypes,
)
from ideal_learning_env.interactable_object_service import (
    InteractableObjectConfig,
)

logger = logging.getLogger(__name__)


@dataclass
class GoalConfig():
    """A dict with str `category` and optional `target`, `target_1`, and
    `target_2` properties that represents the goal and target object(s) in each
    scene. The `target*` properties are only needed if required for the
    specific category of goal. Each `target*` property is either an
    InteractableObjectConfig dict or list of InteractableObjectConfig dicts.
    For each list, one dict will be randomly chosen within the list in each
    new scene.  All goal target objects will be assigned the 'target' label.

    Example:
    ```
    category: retrieval
    target:
        shape: soccer_ball
        scale:
          min: 1.0
          max: 3.0
    ```
    """

    category: str = None
    target: Union[
        InteractableObjectConfig,
        List[InteractableObjectConfig]
    ] = None
    target_1: Union[
        InteractableObjectConfig,
        List[InteractableObjectConfig]
    ] = None
    target_2: Union[
        InteractableObjectConfig,
        List[InteractableObjectConfig]
    ] = None


class GoalServices:
    @staticmethod
    def _generate_goal_data(
        scene: Scene,
        goal: GoalConfig,
        bounds_list: List[ObjectBounds]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        if not goal:
            return None, []

        # Choose a random goal category (and target if needed) from the config.
        goal_metadata = {}
        target_list = []

        # Create the target(s) and add ID(s) to the goal's metadata.
        for prop in ['target', 'target_1', 'target_2']:
            config: InteractableObjectConfig = getattr(goal, prop)
            if config:
                labels = getattr(config, 'labels') or []
                labels = labels if isinstance(labels, list) else [labels]
                if TARGET_LABEL not in labels:
                    labels.append(TARGET_LABEL)
                setattr(config, 'labels', labels)
                instance = FeatureCreationService.create_feature(
                    scene,
                    FeatureTypes.INTERACTABLE,
                    config,
                    bounds_list
                )[0]
                goal_metadata[prop] = {
                    'id': instance['id']
                }
                target_list.append(instance)
                logger.trace(
                    f'Creating goal "{prop}" from config = {vars(config)}'
                )

        description = None
        if goal.category.lower() == 'retrieval' and len(target_list):
            description = (
                f'Find and pick up the {target_list[0]["debug"]["goalString"]}'
            )

        return {
            'category': goal.category.lower(),
            'description': description,
            'metadata': goal_metadata
        }, target_list

    @staticmethod
    def attempt_to_add_goal(
        scene: Scene,
        goal_template: GoalConfig,
        bounds_list: List[ObjectBounds] = None
    ) -> None:
        """Attempt to add a goal to the scene.  The goal_template must have
        all randomness resolved before calling this function"""
        # if the user passes an empty list, use that.
        bounds_list = (bounds_list if bounds_list is not None else find_bounds(
            scene))
        goal_data, target_list = GoalServices._generate_goal_data(
            scene, goal_template, bounds_list)
        if goal_data:
            scene.goal['category'] = goal_data['category']
            scene.goal['description'] = goal_data['description']
            scene.goal['metadata'] = goal_data['metadata']
            logger.trace(
                f'Setting {scene.goal["category"]} goal with '
                f'{len(target_list)} target(s): {scene.goal}'
            )
