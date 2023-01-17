import logging
import math
import random
from dataclasses import dataclass
from typing import List, Union

import matplotlib.pyplot as plt
from machine_common_sense.config_manager import Vector3d

from generator import Scene, geometry
from ideal_learning_env.defs import (
    ILEConfigurationException,
    ILEException,
    RandomizableString
)
from ideal_learning_env.numerics import MinMaxFloat, MinMaxInt, RandomizableInt
from ideal_learning_env.object_services import ObjectRepository

logger = logging.getLogger(__name__)


@dataclass
class StepBeginEnd():
    """
    Contains a step range for a specific event.

    - `begin` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list
    of MinMaxInt dicts):
    The step where the performer agent starts being frozen
    and can only use the `"Pass"` action. For example, if 1, the performer
    agent must pass immediately at the start of the scene.  This is an
    inclusive limit.
    - `end` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list
    of MinMaxInt dicts):
    The step where the performer agent ends being frozen and can resume
    using actions besides `"Pass"`.  Therefore, this is an exclusive limit.
    """
    begin: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    end: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None


@dataclass
class TeleportConfig():
    """
    Contains data to describe when and where a teleport occurs.

    - `step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): The step when the performer agent is teleported.
    This field is required for teleport action restrictions.
    - `look_at_center` (bool): Dynamically set the teleport `rotation_y` using
    the `position_x` and `position_z` so the performer agent is facing the
    center of the room. Requires both `position_x` and `position_z` to be set.
    Overrides `rotation_y` if it is also set. Default: false
    - `position_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts):
    Position in X direction where the performer agent
    is teleported.  This field along with `position_z` are required
    if `rotation_y` is not set.
    - `position_z` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts):
    Position in Z direction where the performer agent
    is teleported.  This field along with `position_x` are required
    if `rotation_y` is not set.
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts):
    Rotation in Y direction where the performer agent
    is teleported.  This field is required for teleport action
    restrictions if `position_x` and `position_z` are not both set.
    """
    step: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    position_x: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    position_z: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    rotation_y: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    look_at_center: bool = False


@dataclass
class SidestepsConfig():
    """
    Contains data to describe the performer's sidesteps.

    - `begin` ([RandomizableInt](#RandomizableInt)):
    The step where the performer agent starts being frozen
    and can only use the `"Pass"` action. For example, if 1, the performer
    agent must pass immediately at the start of the scene.  This is an
    inclusive limit.
    - `object_label` ([RandomizableString](#RandomizableString)):
    The label of the object the performer will sidestep around. The performer
    must be 3 distance away from the object's center for sidesteps to work.
    - `degrees` ([RandomizableInt](#RandomizableInt)):
    The positive or negative degrees the performer will sidestep around the
    object. Positive forces the performer to sidestep right while negative
    sidesteps left. The degree value must always be in 90 or -90 degree
    increments: [90, 180, 270, 360, -90, -180, -270, -360]
    Default: [90, 180, 270, 360, -90, -180, -270, -360]
    """
    begin: RandomizableInt = None
    object_label: RandomizableString = None
    degrees: RandomizableInt = None


