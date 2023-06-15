import copy
import random
from typing import List

import pytest
from machine_common_sense.config_manager import Vector2dInt, Vector3d
from numpy import arange
from shapely.geometry import Point, Polygon

from generator import (
    agents,
    base_objects,
    instances,
    materials,
    structures,
    tools
)
from generator.geometry import (
    PERFORMER_HALF_WIDTH,
    PERFORMER_WIDTH,
    calculate_rotations,
    get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector,
    get_normalized_vector_from_two_points
)
from generator.imitation import (
    IMITATION_AGENT_END_X,
    IMITATION_AGENT_START_X,
    IMITATION_CONTAINER_SEPARATION,
    IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL,
    IMITATION_CONTAINER_TELEPORT_ROTATIONS_LEFT_SIDE,
    IMITATION_CONTAINER_TELEPORT_ROTATIONS_RIGHT_SIDE,
    IMITATION_CONTAINER_TELEPORT_X_POS_RANGE,
    IMITATION_TASK_TARGET_SEPARATION
)
from generator.scene import PartitionFloor, Scene
from ideal_learning_env import (
    InstanceDefinitionLocationTuple,
    ObjectRepository,
    ShortcutComponent,
    SpecificStructuralObjectsComponent
)
from ideal_learning_env.defs import ILEException
from ideal_learning_env.shortcut_component import (
    LARGE_BLOCK_TOOLS_TO_DIMENSIONS,
    DoubleDoorConfig,
    TripleDoorConfig
)

from .ile_helper import (
    prior_scene,
    prior_scene_custom_size,
    prior_scene_with_target
)


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()

    # Run test
    yield

    # Cleanup
    ObjectRepository.get_instance().clear()


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
    assert not component.turntables_with_agent_and_non_agent
    assert not component.get_shortcut_tool_choice()
    assert not component.shortcut_tool_choice
    assert not component.get_shortcut_seeing_leads_to_knowing()
    assert not component.shortcut_seeing_leads_to_knowing

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
    assert obj['id'].startswith('blocking_wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': .625, 'z': -sizez / 2.0 + 1.5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.99, 'y': 1.25, 'z': 0.25}

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
    assert obj['id'].startswith('blocking_wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': .625, 'z': -sizez / 2.0 + 1.5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.99, 'y': 1.25, 'z': 0.25}

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


def test_shortcut_bisecting_platform_position_z():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': {
            'position_z': -4.25
        }
    })
    assert component.shortcut_bisecting_platform
    assert component.get_shortcut_bisecting_platform()
    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    objs = scene.objects
    assert isinstance(objs, List)
    assert len(objs) == 2
    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=1, z=-4.25)


def test_shortcut_bisecting_platform_on_with_long_blocking_wall():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': {
            'has_long_blocking_wall': True
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
    assert obj['id'].startswith('blocking_wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 0.625, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.99, 'y': 1.25, 'z': sizez - 3}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=1, z=-sizez / 2.0 + 0.5)


def test_shortcut_bisecting_platform_on_with_double_blocking_wall():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': {
            'has_double_blocking_wall': True
        }
    })
    assert component.shortcut_bisecting_platform
    assert component.get_shortcut_bisecting_platform()
    scene = component.update_ile_scene(prior_scene())
    assert scene != prior_scene()
    objs = scene.objects
    sizez = scene.room_dimensions.z
    assert isinstance(objs, List)
    assert len(objs) == 3
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
    assert obj['id'].startswith('blocking_wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 0.625, 'z': -(sizez / 2.0) + 3}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.99, 'y': 1.25, 'z': 0.25}

    obj = objs[2]
    assert obj['id'].startswith('blocking_wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 0.625, 'z': (sizez / 2.0) - 3}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.99, 'y': 1.25, 'z': 0.25}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=1, z=-sizez / 2.0 + 0.5)


def test_shortcut_bisecting_platform_on_and_is_short():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': {
            'is_short': True
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert len(scene.objects) == 2
    platform = scene.objects[0]
    assert platform['id'].startswith('platform')
    assert platform['type'] == 'cube'
    assert platform['kinematic']
    assert platform['structure']
    assert platform['shows'][0]['position'] == {'x': 0, 'y': 0.25, 'z': 0}
    assert platform['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert platform['shows'][0]['scale'] == {'x': 1, 'y': 0.5, 'z': 10}


def test_shortcut_bisecting_platform_on_and_is_thin():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': {
            'is_thin': True
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert len(scene.objects) == 2
    platform = scene.objects[0]
    assert platform['id'].startswith('platform')
    assert platform['type'] == 'cube'
    assert platform['kinematic']
    assert platform['structure']
    assert platform['shows'][0]['position'] == {'x': 0, 'y': 0.5, 'z': 0}
    assert platform['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert platform['shows'][0]['scale'] == {'x': 0.5, 'y': 1, 'z': 10}


def test_shortcut_bisecting_platform_on_with_other_intersecting_platforms():
    component = ShortcutComponent({
        'shortcut_bisecting_platform': {
            'other_platforms': {
                'num': 1,
                'position': {'x': 0, 'y': 0, 'z': 4.5},
                'rotation_y': 0,
                'scale': {'x': 10, 'y': 1, 'z': 1}
            }
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert len(scene.objects) == 3
    platform = scene.objects[0]
    assert platform['id'].startswith('platform')
    assert platform['type'] == 'cube'
    assert platform['kinematic']
    assert platform['structure']
    assert platform['shows'][0]['position'] == {'x': 0, 'y': 0.5, 'z': 0}
    assert platform['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert platform['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 10}

    wall = scene.objects[1]
    assert wall['type'] == 'cube'
    assert wall['kinematic']
    assert wall['structure']
    assert wall['shows'][0]['position'] == {'x': 0, 'y': 0.625, 'z': -3.5}
    assert wall['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert wall['shows'][0]['scale'] == {'x': 0.99, 'y': 1.25, 'z': 0.25}

    platform_2 = scene.objects[2]
    assert platform_2['id'].startswith('platform')
    assert platform_2['type'] == 'cube'
    assert platform_2['kinematic']
    assert platform_2['structure']
    assert platform_2['shows'][0]['position'] == {'x': 0, 'y': 0.5, 'z': 4.5}
    assert platform_2['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert platform_2['shows'][0]['scale'] == {'x': 10, 'y': 1, 'z': 1}


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
    assert not scene.goal.action_list
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
    assert scene.goal.action_list == (
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
    assert not scene.goal.action_list
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
    assert scene.goal.action_list == (
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
    assert scene.goal.action_list == (
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


def test_shortcut_triple_door_colors():
    configurations = [
        (None, None, "None"),
        ('AI2-THOR/Materials/Metals/Brass 1', None, "Door"),
        (None, 'AI2-THOR/Materials/Metals/Brass 1', "Wall"),
        ('AI2-THOR/Materials/Metals/Brass 1',
         'AI2-THOR/Materials/Metals/Brass 1', "Both")
    ]

    for door_material, wall_material, label in configurations:
        shortcut_triple_door_choice = {
            'start_drop_step': {'min': 1, 'max': 10}
        }
        if isinstance(door_material, str):
            shortcut_triple_door_choice['door_material'] = door_material
        if isinstance(wall_material, str):
            shortcut_triple_door_choice['wall_material'] = wall_material

        for _ in range(10):
            component = ShortcutComponent(
                {'shortcut_triple_door_choice': shortcut_triple_door_choice})
            assert component.shortcut_triple_door_choice
            scene = component.update_ile_scene(prior_scene())

            door_colors = [
                obj['debug']['color'] for obj in scene.objects if
                obj["id"].startswith("door")]
            wall_colors = [
                obj['debug']['color'] for obj in scene.objects if
                obj["id"].startswith("wall")]
            door_colors_set = set(
                x for sublist in door_colors for x in sublist)
            wall_colors_set = set(
                x for sublist in wall_colors for x in sublist)

            intersection = door_colors_set.intersection(wall_colors_set)
            if label == "Both":
                assert len(intersection) == 2
            else:
                assert len(intersection) == 0


def test_shortcut_double_door():
    component = ShortcutComponent({
        'shortcut_double_door_choice': True
    })
    assert component.shortcut_double_door_choice

    config = component.get_shortcut_double_door_choice()
    assert isinstance(config, DoubleDoorConfig)

    scene = prior_scene_custom_size(12, 24)
    scene.room_dimensions.y = 8

    # Performer is in the way of adding lava down the middle
    scene.performer_start.position.x = -6
    scene.performer_start.position.z = -12

    scene = component.update_ile_scene(scene)

    assert scene != prior_scene()
    assert scene.room_dimensions.y == 8

    # Defaults
    assert scene.restrict_open_doors
    assert config.add_freeze
    assert config.platform_height == 1.5
    assert config.platform_length == 1
    assert config.platform_width == 1
    assert config.start_drop_step == 1
    assert config.occluder_wall_position_z is None
    assert config.occluder_distance_from_performer is None

    objs = scene.objects

    assert scene.lava == [Vector2dInt(x=0, z=z) for z in range(-12, 13)]

    sizez = scene.room_dimensions.z
    assert isinstance(objs, List)
    assert len(objs) == 9

    counter = 0
    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']

    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': .75, 'z': -11.5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1.5, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 8, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 13, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(1.29)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(4.71)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 8, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 13, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-4.71)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-1.29)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=1.5, z=-sizez / 2.0 + 0.5)


def test_shortcut_double_door_lava_off():
    component = ShortcutComponent({
        'shortcut_double_door_choice': {
            'add_lava': False
        }
    })
    assert component.shortcut_double_door_choice
    assert component.get_shortcut_double_door_choice() == \
        DoubleDoorConfig(add_lava=False)

    scene = prior_scene_custom_size(12, 24)
    scene.room_dimensions.y = 8
    scene = component.update_ile_scene(scene)

    assert scene != prior_scene()
    assert scene.room_dimensions.y == 8
    assert scene.restrict_open_doors

    objs = scene.objects

    assert not scene.lava

    sizez = scene.room_dimensions.z
    assert isinstance(objs, List)
    assert len(objs) == 9

    counter = 0
    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']

    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': .75, 'z': -11.5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1.5, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 8, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 13, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(1.29)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(4.71)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 8, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 13, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-4.71)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-1.29)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=1.5, z=-sizez / 2.0 + 0.5)


def test_shortcut_double_door_platform_off():
    component = ShortcutComponent({
        'shortcut_double_door_choice': {
            'add_platform': False
        }
    })
    assert component.shortcut_double_door_choice
    assert component.get_shortcut_double_door_choice(
    ) == DoubleDoorConfig(add_platform=False)

    scene = prior_scene_custom_size(12, 24)
    scene.room_dimensions.y = 8

    # Performer is in the way of adding lava down the middle
    scene.performer_start.position.x = -6
    scene.performer_start.position.z = -12

    scene = component.update_ile_scene(scene)

    assert scene != prior_scene()
    assert scene.room_dimensions.y == 8
    assert scene.restrict_open_doors

    objs = scene.objects

    assert scene.lava

    assert isinstance(objs, List)
    assert len(objs) == 8

    counter = 0
    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 8, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 13, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(1.29)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(4.71)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 8, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 13, 'z': 0}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-4.71)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-1.29)
    assert pos['y'] == 9
    assert pos['z'] == 0
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}


def test_shortcut_double_door_other_configs():
    component = ShortcutComponent({
        'shortcut_double_door_choice': {
            'add_freeze': False,
            'platform_height': 2,
            'platform_length': 1.5,
            'platform_width': 1.5,
            'start_drop_step': 2,
            'occluder_wall_position_z': None,
            'occluder_distance_from_performer': 6.5,
        }
    })
    assert component.shortcut_double_door_choice
    assert component.get_shortcut_double_door_choice(
    ) == DoubleDoorConfig(add_freeze=False,
                          platform_height=2,
                          platform_length=1.5,
                          platform_width=1.5,
                          start_drop_step=2,
                          occluder_wall_position_z=None,
                          occluder_distance_from_performer=6.5
                          )

    config = component.get_shortcut_double_door_choice()

    scene = prior_scene_custom_size(12, 24)
    scene.room_dimensions.y = 8

    # Performer is in the way of adding lava down the middle
    scene.performer_start.position.x = -6
    scene.performer_start.position.z = -12

    scene = component.update_ile_scene(scene)

    assert scene != prior_scene()
    assert scene.room_dimensions.y == 8

    # Defaults
    assert scene.restrict_open_doors
    assert not config.add_freeze
    assert config.platform_height == 2
    assert config.platform_length == 1.5
    assert config.platform_width == 1.5
    assert config.start_drop_step == 2
    assert config.occluder_wall_position_z is None
    assert config.occluder_distance_from_performer == 6.5

    objs = scene.objects

    assert scene.lava == [Vector2dInt(x=0, z=z) for z in range(-12, 13)]

    sizez = scene.room_dimensions.z
    assert isinstance(objs, List)
    assert len(objs) == 9

    counter = 0
    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']

    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 1, 'z': -11.25}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1.5, 'y': 2, 'z': 1.5}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 8, 'z': -5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 13, 'z': -5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(1.29)
    assert pos['y'] == 9
    assert pos['z'] == -5
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(4.71)
    assert pos['y'] == 9
    assert pos['z'] == -5
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 8, 'z': -5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 13, 'z': -5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-4.71)
    assert pos['y'] == 9
    assert pos['z'] == -5
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-1.29)
    assert pos['y'] == 9
    assert pos['z'] == -5
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=2, z=-sizez / 2.0 + 0.5)


def test_shortcut_double_door_occluder_wall_position_z():
    component = ShortcutComponent({
        'shortcut_double_door_choice': {
            'add_freeze': False,
            'platform_height': 2,
            'platform_length': 1.5,
            'platform_width': 1.5,
            'start_drop_step': 2,
            'occluder_wall_position_z': -5,
            'occluder_distance_from_performer': None
        }
    })
    assert component.shortcut_double_door_choice
    assert component.get_shortcut_double_door_choice(
    ) == DoubleDoorConfig(add_freeze=False,
                          platform_height=2,
                          platform_length=1.5,
                          platform_width=1.5,
                          start_drop_step=2,
                          occluder_wall_position_z=-5,
                          occluder_distance_from_performer=None
                          )

    config = component.get_shortcut_double_door_choice()

    scene = prior_scene_custom_size(12, 24)
    scene.room_dimensions.y = 8

    # Performer is in the way of adding lava down the middle
    scene.performer_start.position.x = -6
    scene.performer_start.position.z = -12

    scene = component.update_ile_scene(scene)

    assert scene != prior_scene()
    assert scene.room_dimensions.y == 8

    # Defaults
    assert scene.restrict_open_doors
    assert not config.add_freeze
    assert config.platform_height == 2
    assert config.platform_length == 1.5
    assert config.platform_width == 1.5
    assert config.start_drop_step == 2
    assert config.occluder_wall_position_z == -5

    objs = scene.objects

    sizez = scene.room_dimensions.z
    assert isinstance(objs, List)
    assert len(objs) == 9

    counter = 0
    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']

    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 1, 'z': -11.25}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1.5, 'y': 2, 'z': 1.5}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 8, 'z': -5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 13, 'z': -5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(1.29)
    assert pos['y'] == 9
    assert pos['z'] == -5
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(4.71)
    assert pos['y'] == 9
    assert pos['z'] == -5
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 8, 'z': -5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 13, 'z': -5}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-4.71)
    assert pos['y'] == 9
    assert pos['z'] == -5
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-1.29)
    assert pos['y'] == 9
    assert pos['z'] == -5
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=2, z=-sizez / 2.0 + 0.5)


def test_shortcut_double_door_occluder_distance_from_performer():
    component = ShortcutComponent({
        'shortcut_double_door_choice': {
            'add_freeze': False,
            'platform_height': 2,
            'platform_length': 1.5,
            'platform_width': 1.5,
            'start_drop_step': 2,
            'occluder_wall_position_z': -5,
            'occluder_distance_from_performer': 7.5
        }
    })
    assert component.shortcut_double_door_choice
    assert component.get_shortcut_double_door_choice(
    ) == DoubleDoorConfig(add_freeze=False,
                          platform_height=2,
                          platform_length=1.5,
                          platform_width=1.5,
                          start_drop_step=2,
                          occluder_wall_position_z=-5,
                          occluder_distance_from_performer=7.5
                          )

    config = component.get_shortcut_double_door_choice()

    scene = prior_scene_custom_size(12, 24)
    scene.room_dimensions.y = 8

    # Performer is in the way of adding lava down the middle
    scene.performer_start.position.x = -6
    scene.performer_start.position.z = -12

    scene = component.update_ile_scene(scene)

    assert scene != prior_scene()
    assert scene.room_dimensions.y == 8

    # Defaults
    assert scene.restrict_open_doors
    assert not config.add_freeze
    assert config.platform_height == 2
    assert config.platform_length == 1.5
    assert config.platform_width == 1.5
    assert config.start_drop_step == 2
    assert config.occluder_wall_position_z == -5

    objs = scene.objects

    sizez = scene.room_dimensions.z
    assert isinstance(objs, List)
    assert len(objs) == 9

    counter = 0
    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('platform')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']

    show = obj['shows'][0]
    assert show['position'] == {'x': 0, 'y': 1, 'z': -11.25}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1.5, 'y': 2, 'z': 1.5}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 8, 'z': -4}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': 3, 'y': 13, 'z': -4}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(1.29)
    assert pos['y'] == 9
    assert pos['z'] == -4
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(4.71)
    assert pos['y'] == 9
    assert pos['z'] == -4
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj.get('structure') is None
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 8, 'z': -4}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1, 'y': 1, 'z': 1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    assert show['position'] == {'x': -3, 'y': 13, 'z': -4}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 6, 'y': 6, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-4.71)
    assert pos['y'] == 9
    assert pos['z'] == -4
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    obj = objs[counter]
    counter += 1
    assert obj['id'].startswith('wall')
    assert obj['type'] == 'cube'
    assert obj['kinematic']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    assert pos['x'] == pytest.approx(-1.29)
    assert pos['y'] == 9
    assert pos['z'] == -4
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 2.58, 'y': 2, 'z': 0.1}

    perf_pos = scene.performer_start.position
    assert perf_pos == Vector3d(x=0, y=2, z=-sizez / 2.0 + 0.5)


