import logging
from typing import Any, Dict, List

from extremitypathfinder import PolygonEnvironment
from extremitypathfinder.plotting import PlottingEnvironment
from machine_common_sense.config_manager import Vector2dInt
from shapely.geometry import JOIN_STYLE, mapping

from generator import ObjectBounds, Scene, geometry

from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import ILEException
from .structural_object_service import (
    LABEL_BIDIRECTIONAL_RAMP,
    LABEL_CONNECTED_TO_RAMP,
    LABEL_PLATFORM,
    LABEL_RAMP
)

logger = logging.getLogger(__name__)


class ValidPathComponent(ILEComponent):
    """Validates that a 2D path exists on the ground to avoid lava, holes and
    unmovable objects.  This path does not take Ramps, performers starting
    elevation or any other methods of elevation change into account."""

    check_valid_path: bool = False
    """
    (bool): If true, checks for a valid path between the performer agent's
    starting position and the target's position and retries generating the
    current scene if one cannot be found. Considers all objects and structures
    that would block the performer when their position is y = 0 or are light
    enough to be pushed. The check considers all holes and areas of lava in the
    scene. It also considers moving up and/or down ramps that are attached to
    platforms (via the `attached_ramps` option in `structural_platforms`), as
    well as across those platforms. Pathfinding is otherwise only done in two
    dimensions. This check is skipped if false. Please note that this feature
    is not currently supported for scenes containing multiple targets.
    Default: False

    Simple Example:
    ```
    check_valid_path: false
    ```

    Advanced Example:
    ```
    check_valid_path: true
    ```
    """

    _step_height = 0.2
    _debug_plot = False
    _delayed_target = False
    _delayed_performer_start = False
    _delayed_error_reason = None

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

    # Override
    def update_ile_scene(self, scene: Scene) -> Scene:
        # Might be useful later but also helps with testing
        self.last_path = None
        self.last_distance = None

        if self.check_valid_path:
            self._delayed_target = self._no_target_found(scene)
            self._delayed_performer_start = self._performer_not_within_room(
                scene)

            if not self._delayed_target and not self._delayed_performer_start:
                self._find_valid_path(scene)
        return scene

    def _no_target_found(self, scene) -> bool:
        # Target placement may be delayed
        return len(scene.get_targets()) == 0

    def _performer_not_within_room(self, scene) -> bool:
        # shortcut_start_on_platform triggers a delayed action, placing
        # the performer outside of the room until an appropriate
        # platform is created/found to place them on
        bb_dim = {
            "x": geometry.PERFORMER_WIDTH,
            "y": geometry.PERFORMER_HEIGHT,
            "z": geometry.PERFORMER_WIDTH
        }

        perf_bb = geometry.create_bounds(
            dimensions=bb_dim,
            offset=None,
            position={
                "x": scene.performer_start.position.x,
                "y": scene.performer_start.position.y,
                "z": scene.performer_start.position.z
            },
            rotation={
                "x": scene.performer_start.rotation.x,
                "y": scene.performer_start.rotation.y,
                "z": scene.performer_start.rotation.z
            },
            standing_y=geometry.PERFORMER_HEIGHT
        )

        return not perf_bb.is_within_room({
            "x": scene.room_dimensions.x,
            "y": scene.room_dimensions.y,
            "z": scene.room_dimensions.z
        })

    def _find_valid_path(self, scene: Scene):
        if self.check_valid_path:
            logger.info('Running path validation check...')

            environ = PlottingEnvironment(
                "./plots/") if self._debug_plot else PolygonEnvironment()

            blocked_area = []
            if self._delayed_target:
                raise ILEException(
                    "Path check requires a goal target. "
                    "No goal target found.")

            if self._delayed_performer_start:
                raise ILEException(
                    "Performer start position is not within bounds.")

            # TODO This won't work in scenes with multiple targets.
            targets = scene.get_targets()
            if len(targets) > 1:
                raise ILEException(
                    f'The check_valid_path config option does not currently '
                    f'support scenes containing multiple targets (found '
                    f'{len(targets)} total targets)'
                )
            tgt = targets[0] if targets else None
            start, end = self._compute_start_end(scene, tgt)
            boundary = self._compute_boundary(scene)

            # Add each different type
            # coordinates must be clockwise ordering
            self._add_objects_to_blocked(scene, tgt, blocked_area)
            self._add_blocked_areas(scene.lava, blocked_area)
            # Buffer should be 0.5 to be exactly hole, but then path library
            # thinks it can go between holes.
            self._add_blocked_areas(scene.holes, blocked_area, 0.6)
            # validate

            logger.trace("Setting pathfinding environment")
            environ.store(
                boundary,
                list_of_hole_coordinates=blocked_area,
                validate=True)
            logger.trace("pre-computing possible paths")
            environ.prepare()
            logger.trace(
                "finding shortest path from performer start to target")
            try:
                # if plotting is off, path will be blank and distance will be 0
                self.last_path, self.last_distance = (
                    environ.find_shortest_path(start, end))
                if self.last_path == [] and self.last_distance is None:
                    raise ILEException("Failed to generate valid path")
                logger.debug(
                    f'Found path with distance {self.last_distance} using '
                    f'path {self.last_path}')
            # if plotting is on, no path will throw an exception.
            except Exception as e:
                raise ILEException("Failed to generate valid path") from e

    def _compute_start_end(self, scene, tgt):
        start = (
            scene.performer_start.position.x,
            scene.performer_start.position.z
        )

        tgt_pos = tgt['shows'][0]['position']
        end = tgt_pos['x'], tgt_pos['z']
        return start, end

    def _compute_boundary(self, scene):
        dim = scene.room_dimensions
        x = dim.x / 2.0 - geometry.PERFORMER_HALF_WIDTH
        y = dim.z / 2.0 - geometry.PERFORMER_HALF_WIDTH
        return [(-x, -y), (x, -y), (x, y), (-x, y)]

    def _is_ramp_with_path(self, obj):
        if (obj and obj["debug"] and "labels" in obj["debug"]):
            labels = obj["debug"]["labels"]
            if (LABEL_RAMP in labels and
               LABEL_BIDIRECTIONAL_RAMP in labels):
                return True

        return False

    def _is_platform_with_path(self, obj):
        if (obj and obj["debug"] and "labels" in obj["debug"]):
            labels = obj["debug"]["labels"]
            if (LABEL_PLATFORM in labels and
               LABEL_CONNECTED_TO_RAMP in labels):
                return True
        return False

    def _calc_ramp_blocked_areas(self, obj):
        ramp_pos = obj["shows"][0]["position"]
        ramp_rot = obj["shows"][0]["rotation"]
        ramp_scale = obj["shows"][0]["scale"]
        bb_width = 0.1

        bb_dim = {
            "x": bb_width,
            "y": 1.0,
            "z": ramp_scale["z"] + bb_width +
            geometry.PERFORMER_HALF_WIDTH}
        offset_left = {
            "x": -((ramp_scale["x"] / 2.0) + (bb_width / 2)),
            "y": 0.0,
            "z": -geometry.PERFORMER_HALF_WIDTH
        }
        offset_right = {
            "x": ((ramp_scale["x"] / 2.0) + (bb_width / 2)),
            "y": 0.0,
            "z": -geometry.PERFORMER_HALF_WIDTH
        }

        left_bb = geometry.create_bounds(
            bb_dim, offset_left, ramp_pos, ramp_rot, 0.0)
        right_bb = geometry.create_bounds(
            bb_dim, offset_right, ramp_pos, ramp_rot, 0.0)

        return left_bb, right_bb

    def _get_platform_side(self, platform, bounds_list, side,
                           scale_multiplier, offset_value):
        plat_pos = platform["shows"][0]["position"]
        plat_rot = platform["shows"][0]["rotation"]
        gaps = platform["debug"]["gaps"]
        isFrontBack = side in ["front", "back"]
        bb_width = 0.1
        if (gaps.get(side) is not None):
            count = 0
            max = len(gaps[side])

            # Adapted from ai2thor code (PositionLips() in StructureObject.cs)
            while count < (max + 1):
                start = 0 if count == 0 else gaps[side][count - 1]["high"]
                end = gaps[side][count]["low"] if count != max else 1

                start -= 0.5
                end -= 0.5

                scale = (end - start) * scale_multiplier
                pos = (start + end) / 2.0 * scale_multiplier

                bb_dim_x = scale if isFrontBack else bb_width
                bb_dim_z = bb_width if isFrontBack else scale

                offset_x = pos if isFrontBack else offset_value
                offset_z = offset_value if isFrontBack else pos

                bb_dim = {
                    "x": bb_dim_x,
                    "y": 0.0,
                    "z": bb_dim_z
                }
                offset = {
                    "x": offset_x,
                    "y": 0.0,
                    "z": offset_z
                }

                bb = geometry.create_bounds(
                    bb_dim, offset, plat_pos, plat_rot, 0.0)

                bounds_list.append(bb)

                count += 1
        else:

            bb_dim = {
                "x": scale_multiplier if isFrontBack else bb_width,
                "y": 0.0,
                "z": bb_width if isFrontBack else scale_multiplier
            }

            offset_x = 0.0 if isFrontBack else offset_value
            offset_z = offset_value if isFrontBack else 0.0
            offset = {
                "x": offset_x,
                "y": 0.0,
                "z": offset_z
            }

            bounds_list.append(geometry.create_bounds(
                bb_dim, offset, plat_pos, plat_rot, 0.0))

    def _get_platform_edges(self, obj) -> List[ObjectBounds]:
        plat_scale = obj["shows"][0]["scale"]
        bounds_list = []

        half_scale_x = (plat_scale["x"] / 2.0)
        half_scale_z = (plat_scale["z"] / 2.0)

        self._get_platform_side(
            obj, bounds_list, "left", plat_scale["z"], -half_scale_x
        )

        self._get_platform_side(
            obj, bounds_list, "right", plat_scale["z"], half_scale_x
        )

        # Note that front/back are reversed (may be left as is
        # due to invalidating already released scenes)
        self._get_platform_side(
            obj, bounds_list, "front", plat_scale["x"], -half_scale_z
        )

        self._get_platform_side(
            obj, bounds_list, "back", plat_scale["x"], half_scale_z
        )

        return bounds_list

    def _add_objects_to_blocked(self, scene, tgt, blocked_area):
        objs = scene.objects or []
        default_buffer = geometry.PERFORMER_HALF_WIDTH
        plat_ramp_buffer = 0.1
        for obj in objs:
            valid_ramp = self._is_ramp_with_path(obj)
            valid_platform = self._is_platform_with_path(obj)

            if valid_ramp:
                left_bb, right_bb = self._calc_ramp_blocked_areas(obj)

                self._add_polygon_to_blocked(
                    left_bb, plat_ramp_buffer, blocked_area)
                self._add_polygon_to_blocked(
                    right_bb, plat_ramp_buffer, blocked_area)

            elif valid_platform:
                # Note that this does not handle bisecting platforms
                sides = self._get_platform_edges(obj)

                for side in sides:
                    self._add_polygon_to_blocked(
                        side, plat_ramp_buffer, blocked_area)

            else:
                bb = obj['shows'][0]['boundingBox']

                valid_blocking_object = self.is_object_path_blocking(obj, tgt)
                # TODO MCS-895 We do not support multiple targets yet.
                if valid_blocking_object:
                    self._add_polygon_to_blocked(bb, default_buffer,
                                                 blocked_area)

    def _add_polygon_to_blocked(self, bounding_box, buffer, blocked_area):
        # This creates a new polygon that is bigger by 'buffer'
        # around and the corners are beveled. (basically one cut
        # diagnally on the corner).  This expands the object by
        # half the performer so that we account for the performers
        # width.
        #
        # Bevel is somewhat of an approximation, but using a more
        # accurate rounded corner results in more significant
        # performance penalties.
        buffered = bounding_box.polygon_xz.buffer(
            buffer, join_style=JOIN_STYLE.bevel,
            resolution=1)

        coords = mapping(buffered)['coordinates'][0]
        blocked = list(coords)
        # removing because shapely repeats first coordinate, but
        # pathfinding doesn't want that.
        blocked.pop(-1)
        blocked_area.append(blocked)

    def _add_blocked_areas(
        self,
        areas: List[Vector2dInt],
        blocked_area: list,
        area_buffer: float = 0.5 + geometry.PERFORMER_HALF_WIDTH
    ) -> None:
        for area in areas:
            blocked_area.append([
                (area.x - area_buffer, area.z - area_buffer),
                (area.x - area_buffer, area.z + area_buffer),
                (area.x + area_buffer, area.z + area_buffer),
                (area.x + area_buffer, area.z - area_buffer)
            ])

    def is_object_path_blocking(self, obj, tgt):
        if tgt.get('associatedWithAgent') == obj['id']:
            return False

        show = obj['shows'][0]
        bb = show['boundingBox']
        # Don't add the target
        valid_blocking_object = obj['id'] != tgt['id']
        # Don't add objects that are above

        valid_blocking_object &= (bb.min_y < geometry.PERFORMER_HEIGHT or
                                  bb.max_y > self._step_height)
        # Don't add objects that are pushable
        # If no mass found, then assume object is blocking
        mass = geometry.PERFORMER_MASS + \
            1 if 'mass' not in obj else obj['mass']
        valid_blocking_object &= mass > geometry.PERFORMER_MASS
        return valid_blocking_object

    def get_num_delayed_actions(self) -> int:
        delay = self._delayed_target or self._delayed_performer_start
        no_valid_path = self.last_path == [] and self.last_distance is None

        return 1 if (delay or no_valid_path) else 0

    def run_delayed_actions(self, scene: Scene) -> Scene:
        delay = self._delayed_target or self._delayed_performer_start
        no_valid_path = (self.last_path == [] and
                         self.last_distance is None)
        if delay or no_valid_path:
            try:
                self._delayed_target = self._no_target_found(scene)
                self._delayed_performer_start = self._performer_not_within_room(scene)  # noqa: E501
                self._find_valid_path(scene)
            except Exception as e:
                self._delayed_error_reason = e
                self.last_path = []
                self.last_distance = None
        return scene

    def get_delayed_action_error_strings(self) -> List[str]:
        return [str(self._delayed_error_reason)
                ] if self._delayed_error_reason else []

    def get_check_valid_path(
            self) -> bool:
        return self.check_valid_path or False

    @ile_config_setter()
    def set_check_valid_path(self, data: Any) -> None:
        self.check_valid_path = data
