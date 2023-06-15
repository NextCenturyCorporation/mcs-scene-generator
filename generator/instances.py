import copy
import uuid
from typing import Any, Dict

from . import exceptions, tags
from .definitions import ObjectDefinition
from .geometry import create_bounds
from .objects import SceneObject


def instantiate_object(
    definition: ObjectDefinition,
    object_location: Dict[str, Any]
) -> SceneObject:
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
    instance = SceneObject({
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
    })

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

    if 'rotation' not in object_location:
        object_location['rotation'] = {'x': 0, 'y': 0, 'z': 0}

    object_location['rotation']['x'] += definition.rotation.x
    object_location['rotation']['y'] += definition.rotation.y
    object_location['rotation']['z'] += definition.rotation.z

    instance['debug']['originalRotation'] = vars(definition.rotation)

    shows = [object_location]
    instance['shows'] = shows
    object_location['stepBegin'] = 0
    object_location['scale'] = vars(definition.scale)

    if 'boundingBox' not in object_location:
        object_location['boundingBox'] = create_bounds(
            dimensions=vars(definition.dimensions),
            offset=vars(definition.offset),
            position=object_location['position'],
            rotation=object_location['rotation'],
            standing_y=definition.positionY
        )

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


def get_earliest_active_step(instance: SceneObject) -> int:
    """Return the last step on which the given instance is scripted to move,
    rotate, or have a force applied to it. Return -1 if the given instance is
    never scripted to move, rotate, or has a force applied to it."""
    actions = (
        instance.get('forces', []) + instance.get('moves', []) +
        instance.get('rotates', []) + instance.get('torques', [])
    )
    if not actions:
        return -1
    return min([item['stepBegin'] for item in actions])


def get_last_move_or_rotate_step(instance: SceneObject) -> int:
    """Return the last step on which the given instance is scripted to move or
    rotate, or -1 if the given instance never moves or rotates. Does not work
    with scripted forces."""
    moves_or_rotates = instance.get('moves', []) + instance.get('rotates', [])
    if not moves_or_rotates:
        return -1
    return max([item['stepEnd'] for item in moves_or_rotates])
