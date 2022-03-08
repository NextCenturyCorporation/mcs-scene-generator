from typing import List

import pytest

from generator.geometry import PERFORMER_HALF_WIDTH
from ideal_learning_env import (
    ObjectRepository,
    ShortcutComponent,
    SpecificStructuralObjectsComponent,
)
from ideal_learning_env.defs import ILEException
from ideal_learning_env.shortcut_component import TripleDoorConfig


def prior_scene():
    return {'debug': {}, 'goal': {}, 'performerStart':
            {'position':
             {'x': 0, 'y': 0, 'z': 0},
             'rotation':
             {'x': 0, 'y': 0, 'z': 0}},
            'roomDimensions': {'x': 10, 'y': 3, 'z': 10}}


def prior_scene_custom_size(x, z):
    return {'debug': {}, 'goal': {}, 'performerStart':
            {'position':
             {'x': 0, 'y': 0, 'z': 0},
             'rotation':
             {'x': 0, 'y': 0, 'z': 0}},
            'roomDimensions': {'x': x, 'y': 3, 'z': z}}


def test_defaults():
    component = ShortcutComponent({})
    assert not component._delayed_perf_pos
    assert not component.shortcut_bisecting_platform
    assert not component.get_shortcut_bisecting_platform()
    assert not component.shortcut_ramp_to_platform
    assert not component.get_shortcut_ramp_to_platform()
    assert not component.shortcut_start_on_platform
    assert not component.get_shortcut_start_on_platform()
    assert not component.shortcut_lava_room
    assert not component.get_shortcut_lava_room()
    scene = component.update_ile_scene(prior_scene())
    assert 'objects' not in scene
    assert 'floorTextures' not in scene

    assert scene == prior_scene()


def test_shortcut_bisecting_platform_off():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': False
    })
    assert not component.shortcut_bisecting_platform
    assert not component.get_shortcut_bisecting_platform()
    scene = component.update_ile_scene(prior_scene())
    assert 'objects' not in scene

    assert scene == prior_scene()


def test_shortcut_bisecting_platform_on():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': True
    })
    assert component.shortcut_bisecting_platform
    assert component.get_shortcut_bisecting_platform()
    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    assert 'objects' in scene
    objs = scene['objects']
    sizez = scene['roomDimensions']['z']
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

    perf_pos = scene['performerStart']['position']
    assert perf_pos == {'x': 0, 'y': 1, 'z': -sizez / 2.0 + 0.5}


def test_shortcut_triple_door_off():
    component = ShortcutComponent({
        'shortcut_triple_door_choice': False
    })
    assert not component.shortcut_bisecting_platform
    assert not component.get_shortcut_bisecting_platform()
    scene = component.update_ile_scene(prior_scene())
    assert 'objects' not in scene

    assert scene == prior_scene()


def test_shortcut_triple_door_on():
    component = ShortcutComponent({
        'shortcut_triple_door_choice': True
    })
    assert component.shortcut_triple_door_choice
    assert component.get_shortcut_triple_door_choice() == TripleDoorConfig()
    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    assert 'objects' in scene
    objs = scene['objects']
    sizez = scene['roomDimensions']['z']
    assert isinstance(objs, List)
    assert len(objs) == 13
    obj = objs[0]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
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

    perf_pos = scene['performerStart']['position']
    assert perf_pos == {'x': 0, 'y': 2, 'z': -sizez / 2.0 + 0.5}


