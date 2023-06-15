from __future__ import annotations

import copy
import math
import random
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from machine_common_sense.config_manager import Vector3d

from . import materials, tags
from .objects import SceneObject

MAX_SIZE_DIFF = 0.05


class _DefinitionChoice(ABC):

    @abstractmethod
    def get_debug_props(self) -> List[str]:
        """Return all the names of the debug properties."""
        return []

    @abstractmethod
    def get_props(self) -> List[str]:
        """Return all the names of the non-debug properties."""
        return []

    def get_all(self) -> Dict[str, Any]:
        """Return a dict with all the non-debug properties."""
        return self._get_all(self.get_props())

    def get_debug_all(self) -> Dict[str, Any]:
        """Return a dict with all the debug properties."""
        return self._get_all(self.get_debug_props())

    def _get_all(self, prop_list: List[str]) -> Dict[str, Any]:
        """Return all of this definition's properties with the given names."""
        return dict([
            (prop, getattr(self, prop)) for prop in prop_list
            if getattr(self, prop) is not None
        ])


@dataclass(init=False)
class MaterialChoice(_DefinitionChoice):
    massMultiplier: float = None
    materialCategory: List[str] = None
    salientMaterials: List[str] = None

    DEBUG_PROPS = ['massMultiplier', 'materialCategory']
    PROPS = ['salientMaterials']

    def __init__(
        self,
        materialCategory: List[str] = None,
        salientMaterials: List[str] = None,
        massMultiplier: float = 1
    ):
        self.massMultiplier = massMultiplier
        self.materialCategory = materialCategory
        self.salientMaterials = salientMaterials

    # Override
    def get_debug_props(self) -> List[str]:
        return self.DEBUG_PROPS

    # Override
    def get_props(self) -> List[str]:
        return self.PROPS


@dataclass(init=False)
class SizeChoice(_DefinitionChoice):
    dimensions: Vector3d = None
    enclosedAreas: List[Dict[str, Any]] = None
    mass: float = None
    notSideways: Dict[str, Any] = None
    offset: Vector3d = None
    openAreas: List[Dict[str, Any]] = None
    placerOffsetX: List[float] = None
    placerOffsetY: List[float] = None
    placerOffsetZ: List[float] = None
    positionY: float = None
    scale: Vector3d = None
    sideways: Dict[str, Any] = None
    size: str = None
    untrainedShape: bool = None
    untrainedSize: bool = None

    DEBUG_PROPS = [
        'dimensions',
        'enclosedAreas',
        'offset',
        'openAreas',
        'placerOffsetX',
        'placerOffsetY',
        'placerOffsetZ',
        'positionY',
        'scale',
        'sideways',
        'size',
        'untrainedShape',
        'untrainedSize'
    ]
    PROPS = ['mass']

    def __init__(
        self,
        dimensions: Vector3d = None,
        enclosedAreas: List[Dict[str, Any]] = None,
        mass: float = 1,
        offset: Vector3d = None,
        openAreas: List[Dict[str, Any]] = None,
        placerOffsetX: List[float] = None,
        placerOffsetY: List[float] = None,
        placerOffsetZ: List[float] = None,
        positionY: float = 0,
        scale: Vector3d = None,
        sideways: Dict[str, Any] = None,
        size: str = None,
        untrainedShape: bool = None,
        untrainedSize: bool = None
    ):
        self.dimensions = dimensions
        self.enclosedAreas = enclosedAreas or []
        self.mass = mass
        self.offset = offset or Vector3d()
        self.openAreas = openAreas or []
        self.placerOffsetX = placerOffsetX
        self.placerOffsetY = placerOffsetY
        self.placerOffsetZ = placerOffsetZ
        self.positionY = positionY
        self.scale = scale or Vector3d(x=1, y=1, z=1)
        self.sideways = sideways
        self.size = size
        self.untrainedShape = untrainedShape
        self.untrainedSize = untrainedSize

    # Override
    def get_debug_props(self) -> List[str]:
        return self.DEBUG_PROPS

    # Override
    def get_props(self) -> List[str]:
        return self.PROPS


