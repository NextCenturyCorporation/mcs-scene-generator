import copy
import random
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

from generator import (
    ObjectBounds,
    ObjectDefinition,
    base_objects,
    containers,
    geometry,
    instances,
)
from ideal_learning_env.choosers import choose_random
from ideal_learning_env.defs import ILEDelayException, ILEException

from .numerics import VectorFloatConfig

# All goal targets will be assigned this label automatically
TARGET_LABEL = "target"


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

    _labeled_object_store = DefaultDict(list)

    def clear(self):
        """clears the object repository.
        """
        self._labeled_object_store = DefaultDict(list)

    def has_label(self, label: str):
        return label in self._labeled_object_store

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
                self._labeled_object_store[label].append(obj_defn_loc_tuple)

    def get_one_from_labeled_objects(
            self,
            label: str) -> InstanceDefinitionLocationTuple:
        """Returns one of the objects associated with the label.  If there are
        more than one, one is chosen randomly.  If none exist, returns None"""
        if label and label in self._labeled_object_store:
            objs = self._labeled_object_store[label]
            return random.choice(objs)

    def get_all_from_labeled_objects(
            self, label: str) -> List[InstanceDefinitionLocationTuple]:
        """Returns all objects associated with a given label.  If there are
        none, returns None.
        """
        if label and label in self._labeled_object_store:
            return self._labeled_object_store[label]


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

    @staticmethod
    def get_keyword_location_object_tuple(
        keyword_location,
        definition: ObjectDefinition,
        performer_start: Dict[str, Dict[str, float]],
        bounds: List[ObjectBounds],
        room_dimensions: Dict[str, float]
    ) -> InstanceDefinitionLocationTuple:
        """Create and return an IDL using the given keyword location and
        object definition, or raise an error if unable to position it."""
        instance = instances.instantiate_object(
            definition,
            copy.deepcopy(geometry.ORIGIN_LOCATION)
        )
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
        idl.instance['debug']['positionedBy'] = keyword_location.keyword
        return idl

    @staticmethod
    def move_to_keyword_location(
        keyword_location,
        instance: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds: List[ObjectBounds],
        room_dimensions: Dict[str, float],
        definition: ObjectDefinition = None
    ) -> Dict[str, Any]:
        """Change the position of the given object instance using the given
        keyword location, and return the new location, or raise an error if
        unable to position the object. Definition only needed for containment
        locations. Successful containment locations will return None."""
        con_tag = keyword_location.container_label
        obj_tag = keyword_location.relative_object_label
        obj_repo = ObjectRepository.get_instance()

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
                    f'Cannot find relative object label "{obj_tag}" for '
                    f'keyword location "{keyword}" (maybe you misspelled it?)'
                )

            idl = obj_repo.get_one_from_labeled_objects(obj_tag)
            relative_instance = idl.instance
            relative_defn = idl.definition
            rel_object_location = idl.location
            relative_instance['debug']['positionedBy'] = (
                f'relative_{instance["id"]}_{keyword}'
            )

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
        if keyword in [KeywordLocation.ON_OBJECT,
                       KeywordLocation.ON_OBJECT_CENTERED]:
            try:
                location = geometry.generate_location_on_object(
                    instance,
                    relative_instance, performer_start,
                    bounds, room_dimensions=room_dimensions,
                    center=(keyword == KeywordLocation.ON_OBJECT_CENTERED))
            except Exception:
                # If the object is too big to be on top of the relative object,
                # retry generating the scene, in case the object(s) are random.
                raise ILEException(
                    'Object on top too big for object underneath. Retrying...'
                )
            return KeywordLocation._move_instance_or_raise_error(
                instance, location, keyword)

        if not con_tag or not obj_repo.has_label(con_tag):
            raise ILEDelayException(
                f'Cannot find container object label "{con_tag}" for '
                f'keyword location "{keyword}" (maybe you misspelled it?)'
            )

        idl = obj_repo.get_one_from_labeled_objects(con_tag)
        con_inst = idl.instance
        con_defn = idl.definition
        con_inst['debug']['positionedBy'] = (
            f'relative_{instance["id"]}_{keyword}'
        )

        if keyword == KeywordLocation.IN_CONTAINER:
            indexes = containers.can_contain(con_defn, definition)
            if indexes:
                idx = indexes[0]
                containers.put_object_in_container(
                    instance, con_inst, idx, rotation=indexes[1][0])
                # Location will be None here because its dependent on the
                # parent and shouldn't be used to locate other objects
                return None
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
            return None

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
                f'with keyword location: "{keyword}" because location is null'
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


#  TODO MCS-812 Move to some utility area?
def get_target_object(scene):
    tgt = None
    goal = scene.get('goal', {})
    metadata = goal.get('metadata', {})
    tar = metadata.get('target', {})
    targetId = tar.get('id', {})
    for o in scene.get('objects', []):
        if o.get('id', '') == targetId:
            tgt = o
            break
    return tgt


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
    objs = objs if isinstance(objs, list) else [objs]
    for obj in objs:
        debug = obj.get('debug', {})
        debug['random_position'] = random