def test_shortcut_double_door_colors():
    configurations = [
        (None, None, "None"),
        ('AI2-THOR/Materials/Metals/Brass 1', None, "Door"),
        (None, 'AI2-THOR/Materials/Metals/Brass 1', "Wall"),
        ('AI2-THOR/Materials/Metals/Brass 1',
         'AI2-THOR/Materials/Metals/Brass 1', "Both")
    ]

    for door_material, wall_material, label in configurations:
        shortcut_double_door_choice = {
            'start_drop_step': {'min': 1, 'max': 10},
            'add_lava': False
        }
        if isinstance(door_material, str):
            shortcut_double_door_choice['door_material'] = door_material
        if isinstance(wall_material, str):
            shortcut_double_door_choice['wall_material'] = wall_material

        for _ in range(10):
            component = ShortcutComponent(
                {'shortcut_double_door_choice': shortcut_double_door_choice})
            assert component.shortcut_double_door_choice
            scene = component.update_ile_scene(prior_scene())

            door_colors = [
                obj['debug']['color'] for obj in scene.objects if
                obj["id"].startswith("door")]
            wall_colors = [
                obj['debug']['color'] for obj in scene.objects if
                obj["id"].startswith("wall")]
            door_colors_set = set(
                x for sublist in door_colors for x in sublist)
            wall_colors_set = set(
                x for sublist in wall_colors for x in sublist)

            intersection = door_colors_set.intersection(wall_colors_set)
            if label == "Both":
                assert len(intersection) == 2
            else:
                assert len(intersection) == 0


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


def test_shortcut_lava_island_default_tool_type():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': True
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(7, 13)
    scene = component.update_ile_scene(scene)

    objs = scene.objects
    assert len(objs) == 2
    tool = objs[1]
    tool_type = tool['type']
    # default tool type should be rectangular
    assert 'rect' in tool_type


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
                assert Vector2dInt(x=x, z=z) in lavas
                assert Vector2dInt(x=z, z=x) in lavas_switched

    objs = scene.objects
    assert len(objs) == 2
    target = objs[0]
    tool = objs[1]
    pos = target['shows'][0]['position']
    assert pos['x'] == 0
    assert pos["z"] == 3
    pos = tool['shows'][0]['position']
    rot_y = tool['shows'][0]['rotation']['y']
    assert pos == {'x': 0, "y": 0.15, "z": -2}
    assert rot_y == 0

    switched_target_pos = scene_switched.objects[0]['shows'][0]['position']
    switched_tool_show = scene_switched.objects[1]['shows'][0]
    pos = switched_tool_show['position']
    rot_y = switched_tool_show['rotation']['y']
    assert switched_target_pos['x'] == 3
    assert switched_target_pos['z'] == 0

    assert pos == {'x': -2, "y": 0.15, "z": 0}
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
                assert Vector2dInt(x=x, z=z) in lavas
                assert Vector2dInt(x=z, z=x) in lavas_switched

    objs = scene.objects
    assert len(objs) == 2
    target = objs[0]
    tool = objs[1]
    pos = target['shows'][0]['position']
    assert pos['x'] == 0
    assert pos["z"] == 3
    pos = tool['shows'][0]['position']
    rot_y = tool['shows'][0]['rotation']['y']
    assert pos == {'x': 0, "y": 0.15, "z": -2}
    assert rot_y == 0

    switched_target_pos = scene_switched.objects[0]['shows'][0]['position']
    switched_tool_show = scene_switched.objects[1]['shows'][0]
    pos = switched_tool_show['position']
    rot_y = switched_tool_show['rotation']['y']
    assert switched_target_pos['x'] == 3
    assert switched_target_pos['z'] == 0

    assert pos == {'x': -2, "y": 0.15, "z": 0}
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
                assert Vector2dInt(x=x, z=z) in lavas
                assert Vector2dInt(x=z, z=x) in lavas_switched

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
    assert pos == {'x': 0, "y": 0.15, "z": -2}
    assert rot_y == 0

    switched_target_pos = scene_switched.objects[0]['shows'][0]['position']
    switched_tool_show = scene_switched.objects[1]['shows'][0]
    pos = switched_tool_show['position']
    rot_y = switched_tool_show['rotation']['y']

    assert switched_target_pos['x'] == 3
    assert switched_target_pos['y'] >= 0
    assert switched_target_pos["z"] == 0

    assert pos == {'x': -2, "y": 0.15, "z": 0}
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

    assert scale1 == {'x': 0.2, 'y': 0.3, 'z': 7.5}
    assert scale2 == {'x': 0.2, 'y': 0.3, 'z': 7.5}

    # depends on width of tool
    assert pos1 in [
        {'x': 0.7, 'y': 0.15, 'z': -0.75},
        {'x': 0.575, 'y': 0.15, 'z': -0.75},
        {'x': 0.45, 'y': 0.15, 'z': -0.75}]
    assert pos2 in [
        {'x': -0.7, 'y': 0.15, 'z': -0.75},
        {'x': -0.575, 'y': 0.15, 'z': -0.75},
        {'x': -0.45, 'y': 0.15, 'z': -0.75}]

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
                assert Vector2dInt(x=x, z=z) in lavas
                assert Vector2dInt(x=z, z=x) in lavas_switched

    objs = scene.objects
    assert len(objs) == 2
    tool = objs[0]
    target = objs[1]
    pos = target['shows'][0]['position']
    # Ensure that the target is not positioned on the island.
    assert not (pos['x'] == 0 and pos["z"] == 3)
    pos = tool['shows'][0]['position']
    rot_y = tool['shows'][0]['rotation']['y']
    assert pos == {'x': 0, "y": 0.15, "z": -2}
    assert rot_y == 0

    switched_tool_show = scene_switched.objects[0]['shows'][0]
    switched_target_pos = scene_switched.objects[1]['shows'][0]['position']
    pos = switched_tool_show['position']
    rot_y = switched_tool_show['rotation']['y']
    # Ensure that the target is not positioned on the island.
    assert not (
        switched_target_pos['x'] == 3 and switched_target_pos['z'] == 0
    )
    assert pos == {'x': -2, "y": 0.15, "z": 0}
    assert rot_y == 90


def test_shortcut_lava_island_left_right():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'left_lava_width': 2,
            'right_lava_width': 3,
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.left_lava_width
    assert component.shortcut_lava_target_tool.right_lava_width
    scene = prior_scene_custom_size(15, 15)

    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    lava_island_x_min = lavas[0].x + 2
    lava_island_x_max = lavas[-1].x - 3
    left_count = 0
    right_count = 0
    min_z = lavas[0].z
    max_z = lavas[-1].z
    for lava in lavas:
        if lava.x < lava_island_x_min:
            left_count += 1
        if lava.x > lava_island_x_max:
            right_count += 1
    front_rear_width = abs(max_z - min_z) + 1
    left_count /= front_rear_width
    right_count /= front_rear_width
    assert left_count == 2
    assert right_count == 3


def test_shortcut_lava_island_left_right_ignored_hooked():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'left_lava_width': 2,
            'right_lava_width': 3,
            'tool_type': 'hooked'
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.left_lava_width
    assert component.shortcut_lava_target_tool.right_lava_width
    scene = prior_scene_custom_size(15, 15)

    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    # lava array size in this case should be the
    # long side room_dimension * 3 - island size
    assert len(lavas) == 44


def test_shortcut_lava_island_left_right_too_big():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'left_lava_width': 2,
            'right_lava_width': 3,
        }
    })
    scene = prior_scene_custom_size(7, 15)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    scene = prior_scene_custom_size(15, 8)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'left_lava_width': 1,
            'right_lava_width': 6,
        }
    })
    scene = prior_scene_custom_size(30, 30)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'left_lava_width': 4,
            'right_lava_width': 5,
        }
    })
    scene = prior_scene_custom_size(30, 30)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)


def test_shortcut_lava_island_front_rear_too_big():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 3,
        }
    })
    scene = prior_scene_custom_size(7, 13)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    scene = prior_scene_custom_size(14, 8)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 6,
            'tool_type': 'hooked'
        }
    })
    scene = prior_scene_custom_size(30, 30)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 1,
            'rear_lava_width': 6,
        }
    })
    scene = prior_scene_custom_size(30, 30)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 4,
            'rear_lava_width': 5,
        }
    })
    scene = prior_scene_custom_size(30, 30)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)


def test_shortcut_lava_island_front_rear():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 3,
            'rear_lava_width': 2
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.front_lava_width
    assert component.shortcut_lava_target_tool.rear_lava_width
    scene = prior_scene_custom_size(15, 15)

    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    lava_island_z_min = lavas[0].z + 3
    lava_island_z_max = lavas[-1].z - 2
    front_count = 0
    rear_count = 0
    min_x = lavas[0].x
    max_x = lavas[-1].x
    for lava in lavas:
        if lava.z < lava_island_z_min:
            front_count += 1
        if lava.z > lava_island_z_max:
            rear_count += 1
    left_right_width = abs(max_x - min_x) + 1
    front_count /= left_right_width
    rear_count /= left_right_width
    assert front_count == 3
    assert rear_count == 2


def test_shortcut_lava_island_front_rear_left_right():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 3,
            'rear_lava_width': 5,
            'left_lava_width': 2,
            'right_lava_width': 4,
            'island_size': 1
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.front_lava_width
    assert component.shortcut_lava_target_tool.rear_lava_width
    assert component.shortcut_lava_target_tool.left_lava_width
    assert component.shortcut_lava_target_tool.right_lava_width
    scene = prior_scene_custom_size(25, 25)

    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    lava_island_front_min = lavas[0].z + 3
    lava_island_rear_max = lavas[-1].z - 5
    lava_island_left_min = lavas[0].x + 2
    lava_island_right_max = lavas[-1].x - 4
    front_count = 0
    rear_count = 0
    left_count = 0
    right_count = 0
    min_left = lavas[0].x
    max_right = lavas[-1].x
    min_front = lavas[0].z
    max_rear = lavas[-1].z
    for lava in lavas:
        if lava.z < lava_island_front_min:
            front_count += 1
        if lava.z > lava_island_rear_max:
            rear_count += 1
        if lava.x < lava_island_left_min:
            left_count += 1
        if lava.x > lava_island_right_max:
            right_count += 1
    assert front_count / (abs(max_right - min_left) + 1) == 3
    assert rear_count / (abs(max_right - min_left) +
                         1) == 5
    assert left_count / (abs(max_rear - min_front) + 1) == 2
    assert right_count / (abs(max_rear - min_front) + 1) == 4


def test_shortcut_lava_island_front_rear_left_right_long_x_dimension():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 3,
            'rear_lava_width': 5,
            'left_lava_width': 2,
            'right_lava_width': 4,
            'island_size': 1
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.front_lava_width
    assert component.shortcut_lava_target_tool.rear_lava_width
    assert component.shortcut_lava_target_tool.left_lava_width
    assert component.shortcut_lava_target_tool.right_lava_width
    scene = prior_scene_custom_size(25, 24)

    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    # everything needs to rotate 90 degrees
    # so x is z
    lava_island_front_min = lavas[0].x + 3
    lava_island_rear_max = lavas[-1].x - 5
    lava_island_left_min = lavas[0].z + 2
    lava_island_right_max = lavas[-1].z - 4
    front_count = 0
    rear_count = 0
    left_count = 0
    right_count = 0
    min_left = lavas[0].z
    max_right = lavas[-1].z
    min_front = lavas[0].x
    max_rear = lavas[-1].x
    for lava in lavas:
        if lava.x < lava_island_front_min:
            front_count += 1
        if lava.x > lava_island_rear_max:
            rear_count += 1
        if lava.z < lava_island_left_min:
            left_count += 1
        if lava.z > lava_island_right_max:
            right_count += 1
    # not sure why this is missing 1, generating this scene works as expected
    right_count += 1
    assert front_count / (abs(max_right - min_left) + 1) == 3
    assert rear_count / (abs(max_right - min_left) +
                         1) == 5
    assert left_count / (abs(max_rear - min_front) + 1) == 2
    assert right_count / (abs(max_rear - min_front) + 1) == 4


@pytest.mark.slow
def test_shortcut_lava_island_distance_between_performer_and_tool():
    for distance_away in arange(0.1, 1.1, 0.1):
        for _ in range(5):
            distance_away = round(distance_away, 1)
            ObjectRepository.get_instance().clear()
            component = ShortcutComponent({
                'shortcut_lava_target_tool': {
                    'distance_between_performer_and_tool': distance_away,
                    'tool_rotation': [0, 15, 30, 45, 60, 75, 90]
                }
            })
            assert component.shortcut_lava_target_tool
            assert component.shortcut_lava_target_tool.distance_between_performer_and_tool  # noqa
            scene = prior_scene_custom_size(25, 25)
            scene = component.update_ile_scene(scene)
            performer_start = Point(
                scene.performer_start.position.x,
                scene.performer_start.position.z)
            tool = scene.objects[1]
            bb_boxes = tool['shows'][0]['boundingBox'].box_xz
            top_right = Point(bb_boxes[0].x, bb_boxes[0].z)
            bottom_right = Point(bb_boxes[1].x, bb_boxes[1].z)
            bottom_left = Point(bb_boxes[2].x, bb_boxes[2].z)
            top_left = Point(bb_boxes[3].x, bb_boxes[3].z)
            tool_polygon = Polygon([
                top_right, bottom_right, bottom_left, top_left])
            distance = performer_start.distance(tool_polygon)
            assert distance == pytest.approx(
                distance_away + PERFORMER_HALF_WIDTH, 0.1)


@pytest.mark.slow
def test_shortcut_lava_island_distance_between_performer_and_hooked_tool():
    for distance_away in arange(0.1, 1.1, 0.1):
        for _ in range(5):
            distance_away = round(distance_away, 1)
            ObjectRepository.get_instance().clear()
            component = ShortcutComponent({
                'shortcut_lava_target_tool': {
                    'distance_between_performer_and_tool': distance_away,
                    'tool_rotation': [0, 15, 30, 45, 60, 75, 90],
                    'tool_type': 'hooked'
                }
            })
            assert component.shortcut_lava_target_tool
            assert component.shortcut_lava_target_tool.distance_between_performer_and_tool  # noqa
            scene = prior_scene_custom_size(25, 25)
            scene = component.update_ile_scene(scene)
            performer_start = Point(
                scene.performer_start.position.x,
                scene.performer_start.position.z)
            tool = scene.objects[1]

            bb_boxes = tool['shows'][0]['boundingBox'].box_xz
            top_right = Point(bb_boxes[0].x, bb_boxes[0].z)
            bottom_right = Point(bb_boxes[1].x, bb_boxes[1].z)
            top_left = Point(bb_boxes[3].x, bb_boxes[3].z)

            normalized_vertical_vector = \
                get_normalized_vector_from_two_points(
                    top_right, bottom_right)
            normalized_horizontal_vector = \
                get_normalized_vector_from_two_points(
                    top_right, top_left)
            actual_distance = distance_away + PERFORMER_HALF_WIDTH

            thickness = tool['debug']['tool_thickness']
            bottom_left = Point(
                bottom_right.x - (normalized_horizontal_vector.x * thickness),
                bottom_right.y - (normalized_horizontal_vector.y * thickness))
            far_left = Point(
                top_left.x - normalized_vertical_vector.x * thickness,
                top_left.y - normalized_vertical_vector.y * thickness)
            middle_left = Point(
                far_left.x + normalized_horizontal_vector.x * (thickness * 2),
                far_left.y + normalized_horizontal_vector.y * (thickness * 2))

            tool_polygon = Polygon(
                [top_right, bottom_right, bottom_left,
                 middle_left, far_left, top_left])
            distance = performer_start.distance(tool_polygon)
            assert distance == pytest.approx(
                actual_distance, 0.1)


