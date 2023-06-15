import copy
import math
import uuid
from dataclasses import dataclass
from enum import Enum, auto
from random import choice, randint, uniform
from typing import Dict, List, NamedTuple, Tuple

from machine_common_sense.config_manager import Vector3d

from generator.exceptions import SceneException

from . import materials
from .geometry import create_bounds
from .objects import SceneObject

# Agents were scaled down to 0.6 from their original size.  However, lets
# retain the original bounding box size though and just apply that scale.
AGENT_SCALE = 0.6
AGENT_DIMENSIONS = {'x': 0.5 * AGENT_SCALE,
                    'y': 1.6 * AGENT_SCALE,
                    'z': 0.5 * AGENT_SCALE}

# TODO MCS-1591 Update novel agent types
NOVEL_AGENTS_FEMALE = ['agent_female_05', 'agent_female_06']
NOVEL_AGENTS_MALE = ['agent_male_07', 'agent_male_08']
NOVEL_AGENTS = NOVEL_AGENTS_FEMALE + NOVEL_AGENTS_MALE
FAMILIAR_AGENTS_FEMALE = [
    'agent_female_01',
    'agent_female_02',
    'agent_female_03',
    'agent_female_04'
]
FAMILIAR_AGENTS_MALE = [
    'agent_male_01',
    'agent_male_02',
    'agent_male_03',
    'agent_male_04'
]
FAMILIAR_AGENTS = FAMILIAR_AGENTS_FEMALE + FAMILIAR_AGENTS_MALE
AGENT_TYPES = FAMILIAR_AGENTS + NOVEL_AGENTS

AGENT_MOVEMENT_ANIMATIONS = ['TPM_walk', 'TPM_run', 'TPF_walk', 'TPF_run']

AGENT_TEMPLATE = {
    'id': 'agent_',
    'type': '',
    'debug': {
        'color': [],
        'info': [],
        'offset': {'x': 0, 'y': 0, 'z': 0},
        'positionY': 0
    },
    'mass': 75,
    'agentSettings': {},
    'actions': [],
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}

# Should equal MOVE_MAGNITUDE in MCSSimulationAgent.cs
MOVE_DISTANCE = 0.04

POINT_START_FRAME_COUNT = 7


@dataclass
class BlobInfo():
    dimensions: Vector3d
    standing_y: float = None

    def __post_init__(self):
        if self.standing_y is None:
            self.standing_y = self.dimensions.y / 2.0


BLOB_SHAPES = {
    'blob_01': BlobInfo(Vector3d(x=0.26, y=0.8, z=0.36)),
    'blob_02': BlobInfo(Vector3d(x=0.33, y=0.78, z=0.33)),
    'blob_03': BlobInfo(Vector3d(x=0.25, y=0.69, z=0.25)),
    'blob_04': BlobInfo(Vector3d(x=0.3, y=0.53, z=0.3), standing_y=0.225),
    'blob_05': BlobInfo(Vector3d(x=0.38, y=0.56, z=0.38), standing_y=0.24),
    'blob_06': BlobInfo(Vector3d(x=0.52, y=0.5, z=0.54)),
    'blob_07': BlobInfo(Vector3d(x=0.25, y=0.55, z=0.25), standing_y=0.245),
    'blob_08': BlobInfo(Vector3d(x=0.27, y=0.62, z=0.15)),
    'blob_09': BlobInfo(Vector3d(x=0.33, y=0.78, z=0.44)),
    'blob_10': BlobInfo(Vector3d(x=0.24, y=0.5, z=0.2))
}

BLOB_TEMPLATE = {
    'id': 'blob_',
    'type': '',
    'debug': {
        'color': [],
        'info': [],
        'offset': {'x': 0, 'y': 0, 'z': 0}
    },
    'mass': 75,
    'materials': [],
    'physics': True,
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}

MIN_BLOB_HEIGHT = AGENT_DIMENSIONS['y'] * 0.75
MAX_BLOB_HEIGHT = AGENT_DIMENSIONS['y'] * 1.25


class AgentGroup(Enum):
    FEMALE_ADULT = auto()
    FEMALE_TEEN = auto()
    MALE_ADULT = auto()
    MALE_TEEN = auto()


def get_agent_group(agent_type: str) -> AgentGroup:
    if agent_type in [
        'agent_male_01', 'agent_male_02', 'agent_male_03', 'agent_male_04'
    ]:
        return AgentGroup.MALE_ADULT
    if agent_type in [
        'agent_male_05', 'agent_male_06', 'agent_male_07', 'agent_male_08'
    ]:
        return AgentGroup.MALE_TEEN
    if agent_type in [
        'agent_female_01', 'agent_female_02', 'agent_female_03',
        'agent_female_04'
    ]:
        return AgentGroup.FEMALE_ADULT
    if agent_type in [
        'agent_female_05', 'agent_female_06', 'agent_female_07',
        'agent_female_08'
    ]:
        return AgentGroup.FEMALE_TEEN
    raise Exception(f'agent type not recognized: {agent_type}')


class Clothing(NamedTuple):
    with_dark_skin: bool
    with_light_skin: bool
    color: List[str]


