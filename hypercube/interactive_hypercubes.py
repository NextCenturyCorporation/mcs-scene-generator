import copy
import logging
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

from machine_common_sense.config_manager import PerformerStart, Vector3d

from generator import (
    MAX_TRIES,
    DefinitionDataset,
    InteractiveGoal,
    ObjectBounds,
    ObjectDefinition,
    RetrievalGoal,
    Scene,
    SceneException,
    base_objects,
    containers,
    definitions,
    geometry,
    get_step_limit_from_dimensions,
    instances,
    specific_objects,
    tags
)

from .hypercubes import (
    Hypercube,
    HypercubeFactory,
    update_floor_and_walls,
    update_scene_objects
)
from .interactive_plans import (
    InteractivePlan,
    ObjectLocationPlan,
    ObjectPlan,
    create_container_hypercube_plan_list,
    create_eval_4_container_hypercube_plan_list,
    create_obstacle_hypercube_plan_list,
    create_occluder_hypercube_plan_list
)
from .object_data import (
    ObjectData,
    ReceptacleData,
    TargetData,
    identify_larger_definition
)

logger = logging.getLogger(__name__)

ROOM_SIZE_X = list(range(10, 16))
ROOM_SIZE_Y = list(range(3, 6))
ROOM_SIZE_Z = list(range(10, 16))

SMALL_CONTEXT_OBJECT_CHOICES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
SMALL_CONTEXT_OBJECT_WEIGHTS = [5, 5, 10, 10, 12.5, 15, 12.5, 10, 10, 5, 5]

WALL_CHOICES = [0, 1, 2, 3]
WALL_WEIGHTS = [40, 30, 20, 10]
WALL_MAX_WIDTH = 4
WALL_MIN_WIDTH = 1
WALL_HEIGHT = 3
WALL_DEPTH = 0.1
WALL_SEPARATION = 1


def retrieve_template_list(object_data: ObjectData) -> List[Dict[str, Any]]:
    return [object_data.trained_template, object_data.untrained_template]


