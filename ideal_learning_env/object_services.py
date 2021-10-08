import random
from typing import DefaultDict, Dict, List, NamedTuple, Tuple, Union

from generator import (
    ObjectDefinition,
    base_objects,
    containers,
    geometry,
    util,
)
from ideal_learning_env.defs import ILEDelayException, ILEException


class InstanceDefinitionLocationTuple(NamedTuple):
    """Object that is stored in the object repository.
    """
    # TODO MCS-697 turn into class
    instance: dict
    defintion: ObjectDefinition
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

    FRONT_OF_PERFORMER = "front"
    BACK_OF_PERFORMER = "back"
    BETWEEN_PERFORMER_OBJECT = "between"
    BEHIND_OBJECT_FROM_PERFORMER = "behind"
    ADJACENT_TO_OBJECT = "adjacent"
    IN_CONTAINER = "in"
    IN_CONTAINER_WITH_OBJECT = "in_with"

    @staticmethod
    def get_keyword_location_object_tuple(
        keyword_location,
            defn,
            performer_start: Dict[str, Dict[str, float]],
            bounds: List[List[Dict[str, float]]],
            room_dimensions: Dict[str, float]
    ) -> InstanceDefinitionLocationTuple:
        con_tag = keyword_location.container_label
        obj_tag = keyword_location.relative_object_label
        location = None
        obj_repo = ObjectRepository.get_instance()

        keyword = keyword_location.keyword

        if keyword == KeywordLocation.FRONT_OF_PERFORMER:
            location = geometry.get_location_in_front_of_performer(
                performer_start, defn, room_dimensions=room_dimensions)
            return KeywordLocation._instantiate_object_or_raise(
                defn, location)
        if keyword == KeywordLocation.BACK_OF_PERFORMER:
            location = geometry.get_location_in_back_of_performer(
                performer_start, defn, room_dimensions=room_dimensions)
            return KeywordLocation._instantiate_object_or_raise(
                defn, location)

        if keyword != KeywordLocation.IN_CONTAINER:
            if not obj_tag or not obj_repo.has_label(obj_tag):
                raise ILEDelayException(f"missing object label, {obj_tag}")

            idl = obj_repo.get_one_from_labeled_objects(obj_tag)
            relative_instance = idl.instance
            relative_defn = idl.defintion
            rel_object_location = idl.location

        if (keyword ==
                KeywordLocation.BETWEEN_PERFORMER_OBJECT):
            location = geometry.generate_location_in_line_with_object(
                defn, relative_defn, rel_object_location,
                performer_start, bounds, obstruct=True,
                room_dimensions=room_dimensions)
            return KeywordLocation._instantiate_object_or_raise(
                defn, location)
        if (keyword ==
                KeywordLocation.BEHIND_OBJECT_FROM_PERFORMER):  # noqa
            location = geometry.generate_location_in_line_with_object(
                defn, relative_defn, rel_object_location,
                performer_start, bounds, behind=True,
                room_dimensions=room_dimensions)
            return KeywordLocation._instantiate_object_or_raise(
                defn, location)
        if keyword == KeywordLocation.ADJACENT_TO_OBJECT:
            location = geometry.generate_location_in_line_with_object(
                defn, relative_defn, rel_object_location,
                performer_start, bounds, adjacent=True,
                room_dimensions=room_dimensions)
            return KeywordLocation._instantiate_object_or_raise(
                defn, location)

        if not con_tag or not obj_repo.has_label(con_tag):
            raise ILEDelayException(f"missing container label, {con_tag}")
        idl = obj_repo.get_one_from_labeled_objects(con_tag)
        con_inst = idl.instance
        con_defn = idl.defintion
        temp_loc = geometry.ORIGIN_LOCATION
        obj = util.instantiate_object(defn, temp_loc)

        if keyword == KeywordLocation.IN_CONTAINER:
            indexes = containers.can_contain(con_defn, defn)
            if indexes:
                idx = indexes[0]
                containers.put_object_in_container(
                    obj, con_inst, idx, rotation=indexes[1][0])
                # Location will be None here because its dependent on the
                # parent and shouldn't be used to locate other objects
                return InstanceDefinitionLocationTuple(obj, defn, location)
        if (keyword ==
                KeywordLocation.IN_CONTAINER_WITH_OBJECT):
            tup = containers.can_contain_both(
                con_defn, defn, relative_defn)
            if tup:
                idx = tup[0]
                rots = tup[1]
                orientation = tup[2]
                containers.put_objects_in_container(
                    obj, relative_instance, con_inst, idx,
                    orientation, rots[0], rots[1])
            return InstanceDefinitionLocationTuple(obj, defn, location)

        raise ILEException(
            "Unable to get valid keyword location.  Need to retry.")

    @staticmethod
    def _instantiate_object_or_raise(defn, location):
        if location:
            obj = util.instantiate_object(
                defn, location) if location else None
            if obj:
                return InstanceDefinitionLocationTuple(obj, defn, location)
        raise ILEException("Unable to instantiate object")


class MaterialRestrictions():
    @staticmethod
    def valid_shape_material_or_raise(
            shape: str, material: Union[str, Tuple[str, List[str]]]):
        '''verifies shape and material are valid together or raises an
        ILEException'''
        if not base_objects.is_valid_shape_material(shape, material):
            raise ILEException(
                f"Invalid shape/material combination.  Shape={shape}"
                f" material={material}. "
                f"Possible={base_objects.get_material_restriction(shape)}")

    @staticmethod
    def valid_defn_or_raise(defn):
        shape = defn.type
        for mat in defn.materials or []:
            MaterialRestrictions.valid_shape_material_or_raise(shape, mat)