# Note whether to use specific clothing materials with dark skin and/or light
# skin tone agents (chosen arbitrarily based on looking at the clothing).
FEMALE_ADULT_DRESSES = {
    0: Clothing(True, False, ['yellow']),
    1: Clothing(True, True, ['red']),
    2: Clothing(False, False, ['black', 'white']),
    3: Clothing(False, True, ['black', 'white']),
    4: Clothing(False, True, ['red', 'black']),
    5: Clothing(False, False, ['black', 'yellow']),
    6: Clothing(True, False, ['white', 'orange']),
    7: Clothing(False, True, ['black']),
    8: Clothing(False, False, ['brown']),
    9: Clothing(False, True, ['red', 'black']),
    10: Clothing(False, True, ['blue']),
    11: Clothing(True, False, ['white']),
    12: Clothing(True, True, ['blue']),
    13: Clothing(True, True, ['green'])
}
FEMALE_ADULT_CASUAL_BUTTON_DOWN_SHIRTS = {
    0: Clothing(False, False, ['orange']),
    1: Clothing(True, True, ['blue', 'white']),
    2: Clothing(False, False, ['red']),
    3: Clothing(True, False, ['red']),
    4: Clothing(True, True, ['red']),
    5: Clothing(True, False, ['white']),
    6: Clothing(False, False, ['black', 'brown']),
    7: Clothing(True, False, ['white']),
    8: Clothing(True, True, ['green']),
    9: Clothing(True, False, ['green', 'white', 'yellow']),
    10: Clothing(False, True, ['blue']),
    11: Clothing(False, True, ['green'])
}
FEMALE_ADULT_FORMAL_BUTTON_DOWN_SHIRTS = {
    0: Clothing(True, True, ['purple']),
    1: Clothing(False, False, ['black', 'white']),
    2: Clothing(True, True, ['blue']),
    3: Clothing(False, False, ['blue']),
    4: Clothing(True, False, ['white']),
    5: Clothing(False, True, ['black']),
    6: Clothing(True, False, ['grey']),
    7: Clothing(True, False, ['green']),
    8: Clothing(True, False, ['yellow']),
    9: Clothing(False, True, ['grey']),
    10: Clothing(True, True, ['red'])
}
FEMALE_ADULT_NO_BUTTON_SHIRTS = {
    0: Clothing(True, False, ['yellow']),
    1: Clothing(False, True, ['red']),
    2: Clothing(False, True, ['black']),
    3: Clothing(True, False, ['yellow', 'blue']),
    4: Clothing(False, True, ['purple', 'black']),
    5: Clothing(True, True, ['green']),
    6: Clothing(False, True, ['blue', 'red']),
    7: Clothing(False, True, ['blue', 'black']),
    8: Clothing(True, False, ['yellow', 'pink', 'purple', 'blue']),
    9: Clothing(False, False, ['black', 'white']),
    10: Clothing(True, False, ['white']),
    11: Clothing(True, True, ['blue']),
    12: Clothing(True, False, ['orange']),
    13: Clothing(True, True, ['blue', 'green']),
    14: Clothing(True, True, ['blue'])
}
FEMALE_ADULT_TOPS = {
    # Dress
    0: FEMALE_ADULT_DRESSES,
    # Tank-top
    1: FEMALE_ADULT_DRESSES,
    # Long-sleeve formal button-down
    2: FEMALE_ADULT_FORMAL_BUTTON_DOWN_SHIRTS,
    # Short-sleeve formal button-down
    3: FEMALE_ADULT_FORMAL_BUTTON_DOWN_SHIRTS,
    # Long-sleeve casual button-down
    4: FEMALE_ADULT_CASUAL_BUTTON_DOWN_SHIRTS,
    # Short-sleeve casual button-down
    5: FEMALE_ADULT_CASUAL_BUTTON_DOWN_SHIRTS,
    # High-neck long-sleeve no-button
    6: FEMALE_ADULT_NO_BUTTON_SHIRTS,
    # Long-sleeve no-button
    7: FEMALE_ADULT_NO_BUTTON_SHIRTS,
    # Short-sleeve no-button t-shirt
    8: FEMALE_ADULT_NO_BUTTON_SHIRTS
}
MALE_ADULT_CASUAL_BUTTON_DOWN_SHIRTS = {
    0: Clothing(False, True, ['grey']),
    1: Clothing(False, True, ['blue', 'red']),
    2: Clothing(True, False, ['blue', 'white']),
    3: Clothing(True, False, ['red', 'white']),
    4: Clothing(True, True, ['red']),
    5: Clothing(False, True, ['grey']),
    6: Clothing(False, True, ['red', 'black']),
    7: Clothing(False, True, ['green', 'black']),
    8: Clothing(True, False, ['green', 'yellow']),
    9: Clothing(False, True, ['blue', 'white']),
    10: Clothing(True, False, ['white'])
}
MALE_ADULT_FORMAL_BUTTON_DOWN_SHIRTS = {
    0: Clothing(True, False, ['yellow']),
    1: Clothing(True, False, ['white']),
    2: Clothing(False, True, ['black']),
    3: Clothing(True, False, ['white', 'blue']),
    4: Clothing(False, False, ['white', 'black']),
    5: Clothing(False, False, ['white', 'black']),
    6: Clothing(False, False, ['grey']),
    7: Clothing(True, True, ['blue']),
    8: Clothing(True, True, ['purple']),
    9: Clothing(False, False, ['brown'])
}
MALE_ADULT_NO_BUTTON_SHIRTS = {
    0: Clothing(True, True, ['red']),
    1: Clothing(True, True, ['green']),
    2: Clothing(False, True, ['black']),
    3: Clothing(False, True, ['blue']),
    4: Clothing(True, True, ['red', 'blue']),
    5: Clothing(True, False, ['green', 'blue', 'orange']),
    6: Clothing(False, False, ['black', 'white']),
    7: Clothing(True, False, ['green']),
    8: Clothing(True, False, ['yellow', 'pink', 'purple', 'blue']),
    9: Clothing(False, False, ['yellow', 'black']),
    10: Clothing(True, False, ['white']),
    11: Clothing(False, True, ['green', 'black']),
    12: Clothing(True, False, ['white']),
    13: Clothing(True, True, ['purple'])
}
MALE_ADULT_TOPS = {
    # Long-sleeve formal button-down
    0: MALE_ADULT_FORMAL_BUTTON_DOWN_SHIRTS,
    # Short-sleeve formal button-down
    1: MALE_ADULT_FORMAL_BUTTON_DOWN_SHIRTS,
    # Long-sleeve casual button-down
    2: MALE_ADULT_CASUAL_BUTTON_DOWN_SHIRTS,
    # Short-sleeve casual button-down
    3: MALE_ADULT_CASUAL_BUTTON_DOWN_SHIRTS,
    # High-neck long-sleeve no-button
    4: MALE_ADULT_NO_BUTTON_SHIRTS,
    # Long-sleeve no-button
    5: MALE_ADULT_NO_BUTTON_SHIRTS,
    # Short-sleeve no-button t-shirt
    6: MALE_ADULT_NO_BUTTON_SHIRTS
}
FEMALE_TEEN_SHIRTS = {
    0: Clothing(True, False, ['yellow']),
    1: Clothing(False, True, ['black', 'white']),
    2: Clothing(True, False, ['white', 'yellow', 'red', 'blue']),
    3: Clothing(False, True, ['black', 'white', 'red']),
    4: Clothing(True, True, ['blue', 'white']),
    5: Clothing(True, True, ['purple', 'pink']),
    6: Clothing(True, False, ['white', 'grey']),
    7: Clothing(True, True, ['blue', 'green']),
    8: Clothing(True, True, ['red']),
    9: Clothing(True, True, ['blue', 'green']),
    10: Clothing(True, True, ['green']),
    11: Clothing(True, True, ['green', 'white']),
    12: Clothing(True, True, ['red', 'white']),
    13: Clothing(True, True, ['blue', 'red', 'white']),
    14: Clothing(True, False, ['yellow', 'black']),
    15: Clothing(True, True, ['green', 'yellow'])
}
MALE_TEEN_SHIRTS = {
    0: Clothing(True, True, ['red']),
    1: Clothing(True, True, ['red', 'blue']),
    2: Clothing(False, True, ['black']),
    3: Clothing(True, False, ['yellow']),
    4: Clothing(True, False, ['white', 'grey']),
    5: Clothing(True, True, ['green', 'black', 'white']),
    6: Clothing(False, False, ['grey']),
    7: Clothing(False, False, ['black', 'blue', 'green']),
    8: Clothing(True, True, ['purple']),
    9: Clothing(True, True, ['blue', 'white']),
    10: Clothing(False, True, ['black', 'green']),
    11: Clothing(True, False, ['orange', 'black']),
    12: Clothing(True, True, ['red', 'white']),
    13: Clothing(True, True, ['blue', 'red', 'white']),
    14: Clothing(True, False, ['yellow', 'black']),
    15: Clothing(True, True, ['green', 'yellow'])
}
TEEN_SWEATERS = {
    0: Clothing(True, False, ['white', 'grey']),
    1: Clothing(False, True, ['black']),
    2: Clothing(False, True, ['black', 'grey']),
    3: Clothing(True, True, ['purple']),
    4: Clothing(True, False, ['orange', 'black', 'white']),
    5: Clothing(True, True, ['blue', 'white']),
    6: Clothing(False, True, ['black', 'blue', 'white']),
    7: Clothing(True, False, ['yellow']),
    8: Clothing(True, True, ['red', 'white']),
    9: Clothing(True, True, ['green']),
    10: Clothing(True, True, ['blue', 'green']),
    11: Clothing(True, True, ['purple', 'pink'])
}
FEMALE_TEEN_TOPS = {
    0: FEMALE_TEEN_SHIRTS,
    1: FEMALE_TEEN_SHIRTS,
    2: FEMALE_TEEN_SHIRTS,
    3: TEEN_SWEATERS,
    4: FEMALE_TEEN_SHIRTS,
    5: FEMALE_TEEN_SHIRTS,
    6: FEMALE_TEEN_SHIRTS,
    7: FEMALE_TEEN_SHIRTS,
    8: FEMALE_TEEN_SHIRTS,
    9: FEMALE_TEEN_SHIRTS,
    10: FEMALE_TEEN_SHIRTS
}
MALE_TEEN_TOPS = {
    0: TEEN_SWEATERS,
    1: MALE_TEEN_SHIRTS,
    2: MALE_TEEN_SHIRTS,
    3: MALE_TEEN_SHIRTS,
    4: MALE_TEEN_SHIRTS,
    5: MALE_TEEN_SHIRTS,
    6: MALE_TEEN_SHIRTS,
    7: MALE_TEEN_SHIRTS
}


