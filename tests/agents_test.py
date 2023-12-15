import pytest
from machine_common_sense.config_manager import Vector3d

from generator.agents import (
    FAMILIAR_AGENTS_FEMALE,
    FAMILIAR_AGENTS_MALE,
    NOVEL_AGENTS_FEMALE,
    NOVEL_AGENTS_MALE,
    WALL_MATERIALS_DARK_SKIN,
    WALL_MATERIALS_LIGHT_SKIN,
    WALL_MATERIALS_NO_AGENTS,
    add_agent_action,
    add_agent_pointing,
    create_agent,
    create_blob,
    get_random_agent_settings,
    set_pointing_angle
)
from generator.exceptions import SceneException
from generator.materials import ROOM_WALL_MATERIALS, MaterialTuple
from ideal_learning_env.agent_service import AgentSettings


def test_agent_types():
    assert len(FAMILIAR_AGENTS_FEMALE)
    assert len(FAMILIAR_AGENTS_MALE)
    assert len(NOVEL_AGENTS_FEMALE)
    assert len(NOVEL_AGENTS_MALE)
    for agent_type in FAMILIAR_AGENTS_FEMALE:
        assert agent_type not in FAMILIAR_AGENTS_MALE
        assert agent_type not in NOVEL_AGENTS_FEMALE
        assert agent_type not in NOVEL_AGENTS_MALE
    for agent_type in FAMILIAR_AGENTS_MALE:
        assert agent_type not in FAMILIAR_AGENTS_FEMALE
        assert agent_type not in NOVEL_AGENTS_FEMALE
        assert agent_type not in NOVEL_AGENTS_MALE
    for agent_type in NOVEL_AGENTS_FEMALE:
        assert agent_type not in FAMILIAR_AGENTS_FEMALE
        assert agent_type not in FAMILIAR_AGENTS_MALE
        assert agent_type not in NOVEL_AGENTS_MALE
    for agent_type in NOVEL_AGENTS_MALE:
        assert agent_type not in FAMILIAR_AGENTS_FEMALE
        assert agent_type not in FAMILIAR_AGENTS_MALE
        assert agent_type not in NOVEL_AGENTS_FEMALE


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


def test_add_agent_pointing():
    settings = vars(AgentSettings(chest=2, chestMaterial=4))
    agent = create_agent(
        type='test_type',
        position_x=1,
        position_z=2,
        rotation_y=45,
        settings=settings,
        position_y_modifier=1.5)
    assert agent['actions'] == []
    add_agent_pointing(agent, 1)
    assert len(agent['actions']) == 2
    assert agent['actions'][0]['id'] == 'Point_start_index_finger'
    assert agent['actions'][0]['stepBegin'] == 1
    assert agent['actions'][0]['stepEnd'] == 8
    assert not agent['actions'][0].get('isLoopAnimation')
    assert agent['actions'][1]['id'] == 'Point_hold_index_finger'
    assert agent['actions'][1]['stepBegin'] == 8
    assert agent['actions'][1]['isLoopAnimation'] is True
    assert agent['actions'][1].get('stepEnd') is None

    settings = vars(AgentSettings(chest=2, chestMaterial=4))
    agent = create_agent(
        type='test_type',
        position_x=1,
        position_z=2,
        rotation_y=45,
        settings=settings,
        position_y_modifier=1.5)
    agent['actions'] = [{
        'id': 'wave',
        'stepBegin': 5,
        'stepEnd': 15
    }]
    add_agent_pointing(agent, 21)
    assert len(agent['actions']) == 3
    assert agent['actions'][0]['id'] == 'wave'
    assert agent['actions'][0]['stepBegin'] == 5
    assert agent['actions'][0]['stepEnd'] == 15
    assert not agent['actions'][0].get('isLoopAnimation')
    assert agent['actions'][1]['id'] == 'Point_start_index_finger'
    assert agent['actions'][1]['stepBegin'] == 21
    assert agent['actions'][1]['stepEnd'] == 28
    assert not agent['actions'][1].get('isLoopAnimation')
    assert agent['actions'][2]['id'] == 'Point_hold_index_finger'
    assert agent['actions'][2]['stepBegin'] == 28
    assert agent['actions'][2]['isLoopAnimation'] is True
    assert agent['actions'][2].get('stepEnd') is None


def test_add_agent_pointing_fail():
    settings = vars(AgentSettings(chest=2, chestMaterial=4))
    agent = create_agent(
        type='test_type',
        position_x=1,
        position_z=2,
        rotation_y=45,
        settings=settings,
        position_y_modifier=1.5)
    agent['actions'] = [{
        'id': 'wave',
        'stepBegin': 5,
        'stepEnd': 15
    }]
    with pytest.raises(SceneException):
        add_agent_pointing(agent, 1)


