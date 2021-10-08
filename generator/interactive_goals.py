import copy
import logging
import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AnyStr, Dict, List, Tuple, Union

from . import exceptions, tags
from .definitions import ObjectDefinition
from .geometry import (
    MIN_OBJECTS_SEPARATION_DISTANCE,
    calc_obj_pos,
    position_distance,
)
from .specific_objects import (
    get_interactable_definition_dataset,
    get_pickupable_definition_dataset,
    get_stack_target_definition_dataset,
)

# No target images in Eval 3.
NO_TARGET_IMAGES = True


def generate_image_file_name(target: Dict[str, Any]) -> str:
    if 'materials' not in target or not target['materials']:
        return target['type']

    material_name_list = [item[(item.rfind(
        '/') + 1):].lower().replace(' ', '_') for item in target['materials']]
    return target['type'] + ('_' if len(material_name_list) >
                             0 else '') + ('_'.join(material_name_list))


def find_image_for_object(object_def: Dict[str, Any]) -> AnyStr:
    image_file_name = ""

    try:
        image_file_name = '../images/' + \
            generate_image_file_name(object_def) + '.txt'

        with open(image_file_name, 'r') as image_file:
            target_image = image_file.read()

        return target_image
    except BaseException:
        logging.warning(
            'Image object could not be found, make sure you generated ' +
            ' the image: ' + image_file_name)


def find_image_name(target: Dict[str, Any]) -> str:
    return generate_image_file_name(target) + '.png'


class InteractiveGoal(ABC):
    def __init__(self, name: str, goal_template: Dict[str, Any]):
        self._name = name
        self._goal_template = goal_template

    @abstractmethod
    def choose_target_definition(self, target_number: int) -> ObjectDefinition:
        """Choose and return a target definition."""
        pass

    @abstractmethod
    def get_target_count(self) -> int:
        """Return this goal's number of targets."""
        pass

    @abstractmethod
    def update_goal_template(
        self,
        goal_template: Dict[str, Any],
        target_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update and return the given goal config for a scene."""
        pass

    @abstractmethod
    def validate_target_location(
        self,
        target_number: int,
        target_location: Dict[str, Any],
        previously_made_target_list: List[Dict[str, Any]],
        performer_start: Dict[str, Dict[str, float]]
    ) -> bool:
        """Return if a target can be positioned at the given location based on
        the previously made targets and the performer's start location."""
        pass

    def choose_definition(
        self,
        must_be_pickupable: bool = False
    ) -> ObjectDefinition:
        """Choose and return an object definition."""
        return (
            get_pickupable_definition_dataset() if must_be_pickupable else
            get_interactable_definition_dataset()
        ).filter_on_trained().choose_random_definition()

    def choose_location(
        self,
        definition_or_instance: Union[ObjectDefinition, Dict[str, Any]],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]],
        is_target=False,
        room_dimensions: Dict[str, float] = None
    ) -> Tuple[Dict[str, Any], List[List[Dict[str, float]]]]:
        """Choose and return a location for the given object and the new
        bounds list."""
        def rotation_func():
            return performer_start['rotation']['y']
        bounds_list_copy = copy.deepcopy(bounds_list)
        object_location = calc_obj_pos(
            performer_start['position'],
            bounds_list_copy,
            definition_or_instance,
            rotation_func=rotation_func,
            room_dimensions=room_dimensions
        )
        if not object_location:
            raise exceptions.SceneException(
                f'Cannot position {definition_or_instance}'
            )
        return object_location, bounds_list_copy

    def get_goal_template(self) -> Dict[str, Any]:
        """Return this goal's JSON data template."""
        return self._goal_template

    def get_name(self) -> str:
        """Return this goal's name."""
        return self._name


