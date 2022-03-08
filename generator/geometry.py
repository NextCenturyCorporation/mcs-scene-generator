import copy
import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from machine_common_sense.config_manager import Vector3d
from shapely import affinity, geometry

from .definitions import DefinitionDataset, ObjectDefinition
from .separating_axis_theorem import sat_entry

MAX_TRIES = 50

MAX_REACH_DISTANCE = 1.0
MOVE_DISTANCE = 0.1

PERFORMER_CAMERA_Y = 0.762
PERFORMER_HALF_WIDTH = 0.27
PERFORMER_HEIGHT = PERFORMER_HALF_WIDTH * 4
PERFORMER_MASS = 2
PERFORMER_WIDTH = PERFORMER_HALF_WIDTH * 2.0

MIN_RANDOM_INTERVAL = 0.05
POSITION_DIGITS = 2
VALID_ROTATIONS = (0, 45, 90, 135, 180, 225, 270, 315)

DEFAULT_ROOM_DIMENSIONS = {'x': 10, 'y': 3, 'z': 10}

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


@dataclass
class ObjectBounds():
    """The bounds of a specific object, including its 2D bounding box, 2D
    polygon, and Y range."""
    box_xz: List[Vector3d]
    max_y: float
    min_y: float
    polygon_xz: geometry.Polygon = None

    def __post_init__(self):
        self._update_poly()

    def _update_poly(self) -> None:
        points = [(point.x, point.z) for point in self.box_xz]
        self.polygon_xz = geometry.Polygon(points)

    def expand_by(self, amount: float) -> None:
        """Expand this bounds by the given amount on both the X and Z axes."""
        self.polygon_xz = self.polygon_xz.buffer(
            amount,
            # Ensure the output polygon is also a rectangle.
            join_style=geometry.JOIN_STYLE.mitre
        )
        self.box_xz = [
            Vector3d(point[0], 0, point[1]) for point in
            self.polygon_xz.exterior.coords
        ][:-1]

    def extend_bottom_to_ground(self) -> None:
        """Extend the bottom of this bounds to the ground."""
        # We're not currently saving any height data in the box or polygon,
        # so just update the min_y for now.
        self.min_y = 0

    def is_within_room(self, room_dimensions: Dict[str, float]) -> bool:
        """Return whether this bounds in within the given room dimensions."""
        room_max_x = room_dimensions['x'] / 2.0
        room_max_z = room_dimensions['z'] / 2.0
        return all((
            -room_max_x <= point.x <= room_max_x and
            -room_max_z <= point.z <= room_max_z
        ) for point in self.box_xz)


def __dict_to_vector(data: Dict[str, float]) -> Vector3d:
    return Vector3d(data['x'], data['y'], data['z'])


def create_bounds(
    # TODO MCS-697 MCS-698 Use Vector3d instead of Dict
    dimensions: Dict[str, float],
    offset: Optional[Dict[str, float]],
    position: Dict[str, float],
    rotation: Dict[str, float],
    standing_y: float
) -> ObjectBounds:
    """Creates and returns an ObjectBounds for the object with the given size
    properties in the given location."""
    # TODO MCS-697 MCS-698 Use class props directly instead of converting
    dimensions = __dict_to_vector(dimensions)
    offset = __dict_to_vector(offset) if offset else Vector3d()
    position = __dict_to_vector(position)
    rotation = __dict_to_vector(rotation)

    radian_amount = math.pi * (2 - rotation.y / 180.0)

    rotate_sin = math.sin(radian_amount)
    rotate_cos = math.cos(radian_amount)
    x_plus = (dimensions.x / 2.0) + offset.x
    x_minus = -(dimensions.x / 2.0) + offset.x
    z_plus = (dimensions.z / 2.0) + offset.z
    z_minus = -(dimensions.z / 2.0) + offset.z

    a = Vector3d(
        position.x + x_plus * rotate_cos - z_plus * rotate_sin,
        0,
        position.z + x_plus * rotate_sin + z_plus * rotate_cos
    )
    b = Vector3d(
        position.x + x_plus * rotate_cos - z_minus * rotate_sin,
        0,
        position.z + x_plus * rotate_sin + z_minus * rotate_cos
    )
    c = Vector3d(
        position.x + x_minus * rotate_cos - z_minus * rotate_sin,
        0,
        position.z + x_minus * rotate_sin + z_minus * rotate_cos
    )
    d = Vector3d(
        position.x + x_minus * rotate_cos - z_plus * rotate_sin,
        0,
        position.z + x_minus * rotate_sin + z_plus * rotate_cos
    )

    y_min = position.y - standing_y
    y_max = y_min + dimensions.y
    return ObjectBounds(box_xz=[a, b, c, d], max_y=y_max, min_y=y_min)


