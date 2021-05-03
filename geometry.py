import logging
import math
import random
from typing import List, Dict, Any, Optional, Callable, Tuple

import shapely
from shapely import affinity
from shapely import geometry

import util
from separating_axis_theorem import sat_entry

PERFORMER_MASS = 2

POSITION_DIGITS = 2
VALID_ROTATIONS = (0, 45, 90, 135, 180, 225, 270, 315)

# Add or subtract the performer width to ensure it can move behind any object.
ROOM_X_MIN = -5 + util.PERFORMER_HALF_WIDTH
ROOM_Z_MIN = -5 + util.PERFORMER_HALF_WIDTH
ROOM_X_MAX = 5 - util.PERFORMER_HALF_WIDTH
ROOM_Z_MAX = 5 - util.PERFORMER_HALF_WIDTH

MAX_OBJECTS_ADJACENT_DISTANCE = 0.5
MIN_OBJECTS_SEPARATION_DISTANCE = 2
MIN_FORWARD_VISIBILITY_DISTANCE = 1.25
MIN_GAP = 0.1

ORIGIN = {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0
}

ORIGIN_LOCATION = {
    'position': {
        'x': 0.0,
        'y': 0.0,
        'z': 0.0
    },
    'rotation': {
        'x': 0.0,
        'y': 0.0,
        'z': 0.0
    }
}


def random_position_x() -> float:
    return round(random.uniform(ROOM_X_MIN, ROOM_X_MAX), POSITION_DIGITS)


def random_position_z() -> float:
    return round(random.uniform(ROOM_Z_MIN, ROOM_Z_MAX), POSITION_DIGITS)


def random_rotation() -> float:
    return random.choice(VALID_ROTATIONS)


def dot_prod_dict(v1: Dict[Any, float], v2: Dict[Any, float]) -> float:
    return sum(v1[key] * v2.get(key, 0) for key in v1)


def collision(test_rect: List[Dict[str, float]], test_point: Dict[str, float]):
    # assuming test_rect is an array4 points in order... Clockwise or CCW does
    # not matter
    # points are {x,y,z}
    #
    # From https://math.stackexchange.com/a/190373
    A = test_rect[0]
    B = test_rect[1]
    C = test_rect[2]

    vectorAB = {
        'x': B['x'] - A['x'],
        'y': B['y'] - A['y'],
        'z': B['z'] - A['z']}
    vectorBC = {
        'x': C['x'] - B['x'],
        'y': C['y'] - B['y'],
        'z': C['z'] - B['z']}

    vectorAM = {
        'x': test_point['x'] - A['x'],
        'y': test_point['y'] - A['y'],
        'z': test_point['z'] - A['z']}
    vectorBM = {
        'x': test_point['x'] - B['x'],
        'y': test_point['y'] - B['y'],
        'z': test_point['z'] - B['z']}

    return (
        0 <=
        dot_prod_dict(vectorAB, vectorAM) <=
        dot_prod_dict(vectorAB, vectorAB)
    ) & (
        0 <=
        dot_prod_dict(vectorBC, vectorBM) <=
        dot_prod_dict(vectorBC, vectorBC)
    )


def calc_obj_coords(position_x: float, position_z: float, delta_x: float,
                    delta_z: float, offset_x: float,
                    offset_z: float, rotation: float) \
        -> List[Dict[str, float]]:
    """Returns an array of points that are the coordinates of the
    rectangle """
    radian_amount = math.pi * (2 - rotation / 180.0)

    rotate_sin = math.sin(radian_amount)
    rotate_cos = math.cos(radian_amount)
    x_plus = delta_x + offset_x
    x_minus = -delta_x + offset_x
    z_plus = delta_z + offset_z
    z_minus = -delta_z + offset_z

    a = {'x': position_x + x_plus * rotate_cos - z_plus * rotate_sin,
         'y': 0, 'z': position_z + x_plus * rotate_sin + z_plus * rotate_cos}
    b = {'x': position_x + x_plus * rotate_cos - z_minus * rotate_sin,
         'y': 0, 'z': position_z + x_plus * rotate_sin + z_minus * rotate_cos}
    c = {'x': position_x + x_minus * rotate_cos - z_minus * rotate_sin,
         'y': 0, 'z': position_z + x_minus * rotate_sin + z_minus * rotate_cos}
    d = {'x': position_x + x_minus * rotate_cos - z_plus * rotate_sin,
         'y': 0, 'z': position_z + x_minus * rotate_sin + z_plus * rotate_cos}

    return [a, b, c, d]