def _filter_chest_materials(
    data: Dict[int, Dict[int, Clothing]],
    dark: bool
) -> Dict[int, List[int]]:
    return dict([(chest_index, [
        index for index, clothing in chest_materials.items() if
        getattr(clothing, 'with_dark_skin' if dark else 'with_light_skin')
    ]) for chest_index, chest_materials in data.items()])


# High-contrast chest materials for light or dark skin agents.
MALE_ADULT_DARK_SKIN_TOPS = _filter_chest_materials(MALE_ADULT_TOPS, True)
MALE_ADULT_LIGHT_SKIN_TOPS = _filter_chest_materials(MALE_ADULT_TOPS, False)
FEMALE_ADULT_DARK_SKIN_TOPS = _filter_chest_materials(FEMALE_ADULT_TOPS, True)
FEMALE_ADULT_LIGHT_SKIN_TOPS = _filter_chest_materials(
    FEMALE_ADULT_TOPS,
    False
)
MALE_TEEN_DARK_SKIN_TOPS = _filter_chest_materials(MALE_TEEN_TOPS, True)
MALE_TEEN_LIGHT_SKIN_TOPS = _filter_chest_materials(MALE_TEEN_TOPS, False)
FEMALE_TEEN_DARK_SKIN_TOPS = _filter_chest_materials(FEMALE_TEEN_TOPS, True)
FEMALE_TEEN_LIGHT_SKIN_TOPS = _filter_chest_materials(FEMALE_TEEN_TOPS, False)


