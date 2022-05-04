from typing import List

import pytest
from machine_common_sense.config_manager import Vector3d

from generator.geometry import PERFORMER_HALF_WIDTH
from generator.scene import PartitionFloor, Scene
from ideal_learning_env import (
    ObjectRepository,
    ShortcutComponent,
    SpecificStructuralObjectsComponent,
)
from ideal_learning_env.defs import ILEException
from ideal_learning_env.shortcut_component import TripleDoorConfig

from .ile_helper import (
    prior_scene,
    prior_scene_custom_size,
    prior_scene_with_target,
)


def test_defaults():
    component = ShortcutComponent({})
    assert not component._delayed_perf_pos
    assert not component.shortcut_bisecting_platform
    assert not component.get_shortcut_bisecting_platform()
    assert not component.shortcut_start_on_platform
    assert not component.get_shortcut_start_on_platform()
    assert not component.shortcut_lava_room
    assert not component.get_shortcut_lava_room()
    assert not component.shortcut_agent_with_target
    assert not component.get_shortcut_agent_with_target()

    scene = component.update_ile_scene(prior_scene())
    assert scene.objects == []
    assert scene.floor_textures == []

    assert scene == prior_scene()


def test_shortcut_bisecting_platform_off():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': False
    })
    assert not component.shortcut_bisecting_platform
    assert not component.get_shortcut_bisecting_platform()
    scene = component.update_ile_scene(prior_scene())
    assert scene.objects == []

    assert scene == prior_scene()


def test_shortcut_bisecting_platform_on():
    # Note that this would have a blocking wall on default
    component = ShortcutComponent({
        'shortcut_bisecting_platform': True
    })
    assert component.shortcut_bisecting_platform
    assert component.get_shortcut_bisecting_platform()
    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    objs = scene.objects
    sizez = scene.room_dimensions.z
    assert isinstance(objs, List)
    assert len(objs) == 2
    obj = objs[0]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 0.5, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': sizez}

    obj = objs[1]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': .625, 'z': -sizez / 2.0 + 1.5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.99, 'y': 1.25, 'z': 0.1}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=1, z=-sizez / 2.0 + 0.5)


def test_shortcut_bisecting_platform_on_with_blocking_wall_prop():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': {
            'has_blocking_wall': True
        }
    })
    assert component.shortcut_bisecting_platform
    assert component.get_shortcut_bisecting_platform()
    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    objs = scene.objects
    sizez = scene.room_dimensions.z
    assert isinstance(objs, List)
    assert len(objs) == 2
    obj = objs[0]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 0.5, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': sizez}

    obj = objs[1]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': .625, 'z': -sizez / 2.0 + 1.5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.99, 'y': 1.25, 'z': 0.1}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=1, z=-sizez / 2.0 + 0.5)


def test_shortcut_bisecting_platform_on_no_blocking_wall():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': {
            'has_blocking_wall': False
        }
    })
    assert component.shortcut_bisecting_platform
    assert component.get_shortcut_bisecting_platform()
    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    objs = scene.objects
    sizez = scene.room_dimensions.z
    assert isinstance(objs, List)
    assert len(objs) == 1
    obj = objs[0]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 0.5, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': sizez}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=1, z=-sizez / 2.0 + 0.5)


def test_shortcut_triple_door_off():
    component = ShortcutComponent({
        'shortcut_triple_door_choice': False
    })
    assert not component.shortcut_bisecting_platform
    assert not component.get_shortcut_bisecting_platform()
    scene = component.update_ile_scene(prior_scene())
    assert scene.objects == []

    assert scene == prior_scene()


def test_shortcut_triple_door_on():
    component = ShortcutComponent({
        'shortcut_triple_door_choice': True
    })
    assert component.shortcut_triple_door_choice
    assert component.get_shortcut_triple_door_choice() == TripleDoorConfig()
    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    assert scene.room_dimensions.y == 5
    assert not scene.goal.get('action_list')
    assert scene.restrict_open_doors
    objs = scene.objects
    sizez = scene.room_dimensions.z
    assert isinstance(objs, List)
    assert len(objs) == 13

    obj = objs[0]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    assert obj['lips'] == {
        'back': False,
        'front': False,
        'left': True,
        'right': True,
        'gaps': {
            'left': [{'high': 0.5, 'low': 0}],
            'right': [{'high': 0.5, 'low': 0}]
        }
    }
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 1, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 2, 'z': sizez}

    obj = objs[1]
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 2, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[2]
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 4.125, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 0.25, 'z': 0.1}

    obj = objs[3]
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-0.46)
    assert pos['y'] == 3
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.08, 'y': 2, 'z': 0.1}

    obj = objs[4]
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(0.46)
    assert pos['y'] == 3
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.08, 'y': 2, 'z': 0.1}

    obj = objs[5]
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': 2.75, 'y': 0, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[6]
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 2.75, 'y': 3.125, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 4.5, 'y': 2.25, 'z': 0.1}

    obj = objs[7]
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(1.415)
    assert pos['y'] == 1
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1.83, 'y': 2, 'z': 0.1}

    obj = objs[8]
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(4.085)
    assert pos['y'] == 1
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1.83, 'y': 2, 'z': 0.1}

    obj = objs[9]
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': -2.75, 'y': 0, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[10]
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': -2.75, 'y': 3.125, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 4.5, 'y': 2.25, 'z': 0.1}

    obj = objs[11]
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-4.085)
    assert pos['y'] == 1
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1.83, 'y': 2, 'z': 0.1}

    obj = objs[12]
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    pos = show['position']
    assert pos['x'] == pytest.approx(-1.415)
    assert pos['y'] == 1
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1.83, 'y': 2, 'z': 0.1}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=2, z=-sizez / 2.0 + 0.5)