def point_within_room(point: Dict[str, float]) -> bool:
    return (
        ROOM_X_MIN <= point['x'] <= ROOM_X_MAX and
        ROOM_Z_MIN <= point['z'] <= ROOM_Z_MAX
    )


def rect_within_room(rect: List[Dict[str, float]]) -> bool:
    """Return True iff the passed rectangle is entirely within the bounds of
    the room."""
    return all(point_within_room(point) for point in rect)


def calc_obj_pos(
    performer_position: Dict[str, float],
    other_rects: List[List[Dict[str, float]]],
    definition_or_instance: Dict[str, Any],
    x_func: Callable[[], float] = random_position_x,
    z_func: Callable[[], float] = random_position_z,
    rotation_func: Callable[[], float] = random_rotation,
    xz_func: Callable[[], Tuple[float, float]] = None
) -> Optional[Dict[str, Any]]:
    """Returns new object with rotation & position if we can place the
    object in the frame, None otherwise."""

    dx = definition_or_instance['dimensions']['x'] / 2.0
    dz = definition_or_instance['dimensions']['z'] / 2.0
    if 'offset' in definition_or_instance:
        offset_x = definition_or_instance['offset']['x']
        offset_z = definition_or_instance['offset']['z']
    else:
        offset_x = 0.0
        offset_z = 0.0

    tries = 0
    while tries < util.MAX_TRIES:
        rotation = definition_or_instance.get('rotation', {})
        rotation_x = rotation.get('x', 0)
        rotation_y = rotation.get('y', 0) + rotation_func()
        rotation_z = rotation.get('z', 0)
        if xz_func is not None:
            new_x, new_z = xz_func()
        else:
            new_x = x_func()
            new_z = z_func()

        if new_x is not None and new_z is not None:
            rect = calc_obj_coords(
                new_x, new_z, dx, dz, offset_x, offset_z, rotation_y)
            if validate_location_rect(rect, performer_position, other_rects):
                break
        tries += 1

    if tries < util.MAX_TRIES:
        new_object = {
            'rotation': {'x': rotation_x, 'y': rotation_y, 'z': rotation_z},
            'position': {
                'x': new_x,
                'y': definition_or_instance.get('positionY', 0),
                'z': new_z
            },
            'boundingBox': rect
        }
        other_rects.append(rect)
        return new_object

    logging.debug(f'could not place object: {definition_or_instance}')
    return None


def position_distance(a: Dict[str, float], b: Dict[str, float]) -> float:
    """Compute the distance between two positions."""
    return math.sqrt((a['x'] - b['x'])**2 + (a['y'] -
                                             b['y'])**2 + (a['z'] - b['z'])**2)


def get_room_box() -> geometry.Polygon:
    room = geometry.box(ROOM_X_MIN, ROOM_Z_MIN, ROOM_X_MAX, ROOM_Z_MAX)
    return room


def get_visible_segment(performer_start: Dict[str, Dict[str, float]]) \
        -> geometry.LineString:
    """Get a line segment that should be visible to the performer
    (straight ahead and at least MIN_FORWARD_VISIBILITY_DISTANCE but within
    the room). Return None if no visible segment is possible.
    """
    max_dimension = max(ROOM_X_MAX - ROOM_X_MIN, ROOM_Z_MAX - ROOM_Z_MIN)
    # make it long enough for the far end to be outside the room
    view_segment = geometry.LineString(
        [[0, MIN_FORWARD_VISIBILITY_DISTANCE], [0, max_dimension * 2]])
    view_segment = affinity.rotate(
        view_segment, -performer_start['rotation']['y'], origin=(0, 0))
    view_segment = affinity.translate(
        view_segment,
        performer_start['position']['x'],
        performer_start['position']['z']
    )
    room = get_room_box()

    target_segment = room.intersection(view_segment)
    if target_segment.is_empty:
        logging.debug(
            f'performer too close to the wall, cannot place object in front '
            f'of it (performer location={performer_start})')
        return None
    return target_segment


def get_location_in_front_of_performer(
    performer_start: Dict[str, Dict[str, float]],
    target_definition_or_instance: Dict[str, Any],
    rotation_func: Callable[[], float] = random_rotation
) -> Optional[Dict[str, Any]]:
    visible_segment = get_visible_segment(performer_start)
    if not visible_segment:
        return None

    def segment_xz():
        fraction = random.random()
        point = visible_segment.interpolate(fraction, normalized=True)
        return point.x, point.y

    return calc_obj_pos(
        performer_start['position'],
        [],
        target_definition_or_instance,
        xz_func=segment_xz,
        rotation_func=rotation_func
    )