class SkinTone(Enum):
    LIGHTEST = -3
    LIGHT = -2
    MEDIUM_LIGHT = -1
    MEDIUM_DARK = 1
    DARK = 2
    DARKEST = 3


def get_skin_tone(agent_type: str, skin: int) -> SkinTone:
    """Returns the SkinTone for the agent with the given type and skin
    index."""
    # The adult female models have skin material options with makeup.
    female_adult = (get_agent_group(agent_type) == AgentGroup.FEMALE_ADULT)
    # Lightest tone
    if (not female_adult and skin == 4) or (female_adult and skin == 12):
        return SkinTone.LIGHTEST
    # Light tone
    if (not female_adult and skin == 5) or (female_adult and skin == 13):
        return SkinTone.LIGHT
    # Medium-light tone
    if (
        (not female_adult and skin == 0) or
        (female_adult and skin in [0, 4, 8])
    ):
        return SkinTone.MEDIUM_LIGHT
    # Medium-dark tone
    if (
        (not female_adult and skin == 2) or
        (female_adult and skin in [2, 6, 10])
    ):
        return SkinTone.MEDIUM_DARK
    # Dark tone
    if (
        (not female_adult and skin == 3) or
        (female_adult and skin in [3, 7, 11])
    ):
        return SkinTone.DARK
    # Darkest tone
    if (
        (not female_adult and skin == 1) or
        (female_adult and skin in [1, 5, 9])
    ):
        return SkinTone.DARKEST


def get_agent(scene):
    for obj in scene.objects:
        if 'agent' in obj['type']:
            return obj


