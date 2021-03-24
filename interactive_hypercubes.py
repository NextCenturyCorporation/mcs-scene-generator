import copy
import logging
import random
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

import containers
import exceptions
import geometry
from interactive_goals import InteractiveGoal, RetrievalGoal
from interactive_plans import InteractivePlan, ObjectLocationPlan, \
    ObjectPlan, create_container_hypercube_plan_list, \
    create_obstacle_hypercube_plan_list, create_occluder_hypercube_plan_list
import objects
from object_data import ObjectData, ReceptacleData, TargetData, \
    identify_larger_definition
import separating_axis_theorem
import hypercubes
import tags
import util


LAST_STEP = 10000
SMALL_CONTEXT_OBJECT_CHOICES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
SMALL_CONTEXT_OBJECT_WEIGHTS = [5, 5, 10, 10, 12.5, 15, 12.5, 10, 10, 5, 5]


WALL_CHOICES = [0, 1, 2, 3]
WALL_WEIGHTS = [40, 30, 20, 10]
WALL_MAX_WIDTH = 4
WALL_MIN_WIDTH = 1
WALL_Y = 1.5
WALL_HEIGHT = 3
WALL_DEPTH = 0.1
WALL_SEPARATION = 1


def retrieve_definition_lists(
    original_definition_list: List[Dict[str, Any]],
    object_type: str
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Return the trained and untrained shape definition lists."""
    complete_definition_list = util.retrieve_complete_definition_list(
        original_definition_list
    )
    trained_definition_list = util.retrieve_trained_definition_list(
        complete_definition_list
    )
    untrained_definition_list = util.retrieve_untrained_definition_list(
        complete_definition_list,
        tags.SCENE.UNTRAINED_SHAPE
    )
    return trained_definition_list, untrained_definition_list


def retrieve_template_list(object_data: ObjectData) -> List[Dict[str, Any]]:
    return [object_data.trained_template, object_data.untrained_template]


class InteractiveHypercube(hypercubes.Hypercube):
    """A hypercube of interactive scenes that each have the same goals,
    targets, distractors, walls, materials, and performer starts, except for
    specific differences detailed in its plan."""

    def __init__(
        self,
        body_template: Dict[str, Any],
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
            body_template,
            goal.get_goal_template(),
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
            raise exceptions.SceneException(
                'Interactive hypercubes cannot currently handle a target with '
                'different definitions across scenes')

        if any(self._target_data.untrained_plan_list):
            raise exceptions.SceneException(
                'Interactive hypercubes cannot currently handle a target with '
                'a randomly chosen (not pre-defined) untrained shape')

        # Update _assign_each_object_location to handle new location plans.
        for object_data in self._data['target']:
            if (
                object_data.is_between() or object_data.is_far()
            ):
                raise exceptions.SceneException(
                    'Interactive hypercubes cannot currently handle the '
                    'target location plans: BETWEEN, FAR')

        for object_data in self._data['confusor']:
            if (
                object_data.is_between() or object_data.is_random()
            ):
                raise exceptions.SceneException(
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
                raise exceptions.SceneException(
                    'Interactive hypercubes cannot currently handle the '
                    'container location plans: BACK, BETWEEN, CLOSE, FAR, '
                    'FRONT, INSIDE')

        for object_data in (self._data['obstacle'] + self._data['occluder']):
            if (
                object_data.is_back() or object_data.is_far() or
                object_data.is_front() or object_data.is_inside()
            ):
                raise exceptions.SceneException(
                    'Interactive hypercubes cannot currently handle the '
                    'obstacle or occluder location plans: BACK, FAR, FRONT, '
                    'INSIDE')

    # Override
    def _create_scenes(
        self,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        tries = 0
        while True:
            tries += 1
            try:
                logging.debug(
                    f'\n\n{self.get_name()} initialize scenes try {tries}\n')

                # Reset the half-finished scenes, all of their objects, and
                # their other properties on each try.
                scenes = [
                    copy.deepcopy(body_template) for _
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
                # Save the interior walls used in the hypercube.
                self._interior_wall_list = []
                # Save the performer's start location in the hypercube.
                self._performer_start = self._generate_performer_start()
                # Save the small context objects used in the hypercube.
                self._small_context_object_list = []

                # Initialize all of the objects in all of the scenes.
                self._initialize_each_hypercube_object()

                # Update each scene's template with its corresponding objects,
                # goal, tags, and other specific properties.
                for index, scene in enumerate(scenes):
                    self._update_scene_at_index(scene, index, goal_template)

                logging.debug(
                    f'\n\n{self.get_name()} initialize scenes is done\n ')

                scenes = hypercubes.update_floor_and_walls(
                    body_template,
                    self._data,
                    retrieve_template_list,
                    scenes
                )

                break

            except exceptions.SceneException:
                logging.exception(
                    f'{self.get_name()} _initialize_each_hypercube_object')

            if tries >= util.MAX_TRIES:
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot successfully initialize scenes '
                    f'-- please redo.')

        return scenes

    # Override
    def _get_training_scenes(self) -> List[Dict[str, Any]]:
        return [scene for scene in self._scenes if not scene['evaluationOnly']]

    def _assign_confusor_obstacle_occluder_location(
        self,
        target_data: TargetData,
        target_or_receptacle_definition: Dict[str, Any],
        confusor_data: Optional[ObjectData],
        obstacle_occluder_data_list: List[ObjectData],
        large_container_data_list: List[ReceptacleData],
        goal: InteractiveGoal,
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]],
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
                    logging.debug(
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
                    logging.debug(
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
                    logging.debug(
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
        bounds_list: List[List[Dict[str, float]]]
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
                logging.debug(
                    f'{self.get_name()} container location randomly chosen: '
                    f'{location}')
                bounds = container_data.assign_location_random(location)
                bounds_list.extend(bounds)

    def _assign_front_and_back_location(
        self,
        target_data: TargetData,
        target_or_receptacle_definition: Dict[str, Any],
        confusor_data_list: List[ObjectData],
        bounds_list: List[List[Dict[str, float]]]
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
            logging.debug(
                f'{self.get_name()} location in front of performer start:'
                f'{location_front}')
            logging.debug(
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
        logging.debug(
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
        target_or_receptacle_definition: Dict[str, Any],
        target_location: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]],
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
        logging.debug(
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
        logging.debug(
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
        target_or_receptacle_definition: Dict[str, Any],
        container_data: Optional[ReceptacleData],
        confusor_data_list: List[ObjectData],
        goal: InteractiveGoal,
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]]
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
            logging.debug(
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
            if target_definition.get('notSideways', None):
                target_definition = copy.deepcopy(target_definition)
                target_definition['dimensions'] = (
                    target_definition['notSideways']['dimensions']
                )
                target_definition['offset'] = (
                    target_definition['notSideways'].get('offset', {})
                )
                target_definition['positionY'] = (
                    target_definition['notSideways'].get('positionY', 0)
                )
                target_definition['rotation'] = (
                    target_definition['notSideways'].get('rotation', {})
                )
            location = self._generate_close_to(
                target_definition,
                container_data.larger_definition(),
                target_container_location,
                performer_start,
                bounds_list
            )
            logging.debug(
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
            logging.debug(
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

        logging.debug(
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
        target_definition: Dict[str, Any]
    ) -> None:
        """Update the given confusor data with its object definition using the
        given target data."""

        if not confusor_data:
            return

        trained_list, untrained_list = retrieve_definition_lists(objects.get(
            objects.ObjectDefinitionList.ALL
        ), None)

        if not confusor_data.trained_definition:
            confusor_data.trained_definition = util.get_similar_definition(
                target_definition,
                trained_list
            )
            if not confusor_data.trained_definition:
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot find trained confusor '
                    f'definition_list_length={len(trained_list)} '
                    f'target={target_definition}')

        if not confusor_data.untrained_definition:
            confusor_data.untrained_definition = util.get_similar_definition(
                target_definition,
                untrained_list
            )
            if not confusor_data.untrained_definition:
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot find untrained confusor '
                    f'definition_list_length={len(untrained_list)} '
                    f'target={target_definition}')

        logging.debug(
            f'{self.get_name()} confusor definition: '
            f'trained={confusor_data.trained_definition}'
            f'untrained={confusor_data.untrained_definition}')

    def _choose_small_context_definition(
        self,
        target_confusor_data_list: List[ObjectData]
    ) -> Dict[str, Any]:
        """Choose and return a small context object definition for the given
        target and confusor objects from the given definition list."""
        return util.choose_distractor_definition([
            object_data.trained_definition for object_data
            in target_confusor_data_list
        ] + [
            object_data.untrained_definition for object_data
            in target_confusor_data_list if object_data.untrained_definition
        ])

    def _assign_obstacle_or_occluder_definition(
        self,
        object_data: ObjectData,
        target_definition: Dict[str, Any],
        is_occluder: bool
    ) -> None:
        """Update the given obstacle or occluder data with its object
        definition using the given target data."""

        role = tags.ROLES.OCCLUDER if is_occluder else tags.ROLES.OBSTACLE
        trained_list, untrained_list = retrieve_definition_lists(objects.get(
            objects.ObjectDefinitionList.OCCLUDERS if is_occluder else
            objects.ObjectDefinitionList.OBSTACLES
        ), self._role_to_type[role])

        if not object_data.trained_definition:
            object_data.trained_definition = (
                self._choose_obstacle_or_occluder_definition(
                    target_definition,
                    trained_list,
                    is_occluder
                )
            )

        if not object_data.untrained_definition:
            object_data.untrained_definition = (
                self._choose_obstacle_or_occluder_definition(
                    target_definition,
                    untrained_list,
                    is_occluder
                )
            )

        logging.debug(
            f'{self.get_name()} {"occluder" if is_occluder else "obstacle"} '
            f'definition: trained={object_data.trained_definition} '
            f'untrained={object_data.untrained_definition}')

    def _choose_obstacle_or_occluder_definition(
        self,
        target_definition: Dict[str, Any],
        nested_definition_list: List[List[Dict[str, Any]]],
        is_occluder: bool
    ) -> Dict[str, Any]:
        """Choose and return an obstacle or occluder definition for the given
        target object from the given definition list."""

        obstacle_occluder_definition_list = (
            geometry.retrieve_obstacle_occluder_definition_list(
                target_definition,
                nested_definition_list,
                is_occluder
            )
        )
        if not obstacle_occluder_definition_list:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot find '
                f'{"occluder" if is_occluder else "obstacle"} '
                f'definition_list_length={len(nested_definition_list)} '
                f'target={target_definition}')
        definition, angle = random.choice(random.choice(
            obstacle_occluder_definition_list
        ))
        if 'rotation' not in definition:
            definition['rotation'] = {
                'x': 0,
                'y': 0,
                'z': 0
            }
        # Note that this rotation must be also modified with the final
        # performer start Y.
        definition['rotation']['y'] += angle
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

        trained_list, untrained_list = retrieve_definition_lists(objects.get(
            objects.ObjectDefinitionList.CONTAINERS
        ), self._role_to_type[tags.ROLES.CONTAINER])

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
                trained_list,
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
                untrained_list,
                find_invalid_container
            )

            container_data.untrained_definition = definition
            container_data.untrained_containment.area_index = area_index
            container_data.untrained_containment.orientation = orientation
            container_data.untrained_containment.target_angle = target_angle
            container_data.untrained_containment.confusor_angle = (
                confusor_angle
            )

        logging.debug(
            f'{self.get_name()} container definition: '
            f'trained={container_data.trained_definition} '
            f'untrained={container_data.untrained_definition}')

    def _choose_container_definition(
        self,
        target_data: TargetData,
        confusor_data: Optional[ObjectData],
        confusor_definition: Optional[Dict[str, Any]],
        nested_definition_list: List[List[Dict[str, Any]]],
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
        if target_data.trained_definition.get('sideways'):
            sideways = copy.deepcopy(target_data.trained_definition)
            # Save the original properties.
            sideways['notSideways'] = {
                'dimensions': sideways['dimensions'],
                'offset': sideways.get('offset', {}),
                'positionY': sideways.get('positionY', 0),
                'rotation': sideways.get('rotation', {})
            }
            # Override the original properties with the sideways properties.
            sideways['dimensions'] = sideways['sideways']['dimensions']
            sideways['offset'] = sideways['sideways'].get('offset', {})
            sideways['positionY'] = sideways['sideways'].get('positionY', 0)
            sideways['rotation'] = sideways['sideways'].get('rotation', {})
            sideways['sideways'] = None
            target_definition_list.append(sideways)

        # If needed, find an enclosable container that can hold both the
        # target and the confusor together.
        if target_data.containerize_with(confusor_data):
            for definition_list in nested_definition_list:
                for definition in definition_list:
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

        # Else, find an enclosable container that can hold either the target
        # or confusor individually.
        else:
            confusor_definition_or_none = (
                confusor_definition if confusor_data and
                confusor_data.is_inside() else None
            )

            if not target_data.is_inside():
                target_definition_list = [None]

            for definition_list in nested_definition_list:
                for definition in definition_list:
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

        if not container_definition:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot create '
                f'{"small" if find_invalid_container else "large"} '
                f'container '
                f'definition_list_length={len(nested_definition_list)} '
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

        logging.debug(
            f'{self.get_name()} target definition: '
            f'{target_data.trained_definition}')

    def _create_interior_wall(
        self,
        wall_material: str,
        wall_colors: List[str],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]],
        keep_unobstructed_list: List[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create and return a randomly positioned interior wall with the
        given material and colors. If keep_unobstructed_list is not None, the
        wall won't obstruct the line between the performer_start and the
        objects in keep_unobstructed_list."""

        tries = 0
        performer_rect = geometry.find_performer_rect(
            performer_start['position']
        )
        performer_poly = geometry.rect_to_poly(performer_rect)

        while tries < util.MAX_TRIES:
            rotation = random.choice((0, 90, 180, 270))
            x_position = geometry.random_position_x()
            z_position = geometry.random_position_z()
            x_width = round(
                random.uniform(WALL_MIN_WIDTH, WALL_MAX_WIDTH),
                geometry.POSITION_DIGITS
            )

            # Ensure the wall is not too close to the room's parallel walls.
            if (
                (rotation == 0 or rotation == 180) and
                (
                    z_position < (geometry.ROOM_Z_MIN + WALL_SEPARATION) or
                    z_position > (geometry.ROOM_Z_MAX - WALL_SEPARATION)
                )
            ) or (
                (rotation == 90 or rotation == 270) and
                (
                    x_position < (geometry.ROOM_X_MIN + WALL_SEPARATION) or
                    x_position > (geometry.ROOM_X_MAX - WALL_SEPARATION)
                )
            ):
                continue

            wall_rect = geometry.calc_obj_coords(
                x_position,
                z_position,
                x_width,
                WALL_DEPTH,
                0,
                0,
                rotation
            )
            wall_poly = geometry.rect_to_poly(wall_rect)

            # Ensure parallel walls are not too close one another.
            boundary_rect = geometry.calc_obj_coords(
                x_position,
                z_position,
                x_width + WALL_SEPARATION,
                WALL_DEPTH + WALL_SEPARATION,
                0,
                0,
                rotation
            )

            is_too_close = any(
                separating_axis_theorem.sat_entry(boundary_rect, bounds)
                for bounds in bounds_list
            )

            is_ok = (
                not wall_poly.intersects(performer_poly) and
                geometry.rect_within_room(wall_rect) and
                not is_too_close
            )

            if is_ok and keep_unobstructed_list:
                for instance in keep_unobstructed_list:
                    if (
                        'locationParent' not in instance and
                        geometry.does_fully_obstruct_target(
                            performer_start['position'],
                            instance,
                            wall_poly
                        )
                    ):
                        is_ok = False
                        break

            if is_ok:
                break

            tries += 1

        if tries < util.MAX_TRIES:
            interior_wall = {
                'id': 'wall_' + str(uuid.uuid4()),
                'materials': [wall_material],
                'type': 'cube',
                'kinematic': 'true',
                'structure': 'true',
                'mass': 200,
                'info': wall_colors
            }
            interior_wall['shows'] = [{
                'stepBegin': 0,
                'scale': {'x': x_width, 'y': WALL_HEIGHT, 'z': WALL_DEPTH},
                'rotation': {'x': 0, 'y': rotation, 'z': 0},
                'position': {'x': x_position, 'y': WALL_Y, 'z': z_position},
                'boundingBox': wall_rect
            }]
            return interior_wall

        return None

    def _create_target_list(
        self,
        goal: InteractiveGoal,
        performer_start: Dict[str, float],
        existing_bounds_list: List[List[Dict[str, float]]],
        target_validation_list: List[Dict[str, float]],
        start_index: int = None,
        end_index: int = None
    ) -> Tuple[List[Dict[str, Any]], List[List[Dict[str, float]]]]:
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
            for _ in range(util.MAX_TRIES):
                location, possible_bounds_list = goal.choose_location(
                    definition,
                    performer_start,
                    existing_bounds_list,
                    is_target=True
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
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot find suitable location '
                    f'target={definition}')
            bounds_list = possible_bounds_list
            instance = util.instantiate_object(definition, location)
            target_list.append(instance)

        return target_list, bounds_list

    def _generate_front_and_back(
        self,
        definition: Dict[str, Any],
        target_choice: int = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate a location in front of and (if needed) in back of the
        performer's start location. May change the global performer_start if
        it's needed to generate the two locations. Return the front and back
        locations."""

        location_front = None
        location_back = None

        for _ in range(util.MAX_TRIES):
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
            self._performer_start = self._generate_performer_start()

        if not location_front or not location_back:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot position performer start in '
                f'front of and in back of object={definition}')

        return location_front, location_back

    def _generate_close_to(
        self,
        object_definition: Dict[str, Any],
        existing_definition: Dict[str, Any],
        existing_location: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]],
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
            unreachable=unreachable
        )

        if not location_close:
            if adjacent:
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot position object adjacent to '
                    f'existing:\nperformer_start={performer_start}\n'
                    f'object={object_definition}\n'
                    f'existing={existing_definition}\n'
                    f'location={existing_location}\nbounds={bounds_list}')
            elif behind:
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot position object directly in '
                    f'back of existing:\nperformer_start={performer_start}\n'
                    f'object={object_definition}\n'
                    f'existing={existing_definition}\n'
                    f'location={existing_location}\nbounds={bounds_list}')
            raise exceptions.SceneException(
                f'{self.get_name()} cannot position object directly in '
                f'front of existing:\nperformer_start={performer_start}\n'
                f'object={object_definition}\n'
                f'existing={existing_definition}\n'
                f'location={existing_location}\nbounds={bounds_list}')

        return location_close

    def _generate_far_from(
        self,
        object_definition: Dict[str, Any],
        existing_location: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]]
    ) -> Dict[str, Any]:
        """Generate and return a new location for the given object far away
        from the given location."""

        for _ in range(util.MAX_TRIES):
            bounds_list_copy = copy.deepcopy(bounds_list)
            location_far = geometry.calc_obj_pos(
                performer_start['position'],
                bounds_list_copy,
                object_definition
            )
            if not geometry.are_adjacent(
                existing_location,
                location_far,
                distance=geometry.MIN_OBJECTS_SEPARATION_DISTANCE
            ):
                break
            location_far = None

        if not location_far:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot position object far from existing: '
                f'object={object_definition}\nexisting={existing_location}')

        return location_far

    def _generate_performer_start(self) -> Dict[str, Dict[str, float]]:
        """Generate and return the performer's start location dict."""
        return {
            'position': {
                'x': round(random.uniform(
                    geometry.ROOM_X_MIN + util.PERFORMER_HALF_WIDTH,
                    geometry.ROOM_X_MAX - util.PERFORMER_HALF_WIDTH
                ), geometry.POSITION_DIGITS),
                'y': 0,
                'z': round(random.uniform(
                    geometry.ROOM_Z_MIN + util.PERFORMER_HALF_WIDTH,
                    geometry.ROOM_Z_MAX - util.PERFORMER_HALF_WIDTH
                ), geometry.POSITION_DIGITS)
            },
            'rotation': {
                'x': 0,
                'y': geometry.random_rotation(),
                'z': 0
            }
        }

    def _generate_random_location(
        self,
        definition: Dict[str, Any],
        goal: InteractiveGoal,
        performer_start: Dict[str, float],
        bounds_list: List[List[Dict[str, float]]],
        target_choice: int = None,
        target_location: Dict[str, Any] = None,
        second_definition: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate a random location and return it twice."""

        for _ in range(util.MAX_TRIES):
            location_random, _ = goal.choose_location(
                identify_larger_definition(definition, second_definition)
                if second_definition else definition,
                performer_start,
                bounds_list,
                is_target=(target_choice is not None)
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
                        bounds_poly = geometry.get_bounding_polygon({
                            'boundingBox': bounds
                        })
                        # Also validate the second object definition, if given.
                        second_rect = geometry.generate_object_bounds(
                            second_definition['dimensions'],
                            second_definition.get('offset', None),
                            location_random['position'],
                            location_random['rotation']
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
                            {'boundingBox': second_rect},
                            bounds_poly
                        ) or geometry.does_fully_obstruct_target(
                            performer_start['position'],
                            {'boundingBox': bounds},
                            geometry.get_bounding_polygon({
                                'boundingBox': second_rect
                            })
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
            raise exceptions.SceneException(
                f'{self.get_name()} cannot randomly position '
                f'target={definition}')

        return location_random

    def _identify_front(
        self,
        goal: InteractiveGoal,
        performer_start: Dict[str, float],
        definition: Dict[str, Any],
        target_choice: int = None
    ) -> Dict[str, Any]:
        """Find and return a location in front of the given performer_start."""

        def rotation_func():
            return performer_start['rotation']['y']

        for _ in range(util.MAX_TRIES):
            location_front = geometry.get_location_in_front_of_performer(
                performer_start,
                definition,
                rotation_func=rotation_func
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
        definition: Dict[str, Any],
        target_choice: int = None
    ) -> Dict[str, Any]:
        """Find and return a location in back of the given performer_start."""

        def rotation_func():
            return performer_start['rotation']['y']

        for _ in range(util.MAX_TRIES):
            location_back = geometry.get_location_in_back_of_performer(
                performer_start,
                definition,
                rotation_func
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

            for _ in range(util.MAX_TRIES):
                location, bounds_list = self._goal.choose_location(
                    definition,
                    self._performer_start,
                    self._bounds_list
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
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot find suitable location '
                    f'small context object {definition}')

            self._bounds_list = bounds_list
            instance = util.instantiate_object(definition, location)
            self._small_context_object_list.append(instance)

    def _initialize_interior_walls(self) -> None:
        """Create this hypercube's interior walls. Changes the
        interior_wall_list and the bounds_list."""

        # All scenes will have the same room wall material/colors.
        room_wall_material_name = self._scene_1['wallMaterial']
        room_wall_colors = self._scene_1['wallColors']

        keep_unobstructed_list = [self._target_data.trained_definition]
        if self._confusor_data:
            keep_unobstructed_list.extend([
                self._confusor_data.trained_definition,
                self._confusor_data.untrained_definition
            ])

        number = random.choices(WALL_CHOICES, weights=WALL_WEIGHTS, k=1)[0]
        logging.debug(f'{self.get_name()} {number} interior walls')

        for _ in range(number + 1):
            wall = self._create_interior_wall(
                room_wall_material_name,
                room_wall_colors,
                self._performer_start,
                self._bounds_list,
                keep_unobstructed_list
            )
            if wall:
                self._interior_wall_list.append(wall)
                self._bounds_list.append(wall['shows'][0]['boundingBox'])

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
                        raise exceptions.SceneException(
                            f'{self.get_name()} did not successfully create a '
                            f'target instance in scene {i} (uh-oh)! '
                            f'target_location_plan='
                            f'{self._target_data.location_plan_list[i]}')
                break
            except exceptions.SceneException:
                logging.exception(
                    f'{self.get_name()} _assign_each_object_location')
            if tries >= util.MAX_TRIES:
                raise exceptions.SceneException(
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
                logging.info(
                    f'{self.get_name()} '
                    f'{object_data.role}_{scene_index} '
                    f'{instance["type"]} {instance["id"]} '
                    f'parent={instance.get("locationParent", None)}')
            else:
                logging.info(
                    f'{self.get_name()} '
                    f'{object_data.role}_{scene_index} None')

    def _move_distractor_into_receptacle(
        self,
        object_instance: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]]
    ) -> Dict[str, Any]:
        """Create and return a receptacle object, moving the given object into
        the new receptacle. Changes the bounds_list."""
        # Only a pickupable object can be positioned inside a receptacle.
        if not object_instance.get('pickupable', False):
            return None

        # Please note that an enclosable receptacle (that can have objects
        # positioned inside of it) may also be called a "container".
        definition_list = util.retrieve_complete_definition_list(
            objects.ObjectDefinitionList.CONTAINERS
        )
        definition_list = [
            item for nested_list in definition_list for item in nested_list
        ]

        for definition in definition_list:
            receptacle_definition = util.finalize_object_definition(definition)
            valid_containment = containers.can_contain(
                receptacle_definition,
                object_instance
            )
            if valid_containment:
                location = geometry.calc_obj_pos(
                    performer_start['position'],
                    bounds_list,
                    receptacle_definition
                )
                if location:
                    receptacle_instance = util.instantiate_object(
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
        bounds_list: List[List[Dict[str, float]]]
    ) -> Dict[str, Any]:
        """Create and return a receptacle object, moving the given object onto
        the new receptacle. Changes the bounds_list."""
        # TODO MCS-146 Position objects on top of receptacles.
        return None

    def _update_scene_at_index(
        self,
        scene: Dict[str, Any],
        scene_index: int,
        goal_template: Dict[str, Any]
    ) -> None:
        """Update the given scene with its metadata like all of its objects."""
        scene_plan = self._plan_list[scene_index]
        scene['performerStart'] = self._performer_start
        scene['evaluationOnly'] = any([
            object_plan.untrained
            for object_plan_list in scene_plan.object_plans().values()
            for object_plan in object_plan_list
        ])

        scene['goal'] = copy.deepcopy(goal_template)
        scene['goal'] = self._goal.update_goal_template(
            scene['goal'],
            [self._target_data.instance_list[scene_index]]
        )
        scene['goal']['last_step'] = LAST_STEP

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
        role_to_object_list[tags.ROLES.WALL] = self._interior_wall_list
        hypercubes.update_scene_objects(scene, role_to_object_list)

        scene['goal']['sceneInfo'][tags.SCENE.ID] = [
            scene_plan.scene_id.upper()
        ]
        scene['goal']['sceneInfo'][tags.SCENE.SLICES] = []
        for tag, value in scene_plan.slice_tags.items():
            scene['goal']['sceneInfo'][tag] = value
            scene['goal']['sceneInfo'][tags.SCENE.SLICES].append(
                tags.tag_to_label(tag) + ' ' + str(value)
            )


class InteractiveSingleSceneFactory(hypercubes.HypercubeFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(goal.get_name().capitalize(), training=True)
        self.goal = goal

    def _build(
        self,
        body_template: Dict[str, Any],
        role_to_type: Dict[str, str]
    ) -> hypercubes.Hypercube:
        target_object_plan = ObjectPlan(
            ObjectLocationPlan.RANDOM,
            definition=objects.get_trophy()
        )
        return InteractiveHypercube(
            body_template,
            self.goal,
            role_to_type,
            '',
            [InteractivePlan('', {}, target_object_plan)],
            training=self.training
        )


class InteractiveContainerTrainingHypercubeFactory(
    hypercubes.HypercubeFactory
):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Container' + goal.get_name().capitalize() + 'Training',
            training=True
        )
        self.goal = goal

    def _build(
        self,
        body_template: Dict[str, Any],
        role_to_type: Dict[str, str]
    ) -> hypercubes.Hypercube:
        return InteractiveHypercube(
            body_template,
            self.goal,
            role_to_type,
            'container',
            create_container_hypercube_plan_list(),
            training=self.training
        )


class InteractiveObstacleTrainingHypercubeFactory(hypercubes.HypercubeFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Obstacle' + goal.get_name().capitalize() + 'Training',
            training=True
        )
        self.goal = goal

    def _build(
        self,
        body_template: Dict[str, Any],
        role_to_type: Dict[str, str]
    ) -> hypercubes.Hypercube:
        return InteractiveHypercube(
            body_template,
            self.goal,
            role_to_type,
            'obstacle',
            create_obstacle_hypercube_plan_list(),
            training=self.training
        )


class InteractiveOccluderTrainingHypercubeFactory(hypercubes.HypercubeFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Occluder' + goal.get_name().capitalize() + 'Training',
            training=True
        )
        self.goal = goal

    def _build(
        self,
        body_template: Dict[str, Any],
        role_to_type: Dict[str, str]
    ) -> hypercubes.Hypercube:
        return InteractiveHypercube(
            body_template,
            self.goal,
            role_to_type,
            'occluder',
            create_occluder_hypercube_plan_list(),
            training=self.training
        )


class InteractiveContainerEvaluationHypercubeFactory(
    hypercubes.HypercubeFactory
):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Container' + goal.get_name().capitalize() + 'Evaluation',
            training=False
        )
        self.goal = goal

    def _build(
        self,
        body_template: Dict[str, Any],
        role_to_type: Dict[str, str]
    ) -> hypercubes.Hypercube:
        return InteractiveHypercube(
            body_template,
            self.goal,
            role_to_type,
            'container',
            create_container_hypercube_plan_list(),
            training=self.training
        )


class InteractiveObstacleEvaluationHypercubeFactory(
    hypercubes.HypercubeFactory
):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Obstacle' + goal.get_name().capitalize() + 'Evaluation',
            training=False
        )
        self.goal = goal

    def _build(
        self,
        body_template: Dict[str, Any],
        role_to_type: Dict[str, str]
    ) -> hypercubes.Hypercube:
        return InteractiveHypercube(
            body_template,
            self.goal,
            role_to_type,
            'obstacle',
            create_obstacle_hypercube_plan_list(),
            training=self.training
        )


class InteractiveOccluderEvaluationHypercubeFactory(
    hypercubes.HypercubeFactory
):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(
            'Occluder' + goal.get_name().capitalize() + 'Evaluation',
            training=False
        )
        self.goal = goal

    def _build(
        self,
        body_template: Dict[str, Any],
        role_to_type: Dict[str, str]
    ) -> hypercubes.Hypercube:
        return InteractiveHypercube(
            body_template,
            self.goal,
            role_to_type,
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
    InteractiveContainerEvaluationHypercubeFactory(RetrievalGoal('container')),
    InteractiveObstacleEvaluationHypercubeFactory(RetrievalGoal('obstacle')),
    InteractiveOccluderEvaluationHypercubeFactory(RetrievalGoal('occluder'))
]
