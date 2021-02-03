from enum import Enum, auto
from typing import Dict, Any, Optional, Tuple, List

import geometry


def put_object_in_container(
    instance: Dict[str, Any],
    container: Dict[str, Any],
    area_index: int,
    rotation: Optional[float] = None
) -> None:
    area = container['enclosedAreas'][area_index]
    instance['locationParent'] = container['id']
    instance['parentArea'] = area_index

    # Assume that rotation argument is only either 0 or 90.
    sideways = (rotation == 90)

    instance['shows'][0]['position'] = area['position'].copy()
    if 'offset' in instance:
        x_prop = 'z' if sideways else 'x'
        z_prop = 'x' if sideways else 'z'
        instance['shows'][0]['position']['x'] -= instance['offset'][x_prop]
        instance['shows'][0]['position']['y'] -= instance['offset']['y']
        instance['shows'][0]['position']['z'] -= instance['offset'][z_prop]

    # Position object at bottom of container's enclosed area.
    instance['shows'][0]['position']['y'] += \
        (-area['dimensions']['y'] / 2.0) + instance.get('positionY', 0)

    if 'rotation' not in instance['shows'][0]:
        instance['shows'][0]['rotation'] = geometry.ORIGIN.copy()
    if rotation is not None:
        instance['shows'][0]['rotation']['y'] = rotation

    # if it had a boundingBox, it's not valid any more
    instance.pop('boundingBox', None)

    instance['shows'][0]['boundingBox'] = geometry.generate_object_bounds(
        instance['dimensions'],
        instance.get('offset'),
        instance['shows'][0]['position'],
        instance['shows'][0]['rotation']
    )

    if 'isParentOf' not in container:
        container['isParentOf'] = []
    container['isParentOf'].append(instance['id'])


class Orientation(Enum):
    SIDE_BY_SIDE = auto()
    FRONT_TO_BACK = auto()


def put_objects_in_container(
    object_a: Dict[str, Any],
    object_b: Dict[str, Any],
    container: Dict[str, Any],
    area_index: int,
    orientation: Orientation,
    rotation_a: float,
    rotation_b: float
) -> None:
    """Put two objects in the same enclosed area of a
    container. orientation determines how they are laid out with
    respect to each other within the container. rotation_a and rotation_b must
    be either 0 or 90.
    """
    if rotation_a not in (0, 90):
        raise ValueError(
            f'only 0 and 90 degree rotations supported for object a, '
            f'not {rotation_a}')
    if rotation_b not in (0, 90):
        raise ValueError(
            f'only 0 and 90 degree rotations supported for object b, '
            f'not {rotation_b}')

    # TODO This function should probably verify that both objects can fit
    # together inside the container...

    area = container['enclosedAreas'][area_index]
    object_a['locationParent'] = container['id']
    object_b['locationParent'] = container['id']
    object_a['parentArea'] = area_index
    object_b['parentArea'] = area_index
    shows_a = object_a['shows'][0]
    shows_b = object_b['shows'][0]

    if orientation == Orientation.SIDE_BY_SIDE:
        if rotation_a == 0:
            width_a = object_a['dimensions']['x']
        elif rotation_a == 90:
            width_a = object_a['dimensions']['z']
        shows_a['position'] = area['position'].copy()
        shows_a['position']['x'] -= width_a / 2.0
        if rotation_b == 0:
            width_b = object_b['dimensions']['x']
        elif rotation_b == 90:
            width_b = object_b['dimensions']['z']
        shows_b['position'] = area['position'].copy()
        shows_b['position']['x'] += width_b / 2.0

    elif orientation == Orientation.FRONT_TO_BACK:
        if rotation_a == 0:
            height_a = object_a['dimensions']['z']
        elif rotation_a == 90:
            height_a = object_a['dimensions']['x']
        shows_a['position'] = area['position'].copy()
        shows_a['position']['z'] -= height_a / 2.0
        if rotation_b == 0:
            height_b = object_b['dimensions']['z']
        elif rotation_b == 90:
            height_b = object_b['dimensions']['x']
        shows_b['position'] = area['position'].copy()
        shows_b['position']['z'] += height_b / 2.0

    shows_a['position']['y'] += - \
        (area['dimensions']['y'] / 2.0) + object_a.get('positionY', 0)
    shows_b['position']['y'] += - \
        (area['dimensions']['y'] / 2.0) + object_b.get('positionY', 0)
    shows_a['rotation'] = {'y': rotation_a}
    shows_b['rotation'] = {'y': rotation_b}

    # any boundingBox they may have had is not valid any more
    shows_a.pop('boundingBox', None)
    shows_b.pop('boundingBox', None)

    shows_a['boundingBox'] = geometry.generate_object_bounds(
        object_a['dimensions'],
        object_a.get('offset'),
        shows_a['position'],
        shows_a['rotation']
    )
    shows_b['boundingBox'] = geometry.generate_object_bounds(
        object_b['dimensions'],
        object_b.get('offset'),
        shows_b['position'],
        shows_b['rotation']
    )

    if 'isParentOf' not in container:
        container['isParentOf'] = []
    container['isParentOf'].append(object_a['id'])
    container['isParentOf'].append(object_b['id'])