class InteractiveHypercube(Hypercube):
    """A hypercube of interactive scenes that each have the same goals,
    targets, distractors, walls, materials, and performer starts, except for
    specific differences detailed in its plan."""

    def __init__(
        self,
        starter_scene: Scene,
        goal: InteractiveGoal,
        role_to_type: Dict[str, str],
        plan_name: str,
        plan_list: List[InteractivePlan],
        training=False
    ) -> None:
        self._goal = goal
        self._plan_list = plan_list
        self._role_to_type = role_to_type

        self._initialize_object_data()
        self._validate_object_plan()

        super().__init__(
            goal.get_name() + ((' ' + plan_name) if plan_name else ''),
            starter_scene,
            goal.get_type(),
            training=training
        )

    def _initialize_object_data(self) -> None:
        # Save each possible object's plans across all scenes.
        self._data = {
            'target': [TargetData(self._plan_list[0].target_plan, 0)],
            'confusor': [
                ObjectData(tags.ROLES.CONFUSOR, object_plan) for object_plan
                in self._plan_list[0].confusor_plan_list
            ],
            'large_container': [
                ReceptacleData(tags.ROLES.CONTAINER, object_plan)
                for object_plan in self._plan_list[0].large_container_plan_list
            ],
            'obstacle': [
                ReceptacleData(tags.ROLES.OBSTACLE, object_plan)
                for object_plan in self._plan_list[0].obstacle_plan_list
            ],
            'occluder': [
                ReceptacleData(tags.ROLES.OCCLUDER, object_plan)
                for object_plan in self._plan_list[0].occluder_plan_list
            ],
            'small_container': [
                ReceptacleData(tags.ROLES.CONTAINER, object_plan)
                for object_plan in self._plan_list[0].small_container_plan_list
            ]
        }

        # Assume that each object has a plan in each scene. An object that does
        # not appear in a scene should be given a NONE location plan.
        for scene_plan in self._plan_list[1:]:
            for role, object_plan_list in scene_plan.object_plans().items():
                for index, object_plan in enumerate(object_plan_list):
                    self._data[role][index].append_object_plan(object_plan)

        # Assume only one target plan, and always use the index 0 target.
        self._target_data = self._data['target'][0]
        # Assume only zero or one confusor plan.
        self._confusor_data = (
            self._data['confusor'][0] if len(self._data['confusor']) > 0
            else None
        )

    def _validate_object_plan(self) -> None:
        if any([
            scene_plan.target_plan.definition !=
            self._target_data.original_definition
            for scene_plan in self._plan_list
        ]):
            raise SceneException(
                'Interactive hypercubes cannot currently handle a target with '
                'different definitions across scenes')

        if any(self._target_data.untrained_plan_list):
            raise SceneException(
                'Interactive hypercubes cannot currently handle a target with '
                'a randomly chosen (not pre-defined) untrained shape')

        # Update _assign_each_object_location to handle new location plans.
        for object_data in self._data['target']:
            if (
                object_data.is_between() or object_data.is_far()
            ):
                raise SceneException(
                    'Interactive hypercubes cannot currently handle the '
                    'target location plans: BETWEEN, FAR')

        for object_data in self._data['confusor']:
            if (
                object_data.is_between() or object_data.is_random()
            ):
                raise SceneException(
                    'Interactive hypercubes cannot currently handle the '
                    'confusor location plans: BETWEEN, RANDOM')

        for object_data in (
            self._data['large_container'] + self._data['small_container']
        ):
            if (
                object_data.is_back() or object_data.is_between() or
                object_data.is_close() or object_data.is_far() or
                object_data.is_front() or object_data.is_inside()
            ):
                raise SceneException(
                    'Interactive hypercubes cannot currently handle the '
                    'container location plans: BACK, BETWEEN, CLOSE, FAR, '
                    'FRONT, INSIDE')

        for object_data in (self._data['obstacle'] + self._data['occluder']):
            if (
                object_data.is_back() or object_data.is_far() or
                object_data.is_front() or object_data.is_inside()
            ):
                raise SceneException(
                    'Interactive hypercubes cannot currently handle the '
                    'obstacle or occluder location plans: BACK, FAR, FRONT, '
                    'INSIDE')

    # Override
    def _create_scenes(
        self,
        starter_scene: Scene,
        goal_template: Dict[str, Any]
    ) -> List[Scene]:

        tries = 0
        while True:
            tries += 1
            try:
                logger.debug(
                    f'\n\n{self.get_name()} initialize scenes try {tries}\n')

                # Reset the half-finished scenes, all of their objects, and
                # their other properties on each try.
                scenes = [
                    copy.deepcopy(starter_scene) for _
                    in range(len(self._plan_list))
                ]
                for object_data_list in self._data.values():
                    for object_data in object_data_list:
                        object_data.reset_all_properties()

                # Save the bounds of each object in each of its possible
                # locations across all the scenes to detect collisions with
                # any subsequently positioned objects.
                self._bounds_list = []
                # Save the targets used in the hypercube that are not defined
                # by the plan, if the goal has multiple targets.
                self._common_target_list = []
                # Save the randomized room dimensions in the hypercube.
                self._room_dimensions = self._generate_room_dimensions()
                # Save the performer's start location in the hypercube.
                self._performer_start = self._generate_performer_start(
                    self._room_dimensions
                )
                # Save the small context objects used in the hypercube.
                self._small_context_object_list = []

                # Initialize all of the objects in all of the scenes.
                self._initialize_each_hypercube_object()

                # Update each scene's template with its corresponding objects,
                # goal, tags, and other specific properties.
                for index, scene in enumerate(scenes):
                    self._update_scene_at_index(scene, index, goal_template)

                logger.debug(
                    f'\n\n{self.get_name()} initialize scenes is done\n ')

                scenes = update_floor_and_walls(
                    starter_scene,
                    self._data,
                    retrieve_template_list,
                    scenes
                )

                break

            except SceneException:
                logger.exception(
                    f'{self.get_name()} _initialize_each_hypercube_object')

            if tries >= MAX_TRIES:
                raise SceneException(
                    f'{self.get_name()} cannot successfully initialize scenes '
                    f'-- please redo.')

        return scenes

    # Override
    def _get_slices(self) -> List[str]:
        # This hypercube handles setting its slice tags elsewhere.
        return []

    # Override
    def _get_training_scenes(self) -> List[Scene]:
        return [
            scene for scene in self._scenes
            if not scene.debug['evaluationOnly']
        ]

    def _assign_confusor_obstacle_occluder_location(
        self,
        target_data: TargetData,
        target_or_receptacle_definition: ObjectDefinition,
        confusor_data: Optional[ObjectData],
        obstacle_occluder_data_list: List[ObjectData],
        large_container_data_list: List[ReceptacleData],
        goal: InteractiveGoal,
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[ObjectBounds],
        plans_to_locations: Dict[ObjectLocationPlan, List[Dict[str, Any]]]
    ) -> None:
        """Generate and assign locations to the given confusor, obstacle, and
        occluder objects, if needed. Will update the given bounds_list."""

        # Objects positioned relative to the target (confusors, obstacles, and
        # occluders) must each choose new locations for each of the target's
        # distinct locations (or its receptacle's locations) across scenes.
        target_locations_with_indexes = (
            target_data.locations_with_indexes(large_container_data_list)
        )

        # Next, choose a location for an obstacle/occluder either between the
        # performer's start location and the target or behind the target (if
        # needed). Assume only one obstacle or occluder is ever "in between"
        # OR "close" in a single scene.
        for target_location_plan, indexes in target_locations_with_indexes:
            for object_data in obstacle_occluder_data_list:
                is_obstacle = (object_data.role == tags.ROLES.OBSTACLE)
                if object_data.is_between():
                    # Use the same location for the object across scenes in
                    # which the target is in this specific location.
                    self._assign_single_obstacle_occluder_location(
                        object_data,
                        target_or_receptacle_definition,
                        plans_to_locations[target_location_plan],
                        performer_start,
                        bounds_list,
                        'between',
                        object_data.assign_location_between,
                        indexes,
                        obstruct=(not is_obstacle),
                        unreachable=is_obstacle
                    )
                if object_data.is_close():
                    # Use the same location for the object across scenes in
                    # which the target is in this specific location.
                    self._assign_single_obstacle_occluder_location(
                        object_data,
                        target_or_receptacle_definition,
                        plans_to_locations[target_location_plan],
                        performer_start,
                        bounds_list,
                        'behind',
                        object_data.assign_location_close,
                        indexes,
                        behind=True
                    )
                if object_data.is_random():
                    # Use the same location for the object across scenes in
                    # which the target is in this specific location.
                    location = self._generate_random_location(
                        object_data.trained_definition,
                        goal,
                        performer_start,
                        bounds_list,
                        target_location=(
                            plans_to_locations[target_location_plan]
                        ),
                        second_definition=object_data.untrained_definition
                    )
                    logger.debug(
                        f'{self.get_name()} obstacle/occluder location '
                        f'randomly chosen but not obstructing target: '
                        f'{location}')
                    bounds = object_data.assign_location_random(location)
                    bounds_list.extend(bounds)

        # Next, choose a location for the confusor, close to or far from the
        # target (if needed).
        if confusor_data:
            for target_location_plan, indexes in target_locations_with_indexes:
                if confusor_data.is_close():
                    # Use the same location for the object across scenes in
                    # which the target is in this specific location.
                    location = self._generate_close_to(
                        confusor_data.larger_definition(),
                        target_or_receptacle_definition,
                        plans_to_locations[target_location_plan],
                        performer_start,
                        bounds_list,
                        adjacent=True
                    )
                    logger.debug(
                        f'{self.get_name()} confusor location close to: '
                        f'{location}')
                    bounds = confusor_data.assign_location_close(
                        location,
                        indexes
                    )
                    bounds_list.extend(bounds)
                if confusor_data.is_far():
                    # Use the same location for the object across scenes in
                    # which the target is in this specific location.
                    location = self._generate_far_from(
                        confusor_data.larger_definition(),
                        plans_to_locations[target_location_plan],
                        performer_start,
                        bounds_list
                    )
                    logger.debug(
                        f'{self.get_name()} confusor location far from: '
                        f'{location}')
                    bounds = confusor_data.assign_location_far(
                        location,
                        indexes
                    )
                    bounds_list.extend(bounds)

    def _assign_container_location(
        self,
        container_data_list: List[ReceptacleData],
        goal: InteractiveGoal,
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[ObjectBounds]
    ) -> None:
        """Generate and assign locations to the given container receptacle
        objects, if needed. Will update the given bounds_list."""

        # Next, choose the locations for the remaining containers (if needed).
        for container_data in container_data_list:
            if container_data.is_random():
                # Use the same location for the object across scenes in which
                # the object is randomly positioned.
                location = self._generate_random_location(
                    container_data.larger_definition(),
                    goal,
                    performer_start,
                    bounds_list
                )
                logger.debug(
                    f'{self.get_name()} container location randomly chosen: '
                    f'{location}')
                bounds = container_data.assign_location_random(location)
                bounds_list.extend(bounds)

    def _assign_front_and_back_location(
        self,
        target_data: TargetData,
        target_or_receptacle_definition: ObjectDefinition,
        confusor_data_list: List[ObjectData],
        bounds_list: List[ObjectBounds]
    ) -> Dict[ObjectLocationPlan, List[Dict[str, Any]]]:
        """Generate and assign front and back locations to the given target and
        confusor objects, if needed. Will update the given bounds_list. Return
        the target's location corresponding to each unique location plan."""

        # Save the target's location corresponding to each location plan.
        plans_to_locations = {}

        front_and_back_object_data_list = [target_data] + confusor_data_list

        if any([
            (object_data.is_front() or object_data.is_back()) for object_data
            in front_and_back_object_data_list
        ]):
            # Assume only one object is ever "in front" and only one object
            # is ever "in back" in a single scene, so use the same front and
            # back locations on each relevant object.
            location_front, location_back = self._generate_front_and_back(
                target_or_receptacle_definition,
                target_data.choice
            )
            logger.debug(
                f'{self.get_name()} location in front of performer start:'
                f'{location_front}')
            logger.debug(
                f'{self.get_name()} location in back of performer start:'
                f'{location_back}')
            for object_data in front_and_back_object_data_list:
                bounds = object_data.assign_location_front(location_front)
                bounds_list.extend(bounds)
                bounds = object_data.assign_location_back(location_back)
                bounds_list.extend(bounds)
            plans_to_locations[ObjectLocationPlan.FRONT] = location_front
            plans_to_locations[ObjectLocationPlan.BACK] = location_back

        # We assume the performer_start won't be modified past here.
        logger.debug(
            f'{self.get_name()} performer start: {self._performer_start}')

        return plans_to_locations

    def _assign_object_location_inside_container(
        self,
        target_data: TargetData,
        confusor_data: Optional[ObjectData],
        large_container_data_list: List[ReceptacleData]
    ) -> None:
        """Generate and assign locations to the given target and confusor
        objects inside the given container objects, if needed. Will update the
        given bounds_list."""

        target_contained_indexes = target_data.contained_indexes(
            large_container_data_list,
            confusor_data
        )

        # Finally, position the target and confusor inside containers.
        for index, container_data, confusor_data in target_contained_indexes:
            # Create a new instance of each object to use in this scene.
            target_instance = copy.deepcopy(target_data.trained_template)
            containment = (
                container_data.untrained_containment
                if container_data.untrained_plan_list[index]
                else container_data.trained_containment
            )
            # If confusor_data is None, put just the target in the container.
            if not confusor_data:
                containers.put_object_in_container(
                    target_instance,
                    container_data.instance_list[index],
                    containment.area_index,
                    containment.target_angle
                )
            # Else, put both the target and confusor together in the container.
            else:
                confusor_instance = copy.deepcopy(
                    confusor_data.untrained_template
                    if confusor_data.untrained_plan_list[index]
                    else confusor_data.trained_template
                )
                containers.put_objects_in_container(
                    target_instance,
                    confusor_instance,
                    container_data.instance_list[index],
                    containment.area_index,
                    containment.orientation,
                    containment.target_angle,
                    containment.confusor_angle
                )
                # Save the confusor instance in the hypercube data.
                confusor_data.instance_list[index] = confusor_instance
            # Save the target instance in the hypercube data.
            target_data.instance_list[index] = target_instance

        confusor_contained_indexes = confusor_data.contained_indexes(
            large_container_data_list,
            target_data
        ) if confusor_data else []

        for index, container_data, target_data in confusor_contained_indexes:
            # Create a new instance of each object to use in this scene.
            confusor_instance = copy.deepcopy(
                confusor_data.untrained_template
                if confusor_data.untrained_plan_list[index]
                else confusor_data.trained_template
            )
            # If target_data is None, put just the confusor in the container.
            if not target_data:
                containers.put_object_in_container(
                    confusor_instance,
                    container_data.instance_list[index],
                    container_data.area_index,
                    container_data.confusor_angle
                )
                # Save the confusor instance in the hypercube data.
                confusor_data.instance_list[index] = confusor_instance
            # Else, we already put both objects together in a container, above.

    def _assign_single_obstacle_occluder_location(
        self,
        obstacle_occluder_data: ObjectData,
        target_or_receptacle_definition: ObjectDefinition,
        target_location: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[ObjectBounds],
        debug_label: str,
        location_function: Callable,
        indexes: List[float],
        behind: bool = False,
        obstruct: bool = False,
        unreachable: bool = False
    ) -> None:
        """Generate and assign new locations to a single given obstacle or
        occluder using the given function either obstructing or behind the
        target. Find separate locations for both the trained and the untrained
        definitions because each must be able to obstruct the target."""
        trained_location = self._generate_close_to(
            obstacle_occluder_data.trained_definition,
            target_or_receptacle_definition,
            target_location,
            performer_start,
            bounds_list,
            behind=behind,
            obstruct=obstruct,
            unreachable=unreachable
        )
        logger.debug(
            f'{self.get_name()} trained obstacle/occluder location '
            f'{debug_label} target and performer start: {trained_location}')
        untrained_location = self._generate_close_to(
            obstacle_occluder_data.untrained_definition,
            target_or_receptacle_definition,
            target_location,
            performer_start,
            bounds_list,
            behind=behind,
            obstruct=obstruct,
            unreachable=unreachable
        )
        logger.debug(
            f'{self.get_name()} untrained obstacle/occluder location '
            f'{debug_label} target and performer start: {untrained_location}')
        bounds_trained = location_function(trained_location, [
            index for index in indexes
            if not obstacle_occluder_data.untrained_plan_list[index]
        ])
        bounds_list.extend(bounds_trained)
        bounds_untrained = location_function(untrained_location, [
            index for index in indexes
            if obstacle_occluder_data.untrained_plan_list[index]
        ])
        bounds_list.extend(bounds_untrained)

    def _assign_target_location(
        self,
        target_data: TargetData,
        target_or_receptacle_definition: ObjectDefinition,
        container_data: Optional[ReceptacleData],
        confusor_data_list: List[ObjectData],
        goal: InteractiveGoal,
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[ObjectBounds]
    ) -> Dict[ObjectLocationPlan, List[Dict[str, Any]]]:
        """Generate and assign locations to the given target, as well as the
        given target's receptacle and confusor objects if needed. Will update
        the given bounds_list. Return the target's location corresponding to
        each unique location plan."""

        # First, choose the locations for the objects positioned relative to
        # the performer's start location (if needed), both in front of it and
        # in back of it. Do FIRST because it may change performer_start.
        plans_to_locations = self._assign_front_and_back_location(
            target_data,
            target_or_receptacle_definition,
            confusor_data_list,
            bounds_list
        )

        # Next, choose the locations for the target's container (if needed).
        target_container_location = None
        if container_data and container_data.is_random():
            # Use the same location for the object across scenes in which
            # the object is randomly positioned.
            target_container_location = self._generate_random_location(
                container_data.larger_definition(),
                goal,
                performer_start,
                bounds_list
            )
            logger.debug(
                f'{self.get_name()} container location randomly chosen: '
                f'{target_container_location}')
            bounds = container_data.assign_location_random(
                target_container_location
            )
            bounds_list.extend(bounds)

        # Next, choose a location close to the target's container (if any).
        # Assume a "close" target is always close to its container.
        if target_data.is_close():
            target_definition = target_data.larger_definition()
            # If the target was turned sideways, revert it for the location
            # close to the target's container.
            if target_definition.notSideways:
                target_definition = copy.deepcopy(target_definition)
                target_definition.dimensions = (
                    target_definition.notSideways['dimensions']
                )
                target_definition.offset = (
                    target_definition.notSideways['offset']
                )
                target_definition.positionY = (
                    target_definition.notSideways['positionY']
                )
                target_definition.rotation = (
                    target_definition.notSideways['rotation']
                )
            location = self._generate_close_to(
                target_definition,
                container_data.larger_definition(),
                target_container_location,
                performer_start,
                bounds_list
            )
            logger.debug(
                f'{self.get_name()} target location close to the first '
                f'large container: {location}')
            bounds = target_data.assign_location_close(
                location,
                None
            )
            bounds_list.extend(bounds)
            plans_to_locations[ObjectLocationPlan.CLOSE] = location

        # Next, handle the remaining cases for choosing the target's location.
        if target_data.is_random():
            # Use the same location for the target across scenes in which the
            # target is positioned randomly.
            location = self._generate_random_location(
                target_or_receptacle_definition,
                goal,
                performer_start,
                bounds_list,
                target_choice=target_data.choice
            )
            logger.debug(
                f'{self.get_name()} target location randomly chosen: '
                f'{location}')
            bounds = target_data.assign_location_random(location)
            bounds_list.extend(bounds)
            plans_to_locations[ObjectLocationPlan.RANDOM] = location

        return plans_to_locations

    def _assign_each_object_location(self) -> None:
        """Assign each object's final location in all of the scenes by creating
        separate instances of them to use in each individual scene."""

        # Use the larger definition of the target or its receptacle in any
        # scene to save a big enough area for all objects.
        larger_target_definition = self._target_data.larger_definition_of(
            self._data['large_container'],
            self._confusor_data
        )

        logger.debug(
            f'{self.get_name()} larger definition of trained/untrained '
            f'target/confusor/container: {larger_target_definition}')

        # Save the target's location corresponding to each location plan.
        target_location_plans_to_locations = self._assign_target_location(
            self._target_data,
            larger_target_definition,
            # Assume the 1st large container may have the target inside of it.
            self._data['large_container'][0]
            if len(self._data['large_container']) > 0 else None,
            self._data['confusor'],
            self._goal,
            self._performer_start,
            self._bounds_list
        )

        self._assign_confusor_obstacle_occluder_location(
            self._target_data,
            larger_target_definition,
            self._confusor_data,
            self._data['obstacle'] + self._data['occluder'],
            self._data['large_container'],
            self._goal,
            self._performer_start,
            self._bounds_list,
            target_location_plans_to_locations
        )

        self._assign_container_location(
            # Assume the 1st large container may have the target inside of it,
            # and thus it will have been positioned previously, but the other
            # containers will not have any objects inside of them.
            self._data['large_container'][1:] + self._data['small_container'],
            self._goal,
            self._performer_start,
            self._bounds_list
        )

        self._assign_object_location_inside_container(
            self._target_data,
            self._confusor_data,
            self._data['large_container']
        )

    def _assign_confusor_definition(
        self,
        confusor_data: Optional[ObjectData],
        target_definition: ObjectDefinition
    ) -> None:
        """Update the given confusor data with its object definition using the
        given target data."""

        if not confusor_data:
            return

        dataset = specific_objects.get_interactable_definition_dataset()
        trained_dataset = dataset.filter_on_trained()
        untrained_dataset = dataset.filter_on_untrained(
            tags.SCENE.UNTRAINED_SHAPE
        )

        if not confusor_data.trained_definition:
            confusor_data.trained_definition = (
                definitions.get_similar_definition(
                    target_definition,
                    trained_dataset
                )
            )
            if not confusor_data.trained_definition:
                raise SceneException(
                    f'{self.get_name()} cannot find trained confusor '
                    f'size={trained_dataset.size()} '
                    f'target={target_definition}')

        if not confusor_data.untrained_definition:
            confusor_data.untrained_definition = (
                definitions.get_similar_definition(
                    target_definition,
                    untrained_dataset
                )
            )
            if not confusor_data.untrained_definition:
                raise SceneException(
                    f'{self.get_name()} cannot find untrained confusor '
                    f'size={untrained_dataset.size()} '
                    f'target={target_definition}')

        logger.debug(
            f'{self.get_name()} confusor definition: '
            f'trained={confusor_data.trained_definition}'
            f'untrained={confusor_data.untrained_definition}')

    def _choose_small_context_definition(
        self,
        target_confusor_data_list: List[ObjectData]
    ) -> Dict[str, Any]:
        """Choose and return a small context object definition for the given
        target and confusor objects from the given definition list."""
        return specific_objects.choose_distractor_definition([
            object_data.trained_definition.shape for object_data
            in target_confusor_data_list
        ] + [
            object_data.untrained_definition.shape for object_data
            in target_confusor_data_list if object_data.untrained_definition
        ])

    def _assign_obstacle_or_occluder_definition(
        self,
        object_data: ObjectData,
        target_definition: ObjectDefinition,
        is_occluder: bool
    ) -> None:
        """Update the given obstacle or occluder data with its object
        definition using the given target data."""

        dataset = (
            specific_objects.get_occluder_definition_dataset() if is_occluder
            else specific_objects.get_obstacle_definition_dataset()
        )
        trained_dataset = dataset.filter_on_trained()
        untrained_dataset = dataset.filter_on_untrained(
            tags.SCENE.UNTRAINED_SHAPE
        )

        if not object_data.trained_definition:
            object_data.trained_definition = (
                self._choose_obstacle_or_occluder_definition(
                    target_definition,
                    trained_dataset,
                    is_occluder
                )
            )

        if not object_data.untrained_definition:
            object_data.untrained_definition = (
                self._choose_obstacle_or_occluder_definition(
                    target_definition,
                    untrained_dataset,
                    is_occluder
                )
            )

        logger.debug(
            f'{self.get_name()} {"occluder" if is_occluder else "obstacle"} '
            f'definition: trained={object_data.trained_definition} '
            f'untrained={object_data.untrained_definition}')

    def _choose_obstacle_or_occluder_definition(
        self,
        target_definition: ObjectDefinition,
        definition_dataset: DefinitionDataset,
        is_occluder: bool
    ) -> Dict[str, Any]:
        """Choose and return an obstacle or occluder definition for the given
        target object from the given definition list."""

        output = geometry.retrieve_obstacle_occluder_definition_list(
            target_definition,
            definition_dataset,
            is_occluder
        )
        if not output:
            raise SceneException(
                f'{self.get_name()} cannot find '
                f'{"occluder" if is_occluder else "obstacle"} '
                f'size={definition_dataset.size()} '
                f'target={target_definition}')
        definition, angle = output
        # Note that this rotation must be also modified with the final
        # performer start Y.
        definition.rotation.y += angle
        return definition

    def _assign_container_definition(
        self,
        container_data: ReceptacleData,
        target_data: TargetData,
        confusor_data: Optional[ObjectData],
        find_invalid_container: bool = False
    ) -> None:
        """Update the given container data with its object definition using the
        given target and confusor data and whether it should be a valid or an
        invalid size to fit either or both of the objects inside of it."""

        dataset = specific_objects.get_container_openable_definition_dataset()
        trained_dataset = dataset.filter_on_trained()
        untrained_dataset = dataset.filter_on_untrained(
            tags.SCENE.UNTRAINED_SHAPE
        )

        if not container_data.trained_definition:
            (
                definition,
                area_index,
                orientation,
                target_angle,
                confusor_angle
            ) = self._choose_container_definition(
                target_data,
                confusor_data,
                confusor_data.trained_definition if confusor_data else None,
                trained_dataset,
                find_invalid_container
            )

            container_data.trained_definition = definition
            container_data.trained_containment.area_index = area_index
            container_data.trained_containment.orientation = orientation
            container_data.trained_containment.target_angle = target_angle
            container_data.trained_containment.confusor_angle = confusor_angle

        if not container_data.untrained_definition:
            (
                definition,
                area_index,
                orientation,
                target_angle,
                confusor_angle
            ) = self._choose_container_definition(
                target_data,
                confusor_data,
                confusor_data.untrained_definition if confusor_data else None,
                untrained_dataset,
                find_invalid_container
            )

            container_data.untrained_definition = definition
            container_data.untrained_containment.area_index = area_index
            container_data.untrained_containment.orientation = orientation
            container_data.untrained_containment.target_angle = target_angle
            container_data.untrained_containment.confusor_angle = (
                confusor_angle
            )

        logger.debug(
            f'{self.get_name()} container definition: '
            f'trained={container_data.trained_definition} '
            f'untrained={container_data.untrained_definition}')

    def _choose_container_definition(
        self,
        target_data: TargetData,
        confusor_data: Optional[ObjectData],
        confusor_definition: Optional[ObjectDefinition],
        definition_dataset: DefinitionDataset,
        find_invalid_container: bool = False,
    ) -> Tuple[Dict[str, Any], int, containers.Orientation, float, float]:
        """Choose and return a valid or an invalid container definition for the
        given target and confusor objects from the given definition list."""

        container_definition = None
        area_index = None
        orientation = None
        target_angle = None
        confusor_angle = None

        target_definition_list = [target_data.trained_definition]
        # Also try the target definition's sideways option if it exists.
        if target_data.trained_definition.sideways:
            sideways_definition = copy.deepcopy(target_data.trained_definition)
            # Save the original properties.
            sideways_definition.notSideways = {
                'dimensions': sideways_definition.dimensions,
                'offset': sideways_definition.offset,
                'positionY': sideways_definition.positionY,
                'rotation': sideways_definition.rotation
            }
            # Override the original properties with the sideways properties.
            sideways_definition.dimensions = (
                sideways_definition.sideways['dimensions']
            )
            sideways_definition.offset = (
                sideways_definition.sideways['offset']
            )
            sideways_definition.positionY = (
                sideways_definition.sideways['positionY']
            )
            sideways_definition.rotation = (
                sideways_definition.sideways['rotation']
            )
            sideways_definition.sideways = None
            target_definition_list.append(sideways_definition)

        # Get the groups from the dataset so we can randomize them correctly.
        definition_groups = definition_dataset.groups()
        group_indexes = list(range(len(definition_groups)))
        inner_indexes = [
            list(range(len(definition_selections)))
            for definition_selections in definition_groups
        ]

        while any([len(indexes) for indexes in inner_indexes]):
            # Choose a random group, then choose a random list in that group.
            group_index = random.choice(group_indexes)
            inner_index = random.choice(inner_indexes[group_index])
            # Remove the chosen inner index from its list.
            inner_indexes[group_index] = [
                i for i in inner_indexes[group_index] if i != inner_index
            ]
            # If there are no more defs available for a group, remove it.
            if not len(inner_indexes[group_index]):
                group_indexes = [i for i in group_indexes if i != group_index]
            # Choose a random material for the chosen definition.
            definition = random.choice(
                definition_groups[group_index][inner_index]
            )

            # If needed, find an enclosable container that can hold both the
            # target and the confusor together.
            if target_data.containerize_with(confusor_data):
                for target_definition in target_definition_list:
                    valid_containment = containers.can_contain_both(
                        definition,
                        target_definition,
                        confusor_definition
                    )
                    if valid_containment and not find_invalid_container:
                        target_data.trained_definition = target_definition
                        container_definition = definition
                        area_index, angles, orientation = valid_containment
                        target_angle = angles[0]
                        confusor_angle = angles[1]
                        break
                    elif not valid_containment and find_invalid_container:
                        target_data.trained_definition = target_definition
                        container_definition = definition
                        break

            # Else, find an enclosable container that can hold either the
            # target or confusor individually.
            else:
                confusor_definition_or_none = (
                    confusor_definition if confusor_data and
                    confusor_data.is_inside() else None
                )

                if not target_data.is_inside():
                    target_definition_list = [None]

                for target_definition in target_definition_list:
                    valid_containment = containers.can_contain(
                        definition,
                        target_definition,
                        confusor_definition_or_none
                    )
                    if valid_containment and not find_invalid_container:
                        if target_definition:
                            target_data.trained_definition = (
                                target_definition
                            )
                        container_definition = definition
                        area_index, angles = valid_containment
                        target_angle = angles[0]
                        confusor_angle = angles[1]
                        break
                    elif not valid_containment and find_invalid_container:
                        if target_definition:
                            target_data.trained_definition = (
                                target_definition
                            )
                        container_definition = definition
                        break

            if container_definition:
                break

        if not container_definition:
            raise SceneException(
                f'{self.get_name()} cannot create '
                f'{"small" if find_invalid_container else "large"} '
                f'container size={definition_dataset.size()} '
                f'target={target_data.trained_definition}\n'
                f'confusor={confusor_definition}')

        return (
            container_definition, area_index, orientation, target_angle,
            confusor_angle
        )

    def _assign_target_definition(
        self,
        target_data: TargetData,
        goal: InteractiveGoal
    ) -> None:
        """Update the given target data with its object definition using the
        given interactive goal."""

        if not target_data.trained_definition:
            target_data.trained_definition = goal.choose_target_definition(
                target_data.choice
            )

        logger.debug(
            f'{self.get_name()} target definition: '
            f'{target_data.trained_definition}')

    def _create_target_list(
        self,
        goal: InteractiveGoal,
        performer_start: Dict[str, float],
        existing_bounds_list: List[ObjectBounds],
        target_validation_list: List[Dict[str, float]],
        start_index: int = None,
        end_index: int = None
    ) -> Tuple[List[Dict[str, Any]], List[ObjectBounds]]:
        """Create and return each of the goal's targets between the start_index
        and the end_index. Used if the goal needs more targets than are defined
        by the hypercube's plan. Changes the bounds_list."""

        valid_start_index = 0 if start_index is None else start_index

        # Only create targets up to the given index, or create each of the
        # targets if no end_index was given. Keep each existing target.
        valid_end_index = (
            goal.get_target_count() if end_index is None else end_index
        )

        if valid_start_index >= valid_end_index:
            return [], existing_bounds_list

        target_list = []
        bounds_list = existing_bounds_list

        for i in range(valid_start_index, valid_end_index):
            definition = goal.choose_target_definition(i)
            for _ in range(MAX_TRIES):
                location, possible_bounds_list = goal.choose_location(
                    definition,
                    performer_start,
                    existing_bounds_list,
                    is_target=True,
                    room_dimensions=self._room_dimensions
                )
                if goal.validate_target_location(
                    i,
                    location,
                    target_validation_list,
                    performer_start
                ):
                    break
                location = None
            if not location:
                raise SceneException(
                    f'{self.get_name()} cannot find suitable location '
                    f'target={definition}')
            bounds_list = possible_bounds_list
            target_instance = instances.instantiate_object(
                definition,
                location
            )
            target_list.append(target_instance)

        return target_list, bounds_list

    def _generate_front_and_back(
        self,
        definition: ObjectDefinition,
        target_choice: int = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate a location in front of and (if needed) in back of the
        performer's start location. May change the global performer_start if
        it's needed to generate the two locations. Return the front and back
        locations."""

        location_front = None
        location_back = None

        for _ in range(MAX_TRIES):
            location_front = self._identify_front(
                self._goal,
                self._performer_start,
                definition,
                target_choice
            )
            if location_front:
                location_back = self._identify_back(
                    self._goal,
                    self._performer_start,
                    definition,
                    target_choice
                )
                if location_back:
                    break
            location_front = None
            location_back = None
            self._performer_start = self._generate_performer_start(
                self._room_dimensions
            )

        if not location_front or not location_back:
            raise SceneException(
                f'{self.get_name()} cannot position performer start in '
                f'front of and in back of object={definition}')

        return location_front, location_back

    def _generate_close_to(
        self,
        object_definition: ObjectDefinition,
        existing_definition: ObjectDefinition,
        existing_location: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[ObjectBounds],
        adjacent: bool = False,
        behind: bool = False,
        obstruct: bool = False,
        unreachable: bool = False
    ) -> Dict[str, Any]:
        """Generate and return a new location for the given object very close
        to the given previously-positioned object and its given location."""

        location_close = geometry.generate_location_in_line_with_object(
            object_definition,
            existing_definition,
            existing_location,
            performer_start,
            bounds_list,
            adjacent=adjacent,
            behind=behind,
            obstruct=obstruct,
            unreachable=unreachable,
            room_dimensions=self._room_dimensions
        )

        if not location_close:
            if adjacent:
                raise SceneException(
                    f'{self.get_name()} cannot position object adjacent to '
                    f'existing:\nperformer_start={performer_start}\n'
                    f'object={object_definition}\n'
                    f'existing={existing_definition}\n'
                    f'location={existing_location}\nbounds={bounds_list}')
            elif behind:
                raise SceneException(
                    f'{self.get_name()} cannot position object directly in '
                    f'back of existing:\nperformer_start={performer_start}\n'
                    f'object={object_definition}\n'
                    f'existing={existing_definition}\n'
                    f'location={existing_location}\nbounds={bounds_list}')
            raise SceneException(
                f'{self.get_name()} cannot position object directly in '
                f'front of existing:\nperformer_start={performer_start}\n'
                f'object={object_definition}\n'
                f'existing={existing_definition}\n'
                f'location={existing_location}\nbounds={bounds_list}')

        return location_close

    def _generate_far_from(
        self,
        object_definition: ObjectDefinition,
        existing_location: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[ObjectBounds]
    ) -> Dict[str, Any]:
        """Generate and return a new location for the given object far away
        from the given location."""

        for _ in range(MAX_TRIES):
            bounds_list_copy = copy.deepcopy(bounds_list)
            location_far = geometry.calc_obj_pos(
                performer_start['position'],
                bounds_list_copy,
                object_definition,
                room_dimensions=self._room_dimensions
            )
            if not geometry.are_adjacent(
                existing_location,
                location_far,
                distance=geometry.MIN_OBJECTS_SEPARATION_DISTANCE
            ):
                break
            location_far = None

        if not location_far:
            raise SceneException(
                f'{self.get_name()} cannot position object far from existing: '
                f'object={object_definition}\nexisting={existing_location}')

        return location_far

    def _generate_performer_start(
        self,
        room_dimensions: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """Generate and return the performer's starting location dict."""
        # Add or subtract the performer width from the room dimensions to
        # ensure the performer agent can move behind any object.
        room_x_min = -(room_dimensions['x'] / 2.0) + geometry.PERFORMER_WIDTH
        room_z_min = -(room_dimensions['z'] / 2.0) + geometry.PERFORMER_WIDTH
        room_x_max = (room_dimensions['x'] / 2.0) - geometry.PERFORMER_WIDTH
        room_z_max = (room_dimensions['z'] / 2.0) - geometry.PERFORMER_WIDTH
        return {
            'position': {
                'x': round(
                    random.uniform(room_x_min, room_x_max),
                    geometry.POSITION_DIGITS
                ),
                'y': 0,
                'z': round(
                    random.uniform(room_z_min, room_z_max),
                    geometry.POSITION_DIGITS
                )
            },
            'rotation': {
                'x': 0,
                'y': geometry.random_rotation(),
                'z': 0
            }
        }

    def _generate_random_location(
        self,
        definition: ObjectDefinition,
        goal: InteractiveGoal,
        performer_start: Dict[str, float],
        bounds_list: List[ObjectBounds],
        target_choice: int = None,
        target_location: Dict[str, Any] = None,
        second_definition: ObjectDefinition = None
    ) -> Dict[str, Any]:
        """Generate a random location and return it twice."""

        for _ in range(MAX_TRIES):
            location_random, _ = goal.choose_location(
                identify_larger_definition(definition, second_definition)
                if second_definition else definition,
                performer_start,
                bounds_list,
                is_target=(target_choice is not None),
                room_dimensions=self._room_dimensions
            )
            if location_random:
                # If generating a location for the target object...
                if target_choice:
                    if goal.validate_target_location(
                        target_choice,
                        location_random,
                        bounds_list,
                        performer_start
                    ):
                        # Successful
                        break
                # If generating a location that must ensure the visibility of
                # this object, the target object, and other critical objects to
                # the performer's start location...
                elif target_location:
                    # Assume that all of the bounds that have been set by now
                    # will only be for critical objects (specifically targets,
                    # confusors, containers, obstacles, occluders).
                    for bounds in bounds_list:
                        bounds_poly = bounds.polygon_xz
                        # Also validate the second object definition, if given.
                        second_bounds = geometry.create_bounds(
                            dimensions=vars(second_definition.dimensions),
                            offset=vars(second_definition.offset),
                            position=location_random['position'],
                            rotation=location_random['rotation'],
                            standing_y=second_definition.positionY
                        )
                        # This location should not completely obstruct or be
                        # obstructed by any critical object's location.
                        if geometry.does_fully_obstruct_target(
                            performer_start['position'],
                            location_random,
                            bounds_poly
                        ) or geometry.does_fully_obstruct_target(
                            performer_start['position'],
                            {'boundingBox': bounds},
                            geometry.get_bounding_polygon(location_random)
                        ) or geometry.does_fully_obstruct_target(
                            performer_start['position'],
                            {'boundingBox': second_bounds},
                            bounds_poly
                        ) or geometry.does_fully_obstruct_target(
                            performer_start['position'],
                            {'boundingBox': bounds},
                            second_bounds.polygon_xz
                        ):
                            # Failed
                            location_random = None
                            break
                    if location_random:
                        # This location should not partly obstruct the target
                        # object's location.
                        if not geometry.does_partly_obstruct_target(
                            self._performer_start['position'],
                            target_location,
                            geometry.get_bounding_polygon(location_random)
                        ):
                            # Successful
                            break
                # Otherwise...
                else:
                    # Successful
                    break
                # Failed
                location_random = None

        if not location_random:
            raise SceneException(
                f'{self.get_name()} cannot randomly position '
                f'target={definition}')

        return location_random

    def _generate_room_dimensions(self) -> Dict[str, Dict[str, float]]:
        """Generate and return the room's randomized dimensions dict."""
        return {
            'x': random.choice(ROOM_SIZE_X),
            'y': random.choice(ROOM_SIZE_Y),
            'z': random.choice(ROOM_SIZE_Z)
        }

    def _identify_front(
        self,
        goal: InteractiveGoal,
        performer_start: Dict[str, float],
        definition: ObjectDefinition,
        target_choice: int = None
    ) -> Dict[str, Any]:
        """Find and return a location in front of the given performer_start."""

        def rotation_func():
            return performer_start['rotation']['y']

        for _ in range(MAX_TRIES):
            location_front = geometry.get_location_in_front_of_performer(
                performer_start,
                definition,
                rotation_func=rotation_func,
                room_dimensions=self._room_dimensions
            )
            # If we've found a valid location...
            if location_front:
                # If this is a target location, ensure it's valid for the goal.
                if target_choice is None or goal.validate_target_location(
                    target_choice,
                    location_front,
                    [],
                    performer_start
                ):
                    break
            # Else, find a new location.
            location_front = None

        return location_front

    def _identify_back(
        self,
        goal: InteractiveGoal,
        performer_start: Dict[str, float],
        definition: ObjectDefinition,
        target_choice: int = None
    ) -> Dict[str, Any]:
        """Find and return a location in back of the given performer_start."""

        def rotation_func():
            return performer_start['rotation']['y']

        for _ in range(MAX_TRIES):
            location_back = geometry.get_location_in_back_of_performer(
                performer_start,
                definition,
                rotation_func,
                room_dimensions=self._room_dimensions
            )
            # If we've found a valid location...
            if location_back:
                # If this is a target location, ensure it's valid for the goal.
                if target_choice is None or goal.validate_target_location(
                    target_choice,
                    location_back,
                    [],
                    performer_start
                ):
                    break
            # Else, find a new location.
            location_back = None

        return location_back

    def _initialize_context_objects(self) -> None:
        """Create this hypercube's small context objects."""

        critical_object_data_list = (
            self._data['target'] + self._data['confusor'] +
            self._data['obstacle'] + self._data['occluder']
        )

        context_count = random.choices(
            SMALL_CONTEXT_OBJECT_CHOICES,
            weights=SMALL_CONTEXT_OBJECT_WEIGHTS,
            k=1
        )[0]

        for _ in range(context_count):
            definition = self._choose_small_context_definition(
                critical_object_data_list
            )

            for _ in range(MAX_TRIES):
                location, bounds_list = self._goal.choose_location(
                    definition,
                    self._performer_start,
                    self._bounds_list,
                    room_dimensions=self._room_dimensions
                )
                successful = True
                if successful:
                    for object_data in critical_object_data_list:
                        for instance in object_data.instance_list:
                            if not instance:
                                continue
                            if geometry.does_fully_obstruct_target(
                                self._performer_start['position'],
                                instance,
                                geometry.get_bounding_polygon(location)
                            ):
                                successful = False
                                break
                        if not successful:
                            break
                if successful:
                    break
                location = False

            if not location:
                raise SceneException(
                    f'{self.get_name()} cannot find suitable location '
                    f'small context object {definition}')

            self._bounds_list = bounds_list
            small_context_instance = instances.instantiate_object(
                definition,
                location
            )
            self._small_context_object_list.append(small_context_instance)

    def _choose_each_object_definition(self) -> None:
        """Choose each object's definition to use across scenes."""

        # Create all targets in the hypercube that the goal must make before
        # the target chosen by the plan, if the goal has multiple targets.
        self._common_target_list, self._bounds_list = self._create_target_list(
            self._goal,
            self._performer_start,
            self._bounds_list,
            [],
            end_index=self._target_data.choice
        )

        self._assign_target_definition(self._target_data, self._goal)

        self._assign_confusor_definition(
            self._confusor_data,
            self._target_data.trained_definition
        )

        for container in self._data['large_container']:
            self._assign_container_definition(
                container,
                self._target_data,
                self._confusor_data
            )

        for container in self._data['small_container']:
            self._assign_container_definition(
                container,
                self._target_data,
                self._confusor_data,
                find_invalid_container=True
            )

        larger_target_definition = self._target_data.larger_definition_of(
            self._data['large_container'],
            self._confusor_data
        )

        for obstacle in self._data['obstacle']:
            self._assign_obstacle_or_occluder_definition(
                obstacle,
                larger_target_definition,
                is_occluder=False
            )

        for occluder in self._data['occluder']:
            self._assign_obstacle_or_occluder_definition(
                occluder,
                larger_target_definition,
                is_occluder=True
            )

    def _create_each_object_template(self) -> None:
        """Create each object's template at a base location, since later we'll
        move them to their final locations in all of the scenes."""

        for object_data_list in self._data.values():
            for object_data in object_data_list:
                object_data.recreate_both_templates()
                # Reset object's half-finished instances in all scenes.
                object_data.reset_all_instances()

    def _initialize_each_hypercube_object(self) -> None:
        """
        Initialize this hypercube's objects:
        - 1. Create objects that may change in each scene (like targets).
        - 2. Containerize objects as needed by this hypercube's plan.
        - 3. Move objects into locations specific to each scene.
        - 4. Save objects specific to each scene.
        - 5. Create all other objects shared by both scenes (like distractors).
        """

        self._choose_each_object_definition()
        tries = 0
        while True:
            tries += 1
            # Reset the bounds_list on each new try.
            self._bounds_list = []
            self._create_each_object_template()
            try:
                self._assign_each_object_location()
                for i, instance in enumerate(self._target_data.instance_list):
                    if not instance:
                        raise SceneException(
                            f'{self.get_name()} did not successfully create a '
                            f'target instance in scene {i} (uh-oh)! '
                            f'target_location_plan='
                            f'{self._target_data.location_plan_list[i]}')
                break
            except SceneException:
                logger.exception(
                    f'{self.get_name()} _assign_each_object_location')
            if tries >= MAX_TRIES:
                raise SceneException(
                    f'{self.get_name()} cannot successfully assign each '
                    f'object to a location -- please redo.')

        for object_data_list in self._data.values():
            for object_data in object_data_list:
                self._log_debug_object_data(object_data)

        # Create other targets in the hypercube that the goal must make after
        # the target chosen by the plan, if the goal has multiple targets.
        common_target_list, self._bounds_list = self._create_target_list(
            self._goal,
            self._performer_start,
            self._bounds_list,
            self._common_target_list + [
                instance for instance in self._target_data.instance_list
                if instance
            ],
            start_index=(len(self._common_target_list) + 1)
        )
        self._common_target_list.extend(common_target_list)

        self._initialize_context_objects()

        # Add the canContainTarget tag to each container in each scene.
        for container_data in self._data['large_container']:
            for instance in container_data.instance_list:
                if instance:
                    instance['canContainTarget'] = True
        for container_data in self._data['small_container']:
            for instance in container_data.instance_list:
                if instance:
                    instance['canContainTarget'] = False

    def _log_debug_object_data(self, object_data: ObjectData) -> None:
        """Log debug info for the given object data."""
        for scene_index, instance in enumerate(object_data.instance_list):
            if instance:
                logger.debug(
                    f'{self.get_name()} '
                    f'{object_data.role}_{scene_index} '
                    f'{instance["type"]} {instance["id"]} '
                    f'parent={instance.get("locationParent", None)}')
            else:
                logger.debug(
                    f'{self.get_name()} '
                    f'{object_data.role}_{scene_index} None')

    def _move_distractor_into_receptacle(
        self,
        object_instance: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[ObjectBounds]
    ) -> Dict[str, Any]:
        """Create and return a receptacle object, moving the given object into
        the new receptacle. Changes the bounds_list."""
        # Only a pickupable object can be positioned inside a receptacle.
        if not object_instance.get('pickupable', False):
            return None

        # Please note that an enclosable receptacle (that can have objects
        # positioned inside of it) may also be called a "container".
        dataset = specific_objects.get_container_openable_definition_dataset()

        for receptacle_definition in dataset.definitions():
            valid_containment = containers.can_contain(
                receptacle_definition,
                object_instance
            )
            if valid_containment:
                location = geometry.calc_obj_pos(
                    performer_start['position'],
                    bounds_list,
                    receptacle_definition,
                    room_dimensions=self._room_dimensions
                )
                if location:
                    receptacle_instance = instances.instantiate_object(
                        receptacle_definition,
                        location
                    )
                    area, angles = valid_containment
                    containers.put_object_in_container(
                        object_instance,
                        receptacle_instance,
                        area,
                        angles[0]
                    )
                    return receptacle_instance
        return None

    def _move_distractor_onto_receptacle(
        self,
        object_instance: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[ObjectBounds]
    ) -> Dict[str, Any]:
        """Create and return a receptacle object, moving the given object onto
        the new receptacle. Changes the bounds_list."""
        # TODO MCS-146 Position objects on top of receptacles.
        return None

    def _update_scene_at_index(
        self,
        scene: Scene,
        scene_index: int,
        goal_template: Dict[str, Any]
    ) -> None:
        """Update the given scene with its metadata like all of its objects."""
        scene_plan = self._plan_list[scene_index]
        scene.room_dimensions = Vector3d(
            x=self._room_dimensions['x'],
            y=self._room_dimensions['y'],
            z=self._room_dimensions['z']
        )
        scene.performer_start = PerformerStart(
            position=Vector3d(
                x=self._performer_start['position']['x'],
                y=self._performer_start['position']['y'],
                z=self._performer_start['position']['z']
            ),
            rotation=Vector3d(
                x=self._performer_start['rotation']['x'],
                y=self._performer_start['rotation']['y'],
                z=self._performer_start['rotation']['z']
            )
        )
        scene.debug['evaluationOnly'] = any([
            object_plan.untrained
            for object_plan_list in scene_plan.object_plans().values()
            for object_plan in object_plan_list
        ])

        scene.goal = copy.deepcopy(goal_template)
        scene.goal = self._goal.update_goal_template(
            scene.goal,
            [self._target_data.instance_list[scene_index]]
        )

        scene.goal['last_step'] = get_step_limit_from_dimensions(
            scene.room_dimensions.x,
            scene.room_dimensions.z
        )

        role_to_object_list = {}
        role_to_object_list[tags.ROLES.TARGET] = [
            object_data.instance_list[scene_index] for object_data in
            self._data['target'] if object_data.instance_list[scene_index]
        ] + self._common_target_list
        role_to_object_list[tags.ROLES.CONFUSOR] = [
            object_data.instance_list[scene_index] for object_data in
            self._data['confusor'] if object_data.instance_list[scene_index]
        ]
        role_to_object_list[tags.ROLES.CONTAINER] = [
            object_data.instance_list[scene_index] for object_data in
            (self._data['large_container'] + self._data['small_container'])
            if object_data.instance_list[scene_index]
        ]
        role_to_object_list[tags.ROLES.CONTEXT] = (
            self._small_context_object_list
        )
        role_to_object_list[tags.ROLES.OBSTACLE] = [
            object_data.instance_list[scene_index] for object_data in
            self._data['obstacle'] if object_data.instance_list[scene_index]
        ]
        role_to_object_list[tags.ROLES.OCCLUDER] = [
            object_data.instance_list[scene_index] for object_data in
            self._data['occluder'] if object_data.instance_list[scene_index]
        ]
        update_scene_objects(scene, role_to_object_list)

        scene.goal['sceneInfo'][tags.SCENE.ID] = [
            scene_plan.scene_id.upper()
        ]
        scene.goal['sceneInfo'][tags.SCENE.SLICES] = []
        for tag, value in scene_plan.slice_tags.items():
            scene.goal['sceneInfo'][tag] = value
            scene.goal['sceneInfo'][tags.SCENE.SLICES].append(
                tags.tag_to_label(tag) + ' ' + str(value)
            )


class InteractiveSingleSceneFactory(HypercubeFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            goal.get_name().replace(' ', '').capitalize(),
            training=True
        )
        self.goal = goal

    def _build(self, starter_scene: Scene) -> Hypercube:
        target_object_plan = ObjectPlan(
            ObjectLocationPlan.RANDOM,
            definition=base_objects.create_soccer_ball()
        )
        return InteractiveHypercube(
            starter_scene,
            self.goal,
            self.role_to_type,
            '',
            [InteractivePlan('', {}, target_object_plan)],
            training=self.training
        )


class InteractiveContainerTrainingHypercubeFactory(HypercubeFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Container' + goal.get_name().replace(' ', '').capitalize() +
            'Training',
            training=True
        )
        self.goal = goal

    def _build(self, starter_scene: Scene) -> Hypercube:
        return InteractiveHypercube(
            starter_scene,
            self.goal,
            self.role_to_type,
            'container',
            create_container_hypercube_plan_list(),
            training=self.training
        )


class InteractiveObstacleTrainingHypercubeFactory(HypercubeFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Obstacle' + goal.get_name().replace(' ', '').capitalize() +
            'Training',
            training=True
        )
        self.goal = goal

    def _build(self, starter_scene: Scene) -> Hypercube:
        return InteractiveHypercube(
            starter_scene,
            self.goal,
            self.role_to_type,
            'obstacle',
            create_obstacle_hypercube_plan_list(),
            training=self.training
        )


class InteractiveOccluderTrainingHypercubeFactory(HypercubeFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Occluder' + goal.get_name().replace(' ', '').capitalize() +
            'Training',
            training=True
        )
        self.goal = goal

    def _build(self, starter_scene: Scene) -> Hypercube:
        return InteractiveHypercube(
            starter_scene,
            self.goal,
            self.role_to_type,
            'occluder',
            create_occluder_hypercube_plan_list(),
            training=self.training
        )


class InteractiveContainerEvaluation4HypercubeFactory(HypercubeFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Container' + goal.get_name().replace(' ', '').capitalize(),
            training=False
        )
        self.goal = goal

    def _build(self, starter_scene: Scene) -> Hypercube:
        return InteractiveHypercube(
            starter_scene,
            self.goal,
            self.role_to_type,
            'container',
            create_eval_4_container_hypercube_plan_list(),
            training=self.training
        )


class InteractiveObstacleEvaluationHypercubeFactory(HypercubeFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Obstacle' + goal.get_name().replace(' ', '').capitalize(),
            training=False
        )
        self.goal = goal

    def _build(self, starter_scene: Scene) -> Hypercube:
        return InteractiveHypercube(
            starter_scene,
            self.goal,
            self.role_to_type,
            'obstacle',
            create_obstacle_hypercube_plan_list(),
            training=self.training
        )


class InteractiveOccluderEvaluationHypercubeFactory(HypercubeFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Occluder' + goal.get_name().replace(' ', '').capitalize(),
            training=False
        )
        self.goal = goal

    def _build(self, starter_scene: Scene) -> Hypercube:
        return InteractiveHypercube(
            starter_scene,
            self.goal,
            self.role_to_type,
            'occluder',
            create_occluder_hypercube_plan_list(),
            training=self.training
        )


INTERACTIVE_TRAINING_HYPERCUBE_LIST = [
    InteractiveSingleSceneFactory(RetrievalGoal('retrieval')),
    InteractiveContainerTrainingHypercubeFactory(RetrievalGoal('container')),
    InteractiveObstacleTrainingHypercubeFactory(RetrievalGoal('obstacle')),
    InteractiveOccluderTrainingHypercubeFactory(RetrievalGoal('occluder'))
]


INTERACTIVE_EVALUATION_HYPERCUBE_LIST = [
    InteractiveObstacleEvaluationHypercubeFactory(RetrievalGoal('obstacle')),
    InteractiveOccluderEvaluationHypercubeFactory(RetrievalGoal('occluder')),
    InteractiveContainerEvaluation4HypercubeFactory(RetrievalGoal('container'))
]
