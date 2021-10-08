import copy
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

from generator import ObjectDefinition, geometry, util

from .interactive_plans import ObjectLocationPlan, ObjectPlan


def identify_larger_definition(
    one: ObjectDefinition,
    two: ObjectDefinition
) -> Dict[str, Any]:
    """Return the larger (in dimensions) of the two given definitions."""
    if not one:
        return two
    if not two:
        return one
    # TODO Handle if one has a larger X but other has a larger Z
    return one if (
        one.dimensions.x > two.dimensions.x or
        one.dimensions.z > two.dimensions.z
    ) else two


class ObjectData():
    """Setup options and instances of a single object across all scenes in an
    interactive hypercube."""

    def __init__(self, role: str, object_plan: ObjectPlan) -> None:
        self.role = role
        # Each plan corresponds to the setup in a specific scene.
        self.location_plan_list = [object_plan.location]
        self.untrained_plan_list = [object_plan.untrained]
        # Save a specific definition from the object plan, if one is given. For
        # example, if the target object is always a trophy. Usually None.
        self.original_definition = object_plan.definition
        self.trained_definition = object_plan.definition
        self.untrained_definition = object_plan.definition
        # Each template is an instance of the object but not tied to a specific
        # scene and without its final location.
        self.trained_template = None
        self.untrained_template = None
        # Each instance is tied to a specific scene with a specific location.
        self.instance_list = [None]

    def _assign_location(
        self,
        location: Dict[str, Any],
        object_location: ObjectLocationPlan,
        indexes: List[int] = None
    ) -> List[List[Dict[str, float]]]:
        # Create a copy of the trained shape template at the given location.
        trained_instance = copy.deepcopy(self.trained_template)
        util.move_to_location(
            trained_instance,
            location,
            geometry.generate_object_bounds(
                vars(self.trained_definition.dimensions),
                vars(self.trained_definition.offset),
                location['position'],
                location['rotation']
            ),
            self.trained_definition
        )

        # Create a copy of the untrained shape template at the given location.
        if self.untrained_template:
            untrained_instance = copy.deepcopy(self.untrained_template)
            util.move_to_location(
                untrained_instance,
                location,
                geometry.generate_object_bounds(
                    vars(self.untrained_definition.dimensions),
                    vars(self.untrained_definition.offset),
                    location['position'],
                    location['rotation']
                ),
                self.untrained_definition
            )

        is_trained_needed = False
        is_untrained_needed = False

        # Assign a copy of the trained/untrained instance to each scene in
        # which this object's location plan equals the given location plan
        # (and the scene's index is in the given index list, if any).
        for index, location_plan in enumerate(self.location_plan_list):
            if location_plan == object_location:
                if (not indexes) or (index in indexes):
                    if self.untrained_plan_list[index]:
                        instance = untrained_instance
                        is_untrained_needed = True
                    else:
                        instance = trained_instance
                        is_trained_needed = True
                    self.instance_list[index] = copy.deepcopy(instance)

        # Return all needed object/location bounds.
        return [] + (
            [trained_instance['shows'][0]['boundingBox']]
            if is_trained_needed else []
        ) + (
            [untrained_instance['shows'][0]['boundingBox']]
            if is_untrained_needed else []
        )

    def _uses_location_plan(self, object_location: ObjectLocationPlan) -> bool:
        return any([
            location_plan == object_location
            for location_plan in self.location_plan_list
        ])

    def append_object_plan(self, object_plan: ObjectPlan) -> None:
        """Appends the given object plan to this data."""
        if not object_plan:
            return
        self.location_plan_list.append(object_plan.location)
        self.untrained_plan_list.append(object_plan.untrained)
        self.instance_list.append(None)

    def assign_location_back(
        self,
        location: Dict[str, Any]
    ) -> List[List[Dict[str, float]]]:
        """Assign the given location (by creating a new instance of the object)
        to each scene in which this object's location plan is BACK."""
        return self._assign_location(location, ObjectLocationPlan.BACK)

    def assign_location_between(
        self,
        location: Dict[str, Any],
        indexes: List[int]
    ) -> List[List[Dict[str, float]]]:
        """Assign the given location (by creating a new instance of the object)
        to each scene with one of the given indexes in which this object's
        location plan is BETWEEN."""
        return self._assign_location(
            location,
            ObjectLocationPlan.BETWEEN,
            indexes
        )

    def assign_location_close(
        self,
        location: Dict[str, Any],
        indexes: List[int]
    ) -> List[List[Dict[str, float]]]:
        """Assign the given location (by creating a new instance of the object)
        to each scene with one of the given indexes in which this object's
        location plan is CLOSE."""
        return self._assign_location(
            location,
            ObjectLocationPlan.CLOSE,
            indexes
        )

    def assign_location_far(
        self,
        location: Dict[str, Any],
        indexes: List[int]
    ) -> List[List[Dict[str, float]]]:
        """Assign the given location (by creating a new instance of the object)
        to each scene with one of the given indexes in which this object's
        location plan is FAR."""
        return self._assign_location(
            location,
            ObjectLocationPlan.FAR,
            indexes
        )

    def assign_location_front(
        self,
        location: Dict[str, Any]
    ) -> List[List[Dict[str, float]]]:
        """Assign the given location (by creating a new instance of the object)
        to each scene in which this object's location plan is FRONT."""
        return self._assign_location(location, ObjectLocationPlan.FRONT)

    def assign_location_random(
        self,
        location: Dict[str, Any]
    ) -> List[List[Dict[str, float]]]:
        """Assign the given location (by creating a new instance of the object)
        to each scene in which this object's location plan is RANDOM."""
        return self._assign_location(location, ObjectLocationPlan.RANDOM)

    def contained_indexes(
        self,
        container_data_list: List[Any],
        second_object_data: Optional[Any] = None
    ) -> List[Tuple[int, Any, Optional[Any]]]:
        """Return the scene indexes in which this object is contained, as well
        as its corresponding container from the given list, plus the given
        second object if it's contained together with this object."""
        contained_indexes = []
        for index, location_plan in enumerate(self.location_plan_list):
            if location_plan == ObjectLocationPlan.INSIDE_0:
                second_object_data_or_none = (
                    second_object_data if location_plan ==
                    second_object_data.location_plan_list[index] else None
                ) if second_object_data else None
                contained_indexes.append(
                    (index, container_data_list[0], second_object_data_or_none)
                )
        return contained_indexes

    def containerize_with(
        self,
        object_data: Optional[Any],
    ) -> List[int]:
        """Return if both this object and the given object must ever be
        positioned together inside the same container in the same scene."""
        if not object_data:
            return False
        return any([(
            location_plan == ObjectLocationPlan.INSIDE_0 and
            location_plan == object_data.location_plan_list[index]
        ) for index, location_plan in enumerate(self.location_plan_list)])

    def is_back(self) -> bool:
        """Return whether this object ever uses location plan BACK."""
        return self._uses_location_plan(ObjectLocationPlan.BACK)

    def is_between(self) -> bool:
        """Return whether this object ever uses location plan BETWEEN."""
        return self._uses_location_plan(ObjectLocationPlan.BETWEEN)

    def is_close(self) -> bool:
        """Return whether this object ever uses location plan CLOSE."""
        return self._uses_location_plan(ObjectLocationPlan.CLOSE)

    def is_far(self) -> bool:
        """Return whether this object ever uses location plan FAR."""
        return self._uses_location_plan(ObjectLocationPlan.FAR)

    def is_front(self) -> bool:
        """Return whether this object ever uses location plan FRONT."""
        return self._uses_location_plan(ObjectLocationPlan.FRONT)

    def is_inside(self) -> bool:
        """Return whether this object ever uses location plan INSIDE_*."""
        return self._uses_location_plan(ObjectLocationPlan.INSIDE_0)

    def is_random(self) -> bool:
        """Return whether this object ever uses location plan RANDOM."""
        return self._uses_location_plan(ObjectLocationPlan.RANDOM)

    def larger_definition(self) -> Dict[str, Any]:
        """Return the larger (in dimensions) of this object's trained or
        untrained definition."""
        return identify_larger_definition(
            self.trained_definition,
            self.untrained_definition
        ) if self.untrained_definition else self.trained_definition

    def larger_definition_of(
        self,
        container_data_list: List[Any],
        second_object_data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Return the larger (in dimensions) of this object's, the given second
        object's, or this object's container's trained or untrained definition.
        Useful if you need to reserve space for the object, since we assume the
        object's receptacle will always be larger than itself."""

        second_object_is_close_and_inside = (
            second_object_data and second_object_data.is_close() and
            second_object_data.is_inside()
        )

        # This object and the second are inside two different containers.
        if (
            self.is_inside() and second_object_is_close_and_inside and
            (not self.containerize_with(second_object_data))
        ):
            # TODO Handle this specific case if needed in the future
            pass

        # This object and the second are inside the same container.
        if self.is_inside() or second_object_is_close_and_inside:
            # TODO May not always be inside container at index 0 in the future
            return container_data_list[0].larger_definition()

        # This object and the second are next to one another.
        if second_object_data and second_object_data.is_close():
            # TODO Return the combined dimensions (target and second object)
            return identify_larger_definition(
                self.larger_definition(),
                second_object_data.larger_definition()
            )

        # Else ignore the second object and just use this object.
        return self.larger_definition()

    def locations_with_indexes(
        self,
        container_data_list: List[Any]
    ) -> List[Tuple[ObjectLocationPlan, List[int]]]:
        """Return this object's distinct location plans and the corresponding
        scene indexes in which the location plan is used."""
        locations_to_indexes = {}
        for index, location_plan in enumerate(self.location_plan_list):
            distinct_location_plan = location_plan
            if location_plan == ObjectLocationPlan.INSIDE_0:
                distinct_location_plan = (
                    container_data_list[0].location_plan_list[index]
                )
            locations_to_indexes[distinct_location_plan] = (
                locations_to_indexes.get(distinct_location_plan, [])
            )
            locations_to_indexes[distinct_location_plan].append(index)
        return list(locations_to_indexes.items())

    def recreate_both_templates(self) -> None:
        """Recreate both templates in this data."""
        self.trained_template = util.instantiate_object(
            self.trained_definition,
            geometry.ORIGIN_LOCATION
        )
        self.untrained_template = util.instantiate_object(
            self.untrained_definition,
            geometry.ORIGIN_LOCATION
        ) if self.untrained_definition else None
        if self.untrained_template:
            self.untrained_template['id'] = self.trained_template['id']

    def reset_all_instances(self) -> None:
        """Reset all instances in this data."""
        for index in range(len(self.instance_list)):
            self.instance_list[index] = None

    def reset_all_properties(self) -> None:
        """Reset all definitions, templates, and instances."""
        self.trained_definition = self.original_definition
        self.untrained_definition = self.original_definition
        self.trained_template = None
        self.untrained_template = None
        self.reset_all_instances()


# Receptacles are anything that may have an object on top of or inside it.
class ReceptacleData(ObjectData):
    def __init__(self, role: str, object_plan: ObjectPlan) -> None:
        super().__init__(role, object_plan)
        self.trained_containment = SimpleNamespace(
            area_index=None,
            orientation=None,
            target_angle=None,
            confusor_angle=None
        )
        self.untrained_containment = SimpleNamespace(
            area_index=None,
            orientation=None,
            target_angle=None,
            confusor_angle=None
        )


class TargetData(ObjectData):
    def __init__(self, object_plan: ObjectPlan, choice: int) -> None:
        super().__init__('TARGET', object_plan)
        self.choice = choice