def get_random_agent_settings(
    agent_type: str,
    short_sleeves_only: bool = False,
    high_contrast_only: bool = False,
    settings: Dict[str, int] = None
) -> Dict[str, int]:
    """Returns random settings for the agent with the given type. Only chooses
    short-sleeved shirts and dresses if short_sleeves_only is True. Only
    chooses shirt and dress materials with high contract compared to skin tone
    if high_contrast_only is True. Will attempt to properly use the given
    settings, but will not override illegal values or combinations."""
    output = (settings or {}).copy()
    group = get_agent_group(agent_type)
    if output.get('chest') is None:
        if group == AgentGroup.FEMALE_ADULT:
            output['chest'] = choice(
                [0, 1, 3, 5, 8] if short_sleeves_only else list(range(0, 9))
            )
        if group == AgentGroup.MALE_ADULT:
            output['chest'] = choice(
                [1, 3, 6] if short_sleeves_only else list(range(0, 7))
            )
        if group == AgentGroup.FEMALE_TEEN:
            output['chest'] = choice(
                [0, 1, 4, 5, 7, 8, 9] if short_sleeves_only else
                list(range(0, 11))
            )
        if group == AgentGroup.MALE_TEEN:
            output['chest'] = choice(
                [1, 4, 5, 7] if short_sleeves_only else list(range(0, 8))
            )
    if output.get('skin') is None:
        if group == AgentGroup.FEMALE_ADULT:
            output['skin'] = choice([0, 1, 2, 3, 12, 13])
        else:
            output['skin'] = randint(0, 5)
    dark = get_skin_tone(agent_type, output['skin']).value > 0
    if output.get('chestMaterial') is None:
        if high_contrast_only:
            if group == AgentGroup.FEMALE_ADULT:
                output['chestMaterial'] = choice((
                    FEMALE_ADULT_DARK_SKIN_TOPS if dark else
                    FEMALE_ADULT_LIGHT_SKIN_TOPS
                )[output['chest']])
            if group == AgentGroup.MALE_ADULT:
                output['chestMaterial'] = choice((
                    MALE_ADULT_DARK_SKIN_TOPS if dark else
                    MALE_ADULT_LIGHT_SKIN_TOPS
                )[output['chest']])
        else:
            if group == AgentGroup.FEMALE_ADULT:
                chest_material_max = 14
                if output['chest'] in [0, 1]:
                    chest_material_max = 13
                if output['chest'] in [2, 3]:
                    chest_material_max = 10
                if output['chest'] in [4, 5]:
                    chest_material_max = 11
            if group == AgentGroup.MALE_ADULT:
                chest_material_max = 11
                if output['chest'] in [0, 1]:
                    chest_material_max = 9
                if output['chest'] in [2, 3]:
                    chest_material_max = 10
            if group in [AgentGroup.FEMALE_TEEN, AgentGroup.MALE_TEEN]:
                chest_material_max = 15
                if (
                    group == AgentGroup.FEMALE_TEEN and output['chest'] == 3 or
                    group == AgentGroup.MALE_TEEN and output['chest'] == 0
                ):
                    chest_material_max = 11
            output['chestMaterial'] = randint(0, chest_material_max)
    if output.get('eyes') is None:
        output['eyes'] = randint(0, 3)
    if output.get('feet') is None:
        if group == AgentGroup.FEMALE_ADULT:
            output['feet'] = randint(0, 1)
        if group == AgentGroup.MALE_ADULT:
            output['feet'] = randint(0, 2)
        if group in [AgentGroup.FEMALE_TEEN, AgentGroup.MALE_TEEN]:
            output['feet'] = randint(0, 3)
    if output.get('feetMaterial') is None:
        feet_material_max = 11
        if group in [AgentGroup.FEMALE_ADULT, AgentGroup.MALE_ADULT]:
            if output['feet'] == 1:
                feet_material_max = 9
            if output['feet'] == 2:
                feet_material_max = 10
        output['feetMaterial'] = randint(0, feet_material_max)
    if output.get('hair') is None:
        if group in [AgentGroup.FEMALE_ADULT, AgentGroup.MALE_ADULT]:
            output['hair'] = randint(0, 9)
        if group in [AgentGroup.FEMALE_TEEN, AgentGroup.MALE_TEEN]:
            # TODO MCS-1724 Replace
            # output['hair'] = randint(0, 6)
            output['hair'] = randint(
                0,
                5 if group == AgentGroup.MALE_TEEN else 6
            )
    if output.get('hairMaterial') is None:
        if group in [AgentGroup.FEMALE_ADULT, AgentGroup.MALE_ADULT]:
            output['hairMaterial'] = (
                0 if output['hair'] == 5 else randint(0, 3)
            )
        if group == AgentGroup.FEMALE_TEEN:
            output['hairMaterial'] = randint(0, 4)
        if group == AgentGroup.MALE_TEEN:
            hair_material_max = 3 if output['hair'] in [3, 5] else 4
            output['hairMaterial'] = randint(0, hair_material_max)
    if output.get('hatMaterial') is None:
        if group in [AgentGroup.FEMALE_ADULT, AgentGroup.MALE_ADULT]:
            output['hatMaterial'] = (
                randint(0, 5 if output['hair'] == 9 else 11)
                if output['hair'] >= 7 else -1
            )
        if group in [AgentGroup.FEMALE_TEEN, AgentGroup.MALE_TEEN]:
            output['hatMaterial'] = (
                randint(0, 11) if output['hair'] >= 5 else -1
            )
    if output.get('hideHair') is None:
        output['hideHair'] = choice([False] * 4 + [True])
    if output.get('isElder') is None:
        if group in [AgentGroup.FEMALE_ADULT, AgentGroup.MALE_ADULT]:
            output['isElder'] = choice([False] * 4 + [True])
        if group in [AgentGroup.FEMALE_TEEN, AgentGroup.MALE_TEEN]:
            output['isElder'] = False
    if output.get('legs') is None:
        if group == AgentGroup.FEMALE_ADULT:
            output['legs'] = randint(0, 3)
        if group == AgentGroup.MALE_ADULT:
            output['legs'] = randint(0, 1)
        if group == AgentGroup.FEMALE_TEEN:
            output['legs'] = randint(0, 9)
        if group == AgentGroup.MALE_TEEN:
            output['legs'] = randint(0, 6)
    if output.get('legsMaterial') is None:
        if group in [AgentGroup.FEMALE_ADULT, AgentGroup.MALE_ADULT]:
            output['legsMaterial'] = randint(
                0,
                13 if output['legs'] == 3 else 14
            )
        if group in [AgentGroup.FEMALE_TEEN, AgentGroup.MALE_TEEN]:
            output['legsMaterial'] = randint(0, 23)
    # Do not use the following properites unless configured.
    for prop in ['glasses', 'jacket', 'jacketMaterial', 'tie', 'tieMaterial']:
        if output.get(prop) is None:
            output[prop] = 0
    for prop in ['showBeard', 'showGlasses', 'showJacket', 'showTie']:
        if output.get(prop) is None:
            output[prop] = False
    return output


