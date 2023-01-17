import logging
from typing import Any, Dict, List, Union

from generator import tags
from ideal_learning_env.defs import (
    ILEConfigurationException,
    RandomizableString
)

from .action_service import (
    ActionService,
    SidestepsConfig,
    StepBeginEnd,
    TeleportConfig
)
from .choosers import choose_random
from .components import ILEComponent
from .decorators import ile_config_setter
from .numerics import MinMaxInt
from .validators import ValidateNumber, ValidateOptions

logger = logging.getLogger(__name__)


class ActionRestrictionsComponent(ILEComponent):
    passive_scene: bool = False
    """
    (bool): Determine if scene should be considered passive and the
    performer agent should be restricted to only use the `"Pass"` action.
    If true, ILE will raise an exception if last_step is not set or either
    `circles`, `freezes`, `swivels` or `teleports` has any entries.
    Redundant if the `passive_physics_scene` config option is `true`.
    Default: `false`
    """

    circles: List[Union[int, MinMaxInt, List[Union[int, MinMaxInt]]]] = None
    """
    (list of either ints, or lists of ints, or [MinMaxInt](#MinMaxInt) dicts,
    or lists of MinMaxInt dicts): When the AI should be forced to rotate in a
    complete circle counterclockwise (by only allowing RotateRight actions for
    36 consecutive actions).
    This field must be blank or an empty array if `passive_scene` is `true`.

    Simple Example:
    ```
    circles: null
    ```

    Advanced Example:
    ```
    circles:
      - 7
      - [107, 207]
    ```
    """

    freezes: List[Union[StepBeginEnd, List[StepBeginEnd]]] = None
    """
    (list of [StepBeginEnd](#StepBeginEnd) dicts): When a freeze
    should occur.  A freeze forces the performer agent to only `"Pass"` for a
    range of steps.  User should try to avoid freeze overlaps, but if using
    ranges and choices, the ILE will retry on overlaps.  This field must be
    blank or an empty array if `passive_scene` is `true`.

    Simple Example:
    ```
    freezes: null
    ```

    Advanced Example:
    ```
    freezes:
      -
        begin: 1
        end: 3
      -
        begin: [11, 13 ,15]
        end:
          min: 16
          max: 26

    ```
    """

    freeze_while_moving: RandomizableString = None
    """
    (string or list of strings): Forces the performer to freeze ("Pass") until
    all objects with the given labels complete their last movements and
    rotations. This field must be blank or an empty array if
    `passive_scene` is `true`.

    Simple Example:
    ```
    freeze_while_moving: null
    ```

    Advanced Example:
    ```
    freezes_while_moving:
      - [placers, turntables]
      - [turntables]

    ```
    """

    swivels: List[Union[StepBeginEnd, List[StepBeginEnd]]] = None
    """
    (list of [StepBeginEnd](#StepBeginEnd) dicts): When a swivel
    action should occur.  A swivel forces the performer agent to only
    `"['LookDown', 'LookUp', 'RotateLeft', 'RotateRight']"` for a
    range of steps.  User should try to avoid swivel (and freeze) overlaps
    but if using ranges and choices, the ILE will retry on overlaps.
    This field must be blank or an empty array if `passive_scene` is `true`.

    Simple Example:
    ```
    swivels: null
    ```

    Advanced Example:
    ```
    swivels:
      -
        begin: 7
        end: 9
      -
        begin: [16, 18, 20]
        end:
          min: 26
          max: 30

    ```
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
    teleports: null
    ```

    Advanced Example:
    ```
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

    sidesteps: List[Union[SidestepsConfig, List[SidestepsConfig]]] = None
    """
    (list of [SidestepsConfig](#SidestepsConfig) dicts): When a sequence of
    sidesteps will occur, the label of the object the performer will sidestep
    around, and the degrees around the object the performer will sidestep.
    Degrees must be in increments of
    90 or -90: [90, 180, 270, 360, -90, -180, -270, -360].
    If a consecutive list all labels MUST be identical.
    The performer must be 3 distance away from the object's center
    for sidesteps to work.
    *Important Note*: this property will OVERRIDE 'performer_look_at'
    and `performer_start_rotation` forcing the performer to look at
    this object on scene start.

    Simple Example:
    ```
    sidesteps: null
    ```

    Advanced Example:
    ```
    sidesteps:
      -
        begin: 50
        object_label: turntable
        degrees: 90
      -
        begin: 1
        object_label: turntable
        degrees: [90, 180, 270, 360, -90, -180, -270, -360]
    ```
    """

    @ile_config_setter()
    def set_passive_scene(self, data: Any) -> None:
        self.passive_scene = data

    def get_passive_scene(self) -> bool:
        return self.passive_scene

    @ile_config_setter(validator=ValidateNumber(min_value=1, null_ok=True))
    def set_circles(self, data: Any) -> None:
        self.circles = data

    def get_circles(self) -> List[StepBeginEnd]:
        return [choose_random(s) for s in (self.circles or [])]

    @ile_config_setter(validator=ValidateNumber(
        props=['begin', 'end'], min_value=1,
        null_ok=True))
    def set_freezes(self, data: Any) -> None:
        self.freezes = data

    def get_freezes(self) -> List[
        StepBeginEnd
    ]:
        return [choose_random(f) for f in (self.freezes or [])]

    @ile_config_setter()
    def set_freeze_while_moving(self, data: Any) -> None:
        self.freeze_while_moving = data

    def get_freeze_while_moving(self) -> List[str]:
        return self.freeze_while_moving

    @ile_config_setter(validator=ValidateNumber(
        props=['begin', 'end'], min_value=1,
        null_ok=True))
    def set_swivels(self, data: Any) -> None:
        self.swivels = data

    def get_swivels(self) -> List[StepBeginEnd]:
        return [choose_random(s) for s in (self.swivels or [])]

    @ile_config_setter(validator=ValidateNumber(
        props=['step'], min_value=1))
    @ile_config_setter(validator=ValidateNumber(
        props=['rotation_y'], min_value=0,
        null_ok=True))
    def set_teleports(self, data: Any) -> None:
        self.teleports = data

    def get_teleports(self) -> List[TeleportConfig]:
        return [choose_random(t) for t in (self.teleports or [])]

    @ile_config_setter(validator=ValidateOptions(
        props=['degrees'],
        options=[90, 180, 270, 360, -90, -180, -270, -360]))
    def set_sidesteps(self, data: Any) -> None:
        self.sidesteps = data

    def get_sidesteps(self) -> List[SidestepsConfig]:
        return [choose_random(s) for s in (self.sidesteps or [])]

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring action restrictions for the scene...')

        goal = scene.goal or {}
        total_steps = goal.get('last_step')
        circles = sorted(self.get_circles())
        freezes = sorted(self.get_freezes(), key=lambda x: x.begin)
        freeze_while_moving = self.get_freeze_while_moving()
        swivels = sorted(self.get_swivels(), key=lambda x: x.begin)
        teleports = sorted(self.get_teleports(), key=lambda x: x.step)
        sidesteps = sorted(self.get_sidesteps(), key=lambda x: x.begin)
        self._restriction_validation(
            circles,
            freezes,
            freeze_while_moving,
            swivels,
            teleports,
            sidesteps,
            total_steps
        )
        passive = self.get_passive_scene() or scene.intuitive_physics
        self._delayed_actions = 0
        self._delayed_sidesteps = None
        if passive:
            goal['category'] = tags.tag_to_label(
                tags.SCENE.INTUITIVE_PHYSICS)
            goal['action_list'] = [['Pass']] * total_steps
            logger.trace('Setting whole scene as passive')
        if circles:
            ActionService.add_circles(goal, circles)
            logger.trace(f'Adding {len(circles)} circles to scene')
        if freezes:
            ActionService.add_freezes(goal, freezes)
            logger.trace(f'Adding {len(freezes)} freezes to scene')
        if freeze_while_moving:
            self.freeze_while_moving = freeze_while_moving
            logger.trace(
                f'Adding {len(freeze_while_moving)} '
                f'freeze_while_moving to scene')
        if swivels:
            ActionService.add_swivels(goal, swivels)
            logger.trace(
                f'Adding {len(swivels)} swivels to scene')
        if teleports:
            ActionService.add_teleports(goal, teleports, passive)
            logger.trace(f'Adding {len(teleports)} teleports to scene')
        if sidesteps:
            self._delayed_sidesteps = sidesteps
            self._delayed_actions += 1
            logger.trace(f'Adding {len(sidesteps)} teleports to scene')
        return scene

    def get_num_delayed_actions(self) -> int:
        return self._delayed_actions

    def run_delayed_actions(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        if self._delayed_sidesteps:
            ActionService.add_sidesteps(
                scene.goal, self._delayed_sidesteps, scene)
        self._delayed_actions = 0
        return scene

    def run_actions_at_end_of_scene_generation(
            self, scene: Dict[str, Any]) -> Dict[str, Any]:
        if self.freeze_while_moving:
            ActionService.add_freeze_while_moving(
                scene.goal, self.freeze_while_moving)
        return scene

    def _restriction_validation(
            self, circles, freezes, freeze_while_moving, swivels,
            teleports, sidesteps, total_steps):
        if self.get_passive_scene():
            if not total_steps or total_steps <= 0:
                raise ILEConfigurationException(
                    "Error with action restriction "
                    "configuration. When 'passive_scene'=true"
                    "total_steps must be set and greater than 0.")
            if self.circles:
                raise ILEConfigurationException(
                    "Error with action restriction "
                    "configuration. When 'passive_scene'=true"
                    "'circles' can not be used")
            if self.freezes:
                raise ILEConfigurationException(
                    "Error with action restriction "
                    "configuration. When 'passive_scene'=true"
                    "'freezes' can not be used")
            if self.swivels:
                raise ILEConfigurationException(
                    "Error with action restriction "
                    "configuration. When 'passive_scene'=true"
                    "'swivels' can not be used")
            if self.sidesteps:
                raise ILEConfigurationException(
                    "Error with action restriction "
                    "configuration. When 'passive_scene'=true"
                    "'sidesteps' can not be used")
        if freezes:
            for f in freezes:
                if not f.begin and not f.end:
                    raise ILEConfigurationException(
                        "Error with action restriction "
                        "configuration.  'freezes' entries must have "
                        "at least one of 'begin' or 'end' fields.")
        if swivels:
            for s in swivels:
                if not s.begin and not s.end:
                    raise ILEConfigurationException(
                        "Error with action restriction "
                        "configuration. 'swivels' entries must have "
                        "at least one of 'begin' or 'end' fields.")
        if teleports:
            for t in teleports:
                if (
                    (t.position_x is not None and t.position_z is None) or
                    (t.position_x is None and t.position_z is not None)
                ):
                    raise ILEConfigurationException(
                        "Error with action restriction "
                        "configuration.  'teleport' entries with a "
                        "'position_x' or 'position_z' must also have the "
                        "other."
                    )
        if sidesteps:
            for s in sidesteps:
                if not s.begin and s.object_label:
                    raise ILEConfigurationException(
                        "Error with action restriction "
                        "configuration. 'sidesteps' entries must have "
                        "both 'begin' and 'object_label' fields.")