def random_real(a: float, b: float,
                step: float = MIN_RANDOM_INTERVAL) -> float:
    """Return a random real number N where a <= N <= b and N - a is
    divisible by step."""
    steps = int((b - a) / step)
    try:
        n = random.randint(0, steps)
    except ValueError as e:
        raise ValueError(f'bad args to random_real: ({a}, {b}, {step})', e)
    return a + (n * step)


def random_position_x(room_dimensions: Dict[str, float]) -> float:
    room_max_x = room_dimensions['x'] / 2.0
    return round(random.uniform(-room_max_x, room_max_x), POSITION_DIGITS)


def random_position_z(room_dimensions: Dict[str, float]) -> float:
    room_max_z = room_dimensions['z'] / 2.0
    return round(random.uniform(-room_max_z, room_max_z), POSITION_DIGITS)


def random_rotation() -> float:
    return random.choice(VALID_ROTATIONS)


def calc_obj_pos(
    performer_position: Dict[str, float],
    bounds_list: List[ObjectBounds],
    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    definition_or_instance: Union[ObjectDefinition, Dict[str, Any]],
    x_func: Callable[[Dict[str, float]], float] = random_position_x,
    z_func: Callable[[Dict[str, float]], float] = random_position_z,
    rotation_func: Callable[[], float] = None,
    xz_func: Callable[[], Tuple[float, float]] = None,
    room_dimensions: Dict[str, float] = None
) -> Optional[Dict[str, Any]]:
    """Returns new object with rotation & position if we can place the
    object in the frame, None otherwise."""

    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    if isinstance(definition_or_instance, dict):
        debug = definition_or_instance['debug']
        dimensions = debug['dimensions']
        offset = debug.get('offset', {'x': 0, 'z': 0})
        position_y = debug.get('positionY', 0)
        rotation = debug.get('rotation', {'x': 0, 'y': 0, 'z': 0})
    else:
        dimensions = vars(definition_or_instance.dimensions)
        offset = vars(definition_or_instance.offset)
        position_y = definition_or_instance.positionY
        rotation = vars(definition_or_instance.rotation)

    tries = 0
    while tries < MAX_TRIES:
        rotation_x = rotation['x']
        rotation_y = rotation['y'] + (
            rotation_func() if rotation_func else random_rotation()
        )
        rotation_z = rotation['z']
        if xz_func is not None:
            new_x, new_z = xz_func(room_dimensions or DEFAULT_ROOM_DIMENSIONS)
        else:
            new_x = x_func(room_dimensions or DEFAULT_ROOM_DIMENSIONS)
            new_z = z_func(room_dimensions or DEFAULT_ROOM_DIMENSIONS)

        if new_x is not None and new_z is not None:
            bounds = create_bounds(
                dimensions=dimensions,
                offset=offset,
                position={'x': new_x, 'y': position_y, 'z': new_z},
                rotation={'x': rotation_x, 'y': rotation_y, 'z': rotation_z},
                standing_y=position_y
            )
            if validate_location_rect(
                bounds,
                performer_position,
                bounds_list,
                room_dimensions or DEFAULT_ROOM_DIMENSIONS
            ):
                break
        tries += 1

    if tries < MAX_TRIES:
        object_location = {
            'rotation': {'x': rotation_x, 'y': rotation_y, 'z': rotation_z},
            'position': {
                'x': new_x,
                'y': position_y,
                'z': new_z
            },
            'boundingBox': bounds
        }
        bounds_list.append(bounds)
        return object_location

    logging.debug(f'could not place object: {definition_or_instance}')
    return None


def position_distance(a: Dict[str, float], b: Dict[str, float]) -> float:
    """Compute the distance between two positions."""
    return math.sqrt((a['x'] - b['x'])**2 + (a['y'] -
                                             b['y'])**2 + (a['z'] - b['z'])**2)