def create_agent(
    type: str,
    position_x: float,
    position_z: float,
    rotation_y: float,
    settings: dict = None,
    position_y_modifier: float = 0
) -> SceneObject:
    """Create and return an instance of an agent without any actions."""
    agent = SceneObject(copy.deepcopy(AGENT_TEMPLATE))
    agent['id'] += str(uuid.uuid4())

    agent['type'] = type
    agent['shows'][0]['position'] = {
        'x': position_x,
        'y': position_y_modifier + agent['debug']['positionY'],
        'z': position_z
    }
    agent['shows'][0]['rotation'] = {
        'x': 0,
        'y': rotation_y,
        'z': 0
    }
    agent['shows'][0]['scale'] = {'x': 1, 'y': 1, 'z': 1}
    agent['agentSettings'] = settings
    agent['shows'][0]['boundingBox'] = create_bounds(
        dimensions=AGENT_DIMENSIONS,
        offset={'x': 0, 'y': 0, 'z': 0},
        position=agent['shows'][0]['position'],
        rotation=agent['shows'][0]['rotation'],
        standing_y=0
    )
    agent['debug']['dimensions'] = copy.deepcopy(AGENT_DIMENSIONS)
    if type in NOVEL_AGENTS:
        agent['debug']['untrainedShape'] = True
    return agent


def create_blob(
    type: str,
    position_x: float,
    position_z: float,
    rotation_y: float,
    material_tuple: materials.MaterialTuple,
    height: float = None,
    position_y_modifier: float = 0,
    with_nose: bool = False
) -> SceneObject:
    """Create and return an instance of a blob. By default, it will be
    approximately as tall as a normal agent."""
    blob = SceneObject(copy.deepcopy(BLOB_TEMPLATE))
    blob['id'] += str(uuid.uuid4())
    blob['type'] = type + ('_nose' if with_nose else '')
    blob['shows'][0]['rotation'] = {
        'x': 0,
        'y': rotation_y,
        'z': 0
    }

    base_dimensions = BLOB_SHAPES[type].dimensions
    blob_height = height or uniform(MIN_BLOB_HEIGHT, MAX_BLOB_HEIGHT)
    scale = round(blob_height / base_dimensions.y, 4)
    blob['shows'][0]['scale'] = {'x': scale, 'y': scale, 'z': scale}
    blob['debug']['dimensions'] = {
        'x': round(base_dimensions.x * scale, 4),
        'y': round(base_dimensions.y * scale, 4),
        'z': round(base_dimensions.z * scale, 4)
    }

    standing_y = round(BLOB_SHAPES[type].standing_y * scale, 4)
    blob['shows'][0]['position'] = {
        'x': position_x,
        'y': standing_y + position_y_modifier,
        'z': position_z
    }
    blob['debug']['positionY'] = standing_y

    blob['materials'] = [material_tuple.material]
    blob['debug']['color'] = material_tuple.color

    blob['shows'][0]['boundingBox'] = create_bounds(
        dimensions=blob['debug']['dimensions'],
        offset={'x': 0, 'y': 0, 'z': 0},
        position=blob['shows'][0]['position'],
        rotation=blob['shows'][0]['rotation'],
        standing_y=standing_y
    )

    return blob


def _check_steps(
    actions: list,
    step_begin: int,
    step_end: int,
    is_loop: bool
) -> None:
    if step_begin is None or step_begin < 0 or (
        (not isinstance(step_begin, int)) and (not step_begin.is_integer())
    ):
        raise SceneException(
            f"The step_begin must be an integer greater than or equal to 0, "
            f"but was: {step_begin}"
        )

    for action in actions:
        if 'stepEnd' not in action:
            if action['stepBegin'] == step_begin:
                raise SceneException(
                    f"Cannot add a new agent action when an action that does "
                    f"not end already exists with the same step_begin: "
                    f"{step_begin}"
                )
            continue
        if action['stepBegin'] <= step_begin < action['stepEnd']:
            raise SceneException(
                f"Cannot add a new agent action when an action already "
                f"exists during that step: {action['stepBegin']} <= "
                f"{step_begin=} < {action['stepEnd']}"
            )
        if step_end and (action['stepBegin'] <= step_end < action['stepEnd']):
            raise SceneException(
                f"Cannot add a new agent action when an action already "
                f"exists during that step: {action['stepBegin']} <= "
                f"{step_end=} < {action['stepEnd']}"
            )
        if is_loop and (
            step_begin < action['stepBegin'] or step_begin < action['stepEnd']
        ):
            raise SceneException(
                f"Cannot add a new agent action that does not end when an "
                f"action already exists after that step: {step_begin=} < "
                f"({action['stepBegin']} ==> {action['stepEnd']})"
            )


def add_agent_action(agent: SceneObject, action_id, step_begin,
                     step_end=None, is_loop=False):
    actions = agent.get('actions', [])
    _check_steps(actions, step_begin, step_end, is_loop)

    if action_id is None or not isinstance(action_id, str):
        raise SceneException(
            f"The action_id must be a string, but was: {action_id}"
        )

    new_action = {
        'id': action_id,
        'stepBegin': step_begin,
        'isLoopAnimation': is_loop
    }
    if step_end:
        new_action['stepEnd'] = step_end
    actions.append(new_action)
    agent['actions'] = sorted(actions, key=lambda x: x['stepBegin'])


