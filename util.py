import copy
import math
import random
import uuid
from typing import Dict, Any, Optional, List, Tuple

import exceptions
import materials
import objects
import tags


MAX_SIZE_DIFFERENCE = 0.05
MAX_TRIES = 50
MIN_RANDOM_INTERVAL = 0.05
PERFORMER_HALF_WIDTH = 0.27
PERFORMER_WIDTH = PERFORMER_HALF_WIDTH * 2.0

MAX_REACH_DISTANCE = 1.0
MOVE_DISTANCE = 0.1
PERFORMER_CAMERA_Y = 0.762


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


def finalize_object_definition(
    object_definition: Dict[str, Any],
    choice_material: Optional[Dict[str, Any]] = None,
    choice_size: Optional[Dict[str, Any]] = None,
    choice_type: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    definition_copy = copy.deepcopy(object_definition)

    if choice_material is None and 'chooseMaterial' in definition_copy:
        choice_material = random.choice(definition_copy['chooseMaterial'])

    if choice_size is None and 'chooseSize' in definition_copy:
        choice_size = random.choice(definition_copy['chooseSize'])

    if choice_type is None and 'chooseType' in definition_copy:
        choice_type = random.choice(definition_copy['chooseType'])

    if choice_material:
        for key in choice_material:
            definition_copy[key] = choice_material[key]
        definition_copy.pop('chooseMaterial', None)

    if choice_size:
        for key in choice_size:
            definition_copy[key] = choice_size[key]
        definition_copy.pop('chooseSize', None)

    if choice_type:
        for key in choice_type:
            definition_copy[key] = choice_type[key]
        definition_copy.pop('chooseType', None)

    return definition_copy


def generate_materials_lists(material_category_list, previous_materials_lists):
    if len(material_category_list) == 0:
        return previous_materials_lists

    output_materials_lists = []
    material_attr = material_category_list[0].upper() + '_MATERIALS'
    for material_and_color in getattr(materials, material_attr):
        if not previous_materials_lists:
            output_materials_lists.append([material_and_color])
        else:
            for material_list in previous_materials_lists:
                output_materials_lists.append(
                    copy.deepcopy(material_list) + [material_and_color])
    return generate_materials_lists(
        material_category_list[1:],
        output_materials_lists
    )


def finalize_object_materials_and_colors(
    object_definition: Dict[str, Any],
    override_materials_list: Optional[List[Tuple[str, List[str]]]] = None
) -> List[Dict[str, Any]]:
    """Finalizes each possible choice of materials (patterns/textures)
    and colors as a copy of the given object
    definition and returns the list."""

    materials_lists = (
        [override_materials_list] if override_materials_list else []
    )

    if 'materialCategory' not in object_definition:
        object_definition['materialCategory'] = []

    if not materials_lists:
        materials_lists = generate_materials_lists(
            object_definition['materialCategory'],
            []
        )

    if not materials_lists:
        definition_copy = copy.deepcopy(object_definition)
        definition_copy['color'] = definition_copy.get('color', [])
        definition_copy['materials'] = definition_copy.get('materials', [])
        return [definition_copy]

    object_definition_list = []
    for materials_list in materials_lists:
        definition_copy = copy.deepcopy(object_definition)
        definition_copy['color'] = []
        definition_copy['materials'] = [
            material_and_color[0] for material_and_color in materials_list]
        for material_and_color in materials_list:
            if material_and_color[0] in materials.UNTRAINED_COLOR_LIST:
                definition_copy['untrainedColor'] = True
            for color in material_and_color[1]:
                if color not in definition_copy['color']:
                    definition_copy['color'].append(color)
        object_definition_list.append(definition_copy)
    return object_definition_list


def instantiate_object(
    definition: Dict[str, Any],
    object_location: Dict[str, Any],
    materials_list: Optional[List[Tuple[str, List[str]]]] = None
) -> Dict[str, Any]:
    """Create a new object from an object definition (as from the objects.json
    file). object_location will be modified by this function."""
    if definition is None or object_location is None:
        raise ValueError('instantiate_object cannot take None parameters')

    # Call the finalize function here in case it wasn't called before now
    # (calling it twice shouldn't hurt anything).
    definition = finalize_object_definition(definition)

    instance = {
        'id': str(uuid.uuid4()),
        'type': definition['type'],
        'role': '',
        'info': [definition['size']],
        'mass': definition['mass'] * definition.get('massMultiplier', 1),
        'positionY': definition.get('positionY', 0),
        'salientMaterials': None,
        'color': None,
        'shape': (
            definition['shape'] if isinstance(definition['shape'], list)
            else [definition['shape']]
        ),
        'size': definition['size']
    }
    if 'dimensions' in definition:
        instance['dimensions'] = definition['dimensions']
    else:
        raise exceptions.SceneException(
            f'object definition "{definition["type"]}" doesn\'t have '
            f'dimensions')

    instance[tags.SCENE.UNTRAINED_CATEGORY] = (
        definition.get('untrainedCategory', False)
    )
    instance[tags.SCENE.UNTRAINED_COLOR] = (
        definition.get('untrainedColor', False)
    )
    instance[tags.SCENE.UNTRAINED_COMBINATION] = (
        definition.get('untrainedCombination', False)
    )
    instance[tags.SCENE.UNTRAINED_SHAPE] = (
        definition.get('untrainedShape', False)
    )
    instance[tags.SCENE.UNTRAINED_SIZE] = (
        definition.get('untrainedSize', False)
    )

    for attribute in definition.get('attributes', []):
        instance[attribute] = True

    object_location = copy.deepcopy(object_location)
    if 'offset' in definition:
        object_location['position']['x'] -= definition['offset']['x']
        object_location['position']['z'] -= definition['offset']['z']

    instance['offset'] = definition.get('offset', {'x': 0, 'y': 0, 'z': 0})
    if definition.get('closedDimensions'):
        instance['closedDimensions'] = definition.get('closedDimensions')
    if definition.get('closedOffset'):
        instance['closedOffset'] = definition.get('closedOffset')

    if 'rotation' not in definition:
        definition['rotation'] = {'x': 0, 'y': 0, 'z': 0}

    if 'rotation' not in object_location:
        object_location['rotation'] = {'x': 0, 'y': 0, 'z': 0}

    object_location['rotation']['x'] += definition['rotation']['x']
    object_location['rotation']['y'] += definition['rotation']['y']
    object_location['rotation']['z'] += definition['rotation']['z']

    shows = [object_location]
    instance['shows'] = shows
    object_location['stepBegin'] = 0
    object_location['scale'] = definition['scale']

    if 'color' not in definition or 'materials' not in definition:
        definition = random.choice(
            finalize_object_materials_and_colors(definition, materials_list)
        )

    definition['color'] = sorted(list(set(definition['color'])))
    instance['materialCategory'] = definition.get('materialCategory', [])
    instance['materials'] = definition['materials']
    instance['color'] = definition['color']

    # The info list contains words that we can use to filter on specific
    # object tags in the UI. Start with this specific ordering of object
    # tags in the info list needed for making the goalString:
    # size weight color(s) material(s) shape
    if 'pickupable' in definition.get('attributes', []):
        instance['weight'] = 'light'
    elif 'moveable' in definition.get('attributes', []):
        instance['weight'] = 'heavy'
    else:
        instance['weight'] = 'massive'
    instance['info'].append(instance['weight'])

    instance['info'].extend(instance['color'])

    if 'salientMaterials' in definition:
        salient_materials = definition['salientMaterials']
        instance['salientMaterials'] = salient_materials
        instance['info'].extend(salient_materials)

    instance['info'].extend(instance['shape'])

    # Use the object's goalString for goal descriptions.
    instance['goalString'] = ' '.join(instance['info'])

    for key in ['salientMaterials', 'color', 'shape']:
        if instance[key] and len(instance[key]) > 1:
            instance['info'].append(' '.join(instance[key]))

    info_keys = ['size', 'weight', 'salientMaterials', 'color', 'shape']
    for index_1, key_1 in enumerate(info_keys):
        value_1 = instance[key_1]
        if isinstance(value_1, list):
            value_1 = ' '.join(value_1)
        for index_2, key_2 in enumerate(info_keys):
            value_2 = instance[key_2]
            if isinstance(value_2, list):
                value_2 = ' '.join(value_2)
            if index_2 > index_1 and value_1 and value_2:
                instance['info'].append(value_1 + ' ' + value_2)

    instance['info'].append(instance['goalString'])

    is_untrained = False

    for tag in [
        tags.SCENE.UNTRAINED_CATEGORY,
        tags.SCENE.UNTRAINED_COLOR,
        tags.SCENE.UNTRAINED_COMBINATION,
        tags.SCENE.UNTRAINED_SHAPE,
        tags.SCENE.UNTRAINED_SIZE
    ]:
        if instance[tag]:
            instance['info'].append(tags.tag_to_label(tag))
            is_untrained = True

    if is_untrained:
        instance['info'].append('untrained ' + instance['goalString'])

    # Add isContainer tag if needed.
    instance['enclosedAreas'] = definition.get('enclosedAreas', [])
    if len(instance['enclosedAreas']) > 0:
        instance[tags.role_to_tag(tags.ROLES.CONTAINER)] = True

    return instance


def get_similar_definition(
    target_object: Dict[str, Any],
    nested_definition_list: List[List[Dict[str, Any]]]
) -> Optional[Dict[str, Any]]:
    """Get an object definition similar to obj but different in one of
    type, material, or scale. It is possible but unlikely that no such
    definition can be found, in which case it returns None.
    """
    choices = ['color', 'shape', 'size']
    for choice in choices:
        if choice == 'color':
            similarity_function = is_similar_except_in_color
        elif choice == 'shape':
            similarity_function = is_similar_except_in_shape
        elif choice == 'size':
            similarity_function = is_similar_except_in_size

        output_list = []
        for definition_list in nested_definition_list:
            output_internal_list = []
            for definition in definition_list:
                output_double_internal_list = []
                for comparison in (
                    finalize_object_materials_and_colors(definition)
                ):
                    if similarity_function(target_object, comparison):
                        output_double_internal_list.append(comparison)
            if len(output_double_internal_list) > 0:
                output_internal_list.append(output_double_internal_list)
        if len(output_internal_list) > 0:
            output_list.append(output_internal_list)

        if len(output_list) == 0:
            continue

        object_definition = random.choice(random.choice(random.choice(
            output_list
        )))
        object_definition['similarity'] = choice
        return object_definition

    return None


def finalize_each_definition_choice(
    object_definition: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Finalize each possible material category, size, and type choice in the
    given object definition (but NOT the materials property itself) and return
    the list with each possible object definition choice."""
    choice_list = []
    for prop in ['chooseMaterial', 'chooseSize', 'chooseType']:
        if prop in object_definition and len(object_definition[prop]) > 0:
            previous_choice_list = copy.deepcopy(choice_list)
            next_choice_list = []
            for choice_string in object_definition[prop]:
                if not previous_choice_list:
                    choice_dict = {
                        'chooseMaterial': None,
                        'chooseSize': None,
                        'chooseType': None
                    }
                    choice_dict[prop] = choice_string
                    next_choice_list.append(choice_dict)
                else:
                    for previous_choice_dict in previous_choice_list:
                        choice_dict = copy.deepcopy(previous_choice_dict)
                        choice_dict[prop] = choice_string
                        next_choice_list.append(choice_dict)
            choice_list = next_choice_list

    if not choice_list:
        return [finalize_object_definition(copy.deepcopy(object_definition))]

    output_list = []
    for choice_dict in choice_list:
        output_list.append(
            finalize_object_definition(
                copy.deepcopy(object_definition),
                choice_material=choice_dict['chooseMaterial'],
                choice_size=choice_dict['chooseSize'],
                choice_type=choice_dict['chooseType']
            )
        )
    random.shuffle(output_list)
    return output_list


def move_to_location(
    object_instance: Dict[str, Any],
    location: Dict[str, Any],
    object_bounds: List[Dict[str, float]],
    previous_object: Dict[str, Any]
) -> Dict[str, Any]:
    """Move the given object to a new location and return the object."""
    new_location = copy.deepcopy(location)
    if previous_object and 'offset' in previous_object:
        new_location['position']['x'] += previous_object['offset']['x']
        new_location['position']['z'] += previous_object['offset']['z']
    if 'offset' in object_instance:
        new_location['position']['x'] -= object_instance['offset']['x']
        new_location['position']['z'] -= object_instance['offset']['z']
    object_instance['shows'][0]['position'] = new_location['position']
    object_instance['shows'][0]['rotation'] = new_location['rotation']
    object_instance['shows'][0]['boundingBox'] = object_bounds
    return object_instance


def retrieve_complete_definition_list(
    nested_definition_list: List[List[Dict[str, Any]]]
) -> List[List[Dict[str, Any]]]:
    """Return an object definition list in which finalize_object_definition was
    called on each definition in the given list so that the returned list has
    each possible choice (except materials)."""
    output_list = []
    for definition_list in nested_definition_list:
        output_internal_list = []
        for definition in definition_list:
            output_internal_list.extend(finalize_each_definition_choice(
                definition
            ))
        random.shuffle(output_internal_list)
        output_list.append(output_internal_list)
    random.shuffle(output_list)
    return output_list


def retrieve_trained_definition_list(
    nested_definition_list: List[List[Dict[str, Any]]]
) -> List[List[Dict[str, Any]]]:
    """Return only the trained object definitions from the given list."""
    output_list = []
    for definition_list in nested_definition_list:
        output_internal_list = []
        for definition in definition_list:
            if not (
                (definition.get(tags.SCENE.UNTRAINED_CATEGORY, False)) or
                (definition.get(tags.SCENE.UNTRAINED_COLOR, False)) or
                (definition.get(tags.SCENE.UNTRAINED_COMBINATION, False)) or
                (definition.get(tags.SCENE.UNTRAINED_SHAPE, False)) or
                (definition.get(tags.SCENE.UNTRAINED_SIZE, False))
            ):
                output_internal_list.append(definition)
        if len(output_internal_list) > 0:
            output_list.append(output_internal_list)
    return output_list


def retrieve_untrained_definition_list(
    nested_definition_list: List[List[Dict[str, Any]]],
    untrained_tag: str
) -> List[List[Dict[str, Any]]]:
    """Return only the object definitions from the given list that have the
    given untrained tag but are otherwise completely trained."""
    # TODO FIXME MCS-635
    if untrained_tag == tags.SCENE.UNTRAINED_SHAPE:
        return retrieve_trained_definition_list(nested_definition_list)
    trained_tag_list = [tag for tag in [
        tags.SCENE.UNTRAINED_CATEGORY,
        tags.SCENE.UNTRAINED_COLOR,
        tags.SCENE.UNTRAINED_COMBINATION,
        tags.SCENE.UNTRAINED_SHAPE,
        tags.SCENE.UNTRAINED_SIZE
    ] if tag != untrained_tag]
    output_list = []
    for definition_list in nested_definition_list:
        output_internal_list = []
        for definition in definition_list:
            if definition.get(untrained_tag, False):
                validated = True
                for tag in trained_tag_list:
                    if definition.get(tag, False):
                        validated = False
                        break
                if validated:
                    output_internal_list.append(definition)
        if len(output_internal_list) > 0:
            output_list.append(output_internal_list)
    return output_list


def _create_size_list(
    definition_or_instance_1: Dict[str, Any],
    definition_or_instance_2: Dict[str, Any],
    only_diagonal_size: bool
) -> List[Tuple[float, float]]:
    x_size_1 = definition_or_instance_1['dimensions']['x']
    x_size_2 = definition_or_instance_2['dimensions']['x']
    y_size_1 = definition_or_instance_1['dimensions']['y']
    y_size_2 = definition_or_instance_2['dimensions']['y']
    z_size_1 = definition_or_instance_1['dimensions']['z']
    z_size_2 = definition_or_instance_2['dimensions']['z']
    size_list = [
        (x_size_1, x_size_2),
        (y_size_1, y_size_2),
        (z_size_1, z_size_2)
    ]
    if only_diagonal_size:
        size_list = [(
            math.sqrt(x_size_1**2 + z_size_1**2),
            math.sqrt(x_size_2**2 + z_size_2**2)
        )]
    return size_list


def are_materials_equivalent(
    material_list_1: List[str],
    material_list_2: List[str]
) -> bool:
    """Returns whether the two given material string lists are equivalent."""
    material_set_1 = set(material_list_1)
    material_set_2 = set(material_list_2)
    return material_set_1 == material_set_2


def is_similar_except_in_color(
    definition_or_instance_1: Dict[str, Any],
    definition_or_instance_2: Dict[str, Any],
    only_diagonal_size: bool = False
) -> bool:
    """Return whether the two given objects are similar in shape
    (type) and size (dimensions) but not color (material category)."""
    size_list = _create_size_list(
        definition_or_instance_1,
        definition_or_instance_2,
        only_diagonal_size
    )
    return (
        definition_or_instance_1 != definition_or_instance_2 and
        definition_or_instance_1['type'] ==
        definition_or_instance_2['type'] and
        'materials' in definition_or_instance_1 and
        'materials' in definition_or_instance_2 and
        not are_materials_equivalent(
            definition_or_instance_1['materials'],
            definition_or_instance_2['materials']
        ) and
        definition_or_instance_1['color'] !=
        definition_or_instance_2['color'] and
        all([(
            (size_1 + MAX_SIZE_DIFFERENCE) >= size_2 and
            (size_1 - MAX_SIZE_DIFFERENCE) <= size_2
        ) for size_1, size_2 in size_list])
    )


def is_similar_except_in_shape(
    definition_or_instance_1: Dict[str, Any],
    definition_or_instance_2: Dict[str, Any],
    only_diagonal_size: bool = False
) -> bool:
    """Return whether the two given objects are similar in color
    (material category) and size (dimensions) but not shape (type)."""
    size_list = _create_size_list(
        definition_or_instance_1,
        definition_or_instance_2,
        only_diagonal_size
    )
    return (
        definition_or_instance_1 != definition_or_instance_2 and
        definition_or_instance_1['type'] !=
        definition_or_instance_2['type'] and
        'materials' in definition_or_instance_1 and
        'materials' in definition_or_instance_2 and
        are_materials_equivalent(
            definition_or_instance_1['materials'],
            definition_or_instance_2['materials']
        ) and
        all([(
            (size_1 + MAX_SIZE_DIFFERENCE) >= size_2 and
            (size_1 - MAX_SIZE_DIFFERENCE) <= size_2
        ) for size_1, size_2 in size_list])
    )


def is_similar_except_in_size(
    definition_or_instance_1: Dict[str, Any],
    definition_or_instance_2: Dict[str, Any],
    only_diagonal_size: bool = False
) -> bool:
    """Return whether the two given objects are similar in color
    (material category) and shape (type) but not size (dimensions)."""
    size_list = _create_size_list(
        definition_or_instance_1,
        definition_or_instance_2,
        only_diagonal_size
    )
    return (
        definition_or_instance_1 != definition_or_instance_2 and
        definition_or_instance_1['type'] ==
        definition_or_instance_2['type'] and
        'materials' in definition_or_instance_1 and
        'materials' in definition_or_instance_2 and
        are_materials_equivalent(
            definition_or_instance_1['materials'],
            definition_or_instance_2['materials']
        ) and
        any([(
            (size_1 + MAX_SIZE_DIFFERENCE) < size_2 or
            (size_1 - MAX_SIZE_DIFFERENCE) > size_2
        ) for size_1, size_2 in size_list])
    )


def choose_distractor_definition(
    target_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Choose and return a distractor definition for the given objects."""
    invalid_shape_list = [target['shape'][-1] for target in target_list]
    for _ in range(MAX_TRIES):
        # Distractors should always be both trained and pickupable.
        definition_list = random.choice(retrieve_trained_definition_list(
            objects.get(objects.ObjectDefinitionList.PICKUPABLES)
        ))
        # Finalize the material now.
        definition = random.choice(finalize_object_materials_and_colors(
            finalize_object_definition(random.choice(definition_list))
        ))
        # Distractors cannot have the same shape as an existing object from the
        # given list so we don't unintentionally generate a new confusor.
        if definition['shape'][-1] not in invalid_shape_list:
            break
        definition = None
    return definition