def test_shortcut_triple_door_drop_on_step_1():
    component = ShortcutComponent({
        'shortcut_triple_door_choice': {
            'start_drop_step': 1
        }
    })
    assert component.shortcut_triple_door_choice
    config = component.get_shortcut_triple_door_choice()
    assert isinstance(config, TripleDoorConfig)
    assert config.start_drop_step == 1
    scene = component.update_ile_scene(prior_scene())
    sizez = scene.room_dimensions.z
    assert scene != prior_scene()
    assert scene.room_dimensions.y == 5
    assert scene.goal['action_list'] == (
        [['Pass']] * (scene.room_dimensions.y * 4)
    )
    assert scene.restrict_open_doors
    objs = scene.objects
    assert isinstance(objs, List)
    assert len(objs) == 13

    obj = objs[0]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'

    move = {
        'stepBegin': 1,
        'stepEnd': 20,
        'vector': {'x': 0, 'y': -0.25, 'z': 0}
    }

    obj = objs[1]
    assert obj['id'].startswith('door')
    assert obj['moves'][0] == move

    obj = objs[2]
    assert obj['id'].startswith('wall')
    assert obj['moves'][0] == move

    obj = objs[3]
    assert obj['id'].startswith('wall')
    assert obj['moves'][0] == move

    obj = objs[4]
    assert obj['id'].startswith('wall')
    assert obj['moves'][0] == move

    obj = objs[5]
    assert obj['id'].startswith('door')
    assert obj['moves'][0] == move

    obj = objs[6]
    assert obj['id'].startswith('wall')
    assert obj['moves'][0] == move

    obj = objs[7]
    assert obj['id'].startswith('wall')
    assert obj['moves'][0] == move

    obj = objs[8]
    assert obj['id'].startswith('wall')
    assert obj['moves'][0] == move

    obj = objs[9]
    assert obj['id'].startswith('door')
    assert obj['moves'][0] == move

    obj = objs[10]
    assert obj['id'].startswith('wall')
    assert obj['moves'][0] == move

    obj = objs[11]
    assert obj['id'].startswith('wall')
    assert obj['moves'][0] == move

    obj = objs[12]
    assert obj['id'].startswith('wall')
    assert obj['moves'][0] == move

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=2, z=-sizez / 2.0 + 0.5)


def test_shortcut_triple_door_config():
    component = ShortcutComponent({
        'shortcut_triple_door_choice': {
            'add_freeze': False,
            'add_lips': False,
            'restrict_open_doors': False,
            'start_drop_step': 30,
            'door_material': 'AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
            'wall_material': 'AI2-THOR/Materials/Walls/DrywallGreen'
        }
    })
    assert component.shortcut_triple_door_choice
    config = component.get_shortcut_triple_door_choice()
    assert isinstance(config, TripleDoorConfig)
    assert not config.add_freeze
    assert not config.add_lips
    assert not config.restrict_open_doors
    assert config.start_drop_step == 30
    assert config.door_material == (
        'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')
    assert config.wall_material == 'AI2-THOR/Materials/Walls/DrywallGreen'
    scene = component.update_ile_scene(prior_scene())
    sizez = scene.room_dimensions.z
    assert scene != prior_scene()
    assert scene.room_dimensions.y == 5
    assert not scene.goal.get('action_list')
    assert not scene.restrict_open_doors
    objs = scene.objects
    assert isinstance(objs, List)
    assert len(objs) == 13

    obj = objs[0]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['lips'] == {
        'back': False,
        'front': False,
        'left': False,
        'right': False
    }

    move = {
        'stepBegin': 30,
        'stepEnd': 49,
        'vector': {'x': 0, 'y': -0.25, 'z': 0}
    }

    obj = objs[1]
    assert obj['id'].startswith('door')
    assert obj['shows'][0]['position']['y'] == 7
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')
    assert obj['moves'][0] == move

    obj = objs[2]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 9.125
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[3]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 8
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[4]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 8
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[5]
    assert obj['id'].startswith('door')
    assert obj['shows'][0]['position']['y'] == 5
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')
    assert obj['moves'][0] == move

    obj = objs[6]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 8.125
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[7]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 6
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[8]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 6
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[9]
    assert obj['id'].startswith('door')
    assert obj['shows'][0]['position']['y'] == 5
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')
    assert obj['moves'][0] == move

    obj = objs[10]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 8.125
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[11]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 6
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[12]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 6
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=2, z=-sizez / 2.0 + 0.5)


