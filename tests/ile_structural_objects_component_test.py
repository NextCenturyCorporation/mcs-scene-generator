from typing import List

from machine_common_sense.config_manager import Vector3d

from ideal_learning_env import RandomStructuralObjectsComponent
from ideal_learning_env.numerics import MinMaxFloat, VectorFloatConfig
from ideal_learning_env.structural_objects_component import (
    RandomStructuralObjectConfig,
    SpecificStructuralObjectsComponent,
    StructuralLOccluderConfig,
    StructuralPlatformConfig,
    StructuralRampConfig,
    StructuralWallConfig,
)


def prior_scene():
    return {'debug': {}, 'goal': {}, 'performerStart':
            {'position':
             {'x': 0, 'y': 0, 'z': 0}},
            'roomDimensions': {'x': 10, 'y': 3, 'z': 10}}


def test_random_structural_objects_defaults():
    component = RandomStructuralObjectsComponent({})
    assert component.random_structural_objects is None

    scene = component.update_ile_scene(prior_scene())
    objs = scene['objects']
    assert isinstance(objs, list)
    occluders = sum(1 for o in objs if o['id'].startswith('occluder'))
    num_objs = len(objs) - occluders / 2
    assert 2 <= num_objs <= 4


def test_random_structural_objects_num():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'num': 3
        }
    })
    assert component.random_structural_objects.num == 3
    assert component.random_structural_objects.type is None

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects.
    occluders = sum(1 for o in objs if o['id'].startswith('occluder'))
    assert len(objs) == 3 + occluders / 2


def test_random_structural_objects_min_max():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'num': {'min': 1, 'max': 4}
        }
    })
    assert component.random_structural_objects.num.min == 1
    assert component.random_structural_objects.num.max == 4
    computed = component.get_random_structural_objects()
    assert 1 <= computed[0].num <= 4

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects
    occluders = sum(bool(o['id'].startswith('occluder')) for o in objs) / 2
    min = 1 + occluders
    max = 4 + occluders
    assert min <= len(objs) <= max
    for obj in objs:
        assert obj['structure']


def test_random_structural_objects_walls():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'walls',
            'num': 2
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.num == 2
    assert component.random_structural_objects.type == 'walls'

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    for obj in objs:
        assert obj['structure']
        assert obj['id'].startswith('wall')


def test_random_structural_objects_platforms():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'platforms',
            'num': {
                'min': 1,
                'max': 3
            }
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.num.min == 1
    assert component.random_structural_objects.num.max == 3
    assert component.random_structural_objects.type == 'platforms'

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'platforms'
    assert 1 <= computed[0].num <= 3

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert 1 <= len(objs) <= 3
    for obj in objs:
        assert obj['structure']
        assert obj['id'].startswith('platform')


def test_random_structural_objects_ramps():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'ramps',
            'num': [0, 1, 2]
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'ramps'
    assert component.random_structural_objects.num == [0, 1, 2]

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'ramps'
    assert computed[0].num in [0, 1, 2]

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) in [0, 1, 2]
    for obj in objs:
        assert obj['structure']
        assert obj['id'].startswith('ramp')


def test_random_structural_objects_l_occluders():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'l_occluders',
            'num': 2
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'l_occluders'
    assert component.random_structural_objects.num == 2

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'l_occluders'
    assert computed[0].num == 2

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects each
    assert len(objs) == 4
    for obj in objs:
        assert obj['structure']
        assert obj['id'].startswith('occluder')


def test_random_structural_objects_all():
    # This is minimized for all to avoid rare failures due to big objects
    # coming early and causing the test to fail.
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': [{
            'type': 'walls',
            'num': {'min': 1, 'max': 1}
        }, {
            'type': 'platforms',
            'num': 1
        }, {
            'type': 'ramps',
            'num': 1
        }, {
            'type': 'l_occluders',
            'num': 1
        }]
    })
    assert isinstance(
        component.random_structural_objects, List)
    assert component.random_structural_objects[0].num.min == 1
    assert component.random_structural_objects[0].num.max == 1
    assert component.random_structural_objects[0].type == "walls"
    assert component.random_structural_objects[1].num == 1
    assert component.random_structural_objects[1].type == "platforms"
    assert component.random_structural_objects[2].num == 1
    assert component.random_structural_objects[2].type == "ramps"
    assert component.random_structural_objects[3].num == 1
    assert component.random_structural_objects[3].type == "l_occluders"

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == "walls"
    assert computed[0].num == 1
    assert computed[1].type == "platforms"
    assert computed[1].num == 1
    assert computed[2].type == "ramps"
    assert computed[2].num == 1
    assert computed[3].type == "l_occluders"
    assert computed[3].num == 1

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects each
    assert len(objs) == 5
    wall = 0
    plat = 0
    ramp = 0
    occ = 0
    for obj in objs:
        assert obj['structure']
        if obj['id'].startswith('wall'):
            wall += 1
        if obj['id'].startswith('platform'):
            plat += 1
        if obj['id'].startswith('ramp'):
            ramp += 1
        if obj['id'].startswith('occluder'):
            occ += 1
    occ /= 2
    assert wall == 1
    assert plat == 1
    assert ramp == 1
    assert occ == 1


