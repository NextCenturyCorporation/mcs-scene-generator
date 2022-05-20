import copy
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from machine_common_sense.config_manager import Vector3d

from generator.exceptions import SceneException

from .geometry import create_bounds
from .materials import MaterialTuple

# Agents were scaled down to 0.6 from their original size.  However, lets
# retain the original bounding box size though and just apply that scale.
AGENT_SCALE = 0.6
AGENT_DIMENSIONS = {'x': 0.5 * AGENT_SCALE,
                    'y': 1.6 * AGENT_SCALE,
                    'z': 0.5 * AGENT_SCALE}
AGENT_TYPES = [
    'agent_female_01', 'agent_female_02', 'agent_female_04',
    'agent_male_02', 'agent_male_03', 'agent_male_04']

AGENT_MOVEMENT_ANIMATIONS = ['TPM_walk', 'TPM_run', 'TPF_walk', 'TPF_run']

AGENT_TEMPLATE = {
    'id': 'agent_',
    'type': '',
    'debug': {
        'color': [],
        'info': []
    },
    'mass': None,
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
        'info': []
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


def create_agent(
    type: str,
    position_x: float,
    position_z: float,
    rotation_y: float,
    settings: dict = None,
    position_y_modifier: float = 0
) -> Dict[str, Any]:
    """Create and return an instance of an agent without any actions."""
    agent = copy.deepcopy(AGENT_TEMPLATE)
    agent['id'] += str(uuid.uuid4())
    agent['type'] = type
    agent['shows'][0]['position'] = {
        'x': position_x,
        'y': position_y_modifier,
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
    agent['debug']['offset'] = {'x': 0, 'y': 0, 'z': 0}
    agent['debug']['positionY'] = 0
    return agent


def create_blob(
    type: str,
    position_x: float,
    position_z: float,
    rotation_y: float,
    material_tuple: MaterialTuple,
    height: float = 0.9,
    position_y_modifier: float = 0
) -> Dict[str, Any]:
    """Create and return an instance of a blob. By default, it will be
    approximately as tall as a normal agent."""
    blob = copy.deepcopy(BLOB_TEMPLATE)
    blob['id'] += str(uuid.uuid4())
    blob['type'] = type
    blob['shows'][0]['rotation'] = {
        'x': 0,
        'y': rotation_y,
        'z': 0
    }

    base_dimensions = BLOB_SHAPES[type].dimensions
    scale = round(height / base_dimensions.y, 4)
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


def add_agent_action(agent: dict, action_id, step_begin,
                     step_end=None, is_loop=False):
    actions = agent.get('actions', [])
    if step_begin is None or step_begin < 0 or not isinstance(step_begin, int):
        raise SceneException(
            f"step_begin must be an integer greater or equal to 0.  "
            f"step_begin={step_begin}")

    if action_id is None or not isinstance(action_id, str):
        raise SceneException(
            f"action_id must be an string. action_id={action_id}")

    for action in actions:
        if action['stepBegin'] == step_begin:
            raise SceneException(
                f"Cannot add agent action when an action already exists with "
                f"the same 'stepBegin'.  StepBegin={step_begin}")

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
        agent: dict, step_begin: int, points: List[Tuple[float, float]],
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
