from enum import Enum, auto
from typing import Dict, List

from generator import ObjectDefinition, base_objects, tags


class ObjectLocationPlan(Enum):
    # Positioned in front of the performer.
    FRONT = auto()
    # Positioned in back of the performer.
    BACK = auto()
    # Positioned very close to the target (for confusors) OR
    # positioned in front of the large container at index 0 (for targets) OR
    # positioned behind the target (for obstacles and occluders).
    CLOSE = auto()
    # Positioned far away from the target.
    FAR = auto()
    # Positioned somewhere between the performer and the target.
    BETWEEN = auto()
    # Positioned randomly anywhere in the scene.
    RANDOM = auto()
    # Positioned inside the large container at index 0.
    INSIDE_0 = auto()
    # Not positioned anywhere in the scene (object does not exist).
    NONE = auto()


class ObjectPlan():
    """Configurable setup options for a single object in a single interactive
    scene."""

    def __init__(
        self,
        location: ObjectLocationPlan,
        untrained: bool = False,
        definition: ObjectDefinition = None
    ) -> None:
        self.location = location
        self.untrained = untrained
        self.definition = definition


class InteractivePlan():
    """Configurable setup options for a single interactive scene."""

    def __init__(
        self,
        scene_id: str,
        slice_tags: Dict[str, str],
        target_plan: ObjectPlan,
        confusor_plan: ObjectPlan = None,
        large_container_plan_list: List[ObjectPlan] = None,
        obstacle_plan_list: List[ObjectPlan] = None,
        occluder_plan_list: List[ObjectPlan] = None,
        small_container_plan_list: List[ObjectPlan] = None
    ) -> None:
        self.scene_id = scene_id
        self.slice_tags = slice_tags
        # A target object for the interactive hypercube's goal.
        self.target_plan = target_plan
        # The target's confusor, similar in two of: color, shape, size.
        self.confusor_plan_list = [confusor_plan] if confusor_plan else []
        # List of containers large enough to hold the target inside.
        self.large_container_plan_list = (
            large_container_plan_list if large_container_plan_list else []
        )
        # List of target's possible obstacles (blocks navigation).
        self.obstacle_plan_list = (
            obstacle_plan_list if obstacle_plan_list else []
        )
        # List of target's possible occluders (blocks navigation/vision).
        self.occluder_plan_list = (
            occluder_plan_list if occluder_plan_list else []
        )
        # List of containers too small to hold the target inside.
        self.small_container_plan_list = (
            small_container_plan_list if small_container_plan_list else []
        )

    def object_plans(self) -> Dict[str, List[ObjectPlan]]:
        return {
            'target': [self.target_plan],
            'confusor': self.confusor_plan_list,
            'large_container': self.large_container_plan_list,
            'obstacle': self.obstacle_plan_list,
            'occluder': self.occluder_plan_list,
            'small_container': self.small_container_plan_list
        }