class RetrievalGoal(InteractiveGoal):
    GOAL_TEMPLATE = {
        'category': tags.tag_to_label(tags.SCENE.RETRIEVAL),
        'domainsInfo': {
            'objects': [
                tags.DOMAINS.OBJECTS_1,
                tags.DOMAINS.OBJECTS_3
            ],
            'places': [
                tags.DOMAINS.PLACES_2,
                tags.DOMAINS.PLACES_3
            ],
            'agents': []
        },
        'sceneInfo': {}
    }

    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.PRIMARY] = (
        tags.tag_to_label(tags.SCENE.INTERACTIVE)
    )
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.SECONDARY] = (
        tags.tag_to_label(tags.SCENE.RETRIEVAL)
    )
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.TERTIARY] = (
        tags.tag_to_label(tags.SCENE.RETRIEVAL)
    )
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.QUATERNARY] = (
        tags.tag_to_label(tags.SCENE.ACTION_FULL)
    )

    def __init__(self, hypercube_type: str):
        goal_template = copy.deepcopy(RetrievalGoal.GOAL_TEMPLATE)
        goal_template['sceneInfo'][tags.SCENE.TERTIARY] = hypercube_type
        super().__init__(tags.SCENE.RETRIEVAL, goal_template)

    # Override
    def choose_target_definition(self, target_number: int) -> ObjectDefinition:
        return self.choose_definition(must_be_pickupable=True)

    # Override
    def get_target_count(self) -> int:
        return 1

    # Override
    def update_goal_template(
        self,
        goal_template: Dict[str, Any],
        target_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        goal_template['metadata'] = {
            'target': {
                'id': target_list[0]['id'],
                'info': target_list[0]['debug']['info']
            }
        }
        goal_template['description'] = f'Find and pick up the ' \
            f'{target_list[0]["debug"]["goalString"]}.'
        if not NO_TARGET_IMAGES:
            image = find_image_for_object(target_list[0])
            image_name = find_image_name(target_list[0])
            goal_template['metadata']['target']['image'] = image
            goal_template['metadata']['target']['image_name'] = image_name
            goal_template['metadata']['target']['match_image'] = True
        return goal_template

    # Override
    def validate_target_location(
        self,
        target_number: int,
        target_location: Dict[str, Any],
        previously_made_target_list: List[Dict[str, Any]],
        performer_start: Dict[str, Dict[str, float]]
    ) -> bool:
        return True


class TransferralGoal(InteractiveGoal):
    class RelationshipType(Enum):
        NEXT_TO = 'next to'
        ON_TOP_OF = 'on top of'

    GOAL_TEMPLATE = {
        'category': tags.tag_to_label(tags.SCENE.TRANSFERRAL),
        'domainsInfo': {
            'objects': [
                # TODO
            ],
            'places': [
                # TODO
            ],
            'agents': []
        },
        'sceneInfo': {}
    }

    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.PRIMARY] = (
        tags.tag_to_label(tags.SCENE.INTERACTIVE)
    )
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.SECONDARY] = (
        tags.tag_to_label(tags.SCENE.TRANSFERRAL)
    )
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.TERTIARY] = (
        tags.tag_to_label(tags.SCENE.TRANSFERRAL)
    )
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.QUATERNARY] = (
        tags.tag_to_label(tags.SCENE.ACTION_FULL)
    )

    def __init__(self, hypercube_type: str):
        goal_template = copy.deepcopy(TransferralGoal.GOAL_TEMPLATE)
        goal_template['sceneInfo'][tags.SCENE.TERTIARY] = hypercube_type
        super().__init__(tags.SCENE.TRANSFERRAL, goal_template)

    # Override
    def choose_target_definition(self, target_number: int) -> ObjectDefinition:
        if target_number == 0:
            return self.choose_definition(must_be_pickupable=True)

        if target_number != 1:
            raise exceptions.SceneException(
                f'Expected target with number 0 or 1 but got {target_number}')

        return (
            get_stack_target_definition_dataset()
        ).filter_on_trained().choose_random_definition()

    # Override
    def get_target_count(self) -> int:
        return 2

    # Override
    def update_goal_template(
        self,
        goal_template: Dict[str, Any],
        target_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        relationship = random.choice(list(self.RelationshipType))
        goal_template['metadata'] = {
            'target_1': {
                'id': target_list[0]['id'],
                'info': target_list[0]['debug']['info']
            },
            'target_2': {
                'id': target_list[1]['id'],
                'info': target_list[1]['debug']['info']
            },
            'relationship': ['target_1', relationship.value, 'target_2']
        }
        goal_template['description'] = f'Find and pick up the ' \
            f'{target_list[0]["debug"]["goalString"]} and move it ' \
            f'{relationship.value} the ' \
            f'{target_list[1]["debug"]["goalString"]}.'
        if not NO_TARGET_IMAGES:
            image_1 = find_image_for_object(target_list[0])
            image_2 = find_image_for_object(target_list[1])
            image_name_1 = find_image_name(target_list[0])
            image_name_2 = find_image_name(target_list[1])
            goal_template['metadata']['target_1']['image'] = image_1
            goal_template['metadata']['target_1']['image_name'] = image_name_1
            goal_template['metadata']['target_1']['match_image'] = True
            goal_template['metadata']['target_2']['image'] = image_2
            goal_template['metadata']['target_2']['image_name'] = image_name_2
            goal_template['metadata']['target_2']['match_image'] = True
        return goal_template

    # Override
    def validate_target_location(
        self,
        target_number: int,
        target_location: Dict[str, Any],
        previously_made_target_list: List[Dict[str, Any]],
        performer_start: Dict[str, Dict[str, float]]
    ) -> bool:
        if target_number == 0:
            return True

        elif target_number != 1:
            raise exceptions.SceneException(
                f'Expected target with number 0 or 1 but got {target_number}')

        if len(previously_made_target_list) == 0:
            raise exceptions.SceneException(
                'Expected existing transferral target')

        distance = position_distance(
            previously_made_target_list[0]['shows'][0]['position'],
            target_location['position']
        )

        # Don't position too close to the existing target.
        return distance >= MIN_OBJECTS_SEPARATION_DISTANCE


class TraversalGoal(InteractiveGoal):
    GOAL_TEMPLATE = {
        'category': tags.tag_to_label(tags.SCENE.TRAVERSAL),
        'domainsInfo': {
            'objects': [
                # TODO
            ],
            'places': [
                # TODO
            ],
            'agents': []
        },
        'sceneInfo': {}
    }

    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.PRIMARY] = (
        tags.tag_to_label(tags.SCENE.INTERACTIVE)
    )
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.SECONDARY] = (
        tags.tag_to_label(tags.SCENE.TRAVERSAL)
    )
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.TERTIARY] = (
        tags.tag_to_label(tags.SCENE.TRAVERSAL)
    )
    GOAL_TEMPLATE['sceneInfo'][tags.SCENE.QUATERNARY] = (
        tags.tag_to_label(tags.SCENE.ACTION_FULL)
    )

    def __init__(self, hypercube_type: str):
        goal_template = copy.deepcopy(TraversalGoal.GOAL_TEMPLATE)
        goal_template['sceneInfo'][tags.SCENE.TERTIARY] = hypercube_type
        super().__init__(tags.SCENE.TRAVERSAL, goal_template)

    # Override
    def choose_target_definition(self, target_number: int) -> ObjectDefinition:
        return self.choose_definition()

    # Override
    def get_target_count(self) -> int:
        return 1

    # Override
    def update_goal_template(
        self,
        goal_template: Dict[str, Any],
        target_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        goal_template['metadata'] = {
            'target': {
                'id': target_list[0]['id'],
                'info': target_list[0]['debug']['info']
            }
        }
        goal_template['description'] = f'Find the ' \
            f'{target_list[0]["debug"]["goalString"]} and move near it.'
        if not NO_TARGET_IMAGES:
            image = find_image_for_object(target_list[0])
            image_name = find_image_name(target_list[0])
            goal_template['metadata']['target']['image'] = image
            goal_template['metadata']['target']['image_name'] = image_name
            goal_template['metadata']['target']['match_image'] = True
        return goal_template

    # Override
    def validate_target_location(
        self,
        target_number: int,
        target_location: Dict[str, Any],
        previously_made_target_list: List[Dict[str, Any]],
        performer_start: Dict[str, Dict[str, float]]
    ) -> bool:
        distance = position_distance(
            performer_start['position'],
            target_location['position']
        )
        # Don't position too close to performer's start location.
        return distance >= MIN_OBJECTS_SEPARATION_DISTANCE