def test_shortcut_triple_door_with_extension():
    component = ShortcutComponent({
        'shortcut_triple_door_choice': {
            'add_extension': True,
            'start_drop_step': 30
        }
    })
    assert component.shortcut_triple_door_choice
    config = component.get_shortcut_triple_door_choice()
    assert isinstance(config, TripleDoorConfig)
    assert config.add_extension
    assert config.start_drop_step == 30

    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    assert scene.room_dimensions.y == 5
    assert scene.goal['action_list'] == (
        [['Pass']] * (scene.room_dimensions.y * 4 + 29)
    )
    assert scene.restrict_open_doors

    assert len(scene.objects) == 14

    room_dimensions = scene.room_dimensions

    extension = scene.objects[1]
    assert extension['id'].startswith('platform')
    assert extension['type'] == 'cube'
    assert extension['kinematic']
    assert extension['structure']
    show = extension['shows'][0]
    assert 0.5 < show['scale']['x'] <= (room_dimensions.x / 2.0 - 0.5)
    assert show['scale']['y'] == 2
    assert show['scale']['z'] == 1
    assert abs(show['position']['x']) == pytest.approx(0.5001 + (
        show['scale']['x'] / 2.0
    ))
    assert show['position']['y'] == 1
    assert 0.5 < show['position']['z'] <= (room_dimensions.z / 2.0 - 0.5)
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    is_left_side = (show['position']['x'] < 0)
    assert extension['lips'] == {
        'back': True,
        'front': True,
        'left': is_left_side,
        'right': not is_left_side
    }

    platform = scene.objects[0]
    assert platform['id'].startswith('platform')
    assert platform['type'] == 'cube'
    assert platform['kinematic']
    assert platform['structure']
    assert not platform['lips']['back']
    assert not platform['lips']['front']
    assert platform['lips']['left']
    assert platform['lips']['right']
    high = 0.5 + (show['position']['z'] + 0.5) / room_dimensions.z
    low = 0.5 + (show['position']['z'] - 0.5) / room_dimensions.z
    if is_left_side:
        assert platform['lips']['gaps']['left'] == [
            {'high': 0.5, 'low': 0},
            {'high': high, 'low': low}
        ]
        assert platform['lips']['gaps']['right'] == [{'high': 0.5, 'low': 0}]
    else:
        assert platform['lips']['gaps']['right'] == [
            {'high': 0.5, 'low': 0},
            {'high': high, 'low': low}
        ]
        assert platform['lips']['gaps']['left'] == [{'high': 0.5, 'low': 0}]
    show = platform['shows'][0]
    assert show['position'] == {'x': 0, 'y': 1, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 2, 'z': scene.room_dimensions.z}


def test_shortcut_triple_door_with_bigger_far_end():
    component = ShortcutComponent({
        'shortcut_triple_door_choice': {
            'bigger_far_end': True,
            'start_drop_step': 30
        }
    })
    assert component.shortcut_triple_door_choice
    config = component.get_shortcut_triple_door_choice()
    assert isinstance(config, TripleDoorConfig)
    assert config.bigger_far_end
    assert config.start_drop_step == 30

    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    assert scene.room_dimensions.y == 5
    assert scene.goal['action_list'] == (
        [['Pass']] * (scene.room_dimensions.y * 4 + 29)
    )
    assert scene.restrict_open_doors

    assert len(scene.objects) == 14

    room_dimensions = scene.room_dimensions

    bigger = scene.objects[1]
    assert bigger['id'].startswith('platform')
    assert bigger['type'] == 'cube'
    assert bigger['kinematic']
    assert bigger['structure']
    show = bigger['shows'][0]
    assert show['scale']['x'] == 2
    assert show['scale']['y'] == 2.25
    assert show['scale']['z'] == (room_dimensions.z / 2.0)
    assert show['position']['x'] == 0
    assert show['position']['y'] == 1.125
    assert show['position']['z'] == (room_dimensions.z / 4.0)
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert not bigger['lips']['back']
    assert not bigger['lips']['front']
    assert not bigger['lips']['left']
    assert not bigger['lips']['right']

    platform = scene.objects[0]
    assert platform['id'].startswith('platform')
    assert platform['type'] == 'cube'
    assert platform['kinematic']
    assert platform['structure']
    assert not platform['lips']['back']
    assert not platform['lips']['front']
    assert not platform['lips']['left']
    assert not platform['lips']['right']
    show = platform['shows'][0]
    assert show['position'] == {'x': 0, 'y': 1, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 2, 'z': scene.room_dimensions.z}


def test_shortcut_start_on_platform_off():
    component = ShortcutComponent({
        'shortcut_start_on_platform': False
    })
    assert not component.shortcut_start_on_platform
    assert not component.get_shortcut_start_on_platform()
    scene = component.update_ile_scene(prior_scene())

    assert scene == prior_scene()

    assert not component._delayed_perf_pos
    assert scene.objects == []
    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d()


def test_shortcut_start_on_platform_on():
    component = ShortcutComponent({
        'shortcut_start_on_platform': True

    })
    assert component.shortcut_start_on_platform
    assert component.get_shortcut_start_on_platform()
    scene = component.update_ile_scene(prior_scene())

    p_scene = prior_scene()
    assert scene != p_scene

    assert component._delayed_perf_pos

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=10, y=0, z=10)


