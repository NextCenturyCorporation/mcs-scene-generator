import copy
import random
import uuid
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

from machine_common_sense.config_manager import Goal

from generator import Scene, SceneException, SceneObject, materials, tags


def initialize_goal(goal_template: Goal) -> Goal:
    """Initialize and return the properties in the given goal template."""

    goal_copy = copy.deepcopy(goal_template)

    scene_info = goal_copy.scene_info
    scene_info[tags.ALL] = scene_info.get(tags.ALL, [])
    scene_info[tags.SCENE.SLICES] = scene_info.get(tags.SCENE.SLICES, [])

    goal_copy.objects_info = goal_copy.objects_info or {}
    goal_copy.objects_info[tags.ALL] = []

    # Add scene tags like 'fallDown', 'moveAcross', 'targetLocation', etc.
    for tag in tags.SCENE_OPTIONAL_TAGS_DICT.values():
        scene_info[tag] = scene_info.get(tag)

    # Add scene tags like 'contained', 'trained', 'untrained', etc.
    for tag in tags.SCENE_ROLE_TAGS_DICT.values():
        scene_info[tag] = {}
        if tag == tags.SCENE.COUNT:
            scene_info[tag][tags.ALL] = 0
        if tag != tags.SCENE.COUNT and tag != tags.SCENE.PRESENT:
            scene_info[tag][tags.ANY] = False

    # Add all role-specific scene and objects tags.
    for role in tags.ROLE_DICT.values():
        for tag in tags.SCENE_ROLE_TAGS_DICT.values():
            scene_info[tag][tags.role_to_key(role)] = (
                0 if tag == tags.SCENE.COUNT else False
            )

        goal_copy.objects_info[tags.role_to_key(role)] = []

    return goal_copy


def update_floor_and_walls(
    scene: Scene,
    role_to_object_data_list: Dict[str, List[Any]],
    retrieve_object_list_from_data: Callable[[Any], List[SceneObject]],
    scenes: List[Scene],
    floor_material_list=materials.FLOOR_MATERIALS,
    wall_material_list=materials.WALL_MATERIALS
) -> List[Scene]:
    """Change the floor and/or wall materials in each of the given scenes if
    the material is the same color as a non-context object."""

    for prefix, material_list in [
        ('floor', floor_material_list),
        ('wall', wall_material_list)
    ]:
        room_colors = scene.debug[prefix + 'Colors']
        room_material = getattr(scene, prefix + '_material')
        object_colors = []
        for role in [
            'target', 'confusor', 'large_container', 'small_container',
            'obstacle', 'occluder', 'non_target'
        ]:
            for object_data in role_to_object_data_list.get(role, []):
                for template in retrieve_object_list_from_data(object_data):
                    if template:
                        object_colors.extend(template['debug']['color'])
        choice_list = copy.deepcopy(material_list)
        random.shuffle(choice_list)
        successful = False
        for choice in choice_list:
            if all([color not in object_colors for color in room_colors]):
                successful = True
                break
            room_material = choice[0]
            room_colors = choice[1]
        if not successful:
            raise SceneException(
                f'Cannot find a {prefix} material without color(s) '
                f'{object_colors}\nCHOICES: {choice_list}\n'
                f'OBJECTS: {role_to_object_data_list}'
            )
        if room_material != getattr(scene, prefix + '_material'):
            for scene in scenes:
                setattr(scene, prefix + '_material', room_material)
                scene.debug[prefix + 'Colors'] = room_colors
    return scenes


def update_scene_objects(
    scene: Scene,
    role_to_object_list: Dict[str, List[SceneObject]]
) -> Scene:
    """Update and return the given scene with the given objects."""

    # Add each object to the scene's 'objects' list.
    scene.objects = [
        instance for object_list in role_to_object_list.values()
        for instance in object_list
    ]

    # Add all role-specific scene and objects tags.
    for role in tags.ROLE_DICT.values():
        for instance in scene.objects:
            instance['debug'][tags.role_to_tag(role)] = False

        count = (
            len(role_to_object_list[role])
            if role in role_to_object_list
            else 0
        )

        if (role == tags.ROLES.INTUITIVE_PHYSICS_OCCLUDER):
            # The intuitive physics occluders are always two objects.
            count = (int)(count / 2)

        scene.goal.scene_info[tags.SCENE.COUNT][
            tags.role_to_key(role)
        ] = count
        scene.goal.scene_info[tags.SCENE.PRESENT][
            tags.role_to_key(role)
        ] = (count > 0)
        scene.goal.scene_info[tags.SCENE.COUNT][tags.ALL] += count

    tags.append_object_tags(
        scene.goal.scene_info,
        scene.goal.objects_info,
        role_to_object_list
    )

    for role, object_list in role_to_object_list.items():
        for instance in object_list:
            # First add this object's info to the scene's objects tags.
            scene.goal.objects_info[tags.role_to_key(role)].extend(
                instance['debug']['info']
            )

            # Then assign this object's role info.
            instance['debug']['info'].append(role)
            instance['debug']['role'] = role
            instance['debug'][tags.role_to_tag(role)] = True

    return update_scene_objects_tag_lists(scene)


