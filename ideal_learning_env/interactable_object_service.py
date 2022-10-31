import copy
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from machine_common_sense.config_manager import PerformerStart, Vector3d

from generator import (
    ObjectBounds,
    ObjectDefinition,
    base_objects,
    geometry,
    instances,
    specific_objects
)
from generator.materials import MaterialTuple
from generator.mechanisms import CYLINDRICAL_SHAPES
from generator.scene import Scene
from ideal_learning_env.defs import (
    ILEDelayException,
    ILEException,
    ILESharedConfiguration
)
from ideal_learning_env.feature_creation_service import (
    BaseFeatureConfig,
    BaseObjectCreationService,
    FeatureCreationService,
    FeatureTypes,
    log_feature_template,
    position_relative_to,
    save_to_object_repository
)
from ideal_learning_env.object_services import (
    InstanceDefinitionLocationTuple,
    KeywordLocation,
    ObjectRepository,
    RelativePositionConfig,
    add_random_placement_tag
)

from .choosers import (
    choose_material_tuple_from_material,
    choose_position,
    choose_rotation,
    choose_scale,
    choose_shape_material
)
from .numerics import (
    MinMaxFloat,
    MinMaxInt,
    RandomizableVectorFloat3dOrFloat,
    VectorFloatConfig,
    VectorIntConfig
)

logger = logging.getLogger(__name__)