def test_start_position_delayed():
    label = "start_structure"
    scene = prior_scene()
    scene.room_dimensions.y = 10

    data = {
        "structural_platforms": {
            "num": 1,
            "labels": label
        },
        "shortcut_start_on_platform": True
    }

    component = ShortcutComponent(data)

    scene = component.update_ile_scene(scene)
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 0
    assert component._delayed_perf_pos
    assert component.get_num_delayed_actions() == 1

    struct_obj_comp = SpecificStructuralObjectsComponent(data)
    scene = struct_obj_comp.update_ile_scene(scene)
    assert len(objects) == 1

    scene = component.run_delayed_actions(scene)
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 1
    component.get_num_delayed_actions() == 0
    assert not component._delayed_perf_pos
    assert objects[0]['type'] == "cube"
    assert ObjectRepository.get_instance().has_label(label)

    perf_pos = scene.performer_start.position
    platform_pos = objects[0]['shows'][0]['position']
    platform_scale = objects[0]['shows'][0]['scale']

    padding = 0.1 + PERFORMER_HALF_WIDTH
    min_x = platform_pos['x'] - (
        (platform_scale['x'] / 2) +
        (padding)
    )
    max_x = platform_pos['x'] + (
        (platform_scale['x'] / 2) +
        (padding)
    )
    min_z = platform_pos['z'] - (
        (platform_scale['z'] / 2) +
        (padding)
    )
    max_z = platform_pos['z'] + (
        (platform_scale['z'] / 2) +
        (padding)
    )

    assert min_x <= perf_pos.x <= max_x
    assert perf_pos.y == platform_scale['y']
    assert min_z <= perf_pos.z <= max_z


def test_start_on_platform_no_auto_adjust():
    ObjectRepository.get_instance().clear()
    label = "start_structure"
    scene = prior_scene_custom_size(10, 10)
    scene.room_dimensions.y = 4

    data = {
        "structural_platforms": {
            "num": 1,
            "labels": label,
            "scale": 3.5
        },
        "shortcut_start_on_platform": True
    }

    component = ShortcutComponent(data)

    scene = component.update_ile_scene(scene)
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 0
    assert component._delayed_perf_pos
    assert component.get_num_delayed_actions() == 1

    struct_obj_comp = SpecificStructuralObjectsComponent(data)
    scene = struct_obj_comp.update_ile_scene(scene)
    assert len(objects) == 1

    assert component._delayed_perf_pos_reason is None
    scene = component.run_delayed_actions(scene)
    error = ILEException(message="Attempt to position performer on chosen " +
                         "platform failed. Unable to place performer on " +
                         "platform with '" + label + "' label.")
    assert isinstance(component._delayed_perf_pos_reason, ILEException)
    assert str(component._delayed_perf_pos_reason) == str(error)


def test_start_on_platform_auto_adjust():
    ObjectRepository.get_instance().clear()
    label = "start_structure"
    scene = prior_scene_custom_size(10, 10)
    scene.room_dimensions.y = 5

    data = {
        "structural_platforms": {
            "num": 1,
            "labels": label,
            "position": {
                "x": 0,
                "y": 0,
                "z": 0
            },
            "scale": {
                "x": 4.9,
                "y": 4.9,
                "z": 4.9
            },
            "auto_adjust_platforms": True
        },
        "shortcut_start_on_platform": True
    }

    component = ShortcutComponent(data)

    scene = component.update_ile_scene(scene)
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 0
    assert component._delayed_perf_pos
    assert component.get_num_delayed_actions() == 1

    struct_obj_comp = SpecificStructuralObjectsComponent(data)
    scene = struct_obj_comp.update_ile_scene(scene)
    assert len(objects) == 1

    scene = component.run_delayed_actions(scene)
    objects = scene.objects
    assert isinstance(objects, list)
    assert len(objects) == 1
    component.get_num_delayed_actions() == 0
    assert not component._delayed_perf_pos
    assert objects[0]['type'] == "cube"
    assert ObjectRepository.get_instance().has_label(label)

    perf_pos = scene.performer_start.position
    platform_pos = objects[0]['shows'][0]['position']
    platform_scale = objects[0]['shows'][0]['scale']

    padding = 0.1 + PERFORMER_HALF_WIDTH
    min_x = platform_pos['x'] - (
        (platform_scale['x'] / 2) +
        (padding)
    )
    max_x = platform_pos['x'] + (
        (platform_scale['x'] / 2) +
        (padding)
    )
    min_z = platform_pos['z'] - (
        (platform_scale['z'] / 2) +
        (padding)
    )
    max_z = platform_pos['z'] + (
        (platform_scale['z'] / 2) +
        (padding)
    )

    assert min_x <= perf_pos.x <= max_x
    assert perf_pos.y == 3.75
    assert min_z <= perf_pos.z <= max_z


