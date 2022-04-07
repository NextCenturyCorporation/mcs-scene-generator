import pytest
from machine_common_sense.config_manager import Vector3d

from generator.agents import AGENT_TYPES
from generator.scene import Scene
from ideal_learning_env.agent_service import (
    AgentActionConfig,
    AgentConfig,
    AgentCreationService,
    AgentSettings,
)
from ideal_learning_env.defs import ILEException
from ideal_learning_env.numerics import MinMaxFloat, VectorFloatConfig
from ideal_learning_env.object_services import ObjectRepository


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()

    # Run test
    yield

    # Cleanup
    ObjectRepository.get_instance().clear()


def test_agent_service_reconcile():
    scene = Scene()
    template = AgentConfig(
        1,
        type=[
            'test_type',
            'test_type2'],
        agent_settings=AgentSettings(
            chest=[
                2,
                4]),
        position=VectorFloatConfig([1, 2], MinMaxFloat(0.5, 0.6),
                                   [1, MinMaxFloat(4.4, 4.5)]),
        rotation_y=[56, 57])
    srv = AgentCreationService()
    reconciled: AgentConfig = srv.reconcile(scene, template)
    assert reconciled.num == 1
    assert reconciled.type in ['test_type', 'test_type2']
    assert reconciled.agent_settings.chest in [2, 4]
    assert reconciled.position.x in [1, 2]
    assert 0.5 <= reconciled.position.y <= 0.6
    assert reconciled.position.z == 1 or 4.4 <= reconciled.position.z <= 4.5
    assert reconciled.rotation_y in [56, 57]


def test_agent_service_reconcile_default():
    scene = Scene()
    template = AgentConfig(1)
    srv = AgentCreationService()
    reconciled: AgentConfig = srv.reconcile(scene, template)
    assert reconciled.num == 1
    assert reconciled.type in AGENT_TYPES
    assert -5 <= reconciled.position.x <= 5
    assert 0 == reconciled.position.y
    assert -5 <= reconciled.position.z <= 5
    assert 0 <= reconciled.rotation_y <= 360


def test_agent_service_create():
    scene = Scene()
    template = AgentConfig(
        1,
        type='test_type',
        agent_settings=AgentSettings(),
        position=VectorFloatConfig(1, 0.5, 1),
        rotation_y=90)
    srv = AgentCreationService()
    agent = srv.create_feature_from_specific_values(
        scene, template, template)
    assert agent['type'] == 'test_type'
    assert agent['id'].startswith('agent')
    assert agent['agentSettings']
    assert agent['shows'][0]['position']['x'] == 1
    assert agent['shows'][0]['position']['y'] == 0.5
    assert agent['shows'][0]['position']['z'] == 1
    assert agent['shows'][0]['rotation']['x'] == 0
    assert agent['shows'][0]['rotation']['y'] == 90
    assert agent['shows'][0]['rotation']['z'] == 0
    assert agent['shows'][0]['scale']['x'] == 1
    assert agent['shows'][0]['scale']['y'] == 1
    assert agent['shows'][0]['scale']['z'] == 1
    bb = agent['shows'][0]['boundingBox']
    assert bb.min_y == 0.5
    assert bb.max_y == 1.46
    assert bb.box_xz[0] == Vector3d(x=1.15, y=0, z=0.85)
    assert bb.box_xz[1] == Vector3d(x=0.85, y=0, z=0.85)
    assert bb.box_xz[2] == Vector3d(x=0.85, y=0, z=1.15)
    assert bb.box_xz[3] == Vector3d(x=1.15, y=0, z=1.15)

    assert agent['debug']['dimensions'] == {'x': 0.3, 'y': 0.96, 'z': 0.3}


def test_agent_service_add():
    scene = Scene()
    template = AgentConfig(
        1,
        type='test_type',
        agent_settings=AgentSettings(),
        position=VectorFloatConfig(1, 0.5, 1),
        rotation_y=90)
    srv = AgentCreationService()
    agents, _ = srv.add_to_scene(scene, template, [])
    agent = agents[0]
    assert agent['type'] == 'test_type'
    assert agent['id'].startswith('agent')
    assert agent['agentSettings']
    assert agent['shows'][0]['position']['x'] == 1
    assert agent['shows'][0]['position']['y'] == 0.5
    assert agent['shows'][0]['position']['z'] == 1
    assert agent['shows'][0]['rotation']['x'] == 0
    assert agent['shows'][0]['rotation']['y'] == 90
    assert agent['shows'][0]['rotation']['z'] == 0
    assert agent['shows'][0]['scale']['x'] == 1
    assert agent['shows'][0]['scale']['y'] == 1
    assert agent['shows'][0]['scale']['z'] == 1
    bb = agent['shows'][0]['boundingBox']
    assert bb.min_y == 0.5
    assert bb.max_y == 1.46
    assert bb.box_xz[0] == Vector3d(x=1.15, y=0, z=0.85)
    assert bb.box_xz[1] == Vector3d(x=0.85, y=0, z=0.85)
    assert bb.box_xz[2] == Vector3d(x=0.85, y=0, z=1.15)
    assert bb.box_xz[3] == Vector3d(x=1.15, y=0, z=1.15)

    assert agent['debug']['dimensions'] == {'x': 0.3, 'y': 0.96, 'z': 0.3}
    repo_agents = (ObjectRepository.get_instance().
                   get_all_from_labeled_objects('agent'))
    assert len(repo_agents) == 1
    assert repo_agents[0].instance == agents[0]