def get_location_in_back_of_performer(
    performer_start: Dict[str, Dict[str, float]],
    target_definition_or_instance: Dict[str, Any],
    rotation_func: Callable[[], float] = random_rotation
) -> Optional[Dict[str, Any]]:
    offset = target_definition_or_instance.get('offset', {'x': 0, 'z': 0})
    # We may rotate the object so use its larger X/Z size.
    object_half_size = max(
        target_definition_or_instance['dimensions']['x'] / 2.0 - offset['x'],
        target_definition_or_instance['dimensions']['z'] / 2.0 - offset['z']
    )

    # Find the part of the room that's behind the performer's start location
    # (the 180 degree arc in the opposite direction from its start rotation).
    # If the performer would start at (0, 0) facing north (its rotation is 0),
    # its rear poly would then be: minx, miny, maxx, maxy
    rear_poly = geometry.box(
        -(ROOM_X_MAX - ROOM_X_MIN),
        -(ROOM_Z_MAX - ROOM_Z_MIN),
        (ROOM_X_MAX - ROOM_X_MIN),
        -0.5 - object_half_size
    )
    # Move the rear poly to behind the performer's start location.
    performer_point = geometry.Point(
        performer_start['position']['x'],
        performer_start['position']['z']
    )
    rear_poly = affinity.translate(
        rear_poly,
        performer_point.x,
        performer_point.y
    )
    # Rotate the rear poly based on the performer's start rotation.
    rear_poly = affinity.rotate(
        rear_poly,
        -performer_start['rotation']['y'],
        origin=performer_point
    )
    # Restrict the rear poly to the room's dimensions.
    room_poly = geometry.box(
        ROOM_X_MIN + object_half_size,
        ROOM_Z_MIN + object_half_size,
        ROOM_X_MAX - object_half_size,
        ROOM_Z_MAX - object_half_size
    )
    rear_poly = rear_poly.intersection(room_poly)

    if not rear_poly or rear_poly.is_empty:
        return None

    rear_min_x = min(ROOM_X_MAX, max(ROOM_X_MIN, rear_poly.bounds[0]))
    rear_max_x = min(ROOM_X_MAX, max(ROOM_X_MIN, rear_poly.bounds[2]))
    rear_min_z = min(ROOM_Z_MAX, max(ROOM_Z_MIN, rear_poly.bounds[1]))
    rear_max_z = min(ROOM_Z_MAX, max(ROOM_Z_MIN, rear_poly.bounds[3]))

    def compute_xz():
        for _ in range(util.MAX_TRIES):
            # Try choosing a random X within the rear X bounds.
            x = util.random_real(rear_min_x, rear_max_x)
            # Draw a vertical line with that X within the rear Z bounds.
            vertical_line = geometry.LineString(
                [[x, rear_min_z], [x, rear_max_z]]
            )
            # Restrict that vertical line to within the full rear bounds.
            line_in_rear = vertical_line.intersection(rear_poly)
            # Try again if the chosen X doesn't work.
            if not line_in_rear.is_empty:
                break
            line_in_rear = None
        # Location is not possible.
        if not line_in_rear or line_in_rear.is_empty:
            return None, None
        # Unlikely but possible to find just a single point here.
        elif line_in_rear.geom_type == 'Point':
            location = line_in_rear
        else:
            # Choose a random position on that vertical line.
            fraction = random.random()
            location = line_in_rear.interpolate(fraction, normalized=True)
        return location.x, location.y

    return calc_obj_pos(
        performer_start['position'],
        [],
        target_definition_or_instance,
        xz_func=compute_xz,
        rotation_func=rotation_func
    )