def test_shortcut_lava_room_off():
    component = ShortcutComponent({
        'shortcut_lava_room': False
    })
    assert not component.shortcut_lava_room
    assert not component.get_shortcut_lava_room()
    scene: Scene = component.update_ile_scene(prior_scene())
    assert scene.floor_textures == []
    assert not scene.lava
    assert not scene.partition_floor

    assert scene == prior_scene()


def test_shortcut_lava_room_on_room():
    x_size = 3
    z_size = 3
    component = ShortcutComponent({
        'shortcut_lava_room': True
    })
    assert component.shortcut_lava_room
    assert component.get_shortcut_lava_room()
    scene = component.update_ile_scene(prior_scene_custom_size(x_size,
                                                               z_size))
    assert scene != prior_scene_custom_size(x_size, z_size)

    assert not scene.lava
    assert scene.partition_floor
    assert scene.partition_floor == PartitionFloor(
        leftHalf=2 / 3, rightHalf=2 / 3)

    perf_pos = scene.performer_start.position
    perf_rot_y = scene.performer_start.rotation.y
    assert perf_pos == Vector3d(x=0, y=0, z=-1 * (z_size / 2.0) + 0.5)
    assert perf_rot_y >= -90
    assert perf_rot_y <= 90


def test_shortcut_lava_island_too_small():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': True
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(6, 15)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    scene = prior_scene_custom_size(15, 6)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    scene = prior_scene_custom_size(12, 7)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    scene = prior_scene_custom_size(7, 12)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    scene = prior_scene_custom_size(5, 5)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)


def test_shortcut_lava_island_min_size():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': True
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(7, 13)
    scene_switched = prior_scene_custom_size(13, 7)

    scene = component.update_ile_scene(scene)
    scene_switched = component.update_ile_scene(scene_switched)
    lavas = scene.lava
    lavas_switched = scene_switched.lava
    assert len(lavas) == 24
    for x in range(-2, 3):
        for z in range(1, 6):
            if x != 0 and z != 4:
                assert {'x': x, 'z': z} in lavas
                assert {'x': z, 'z': x} in lavas_switched

    objs = scene.objects
    assert len(objs) == 2
    target = objs[0]
    tool = objs[1]
    pos = target['shows'][0]['position']
    assert pos['x'] == 0
    assert pos["z"] == 3
    pos = tool['shows'][0]['position']
    rot_y = tool['shows'][0]['rotation']['y']
    assert pos == {'x': 0, "y": 0.15, "z": -3}
    assert rot_y == 0

    switched_target_pos = scene_switched.objects[0]['shows'][0]['position']
    switched_tool_show = scene_switched.objects[1]['shows'][0]
    pos = switched_tool_show['position']
    rot_y = switched_tool_show['rotation']['y']
    assert switched_target_pos['x'] == 3
    assert switched_target_pos['z'] == 0

    assert pos == {'x': -3, "y": 0.15, "z": 0}
    assert rot_y == 90


def test_shortcut_lava_island_min_size_plus_one():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': True
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(8, 14)
    scene_switched = prior_scene_custom_size(14, 8)

    scene = component.update_ile_scene(scene)
    scene_switched = component.update_ile_scene(scene_switched)
    lavas = scene.lava
    lavas_switched = scene_switched.lava
    assert len(lavas) == 24
    for x in range(-2, 3):
        for z in range(1, 6):
            if x != 0 and z != 4:
                assert {'x': x, 'z': z} in lavas
                assert {'x': z, 'z': x} in lavas_switched

    objs = scene.objects
    assert len(objs) == 2
    target = objs[0]
    tool = objs[1]
    pos = target['shows'][0]['position']
    assert pos['x'] == 0
    assert pos["z"] == 3
    pos = tool['shows'][0]['position']
    rot_y = tool['shows'][0]['rotation']['y']
    assert pos == {'x': 0, "y": 0.15, "z": -3}
    assert rot_y == 0

    switched_target_pos = scene_switched.objects[0]['shows'][0]['position']
    switched_tool_show = scene_switched.objects[1]['shows'][0]
    pos = switched_tool_show['position']
    rot_y = switched_tool_show['rotation']['y']
    assert switched_target_pos['x'] == 3
    assert switched_target_pos['z'] == 0

    assert pos == {'x': -3, "y": 0.15, "z": 0}
    assert rot_y == 90


def test_shortcut_lava_island_big_room():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': True
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(25, 25)
    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    assert len(lavas) >= 24

    objs = scene.objects
    assert len(objs) == 2
    target = objs[0]
    tool = objs[1]
    target_pos = target['shows'][0]['position']
    tool_pos = tool['shows'][0]['position']

    if target_pos['x'] in [0, 0.5]:
        assert tool_pos['x'] in [0, 0.5]
        assert tool['shows'][0]['rotation']['y'] == 0
    else:
        assert target_pos['z'] in [0, 0.5]
        assert tool_pos['z'] in [0, 0.5]
        assert tool['shows'][0]['rotation']['y'] == 90

    assert target['type'] == 'soccer_ball'
    assert target['moveable']
    assert target['pickupable']

    assert tool['type'].startswith('tool_rect')


