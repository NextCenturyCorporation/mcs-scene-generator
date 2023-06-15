import copy
import logging
import random
from dataclasses import dataclass
from typing import (
    Any,
    DefaultDict,
    Dict,
    List,
    NamedTuple,
    Optional,
    Tuple,
    TypeVar,
    Union
)

from machine_common_sense.config_manager import PerformerStart, Vector3d
from shapely import affinity

from generator import (
    ObjectBounds,
    ObjectDefinition,
    Scene,
    SceneException,
    SceneObject,
    base_objects,
    containers,
    geometry,
    instances
)

from .choosers import choose_random
from .defs import (
    ILEConfigurationException,
    ILEDelayException,
    ILEException,
    RandomizableBool,
    RandomizableString,
    return_list
)
from .numerics import (
    RandomizableFloat,
    RandomizableVectorFloat3d,
    VectorFloatConfig
)

logger = logging.getLogger(__name__)

DEBUG_FINAL_POSITION_KEY = 'final_position'


@dataclass
class KeywordLocationConfig():
    """Describes an object's keyword location. Can have the following
    properties:
    - `keyword` (string, or list of strings): The keyword location, which can
    be one of the following:
        - `adjacent` - The object will be placed near another object. The other
        object must be referenced by the 'relative_object_label' field, and the
        distance away from the relative object must be set by the
        `adjacent_distance` field.
        - `adjacent_corner` - The object will be placed near the corner
        referenced by the 'relative_object_label' field.  The corner labels
        are 'front_left' (-X, +Z), 'front_right' (+X, +Z),
        'back_left' (-X, -Z), and 'back_right' (+X, -Z).  The
        distance away from the corner will be determined by the
        `adjacent_distance` field.
        - `adjacent_performer` - The object will be placed next to the
        performer.  The object can be placed in 'front', 'back', left, or
        'right' of the performer using the 'direction'.  The object
        can also be specified to be 'in_reach' or 'out_of_reach' via the
        'distance'.  By default, the object will be placed in a random
        direction, but 'in_reach'.
        other object must be referenced by the 'relative_object_label' field.
        If multiple objects have this label, one will be randomly chosen.
        - `back` - The object will be placed in the 180 degree arc behind the
        performer's start position.
        - `behind` - The object will be placed behind another object, relative
        to the performer's start position.  The other object must be referenced
        by the 'relative_object_label' field.  If multiple objects have this
        label, one will be randomly chosen.
        - `between` - The object will be placed between the performer's start
        position and another object.  The other object must be referenced by
        the 'relative_object_label' field.  If multiple objects have this
        label, one will be randomly chosen.
        - `front` - The object will be placed in a line in front of the
        performer's start position.
        - `in` - The object will be placed inside a container.  The container
        must be referenced by the 'container_label' field.  If multiple objects
        have this label, one will be randomly chosen.
        - `in_with` - The object will be placed inside a container along with
        another object.  The container must be referenced by the
        'container_label' field.  The other object must be referenced by the
        'relative_object_label' field.  If multiple objects have these label,
        one will be randomly chosen for each field.
        - `occlude` - The object will be placed between the performer's start
        position and another object so that this object completely occludes the
        view of the other object.  The other object must be referenced by
        the 'relative_object_label' field.  If multiple objects have this
        label, one will be randomly chosen.
        - `on_center` - The object will be placed on top of another object
        in the center of the bounds.  This option is best for objects the are
        similar in size or for use cases where objects are desired to be
        centered.  The object must be referenced by the 'relative_object_label'
        field.  If multiple objects have this label,
        one will be randomly chosen.
        - `on_top` - The object will be placed on top of another object in a
        random location.  This option is best for when the object is
        significantly smaller than the object it is placed on (I.E. a small
        ball on a large platform).  If the objects are similar in size
        (I.E. two bowls), use 'on_center'.  The object must be referenced by
        the 'relative_object_label' field.  If multiple objects have this
        label, one will be randomly chosen.
        - `opposite_x` - The object will be placed in the exact same location
        as the object referenced by `relative_object_label` except that its x
        location will be on the opposite side of the room. Its rotation will
        also be mirrored, though it can be adjusted using the `rotation`
        property within this keyword location option. There are no adjustments
        to find a valid location if another object already exists in the final
        location.
        - `opposite_z` - The object will be placed in the exact same location
        as the object referenced by `relative_object_label` except that its z
        location will be on the opposite side of the room.  There are no
        adjustments to find a valid location if another object already exists
        in final location.
        - `random` - The object will be positioned in a random location, as if
        it did not have a keyword location.
        - `associated_with_agent` - This object will be held by an agent
        referenced by the 'relative_object_label' field.
        - `along_wall` - This object will be placed along a wall
        referenced by the 'relative_object_label' field.  The wall labels are
        'front_wall', 'back_wall', 'left_wall, and 'right_wall'.  If no wall is
        provided, a wall will be chosen at random.
    - `adjacent_distance` (VectorFloatConfig, or list of VectorFloatConfigs):
    The X/Z distance in global coordinates between this object's position and
    the relative object's (or corner's) position. Only usable with the
    `adjacent` or `adjacent_corner` keyword. By default, this object will be
    positioned 0.1 away from the relative object (or corner) in a random,
    valid direction.  Note that if using this for a corner with the
    `surrounded_by_lava` property, you'll need to use the same dimensions for
    x/z and that they're divisible by 0.5 to make sure they line up correctly
    with the lava island.
    - `container_label` (string, or list of strings): The label of a container
    object that already exists in your configuration. Only required by some
    keyword locations.
    - `relative_object_label` (string, or list of strings): The label of a
    second object that already exists in your configuration. Only required by
    some keyword locations.
    - `position_relative_to_start` (VectorFloatConfig, or list of
    VectorFloatConfigs): Currently only supported with the `on_center` keyword:
    How much to translate object from the center position of the relative
    object along the x and z axis. This works like a percentage, represented
    as x/z values that range from -1.0 to 1.0 (with both of those values being
    furthest from the center in either direction). Note that this assumes the
    relative object has a rectangular boundary.

    """
    keyword: RandomizableString = None
    container_label: RandomizableString = None
    relative_object_label: RandomizableString = None
    distance: RandomizableString = None
    direction: RandomizableString = None
    position_relative_to_start: RandomizableVectorFloat3d = None
    adjacent_distance: RandomizableVectorFloat3d = None
    rotation: RandomizableVectorFloat3d = None