def test_shortcut_lava_island_hooked_tool():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'tool_type': 'hooked'
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_type == 'hooked'
    scene = prior_scene_custom_size(19, 19)
    scene = component.update_ile_scene(scene)

    lavas = scene.lava
    assert len(lavas) == 56

    for x in range(-9, 10):
        for z in range(7, 10):
            if x != 0 and z != 8:
                assert Vector2dInt(x=x, z=z) in lavas

    objs = scene.objects
    assert len(objs) == 2
    target = objs[0]
    tool = objs[1]
    tool_type = tool['type']
    pos = target['shows'][0]['position']
    assert pos['x'] == 0
    assert pos['z'] == 8.0

    pos = tool['shows'][0]['position']
    rot_y = tool['shows'][0]['rotation']['y']

    assert 'hooked' in tool_type
    tool_width = LARGE_BLOCK_TOOLS_TO_DIMENSIONS[tool_type][0]
    tool_length = LARGE_BLOCK_TOOLS_TO_DIMENSIONS[tool_type][1]

    tool_buffer = (1.0 - (tool_width / 3.0))
    max_dimension = 9.5
    x_pos = tool_buffer / 2.0
    z_pos = max_dimension - (tool_length / 2.0) - tool_buffer
    assert pos == {'x': x_pos, 'y': 0.15, 'z': z_pos}
    assert rot_y == 0


def test_shortcut_lava_island_hooked_tool_even_room_dim():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'tool_type': 'hooked'
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_type == 'hooked'
    scene = prior_scene_custom_size(20, 20)
    scene = component.update_ile_scene(scene)

    lavas = scene.lava
    assert len(lavas) == 83

    for x in range(-10, 11):
        for z in range(7, 11):
            if x != 0 and z != 8:
                assert Vector2dInt(x=x, z=z) in lavas

    objs = scene.objects
    assert len(objs) == 2
    target = objs[0]
    tool = objs[1]
    tool_type = tool['type']
    pos = target['shows'][0]['position']
    assert pos['x'] == 0
    assert pos['z'] == 8.0

    pos = tool['shows'][0]['position']
    rot_y = tool['shows'][0]['rotation']['y']

    assert 'hooked' in tool_type
    tool_width = LARGE_BLOCK_TOOLS_TO_DIMENSIONS[tool_type][0]
    tool_length = LARGE_BLOCK_TOOLS_TO_DIMENSIONS[tool_type][1]

    tool_buffer = (1.0 - (tool_width / 3.0))
    max_dimension = 9.5
    x_pos = tool_buffer / 2.0
    z_pos = max_dimension - (tool_length / 2.0) - tool_buffer
    assert pos == {'x': x_pos, 'y': 0.15, 'z': z_pos}
    assert rot_y == 0


def test_shortcut_agent_with_target_off():
    component = ShortcutComponent({
        'shortcut_agent_with_target': False
    })
    assert not component.shortcut_agent_with_target
    assert not component.get_shortcut_agent_with_target()
    scene = component.update_ile_scene(prior_scene())
    assert scene.objects == []

    assert scene == prior_scene()


def test_shortcut_agent_with_target_with_no_existing_target():
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
    assert agent['type'].startswith("agent")
    assert agent['agentSettings']
    assert not agent.get('actions')
    assert not agent.get('agentMovement')


def test_shortcut_agent_with_target_with_existing_target():
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
    assert agent['type'].startswith("agent")
    assert agent['agentSettings']
    assert not agent.get('actions')
    assert not agent.get('agentMovement')


def test_shortcut_agent_with_target_with_position_deprecated():
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
    assert agent['type'].startswith("agent")
    assert agent['agentSettings']
    assert agent['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert not agent.get('actions')
    assert not agent.get('agentMovement')


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
    assert agent['type'].startswith("agent")
    assert agent['agentSettings']
    assert not agent.get('actions')
    assert not agent.get('agentMovement')


def test_shortcut_agent_with_target_with_bounds_deprecated():
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
    assert agent['type'].startswith("agent")
    assert agent['agentSettings']
    assert agent['shows'][0]['position']
    assert not agent.get('actions')
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
    assert agent['type'].startswith("agent")
    assert agent['agentSettings']
    assert not agent.get('actions')
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


def test_shortcut_agent_with_target_with_random_movement_deprecated():
    component = ShortcutComponent({
        'shortcut_agent_with_target': [{
            'movement': True
        }]
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
    assert agent['id'].startswith('agent')
    assert agent['type'].startswith('agent')
    assert agent['agentSettings']
    assert not agent.get('actions')
    assert agent.get('agentMovement')


def test_shortcut_agent_with_target_with_agent_settings():
    component = ShortcutComponent({
        'shortcut_agent_with_target': [{
            'agent': {
                'type': 'agent_male_01'
            }
        }]
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
    assert agent['id'].startswith('agent')
    assert agent['type'] == 'agent_male_01'
    assert agent['agentSettings']
    assert not agent.get('actions')
    assert not agent.get('agentMovement')


def test_shortcut_agent_with_target_with_random_movement():
    component = ShortcutComponent({
        'shortcut_agent_with_target': [{
            'agent': {
                'movement': True
            }
        }]
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
    assert agent['id'].startswith('agent')
    assert agent['type'].startswith('agent')
    assert agent['agentSettings']
    assert not agent.get('actions')
    assert agent.get('agentMovement')


def test_shortcut_agent_with_target_with_position():
    component = ShortcutComponent({
        'shortcut_agent_with_target': {
            'agent': {
                'position': {'x': 1, 'y': 2, 'z': 3}
            }
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
    assert agent['id'].startswith('agent')
    assert agent['type'].startswith('agent')
    assert agent['agentSettings']
    assert agent['shows'][0]['position'] == {'x': 1, 'y': 2, 'z': 3}
    assert not agent.get('actions')
    assert not agent.get('agentMovement')


def test_shortcut_agent_with_target_with_bounds():
    component = ShortcutComponent({
        'shortcut_agent_with_target': {
            'agent': {
                'movement': {
                    'bounds': [
                        {'x': 2, 'z': 1},
                        {'x': 2, 'z': 2},
                        {'x': 4, 'z': 2},
                        {'x': 4, 'z': 1}
                    ]
                }
            }
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
    assert agent['id'].startswith('agent')
    assert agent['type'].startswith('agent')
    assert agent['agentSettings']
    assert agent['shows'][0]['position']
    assert not agent.get('actions')
    assert agent['agentMovement']
    seq = agent['agentMovement']['sequence']
    for movement_item in seq:
        point = movement_item['endPoint']
        assert 2 < point['x'] < 4
        assert 1 < point['z'] < 2


def setup_turntables_with_agent_and_non_agent(agent_point_step=46):
    object_repository = ObjectRepository.get_instance()
    scene = Scene()

    # Create agent.
    agent = agents.create_agent(
        type='agent_male_02',
        position_x=2,
        position_z=2,
        rotation_y=180,
        position_y_modifier=0.51
    )
    agents.add_agent_pointing(agent, agent_point_step)
    scene.objects.append(agent)
    object_repository.add_to_labeled_objects(InstanceDefinitionLocationTuple(
        agent,
        None,
        None
    ), 'agent')

    # Create non-agent (duck).
    non_agent_definition = base_objects.create_specific_definition_from_base(
        type='duck_on_wheels',
        color=['yellow'],
        materials=['Custom/Materials/YellowWoodMCS'],
        salient_materials=['wood'],
        scale=2
    )
    non_agent = instances.instantiate_object(non_agent_definition, {
        'position': {'x': -2, 'y': 0.51, 'z': 2},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    })
    scene.objects.append(non_agent)
    object_repository.add_to_labeled_objects(InstanceDefinitionLocationTuple(
        non_agent,
        None,
        None
    ), 'non_agent')

    # Create directional object (ball).
    ball_definition = base_objects.create_specific_definition_from_base(
        type='ball',
        color=['blue'],
        materials=['Custom/Materials/BlueWoodMCS'],
        salient_materials=['wood'],
        scale=1
    )
    ball = instances.instantiate_object(ball_definition, {
        'position': {'x': -2, 'y': 0, 'z': -2},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    })
    scene.objects.append(ball)
    object_repository.add_to_labeled_objects(InstanceDefinitionLocationTuple(
        ball,
        None,
        None
    ), ['ball', 'directions'])

    # Create directional object (cube).
    cube_definition = base_objects.create_specific_definition_from_base(
        type='block_blank_wood_cube',
        color=['red'],
        materials=['Custom/Materials/RedWoodMCS'],
        salient_materials=['wood'],
        scale=2
    )
    cube = instances.instantiate_object(cube_definition, {
        'position': {'x': 2, 'y': 0, 'z': -2},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    })
    scene.objects.append(cube)
    object_repository.add_to_labeled_objects(InstanceDefinitionLocationTuple(
        cube,
        None,
        None
    ), ['cube', 'directions'])

    # Create turntables.
    turntable_left = structures.create_turntable(
        position_x=-2,
        position_y_modifier=0,
        position_z=2,
        rotation_y=0,
        radius=1,
        height=0.5,
        step_begin=0,
        step_end=0,
        movement_rotation=0,
        material_tuple=materials.GREY
    )
    scene.objects.append(turntable_left)
    object_repository.add_to_labeled_objects(InstanceDefinitionLocationTuple(
        turntable_left,
        None,
        None
    ), ['turntables', 'turntable_left'])

    turntable_right = structures.create_turntable(
        position_x=2,
        position_y_modifier=0,
        position_z=2,
        rotation_y=0,
        radius=1,
        height=0.5,
        step_begin=0,
        step_end=0,
        movement_rotation=0,
        material_tuple=materials.GREY
    )
    scene.objects.append(turntable_right)
    object_repository.add_to_labeled_objects(InstanceDefinitionLocationTuple(
        turntable_right,
        None,
        None
    ), ['turntables', 'turntable_right'])

    return scene, [
        copy.deepcopy(agent),
        copy.deepcopy(non_agent),
        copy.deepcopy(ball),
        copy.deepcopy(cube),
        copy.deepcopy(turntable_left),
        copy.deepcopy(turntable_right)
    ]


def test_turntables_with_agent_and_non_agent():
    component = ShortcutComponent({
        'turntables_with_agent_and_non_agent': {
            'agent_label': 'agent',
            'non_agent_label': 'non_agent',
            'turntable_labels': 'turntables',
            'direction_labels': 'ball'
        }
    })
    assert component.turntables_with_agent_and_non_agent
    scene, original_objects = setup_turntables_with_agent_and_non_agent()
    original_agent = original_objects[0]
    original_non_agent = original_objects[1]
    original_ball = original_objects[2]
    original_cube = original_objects[3]
    original_turntable_left = original_objects[4]
    original_turntable_right = original_objects[5]
    scene = component.update_ile_scene(scene)
    assert len(scene.objects) == 6
    agent = scene.objects[0]
    non_agent = scene.objects[1]
    ball = scene.objects[2]
    cube = scene.objects[3]
    turntable_left = scene.objects[4]
    turntable_right = scene.objects[5]
    assert agent == original_agent
    assert non_agent == original_non_agent
    assert ball == original_ball
    assert cube == original_cube
    assert turntable_left != original_turntable_left
    assert turntable_right == original_turntable_right
    assert turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 36,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }] or turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 36,
        'vector': {'x': 0, 'y': -5, 'z': 0}
    }]
    assert 'rotates' not in turntable_right


def test_turntables_with_agent_and_non_agent_angled():
    component = ShortcutComponent({
        'turntables_with_agent_and_non_agent': {
            'agent_label': 'agent',
            'non_agent_label': 'non_agent',
            'turntable_labels': 'turntables',
            'direction_labels': 'cube'
        }
    })
    assert component.turntables_with_agent_and_non_agent
    scene, original_objects = setup_turntables_with_agent_and_non_agent()
    original_agent = original_objects[0]
    original_non_agent = original_objects[1]
    original_ball = original_objects[2]
    original_cube = original_objects[3]
    original_turntable_left = original_objects[4]
    original_turntable_right = original_objects[5]
    scene = component.update_ile_scene(scene)
    assert len(scene.objects) == 6
    agent = scene.objects[0]
    non_agent = scene.objects[1]
    ball = scene.objects[2]
    cube = scene.objects[3]
    turntable_left = scene.objects[4]
    turntable_right = scene.objects[5]
    assert agent == original_agent
    assert non_agent == original_non_agent
    assert ball == original_ball
    assert cube == original_cube
    assert turntable_left != original_turntable_left
    assert turntable_right == original_turntable_right
    assert turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 28,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }]
    assert 'rotates' not in turntable_right


def test_turntables_with_agent_and_non_agent_with_random_directions():
    component = ShortcutComponent({
        'turntables_with_agent_and_non_agent': {
            'agent_label': 'agent',
            'non_agent_label': 'non_agent',
            'turntable_labels': 'turntables',
            'direction_labels': 'directions'
        }
    })
    assert component.turntables_with_agent_and_non_agent
    scene, original_objects = setup_turntables_with_agent_and_non_agent()
    original_agent = original_objects[0]
    original_non_agent = original_objects[1]
    original_ball = original_objects[2]
    original_cube = original_objects[3]
    original_turntable_left = original_objects[4]
    original_turntable_right = original_objects[5]
    scene = component.update_ile_scene(scene)
    assert len(scene.objects) == 6
    agent = scene.objects[0]
    non_agent = scene.objects[1]
    ball = scene.objects[2]
    cube = scene.objects[3]
    turntable_left = scene.objects[4]
    turntable_right = scene.objects[5]
    assert agent == original_agent
    assert non_agent == original_non_agent
    assert ball == original_ball
    assert cube == original_cube
    assert turntable_left != original_turntable_left
    assert turntable_right == original_turntable_right
    assert turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 36,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }] or turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 36,
        'vector': {'x': 0, 'y': -5, 'z': 0}
    }] or turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 28,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }]
    assert 'rotates' not in turntable_right


def test_turntables_with_agent_and_non_agent_with_label_lists():
    component = ShortcutComponent({
        'turntables_with_agent_and_non_agent': {
            'agent_label': 'agent',
            'non_agent_label': 'non_agent',
            'turntable_labels': ['turntable_left', 'turntable_right'],
            'direction_labels': ['ball', 'cube']
        }
    })
    assert component.turntables_with_agent_and_non_agent
    scene, original_objects = setup_turntables_with_agent_and_non_agent()
    original_agent = original_objects[0]
    original_non_agent = original_objects[1]
    original_ball = original_objects[2]
    original_cube = original_objects[3]
    original_turntable_left = original_objects[4]
    original_turntable_right = original_objects[5]
    scene = component.update_ile_scene(scene)
    assert len(scene.objects) == 6
    agent = scene.objects[0]
    non_agent = scene.objects[1]
    ball = scene.objects[2]
    cube = scene.objects[3]
    turntable_left = scene.objects[4]
    turntable_right = scene.objects[5]
    assert agent == original_agent
    assert non_agent == original_non_agent
    assert ball == original_ball
    assert cube == original_cube
    assert turntable_left != original_turntable_left
    assert turntable_right == original_turntable_right
    assert turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 36,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }] or turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 36,
        'vector': {'x': 0, 'y': -5, 'z': 0}
    }] or turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 28,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }]
    assert 'rotates' not in turntable_right


def test_turntables_with_agent_and_non_agent_with_mirrored_rotation():
    component = ShortcutComponent({
        'turntables_with_agent_and_non_agent': {
            'agent_label': 'agent',
            'non_agent_label': 'non_agent',
            'turntable_labels': 'turntables',
            'direction_labels': 'directions'
        }
    })
    assert component.turntables_with_agent_and_non_agent
    scene, original_objects = setup_turntables_with_agent_and_non_agent()
    original_agent = original_objects[0]
    original_non_agent = original_objects[1]
    original_ball = original_objects[2]
    original_cube = original_objects[3]
    original_turntable_left = original_objects[4]
    original_turntable_right = original_objects[5]
    # Override non-agent rotation and set mirroredRotation.
    scene.objects[1]['shows'][0]['rotation']['y'] = -90
    scene.objects[1]['debug']['mirroredRotation'] = 0
    original_non_agent = copy.deepcopy(scene.objects[1])
    scene = component.update_ile_scene(scene)
    assert len(scene.objects) == 6
    agent = scene.objects[0]
    non_agent = scene.objects[1]
    ball = scene.objects[2]
    cube = scene.objects[3]
    turntable_left = scene.objects[4]
    turntable_right = scene.objects[5]
    assert agent == original_agent
    assert non_agent == original_non_agent
    assert ball == original_ball
    assert cube == original_cube
    assert turntable_left != original_turntable_left
    assert turntable_right == original_turntable_right
    assert turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 36,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }] or turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 36,
        'vector': {'x': 0, 'y': -5, 'z': 0}
    }] or turntable_left['rotates'] == [{
        'stepBegin': 1,
        'stepEnd': 28,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }]
    assert 'rotates' not in turntable_right


