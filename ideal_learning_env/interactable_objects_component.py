import itertools
import logging
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Union

from machine_common_sense.config_manager import Vector3d

from generator import (
    ALL_LARGE_BLOCK_TOOLS,
    MAX_TRIES,
    DefinitionDataset,
    ImmutableObjectDefinition,
    ObjectBounds,
    ObjectDefinition,
    SceneObject,
    base_objects,
    containers,
    definitions,
    geometry,
    instances,
    materials,
    specific_objects
)
from generator.containers import shift_lid_positions_based_on_movement
from generator.scene import Scene

from .choosers import (
    choose_counts,
    choose_position,
    choose_random,
    choose_rotation
)
from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import (
    ILEDelayException,
    ILEException,
    ILESharedConfiguration,
    RandomizableString,
    find_bounds,
    return_list
)
from .feature_creation_service import (
    BaseFeatureConfig,
    FeatureCreationService,
    FeatureTypes
)
from .interactable_object_service import (
    InteractableObjectConfig,
    ToolConfig,
    create_user_configured_interactable_object
)
from .numerics import (
    MinMaxInt,
    RandomizableVectorFloat3d,
    VectorFloatConfig,
    VectorIntConfig
)
from .object_services import (
    InstanceDefinitionLocationTuple,
    KeywordLocation,
    KeywordLocationConfig,
    MaterialRestrictions,
    ObjectRepository,
    get_step_after_movement
)
from .validators import ValidateNumber, ValidateOptions

