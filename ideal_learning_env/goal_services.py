import logging
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

from generator import ObjectBounds, Scene, tags

from .choosers import choose_random
from .defs import ILEConfigurationException, find_bounds, return_list
from .interactable_object_service import (
    InteractableObjectConfig,
    create_user_configured_interactable_object
)

logger = logging.getLogger(__name__)


@dataclass
class GoalConfig():
    """A dict with str `category` and optional `target` or `targets` properties
    that correspond to the goal and target object(s) in each scene.

    The goal `category` for interactive scenes is either `"retrieval"` (for
    one target) or `"multi retrieval"` (for multiple targets). If the
    `category` is not set, it will default to `"retrieval"` if `target` is set
    or `"multi retrieval"` if `targets` is set.

    The goal `category` for passive scenes is either `"intuitive physics"`
    (for passive physics scenes), `"agents"` (for NYU passive agent scenes), or
    `"passive"` (for all other passive scenes). Please see
    `passive_physics_scene` for making passive physics scenes. Please do not
    use the ILE Scene Generator for making NYU passive agent scenes.

    See the MCS Python API for more information about the goal categories:

    https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.GoalCategory

    The `target` property is only needed for `"retrieval"` scenes, and the
    `targets` property is only needed for `"multi retrieval"` scenes.
    The `target` property is either an InteractableObjectConfig dict or a list
    of InteractableObjectConfig dicts. For a list, one dict will be randomly
    chosen within the list in each new scene. The `targets` property is a list
    of InteractableObjectConfig dicts, and ALL the dicts will be used as
    targets in each new scene. All goal target objects will be assigned the
    'target' label. The `num` property will only be used with multiple
    `targets`.

    Please note that the `"traversal"` and `"transferral"` goal categories,
    along with the `target_1` and `target_2` properties, are no longer
    supported.

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
    targets: List[InteractableObjectConfig] = None


class GoalServices:
    @staticmethod
    def validate_goal_category(goal_template: GoalConfig) -> List[str]:
        """Validates all the categories in the given goal config template and
        returns the list of all possible categories (for reconciliation).
        Throws an exception if any categories are invalid."""
        categories = [goal_category.lower() for goal_category in return_list(
            goal_template.category
        )]
        if not categories:
            if goal_template.target:
                categories = [tags.SCENE.RETRIEVAL]
            elif goal_template.targets:
                categories = [tags.SCENE.MULTI_RETRIEVAL]
            else:
                raise ILEConfigurationException(
                    'Cannot set a default goal category without one of the ' +
                    'following properties: "target", "targets"'
                )
        for goal_category in categories:
            if goal_category == tags.SCENE.RETRIEVAL:
                if not goal_template.target:
                    raise ILEConfigurationException(
                        f'Goal with {tags.SCENE.RETRIEVAL} category '
                        f'must also have configured "target" property'
                    )
            elif goal_category == tags.SCENE.MULTI_RETRIEVAL:
                if not goal_template.targets:
                    raise ILEConfigurationException(
                        f'Goal with {tags.SCENE.MULTI_RETRIEVAL} category '
                        f'must also have configured "targets" property'
                    )
            elif goal_category not in [
                tags.SCENE.INTUITIVE_PHYSICS, tags.SCENE.PASSIVE,
                tags.SCENE.IMITATION
            ]:
                raise ILEConfigurationException(
                    f'Interactive goal category must be one of the following: '
                    f'{tags.SCENE.RETRIEVAL}, {tags.SCENE.MULTI_RETRIEVAL}, '
                    f'{tags.SCENE.PASSIVE}, {tags.SCENE.INTUITIVE_PHYSICS}, '
                    f'{tags.SCENE.IMITATION}'
                )
        return categories if len(categories) > 1 else categories[0]

    @staticmethod
    def _generate_goal_data(
        scene: Scene,
        goal_template: GoalConfig,
        bounds_list: List[ObjectBounds]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        if not goal_template:
            return None, []

        config_list = []
        target_list = []
        goal_metadata = {}

        # Choose a random goal category from the config.
        categories = GoalServices.validate_goal_category(goal_template)
        goal_category = choose_random(categories)

        # Ensure retrieval goals have configured target(s).
        if goal_category == tags.SCENE.RETRIEVAL:
            # If the config is a list, choose just one random target, but do
            # NOT resolve the random properties within that target config.
            target_template = random.choice(return_list(goal_template.target))
            config_list.append(target_template)
            goal_metadata['target'] = {}
        if goal_category == tags.SCENE.MULTI_RETRIEVAL:
            # Do NOT choose only one random target (use all of them!) and do
            # NOT resolve the random properties within the target configs.
            for target_template in goal_template.targets:
                num = choose_random(target_template.num or 1)
                # Repeat the target config for the configured amount.
                for _ in range(num):
                    config_list.append(target_template)
            goal_metadata['targets'] = []
        if goal_category == tags.SCENE.IMITATION:
            target_reconciled = choose_random(goal_template.target)
            config_list.append(target_reconciled)
            goal_metadata['target'] = {}

        # Create the target(s) and add ID(s) to the goal's metadata.
        for config in config_list:
            instance = create_user_configured_interactable_object(
                scene,
                bounds_list,
                config,
                is_target=True
            )

            # Update the goal's metadata.
            if goal_category == tags.SCENE.RETRIEVAL or \
                    goal_category == tags.SCENE.IMITATION:
                goal_metadata['target'] = {
                    'id': instance['id']
                }
            if goal_category == tags.SCENE.MULTI_RETRIEVAL:
                goal_metadata['targets'].append({
                    'id': instance['id']
                })

            target_list.append(instance)
            logger.trace(f'Creating goal target from config = {vars(config)}')

        # Create the description for interactive goals.
        goal_description = ''
        if goal_category == tags.SCENE.RETRIEVAL:
            goal_string = target_list[0]["debug"]["goalString"]
            goal_description = f'Find and pick up the {goal_string}.'
        if goal_category == tags.SCENE.MULTI_RETRIEVAL:
            goal_strings = [i['debug']['goalString'] for i in target_list]
            goal_strings = sorted(set(goal_strings))
            goal_string = goal_strings[0] if len(goal_strings) == 1 else (
                '; '.join(goal_strings[:-1]) + '; and ' + goal_strings[-1]
            )
            goal_description = (
                f'Find and pick up as many objects as possible of type: '
                f'{goal_string}.'
            )
        if goal_category == tags.SCENE.IMITATION:
            goal_string = target_list[0]["debug"]["goalString"]
            goal_description = (
                f'Open the containers in the correct order for '
                f'the {goal_string} to be placed.'
            )
        return {
            'category': goal_category,
            'description': goal_description,
            'metadata': goal_metadata
        }, target_list

    @staticmethod
    def attempt_to_add_goal(
        scene: Scene,
        goal_template: GoalConfig,
        bounds_list: List[ObjectBounds] = None
    ) -> List[Dict[str, Any]]:
        """Attempt to add the given goal to the scene. The goal_template must
        NOT have randomness resolved (a.k.a. be reconciled) before calling this
        function. Returns the list of target objects."""
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
        return target_list