def test_turntables_with_agent_and_non_agent_with_point_step_begin_before_46():
    component = ShortcutComponent({
        'turntables_with_agent_and_non_agent': {
            'agent_label': 'agent',
            'non_agent_label': 'non_agent',
            'turntable_labels': 'turntables',
            'direction_labels': 'directions'
        }
    })
    assert component.turntables_with_agent_and_non_agent
    # Start agent point before step 46.
    scene, original_objects = setup_turntables_with_agent_and_non_agent(43)
    original_agent = original_objects[0]
    original_non_agent = original_objects[1]
    original_ball = original_objects[2]
    original_cube = original_objects[3]
    original_turntable_left = original_objects[4]
    original_turntable_right = original_objects[5]
    scene = component.update_ile_scene(scene)
    assert len(scene.objects) == 6
    agent = scene.objects[0]
    non_agent = scene.objects[1]
    ball = scene.objects[2]
    cube = scene.objects[3]
    turntable_left = scene.objects[4]
    turntable_right = scene.objects[5]
    assert agent == original_agent
    assert non_agent == original_non_agent
    assert ball == original_ball
    assert cube == original_cube
    assert turntable_left != original_turntable_left
    assert turntable_right == original_turntable_right
    assert turntable_left['rotates'] == [{
        'stepBegin': 51,
        'stepEnd': 86,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }] or turntable_left['rotates'] == [{
        'stepBegin': 51,
        'stepEnd': 86,
        'vector': {'x': 0, 'y': -5, 'z': 0}
    }] or turntable_left['rotates'] == [{
        'stepBegin': 51,
        'stepEnd': 78,
        'vector': {'x': 0, 'y': 5, 'z': 0}
    }]
    assert 'rotates' not in turntable_right


def test_shortcut_tool_choice_too_small():
    component = ShortcutComponent({
        'shortcut_tool_choice': True
    })
    assert component.shortcut_tool_choice
    assert component.get_shortcut_tool_choice()
    scene = prior_scene_custom_size(14, 15)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    scene = prior_scene_custom_size(15, 12)
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


def test_shortcut_tool_choice_default():
    component = ShortcutComponent({
        'shortcut_tool_choice': True
    })
    assert component.shortcut_tool_choice
    assert component.get_shortcut_tool_choice()
    scene = prior_scene_custom_size(20, 20)

    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    assert len(lavas) > 0
    assert len(lavas) % 2 == 0

    for square in lavas:
        assert (square.x > 1 or square.x < -1)
        assert (square.x < 9 or square.x > -9)
        assert (square.z > 0)

    assert scene.goal.metadata['target']
    assert 'targets' not in scene.goal.metadata
    assert scene.goal.action_list
    assert len(scene.goal.action_list) == 36
    for action in scene.goal.action_list:
        assert action == ['RotateRight']

    objs = scene.objects
    assert len(objs) == 4 or len(objs) == 5

    platform = objs[0]
    soccer_balls = list(filter(lambda obj: obj['type'] == 'soccer_ball', objs))
    assert len(soccer_balls) == 2
    ball_1 = soccer_balls[0]
    ball_2 = soccer_balls[1]
    tool_list = list(
        filter(
            lambda obj: obj['type'].startswith('tool_rect'),
            objs))
    assert len(tool_list) == 2
    tool_1 = tool_list[0]
    tool_2 = tool_list[1] if len(tool_list) == 2 else None

    # check platform properties and all object types
    assert platform['type'] == 'cube'
    assert platform['shows'][0]['position'] == {
        'x': 0, 'y': 0.5, 'z': 0}

    # ensure x axis of tool position for any tool matches that of target
    ball_1_pos = ball_1['shows'][0]['position']
    ball_2_pos = ball_2['shows'][0]['position']
    tool_1_pos = tool_1['shows'][0]['position']
    assert (ball_1_pos['x'] == tool_1_pos['x'] or (
        ball_1_pos['x'] == tool_2['shows'][0]['position']['x'] if tool_2 is not None else False))  # noqa
    assert (ball_2_pos['x'] == tool_1_pos['x'] or (
        ball_2_pos['x'] == tool_2['shows'][0]['position']['x'] if tool_2 is not None else False))  # noqa


def test_shortcut_tool_choice_too_short():
    component = ShortcutComponent({
        'shortcut_tool_choice': {
            'improbable_option': 'too_short'
        }
    })

    assert component.shortcut_tool_choice
    assert component.get_shortcut_tool_choice()
    scene = prior_scene_custom_size(20, 20)

    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    assert len(lavas) > 0
    assert len(lavas) % 2 == 0

    for square in lavas:
        assert (square.x > 1 or square.x < -1)
        assert (square.x < 9 or square.x > -9)
        assert (square.z > 0)

    assert scene.goal.metadata['target']
    assert 'targets' not in scene.goal.metadata
    assert scene.goal.action_list
    assert len(scene.goal.action_list) == 36
    for action in scene.goal.action_list:
        assert action == ['RotateRight']

    objs = scene.objects
    assert len(objs) == 5

    platform = objs[0]
    soccer_balls = list(filter(lambda obj: obj['type'] == 'soccer_ball', objs))
    assert len(soccer_balls) == 2
    ball_1 = soccer_balls[0]
    ball_2 = soccer_balls[1]
    tool_list = list(
        filter(
            lambda obj: obj['type'].startswith('tool_rect'),
            objs))
    assert len(tool_list) == 2
    tool_1 = tool_list[0]
    tool_2 = tool_list[1]

    # check platform properties and all object types
    assert platform['type'] == 'cube'
    assert platform['shows'][0]['position'] == {
        'x': 0, 'y': 0.5, 'z': 0}
    assert (tool_1['type'].endswith('x_1_00') or
            tool_2['type'].endswith('x_1_00'))
    assert (not tool_1['type'].endswith('x_1_00') or
            not tool_2['type'].endswith('x_1_00'))

    # ensure x axis of tool position for any tool matches that of
    # target, and that soccer_balls and tools are placed on
    # opposite x coordinates
    ball_1_pos = ball_1['shows'][0]['position']
    ball_2_pos = ball_2['shows'][0]['position']
    tool_1_pos = tool_1['shows'][0]['position']
    tool_2_pos = tool_2['shows'][0]['position']
    assert (ball_1_pos['x'] == tool_1_pos['x'] or
            ball_1_pos['x'] == tool_2_pos['x'])
    assert (ball_2_pos['x'] == tool_1_pos['x'] or
            ball_2_pos['x'] == tool_2_pos['x'])
    assert ball_1_pos['x'] == (ball_2_pos['x'] * -1)
    assert ball_1_pos['y'] == ball_2_pos['y']
    assert ball_1_pos['z'] == ball_2_pos['z']
    assert tool_1_pos['x'] == (tool_2_pos['x'] * -1)


def test_shortcut_tool_choice_no_tool():
    component = ShortcutComponent({
        'shortcut_tool_choice': {
            'improbable_option': 'no_tool'
        }
    })

    assert component.shortcut_tool_choice
    assert component.get_shortcut_tool_choice()
    scene = prior_scene_custom_size(20, 20)

    scene = component.update_ile_scene(scene)
    lavas = scene.lava
    assert len(lavas) > 0
    assert len(lavas) % 2 == 0

    for square in lavas:
        assert (square.x > 1 or square.x < -1)
        assert (square.x < 9 or square.x > -9)
        assert (square.z > 0)

    assert scene.goal.metadata['target']
    assert 'targets' not in scene.goal.metadata
    assert scene.goal.action_list
    assert len(scene.goal.action_list) == 36
    for action in scene.goal.action_list:
        assert action == ['RotateRight']

    objs = scene.objects
    assert len(objs) == 4

    platform = objs[0]
    ball_1 = objs[1]
    ball_2 = objs[2]
    tool = objs[3]

    # check platform properties and all object types
    assert platform['type'] == 'cube'
    assert platform['shows'][0]['position'] == {
        'x': 0, 'y': 0.5, 'z': 0}
    assert ball_1['type'] == 'soccer_ball'
    assert ball_2['type'] == 'soccer_ball'
    assert tool['type'].startswith('tool_rect')
    assert (not tool['type'].endswith('x_1_00'))

    # ensure x axis of tool position for any tool matches one of
    # the soccer balls
    ball_1_pos = ball_1['shows'][0]['position']
    ball_2_pos = ball_2['shows'][0]['position']
    tool_pos = tool['shows'][0]['position']
    assert (ball_1_pos['x'] == tool_pos['x'] or
            ball_2_pos['x'] == tool_pos['x'])
    assert ball_1_pos['x'] == (ball_2_pos['x'] * -1)
    assert ball_1_pos['y'] == ball_2_pos['y']
    assert ball_1_pos['z'] == ball_2_pos['z']


def test_shortcut_imitation_left_side_teleport_containers_rotation_left_right():  # noqa
    component = ShortcutComponent({
        'shortcut_imitation_task': {
            'trigger_order': 'left_right',
            'containers_on_right_side': False,
            'kidnap_option': 'containers'
        }
    })

    assert component.shortcut_imitation_task
    assert component.shortcut_imitation_task.containers_on_right_side is False
    assert component.shortcut_imitation_task.kidnap_option == 'containers'
    assert component.shortcut_imitation_task.trigger_order == 'left_right'

    scene = component.update_ile_scene(prior_scene())

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert scene.goal.category == 'imitation'
    assert scene.goal.description == (
        'Open the containers in the correct order for '
        'the tiny light black white rubber ball to be placed.')
    assert len(scene.goal.triggered_by_target_sequence) == 2
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[0]['id']
    # right container
    assert scene.goal.triggered_by_target_sequence[1] == scene.objects[2]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config
    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0
    assert scene.debug['endHabituationStep'] == kidnapp_step

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[0]['shows']
    teleport_rotation = containers[0]['shows'][1]['rotation']['y']
    first_container_teleport_position = containers[0]['shows'][1]['position']
    start_x = first_container_teleport_position['x']
    start_z = first_container_teleport_position['z']
    teleport_positions = []
    teleport_positions.append((start_x, start_z))
    for _ in range(1, 3):
        x, z = \
            get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
                teleport_rotation, -IMITATION_CONTAINER_SEPARATION, 0)
        start_x += x
        start_z += z
        teleport_positions.append((start_x, start_z))
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == (i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == 90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1

        teleport = containers[i]['shows'][1]
        assert teleport['position']['x'] == teleport_positions[i][0]
        assert teleport['position']['z'] == teleport_positions[i][1]
        assert teleport['rotation']['y'] in IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL  # noqa
        assert teleport['rotation']['y'] == teleport_rotation
        assert containers[i]['shows'][1]['stepBegin'] == kidnapp_step
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[0]['openClose'][0]['step'] == 22
    assert containers[0]['openClose'][0]['open'] is True
    assert containers[0]['openClose'][1]['step'] == kidnapp_step
    assert containers[0]['openClose'][1]['open'] is False
    assert containers[1].get('openClose') is None  # middle container
    assert containers[2]['openClose'][0]['step'] == 97
    assert containers[2]['openClose'][0]['open'] is True
    assert containers[2]['openClose'][1]['step'] == kidnapp_step
    assert containers[2]['openClose'][1]['open'] is False
    # left container is in view after rotation, it tells us if the other
    # containers are in view because they are in a straight line
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert min_max[0] <= scene.objects[0]['shows'][1]['position']['x'] \
        <= min_max[1]
    agent_stand_behind_buffer = 1
    assert 0 <= scene.objects[0]['shows'][1]['position']['z'] <= \
        scene.room_dimensions.z / 2 - agent_stand_behind_buffer

    # target
    x, z = \
        get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
            teleport_rotation, -IMITATION_TASK_TARGET_SEPARATION, 0)
    x = first_container_teleport_position['x'] - x
    z = first_container_teleport_position['z'] - z
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == x
    assert target['shows'][1]['position']['z'] == z
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == x
    assert placer['shows'][1]['position']['z'] == z
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 26
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == IMITATION_AGENT_START_X
    assert start['position']['z'] == -1  # left chest
    assert start['rotation']['y'] == -90  # face right
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    assert teleport['rotation']['y'] == 180  # face performer
    # behind containers
    separation = 1
    max_container_z = \
        max(containers, key=lambda c: c['shows'][1]['position']['z'])[
            'shows'][1]['position']['z']
    assert teleport['position']['z'] == max_container_z + separation
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        containers[0]['shows'][1]['rotation']['y'])
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert (
        teleport['position']['x'] == min_max[0] - separation or
        teleport['position']['x'] == min_max[1] + separation)
    assert len(agent['rotates']) == 1
    assert agent['rotates'][0]['stepBegin'] == 83
    # left rotation because agent is walking torward perfromer
    assert agent['rotates'][0]['vector']['y'] == -9
    # opening containers sequence
    animations = agent['actions']
    assert len(animations) == 3
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    assert animations[1]['id'] == 'TPM_turnL45'
    assert animations[1]['stepBegin'] == 83
    assert animations[1]['stepEnd'] == 93
    assert animations[2]['id'] == 'TPE_jump'
    assert animations[2]['stepBegin'] == 93
    assert animations[2]['stepEnd'] == 103
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 3
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] ==
            movement['sequence'][2]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] ==
            movement['sequence'][2]['endPoint']['x'] == -IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == -1.0  # left
    assert movement['sequence'][1]['endPoint']['z'] == 1.0  # right
    assert movement['sequence'][2]['endPoint']['z'] == 0.85  # face performer


def test_shortcut_imitation_right_side_teleport_containers_rotation_left_right():  # noqa
    component = ShortcutComponent({
        'shortcut_imitation_task': {
            'trigger_order': 'left_right',
            'containers_on_right_side': True,
            'kidnap_option': 'containers'
        }
    })

    assert component.shortcut_imitation_task
    assert component.shortcut_imitation_task.containers_on_right_side is True
    assert component.shortcut_imitation_task.kidnap_option == \
        'containers'
    assert component.shortcut_imitation_task.trigger_order == 'left_right'

    scene = component.update_ile_scene(prior_scene())

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert scene.goal.category == 'imitation'
    assert scene.goal.description == (
        'Open the containers in the correct order for '
        'the tiny light black white rubber ball to be placed.')
    assert len(scene.goal.triggered_by_target_sequence) == 2
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[0]['id']
    # right container
    assert scene.goal.triggered_by_target_sequence[1] == scene.objects[2]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config
    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0
    assert scene.debug['endHabituationStep'] == kidnapp_step

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[-1]['shows']
    teleport_rotation = containers[0]['shows'][1]['rotation']['y']
    first_container_teleport_position = containers[0]['shows'][1]['position']
    start_x = first_container_teleport_position['x']
    start_z = first_container_teleport_position['z']
    teleport_positions = []
    teleport_positions.append((start_x, start_z))
    for _ in range(1, 3):
        x, z = \
            get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
                teleport_rotation, IMITATION_CONTAINER_SEPARATION, 0)
        start_x -= x
        start_z -= z
        teleport_positions.append((start_x, start_z))
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == -(i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == -90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1

        teleport = containers[i]['shows'][1]
        assert round(
            teleport['position']['x'], 3) == round(
            teleport_positions[i][0], 3)
        assert round(
            teleport['position']['z'], 3) == round(
            teleport_positions[i][1], 3)
        assert teleport['rotation']['y'] in IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL  # noqa
        assert teleport['rotation']['y'] == teleport_rotation
        assert containers[i]['shows'][1]['stepBegin'] == kidnapp_step
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[0]['openClose'][0]['step'] == 22
    assert containers[0]['openClose'][0]['open'] is True
    assert containers[0]['openClose'][1]['step'] == kidnapp_step
    assert containers[0]['openClose'][1]['open'] is False
    assert containers[1].get('openClose') is None  # middle container
    assert containers[2]['openClose'][0]['step'] == 96
    assert containers[2]['openClose'][0]['open'] is True
    assert containers[2]['openClose'][1]['step'] == kidnapp_step
    assert containers[2]['openClose'][1]['open'] is False
    # left container is in view after rotation, it tells us if the other
    # containers are in view because they are in a straight line
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert min_max[0] <= scene.objects[0]['shows'][1]['position']['x'] \
        <= min_max[1]
    agent_stand_behind_buffer = 1
    assert 0 <= scene.objects[0]['shows'][1]['position']['z'] <= \
        scene.room_dimensions.z / 2 - agent_stand_behind_buffer

    # target
    x, z = \
        get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
            teleport_rotation, IMITATION_TASK_TARGET_SEPARATION, 0)
    x = end_container[1]['position']['x'] - x
    z = end_container[1]['position']['z'] - z
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == x
    assert target['shows'][1]['position']['z'] == z
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == x
    assert placer['shows'][1]['position']['z'] == z
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 26
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == -IMITATION_AGENT_START_X
    assert start['position']['z'] == 1  # left chest
    assert start['rotation']['y'] == 90  # face right
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    assert teleport['rotation']['y'] == 180  # face performer
    # behind containers
    separation = 1
    max_container_z = \
        max(containers, key=lambda c: c['shows'][1]['position']['z'])[
            'shows'][1]['position']['z']
    assert teleport['position']['z'] == max_container_z + separation
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert (
        teleport['position']['x'] == min_max[0] - separation or
        teleport['position']['x'] == min_max[1] + separation)
    assert len(agent['rotates']) == 1
    assert agent['rotates'][0]['stepBegin'] == 82
    # left rotation because agent is walking torward perfromer
    assert agent['rotates'][0]['vector']['y'] == -9
    # opening containers sequence
    animations = agent['actions']
    assert len(animations) == 3
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    assert animations[1]['id'] == 'TPM_turnL45'
    assert animations[1]['stepBegin'] == 82
    assert animations[1]['stepEnd'] == 92
    assert animations[2]['id'] == 'TPE_jump'
    assert animations[2]['stepBegin'] == 92
    assert animations[2]['stepEnd'] == 102
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 3
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] ==
            movement['sequence'][2]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] ==
            movement['sequence'][2]['endPoint']['x'] == IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == 1.0  # left
    assert movement['sequence'][1]['endPoint']['z'] == -1.0  # right
    assert movement['sequence'][2]['endPoint']['z'] == -1.15  # face performer