def test_shortcut_triple_door_config():
    component = ShortcutComponent({
        'shortcut_triple_door_choice': {
            'start_drop_step': 3,
            'door_material': 'AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
            'wall_material': 'AI2-THOR/Materials/Walls/DrywallGreen'
        }
    })
    assert component.shortcut_triple_door_choice
    config = component.get_shortcut_triple_door_choice()
    assert isinstance(config, TripleDoorConfig)
    assert config.start_drop_step == 3
    assert config.door_material == (
        'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')
    assert config.wall_material == 'AI2-THOR/Materials/Walls/DrywallGreen'
    scene = component.update_ile_scene(prior_scene())
    sizez = scene['roomDimensions']['z']
    assert scene != prior_scene()
    assert 'objects' in scene
    objs = scene['objects']
    assert isinstance(objs, List)
    assert len(objs) == 13
    obj = objs[0]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'

    move = {
        'stepBegin': 3,
        'stepEnd': 14,
        'vector': {'x': 0, 'y': -0.25, 'z': 0}
    }

    obj = objs[1]
    assert obj['id'].startswith('door')
    assert obj['shows'][0]['position']['y'] == 5
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')
    assert obj['moves'][0] == move

    obj = objs[2]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 7.125
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[3]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 6
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[4]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 6
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[5]
    assert obj['id'].startswith('door')
    assert obj['shows'][0]['position']['y'] == 3
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')
    assert obj['moves'][0] == move

    obj = objs[6]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 6.125
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[7]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 4
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[8]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 4
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[9]
    assert obj['id'].startswith('door')
    assert obj['shows'][0]['position']['y'] == 3
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')
    assert obj['moves'][0] == move

    obj = objs[10]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 6.125
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[11]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 4
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    obj = objs[12]
    assert obj['id'].startswith('wall')
    assert obj['shows'][0]['position']['y'] == 4
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Walls/DrywallGreen')
    assert obj['moves'][0] == move

    perf_pos = scene['performerStart']['position']
    assert perf_pos == {'x': 0, 'y': 2, 'z': -sizez / 2.0 + 0.5}


def test_shortcut_start_on_platform_off():
    component = ShortcutComponent({
        'shortcut_start_on_platform': False
    })
    assert not component.shortcut_start_on_platform
    assert not component.get_shortcut_start_on_platform()
    scene = component.update_ile_scene(prior_scene())

    assert scene == prior_scene()

    assert not component._delayed_perf_pos
    assert 'objects' not in scene
    perf_pos = scene['performerStart']['position']
    assert perf_pos == {'x': 0, 'y': 0, 'z': 0}


def test_shortcut_start_on_platform_on():
    component = ShortcutComponent({
        'shortcut_start_on_platform': True
    })
    assert not component.shortcut_ramp_to_platform
    assert not component.get_shortcut_ramp_to_platform()
    assert component.shortcut_start_on_platform
    assert component.get_shortcut_start_on_platform()
    scene = component.update_ile_scene(prior_scene())

    assert scene != prior_scene()

    assert component._delayed_perf_pos
    assert 'objects' in scene
    perf_pos = scene['performerStart']['position']
    assert perf_pos == {'x': 10, 'y': 0, 'z': 10}


def test_shortcut_ramp_to_platform_off():
    component = ShortcutComponent({
        'shortcut_ramp_to_platform': False
    })
    assert not component.shortcut_ramp_to_platform
    assert not component.get_shortcut_ramp_to_platform()
    scene = component.update_ile_scene(prior_scene())
    assert 'objects' not in scene

    assert scene == prior_scene()


def test_shortcut_ramp_to_platform_on():
    component = ShortcutComponent({
        'shortcut_ramp_to_platform': True
    })
    assert component.shortcut_ramp_to_platform
    assert component.get_shortcut_ramp_to_platform()
    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    assert 'objects' in scene
    objs = scene['objects']
    sizey = scene['roomDimensions']['y']
    assert isinstance(objs, List)
    assert len(objs) == 2
    obj = objs[0]
    assert obj['id'].startswith('ramp')
    assert obj['type'] == 'triangle'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    r_rot_y = show['rotation']['y']

    obj = objs[1]
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    assert objs[0]['materials'] == objs[1]['materials']
    show = obj['shows'][0]
    assert show['rotation']['y'] == r_rot_y
    assert 1 <= show['scale']['y'] <= sizey - 1.0
    assert ObjectRepository.get_instance().has_label('platform_next_to_ramp')
    assert ObjectRepository.get_instance().has_label('ramp_next_to_platform')