def create_container_hypercube_plan_list() -> List[InteractivePlan]:
    plans = {}

    # Each scene must have a target and a main container with the target inside
    # of it, and may have one to four additional containers, some large enough
    # to fit the target inside of them, some not.
    for i in [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
        'o', 'p', 'q', 'r'
    ]:
        for j in ['1', '2']:
            slice_tags = {}
            slice_tags[tags.TYPES.INTERACTIVE_CONTAINERS_LARGE] = (
                tags.CELLS.INTERACTIVE_CONTAINERS_LARGE.ONE
            )
            slice_tags[tags.TYPES.INTERACTIVE_CONTAINERS_SMALL] = (
                tags.CELLS.INTERACTIVE_CONTAINERS_SMALL.ZERO
            )
            slice_tags[tags.TYPES.INTERACTIVE_CONTAINERS_TRAINED] = (
                tags.CELLS.INTERACTIVE_CONTAINERS_TRAINED.YES
            )
            slice_tags[tags.TYPES.INTERACTIVE_TARGET_INSIDE] = (
                tags.CELLS.INTERACTIVE_TARGET_INSIDE.YES
            )
            plans[i + j] = InteractivePlan(
                i + j,
                slice_tags,
                target_plan=ObjectPlan(
                    ObjectLocationPlan.INSIDE_0,
                    definition=base_objects.create_soccer_ball()
                ),
                large_container_plan_list=[
                    ObjectPlan(ObjectLocationPlan.RANDOM),
                    ObjectPlan(ObjectLocationPlan.NONE),
                    ObjectPlan(ObjectLocationPlan.NONE)
                ],
                small_container_plan_list=[
                    ObjectPlan(ObjectLocationPlan.NONE),
                    ObjectPlan(ObjectLocationPlan.NONE)
                ]
            )

    # Target is not inside the container.
    for i in ['d', 'e', 'f', 'j', 'k', 'l', 'p', 'q', 'r']:
        for j in ['1', '2']:
            plans[i + j].target_plan.location = ObjectLocationPlan.CLOSE
            plans[i + j].slice_tags[tags.TYPES.INTERACTIVE_TARGET_INSIDE] = (
                tags.CELLS.INTERACTIVE_TARGET_INSIDE.NO
            )

    # Add one or two large containers anywhere in the scene.
    for i in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']:
        for j in ['1', '2']:
            plans[i + j].large_container_plan_list[1].location = (
                ObjectLocationPlan.RANDOM
            )
            if i in ['a', 'b', 'c', 'd', 'e', 'f']:
                plans[i + j].large_container_plan_list[2].location = (
                    ObjectLocationPlan.RANDOM
                )
                plans[i + j].slice_tags[
                    tags.TYPES.INTERACTIVE_CONTAINERS_LARGE
                ] = tags.CELLS.INTERACTIVE_CONTAINERS_LARGE.THREE
            else:
                plans[i + j].slice_tags[
                    tags.TYPES.INTERACTIVE_CONTAINERS_LARGE
                ] = tags.CELLS.INTERACTIVE_CONTAINERS_LARGE.TWO

    # Add one or two small containers anywhere in the scene.
    for i in ['b', 'c', 'e', 'f', 'h', 'i', 'k', 'l', 'n', 'o', 'q', 'r']:
        for j in ['1', '2']:
            plans[i + j].small_container_plan_list[0].location = (
                ObjectLocationPlan.RANDOM
            )
            if i in ['c', 'f', 'i', 'l', 'o', 'r']:
                plans[i + j].small_container_plan_list[1].location = (
                    ObjectLocationPlan.RANDOM
                )
                plans[i + j].slice_tags[
                    tags.TYPES.INTERACTIVE_CONTAINERS_SMALL
                ] = tags.CELLS.INTERACTIVE_CONTAINERS_SMALL.TWO
            else:
                plans[i + j].slice_tags[
                    tags.TYPES.INTERACTIVE_CONTAINERS_SMALL
                ] = tags.CELLS.INTERACTIVE_CONTAINERS_SMALL.ONE

    # Each container is an untrained shape.
    for i in [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
        'o', 'p', 'q', 'r'
    ]:
        plans[i + '2'].large_container_plan_list[0].untrained = True
        plans[i + '2'].large_container_plan_list[1].untrained = True
        plans[i + '2'].large_container_plan_list[2].untrained = True
        plans[i + '2'].small_container_plan_list[0].untrained = True
        plans[i + '2'].small_container_plan_list[1].untrained = True
        plans[i + '2'].slice_tags[
            tags.TYPES.INTERACTIVE_CONTAINERS_TRAINED
        ] = tags.CELLS.INTERACTIVE_CONTAINERS_TRAINED.NO

    # Sort plans by ID.
    return sorted(list(plans.values()), key=lambda x: x.scene_id)