logger = logging.getLogger(__name__)


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

    tools: Union[ToolConfig, List[ToolConfig]] = 0
    """
    ([ToolConfig](#ToolConfig), or list of [ToolConfig](#ToolConfig) dict) --
    Groups of large block tool configurations and how many should be generated
    from the given options.
    Default: 0


    Simple Example:
    ```
    tools:
        - num: 0
    ```

    Advanced Example:
    ```
    tools:
        - num:
            min: 1
            max: 3
        - num: 1
            shape: tool_rect_1_00_x_9_00
            position:
            x: [1,2]
            y: 0
            z:
                min: -3
                max: 3
        - num: [1, 3]
            shape:
            - tool_rect_0_50_x_4_00
            - tool_rect_0_75_x_4_00
            - tool_rect_1_00_x_4_00
            position:
            x: [4, 5]
            y: 0
            z:
                min: -5
                max: -4

    ```
    """

    _delayed_templates = []
    _delayed_separate_lids = []
    _delayed_tools = []

    @ile_config_setter(validator=ValidateNumber(
        props=['num'], min_value=0, null_ok=True))
    @ile_config_setter(validator=ValidateNumber(
        props=['num_targets_minus'], min_value=0, null_ok=True))
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

    @ile_config_setter(validator=ValidateNumber(
        props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['shape'], options=ALL_LARGE_BLOCK_TOOLS))
    def set_tools(self, data: Any) -> None:
        self.tools = data

    # Override
    def update_ile_scene(self, scene: Scene) -> Scene:
        logger.info('Configuring specific interactable objects...')

        bounds = find_bounds(scene)
        self._delayed_templates = []
        self._delayed_separate_lids = []
        self._delayed_tools = []
        templates = return_list(self.specific_interactable_objects)
        for template, num in choose_counts(templates):
            self._add_objects_from_template(scene, bounds, template, num)
        tool_templates = return_list(self.tools)
        for tool_template, num in choose_counts(tool_templates):
            self._add_tools_from_template(scene, bounds, tool_template, num)
        return scene

    def run_delayed_actions(self, scene: Scene) -> Scene:
        bounds = find_bounds(scene)
        # Read ALL of the delayed actions BEFORE trying to run them again.
        templates = self._delayed_templates
        self._delayed_templates = []
        separate_lids = self._delayed_separate_lids
        self._delayed_separate_lids = []
        tool_templates = self._delayed_tools
        self._delayed_tools = []
        # Try running the delayed actions again.
        for _, template, num in templates:
            self._add_objects_from_template(scene, bounds, template, num)
        for _, instance, separate_lid, separate_lid_after in separate_lids:
            self._add_separate_lid(
                scene,
                instance,
                separate_lid,
                separate_lid_after
            )
        for _, tool_template, num in tool_templates:
            self._add_tools_from_template(scene, bounds, tool_template, num)
        return scene

    def get_num_delayed_actions(self) -> bool:
        return (
            len(self._delayed_templates) +
            len(self._delayed_separate_lids) +
            len(self._delayed_tools)
        )

    def get_delayed_action_error_strings(self) -> List[str]:
        delayed = (
            self._delayed_templates + self._delayed_separate_lids +
            self._delayed_tools
        )
        # The first element in each tuple should be the exception.
        return [str(data[0]) for data in delayed]

    def run_actions_at_end_of_scene_generation(
            self, scene: Scene) -> Scene:
        if scene.debug.get('containsSeparateLids'):
            scene.objects = shift_lid_positions_based_on_movement(
                scene.objects)
        return scene

    def _add_object_from_template(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        template: InteractableObjectConfig
    ) -> None:
        # Will automatically update the bounds list.
        try:
            instance = create_user_configured_interactable_object(
                scene,
                bounds,
                template
            )
        except ILEDelayException as e:
            self._delayed_templates.append((e, template, 1))
            return

        if instance['type'] == 'separate_container':
            # Reconcile the configured separate_lid options.
            separate_lid = choose_random(template.separate_lid)
            # Use ALL the labels in the configured separate_lid_after.
            separate_lid_after = return_list(template.separate_lid_after)
            try:
                self._add_separate_lid(
                    scene,
                    instance,
                    separate_lid,
                    separate_lid_after
                )
            except ILEDelayException as e:
                self._delayed_separate_lids.append(
                    (e, instance, separate_lid, separate_lid_after)
                )

    def _add_objects_from_template(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        template: InteractableObjectConfig,
        num: int
    ) -> None:
        if template.num_targets_minus is not None:
            num_targets_minus = choose_random(template.num_targets_minus)
            try:
                targets = scene.get_targets()
                if not targets:
                    raise ILEDelayException(
                        f'No targets for configured "num_targets_minus: '
                        f'{num_targets_minus}'
                    )
                # Not fewer than zero.
                num = max((len(targets) - num_targets_minus), 0)
            except ILEDelayException as e:
                self._delayed_templates.append(
                    (e, template, num_targets_minus)
                )

        logger.trace(
            f'Creating {num} of configured interactable object template = '
            f'{vars(template)}'
        )
        for _ in range(num):
            self._add_object_from_template(scene, bounds, template)

    def _add_separate_lid(
        self,
        scene: Scene,
        instance: SceneObject,
        separate_lid: int,
        separate_lid_after: List[str]
    ) -> None:
        if separate_lid_after:
            step = get_step_after_movement(separate_lid_after)
            if step >= 1:
                separate_lid = step
        if (
            separate_lid is not None and separate_lid is not False and
            separate_lid >= 0
        ):
            service = FeatureCreationService.get_service(
                FeatureTypes.INTERACTABLE
            )
            service.add_separate_lid(scene, separate_lid, instance)

    def _add_tools_from_template(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        tool_template: ToolConfig,
        num: int
    ) -> None:
        for _ in range(num):
            try:
                FeatureCreationService.create_feature(
                    scene,
                    FeatureTypes.TOOLS,
                    tool_template,
                    bounds
                )
            except ILEDelayException as e:
                self._delayed_tools.append((e, tool_template, 1))


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
    def update_ile_scene(self, scene: Scene) -> Scene:
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
class KeywordObjectsConfig(BaseFeatureConfig):
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
    group as a whole. Overrides any configured `position` and `rotation`.
    - `labels` (string, or list of strings): labels to associate with this
    object.  Components can use this label to reference this object or a group
    of objects.  Labels do not need to be unique and when objects share a
    labels, components have options to randomly choose one or choose all.  See
    specific label options for details.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The position of these objects in each scene. If
    given a list, a position will be randomly chosen for each object and each
    scene. Is overridden by the `keyword_location`. Default: random
    - `position_relative` ([RelativePositionConfig](#RelativePositionConfig)
    dict, or list of RelativePositionConfig dicts): Configuration options for
    positioning this object relative to another object, rather than using
    `position`. If configuring this as a list, then all listed options will be
    applied to each scene in the listed order, with later options overriding
    earlier options if necessary. Default: not used
    - `rotation` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The rotation of these objects in each scene. If
    given a list, a rotation will be randomly chosen for each object and each
    scene. Is overridden by the `keyword_location`. Default: random
    """
    keyword: RandomizableString = None
    keyword_location: KeywordLocationConfig = None
    position: RandomizableVectorFloat3d = None
    rotation: RandomizableVectorFloat3d = None


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
    _delayed_actions = []

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

    DEFAULT_VALUE = [KeywordObjectsConfig(
        keyword=["containers", "obstacles", "occluders"],
        num=MinMaxInt(2, 4)
    ), KeywordObjectsConfig(keyword="context", num=MinMaxInt(0, 10))]

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
    def update_ile_scene(self, scene: Scene) -> Scene:
        logger.info('Configuring random keyword objects...')

        self._delayed_actions = []
        bounds = find_bounds(scene)
        templates = return_list(self.keyword_objects, self.DEFAULT_VALUE)
        using_default = (templates == self.DEFAULT_VALUE)

        for template, num in choose_counts(templates):
            logger.trace(
                f'Creating {num} of random keyword object template = '
                f'{vars(template)}'
            )
            for x in range(num):
                keyword = choose_random(
                    getattr(template, 'keyword') or self.FULL_KEYWORD_LIST
                )
                if using_default:
                    logger.info(
                        f'Using default setting to generate random '
                        f'keyword object number {x + 1} / {num}: '
                        f'{keyword.lower().replace("_", " ")}'
                    )
                else:
                    logger.debug(
                        f'Using configured setting to generate random '
                        f'keyword object number {x + 1} / {num}: '
                        f'{keyword.lower().replace("_", " ")}'
                    )
                try:
                    self._add_object_to_scene(
                        keyword,
                        scene,
                        bounds,
                        x,
                        template
                    )
                except ILEDelayException as e:
                    self._delayed_actions.append((keyword, x, template, e))

        return scene

    def run_delayed_actions(self, scene: Scene) -> Scene:
        bounds = find_bounds(scene)
        actions = self._delayed_actions
        self._delayed_actions = []
        for keyword, index, template, _ in actions:
            self._add_object_to_scene(keyword, scene, bounds, index, template)
        return scene

    def get_num_delayed_actions(self) -> bool:
        return len(self._delayed_actions)

    def get_delayed_action_error_strings(self) -> List[str]:
        return [str(err) for _, _, _, err in self._delayed_actions]

    def _add_object_to_scene(
        self,
        keyword: str,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        template: KeywordObjectsConfig
    ) -> None:
        obj = self._get_generator(keyword)(scene, bounds, index, template)
        debug = obj.get('debug', {})
        debug['random_position'] = True
        scene.objects.append(obj)
        bounds.append(obj['shows'][0]['boundingBox'])

    def _add_asymmetric_container(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        template: KeywordObjectsConfig
    ) -> SceneObject:
        return self._add_special_container(
            scene,
            bounds,
            index,
            template,
            'asymmetric container',
            self.LABEL_KEYWORDS_ASYMMETRIC_CONTAINERS,
            specific_objects.get_container_asymmetric_definition_dataset()
        )

    def _add_bin_container(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        template: KeywordObjectsConfig
    ) -> SceneObject:
        return self._add_special_container(
            scene,
            bounds,
            index,
            template,
            'bin container',
            self.LABEL_KEYWORDS_BINS,
            specific_objects.get_container_bin_definition_dataset()
        )

    def _add_confusor(self, scene, bounds, index, template):
        targets = scene.get_targets()
        target = random.choice(targets) if targets else None
        if target is not None:
            dataset = specific_objects.get_interactable_definition_dataset()

            def _choose_definition_callback() -> ObjectDefinition:
                return definitions.get_similar_definition(target, dataset)

            return self._generate_instance_with_valid_location(
                scene, bounds, _choose_definition_callback, index,
                [self.LABEL_KEYWORDS_CONFUSORS], template)
        else:
            raise ILEDelayException(
                'Cannot create a confusor object without a configured goal '
                'and target object!'
            )

    def _add_container_target_valid(
            self, scene, bounds, index, template):
        return self._add_container(scene, bounds, index, template, True)

    def _add_container_target_invalid(
            self, scene, bounds, index, template):
        return self._add_container(scene, bounds, index, template, False)

    def _add_container(self, scene, bounds, index, template,
                       contain_target=None):
        labels = [self.LABEL_KEYWORDS_CONTAINERS]
        dataset = specific_objects.get_container_openable_definition_dataset()

        if contain_target is not None:
            targets = scene.get_targets()
            target = random.choice(targets) if targets else None
            if target is None:
                raise ILEDelayException(
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

        return self._generate_instance_with_valid_location(
            scene, bounds, dataset.choose_random_definition, index,
            labels, template)

    def _add_obstacle_or_occluder(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        dataset: DefinitionDataset,
        index: int,
        is_occluder: bool,
        template: KeywordObjectsConfig
    ):
        targets = scene.get_targets()
        target = random.choice(targets) if targets else None
        chosen_rotation = None

        def _choose_definition_callback() -> ObjectDefinition:
            if target is None:
                chosen_rotation = None
                return dataset.choose_random_definition()
            output = geometry.retrieve_obstacle_occluder_definition_list(
                target,
                dataset,
                is_occluder
            )
            if not output:
                raise ILEException(
                    f'No valid {"occluder" if is_occluder else "obstacle"} '
                    f'for object {target["type"]}'
                )
            chosen_definition, chosen_rotation = output
            return chosen_definition

        def _choose_rotation_callback() -> ObjectDefinition:
            return chosen_rotation

        label = (self.LABEL_KEYWORDS_OCCLUDERS
                 if is_occluder else self.LABEL_KEYWORDS_OBSTACLES)

        return self._generate_instance_with_valid_location(
            scene,
            bounds,
            _choose_definition_callback,
            index,
            [label],
            template,
            choose_rotation_callback=(
                _choose_rotation_callback if (chosen_rotation is not None)
                else None
            )
        )

    def _add_obstacle(self, scene, bounds, index, template):
        dataset = specific_objects.get_obstacle_definition_dataset()
        return self._add_obstacle_or_occluder(
            scene, bounds, dataset, index, False, template)

    def _add_occluder(self, scene, bounds, index, template):
        dataset = specific_objects.get_occluder_definition_dataset()
        return self._add_obstacle_or_occluder(
            scene, bounds, dataset, index, True, template)

    def _add_context(self, scene, bounds, index, template):
        targets = scene.get_targets()
        target_shapes = [target['debug']['shape'] for target in targets]

        def _choose_definition_callback() -> ObjectDefinition:
            return specific_objects.choose_distractor_definition(target_shapes)

        return self._generate_instance_with_valid_location(
            scene, bounds, _choose_definition_callback, index,
            [self.LABEL_KEYWORDS_CONTEXT], template)

    def _add_open_topped_container(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        template: KeywordObjectsConfig
    ) -> SceneObject:
        return self._add_special_container(
            scene,
            bounds,
            index,
            template,
            'open topped container',
            self.LABEL_KEYWORDS_OPEN_TOPPED_CONTAINERS,
            specific_objects.get_container_open_topped_definition_dataset()
        )

    def _add_special_container(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        template: KeywordObjectsConfig,
        keyword: str,
        label: str,
        dataset: DefinitionDataset
    ) -> SceneObject:
        def _choose_definition_callback() -> ObjectDefinition:
            return dataset.choose_random_definition()

        return self._generate_instance_with_valid_location(
            scene, bounds, _choose_definition_callback, index,
            [label], template)

    def _add_symmetric_container(
        self,
        scene: Scene,
        bounds: List[ObjectBounds],
        index: int,
        template: KeywordObjectsConfig
    ) -> SceneObject:
        return self._add_special_container(
            scene,
            bounds,
            index,
            template,
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
        labels: RandomizableString,
        template: KeywordObjectsConfig,
        choose_rotation_callback: Callable[[], float] = None
    ) -> SceneObject:

        object_repo = ObjectRepository.get_instance()
        shared_config = ILESharedConfiguration.get_instance()
        # Choose a random object definition for the keyword object type; we may
        # need to choose a different one later if this one can't fit.
        defn = shared_config.choose_definition_from_included_shapes(
            choose_definition_callback
        )
        MaterialRestrictions.valid_defn_or_raise(defn)

        # Copy the labels from the template into the label array.
        template_labels = template.labels or []
        if not isinstance(template_labels, list):
            template_labels = [template_labels]
        labels.extend(template_labels)

        # Find the keyword location or position/rotation from the template
        source_keyword_location = getattr(template, 'keyword_location')
        reconciled_keyword_location = choose_random(source_keyword_location)
        positions = getattr(template, 'position') or []
        positions = positions if isinstance(positions, list) else [positions]
        rotations = getattr(template, 'rotation') or []
        rotations = rotations if isinstance(rotations, list) else [rotations]
        # If positions are configured, but not rotations, or visa-versa, set a
        # random default for the unconfigured option.
        if positions and not rotations:
            rotations = [VectorIntConfig()]
        if rotations and not positions:
            positions = [VectorFloatConfig()]
        # If multiple possible positions and rotations are configured, try out
        # each pair in a random order.
        positions_rotations = list(itertools.product(positions, rotations))
        random.shuffle(positions_rotations)

        # Use the keyword location is one was configured.
        if reconciled_keyword_location:
            idl = KeywordLocation.get_keyword_location_object_tuple(
                reconciled_keyword_location,
                source_keyword_location,
                defn,
                scene.performer_start,
                bounds,
                scene.room_dimensions
            )
            if labels and idl:
                object_repo.add_to_labeled_objects(idl, labels)
            return idl.instance
        else:
            # Find a valid location for the current definition; if impossible,
            # choose a new definition and retry.
            for _ in range(MAX_TRIES):
                # Use the positions/rotations if they were configured.
                if positions_rotations:
                    for position, rotation in positions_rotations:
                        # Use the position and rotation configs to find the
                        # position and rotation vectors for the location.
                        chosen_position = choose_position(
                            position,
                            defn.dimensions.x,
                            defn.dimensions.z,
                            scene.room_dimensions.x,
                            scene.room_dimensions.y,
                            scene.room_dimensions.z
                        )
                        chosen_rotation = choose_rotation(rotation)
                        location = {
                            'position': vars(chosen_position),
                            'rotation': vars(chosen_rotation)
                        }
                        location['position']['y'] += defn.positionY
                        location['boundingBox'] = geometry.create_bounds(
                            dimensions=vars(defn.dimensions),
                            offset=vars(defn.offset),
                            position=location['position'],
                            rotation=location['rotation'],
                            standing_y=defn.positionY
                        )
                        # If this location is not valid, try a different one.
                        if not geometry.validate_location_rect(
                            location['boundingBox'],
                            vars(scene.performer_start.position),
                            bounds,
                            vars(scene.room_dimensions)
                        ):
                            location = None
                        # Otherwise, break the loop.
                        if location:
                            break
                else:
                    # Otherwise choose a random unoccupied location.
                    location = geometry.calc_obj_pos(
                        vars(scene.performer_start.position),
                        bounds,
                        defn,
                        room_dimensions=vars(scene.room_dimensions),
                        rotation_func=choose_rotation_callback
                    )
                # If this location is valid, break the loop.
                if location:
                    break
                # Otherwise, try a different object definition.
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

    def _get_generator(self, keyword: str) -> Callable:
        if keyword == self.KEYWORDS_ASYMMETRIC_CONTAINERS:
            return self._add_asymmetric_container
        if keyword == self.KEYWORDS_BINS:
            return self._add_bin_container
        if keyword == self.KEYWORDS_CONTEXT:
            return self._add_context
        if keyword == self.KEYWORDS_CONFUSORS:
            return self._add_confusor
        if keyword == self.KEYWORDS_CONTAINERS:
            return self._add_container
        if keyword == self.KEYWORDS_CONTAINERS_CAN_CONTAIN_TARGET:
            return self._add_container_target_valid
        if keyword == self.KEYWORDS_CONTAINERS_CANNOT_CONTAIN_TARGET:
            return self._add_container_target_invalid
        if keyword == self.KEYWORDS_OBSTACLES:
            return self._add_obstacle
        if keyword == self.KEYWORDS_OCCLUDERS:
            return self._add_occluder
        if keyword == self.KEYWORDS_OPEN_TOPPED_CONTAINERS:
            return self._add_open_topped_container
        if keyword == self.KEYWORDS_SYMMETRIC_CONTAINERS:
            return self._add_symmetric_container
        return None
