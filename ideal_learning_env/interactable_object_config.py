from dataclasses import dataclass
from typing import Any, Dict, List, Union

from generator import (
    MAX_TRIES,
    ObjectBounds,
    ObjectDefinition,
    base_objects,
    geometry,
    instances,
)
from ideal_learning_env.defs import ILEException, ILESharedConfiguration
from ideal_learning_env.object_services import (
    InstanceDefinitionLocationTuple,
    KeywordLocation,
    ObjectRepository,
)

from .choosers import (
    choose_position,
    choose_rotation,
    choose_scale,
    choose_shape_material,
)
from .numerics import (
    MinMaxFloat,
    MinMaxInt,
    VectorFloatConfig,
    VectorIntConfig,
)


@dataclass
class KeywordLocationConfig():
    """Describes an object's keyword location. Can have the following
    properties:
    - `keyword` (string, or list of strings): The keyword location, which can
    be one of the following:
        - `adjacent` - The object will be placed next to another object.  The
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
    - `container_label` (string, or list of strings): The label of a container
    object that already exists in your configuration. Only required by some
    keyword locations.
    - `relative_object_label` (string, or list of strings): The label of a
    second object that already exists in your configuration. Only required by
    some keyword locations.
    """
    keyword: Union[str, List[str]] = None
    container_label: Union[str, List[str]] = None
    relative_object_label: Union[str, List[str]] = None