def create_eval_4_container_hypercube_plan_list() -> List[InteractivePlan]:
    plans = {}

    # Each scene must have a target and a main container with the target inside
    # of it, and may have one to four additional containers, some large enough
    # to fit the target inside of them, some not.
    for i in ['a', 'd', 'g', 'j', 'm', 'p']:
        for j in ['1', '2']:
            slice_tags = {}
            slice_tags[tags.TYPES.INTERACTIVE_CONTAINERS_LARGE] = (
                tags.CELLS.INTERACTIVE_CONTAINERS_LARGE.ONE
            )
            slice_tags[tags.TYPES.INTERACTIVE_CONTAINERS_SMALL] = (
                tags.CELLS.INTERACTIVE_CONTAINERS_SMALL.ZERO
            )
            slice_tags[tags.TYPES.INTERACTIVE_CONTAINERS_TRAINED] = (
                tags.CELLS.INTERACTIVE_CONTAINERS_TRAINED.YES
            )
            slice_tags[tags.TYPES.INTERACTIVE_TARGET_INSIDE] = (
                tags.CELLS.INTERACTIVE_TARGET_INSIDE.YES
            )
            plans[i + j] = InteractivePlan(
                i + j,
                slice_tags,
                target_plan=ObjectPlan(
                    ObjectLocationPlan.INSIDE_0,
                    definition=base_objects.create_soccer_ball()
                ),
                large_container_plan_list=[
                    ObjectPlan(ObjectLocationPlan.RANDOM),
                    ObjectPlan(ObjectLocationPlan.NONE),
                    ObjectPlan(ObjectLocationPlan.NONE)
                ]
            )

    # Target is not inside the container.
    for i in ['d', 'j', 'p']:
        for j in ['1', '2']:
            plans[i + j].target_plan.location = ObjectLocationPlan.CLOSE
            plans[i + j].slice_tags[tags.TYPES.INTERACTIVE_TARGET_INSIDE] = (
                tags.CELLS.INTERACTIVE_TARGET_INSIDE.NO
            )

    # Add one or two large containers anywhere in the scene.
    for i in ['a', 'd', 'g', 'j']:
        for j in ['1', '2']:
            plans[i + j].large_container_plan_list[1].location = (
                ObjectLocationPlan.RANDOM
            )
            if i in ['a', 'b', 'c', 'd', 'e', 'f']:
                plans[i + j].large_container_plan_list[2].location = (
                    ObjectLocationPlan.RANDOM
                )
                plans[i + j].slice_tags[
                    tags.TYPES.INTERACTIVE_CONTAINERS_LARGE
                ] = tags.CELLS.INTERACTIVE_CONTAINERS_LARGE.THREE
            else:
                plans[i + j].slice_tags[
                    tags.TYPES.INTERACTIVE_CONTAINERS_LARGE
                ] = tags.CELLS.INTERACTIVE_CONTAINERS_LARGE.TWO

    # Each container is an untrained shape.
    for i in ['a', 'd', 'g', 'j', 'm', 'p']:
        plans[i + '2'].large_container_plan_list[0].untrained = True
        plans[i + '2'].large_container_plan_list[1].untrained = True
        plans[i + '2'].large_container_plan_list[2].untrained = True
        plans[i + '2'].slice_tags[
            tags.TYPES.INTERACTIVE_CONTAINERS_TRAINED
        ] = tags.CELLS.INTERACTIVE_CONTAINERS_TRAINED.NO

    # Sort plans by ID.
    return sorted(list(plans.values()), key=lambda x: x.scene_id)


def create_obstacle_hypercube_plan_list() -> List[InteractivePlan]:
    plans = {}

    # Each scene must have a target and an obstacle. By default, the target is
    # in back of the performer, and the obstacle in between the performer and
    # the target.
    for i in ['a', 'b', 'c', 'd']:
        for j in ['1', '2']:
            slice_tags = {}
            slice_tags[tags.TYPES.INTERACTIVE_OBSTACLE_BETWEEN] = (
                tags.CELLS.INTERACTIVE_OBSTACLE_BETWEEN.YES
            )
            slice_tags[tags.TYPES.INTERACTIVE_OBSTACLE_TRAINED] = (
                tags.CELLS.INTERACTIVE_OBSTACLE_TRAINED.YES
            )
            slice_tags[tags.TYPES.INTERACTIVE_TARGET_BEHIND] = (
                tags.CELLS.INTERACTIVE_TARGET_BEHIND.YES
            )
            plans[i + j] = InteractivePlan(
                i + j,
                slice_tags,
                target_plan=ObjectPlan(
                    ObjectLocationPlan.BACK,
                    definition=base_objects.create_soccer_ball()
                ),
                obstacle_plan_list=[ObjectPlan(ObjectLocationPlan.BETWEEN)]
            )

    # Target is in front of performer.
    for i in ['c', 'd']:
        for j in ['1', '2']:
            plans[i + j].target_plan.location = ObjectLocationPlan.FRONT
            plans[i + j].slice_tags[tags.TYPES.INTERACTIVE_TARGET_BEHIND] = (
                tags.CELLS.INTERACTIVE_TARGET_BEHIND.NO
            )

    # Obstacle is behind target.
    for i in ['b', 'd']:
        for j in ['1', '2']:
            plans[i + j].obstacle_plan_list[0].location = (
                ObjectLocationPlan.CLOSE
            )
            plans[i + j].slice_tags[
                tags.TYPES.INTERACTIVE_OBSTACLE_BETWEEN
            ] = (
                tags.CELLS.INTERACTIVE_OBSTACLE_BETWEEN.NO
            )

    # Obstacle is an untrained shape.
    for i in ['a', 'b', 'c', 'd']:
        plans[i + '2'].obstacle_plan_list[0].untrained = True
        plans[i + '2'].slice_tags[tags.TYPES.INTERACTIVE_OBSTACLE_TRAINED] = (
            tags.CELLS.INTERACTIVE_OBSTACLE_TRAINED.NO
        )

    # Sort plans by ID.
    return sorted(list(plans.values()), key=lambda x: x.scene_id)