class InstanceDefinitionLocationTuple(NamedTuple):
    """Object that is stored in the object repository.
    """
    instance: SceneObject
    definition: ObjectDefinition
    # TODO MCS-698 turn into class
    location: Dict[str, Any]


class ObjectRepository():
    """
    Repository for objects for the ILE.  Used such that components can
    reference other objects.
    """
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if ObjectRepository.__instance is None:
            ObjectRepository()
        return ObjectRepository.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ObjectRepository.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ObjectRepository.__instance = self
        self.clear()

    def clear(self):
        """clears the object repository.
        """
        self._id_object_store = {}
        self._labeled_object_store = DefaultDict(list)

    def has_label(self, label: str):
        return (label in self._labeled_object_store or
                label in self._id_object_store)

    def add_to_labeled_objects(
            self,
            obj_defn_loc_tuple: InstanceDefinitionLocationTuple,
            labels: RandomizableString):
        """Adds an object instance, definition, and location to a single or
        multiple labels.
        """
        if labels and obj_defn_loc_tuple:
            labels = labels if isinstance(labels, list) else [labels]
            for label in labels:
                logger.debug(
                    f"Adding object '{obj_defn_loc_tuple.instance['id']}' with"
                    f" label '{label}' to the object repository"
                )
                self._labeled_object_store[label].append(obj_defn_loc_tuple)
        if obj_defn_loc_tuple and obj_defn_loc_tuple.instance:
            if id := obj_defn_loc_tuple.instance.get('id'):
                self._id_object_store[id] = obj_defn_loc_tuple

    def get_one_from_labeled_objects(
            self,
            label: str) -> InstanceDefinitionLocationTuple:
        """Returns one of the objects associated with the label.  If there are
        more than one, one is chosen randomly.  If none exist, returns None"""
        if label and label in self._id_object_store:
            return self._id_object_store.get(label)
        if label and label in self._labeled_object_store:
            objs = self._labeled_object_store[label]
            return random.choice(objs)

    def get_all_from_labeled_objects(
            self, label: str) -> List[InstanceDefinitionLocationTuple]:
        """Returns all objects associated with a given label.  If there are
        none, returns None.
        """
        if label and label in self._id_object_store:
            return [self._id_object_store.get(label)]
        if label and label in self._labeled_object_store:
            return self._labeled_object_store[label]

    def remove_from_labeled_objects(self, instance_id: str, label: str):
        """Removes the object with the given ID from the given label."""
        if label and label in self._labeled_object_store:
            logger.debug(f'Removing object {instance_id} from label {label}')
            self._labeled_object_store[label] = [
                idl for idl in self._labeled_object_store[label]
                if idl.instance['id'] != instance_id
            ]


