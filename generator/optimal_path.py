import logging
import math
from typing import Any, Dict, List, Optional, Tuple

from extremitypathfinder import plotting
from extremitypathfinder.extremitypathfinder import (
    PolygonEnvironment as Environment,
)
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from .exceptions import SceneException
from .geometry import (
    DEFAULT_ROOM_DIMENSIONS,
    MAX_REACH_DISTANCE,
    MOVE_DISTANCE,
    PERFORMER_CAMERA_Y,
    PERFORMER_HALF_WIDTH,
)

plotting.EXPORT_SIZE_X = plotting.EXPORT_SIZE_Y


VARIANCE = 0.01


class ShortestPath():
    def __init__(
        self,
        action_list: List[Dict[str, Any]],
        position: Tuple[float, float],
        rotation: float
    ):
        self.action_list = action_list
        self.position = position
        self.rotation = rotation


def _dilate_and_unify_object_bounds(
    object_bounds_list: List[List[Dict[str, float]]],
    dilation_amount: float,
    source: Tuple[float, float] = None,
    target: Tuple[float, float] = None
) -> Optional[List[Polygon]]:
    """Dilate the given object bounds by the given amount and return the
    resulting coordinates. Fall back to the original bounds if the new bounds
    would overlap the given source or target point."""
    source_point = Point(source) if source else None
    target_point = Point(target) if target else None

    # Expand the rects by the dilation into bigger polys with 8 points.
    poly_list = []
    for bounds in object_bounds_list:
        poly = Polygon([(point['x'], point['z']) for point in bounds])
        logging.debug(f'original poly {poly}')
        modified_poly = poly.buffer(dilation_amount, resolution=1, cap_style=3)
        logging.debug(f'modified poly {modified_poly}')
        # Use original poly if dilation would overlap with source/target.
        if ((
            source and not poly.contains(source_point) and
            modified_poly.contains(source_point)
        ) or (
            target and not poly.contains(target_point) and
            modified_poly.contains(target_point)
        )):
            poly_list.append(poly)
        else:
            poly_list.append(modified_poly)

    # Merge any intersecting polys.
    merged_poly_list = (
        unary_union(poly_list) if len(poly_list) > 1 else poly_list
    )
    if isinstance(merged_poly_list, Polygon):
        merged_poly_list = [merged_poly_list]

    poly_coords_list = [
        list(poly.exterior.coords) for poly in merged_poly_list
    ]
    # The polys returned by unary_union have the same first and last point,
    # but the shortest path code doesn't want them to have the repeated point.
    for coords in poly_coords_list:
        if coords[0] == coords[-1]:
            del coords[-1]

    return poly_coords_list


def _dilate_target_bounds(
    target_bounds: List[Dict[str, float]]
) -> List[Dict[str, float]]:
    """Dilate the given target bounds and return the resulting coordinates."""
    # Dilate the bounds to account for the performer's reach distance.
    # The resulting polygon should always have eight points.
    coords = _dilate_and_unify_object_bounds(
        [target_bounds],
        MAX_REACH_DISTANCE - VARIANCE
    )[0]
    # Identify if the first two points are a (short) corner or a (long) side.
    distance_1 = Point(coords[0]).distance(Point(coords[1]))
    distance_2 = Point(coords[1]).distance(Point(coords[2]))
    # Add the center points of each of the target's original four sides.
    if distance_1 < distance_2:
        coords.insert(0, coords.pop())
    for i, j in [(6, 7), (4, 5), (2, 3), (0, 1)]:
        center = LineString([coords[i], coords[j]]).centroid.coords[0]
        coords.insert(j, center)
    return coords


