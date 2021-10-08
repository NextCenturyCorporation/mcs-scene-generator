import copy
import random
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from . import exceptions, tags
from .definitions import (
    DefinitionDataset,
    ImmutableObjectDefinition,
    ObjectDefinition,
    is_similar_except_in_color,
    is_similar_except_in_shape,
    is_similar_except_in_size,
)
from .specific_objects import get_pickupable_definition_dataset

MAX_TRIES = 50
MIN_RANDOM_INTERVAL = 0.05
PERFORMER_HALF_WIDTH = 0.27
PERFORMER_WIDTH = PERFORMER_HALF_WIDTH * 2.0

MAX_REACH_DISTANCE = 1.0
MOVE_DISTANCE = 0.1
PERFORMER_CAMERA_Y = 0.762

DISTRACTOR_DATASET = None


def random_real(a: float, b: float,
                step: float = MIN_RANDOM_INTERVAL) -> float:
    """Return a random real number N where a <= N <= b and N - a is
    divisible by step."""
    steps = int((b - a) / step)
    try:
        n = random.randint(0, steps)
    except ValueError as e:
        raise ValueError(f'bad args to random_real: ({a}, {b}, {step})', e)
    return a + (n * step)


def instantiate_object(
    definition: ObjectDefinition,
    object_location: Dict[str, Any],
    materials_list: Optional[List[Tuple[str, List[str]]]] = None
) -> Dict[str, Any]:
    """Create a new object from an object definition (as from the objects.json
    file). object_location will be modified by this function."""
    if definition is None or object_location is None:
        raise ValueError('instantiate_object cannot take None parameters')

    if (
        definition.chooseMaterialList or definition.chooseSizeList or
        definition.chooseTypeList
    ):
        raise exceptions.SceneException(
            f'ObjectDefinition passed to instantiate_object still has one or '
            f'more choice lists, but it should not by now... How has '
            f'finalize_object_definition() not yet been called on it? '
            f'{definition}'
        )

    # TODO MCS-697 Define and use an ObjectInstance class here.
    instance = {
        'id': str(uuid.uuid4()),
        'type': definition.type,
        'mass': definition.mass * definition.massMultiplier,
        'salientMaterials': definition.salientMaterials,
        'debug': {
            'dimensions': vars(definition.dimensions),
            'info': [definition.size],
            'positionY': definition.positionY,
            'role': '',
            'shape': definition.shape,
            'size': definition.size
        }
    }

    if not definition.dimensions:
        raise exceptions.SceneException(
            f'object definition "{definition.type}" doesn\'t have dimensions'
        )

    instance['debug'][tags.SCENE.UNTRAINED_CATEGORY] = (
        definition.untrainedCategory
    )
    instance['debug'][tags.SCENE.UNTRAINED_COLOR] = (
        definition.untrainedColor
    )
    instance['debug'][tags.SCENE.UNTRAINED_COMBINATION] = (
        definition.untrainedCombination
    )
    instance['debug'][tags.SCENE.UNTRAINED_SHAPE] = (
        definition.untrainedShape
    )
    instance['debug'][tags.SCENE.UNTRAINED_SIZE] = (
        definition.untrainedSize
    )

    for attribute in definition.attributes:
        instance[attribute] = True

    object_location = copy.deepcopy(object_location)
    object_location['position']['x'] -= definition.offset.x
    object_location['position']['z'] -= definition.offset.z

    instance['debug']['offset'] = vars(definition.offset)
    if definition.closedDimensions:
        instance['debug']['closedDimensions'] = vars(
            definition.closedDimensions
        )
    if definition.closedOffset:
        instance['debug']['closedOffset'] = vars(definition.closedOffset)

    if 'rotation' not in object_location:
        object_location['rotation'] = {'x': 0, 'y': 0, 'z': 0}

    object_location['rotation']['x'] += definition.rotation.x
    object_location['rotation']['y'] += definition.rotation.y
    object_location['rotation']['z'] += definition.rotation.z

    shows = [object_location]
    instance['shows'] = shows
    object_location['stepBegin'] = 0
    object_location['scale'] = vars(definition.scale)

    if not definition.color:
        raise exceptions.SceneException(
            f'ObjectDefinition passed to instantiate_object does not have any '
            f'colors yet, but it should by now... How has this happened? '
            f'{definition}'
        )

    colors = sorted(list(set(definition.color)))
    instance['debug']['materialCategory'] = (definition.materialCategory or [])
    instance['materials'] = definition.materials
    instance['debug']['color'] = colors

    # The info list contains words that we can use to filter on specific
    # object tags in the UI. Start with this specific ordering of object
    # tags in the info list needed for making the goalString:
    # size weight color(s) material(s) shape
    if 'pickupable' in definition.attributes:
        instance['debug']['weight'] = 'light'
    elif 'moveable' in definition.attributes:
        instance['debug']['weight'] = 'heavy'
    else:
        instance['debug']['weight'] = 'massive'
    instance['debug']['info'].append(instance['debug']['weight'])

    instance['debug']['info'].extend(instance['debug']['color'])

    salient_materials = definition.salientMaterials
    if salient_materials:
        instance['salientMaterials'] = salient_materials
        instance['debug']['info'].extend(salient_materials)

    instance['debug']['info'].extend(instance['debug']['shape'])

    # Use the object's goalString for goal descriptions.
    instance['debug']['goalString'] = ' '.join(instance['debug']['info'])

    instance['debug']['salientMaterials'] = instance['salientMaterials']
    for key in ['salientMaterials', 'color', 'shape']:
        if instance['debug'][key] and len(instance['debug'][key]) > 1:
            instance['debug']['info'].append(' '.join(instance['debug'][key]))

    info_keys = ['size', 'weight', 'salientMaterials', 'color', 'shape']
    for index_1, key_1 in enumerate(info_keys):
        value_1 = instance['debug'][key_1]
        if isinstance(value_1, list):
            value_1 = ' '.join(value_1)
        for index_2, key_2 in enumerate(info_keys):
            value_2 = instance['debug'][key_2]
            if isinstance(value_2, list):
                value_2 = ' '.join(value_2)
            if index_2 > index_1 and value_1 and value_2:
                instance['debug']['info'].append(value_1 + ' ' + value_2)

    instance['debug']['info'].append(instance['debug']['goalString'])

    is_untrained = False

    for tag in [
        tags.SCENE.UNTRAINED_CATEGORY,
        tags.SCENE.UNTRAINED_COLOR,
        tags.SCENE.UNTRAINED_COMBINATION,
        tags.SCENE.UNTRAINED_SHAPE,
        tags.SCENE.UNTRAINED_SIZE
    ]:
        if instance['debug'][tag]:
            instance['debug']['info'].append(tags.tag_to_label(tag))
            is_untrained = True

    if is_untrained:
        instance['debug']['info'].append(
            'untrained ' + instance['debug']['goalString']
        )

    # Add isContainer tag if needed.
    instance['debug']['enclosedAreas'] = copy.deepcopy(
        definition.enclosedAreas or []
    )
    if len(instance['debug']['enclosedAreas']) > 0:
        instance['debug'][tags.role_to_tag(tags.ROLES.CONTAINER)] = True

    return instance