def add_agent_movement(
        agent: SceneObject, step_begin: int, points: List[Tuple[float, float]],
        animation: str = "TPM_walk", repeat=False):
    sequence = [{
        "animation": animation,
        "endPoint": {
            "x": point[0],
            "z": point[1]
        }
    } for point in points]
    agent["agentMovement"] = {
        "repeat": repeat,
        "stepBegin": step_begin,
        "sequence": sequence
    }


def add_agent_pointing(agent: SceneObject, step_begin: int) -> None:
    """Adds a pointing animation (the agent points in whatever direction it's
    facing) that begins at the given step and is held indefinitely."""

    actions = agent.get('actions', [])
    _check_steps(actions, step_begin, None, True)

    actions.extend([{
        'id': 'Point_start_index_finger',
        'stepBegin': step_begin,
        'stepEnd': step_begin + POINT_START_FRAME_COUNT
    }, {
        'id': 'Point_hold_index_finger',
        'stepBegin': step_begin + POINT_START_FRAME_COUNT,
        'isLoopAnimation': True
    }])

    agent['actions'] = sorted(actions, key=lambda x: x['stepBegin'])


def estimate_move_step_length(begin: dict, end: dict) -> int:
    """Estimates and returns the number of action steps the agent will take to
    move from the given begin point to the given end point."""
    distance = math.dist([begin['x'], begin['z']], [end['x'], end['z']])
    # Add 6 steps for the rotation
    return math.ceil((distance / MOVE_DISTANCE) + 6)


AGENT_ANIMATIONS = [
    'amazed',
    'angry',
    'disgust',
    'happy',
    'sad',
    'TPE_clap',
    'TPE_cry',
    'TPE_freefall',
    'TPE_freeze',
    'TPE_hitbackwards',
    'TPE_hitforward',
    'TPE_idle1',
    'TPE_idle2',
    'TPE_idle3',
    'TPE_idle4',
    'TPE_idle5',
    'TPE_idleafraid',
    'TPE_idleangry',
    'TPE_idlehappy',
    'TPE_idlesad',
    'TPE_jump',
    'TPE_land',
    'TPE_laugh',
    'TPE_lookback',
    'TPE_phone1',
    'TPE_phone2',
    'TPE_run',
    'TPE_runbackwards',
    'TPE_runIN',
    'TPE_runjumpFLY',
    'TPE_runjumpIN',
    'TPE_runjumpOUT',
    'TPE_runL',
    'TPE_runOUT',
    'TPE_runR',
    'TPE_scream',
    'TPE_sitdownIN',
    'TPE_sitdownOUT',
    'TPE_sitidle1',
    'TPE_sitidle2',
    'TPE_sitphone1',
    'TPE_sitphone2',
    'TPE_stairsDOWN',
    'TPE_stairsUP',
    'TPE_strafeL',
    'TPE_strafeR',
    'TPE_talk1',
    'TPE_talk2',
    'TPE_telloff',
    'TPE_turnL45',
    'TPE_turnL90',
    'TPE_turnR45',
    'TPE_turnR90',
    'TPE_walk',
    'TPE_walkbackwards',
    'TPE_wave',
    'TPF_brake',
    'TPF_clap',
    'TPF_cry',
    'TPF_fallbackwardsFLY',
    'TPF_fallbackwardsIN',
    'TPF_fallbackwardsOUT',
    'TPF_fallforwardFLY',
    'TPF_fallforwardIN',
    'TPF_fallforwardOUT',
    'TPF_freefall',
    'TPF_freeze',
    'TPF_hitbackwards',
    'TPF_hitforward',
    'TPF_idle1',
    'TPF_idle2',
    'TPF_idle3',
    'TPF_idle4',
    'TPF_idle5',
    'TPF_idleafraid',
    'TPF_idleangry',
    'TPF_idlehappy',
    'TPF_idlesad',
    'TPF_jump',
    'TPF_land',
    'TPF_laugh',
    'TPF_lookback',
    'TPF_phone1',
    'TPF_phone2',
    'TPF_run',
    'TPF_runbackwards',
    'TPF_runIN',
    'TPF_runjumpFLY',
    'TPF_runjumpIN',
    'TPF_runjumpOUT',
    'TPF_runL',
    'TPF_runOUT',
    'TPF_runR',
    'TPF_runstrafeL',
    'TPF_runstrafeR',
    'TPF_scream',
    'TPF_sitdownIN',
    'TPF_sitdownOUT',
    'TPF_sitidle1',
    'TPF_sitidle2',
    'TPF_sitphone1',
    'TPF_sitphone2',
    'TPF_stairsDOWN',
    'TPF_stairsUP',
    'TPF_static',
    'TPF_strafeL',
    'TPF_strafeR',
    'TPF_talk1',
    'TPF_talk2',
    'TPF_telloff',
    'TPF_turnL45',
    'TPF_turnL90',
    'TPF_turnR45',
    'TPF_turnR90',
    'TPF_walk',
    'TPF_walkbackwards',
    'TPF_wave',
    'TPM_brake',
    'TPM_clap',
    'TPM_cry',
    'TPM_fallbackwardsFLY',
    'TPM_fallbackwardsIN',
    'TPM_fallbackwardsOUT',
    'TPM_fallforwardFLY',
    'TPM_fallforwardIN',
    'TPM_fallforwardOUT',
    'TPM_freefall',
    'TPM_freeze',
    'TPM_hitbackwards',
    'TPM_hitforward',
    'TPM_idle1',
    'TPM_idle2',
    'TPM_idle3',
    'TPM_idle4',
    'TPM_idle5',
    'TPM_idleafraid',
    'TPM_idleangry',
    'TPM_idlehappy',
    'TPM_idlesad',
    'TPM_jump',
    'TPM_land',
    'TPM_laugh',
    'TPM_lookback',
    'TPM_phone1',
    'TPM_phone2',
    'TPM_run',
    'TPM_runbackwards',
    'TPM_runIN',
    'TPM_runjumpFLY',
    'TPM_runjumpIN',
    'TPM_runjumpOUT',
    'TPM_runL',
    'TPM_runOUT',
    'TPM_runR',
    'TPM_runstrafeL',
    'TPM_runstrafeR',
    'TPM_scream',
    'TPM_sitdownIN',
    'TPM_sitdownOUT',
    'TPM_sitidle1',
    'TPM_sitidle2',
    'TPM_sitphone1',
    'TPM_sitphone2',
    'TPM_stairsDOWN',
    'TPM_stairsUP',
    'TPM_static',
    'TPM_strafeL',
    'TPM_strafeR',
    'TPM_talk1',
    'TPM_talk2',
    'TPM_telloff',
    'TPM_turnL45',
    'TPM_turnL90',
    'TPM_turnR45',
    'TPM_turnR90',
    'TPM_walk',
    'TPM_walkbackwards',
    'TPM_wave'
]


