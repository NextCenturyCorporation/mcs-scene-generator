import pytest
from machine_common_sense.config_manager import Vector3d

from generator.agents import add_agent_action, create_agent, create_blob
from generator.exceptions import SceneException
from generator.materials import MaterialTuple
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


def test_create_blob_simple():
    blob = create_blob(
        type='blob_02',
        position_x=1,
        position_z=2,
        rotation_y=0,
        material_tuple=MaterialTuple('test_material', ['test_color'])
    )

    assert blob['id'].startswith('blob')
    assert blob['type'] == 'blob_02'
    assert blob['physics'] is True
    assert blob['mass']
    assert blob['materials'] == ['test_material']
    assert blob['debug']['color'] == ['test_color']
    assert blob['shows'][0]['position'] == {'x': 1, 'y': 0.45, 'z': 2}
    assert blob['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert blob['shows'][0]['scale'] == {'x': 1.1538, 'y': 1.1538, 'z': 1.1538}
    assert blob['debug']['dimensions'] == {
        'x': 0.3808,
        'y': 0.9,
        'z': 0.3808
    }
    assert blob['shows'][0]['boundingBox'].box_xz == [
        Vector3d(x=1.1904, y=0, z=2.1904),
        Vector3d(x=1.1904, y=0, z=1.8096),
        Vector3d(x=0.8096, y=0, z=1.8096),
        Vector3d(x=0.8096, y=0, z=2.1904),
    ]
    assert blob['shows'][0]['boundingBox'].min_y == 0
    assert blob['shows'][0]['boundingBox'].max_y == 0.9


def test_create_blob_advanced():
    blob = create_blob(
        type='blob_02',
        position_x=-1,
        position_z=-2,
        rotation_y=45,
        material_tuple=MaterialTuple('test_material', ['test_color']),
        height=1.8,
        position_y_modifier=10
    )

    assert blob['id'].startswith('blob')
    assert blob['type'] == 'blob_02'
    assert blob['physics'] is True
    assert blob['mass']
    assert blob['materials'] == ['test_material']
    assert blob['debug']['color'] == ['test_color']
    assert blob['shows'][0]['position'] == {'x': -1, 'y': 10.9, 'z': -2}
    assert blob['shows'][0]['rotation'] == {'x': 0, 'y': 45, 'z': 0}
    assert blob['shows'][0]['scale'] == {'x': 2.3077, 'y': 2.3077, 'z': 2.3077}
    assert blob['debug']['dimensions'] == {
        'x': 0.7615,
        'y': 1.8,
        'z': 0.7615
    }
    assert blob['shows'][0]['boundingBox'].box_xz == [
        Vector3d(x=-0.461538, y=0, z=-2.0),
        Vector3d(x=-1.0, y=0, z=-2.538462),
        Vector3d(x=-1.538462, y=0, z=-2.0),
        Vector3d(x=-1.0, y=0, z=-1.461538),
    ]
    assert blob['shows'][0]['boundingBox'].min_y == 10
    assert blob['shows'][0]['boundingBox'].max_y == 11.8


def test_create_blob_type_with_standing_y():
    blob = create_blob(
        type='blob_05',
        position_x=1,
        position_z=2,
        rotation_y=0,
        material_tuple=MaterialTuple('test_material', ['test_color'])
    )

    assert blob['id'].startswith('blob')
    assert blob['type'] == 'blob_05'
    assert blob['physics'] is True
    assert blob['mass']
    assert blob['materials'] == ['test_material']
    assert blob['debug']['color'] == ['test_color']
    assert blob['shows'][0]['position'] == {'x': 1, 'y': 0.3857, 'z': 2}
    assert blob['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert blob['shows'][0]['scale'] == {'x': 1.6071, 'y': 1.6071, 'z': 1.6071}
    assert blob['debug']['dimensions'] == {
        'x': 0.6107,
        'y': 0.9,
        'z': 0.6107
    }
    assert blob['shows'][0]['boundingBox'].box_xz == [
        Vector3d(x=1.30535, y=0, z=2.30535),
        Vector3d(x=1.30535, y=0, z=1.69465),
        Vector3d(x=0.69465, y=0, z=1.69465),
        Vector3d(x=0.69465, y=0, z=2.30535),
    ]
    assert blob['shows'][0]['boundingBox'].min_y == 0
    assert blob['shows'][0]['boundingBox'].max_y == 0.9
