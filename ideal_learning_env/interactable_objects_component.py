import logging
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Union

from machine_common_sense.config_manager import Vector3d

from generator import (
    MAX_TRIES,
    DefinitionDataset,
    ImmutableObjectDefinition,
    ObjectBounds,
    ObjectDefinition,
    base_objects,
    containers,
    definitions,
    geometry,
    instances,
    materials,
    specific_objects,
)
from generator.scene import Scene
from ideal_learning_env.defs import ILEDelayException
from ideal_learning_env.feature_creation_service import (
    FeatureCreationService,
    FeatureTypes,
)

from .choosers import choose_counts, choose_random
from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import (
    ILEConfigurationException,
    ILEException,
    ILESharedConfiguration,
    find_bounds,
    return_list,
)
from .interactable_object_service import (
    InteractableObjectConfig,
    KeywordLocationConfig,
)
from .numerics import MinMaxInt
from .object_services import (
    InstanceDefinitionLocationTuple,
    KeywordLocation,
    MaterialRestrictions,
    ObjectRepository,
)
from .validators import ValidateNumber, ValidateOptions

logger = logging.getLogger(__name__)


def log_keyword_location_object(
    keyword: str,
    keyword_location: KeywordLocationConfig
) -> None:
    logger.trace(
        f'Added {keyword} with keyword location = '
        f'{vars(keyword_location) if keyword_location else "None"}'
    )