def test_shortcut_imitation_left_side_teleport_containers_right_middle():
    component = ShortcutComponent({
        'shortcut_imitation_task': {
            'trigger_order': 'right_middle',
            'containers_on_right_side': False,
            'kidnap_option': 'containers'
        }
    })

    assert component.shortcut_imitation_task
    assert component.shortcut_imitation_task.containers_on_right_side is False
    assert component.shortcut_imitation_task.kidnap_option == \
        'containers'
    assert component.shortcut_imitation_task.trigger_order == 'right_middle'

    scene = component.update_ile_scene(prior_scene())

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert scene.goal.category == 'imitation'
    assert scene.goal.description == (
        'Open the containers in the correct order for '
        'the tiny light black white rubber ball to be placed.')
    assert len(scene.goal.triggered_by_target_sequence) == 2
    # right container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[2]['id']
    # middle container
    assert scene.goal.triggered_by_target_sequence[1] == scene.objects[1]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config
    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0
    assert scene.debug['endHabituationStep'] == kidnapp_step

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[0]['shows']
    teleport_rotation = containers[0]['shows'][1]['rotation']['y']
    first_container_teleport_position = containers[0]['shows'][1]['position']
    start_x = first_container_teleport_position['x']
    start_z = first_container_teleport_position['z']
    teleport_positions = []
    teleport_positions.append((start_x, start_z))
    for _ in range(1, 3):
        x, z = \
            get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
                teleport_rotation, -IMITATION_CONTAINER_SEPARATION, 0)
        start_x += x
        start_z += z
        teleport_positions.append((start_x, start_z))
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == (i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == 90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1

        teleport = containers[i]['shows'][1]
        assert teleport['position']['x'] == teleport_positions[i][0]
        assert teleport['position']['z'] == teleport_positions[i][1]
        assert teleport['rotation']['y'] in IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL  # noqa
        assert teleport['rotation']['y'] == teleport_rotation
        assert containers[i]['shows'][1]['stepBegin'] == kidnapp_step
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[2]['openClose'][0]['step'] == 22
    assert containers[2]['openClose'][0]['open'] is True
    assert containers[2]['openClose'][1]['step'] == kidnapp_step
    assert containers[2]['openClose'][1]['open'] is False
    assert containers[0].get('openClose') is None  # left container
    assert containers[1]['openClose'][0]['step'] == 71
    assert containers[1]['openClose'][0]['open'] is True
    assert containers[1]['openClose'][1]['step'] == kidnapp_step
    assert containers[1]['openClose'][1]['open'] is False
    # left container is in view after rotation, it tells us if the other
    # containers are in view because they are in a straight line
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert min_max[0] <= scene.objects[0]['shows'][1]['position']['x'] \
        <= min_max[1]
    agent_stand_behind_buffer = 1
    assert 0 <= scene.objects[0]['shows'][1]['position']['z'] <= \
        scene.room_dimensions.z / 2 - agent_stand_behind_buffer

    # target
    x, z = \
        get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
            teleport_rotation, -IMITATION_TASK_TARGET_SEPARATION, 0)
    x = first_container_teleport_position['x'] - x
    z = first_container_teleport_position['z'] - z
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == x
    assert target['shows'][1]['position']['z'] == z
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == x
    assert placer['shows'][1]['position']['z'] == z
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 26
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == IMITATION_AGENT_START_X
    assert start['position']['z'] == 1  # right chest
    assert start['rotation']['y'] == -90  # face left
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    assert teleport['rotation']['y'] == 180  # face performer
    # behind containers
    separation = 1
    max_container_z = \
        max(containers, key=lambda c: c['shows'][1]['position']['z'])[
            'shows'][1]['position']['z']
    assert teleport['position']['z'] == max_container_z + separation
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert (
        teleport['position']['x'] == min_max[0] - separation or
        teleport['position']['x'] == min_max[1] + separation)
    assert len(agent['rotates']) == 1
    assert agent['rotates'][0]['stepBegin'] == 57
    # left rotation because agent is walking torward perfromer
    assert agent['rotates'][0]['vector']['y'] == 9
    # opening containers sequence
    animations = agent['actions']
    assert len(animations) == 3
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    assert animations[1]['id'] == 'TPM_turnR45'
    assert animations[1]['stepBegin'] == 57
    assert animations[1]['stepEnd'] == 67
    assert animations[2]['id'] == 'TPE_jump'
    assert animations[2]['stepBegin'] == 67
    assert animations[2]['stepEnd'] == 77
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 3
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] ==
            movement['sequence'][2]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] ==
            movement['sequence'][2]['endPoint']['x'] == -IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == 1.0  # right
    assert movement['sequence'][1]['endPoint']['z'] == 0.0  # middle
    assert movement['sequence'][2]['endPoint']['z'] == -0.15  # face performer


def test_shortcut_imitation_right_side_teleport_containers_right_middle():
    component = ShortcutComponent({
        'shortcut_imitation_task': {
            'trigger_order': 'right_middle',
            'containers_on_right_side': True,
            'kidnap_option': 'containers'
        }
    })

    assert component.shortcut_imitation_task
    assert component.shortcut_imitation_task.containers_on_right_side is True
    assert component.shortcut_imitation_task.kidnap_option == \
        'containers'
    assert component.shortcut_imitation_task.trigger_order == 'right_middle'

    scene = component.update_ile_scene(prior_scene())

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert scene.goal.category == 'imitation'
    assert scene.goal.description == (
        'Open the containers in the correct order for '
        'the tiny light black white rubber ball to be placed.')
    assert len(scene.goal.triggered_by_target_sequence) == 2
    # right container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[2]['id']
    # middle container
    assert scene.goal.triggered_by_target_sequence[1] == scene.objects[1]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')
    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config
    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0
    assert scene.debug['endHabituationStep'] == kidnapp_step

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[-1]['shows']
    teleport_rotation = containers[0]['shows'][1]['rotation']['y']
    first_container_teleport_position = containers[0]['shows'][1]['position']
    start_x = first_container_teleport_position['x']
    start_z = first_container_teleport_position['z']
    teleport_positions = []
    teleport_positions.append((start_x, start_z))
    for _ in range(1, 3):
        x, z = \
            get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
                teleport_rotation, IMITATION_CONTAINER_SEPARATION, 0)
        start_x -= x
        start_z -= z
        teleport_positions.append((start_x, start_z))
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == -(i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == -90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1

        teleport = containers[i]['shows'][1]
        assert round(
            teleport['position']['x'], 3) == round(
            teleport_positions[i][0], 3)
        assert round(
            teleport['position']['z'], 3) == round(
            teleport_positions[i][1], 3)
        assert teleport['rotation']['y'] in IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL  # noqa
        assert teleport['rotation']['y'] == teleport_rotation
        assert containers[i]['shows'][1]['stepBegin'] == kidnapp_step
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[2]['openClose'][0]['step'] == 22
    assert containers[2]['openClose'][0]['open'] is True
    assert containers[2]['openClose'][1]['step'] == kidnapp_step
    assert containers[2]['openClose'][1]['open'] is False
    assert containers[0].get('openClose') is None  # left container
    assert containers[1]['openClose'][0]['step'] == 71
    assert containers[1]['openClose'][0]['open'] is True
    assert containers[1]['openClose'][1]['step'] == kidnapp_step
    assert containers[1]['openClose'][1]['open'] is False
    # left container is in view after rotation, it tells us if the other
    # containers are in view because they are in a straight line
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert min_max[0] <= scene.objects[0]['shows'][1]['position']['x'] \
        <= min_max[1]
    agent_stand_behind_buffer = 1
    assert 0 <= scene.objects[0]['shows'][1]['position']['z'] <= \
        scene.room_dimensions.z / 2 - agent_stand_behind_buffer

    # target
    x, z = \
        get_magnitudes_of_x_z_dirs_for_rotation_and_move_vector(
            teleport_rotation, IMITATION_TASK_TARGET_SEPARATION, 0)
    x = end_container[1]['position']['x'] - x
    z = end_container[1]['position']['z'] - z
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == x
    assert target['shows'][1]['position']['z'] == z
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == x
    assert placer['shows'][1]['position']['z'] == z
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 26
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == -IMITATION_AGENT_START_X
    assert start['position']['z'] == -1  # left chest
    assert start['rotation']['y'] == 90  # face right
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    assert teleport['rotation']['y'] == 180  # face performer
    # behind containers
    separation = 1
    max_container_z = \
        max(containers, key=lambda c: c['shows'][1]['position']['z'])[
            'shows'][1]['position']['z']
    assert teleport['position']['z'] == max_container_z + separation
    index = IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL.index(
        teleport_rotation)
    min_max = IMITATION_CONTAINER_TELEPORT_X_POS_RANGE[index]
    assert (
        teleport['position']['x'] == min_max[0] - separation or
        teleport['position']['x'] == min_max[1] + separation)
    assert len(agent['rotates']) == 1
    assert agent['rotates'][0]['stepBegin'] == 57
    # left rotation because agent is walking torward perfromer
    assert agent['rotates'][0]['vector']['y'] == 9
    # opening containers sequence
    animations = agent['actions']
    assert len(animations) == 3
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    assert animations[1]['id'] == 'TPM_turnR45'
    assert animations[1]['stepBegin'] == 57
    assert animations[1]['stepEnd'] == 67
    assert animations[2]['id'] == 'TPE_jump'
    assert animations[2]['stepBegin'] == 67
    assert animations[2]['stepEnd'] == 77
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 3
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] ==
            movement['sequence'][2]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] ==
            movement['sequence'][2]['endPoint']['x'] == IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == -1.0  # right
    assert movement['sequence'][1]['endPoint']['z'] == 0.0  # middle
    assert movement['sequence'][2]['endPoint']['z'] == -0.15  # face performer


def test_shortcut_imitation_left_side_teleport_performer_left():
    component = ShortcutComponent({
        'shortcut_imitation_task': {
            'trigger_order': 'left',
            'containers_on_right_side': False,
            'kidnap_option': 'performer'
        }
    })

    assert component.shortcut_imitation_task
    assert component.shortcut_imitation_task.containers_on_right_side is False
    assert component.shortcut_imitation_task.kidnap_option == \
        'performer'
    assert component.shortcut_imitation_task.trigger_order == 'left'

    scene = component.update_ile_scene(prior_scene())

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert scene.goal.category == 'imitation'
    assert scene.goal.description == (
        'Open the containers in the correct order for '
        'the tiny light black white rubber ball to be placed.')
    assert len(scene.goal.triggered_by_target_sequence) == 1
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[0]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config

    shift = 2.5
    neg_range_x = (-scene.room_dimensions.x / 2 - PERFORMER_WIDTH, -shift)
    pos_range_x = (shift, scene.room_dimensions.x / 2 - PERFORMER_WIDTH)
    neg_range_z = (-scene.room_dimensions.z / 2 - PERFORMER_WIDTH, -shift)
    pos_range_z = (shift, scene.room_dimensions.z / 2 - PERFORMER_WIDTH)
    assert (
        (neg_range_x[0] <= scene.debug['endHabituationTeleportPositionX'] <=
         neg_range_x[1]) or
        (pos_range_x[0] <= scene.debug['endHabituationTeleportPositionX'] <=
         pos_range_x[1])
    )
    assert (
        (neg_range_z[0] <= scene.debug['endHabituationTeleportPositionZ'] <=
         neg_range_z[1]) or
        (pos_range_z[0] <= scene.debug['endHabituationTeleportPositionZ'] <=
         pos_range_z[1])
    )
    _, rotation_y = calculate_rotations(
        Vector3d(
            x=scene.debug['endHabituationTeleportPositionX'],
            y=0,
            z=scene.debug['endHabituationTeleportPositionZ']),
        Vector3d(x=0, y=0, z=0)
    )
    assert scene.debug['endHabituationTeleportRotationY'] == rotation_y

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[0]['shows']
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == (i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == 90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[1].get('openClose') is None  # middle container
    assert containers[2].get('openClose') is None  # right container
    assert containers[0]['openClose'][0]['step'] == 22
    assert containers[0]['openClose'][0]['open'] is True
    assert containers[0]['openClose'][1]['step'] == kidnapp_step
    assert containers[0]['openClose'][1]['open'] is False

    # target
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 26
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == IMITATION_AGENT_START_X
    assert start['position']['z'] == -1  # left chest
    assert start['rotation']['y'] == -90  # face right
    # move agent after kidnapp
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    agent_z_choices = (-2, 2)
    agent_x_range = (-2, 2)
    assert teleport['rotation']['y'] == \
        (180 if teleport['position']['z'] > 0 else 0)
    assert teleport['position']['z'] == \
        agent_z_choices[0] or teleport['position']['z'] == agent_z_choices[1]
    assert agent_x_range[0] <= teleport['position']['x'] <= agent_x_range[1]

    # opening containers sequence
    assert agent.get('rotates') is None
    animations = agent['actions']
    assert len(animations) == 1
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 2
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] == -IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == -1  # left
    assert movement['sequence'][1]['endPoint']['z'] == -1.15  # face performer


