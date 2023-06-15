from __future__ import annotations

import copy
import logging
import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union

from machine_common_sense.config_manager import Vector2dInt, Vector3d

from generator import MAX_TRIES, Scene, SceneObject, geometry

from .choosers import choose_random
from .defs import (
    ILEConfigurationException,
    ILEDelayException,
    ILEException,
    RandomizableString,
    return_list
)
from .numerics import RandomizableInt
from .object_services import (
    InstanceDefinitionLocationTuple,
    ObjectRepository,
    RelativePositionConfig,
    reconcile_template
)

logger = logging.getLogger(__name__)


class FeatureTypes(Enum):
    DOORS = auto()
    DROPPERS = auto()
    FLOOR_MATERIALS = auto()
    HOLES = auto()
    L_OCCLUDERS = auto()
    LAVA = auto()
    MOVING_OCCLUDERS = auto()
    OCCLUDING_WALLS = auto()
    PARTITION_FLOOR = auto()
    PLACERS = auto()
    PLATFORMS = auto()
    RAMPS = auto()
    THROWERS = auto()
    WALLS = auto()
    TOOLS = auto()
    INTERACTABLE = auto()
    AGENT = auto()
    TUBE_OCCLUDERS = auto()
    TURNTABLES = auto()
    # Should be the same as the TARGET_LABEL
    TARGET = auto()


@dataclass
class BaseFeatureConfig():
    """Base class that should used for all structural objects."""
    num: RandomizableInt = 1
    labels: RandomizableString = None
    randomize_once: Dict = None


class FeatureCreationService():
    services = {}

    @staticmethod
    def get_service(type: FeatureTypes):
        return FeatureCreationService.services[type]()

    @staticmethod
    def register_creation_service(
            type: FeatureTypes, service_class: BaseObjectCreationService):
        if type is not None and service_class is not None:
            FeatureCreationService.services[type] = service_class

    @staticmethod
    def create_feature(scene: Scene, type: FeatureTypes,
                       template: BaseFeatureConfig, bounds: List,
                       retries: int = MAX_TRIES) -> List:
        """Attempts to take a scene and a bounds and add an structural object
        of a given type.  If a template is provided, then the template will be
        used for the values provided.

        If there are more attempts than retries without success, an
        ILEException will be thrown.

        Returns a list of instances.
        """

        template_str = vars(template) if template else "None"
        logger.trace(
            f"Attempting to create "
            f"{type.name.lower().replace('_', ' ')} from template: "
            f"{template_str}"
        )

        # Should we remove the type enum completely?  Right now lava and holes
        # use the same config class or we could use the config.
        service = FeatureCreationService.services[type]()
        return service.add_to_scene(scene, template, bounds)[0]


