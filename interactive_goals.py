import copy
import logging
import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AnyStr, Dict, List, Tuple

import exceptions
import geometry
import objects
import tags
from util import (
    finalize_object_definition,
    finalize_object_materials_and_colors,
    retrieve_trained_definition_list
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
    def choose_target_definition(self, target_number: int) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
        """Choose and return an object definition."""
        definition_list = random.choice(retrieve_trained_definition_list(
            objects.get(objects.ObjectDefinitionList.PICKUPABLES)
            if must_be_pickupable
            else objects.get(objects.ObjectDefinitionList.ALL)
        ))
        # Same chance to pick each object definition from the list.
        definition = finalize_object_definition(random.choice(definition_list))
        # Finalize the material here in case we need to make a confusor.
        return random.choice(finalize_object_materials_and_colors(definition))

    def choose_location(
        self,
        definition_or_instance: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]],
        is_target=False
    ) -> Tuple[Dict[str, Any], List[List[Dict[str, float]]]]:
        """Choose and return a location for the given object and the new
        bounds list."""
        def rotation_func():
            return performer_start['rotation']['y']
        bounds_list_copy = copy.deepcopy(bounds_list)
        object_location = geometry.calc_obj_pos(
            performer_start['position'],
            bounds_list_copy,
            definition_or_instance,
            rotation_func=rotation_func
        )
        if not object_location:
            raise exceptions.SceneException(
                f'Cannot position {definition_or_instance["type"]}')
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
    def choose_target_definition(self, target_number: int) -> Dict[str, Any]:
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
                'info': target_list[0]['info']
            }
        }
        goal_template['description'] = f'Find and pick up the ' \
            f'{target_list[0]["goalString"]}.'
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
    def choose_target_definition(self, target_number: int) -> Dict[str, Any]:
        if target_number == 0:
            return self.choose_definition(must_be_pickupable=True)

        if target_number != 1:
            raise exceptions.SceneException(
                f'Expected target with number 0 or 1 but got {target_number}')

        definition_list = random.choice(retrieve_trained_definition_list(
            objects.get(objects.ObjectDefinitionList.STACK_TARGETS)
        ))

        # Same chance to pick each object definition from the list.
        definition = finalize_object_definition(random.choice(definition_list))
        # Finalize the material here in case we need to make a confusor.
        return random.choice(finalize_object_materials_and_colors(definition))

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
                'info': target_list[0]['info']
            },
            'target_2': {
                'id': target_list[1]['id'],
                'info': target_list[1]['info']
            },
            'relationship': ['target_1', relationship.value, 'target_2']
        }
        goal_template['description'] = f'Find and pick up the ' \
            f'{target_list[0]["goalString"]} and move it ' \
            f'{relationship.value} the {target_list[1]["goalString"]}.'
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

        distance = geometry.position_distance(
            previously_made_target_list[0]['shows'][0]['position'],
            target_location['position']
        )

        # Don't position too close to the existing target.
        return distance >= geometry.MIN_OBJECTS_SEPARATION_DISTANCE


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
    def choose_target_definition(self, target_number: int) -> Dict[str, Any]:
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
                'info': target_list[0]['info']
            }
        }
        goal_template['description'] = f'Find the ' \
            f'{target_list[0]["goalString"]} and move near it.'
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
        distance = geometry.position_distance(
            performer_start['position'],
            target_location['position']
        )
        # Don't position too close to performer's start location.
        return distance >= geometry.MIN_OBJECTS_SEPARATION_DISTANCE
