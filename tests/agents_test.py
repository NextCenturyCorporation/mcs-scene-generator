import pytest

from generator.agents import add_agent_action, create_agent
from generator.exceptions import SceneException
from ideal_learning_env.agent_service import AgentSettings


def test_create_agent():
    settings = vars(AgentSettings(chest=2, chestMaterial=4))
    agent = create_agent(
        type='test_type',
        position_x=1,
        position_z=2,
        rotation_y=45,
        settings=settings,
        position_y_modifier=1.5)
    assert agent['id'].startswith('agent')
    assert agent['type'] == 'test_type'
    pos = agent['shows'][0]['position']
    rot = agent['shows'][0]['rotation']
    scale = agent['shows'][0]['scale']
    assert pos == {'x': 1, 'y': 1.5, 'z': 2}
    assert rot == {'x': 0, 'y': 45, 'z': 0}
    assert scale == {'x': 1, 'y': 1, 'z': 1}
    assert agent['agentSettings']['chest'] == 2
    assert agent['agentSettings']['chestMaterial'] == 4


def test_add_agent_action():
    settings = vars(AgentSettings(chest=2, chestMaterial=4))
    agent = create_agent(
        type='test_type',
        position_x=1,
        position_z=2,
        rotation_y=45,
        settings=settings,
        position_y_modifier=1.5)

    assert agent['actions'] == []
    add_agent_action(agent, "wave", 4, 6, True)
    add_agent_action(agent, "dance", 1)

    actions = agent['actions']
    assert len(actions) == 2
    dance = actions[0]
    wave = actions[1]

    assert dance['id'] == 'dance'
    assert dance['stepBegin'] == 1
    assert dance.get('stepEnd') is None
    assert dance['isLoopAnimation'] is False

    assert wave['id'] == 'wave'
    assert wave['stepBegin'] == 4
    assert wave.get('stepEnd') == 6
    assert wave['isLoopAnimation'] is True


def test_add_agent_action_fail():
    settings = vars(AgentSettings(chest=2, chestMaterial=4))
    agent = create_agent(
        type='test_type',
        position_x=1,
        position_z=2,
        rotation_y=45,
        settings=settings,
        position_y_modifier=1.5)

    assert agent['actions'] == []
    add_agent_action(agent, "wave", 4, 6, True)
    with pytest.raises(SceneException):
        add_agent_action(agent, "dance", 4)