def generate_location_in_line_with_object(
    object_definition_or_instance: Dict[str, Any],
    static_definition_or_instance: Dict[str, Any],
    static_location: Dict[str, Any],
    performer_start: Dict[str, Dict[str, float]],
    bounds_list: List[List[Dict[str, float]]],
    adjacent: bool = False,
    behind: bool = False,
    obstruct: bool = False,
    unreachable: bool = False
) -> Dict[str, Any]:
    """Generate and return a new location for the given object so it's in line
    with the given static object at its given location based on the given
    performer start location. By default, the location is in front of the
    static object. If adjacent=True, the location is to the left or the right
    of the static object. If behind=True, the location is in back of the static
    object. If obstruct=True, the location must obstruct the static object.
    If unreachable=True, the location must be far enough away from the static
    object so that the performer cannot reach the static object. Assume only
    one bool flag is ever used."""

    dimensions = object_definition_or_instance['dimensions']
    offset = object_definition_or_instance.get('offset', {'x': 0, 'z': 0})
    if object_definition_or_instance.get('closedDimensions'):
        dimensions = object_definition_or_instance.get('closedDimensions')
    if object_definition_or_instance.get('closedOffset'):
        offset = object_definition_or_instance.get('closedOffset')
    static_offset = static_definition_or_instance.get(
        'offset',
        {'x': 0, 'z': 0}
    )
    static_x = (static_location['position']['x'] + static_offset['x'])
    static_z = (static_location['position']['z'] + static_offset['z'])
    static_rect = generate_object_bounds(
        static_definition_or_instance['dimensions'],
        static_offset,
        static_location['position'],
        static_location['rotation']
    )

    # The distance needs to be at least the min dimensions of the two objects
    # added together with a gap in between them.
    min_distance_between_objects = MIN_GAP + min(
        (static_definition_or_instance['dimensions']['x'] / 2.0),
        (static_definition_or_instance['dimensions']['z'] / 2.0)
    ) + min((dimensions['x'] / 2.0), (dimensions['z'] / 2.0))

    distance_from_performer_start_to_object = math.sqrt(
        (static_x - performer_start['position']['x'])**2 +
        (static_z - performer_start['position']['z'])**2
    )

    if (not adjacent) and (not behind) and (
        distance_from_performer_start_to_object <
        (min_distance_between_objects * 2)
    ):
        return None

    diagonal_distance_between_objects = MIN_GAP + math.sqrt(
        (static_definition_or_instance['dimensions']['x'] / 2.0)**2 +
        (static_definition_or_instance['dimensions']['z'] / 2.0)**2
    ) + math.sqrt(
        (dimensions['x'] / 2.0)**2 +
        (dimensions['z'] / 2.0)**2
    )

    # The distance shouldn't need to be any more than the diagonal distance
    # between the two objects added together with a gap in between them, unless
    # obstruct=True or unreachable=True, then use the distance between the
    # static object's location and the performer's start location. Subtract the
    # diagonal_distance_between_objects to account for the objects' dimensions.
    max_distance = (
        distance_from_performer_start_to_object -
        diagonal_distance_between_objects
    ) if (obstruct or unreachable) else diagonal_distance_between_objects

    # Find the angle drawn between the static object and the performer start.
    performer_angle = math.degrees(math.atan2(
        (static_z - performer_start['position']['z']),
        (static_x - performer_start['position']['x'])
    ))
    # If behind=True, rotate the angle by 180 degrees.
    line_rotation_list = [performer_angle] if behind else (
        # If adjacent=True, rotate the angle by 90 or 270 degrees.
        [performer_angle + 90, performer_angle + 270] if adjacent
        else [performer_angle + 180]
    )
    random.shuffle(line_rotation_list)

    location = None
    for line_rotation in line_rotation_list:
        line_distance = min_distance_between_objects
        # Try to position the 2nd object at a distance away from the static
        # object. If that doesn't work, increase the distance a little bit.
        while line_distance <= max_distance:
            # Create a line of the distance and rotation away from the static
            # object to identify the 2nd object's possible location.
            line = geometry.LineString([[0, 0], [line_distance, 0]])
            line = affinity.rotate(line, line_rotation, origin=(0, 0))
            line = affinity.translate(line, static_x, static_z)
            x = line.coords[1][0] - offset['x']
            z = line.coords[1][1] - offset['z']
            object_rect = calc_obj_coords(
                x,
                z,
                dimensions['x'] / 2.0,
                dimensions['z'] / 2.0,
                offset['x'],
                offset['z'],
                static_location['rotation']['y']
            )

            # Ensure the location is within the room and doesn't overlap with
            # any existing object location or the performer start location.
            successful = validate_location_rect(
                object_rect,
                performer_start['position'],
                bounds_list + [static_rect]
            )

            if successful and obstruct:
                object_poly = get_bounding_polygon({
                    'boundingBox': object_rect
                })
                # If obstruct=True, ensure the location will obstruct the
                # static object.
                if not does_fully_obstruct_target(
                    performer_start['position'],
                    static_location,
                    object_poly
                ):
                    successful = False

            if successful and unreachable:
                object_poly = get_bounding_polygon({
                    'boundingBox': object_rect
                })
                static_poly = get_bounding_polygon({
                    'boundingBox': static_rect
                })
                # If unreachable=True, ensure the location is far enough away
                # from the static object so that the performer cannot reach it.
                reachable_distance = object_poly.distance(static_poly) + max(
                    (dimensions['x'] / 2.0),
                    (dimensions['z'] / 2.0)
                )
                if reachable_distance <= util.MAX_REACH_DISTANCE:
                    successful = False

            if successful:
                rotation = object_definition_or_instance.get('rotation', {})
                location = {
                    'position': {
                        'x': x,
                        'y': object_definition_or_instance.get('positionY', 0),
                        'z': z
                    },
                    'rotation': {
                        'x': rotation.get('x', 0),
                        # Rotate the object to align with the performer.
                        # This is needed for obstacle tasks.
                        # Transform geometric angle into Unity rotation.
                        'y': 450 - performer_angle,
                        'z': rotation.get('z', 0)
                    },
                    'boundingBox': object_rect
                }
                break
            else:
                location = None
                line_distance += MIN_GAP
        if location:
            break

    return location


