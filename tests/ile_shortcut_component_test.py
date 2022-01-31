from typing import List

from ideal_learning_env import ObjectRepository, ShortcutComponent


def prior_scene():
    return {'debug': {}, 'goal': {}, 'performerStart':
            {'position':
             {'x': 0, 'y': 0, 'z': 0}},
            'roomDimensions': {'x': 10, 'y': 3, 'z': 10}}


def prior_scene_custom_size(x, z):
    return {'debug': {}, 'goal': {}, 'performerStart':
            {'position':
             {'x': 0, 'y': 0, 'z': 0}},
            'roomDimensions': {'x': x, 'y': 3, 'z': z}}


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