def _get_visible_segment(
    performer_start: Dict[str, Dict[str, float]],
    room_dimensions: Dict[str, float]
) -> geometry.LineString:
    """Get a line segment that should be visible to the performer
    (straight ahead and at least MIN_FORWARD_VISIBILITY_DISTANCE but within
    the room). Return None if no visible segment is possible.
    """
    max_dimension = max(room_dimensions['x'], room_dimensions['z'])
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
    room_max_x = room_dimensions['x'] / 2.0
    room_max_z = room_dimensions['z'] / 2.0
    room = geometry.box(-room_max_x, -room_max_z, room_max_x, room_max_z)

    target_segment = room.intersection(view_segment)
    if target_segment.is_empty:
        logging.debug(
            f'performer too close to the wall, cannot place object in front '
            f'of it (performer location={performer_start})')
        return None
    return target_segment


def get_location_in_front_of_performer(
    performer_start: Dict[str, Dict[str, float]],
    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    target_definition_or_instance: Union[ObjectDefinition, Dict[str, Any]],
    rotation_func: Callable[[], float] = random_rotation,
    room_dimensions: Dict[str, float] = None
) -> Optional[Dict[str, Any]]:
    """Return a random location in the line directly in front of the performer
    agent's starting position and rotation."""

    visible_segment = _get_visible_segment(
        performer_start,
        room_dimensions or DEFAULT_ROOM_DIMENSIONS
    )
    if not visible_segment:
        return None

    def segment_xz(_room_dimensions: Dict[str, float]) -> Tuple[float, float]:
        fraction = random.random()
        point = visible_segment.interpolate(fraction, normalized=True)
        return point.x, point.y

    return calc_obj_pos(
        performer_start['position'],
        [],
        target_definition_or_instance,
        xz_func=segment_xz,
        rotation_func=rotation_func,
        room_dimensions=(room_dimensions or DEFAULT_ROOM_DIMENSIONS)
    )


def get_location_in_back_of_performer(
    performer_start: Dict[str, Dict[str, float]],
    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    target_definition_or_instance: Union[ObjectDefinition, Dict[str, Any]],
    rotation_func: Callable[[], float] = random_rotation,
    room_dimensions: Dict[str, float] = None
) -> Optional[Dict[str, Any]]:
    """Return a random location in the 180-degree-arc directly in back of the
    performer agent's starting position and rotation."""

    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    if isinstance(target_definition_or_instance, dict):
        debug = target_definition_or_instance['debug']
        dimensions = debug['dimensions']
        offset = debug.get('offset', {'x': 0, 'z': 0})
    else:
        dimensions = vars(target_definition_or_instance.dimensions)
        offset = vars(target_definition_or_instance.offset)

    # We may rotate the object so use its larger X/Z size.
    object_half_size = max(
        dimensions['x'] / 2.0 - offset['x'],
        dimensions['z'] / 2.0 - offset['z']
    )

    # Find the part of the room that's behind the performer's start location
    # (the 180 degree arc in the opposite direction from its start rotation).
    # If the performer would start at (0, 0) facing north (its rotation is 0),
    # its rear poly would then be: minx, miny, maxx, maxy
    rear_poly = geometry.box(
        -((room_dimensions or DEFAULT_ROOM_DIMENSIONS)['x']),
        -((room_dimensions or DEFAULT_ROOM_DIMENSIONS)['z']),
        ((room_dimensions or DEFAULT_ROOM_DIMENSIONS)['x']),
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
    room_max_x = (room_dimensions or DEFAULT_ROOM_DIMENSIONS)['x'] / 2.0
    room_max_z = (room_dimensions or DEFAULT_ROOM_DIMENSIONS)['z'] / 2.0
    room_poly = geometry.box(
        -room_max_x + object_half_size,
        -room_max_z + object_half_size,
        room_max_x - object_half_size,
        room_max_z - object_half_size
    )
    rear_poly = rear_poly.intersection(room_poly)

    if not rear_poly or rear_poly.is_empty:
        return None

    rear_min_x = min(room_max_x, max(-room_max_x, rear_poly.bounds[0]))
    rear_max_x = min(room_max_x, max(-room_max_x, rear_poly.bounds[2]))
    rear_min_z = min(room_max_z, max(-room_max_z, rear_poly.bounds[1]))
    rear_max_z = min(room_max_z, max(-room_max_z, rear_poly.bounds[3]))

    def compute_xz(_room_dimensions: Dict[str, float]) -> Tuple[float, float]:
        for _ in range(MAX_TRIES):
            # Try choosing a random X within the rear X bounds.
            x = random_real(rear_min_x, rear_max_x)
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
        rotation_func=rotation_func,
        room_dimensions=(room_dimensions or DEFAULT_ROOM_DIMENSIONS)
    )