class ActionService():
    @staticmethod
    def add_circles(goal: dict, circles: List):
        """Adds restrictions to the steps in the goal portion of a scene such
        that the performer can only rotate clockwise for 36 consecutive steps.
        The intervals provided by 'circles' should not overlap."""
        circle_action_list = ['RotateRight']
        circle_length = 36
        goal['action_list'] = goal.get('action_list', [])
        action_list = goal['action_list']

        for circle in circles:
            no_actions = len(action_list) == 0

            if no_actions or circle > len(action_list):
                circle_skip = (
                    circle if no_actions else (circle - len(action_list))
                ) - 1
                action_list += ([[]] * (circle_skip))
                action_list += ([circle_action_list] * (circle_length))

            else:
                step = circle
                while step <= circle_length:
                    if len(action_list) >= step:
                        if (
                            action_list[step - 1] != [] and
                            action_list[step - 1] != circle_action_list
                        ):
                            raise ILEException(
                                f"Circles {circle} overlaps with existing "
                                f"action restriction in action_list: "
                                f"{action_list[step-1]}"
                            )
                        action_list[step - 1] = circle_action_list
                    else:
                        action_list += circle_action_list
                    step = step + 1

    @staticmethod
    def add_freezes(goal: dict, freezes: List[StepBeginEnd]):
        """Adds freezes to the goal portion of the scene. The freezes occur
        over ranges provided by `freezes` and should not overlap.  All random
        choices in any StepBeginEnd instances should be determined prior to
        calling this method."""
        goal['action_list'] = goal.get('action_list', [])
        al = goal['action_list']
        limit = 1
        for f in freezes:
            f.begin = 1 if f.begin is None else f.begin
            if f.end is None:
                if goal['last_step'] is None:
                    raise ILEConfigurationException(
                        "Configuration error.  A freeze without an 'end' "
                        "requires 'last_step' to be set.")
                else:
                    # Add one so we include the last step.  End is exclusive.
                    f.end = goal['last_step'] + 1
            if (limit > f.begin):
                raise ILEException(f"Freezes overlapped at {limit}")
            if f.begin >= f.end:
                raise ILEException(
                    f"Freezes has begin >= end ({f.begin} >= {f.end})")
            num_free = f.begin - limit
            num_limited = f.end - f.begin
            al += ([[]] * (num_free))
            al += ([['Pass']] * (num_limited))
            limit = f.end

    @staticmethod
    def add_freeze_while_moving(goal: dict, freeze_while_moving):
        """Adds freeze while moving"""
        goal['action_list'] = goal.get('action_list', [])
        al = goal['action_list']
        # Must be the first action
        if len(al) > 0:
            raise ILEException(
                "The 'Pass' actions from freeze_while_moving must be the "
                "first actions in the action_list. Any additional actions "
                "must be after.")
        last_move = 0
        last_rotate = 0
        if isinstance(freeze_while_moving, str):
            freeze_while_moving = [freeze_while_moving]
        for label in freeze_while_moving:
            obj_repo = ObjectRepository.get_instance()
            instances = obj_repo.get_all_from_labeled_objects(label)
            if instances is None or len(instances) == 0:
                raise ILEException(
                    "No valid objects matching 'freeze_while_moving' "
                    f"label': {label}"
                )
            objects = [instance.instance for instance in instances]
            for object in objects:
                moves = object.get("moves")
                rotates = object.get("rotates")
                if moves:
                    last_move = max(moves[-1]['stepEnd'], last_move)
                if rotates:
                    last_rotate = max(rotates[-1]['stepEnd'], last_rotate)
        al += ([['Pass']] * (max(last_move, last_rotate)))

    @staticmethod
    def add_teleports(
        goal: dict,
        teleports: List[TeleportConfig],
        passive: bool
    ):
        """adds teleport actions to the goal portion of the scene where a
        performer will be teleported to a new position and/or rotation. All
        random choices in any TeleportConfig instances should be determined
        prior to calling this method."""
        goal['action_list'] = goal.get('action_list', [])
        al = goal['action_list']
        for t in teleports:
            rotation_y = t.rotation_y
            # See TeleportConfig docs for information and assumptions.
            if t.look_at_center:
                if t.position_x is not None and t.position_z is not None:
                    # If we ever need to set the rotation_x in the future,
                    # we'll need to identify the performer's Y position.
                    _, rotation_y = geometry.calculate_rotations(
                        Vector3d(x=t.position_x, y=0, z=t.position_z),
                        Vector3d(x=0, y=0, z=0)
                    )
            step = t.step
            cmd = "EndHabituation"
            if t.position_x is not None:
                cmd += f",xPosition={t.position_x}"
            if t.position_z is not None:
                cmd += f",zPosition={t.position_z}"
            if rotation_y is not None:
                cmd += f",yRotation={rotation_y}"
            length = len(al)
            if step > length:
                al += ([[]] * (step - length))
            if al[step - 1] != [] and not passive:
                raise ILEException(
                    f"Cannot teleport during freeze or swivel "
                    f"at step={step - 1}")
            al[step - 1] = [cmd]

    @staticmethod
    def add_swivels(goal: dict, swivels: List[StepBeginEnd]):
        """Adds restrictions to steps the goal portion of a scene such that the
        performer can only rotate its view (LookDown, LookUp, RotateLeft, or
        RotateRight).  The intervals provided by 'swivels' should not
        overlap. All random choices in any StepBeginEnd instances should be
        determined prior to calling this method."""
        swivel_actions = ['LookDown', 'LookUp', 'RotateLeft', 'RotateRight']
        goal['action_list'] = goal.get('action_list', [])
        al = goal['action_list']

        # check if actions already exist in action list
        # at the start
        al_length = len(al)
        no_actions = al_length == 0

        limit = 1
        for s in swivels:
            s.begin = 1 if s.begin is None else s.begin
            if s.end is None:
                if goal['last_step'] is None:
                    raise ILEConfigurationException(
                        "Configuration error.  A swivel without an 'end' "
                        "requires 'last_step' to be set.")
                else:
                    # Add one so we include the last step.  End is exclusive.
                    s.end = goal['last_step'] + 1
            if (limit > s.begin):
                raise ILEException(f"Swivels overlapped at {limit}")
            if s.begin >= s.end:
                raise ILEException(
                    f"Swivels has begin >= end ({s.begin} >= {s.end})")

            if(no_actions or s.begin > al_length):
                num_free = s.begin - \
                    limit if no_actions else (s.begin - al_length - 1)
                num_limited = s.end - s.begin
                al += ([[]] * (num_free))
                al += ([swivel_actions] * (num_limited))

            else:
                step = s.begin

                while(step < s.end):
                    if(len(al) >= step):
                        if(al[step - 1] != []):
                            raise ILEException(
                                f"Swivels with begin {s.begin} and end "
                                f"{s.end} overlap with existing action "
                                f"in action_list")
                        al[step - 1] = swivel_actions
                    else:
                        al += swivel_actions
                    step = step + 1
            limit = s.end

    @staticmethod
    def add_sidesteps(goal: dict,
                      sidesteps: List[SidestepsConfig],
                      scene: Scene):
        """Adds sidesteps to the goal portion of the scene. The sidesteps occur
        over ranges provided by `sidesteps` and should not overlap.  All random
        choices in any SidestepsConfig instances should be determined prior to
        calling this method."""
        # For a 90 degree increment
        goal['action_list'] = goal.get('action_list', [])
        al = goal['action_list']
        object = None
        label = None
        start_x = scene.performer_start.position.x
        start_z = scene.performer_start.position.z
        start_rot_y = scene.performer_start.rotation.y
        actions = []
        for i, s in enumerate(sidesteps):
            sidesteps_degrees = [90, 180, 270, 360, -90, -180, -270, -360]
            if s.degrees is None:
                s.degrees = random.choice(sidesteps_degrees)
            if s.degrees not in sidesteps_degrees:
                raise ILEException(
                    f"Sidesteps with begin {s.begin} and degrees "
                    f"{s.degrees} must have a degrees value of: "
                    f"[90, 180, 270, 360, -90, -180, -270, -360]"
                )
            # Overlap
            for step in range(s.begin - 1, len(al)):
                if al[step] != []:
                    raise ILEException(
                        f"Sidesteps with begin {s.begin} and degrees "
                        f"{s.degrees} overlap an existing action in "
                        f"action_list. Sidestep {i} of {len(sidesteps)} "
                        f"must begin or be greater than step: "
                        f"{len(al) + 1}"
                    )
            # No overlap
            if len(al) < s.begin:
                empty_to_add = s.begin - len(al) - 1
                al += [[]] * (empty_to_add)
            movement_direction = "MoveRight" if s.degrees > 0 else "MoveLeft"
            rotation_direction = \
                "RotateLeft" if s.degrees > 0 else "RotateRight"

            # Force the performer to look at the target
            # And make sure labels are the same
            if object is None:
                label = s.object_label
                # Object
                obj_repo = ObjectRepository.get_instance()
                instances = obj_repo.get_all_from_labeled_objects(
                    s.object_label)
                if instances is None or len(instances) == 0:
                    raise ILEException(
                        "No valid objects matching 'sidesteps."
                        f"object_label': {s.object_label}"
                    )
                objects = [instance.instance for instance in instances]
                object = random.choice(objects)
                perf_pos = scene.performer_start.position
                object_pos = object['shows'][0]['position']
                tbb = object['shows'][0]['boundingBox']

                # Forced to look at object with label
                object_y = (tbb.min_y + tbb.max_y) / 2.0
                tilt, rot = geometry.calculate_rotations(
                    perf_pos,
                    Vector3d(x=object_pos['x'], y=object_y, z=object_pos['z'])
                )
                scene.performer_start.rotation.y = rot
                scene.performer_start.rotation.x = tilt
                start_rot_y = scene.performer_start.rotation.y
            elif s.object_label != label:
                raise ILEException(
                    "All consecutive 'sidesteps.object_labels' "
                    f"must be identical. Mismatching labels: "
                    f"('{s.object_label}', '{label}')"
                )

            # Distance
            center_x, center_z = object[
                'shows'][0]['boundingBox'].polygon_xz.centroid.coords[0]
            base_distance = math.dist([center_x, center_z], [start_x, start_z])

            # Any distance closer results in inconsistent behavior
            # Where the performer may move and rotate in a circle endlessly
            min_distance_to_prevent_circling = 3
            base_rounded_distance = round(base_distance, 1)
            if base_rounded_distance < min_distance_to_prevent_circling:
                raise ILEException(
                    "Performer must be at least "
                    f"{min_distance_to_prevent_circling} distance away "
                    "from the center of object with label "
                    f"'{s.object_label}' when using 'sidesteps'"
                )
            end_x, end_z = geometry.rotate_point_around_origin(
                center_x, center_z, start_x, start_z, -s.degrees)
            end_x = round(end_x, 2)
            end_z = round(end_z, 2)
            position_x = start_x
            position_z = start_z
            rotation_y = start_rot_y

            # This is so the movement after rotation has time to readjusted
            # to the desired distance instead of rotating in circles
            # endlessly and also makes sure the performer is guranteed to
            # look at the object a few steps before rotating
            base_skip_rotation_count = 2
            skip_rotation_count = base_distance
            # This is so if its a 360 degree rotation that the movement
            # starts otherwise we are already where we want to be
            # and nothing happens
            initial_distance_check_skips = 2
            # Small buffer for checking if the performer is where they
            # need to be
            move_distance = geometry.MOVE_DISTANCE

            """
            ***Note*** If you want to see this visually traced set
            create_debug_graph to True to create a graph showing the path
            """
            create_debug_graph = False  # *DEBUG*
            if create_debug_graph:
                xs = []
                zs = []

            while True:
                # Get current distance
                distance = math.dist(
                    [center_x, center_z],
                    [position_x, position_z])
                # Check if we need to rotate if the distance is too big now
                if (abs(distance - base_distance) > move_distance and
                        skip_rotation_count <= 0):
                    actions.append([rotation_direction])
                    rotation_y += 10 if s.degrees < 0 else -10
                    skip_rotation_count = base_skip_rotation_count

                # Get the transform right or left vector components of
                # the performer
                x, z = geometry.get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(  # noqa
                    rotation_y,
                    move_distance if s.degrees > 0 else -move_distance,
                    0
                )
                # Keep track of where we are
                position_x += x
                position_z += z
                # Add action
                actions.append([movement_direction])

                # Mark that we are closer to when we can rotate
                skip_rotation_count -= 1
                # Mark that we are clearing the start distance
                initial_distance_check_skips -= \
                    1 if initial_distance_check_skips > 0 else 0

                buffer = 0.01
                # If both x and z positions have reached the end
                if (abs(position_x - end_x) <= move_distance + buffer and
                    abs(position_z - end_z) <= move_distance + buffer and
                        initial_distance_check_skips <= 0):
                    # May need to add one more move if we are not totally
                    # where we need to be
                    if distance > base_distance:
                        position_x += x
                        position_z += z
                        actions.append([movement_direction])
                    # Then make sure we rotated the correct amount too
                    # We are probably only 1 off in either direction
                    # But check if theres more than 1 just in case
                    if (rotation_y != scene.performer_start.rotation.y -
                            s.degrees):
                        additional_rotations = round((
                            (rotation_y -
                                (scene.performer_start.rotation.y -
                                 s.degrees)) / 10))
                        # Rotated too much
                        if (additional_rotations < 0 and
                                rotation_direction == "RotateLeft"):
                            actions += [["RotateRight"]] * \
                                abs(additional_rotations)
                        elif (additional_rotations > 0 and
                                rotation_direction == "RotateRight"):
                            actions += [["RotateLeft"]] * \
                                abs(additional_rotations)
                        # Rotated too little
                        else:
                            actions += [[rotation_direction]] * \
                                additional_rotations
                    start_x = position_x
                    start_z = position_z
                    start_rot_y = rotation_y
                    break
                if create_debug_graph:
                    xs.append(position_x)
                    zs.append(position_z)
            if create_debug_graph:
                plt.gca().set_aspect('equal', adjustable='box')
                plt.scatter(xs, zs)
                plt.scatter(
                    scene.performer_start.position.x,
                    scene.performer_start.position.z)
                plt.savefig("sidesteps.png")

            al += actions
