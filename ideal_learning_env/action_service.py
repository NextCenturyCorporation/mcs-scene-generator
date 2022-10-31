import logging
from dataclasses import dataclass
from typing import List, Union

from machine_common_sense.config_manager import Vector3d

from generator import geometry
from ideal_learning_env.defs import ILEConfigurationException, ILEException
from ideal_learning_env.numerics import MinMaxFloat, MinMaxInt

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