def test_shortcut_lava_island_guide_rail():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'guide_rails': True
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(7, 13)
    scene_switched = prior_scene_custom_size(13, 7)

    scene = component.update_ile_scene(scene)
    scene_switched = component.update_ile_scene(scene_switched)
    lavas = scene.lava
    lavas_switched = scene_switched.lava
    assert len(lavas) == 24
    for x in range(-2, 3):
        for z in range(1, 6):
            if x != 0 and z != 4:
                assert {'x': x, 'z': z} in lavas
                assert {'x': z, 'z': x} in lavas_switched

    objs = scene.objects
    assert len(objs) == 4
    assert len(scene_switched.objects) == 4
    target = objs[0]
    tool = objs[1]
    tool_type = tool['type']
    assert tool_type in [
        'tool_rect_1_00_x_5_00',
        'tool_rect_0_50_x_5_00',
        'tool_rect_0_75_x_5_00']
    pos = target['shows'][0]['position']
    assert pos['x'] == 0
    assert pos['y'] >= 0
    assert pos["z"] == 3
    pos = tool['shows'][0]['position']
    rot_y = tool['shows'][0]['rotation']['y']
    assert pos == {'x': 0, "y": 0.15, "z": -3}
    assert rot_y == 0

    switched_target_pos = scene_switched.objects[0]['shows'][0]['position']
    switched_tool_show = scene_switched.objects[1]['shows'][0]
    pos = switched_tool_show['position']
    rot_y = switched_tool_show['rotation']['y']

    assert switched_target_pos['x'] == 3
    assert switched_target_pos['y'] >= 0
    assert switched_target_pos["z"] == 0

    assert pos == {'x': -3, "y": 0.15, "z": 0}
    assert rot_y == 90

    rail1 = objs[2]
    rail2 = objs[3]

    assert rail1['id'].startswith('guide_rail')
    assert rail1['type'] == 'cube'
    assert rail1['structure']
    assert rail1['kinematic']
    show = rail1['shows'][0]
    pos1 = show['position']
    scale1 = show['scale']

    assert rail2['id'].startswith('guide_rail')
    assert rail2['type'] == 'cube'
    assert rail2['structure']
    assert rail2['kinematic']
    show = rail2['shows'][0]
    pos2 = show['position']
    scale2 = show['scale']

    assert scale1 == {'x': 0.2, 'y': 0.2, 'z': 8.5}
    assert scale2 == {'x': 0.2, 'y': 0.2, 'z': 8.5}

    # depends on width of tool
    assert pos1 in [
        {'x': 0.7, 'y': 0.1, 'z': -1.25},
        {'x': 0.575, 'y': 0.1, 'z': -1.25},
        {'x': 0.45, 'y': 0.1, 'z': -1.25}]
    assert pos2 in [
        {'x': -0.7, 'y': 0.1, 'z': -1.25},
        {'x': -0.575, 'y': 0.1, 'z': -1.25},
        {'x': -0.45, 'y': 0.1, 'z': -1.25}]

    assert rail1['materials'] == rail2['materials']


def test_shortcut_lava_island_rotate_tool_z():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'tool_rotation': 35
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(7, 21)
    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    assert len(lavas) >= 24

    objs = scene.objects
    assert len(objs) == 2
    tool = objs[1]

    assert tool['type'].startswith('tool_rect')
    assert tool['shows'][0]['rotation']['y'] == 35


def test_shortcut_lava_island_rotate_tool_x():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'tool_rotation': [55, 135]
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()

    scene = prior_scene_custom_size(21, 7)
    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    assert len(lavas) >= 24

    objs = scene.objects
    assert len(objs) == 2
    tool = objs[1]

    assert tool['type'].startswith('tool_rect')
    assert tool['shows'][0]['rotation']['y'] in [145, 225]


def test_shortcut_lava_island_rotate_random_start():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'random_performer_position': True
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()

    scene = prior_scene_custom_size(21, 10)
    scene = component.update_ile_scene(scene)
    assert (scene.performer_start.position.x !=
            -10 or scene.performer_start.position.z not in [0, 0.5])

    scene = prior_scene_custom_size(10, 21)
    scene = component.update_ile_scene(scene)
    assert (scene.performer_start.position.x not in
            [0, 0.5] or scene.performer_start.position.z != -10)


def test_shortcut_lava_island_rails_and_rotation_fail():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'tool_rotation': {
                'min': 5,
                'max': 39
            },
            'guide_rails': True
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()

    scene = prior_scene_custom_size(21, 7)
    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_shortcut_lava_island_rails():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'guide_rails': True
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()

    scene = prior_scene_custom_size(21, 8)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    assert len(objs) == 4
    tgt = scene.objects[0]
    # lets make sure the target is moved
    show = tgt['shows'][0]
    pos = show['position']
    assert tgt['type'] == 'soccer_ball'
    assert pos['z'] in [0, 0.5]
    assert pos['x'] > 2
    assert objs[1]['type'].startswith('tool_rect_')
    assert objs[2]['type'] == 'cube'
    assert objs[3]['type'] == 'cube'


