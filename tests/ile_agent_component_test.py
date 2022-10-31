import pytest

from generator.agents import AGENT_TYPES
from generator.scene import Scene
from ideal_learning_env.agent_component import (
    RandomAgentComponent,
    SpecificAgentComponent
)
from ideal_learning_env.defs import ILEException
from ideal_learning_env.object_services import ObjectRepository


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()

    # Run test
    yield

    # Cleanup
    ObjectRepository.get_instance().clear()


def test_specific_agent_component_default():
    scene = Scene()
    cmp = SpecificAgentComponent({})
    assert cmp.specific_agents is None
    assert cmp.get_specific_agents() is None
    scene: Scene = cmp.update_ile_scene(scene)
    assert len(scene.objects) == 0


def test_specific_agent_component_basic_full():
    scene = Scene()
    cmp = SpecificAgentComponent({
        'specific_agents': {
            'num': 2,
            'position': {
                'x': [1, 0], 'y': 0, 'z': 3
            },
            'rotation_y': 45,
            'type': 'agent_female_02',
            'agent_settings': {
                'chest': 1,
                'eyes': 1
            }
        }
    })
    assert cmp.specific_agents
    assert cmp.get_specific_agents()
    scene: Scene = cmp.update_ile_scene(scene)
    assert len(scene.objects) == 2
    agent1 = scene.objects[0]
    agent2 = scene.objects[1]
    if agent1['shows'][0]['position']['x'] == 1:
        agent1, agent2 = agent2, agent1
    assert agent1['id'].startswith('agent')
    assert agent1['type'] == 'agent_female_02'
    assert agent1['type'] in AGENT_TYPES
    assert agent1['shows'][0]['position']['x'] == 0
    assert agent1['shows'][0]['position']['y'] == 0
    assert agent1['shows'][0]['position']['z'] == 3
    assert agent1['shows'][0]['rotation']['x'] == 0
    assert agent1['shows'][0]['rotation']['y'] == 45
    assert agent1['shows'][0]['rotation']['z'] == 0
    assert agent1['shows'][0]['scale']['x'] == 1
    assert agent1['shows'][0]['scale']['y'] == 1
    assert agent1['shows'][0]['scale']['z'] == 1
    assert agent1['agentSettings']['chest'] == 1
    assert agent1['agentSettings']['eyes'] == 1
    assert agent1['actions'] == []

    assert agent2['id'].startswith('agent')
    assert agent2['type'] == 'agent_female_02'
    assert agent2['type'] in AGENT_TYPES
    assert agent2['shows'][0]['position']['x'] == 1
    assert agent2['shows'][0]['position']['y'] == 0
    assert agent2['shows'][0]['position']['z'] == 3
    assert agent2['shows'][0]['rotation']['x'] == 0
    assert agent2['shows'][0]['rotation']['y'] == 45
    assert agent2['shows'][0]['rotation']['z'] == 0
    assert agent2['shows'][0]['scale']['x'] == 1
    assert agent2['shows'][0]['scale']['y'] == 1
    assert agent2['shows'][0]['scale']['z'] == 1
    assert agent2['agentSettings']['chest'] == 1
    assert agent2['agentSettings']['eyes'] == 1
    assert agent2['actions'] == []


def test_specific_agent_component_with_actions():
    scene = Scene()
    cmp = SpecificAgentComponent({
        'specific_agents': {
            'num': 1,
            'position': {
                'x': 2, 'y': 0, 'z': 3
            },
            'actions': [
                {
                    'step_begin': [8, 10],
                    'step_end': [20, 23],
                    'is_loop_animation': False,
                    'id': 'TPE_cry'
                },
                {
                    'step_begin': [0, 1],
                    'step_end': [4, 5],
                    'is_loop_animation': False,
                    'id': 'TPE_clap'
                }
            ]
        }
    })
    assert cmp.specific_agents
    assert cmp.get_specific_agents()
    scene: Scene = cmp.update_ile_scene(scene)
    assert len(scene.objects) == 1
    agent1 = scene.objects[0]
    assert agent1['id'].startswith('agent')
    assert agent1['type'] in AGENT_TYPES
    assert agent1['shows'][0]['position']['x'] == 2
    assert agent1['shows'][0]['position']['y'] == 0
    assert agent1['shows'][0]['position']['z'] == 3
    assert agent1['shows'][0]['rotation']['x'] == 0
    assert agent1['shows'][0]['rotation']['z'] == 0
    assert agent1['shows'][0]['scale']['x'] == 1
    assert agent1['shows'][0]['scale']['y'] == 1
    assert agent1['shows'][0]['scale']['z'] == 1
    assert len(agent1['actions']) == 2
    action = agent1['actions'][0]
    assert action['stepBegin'] in [0, 1]
    assert action['stepEnd'] in [4, 5]
    assert action['isLoopAnimation'] is False
    assert action['id'] == 'TPE_clap'
    action = agent1['actions'][1]
    assert action['stepBegin'] in [8, 10]
    assert action['stepEnd'] in [20, 23]
    assert action['isLoopAnimation'] is False
    assert action['id'] == 'TPE_cry'


def test_specific_agent_component_with_actions_fail():
    scene = Scene()
    cmp = SpecificAgentComponent({
        'specific_agents': {
            'num': 1,
            'position': {
                'x': 2, 'y': 0, 'z': 3
            },
            'actions': [
                {
                    'step_begin': 3,
                    'step_end': [20, 23],
                    'is_loop_animation': False,
                    'id': 'TPE_cry'
                },
                {
                    'step_begin': 3,
                    'step_end': [4, 5],
                    'is_loop_animation': False,
                    'id': 'TPE_clap'
                }
            ]
        }
    })
    assert cmp.specific_agents
    assert cmp.get_specific_agents()
    with pytest.raises(ILEException):
        scene: Scene = cmp.update_ile_scene(scene)