def test_shortcut_imitation_right_side_teleport_performer_right():
    component = ShortcutComponent({
        'shortcut_imitation_task': {
            'trigger_order': 'right',
            'containers_on_right_side': True,
            'kidnap_option': 'performer'
        }
    })

    assert component.shortcut_imitation_task
    assert component.shortcut_imitation_task.containers_on_right_side is True
    assert component.shortcut_imitation_task.kidnap_option == \
        'performer'
    assert component.shortcut_imitation_task.trigger_order == 'right'

    scene = component.update_ile_scene(prior_scene())

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert scene.goal.category == 'imitation'
    assert scene.goal.description == (
        'Open the containers in the correct order for '
        'the tiny light black white rubber ball to be placed.')
    assert len(scene.goal.triggered_by_target_sequence) == 1
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[2]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config

    shift = 2.5
    neg_range_x = (-scene.room_dimensions.x / 2 - PERFORMER_WIDTH, -shift)
    pos_range_x = (shift, scene.room_dimensions.x / 2 - PERFORMER_WIDTH)
    neg_range_z = (-scene.room_dimensions.z / 2 - PERFORMER_WIDTH, -shift)
    pos_range_z = (shift, scene.room_dimensions.z / 2 - PERFORMER_WIDTH)
    assert (
        (neg_range_x[0] <= scene.debug['endHabituationTeleportPositionX'] <=
         neg_range_x[1]) or
        (pos_range_x[0] <= scene.debug['endHabituationTeleportPositionX'] <=
         pos_range_x[1])
    )
    assert (
        (neg_range_z[0] <= scene.debug['endHabituationTeleportPositionZ'] <=
         neg_range_z[1]) or
        (pos_range_z[0] <= scene.debug['endHabituationTeleportPositionZ'] <=
         pos_range_z[1])
    )
    _, rotation_y = calculate_rotations(
        Vector3d(
            x=scene.debug['endHabituationTeleportPositionX'],
            y=0,
            z=scene.debug['endHabituationTeleportPositionZ']),
        Vector3d(x=0, y=0, z=0)
    )
    assert scene.debug['endHabituationTeleportRotationY'] == rotation_y

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[-1]['shows']
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == -(i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == -90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[0].get('openClose') is None  # left container
    assert containers[1].get('openClose') is None  # middle container
    assert containers[2]['openClose'][0]['step'] == 22
    assert containers[2]['openClose'][0]['open'] is True
    assert containers[2]['openClose'][1]['step'] == kidnapp_step
    assert containers[2]['openClose'][1]['open'] is False

    # target
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 26
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == -IMITATION_AGENT_START_X
    assert start['position']['z'] == -1  # right chest
    assert start['rotation']['y'] == 90  # face right
    # move agent after kidnapp
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    agent_z_choices = (-2, 2)
    agent_x_range = (-2, 2)
    assert teleport['rotation']['y'] == \
        (180 if teleport['position']['z'] > 0 else 0)
    assert teleport['position']['z'] == \
        agent_z_choices[0] or teleport['position']['z'] == agent_z_choices[1]
    assert agent_x_range[0] <= teleport['position']['x'] <= agent_x_range[1]

    # opening containers sequence
    assert agent.get('rotates') is None
    animations = agent['actions']
    assert len(animations) == 1


def test_shortcut_imitation_left_side_middle():
    component = ShortcutComponent({
        'shortcut_imitation_task': {
            'trigger_order': 'middle',
            'containers_on_right_side': False,
            'kidnap_option': 'agent_only'
        }
    })

    assert component.shortcut_imitation_task
    assert component.shortcut_imitation_task.containers_on_right_side is False
    assert component.shortcut_imitation_task.kidnap_option == \
        'agent_only'
    assert component.shortcut_imitation_task.trigger_order == 'middle'

    scene = component.update_ile_scene(prior_scene())

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert scene.goal.category == 'imitation'
    assert scene.goal.description == (
        'Open the containers in the correct order for '
        'the tiny light black white rubber ball to be placed.')
    assert len(scene.goal.triggered_by_target_sequence) == 1
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[1]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config

    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[0]['shows']
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == (i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == 90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[0].get('openClose') is None  # left container
    assert containers[2].get('openClose') is None  # right container
    assert containers[1]['openClose'][0]['step'] == 22
    assert containers[1]['openClose'][0]['open'] is True
    assert containers[1]['openClose'][1]['step'] == kidnapp_step
    assert containers[1]['openClose'][1]['open'] is False

    # target
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 26
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == IMITATION_AGENT_START_X
    assert start['position']['z'] == 0  # middle chest
    assert start['rotation']['y'] == -90  # face left
    # move agent after kidnapp
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    agent_x_range = (-2, 2)
    assert teleport['rotation']['y'] == 180
    assert teleport['position']['z'] == 2
    assert agent_x_range[0] <= teleport['position']['x'] <= agent_x_range[1]

    # opening containers sequence
    assert agent.get('rotates') is None
    animations = agent['actions']
    assert len(animations) == 1
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 2
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] == -IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == 0  # middle
    assert movement['sequence'][1]['endPoint']['z'] == -0.15  # face performer


def test_shortcut_imitation_right_side_middle_left():
    component = ShortcutComponent({
        'shortcut_imitation_task': {
            'trigger_order': 'middle_left',
            'containers_on_right_side': True,
            'kidnap_option': 'agent_only'
        }
    })

    assert component.shortcut_imitation_task
    assert component.shortcut_imitation_task.containers_on_right_side is True
    assert component.shortcut_imitation_task.kidnap_option == \
        'agent_only'
    assert component.shortcut_imitation_task.trigger_order == 'middle_left'

    scene = component.update_ile_scene(prior_scene())

    kidnapp_step = scene.debug['endHabituationStep']

    # goal
    assert scene.goal.category == 'imitation'
    assert scene.goal.description == (
        'Open the containers in the correct order for '
        'the tiny light black white rubber ball to be placed.')
    assert len(scene.goal.triggered_by_target_sequence) == 2
    # left container
    assert scene.goal.triggered_by_target_sequence[0] == scene.objects[1]['id']
    # action list
    assert len(scene.goal.action_list) == kidnapp_step
    for i in range(kidnapp_step):
        scene.goal.action_list[i][0] == 'Pass'
    assert scene.goal.action_list[-1][0].startswith('EndHabituation')

    # rectangular room with always 3 ceiling height
    assert (scene.room_dimensions.x == scene.room_dimensions.z /
            2 or scene.room_dimensions.x == scene.room_dimensions.z * 2)
    assert 8 <= min(scene.room_dimensions.x, scene.room_dimensions.z) <= 10
    assert scene.room_dimensions.y == 3

    # performer
    assert scene.performer_start.position.x == 0
    assert scene.performer_start.position.z == -3.75
    assert scene.performer_start.rotation.y == 0
    # do NOT teleport performer for this config
    assert scene.debug['endHabituationTeleportPositionX'] == 0
    assert scene.debug['endHabituationTeleportPositionZ'] == -3.75
    assert scene.debug['endHabituationTeleportRotationY'] == 0
    assert scene.debug['endHabituationStep'] == kidnapp_step

    # objects
    assert len(scene.objects) == 6

    # containers
    colors_used = []
    containers = scene.objects[0:3]
    end_container = containers[-1]['shows']
    for i in range(3):
        colors_used.append(containers[i]['debug']['color'][0])
        assert containers[i]['shows'][0]['position']['z'] == -(i - 1)
        assert containers[i]['shows'][0]['rotation']['y'] == -90
        assert containers[i]['type'] == 'chest_1'
        assert containers[i]['shows'][0]['scale']['x'] == 1
        assert containers[i]['shows'][0]['scale']['y'] == 1
        assert containers[i]['shows'][0]['scale']['z'] == 1
    # no duplicate colors
    assert len(colors_used) == len(set(colors_used))
    # open close
    assert containers[2].get('openClose') is None  # left container
    assert containers[1]['openClose'][0]['step'] == 22
    assert containers[1]['openClose'][0]['open'] is True
    assert containers[1]['openClose'][1]['step'] == kidnapp_step
    assert containers[1]['openClose'][1]['open'] is False
    assert containers[0]['openClose'][0]['step'] == 71
    assert containers[0]['openClose'][0]['open'] is True
    assert containers[0]['openClose'][1]['step'] == kidnapp_step
    assert containers[0]['openClose'][1]['open'] is False

    # target
    target = scene.objects[3]
    assert target['triggeredBy']
    assert target['type'] == 'soccer_ball'
    assert target['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert target['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert target['shows'][1]['stepBegin'] == kidnapp_step
    assert target['kinematic']
    assert len(target['moves']) == 1
    assert target['moves'][0]['vector']['y'] == -0.25
    assert target['moves'][0]['stepBegin'] == 0
    assert target['moves'][0]['stepEnd'] == 8
    assert len(target['togglePhysics']) == 1
    assert target['togglePhysics'][0]['stepBegin'] == 14

    # placer
    placer = scene.objects[4]
    assert placer['triggeredBy']
    assert placer['type'] == 'cylinder'
    assert placer['shows'][0]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][0]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['position']['x'] == \
        end_container[0]['position']['x']
    assert placer['shows'][1]['position']['z'] == \
        end_container[0]['position']['z'] - IMITATION_TASK_TARGET_SEPARATION
    assert placer['shows'][1]['stepBegin'] == kidnapp_step
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 0
    assert placer['moves'][0]['stepEnd'] == 8
    assert placer['moves'][0]['vector']['y'] == -0.25
    assert placer['moves'][1]['stepBegin'] == 19
    assert placer['moves'][1]['stepEnd'] == 26
    assert placer['moves'][1]['vector']['y'] == 0.25
    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 14

    # agent
    agent = scene.objects[5]
    assert agent['type'].startswith('agent')
    # positions
    start = agent['shows'][0]
    assert start['position']['x'] == -IMITATION_AGENT_START_X
    assert start['position']['z'] == 0  # middle chest
    assert start['rotation']['y'] == 90  # face right
    teleport = agent['shows'][1]
    assert teleport['stepBegin'] == kidnapp_step
    assert teleport['rotation']['y'] == 180  # face performer
    # behind containers
    # of to the right or the left since the containers were rotate 90
    assert -2 <= teleport['position']['x'] <= 2
    assert teleport['position']['z'] == 2
    assert len(agent['rotates']) == 1
    assert agent['rotates'][0]['stepBegin'] == 57
    # right rotation because agent is walking torward perfromer
    assert agent['rotates'][0]['vector']['y'] == 9
    # opening containers sequence
    animations = agent['actions']
    assert len(animations) == 3
    assert animations[0]['id'] == 'TPE_jump'
    assert animations[0]['stepBegin'] == 18
    assert animations[0]['stepEnd'] == 28
    assert animations[1]['id'] == 'TPM_turnR45'
    assert animations[1]['stepBegin'] == 57
    assert animations[1]['stepEnd'] == 67
    assert animations[2]['id'] == 'TPE_jump'
    assert animations[2]['stepBegin'] == 67
    assert animations[2]['stepEnd'] == 77
    # movement
    movement = agent['agentMovement']
    assert len(movement['sequence']) == 3
    assert movement['repeat'] is False
    assert movement['stepBegin'] == 1
    assert (movement['sequence'][0]['animation'] ==
            movement['sequence'][1]['animation'] ==
            movement['sequence'][2]['animation'] == 'TPM_walk')
    assert (movement['sequence'][0]['endPoint']['x'] ==
            movement['sequence'][1]['endPoint']['x'] ==
            movement['sequence'][2]['endPoint']['x'] == IMITATION_AGENT_END_X)
    assert movement['sequence'][0]['endPoint']['z'] == 0  # middle
    assert movement['sequence'][1]['endPoint']['z'] == 1  # left
    assert movement['sequence'][2]['endPoint']['z'] == 0.85  # face performer


def test_shortcut_imitation_container_rotations():
    right_side_check = (True, IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL,
                        IMITATION_CONTAINER_TELEPORT_ROTATIONS_RIGHT_SIDE)
    left_side_check = (False, IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL,
                       IMITATION_CONTAINER_TELEPORT_ROTATIONS_LEFT_SIDE)
    for (on_right_side, global_rotations, relative_rotations) in \
            [right_side_check, left_side_check]:
        rotation_amount_with_rotation_types = (
            [(rot, 'global') for rot in global_rotations] +
            [(rot, 'relative') for rot in relative_rotations])
        for rot, rotation_type in rotation_amount_with_rotation_types:
            component = ShortcutComponent({
                'shortcut_imitation_task': {
                    'containers_on_right_side': on_right_side,
                    'kidnap_option': 'containers',
                    f'{rotation_type}_container_rotation': rot
                }
            })
            assert (
                component.shortcut_imitation_task.containers_on_right_side ==
                on_right_side)
            assert (
                component.shortcut_imitation_task.kidnap_option ==
                'containers')
            scene = component.update_ile_scene(prior_scene())
            containers = scene.objects[0:3]
            teleport_rotation = (rot if rotation_type == 'global' else
                                 ((270 if on_right_side else 90) + rot) % 360)
            assert all(
                c['shows'][1]['rotation']['y'] == teleport_rotation
                for c in containers)


def test_shortcut_imitation_container_rotations_global_override():
    right_side_check = (True, IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL,
                        IMITATION_CONTAINER_TELEPORT_ROTATIONS_RIGHT_SIDE)
    left_side_check = (False, IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL,
                       IMITATION_CONTAINER_TELEPORT_ROTATIONS_LEFT_SIDE)
    for (on_right_side, global_rotations, relative_rotations) in \
            [right_side_check, left_side_check]:
        for global_rotation in global_rotations:
            for relative_rotation in relative_rotations:
                component = ShortcutComponent({
                    'shortcut_imitation_task': {
                        'containers_on_right_side': on_right_side,
                        'kidnap_option': 'containers',
                        'global_container_rotation': global_rotation,
                        'relative_container_rotation': relative_rotation
                    }
                })
                assert (
                    component.shortcut_imitation_task.containers_on_right_side ==  # noqa
                    on_right_side)
                assert (
                    component.shortcut_imitation_task.kidnap_option ==
                    'containers')
                scene = component.update_ile_scene(prior_scene())
                containers = scene.objects[0:3]
                # Expecting global rotation to override relative rotation
                assert all(
                    c['shows'][1]['rotation']['y'] == global_rotation
                    for c in containers)


def test_shortcut_imitation_container_rotations_multiple_choices():
    right_side_check = (True, IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL,
                        IMITATION_CONTAINER_TELEPORT_ROTATIONS_RIGHT_SIDE)
    left_side_check = (False, IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL,
                       IMITATION_CONTAINER_TELEPORT_ROTATIONS_LEFT_SIDE)
    for (on_right_side, global_rotations, relative_rotations) in \
            [right_side_check, left_side_check]:
        rotation_amounts_with_rotation_types = \
            [('global', global_rotations), ('relative', relative_rotations)]
        for rotation_type, rotations in rotation_amounts_with_rotation_types:
            # make sure all rotations are randomly ran
            for i in range(25):
                component = ShortcutComponent({
                    'shortcut_imitation_task': {
                        'containers_on_right_side': on_right_side,
                        'kidnap_option': 'containers',
                        f'{rotation_type}_container_rotation': rotations
                    }
                })
                assert (
                    component.shortcut_imitation_task.containers_on_right_side ==  # noqa
                    on_right_side)
                assert (
                    component.shortcut_imitation_task.kidnap_option ==
                    'containers')
                scene = component.update_ile_scene(prior_scene())
                containers = scene.objects[0:3]
                teleport_rotation = containers[0]['shows'][1]['rotation']['y']
                global_rot = teleport_rotation
                right_side_rot = (teleport_rotation - 270) % 360
                left_side_rot = (teleport_rotation - 90) % 360
                assert (
                    global_rot in
                    IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL if
                    rotation_type == "global" else
                    right_side_rot in
                    IMITATION_CONTAINER_TELEPORT_ROTATIONS_RIGHT_SIDE if
                    on_right_side else left_side_rot in
                    IMITATION_CONTAINER_TELEPORT_ROTATIONS_LEFT_SIDE)
                assert all(
                    c['shows'][1]['rotation']['y'] == teleport_rotation
                    for c in containers)


def test_shortcut_imitation_container_rotations_only_on_container_kidnap():
    for on_right_side in [True, False]:
        for kidnap_option in ['agent_only', 'performer']:
            for rotation_type in ['global', 'relative']:
                component = ShortcutComponent({
                    'shortcut_imitation_task': {
                        'containers_on_right_side': on_right_side,
                        'kidnap_option': kidnap_option,
                        f'{rotation_type}_container_rotation': 45
                    }
                })
                assert (
                    component.shortcut_imitation_task.kidnap_option ==
                    kidnap_option
                )
                scene = component.update_ile_scene(prior_scene())
                containers = scene.objects[0:3]
                same_start_rotation = -90 if on_right_side else 90
                assert all(len(c['shows']) == 1 for c in containers)
                assert all(
                    c['shows'][0]['rotation']['y'] == same_start_rotation
                    for c in containers)


def test_shortcut_imitation_container_rotations_errors():
    global_rotations = [
        i for i in range(361) if i not in
        IMITATION_CONTAINER_TELEPORT_ROTATIONS_GLOBAL]
    right_side_relative_rotations = [
        i for i in range(361) if i not in
        IMITATION_CONTAINER_TELEPORT_ROTATIONS_RIGHT_SIDE]
    left_side_relative_rotations = [
        i for i in range(361) if i not in
        IMITATION_CONTAINER_TELEPORT_ROTATIONS_LEFT_SIDE]
    rotation_type_lists = [
        ('global', global_rotations),
        ('relative_right', right_side_relative_rotations),
        ('relative_left', left_side_relative_rotations)]

    for rotation_type, rotation_list in rotation_type_lists:
        side_conditions = (
            [True, False] if rotation_type == 'global' else
            [True] if rotation_type.endswith("right") else [False]
        )
        component_rotation_type = \
            "global" if rotation_type == "global" else "relative"
        for on_right_side in side_conditions:
            for rot in rotation_list:
                component = ShortcutComponent({
                    'shortcut_imitation_task': {
                        'containers_on_right_side': on_right_side,
                        'kidnap_option': 'containers',
                        f'{component_rotation_type}_container_rotation': rot
                    }
                })
                with pytest.raises(ILEException):
                    component.update_ile_scene(prior_scene())


def test_shortcut_imitation_true():
    component = ShortcutComponent({
        'shortcut_imitation_task': True
    })
    assert component.shortcut_imitation_task

    scene = component.update_ile_scene(prior_scene())
    # this test makes sure the fundamentals of the scene are created
    assert len(scene.objects) == 6
    assert scene.objects[0]['type'] == 'chest_1'
    assert scene.objects[1]['type'] == 'chest_1'
    assert scene.objects[2]['type'] == 'chest_1'
    assert scene.objects[3]['type'] == 'soccer_ball'
    assert scene.objects[4]['type'] == 'cylinder'
    assert scene.objects[5]['type'].startswith('agent')


def test_shortcut_imitation_failures():
    trigger_order_options = [
        'error', 'left_middle_right', 'left_right_middle', 'middle_right_left',
        'middle_left_right', 'right_middle_left', 'right_left_middle']
    for option in trigger_order_options:
        with pytest.raises(ILEException):
            ShortcutComponent({
                'shortcut_imitation_task': {
                    'trigger_order': option,
                }
            })
    with pytest.raises(ILEException):
        ShortcutComponent({
            'shortcut_imitation_task': {
                'kidnap_option': 'error'
            }
        })


def test_shortcut_imitation_options():
    trigger_order_options = [
        'left', 'middle', 'right', 'left_middle', 'left_right',
        'middle_left', 'middle_right', 'right_middle', 'right_left']
    for option in trigger_order_options:
        component = ShortcutComponent({
            'shortcut_imitation_task': {
                'trigger_order': option,
            }
        })
        assert component.shortcut_imitation_task
        assert component.shortcut_imitation_task.trigger_order == option

    kidnap_options = ['agent_only', 'containers', 'performer']
    for option in kidnap_options:
        component = ShortcutComponent({
            'shortcut_imitation_task': {
                'kidnap_option': option,
            }
        })
        assert component.shortcut_imitation_task
        assert component.shortcut_imitation_task.kidnap_option == option


def test_shortcut_lava_target_tool_offset_rectangular():
    horizontal = 1
    backward = 1
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_horizontal_offset': horizontal,
            'tool_offset_backward_from_lava': backward,
            'tool_type': 'rectangular',
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_horizontal_offset == 1
    assert \
        component.shortcut_lava_target_tool.tool_offset_backward_from_lava == 1
    assert component.shortcut_lava_target_tool.tool_type == 'rectangular'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool_pos['x'] == 1
    assert tool_pos['z'] == 0

    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool_pos['x'] == 0
    assert tool_pos['z'] == -1

    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_horizontal_offset': -1,
            'tool_offset_backward_from_lava': 1,
            'tool_type': 'rectangular',
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_horizontal_offset == -1
    assert \
        component.shortcut_lava_target_tool.tool_offset_backward_from_lava == 1
    assert component.shortcut_lava_target_tool.tool_type == 'rectangular'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool_pos['x'] == -horizontal
    assert tool_pos['z'] == 0

    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool_pos['x'] == 0
    assert tool_pos['z'] == horizontal


@pytest.mark.slow
def test_shortcut_lava_target_tool_offset_rectangular_out_of_room():
    horizontal = 100
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'tool_horizontal_offset': horizontal,
            'tool_type': 'rectangular'
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_horizontal_offset == 100
    assert component.shortcut_lava_target_tool.tool_type == 'rectangular'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)
    scene = prior_scene_custom_size(20, 15)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    horizontal = -100
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'tool_horizontal_offset': horizontal,
            'tool_type': 'rectangular'
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_horizontal_offset == -100
    assert component.shortcut_lava_target_tool.tool_type == 'rectangular'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)
    scene = prior_scene_custom_size(20, 15)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)