class BaseObjectCreationService(ABC):
    """Base class for object/feature creation services.  All creation service
    instances are intended to be used once and discarded.  This feature allows
    them to save state as necessary.  Services are typically only called via
    add_to_scene() to add the feature.  It is usually easiest to just use
    the FeatureCreationService.create_feature() method."""
    _default_template: BaseFeatureConfig = None
    _type = None
    _last_exception = None

    def _get_type(self) -> str:
        return (self._type.name if self._type is not None and hasattr(
            self._type, 'name') else '')

    def add_to_scene(self, scene: Scene,
                     source_template: BaseFeatureConfig,
                     bounds: List, tries: int = MAX_TRIES
                     ) -> tuple(List, BaseFeatureConfig):
        """Attempts to add object/feature to a scene using template if
        provided.  Returns a list of instances and the reconciled template"""
        self.bounds = bounds
        # TODO handle retries for loop or tenacity?
        for i in range(tries):
            try:
                reconciled = self.reconcile(scene, source_template)
                instance = self.create_feature_from_specific_values(
                    scene, reconciled, source_template)
                insts = instance if isinstance(instance, list) else [instance]

                if self.is_valid(scene, insts,
                                 bounds, try_num=i + 1, retries=tries):
                    self._on_valid_instances(scene, reconciled, insts)
                    return insts, reconciled
                else:
                    logger.trace(f"Invalid feature:\nreconciled={reconciled}"
                                 f"\nsource={source_template}")
            except ILEDelayException as delay:
                raise delay from delay
            except ILEConfigurationException as conf:
                raise conf from conf
            except Exception as e:
                logger.debug(
                    f"Error adding feature {self._get_type()} ",
                    exc_info=e)
                self._last_exception = e
        self._handle_failure(tries)

    def _handle_failure(self, retries: int):
        msg = (
            f"Failed to create object of {self._get_type()} "
            f"after {retries} tries. Try reducing the number of objects, "
            f"using smaller objects, or using a larger room."
        )
        logger.debug(msg, exc_info=self._last_exception)
        if self._last_exception:
            raise ILEException(msg) from self._last_exception
        else:
            raise ILEException(msg)

    def _on_valid_instances(
            self, scene: Scene,
            reconciled_template: BaseFeatureConfig,
            new_obj: SceneObject, key: str = 'objects'):
        if new_obj is not None:
            for obj in new_obj:
                key_list = getattr(scene, key)
                key_list.append(obj)
                save_to_object_repository(
                    obj,
                    self._type,
                    reconciled_template.labels
                )
            log_feature_template(
                self._get_type().lower().replace('_', ' '),
                'ids' if len(new_obj) > 1 else 'id',
                [part['id'] for part in new_obj] if len(new_obj) > 1 else
                new_obj[0]['id'],
                [self, reconciled_template]
            )

    def reconcile(self, scene: Scene,
                  source_template: BaseFeatureConfig
                  ) -> BaseFeatureConfig:
        """Given a scene this method will combine the provided template and
        default template and provide a new template with distinct values.
        Some default values may be dependent on scene values (I.E. room size
        for certain locations)."""
        reconciled_template = reconcile_template(
            default_template=self._default_template,
            source_template=source_template)
        reconciled_template = choose_random(reconciled_template)
        return self._handle_dependent_defaults(
            scene, reconciled_template, source_template)

    # should be overriden when needed
    def _handle_dependent_defaults(
            self, scene: Scene,
            reconciled_template: BaseFeatureConfig,
            source_template: BaseFeatureConfig
    ) -> BaseFeatureConfig:
        return reconciled_template

    # Must be overriden
    @abstractmethod
    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: BaseObjectCreationService,
            source_template: BaseObjectCreationService):
        """Creates the instance of the object/feature from a template with
        only specific values.  Source template is provided as well for
        convenience and logging."""
        pass

    def is_valid(self, scene, new_obj, bounds, try_num, retries):
        valid = False
        if not new_obj or None in new_obj:
            return False
        if validate_all_locations_and_update_bounds(new_obj, scene, bounds):
            valid = True
        else:
            # Checks if enabled for TRACE logging.
            if logger.isEnabledFor(logging.TRACE):
                debug_bounds = [{
                    'box_xz': single_bounds.box_xz,
                    'min_y': single_bounds.min_y,
                    'max_y': single_bounds.max_y
                } for single_bounds in bounds]
                logger.trace(
                    f'Failed validating location of {self._get_type()} on'
                    f' try {try_num} of {retries}.'
                    f'\nEXISTING BOUNDS = {debug_bounds}'
                    f'\nFAILED OBJECT = {new_obj}'
                    f'\nROOM DIMENSIONS = {scene.room_dimensions}'
                )
            else:
                logger.debug(
                    f'Failed validating location of {self._get_type()} on'
                    f' try {try_num} of {retries}.'
                )
            new_obj = None
        return valid


def save_to_object_repository(
    obj_or_idl: Union[SceneObject, InstanceDefinitionLocationTuple],
    structural_type: FeatureTypes,
    labels: List[str]
) -> None:
    """Saves the given object instance (or IDL) to the ObjectRepository under
    the given labels, using the given feature type as an additional label."""
    if isinstance(obj_or_idl, InstanceDefinitionLocationTuple):
        idl = obj_or_idl
        obj = idl.instance
    else:
        obj = obj_or_idl
        loc = {
            'position': copy.deepcopy(obj['shows'][0]['position']),
            'rotation': copy.deepcopy(obj['shows'][0]['rotation']),
            'boundingBox': copy.deepcopy(obj['shows'][0]['boundingBox']),
        }
        idl = InstanceDefinitionLocationTuple(obj, None, loc)

    # debug labels are labels going into the debug key.
    # We use the debug key because we need to generate the labels before we
    # are sure they object will be added to the scene.
    debug_labels = obj.get('debug', {}).get('labels')
    if debug_labels is not None:
        labels_list = debug_labels.copy()
    else:
        labels_list = labels.copy() if isinstance(labels, list) else (
            [labels] if labels else []
        )
        if structural_type.name.lower() not in labels_list:
            labels_list.append(structural_type.name.lower())
    obj_repo = ObjectRepository.get_instance()
    obj_repo.add_to_labeled_objects(idl, labels=labels_list)


