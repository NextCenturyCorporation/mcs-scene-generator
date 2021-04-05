import copy
import logging
import random
import uuid
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

import exceptions
import materials
import tags


def initialize_goal(goal: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize and return the properties in the given goal template."""

    goal_copy = copy.deepcopy(goal)
    for prop in ['category', 'domainsInfo', 'sceneInfo']:
        if prop not in goal_copy:
            raise ValueError(f'Hypercube goal template must have {prop}')

    goal_copy['objectsInfo'] = goal_copy.get('objectsInfo', {})
    goal_copy['objectsInfo'][tags.ALL] = []

    # Add scene tags like 'fallDown', 'moveAcross', 'targetLocation', etc.
    for tag in tags.SCENE_OPTIONAL_TAGS_DICT.values():
        goal_copy['sceneInfo'][tag] = (
            goal_copy['sceneInfo'].get(tag, None)
        )

    # Add scene tags like 'contained', 'trained', 'untrained', etc.
    for tag in tags.SCENE_ROLE_TAGS_DICT.values():
        goal_copy['sceneInfo'][tag] = {}
        if tag == tags.SCENE.COUNT:
            goal_copy['sceneInfo'][tag][tags.ALL] = 0
        if tag != tags.SCENE.COUNT and tag != tags.SCENE.PRESENT:
            goal_copy['sceneInfo'][tag][tags.ANY] = False

    # Add all role-specific scene and objects tags.
    for role in tags.ROLE_DICT.values():
        for tag in tags.SCENE_ROLE_TAGS_DICT.values():
            goal_copy['sceneInfo'][tag][tags.role_to_key(role)] = (
                0 if tag == tags.SCENE.COUNT else False
            )

        goal_copy['objectsInfo'][tags.role_to_key(role)] = []

    return goal_copy


def update_floor_and_walls(
    body_template: Dict[str, Any],
    role_to_object_data_list: Dict[str, Any],
    retrieve_object_list_from_data: Callable[[], List[Dict[str, Any]]],
    scenes: List[Dict[str, Any]],
    floor_material_list=materials.FLOOR_MATERIALS,
    wall_material_list=materials.WALL_MATERIALS
) -> List[Dict[str, Any]]:
    """Change the floor and/or wall materials in each of the given scenes if
    the material is the same color as a non-context object."""

    for prefix, material_list in [
        ('floor', floor_material_list),
        ('wall', wall_material_list)
    ]:
        room_colors = body_template[prefix + 'Colors']
        room_material = body_template[prefix + 'Material']
        object_colors = []
        for role in [
            'target', 'confusor', 'large_container', 'small_container',
            'obstacle', 'occluder', 'non_target'
        ]:
            for object_data in role_to_object_data_list.get(role, []):
                for template in retrieve_object_list_from_data(object_data):
                    if template:
                        object_colors.extend(template['color'])
        choice_list = copy.deepcopy(material_list)
        random.shuffle(choice_list)
        successful = False
        for choice in choice_list:
            if room_colors[0] not in object_colors:
                successful = True
                break
            room_material = choice[0]
            room_colors = choice[1]
        if not successful:
            raise exceptions.SceneException(
                f'Cannot find {prefix} material without color {object_colors}')
        if room_material != body_template[prefix + 'Material']:
            for scene in scenes:
                scene[prefix + 'Material'] = room_material
                scene[prefix + 'Colors'] = room_colors
    return scenes


def update_scene_objects(
    scene: Dict[str, Any],
    role_to_object_list: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Update and return the given scene with the given objects."""

    # Add each object to the scene's 'objects' list.
    scene['objects'] = [
        instance for object_list in role_to_object_list.values()
        for instance in object_list
    ]

    # Add all role-specific scene and objects tags.
    for role in tags.ROLE_DICT.values():
        for instance in scene['objects']:
            instance[tags.role_to_tag(role)] = False

        count = (
            len(role_to_object_list[role])
            if role in role_to_object_list
            else 0
        )

        if (role == tags.ROLES.INTUITIVE_PHYSICS_OCCLUDER):
            # The intuitive physics occluders are always two objects.
            count = (int)(count / 2)

        scene['goal']['sceneInfo'][tags.SCENE.COUNT][
            tags.role_to_key(role)
        ] = count
        scene['goal']['sceneInfo'][tags.SCENE.PRESENT][
            tags.role_to_key(role)
        ] = (count > 0)
        scene['goal']['sceneInfo'][tags.SCENE.COUNT][tags.ALL] += count

    tags.append_object_tags(
        scene['goal']['sceneInfo'],
        scene['goal']['objectsInfo'],
        role_to_object_list
    )

    for role, object_list in role_to_object_list.items():
        for instance in object_list:
            # First add this object's info to the scene's objects tags.
            scene['goal']['objectsInfo'][tags.role_to_key(role)].extend(
                instance['info']
            )

            # Then assign this object's role info.
            instance['info'].append(role)
            instance['role'] = role
            instance[tags.role_to_tag(role)] = True

    return update_scene_objects_tag_lists(scene)


def update_scene_objects_tag_lists(
    scene: Dict[str, Any]
) -> Dict[str, Any]:

    for role in tags.ROLE_DICT.values():
        # Ensure the objects tags have only unique values.
        scene['goal']['objectsInfo'][tags.role_to_key(role)] = list(
            set(scene['goal']['objectsInfo'][tags.role_to_key(role)])
        )

        if role in scene['goal']['objectsInfo'][tags.role_to_key(role)]:
            scene['goal']['objectsInfo'][tags.role_to_key(role)].remove(
                role
            )

        # Add the list of object tags by role to the list of all tags.
        if len(scene['goal']['objectsInfo'][tags.role_to_key(role)]) > 0:
            scene['goal']['objectsInfo'][tags.ALL].extend(
                [role] +
                scene['goal']['objectsInfo'][tags.role_to_key(role)]
            )

    # Ensure the objects tags have only unique values.
    scene['goal']['objectsInfo'][tags.ALL] = list(
        set(scene['goal']['objectsInfo'][tags.ALL])
    )

    # Add all domains tags to the 'all' list.
    scene['goal']['domainsInfo'][tags.ALL] = (
        scene['goal']['domainsInfo'].get(tags.DOMAINS.OBJECTS, []) +
        scene['goal']['domainsInfo'].get(tags.DOMAINS.PLACES, []) +
        scene['goal']['domainsInfo'].get(tags.DOMAINS.AGENTS, [])
    )

    # Add all scene tags to the 'all' list.
    scene['goal']['sceneInfo'][tags.ALL] = list(filter(None, [
        scene['goal']['sceneInfo'].get(tags.SCENE.PRIMARY, None),
        scene['goal']['sceneInfo'].get(tags.SCENE.SECONDARY, None),
        scene['goal']['sceneInfo'].get(tags.SCENE.TERTIARY, None),
        scene['goal']['sceneInfo'].get(tags.SCENE.QUATERNARY, None)
    ]))

    for tag in tags.SCENE_OPTIONAL_TAGS_DICT.values():
        # Ignore fallDown and moveAcross (redundant with sceneSetup).
        if tag != tags.SCENE.FALL_DOWN and tag != tags.SCENE.MOVE_ACROSS:
            tag_label = (
                '' if tag == tags.SCENE.SETUP else tags.tag_to_label(tag)
            )
            tag_value = scene['goal']['sceneInfo'][tag]
            if tag_value:
                scene['goal']['sceneInfo'][tags.ALL].append(
                    ((tag_label + ' ') if tag_label else '') + tag_value
                )

    for tag in tags.SCENE_ROLE_TAGS_DICT.values():
        tag_label = tags.tag_to_label(tag)
        for role in tags.ROLE_DICT.values():
            if scene['goal']['sceneInfo'][tag][tags.role_to_key(role)]:
                scene['goal']['sceneInfo'][tags.ALL].append(role + ' ' + (
                    tag_label if tag != 'count'
                    else str(scene['goal']['sceneInfo'][tag][
                        tags.role_to_key(role)
                    ])
                ))

    return scene


class Hypercube(ABC):
    """Creates a unique hypercube of one or more scenes that each have the same
    goals, objects, and variables, except for specific differences."""

    def __init__(
        self,
        name: str,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any],
        training=False
    ) -> None:
        self._uuid = str(uuid.uuid4()).upper()
        self._name = name
        self._training = training
        goal_copy = initialize_goal(goal_template)
        prefix = ((self._name + ' ') if self._name else '').replace(' ', '_')
        self._scenes = self._create_scenes(body_template, goal_copy)
        for index, scene in enumerate(self._scenes):
            if tags.SCENE.ID not in scene['goal']['sceneInfo']:
                scene['goal']['sceneInfo'][tags.SCENE.ID] = [
                    f'{(index + 1):02}'
                ]
            if tags.SCENE.NAME not in scene['goal']['sceneInfo']:
                scene['goal']['sceneInfo'][tags.SCENE.NAME] = (
                    prefix + scene['goal']['sceneInfo'][tags.SCENE.ID][0]
                )
            scene['goal']['sceneInfo'][tags.SCENE.HYPERCUBE_ID] = (
                scene['goal']['sceneInfo'][tags.SCENE.NAME] + '_' + self._uuid
            )
            scene['goal']['sceneInfo'][tags.ALL].extend(
                [scene['goal']['sceneInfo'][tags.SCENE.NAME]] +
                scene['goal']['sceneInfo'][tags.SCENE.ID]
            )

    @abstractmethod
    def _create_scenes(
        self,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create and return this hypercube's scenes."""
        pass

    @abstractmethod
    def _get_training_scenes(self) -> List[Dict[str, Any]]:
        """Return this hypercube's list of training (non-evaluation) scenes."""
        pass

    def get_name(self) -> str:
        """Return this hypercube's name."""
        return self._name

    def get_scenes(self) -> List[Dict[str, Any]]:
        """Return this hypercube's list of scenes."""
        if self._training:
            scenes = self._get_training_scenes()
            print(f'{self.get_name()} hypercube made '
                  f'{len(scenes)} training scenes')
            return scenes
        print(f'{self.get_name()} hypercube made '
              f'{len(self._scenes)} non-training scenes')
        return self._scenes


class HypercubeFactory(ABC):
    """Builds Hypercubes."""

    def __init__(self, name: str, training: bool) -> None:
        self.name = name
        self.training = training

    @abstractmethod
    def _build(
        self,
        body_template: Dict[str, Any],
        role_to_type: Dict[str, str]
    ) -> Hypercube:
        """Create and return a new hypercube built by this factory."""
        pass

    def build(
        self,
        total: str,
        body_template_function: Callable[[], Dict[str, Any]],
        role_to_type: Dict[str, str],
        throw_error=False
    ) -> List[Hypercube]:
        """Create and return a new list of scenes built by this factory."""
        hypercubes = []
        for count in range(1, total + 1):
            print(f'Generating hypercube {count} / {total}')
            tries = 0
            while tries < 100:
                tries += 1
                try:
                    # Build the hypercube and all of its scenes.
                    hypercube = self._build(
                        body_template_function(),
                        role_to_type
                    )
                    hypercubes.append(hypercube)
                    break
                except (
                    RuntimeError,
                    ZeroDivisionError,
                    TypeError,
                    exceptions.SceneException,
                    ValueError
                ):
                    logging.exception(f'Fail to create {self.name} hypercube')
                    if throw_error or tries >= 100:
                        raise

        return hypercubes