def test_structural_objects_defaults():
    component = SpecificStructuralObjectsComponent({})
    assert component.structural_walls is None
    assert component.structural_platforms is None
    assert component.structural_l_occluders is None
    assert component.structural_ramps is None

    scene = component.update_ile_scene(prior_scene())
    objs = scene['objects']
    assert isinstance(objs, list)
    assert len(objs) == 0


def test_structural_objects_walls_full():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]
    component = SpecificStructuralObjectsComponent({
        'structural_walls': {
            'num': 1,
            'position': {
                'x': 1,
                'y': 2,
                'z': 3
            },
            'rotation_y': 30,
            'material': my_mats,
            'width': 1,
            'height': 1
        }
    })
    pre_walls = component.structural_walls
    assert isinstance(pre_walls, StructuralWallConfig)
    assert pre_walls.num == 1
    assert isinstance(pre_walls.position, VectorFloatConfig)
    assert pre_walls.position.x == 1
    assert pre_walls.position.z == 3
    assert pre_walls.rotation_y == 30
    assert pre_walls.material == my_mats
    assert pre_walls.width == 1
    assert pre_walls.height == 1

    # computed walls
    cwalls = component.get_structural_walls()
    assert isinstance(cwalls, StructuralWallConfig)
    assert cwalls.num == 1
    assert isinstance(cwalls.position, Vector3d)
    assert cwalls.position.x == 1
    assert cwalls.position.z == 3
    assert cwalls.rotation_y == 30
    assert isinstance(cwalls.material, str)
    assert cwalls.material in my_mats
    assert cwalls.width == 1
    assert cwalls.height == 1

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects.
    assert len(objs) == 1
    obj = objs[0]
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    rot = show['rotation']
    assert pos['x'] == 1
    assert pos['z'] == 3
    assert rot['y'] == 30


def test_structural_objects_walls_empty():

    component = SpecificStructuralObjectsComponent({
        'structural_walls': {
            'num': 1
        }
    })
    pre_walls = component.structural_walls
    assert isinstance(pre_walls, StructuralWallConfig)
    assert pre_walls.num == 1
    assert pre_walls.position is None
    assert pre_walls.material is None
    assert pre_walls.material is None
    assert pre_walls.width is None
    assert pre_walls.height is None

    # computed walls
    cwalls = component.get_structural_walls()
    assert isinstance(cwalls, StructuralWallConfig)
    assert cwalls.num == 1
    assert cwalls.position is None
    assert cwalls.material is None
    assert cwalls.width is None
    assert cwalls.height is None

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects.
    assert len(objs) == 1
    obj = objs[0]
    show = obj['shows'][0]
    pos = show['position']
    rot = show['rotation']
    assert isinstance(pos, dict)
    assert isinstance(rot, dict)
    assert isinstance(obj['materials'], list)
    assert isinstance(pos['x'], float)
    assert isinstance(pos['z'], float)
    assert isinstance(rot['y'], int)


def test_structural_objects_platforms_full():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]
    component = SpecificStructuralObjectsComponent({
        'structural_platforms': {
            'num': 1,
            'position': {
                'x': 1,
                'y': 2,
                'z': 3
            },
            'rotation_y': 30,
            'material': my_mats,
            'scale': {
                'x': 0.4,
                'y': 0.5,
                'z': 0.6
            }

        }
    })
    pre_plat = component.structural_platforms
    assert isinstance(pre_plat, StructuralPlatformConfig)
    assert pre_plat.num == 1
    assert isinstance(pre_plat.position, VectorFloatConfig)
    assert pre_plat.position.x == 1
    assert pre_plat.position.z == 3
    assert pre_plat.rotation_y == 30
    assert pre_plat.material == my_mats
    scale = pre_plat.scale
    assert isinstance(scale, VectorFloatConfig)
    assert scale.x == .4
    assert scale.y == .5
    assert scale.z == .6

    # computed walls
    cplat = component.get_structural_platforms()
    assert isinstance(cplat, StructuralPlatformConfig)
    assert cplat.num == 1
    assert isinstance(cplat.position, Vector3d)
    assert cplat.position.x == 1
    assert cplat.position.z == 3
    assert cplat.rotation_y == 30
    assert isinstance(cplat.material, str)
    assert cplat.material in my_mats
    scale = cplat.scale
    assert isinstance(scale, Vector3d)
    assert scale.x == .4
    assert scale.y == .5
    assert scale.z == .6

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects.
    assert len(objs) == 1
    obj = objs[0]
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    rot = show['rotation']
    assert pos['x'] == 1
    assert pos['z'] == 3
    assert rot['y'] == 30