def validate_all_locations_and_update_bounds(
    objects: Union[SceneObject, List[SceneObject]],
    scene: Scene,
    bounds: List[geometry.ObjectBounds]
) -> bool:
    '''Returns true if objects don't intersect with existing bounds or
    false otherwise.  If true, will also add new object bounds to bounds
    object.'''

    starting_pos = scene.performer_start.position
    for object in objects:
        skip = (object.get('locationParent', False) or (
            object['type'] == 'lid' and
            scene.objects[-1]['type'] == 'separate_container'))
        bb = object.get('shows')[0].get('boundingBox')
        if not skip and not geometry.validate_location_rect(
            bb,
            vars(starting_pos),
            bounds,
            vars(scene.room_dimensions)
        ):
            return False
    for object in objects:
        bb = object['shows'][0]['boundingBox']
        bounds.append(bb)
    return True


def log_feature_template(
    label: str,
    key: str,
    value: Any,
    templates: Optional[List] = None
) -> None:
    config_string = (
        f'\nTEMPLATE = {vars(templates[0]) if templates[0] else "None"}'
        if templates else ''
    )
    reconciled_string = (
        f'\nRECONCILED = {vars(templates[1] if templates[1] else "None")}'
        if templates and len(templates) > 1 else ''
    )
    logger.trace(
        f'Added {label}: {key.upper()} = {value}'
        f'{config_string}'
        f'{reconciled_string}'
    )


def position_relative_to(
    source_config: Union[RelativePositionConfig, List[RelativePositionConfig]],
    object_position_xz: Tuple[float, float],
    performer_start_position: Vector3d,
    debug_str: str
) -> Tuple[float, float]:
    """Return the relative X and Z positions for an object based on the given
    config."""
    if not source_config:
        return None, None

    position_x = None
    position_z = None

    object_repository = ObjectRepository.get_instance()
    for config in return_list(source_config):
        add_x = choose_random(config.add_x)
        add_z = choose_random(config.add_z)
        use_x = choose_random(config.use_x)
        use_z = choose_random(config.use_z)
        view_angle_x = choose_random(config.view_angle_x)

        if use_x is None and use_z is None:
            use_x = True
            use_z = True

        # Consider ALL relative labels.
        relative_labels = return_list(config.label)
        random.shuffle(relative_labels)
        found_label = False
        for label in relative_labels:
            if not object_repository.has_label(label):
                continue
            relative_object = random.choice(
                object_repository.get_all_from_labeled_objects(label)
            )
            relative_instance = relative_object.instance
            relative_position = relative_instance['shows'][0]['position']
            if use_x:
                position_x = relative_position['x']
            if use_z:
                position_z = relative_position['z']
            if view_angle_x:
                position_x = geometry.occluder_x_to_object_x(
                    relative_position['x'],
                    relative_position['z'],
                    object_position_xz[1] if position_z is None else
                    position_z,
                    performer_start_position.x,
                    performer_start_position.z
                )
            if position_x is not None and add_x is not None:
                position_x += add_x
            if position_z is not None and add_z is not None:
                position_z += add_z
            found_label = True

        if not found_label:
            raise ILEDelayException(
                f'Cannot find relative object label {relative_labels} to '
                f'position a new {debug_str}'
            )

    return position_x, position_z


def validate_floor_position(
        scene: Scene, floor_pos: Vector2dInt, key, restrict_under_user,
        bounds):
    room_dim = scene.room_dimensions
    x = floor_pos.x
    z = floor_pos.z
    perf_x = round(scene.performer_start.position.x)
    perf_z = round(scene.performer_start.position.z)
    xmax = math.floor(room_dim.x / 2)
    zmax = math.floor(room_dim.z / 2)
    valid = not (x < -xmax or x > xmax or z < -zmax or z > zmax)
    bb = geometry.generate_floor_area_bounds(x, z)
    # It is expected that some holes/lava will extend beyond the walls, so we
    # extend the room bounds.
    room_dim_extended = Vector3d(
        x=scene.room_dimensions.x + 1,
        y=scene.room_dimensions.y,
        z=scene.room_dimensions.z + 1)
    valid = valid and geometry.validate_location_rect(
        bb,
        vars(scene.performer_start.position),
        bounds,
        vars(room_dim_extended))
    valid = valid and floor_pos not in getattr(scene, key, '')
    restricted = restrict_under_user and x == perf_x and z == perf_z
    valid = valid and not restricted
    return valid, bb