class KeywordLocation():
    ADJACENT_TO_OBJECT = "adjacent"
    ADJACENT_TO_PERFORMER = "adjacent_performer"
    BACK_OF_PERFORMER = "back"
    BEHIND_OBJECT_FROM_PERFORMER = "behind"
    BETWEEN_PERFORMER_OBJECT = "between"
    FRONT_OF_PERFORMER = "front"
    IN_CONTAINER = "in"
    IN_CONTAINER_WITH_OBJECT = "in_with"
    OCCLUDE_OBJECT = "occlude"
    ON_OBJECT = "on_top"
    ON_OBJECT_CENTERED = "on_center"
    RANDOM = "random"
    ASSOCIATED_WITH_AGENT = "associated_with_agent"
    OPPOSITE_X = "opposite_x"
    OPPOSITE_Z = "opposite_z"
    ALONG_WALL = "along_wall"
    ADJACENT_TO_CORNER = "adjacent_corner"

    ADJACENT_TO_PERFORMER_FRONT = "front"
    ADJACENT_TO_PERFORMER_BACK = "back"
    ADJACENT_TO_PERFORMER_LEFT = "left"
    ADJACENT_TO_PERFORMER_RIGHT = "right"
    ADJACENT_TO_PERFORMER_IN_REACH = "in_reach"
    ADJACENT_TO_PERFORMER_OUT_OF_REACH = "out_of_reach"

    ADJACENT_TO_PERFORMER_DIRECTION_DEFAULT = [
        ADJACENT_TO_PERFORMER_FRONT,
        ADJACENT_TO_PERFORMER_BACK,
        ADJACENT_TO_PERFORMER_LEFT,
        ADJACENT_TO_PERFORMER_RIGHT]

    ADJACENT_TO_PERFORMER_DISTANCE_DEFAULT = [
        ADJACENT_TO_PERFORMER_IN_REACH]

    @staticmethod
    def get_keyword_location_object_tuple(
        reconciled: KeywordLocationConfig,
        source: KeywordLocationConfig,
        definition: ObjectDefinition,
        performer_start: PerformerStart,
        bounds: List[ObjectBounds],
        room_dimensions: Vector3d
    ) -> InstanceDefinitionLocationTuple:
        """Create and return an IDL using the given keyword location and
        object definition, or raise an error if unable to position it."""
        instance = instances.instantiate_object(
            definition,
            copy.deepcopy(geometry.ORIGIN_LOCATION)
        )
        if reconciled.keyword == KeywordLocation.ASSOCIATED_WITH_AGENT:
            location = None
            KeywordLocation.associate_with_agent(reconciled, instance)
        else:
            # Location may be None; will raise an error if unable to position.
            location = KeywordLocation.move_to_keyword_location(
                reconciled,
                source,
                instance,
                performer_start,
                bounds,
                room_dimensions,
                definition
            )
        idl = InstanceDefinitionLocationTuple(instance, definition, location)
        idl.instance['debug']['positionedBy'] = reconciled.keyword
        idl.instance['debug'][DEBUG_FINAL_POSITION_KEY] = True
        return idl

    @staticmethod
    def associate_with_agent(keyword_location, instance):
        label = keyword_location.relative_object_label
        obj_repo = ObjectRepository.get_instance()
        if not obj_repo.has_label(label):
            raise ILEDelayException(
                f'{instance["type"]} cannot find relative object label '
                f'"{label}" for '
                f'keyword location "{keyword_location.keyword}". '
                f'The relative object label or corresponding '
                f'keyword could be misspelled, invalid, '
                f'or does not exist'
            )
        agent_idl = obj_repo.get_one_from_labeled_objects(label=label)
        agent = agent_idl.instance
        if not agent['id'].startswith('agent'):
            raise ILEException(
                f"Found object with label='{label}' for keyword location "
                f"'{keyword_location.keyword}', but object was not an agent.")
        instance['associatedWithAgent'] = agent['id']
        show = instance['shows'][0]
        show['position'] = agent['shows'][0]['position']
        x = show['position']['x']
        y = show['position']['y']
        z = show['position']['z']
        show['boundingBox'] = ObjectBounds(
            [Vector3d(x=x, y=y, z=z), Vector3d(x=x, y=y, z=z),
             Vector3d(x=x, y=y, z=z), Vector3d(x=x, y=y, z=z)],
            0, 0)

    @staticmethod
    def move_to_keyword_location(
        reconciled: KeywordLocationConfig,
        source: KeywordLocationConfig,
        instance: SceneObject,
        performer_start: PerformerStart,
        bounds: List[ObjectBounds],
        room_dimensions: Vector3d,
        definition: ObjectDefinition = None
    ) -> Dict[str, Any]:
        """Change the position of the given object instance using the given
        keyword location, and return the new location, or raise an error if
        unable to position the object. Definition only needed for containment
        locations. Successful containment locations will return None."""
        con_tag = reconciled.container_label
        obj_tag = reconciled.relative_object_label
        pos_rel_start = reconciled.position_relative_to_start
        obj_repo = ObjectRepository.get_instance()

        # TODO MCS-815 or MCS-1236
        # All uses below are in the generator folder and are not going to be
        # updated to use classes yet.
        performer_start = performer_start.dict()
        room_dimensions = room_dimensions.dict()

        keyword = reconciled.keyword

        if keyword == KeywordLocation.FRONT_OF_PERFORMER:
            location = geometry.get_location_in_front_of_performer(
                performer_start, instance, room_dimensions=room_dimensions)
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if keyword == KeywordLocation.BACK_OF_PERFORMER:
            location = geometry.get_location_in_back_of_performer(
                performer_start, instance, room_dimensions=room_dimensions)
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if keyword == KeywordLocation.ADJACENT_TO_PERFORMER:
            distance_label = reconciled.distance or random.choice(
                KeywordLocation.ADJACENT_TO_PERFORMER_DISTANCE_DEFAULT)
            direction = reconciled.direction or random.choice(
                KeywordLocation.ADJACENT_TO_PERFORMER_DIRECTION_DEFAULT)
            dir_rot = (0 if direction == KeywordLocation.ADJACENT_TO_PERFORMER_FRONT else  # noqa
                       90 if direction == KeywordLocation.ADJACENT_TO_PERFORMER_RIGHT else  # noqa
                       180 if direction == KeywordLocation.ADJACENT_TO_PERFORMER_BACK else  # noqa
                       270 if direction == KeywordLocation.ADJACENT_TO_PERFORMER_LEFT else  # noqa
                       0)
            dist = (random.uniform(0.25, 0.9) if
                    distance_label ==
                    KeywordLocation.ADJACENT_TO_PERFORMER_IN_REACH else
                    random.uniform(1.1, 1.2))

            location = geometry.get_location_adjacent_to_performer(
                performer_start, instance, room_dimensions=room_dimensions,
                distance=dist, direction_rotation=dir_rot)
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if keyword == KeywordLocation.ALONG_WALL:
            wall = obj_tag or [
                geometry.FRONT_WALL_LABEL,
                geometry.BACK_WALL_LABEL,
                geometry.LEFT_WALL_LABEL,
                geometry.RIGHT_WALL_LABEL]
            wall = wall if isinstance(wall, list) else [wall]
            wall = random.choice(wall)
            location = geometry.get_location_along_wall(
                performer_start, wall, instance, room_dimensions)
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)

        if keyword == KeywordLocation.ADJACENT_TO_CORNER:
            # Choose a random corner to use if one isn't specified
            corners = obj_tag or [
                geometry.FRONT_LEFT_CORNER,
                geometry.FRONT_RIGHT_CORNER,
                geometry.BACK_LEFT_CORNER,
                geometry.BACK_RIGHT_CORNER]
            corners = corners if isinstance(corners, list) else [corners]
            random.shuffle(corners)

            # Use all of the configured distances (if any) from the source
            # template, rather than the single randomly chosen distance that
            # will be in the reconciled template.
            distances = return_list(source.adjacent_distance)
            if not distances:
                # By default, position the object 0.1 away from the relative
                # corner in the x or z direction.
                distances = [
                    Vector3d(x=0.1, y=0, z=0.1)
                ]
            # Loop over each configured (or default) distance in a random order
            # and use the first valid adjacent location that's found.
            random.shuffle(distances)
            for distance in distances:
                for corner in corners:
                    location = geometry.get_location_adjacent_to_corner(
                        performer_start, instance, room_dimensions,
                        distance_from_corner=distance, corner_label=corner)
                    if location:
                        break
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)

        if keyword != KeywordLocation.IN_CONTAINER:
            if not obj_tag or not obj_repo.has_label(obj_tag):
                raise ILEDelayException(
                    f'{instance["type"]} cannot find relative object label '
                    f'"{obj_tag}" for keyword location "{keyword}". '
                    f'The relative object label or corresponding '
                    f'keyword could be misspelled, invalid, '
                    f'or does not exist'
                )

            idl = obj_repo.get_one_from_labeled_objects(obj_tag)
            relative_instance = idl.instance
            relative_defn = idl.definition
            rel_object_location = idl.location
            relative_instance['debug']['positionedBy'] = (
                relative_instance['debug'].get('positionedBy') or
                'relative_label'
            )
            relative_instance['debug'][DEBUG_FINAL_POSITION_KEY] = True

        if keyword in [
            KeywordLocation.BETWEEN_PERFORMER_OBJECT,
            KeywordLocation.OCCLUDE_OBJECT,
        ]:
            location = geometry.generate_location_in_line_with_object(
                instance,
                relative_defn or relative_instance,
                rel_object_location,
                performer_start,
                bounds,
                obstruct=(keyword == KeywordLocation.OCCLUDE_OBJECT),
                room_dimensions=room_dimensions
            )
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if (keyword == KeywordLocation.BEHIND_OBJECT_FROM_PERFORMER):
            location = geometry.generate_location_in_line_with_object(
                instance,
                relative_defn or relative_instance,
                rel_object_location,
                performer_start,
                bounds,
                behind=True,
                room_dimensions=room_dimensions
            )
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if keyword == KeywordLocation.ADJACENT_TO_OBJECT:
            # Use all of the configured distances (if any) from the source
            # template, rather than the single randomly chosen distance that
            # will be in the reconciled template.
            distances = return_list(source.adjacent_distance)
            if not distances:
                # By default, position the object 0.1 away from the relative
                # object in a random direction: +X, -X, +Z, or -Z.
                distances = [
                    Vector3d(x=0.1, y=0, z=0),
                    Vector3d(x=-0.1, y=0, z=0),
                    Vector3d(x=0, y=0, z=0.1),
                    Vector3d(x=0, y=0, z=-0.1)
                ]
            # Loop over each configured (or default) distance in a random order
            # and use the first valid adjacent location that's found.
            random.shuffle(distances)
            for distance in distances:
                location = geometry.generate_location_adjacent_to(
                    instance,
                    relative_instance,
                    distance.x,
                    distance.z,
                    performer_start,
                    bounds,
                    room_dimensions=room_dimensions
                )
                if location:
                    break
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if keyword == KeywordLocation.OPPOSITE_X:
            location = copy.deepcopy(rel_object_location)
            location['position']['x'] *= -1
            location['position']['y'] += (
                instance['debug']['positionY'] -
                relative_instance['debug']['positionY']
            )
            # Mirror the object's rotation.
            mirrored_rotation = round(-location['rotation']['y'], 2) % 360
            location['rotation']['y'] = (
                mirrored_rotation +
                # Add the configured rotation, if any.
                (reconciled.rotation or Vector3d()).y
            )
            # Save the mirrored rotation for use elsewhere in the codebase.
            instance['debug']['mirroredRotation'] = mirrored_rotation
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if keyword == KeywordLocation.OPPOSITE_Z:
            location = copy.deepcopy(rel_object_location)
            location['position']['z'] *= -1
            location['position']['y'] += (
                instance['debug']['positionY'] -
                relative_instance['debug']['positionY']
            )
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if keyword in [KeywordLocation.ON_OBJECT,
                       KeywordLocation.ON_OBJECT_CENTERED]:
            all_idls = obj_repo.get_all_from_labeled_objects(obj_tag)
            random.shuffle(all_idls)
            attempts = 0
            if (keyword == KeywordLocation.ON_OBJECT_CENTERED and
                    pos_rel_start is not None):

                pos_rel_start.x = (
                    pos_rel_start.x if pos_rel_start.x is not None else 0)
                pos_rel_start.z = (
                    pos_rel_start.z if pos_rel_start.z is not None else 0)

                if (pos_rel_start.x < -1.0 or pos_rel_start.x > 1.0 or
                        pos_rel_start.z < -1.0 or pos_rel_start.z > 1.0):
                    raise ILEConfigurationException(
                        "position_relative_to_start x and z values must "
                        "be within the range of -1.0 and 1.0.")
            for idl in all_idls:
                try:
                    location = geometry.generate_location_on_object(
                        instance,
                        relative_instance, performer_start,
                        bounds, room_dimensions=room_dimensions,
                        center=(keyword == KeywordLocation.ON_OBJECT_CENTERED),
                        position_relative_to_start=pos_rel_start)
                    relative_instance = idl.instance
                    relative_defn = idl.definition
                    rel_object_location = idl.location
                    relative_instance['debug']['positionedBy'] = (
                        relative_instance['debug'].get('positionedBy') or
                        'relative_label'
                    )
                    relative_instance['debug'][DEBUG_FINAL_POSITION_KEY] = True
                    if relative_instance['type'] == 'rotating_cog':
                        relative_id = relative_instance['id']
                        instance['debug']['isRotatedBy'] = relative_id
                except Exception as e:
                    attempts += 1
                    if attempts == len(all_idls):
                        # If the object is too big to be on top of all
                        # relative objects, retry generating the scene
                        raise ILEException(
                            'Object on top too big for object underneath.'
                            'Retrying...'
                        ) from e
                    # If the object is too big to be on top of the relative
                    # object, retry with another realtive object in the scene
                    continue
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)

        if not con_tag or not obj_repo.has_label(con_tag):
            raise ILEDelayException(
                f'{instance["type"]} cannot find container object label '
                f'"{con_tag}" for '
                f'keyword location "{keyword}". '
                f'The container object label or corresponding '
                f'keyword could be misspelled, invalid, '
                f'or does not exist'
            )

        idl = obj_repo.get_one_from_labeled_objects(con_tag)
        con_inst = idl.instance
        con_defn = idl.definition

        if keyword == KeywordLocation.IN_CONTAINER:
            indexes = containers.can_contain(con_defn, definition)
            if indexes:
                idx = indexes[0]
                containers.put_object_in_container(
                    instance, con_inst, idx, rotation=indexes[1][0])

                # Make sure containers positioned by placers apply
                # their rules to any objects inside of them.
                #
                # Note: 'moves' and 'positionedBy' should be enough for
                # now to differentiate this case, but this could change
                # in the future.
                positioned_by = con_inst['debug'].get('positionedBy', None)

                if (positioned_by == 'mechanism' and
                        con_inst.get('moves') is not None):
                    ctr_moves = con_inst.get('moves')
                    moves = instance.get('moves', [])
                    for ctr_move in ctr_moves:
                        moves.append(copy.deepcopy(ctr_move))

                    instance['moves'] = moves
                    instance['kinematic'] = con_inst['kinematic']
                    if (con_inst.get('togglePhysics') is not None):
                        ctr_tog_list = con_inst.get('togglePhysics')
                        tog_list = instance.get('togglePhysics', [])
                        for ctr_tog in ctr_tog_list:
                            tog_list.append(copy.deepcopy(ctr_tog))

                        instance['togglePhysics'] = tog_list

                con_inst['debug']['positionedBy'] = (
                    positioned_by or 'container_label'
                )
                con_inst['debug'][DEBUG_FINAL_POSITION_KEY] = True

                # Location will be None here because its dependent on the
                # parent and shouldn't be used to locate other objects
                return None
            else:
                raise ILEException(
                    f'Unable to find a valid keyword location because the '
                    f'container cannot hold the object:'
                    f'\nCONTAINER={con_defn}'
                    f'\nOBJECT={definition}'
                )
        if keyword == KeywordLocation.IN_CONTAINER_WITH_OBJECT:
            tup = containers.can_contain_both(
                con_defn,
                definition,
                relative_defn
            )
            if tup:
                idx = tup[0]
                rots = tup[1]
                orientation = tup[2]
                containers.put_objects_in_container(
                    instance, relative_instance, con_inst, idx,
                    orientation, rots[0], rots[1])
                relative_instance['debug']['positionedBy'] = (
                    relative_instance['debug'].get('positionedBy') or
                    'relative_label'
                )
                con_inst['debug']['positionedBy'] = (
                    con_inst['debug'].get('positionBy') or 'container_label'
                )
                con_inst['debug'][DEBUG_FINAL_POSITION_KEY] = True
                return None
            else:
                raise ILEException(
                    f'Unable to find a valid keyword location because the '
                    f'container cannot hold the object with a relative object:'
                    f'\nCONTAINER={con_defn}'
                    f'\nOBJECT={definition}'
                    f'\nRELATIVE={relative_defn}'
                )

        raise ILEException(
            "Unable to get valid keyword location.  Need to retry.")

    @staticmethod
    def _move_instance_or_raise_error(
        instance: SceneObject,
        location: Dict[str, Any],
        keyword: str
    ) -> Dict[str, Any]:
        if not location:
            raise ILEException(
                f'Unable to position an object of type "{instance["type"]}" '
                f'with keyword location: "{keyword}" because a valid location'
                f' could not be found.'
            )
        geometry.move_to_location(instance, location)
        return location