def test_start_position_delayed():
    label = "start_structure"
    scene = prior_scene()

    data = {
        "structural_platforms": {
            "num": 1,
            "labels": label
        },
        "shortcut_start_on_platform": True
    }

    component = ShortcutComponent(data)

    scene = component.update_ile_scene(scene)
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 0
    assert component._delayed_perf_pos
    assert component.get_num_delayed_actions() == 1

    struct_obj_comp = SpecificStructuralObjectsComponent(data)
    scene = struct_obj_comp.update_ile_scene(scene)
    assert len(objects) == 1

    scene = component.run_delayed_actions(scene)
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 1
    component.get_num_delayed_actions() == 0
    assert not component._delayed_perf_pos
    assert objects[0]['type'] == "cube"
    assert ObjectRepository.get_instance().has_label(label)

    perf_pos = scene['performerStart']['position']
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

    assert min_x <= perf_pos['x'] <= max_x
    assert perf_pos['y'] == platform_scale['y']
    assert min_z <= perf_pos['z'] <= max_z


def test_shortcut_lava_room_off():
    component = ShortcutComponent({
        'shortcut_lava_room': False
    })
    assert not component.shortcut_lava_room
    assert not component.get_shortcut_lava_room()
    scene = component.update_ile_scene(prior_scene())
    assert 'floorTextures' not in scene

    assert scene == prior_scene()


def test_shortcut_lava_room_on_3x3_room():
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

    assert 'lava' in scene
    lava = scene['lava']
    assert len(lava) == 6
    assert lava[0]['x'] == -1
    assert lava[0]['z'] == -1
    assert lava[1]['x'] == 1
    assert lava[1]['z'] == -1
    assert lava[2]['x'] == -1
    assert lava[2]['z'] == 0
    assert lava[3]['x'] == 1
    assert lava[3]['z'] == 0
    assert lava[4]['x'] == -1
    assert lava[4]['z'] == 1
    assert lava[5]['x'] == 1
    assert lava[5]['z'] == 1

    perf_pos = scene['performerStart']['position']
    perf_rot_y = scene['performerStart']['rotation']['y']
    assert perf_pos == {'x': 0, 'y': 0, 'z': -1 * (z_size / 2.0) + 0.5}
    assert perf_rot_y >= -90
    assert perf_rot_y <= 90


def test_shortcut_lava_room_on_4x2_room():
    x_size = 4
    z_size = 2
    component = ShortcutComponent({
        'shortcut_lava_room': True
    })
    assert component.shortcut_lava_room
    assert component.get_shortcut_lava_room()
    scene = component.update_ile_scene(prior_scene_custom_size(x_size,
                                                               z_size))
    assert scene != prior_scene_custom_size(x_size, z_size)

    assert 'lava' in scene
    lava = scene['lava']
    assert len(lava) == 12
    assert lava == [
        {'x': -1, 'z': -1},
        {'x': 1, 'z': -1},
        {'x': -2, 'z': -1},
        {'x': 2, 'z': -1},
        {'x': -1, 'z': 0},
        {'x': 1, 'z': 0},
        {'x': -2, 'z': 0},
        {'x': 2, 'z': 0},
        {'x': -1, 'z': 1},
        {'x': 1, 'z': 1},
        {'x': -2, 'z': 1},
        {'x': 2, 'z': 1}
    ]

    perf_pos = scene['performerStart']['position']
    perf_rot_y = scene['performerStart']['rotation']['y']
    assert perf_pos == {'x': 0, 'y': 0, 'z': -1 * (z_size / 2.0) + 0.5}
    assert perf_rot_y >= -90
    assert perf_rot_y <= 90


def test_shortcut_lava_room_on_7x1_room():
    x_size = 7
    z_size = 1
    component = ShortcutComponent({
        'shortcut_lava_room': True
    })
    assert component.shortcut_lava_room
    assert component.get_shortcut_lava_room()
    scene = component.update_ile_scene(prior_scene_custom_size(x_size,
                                                               z_size))
    assert scene != prior_scene_custom_size(x_size, z_size)

    assert 'lava' in scene
    lava = scene['lava']
    assert len(lava) == 4
    assert lava[0]['x'] == -2
    assert lava[0]['z'] == 0
    assert lava[1]['x'] == 2
    assert lava[1]['z'] == 0
    assert lava[2]['x'] == -3
    assert lava[2]['z'] == 0
    assert lava[3]['x'] == 3
    assert lava[3]['z'] == 0

    perf_pos = scene['performerStart']['position']
    perf_rot_y = scene['performerStart']['rotation']['y']
    assert perf_pos == {'x': 0, 'y': 0, 'z': -1 * (z_size / 2.0) + 0.5}
    assert perf_rot_y >= -90
    assert perf_rot_y <= 90