def get_similar_definition(
    target_object: Union[ObjectDefinition, Dict[str, Any]],
    definition_dataset: DefinitionDataset,
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> Optional[ObjectDefinition]:
    """Get an object definition similar to obj but different in one of
    type, dimensions, or color. It is possible but unlikely that no such
    definition can be found, in which case it returns None.
    """

    choices = ['color', 'size', 'shape']
    if not unshuffled:
        random.shuffle(choices)

    for choice in choices:
        if choice == 'color':
            similarity_function = is_similar_except_in_color
        elif choice == 'shape':
            similarity_function = is_similar_except_in_shape
        elif choice == 'size':
            similarity_function = is_similar_except_in_size

        # Just find and return the first similar definition, since this
        # function may otherwise take a very long time to run.
        for definition in definition_dataset.definitions():
            if similarity_function(target_object, definition):
                definition.difference = choice
                return definition

    return None


def move_to_location(
    object_instance: Dict[str, Any],
    previous_location: Dict[str, Any],
    object_bounds: List[Dict[str, float]],
    previous_object: ObjectDefinition
) -> Dict[str, Any]:
    """Move the given object to a new location and return the object."""
    location = copy.deepcopy(previous_location)
    if previous_object and previous_object.offset:
        location['position']['x'] += previous_object.offset.x
        location['position']['z'] += previous_object.offset.z
    if 'offset' in object_instance['debug']:
        location['position']['x'] -= object_instance['debug']['offset']['x']
        location['position']['z'] -= object_instance['debug']['offset']['z']
    object_instance['shows'][0]['position'] = location['position']
    object_instance['shows'][0]['rotation'] = location['rotation']
    object_instance['shows'][0]['boundingBox'] = object_bounds
    return object_instance


def choose_distractor_definition(
    shapes_list: List[List[str]]
) -> ObjectDefinition:
    """Choose and return a distractor definition for the given objects."""
    # Use the final shape, since it should always be the most descriptive.
    invalid_shape_list = [shapes[-1] for shapes in shapes_list]

    # Save the distractor dataset for future use once it's made.
    global DISTRACTOR_DATASET
    if not DISTRACTOR_DATASET:
        # Distractors should always be both trained and pickupable.
        DISTRACTOR_DATASET = (
            get_pickupable_definition_dataset().filter_on_trained()
        )

    def _filter_data_callback(definition: ImmutableObjectDefinition) -> bool:
        # Distractors cannot have the same shape as an existing object from the
        # given list so we don't unintentionally generate a new confusor.
        return definition.shape[-1] not in invalid_shape_list

    dataset = DISTRACTOR_DATASET.filter_on_custom(_filter_data_callback)
    return dataset.choose_random_definition()
