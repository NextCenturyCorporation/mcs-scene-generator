import logging
from typing import Any, Dict

from extremitypathfinder import PolygonEnvironment
from extremitypathfinder.plotting import PlottingEnvironment
from shapely.geometry import JOIN_STYLE, mapping

from generator import geometry, materials
from ideal_learning_env.decorators import ile_config_setter

from .components import ILEComponent
from .defs import ILEConfigurationException, ILEException
from .object_services import get_target_object

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
    that the performer would hit when their position is y = 0 or are light
    enough to be pushed.  The check also considers all holes and areas of lava
    in the scene. Pathfinding is only done in two dimensions. Check is skipped
    if false.
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

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        # Might be useful later but also helps with testing
        self.last_path = None
        self.last_distance = None
        if self.check_valid_path:
            logger.info('  Running path validation check...')

            environ = PlottingEnvironment(
                "./plots/") if self._debug_plot else PolygonEnvironment()

            tgt = get_target_object(scene)
            blocked_area = []
            if not tgt:
                raise ILEConfigurationException(
                    "Path check requires a goal target. "
                    "No goal target found.")

            start, end = self._compute_start_end(scene, tgt)
            boundary = self._compute_boundary(scene)

            # Add each different type
            # coordinates must be clockwise ordering
            self._add_objects_to_blocked(scene, tgt, blocked_area)
            self._add_lava_to_blocked(scene, blocked_area)
            self._add_holes_to_blocked(scene, blocked_area)
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

        return scene

    def _compute_start_end(self, scene, tgt):
        start = (
            scene["performerStart"]["position"]["x"],
            scene["performerStart"]["position"]["z"]
        )

        tgt_pos = tgt['shows'][0]['position']
        end = tgt_pos['x'], tgt_pos['z']
        return start, end

    def _compute_boundary(self, scene):
        dim = scene['roomDimensions']
        x = dim['x'] / 2.0 - geometry.PERFORMER_HALF_WIDTH
        y = dim['z'] / 2.0 - geometry.PERFORMER_HALF_WIDTH
        return [(-x, -y), (x, -y), (x, y), (-x, y)]

    def _add_objects_to_blocked(self, scene, tgt, blocked_area):
        objs = scene['objects'] or []
        buffer = geometry.PERFORMER_HALF_WIDTH
        for obj in objs:
            bb = obj['shows'][0]['boundingBox']
            valid_blocking_object = self.is_object_path_blocking(obj, tgt)
            # TODO MCS-895 We do not support multiple targets yet.
            if valid_blocking_object:
                # This creates a new polygon that is bigger by 'buffer' around
                # and the corners are beveled. (basically one cut diagnally on
                # the corner).  This expands the object by half the performer
                # so that we account for the performers width.
                #
                # Bevel is somewhat of an approximation, but using a more
                # accurate rounded corner results in more significant
                # performance penalties.
                buffered = bb.polygon_xz.buffer(
                    buffer, join_style=JOIN_STYLE.bevel,
                    resolution=1)

                coords = mapping(buffered)['coordinates'][0]
                blocked = list(coords)
                # removing because shapely repeats first coordinate, but
                # pathfinding doesn't want that.
                blocked.pop(-1)
                blocked_area.append(blocked)

    def _add_lava_to_blocked(self, scene, blocked_area):
        # To place the buffer exactly, we'd use 0.5 for the lava buffer.
        # Need to also account for performer width.
        lava_buffer = 0.5 + geometry.PERFORMER_HALF_WIDTH
        floor_text = scene.get('floorTextures', [])
        lava_mats = [mat.material for mat in materials.LAVA_MATERIALS]
        for floor in floor_text:
            if floor['material'] in lava_mats:
                for pos in floor['positions']:
                    blocked_area.append([
                        (pos["x"] - lava_buffer, pos["z"] - lava_buffer),
                        (pos["x"] - lava_buffer, pos["z"] + lava_buffer),
                        (pos["x"] + lava_buffer, pos["z"] + lava_buffer),
                        (pos["x"] + lava_buffer, pos["z"] - lava_buffer),
                    ])

    def _add_holes_to_blocked(self, scene, blocked_area):
        # Add holes, with a minor buffer.  The agent can walk
        # on the edge.
        holes = scene.get('holes', [])
        # should be 0.5 to be exactly hole, but then path library
        # thinks it can go between holes.
        hole_buffer = 0.6
        for hole in holes:
            blocked_area.append([
                (hole["x"] - hole_buffer, hole["z"] - hole_buffer),
                (hole["x"] - hole_buffer, hole["z"] + hole_buffer),
                (hole["x"] + hole_buffer, hole["z"] + hole_buffer),
                (hole["x"] + hole_buffer, hole["z"] - hole_buffer),
            ])

    def is_object_path_blocking(self, obj, tgt):
        show = obj['shows'][0]
        bb = show['boundingBox']
        # Don't add the target
        valid_blocking_object = obj['id'] != tgt['id']
        # Don't add objects that are above
        valid_blocking_object &= (bb.min_y < geometry.PERFORMER_HEIGHT or
                                  bb.max_y > self._step_height)
        # Don't add objects that are pushable

        valid_blocking_object &= obj['mass'] > geometry.PERFORMER_MASS
        return valid_blocking_object

    def get_check_valid_path(
            self) -> bool:
        return self.check_valid_path or False

    @ile_config_setter()
    def set_check_valid_path(self, data: Any) -> None:
        self.check_valid_path = data