def test_create_blob_simple():
    blob = create_blob(
        type='blob_17',
        position_x=1,
        position_z=2,
        rotation_y=0,
        material_tuple=MaterialTuple('test_material', ['test_color']),
        height=0.9
    )

    assert blob['id'].startswith('blob')
    assert blob['type'] == 'blob_17'
    assert blob['physics'] is True
    assert blob['mass']
    assert blob['materials'] == ['test_material']
    assert blob['debug']['color'] == ['test_color']
    assert blob['shows'][0]['position'] == {'x': 1, 'y': 0.444, 'z': 2}
    assert blob['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert blob['shows'][0]['scale'] == {'x': 1.1538, 'y': 1.1538, 'z': 1.1538}
    assert blob['debug']['dimensions'] == {'x': 0.3692, 'y': 0.9, 'z': 0.4731}
    assert blob['shows'][0]['boundingBox'].box_xz == [
        Vector3d(x=1.1846, y=0, z=2.23655),
        Vector3d(x=1.1846, y=0, z=1.76345),
        Vector3d(x=0.8154, y=0, z=1.76345),
        Vector3d(x=0.8154, y=0, z=2.23655),
    ]
    assert blob['shows'][0]['boundingBox'].min_y == 0
    assert blob['shows'][0]['boundingBox'].max_y == 0.9


def test_create_blob_advanced():
    blob = create_blob(
        type='blob_17',
        position_x=-1,
        position_z=-2,
        rotation_y=45,
        material_tuple=MaterialTuple('test_material', ['test_color']),
        height=1.8,
        position_y_modifier=10
    )

    assert blob['id'].startswith('blob')
    assert blob['type'] == 'blob_17'
    assert blob['physics'] is True
    assert blob['mass']
    assert blob['materials'] == ['test_material']
    assert blob['debug']['color'] == ['test_color']
    assert blob['shows'][0]['position'] == {'x': -1, 'y': 10.888, 'z': -2}
    assert blob['shows'][0]['rotation'] == {'x': 0, 'y': 45, 'z': 0}
    assert blob['shows'][0]['scale'] == {'x': 2.3077, 'y': 2.3077, 'z': 2.3077}
    assert blob['debug']['dimensions'] == {'x': 0.7385, 'y': 1.8, 'z': 0.9462}
    assert blob['shows'][0]['boundingBox'].box_xz == [
        Vector3d(x=-0.404369, y=0, z=-1.926567),
        Vector3d(x=-1.073433, y=0, z=-2.595631),
        Vector3d(x=-1.595631, y=0, z=-2.073433),
        Vector3d(x=-0.926567, y=0, z=-1.404369),
    ]
    assert blob['shows'][0]['boundingBox'].min_y == 10
    assert blob['shows'][0]['boundingBox'].max_y == 11.8


def test_create_blob_type_with_standing_y():
    blob = create_blob(
        type='blob_19',
        position_x=1,
        position_z=2,
        rotation_y=0,
        material_tuple=MaterialTuple('test_material', ['test_color']),
        height=0.9
    )

    assert blob['id'].startswith('blob')
    assert blob['type'] == 'blob_19'
    assert blob['physics'] is True
    assert blob['mass']
    assert blob['materials'] == ['test_material']
    assert blob['debug']['color'] == ['test_color']
    assert blob['shows'][0]['position'] == {'x': 1, 'y': 0.5085, 'z': 2}
    assert blob['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert blob['shows'][0]['scale'] == {'x': 1.125, 'y': 1.125, 'z': 1.125}
    assert blob['debug']['dimensions'] == {
        'x': 0.4388,
        'y': 0.9,
        'z': 0.4388
    }
    assert blob['shows'][0]['boundingBox'].box_xz == [
        Vector3d(x=1.2194, y=0, z=2.2194),
        Vector3d(x=1.2194, y=0, z=1.7806),
        Vector3d(x=0.7806, y=0, z=1.7806),
        Vector3d(x=0.7806, y=0, z=2.2194),
    ]
    assert blob['shows'][0]['boundingBox'].min_y == 0
    assert blob['shows'][0]['boundingBox'].max_y == 0.9


def test_create_blob_with_nose():
    blob = create_blob(
        type='blob_17',
        position_x=1,
        position_z=2,
        rotation_y=0,
        material_tuple=MaterialTuple('test_material', ['test_color']),
        height=0.9,
        with_nose=True
    )

    assert blob['id'].startswith('blob')
    assert blob['type'] == 'blob_17_nose'
    assert blob['physics'] is True
    assert blob['mass']
    assert blob['materials'] == ['test_material']
    assert blob['debug']['color'] == ['test_color']
    assert blob['shows'][0]['position'] == {'x': 1, 'y': 0.444, 'z': 2}
    assert blob['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert blob['shows'][0]['scale'] == {'x': 1.1538, 'y': 1.1538, 'z': 1.1538}
    assert blob['debug']['dimensions'] == {'x': 0.3692, 'y': 0.9, 'z': 0.4731}
    assert blob['shows'][0]['boundingBox'].box_xz == [
        Vector3d(x=1.1846, y=0, z=2.23655),
        Vector3d(x=1.1846, y=0, z=1.76345),
        Vector3d(x=0.8154, y=0, z=1.76345),
        Vector3d(x=0.8154, y=0, z=2.23655),
    ]
    assert blob['shows'][0]['boundingBox'].min_y == 0
    assert blob['shows'][0]['boundingBox'].max_y == 0.9


def verify_agent_settings(settings):
    assert settings['chest'] is not None
    assert settings['chestMaterial'] is not None
    assert settings['eyes'] is not None
    assert settings['feet'] is not None
    assert settings['feetMaterial'] is not None
    assert settings['hair'] is not None
    assert settings['hairMaterial'] is not None
    assert settings['hatMaterial'] is not None
    assert settings['legs'] is not None
    assert settings['legsMaterial'] is not None
    assert settings['skin'] is not None
    assert settings['hideHair'] in [True, False]
    assert settings['isElder'] in [True, False]
    assert settings['glasses'] == 0
    assert settings['jacket'] == 0
    assert settings['jacketMaterial'] == 0
    assert settings['tie'] == 0
    assert settings['tieMaterial'] == 0
    assert settings['showBeard'] is False
    assert settings['showGlasses'] is False
    assert settings['showJacket'] is False
    assert settings['showTie'] is False


def test_get_random_agent_settings_male():
    settings = get_random_agent_settings('agent_male_01')
    verify_agent_settings(settings)


def test_get_random_agent_settings_female():
    settings = get_random_agent_settings('agent_female_01')
    verify_agent_settings(settings)


def test_get_random_agent_settings_male_teen():
    settings = get_random_agent_settings('agent_male_08')
    verify_agent_settings(settings)
    assert settings['isElder'] is False


def test_get_random_agent_settings_female_teen():
    settings = get_random_agent_settings('agent_female_05')
    verify_agent_settings(settings)
    assert settings['isElder'] is False


def test_get_random_agent_settings_short_sleeves_male():
    settings = get_random_agent_settings(
        'agent_male_01',
        short_sleeves_only=True
    )
    assert settings['chest'] in [1, 3, 6]
    verify_agent_settings(settings)


def test_get_random_agent_settings_short_sleeves_female():
    settings = get_random_agent_settings(
        'agent_female_01',
        short_sleeves_only=True
    )
    assert settings['chest'] in [0, 1, 3, 5, 8]
    verify_agent_settings(settings)


def test_get_random_agent_settings_custom_settings():
    settings = get_random_agent_settings(
        'agent_male_01',
        settings={'chest': 1, 'skin': 3}
    )
    assert settings['chest'] == 1
    assert settings['skin'] == 3
    verify_agent_settings(settings)


def test_get_random_agent_settings_custom_settings_override():
    settings = get_random_agent_settings('agent_male_01', settings={
        'glasses': 1,
        'jacket': 1,
        'jacketMaterial': 1,
        'showBeard': True,
        'showGlasses': True,
        'showJacket': True,
        'showTie': True,
        'tie': 1,
        'tieMaterial': 1
    })
    assert settings['chest'] is not None
    assert settings['chestMaterial'] is not None
    assert settings['eyes'] is not None
    assert settings['feet'] is not None
    assert settings['feetMaterial'] is not None
    assert settings['hair'] is not None
    assert settings['hairMaterial'] is not None
    assert settings['hatMaterial'] is not None
    assert settings['legs'] is not None
    assert settings['legsMaterial'] is not None
    assert settings['skin'] is not None
    assert settings['hideHair'] in [True, False]
    assert settings['isElder'] in [True, False]
    assert settings['glasses'] == 1
    assert settings['jacket'] == 1
    assert settings['jacketMaterial'] == 1
    assert settings['tie'] == 1
    assert settings['tieMaterial'] == 1
    assert settings['showBeard'] is True
    assert settings['showGlasses'] is True
    assert settings['showJacket'] is True
    assert settings['showTie'] is True


def test_wall_materials():
    assert len(ROOM_WALL_MATERIALS)
    assert len(WALL_MATERIALS_DARK_SKIN)
    assert len(WALL_MATERIALS_LIGHT_SKIN)
    for wall_material in ROOM_WALL_MATERIALS:
        assert (
            wall_material in WALL_MATERIALS_DARK_SKIN or
            wall_material in WALL_MATERIALS_LIGHT_SKIN or
            wall_material in WALL_MATERIALS_NO_AGENTS
        )


def test_set_pointing_angle():
    assert set_pointing_angle(0, 0) == 0
    assert set_pointing_angle(0.6, 0) == 15
    assert set_pointing_angle(1.1, 0) == 30
    assert set_pointing_angle(1.6, 0) == 45