def create_occluder_hypercube_plan_list() -> List[InteractivePlan]:
    plans = {}

    # Each scene must have a target and a main occluder, and may have one or
    # two additional occluder-sized objects NOT between the target and the
    # performer. By default, the target is in back of the performer, and the
    # main occluder is between the performer and the target.
    for i in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']:
        for j in ['1', '2']:
            slice_tags = {}
            slice_tags[tags.TYPES.INTERACTIVE_OCCLUDERS] = (
                tags.CELLS.INTERACTIVE_OCCLUDERS.ONE
            )
            slice_tags[tags.TYPES.INTERACTIVE_OCCLUDERS_TRAINED] = (
                tags.CELLS.INTERACTIVE_OCCLUDERS_TRAINED.YES
            )
            slice_tags[tags.TYPES.INTERACTIVE_TARGET_BEHIND] = (
                tags.CELLS.INTERACTIVE_TARGET_BEHIND.YES
            )
            slice_tags[tags.TYPES.INTERACTIVE_TARGET_HIDDEN] = (
                tags.CELLS.INTERACTIVE_TARGET_HIDDEN.YES
            )
            plans[i + j] = InteractivePlan(
                i + j,
                slice_tags,
                target_plan=ObjectPlan(
                    ObjectLocationPlan.BACK,
                    definition=base_objects.create_soccer_ball()
                ),
                occluder_plan_list=[
                    ObjectPlan(ObjectLocationPlan.BETWEEN),
                    ObjectPlan(ObjectLocationPlan.NONE),
                    ObjectPlan(ObjectLocationPlan.NONE)
                ]
            )

    # Target is in front of performer.
    for i in ['c', 'd', 'g', 'h', 'k', 'l']:
        for j in ['1', '2']:
            plans[i + j].target_plan.location = ObjectLocationPlan.FRONT
            plans[i + j].slice_tags[tags.TYPES.INTERACTIVE_TARGET_BEHIND] = (
                tags.CELLS.INTERACTIVE_TARGET_BEHIND.NO
            )

    # Main occluder is behind target.
    for i in ['b', 'd', 'f', 'h', 'j', 'l']:
        for j in ['1', '2']:
            plans[i + j].occluder_plan_list[0].location = (
                ObjectLocationPlan.CLOSE
            )
            plans[i + j].slice_tags[tags.TYPES.INTERACTIVE_TARGET_HIDDEN] = (
                tags.CELLS.INTERACTIVE_TARGET_HIDDEN.NO
            )

    # Add one or two occluder-sized objects anywhere in the scene.
    for i in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
        for j in ['1', '2']:
            plans[i + j].occluder_plan_list[1].location = (
                ObjectLocationPlan.RANDOM
            )
            if i in ['a', 'b', 'c', 'd']:
                plans[i + j].occluder_plan_list[2].location = (
                    ObjectLocationPlan.RANDOM
                )
                plans[i + j].slice_tags[tags.TYPES.INTERACTIVE_OCCLUDERS] = (
                    tags.CELLS.INTERACTIVE_OCCLUDERS.THREE
                )
            else:
                plans[i + j].slice_tags[tags.TYPES.INTERACTIVE_OCCLUDERS] = (
                    tags.CELLS.INTERACTIVE_OCCLUDERS.TWO
                )

    # Each occluder is an untrained shape.
    for i in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']:
        plans[i + '2'].occluder_plan_list[0].untrained = True
        plans[i + '2'].occluder_plan_list[1].untrained = True
        plans[i + '2'].occluder_plan_list[2].untrained = True
        plans[i + '2'].slice_tags[tags.TYPES.INTERACTIVE_OCCLUDERS_TRAINED] = (
            tags.CELLS.INTERACTIVE_OCCLUDERS_TRAINED.NO
        )

    # Sort plans by ID.
    return sorted(list(plans.values()), key=lambda x: x.scene_id)