class MaterialRestrictions():
    @staticmethod
    def valid_shape_material_or_raise(
            shape: str, material: Union[str, Tuple[str, List[str]]]):
        '''verifies shape and material are valid together or raises an
        ILEException'''
        if not base_objects.is_valid_shape_material(shape, material):
            mat_res = base_objects.get_material_restriction_strings(shape)
            raise ILEException(
                f"Invalid shape/material combination.  Shape={shape}"
                f" material={material}. "
                f"Possible={mat_res}")

    @staticmethod
    def valid_defn_or_raise(defn):
        shape = defn.type
        for mat in defn.materials or []:
            MaterialRestrictions.valid_shape_material_or_raise(shape, mat)


T = TypeVar('T')


def reconcile_template(default_template: T, source_template: T) -> T:
    '''Takes 2 templates (one of our data classes that represents input data
    that usually is suffixed by `Config`).  The first template contains the
    default values.  This could MinMaxFloat/Int, arrays for choices or single
    values.  Some values in the default template can be None and then should be
    managed inside the specific component that uses that template.  This is
    common for materials and values that are dependent on other values.  The
    other template is the template produced from the input config file.'''
    # Move to a more generic location so that other components can use it
    if source_template is None:
        obj_values = default_template.__class__()
    else:
        obj_values = choose_random(source_template)
    for key in vars(default_template):
        val = getattr(obj_values, key, None)
        if val is None:
            new_val = getattr(default_template, key, None)
            if new_val:
                new_val = choose_random(new_val)
            setattr(obj_values, key, new_val)
    return obj_values


