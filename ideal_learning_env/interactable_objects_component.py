import logging
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Union

from machine_common_sense.config_manager import Vector3d

from generator import (
    DefinitionDataset,
    ImmutableObjectDefinition,
    ObjectDefinition,
    containers,
    geometry,
    materials,
    specific_objects,
    util,
)
from ideal_learning_env.defs import ILEDelayException

from .choosers import choose_random
from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import ILEConfigurationException, ILEException, find_bounds
from .interactable_object_config import (
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

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=1))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(
            materials.ALL_MATERIAL_LISTS + materials.ALL_MATERIAL_STRINGS
        )
    ))
    def set_specific_interactable_objects(self, data: Any) -> None:
        self.specific_interactable_objects = data

    def get_specific_interactable_objects(self) -> List[
        InteractableObjectConfig
    ]:
        # force to array
        if self.specific_interactable_objects is None:
            return []
        sio = self.specific_interactable_objects
        sio = sio if isinstance(sio, list) else [sio]
        return [choose_random(object_config) for object_config in (sio or [])]

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug('Running specific interactable objects component...')

        scene['objects'] = scene.get('objects', [])
        bounds = find_bounds(scene['objects'])
        self._delayed_templates = []

        # Get the templates here to randomly choose the number of objects to
        # generate for each template; ignore the remaining properties for now.
        # TODO MCS-854 Should we reconsider this approach to the config?
        num_per_template = [
            template.num for template in
            self.get_specific_interactable_objects()
        ]

        # Save the original templates because we'll soon call create_instance
        # on each of them to randomly choose the remaining properties.
        templates = (
            self.specific_interactable_objects
            if isinstance(self.specific_interactable_objects, list) else
            [self.specific_interactable_objects]
        )

        for i in range(len(num_per_template)):
            object_config = templates[i]
            logger.debug(
                f'Creating {num_per_template[i]} of configured interactable '
                f'object template = {vars(object_config)}'
            )
            for j in range(num_per_template[i]):
                self._add_object_from_template(
                    scene, bounds, i, j, object_config)
        return scene

    def run_delayed_actions(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        scene['objects'] = scene.get('objects', [])
        bounds = find_bounds(scene['objects'])
        templates = self._delayed_templates
        self._delayed_templates = []
        for template in templates:
            self._add_object_from_template(scene, bounds, 0, 0, template)
        return scene

    def get_num_delayed_actions(self) -> bool:
        return len(self._delayed_templates)

    def _add_object_from_template(self, scene, bounds, i, j, object_config):
        try:
            new_obj = object_config.create_instance(
                scene['roomDimensions'],
                scene['performerStart'],
                bounds
            )
            if not new_obj:
                raise ILEException(
                    f"Failed to place specific object index={i} "
                    f"number={j}; please try using fewer objects."
                )
            scene['objects'].append(new_obj)
        except ILEDelayException:
            self._delayed_templates.append(object_config)


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
        logger.debug('Running random interactable objects component...')

        scene['objects'] = scene.get('objects', [])
        bounds = find_bounds(scene['objects'])
        num_objects = self.get_num_random_interactable_objects()
        logger.debug(
            f'Creating {num_objects} random interactable objects...'
        )

        retries = util.MAX_TRIES

        for n in range(num_objects):
            for _ in range(retries):
                object = self._get_object()
                MaterialRestrictions.valid_defn_or_raise(object)
                location = geometry.calc_obj_pos(
                    scene['performerStart']['position'],
                    bounds,
                    object,
                    room_dimensions=scene['roomDimensions']
                )
                if location is not None:
                    break
            if location is None:
                raise ILEException(
                    f"Failed to place object {n} after {retries} retries."
                    f"  Try using fewer objects.")
            scene['objects'].append(util.instantiate_object(object, location))

        return scene

    def _get_object(self) -> Dict[str, Any]:
        dataset = specific_objects.get_interactable_definition_dataset()
        return dataset.choose_random_definition()

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
        - `"obstacles"`: Objects that prevent movement through/under them but
        allow sight through them, like chairs or tables with four individual
        legs.
        - `"occluders"`: Objects that prevent both movement through/under them
        AND sight through them, like sofas or bookcases with solid back panels.
        This is completely different from the occluders in passive
        intuitive physics scenes.
        - `"context"`: Objects (also called "distractors") that are small,
        pickupable, and serve to clutter the room to possibly distract the AI.
        They are never the same shape as the target object, if the scene has a
        goal with a target object.
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
      - confusors: keywords_confusors
      - containers: keywords_container
      - containers_can_contain_target:
          keywords_container, keywords_container_can_contain_target
      - containers_cannot_contain_target:
          keywords_container, keywords_container_cannot_contain_target
      - obstacles: keywords_obstacles
      - occluders: keywords_occluders
      - context: keywords_context

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

    LABEL_KEYWORDS_CONFUSORS = "keywords_confusors"
    LABEL_KEYWORDS_CONTAINERS = "keywords_container"
    LABEL_KEYWORDS_CONTAINERS_CAN_CONTAIN_TARGET = "keywords_container_can_contain_target"  # noqa
    LABEL_KEYWORDS_CONTAINERS_CANNOT_CONTAIN_TARGET = "keywords_container_cannot_contain_target"  # noqa
    LABEL_KEYWORDS_OBSTACLES = "keywords_obstacles"
    LABEL_KEYWORDS_OCCLUDERS = "keywords_occluders"
    LABEL_KEYWORDS_CONTEXT = "keywords_context"

    FULL_KEYWORD_LIST = []

    DEFAULT_VALUE = [
        KeywordObjectsConfig(
            ["containers", "obstacles", "occluders"], MinMaxInt(2, 4)),
        KeywordObjectsConfig(
            "context", MinMaxInt(0, 10)),
    ]

    def __init__(self, data: Dict[str, Any]):
        self.FULL_KEYWORD_LIST = [
            self.LABEL_KEYWORDS_CONFUSORS,
            self.LABEL_KEYWORDS_CONTAINERS,
            self.LABEL_KEYWORDS_CONTAINERS_CAN_CONTAIN_TARGET,
            self.LABEL_KEYWORDS_CONTAINERS_CANNOT_CONTAIN_TARGET,
            self.LABEL_KEYWORDS_OBSTACLES,
            self.LABEL_KEYWORDS_OCCLUDERS,
            self.LABEL_KEYWORDS_CONTEXT]
        super().__init__(data)

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug('Running random keyword objects component...')

        scene['objects'] = scene.get('objects', [])
        bounds = find_bounds(scene['objects'])
        template_list = self.keyword_objects
        if template_list is None:
            template_list = self.DEFAULT_VALUE
        template_list = template_list if isinstance(
            template_list, List) else [template_list]

        switcher = {
            'confusors': self._add_confusor,
            'containers': self._add_container,
            'containers_can_contain_target': self._add_container_target_valid,
            'containers_cannot_contain_target':
                self._add_container_target_invalid,
            'obstacles': self._add_obstacle,
            'occluders': self._add_occluder,
            'context': self._add_context,
        }
        for template in template_list:
            num = choose_random(getattr(template, 'num', 1))
            logger.debug(
                f'Creating {num} of random keyword object template = '
                f'{vars(template)}'
            )
            for x in range(num):
                keyword_location = choose_random(
                    getattr(template, 'keyword_location'))
                keyword = choose_random(
                    getattr(
                        template,
                        'keyword',
                        self.FULL_KEYWORD_LIST))
                obj = switcher[keyword](
                    scene, bounds, x, keyword_location=keyword_location)
                scene['objects'].append(obj)

        return scene

    def _add_confusor(self, scene, bounds, index, keyword_location):
        # Requires target but ILE doesn't support that yet
        target = self._get_target_object(scene)
        if target is not None:
            dataset = specific_objects.get_interactable_definition_dataset()

            def _choose_definition_callback() -> ObjectDefinition:
                return util.get_similar_definition(target, dataset)

            logger.debug(
                f'Creating a confusor with the keyword location = '
                f'{keyword_location}'
            )

            return self._generate_instance_with_valid_location(
                scene, bounds, _choose_definition_callback, index,
                [self.LABEL_KEYWORDS_CONFUSORS], keyword_location)
        else:
            logger.warning(
                'Cannot create a confusor object without a configured goal '
                'and target object!'
            )

    #  TODO MCS-812 Move to some utility area?
    def _get_target_object(self, scene):
        tgt = None
        goal = scene.get('goal', {})
        metadata = goal.get('metadata', {})
        tar = metadata.get('target', {})
        targetId = tar.get('id', {})
        for o in scene['objects']:
            if o.get('id', '') == targetId:
                tgt = o
                break
        return tgt

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
        dataset = specific_objects.get_container_definition_dataset()

        if contain_target is not None:
            target = self._get_target_object(scene)
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
                dimensions=Vector3d(dim['x'], dim['y'], dim['z']))

            def _callback(definition: ImmutableObjectDefinition) -> bool:
                contain = (
                    containers.can_contain(definition, target_od) is not None
                )
                return contain_target == contain

            # Filter the dataset to only (in)valid container definitions.
            dataset = dataset.filter_on_custom(_callback)

            logger.debug(
                f'Creating a container with the keyword location = '
                f'{keyword_location} that '
                f'{"can" if contain_target else "cannot"} contain the target '
                f'object'
            )
        else:
            logger.debug(
                f'Creating a container with the keyword location = '
                f'{keyword_location}'
            )

        return self._generate_instance_with_valid_location(
            scene, bounds, dataset.choose_random_definition, index,
            labels, keyword_location)

    def _add_obstacle_or_occluder(
        self,
        scene: Dict[str, Any],
        bounds: List[List[Dict[str, float]]],
        dataset: DefinitionDataset,
        index: int,
        is_occluder: bool,
        keyword_location: KeywordLocationConfig
    ):
        target = self._get_target_object(scene)
        if target is None:
            chosen_definition = dataset.choose_random_definition()
            chosen_rotation = None
        else:
            output_list = geometry.retrieve_obstacle_occluder_definition_list(
                target,
                dataset,
                is_occluder
            )
            chosen_definition, chosen_rotation = random.choice(output_list)

        label = (self.LABEL_KEYWORDS_OCCLUDERS
                 if is_occluder else self.LABEL_KEYWORDS_OBSTACLES)

        def _choose_definition_callback() -> ObjectDefinition:
            return chosen_definition

        def _choose_rotation_callback() -> ObjectDefinition:
            return chosen_rotation

        logger.debug(
            f'Creating an {"occluder" if is_occluder else "obstacle"} with '
            f'the keyword location = {keyword_location}'
        )

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
        target = self._get_target_object(scene)
        targets = []
        if target is not None:
            targets = [target['debug']['shape']]

        def _choose_definition_callback() -> ObjectDefinition:
            return util.choose_distractor_definition(targets)

        logger.debug(
            f'Creating a context object (distractor) with the keyword '
            f'location = {keyword_location}'
        )

        return self._generate_instance_with_valid_location(
            scene, bounds, _choose_definition_callback, index,
            [self.LABEL_KEYWORDS_CONTEXT], keyword_location)

    def get_keyword_objects(self) -> List[KeywordObjectsConfig]:
        keyword_list = self.keyword_objects
        keyword_list = (
            self.DEFAULT_VALUE if keyword_list is None else keyword_list)
        keyword_list = keyword_list if isinstance(
            keyword_list, List) else [keyword_list]
        return [choose_random(keyword_obj) for keyword_obj in keyword_list]

    # If not null, each number must be an integer zero or greater.
    @ile_config_setter(validator=ValidateNumber(
        props=['num'],
        min_value=0)
    )
    def set_keyword_objects(self, data: Any) -> None:
        self.keyword_objects = data

    def _generate_instance_with_valid_location(
        self,
        scene: Dict[str, Any],
        bounds: List[List[Dict[str, float]]],
        choose_definition_callback: Callable[[], ObjectDefinition],
        index: int,
        labels: Union[str, List[str]] = None,
        keyword_location: KeywordLocationConfig = None,
        choose_rotation_callback: Callable[[], float] = None
    ) -> Dict[str, Any]:

        defn = choose_definition_callback()
        MaterialRestrictions.valid_defn_or_raise(defn)
        if keyword_location:
            idl = KeywordLocation.get_keyword_location_object_tuple(
                keyword_location, defn, scene['performerStart'], bounds,
                scene['roomDimensions'])

            if labels and idl:
                ObjectRepository.get_instance().add_to_labeled_objects(idl,
                                                                       labels)
            return idl.instance
        else:
            for _ in range(util.MAX_TRIES):
                defn = choose_definition_callback()
                MaterialRestrictions.valid_defn_or_raise(defn)
                location = geometry.calc_obj_pos(
                    scene['performerStart']['position'],
                    bounds,
                    defn,
                    room_dimensions=scene['roomDimensions'],
                    rotation_func=choose_rotation_callback
                )
                if location is not None:
                    break
            if location is None:
                raise ILEException(
                    f"Failed to place object {index} after {util.MAX_TRIES} "
                    f"retries. Try using fewer objects.")
            obj = util.instantiate_object(defn, location)
            if labels and obj:
                idl = InstanceDefinitionLocationTuple(obj, defn, location)
                ObjectRepository.get_instance().add_to_labeled_objects(idl,
                                                                       labels)
            return obj