def can_enclose(area: Dict[str, Any],
                target: Dict[str, Any]) -> Optional[float]:
    """iff each 'dimensions' of area is >= the corresponding dimension
    of target, returns 0 (degrees). Otherwise it returns 90 if
    target fits in area when it's rotated 90 degrees. Otherwise it
    returns None.
    """
    if area['dimensions']['x'] >= target['dimensions']['x'] and \
            area['dimensions']['y'] >= target['dimensions']['y'] and \
            area['dimensions']['z'] >= target['dimensions']['z']:
        return 0
    elif area['dimensions']['x'] >= target['dimensions']['z'] and \
            area['dimensions']['y'] >= target['dimensions']['y'] and \
            area['dimensions']['z'] >= target['dimensions']['x']:
        return 90
    else:
        return None


def can_contain(
    container: Dict[str, Any],
    definition_a: Dict[str, Any],
    definition_b: Dict[str, Any] = None
) -> Optional[Tuple[int, List[float]]]:
    """Return the index of the container's "enclosedAreas" that all
     objects fit in, or None if they all do not fit in any of the
     enclosedAreas (or if the container doesn't have any). Does not
     try any rotation to see if that makes it possible to fit.
    """
    if 'enclosedAreas' not in container:
        return None
    for area_index in range(len(container['enclosedAreas'])):
        enclosed_area = container['enclosedAreas'][area_index]
        angles = []
        fits = True
        for definition in [definition_a, definition_b]:
            if definition:
                angle = can_enclose(enclosed_area, definition)
                if angle is None:
                    fits = False
                    break
                angles.append(angle)
            else:
                angles.append(None)
        if fits:
            return area_index, angles
    return None


def can_contain_both(
    container: Dict[str, Any],
    definition_a: Dict[str, Any],
    definition_b: Dict[str, Any]
) -> Optional[Tuple[int, List[float], Orientation]]:
    if 'enclosedAreas' not in container:
        return None
    for area_index in range(len(container['enclosedAreas'])):
        enclosed_area = container['enclosedAreas'][area_index]

        ax = definition_a['dimensions']['x']
        bx = definition_b['dimensions']['x']
        az = definition_a['dimensions']['z']
        bz = definition_b['dimensions']['z']
        cx = enclosed_area['dimensions']['x']
        cz = enclosed_area['dimensions']['z']

        # first try side-by-side
        width = ax + bx
        depth = max(az, bz)
        if cx >= width and cz >= depth:
            return area_index, [0, 0], Orientation.SIDE_BY_SIDE

        # rotate b 90 degrees
        width = ax + bz
        depth = max(az, bx)
        if cx >= width and cz >= depth:
            return area_index, [0, 90], Orientation.SIDE_BY_SIDE

        # rotate a 90 degrees
        width = az + bx
        depth = max(ax, bz)
        if cx >= width and cz >= depth:
            return area_index, [0, 0], Orientation.SIDE_BY_SIDE

        # rotate both 90 degrees
        width = az + bz
        depth = max(ax, bx)
        if cx >= width and cz >= depth:
            return area_index, [0, 90], Orientation.SIDE_BY_SIDE

        # try front-to-back
        width = max(ax, bx)
        depth = az + bz
        if cx >= width and cz >= depth:
            return area_index, [0, 0], Orientation.FRONT_TO_BACK

        # rotate b 90 degrees
        width = max(ax, bz)
        depth = az + bx
        if cx >= width and cz >= depth:
            return area_index, [0, 90], Orientation.FRONT_TO_BACK

        # rotate a 90 degrees
        width = max(az, bx)
        depth = ax + bz
        if cx >= width and cz >= depth:
            return area_index, [90, 0], Orientation.FRONT_TO_BACK

        # rotate both 90 degrees
        width = max(az, bz)
        depth = ax + bx
        if cx >= width and cz >= depth:
            return area_index, [90, 90], Orientation.FRONT_TO_BACK

        return None