def add_random_placement_tag(objs: Union[SceneObject, List[SceneObject]],
                             template) -> None:
    random = True
    if hasattr(template, 'position'):
        pos = getattr(template, 'position')
        random = pos is None or not isinstance(pos, VectorFloatConfig)
        if not random:
            rand_x = pos.x is None or not isinstance(pos.x, (int, float))
            rand_z = pos.z is None or not isinstance(pos.z, (int, float))
            random = rand_x or rand_z
    if hasattr(template, 'position_relative'):
        position_relative = return_list(getattr(template, 'position_relative'))
        for config in position_relative:
            if hasattr(config, 'label'):
                relative_labels = getattr(config, 'label')
                if random and relative_labels:
                    random = False
    objs = objs if isinstance(objs, list) else [objs]
    for obj in objs:
        debug = obj.get('debug', {})
        debug['random_position'] = random


@dataclass
class RelativePositionConfig():
    """
    Configure this object's position relative to an existing object in your
    scene. All options require the relative object's `label` to be configured.

    - `add_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The value added to this object's X
    position after being positioned at the relative object's X position.
    Default: 0
    - `add_z` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The value added to this object's Z
    position after being positioned at the relative object's Z position.
    Default: 0
    - `label` (str, or list of strs): The label for an existing object to use
    as the "relative object" for positioning this object. Labels are not
    unique, so if multiple objects share the same label, the ILE will choose
    one of the available objects for each scene it generates.
    - `use_x` (bool, or list of bools): Whether to use the relative object's
    X position for this object's X position. Default: if `use_z` is not set,
    then `true`; otherwise, `false`
    - `use_z` (bool, or list of bools): Whether to use the relative object's
    Z position for this object's Z position. Default: if `use_x` is not set,
    then `true`; otherwise, `false`
    - `view_angle_x` (bool, or list of bools): Whether to adjust this object's
    X position based on the angle of view from the performer agent's starting
    position and the relative object's position. Useful for positioning objects
    behind occluders (especially in the passive physics tasks).
    """
    add_x: RandomizableFloat = None
    add_z: RandomizableFloat = None
    label: RandomizableString = None
    use_x: RandomizableBool = None
    use_z: RandomizableBool = None
    view_angle_x: RandomizableBool = None


