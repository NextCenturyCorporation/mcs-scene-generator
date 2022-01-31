import logging
import math
import random
from typing import Any, Dict

from generator import MAX_TRIES
from ideal_learning_env.numerics import MinMaxFloat, VectorFloatConfig

from .components import ILEComponent
from .defs import ILEException, find_bounds
from .structural_object_generator import (
    StructuralPlatformConfig,
    StructuralRampConfig,
    StructuralTypes,
    add_structural_object_with_retries_or_throw,
)

logger = logging.getLogger(__name__)


class ShortcutComponent(ILEComponent):
    """Manages the settings for common shortcuts for an ILE scene."""

    # Ramp to platform constants
    RAMP_ANGLE_MAX = 40
    RAMP_ANGLE_MIN = 5
    RAMP_TO_PLATFORM_PLATFORM_LENGTH_MIN = 1
    RAMP_TO_PLATFORM_PLATFORM_LENGTH_MAX = 5
    RAMP_TO_PLATFORM_MIN_HEIGHT = 1
    RAMP_TO_PLATFORM_MIN_DIST_TO_CEILING = 1

    shortcut_bisecting_platform: bool = False
    """
    (bool): Creates a platform bisecting the room.  The performer starts on one
    end with a wall in front of them such that the performer is forced to make
    a choice on which side they want to drop off and they cannot get back to
    the other side.  Default: False

    Simple Example:
    ```
    shortcut_bisecting_platform: False
    ```

    Advanced Example:
    ```
    shortcut_bisecting_platform: True
    ```
    """

    shortcut_ramp_to_platform: bool = False
    """
    (bool): Creates a ramp with a platform connected to it such that a
    performer can climb the ramp up to the platform. Will automatically add the
    "platform_next_to_ramp" label to the platform and the
    "ramp_next_to_platform" label to the ramp.  Default: False

    Simple Example:
    ```
    shortcut_ramp_to_platform: False
    ```

    Advanced Example:
    ```
    shortcut_ramp_to_platform: True
    ```
    """

    def set_shortcut_bisecting_platform(self, data: Any) -> None:
        self.shortcut_bisecting_platform = data

    def get_shortcut_bisecting_platform(
            self) -> bool:
        return self.shortcut_bisecting_platform

    def set_shortcut_ramp_to_platform(self, data: Any) -> None:
        self.shortcut_ramp_to_platform = data

    def get_shortcut_ramp_to_platform(
            self) -> bool:
        return self.shortcut_ramp_to_platform

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring shortcut options for the scene...')
        room_dim = scene['roomDimensions']

        scene = self._add_bisecting_platform(scene, room_dim)
        scene = self._add_ramp_to_platform(scene, room_dim)
        return scene

    def _add_bisecting_platform(self, scene, room_dim):
        if self.get_shortcut_bisecting_platform():
            logger.trace("Adding bisecting platform shortcut")
            scene['objects'] = scene.get('objects', [])

            # Second platform is the wall to prevent performer from moving too
            # far before getting off the platform.  Since walls go to the
            # ceiling and platforms all start on the floor, we overlap this
            # platform.

            bounds = find_bounds(scene)
            performer_z = -room_dim['z'] / 2.0
            platform = StructuralPlatformConfig(
                num=1, position=VectorFloatConfig(0, 0.5, 0), rotation_y=0,
                scale=VectorFloatConfig(1, 1, room_dim['z']))
            blocking_wall_platform = StructuralPlatformConfig(
                num=1, position=VectorFloatConfig(0, 0, performer_z + 1.5),
                rotation_y=0,
                scale=VectorFloatConfig(0.99, 1.25, 0.1))
            scene['performerStart']['position'] = {
                'x': 0,
                'y': platform.scale.y,
                'z': (performer_z) + 0.5
            }

            struct_type = StructuralTypes.PLATFORMS
            # Nones are unneeded values
            add_structural_object_with_retries_or_throw(
                scene, bounds, MAX_TRIES, platform, struct_type, 0, None,
                None, None)
            add_structural_object_with_retries_or_throw(
                # Ignore the platform's bounds
                scene, bounds[:-1], MAX_TRIES, blocking_wall_platform,
                struct_type, 0, None,
                None, None)

        return scene

    def _add_ramp_to_platform(self, scene, room_dim):
        if not self.shortcut_ramp_to_platform:
            return scene
        logger.trace("Adding ramp to platform shortcut")
        scene['objects'] = scene.get('objects', [])
        num_prev_objs = len(scene['objects'])
        for _ in range(MAX_TRIES):
            try:
                bounds = find_bounds(scene)
                # need 2 copies of bounds since the two objects will overlap
                # intentionally and adding the ramp will alter the first copy
                bounds2 = find_bounds(scene)
                angle = random.randint(
                    self.RAMP_ANGLE_MIN, self.RAMP_ANGLE_MAX)
                radians = math.radians(angle)

                min_length = (
                    self.RAMP_TO_PLATFORM_MIN_HEIGHT) / math.tan(radians)
                max_length = (
                    (room_dim['y'] -
                     self.RAMP_TO_PLATFORM_MIN_DIST_TO_CEILING) /
                    math.tan(radians))

                ramp_config = StructuralRampConfig(
                    num=1,
                    angle=angle,
                    length=MinMaxFloat(min_length, max_length),
                    labels=['ramp_next_to_platform']
                )
                add_structural_object_with_retries_or_throw(
                    scene,
                    bounds,
                    MAX_TRIES,
                    ramp_config,
                    StructuralTypes.RAMPS,
                    0,
                    None,
                    None,
                    None)

                objs = scene['objects']
                ramp = objs[-1]
                show = ramp['shows'][0]
                # Figure out ramp rotation
                ramp_rot_y = show['rotation']['y']

                rpos = show['position']
                rscale = show['scale']
                ramp_width = rscale['x']

                platform_z = random.uniform(
                    self.RAMP_TO_PLATFORM_PLATFORM_LENGTH_MIN,
                    self.RAMP_TO_PLATFORM_PLATFORM_LENGTH_MAX)

                ramp_length = rscale['z']
                height = rscale['y']

                z_inc = (ramp_length + platform_z) / 2.0 * \
                    math.cos(math.radians(ramp_rot_y))
                x_inc = (ramp_length + platform_z) / 2.0 * \
                    math.sin(math.radians(ramp_rot_y))

                platform_scale = VectorFloatConfig(
                    ramp_width, height, platform_z)

                # Figure out position such that platform will be against
                # ramp
                platform_position = VectorFloatConfig(
                    rpos['x'] + x_inc, rpos['y'], rpos['z'] + z_inc)

                platform_config = StructuralPlatformConfig(
                    num=1,
                    material=ramp['materials'],
                    position=platform_position,
                    rotation_y=ramp_rot_y,
                    scale=platform_scale,
                    labels=['platform_next_to_ramp']
                )
                add_structural_object_with_retries_or_throw(
                    scene,
                    bounds2,
                    MAX_TRIES,
                    platform_config,
                    StructuralTypes.PLATFORMS,
                    0,
                    None,
                    None,
                    None)
                return scene
            except BaseException:
                # remove added objects on failure
                num_extra = len(scene['objects']) - num_prev_objs
                if num_extra > 0:
                    scene['objects'].pop(-1)
        raise ILEException("Failed to create ramp to platform")