def test_shortcut_lava_island_rails_with_existing_target():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'guide_rails': True
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()

    scene = prior_scene_with_target(21, 8)
    scene = component.update_ile_scene(scene)
    tgt = scene.objects[0]
    # lets make sure the target is moved
    show = tgt['shows'][0]
    pos = show['position']
    assert tgt['type'] == 'soccer_ball'
    assert pos['z'] in [0, 0.5]
    assert pos['x'] > 2


def test_shortcut_lava_island_random_target_position():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'random_target_position': True
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.random_target_position
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(7, 13)
    scene_switched = prior_scene_custom_size(13, 7)

    scene = component.update_ile_scene(scene)
    scene_switched = component.update_ile_scene(scene_switched)
    lavas = scene.lava
    lavas_switched = scene_switched.lava
    assert len(lavas) == 24
    for x in range(-2, 3):
        for z in range(1, 6):
            if x != 0 and z != 4:
                assert {'x': x, 'z': z} in lavas
                assert {'x': z, 'z': x} in lavas_switched

    objs = scene.objects
    assert len(objs) == 2
    tool = objs[0]
    target = objs[1]
    pos = target['shows'][0]['position']
    # Ensure that the target is not positioned on the island.
    assert not (pos['x'] == 0 and pos["z"] == 3)
    pos = tool['shows'][0]['position']
    rot_y = tool['shows'][0]['rotation']['y']
    assert pos == {'x': 0, "y": 0.15, "z": -3}
    assert rot_y == 0

    switched_tool_show = scene_switched.objects[0]['shows'][0]
    switched_target_pos = scene_switched.objects[1]['shows'][0]['position']
    pos = switched_tool_show['position']
    rot_y = switched_tool_show['rotation']['y']
    # Ensure that the target is not positioned on the island.
    assert not (
        switched_target_pos['x'] == 3 and switched_target_pos['z'] == 0
    )
    assert pos == {'x': -3, "y": 0.15, "z": 0}
    assert rot_y == 90


def test_shortcut_agent_with_target_off():
    component = ShortcutComponent({
        'shortcut_agent_with_target': False
    })
    assert not component.shortcut_agent_with_target
    assert not component.get_shortcut_agent_with_target()
    scene = component.update_ile_scene(prior_scene())
    assert scene.objects == []

    assert scene == prior_scene()


def test_shortcut_agent_with_target_on_agent_no_target():
    component = ShortcutComponent({
        'shortcut_agent_with_target': True
    })
    assert component.shortcut_agent_with_target
    assert component.get_shortcut_agent_with_target()
    scene = component.update_ile_scene(prior_scene())
    assert len(scene.objects) == 2
    target = scene.objects[1]
    agent = scene.objects[0]
    assert target['id']
    assert target['type'] == 'soccer_ball'
    assert target['associatedWithAgent'] == agent['id']
    assert target['shows'][0]['boundingBox'].max_y == 0
    assert target['shows'][0]['boundingBox'].min_y == 0
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert target['moveable']
    assert target['pickupable']
    assert agent['id'].startswith("agent")
    assert agent['agentSettings']


def test_shortcut_agent_with_target_on_with_agent():
    component = ShortcutComponent({
        'shortcut_agent_with_target': True
    })
    assert component.shortcut_agent_with_target
    assert component.get_shortcut_agent_with_target()
    scene = component.update_ile_scene(prior_scene_with_target())
    assert len(scene.objects) == 2
    target = scene.objects[0]
    agent = scene.objects[1]
    assert target['id']
    assert target['type'] == 'soccer_ball'
    assert target['associatedWithAgent'] == agent['id']
    assert target['shows'][0]['boundingBox'].max_y == 0
    assert target['shows'][0]['boundingBox'].min_y == 0
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert target['moveable']
    assert target['pickupable']
    assert agent['id'].startswith("agent")
    assert agent['agentSettings']