class SpecificInteractableObjectsComponent(ILEComponent):
    specific_interactable_objects: Union[
        InteractableObjectConfig,
        List[InteractableObjectConfig]] = None
    """
    ([InteractableObjectConfig](#InteractableObjectConfig) dict, or list of
    InteractableObjectConfig dicts): One or more specific objects (with one
    or more possible variations) that will be added to each scene.

    Simple Example:
    ```
    specific_interactable_objects: null
    ```

    Advanced Example:
    ```
    specific_interactable_objects:
      -
        num: 1
        material: ["WOOD_MATERIALS", "PLASTIC_MATERIALS"]
        scale: 1.2
        shape: "table_2"
        position:
          x: 3
          z: 3
      -
        num:
          min: 10
          max: 30
        material:
          - "WOOD_MATERIALS"
          - "PLASTIC_MATERIALS"
          - "AI2-THOR/Materials/Metals/Brass 1"
        scale:
          min: 0.8
          max: 1.4
        shape:
          - "car_1"
          - "racecar_red"
          - "crayon_blue"
        position:
          x:
            min: -4
            max: 1
          z:
            min: -4
            max: 1
    ```
    """
    _delayed_templates = []

    @ile_config_setter(validator=ValidateNumber(
        props=['num'], min_value=1, null_ok=True))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(materials.ALL_CONFIGURABLE_MATERIAL_LISTS_AND_STRINGS)
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['shape'],
        options=base_objects.FULL_TYPE_LIST
    ))
    def set_specific_interactable_objects(self, data: Any) -> None:
        self.specific_interactable_objects = data

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring specific interactable objects...')

        bounds = find_bounds(scene)
        self._delayed_templates = []
        templates = return_list(self.specific_interactable_objects)
        for template, num in choose_counts(templates):
            logger.trace(
                f'Creating {num} of configured interactable object template = '
                f'{vars(template)}'
            )
            for _ in range(num):
                self._add_object_from_template(scene, bounds, template)
        return scene

    def run_delayed_actions(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        bounds = find_bounds(scene)
        templates = self._delayed_templates
        self._delayed_templates = []
        for template, _ in templates:
            self._add_object_from_template(scene, bounds, template)
        return scene

    def get_num_delayed_actions(self) -> bool:
        return len(self._delayed_templates)

    def get_delayed_action_error_strings(self) -> List[str]:
        return [str(err) for _, err in self._delayed_templates]

    def _add_object_from_template(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        object_config: InteractableObjectConfig
    ) -> None:
        # Will automatically update the bounds list.
        try:
            # If identical_to is used, pick that object's shape/scale/material.
            # Otherwise, if identical_except_color is used, pick that object's
            # shape/scale, but not its material.
            cannot_have_same_material = False
            if(
                object_config.identical_to or
                object_config.identical_except_color
            ):
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
                object_config.scale = obj_to_use.definition.scale
                if object_config.identical_to:
                    object_config.material = obj_to_use.definition.materials
                else:
                    cannot_have_same_material = True

            obj = FeatureCreationService.create_feature(
                scene,
                FeatureTypes.INTERACTABLE,
                object_config,
                bounds
            )[0]

            if cannot_have_same_material:
                if obj_to_use.definition.materials == obj['materials']:
                    raise ILEException(
                        'Random object accidentally matches in color'
                    )

        except ILEDelayException as e:
            self._delayed_templates.append((object_config, e))


class RandomInteractableObjectsComponent(ILEComponent):
    """Adds random objects to an ILE scene.  Users can specify an exact number
    or a range.  When a range is specified, each generated scene will have
    a uniformly distributed random number be generated within that range,
    inclusively.

    This component requires performerStart.location to be set in the scene
    prior. This is typically handles by the GlobalSettingsComponent"""

    num_random_interactable_objects: Union[int, MinMaxInt] = None
    """
    (int, or [MinMaxInt](#MinMaxInt) dict): The number of random interactable
    objects that will be added to each scene. Default: 0

    Simple Example:
    ```
    num_random_interactable_objects: null
    ```

    Advanced Example:
    ```
    num_random_interactable_objects:
        min: 1
        max: 10
    ```
    """

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring random interactable objects...')

        bounds = find_bounds(scene)
        num_objects = self.get_num_random_interactable_objects()
        logger.trace(
            f'Creating {num_objects} random interactable objects...'
        )

        for _ in range(num_objects):
            object_config = InteractableObjectConfig()
            instance = FeatureCreationService().create_feature(
                scene, FeatureTypes.INTERACTABLE, object_config, bounds
            )[0]

            debug = instance.get('debug', {})
            debug['random_position'] = True

        return scene

    def get_num_random_interactable_objects(self) -> int:
        return (
            0 if self.num_random_interactable_objects is None else
            choose_random(self.num_random_interactable_objects, int)
        )

    # If not null, each number must be an integer zero or greater.
    @ile_config_setter(validator=ValidateNumber(min_value=0))
    def set_num_random_interactable_objects(self, data: Any) -> None:
        self.num_random_interactable_objects = data


@dataclass
class KeywordObjectsConfig():
    """
    Describes a single group of a keyword objects.  Keyword objects has the
    following properties:
    - `keyword` (string, or list of strings): The type of object, like
    confusor, container, obstacle, or occluder.
    If an array is given, one will be chosen for each creation of this group.
        - `"asymmetric_containers"`: Asymmetric open-topped containers.
        Subset of `"open_topped_containers"`. Used in interactive support
        relations tasks.
        - `"bins"`: Bin-like containers. Subset of `"open_topped_containers"`.
        Used in interactive spatial reorientation tasks.
        - `"confusors"`: Objects that are similar to the target in two of the
        following: color, shape, size.
        - `"containers"`: Receptacles that can contain other objects and can
        open and close, like chests.  These containers can be of any size.
        - `"containers_can_contain_target"`: Receptacles that can contain other
        objects and can open and close, like chests.  These containers
        will be large enough to contain the target.  If a goal target does
        not exist, generation will fail.
        - `"containers_cannot_contain_target"`: Receptacles that can contain
        other objects and can open and close, like chests.  These containers
        will not be large enough to contain the target.  If a goal target does
        not exist, generation will fail.
        - `"context"`: Objects (also called "distractors") that are small,
        pickupable, and serve to clutter the room to possibly distract the AI.
        They are never the same shape as the target object, if the scene has a
        goal with a target object.
        - `"obstacles"`: Objects that prevent movement through/under them but
        allow sight through them, like chairs or tables with four individual
        legs.
        - `"occluders"`: Objects that prevent both movement through/under them
        AND sight through them, like sofas or bookcases with solid back panels.
        This is completely different from the occluders in passive
        intuitive physics scenes.
        - `"open_topped_containers"`: Objects that can contain other objects
        but have no lid and open tops instead.
        - `"symmetric_containers"`: Symmetric open-topped containers.
        Subset of `"open_topped_containers"`. Used in interactive support
        relations tasks.
    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): The number of this object the user wants to create.
    - `keyword_location`: ([KeywordLocationConfig](#KeywordLocationConfig)):
    One of the keyword locations for this object or set of objects. Any choices
    in `keyword_location` are made for each object inside the group, not the
    group as a whole.
    """
    keyword: Union[str, List[str]] = None
    num: Union[int, List[Union[int, MinMaxInt]], MinMaxInt] = 0
    keyword_location: KeywordLocationConfig = None


class RandomKeywordObjectsComponent(ILEComponent):
    """Adds random objects of certain types to an ILE scene.

    This component requires performerStart.location to be set in the scene
    prior. This is typically handles by the GlobalSettingsComponent"""

    keyword_objects: Union[KeywordObjectsConfig,
                           List[KeywordObjectsConfig]] = None
    """
    ([KeywordObjectsConfig](#KeywordObjectsConfig) dict, or list of
    KeywordObjectsConfig dicts): Creates interactable objects of specific
    categories like confusors, containers, obstacles, or occluders.
    Default:
      * 0 to 10 context objects
      * 2 to 4 of container, obstacles, and occluders
    ```
    keyword_objects:
        - keyword: ["containers", "obstacles", "occluders"]
        num:
            min: 2
            max: 4
        - keyword: "context"
            min: 0
            max: 10
    ```

    All objects created here will be given the following labels.  For more
    information see ([InteractableObjectConfig](#InteractableObjectConfig))
    for more information on labels.
      - asymmetric_containers: keywords_asymmetric_containers
      - bins: keywords_bins
      - confusors: keywords_confusors
      - containers: keywords_containers
      - containers_can_contain_target:
          keywords_containers, keywords_containers_can_contain_target
      - containers_cannot_contain_target:
          keywords_containers, keywords_containers_cannot_contain_target
      - context: keywords_context
      - obstacles: keywords_obstacles
      - occluders: keywords_occluders
      - open_topped_containers: keywords_open_topped_containers
      - symmetric_containers: keywords_symmetric_containers

    Simple Example:
    ```
    keyword_objects: null
    ```

    Advanced Example:
    ```
    keyword_objects:
      -
        keyword: confusors
        num: 1
      -
        keyword: containers
        num:
          min: 0
          max: 3
      -
        keyword: containers_can_contain_target
        num: 1
        keyword_location:
          keyword: front
      -
        keyword: containers_cannot_contain_target
        num: 1
      -
        keyword: obstacles
        num: [2, 4]
        keyword_location:
          keyword: adjacent
          relative_object_label: other_object
      -
        keyword: occluders
        num: 1
      -
        keyword: context
        num: 20
    ```

    Note: Creating too many random objects can increase the chance of failure.
    """

    LABEL_KEYWORDS_ASYMMETRIC_CONTAINERS = "keywords_asymmetric_containers"
    LABEL_KEYWORDS_BINS = "keywords_bins"
    LABEL_KEYWORDS_CONFUSORS = "keywords_confusors"
    LABEL_KEYWORDS_CONTAINERS = "keywords_containers"
    LABEL_KEYWORDS_CONTAINERS_CAN_CONTAIN_TARGET = "keywords_containers_can_contain_target"  # noqa
    LABEL_KEYWORDS_CONTAINERS_CANNOT_CONTAIN_TARGET = "keywords_containers_cannot_contain_target"  # noqa
    LABEL_KEYWORDS_CONTEXT = "keywords_context"
    LABEL_KEYWORDS_OBSTACLES = "keywords_obstacles"
    LABEL_KEYWORDS_OCCLUDERS = "keywords_occluders"
    LABEL_KEYWORDS_OPEN_TOPPED_CONTAINERS = "keywords_open_topped_containers"
    LABEL_KEYWORDS_SYMMETRIC_CONTAINERS = "keywords_symmetric_containers"

    KEYWORDS_ASYMMETRIC_CONTAINERS = "asymmetric_containers"
    KEYWORDS_BINS = "bins"
    KEYWORDS_CONFUSORS = "confusors"
    KEYWORDS_CONTAINERS = "containers"
    KEYWORDS_CONTEXT = "context"
    KEYWORDS_CONTAINERS_CAN_CONTAIN_TARGET = "containers_can_contain_target"
    KEYWORDS_CONTAINERS_CANNOT_CONTAIN_TARGET = "containers_cannot_contain_target"  # noqa
    KEYWORDS_OBSTACLES = "obstacles"
    KEYWORDS_OCCLUDERS = "occluders"
    KEYWORDS_OPEN_TOPPED_CONTAINERS = "open_topped_containers"
    KEYWORDS_SYMMETRIC_CONTAINERS = "symmetric_containers"

    FULL_KEYWORD_LIST = []

    DEFAULT_VALUE = [
        KeywordObjectsConfig(
            ["containers", "obstacles", "occluders"],
            MinMaxInt(2, 4)),
        KeywordObjectsConfig(
            "context", MinMaxInt(0, 10)),
    ]

    def __init__(self, data: Dict[str, Any]):
        self.FULL_KEYWORD_LIST = [
            self.KEYWORDS_ASYMMETRIC_CONTAINERS,
            self.KEYWORDS_BINS,
            self.KEYWORDS_CONTEXT,
            self.KEYWORDS_CONFUSORS,
            self.KEYWORDS_CONTAINERS,
            self.KEYWORDS_CONTAINERS_CAN_CONTAIN_TARGET,
            self.KEYWORDS_CONTAINERS_CANNOT_CONTAIN_TARGET,
            self.KEYWORDS_OBSTACLES,
            self.KEYWORDS_OCCLUDERS,
            self.KEYWORDS_OPEN_TOPPED_CONTAINERS,
            self.KEYWORDS_SYMMETRIC_CONTAINERS
        ]
        super().__init__(data)

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring random keyword objects...')

        bounds = find_bounds(scene)
        templates = return_list(self.keyword_objects, self.DEFAULT_VALUE)
        using_default = (templates == self.DEFAULT_VALUE)

        switcher = {
            self.KEYWORDS_ASYMMETRIC_CONTAINERS:
                self._add_asymmetric_container,
            self.KEYWORDS_BINS: self._add_bin_container,
            self.KEYWORDS_CONTEXT: self._add_context,
            self.KEYWORDS_CONFUSORS: self._add_confusor,
            self.KEYWORDS_CONTAINERS: self._add_container,
            self.KEYWORDS_CONTAINERS_CAN_CONTAIN_TARGET:
                self._add_container_target_valid,
            self.KEYWORDS_CONTAINERS_CANNOT_CONTAIN_TARGET:
                self._add_container_target_invalid,
            self.KEYWORDS_OBSTACLES: self._add_obstacle,
            self.KEYWORDS_OCCLUDERS: self._add_occluder,
            self.KEYWORDS_OPEN_TOPPED_CONTAINERS:
                self._add_open_topped_container,
            self.KEYWORDS_SYMMETRIC_CONTAINERS: self._add_symmetric_container
        }
        for template, num in choose_counts(templates):
            logger.trace(
                f'Creating {num} of random keyword object template = '
                f'{vars(template)}'
            )
            for x in range(num):
                keyword_location = choose_random(
                    getattr(template, 'keyword_location'))
                keyword = choose_random(
                    getattr(template, 'keyword', self.FULL_KEYWORD_LIST))
                if using_default:
                    logger.info(
                        f'Using default setting to generate random '
                        f'keyword object number {x + 1} / {num + 1}: '
                        f'{keyword.lower().replace("_", " ")}'
                    )
                else:
                    logger.debug(
                        f'Using configured setting to generate random '
                        f'keyword object number {x + 1} / {num + 1}: '
                        f'{keyword.lower().replace("_", " ")}'
                    )
                obj = switcher[keyword](
                    scene, bounds, x, keyword_location=keyword_location)
                debug = obj.get('debug', {})
                debug['random_position'] = True
                scene.objects.append(obj)
                bounds.append(obj['shows'][0]['boundingBox'])

        return scene

    def _add_asymmetric_container(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        keyword_location: KeywordLocationConfig
    ) -> Dict[str, Any]:
        return self._add_special_container(
            scene,
            bounds,
            index,
            keyword_location,
            'asymmetric container',
            self.LABEL_KEYWORDS_ASYMMETRIC_CONTAINERS,
            specific_objects.get_container_asymmetric_definition_dataset()
        )

    def _add_bin_container(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        keyword_location: KeywordLocationConfig
    ) -> Dict[str, Any]:
        return self._add_special_container(
            scene,
            bounds,
            index,
            keyword_location,
            'bin container',
            self.LABEL_KEYWORDS_BINS,
            specific_objects.get_container_bin_definition_dataset()
        )

    def _add_confusor(self, scene, bounds, index, keyword_location):
        # Requires target but ILE doesn't support that yet
        target = scene.get_target_object()
        if target is not None:
            dataset = specific_objects.get_interactable_definition_dataset()

            def _choose_definition_callback() -> ObjectDefinition:
                return definitions.get_similar_definition(target, dataset)

            log_keyword_location_object('confusor', keyword_location)

            return self._generate_instance_with_valid_location(
                scene, bounds, _choose_definition_callback, index,
                [self.LABEL_KEYWORDS_CONFUSORS], keyword_location)
        else:
            raise ILEConfigurationException(
                'Cannot create a confusor object without a configured goal '
                'and target object!'
            )

    def _add_container_target_valid(
            self, scene, bounds, index, keyword_location):
        return self._add_container(
            scene, bounds, index, True, keyword_location)

    def _add_container_target_invalid(
            self, scene, bounds, index, keyword_location):
        return self._add_container(
            scene, bounds, index, False, keyword_location)

    def _add_container(self, scene, bounds, index,
                       contain_target=None, keyword_location=None):
        labels = [self.LABEL_KEYWORDS_CONTAINERS]
        dataset = specific_objects.get_container_openable_definition_dataset()

        if contain_target is not None:
            target = scene.get_target_object()
            if target is None:
                raise ILEConfigurationException(
                    "ILE configured to add "
                    "containers relative to goal target size "
                    "('containers_can_contain_target' or "
                    "'containers_can_contain_target') but scene did not "
                    "contain goal target")
            labels.append(
                self.LABEL_KEYWORDS_CONTAINERS_CAN_CONTAIN_TARGET
                if contain_target
                else self.LABEL_KEYWORDS_CONTAINERS_CANNOT_CONTAIN_TARGET)
            dim = target['debug']['dimensions']
            target_od = ObjectDefinition(
                dimensions=Vector3d(x=dim['x'], y=dim['y'], z=dim['z']))

            def _callback(definition: ImmutableObjectDefinition) -> bool:
                contain = (
                    containers.can_contain(definition, target_od) is not None
                )
                return contain_target == contain

            # Filter the dataset to only (in)valid container definitions.
            dataset = dataset.filter_on_custom(_callback)

            log_keyword_location_object(
                f'container that {"can" if contain_target else "cannot"} '
                f'contain the target object',
                keyword_location
            )
        else:
            log_keyword_location_object('container', keyword_location)

        return self._generate_instance_with_valid_location(
            scene, bounds, dataset.choose_random_definition, index,
            labels, keyword_location)

    def _add_obstacle_or_occluder(
        self,
        scene: Dict[str, Any],
        bounds: List[ObjectBounds],
        dataset: DefinitionDataset,
        index: int,
        is_occluder: bool,
        keyword_location: KeywordLocationConfig
    ):
        target = scene.get_target_object()
        chosen_rotation = None

        def _choose_definition_callback() -> ObjectDefinition:
            if target is None:
                chosen_rotation = None
                return dataset.choose_random_definition()
            output_list = geometry.retrieve_obstacle_occluder_definition_list(
                target,
                dataset,
                is_occluder
            )
            chosen_definition, chosen_rotation = random.choice(output_list)
            return chosen_definition

        def _choose_rotation_callback() -> ObjectDefinition:
            return chosen_rotation

        log_keyword_location_object(
            f'{"occluder" if is_occluder else "obstacle"}',
            keyword_location
        )

        label = (self.LABEL_KEYWORDS_OCCLUDERS
                 if is_occluder else self.LABEL_KEYWORDS_OBSTACLES)

        return self._generate_instance_with_valid_location(
            scene,
            bounds,
            _choose_definition_callback,
            index,
            [label],
            keyword_location,
            choose_rotation_callback=(
                _choose_rotation_callback if (chosen_rotation is not None)
                else None
            )
        )

    def _add_obstacle(self, scene, bounds, index, keyword_location):
        dataset = specific_objects.get_obstacle_definition_dataset()
        return self._add_obstacle_or_occluder(
            scene, bounds, dataset, index, False, keyword_location)

    def _add_occluder(self, scene, bounds, index, keyword_location):
        dataset = specific_objects.get_occluder_definition_dataset()
        return self._add_obstacle_or_occluder(
            scene, bounds, dataset, index, True, keyword_location)

    def _add_context(self, scene, bounds, index, keyword_location):
        target = scene.get_target_object()
        targets = []
        if target is not None:
            targets = [target['debug']['shape']]

        def _choose_definition_callback() -> ObjectDefinition:
            return specific_objects.choose_distractor_definition(targets)

        log_keyword_location_object(
            'context object (distractor)',
            keyword_location
        )

        return self._generate_instance_with_valid_location(
            scene, bounds, _choose_definition_callback, index,
            [self.LABEL_KEYWORDS_CONTEXT], keyword_location)

    def _add_open_topped_container(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        keyword_location: KeywordLocationConfig
    ) -> Dict[str, Any]:
        return self._add_special_container(
            scene,
            bounds,
            index,
            keyword_location,
            'open topped container',
            self.LABEL_KEYWORDS_OPEN_TOPPED_CONTAINERS,
            specific_objects.get_container_open_topped_definition_dataset()
        )

    def _add_special_container(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        keyword_location: KeywordLocationConfig,
        keyword: str,
        label: str,
        dataset: DefinitionDataset
    ) -> Dict[str, Any]:
        def _choose_definition_callback() -> ObjectDefinition:
            return dataset.choose_random_definition()

        log_keyword_location_object(keyword, keyword_location)

        return self._generate_instance_with_valid_location(
            scene, bounds, _choose_definition_callback, index,
            [label], keyword_location)

    def _add_symmetric_container(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        keyword_location: KeywordLocationConfig
    ) -> Dict[str, Any]:
        return self._add_special_container(
            scene,
            bounds,
            index,
            keyword_location,
            'symmetric container',
            self.LABEL_KEYWORDS_SYMMETRIC_CONTAINERS,
            specific_objects.get_container_symmetric_definition_dataset()
        )

    # If not null, each number must be an integer zero or greater.
    @ile_config_setter(validator=ValidateNumber(
        props=['num'],
        min_value=0)
    )
    def set_keyword_objects(self, data: Any) -> None:
        self.keyword_objects = data

    def _generate_instance_with_valid_location(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        choose_definition_callback: Callable[[], ObjectDefinition],
        index: int,
        labels: Union[str, List[str]] = None,
        keyword_location: KeywordLocationConfig = None,
        choose_rotation_callback: Callable[[], float] = None
    ) -> Dict[str, Any]:

        object_repo = ObjectRepository.get_instance()
        shared_config = ILESharedConfiguration.get_instance()
        defn = shared_config.choose_definition_from_included_shapes(
            choose_definition_callback
        )
        MaterialRestrictions.valid_defn_or_raise(defn)
        if keyword_location:
            idl = KeywordLocation.get_keyword_location_object_tuple(
                keyword_location, defn, scene.performer_start, bounds,
                scene.room_dimensions)

            if labels and idl:
                object_repo.add_to_labeled_objects(idl, labels)
            return idl.instance
        else:
            for _ in range(MAX_TRIES):
                location = geometry.calc_obj_pos(
                    vars(scene.performer_start.position),
                    bounds,
                    defn,
                    room_dimensions=vars(scene.room_dimensions),
                    rotation_func=choose_rotation_callback
                )
                if location is not None:
                    break
                defn = shared_config.choose_definition_from_included_shapes(
                    choose_definition_callback
                )
                MaterialRestrictions.valid_defn_or_raise(defn)
            if location is None:
                raise ILEException(
                    f"Failed to place object {index} after {MAX_TRIES} "
                    f"retries. Try using fewer objects.")
            obj = instances.instantiate_object(defn, location)
            if labels and obj:
                idl = InstanceDefinitionLocationTuple(obj, defn, location)
                object_repo.add_to_labeled_objects(idl, labels)
            return obj