def retrieve_obstacle_occluder_definition_list(
    target_definition_or_instance: Dict[str, Any],
    nested_definition_list: List[List[Dict[str, Any]]],
    is_occluder: bool
) -> Optional[Dict[str, Any]]:
    """Return all object definitions both taller and either wider or
    deeper. If wider (x-axis), angle 0 is returned; if deeper
    (z-axis), 90 degrees is returned. Objects returned may be equal in
    dimensions, not just strictly greater.
    """
    output_list = []
    object_attr = ('occluder' if is_occluder else 'obstacle')
    for definition_list in nested_definition_list:
        output_internal_list = []
        for definition in definition_list:
            if object_attr not in definition.get('attributes', []):
                continue
            target_dimensions = target_definition_or_instance['dimensions']
            if target_definition_or_instance.get('closedDimensions'):
                target_dimensions = target_definition_or_instance.get(
                    'closedDimensions'
                )
            dimensions = definition['dimensions']
            if definition.get('closedDimensions'):
                dimensions = definition.get('closedDimensions')
            cannot_walk_over = (
                dimensions['y'] >= (util.PERFORMER_CAMERA_Y / 2.0)
            )
            cannot_walk_into = definition['mass'] > PERFORMER_MASS
            # Only need a larger Y dimension if the object is an occluder.
            if cannot_walk_over and cannot_walk_into and (
                not is_occluder or dimensions['y'] >= target_dimensions['y']
            ):
                if dimensions['x'] >= target_dimensions['x']:
                    output_internal_list.append((definition, 0))
                elif dimensions['z'] >= target_dimensions['x']:
                    output_internal_list.append((definition, 90))
        if len(output_internal_list) > 0:
            output_list.append(output_internal_list)
    return output_list


def get_bounding_polygon(
        object_or_location: Dict[str, Any]) -> geometry.Polygon:
    if 'boundingBox' in object_or_location:
        bounding_box: List[Dict[str, float]
                           ] = object_or_location['boundingBox']
        poly = rect_to_poly(bounding_box)
    else:
        show = object_or_location['shows'][0]
        if 'boundingBox' in show:
            bounding_box: List[Dict[str, float]] = show['boundingBox']
            poly = rect_to_poly(bounding_box)
        else:
            # TODO I think we need to consider the affect of the object's
            # offsets on its poly here
            x = show['position']['x']
            z = show['position']['z']
            dx = object_or_location['dimensions']['x'] / 2.0
            dz = object_or_location['dimensions']['z'] / 2.0
            poly = geometry.box(x - dx, z - dz, x + dx, z + dz)
            poly = shapely.affinity.rotate(poly, -show['rotation']['y'])
    return poly


def are_adjacent(obj_a: Dict[str, Any], obj_b: Dict[str, Any],
                 distance: float = MAX_OBJECTS_ADJACENT_DISTANCE) -> bool:
    poly_a = get_bounding_polygon(obj_a)
    poly_b = get_bounding_polygon(obj_b)
    actual_distance = poly_a.distance(poly_b)
    return actual_distance <= distance