def generate_location_on_object(
    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    object_definition_or_instance: Union[ObjectDefinition, Dict[str, Any]],
    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    static_instance: Dict[str, Any],
    performer_start: Dict[str, Dict[str, float]],
    bounds_list: List[ObjectBounds],
    room_dimensions: Dict[str, float] = None,
    center: bool = False
) -> Dict[str, Any]:
    """Creates a location for the object to place it on top of the static object.

    Returns:
        Dict[str, Any]: Location dict or None if it cannot be determined.
    """
    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    if isinstance(object_definition_or_instance, dict):
        debug = object_definition_or_instance['debug']
        dimensions = debug['dimensions']
        offset = debug.get('offset', {'x': 0, 'y': 0, 'z': 0})
        position_y = debug.get('positionY', 0)
        rotation = debug.get('rotation', {'x': 0, 'y': 0, 'z': 0})
        if debug.get('closedDimensions'):
            dimensions = debug.get('closedDimensions')
        if debug.get('closedOffset'):
            offset = debug.get('closedOffset')
    else:
        dimensions = vars(object_definition_or_instance.dimensions)
        offset = vars(object_definition_or_instance.offset)
        position_y = object_definition_or_instance.positionY
        rotation = vars(object_definition_or_instance.rotation)
        if object_definition_or_instance.closedDimensions:
            dimensions = vars(object_definition_or_instance.closedDimensions)
        if object_definition_or_instance.closedOffset:
            offset = vars(object_definition_or_instance.closedOffset)

    if not isinstance(static_instance, dict):
        raise Exception(
            "Generate_location_on_object() must be passed a static instance")

    # determine bounds of static object
    static_bounds = (
        static_instance['shows'][0]['boundingBox']
    )
    xy_bounds = static_bounds.box_xz

    location = None
    for _ in range(MAX_TRIES):
        # determine x,z of object in static bounds
        if center:
            x, z = static_bounds.polygon_xz.centroid.coords[0]
        else:
            # Create some basic bounds to limit where we place the object
            # We will test more precisely later
            buffer = min(dimensions['x'], dimensions['z'])
            xmax = max(xy_bounds[0].x, xy_bounds[1].x,
                       xy_bounds[2].x, xy_bounds[3].x) - buffer
            xmin = min(xy_bounds[0].x, xy_bounds[1].x,
                       xy_bounds[2].x, xy_bounds[3].x) + buffer
            zmax = max(xy_bounds[0].z, xy_bounds[1].z,
                       xy_bounds[2].z, xy_bounds[3].z) - buffer
            zmin = min(xy_bounds[0].z, xy_bounds[1].z,
                       xy_bounds[2].z, xy_bounds[3].z) + buffer
            if xmin > xmax or zmin > zmax:
                raise Exception(
                    "Object with keyword location 'on_top' or "
                    "'on_center' too large to fit on base object.")
            x = random.uniform(xmin, xmax)
            z = random.uniform(zmin, zmax)

        # set y position
        y = static_bounds.max_y + position_y
        obj_position = {'x': x, 'y': y, 'z': z}

        # determine new bounds for object
        object_bounds = create_bounds(
            dimensions=dimensions,
            offset=offset,
            position=obj_position,
            rotation=rotation,
            standing_y=position_y
        )

        # only continue if the object is within the bounds of the static object
        if static_bounds.polygon_xz.contains(object_bounds.polygon_xz):
            location = {
                'position': obj_position,
                'rotation': {
                    'x': rotation['x'],
                    'y': rotation['y'],
                    'z': rotation['z']
                },
                'boundingBox': object_bounds
            }

            if validate_location_rect(
                object_bounds,
                performer_start['position'],
                bounds_list + [static_bounds],
                room_dimensions or DEFAULT_ROOM_DIMENSIONS
            ):
                break
    return location


