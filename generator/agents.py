import copy
import uuid
from typing import Any, Dict, List, Tuple

from generator.exceptions import SceneException

from .geometry import create_bounds

# Agents were scaled down to 0.6 from their original size.  However, lets
# retain the original bounding box size though and just apply that scale.
AGENT_SCALE = 0.6
AGENT_DIMENSIONS = {'x': 0.5 * AGENT_SCALE,
                    'y': 1.6 * AGENT_SCALE,
                    'z': 0.5 * AGENT_SCALE}
AGENT_TYPES = [
    'agent_female_01', 'agent_female_02', 'agent_female_04',
    'agent_male_02', 'agent_male_03', 'agent_male_04']

AGENT_MOVEMENT_ANIMATIONS = ['TPM_walk', 'TPM_run']

AGENT_TEMPLATE = {
    'id': 'agent_',
    'type': '',
    'debug': {
        'color': [],
        'info': []
    },
    'mass': None,
    'agentSettings': {},
    'agentMovement': [],
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
    return agent


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