def test_shortcut_lava_room_on_9x4_room():
    x_size = 9
    z_size = 4
    component = ShortcutComponent({
        'shortcut_lava_room': True
    })
    assert component.shortcut_lava_room
    assert component.get_shortcut_lava_room()
    scene = component.update_ile_scene(prior_scene_custom_size(x_size,
                                                               z_size))
    assert scene != prior_scene_custom_size(x_size, z_size)

    assert 'lava' in scene
    lava = scene['lava']
    assert len(lava) == 30

    perf_pos = scene['performerStart']['position']
    perf_rot_y = scene['performerStart']['rotation']['y']
    assert perf_pos == {'x': 0, 'y': 0, 'z': -1 * (z_size / 2.0) + 0.5}
    assert perf_rot_y >= -90
    assert perf_rot_y <= 90


def test_shortcut_lava_room_on_10x10_room():
    z_size = 10
    component = ShortcutComponent({
        'shortcut_lava_room': True
    })
    assert component.shortcut_lava_room
    assert component.get_shortcut_lava_room()
    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()

    assert 'lava' in scene
    lava = scene['lava']
    assert len(lava) == 88

    perf_pos = scene['performerStart']['position']
    perf_rot_y = scene['performerStart']['rotation']['y']
    assert perf_pos == {'x': 0, 'y': 0, 'z': -1 * (z_size / 2.0) + 0.5}
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
    lavas = scene['lava']
    lavas_switched = scene_switched['lava']
    assert len(lavas) == 24
    for x in range(-2, 3):
        for z in range(1, 6):
            if x != 0 and z != 4:
                assert {'x': x, 'z': z} in lavas
                assert {'x': z, 'z': x} in lavas_switched

    objs = scene['objects']
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

    switched_target_pos = scene_switched['objects'][0]['shows'][0]['position']
    switched_tool_show = scene_switched['objects'][1]['shows'][0]
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
    lavas = scene['lava']
    lavas_switched = scene_switched['lava']
    assert len(lavas) == 24
    for x in range(-2, 3):
        for z in range(1, 6):
            if x != 0 and z != 4:
                assert {'x': x, 'z': z} in lavas
                assert {'x': z, 'z': x} in lavas_switched

    objs = scene['objects']
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

    switched_target_pos = scene_switched['objects'][0]['shows'][0]['position']
    switched_tool_show = scene_switched['objects'][1]['shows'][0]
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
    lavas = scene['lava']
    assert len(lavas) >= 24

    objs = scene['objects']
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
    lavas = scene['lava']
    lavas_switched = scene_switched['lava']
    assert len(lavas) == 24
    for x in range(-2, 3):
        for z in range(1, 6):
            if x != 0 and z != 4:
                assert {'x': x, 'z': z} in lavas
                assert {'x': z, 'z': x} in lavas_switched

    objs = scene['objects']
    assert len(objs) == 4
    assert len(scene_switched['objects']) == 4
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

    switched_target_pos = scene_switched['objects'][0]['shows'][0]['position']
    switched_tool_show = scene_switched['objects'][1]['shows'][0]
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
        {'x': 0.7, 'y': 0.15, 'z': -1.25},
        {'x': 0.575, 'y': 0.15, 'z': -1.25},
        {'x': 0.45, 'y': 0.15, 'z': -1.25}]
    assert pos2 in [
        {'x': -0.7, 'y': 0.15, 'z': -1.25},
        {'x': -0.575, 'y': 0.15, 'z': -1.25},
        {'x': -0.45, 'y': 0.15, 'z': -1.25}]

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
    lavas = scene['lava']
    assert len(lavas) >= 24

    objs = scene['objects']
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
    lavas = scene['lava']
    assert len(lavas) >= 24

    objs = scene['objects']
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
    assert (scene['performerStart']['position']['x'] !=
            -10 or scene['performerStart']['position']['z'] not in [0, 0.5])

    scene = prior_scene_custom_size(10, 21)
    scene = component.update_ile_scene(scene)
    assert (scene['performerStart']['position']['x'] not in
            [0, 0.5] or scene['performerStart']['position']['z'] != -10)


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