def test_shortcut_agent_with_target_with_position():
    component = ShortcutComponent({
        'shortcut_agent_with_target': {
            'agent_position': {'x': 1, 'y': 2, 'z': 3}
        }
    })
    scene = prior_scene_with_target()
    scene.room_dimensions.y = 10
    assert component.shortcut_agent_with_target
    assert component.get_shortcut_agent_with_target()
    scene = component.update_ile_scene(scene)
    assert len(scene.objects) == 2
    target = scene.objects[0]
    agent = scene.objects[1]
    assert target['id']
    assert target['type'] == 'soccer_ball'
    assert target['associatedWithAgent'] == agent['id']
    assert target['shows'][0]['boundingBox'].max_y == 0
    assert target['shows'][0]['boundingBox'].min_y == 0
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert target['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert target['moveable']
    assert target['pickupable']
    assert agent['id'].startswith("agent")
    assert agent['agentSettings']
    assert agent['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}


def test_shortcut_agent_with_target_with_no_bounds():
    component = ShortcutComponent({
        'shortcut_agent_with_target': {
            'movement_bounds': []
        }
    })
    assert component.shortcut_agent_with_target
    assert component.get_shortcut_agent_with_target()
    scene = component.update_ile_scene(
        prior_scene_with_target(
            size_x=3, size_z=3))
    assert len(scene.objects) == 2
    target = scene.objects[0]
    agent = scene.objects[1]
    assert target['id']
    assert target['type'] == 'soccer_ball'
    assert target['associatedWithAgent'] == agent['id']
    assert target['shows'][0]['boundingBox'].max_y == 0
    assert target['shows'][0]['boundingBox'].min_y == 0
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert target['shows'][0]['position']
    assert target['moveable']
    assert target['pickupable']
    assert agent['id'].startswith("agent")
    assert agent['agentSettings']
    assert agent['agentMovement']
    seq = agent['agentMovement']['sequence']
    for movement_item in seq:
        point = movement_item['endPoint']
        assert -3 < point['x'] < 3
        assert -3 < point['z'] < 3


def test_shortcut_agent_with_target_with_line_bounds_means_no_bounds():
    component = ShortcutComponent({
        'shortcut_agent_with_target': {
            'movement_bounds': [
                {'x': 1, 'z': 1},
                {'x': 1, 'z': 1.1}
            ]
        }
    })
    assert component.shortcut_agent_with_target
    assert component.get_shortcut_agent_with_target()
    scene = component.update_ile_scene(
        prior_scene_with_target(
            size_x=3, size_z=3))
    assert len(scene.objects) == 2
    target = scene.objects[0]
    agent = scene.objects[1]
    assert target['id']
    assert target['type'] == 'soccer_ball'
    assert target['associatedWithAgent'] == agent['id']
    assert target['shows'][0]['boundingBox'].max_y == 0
    assert target['shows'][0]['boundingBox'].min_y == 0
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert target['shows'][0]['position']
    assert target['moveable']
    assert target['pickupable']
    assert agent['id'].startswith("agent")
    assert agent['agentSettings']
    assert not hasattr(agent, 'agentMovement')


def test_shortcut_agent_with_target_with_bounds():
    component = ShortcutComponent({
        'shortcut_agent_with_target': {
            'movement_bounds': [
                {'x': 2, 'z': 1},
                {'x': 2, 'z': 2},
                {'x': 4, 'z': 2},
                {'x': 4, 'z': 1}
            ]
        }
    })
    assert component.shortcut_agent_with_target
    assert component.get_shortcut_agent_with_target()
    scene = component.update_ile_scene(prior_scene_with_target())
    assert len(scene.objects) == 2
    target = scene.objects[0]
    agent = scene.objects[1]
    assert target['id']
    assert target['type'] == 'soccer_ball'
    assert target['associatedWithAgent'] == agent['id']
    assert target['shows'][0]['boundingBox'].max_y == 0
    assert target['shows'][0]['boundingBox'].min_y == 0
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert target['shows'][0]['position']
    assert target['moveable']
    assert target['pickupable']
    assert agent['id'].startswith("agent")
    assert agent['agentSettings']
    assert agent['shows'][0]['position']
    assert agent['agentMovement']
    seq = agent['agentMovement']['sequence']
    for movement_item in seq:
        point = movement_item['endPoint']
        assert 2 < point['x'] < 4
        assert 1 < point['z'] < 2


def test_shortcut_agent_with_target_with_bounds_location_choice():
    component = ShortcutComponent({
        "shortcut_agent_with_target": [{
            "agent_position": {
                "x": 1.5,
                "z": 1.5
            },
            "movement_bounds": [{
                "x": 1,
                "z": 2
            }, {
                "x": 2,
                "z": 2
            }, {
                "x": 2,
                "z": 1
            }, {
                "x": 1,
                "z": 1
            }]
        },
            {
            "agent_position": {
                "x": -1.5,
                "z": -1.5
            },
            "movement_bounds": [{
                "x": -1,
                "z": -2
            }, {
                "x": -2,
                "z": -2
            }, {
                "x": -2,
                "z": -1
            }, {
                "x": -1,
                "z": -1
            }]
        }]
    })
    assert component.shortcut_agent_with_target
    assert isinstance(component.shortcut_agent_with_target, List)
    assert component.get_shortcut_agent_with_target()
    assert not isinstance(component.get_shortcut_agent_with_target(), List)
    scene = component.update_ile_scene(prior_scene_with_target())
    assert len(scene.objects) == 2
    target = scene.objects[0]
    agent = scene.objects[1]
    assert target['id']
    assert target['type'] == 'soccer_ball'
    assert target['associatedWithAgent'] == agent['id']
    assert target['shows'][0]['boundingBox'].max_y == 0
    assert target['shows'][0]['boundingBox'].min_y == 0
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert target['shows'][0]['position']
    assert target['moveable']
    assert target['pickupable']
    assert agent['id'].startswith("agent")
    assert agent['agentSettings']
    pos = agent['shows'][0]['position']
    assert agent['agentMovement']
    seq = agent['agentMovement']['sequence']
    if pos['x'] > 0:
        assert pos['x'] == 1.5
        assert pos['z'] == 1.5
    else:
        assert pos['x'] == -1.5
        assert pos['z'] == -1.5
    for movement_item in seq:
        point = movement_item['endPoint']
        if pos['x'] > 0:
            assert 1 < point['x'] < 2
            assert 1 < point['z'] < 2
        else:
            assert -2 < point['x'] < -1
            assert -2 < point['z'] < -1