def test_specific_agent_component_on_performer_fail():
    scene = Scene()
    cmp = SpecificAgentComponent({
        'specific_agents': {
            'num': 1,
            'position': {
                'x': 0, 'y': 0, 'z': 0
            }
        }
    })
    assert cmp.specific_agents
    assert cmp.get_specific_agents()
    with pytest.raises(ILEException):
        cmp.update_ile_scene(scene)


def test_specific_agent_component_overlap_fail():
    scene = Scene()
    cmp = SpecificAgentComponent({
        'specific_agents': {
            'num': 2,
            'position': {
                'x': 3, 'y': 0, 'z': 3
            }
        }
    })
    assert cmp.specific_agents
    assert cmp.get_specific_agents()
    with pytest.raises(ILEException):
        cmp.update_ile_scene(scene)


def test_specific_agent_component_bad_type_fail():
    with pytest.raises(ILEException):
        SpecificAgentComponent({
            'specific_agents': {
                'num': 1,
                'type': 'fancy_agent'
            }
        })


def test_random_agent_component_default():
    scene = Scene()
    cmp = RandomAgentComponent({})
    assert cmp.num_random_agents is None
    assert cmp.get_num_random_agents() == 0
    scene: Scene = cmp.update_ile_scene(scene)
    assert len(scene.objects) == 0


def test_random_agent_component_num():
    scene = Scene()
    cmp = RandomAgentComponent({
        'num_random_agents': 2
    })
    assert cmp.num_random_agents == 2
    assert cmp.get_num_random_agents() == 2
    scene: Scene = cmp.update_ile_scene(scene)
    assert len(scene.objects) == 2
    agent = scene.objects[0]
    assert agent['id'].startswith('agent')
    assert 'agent_' in agent['type']
    assert '_male_0' in agent['type'] or '_female_0' in agent['type']
    assert agent['type'] in AGENT_TYPES
    assert agent['shows'][0]['position']['y'] == 0
    assert agent['shows'][0]['rotation']['x'] == 0
    assert agent['shows'][0]['rotation']['z'] == 0
    assert agent['shows'][0]['scale']['x'] == 1
    assert agent['shows'][0]['scale']['y'] == 1
    assert agent['shows'][0]['scale']['z'] == 1


def test_random_agent_component_doc_example():
    scene = Scene()
    cmp = SpecificAgentComponent({
        "specific_agents": {
            "num": 1,
            "type": "agent_female_02",
            "agent_settings": {
                "chest": 2,
                "eyes": 1
            },
            "position": {
                "x": [1, 0, -1, 0.5, -0.5],
                "y": 0,
                "z": [1, 0, -1]
            },
            "rotation_y": [0, 10, 350],
            "actions": [{
                "step_begin": [1, 2],
                "step_end": 7,
                "is_loop_animation": False,
                "id": ["TPM_clap", "TPM_cry"]
            }, {
                "step_begin": [13, 14],
                "step_end": 17,
                "is_loop_animation": True,
                "id": ["TPM_clap", "TPM_cry"]
            }
            ],
            "movement": {
                "animation": "TPE_walk",
                "step_begin": [2, 4],
                "bounds": [{
                    "x": 2,
                    "z": 0
                }, {
                    "x": 0,
                    "z": 2
                }, {
                    "x": -2,
                    "z": 0
                }, {
                    "x": 0,
                    "z": -2
                }
                ],
                "num_points": 5,
                "repeat": True
            }
        }})
    assert cmp.specific_agents
    assert cmp.get_specific_agents()
    scene: Scene = cmp.update_ile_scene(scene)
    assert len(scene.objects) == 1
    agent = scene.objects[0]
    assert agent['id'].startswith('agent')
    assert 'agent_' in agent['type']
    assert agent['type'] == "agent_female_02"
    assert agent['shows'][0]['position']['x'] in [1, 0, -1, 0.5, -0.5]
    assert agent['shows'][0]['position']['y'] == 0
    assert agent['shows'][0]['position']['z'] in [1, 0, -1]
    assert agent['shows'][0]['rotation']['x'] == 0
    assert agent['shows'][0]['rotation']['y'] in [0, 10, 350]
    assert agent['shows'][0]['rotation']['z'] == 0
    assert agent['shows'][0]['scale']['x'] == 1
    assert agent['shows'][0]['scale']['y'] == 1
    assert agent['shows'][0]['scale']['z'] == 1
    actions = agent['actions']
    assert len(actions) == 2
    actions[0]['stepBegin'] in [1, 2]
    actions[0]['stepEnd'] == 7
    actions[0]['isLoopAnimation'] is False
    actions[0]['id'] in ["TPM_clap", "TPM_cry"]
    actions[1]['stepBegin'] in [13, 14]
    actions[1]['stepEnd'] == 17
    actions[1]['isLoopAnimation'] is True
    actions[1]['id'] in ["TPM_clap", "TPM_cry"]
    move = agent['agentMovement']
    assert move['stepBegin'] in [2, 4]
    assert move['repeat'] is True
    seq = move['sequence']
    assert len(seq) == 5
    for item in seq:
        assert item['animation'] == 'TPE_walk'
        assert -2 <= item['endPoint']['x'] <= 2
        assert -2 <= item['endPoint']['z'] <= 2