def get_step_after_movement(labels: RandomizableString) -> int:
    """Return the step after the last step on which all the objects for all the
    given labels are scripted to end moving or rotating. Raise an
    ILEDelayException if any of the labels do not have objects."""
    object_repository = ObjectRepository.get_instance()
    last_step = 0
    for label in return_list(labels):
        if not label:
            continue
        objects = object_repository.get_all_from_labeled_objects(label)
        if not objects:
            raise ILEDelayException(
                f'Cannot find any existing objects with label: {label}'
            )
        for idl in objects:
            step = instances.get_earliest_active_step(idl.instance)
            step = instances.get_last_move_or_rotate_step(idl.instance)
            if step > last_step:
                last_step = step
    return last_step + 1


def get_step_after_movement_or_start(labels: RandomizableString) -> int:
    """Return 1 if all the objects for all the given labels are scripted to
    begin moving and rotating AFTER step 1 (or not at all); otherwise return
    the step after the last step on which all the objects for all the given
    labels are scripted to end moving or rotating. Raise an ILEDelayException
    if any of the labels do not have objects."""
    object_repository = ObjectRepository.get_instance()
    last_step = 0
    earliest_step = 0
    for label in return_list(labels):
        if not label:
            continue
        objects = object_repository.get_all_from_labeled_objects(label)
        if not objects:
            raise ILEDelayException(
                'Cannot find any existing objects with label: {label}'
            )
        for idl in objects:
            step = instances.get_earliest_active_step(idl.instance)
            if step >= 0 and (earliest_step == 0 or step < earliest_step):
                earliest_step = step
            step = instances.get_last_move_or_rotate_step(idl.instance)
            if step > last_step:
                last_step = step
    return (last_step + 1) if earliest_step == 1 else 1