def test_shortcut_lava_target_tool_offset_hooked():
    horizontal = 2
    backward = 1
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_horizontal_offset': horizontal,
            'tool_offset_backward_from_lava': backward,
            'tool_type': 'hooked',
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_horizontal_offset == 2
    assert \
        component.shortcut_lava_target_tool.tool_offset_backward_from_lava == 1
    assert component.shortcut_lava_target_tool.tool_type == 'hooked'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    tool_width = tool['debug']['tool_thickness'] * 3
    tool_buffer = 1.0 - (tool_width / 3.0)
    rear_buffer = 1.0
    lava_front_to_behind_island = rear_buffer + 3
    tool_pos_increment = lava_front_to_behind_island - tool_buffer
    island_coord = 7
    front_lava_width = 2
    long_tool_pos = (
        island_coord - front_lava_width - tool['debug']['length'] / 2.0 - 0.5)
    long_tool_pos = long_tool_pos + tool_pos_increment
    short_coord = tool_buffer / 2.0
    assert tool_pos['x'] == short_coord + horizontal
    assert tool_pos['z'] == long_tool_pos - backward

    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    tool_width = tool['debug']['tool_thickness'] * 3
    tool_buffer = 1.0 - (tool_width / 3.0)
    rear_buffer = 1.0
    lava_front_to_behind_island = rear_buffer + 3
    tool_pos_increment = lava_front_to_behind_island - tool_buffer
    island_coord = 7
    front_lava_width = 2
    long_tool_pos = (
        island_coord - front_lava_width - tool['debug']['length'] / 2.0 - 0.5)
    long_tool_pos = long_tool_pos + tool_pos_increment
    short_coord = tool_buffer / 2.0
    assert tool_pos['z'] == short_coord - horizontal
    assert tool_pos['x'] == long_tool_pos - backward


def test_shortcut_lava_target_tool_small():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_type': 'small'
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_type == 'small'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool['type'].startswith('tool_rect')
    assert tool_pos['x'] == 0
    assert tool_pos['z'] == 3
    assert tool['debug']['length'] == 1

    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool['type'].startswith('tool_rect')
    assert tool_pos['x'] == 3
    assert tool_pos['z'] == 0
    assert tool['debug']['length'] == 1


def test_shortcut_lava_target_tool_offset_small():
    horizontal = 3
    backward = 3
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_horizontal_offset': horizontal,
            'tool_offset_backward_from_lava': backward,
            'tool_type': 'small',
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_horizontal_offset == \
        horizontal
    assert \
        component.shortcut_lava_target_tool.tool_offset_backward_from_lava == \
        backward
    assert component.shortcut_lava_target_tool.tool_type == 'small'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool_pos['x'] == horizontal
    assert tool_pos['z'] == 0

    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool_pos['x'] == 0
    assert tool_pos['z'] == -horizontal

    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_horizontal_offset': -horizontal,
            'tool_offset_backward_from_lava': backward,
            'tool_type': 'small',
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_horizontal_offset == \
        -horizontal
    assert \
        component.shortcut_lava_target_tool.tool_offset_backward_from_lava == \
        backward
    assert component.shortcut_lava_target_tool.tool_type == 'small'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool_pos['x'] == -horizontal
    assert tool_pos['z'] == 0
    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool_pos['x'] == 0
    assert tool_pos['z'] == horizontal


def test_shortcut_lava_target_tool_broken():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_type': 'broken'
        }
    })
    minimum = tools.BROKEN_TOOL_HORIZONTAL_SEPARATION_MIN
    maximum = tools.BROKEN_TOOL_HORIZONTAL_SEPARATION_MAX
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_type == 'broken'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool_list = objs[1:]
    assert len(tool_list) == 5
    first_tool_pos = tool_list[0]['shows'][0]['position']
    last_tool_pos = tool_list[-1]['shows'][0]['position']
    assert first_tool_pos['z'] == 3
    assert last_tool_pos['z'] == round(
        first_tool_pos['z'] -
        tools.BROKEN_TOOL_VERTICAL_SEPARATION * (len(tool_list) - 1), 2)
    for tool in tool_list:
        assert tool['type'].startswith('tool_rect')
        assert tool['debug']['length'] == 1
        pos_x = tool['shows'][0]['position']['x']
        assert \
            (-maximum <= pos_x <= -minimum) or (minimum <= pos_x <= maximum)

    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool_list = objs[1:]
    assert len(tool_list) == 5
    first_tool_pos = tool_list[0]['shows'][0]['position']
    last_tool_pos = tool_list[-1]['shows'][0]['position']
    assert first_tool_pos['x'] == 3
    assert last_tool_pos['x'] == round(
        first_tool_pos['x'] -
        tools.BROKEN_TOOL_VERTICAL_SEPARATION * (len(tool_list) - 1), 2)
    for tool in tool_list:
        assert tool['type'].startswith('tool_rect')
        assert tool['debug']['length'] == 1
        pos_z = tool['shows'][0]['position']['z']
        assert \
            (-maximum <= pos_z <= -minimum) or (minimum <= pos_z <= maximum)


def test_shortcut_lava_target_tool_broken_rotated():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_type': 'broken',
            'tool_rotation': 90
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_type == 'broken'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool_list = objs[1:]
    assert len(tool_list) == 5
    first_tool_pos = tool_list[0]['shows'][0]['position']
    last_tool_pos = tool_list[-1]['shows'][0]['position']
    assert first_tool_pos['x'] == 2
    assert last_tool_pos['x'] == round(
        first_tool_pos['x'] -
        tools.BROKEN_TOOL_VERTICAL_SEPARATION * (len(tool_list) - 1), 2)
    center_of_broken_tools = 1
    positive_x_maximum = center_of_broken_tools + \
        tools.BROKEN_TOOL_HORIZONTAL_SEPARATION_MAX
    negative_x_maximum = center_of_broken_tools - \
        tools.BROKEN_TOOL_HORIZONTAL_SEPARATION_MAX
    for tool in tool_list:
        assert tool['type'].startswith('tool_rect')
        assert tool['debug']['length'] == 1
        pos_z = tool['shows'][0]['position']['z']
        assert negative_x_maximum <= pos_z <= positive_x_maximum

    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool_list = objs[1:]
    assert len(tool_list) == 5
    first_tool_pos = tool_list[0]['shows'][0]['position']
    last_tool_pos = tool_list[-1]['shows'][0]['position']
    assert first_tool_pos['z'] == -2
    assert last_tool_pos['z'] == round(
        first_tool_pos['z'] +
        tools.BROKEN_TOOL_VERTICAL_SEPARATION * (len(tool_list) - 1), 2)
    center_of_broken_tools = 1
    positive_x_maximum = center_of_broken_tools + \
        tools.BROKEN_TOOL_HORIZONTAL_SEPARATION_MAX
    negative_x_maximum = center_of_broken_tools - \
        tools.BROKEN_TOOL_HORIZONTAL_SEPARATION_MAX
    for tool in tool_list:
        assert tool['type'].startswith('tool_rect')
        assert tool['debug']['length'] == 1
        pos_x = tool['shows'][0]['position']['x']
        assert negative_x_maximum <= pos_x <= positive_x_maximum


def test_shortcut_lava_target_tool_inaccessible_positive():
    horizontal = random.choice([-1, 1])
    backward = 2
    blocking = 1
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'random_performer_position': True,
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_horizontal_offset': horizontal,
            'tool_offset_backward_from_lava': backward,
            'inaccessible_tool_blocking_wall_horizontal_offset': blocking,
            'tool_type': 'inaccessible',
            'tool_rotation': 45
        }
    })

    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_type == 'inaccessible'
    assert component.get_shortcut_lava_target_tool()

    # Z long direction
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects

    wall = objs[2]
    wall_pos = wall['shows'][0]['position']
    assert wall['shows'][0]['scale']['x'] == 0.1
    assert wall['shows'][0]['scale']['y'] == 0.25
    assert wall['shows'][0]['scale']['z'] == 20
    assert wall['shows'][0]['rotation']['y'] == 0
    assert wall_pos['x'] == 1
    assert wall_pos['z'] == 0

    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool['shows'][0]['rotation']['y'] == 45
    assert tool['type'].startswith('tool_rect')
    assert tool['debug']['length'] == 5
    assert tool_pos['z'] == -1
    minimum_bound = round(
        min(getattr(pos, 'x')
            for pos in tool['shows'][0]['boundingBox'].box_xz), 2)
    assert minimum_bound == \
        wall_pos['x'] + wall['shows'][0]['scale']['x'] + abs(horizontal)

    assert scene.performer_start.position.x < wall_pos['x'] + \
        PERFORMER_HALF_WIDTH

    # X long direction
    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects

    wall = objs[2]
    wall_pos = wall['shows'][0]['position']
    assert wall['shows'][0]['scale']['x'] == 0.1
    assert wall['shows'][0]['scale']['y'] == 0.25
    assert wall['shows'][0]['scale']['z'] == 20
    assert wall['shows'][0]['rotation']['y'] == 90
    assert wall_pos['x'] == 0
    assert wall_pos['z'] == -1

    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool['shows'][0]['rotation']['y'] == 135
    assert tool['type'].startswith('tool_rect')
    assert tool['debug']['length'] == 5
    assert tool_pos['x'] == -1
    maximum_bound = round(
        max(getattr(pos, 'z')
            for pos in tool['shows'][0]['boundingBox'].box_xz), 2)
    assert maximum_bound == \
        wall_pos['z'] - wall['shows'][0]['scale']['x'] - abs(horizontal)

    assert scene.performer_start.position.z > wall_pos['z'] + \
        PERFORMER_HALF_WIDTH


def test_shortcut_lava_target_tool_inaccessible_negative():
    horizontal = random.choice([-1, 1])
    backward = 2
    blocking = -1
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'random_performer_position': True,
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_horizontal_offset': horizontal,
            'tool_offset_backward_from_lava': backward,
            'inaccessible_tool_blocking_wall_horizontal_offset': blocking,
            'tool_type': 'inaccessible',
            'tool_rotation': 45
        }
    })

    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_type == 'inaccessible'
    assert component.get_shortcut_lava_target_tool()

    # Z long direction
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects

    wall = objs[2]
    wall_pos = wall['shows'][0]['position']
    assert wall['shows'][0]['scale']['x'] == 0.1
    assert wall['shows'][0]['scale']['y'] == 0.25
    assert wall['shows'][0]['scale']['z'] == 20
    assert wall['shows'][0]['rotation']['y'] == 0
    assert wall_pos['x'] == -1
    assert wall_pos['z'] == 0

    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool['shows'][0]['rotation']['y'] == 45
    assert tool['type'].startswith('tool_rect')
    assert tool['debug']['length'] == 5
    assert tool_pos['z'] == -1
    maximum_bound = round(
        max(getattr(pos, 'x')
            for pos in tool['shows'][0]['boundingBox'].box_xz), 2)
    assert maximum_bound == \
        wall_pos['x'] - wall['shows'][0]['scale']['x'] - abs(horizontal)

    assert scene.performer_start.position.x > wall_pos['x'] + \
        PERFORMER_HALF_WIDTH

    # X long direction
    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects

    wall = objs[2]
    wall_pos = wall['shows'][0]['position']
    assert wall['shows'][0]['scale']['x'] == 0.1
    assert wall['shows'][0]['scale']['y'] == 0.25
    assert wall['shows'][0]['scale']['z'] == 20
    assert wall['shows'][0]['rotation']['y'] == 90
    assert wall_pos['x'] == 0
    assert wall_pos['z'] == 1

    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool['shows'][0]['rotation']['y'] == 135
    assert tool['type'].startswith('tool_rect')
    assert tool['debug']['length'] == 5
    assert tool_pos['x'] == -1
    minimum_bound = round(
        min(getattr(pos, 'z')
            for pos in tool['shows'][0]['boundingBox'].box_xz), 2)
    assert minimum_bound == \
        wall_pos['z'] + wall['shows'][0]['scale']['x'] + abs(horizontal)

    assert scene.performer_start.position.z < wall_pos['z'] - \
        PERFORMER_HALF_WIDTH


def test_shortcut_lava_target_tool_inaccessible_no_config():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'random_performer_position': True,
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_type': 'inaccessible',
            'tool_rotation': 90
        }
    })

    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_type == 'inaccessible'
    assert component.get_shortcut_lava_target_tool()

    # Z long direction
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects

    wall = objs[2]
    wall_pos = wall['shows'][0]['position']
    assert wall['shows'][0]['scale']['x'] == 0.1
    assert wall['shows'][0]['scale']['y'] == 0.25
    assert wall['shows'][0]['scale']['z'] == 20
    assert wall['shows'][0]['rotation']['y'] == 0
    assert -1 <= wall_pos['x'] <= -0.5 or 0.5 <= wall_pos['x'] <= 1
    assert wall_pos['z'] == 0

    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool['shows'][0]['rotation']['y'] == 90
    assert tool['type'].startswith('tool_rect')
    assert tool['debug']['length'] == 5
    assert tool_pos['z'] == 1
    maximum_bound = round(
        max(getattr(pos, 'x')
            for pos in tool['shows'][0]['boundingBox'].box_xz), 2)
    minimum_bound = round(
        min(getattr(pos, 'x')
            for pos in tool['shows'][0]['boundingBox'].box_xz), 2)
    wall_scale = wall['shows'][0]['scale']
    assert (
        maximum_bound == pytest.approx(wall_pos['x'] - wall_scale['x']) or
        minimum_bound == pytest.approx(wall_pos['x'] + wall_scale['x'])
    )

    left_side_wall = wall_pos['x'] <= -0.5
    assert (
        scene.performer_start.position.x > wall_pos['x'] +
        PERFORMER_HALF_WIDTH if left_side_wall else
        scene.performer_start.position.x < wall_pos['x'] -
        PERFORMER_HALF_WIDTH
    )

    # X long direction
    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects

    wall = objs[2]
    wall_pos = wall['shows'][0]['position']
    assert wall['shows'][0]['scale']['x'] == 0.1
    assert wall['shows'][0]['scale']['y'] == 0.25
    assert wall['shows'][0]['scale']['z'] == 20
    assert wall['shows'][0]['rotation']['y'] == 90
    assert wall_pos['x'] == 0
    assert -1 <= wall_pos['z'] <= -0.5 or 0.5 <= wall_pos['z'] <= 1

    tool = objs[1]
    tool_pos = tool['shows'][0]['position']
    assert tool['shows'][0]['rotation']['y'] == 180
    assert tool['type'].startswith('tool_rect')
    assert tool['debug']['length'] == 5
    assert tool_pos['x'] == 1
    maximum_bound = round(
        max(getattr(pos, 'z')
            for pos in tool['shows'][0]['boundingBox'].box_xz), 2)
    minimum_bound = round(
        min(getattr(pos, 'z')
            for pos in tool['shows'][0]['boundingBox'].box_xz), 2)
    wall_scale = wall['shows'][0]['scale']
    assert (
        maximum_bound == pytest.approx(wall_pos['z'] - wall_scale['x']) or
        minimum_bound == pytest.approx(wall_pos['z'] + wall_scale['x'])
    )

    left_side_wall = wall_pos['z'] >= -0.5
    assert (
        scene.performer_start.position.z < wall_pos['z'] -
        PERFORMER_HALF_WIDTH if left_side_wall else
        scene.performer_start.position.z > wall_pos['z'] +
        PERFORMER_HALF_WIDTH
    )


def test_shortcut_lava_target_tool_inaccessible_no_config_not_random_start():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'random_performer_position': False,
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_type': 'inaccessible',
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_type == 'inaccessible'
    assert component.get_shortcut_lava_target_tool()

    # Z long direction
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    scene.performer_start.position.x == 0
    scene.performer_start.position.z == -9.5

    # X long direction
    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    scene.performer_start.position.x == -9.5
    scene.performer_start.position.z == 0