@dataclass(init=False)
class TypeChoice(_DefinitionChoice):
    materials: List[str] = None
    type: str = None

    # Debug properties.
    attributes: List[str] = None
    color: List[str] = None
    obstacle: bool = None
    occluder: bool = None
    rotation: Vector3d = None
    shape: List[str] = None
    stackTarget: bool = None
    untrainedCategory: bool = None
    untrainedColor: bool = None
    untrainedCombination: bool = None

    # Lists of specific options (choose one from each to finalize this def).
    chooseMaterialList: List[MaterialChoice] = None
    chooseSizeList: List[SizeChoice] = None

    # Debug properties set post-initialization by hypercubes or utility code.
    difference: str = None
    poly = None
    prettyName: str = None

    DEBUG_PROPS = [
        'attributes',
        'color',
        'difference',
        'obstacle',
        'occluder',
        'poly',
        'prettyName',
        'rotation',
        'shape',
        'stackTarget',
        'untrainedCategory',
        'untrainedColor',
        'untrainedCombination'
    ]
    PROPS = ['materials', 'type']

    def __init__(
        self,
        # Feel free to expose more properties here as needed in the future.
        color: List[str] = None,
        type: str = None,
        chooseMaterialList: List[MaterialChoice] = None,
        chooseSizeList: List[SizeChoice] = None
    ):
        self.color = color
        self.type = type
        self.chooseMaterialList = chooseMaterialList or []
        self.chooseSizeList = chooseSizeList or []

    # Override
    def get_debug_props(self) -> List[str]:
        return self.DEBUG_PROPS

    # Override
    def get_props(self) -> List[str]:
        return self.PROPS


@dataclass(init=False)
class ObjectDefinition(
    TypeChoice,
    SizeChoice,
    MaterialChoice
):
    chooseTypeList: List[TypeChoice] = None

    def __init__(
        self,
        attributes: List[str] = None,
        color: List[str] = None,
        difference: str = None,
        dimensions: Vector3d = None,
        enclosedAreas: List[Dict[str, Any]] = None,
        mass: float = 1,
        massMultiplier: float = 1,
        materials: List[str] = None,
        materialCategory: List[str] = None,
        notSideways: Dict[str, Any] = None,
        obstacle: bool = False,
        occluder: bool = False,
        offset: Vector3d = None,
        openAreas: List[Dict[str, Any]] = None,
        poly=None,
        placerOffsetX: List[float] = None,
        placerOffsetY: List[float] = None,
        placerOffsetZ: List[float] = None,
        positionY: float = 0,
        prettyName: str = None,
        rotation: Vector3d = None,
        salientMaterials: List[str] = None,
        scale: Vector3d = None,
        shape: List[str] = None,
        sideways: Dict[str, Any] = None,
        size: str = None,
        stackTarget: bool = False,
        type: str = None,
        untrainedCategory: bool = False,
        untrainedColor: bool = False,
        untrainedCombination: bool = False,
        untrainedShape: bool = False,
        untrainedSize: bool = False,
        chooseMaterialList: List[MaterialChoice] = None,
        chooseSizeList: List[SizeChoice] = None,
        chooseTypeList: List[TypeChoice] = None
    ):
        self.attributes = attributes or []
        self.color = color
        self.difference = difference
        self.dimensions = dimensions
        self.enclosedAreas = enclosedAreas
        self.mass = mass
        self.massMultiplier = massMultiplier or 1
        self.materials = materials
        self.materialCategory = materialCategory or []
        self.notSideways = notSideways
        self.offset = offset or Vector3d()
        self.openAreas = openAreas
        self.poly = poly
        self.placerOffsetX = placerOffsetX
        self.placerOffsetY = placerOffsetY
        self.placerOffsetZ = placerOffsetZ
        self.positionY = positionY
        self.prettyName = prettyName
        self.rotation = rotation or Vector3d()
        self.salientMaterials = salientMaterials
        self.scale = scale
        self.shape = shape or []
        self.sideways = sideways
        self.size = size
        self.type = type
        self.untrainedCategory = untrainedCategory
        self.untrainedColor = untrainedColor
        self.untrainedCombination = untrainedCombination
        self.untrainedShape = untrainedShape
        self.untrainedSize = untrainedSize

        self.obstacle = obstacle
        self.occluder = occluder
        self.stackTarget = stackTarget

        self.chooseMaterialList = chooseMaterialList or []
        self.chooseSizeList = chooseSizeList or []
        self.chooseTypeList = chooseTypeList or []

        if len(self.chooseMaterialList) == 1:
            self.assign_chosen_material(self.chooseMaterialList[0])
        if len(self.chooseSizeList) == 1:
            self.assign_chosen_size(self.chooseSizeList[0])
        if len(self.chooseTypeList) == 1:
            self.assign_chosen_type(self.chooseTypeList[0])

    # Override
    def get_debug_props(self) -> List[str]:
        return (
            MaterialChoice.DEBUG_PROPS +
            SizeChoice.DEBUG_PROPS +
            TypeChoice.DEBUG_PROPS
        )

    # Override
    def get_props(self) -> List[str]:
        return (
            MaterialChoice.PROPS +
            SizeChoice.PROPS +
            TypeChoice.PROPS
        )

    def assign_chosen_material(self, choice: MaterialChoice) -> None:
        self._assign_chosen_option(choice)
        self.chooseMaterialList = []

    def assign_chosen_size(self, choice: SizeChoice) -> None:
        self._assign_chosen_option(choice)
        self.chooseSizeList = []

    def assign_chosen_type(self, choice: TypeChoice) -> None:
        self._assign_chosen_option(choice)
        if choice.chooseMaterialList:
            self.chooseMaterialList = choice.chooseMaterialList
        if choice.chooseSizeList:
            self.chooseSizeList = choice.chooseSizeList
        self.chooseTypeList = []

    def _assign_chosen_option(self, choice: _DefinitionChoice) -> None:
        for prop in (choice.get_props() + choice.get_debug_props()):
            data = getattr(choice, prop)
            if data is not None:
                if prop == 'massMultiplier' and self.massMultiplier:
                    data *= self.massMultiplier
                # This will override the existing property, if set.
                setattr(self, prop, data)