def calculate_rotated_position(
    scene: Scene,
    lid_step_begin: int,
    container: SceneObject
) -> Optional[Dict[str, float]]:
    """Calculate and return the position for the given object at the given
    step, assuming that the object is on top of a rotating turntable."""

    # Assumes the container was positioned using the "on_center" or
    # "on_top" keyword location, which would set isRotatedBy
    # (see KeywordLocation.move_to_keyword_location)
    if not container['debug'].get('isRotatedBy'):
        return None

    turntable = scene.get_object_by_id(container['debug']['isRotatedBy'])
    if not turntable.get('rotates') or not turntable['rotates'][0]:
        return None

    # Estimate the number of steps it will take for the lid placer to move.
    container_position_y = container['shows'][0]['position']['y']
    container_dimensions_y = container['debug']['dimensions']['y']
    container_standing_y = container['debug']['positionY']
    container_top = (
        container_position_y + container_dimensions_y -
        container_standing_y
    )
    placer_steps = (scene.room_dimensions.y - container_top) / 0.25

    # Placing the lid during rotation is currently unsupported.
    rotate = turntable['rotates'][0]
    if (
        lid_step_begin > 0 and
        rotate['stepBegin'] <= (lid_step_begin + placer_steps) and
        rotate['stepEnd'] >= (lid_step_begin + placer_steps)
    ):
        raise SceneException(
            f'Cannot place separate lid at step {lid_step_begin} '
            f'and estimated placer movement steps {placer_steps} '
            f'because container {container["id"]} is on top '
            f'of turntable {turntable["id"]} which is rotating '
            f'between steps {rotate["stepBegin"]} and '
            f'{rotate["stepEnd"]}'
        )

    # If the lid will be placed after the turntable completely finishes
    # rotating, then calculate the new position for the container.
    turntable_position = turntable['shows'][0]['position']
    turntable_x = turntable_position['x']
    turntable_z = turntable_position['z']
    if (
        lid_step_begin > 0 and
        (lid_step_begin + placer_steps) > rotate['stepEnd']
    ):
        rotate_steps = rotate['stepEnd'] - rotate['stepBegin'] + 1
        rotate_degrees = rotate['vector']['y'] * rotate_steps
        rotated_polygon = affinity.rotate(
            container['shows'][0]['boundingBox'].polygon_xz,
            -rotate_degrees,
            origin=(turntable_x, turntable_z)
        )
        rotated_point = rotated_polygon.centroid.coords[0]
        container_position = {
            'x': rotated_point[0],
            'y': container_position_y,
            'z': rotated_point[1]
        }
        return container_position

    # Otherwise, no new position is needed.
    return None