def test_agent_service_add_fail():
    scene = Scene()
    template = AgentConfig(
        2,
        type='test_type',
        agent_settings=AgentSettings(),
        position=VectorFloatConfig(1, 0.5, 1),
        rotation_y=90)
    srv = AgentCreationService()
    bounds = []
    srv.add_to_scene(scene, template, bounds)
    with pytest.raises(ILEException):
        srv.add_to_scene(scene, template, bounds)


def test_agent_service_add_actions():
    scene = Scene()
    actions = [
        AgentActionConfig(id='action2', step_begin=10),
        AgentActionConfig(id='action1', step_begin=2, step_end=7),
        AgentActionConfig(id='action3', step_begin=20, is_loop_animation=True)
    ]
    template = AgentConfig(
        1,
        type='test_type',
        agent_settings=AgentSettings(),
        position=VectorFloatConfig(0, 0, 2),
        rotation_y=180,
        actions=actions)
    srv = AgentCreationService()
    agents, _ = srv.add_to_scene(scene, template, [])
    agent = agents[0]
    assert agent['type'] == 'test_type'
    assert agent['id'].startswith('agent')
    assert agent['agentSettings']
    assert agent['shows'][0]['position']['x'] == 0
    assert agent['shows'][0]['position']['y'] == 0
    assert agent['shows'][0]['position']['z'] == 2
    assert agent['shows'][0]['rotation']['x'] == 0
    assert agent['shows'][0]['rotation']['y'] == 180
    assert agent['shows'][0]['rotation']['z'] == 0
    assert agent['shows'][0]['scale']['x'] == 1
    assert agent['shows'][0]['scale']['y'] == 1
    assert agent['shows'][0]['scale']['z'] == 1
    bb = agent['shows'][0]['boundingBox']
    assert bb.min_y == 0
    assert bb.max_y == 0.96
    assert bb.box_xz[0].x == pytest.approx(-0.15)
    assert bb.box_xz[0].y == 0
    assert bb.box_xz[0].z == 1.85
    assert bb.box_xz[1].x == pytest.approx(-0.15)
    assert bb.box_xz[1].y == 0
    assert bb.box_xz[1].z == 2.15
    assert bb.box_xz[2].x == pytest.approx(0.15)
    assert bb.box_xz[2].y == 0
    assert bb.box_xz[2].z == 2.15
    assert bb.box_xz[3].x == pytest.approx(0.15)
    assert bb.box_xz[3].y == 0
    assert bb.box_xz[3].z == 1.85

    assert len(agent['actions']) == 3
    assert agent['actions'][0]['id'] == 'action1'
    assert agent['actions'][0]['stepBegin'] == 2
    assert agent['actions'][0].get('stepEnd') == 7
    assert agent['actions'][0].get('isLoopAnimation') is False
    assert agent['actions'][1]['id'] == 'action2'
    assert agent['actions'][1]['stepBegin'] == 10
    assert agent['actions'][1].get('stepEnd') is None
    assert agent['actions'][1].get('isLoopAnimation') is False
    assert agent['actions'][2]['id'] == 'action3'
    assert agent['actions'][2]['stepBegin'] == 20
    assert agent['actions'][2].get('stepEnd') is None
    assert agent['actions'][2].get('isLoopAnimation') is True

    assert agent['debug']['dimensions'] == {'x': 0.3, 'y': 0.96, 'z': 0.3}
    repo_agents = (ObjectRepository.get_instance().
                   get_all_from_labeled_objects('agent'))
    assert len(repo_agents) == 1
    assert repo_agents[0].instance == agents[0]


def test_agent_service_add_actions_fail():
    scene = Scene()
    actions = [
        AgentActionConfig(id='action2', step_begin=1),
        AgentActionConfig(id='action1', step_begin=1, step_end=7),
        AgentActionConfig(id='action3', step_begin=20, is_loop_animation=True)
    ]
    template = AgentConfig(
        1,
        type='test_type',
        agent_settings=AgentSettings(),
        position=VectorFloatConfig(0, 0, 2),
        rotation_y=180,
        actions=actions)
    srv = AgentCreationService()
    with pytest.raises(ILEException):
        srv.add_to_scene(scene, template, [])