class ChosenMaterial(Enum):
    """Convenient enum for generating all MaterialDefinition variables."""

    BLOCK_LETTER = MaterialChoice(['block_letter'], ['wood'], 2)
    BLOCK_NUMBER = MaterialChoice(['block_number'], ['wood'], 2)
    BLOCK_WOOD = MaterialChoice(['block_blank'], ['wood'], 2)
    INTUITIVE_PHYSICS_BLOCK = MaterialChoice(
        ['intuitive_physics_block'],
        ['wood'],
        5
    )
    INTUITIVE_PHYSICS_PLASTIC = MaterialChoice(
        ['intuitive_physics_plastic'],
        ['plastic'],
        5
    )
    INTUITIVE_PHYSICS_WOOD = MaterialChoice(
        ['intuitive_physics_wood'],
        ['wood'],
        5
    )
    METAL = MaterialChoice(['metal'], ['metal'], 3)
    NONE = MaterialChoice([], [])
    PLASTIC = MaterialChoice(['plastic'], ['plastic'])
    PLASTIC_HOLLOW = MaterialChoice(['plastic'], ['plastic', 'hollow'])
    RUBBER = MaterialChoice(['rubber'], ['rubber'], 1.5)
    WOOD = MaterialChoice(['wood'], ['wood'], 2)

    def copy(self, extend: int = None) -> MaterialChoice:
        choice = copy.deepcopy(self.value)
        if extend:
            choice.materialCategory = choice.materialCategory * extend
        return choice


def finalize_object_definition(
    object_definition: ObjectDefinition,
    choice_material: Optional[MaterialChoice] = None,
    choice_size: Optional[SizeChoice] = None,
    choice_type: Optional[TypeChoice] = None
) -> ObjectDefinition:
    """Finalize and return the given object definition by randomly choosing
    a material category, size, and type from the definition's corresponding
    choice lists, or using the given choice lists. Does NOT set the object
    definition's "materials" property. Not needed if the definition doesn't
    have any choice lists."""
    definition_copy = copy.deepcopy(object_definition)

    # Assign the type choice BEFORE the material and size choices.
    if not choice_type and definition_copy.chooseTypeList:
        choice_type = random.choice(definition_copy.chooseTypeList)

    if choice_type:
        definition_copy.assign_chosen_type(choice_type)

    if not choice_material and definition_copy.chooseMaterialList:
        choice_material = random.choice(definition_copy.chooseMaterialList)

    if choice_material:
        definition_copy.assign_chosen_material(choice_material)

    if not choice_size and definition_copy.chooseSizeList:
        choice_size = random.choice(definition_copy.chooseSizeList)

    if choice_size:
        definition_copy.assign_chosen_size(choice_size)

    return definition_copy


