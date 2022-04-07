import pytest

from generator.agents import AGENT_TYPES
from generator.scene import Scene
from ideal_learning_env.agent_component import (
    RandomAgentComponent,
    SpecificAgentComponent,
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