def rect_to_poly(rect: List[Dict[str, Any]]) -> geometry.Polygon:
    points = [(point['x'], point['z']) for point in rect]
    return geometry.Polygon(points)


def find_performer_rect(
        performer_position: Dict[str, float]) -> List[Dict[str, float]]:
    return [
        {'x': performer_position['x'] - util.PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] - util.PERFORMER_HALF_WIDTH},
        {'x': performer_position['x'] - util.PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] + util.PERFORMER_HALF_WIDTH},
        {'x': performer_position['x'] + util.PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] + util.PERFORMER_HALF_WIDTH},
        {'x': performer_position['x'] + util.PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] - util.PERFORMER_HALF_WIDTH}
    ]


def generate_object_bounds(dimensions: Dict[str, float],
                           offset: Dict[str, float],
                           position: Dict[str, float],
                           rotation: Dict[str, float]) \
        -> List[Dict[str, float]]:
    """Returns the bounds for the object with the given properties."""
    x = position['x']
    z = position['z']
    dx = dimensions['x'] / 2.0
    dz = dimensions['z'] / 2.0
    offset_x = offset['x'] if offset else 0.0
    offset_z = offset['z'] if offset else 0.0
    return calc_obj_coords(x, z, dx, dz, offset_x, offset_z, rotation['y'])


def does_fully_obstruct_target(performer_start_position: Dict[str, float],
                               target_or_location: Dict[str, Any],
                               object_poly: geometry.Polygon) -> bool:
    """Returns whether the given object_poly obstructs each line between the
    given performer_start_position and
    all four corners of the given target object or location."""

    return _does_obstruct_target_helper(
        performer_start_position,
        target_or_location,
        object_poly,
        fully=True
    )


def does_partly_obstruct_target(performer_start_position: Dict[str, float],
                                target_or_location: Dict[str, Any],
                                object_poly: geometry.Polygon) -> bool:
    """Returns whether the given object_poly obstructs one line between the
    given performer_start_position and
    the four corners of the given target object or location."""

    return _does_obstruct_target_helper(
        performer_start_position,
        target_or_location,
        object_poly,
        fully=False
    )


def _does_obstruct_target_helper(performer_start_position: Dict[str, float],
                                 target_or_location: Dict[str, Any],
                                 object_poly: geometry.Polygon,
                                 fully: bool = False) -> bool:

    obstructing_points = 0
    performer_start_coordinates = (
        performer_start_position['x'],
        performer_start_position['z'])
    bounds = target_or_location.get('boundingBox', target_or_location.get(
        'shows',
        [{'boundingBox': []}]
    )[0]['boundingBox'])

    target_poly = rect_to_poly(bounds)
    target_center = target_poly.centroid.coords[0]
    points = bounds + [{'x': target_center[0], 'z': target_center[1]}]

    if not fully:
        for index, next_point in enumerate(bounds):
            previous_point = bounds[(index - 1) if (index > 0) else -1]
            line_full = geometry.LineString([
                (previous_point['x'], previous_point['z']),
                (next_point['x'], next_point['z'])
            ])
            line_full_center = line_full.centroid.coords[0]
            center_point = {'x': line_full_center[0], 'z': line_full_center[1]}
            points.append(center_point)
            for point_1, point_2 in [
                (previous_point, center_point), (center_point, next_point)
            ]:
                line = geometry.LineString([
                    (point_1['x'], point_1['z']), (point_2['x'], point_2['z'])
                ])
                line_center = line.centroid.coords[0]
                points.append({'x': line_center[0], 'z': line_center[1]})

    for point in points:
        target_corner_coordinates = (point['x'], point['z'])
        line_to_target = geometry.LineString([
            performer_start_coordinates,
            target_corner_coordinates
        ])
        if object_poly.intersects(line_to_target):
            obstructing_points += 1
    return obstructing_points == 5 if fully else obstructing_points > 0


def validate_location_rect(
    location_rect: List[Dict[str, float]],
    performer_start_position: Dict[str, float],
    rect_list: List[List[Dict[str, float]]]
) -> bool:
    """Returns if the given location rect is valid using the given performer
    start position and rect list corresponding to other positioned objects."""
    performer_start_rect = find_performer_rect(performer_start_position)
    return (
        rect_within_room(location_rect) and
        not sat_entry(location_rect, performer_start_rect) and
        not any(sat_entry(location_rect, rect) for rect in rect_list)
    )