def finalize_each_definition_choice(
    object_definition: ObjectDefinition,
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> List[ObjectDefinition]:
    """Finalize each possible material category, size, and type choice in the
    given object definition (but NOT the materials property itself) and return
    the list with each possible object definition choice."""
    choice_list = []
    for data, prop in list(filter(lambda item: (item[0] and len(item[0])), [
        (object_definition.chooseMaterialList, 'chooseMaterial'),
        (object_definition.chooseSizeList, 'chooseSize'),
        (object_definition.chooseTypeList, 'chooseType')
    ])):
        previous_choice_list = copy.deepcopy(choice_list)
        next_choice_list = []
        for choice in data:
            if not previous_choice_list:
                choice_dict = {
                    'chooseMaterial': None,
                    'chooseSize': None,
                    'chooseType': None
                }
                choice_dict[prop] = choice
                next_choice_list.append(choice_dict)
            else:
                for previous_choice_dict in previous_choice_list:
                    choice_dict = copy.deepcopy(previous_choice_dict)
                    choice_dict[prop] = choice
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
    if not unshuffled:
        random.shuffle(output_list)
    return output_list


def retrieve_complete_definition_list(
    definition_groups: List[List[ObjectDefinition]],
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> List[List[List[ObjectDefinition]]]:
    """Return an object definition list in which finalize_object_definition was
    called on each definition in the given list so that the returned list has
    each possible choice (INCLUDING materials)."""
    output_list = []
    for definition_selections in definition_groups:
        output_selections = []
        for definition in definition_selections:
            intermediate_list = finalize_each_definition_choice(
                definition,
                unshuffled=unshuffled
            )
            for intermediate_definition in intermediate_list:
                output_selections.append(finalize_object_materials_and_colors(
                    intermediate_definition,
                    unshuffled=unshuffled
                ))
        if not unshuffled:
            random.shuffle(output_selections)
        output_list.append(output_selections)
    if not unshuffled:
        random.shuffle(output_list)
    return output_list


def _generate_materials_lists(
    material_category_list: List[str],
    previous_materials_lists: List[materials.MaterialTuple]
):
    if len(material_category_list) == 0:
        return previous_materials_lists

    output_materials_lists = []
    material_attr = material_category_list[0].upper() + '_MATERIALS'
    # To improve runtime performance, for objects with multiple distinct slots
    # that can be assigned different materials, we no longer return each
    # possible combination of materials, and instead assign the same material
    # to each slot. Keeping this code in case we ever want to use it again.
    # ------------------------------------------------------------------------
    # for material_and_color in getattr(materials, material_attr):
    #     if not previous_materials_lists:
    #         output_materials_lists.append([material_and_color])
    #     else:
    #         for material_list in previous_materials_lists:
    #             output_materials_lists.append(
    #                 copy.deepcopy(material_list) + [material_and_color])
    # return _generate_materials_lists(
    #     material_category_list[1:],
    #     output_materials_lists
    # )
    for material_and_color in getattr(materials, material_attr):
        output_materials_lists.append(
            [material_and_color] * len(material_category_list)
        )
    return output_materials_lists


CACHED_MATERIALS_LISTS = {}


def finalize_object_materials_and_colors(
    object_definition: ObjectDefinition,
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> List[ObjectDefinition]:
    """Finalizes each possible choice of materials (patterns/textures)
    and colors as a copy of the given object
    definition and returns the list."""

    # Cache the materials lists to improve runtime performance.
    cache_key = ','.join(object_definition.materialCategory)
    if cache_key in CACHED_MATERIALS_LISTS:
        materials_lists = CACHED_MATERIALS_LISTS[cache_key]
    else:
        materials_lists = _generate_materials_lists(
            object_definition.materialCategory,
            []
        )
        CACHED_MATERIALS_LISTS[cache_key] = materials_lists

    if not materials_lists:
        definition_copy = copy.deepcopy(object_definition)
        definition_copy.color = definition_copy.color or []
        definition_copy.materials = definition_copy.materials or []
        return [definition_copy]

    object_definition_list = []
    for materials_list in materials_lists:
        definition_copy = copy.deepcopy(object_definition)
        definition_copy.color = []
        definition_copy.materials = [
            material_and_color[0] for material_and_color in materials_list
        ]
        for material_and_color in materials_list:
            if material_and_color[0] in materials.UNTRAINED_COLOR_LIST:
                definition_copy.untrainedColor = True
            for color in material_and_color[1]:
                if color not in (definition_copy.color or []):
                    definition_copy.color = (
                        (definition_copy.color or []) + [color]
                    )
        object_definition_list.append(definition_copy)

    if not unshuffled:
        random.shuffle(object_definition_list)

    return object_definition_list


def _create_size_list(
    definition_or_instance_1: Union[ObjectDefinition, SceneObject],
    definition_or_instance_2: Union[ObjectDefinition, SceneObject],
    only_diagonal_size: bool
) -> List[Tuple[float, float]]:

    # TODO MCS-697 Use dot notation for SceneObject
    if isinstance(definition_or_instance_1, (SceneObject, dict)):
        dimensions_1 = definition_or_instance_1['debug']['dimensions']
    else:
        dimensions_1 = vars(definition_or_instance_1.dimensions)

    # TODO MCS-697 Use dot notation for SceneObject
    if isinstance(definition_or_instance_2, (SceneObject, dict)):
        dimensions_2 = definition_or_instance_2['debug']['dimensions']
    else:
        dimensions_2 = vars(definition_or_instance_2.dimensions)

    size_list = [
        (dimensions_1['x'], dimensions_2['x']),
        (dimensions_1['y'], dimensions_2['y']),
        (dimensions_1['z'], dimensions_2['z'])
    ]

    if only_diagonal_size:
        size_list = [(
            math.sqrt(dimensions_1['x']**2 + dimensions_1['z']**2),
            math.sqrt(dimensions_2['x']**2 + dimensions_2['z']**2)
        )]

    return size_list


def do_materials_match(
    materials_1: List[str],
    materials_2: List[str],
    colors_1: List[str],
    colors_2: List[str]
) -> bool:
    """Returns whether the two given material lists match, or, if either of the
    given material lists are empty, returns whether the two given color lists
    overlap."""
    if materials_1 and materials_2:
        return materials_1 == materials_2
    return len(set(colors_1).intersection(set(colors_2))) > 0


def is_similar_except_in_color(
    definition_or_instance_1: Union[ObjectDefinition, SceneObject],
    definition_or_instance_2: Union[ObjectDefinition, SceneObject],
    only_diagonal_size: bool = False
) -> bool:
    """Return whether the two given objects are similar in shape
    (type) and size (dimensions) but not color."""

    # TODO MCS-697 Use dot notation for SceneObject
    if isinstance(definition_or_instance_1, (SceneObject, dict)):
        type_1 = definition_or_instance_1['type']
        material_1 = definition_or_instance_1['materials'] or []
        color_1 = definition_or_instance_1['debug']['color'] or []
    else:
        type_1 = definition_or_instance_1.type
        material_1 = definition_or_instance_1.materials or []
        color_1 = definition_or_instance_1.color or []

    # TODO MCS-697 Use dot notation for SceneObject
    if isinstance(definition_or_instance_2, (SceneObject, dict)):
        type_2 = definition_or_instance_2['type']
        material_2 = definition_or_instance_2['materials'] or []
        color_2 = definition_or_instance_2['debug']['color'] or []
    else:
        type_2 = definition_or_instance_2.type
        material_2 = definition_or_instance_2.materials or []
        color_2 = definition_or_instance_2.color or []

    # Special cases for specific object types.
    for type_prefix in ['apple', 'crayon']:
        if type_1.startswith(type_prefix):
            type_1 = type_prefix
        if type_2.startswith(type_prefix):
            type_2 = type_prefix

    size_list = _create_size_list(
        definition_or_instance_1,
        definition_or_instance_2,
        only_diagonal_size
    )

    return (
        definition_or_instance_1 != definition_or_instance_2 and
        type_1 == type_2 and
        not do_materials_match(material_1, material_2, color_1, color_2) and
        all([(
            (size_1 + MAX_SIZE_DIFF) >= size_2 and
            (size_1 - MAX_SIZE_DIFF) <= size_2
        ) for size_1, size_2 in size_list])
    )


def is_similar_except_in_shape(
    definition_or_instance_1: Union[ObjectDefinition, SceneObject],
    definition_or_instance_2: Union[ObjectDefinition, SceneObject],
    only_diagonal_size: bool = False
) -> bool:
    """Return whether the two given objects are similar in color
    and size (dimensions) but not shape (type)."""

    # TODO MCS-697 Use dot notation for SceneObject
    if isinstance(definition_or_instance_1, (SceneObject, dict)):
        type_1 = definition_or_instance_1['type']
        material_1 = definition_or_instance_1['materials'] or []
        color_1 = definition_or_instance_1['debug']['color'] or []
    else:
        type_1 = definition_or_instance_1.type
        material_1 = definition_or_instance_1.materials or []
        color_1 = definition_or_instance_1.color or []

    # TODO MCS-697 Use dot notation for SceneObject
    if isinstance(definition_or_instance_2, (SceneObject, dict)):
        type_2 = definition_or_instance_2['type']
        material_2 = definition_or_instance_2['materials'] or []
        color_2 = definition_or_instance_2['debug']['color'] or []
    else:
        type_2 = definition_or_instance_2.type
        material_2 = definition_or_instance_2.materials or []
        color_2 = definition_or_instance_2.color or []

    # Special cases for specific object types.
    for type_prefix in ['apple', 'crayon']:
        if type_1.startswith(type_prefix):
            type_1 = type_prefix
        if type_2.startswith(type_prefix):
            type_2 = type_prefix

    size_list = _create_size_list(
        definition_or_instance_1,
        definition_or_instance_2,
        only_diagonal_size
    )

    return (
        definition_or_instance_1 != definition_or_instance_2 and
        type_1 != type_2 and
        do_materials_match(material_1, material_2, color_1, color_2) and
        all([(
            (size_1 + MAX_SIZE_DIFF) >= size_2 and
            (size_1 - MAX_SIZE_DIFF) <= size_2
        ) for size_1, size_2 in size_list])
    )


def is_similar_except_in_size(
    definition_or_instance_1: Union[ObjectDefinition, SceneObject],
    definition_or_instance_2: Union[ObjectDefinition, SceneObject],
    only_diagonal_size: bool = False
) -> bool:
    """Return whether the two given objects are similar in color
    and shape (type) but not size (dimensions)."""

    # TODO MCS-697 Use dot notation for SceneObject
    if isinstance(definition_or_instance_1, (SceneObject, dict)):
        type_1 = definition_or_instance_1['type']
        material_1 = definition_or_instance_1['materials'] or []
        color_1 = definition_or_instance_1['debug']['color'] or []
    else:
        type_1 = definition_or_instance_1.type
        material_1 = definition_or_instance_1.materials or []
        color_1 = definition_or_instance_1.color or []

    # TODO MCS-697 Use dot notation for SceneObject
    if isinstance(definition_or_instance_2, (SceneObject, dict)):
        type_2 = definition_or_instance_2['type']
        material_2 = definition_or_instance_2['materials'] or []
        color_2 = definition_or_instance_2['debug']['color'] or []
    else:
        type_2 = definition_or_instance_2.type
        material_2 = definition_or_instance_2.materials or []
        color_2 = definition_or_instance_2.color or []

    # Special cases for specific object types.
    for type_prefix in ['apple', 'crayon']:
        if type_1.startswith(type_prefix):
            type_1 = type_prefix
        if type_2.startswith(type_prefix):
            type_2 = type_prefix

    size_list = _create_size_list(
        definition_or_instance_1,
        definition_or_instance_2,
        only_diagonal_size
    )

    return (
        definition_or_instance_1 != definition_or_instance_2 and
        type_1 == type_2 and
        do_materials_match(material_1, material_2, color_1, color_2) and
        any([(
            (size_1 + MAX_SIZE_DIFF) < size_2 or
            (size_1 - MAX_SIZE_DIFF) > size_2
        ) for size_1, size_2 in size_list])
    )


def get_similar_definition(
    target_object: Union[ObjectDefinition, SceneObject],
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


_object_definition = ObjectDefinition()
_object_definition_properties = [var for var in dir(ObjectDefinition) if (
    # Ignore functions, private variables, and static (uppercase) variables.
    not callable(getattr(_object_definition, var)) and
    not var.startswith('_') and not var.isupper()
)]
# A NamedTuple with all of the ObjectDefinition properties.
ImmutableObjectDefinition = namedtuple(
    'ImmutableObjectDefinition',
    _object_definition_properties,
    defaults=(None,) * len(_object_definition_properties)
)


def create_dataset(
    definition_list: List[List[ObjectDefinition]],
    # We should only ever set unshuffled to True in a unit test.
    unshuffled: bool = False
) -> DefinitionDataset:
    """Create and return a new DefinitionDataset for the given definition
    list by retrieving all choice and material combinations for all definitions
    in the list and making them immutable."""

    complete_definition_list = retrieve_complete_definition_list(
        definition_list,
        unshuffled=unshuffled
    )

    immutable_groups = []
    for definition_selections in complete_definition_list:
        immutable_selections = []
        for definition_variations in definition_selections:
            immutable_variations = [
                # Convert the object definition to an immutable namedtuple.
                ImmutableObjectDefinition(**vars(definition))
                for definition in definition_variations
            ]
            # Convert the list to a tuple so it will be immutable.
            immutable_selections.append(tuple(immutable_variations))
        # Convert the list to a tuple so it will be immutable.
        immutable_groups.append(tuple(immutable_selections))

    # Convert the list to a tuple so it will be immutable.
    return DefinitionDataset(tuple(immutable_groups))


class DefinitionDataset():
    """Manages a collection of object definitions in a given triple-nested
    list. Can filter definitions on specific properties and choose a random
    definition from the lists."""

    def __init__(
        self,
        definition_groups: Tuple[Tuple[Tuple[ImmutableObjectDefinition]]]
    ) -> None:
        """Please call the create_dataset function to create a new
        DatasetDefinition."""
        self._definition_groups = definition_groups

    def choose_random_definition(self) -> ObjectDefinition:
        """Choose and return a random object definition from this dataset."""
        immutable_definition = random.choice(random.choice(random.choice(
            self._definition_groups
        )))
        return ObjectDefinition(**immutable_definition._asdict())

    def definitions(self, unshuffled: bool = False) -> List[ObjectDefinition]:
        """Return a list of all of the object definitions in this dataset."""
        definitions = [
            ObjectDefinition(**immutable_definition._asdict())
            for definition_selections in self._definition_groups
            for definition_variations in definition_selections
            for immutable_definition in definition_variations
        ]
        if not unshuffled:
            random.shuffle(definitions)
        return definitions

    def groups(self) -> List[ObjectDefinition]:
        """Return a deep copy of all the definition groups in this dataset."""
        return copy.deepcopy(list(self._definition_groups))

    def size(self) -> int:
        """Return the number of definitions in this dataset."""
        return len([
            definition for definition_selections in self._definition_groups
            for definition_variations in definition_selections
            for definition in definition_variations
        ])

    def filter_on_custom(
        self,
        callback: Callable[[ImmutableObjectDefinition], bool]
    ) -> DefinitionDataset:
        """Return a copy of this dataset filtered using the given callback
        function."""
        output_list = []
        for definition_selections in self._definition_groups:
            output_selections = []
            for definition_variations in definition_selections:
                output_variations = []
                for definition in definition_variations:
                    if callback(definition):
                        output_variations.append(definition)
                if len(output_variations) > 0:
                    output_selections.append(output_variations)
            if len(output_selections) > 0:
                output_list.append(output_selections)
        return DefinitionDataset(output_list)

    def filter_on_similar_except_color(
        self,
        target_definition: ObjectDefinition,
        only_diagonal_size: bool = False
    ) -> DefinitionDataset:
        """Return a copy of this dataset containing only definitions that are
        similar to the given definition except in materials/colors."""

        def _callback(definition: ImmutableObjectDefinition) -> bool:
            return is_similar_except_in_color(
                target_definition,
                definition,
                only_diagonal_size=only_diagonal_size
            )

        return self.filter_on_custom(_callback)

    def filter_on_similar_except_shape(
        self,
        target_definition: ObjectDefinition,
        only_diagonal_size: bool = False
    ) -> DefinitionDataset:
        """Return a copy of this dataset containing only definitions that are
        similar to the given definition except in type."""

        def _callback(definition: ImmutableObjectDefinition) -> bool:
            return is_similar_except_in_shape(
                target_definition,
                definition,
                only_diagonal_size=only_diagonal_size
            )

        return self.filter_on_custom(_callback)

    def filter_on_similar_except_size(
        self,
        target_definition: ObjectDefinition,
        only_diagonal_size: bool = False
    ) -> DefinitionDataset:
        """Return a copy of this dataset containing only definitions that are
        similar to the given definition except in size/dimensions."""

        def _callback(definition: ImmutableObjectDefinition) -> bool:
            return is_similar_except_in_size(
                target_definition,
                definition,
                only_diagonal_size=only_diagonal_size
            )

        return self.filter_on_custom(_callback)

    def filter_on_trained(self) -> DefinitionDataset:
        """Return a copy of this dataset containing only definitions that are
        trained."""

        def _callback(definition: ImmutableObjectDefinition) -> bool:
            props = definition._asdict()
            return not (
                (props.get(tags.SCENE.UNTRAINED_CATEGORY, False)) or
                (props.get(tags.SCENE.UNTRAINED_COLOR, False)) or
                (props.get(tags.SCENE.UNTRAINED_COMBINATION, False)) or
                (props.get(tags.SCENE.UNTRAINED_SHAPE, False)) or
                (props.get(tags.SCENE.UNTRAINED_SIZE, False))
            )

        return self.filter_on_custom(_callback)

    def filter_on_type(
        self,
        must_be: List[str] = None,
        cannot_be: List[str] = None
    ) -> DefinitionDataset:
        """Return a copy of this dataset containing only definitions that
        either are or are not the given type(s)."""

        def _callback(definition: ImmutableObjectDefinition) -> bool:
            if cannot_be:
                return definition.type not in cannot_be
            if must_be:
                return definition.type in must_be
            return True

        return self.filter_on_custom(_callback)

    def filter_on_untrained(
        self,
        untrained_tag: str
    ) -> DefinitionDataset:
        """Return a copy of this dataset containing only definitions that are
        untrained using the given tag."""

        trained_tag_list = [tag for tag in [
            tags.SCENE.UNTRAINED_CATEGORY,
            tags.SCENE.UNTRAINED_COLOR,
            tags.SCENE.UNTRAINED_COMBINATION,
            tags.SCENE.UNTRAINED_SHAPE,
            tags.SCENE.UNTRAINED_SIZE
        ] if tag != untrained_tag]

        def _callback(definition: ImmutableObjectDefinition) -> bool:
            props = definition._asdict()
            if props.get(untrained_tag, False):
                # Return False if any other tag is marked untrained (True)
                return not any(
                    [props.get(tag, False) for tag in trained_tag_list]
                )
            return False

        return self.filter_on_custom(_callback)

    def dataset_unique_shape_scale(self, keep: int = 1) -> DefinitionDataset:
        """Function for unit tests: Return a new dataset containing all of the
        definitions in this dataset, but only keep one (or the given number)
        definition with the same shape and scale combination (ignore color)."""
        unique = {}
        groups = []
        for definition_selections in self._definition_groups:
            selections = []
            for definition_variations in definition_selections:
                variations = []
                for definition in definition_variations[:keep]:
                    if definition.type not in unique:
                        unique[definition.type] = {}
                    scale_str = str(definition.scale)
                    if scale_str not in unique[definition.type]:
                        unique[definition.type][scale_str] = 0
                    if unique[definition.type][scale_str] < keep:
                        unique[definition.type][scale_str] += 1
                        variations.append(definition)
                if variations:
                    selections.append(variations)
            if selections:
                groups.append(selections)
        return DefinitionDataset(groups)

    def definitions_unique_shape_scale(self) -> List[ObjectDefinition]:
        """Function for unit tests: Return a list of all of the object
        definitions in this dataset, but only keep one definition with the same
        shape and scale combination (ignore color)."""
        unique = {}
        output = []
        for definition_selections in self._definition_groups:
            for definition_variations in definition_selections:
                for definition in definition_variations[:1]:
                    if definition.type not in unique:
                        unique[definition.type] = {}
                    scale_str = str(definition.scale)
                    if scale_str not in unique[definition.type]:
                        unique[definition.type][scale_str] = 0
                    if unique[definition.type][scale_str] < 1:
                        unique[definition.type][scale_str] += 1
                        output.append(ObjectDefinition(**definition._asdict()))
        return output


DATASETS: Dict[str, DefinitionDataset] = {}
DATASETS_UNSHUFFLED: Dict[str, DefinitionDataset] = {}


def get_dataset(
    definition_list: List[List[ObjectDefinition]],
    prop: str,
    unshuffled: bool = False
) -> DefinitionDataset:
    """Return a new DefinitionDataset using the given definition list, or the
    existing dataset for the given property if it's already made."""
    datasets = DATASETS_UNSHUFFLED if unshuffled else DATASETS
    if not datasets.get(prop):
        datasets[prop] = create_dataset(definition_list, unshuffled=unshuffled)
    return datasets[prop]
