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
    Tuple,
    TypeVar,
    Union,
)

from machine_common_sense.config_manager import PerformerStart, Vector3d

from generator import (
    ObjectBounds,
    ObjectDefinition,
    base_objects,
    containers,
    geometry,
    instances,
)
from ideal_learning_env.choosers import choose_random
from ideal_learning_env.defs import (
    ILEDelayException,
    ILEException,
    return_list,
)

from .numerics import MinMaxFloat, VectorFloatConfig

logger = logging.getLogger(__name__)

DEBUG_FINAL_POSITION_KEY = 'final_position'


class InstanceDefinitionLocationTuple(NamedTuple):
    """Object that is stored in the object repository.
    """
    # TODO MCS-697 turn into class
    instance: dict
    definition: ObjectDefinition
    # TODO MCS-698 turn into class
    location: dict


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
            labels: Union[str, List[str]]):
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

    @staticmethod
    def get_keyword_location_object_tuple(
        keyword_location,
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
        if keyword_location.keyword == KeywordLocation.ASSOCIATED_WITH_AGENT:
            location = None
            KeywordLocation.associate_with_agent(keyword_location, instance)
        else:
            # Location may be None; will raise an error if unable to position.
            location = KeywordLocation.move_to_keyword_location(
                keyword_location,
                instance,
                performer_start,
                bounds,
                room_dimensions,
                definition
            )
        idl = InstanceDefinitionLocationTuple(instance, definition, location)
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
                f'keyword location "{keyword_location.keyword}"')
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
        keyword_location,
        instance: Dict[str, Any],
        performer_start: PerformerStart,
        bounds: List[ObjectBounds],
        room_dimensions: Vector3d,
        definition: ObjectDefinition = None
    ) -> Dict[str, Any]:
        """Change the position of the given object instance using the given
        keyword location, and return the new location, or raise an error if
        unable to position the object. Definition only needed for containment
        locations. Successful containment locations will return None."""
        con_tag = keyword_location.container_label
        obj_tag = keyword_location.relative_object_label
        obj_repo = ObjectRepository.get_instance()

        # TODO MCS-815 or MCS-1236
        # All uses below are in the generator folder and are not going to be
        # updated to use classes yet.
        performer_start = performer_start.dict()
        room_dimensions = room_dimensions.dict()

        keyword = keyword_location.keyword

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

        if keyword != KeywordLocation.IN_CONTAINER:
            if not obj_tag or not obj_repo.has_label(obj_tag):
                raise ILEDelayException(
                    f'{instance["type"]} cannot find relative object label '
                    f'"{obj_tag}" for keyword location "{keyword}"'
                )

            idl = obj_repo.get_one_from_labeled_objects(obj_tag)
            relative_instance = idl.instance
            relative_defn = idl.definition
            rel_object_location = idl.location
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
        if (keyword ==
                KeywordLocation.BEHIND_OBJECT_FROM_PERFORMER):  # noqa
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
            location = geometry.generate_location_in_line_with_object(
                instance,
                relative_defn or relative_instance,
                rel_object_location,
                performer_start,
                bounds,
                adjacent=True,
                room_dimensions=room_dimensions
            )
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if keyword == KeywordLocation.OPPOSITE_X:
            location = copy.deepcopy(rel_object_location)
            location['position']['x'] *= -1
            location['position']['y'] -= (
                relative_instance['debug']['positionY'])
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if keyword == KeywordLocation.OPPOSITE_Z:
            location = copy.deepcopy(rel_object_location)
            location['position']['z'] *= -1
            location['position']['y'] -= (
                relative_instance['debug']['positionY'])
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)
        if keyword in [KeywordLocation.ON_OBJECT,
                       KeywordLocation.ON_OBJECT_CENTERED]:
            all_idls = obj_repo.get_all_from_labeled_objects(obj_tag)
            random.shuffle(all_idls)
            attempts = 0
            for idl in all_idls:
                try:
                    location = geometry.generate_location_on_object(
                        instance,
                        relative_instance, performer_start,
                        bounds, room_dimensions=room_dimensions,
                        center=(keyword == KeywordLocation.ON_OBJECT_CENTERED))
                    relative_instance = idl.instance
                    relative_defn = idl.definition
                    rel_object_location = idl.location
                    relative_instance['debug'][DEBUG_FINAL_POSITION_KEY] = True
                except Exception:
                    attempts += 1
                    if attempts == len(all_idls):
                        # If the object is too big to be on top of all
                        # relative objects, retry generating the scene
                        raise ILEException(
                            'Object on top too big for object underneath.'
                            'Retrying...')
                    # If the object is too big to be on top of the relative
                    # object, retry with another realtive object in the scene
                    continue
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)

        if not con_tag or not obj_repo.has_label(con_tag):
            raise ILEDelayException(
                f'{instance["type"]} cannot find container object label '
                f'"{con_tag}" for '
                f'keyword location "{keyword}"'
            )

        idl = obj_repo.get_one_from_labeled_objects(con_tag)
        con_inst = idl.instance
        con_defn = idl.definition
        con_inst['debug'][DEBUG_FINAL_POSITION_KEY] = True

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

                if(positioned_by == 'mechanism' and
                   con_inst.get('moves') is not None):
                    ctr_moves = con_inst.get('moves')
                    moves = instance.get('moves', [])
                    for ctr_move in ctr_moves:
                        moves.append(copy.deepcopy(ctr_move))

                    instance['moves'] = moves
                    instance['kinematic'] = con_inst['kinematic']
                    if(con_inst.get('togglePhysics') is not None):
                        ctr_tog_list = con_inst.get('togglePhysics')
                        tog_list = instance.get('togglePhysics', [])
                        for ctr_tog in ctr_tog_list:
                            tog_list.append(copy.deepcopy(ctr_tog))

                        instance['togglePhysics'] = tog_list

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
                    keyword_location.keyword)
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
        instance: Dict[str, Any],
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


def add_random_placement_tag(objs: Union[list, dict],
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
    add_x: Union[
        float, MinMaxFloat, List[Union[float, MinMaxFloat]]
    ] = None
    add_z: Union[
        float, MinMaxFloat, List[Union[float, MinMaxFloat]]
    ] = None
    label: Union[str, List[str]] = None
    use_x: Union[bool, List[bool]] = None
    use_z: Union[bool, List[bool]] = None
    view_angle_x: Union[bool, List[bool]] = None