@pytest.mark.slow
def test_shortcut_lava_target_tool_inaccessible_errors_positive():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'inaccessible_tool_blocking_wall_horizontal_offset': 100,
            'tool_type': 'inaccessible'
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)
    scene = prior_scene_custom_size(20, 15)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'inaccessible_tool_blocking_wall_horizontal_offset': 0.4,
            'tool_type': 'inaccessible'
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)
    scene = prior_scene_custom_size(20, 15)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)


@pytest.mark.slow
def test_shortcut_lava_target_tool_inaccessible_errors_negative():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'inaccessible_tool_blocking_wall_horizontal_offset': -100,
            'tool_type': 'inaccessible'
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)
    scene = prior_scene_custom_size(20, 15)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)

    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'inaccessible_tool_blocking_wall_horizontal_offset': -0.4,
            'tool_type': 'inaccessible'
        }
    })
    assert component.shortcut_lava_target_tool
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)
    scene = prior_scene_custom_size(20, 15)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)


def test_shortcut_lava_target_tool_no_inaccessible_blocking_wall():
    separation = 1
    tool_types = ['rectangular', 'hooked', 'broken', 'small']

    for tool_type in tool_types:
        component = ShortcutComponent({
            'shortcut_lava_target_tool': {
                'inaccessible_tool_blocking_wall_horizontal_offset': separation,  # noqa
                'tool_type': tool_type
            }
        })

        assert component.shortcut_lava_target_tool
        assert component.shortcut_lava_target_tool.tool_type != 'inaccessible'
        assert component.get_shortcut_lava_target_tool()
        scene = prior_scene_custom_size(15, 20)
        scene = component.update_ile_scene(scene)
        for obj in scene.objects:
            assert not obj['id'].startswith('wall')


def test_shortcut_lava_target_tool_offset_broken():
    horizontal = 2
    backward = 1
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'front_lava_width': 2,
            'rear_lava_width': 2,
            'left_lava_width': 2,
            'right_lava_width': 2,
            'island_size': 1,
            'tool_horizontal_offset': horizontal,
            'tool_offset_backward_from_lava': backward,
            'tool_type': 'broken',
            'tool_rotation': 0
        }
    })
    minimum_positive = \
        tools.BROKEN_TOOL_HORIZONTAL_SEPARATION_MIN + horizontal
    maximum_positive = \
        tools.BROKEN_TOOL_HORIZONTAL_SEPARATION_MAX + horizontal
    minimum_negative = \
        tools.BROKEN_TOOL_HORIZONTAL_SEPARATION_MIN - horizontal
    maximum_negative = \
        tools.BROKEN_TOOL_HORIZONTAL_SEPARATION_MAX - horizontal
    assert component.shortcut_lava_target_tool
    assert component.shortcut_lava_target_tool.tool_type == 'broken'
    assert component.get_shortcut_lava_target_tool()
    scene = prior_scene_custom_size(15, 20)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool_list = objs[1:]
    assert len(tool_list) == 5
    first_tool_pos = tool_list[0]['shows'][0]['position']
    last_tool_pos = tool_list[-1]['shows'][0]['position']
    assert first_tool_pos['z'] == 3 - backward
    assert last_tool_pos['z'] == round(
        first_tool_pos['z'] -
        tools.BROKEN_TOOL_VERTICAL_SEPARATION * (len(tool_list) - 1), 2)
    for tool in tool_list:
        assert tool['type'].startswith('tool_rect')
        assert tool['debug']['length'] == 1
        pos_x = tool['shows'][0]['position']['x']
        assert \
            (-maximum_negative <= pos_x <= -
             minimum_negative) or (
                 minimum_positive <= pos_x <= maximum_positive)

    scene = prior_scene_custom_size(20, 15)
    scene = component.update_ile_scene(scene)
    objs = scene.objects
    tool_list = objs[1:]
    assert len(tool_list) == 5
    first_tool_pos = tool_list[0]['shows'][0]['position']
    last_tool_pos = tool_list[-1]['shows'][0]['position']
    assert first_tool_pos['x'] == 3 - backward
    assert last_tool_pos['x'] == round(
        first_tool_pos['x'] -
        tools.BROKEN_TOOL_VERTICAL_SEPARATION * (len(tool_list) - 1), 2)
    for tool in tool_list:
        assert tool['type'].startswith('tool_rect')
        assert tool['debug']['length'] == 1
        pos_z = tool['shows'][0]['position']['z']
        assert \
            (minimum_negative <= pos_z <=
             maximum_negative) or (
                -maximum_positive <= pos_z <= -minimum_positive)


@pytest.mark.slow
def test_shortcut_lava_target_tool_distance_between_performer_broken():
    for distance_away in arange(0.1, 1.1, 0.1):
        for _ in range(5):
            distance_away = round(distance_away, 1)
            ObjectRepository.get_instance().clear()
            component = ShortcutComponent({
                'shortcut_lava_target_tool': {
                    'distance_between_performer_and_tool': distance_away,
                    'tool_rotation': [0, 15, 30, 45, 60, 75, 90],
                    'tool_type': 'broken'
                }
            })
            assert component.shortcut_lava_target_tool
            assert component.shortcut_lava_target_tool.distance_between_performer_and_tool  # noqa
            assert component.shortcut_lava_target_tool.tool_type == 'broken'
            scene = prior_scene_custom_size(25, 25)
            scene = component.update_ile_scene(scene)
            performer_start = Point(
                scene.performer_start.position.x,
                scene.performer_start.position.z)
            tool_list = scene.objects[1:]
            valid = False
            for tool in tool_list:
                bb_boxes = tool['shows'][0]['boundingBox'].box_xz
                top_right = Point(bb_boxes[0].x, bb_boxes[0].z)
                bottom_right = Point(bb_boxes[1].x, bb_boxes[1].z)
                bottom_left = Point(bb_boxes[2].x, bb_boxes[2].z)
                top_left = Point(bb_boxes[3].x, bb_boxes[3].z)
                tool_polygon = Polygon([
                    top_right, bottom_right, bottom_left, top_left])
                distance = performer_start.distance(tool_polygon)
                valid = round(
                    distance,
                    2) == round(
                    distance_away +
                    PERFORMER_HALF_WIDTH,
                    2)
                if valid:
                    break
            assert valid


def test_shortcut_lava_target_tool_distance_between_performer_inaccessible():
    component = ShortcutComponent({
        'shortcut_lava_target_tool': {
            'distance_between_performer_and_tool': 1,
            'tool_type': 'inaccessible'
        }
    })
    assert component.shortcut_lava_target_tool
    assert \
        component.shortcut_lava_target_tool.distance_between_performer_and_tool
    assert component.shortcut_lava_target_tool.tool_type == 'inaccessible'
    scene = prior_scene_custom_size(25, 25)
    with pytest.raises(ILEException):
        scene = component.update_ile_scene(scene)


def test_shortcut_seeing_leads_to_knowing_default():
    component = ShortcutComponent({
        'shortcut_seeing_leads_to_knowing': True
    })
    assert component.shortcut_seeing_leads_to_knowing
    assert component.get_shortcut_seeing_leads_to_knowing()
    scene = prior_scene_custom_size(10, 10)

    scene = component.update_ile_scene(scene)

    objs = scene.objects
    assert len(objs) == 11

    platform = objs[0]
    target = objs[1]
    agent = objs[10]

    # platform and performer start
    assert platform['type'] == 'cube'
    assert platform['shows'][0]['position'] == {
        'x': 0, 'y': 0.5, 'z': -2.65}
    assert platform['shows'][0]['scale'] == {
        'x': 1, 'y': 1, 'z': 1}

    perf_pos = scene.performer_start.position
    perf_rot = scene.performer_start.rotation
    assert perf_pos == Vector3d(x=0, y=1.762, z=-2.65)
    assert perf_rot == Vector3d(x=30, y=0, z=0)

    # target and goal info
    assert scene.goal
    assert scene.goal.metadata['target']
    assert 'targets' not in scene.goal.metadata
    assert scene.goal.category == 'passive'
    assert scene.goal.answer['choice'] == 'plausible'
    assert scene.goal.last_step == 105
    assert scene.goal.action_list
    assert len(scene.goal.action_list) == 105
    for action in scene.goal.action_list:
        assert action == ['Pass']

    assert target['debug']['dimensions'] == {
        'x': 0.165, 'y': 0.165, 'z': 0.165}
    assert target['debug']['positionY'] == 0.0825
    target_pos = target['shows'][0]['position']
    # target should start in a placer
    assert abs(target_pos['x']) == 1
    assert target_pos['y'] == 2.8825
    assert abs(target_pos['z']) == 0.5
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert 'moves' in target
    assert target['moves'] == [
        {'stepBegin': 50, 'stepEnd': 60,
         'vector': {'x': 0, 'y': -0.25, 'z': 0}}
    ]

    # placers and bins
    check_shortcut_seeing_leads_to_knowing_bins_placers(objs)

    # agent info
    check_shortcut_seeing_leads_to_knowing_agent(agent)


def test_shortcut_seeing_leads_to_knowing_target_behind_agent():
    component = ShortcutComponent({
        'shortcut_seeing_leads_to_knowing': {
            'target_behind_agent': True
        }
    })
    assert component.shortcut_seeing_leads_to_knowing
    assert component.get_shortcut_seeing_leads_to_knowing()
    scene = prior_scene_custom_size(10, 10)

    scene = component.update_ile_scene(scene)

    objs = scene.objects
    assert len(objs) == 11

    platform = objs[0]
    target = objs[1]
    agent = objs[10]

    # platform and performer start
    assert platform['type'] == 'cube'
    assert platform['shows'][0]['position'] == {
        'x': 0, 'y': 0.5, 'z': -2.65}
    assert platform['shows'][0]['scale'] == {
        'x': 1, 'y': 1, 'z': 1}

    perf_pos = scene.performer_start.position
    perf_rot = scene.performer_start.rotation
    assert perf_pos == Vector3d(x=0, y=1.762, z=-2.65)
    assert perf_rot == Vector3d(x=30, y=0, z=0)

    # target and goal info
    assert scene.goal
    assert scene.goal.metadata['target']
    assert 'targets' not in scene.goal.metadata
    assert scene.goal.category == 'passive'
    assert scene.goal.answer['choice'] == 'plausible'
    assert scene.goal.last_step == 105
    assert scene.goal.action_list
    assert len(scene.goal.action_list) == 105
    for action in scene.goal.action_list:
        assert action == ['Pass']

    assert target['debug']['dimensions'] == {
        'x': 0.165, 'y': 0.165, 'z': 0.165}
    assert target['debug']['positionY'] == 0.0825
    target_pos = target['shows'][0]['position']
    # target should start in a placer
    assert abs(target_pos['x']) == 1
    assert target_pos['y'] == 2.8825
    assert abs(target_pos['z']) == 0.5
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert 'moves' in target
    assert target['moves'] == [
        {'stepBegin': 50, 'stepEnd': 60,
         'vector': {'x': 0, 'y': -0.25, 'z': 0}}
    ]
    # placers and bins
    check_shortcut_seeing_leads_to_knowing_bins_placers(objs)

    # agent info
    check_shortcut_seeing_leads_to_knowing_agent(agent)

    agent_start_on_left = agent['shows'][0]['position']['x'] == -2

    # ensure target is behind agent's path
    if (agent_start_on_left):
        assert target_pos['x'] == -1
    else:
        assert target_pos['x'] == 1


def test_shortcut_seeing_leads_to_knowing_target_ahead_agent():
    component = ShortcutComponent({
        'shortcut_seeing_leads_to_knowing': {
            'target_behind_agent': False
        }
    })
    assert component.shortcut_seeing_leads_to_knowing
    assert component.get_shortcut_seeing_leads_to_knowing()
    scene = prior_scene_custom_size(10, 10)

    scene = component.update_ile_scene(scene)

    objs = scene.objects
    assert len(objs) == 11

    platform = objs[0]
    target = objs[1]
    agent = objs[10]

    # platform and performer start
    assert platform['type'] == 'cube'
    assert platform['shows'][0]['position'] == {
        'x': 0, 'y': 0.5, 'z': -2.65}
    assert platform['shows'][0]['scale'] == {
        'x': 1, 'y': 1, 'z': 1}

    perf_pos = scene.performer_start.position
    perf_rot = scene.performer_start.rotation
    assert perf_pos == Vector3d(x=0, y=1.762, z=-2.65)
    assert perf_rot == Vector3d(x=30, y=0, z=0)

    # target and goal info
    assert scene.goal
    assert scene.goal.metadata['target']
    assert 'targets' not in scene.goal.metadata
    assert scene.goal.category == 'passive'
    assert scene.goal.answer['choice'] == 'plausible'
    assert scene.goal.last_step == 105
    assert scene.goal.action_list
    assert len(scene.goal.action_list) == 105
    for action in scene.goal.action_list:
        assert action == ['Pass']

    assert target['debug']['dimensions'] == {
        'x': 0.165, 'y': 0.165, 'z': 0.165}
    assert target['debug']['positionY'] == 0.0825
    target_pos = target['shows'][0]['position']
    # target should start in a placer
    assert abs(target_pos['x']) == 1
    assert target_pos['y'] == 2.8825
    assert abs(target_pos['z']) == 0.5
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert 'moves' in target
    assert target['moves'] == [
        {'stepBegin': 50, 'stepEnd': 60,
         'vector': {'x': 0, 'y': -0.25, 'z': 0}}
    ]

    # placers and bins
    check_shortcut_seeing_leads_to_knowing_bins_placers(objs)

    # agent info
    check_shortcut_seeing_leads_to_knowing_agent(agent)

    agent_start_on_left = agent['shows'][0]['position']['x'] == -2

    # ensure target is ahead of agent's path
    if (agent_start_on_left):
        assert target_pos['x'] == 1
    else:
        assert target_pos['x'] == -1


def check_shortcut_seeing_leads_to_knowing_agent(agent):
    assert abs(agent['shows'][0]['position']['x']) == 2
    assert agent['shows'][0]['position']['y'] == 0
    assert agent['shows'][0]['position']['z'] == 0
    assert (agent['shows'][0]['rotation']['y'] ==
            90 or agent['shows'][0]['rotation']['y'] == 270)
    assert 'actions' in agent
    assert agent['actions'] == [
        {'id': 'TPM_idle1', 'stepBegin': 51,
         'isLoopAnimation': True, 'stepEnd': 76}]
    assert 'agentMovement' in agent
    assert 'sequence' in agent['agentMovement']
    assert len(agent['agentMovement']['sequence']) == 2
    mvmt_seq = agent['agentMovement']['sequence']
    assert mvmt_seq[0] == {
        'animation': 'TPM_walk', 'endPoint': {'x': 0.0, 'z': 0.0}}
    assert mvmt_seq[1]['animation'] == 'TPM_walk'
    assert abs(mvmt_seq[1]['endPoint']['x']) == 1
    assert abs(mvmt_seq[1]['endPoint']['z']) == 0.5


def check_shortcut_seeing_leads_to_knowing_bins_placers(objs):
    placers = list(
        filter(
            lambda obj: obj['type'] == ('cylinder'), objs))
    bins = list(
        filter(
            lambda obj: obj['type'].startswith('cup_'), objs))
    assert len(bins) == 4
    assert len(placers) == 4

    assert bins[0]['shows'][0]['position']['x'] == -1
    assert bins[0]['shows'][0]['position']['z'] == 0.5
    assert bins[0]['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placers[0]['shows'][0]['position']['x'] == -1
    assert placers[0]['shows'][0]['position']['z'] == 0.5

    assert bins[1]['shows'][0]['position']['x'] == -1
    assert bins[1]['shows'][0]['position']['z'] == -0.5
    assert bins[1]['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placers[1]['shows'][0]['position']['x'] == -1
    assert placers[1]['shows'][0]['position']['z'] == -0.5

    assert bins[2]['shows'][0]['position']['x'] == 1
    assert bins[2]['shows'][0]['position']['z'] == 0.5
    assert bins[2]['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placers[2]['shows'][0]['position']['x'] == 1
    assert placers[2]['shows'][0]['position']['z'] == 0.5

    assert bins[3]['shows'][0]['position']['x'] == 1
    assert bins[3]['shows'][0]['position']['z'] == -0.5
    assert bins[3]['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placers[3]['shows'][0]['position']['x'] == 1
    assert placers[3]['shows'][0]['position']['z'] == -0.5

    bin_material = bins[0]['materials']
    for bin_object in bins:
        assert bin_object['materials'] == bin_material

    for placer in placers:
        assert placer['materials'] == ['Custom/Materials/Magenta']
        assert 'moves' in placer
        assert len(placer['moves']) == 2
        assert placer['moves'][0] == {
            'stepBegin': 50, 'stepEnd': 60, 'vector': {
                'x': 0, 'y': -0.25, 'z': 0}}
        assert placer['moves'][1] == {
            'stepBegin': 70, 'stepEnd': 79, 'vector': {
                'x': 0, 'y': 0.25, 'z': 0}}
        assert len(placer['changeMaterials']) == 1
        assert placer['changeMaterials'][0]['stepBegin'] == 65
        assert placer['changeMaterials'][0]['materials'] == [
            'Custom/Materials/Cyan']
        assert placer['states'] == ([['active']] * 64) + ([['inactive']] * 40)