def test_structural_objects_platforms_variables():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]
    component = SpecificStructuralObjectsComponent({
        'structural_platforms': {
            'num': 1,
            'position': {
                'x': {
                    'min': -4,
                    'max': 4
                },
                'y': 2,
                'z': [-3, 0, 3]
            },
            'rotation_y': 30,
            'material': my_mats,
            'scale': {
                'min': 0.2,
                'max': 1.5
            }

        }
    })
    pre_plat = component.structural_platforms
    assert isinstance(pre_plat, StructuralPlatformConfig)
    assert pre_plat.num == 1
    assert isinstance(pre_plat.position, VectorFloatConfig)
    assert pre_plat.position.x == MinMaxFloat(min=-4, max=4)
    assert pre_plat.position.z == [-3, 0, 3]
    assert pre_plat.rotation_y == 30
    assert pre_plat.material == my_mats
    scale = pre_plat.scale
    assert scale == MinMaxFloat(min=0.2, max=1.5)

    # computed walls
    cplat = component.get_structural_platforms()
    assert isinstance(cplat, StructuralPlatformConfig)
    assert cplat.num == 1
    assert isinstance(cplat.position, Vector3d)
    assert -4 <= cplat.position.x <= 4
    assert cplat.position.z in [-3, 0, 3]
    assert cplat.rotation_y == 30
    assert isinstance(cplat.material, str)
    assert cplat.material in my_mats
    scale = cplat.scale
    assert 0.2 <= scale <= 1.5

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects.
    assert len(objs) == 1
    obj = objs[0]
    assert obj['structure']
    show = obj['shows'][0]
    rot = show['rotation']
    scale = show['scale']
    assert rot['y'] == 30
    assert 0.2 <= scale['x'] <= 1.5
    assert 0.2 <= scale['y'] <= 1.5
    assert 0.2 <= scale['z'] <= 1.5


def test_structural_objects_l_occluders_full():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]
    component = SpecificStructuralObjectsComponent({
        'structural_l_occluders': {
            'num': 1,
            'position': {
                'x': 1,
                'y': 2,
                'z': 3
            },
            'rotation_y': 30,
            'material': my_mats,
            'scale_front_x': 0.3,
            'scale_front_z': 0.4,
            'scale_side_x': 0.5,
            'scale_side_z': 0.6,
            'scale_y': 0.7
        }
    })
    pre_occ = component.structural_l_occluders
    assert isinstance(pre_occ, StructuralLOccluderConfig)
    assert pre_occ.num == 1
    assert isinstance(pre_occ.position, VectorFloatConfig)
    assert pre_occ.position.x == 1
    assert pre_occ.position.z == 3
    assert pre_occ.rotation_y == 30
    assert pre_occ.material == my_mats
    assert pre_occ.scale_front_x == .3
    assert pre_occ.scale_front_z == .4
    assert pre_occ.scale_side_x == .5
    assert pre_occ.scale_side_z == .6
    assert pre_occ.scale_y == .7

    # computed occluder
    comp_occ = component.get_structural_l_occluders()
    assert isinstance(comp_occ, StructuralLOccluderConfig)
    assert comp_occ.num == 1
    assert isinstance(comp_occ.position, Vector3d)
    assert comp_occ.position.x == 1
    assert comp_occ.position.z == 3
    assert comp_occ.rotation_y == 30
    assert isinstance(comp_occ.material, str)
    assert comp_occ.material in my_mats
    assert comp_occ.scale_front_x == .3
    assert comp_occ.scale_front_z == .4
    assert comp_occ.scale_side_x == .5
    assert comp_occ.scale_side_z == .6
    assert comp_occ.scale_y == .7

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects.
    assert len(objs) == 2
    for obj in objs:
        assert obj['structure']
        show = obj['shows'][0]
        rot = show['rotation']
        assert rot['y'] == 30


def test_structural_objects_ramps_full():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]

    component = SpecificStructuralObjectsComponent({
        'structural_ramps': {
            'num': 1,
            'position': {
                'x': 1,
                'y': 2,
                'z': 3
            },
            'rotation_y': 30,
            'material': my_mats,
            'angle': 30,
            'width': 0.4,
            'length': 0.5
        }
    })
    pre_ramp = component.structural_ramps
    assert isinstance(pre_ramp, StructuralRampConfig)
    assert pre_ramp.num == 1
    assert isinstance(pre_ramp.position, VectorFloatConfig)
    assert pre_ramp.position.x == 1
    assert pre_ramp.position.z == 3
    assert pre_ramp.rotation_y == 30
    assert pre_ramp.material == my_mats
    assert pre_ramp.angle == 30
    assert pre_ramp.width == .4
    assert pre_ramp.length == .5

    # computed ramps
    cramp = component.get_structural_ramps()
    assert isinstance(cramp, StructuralRampConfig)
    assert cramp.num == 1
    assert isinstance(cramp.position, Vector3d)
    assert cramp.position.x == 1
    assert cramp.position.z == 3
    assert cramp.rotation_y == 30
    assert isinstance(cramp.material, str)
    assert cramp.material in my_mats
    assert cramp.angle == 30
    assert cramp.width == .4
    assert cramp.length == .5

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects.
    assert len(objs) == 1
    obj = objs[0]
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    rot = show['rotation']
    assert pos['x'] == 1
    assert pos['z'] == 3
    assert rot['y'] == 30
