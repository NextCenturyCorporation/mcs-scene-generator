import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from ideal_learning_env.defs import ILEConfigurationException, ILEException
from ideal_learning_env.numerics import MinMaxFloat

from .choosers import choose_random
from .components import ILEComponent
from .decorators import ile_config_setter
from .numerics import MinMaxInt
from .validators import ValidateNumber

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


class ActionRestrictionsComponent(ILEComponent):
    passive_scene: bool = False
    """
    (bool): Determine if scene should be considered passive and the
    performer agent should be restricted to only use the `"Pass"` action.
    If true, ILE will raise an exception if last_step is not set or either
    `freezes` or `teleports` has any entries.
    """
    freezes: List[Union[StepBeginEnd, List[StepBeginEnd]]] = None
    """
    (list of [StepBeginEnd](#StepBeginEnd) dicts): When a freeze
    should occur.  A freeze forces the performer agent to only `"Pass"` for a
    range of steps.  User should try to avoid freeze overlaps, but if using
    ranges and choices, the ILE will retry on overlaps.  This field must be
    blank or an empty array if `passive_scene` is `true`.
    """
    teleports: List[Union[TeleportConfig, List[TeleportConfig]]] = None
    """
    (list of [TeleportConfig](#TeleportConfig) dicts): When a
    kidnap/teleport will occur and where the player agent should be teleported.
    This field must contain either both position fields or the `rotation_y`
    field or an exception will be thrown.  This field must be blank or an empty
    array if `passive_scene` is `true`.

    Simple Example:
    ```
    passive_scene: false
    freezes: null
    teleports: null
    ```

    Advanced Example:
    ```
    passive_scene: false
    freezes:
      -
        begin: 1
        end: 3
      -
        begin: [11, 13 ,15]
        end:
          min: 16
          max: 26

    teleports:
      -
        step: 5
        position_x: 3
        position_z: 6
        rotation_y: 45
      -
        step: [34, 36]
        position_x:
          min: -3
          max: 3
        position_z: [3, 5, 7]
      -
        step:
          min: 41
          max: 48
        rotation_y: [30, 120, 270]
    ```
    """
    @ile_config_setter()
    def set_passive_scene(self, data: Any) -> None:
        self.passive_scene = data

    def get_passive_scene(self) -> bool:
        return self.passive_scene

    @ile_config_setter(validator=ValidateNumber(
        props=['begin', 'end'], min_value=1,
        null_ok=True))
    def set_freezes(self, data: Any) -> None:
        self.freezes = data

    def get_freezes(self) -> List[
        StepBeginEnd
    ]:
        return [choose_random(f) for f in (self.freezes or [])]

    @ile_config_setter(validator=ValidateNumber(
        props=['step'], min_value=1))
    @ile_config_setter(validator=ValidateNumber(
        props=['rotation_y'], min_value=0,
        null_ok=True))
    def set_teleports(self, data: Any) -> None:
        self.teleports = data

    def get_teleports(self) -> List[
        TeleportConfig
    ]:
        return [choose_random(t) for t in (self.teleports or [])]

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug('Running action restriction component...')

        scene['objects'] = scene.get('objects', [])
        goal = scene.get('goal', {})
        total_steps = goal.get('last_step')
        freezes = sorted(self.get_freezes(), key=lambda x: x.begin)
        teleports = sorted(self.get_teleports(), key=lambda x: x.step)
        self._restriction_validation(freezes, teleports, total_steps)
        passive = self.get_passive_scene()
        if passive:
            goal['action_list'] = [['Pass']] * total_steps
            logger.debug('Setting whole scene as passive')
        if freezes:
            self._add_freezes(goal, freezes)
            logger.debug(f'Adding {len(freezes)} freezes to scene')
        if teleports:
            self._add_teleports(goal, teleports, passive)
            logger.debug(f'Adding {len(teleports)} teleports to scene')
        return scene

    def _add_teleports(self, goal, teleports, passive):
        goal['action_list'] = goal.get('action_list', [])
        al = goal['action_list']
        for t in teleports:
            step = t.step
            cmd = "EndHabituation"
            cmd += f",xPosition={t.position_x}" if t.position_x else ""
            cmd += f",zPosition={t.position_z}" if t.position_z else ""
            cmd += f",yRotation={t.rotation_y}" if t.rotation_y else ""
            length = len(al)
            if step > length:
                al += ([[]] * (step - length))
            if al[step - 1] != [] and not passive:
                raise ILEException(
                    f"Cannot teleport during freeze at step={step - 1}")
            al[step - 1] = [cmd]

    def _add_freezes(self, goal, freezes):
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
                    f"Freezes has begin >= end ({f.begin} >= {f.end}")
            num_free = f.begin - limit
            num_limited = f.end - f.begin
            al += ([[]] * (num_free))
            al += ([['Pass']] * (num_limited))
            limit = f.end

    def _restriction_validation(self, freezes, teleports, total_steps):
        if self.get_passive_scene():
            if not total_steps or total_steps <= 0:
                raise ILEConfigurationException(
                    "Error with action restriction "
                    "configuration. When 'passive_scene'=true"
                    "total_steps must be set and greater than 0.")
            if self.freezes:
                raise ILEConfigurationException(
                    "Error with action restriction "
                    "configuration. When 'passive_scene'=true"
                    "'freezes' can not be used")
        if freezes:
            for f in freezes:
                if not f.begin and not f.end:
                    raise ILEConfigurationException(
                        "Error with action restriction "
                        "configuration.  'freezes' entries must have "
                        "atleast one of 'begin' or 'end' fields.")
        if teleports:
            for t in teleports:
                if (t.position_x and not t.position_z) or (
                        t.position_z and not t.position_x):
                    raise ILEConfigurationException(
                        "Error with action restriction "
                        "configuration.  'teleport' entries with a "
                        "'position_x' or 'position_z' must also have the "
                        "other."
                    )
                if not (t.rotation_y or (t.position_x and t.position_z)):
                    raise ILEConfigurationException(
                        "Error with action restriction "
                        "configuration.  'teleport' entries must have either "
                        "'rotation_y' field or both 'position_x' and "
                        "'position_z' fields.")