# Note whether to use specific wall materials with dark skin and/or light
# skin tone agents (chosen arbitrarily based on looking at the materials).
WALL_MATERIALS_DARK_SKIN = [
    materials.DRYWALL,
    materials.DRYWALL_BEIGE,
    materials.DRYWALL_GREEN,
    materials.DRYWALL_ORANGE,
    materials.DRYWALL_4_TILED,
    materials.EGGSHELL_DRYWALL,
    materials.WALL_DRYWALL_GREY,
    materials.YELLOW_DRYWALL,
    materials.BEDROOM_FLOOR_1,
    materials.TEXTURES_COM_WOOD_FINE_50_1_SEEMLESS,
    materials.WOOD_FLOORS_CROSS,
    materials.WOOD_GRAIN_TAN,
    materials.KINDERGARTEN_BLUE_WOOD,
    materials.KINDERGARTEN_RED_WOOD,
    materials.KINDERGARTEN_GREEN_WOOD,
    materials.KINDERGARTEN_YELLOW_WOOD,
    materials.NURSERY_BROWN_WOOD,
    materials.CONCRETE_BOARDS_1,
    materials.GREY_GRANITE,
    materials.PINK_CONCRETE_BEDROOM_1,
    materials.WHITE_COUNTERTOP
] + [item for item in (
    materials.CUSTOM_DRYWALL_MATERIALS + materials.CUSTOM_WOOD_MATERIALS
) if (
    not item.material.startswith('Custom/Materials/Black') and
    not item.material.startswith('Custom/Materials/Brown')
)]
WALL_MATERIALS_LIGHT_SKIN = [
    materials.BROWN_DRYWALL,
    materials.DRYWALL,
    materials.DRYWALL_BEIGE,
    materials.DRYWALL_GREEN,
    materials.DRYWALL_4_TILED,
    materials.EGGSHELL_DRYWALL,
    materials.RED_DRYWALL,
    materials.WALL_DRYWALL_GREY,
    materials.DARK_WOOD_2,
    materials.DARK_WOOD_SMOOTH_2,
    materials.WORN_WOOD,
    materials.KINDERGARTEN_BLUE_WOOD,
    materials.KINDERGARTEN_RED_WOOD,
    materials.KINDERGARTEN_GREEN_WOOD,
    materials.KINDERGARTEN_YELLOW_WOOD,
    materials.CONCRETE_BOARDS_1,
    materials.CONCRETE_FLOOR,
    materials.GREY_GRANITE,
    materials.WHITE_COUNTERTOP
] + [item for item in (
    materials.CUSTOM_DRYWALL_MATERIALS + materials.CUSTOM_WOOD_MATERIALS
)]
WALL_MATERIALS_NO_AGENTS = [
    materials.BLACK_WOOD,
    materials.WHITE_WOOD,
    # Ignore most metal textures due to the reflection.
    materials.BLACK_SMOOTH_METAL,
    materials.BRASS_1,
    materials.BROWN_METAL_1,
    materials.BRUSHED_ALUMINUM_BLUE,
    materials.BRUSHED_IRON_ALBEDO,
    materials.GENERIC_STAINLESS_STEEL,
    materials.HAMMERED_METAL_ALBEDO,
    materials.METAL,
    materials.WHITE_METAL,
    materials.NURSERY_CABINET_METAL,
    # Ignore some brown textures.
    materials.LIGHT_WOOD_COUNTERS_1,
    materials.LIGHT_WOOD_COUNTERS_3,
    materials.LIGHT_WOOD_COUNTERS_4,
    materials.WOOD_GRAIN_BROWN,
    materials.BROWN_MARBLE_FAKE_1
]