@dataclass
class KeywordLocationConfig():
    """Describes an object's keyword location. Can have the following
    properties:
    - `keyword` (string, or list of strings): The keyword location, which can
    be one of the following:
        - `adjacent` - The object will be placed next to another object.  The
        other object must be referenced by the 'relative_object_label' field.
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
        location will be on the opposite side of the room.  There is no
        adjustments to find a valid location if another object already exists
        in location specified by this keyword.
        - `opposite_z` - The object will be placed in the exact same location
        as the object referenced by `relative_object_label` except that its z
        location will be on the opposite side of the room.  There is no
        adjustments to find a valid location if another object already exists
        in location specified by this keyword.
        - `random` - The object will be positioned in a random location, as if
        it did not have a keyword location.
        - `associated_with_agent` - This object will be held by an agent
        referenced by the 'relative_object_label' field.
        - `along_wall` - This object will be placed along a wall
        referenced by the 'relative_object_label' field.  The wall labels are
        'front_wall', 'back_wall', 'left_wall, and 'right_wall'.  If no wall is
        provided, a wall will be chosen at random.
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
    keyword: Union[str, List[str]] = None
    container_label: Union[str, List[str]] = None
    relative_object_label: Union[str, List[str]] = None
    distance: Union[str, List[str]] = None
    direction: Union[str, List[str]] = None
    position_relative_to_start: Union[VectorFloatConfig,
                                      List[VectorFloatConfig]] = None


@dataclass
class InteractableObjectConfig(BaseFeatureConfig):
    """Represents the template for a specific object (with one or more possible
    variations) that will be added to each scene. Each template can have the
    following optional properties:
    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict): The number
    of objects with this template to generate in each scene. For a list or a
    MinMaxInt, a new number will be randomly chosen for each scene.
    Default: `1`
    - `num_targets_minus` (int, or list of ints, or [MinMaxInt](#MinMaxInt)
    dict): Overrides the `num` option. Count the total number of targets,
    subtract `num_targets_minus` from the count, and generate that many
    objects. For example, in a scene with 5 targets, a `num_targets_minus` of
    1 would generate 4 objects. Default: null
    - `dimensions` ([VectorFloatConfig](#VectorFloatConfig) dict, int,
    [MinMaxInt](#MinMaxInt), or a list of any of those types): Sets the overal
    dimensions of the object in meters.  This field will override scale.
    Default: Use scale.
    - `identical_to` (str): Used to match to another object with
    the specified label, so that this definition can share that object's
    exact shape, scale, and material. Overrides `identical_except_color`
    - `identical_except_color` (str): Used to match to another object with
    the specified label, so that this definition can share that object's
    exact shape and scale, but not its material (color/texture).
    - `keyword_location`: ([KeywordLocationConfig](#KeywordLocationConfig)):
    Used to identify one of the qualitative locations specified by keywords.
    This field should not be set when `position` or `rotation` are also set.
    - `labels` (string, or list of strings): labels to associate with this
    object.  Components can use this label to reference this object or a group
    of objects.  Labels do not need to be unique and when objects share a
    labels, components have options to randomly choose one or choose all.  See
    specific label options for details.
    - `locked` (bool or list of bools): If true and the resulting object is
    lockable, like a container or door, the object will be locked.  If the
    object is not lockable, this field has no affect.
    - `material` (string, or list of strings): The material (color/texture) to
    use on this object in each scene. For a list, a new material will be
    randomly chosen for each scene. Default: random
    - `not_material` (string): Do not use this material, or any other materials
    that share the same colors as this material, on this object. Default: none
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The position of this object in each scene. For a
    list, a new position will be randomly chosen for each scene.
    Default: random
    - `position_relative` ([RelativePositionConfig](#RelativePositionConfig)
    dict, or list of RelativePositionConfig dicts): Configuration options for
    positioning this object relative to another object, rather than using
    `position`. If configuring this as a list, then all listed options will be
    applied to each scene in the listed order, with later options overriding
    earlier options if necessary. Default: not used
    - `rotation` ([VectorIntConfig](#VectorIntConfig) dict, or list of
    VectorIntConfig dicts): The rotation of this object in each scene. For a
    list, a new rotation will be randomly chosen for each scene.
    Default: random
    - `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts, or [VectorFloatConfig](#VectorFloatConfig)
    dict, or list of VectorFloatConfig dicts): The scale of this object in each
    scene. A single float will be used as the scale for all object dimensions
    (X/Y/Z). For a list or a MinMaxFloat, a new scale will be randomly chosen
    for each scene. This field can be overriden by 'dimensions'. Default: `1`
    - `shape` (string, or list of strings): The shape (object type) of this
    object in each scene. For a list, a new shape will be randomly chosen for
    each scene. Default: random
    - `rotate_cylinders` (bool): Whether or not to rotate cylindrical shapes
    along their x axis so that they are placed on their round sides (needed
    for collision scenes). This would only apply to these shapes: 'cylinder',
    'double_cone', 'dumbbell_1', 'dumbbell_2', 'tie_fighter', 'tube_narrow',
    'tube_wide'. Note that this will override any x rotation previously
    specified by 'rotation'. Default: False

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
      -
        num: 2
        identical_to: my_container
    ```
    """

    dimensions: RandomizableVectorFloat3dOrFloat = None
    material: Union[str, List[str]] = None
    scale: Union[float, MinMaxFloat, VectorFloatConfig,
                 List[Union[float, MinMaxFloat, VectorFloatConfig]]] = None
    shape: Union[str, List[str]] = None
    position: Union[VectorFloatConfig, List[VectorFloatConfig]] = None
    rotation: Union[VectorIntConfig, List[VectorIntConfig]] = None
    keyword_location: Union[KeywordLocationConfig,
                            List[KeywordLocationConfig]] = None
    locked: Union[bool, List[bool]] = False
    identical_to: str = None
    identical_except_color: str = None
    position_relative: Union[
        RelativePositionConfig,
        List[RelativePositionConfig]
    ] = None
    rotate_cylinders: bool = False
    not_material: str = None
    num_targets_minus: Union[
        int,
        MinMaxInt,
        List[Union[int, MinMaxInt]]
    ] = None


DEFAULT_TEMPLATE_INTERACTABLE = InteractableObjectConfig(
    num=1, material=None, scale=1, shape=None, position=None, rotation=None,
    keyword_location=None, locked=False, labels=None, identical_to=None,
    identical_except_color=None, not_material=None)


class InteractableObjectCreationService(BaseObjectCreationService):
    shared_config = None
    bounds = []

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_INTERACTABLE
        self._type = FeatureTypes.INTERACTABLE
        self.shared_config = ILESharedConfiguration.get_instance()
        self.defn = None

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: InteractableObjectConfig,
            source_template: InteractableObjectConfig
    ) -> InteractableObjectConfig:
        if isinstance(reconciled.dimensions, (int, float)):
            val = reconciled.dimensions
            reconciled.dimensions = Vector3d(x=val, y=val, z=val)
        (reconciled.shape, mat) = choose_shape_material(
            reconciled.shape, reconciled.material, reconciled.not_material)
        reconciled.material = mat[0] if isinstance(mat, MaterialTuple) else mat
        reconciled.scale = choose_scale(
            source_template.scale,
            reconciled.shape
        )
        if isinstance(reconciled.scale, (int, float)):
            val = reconciled.scale
            reconciled.scale = Vector3d(x=val, y=val, z=val)
        defn = self._create_definition(reconciled)
        self.defn = defn
        reconciled.scale = defn.scale

        if (
            not reconciled.keyword_location or
            reconciled.keyword_location.keyword == KeywordLocation.RANDOM
        ):
            reconciled.position = choose_position(
                reconciled.position,
                defn.dimensions.x,
                defn.dimensions.z,
                scene.room_dimensions.x,
                scene.room_dimensions.y,
                scene.room_dimensions.z
            )
            reconciled.rotation = choose_rotation(reconciled.rotation)

        # If needed, adjust this device's position relative to another object.
        if source_template.position_relative:
            position_x, position_z = position_relative_to(
                # Use the config list from the source template.
                source_template.position_relative,
                (reconciled.position.x, reconciled.position.z),
                scene.performer_start.position,
                'dropping device'
            )
            if position_x is not None:
                reconciled.position.x = position_x
            if position_z is not None:
                reconciled.position.z = position_z

        return reconciled

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: InteractableObjectConfig,
            source_template: InteractableObjectConfig):
        defn = self.defn
        if (
            reconciled.keyword_location and
            reconciled.keyword_location.keyword != KeywordLocation.RANDOM
        ):
            try:
                idl = KeywordLocation.get_keyword_location_object_tuple(
                    reconciled.keyword_location,
                    defn, scene.performer_start, self.bounds,
                    scene.room_dimensions)
                if idl:
                    self.idl = idl
                    add_random_placement_tag(idl.instance, source_template)
                    return idl.instance
            except ILEException as e:
                # If location can't be found, try again and therefore log
                # but don't let exception continue.  However, if the
                # Exception is a Delay Exception, we want ot pass it up.
                if isinstance(e, ILEDelayException):
                    raise e from e
                logger.debug(
                    f"Failed to place object with keyword location="
                    f"{reconciled.keyword_location}",
                    exc_info=e)
        else:
            location = self._attach_location(
                reconciled,
                defn,
                scene.room_dimensions,
                scene.performer_start,
                self.bounds or []
            )
            if location:
                obj = instances.instantiate_object(
                    defn, location) if location else None
                if obj:
                    # All interactable objects should be moveable.
                    obj['moveable'] = True
                    self.idl = InstanceDefinitionLocationTuple(
                        obj, defn, location)
                    add_random_placement_tag(
                        self.idl.instance, source_template)
                    return self.idl.instance
                else:
                    msg = (f"Failed to create instance. template="
                           f"{reconciled} location={location}")
                    logger.debug(msg)
                    raise ILEException(msg)
            else:
                msg = (f"Failed to find object location. template="
                       f"{reconciled}")
                logger.debug(msg)
                raise ILEException(msg)
        raise ILEException(
            f"Failed to create object from template={reconciled}")

    def _on_valid_instances(
            self, scene: Scene,
            reconciled_template: InteractableObjectConfig,
            new_obj: dict, key: str = 'objects'):
        if new_obj is not None:
            for obj in new_obj:
                if (obj['type'] in specific_objects.get_lockable_shapes()):
                    obj['locked'] = reconciled_template.locked
                save_to_object_repository(
                    self.idl,
                    self._type,
                    reconciled_template.labels
                )
                scene.objects.append(obj)
        log_feature_template(
            self._get_type().lower().replace('_', ' '),
            'ids' if len(new_obj) > 1 else 'id',
            [part['id'] for part in new_obj] if len(new_obj) > 1 else
            new_obj[0]['id'],
            [None, reconciled_template]
        )

    def _attach_location(
        self,
        template,
        defn: ObjectDefinition,
        room_dimensions: Vector3d,
        performer_start: PerformerStart,
        bounds: List[ObjectBounds]
    ) -> Dict[str, Any]:
        """Create and return an object location with properties randomly
        chosen from the config in this class."""

        rotate_cylinders = (template.rotate_cylinders and
                            defn.type in CYLINDRICAL_SHAPES)

        if template.position or template.rotation:
            location = {
                'position': vars(template.position),
                'rotation': vars(template.rotation)
            }
            location['position']['y'] += defn.positionY
            if(rotate_cylinders):
                location['rotation']['x'] = 90
        else:
            if(rotate_cylinders):
                defn.rotation.x = 90

            return geometry.calc_obj_pos(
                vars(performer_start.position),
                # calc_obj_pos addes to bounds, but we don't want this.
                copy.deepcopy(bounds),
                defn,
                room_dimensions=vars(room_dimensions)
            )
        location['boundingBox'] = geometry.create_bounds(
            dimensions=vars(defn.dimensions),
            offset=vars(defn.offset),
            position=location['position'],
            rotation=location['rotation'],
            standing_y=defn.positionY
        )
        return location

    def _create_definition(self, template) -> ObjectDefinition:
        """Create and return an object definition with properties randomly
        chosen from the config in this class."""
        salient_materials = []
        mat = (
            None if template.material is None
            else choose_material_tuple_from_material(
                template.material))
        shape = template.shape
        if mat is None:
            mat = []
            colors = []
        else:
            colors = [mat[0]]
            mat = mat[1]

        defn = base_objects.create_specific_definition_from_base(
            shape,
            mat,
            colors,
            salient_materials,
            template.scale
        )
        if template.dimensions:
            # We need the original defn to get the dimensions at a given scale.
            # We then adjust that scale relative to ratio of given dimensions
            # and desired dimensions to give a scale that will achieve the
            # desired dimensions.
            template.scale.x *= template.dimensions.x / defn.dimensions.x
            template.scale.y *= template.dimensions.y / defn.dimensions.y
            template.scale.z *= template.dimensions.z / defn.dimensions.z
            defn = base_objects.create_specific_definition_from_base(
                shape,
                mat,
                colors,
                salient_materials,
                template.scale
            )
        return defn


FeatureCreationService.register_creation_service(
    FeatureTypes.INTERACTABLE, InteractableObjectCreationService)


class TargetCreationService(InteractableObjectCreationService):
    def __init__(self):
        super().__init__()
        self._type = FeatureTypes.TARGET


FeatureCreationService.register_creation_service(
    FeatureTypes.TARGET, TargetCreationService)


def create_user_configured_interactable_object(
    scene: Scene,
    bounds: List[ObjectBounds],
    object_config: InteractableObjectConfig,
    is_target: bool = False
) -> Dict[str, Any]:
    """Create and return a user-configured interactable object, that may have
    a config option like "identical_to" or "identical_except_color" which must
    be applied appropriately. Automatically updates the given list of object
    bounds. May raise an ILEDelayException."""

    # If identical_to is used, pick that object's shape/scale/material.
    # Otherwise, if identical_except_color is used, pick that object's
    # shape/scale, but not its material.
    if object_config.identical_to or object_config.identical_except_color:
        obj_label = (
            object_config.identical_to or
            object_config.identical_except_color
        )
        obj_repo = ObjectRepository.get_instance()
        obj_to_use = obj_repo.get_one_from_labeled_objects(obj_label)

        if not obj_to_use:
            prop = (
                'identical_to' if object_config.identical_to else
                'identical_except_color'
            )
            raise ILEDelayException(
                f"Failed to find object with {prop} label: {obj_label}"
            )

        object_config.shape = obj_to_use.definition.type
        object_config.scale = copy.deepcopy(obj_to_use.definition.scale)

        # Because a cylinder's height is auto downscaled when its
        # ObjectDefinition is created, upscale it here to compensate.
        if object_config.shape in ['cylinder']:
            if getattr(object_config.scale, 'y'):
                object_config.scale.y *= 2

        # Remember that some object types may not have configurable materials.
        materials = obj_to_use.definition.materials
        if object_config.identical_to:
            object_config.material = copy.deepcopy(materials) or None
        else:
            object_config.not_material = materials[0] if materials else None

    obj = FeatureCreationService.create_feature(
        scene,
        FeatureTypes.TARGET if is_target else FeatureTypes.INTERACTABLE,
        object_config,
        bounds
    )[0]

    if object_config.not_material:
        if (obj_to_use.definition.materials == obj['materials'] or any(
            color in obj['debug']['color'] for color in
            obj_to_use.definition.color
        )):
            logger.debug(
                f'Random object accidentally matches in color:\n'
                f'old object: {obj_to_use}\n'
                f'new object: {obj}\n'
            )
            raise ILEException('Random object accidentally matches in color')

    return obj