def update_scene_objects_tag_lists(
    scene: Scene
) -> Scene:

    for role in tags.ROLE_DICT.values():
        # Ensure the objects tags have only unique values.
        scene.goal.objects_info[tags.role_to_key(role)] = list(
            set(scene.goal.objects_info[tags.role_to_key(role)])
        )

        if role in scene.goal.objects_info[tags.role_to_key(role)]:
            scene.goal.objects_info[tags.role_to_key(role)].remove(
                role
            )

        # Add the list of object tags by role to the list of all tags.
        if len(scene.goal.objects_info[tags.role_to_key(role)]) > 0:
            scene.goal.objects_info[tags.ALL].extend(
                [role] +
                scene.goal.objects_info[tags.role_to_key(role)]
            )

    # Ensure the objects tags have only unique values.
    scene.goal.objects_info[tags.ALL] = list(
        set(scene.goal.objects_info[tags.ALL])
    )

    # Add all domains tags to the 'all' list.
    scene.goal.domains_info[tags.ALL] = (
        scene.goal.domains_info.get(tags.DOMAINS.OBJECTS, []) +
        scene.goal.domains_info.get(tags.DOMAINS.PLACES, []) +
        scene.goal.domains_info.get(tags.DOMAINS.AGENTS, [])
    )

    # Add all scene tags to the 'all' list.
    scene.goal.scene_info[tags.ALL] = list(filter(None, [
        scene.goal.scene_info.get(tags.SCENE.PRIMARY),
        scene.goal.scene_info.get(tags.SCENE.SECONDARY),
        scene.goal.scene_info.get(tags.SCENE.TERTIARY),
        scene.goal.scene_info.get(tags.SCENE.QUATERNARY)
    ]))

    for tag in tags.SCENE_OPTIONAL_TAGS_DICT.values():
        # Ignore fallDown and moveAcross (redundant with sceneSetup).
        if tag != tags.SCENE.FALL_DOWN and tag != tags.SCENE.MOVE_ACROSS:
            tag_label = (
                '' if tag == tags.SCENE.SETUP else tags.tag_to_label(tag)
            )
            tag_value = scene.goal.scene_info[tag]
            if tag_value:
                scene.goal.scene_info[tags.ALL].append(
                    f"{((tag_label + ' ') if tag_label else '')}{tag_value}"
                )

    for tag in tags.SCENE_ROLE_TAGS_DICT.values():
        tag_label = tags.tag_to_label(tag)
        for role in tags.ROLE_DICT.values():
            if scene.goal.scene_info[tag][tags.role_to_key(role)]:
                scene.goal.scene_info[tags.ALL].append(role + ' ' + (
                    tag_label if tag != 'count'
                    else str(scene.goal.scene_info[tag][
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
        starter_scene: Scene,
        task_type: str,
        training=False
    ) -> None:
        self._uuid = str(uuid.uuid4()).upper()
        self._name = name
        self._scenes = []
        self._starter_scene = starter_scene
        self._task_type = task_type
        self._training = training

    def generate_scenes(self) -> List[Scene]:
        """Generate and return the scenes for this hypercube."""
        # Create all the scenes using the starter scene and the goal template.
        goal_template = self._create_goal_template(self._task_type)
        self._scenes = self._create_scenes(self._starter_scene, goal_template)

        # Finalize the slice tags for each scene in this hypercube.
        for scene in self._scenes:
            for tag in self._get_slices():
                scene.goal.scene_info[tags.SCENE.SLICES].append(
                    tags.tag_to_label(tag) + ' ' +
                    str(scene.goal.scene_info[tag])
                )

        # Sort the scenes alphabetically by ID.
        self._scenes = sorted(
            self._scenes,
            key=lambda x: x.goal.scene_info.get(tags.SCENE.ID, [''])[0]
        )

        is_passive_agent = tags.is_passive_agent_task(self._task_type)
        is_passive_physics = tags.is_passive_physics_task(self._task_type)

        # Update specific tags in each scene.
        prefix = ((self._name + ' ') if self._name else '').replace(' ', '_')
        for index, scene in enumerate(self._scenes):
            scene_info = scene.goal.scene_info
            if tags.SCENE.ID not in scene_info:
                scene_info[tags.SCENE.ID] = [f'{(index + 1):02}']
            if tags.SCENE.NAME not in scene_info:
                scene_info[tags.SCENE.NAME] = (
                    prefix + scene_info[tags.SCENE.ID][0]
                )
            scene_info[tags.SCENE.HYPERCUBE_ID] = (
                scene_info[tags.SCENE.NAME] + '_' + self._uuid
            )
            scene_info[tags.ALL].extend(
                [scene_info[tags.SCENE.NAME]] + scene_info[tags.SCENE.ID]
            )
            scene_info[tags.SCENE.DOMAIN_TYPE] = (
                tags.get_domain_type(self._task_type))
            if not (is_passive_agent or is_passive_physics):
                scene_info[tags.SCENE.QUATERNARY] = tags.tag_to_label(
                    tags.SCENE.ACTION_FULL
                    if not len(scene.goal.action_list or []) else
                    tags.SCENE.ACTION_VARIABLE
                )

        return self.get_scenes()

    def _create_goal_template(self, task_type: str) -> Goal:
        """Create and return this hypercube's template for a goal object."""
        goal_template = Goal(
            category='',
            scene_info={},
            # No longer used but kept here to maintain backwards compatibility.
            domains_info={'objects': [], 'places': [], 'agents': []}
        )
        scene_info = goal_template.scene_info
        is_passive_agent = tags.is_passive_agent_task(task_type)
        is_passive_physics = tags.is_passive_physics_task(task_type)
        is_multi_retrieval = tags.is_multi_retrieval(task_type)
        if is_passive_agent:
            goal_template.category = tags.tag_to_label(tags.SCENE.AGENTS)
            scene_info[tags.SCENE.PRIMARY] = tags.tag_to_label(
                tags.SCENE.PASSIVE
            )
            scene_info[tags.SCENE.SECONDARY] = tags.tag_to_label(
                tags.SCENE.AGENTS
            )
            scene_info[tags.SCENE.QUATERNARY] = tags.tag_to_label(
                tags.SCENE.ACTION_NONE
            )
        elif is_passive_physics:
            goal_template.category = tags.tag_to_label(
                tags.SCENE.INTUITIVE_PHYSICS
            )
            scene_info[tags.SCENE.PRIMARY] = tags.tag_to_label(
                tags.SCENE.PASSIVE
            )
            scene_info[tags.SCENE.SECONDARY] = tags.tag_to_label(
                tags.SCENE.INTUITIVE_PHYSICS
            )
            scene_info[tags.SCENE.QUATERNARY] = tags.tag_to_label(
                tags.SCENE.ACTION_NONE
            )
        elif is_multi_retrieval:
            goal_template.category = tags.tag_to_label(
                tags.SCENE.MULTI_RETRIEVAL)
            scene_info[tags.SCENE.PRIMARY] = tags.tag_to_label(
                tags.SCENE.INTERACTIVE
            )
            scene_info[tags.SCENE.SECONDARY] = tags.tag_to_label(
                tags.SCENE.MULTI_RETRIEVAL
            )
        else:
            goal_template.category = tags.tag_to_label(tags.SCENE.RETRIEVAL)
            scene_info[tags.SCENE.PRIMARY] = tags.tag_to_label(
                tags.SCENE.INTERACTIVE
            )
            scene_info[tags.SCENE.SECONDARY] = tags.tag_to_label(
                tags.SCENE.RETRIEVAL
            )
        scene_info[tags.SCENE.TERTIARY] = (
            tags.tag_to_label(task_type) if task_type else
            scene_info[tags.SCENE.SECONDARY]
        )
        return initialize_goal(goal_template)

    @abstractmethod
    def _create_scenes(
        self,
        starter_scene: Scene,
        goal_template: Goal
    ) -> List[Scene]:
        """Create and return this hypercube's scenes."""
        pass

    @abstractmethod
    def _get_slices(self) -> List[str]:
        """Return all of this hypercube's slices (string tags)."""
        pass

    def _get_training_scenes(self) -> List[Scene]:
        """Return this hypercube's list of training (non-evaluation) scenes.
        By default, returns [] (no training data from this hypercube)."""
        return []

    def get_info(self) -> str:
        """Return unique hypercube info. Can override as needed."""
        return ''

    def get_name(self) -> str:
        """Return this hypercube's name."""
        return self._name

    def get_scenes(self) -> List[Scene]:
        """Return this hypercube's list of scenes."""
        if self._training:
            scenes = self._get_training_scenes()
            return scenes
        return self._scenes


class HypercubeFactory(ABC):
    """Builds Hypercubes."""

    def __init__(self, name: str, training: bool = False) -> None:
        self.name = name
        self.training = training
        self.role_to_type = None

    @abstractmethod
    def _build(self, starter_scene: Scene) -> Hypercube:
        """Create and return a new hypercube built by this factory."""
        pass

    def generate_hypercubes(
        self,
        total: str,
        starter_scene_function: Callable[[], Scene],
        role_to_type: Dict[str, str],
        throw_error=False,
        sort_data=False
    ) -> List[Hypercube]:
        """Create and return a new list of hypercubes built by this factory."""
        # Save this now in case it's used by a hypercube factory subclass.
        self.role_to_type = role_to_type

        hypercubes = []
        for count in range(1, total + 1):
            hypercube = self._build(starter_scene_function())
            hypercubes.append(hypercube)
        return hypercubes