def generate_location_in_line_with_object(
    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    object_definition_or_instance: Union[ObjectDefinition, Dict[str, Any]],
    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    static_definition_or_instance: Union[ObjectDefinition, Dict[str, Any]],
    static_location: Dict[str, Any],
    performer_start: Dict[str, Dict[str, float]],
    bounds_list: List[ObjectBounds],
    adjacent: bool = False,
    behind: bool = False,
    obstruct: bool = False,
    unreachable: bool = False,
    room_dimensions: Dict[str, float] = None
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

    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    if isinstance(object_definition_or_instance, dict):
        debug = object_definition_or_instance['debug']
        dimensions = debug['dimensions']
        offset = debug.get('offset', {'x': 0, 'z': 0})
        position_y = debug.get('positionY', 0)
        rotation = debug.get('rotation', {'x': 0, 'y': 0, 'z': 0})
        if debug.get('closedDimensions'):
            dimensions = debug.get('closedDimensions')
        if debug.get('closedOffset'):
            offset = debug.get('closedOffset')
    else:
        dimensions = vars(object_definition_or_instance.dimensions)
        offset = vars(object_definition_or_instance.offset)
        position_y = object_definition_or_instance.positionY
        rotation = vars(object_definition_or_instance.rotation)
        if object_definition_or_instance.closedDimensions:
            dimensions = vars(object_definition_or_instance.closedDimensions)
        if object_definition_or_instance.closedOffset:
            offset = vars(object_definition_or_instance.closedOffset)

    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    if isinstance(static_definition_or_instance, dict):
        static_debug = static_definition_or_instance['debug']
        static_dimensions = static_debug['dimensions']
        static_offset = static_debug.get('offset', {'x': 0, 'y': 0, 'z': 0})
        static_position_y = static_debug.get('positionY', 0)
    else:
        static_dimensions = vars(static_definition_or_instance.dimensions)
        static_offset = vars(static_definition_or_instance.offset)
        static_position_y = static_definition_or_instance.positionY

    static_x = (static_location['position']['x'] + static_offset['x'])
    static_z = (static_location['position']['z'] + static_offset['z'])
    static_bounds = create_bounds(
        dimensions=static_dimensions,
        offset=static_offset,
        position=static_location['position'],
        rotation=static_location['rotation'],
        standing_y=static_position_y
    )

    # The distance needs to be at least the min dimensions of the two objects
    # added together with a gap in between them.
    min_distance_between_objects = MIN_GAP + min(
        (static_dimensions['x'] / 2.0),
        (static_dimensions['z'] / 2.0)
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
        (static_dimensions['x'] / 2.0)**2 +
        (static_dimensions['z'] / 2.0)**2
    ) + math.sqrt(
        (dimensions['x'] / 2.0)**2 +
        (dimensions['z'] / 2.0)**2
    )

    # The distance shouldn't need to be any more than the diagonal distance
    # between the two objects added together with a gap in between them, unless
    # obstruct=True or unreachable=True, then use the distance between the
    # static object's location and the performer's start location. Subtract the
    # min_distance_between_objects to account for the objects' dimensions.
    max_distance = (
        distance_from_performer_start_to_object - min_distance_between_objects
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
            object_bounds = create_bounds(
                dimensions=dimensions,
                offset=offset,
                position={'x': x, 'y': position_y, 'z': z},
                rotation=static_location['rotation'],
                standing_y=position_y
            )
            # Ensure the location is within the room and doesn't overlap with
            # any existing object location or the performer start location.
            successful = validate_location_rect(
                object_bounds,
                performer_start['position'],
                bounds_list + [static_bounds],
                room_dimensions or DEFAULT_ROOM_DIMENSIONS
            )

            if successful and obstruct:
                object_poly = object_bounds.polygon_xz
                static_poly = static_bounds.polygon_xz
                # If obstruct=True, ensure the location is fairly close to the
                # static object and will completely obstruct it from view.
                if object_poly.distance(static_poly) > MAX_REACH_DISTANCE:
                    successful = False
                if successful and not does_fully_obstruct_target(
                    performer_start['position'],
                    static_location,
                    object_poly
                ):
                    successful = False

            if successful and unreachable:
                object_poly = object_bounds.polygon_xz
                static_poly = static_bounds.polygon_xz
                # If unreachable=True, ensure the location is far enough away
                # from the static object so that the performer cannot reach it.
                reachable_distance = object_poly.distance(static_poly) + min(
                    (dimensions['x'] / 2.0),
                    (dimensions['z'] / 2.0)
                )
                if reachable_distance <= MAX_REACH_DISTANCE:
                    successful = False

            if successful:
                location = {
                    'position': {
                        'x': x,
                        'y': position_y,
                        'z': z
                    },
                    'rotation': {
                        'x': rotation['x'],
                        # Rotate the object to align with the performer.
                        # This is needed for obstacle tasks.
                        # Transform geometric angle into Unity rotation.
                        'y': 450 - performer_angle,
                        'z': rotation['z']
                    },
                    'boundingBox': object_bounds
                }
                break
            else:
                location = None
                line_distance += MIN_GAP
        if location:
            break

    return location


def retrieve_obstacle_occluder_definition_list(
    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    target_definition_or_instance: Union[ObjectDefinition, Dict[str, Any]],
    definition_dataset: DefinitionDataset,
    is_occluder: bool
) -> List[Tuple[ObjectDefinition, int]]:
    """Return each object definition from the given list that is both taller
    and wider/deeper that the given target, tupled with a Y rotation amount.
    If wider (x-axis), rotation 0 is returned; if deeper (z-axis), rotation 90
    is returned. If is_occluder is True, each matching definition must be an
    occluder; otherwise, each matching definition must be an obstacle."""

    # TODO MCS-697 Define an ObjectInstance class extending ObjectDefinition.
    if isinstance(target_definition_or_instance, dict):
        debug = target_definition_or_instance['debug']
        target_dimensions = debug['dimensions']
        if debug.get('closedDimensions'):
            target_dimensions = debug.get('closedDimensions')
    else:
        target_dimensions = vars(target_definition_or_instance.dimensions)
        if target_definition_or_instance.closedDimensions:
            target_dimensions = vars(
                target_definition_or_instance.closedDimensions
            )

    output_list = []
    object_attr = ('occluder' if is_occluder else 'obstacle')
    for definition in definition_dataset.definitions():
        if not getattr(definition, object_attr):
            continue
        dimensions = definition.dimensions
        if definition.closedDimensions:
            dimensions = definition.closedDimensions
        cannot_walk_over = dimensions.y >= PERFORMER_HALF_WIDTH
        cannot_walk_into = definition.mass > PERFORMER_MASS
        # Only need a larger Y dimension if the object is an occluder.
        if cannot_walk_over and cannot_walk_into and (
            not is_occluder or dimensions.y >= target_dimensions['y']
        ):
            if dimensions.x >= target_dimensions['x']:
                output_list.append((definition, 0))
            # If the object's Z is bigger than the target's X, rotate it.
            elif dimensions.z >= target_dimensions['x']:
                output_list.append((definition, 90))
    return output_list


def get_bounding_polygon(
    object_or_location: Dict[str, Any]
) -> geometry.Polygon:
    if 'boundingBox' in object_or_location:
        return object_or_location['boundingBox'].polygon_xz
    show = object_or_location['shows'][0]
    if 'boundingBox' in show:
        return show['boundingBox'].polygon_xz


def are_adjacent(obj_a: Dict[str, Any], obj_b: Dict[str, Any],
                 distance: float = MAX_OBJECTS_ADJACENT_DISTANCE) -> bool:
    poly_a = get_bounding_polygon(obj_a)
    poly_b = get_bounding_polygon(obj_b)
    actual_distance = poly_a.distance(poly_b)
    return actual_distance <= distance


def find_performer_bounds(
    performer_position: Dict[str, float]
) -> ObjectBounds:
    return ObjectBounds(
        box_xz=[Vector3d(
            performer_position['x'] - PERFORMER_HALF_WIDTH,
            0,
            performer_position['z'] - PERFORMER_HALF_WIDTH
        ), Vector3d(
            performer_position['x'] - PERFORMER_HALF_WIDTH,
            0,
            performer_position['z'] + PERFORMER_HALF_WIDTH
        ), Vector3d(
            performer_position['x'] + PERFORMER_HALF_WIDTH,
            0,
            performer_position['z'] + PERFORMER_HALF_WIDTH
        ), Vector3d(
            performer_position['x'] + PERFORMER_HALF_WIDTH,
            0,
            performer_position['z'] - PERFORMER_HALF_WIDTH
        )],
        max_y=performer_position['y'] + PERFORMER_HEIGHT,
        min_y=performer_position['y']
    )


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
        performer_start_position['z']
    )
    bounds = (
        target_or_location.get('boundingBox') or
        target_or_location['shows'][0]['boundingBox']
    )

    target_poly = bounds.polygon_xz
    target_center = target_poly.centroid.coords[0]
    points = bounds.box_xz + [Vector3d(target_center[0], 0, target_center[1])]

    if not fully:
        for index, next_point in enumerate(bounds.box_xz):
            previous_point = bounds.box_xz[(index - 1) if (index > 0) else -1]
            line_full = geometry.LineString([
                (previous_point.x, previous_point.z),
                (next_point.x, next_point.z)
            ])
            full_center = line_full.centroid.coords[0]
            center_point = Vector3d(full_center[0], 0, full_center[1])
            points.append(center_point)
            for point_1, point_2 in [
                (previous_point, center_point), (center_point, next_point)
            ]:
                line = geometry.LineString([
                    (point_1.x, point_1.z), (point_2.x, point_2.z)
                ])
                line_center = line.centroid.coords[0]
                points.append(Vector3d(line_center[0], 0, line_center[1]))

    for point in points:
        target_corner_coordinates = (point.x, point.z)
        line_to_target = geometry.LineString([
            performer_start_coordinates,
            target_corner_coordinates
        ])
        if object_poly.intersects(line_to_target):
            obstructing_points += 1
    return obstructing_points == 5 if fully else obstructing_points > 0


def validate_location_rect(
    location_bounds: ObjectBounds,
    performer_start_position: Dict[str, float],
    bounds_list: List[ObjectBounds],
    room_dimensions: Dict[str, float]
) -> bool:
    """Returns if the given location rect is valid using the given performer
    start position and rect list corresponding to other positioned objects."""
    if not location_bounds.is_within_room(room_dimensions):
        return False
    performer_agent_bounds = find_performer_bounds(performer_start_position)
    for bounds in [performer_agent_bounds] + bounds_list:
        # If one bounds is completely above/below another: no collision.
        if (
            location_bounds.min_y >= bounds.max_y or
            location_bounds.max_y <= bounds.min_y
        ):
            continue
        # If one bounds intersects with another: collision! Invalid.
        if sat_entry(location_bounds.box_xz, bounds.box_xz):
            return False
    return True


def move_to_location(
    object_instance: Dict[str, Any],
    object_location: Dict[str, Any]
) -> Dict[str, Any]:
    """Move the given object to the given location and return the object."""
    location = copy.deepcopy(object_location)
    location['position']['x'] -= object_instance['debug']['offset']['x']
    location['position']['z'] -= object_instance['debug']['offset']['z']
    original_rotation = object_instance['debug'].get('originalRotation', {})
    for axis in ['x', 'y', 'z']:
        location['rotation'][axis] += original_rotation.get(axis, 0)
    object_instance['shows'][0]['position'] = location['position']
    object_instance['shows'][0]['rotation'] = location['rotation']
    object_instance['shows'][0]['boundingBox'] = create_bounds(
        dimensions=object_instance['debug']['dimensions'],
        offset=object_instance['debug']['offset'],
        position=location['position'],
        rotation=location['rotation'],
        standing_y=object_instance['debug']['positionY']
    )
    return object_instance


def generate_floor_area_bounds(area_x: float, area_z: float) -> ObjectBounds:
    """Generate and return an ObjectBounds for a floor area (a hole or lava)
    with the given coordinates."""
    points = [
        Vector3d(area_x - 0.5, 0, area_z - 0.5),
        Vector3d(area_x + 0.5, 0, area_z - 0.5),
        Vector3d(area_x + 0.5, 0, area_z + 0.5),
        Vector3d(area_x - 0.5, 0, area_z + 0.5)
    ]
    # Just use an arbitrarily high number for the max_y.
    return ObjectBounds(box_xz=points, max_y=100, min_y=0)