def _find_target_or_parent_dict(
    target_object: Dict[str, Any],
    object_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Find and return the target object dict from the given object list."""
    logging.debug('target {target_object}')
    if 'locationParent' in target_object:
        parent_object = [
            object_dict for object_dict in object_list
            if object_dict['id'] == target_object['locationParent']
        ][0]
        if parent_object is None:
            raise SceneException(
                f'target should have parent {target_object}')
        logging.debug('parent {parent_object}')
        return parent_object
    return target_object


def _generate_path_list(
    previous_path: ShortestPath,
    next_position_list: List[Tuple[float, float]],
    target_position: Tuple[float, float],
    pathfinding_environment: Environment
) -> List[ShortestPath]:
    """Generate and return lists of MCS actions that each may be the shortest
    path to the given target position. First generate MCS rotate and move
    actions to the first element in the given position list, then regenerate
    the shortest path from that position to the target position, and then
    call recursively."""
    logging.debug('----------------------------------------')
    if len(next_position_list) == 0:
        return [previous_path]

    # Generate the MCS rotate and move actions toward just the next position.
    next_path_list = _rotate_then_move(previous_path, next_position_list[0])

    output_path_list = []
    for path in next_path_list:
        logging.debug(f'next path action list length {len(path.action_list)}')
        logging.debug(f'next path position {path.position}')
        logging.debug(f'next path rotation {path.rotation}')
        # If the next part of the path didn't have a change in position...
        if previous_path.position == path.position:
            logging.debug('Path Done: is same position as previous path')
            output_path_list.append(path)
            continue
        # If the next position was near enough to the target position...
        if (
            math.isclose(target_position[0], next_position_list[0][0]) and
            math.isclose(target_position[1], next_position_list[0][1])
        ):
            logging.debug('Path Done: is at target position')
            output_path_list.append(path)
            continue
        # Else generate the path to the NEXT position.
        position_list = _generate_shortest_path_position_list(
            path.position,
            target_position,
            pathfinding_environment
        )
        if position_list:
            output_path_list.extend(_generate_path_list(
                path,
                position_list[1:],
                target_position,
                pathfinding_environment
            ))
    return output_path_list


def _generate_pathfinding_environment(
    room_dimensions: Dict[str, float],
    object_bounds_list: List[List[Dict[str, float]]],
    source: Dict[str, float] = None,
    target: Dict[str, float] = None,
    save_path_plot_with_name: str = None
) -> Optional[Environment]:
    """Generate and return the pathfinding environment using the given list of
    object bounds and the global room bounds. Save plots of the paths to the
    local drive if save_path_plot_with_name is not None."""
    poly_coords_list = _dilate_and_unify_object_bounds(
        object_bounds_list,
        ((PERFORMER_HALF_WIDTH + VARIANCE)),
        (source['x'], source['z']) if source else None,
        (target['x'], target['z']) if target else None
    )
    logging.debug(f'poly coords list {poly_coords_list}')

    pathfinding_environment = (
        plotting.PlottingEnvironment(plotting_dir=save_path_plot_with_name)
        if save_path_plot_with_name else Environment()
    )
    room_max_x = (room_dimensions['x'] / 2.0) - PERFORMER_HALF_WIDTH
    room_max_z = (room_dimensions['z'] / 2.0) - PERFORMER_HALF_WIDTH
    room_bounds = [
        (room_max_x - VARIANCE, room_max_z - VARIANCE),
        (-room_max_x + VARIANCE, room_max_z - VARIANCE),
        (-room_max_x + VARIANCE, -room_max_z + VARIANCE),
        (room_max_x - VARIANCE, -room_max_z + VARIANCE)
    ]
    logging.debug(f'room bounds {room_bounds}')
    try:
        pathfinding_environment.store(
            room_bounds,
            poly_coords_list,
            validate=True
        )
        pathfinding_environment.prepare()
    except Exception as e:
        logging.error('UNEXPECTED ERROR IN ENVIRONMENT')
        logging.error(e)
        return None
    return pathfinding_environment


def _generate_shortest_path_position_list(
    starting_position: Tuple[float, float],
    goal_position: Tuple[float, float],
    pathfinding_environment: Environment
) -> Optional[List[Tuple[float, float]]]:
    """Generate and return the postion list for the shortest path from the
    given starting position to the given goal position."""
    try:
        if not pathfinding_environment.within_map(starting_position):
            logging.debug('Starting position not in pathfinding environment.')
            return None
        if not pathfinding_environment.within_map(goal_position):
            logging.debug('Goal position not in pathfinding environment.')
            return None
        path, length = pathfinding_environment.find_shortest_path(
            starting_position,
            goal_position
        )
    except Exception as e:
        logging.error('UNEXPECTED ERROR IN PATHFINDING')
        logging.error(e)
        return None
    return path if len(path) > 0 else None


def _remove_duplicate_paths(
    path_list: List[ShortestPath]
) -> List[ShortestPath]:
    """Remove each duplicated path from the given list and return a new path
    list."""
    # Map each unique path to its stringified action list.
    unique_path = {}
    for path in path_list:
        # Stringify the path's MCS action list.
        text_action_list = []
        for action_data in path.action_list:
            text_action = action_data['action']
            for key, value in action_data['params'].items():
                text_action += ',' + key + '=' + value
            text_action_list.append(text_action)
        text = ';'.join(text_action_list)
        if text not in unique_path:
            unique_path[text] = path
    return list(unique_path.values())


def _rotate_then_move(
    path: ShortestPath,
    next_position: Tuple[float, float],
    single_best_path: bool = False
) -> List[ShortestPath]:
    """Returns new paths based on the given path that rotates and/or moves to
    the given next position."""
    if (
        math.isclose(path.position[0], next_position[0]) and
        math.isclose(path.position[1], next_position[1])
    ):
        return [path]

    # Find the degree difference from the path's rotation to the next position.
    dx = next_position[0] - path.position[0]
    dz = next_position[1] - path.position[1]
    theta = math.degrees(math.atan2(dz, dx))
    logging.debug(f'path position {path.position}')
    logging.debug(f'path rotation {path.rotation}')
    logging.debug(f'next position {next_position}')
    logging.debug(f'theta {theta}')

    delta = (path.rotation - theta) % 360
    if delta > 180:
        delta -= 360
    rotate_left = (delta < 0)
    logging.debug(f'delta {delta}')

    # Find how many individual rotate actions are needed.
    remainder, count = math.modf(abs(delta) / 10.0)
    count = int(count)
    rotate_list = [count] if remainder == 0 else [count, count + 1]
    if single_best_path:
        rotate_list = [rotate_list[-1]]
    elif remainder != 0:
        # Try a few other rotations to handle some edge cases.
        if remainder <= 0.2:
            rotate_list.append(count - 1)
        if remainder >= 0.8:
            rotate_list.append(count + 2)

    # Create a new path for each rotation amount.
    intermediate_path_list = []
    for amount in rotate_list:
        intermediate_path_list.append(ShortestPath(path.action_list.copy() + [{
            'action': 'RotateLeft' if rotate_left else 'RotateRight',
            "params": {}
        }] * amount, path.position, (
            path.rotation - ((-10 if rotate_left else 10) * amount)
        )))

    # Find the move distance from the path's position to the next position.
    distance = math.sqrt(dx ** 2 + dz ** 2)
    logging.debug(f'distance {distance}')

    # Find how many individual move actions are needed.
    remainder, count = math.modf(distance / MOVE_DISTANCE)
    count = int(count)
    move_list = [count] if remainder == 0 else [count, count + 1]
    if single_best_path:
        move_list = [move_list[-1]]

    # Create a new path for each movement amount.
    output_path_list = []
    for path in intermediate_path_list:
        x_increment = MOVE_DISTANCE * math.cos(math.radians(path.rotation))
        z_increment = MOVE_DISTANCE * math.sin(math.radians(path.rotation))
        for amount in move_list:
            output_path_list.append(ShortestPath(path.action_list.copy() + [{
                "action": "MoveAhead",
                "params": {}
            }] * amount, (
                path.position[0] + x_increment * amount,
                path.position[1] + z_increment * amount
            ), path.rotation))

    # Return len(rotate_list) * len(move_list) paths (unless single_best_path).
    return output_path_list


def find_possible_best_path_list(
    room_dimensions: Optional[Dict[str, float]],
    performer_start: Dict[str, Any],
    target_dict: Dict[str, Any],
    object_list: List[Dict[str, Any]],
    save_path_plot_with_name: str = None
) -> Tuple[List[ShortestPath]]:
    """Find and return lists of MCS actions that each may be the shortest path
    to the target object with the given ID. Because rotate and move actions
    are rounded, try many paths with rotations and movements of varying
    amounts."""
    target_or_parent_dict = _find_target_or_parent_dict(
        target_dict,
        object_list
    )

    object_bounds_list = [
        object_dict['shows'][0]['boundingBox'] for object_dict in object_list
        if object_dict['id'] != target_or_parent_dict['id'] and
        'locationParent' not in object_dict
    ]
    logging.debug(f'object bounds list {object_bounds_list}')

    target_coords = _dilate_target_bounds(
        target_or_parent_dict['shows'][0]['boundingBox']
    )
    logging.debug(f'target coords {target_coords}')

    pathfinding_environment = _generate_pathfinding_environment(
        room_dimensions or DEFAULT_ROOM_DIMENSIONS,
        object_bounds_list,
        performer_start['position'],
        target_or_parent_dict['shows'][0]['position'],
        save_path_plot_with_name
    )
    if pathfinding_environment is None:
        logging.error('Cannot create pathfinding environment!')
        return None

    # Create the base path from the performer start position/rotation.
    # Note that shapely expects 0=east and 90=north but in MCS it's switched.
    base_path = ShortestPath([], (
        performer_start['position']['x'],
        performer_start['position']['z']
    ), (90 - performer_start['rotation']['y']))

    best_path_list = []
    for target in target_coords:
        logging.debug('========================================')
        logging.debug(f'target {target}')
        # Generate the position list for the shortest path to the target point.
        position_list = _generate_shortest_path_position_list(
            base_path.position,
            target,
            pathfinding_environment
        )
        logging.debug(f'position list {position_list}')
        if not position_list:
            logging.debug(f'Cannot find path to target corner {target}')
            continue
        # Generate a path of MCS actions for the shortest path's position list.
        path_list = _generate_path_list(
            base_path,
            position_list[1:],
            target,
            pathfinding_environment
        )
        logging.debug('path list length {len(path_list)}')
        # Add one more set of rotate and move actions to each path.
        best_path_list.extend([_rotate_then_move(path, (
            target_or_parent_dict['shows'][0]['position']['x'],
            target_or_parent_dict['shows'][0]['position']['z']
        ), single_best_path=True)[0] for path in path_list])

    unique_path_list = _remove_duplicate_paths(best_path_list)
    logging.debug('output path list length {len(uniqe_path_list)}')
    return sorted(unique_path_list, key=lambda path: len(path.action_list))


def look_at_target(
    path: ShortestPath,
    target_position: Tuple[float, float],
    target_height: float
) -> None:
    """Update the given path to look down at the target with the given position
    and height."""
    grid_distance = math.sqrt(
        (target_position[0] - path.position[0]) ** 2 +
        (target_position[1] - path.position[1]) ** 2
    )
    height_distance = PERFORMER_CAMERA_Y - target_height
    difference = math.degrees(math.atan2(height_distance, grid_distance))
    while difference > 5:
        path.action_list.append({
            'action': 'LookDown',
            'params': {}
        })
        difference -= 10


def open_container_and_pickup_target(
    path: ShortestPath,
    target_id: str,
    container_dict: Dict[str, Any]
) -> None:
    """Update the given path to open the container with the given data and
    pickup the target with the given ID."""
    path.action_list.append({
        'action': 'OpenObject',
        'params': {
            'objectId': container_dict['id']
        }
    })
    pickup_target(path, target_id)


def pickup_target(
    path: ShortestPath,
    target_id: str
) -> None:
    """Update the given path to pickup the target with the given ID."""
    path.action_list.append({
        'action': 'PickupObject',
        'params': {
            'objectId': target_id
        }
    })