@dataclass
class InteractableObjectConfig():
    """Represents the template for a specific object (with one or more possible
    variations) that will be added to each scene. Each template can have the
    following optional properties:
    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict): The number
    of objects with this template to generate in each scene. For a list or a
    MinMaxInt, a new number will be randomly chosen for each scene.
    Default: `1`
    - `keyword_location`: ([KeywordLocationConfig](#KeywordLocationConfig)):
    Used to identify one of the qualitative locations specified by keywords.
    This field should not be set when `position` or `rotation` are also set.
    - `labels` (string, or list of strings): labels to associate with this
    object.  Components can use this label to reference this object or a group
    of objects.  Labels do not need to be unique and when objects share a
    labels, components have options to randomly choose one or choose all.  See
    specific label options for details.
    - `material` (string, or list of strings): The material (color/texture) to
    use on this object in each scene. For a list, a new material will be
    randomly chosen for each scene. Default: random
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The position of this object in each scene. For a
    list, a new position will be randomly chosen for each scene.
    Default: random
    - `rotation` ([VectorIntConfig](#VectorIntConfig) dict, or list of
    VectorIntConfig dicts): The rotation of this object in each scene. For a
    list, a new rotation will be randomly chosen for each scene.
    Default: random
    - `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts, or [VectorFloatConfig](#VectorFloatConfig)
    dict, or list of VectorFloatConfig dicts): The scale of this object in each
    scene. A single float will be used as the scale for all object dimensions
    (X/Y/Z). For a list or a MinMaxFloat, a new scale will be randomly chosen
    for each scene. Default: `1`
    - `shape` (string, or list of strings): The shape (object type) of this
    object in each scene. For a list, a new shape will be randomly chosen for
    each scene. Default: random

    Example:
    ```
    num: 1
    material: "Custom/Materials/Blue"
    position:
        x: 3
        z: 3
    rotation:
        y: 90
    scale: 1.5
    shape: ball
    ```

    Labels Example:
    ```
    specific_interactable_objects:
      -
        num: 1
        position:
          x: 3
          z: 3
        rotation:
          y: 90
        shape: chest_3
        scale: 1.5
        labels: my_container
      -
        num: 1
        material: "Custom/Materials/Blue"
        scale: 0.5
        shape: ball
        keyword_location:
          keyword: in
          container_label: my_container
      -
        num: 1
        material: "Custom/Materials/Blue"
        scale: 0.5
        shape: ball
        keyword_location:
          keyword: adjacent
          relative_object_label: my_container
    ```
    """

    material: Union[str, List[str]] = None
    num: Union[int, List[int], MinMaxInt] = 1
    scale: Union[float, MinMaxFloat, VectorFloatConfig,
                 List[Union[float, MinMaxFloat, VectorFloatConfig]]] = 1
    shape: Union[str, List[str]] = None
    position: Union[VectorFloatConfig, List[VectorFloatConfig]] = None
    rotation: Union[VectorIntConfig, List[VectorIntConfig]] = None
    keyword_location: Union[KeywordLocationConfig,
                            List[KeywordLocationConfig]] = None
    labels: Union[str, List[str]] = None

    def create_instance(
        self,
        room_dimensions: Dict[str, float],
        performer_start: Dict[str, Dict[str, float]],
        bounds: List[ObjectBounds]
    ) -> Dict[str, Any]:
        return self.create_instance_definition_location_tuple(
            room_dimensions, performer_start, bounds).instance

    def create_instance_definition_location_tuple(
        self,
        room_dimensions: Dict[str, float],
        performer_start: Dict[str, Dict[str, float]],
        bounds: List[ObjectBounds]
    ) -> InstanceDefinitionLocationTuple:
        """Create and return an instance along with definition and location
        objects in a tuple of this specific configured object."""
        shared_config = ILESharedConfiguration.get_instance()
        idl = None
        for _ in range(MAX_TRIES):
            # Try choosing a new random definition AND location each loop, in
            # case the randomly chosen definition is just too big.
            if self.shape:
                defn = self._create_definition()
            else:
                # If a specific object shape was not set (self.shape is None),
                # ensure that the randomly chosen shape has not been excluded.
                defn = shared_config.choose_definition_from_included_shapes(
                    self._create_definition
                )
            if self.keyword_location:
                idl = KeywordLocation.get_keyword_location_object_tuple(
                    self.keyword_location,
                    defn, performer_start, bounds, room_dimensions)
                if idl:
                    break
            else:
                location = self._attach_location(
                    defn,
                    room_dimensions,
                    performer_start,
                    bounds
                )
                if location:
                    obj = instances.instantiate_object(
                        defn, location) if location else None
                    if obj:
                        # All interactable objects should be moveable.
                        obj['moveable'] = True
                        idl = InstanceDefinitionLocationTuple(
                            obj, defn, location)
                        break

        if not idl:
            location_str = f"location={self.keyword_location or self.position}"
            raise ILEException(
                "Failed to create object instance. "
                f"shape={self.shape} {location_str}")

        object_repo = ObjectRepository.get_instance()
        object_repo.add_to_labeled_objects(idl, self.labels)
        return idl

    def _attach_location(
        self,
        defn: ObjectDefinition,
        room_dimensions: Dict[str, float],
        performer_start: Dict[str, Dict[str, float]],
        bounds: List[ObjectBounds]
    ) -> Dict[str, Any]:
        """Create and return an object location with properties randomly
        chosen from the config in this class."""
        if self.position or self.rotation:
            location = {
                'position': vars(choose_position(
                    self.position,
                    defn.dimensions.x,
                    defn.dimensions.z,
                    room_dimensions['x'],
                    room_dimensions['z']
                )),
                'rotation': vars(choose_rotation(self.rotation))
            }
        else:
            return geometry.calc_obj_pos(
                performer_start['position'],
                bounds,
                defn,
                room_dimensions=room_dimensions
            )
        location['boundingBox'] = geometry.create_bounds(
            dimensions=vars(defn.dimensions),
            offset=vars(defn.offset),
            position=location['position'],
            rotation=location['rotation'],
            standing_y=defn.positionY
        )
        if geometry.validate_location_rect(
            location['boundingBox'],
            performer_start['position'],
            bounds,
            room_dimensions
        ):
            bounds.append(location['boundingBox'])
            return location
        return None

    def _create_definition(self) -> ObjectDefinition:
        """Create and return an object definition with properties randomly
        chosen from the config in this class."""
        salient_materials = []
        (shape, mat) = choose_shape_material(self.shape, self.material)
        if mat is None:
            mat = []
            colors = []
        else:
            colors = [mat[0]]
            mat = mat[1]
        return base_objects.create_specific_definition_from_base(
            shape,
            mat,
            colors,
            salient_materials,
            choose_scale(self.scale, shape)
        )
