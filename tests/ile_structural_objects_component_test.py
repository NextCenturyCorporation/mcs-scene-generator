from typing import List

import pytest
from machine_common_sense.config_manager import Vector3d

from generator import ObjectBounds, materials, specific_objects
from ideal_learning_env import ILEException, RandomStructuralObjectsComponent
from ideal_learning_env.interactable_objects_component import (
    SpecificInteractableObjectsComponent,
)
from ideal_learning_env.numerics import (
    MinMaxFloat,
    MinMaxInt,
    VectorFloatConfig,
)
from ideal_learning_env.object_services import (
    TARGET_LABEL,
    InstanceDefinitionLocationTuple,
    ObjectRepository,
)
from ideal_learning_env.structural_objects_component import (
    FloorAreaConfig,
    FloorMaterialConfig,
    RandomStructuralObjectConfig,
    SpecificStructuralObjectsComponent,
    StructuralDoorConfig,
    StructuralDropperConfig,
    StructuralLOccluderConfig,
    StructuralMovingOccluderConfig,
    StructuralOccludingWallConfig,
    StructuralPlacerConfig,
    StructuralPlatformConfig,
    StructuralRampConfig,
    StructuralThrowerConfig,
    StructuralWallConfig,
    WallSide,
)


def prior_scene():
    return {'debug': {}, 'goal': {}, 'performerStart':
            {'position':
             {'x': 0, 'y': 0, 'z': 0},
             'rotation': {'x': 0, 'y': 0, 'z': 0}},
            'roomDimensions': {'x': 10, 'y': 3, 'z': 10}}


def prior_scene_custom_size(x, z):
    return {'debug': {}, 'goal': {}, 'performerStart':
            {'position':
             {'x': 0, 'y': 0, 'z': 0}},
            'roomDimensions': {'x': x, 'y': 3, 'z': z}}


def prior_scene_with_target():
    scene = prior_scene()
    target_inst = {
        'id': '743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f',
        'type': 'soccer_ball',
        'mass': 1.0,
        'salientMaterials': ['rubber'],
        'debug': {
            'dimensions': {'x': 0.22, 'y': 0.22, 'z': 0.22},
            'positionY': 0.11,
            'shape': ['ball'],
            'offset': {'x': 0, 'y': 0.11, 'z': 0},
            'materialCategory': [],
            'color': ['black', 'white']
        },
        'moveable': True,
        'pickupable': True,
        'shows': [{
            'rotation': {'x': 0, 'y': 45, 'z': 0},
            'position': {'x': -1.03, 'y': 0.11, 'z': 4.08},
            'boundingBox': ObjectBounds(box_xz=[
                Vector3d(**{'x': -0.8744, 'y': 0, 'z': 4.08}),
                Vector3d(**{'x': -1.03, 'y': 0, 'z': 3.9244}),
                Vector3d(**{'x': -1.1856, 'y': 0, 'z': 4.08}),
                Vector3d(**{'x': -1.03, 'y': 0, 'z': 4.2356})
            ], max_y=0.22, min_y=0),
            'stepBegin': 0,
            'scale': {'x': 1, 'y': 1, 'z': 1}
        }],
        'materials': []
    }

    scene["objects"] = [target_inst]
    goal = {
        "metadata": {
            "target": {
                "id": "743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f"
            }
        },
        "last_step": 1000,
        "category": "retrieval"
    }
    scene["goal"] = goal
    target_defn = specific_objects.create_soccer_ball()
    target_loc = target_inst['shows'][0]
    t = InstanceDefinitionLocationTuple(target_inst, target_defn, target_loc)
    ObjectRepository.get_instance().clear()
    ObjectRepository.get_instance().add_to_labeled_objects(t, TARGET_LABEL)
    return scene


@pytest.fixture(autouse=True)
def run_before_test():
    ObjectRepository.get_instance().clear()


def test_random_structural_objects_defaults():
    component = RandomStructuralObjectsComponent({})
    assert component.random_structural_objects is None

    scene = component.update_ile_scene(prior_scene())
    objs = scene['objects']
    assert isinstance(objs, list)
    occluders = sum(1 for o in objs if o['id'].startswith('occluder'))
    droppers = sum(bool(o['id'].startswith('dropping_device'))
                   for o in objs)
    throwers = sum(bool(o['id'].startswith('throwing_device'))
                   for o in objs)

    three_part_occluding_walls = sum(bool(o['id'].startswith('top'))
                                     for o in objs)

    placers = sum(bool(o['id'].startswith('placer'))
                  for o in objs)

    holes = len(scene['holes'])
    floor_textures = 0
    ft = scene['floorTextures']
    for text in ft:
        loc_list = text['positions']
        floor_textures += len(loc_list)
    num_objs = len(objs) - occluders / 2 - throwers - droppers + \
        holes + floor_textures - placers - 2 * three_part_occluding_walls

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
    droppers = sum(bool(o['id'].startswith('dropping_device'))
                   for o in objs)
    throwers = sum(bool(o['id'].startswith('throwing_device'))
                   for o in objs)

    three_part_occluding_walls = sum(bool(o['id'].startswith('top'))
                                     for o in objs)
    placers = sum(bool(o['id'].startswith('placer'))
                  for o in objs)
    structural = 0
    thrown_dropped = 0
    for obj in objs:
        if obj.get('structure'):
            structural += 1
        else:
            thrown_dropped += 1
    holes = len(scene['holes'])
    floor_textures = 0
    ft = scene['floorTextures']
    for text in ft:
        loc_list = text['positions']
        floor_textures += len(loc_list)
    assert len(objs) == 3 + occluders / 2 + \
        thrown_dropped - holes - floor_textures + \
        2 * three_part_occluding_walls
    assert thrown_dropped == throwers + droppers + placers
    assert structural + thrown_dropped + 2 * \
        three_part_occluding_walls == len(objs)


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
    droppers = sum(bool(o['id'].startswith('dropping_device'))
                   for o in objs)
    throwers = sum(bool(o['id'].startswith('throwing_device'))
                   for o in objs)
    three_part_occluding_walls = sum(bool(o['id'].startswith('top'))
                                     for o in objs)
    placers = sum(bool(o['id'].startswith('placer'))
                  for o in objs)
    holes = len(scene['holes'])
    floor_textures = 0
    ft = scene['floorTextures']
    for text in ft:
        loc_list = text['positions']
        floor_textures += len(loc_list)
    min = (
        1 +
        occluders +
        throwers +
        droppers -
        holes -
        floor_textures +
        placers + 2 * three_part_occluding_walls)
    max = (
        4 +
        occluders +
        throwers +
        droppers -
        holes -
        floor_textures +
        placers + 2 * three_part_occluding_walls)
    assert min <= len(objs) <= max
    structural = 0
    thrown_dropped = 0
    for obj in objs:
        if obj.get('structure'):
            structural += 1
        else:
            thrown_dropped += 1
    assert thrown_dropped == throwers + droppers + placers
    assert structural + thrown_dropped == len(objs)


def test_random_structural_objects_walls():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'walls',
            'num': 2,
            'labels': 'test_label'
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
        assert obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('walls')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_random_structural_objects_platforms():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'platforms',
            'num': {
                'min': 1,
                'max': 3
            },
            'labels': 'test_label'
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
        assert obj['shows'][0]['scale']['x'] >= 0.5
        assert 3 >= obj['shows'][0]['scale']['y'] >= 0.5
        assert obj['shows'][0]['scale']['z'] >= 0.5
        assert obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('platforms')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_random_structural_objects_ramps():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'ramps',
            'num': [1, 2, 3],
            'labels': 'test_label'
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'ramps'
    assert component.random_structural_objects.num == [1, 2, 3]

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'ramps'
    assert computed[0].num in [1, 2, 3]

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) in [1, 2, 3]
    for obj in objs:
        assert obj['structure']
        assert obj['id'].startswith('ramp')
        assert obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('ramps')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_random_structural_objects_l_occluders():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'l_occluders',
            'num': 2,
            'labels': 'test_label'
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
        assert obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('l_occluders')
    assert ObjectRepository.get_instance().has_label('test_label')


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
        assert obj['debug']['random_position']
    occ /= 2
    assert wall == 1
    assert plat == 1
    assert ramp == 1
    assert occ == 1


def test_random_structural_objects_droppers():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'droppers',
            'num': 2,
            'labels': 'test_label'
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'droppers'
    assert component.random_structural_objects.num == 2

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'droppers'
    assert computed[0].num == 2

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # droppers create 2 objects each, dropper and dropped object
    assert len(objs) == 4
    droppers = 0
    thrown = 0
    for obj in objs:
        if (obj.get('structure') and obj['type'] == 'tube_wide' and
                obj['id'].startswith('dropping_device')):
            droppers += 1
        if 'togglePhysics' in obj:
            thrown += 1
    assert droppers == 2
    assert thrown == 2
    assert ObjectRepository.get_instance().has_label('droppers')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_random_structural_objects_throwers():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'throwers',
            'num': 4,
            'labels': 'test_label'
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'throwers'
    assert component.random_structural_objects.num == 4

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'throwers'
    assert computed[0].num == 4

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # throwers create 2 objects each
    assert len(objs) == 8
    throwers = 0
    thrown = 0
    for obj in objs:
        if (obj.get('structure') and obj['type'] == 'tube_wide' and
                obj['id'].startswith('throwing_device')):
            throwers += 1
        if 'forces' in obj:
            thrown += 1
    assert throwers == 4
    assert thrown == 4
    assert ObjectRepository.get_instance().has_label('throwers')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_random_structural_objects_moving_occluders():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'moving_occluders',
            'num': 3,
            'labels': 'test_label'
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'moving_occluders'
    assert component.random_structural_objects.num == 3

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'moving_occluders'
    assert computed[0].num == 3

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # moving occluders create 2 objects each
    assert len(objs) == 6
    for i, obj in enumerate(objs):
        assert obj['structure']
        assert obj['id'].startswith('occluder')
        if i % 2 == 0:
            occ = obj
            assert occ['id'].startswith("occluder_wall")
            assert occ['type'] == 'cube'
            assert occ['structure']
            assert occ['shows']
            assert occ['moves']
            assert occ['rotates']
        else:
            pole = obj
            assert pole['id'].startswith("occluder_pole")
            assert pole['type'] == 'cylinder'
            assert pole['structure']
            assert pole['shows']
            assert pole['moves']
        assert obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('moving_occluders')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_random_structural_objects_holes():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'holes',
            'num': 50
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'holes'
    assert component.random_structural_objects.num == 50

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'holes'
    assert computed[0].num == 50

    scene = component.update_ile_scene(prior_scene_custom_size(12, 13))
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 0
    holes = scene['holes']
    assert len(holes) == 50
    # moving occluders create 2 objects each
    for hole in holes:
        assert -6 <= hole['x'] <= 6
        assert -6 <= hole['z'] <= 6


def test_random_structural_objects_hole_fail_under_performer():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'holes',
            'num': 1
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'holes'
    assert component.random_structural_objects.num == 1

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'holes'
    assert computed[0].num == 1

    scene = prior_scene_custom_size(1, 1)
    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_random_structural_objects_floor_textures():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'floor_materials',
            'num': 50
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'floor_materials'
    assert component.random_structural_objects.num == 50

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'floor_materials'
    assert computed[0].num == 50

    scene = component.update_ile_scene(prior_scene_custom_size(12, 13))
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 0
    holes = scene['holes']
    assert len(holes) == 0
    ft = scene['floorTextures']
    # moving occluders create 2 objects each
    num_floor_mats = 0
    for text in ft:
        loc_list = text['positions']
        for loc in loc_list:
            assert -6 <= loc['x'] <= 6
            assert -6 <= loc['z'] <= 6
            num_floor_mats += 1
    assert num_floor_mats == 50


def test_random_structural_objects_floor_materials_under_performer():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'floor_materials',
            'num': 1
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'floor_materials'
    assert component.random_structural_objects.num == 1

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'floor_materials'
    assert computed[0].num == 1

    scene = prior_scene_custom_size(1, 1)
    scene = component.update_ile_scene(scene)
    ft = scene['floorTextures']
    assert len(ft) == 1
    pos = ft[0]['positions']
    assert len(pos) == 1
    assert pos[0]['x'] == 0
    assert pos[0]['z'] == 0


def test_random_structural_objects_lava():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'lava',
            'num': 10
        }
    })
    scene = component.update_ile_scene(prior_scene())
    assert len(scene['objects']) == 0
    total_count = 0
    for item in scene['floorTextures']:
        assert (
            item['material'] ==
            'Stylized Lava Texture/Materials/Stylize_Lava_diffuse'
        )
        for area in item['positions']:
            assert -5 <= area['x'] <= 5
            assert -5 <= area['z'] <= 5
        total_count += len(item['positions'])
    assert total_count == 10


def test_random_structural_objects_occluding_wall():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'occluding_walls',
            'num': 1,
            'labels': 'test_label'
        }
    })

    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert (component.random_structural_objects.type ==
            'occluding_walls')
    assert component.random_structural_objects.num == 1
    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'occluding_walls'
    assert computed[0].num == 1

    scene = prior_scene_with_target()

    scene = component.update_ile_scene(scene)
    objs = scene['objects']
    assert len(objs) in [2, 4]
    for i in range(len(objs)):
        if i > 0:
            assert objs[i]['debug']['random_position']
    assert objs[0]['debug']['positionedBy']
    assert objs[1]['debug']['positionedBy']
    assert ObjectRepository.get_instance().has_label('occluding_walls')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_random_structural_objects_placers():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'placers',
            'num': 5,
            'labels': 'test_label'
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'placers'
    assert component.random_structural_objects.num == 5

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'placers'
    assert computed[0].num == 5

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 10
    num_placers = 0
    num_placed = 0
    for obj in objs:
        if obj.get('structure', False):
            assert obj['id'].startswith('placer_')
            num_placers += 1
        else:
            num_placed += 1

    assert num_placed == num_placers
    assert num_placers == 5
    assert num_placed == 5
    assert ObjectRepository.get_instance().has_label('placers')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_random_structural_objects_doors():
    component = RandomStructuralObjectsComponent({
        'random_structural_objects': {
            'type': 'doors',
            'num': 3,
            'labels': 'test_label'
        }
    })
    assert isinstance(
        component.random_structural_objects,
        RandomStructuralObjectConfig)
    assert component.random_structural_objects.type == 'doors'
    assert component.random_structural_objects.num == 3

    computed = component.get_random_structural_objects()
    assert isinstance(computed, List)
    assert computed[0].type == 'doors'
    assert computed[0].num == 3

    scene = prior_scene()
    scene = component.update_ile_scene(scene)
    objects = scene['objects']
    assert len(objects) == 3
    for obj in objects:
        assert obj['id'].startswith('door')
        assert obj['type'] == 'door_4'
        assert obj['kinematic']
        assert obj['openable']
        assert obj['structure']
        assert obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('doors')
    assert ObjectRepository.get_instance().has_label('test_label')


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
            'labels': 'test_label',
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
    assert not obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('walls')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_walls_no_num():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]
    component = SpecificStructuralObjectsComponent({
        'structural_walls': {
            'labels': 'test_label',
            'position': {
                'x': 5,
                'y': 0,
                'z': 1
            },
            'rotation_y': 78,
            'material': my_mats,
            'width': 2,
            'height': 3
        }
    })
    pre_walls = component.structural_walls
    assert isinstance(pre_walls, StructuralWallConfig)
    assert isinstance(pre_walls.position, VectorFloatConfig)
    assert pre_walls.position.x == 5
    assert pre_walls.position.z == 1
    assert pre_walls.rotation_y == 78
    assert pre_walls.material == my_mats
    assert pre_walls.width == 2
    assert pre_walls.height == 3

    # computed walls
    cwalls = component.get_structural_walls()
    assert isinstance(cwalls, StructuralWallConfig)
    assert isinstance(cwalls.position, Vector3d)
    assert cwalls.position.x == 5
    assert cwalls.position.z == 1
    assert cwalls.rotation_y == 78
    assert isinstance(cwalls.material, str)
    assert cwalls.material in my_mats
    assert cwalls.width == 2
    assert cwalls.height == 3

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 0
    assert not ObjectRepository.get_instance().has_label('walls')
    assert not ObjectRepository.get_instance().has_label('test_label')


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
    assert obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('walls')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_platforms_full():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]
    component = SpecificStructuralObjectsComponent({
        'structural_platforms': {
            'num': 1,
            'labels': 'test_label',
            'position': {
                'x': 1,
                'y': 2,
                'z': 3
            },
            'rotation_y': 30,
            'material': my_mats,
            'scale': {
                'x': 1.4,
                'y': 1.5,
                'z': 1.6
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
    assert scale.x == 1.4
    assert scale.y == 1.5
    assert scale.z == 1.6

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
    assert scale.x == 1.4
    assert scale.y == 1.5
    assert scale.z == 1.6

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects.
    assert len(objs) == 1
    obj = objs[0]
    assert not obj['debug']['random_position']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    rot = show['rotation']
    assert pos['x'] == 1
    assert pos['z'] == 3
    assert rot['y'] == 30
    assert ObjectRepository.get_instance().has_label('platforms')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_platforms_min_scale_as_number():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_platforms': {
                'num': 1,
                'scale': 0.4
            }
        })


def test_structural_objects_platforms_min_scale_as_vector():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_platforms': {
                'num': 1,
                'scale': {
                    'x': 1,
                    'y': 0.4,
                    'z': 1
                }
            }
        })


def test_structural_objects_platforms_scale():
    component = SpecificStructuralObjectsComponent({
        'structural_platforms': {
            'num': 1,
            'scale': {
                'x': {
                    'min': 1.3,
                    'max': 1.5
                },
                'y': [0.6, 0.7, 0.8],
                'z': 0.9
            }

        }
    })
    pre_plat = component.structural_platforms
    assert isinstance(pre_plat, StructuralPlatformConfig)
    assert pre_plat.num == 1
    scale = pre_plat.scale
    assert isinstance(scale, VectorFloatConfig)
    assert scale.x == MinMaxFloat(1.3, 1.5)
    assert scale.y == [.6, .7, .8]
    assert scale.z == .9

    # computed walls
    cplat = component.get_structural_platforms()
    assert isinstance(cplat, StructuralPlatformConfig)
    assert cplat.num == 1
    scale = cplat.scale
    assert isinstance(scale, Vector3d)
    assert 1.3 <= scale.x <= 1.5
    assert scale.y in [0.6, 0.7, 0.8]
    assert scale.z == .9

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 1
    obj = objs[0]
    assert obj['structure']
    show = obj['shows'][0]
    scale = show['scale']
    assert 1.3 <= scale['x'] <= 1.5
    assert scale['y'] in [0.6, 0.7, 0.8]
    assert scale['z'] == .9
    assert obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('platforms')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_platforms_variables():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]
    component = SpecificStructuralObjectsComponent({
        'structural_platforms': {
            'num': 1,
            'labels': 'test_label',
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
                'min': 0.8,
                'max': 1.2
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
    assert scale == MinMaxFloat(min=0.8, max=1.2)

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
    assert 0.2 <= scale <= 1.2

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
    assert 0.8 <= scale['x'] <= 1.2
    assert 0.8 <= scale['y'] <= 1.2
    assert 0.8 <= scale['z'] <= 1.2
    assert obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('platforms')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_l_occluders_full():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]
    component = SpecificStructuralObjectsComponent({
        'structural_l_occluders': {
            'num': 1,
            'labels': 'test_label',
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
        assert not obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('l_occluders')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_ramps_full():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]

    component = SpecificStructuralObjectsComponent({
        'structural_ramps': {
            'num': 1,
            'labels': 'test_label',
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
    assert not obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('ramps')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_ramps_labels_convert_array():
    component = SpecificStructuralObjectsComponent({
        'structural_ramps': {
            'num': 1,
            'labels': "test_label"
        }
    })
    pre_ramp = component.structural_ramps
    assert isinstance(pre_ramp, StructuralRampConfig)
    assert pre_ramp.num == 1
    assert pre_ramp.labels == "test_label"

    # computed ramps
    cramp = component.get_structural_ramps()
    assert isinstance(cramp, StructuralRampConfig)
    assert cramp.num == 1
    assert cramp.labels == "test_label"

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 1
    assert objs[0]['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('ramps')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_dropper():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]
    component = SpecificStructuralObjectsComponent({
        'structural_droppers': {
            'num': 1,
            'labels': 'test_label',
            'position_x': 2,
            'position_z': 3,
            'drop_step': 4,
            'projectile_shape': 'soccer_ball',
            'projectile_material': my_mats,
            'projectile_scale': 1.2
        }
    })

    pre_dropper = component.structural_droppers
    assert isinstance(pre_dropper, StructuralDropperConfig)
    assert pre_dropper.num == 1
    assert pre_dropper.position_x == 2
    assert pre_dropper.position_z == 3
    assert pre_dropper.drop_step == 4
    assert pre_dropper.projectile_shape == 'soccer_ball'
    assert pre_dropper.projectile_material == my_mats
    assert pre_dropper.projectile_scale == 1.2

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    drop = objs[0]
    proj = objs[1]
    assert drop['id'].startswith("dropping_device")
    assert drop['type'] == 'tube_wide'
    show = drop['shows'][0]
    assert show['position']['x'] == 2
    assert show['position']['z'] == 3
    assert proj['type'] == 'soccer_ball'
    assert proj['debug']['positionedBy'] == 'mechanism'
    assert proj['moveable']
    assert proj['togglePhysics'][0]['stepBegin'] == 4
    show = proj['shows'][0]
    assert show['position']['x'] == 2
    assert show['position']['z'] == 3
    assert show['scale']['x'] == 1.2
    assert show['scale']['y'] == 1.2
    assert show['scale']['z'] == 1.2
    assert ObjectRepository.get_instance().has_label('droppers')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_dropper_with_existing_labels():
    component = SpecificStructuralObjectsComponent({
        'structural_droppers': {
            'num': 1,
            'position_x': 2,
            'position_z': 3,
            'drop_step': 4,
            'projectile_labels': TARGET_LABEL
        }
    })

    pre_dropper = component.structural_droppers
    assert isinstance(pre_dropper, StructuralDropperConfig)
    assert pre_dropper.num == 1
    assert pre_dropper.position_x == 2
    assert pre_dropper.position_z == 3
    assert pre_dropper.drop_step == 4
    assert pre_dropper.projectile_labels == TARGET_LABEL

    # Prior scene must have target object.
    scene = component.update_ile_scene(prior_scene_with_target())

    assert len(scene['objects']) == 2
    target = scene['objects'][0]
    device = scene['objects'][1]

    assert target['type'] == 'soccer_ball'
    assert target['debug']['positionedBy'] == 'mechanism'
    assert target['kinematic']
    assert target['togglePhysics'][0]['stepBegin'] == 4
    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == device['shows'][0]['position']
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    assert device['id'].startswith("dropping_device")
    assert device['type'] == 'tube_wide'
    assert device['kinematic']
    assert device['structure']
    assert len(device['shows']) == 1
    assert device['shows'][0]['position']['x'] == 2
    assert device['shows'][0]['position']['y'] == 2.775
    assert device['shows'][0]['position']['z'] == 3
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert device['shows'][0]['scale'] == {'x': 0.41, 'y': 0.45, 'z': 0.41}
    assert ObjectRepository.get_instance().has_label('droppers')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_dropper_with_missing_targets():
    component = SpecificStructuralObjectsComponent({
        'structural_droppers': {
            'num': 1,
            'position_x': 2,
            'position_z': 3,
            'drop_step': 4,
            'projectile_labels': TARGET_LABEL
        }
    })

    # Error because object with "target" label must exist in scene.
    with pytest.raises(ILEException):
        # Prior scene must NOT have target object.
        component.update_ile_scene(prior_scene())


def test_structural_objects_dropper_with_new_labels():
    component = SpecificStructuralObjectsComponent({
        'structural_droppers': {
            'num': 1,
            'position_x': 2,
            'position_z': 3,
            'drop_step': 4,
            'projectile_labels': 'my_projectile',
            'projectile_shape': 'soccer_ball',
            'projectile_scale': 2
        }
    })

    pre_dropper = component.structural_droppers
    assert isinstance(pre_dropper, StructuralDropperConfig)
    assert pre_dropper.num == 1
    assert pre_dropper.position_x == 2
    assert pre_dropper.position_z == 3
    assert pre_dropper.drop_step == 4
    assert pre_dropper.projectile_labels == 'my_projectile'
    assert pre_dropper.projectile_shape == 'soccer_ball'
    assert pre_dropper.projectile_scale == 2

    scene = prior_scene_with_target()
    original_position = {
        'x': scene['objects'][0]['shows'][0]['position']['x'],
        'y': scene['objects'][0]['shows'][0]['position']['y'],
        'z': scene['objects'][0]['shows'][0]['position']['z']
    }
    original_rotation = {
        'x': scene['objects'][0]['shows'][0]['rotation']['x'],
        'y': scene['objects'][0]['shows'][0]['rotation']['y'],
        'z': scene['objects'][0]['shows'][0]['rotation']['z']
    }
    scene = component.update_ile_scene(scene)

    assert len(scene['objects']) == 3
    target = scene['objects'][0]
    device = scene['objects'][1]
    projectile = scene['objects'][2]

    assert target['type'] == 'soccer_ball'
    assert 'positionedBy' not in target['debug']
    assert 'kinematic' not in target
    assert 'togglePhysics' not in target
    assert target['shows'][0]['position'] == original_position
    assert target['shows'][0]['rotation'] == original_rotation
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    assert projectile['type'] == 'soccer_ball'
    assert projectile['debug']['positionedBy'] == 'mechanism'
    assert projectile['kinematic']
    assert projectile['togglePhysics'][0]['stepBegin'] == 4
    assert len(projectile['shows']) == 1
    assert projectile['shows'][0]['position'] == device['shows'][0]['position']
    assert projectile['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert projectile['shows'][0]['scale'] == {'x': 2, 'y': 2, 'z': 2}

    assert device['id'].startswith("dropping_device")
    assert device['type'] == 'tube_wide'
    assert device['kinematic']
    assert device['structure']
    assert len(device['shows']) == 1
    assert device['shows'][0]['position']['x'] == 2
    assert device['shows'][0]['position']['y'] == 2.545
    assert device['shows'][0]['position']['z'] == 3
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert device['shows'][0]['scale'] == {'x': 0.83, 'y': 0.91, 'z': 0.83}
    assert ObjectRepository.get_instance().has_label('droppers')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_dropper_with_used_target():
    component = SpecificStructuralObjectsComponent({
        'structural_droppers': {
            # Configure multiple dropper mechanisms with the "target" label.
            'num': 2,
            'position_x': 2,
            'position_z': 3,
            'drop_step': 4,
            'projectile_labels': TARGET_LABEL
        }
    })

    # Error because object with "target" label must not already be used by
    # another mechanism.
    with pytest.raises(ILEException):
        # Prior scene must have target object.
        component.update_ile_scene(prior_scene_with_target())


def test_structural_objects_dropper_no_spec():
    component = SpecificStructuralObjectsComponent({
        'structural_droppers': {
            'num': 1
        }
    })

    pre_dropper = component.structural_droppers
    assert isinstance(pre_dropper, StructuralDropperConfig)
    assert pre_dropper.num == 1

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    drop = objs[0]
    proj = objs[1]
    assert drop['id'].startswith("dropping_device")
    assert drop['type'] == 'tube_wide'
    show = drop['shows'][0]
    drop_pos = show['position']
    assert -5 < drop_pos['x'] < 5
    assert -5 < drop_pos['z'] < 5
    assert proj['moveable']
    assert 0 <= proj['togglePhysics'][0]['stepBegin'] <= 10
    show = proj['shows'][0]
    assert show['position']['x'] == drop_pos['x']
    assert show['position']['z'] == drop_pos['z']
    assert ObjectRepository.get_instance().has_label('droppers')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_thrower():
    my_mats = [
        "PLASTIC_MATERIALS",
        "AI2-THOR/Materials/Metals/Brass 1"
    ]
    component = SpecificStructuralObjectsComponent({
        'structural_throwers': {
            'num': 1,
            'labels': 'test_label',
            'wall': 'front',
            'position_wall': 0,
            'height': 1,
            'rotation': 7,
            'throw_step': 3,
            'throw_force': 600,
            'projectile_shape': 'soccer_ball',
            'projectile_material': my_mats,
            'projectile_scale': 1.2
        }
    })

    pre_thrower = component.structural_throwers
    assert isinstance(pre_thrower, StructuralThrowerConfig)
    assert pre_thrower.num == 1
    assert pre_thrower.wall == WallSide.FRONT
    assert pre_thrower.position_wall == 0
    assert pre_thrower.height == 1
    assert pre_thrower.rotation == 7
    assert pre_thrower.throw_step == 3
    assert pre_thrower.throw_force == 600
    assert pre_thrower.projectile_shape == 'soccer_ball'
    assert pre_thrower.projectile_material == my_mats
    assert pre_thrower.projectile_scale == 1.2

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    throw = objs[0]
    proj = objs[1]
    assert throw['id'].startswith("throwing_device")
    assert throw['type'] == 'tube_wide'
    assert throw['structure']
    show = throw['shows'][0]
    assert show['position']['x'] == 0
    assert show['position']['y'] == 1
    assert 4.5 < show['position']['z'] < 5
    assert show['rotation']['x'] == 0
    assert show['rotation']['y'] == 90
    assert show['rotation']['z'] == 97
    assert proj['type'] == 'soccer_ball'
    assert proj['debug']['positionedBy'] == 'mechanism'
    assert proj['moveable']
    force = proj['forces'][0]
    assert force['stepBegin'] == 3
    assert force['stepEnd'] == 3
    assert force['relative']

    show = proj['shows'][0]
    assert show['position']['x'] == 0
    assert show['position']['y'] == 1
    assert 4.5 < show['position']['z'] < 5
    assert show['scale']['x'] == 1.2
    assert show['scale']['y'] == 1.2
    assert show['scale']['z'] == 1.2
    assert ObjectRepository.get_instance().has_label('throwers')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_thrower_with_existing_labels():
    component = SpecificStructuralObjectsComponent({
        'structural_throwers': {
            'num': 1,
            'wall': 'front',
            'position_wall': 0,
            'height': 1,
            'rotation': 7,
            'throw_step': 3,
            'throw_force': 600,
            'projectile_labels': TARGET_LABEL
        }
    })

    pre_thrower = component.structural_throwers
    assert isinstance(pre_thrower, StructuralThrowerConfig)
    assert pre_thrower.num == 1
    assert pre_thrower.wall == WallSide.FRONT
    assert pre_thrower.position_wall == 0
    assert pre_thrower.height == 1
    assert pre_thrower.rotation == 7
    assert pre_thrower.throw_step == 3
    assert pre_thrower.throw_force == 600
    assert pre_thrower.projectile_labels == TARGET_LABEL

    # Prior scene must have target object.
    scene = component.update_ile_scene(prior_scene_with_target())

    assert len(scene['objects']) == 2
    target = scene['objects'][0]
    device = scene['objects'][1]

    assert target['type'] == 'soccer_ball'
    assert target['debug']['positionedBy'] == 'mechanism'
    assert len(target['forces']) == 1
    assert target['forces'][0]['relative']
    assert target['forces'][0]['stepBegin'] == 3
    assert target['forces'][0]['stepEnd'] == 3
    assert target['forces'][0]['vector'] == {'x': 600, 'y': 0, 'z': 0}
    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == device['shows'][0]['position']
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    assert device['id'].startswith("throwing_device")
    assert device['type'] == 'tube_wide'
    assert device['kinematic']
    assert device['structure']
    assert len(device['shows']) == 1
    assert device['shows'][0]['position']['x'] == 0
    assert device['shows'][0]['position']['y'] == 1
    assert device['shows'][0]['position']['z'] == 4.835
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 97}
    assert device['shows'][0]['scale'] == {'x': 0.41, 'y': 0.6, 'z': 0.41}
    assert ObjectRepository.get_instance().has_label('throwers')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_thrower_with_missing_targets():
    component = SpecificStructuralObjectsComponent({
        'structural_throwers': {
            'num': 1,
            'wall': 'front',
            'position_wall': 0,
            'height': 1,
            'rotation': 7,
            'throw_step': 3,
            'throw_force': 600,
            'projectile_labels': TARGET_LABEL
        }
    })

    # Error because object with "target" label must exist in scene.
    with pytest.raises(ILEException):
        # Prior scene must NOT have target object.
        component.update_ile_scene(prior_scene())


def test_structural_objects_thrower_with_new_labels():
    component = SpecificStructuralObjectsComponent({
        'structural_throwers': {
            'num': 1,
            'wall': 'front',
            'position_wall': 0,
            'height': 1,
            'rotation': 7,
            'throw_step': 3,
            'throw_force': 600,
            'projectile_labels': 'my_projectile',
            'projectile_shape': 'soccer_ball',
            'projectile_scale': 2
        }
    })

    pre_thrower = component.structural_throwers
    assert isinstance(pre_thrower, StructuralThrowerConfig)
    assert pre_thrower.num == 1
    assert pre_thrower.wall == WallSide.FRONT
    assert pre_thrower.position_wall == 0
    assert pre_thrower.height == 1
    assert pre_thrower.rotation == 7
    assert pre_thrower.throw_step == 3
    assert pre_thrower.throw_force == 600
    assert pre_thrower.projectile_labels == 'my_projectile'
    assert pre_thrower.projectile_shape == 'soccer_ball'
    assert pre_thrower.projectile_scale == 2

    scene = prior_scene_with_target()
    original_position = {
        'x': scene['objects'][0]['shows'][0]['position']['x'],
        'y': scene['objects'][0]['shows'][0]['position']['y'],
        'z': scene['objects'][0]['shows'][0]['position']['z']
    }
    original_rotation = {
        'x': scene['objects'][0]['shows'][0]['rotation']['x'],
        'y': scene['objects'][0]['shows'][0]['rotation']['y'],
        'z': scene['objects'][0]['shows'][0]['rotation']['z']
    }
    scene = component.update_ile_scene(scene)

    assert len(scene['objects']) == 3
    target = scene['objects'][0]
    device = scene['objects'][1]
    projectile = scene['objects'][2]

    assert target['type'] == 'soccer_ball'
    assert 'positionedBy' not in target['debug']
    assert 'kinematic' not in target
    assert 'togglePhysics' not in target
    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == original_position
    assert target['shows'][0]['rotation'] == original_rotation
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}

    assert projectile['type'] == 'soccer_ball'
    assert projectile['debug']['positionedBy'] == 'mechanism'
    assert len(projectile['forces']) == 1
    assert projectile['forces'][0]['relative']
    assert projectile['forces'][0]['stepBegin'] == 3
    assert projectile['forces'][0]['stepEnd'] == 3
    assert projectile['forces'][0]['vector'] == {'x': 1200, 'y': 0, 'z': 0}
    assert len(projectile['shows']) == 1
    assert projectile['shows'][0]['position'] == device['shows'][0]['position']
    assert projectile['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 0}
    assert projectile['shows'][0]['scale'] == {'x': 2, 'y': 2, 'z': 2}

    assert device['id'].startswith("throwing_device")
    assert device['type'] == 'tube_wide'
    assert device['kinematic']
    assert device['structure']
    assert len(device['shows']) == 1
    assert device['shows'][0]['position']['x'] == 0
    assert device['shows'][0]['position']['y'] == 1
    assert device['shows'][0]['position']['z'] == 4.67
    assert device['shows'][0]['rotation'] == {'x': 0, 'y': 90, 'z': 97}
    assert device['shows'][0]['scale'] == {'x': 0.83, 'y': 1.2, 'z': 0.83}
    assert ObjectRepository.get_instance().has_label('throwers')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_thrower_no_spec():
    component = SpecificStructuralObjectsComponent({
        'structural_throwers': {
            'num': 1
        }
    })

    pre_thrower = component.structural_throwers
    assert isinstance(pre_thrower, StructuralThrowerConfig)
    assert pre_thrower.num == 1

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    throw = objs[0]
    proj = objs[1]
    assert throw['id'].startswith("throwing_device")
    assert throw['type'] == 'tube_wide'
    assert throw['structure']
    show = throw['shows'][0]
    throw_pos = show['position']
    assert -5 < throw_pos['x'] < 5
    assert 0 < throw_pos['y'] < 3
    assert -5 < throw_pos['z'] < 5
    assert proj['moveable']
    force = proj['forces'][0]
    force_begin = force['stepBegin']
    assert 0 <= force_begin <= 10
    assert force['stepEnd'] == force_begin
    assert force['relative']

    show = proj['shows'][0]
    assert show['position']['x'] == throw_pos['x']
    assert show['position']['y'] == throw_pos['y']
    assert show['position']['z'] == throw_pos['z']
    assert ObjectRepository.get_instance().has_label('throwers')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_thrower_with_used_target():
    component = SpecificStructuralObjectsComponent({
        'structural_throwers': {
            # Configure multiple thrower mechanisms with the "target" label.
            'num': 2,
            'wall': 'front',
            'position_wall': 0,
            'height': 1,
            'rotation': 7,
            'throw_step': 3,
            'throw_force': 600,
            'projectile_labels': TARGET_LABEL
        }
    })

    # Error because object with "target" label must not already be used by
    # another mechanism.
    with pytest.raises(ILEException):
        # Prior scene must have target object.
        component.update_ile_scene(prior_scene_with_target())


def test_structural_objects_thrower_high_angle():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_throwers': {
                'num': 1,
                'rotation': 56,
            }
        })


def test_structural_objects_thrower_invalid_wall():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_throwers': {
                'num': 1,
                'wall': 'invalid',
            }
        })


def test_structural_objects_moving_occluder():
    component = SpecificStructuralObjectsComponent({
        'structural_moving_occluders': {
            'num': 1
        }
    })

    pre_occ = component.structural_moving_occluders
    assert isinstance(pre_occ, StructuralMovingOccluderConfig)
    assert pre_occ.num == 1

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    occ = objs[0]
    pole = objs[1]
    assert occ['id'].startswith("occluder_wall")
    assert occ['type'] == 'cube'
    assert occ['structure']
    assert occ['shows']
    assert occ['moves']
    assert occ['rotates']

    assert pole['id'].startswith("occluder_pole")
    assert pole['type'] == 'cylinder'
    assert pole['structure']
    assert pole['shows']
    assert pole['moves']
    assert occ['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('moving_occluders')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_moving_occluder_full():
    component = SpecificStructuralObjectsComponent({
        'structural_moving_occluders': {
            'num': {
                'min': 1,
                'max': 3
            },
            'labels': 'test_label',
            'wall_material': 'AI2-THOR/Materials/Metals/Brass 1',
            'pole_material': 'AI2-THOR/Materials/Metals/Brass 1',
            'position_x': [1, 2, 1.5, -3, -2, 4, -4, 5, -5],
            'position_z': {
                'min': -5,
                'max': 5.5
            },
            'origin': 'top',
            'occluder_height': 0.9,
            'occluder_width': .5,
            'occluder_thickness': 0.07,
            'repeat_movement': True,
            'repeat_interval': 5,
            'rotation_y': 90
        }
    })

    pre_occ = component.structural_moving_occluders
    assert isinstance(pre_occ, StructuralMovingOccluderConfig)
    assert pre_occ.num == MinMaxInt(1, 3)

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) in [2, 4, 6]
    for i, obj in enumerate(objs):
        if i % 2 == 0:
            occ = obj
            assert occ['id'].startswith("occluder_wall")
            assert occ['type'] == 'cube'
            assert occ['structure']
            assert occ['shows']
            assert occ['moves']
            assert occ['rotates']
            move = occ['moves'][0]
            rot = occ['rotates'][0]
            assert move['stepBegin'] == 1
            assert move['stepEnd'] == 6
            assert move['repeat']
            assert move['stepWait'] == 22
            assert rot['stepBegin'] == 7
            assert rot['stepEnd'] == 9
            assert rot['repeat']
            assert rot['stepWait'] == 25
            assert occ['debug']['random_position']
        else:
            pole = obj
            assert pole['id'].startswith("occluder_pole")
            assert pole['type'] == 'cylinder'
            assert pole['structure']
            assert pole['shows']
            assert pole['moves']
            move = pole['moves'][0]
            assert move['stepBegin'] == 1
            assert move['stepEnd'] == 6
            assert move['repeat']
            assert move['stepWait'] == 22
    assert ObjectRepository.get_instance().has_label('moving_occluders')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_moving_occluder_fail():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_throwers': {
                'num': 3,
                'position_x': 3,
                'position_z': 3,
            }
        })


def test_floor_features_defaults():
    component = SpecificStructuralObjectsComponent({})
    assert component.holes is None
    assert component.floor_material_override is None
    assert component.lava is None

    scene = component.update_ile_scene(prior_scene_custom_size(12, 13))
    holes = scene['holes']
    textures = scene['floorTextures']
    assert isinstance(holes, list)
    assert len(holes) == 0
    assert isinstance(textures, list)
    assert len(textures) == 0


def test_floor_features_holes_specific():
    component = SpecificStructuralObjectsComponent({
        'holes': [{
            'num': 1,
            'position_x': 2,
            'position_z': 3
        }, {
            'num': 1,
            'position_x': -2,
            'position_z': -3
        }]
    })
    pre_hole = component.holes[0]
    assert isinstance(pre_hole, FloorAreaConfig)
    assert pre_hole.num == 1
    assert pre_hole.position_x == 2
    assert pre_hole.position_z == 3
    pre_hole = component.holes[1]
    assert isinstance(pre_hole, FloorAreaConfig)
    assert pre_hole.num == 1
    assert pre_hole.position_x == -2
    assert pre_hole.position_z == -3

    scene = component.update_ile_scene(prior_scene_custom_size(12, 13))
    assert isinstance(scene['holes'], list)
    holes = scene['holes']
    assert len(holes) == 2


def test_floor_features_holes_variables():
    component = SpecificStructuralObjectsComponent({
        'holes': {
            'num': {
                'min': 5,
                'max': 6
            },

            'position_x': [1, 2, -3, -2, 4, -4, 5, -5],
            'position_z': {
                'min': -5,
                'max': -1
            },
        }
    })

    pre_hole = component.holes
    assert isinstance(pre_hole, FloorAreaConfig)
    assert pre_hole.num == MinMaxInt(5, 6)
    assert pre_hole.position_x == [1, 2, -3, -2, 4, -4, 5, -5]
    assert pre_hole.position_z == MinMaxInt(-5, -1)

    scene = component.update_ile_scene(prior_scene_custom_size(12, 13))
    assert isinstance(scene['holes'], list)
    holes = scene['holes']
    assert len(holes) in [5, 6]
    for hole in holes:
        assert hole['x'] in [1, 2, -3, -2, 4, -4, 5, -5]
        assert -5 <= hole['z'] <= -1


def test_floor_features_holes_variables_one_missing():
    component = SpecificStructuralObjectsComponent({
        'holes': [{
            'num': 3,
            'position_x': 3,
        }, {
            'num': 4,
            'position_x': [-2, -4],
        }]
    })

    assert isinstance(component.holes, List)
    pre_hole = component.holes[0]
    assert isinstance(pre_hole, FloorAreaConfig)
    assert pre_hole.num == 3
    assert pre_hole.position_x == 3
    assert pre_hole.position_z is None
    pre_hole = component.holes[1]
    assert isinstance(pre_hole, FloorAreaConfig)
    assert pre_hole.num == 4
    assert pre_hole.position_x == [-2, -4]
    assert pre_hole.position_z is None

    scene = component.update_ile_scene(prior_scene_custom_size(12, 13))
    assert isinstance(scene['holes'], list)
    holes = scene['holes']
    assert len(holes) == 7
    for i, hole in enumerate(holes):
        if i < 3:
            assert hole['x'] == 3
        else:
            assert hole['x'] in [-2, -4]
        assert -6 <= hole['z'] <= 6


def test_floor_features_holes_fail_duplicate():
    component = SpecificStructuralObjectsComponent({
        'holes': {
            'num': 3,
            'position_x': 3,
            'position_z': 3,
        }
    })
    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene_custom_size(12, 13))


def test_floor_features_holes_fail_outside_bounds():
    component = SpecificStructuralObjectsComponent({
        'holes': {
            'num': 1,
            'position_x': 3,
            'position_z': 7,
        }
    })
    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene_custom_size(12, 13))


def test_floor_features_materials_fail_duplicate():
    component = SpecificStructuralObjectsComponent({
        'floor_material_override': {
            'num': 3,
            'position_x': 3,
            'position_z': 3,
        }
    })
    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene_custom_size(12, 13))


def test_floor_features_materials_fail_outside_bounds():
    component = SpecificStructuralObjectsComponent({
        'floor_material_override': {
            'num': 1,
            'position_x': 3,
            'position_z': 7,
        }
    })
    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene_custom_size(12, 13))


def test_floor_features_materials_fail_bad_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'floor_material_override': {
                'num': 1,
                'position_x': 3,
                'position_z': 0,
                'material': "not at material"
            }
        })


def test_floor_features_materials_specific():
    component = SpecificStructuralObjectsComponent({
        'floor_material_override': [{
            'num': 1,
            'position_x': 3,
            'position_z': 3,
            'material': 'AI2-THOR/Materials/Metals/BrushedAluminum_Blue'
        }, {
            'num': 1,
            'position_x': [-2, -4],
            'material': 'PLASTIC_MATERIALS'
        }]
    })

    assert isinstance(component.floor_material_override, List)
    pre_mat = component.floor_material_override[0]
    assert isinstance(pre_mat, FloorMaterialConfig)
    assert pre_mat.num == 1
    assert pre_mat.position_x == 3
    assert pre_mat.position_z == 3
    assert pre_mat.material == 'AI2-THOR/Materials/Metals/BrushedAluminum_Blue'
    pre_mat = component.floor_material_override[1]
    assert isinstance(pre_mat, FloorMaterialConfig)
    assert pre_mat.num == 1
    assert pre_mat.position_x == [-2, -4]
    assert pre_mat.position_z is None
    assert pre_mat.material == 'PLASTIC_MATERIALS'

    scene = component.update_ile_scene(prior_scene_custom_size(12, 13))
    assert isinstance(scene['floorTextures'], list)
    mats = scene['floorTextures']
    assert len(mats) == 2
    mat = mats[0]
    assert mat['material'] == 'AI2-THOR/Materials/Metals/BrushedAluminum_Blue'
    pos = mat['positions']
    assert isinstance(pos, list)
    assert len(pos) == 1
    assert pos[0] == {'x': 3, 'z': 3}

    mat = mats[1]
    plastic = [m[0] for m in materials.PLASTIC_MATERIALS]
    assert mat['material'] in plastic
    pos = mat['positions']
    assert isinstance(pos, list)
    assert len(pos) == 1
    assert pos[0]['x'] in [-2, -4]
    assert -7 <= pos[0]['z'] <= 7


def test_floor_features_materials_missing_material():
    component = SpecificStructuralObjectsComponent({
        'floor_material_override': [{
            'num': 2,
            'position_x': [5, 6],
            'position_z': 6,
        }]
    })

    assert isinstance(component.floor_material_override, List)
    pre_mat = component.floor_material_override[0]
    assert isinstance(pre_mat, FloorMaterialConfig)
    assert pre_mat.num == 2
    assert pre_mat.position_x == [5, 6]
    assert pre_mat.position_z == 6
    assert pre_mat.material is None

    scene = component.update_ile_scene(prior_scene_custom_size(12, 13))
    assert isinstance(scene['floorTextures'], list)
    num = 0
    mats = scene['floorTextures']
    for mat in mats:
        assert mat['material'] in materials.ALL_UNRESTRICTED_MATERIAL_STRINGS
        for pos in mat['positions']:
            num += 1
            assert pos in [{'x': 5, 'z': 6}, {'x': 6, 'z': 6}]
    assert num == 2


def test_floor_features_materials_missing_location():
    component = SpecificStructuralObjectsComponent({
        'floor_material_override': [{
            'num': 5,
            'material': 'CERAMIC_MATERIALS'
        }]
    })

    assert isinstance(component.floor_material_override, List)
    pre_mat = component.floor_material_override[0]
    assert isinstance(pre_mat, FloorMaterialConfig)
    assert pre_mat.num == 5
    assert pre_mat.position_x is None
    assert pre_mat.position_z is None
    assert pre_mat.material == 'CERAMIC_MATERIALS'

    ceramic = [m[0] for m in materials.CERAMIC_MATERIALS]

    scene = component.update_ile_scene(prior_scene_custom_size(12, 13))
    assert isinstance(scene['floorTextures'], list)
    num = 0
    mats = scene['floorTextures']
    for mat in mats:
        assert mat['material'] in ceramic
        for pos in mat['positions']:
            num += 1
            assert -7 <= pos['x'] <= 7
            assert -7 <= pos['z'] <= 7
    assert num == 5


def test_floor_features_lava_specific():
    component = SpecificStructuralObjectsComponent({
        'lava': [{
            'num': 1,
            'position_x': 2,
            'position_z': 3
        }, {
            'num': 1,
            'position_x': -2,
            'position_z': -3
        }]
    })
    assert isinstance(component.lava[0], FloorAreaConfig)
    assert component.lava[0].num == 1
    assert component.lava[0].position_x == 2
    assert component.lava[0].position_z == 3
    assert isinstance(component.lava[1], FloorAreaConfig)
    assert component.lava[1].num == 1
    assert component.lava[1].position_x == -2
    assert component.lava[1].position_z == -3

    scene = component.update_ile_scene(prior_scene())
    assert scene['floorTextures'] == [{
        'material': 'Stylized Lava Texture/Materials/Stylize_Lava_diffuse',
        'positions': [{'x': 2, 'z': 3}, {'x': -2, 'z': -3}]
    }]


def test_floor_features_lava_variable():
    component = SpecificStructuralObjectsComponent({
        'lava': [{
            'num': {
                'min': 5,
                'max': 6
            },
            'position_x': [1, 2],
            'position_z': {
                'min': -4,
                'max': -1
            },
        }]
    })
    assert isinstance(component.lava[0], FloorAreaConfig)
    assert component.lava[0].num == MinMaxInt(5, 6)
    assert component.lava[0].position_x == [1, 2]
    assert component.lava[0].position_z == MinMaxInt(-4, -1)

    scene = component.update_ile_scene(prior_scene())
    assert len(scene['floorTextures']) == 1
    assert (
        scene['floorTextures'][0]['material'] ==
        'Stylized Lava Texture/Materials/Stylize_Lava_diffuse'
    )
    assert len(scene['floorTextures'][0]['positions']) in [5, 6]
    for area in scene['floorTextures'][0]['positions']:
        assert area['x'] in [1, 2]
        assert -4 <= area['z'] <= -1


def test_floor_features_lava_variable_restricted():
    component = SpecificStructuralObjectsComponent({
        'lava': [{
            'num': 2,
            'position_x': [1, 2],
            'position_z': 3
        }]
    })
    assert isinstance(component.lava[0], FloorAreaConfig)
    assert component.lava[0].num == 2
    assert component.lava[0].position_x == [1, 2]
    assert component.lava[0].position_z == 3

    scene = component.update_ile_scene(prior_scene())
    assert len(scene['floorTextures']) == 1
    assert (
        scene['floorTextures'][0]['material'] ==
        'Stylized Lava Texture/Materials/Stylize_Lava_diffuse'
    )
    assert (
        scene['floorTextures'][0]['positions'] ==
        [{'x': 1, 'z': 3}, {'x': 2, 'z': 3}]
    ) or (
        scene['floorTextures'][0]['positions'] ==
        [{'x': 2, 'z': 3}, {'x': 1, 'z': 3}]
    )


def test_floor_features_lava_with_floor_materials():
    component = SpecificStructuralObjectsComponent({
        'floor_material_override': [{
            'num': 1,
            'position_x': 1,
            'position_z': 1,
            'material': 'Custom/Materials/Blue'
        }, {
            'num': 1,
            'position_x': 0,
            'position_z': 1,
            'material': 'Custom/Materials/Yellow'
        }],
        'lava': [{
            'num': 1,
            'position_x': 0,
            'position_z': -1
        }, {
            'num': 1,
            'position_x': -1,
            'position_z': -1
        }]
    })
    floor_materials = component.floor_material_override
    assert isinstance(floor_materials[0], FloorAreaConfig)
    assert floor_materials[0].material == 'Custom/Materials/Blue'
    assert floor_materials[0].num == 1
    assert floor_materials[0].position_x == 1
    assert floor_materials[0].position_z == 1
    assert isinstance(floor_materials[1], FloorAreaConfig)
    assert floor_materials[1].material == 'Custom/Materials/Yellow'
    assert floor_materials[1].num == 1
    assert floor_materials[1].position_x == 0
    assert floor_materials[1].position_z == 1
    assert isinstance(component.lava[0], FloorAreaConfig)
    assert component.lava[0].num == 1
    assert component.lava[0].position_x == -0
    assert component.lava[0].position_z == -1
    assert isinstance(component.lava[1], FloorAreaConfig)
    assert component.lava[1].num == 1
    assert component.lava[1].position_x == -1
    assert component.lava[1].position_z == -1

    scene = component.update_ile_scene(prior_scene())
    assert scene['floorTextures'] == [{
        'material': 'Custom/Materials/Blue',
        'positions': [{'x': 1, 'z': 1}]
    }, {
        'material': 'Custom/Materials/Yellow',
        'positions': [{'x': 0, 'z': 1}]
    }, {
        'material': 'Stylized Lava Texture/Materials/Stylize_Lava_diffuse',
        'positions': [{'x': 0, 'z': -1}, {'x': -1, 'z': -1}]
    }]


def test_floor_features_lava_fail_duplicate():
    component = SpecificStructuralObjectsComponent({
        'lava': {
            'num': 2,
            'position_x': 3,
            'position_z': 3,
        }
    })
    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene())


def test_floor_features_lava_fail_outside_bounds():
    component = SpecificStructuralObjectsComponent({
        'lava': {
            'num': 1,
            'position_x': 3,
            'position_z': 6,
        }
    })
    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene())


def test_floor_features_lava_fail_overlaps_floor_materials():
    component = SpecificStructuralObjectsComponent({
        'floor_material_override': [{
            'num': 1,
            'position_x': 1,
            'position_z': 1,
            'material': 'Custom/Materials/Red'
        }],
        'lava': [{
            'num': 1,
            'position_x': 1,
            'position_z': 1
        }]
    })
    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene())


def test_structural_objects_occluding_wall_base():
    component = SpecificStructuralObjectsComponent({
        'structural_occluding_walls': {
            'num': 1,
            'labels': 'test_label',
            'type': 'occludes'
        }
    })

    pre_occ = component.structural_occluding_walls
    assert isinstance(pre_occ, StructuralOccludingWallConfig)
    assert pre_occ.num == 1
    assert pre_occ.type == 'occludes'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    assert objs[0]['debug']['positionedBy']
    wall = objs[1]
    assert wall['debug']['positionedBy']
    assert wall['id'].startswith("occludes-")
    assert wall['type'] == 'cube'
    assert wall['structure']
    assert wall['shows']
    show = wall['shows'][0]
    scale = show['scale']
    assert scale['x'] == 0.44
    assert scale['y'] == 0.66
    assert 0.1 <= scale['z'] <= 0.5
    assert ObjectRepository.get_instance().has_label('occluding_walls')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_occluding_wall_short():
    component = SpecificStructuralObjectsComponent({
        'structural_occluding_walls': {
            'num': 1,
            'labels': 'test_label',
            'type': 'short'
        }
    })

    pre_occ = component.structural_occluding_walls
    assert isinstance(pre_occ, StructuralOccludingWallConfig)
    assert pre_occ.num == 1
    assert pre_occ.type == 'short'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    assert objs[0]['debug']['positionedBy']
    wall = objs[1]
    assert wall['debug']['positionedBy']
    assert wall['id'].startswith("short-")
    assert wall['type'] == 'cube'
    assert wall['structure']
    assert wall['shows']
    show = wall['shows'][0]
    scale = show['scale']
    assert scale['x'] == 0.44
    assert scale['y'] < 0.66
    assert 0.1 <= scale['z'] <= 0.5
    assert ObjectRepository.get_instance().has_label('occluding_walls')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_occluding_wall_thin():
    component = SpecificStructuralObjectsComponent({
        'structural_occluding_walls': {
            'num': 1,
            'labels': 'test_label',
            'type': 'thin'
        }
    })

    pre_occ = component.structural_occluding_walls
    assert isinstance(pre_occ, StructuralOccludingWallConfig)
    assert pre_occ.num == 1
    assert pre_occ.type == 'thin'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    assert objs[0]['debug']['positionedBy']
    wall = objs[1]
    assert wall['debug']['positionedBy']
    assert wall['id'].startswith("thin-")
    assert wall['type'] == 'cube'
    assert wall['structure']
    assert wall['shows']
    show = wall['shows'][0]
    scale = show['scale']
    assert scale['x'] < 0.44
    assert scale['y'] == 0.66
    assert 0.1 <= scale['z'] <= 0.5
    assert wall['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('occluding_walls')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_occluding_wall_hole():
    component = SpecificStructuralObjectsComponent({
        'structural_occluding_walls': {
            'num': 1,
            'labels': 'test_label',
            'type': 'hole'
        }
    })

    pre_occ = component.structural_occluding_walls
    assert isinstance(pre_occ, StructuralOccludingWallConfig)
    assert pre_occ.num == 1
    assert pre_occ.type == 'hole'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 4
    assert objs[0]['debug']['positionedBy']
    l_col = objs[1]
    r_col = objs[2]
    top = objs[3]
    assert l_col['debug']['positionedBy']
    assert l_col['id'].startswith("l_col-hole")
    assert l_col['type'] == 'cube'
    assert l_col['structure']
    assert l_col['shows']
    show = l_col['shows'][0]
    scale = show['scale']
    assert scale['x'] == 0.3
    assert scale['y'] == 0.22
    assert 0.1 <= scale['z'] <= 0.5
    assert l_col['debug']['random_position']

    assert r_col['debug']['positionedBy']
    assert r_col['id'].startswith("r_col-hole")
    assert r_col['type'] == 'cube'
    assert r_col['structure']
    assert r_col['shows']
    show = r_col['shows'][0]
    scale = show['scale']
    assert scale['x'] == 0.3
    assert scale['y'] == 0.22
    assert 0.1 <= scale['z'] <= 0.5
    assert r_col['debug']['random_position']

    assert top['debug']['positionedBy']
    assert top['id'].startswith("top-hole")
    assert top['type'] == 'cube'
    assert top['structure']
    assert top['shows']
    show = top['shows'][0]
    scale = show['scale']
    assert scale['x'] == 0.82
    assert scale['y'] == 0.22
    assert 0.1 <= scale['z'] <= 0.5
    assert top['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('occluding_walls')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_occluding_wall_position_rotation():
    component = SpecificStructuralObjectsComponent({
        'structural_occluding_walls': {
            'num': 1,
            'type': 'occludes',
            'position': {
                'x': 1,
                'y': 0,
                'z': 3
            },
            'rotation_y': 43
        }
    })

    pre_occ = component.structural_occluding_walls
    assert isinstance(pre_occ, StructuralOccludingWallConfig)
    assert pre_occ.num == 1
    assert pre_occ.type == 'occludes'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    assert not objs[0]['debug'].get('positionedBy')
    wall = objs[1]
    assert not wall['debug'].get('positionedBy')
    assert wall['id'].startswith("occludes-")
    assert wall['type'] == 'cube'
    assert wall['structure']
    assert wall['shows']
    show = wall['shows'][0]
    scale = show['scale']
    pos = show['position']
    rot = show['rotation']
    assert 0.5 <= scale['x'] <= 2
    assert 0.5 <= scale['y'] <= 2
    assert 0.1 <= scale['z'] <= 0.5
    assert pos['x'] == 1
    assert pos['y'] == scale['y'] * 0.5
    assert pos['z'] == 3
    assert rot == {'x': 0, 'y': 43, 'z': 0}
    assert not wall['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('occluding_walls')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_occluding_wall_three_part_position_rotation():
    component = SpecificStructuralObjectsComponent({
        'structural_occluding_walls': {
            'num': 1,
            'type': 'hole',
            'position': {
                'x': 1,
                'y': 0,
                'z': 3
            },
            'rotation_y': 43,
            'scale': {
                'x': 1,
                'y': 1,
                'z': 0.1
            }
        }
    })

    pre_occ = component.structural_occluding_walls
    assert isinstance(pre_occ, StructuralOccludingWallConfig)
    assert pre_occ.num == 1
    assert pre_occ.type == 'hole'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 4
    left = objs[1]
    right = objs[2]
    top = objs[3]
    assert left['id'].startswith("l_col-hole-")
    assert left['type'] == 'cube'
    assert left['structure']
    assert left['shows']
    show = left['shows'][0]
    scale = show['scale']
    pos = show['position']
    rot = show['rotation']
    assert scale['x'] == 0.3
    assert scale['y'] == 0.5
    assert 0.1 <= scale['z'] <= 0.5
    assert pos['x'] == pytest.approx(0.744, 0.01)
    assert pos['y'] == pytest.approx(.25, 0.01)
    assert pos['z'] == pytest.approx(3.227, 0.01)
    assert rot == {'x': 0, 'y': 43, 'z': 0}
    assert not left['debug']['random_position']

    assert right['id'].startswith("r_col-hole-")
    assert right['type'] == 'cube'
    assert right['structure']
    assert right['shows']
    show = right['shows'][0]
    scale = show['scale']
    pos = show['position']
    rot = show['rotation']
    assert scale['x'] == 0.3
    assert scale['y'] == 0.5
    assert 0.1 <= scale['z'] <= 0.5
    assert pos['x'] == pytest.approx(1.2559, 0.01)
    assert pos['y'] == pytest.approx(.25, 0.01)
    assert pos['z'] == pytest.approx(2.772, 0.01)
    assert rot == {'x': 0, 'y': 43, 'z': 0}
    assert not right['debug']['random_position']

    assert top['id'].startswith("top-hole-")
    assert top['type'] == 'cube'
    assert top['structure']
    assert top['shows']
    show = top['shows'][0]
    scale = show['scale']
    pos = show['position']
    rot = show['rotation']
    assert scale['x'] == 1
    assert scale['y'] == 0.5
    assert 0.1 <= scale['z'] <= 0.5
    assert pos == {'x': 1, 'y': 0.75, 'z': 3}
    assert rot == {'x': 0, 'y': 43, 'z': 0}
    assert not top['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('occluding_walls')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_occluding_wall_three_part_pos_rot_scale():
    component = SpecificStructuralObjectsComponent({
        'structural_occluding_walls': {
            'num': 1,
            'type': 'hole',
            'position': {
                'x': 1,
                'y': 0,
                'z': 3
            },
            'rotation_y': 43,
            'scale': {
                'x': 3,
                'y': 2,
                'z': 0.5
            }
        }
    })

    pre_occ = component.structural_occluding_walls
    assert isinstance(pre_occ, StructuralOccludingWallConfig)
    assert pre_occ.num == 1
    assert pre_occ.type == 'hole'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 4
    left = objs[1]
    right = objs[2]
    top = objs[3]
    assert left['id'].startswith("l_col-hole-")
    assert left['type'] == 'cube'
    assert left['structure']
    assert left['shows']
    show = left['shows'][0]
    scale = show['scale']
    pos = show['position']
    rot = show['rotation']
    # y = 0.8 because it is the max hole size
    assert scale == {'x': 0.3, 'y': 0.8, 'z': 0.5}
    assert pos['x'] == pytest.approx(0.0126725, 0.01)
    assert pos['y'] == pytest.approx(.4, 0.01)
    assert pos['z'] == pytest.approx(3.92, 0.01)
    assert rot == {'x': 0, 'y': 43, 'z': 0}
    assert not left['debug']['random_position']

    assert right['id'].startswith("r_col-hole-")
    assert right['type'] == 'cube'
    assert right['structure']
    assert right['shows']
    show = right['shows'][0]
    scale = show['scale']
    pos = show['position']
    rot = show['rotation']
    assert scale == {'x': 0.3, 'y': 0.8, 'z': 0.5}
    assert pos['x'] == pytest.approx(1.98732, 0.01)
    assert pos['y'] == pytest.approx(.4, 0.01)
    assert pos['z'] == pytest.approx(2.079, 0.01)
    assert rot == {'x': 0, 'y': 43, 'z': 0}
    assert not right['debug']['random_position']

    assert top['id'].startswith("top-hole-")
    assert top['type'] == 'cube'
    assert top['structure']
    assert top['shows']
    show = top['shows'][0]
    scale = show['scale']
    pos = show['position']
    rot = show['rotation']
    assert scale == {'x': 3, 'y': 1.2, 'z': 0.5}
    assert pos == {'x': 1, 'y': 1.4, 'z': 3}
    assert rot == {'x': 0, 'y': 43, 'z': 0}
    assert not top['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('occluding_walls')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_structural_objects_occluding_fail_bad_type():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_occluding_walls': {
                'num': 1,
                'type': 'not_a_type',
                'position': {
                    'x': 1,
                    'y': 0,
                    'z': 3
                },
                'rotation_y': 43,
                'scale': {
                    'x': 3,
                    'y': 2,
                    'z': 0.5
                }
            }
        })


def test_structural_objects_occluding_wall_specific_keyword_location():
    component = SpecificStructuralObjectsComponent({
        'structural_occluding_walls': {
            'num': 1,
            'type': 'occludes',
            'keyword_location': {
                'keyword': 'back'
            },
            'rotation_y': 48
        }
    })

    pre_occ = component.structural_occluding_walls
    assert isinstance(pre_occ, StructuralOccludingWallConfig)
    assert pre_occ.num == 1
    assert pre_occ.type == 'occludes'

    scene = component.update_ile_scene(prior_scene_with_target())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    assert not objs[0]['debug'].get('positionedBy')
    wall = objs[1]
    assert wall['debug'].get('positionedBy')
    assert wall['id'].startswith("occludes-")
    assert wall['type'] == 'cube'
    assert wall['structure']
    assert wall['shows']
    show = wall['shows'][0]
    scale = show['scale']
    pos = show['position']
    assert 0.5 <= scale['x'] <= 2
    assert 0.5 <= scale['y'] <= 2
    assert 0.1 <= scale['z'] <= 0.5
    assert pos['z'] < 0
    assert wall['debug']['random_position']
    # keyword location will override rotation

    assert ObjectRepository.get_instance().has_label('occluding_walls')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_placer_specific():
    component = SpecificStructuralObjectsComponent({
        'placers': [{
            'num': 1,
            'labels': 'test_label',
            'placed_object_position': {
                'x': 3,
                'y': 0,
                'z': 2
            },
            'placed_object_rotation': 27,
            'placed_object_scale': {
                'x': .8,
                'y': 1.1,
                'z': 1.3
            },
            'placed_object_material':
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
            'placed_object_shape': 'ball',
            'activation_step': 5
        }]
    })

    assert isinstance(component.placers, List)
    pre_placer = component.placers[0]
    assert isinstance(pre_placer, StructuralPlacerConfig)
    assert pre_placer.num == 1
    assert pre_placer.placed_object_position == VectorFloatConfig(3, 0, 2)
    assert pre_placer.placed_object_rotation == 27
    assert pre_placer.placed_object_scale == VectorFloatConfig(0.8, 1.1, 1.3)
    assert (pre_placer.placed_object_material ==
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')
    assert pre_placer.placed_object_shape == 'ball'
    assert pre_placer.activation_step == 5

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    obj = objs[0]
    assert obj['debug']['positionedBy'] == 'mechanism'
    assert obj['moveable']
    assert (obj['materials'][0] ==
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')
    show = obj['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos['x'] == 3
    assert pos['z'] == 2
    assert rot['y'] == 27
    assert scale['x'] == 0.8
    assert scale['y'] == 1.1
    assert scale['z'] == 1.3
    move = obj['moves'][0]
    assert move['stepBegin'] == 5

    placer = objs[1]
    assert placer['id'].startswith('placer_')
    assert placer['type'] == 'cylinder'
    assert placer['kinematic']
    assert placer['structure']
    move = placer['moves'][0]
    assert ObjectRepository.get_instance().has_label('placers')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_placer_with_existing_labels():
    component = SpecificStructuralObjectsComponent({
        'placers': [{
            'num': 1,
            'placed_object_labels': TARGET_LABEL,
            'placed_object_position': {
                'x': 3,
                'y': 0,
                'z': 2
            },
            'placed_object_rotation': 27,
            'activation_step': 5
        }]
    })

    assert isinstance(component.placers, List)
    pre_placer = component.placers[0]
    assert isinstance(pre_placer, StructuralPlacerConfig)
    assert pre_placer.num == 1
    assert pre_placer.placed_object_labels == TARGET_LABEL
    assert pre_placer.placed_object_position == VectorFloatConfig(3, 0, 2)
    assert pre_placer.placed_object_rotation == 27
    assert pre_placer.activation_step == 5

    # Prior scene must have target object.
    scene = component.update_ile_scene(prior_scene_with_target())

    assert len(scene['objects']) == 2
    target = scene['objects'][0]
    placer = scene['objects'][1]

    assert target['type'] == 'soccer_ball'
    assert target['debug']['positionedBy'] == 'mechanism'
    assert target['kinematic']
    assert target['togglePhysics'][0]['stepBegin'] == 21
    assert len(target['shows']) == 1
    assert target['shows'][0]['position'] == pytest.approx(
        {'x': 3, 'y': 2.885, 'z': 2}
    )
    assert target['shows'][0]['rotation'] == {'x': 0, 'y': 27, 'z': 0}
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert len(target['moves']) == 1
    assert target['moves'][0]['stepBegin'] == 5
    assert target['moves'][0]['stepEnd'] == 15
    assert target['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}

    assert placer['id'].startswith('placer_')
    assert placer['type'] == 'cylinder'
    assert placer['kinematic']
    assert placer['structure']
    assert placer['changeMaterials'][0]['stepBegin'] == 21
    assert len(placer['shows']) == 1
    assert placer['shows'][0]['position'] == pytest.approx(
        {'x': 3, 'y': 4.495, 'z': 2}
    )
    assert placer['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placer['shows'][0]['scale'] == {'x': 0.05, 'y': 1.5, 'z': 0.05}
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 5
    assert placer['moves'][0]['stepEnd'] == 15
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 26
    assert placer['moves'][1]['stepEnd'] == 36
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}
    assert ObjectRepository.get_instance().has_label('placers')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_placer_with_missing_targets():
    component = SpecificStructuralObjectsComponent({
        'placers': [{
            'num': 1,
            'placed_object_labels': TARGET_LABEL,
            'placed_object_position': {
                'x': 3,
                'y': 0,
                'z': 2
            },
            'placed_object_rotation': 27,
            'activation_step': 5
        }]
    })

    # Error because object with "target" label must exist in scene.
    with pytest.raises(ILEException):
        # Prior scene must NOT have target object.
        component.update_ile_scene(prior_scene())


def test_placer_with_new_labels():
    component = SpecificStructuralObjectsComponent({
        'placers': [{
            'num': 1,
            'placed_object_labels': 'my_projectile',
            'placed_object_position': {
                'x': 3,
                'y': 0,
                'z': 2
            },
            'placed_object_rotation': 27,
            'placed_object_scale': 2,
            'placed_object_shape': 'soccer_ball',
            'activation_step': 5
        }]
    })

    assert isinstance(component.placers, List)
    pre_placer = component.placers[0]
    assert isinstance(pre_placer, StructuralPlacerConfig)
    assert pre_placer.num == 1
    assert pre_placer.placed_object_labels == 'my_projectile'
    assert pre_placer.placed_object_position == VectorFloatConfig(3, 0, 2)
    assert pre_placer.placed_object_rotation == 27
    assert pre_placer.placed_object_scale == 2
    assert pre_placer.placed_object_shape == 'soccer_ball'
    assert pre_placer.activation_step == 5

    scene = prior_scene_with_target()
    original_position = {
        'x': scene['objects'][0]['shows'][0]['position']['x'],
        'y': scene['objects'][0]['shows'][0]['position']['y'],
        'z': scene['objects'][0]['shows'][0]['position']['z']
    }
    original_rotation = {
        'x': scene['objects'][0]['shows'][0]['rotation']['x'],
        'y': scene['objects'][0]['shows'][0]['rotation']['y'],
        'z': scene['objects'][0]['shows'][0]['rotation']['z']
    }
    scene = component.update_ile_scene(scene)

    assert len(scene['objects']) == 3
    target = scene['objects'][0]
    placed_object = scene['objects'][1]
    placer = scene['objects'][2]

    assert target['type'] == 'soccer_ball'
    assert 'positionedBy' not in target['debug']
    assert 'kinematic' not in target
    assert 'togglePhysics' not in target
    assert target['shows'][0]['position'] == original_position
    assert target['shows'][0]['rotation'] == original_rotation
    assert target['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert 'moves' not in target

    assert placed_object['type'] == 'soccer_ball'
    assert placed_object['debug']['positionedBy'] == 'mechanism'
    assert placed_object['kinematic']
    assert placed_object['togglePhysics'][0]['stepBegin'] == 20
    assert len(placed_object['shows']) == 1
    assert placed_object['shows'][0]['position'] == pytest.approx(
        {'x': 3, 'y': 2.775, 'z': 2}
    )
    assert placed_object['shows'][0]['rotation'] == {'x': 0, 'y': 27, 'z': 0}
    assert placed_object['shows'][0]['scale'] == {'x': 2, 'y': 2, 'z': 2}
    assert len(placed_object['moves']) == 1
    assert placed_object['moves'][0]['stepBegin'] == 5
    assert placed_object['moves'][0]['stepEnd'] == 14
    assert placed_object['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}

    assert placer['id'].startswith('placer_')
    assert placer['type'] == 'cylinder'
    assert placer['kinematic']
    assert placer['structure']
    assert placer['changeMaterials'][0]['stepBegin'] == 20
    assert len(placer['shows']) == 1
    assert placer['shows'][0]['position'] == pytest.approx(
        {'x': 3, 'y': 4.935, 'z': 2}
    )
    assert placer['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert placer['shows'][0]['scale'] == {'x': 0.18, 'y': 1.5, 'z': 0.18}
    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 5
    assert placer['moves'][0]['stepEnd'] == 14
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 25
    assert placer['moves'][1]['stepEnd'] == 34
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}
    assert ObjectRepository.get_instance().has_label('placers')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_placer_with_used_target():
    component = SpecificStructuralObjectsComponent({
        'placers': [{
            # Configure multiple placer mechanisms with the "target" label.
            'num': 2,
            'placed_object_labels': TARGET_LABEL,
            'placed_object_position': {
                'x': 3,
                'y': 0,
                'z': 2
            },
            'placed_object_rotation': 27,
            'activation_step': 5
        }]
    })

    # Error because object with "target" label must not already be used by
    # another mechanism.
    with pytest.raises(ILEException):
        # Prior scene must have target object.
        component.update_ile_scene(prior_scene_with_target())


def test_placer_test_overlap_fail():
    component = SpecificStructuralObjectsComponent({
        'placers': [{
            'num': 2,
            'placed_object_position': {
                'x': 3,
                'y': 0,
                'z': 2
            },
            'placed_object_rotation': 27,
            'placed_object_scale': {
                'x': .8,
                'y': 1.1,
                'z': 1.3
            },
            'placed_object_material':
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
            'placed_object_shape': 'ball',
            'activation_step': 5
        }]
    })
    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene())


def test_door_random_values():
    component = SpecificStructuralObjectsComponent({
        'doors': [{
            'num': 1
        }]
    })

    assert isinstance(component.doors, List)
    pre_door = component.doors[0]
    assert isinstance(pre_door, StructuralDoorConfig)
    assert pre_door.num == 1
    assert pre_door.position is None
    assert pre_door.rotation_y is None
    assert pre_door.scale is None
    assert pre_door.material is None

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)

    objs = scene['objects']
    for obj in objs:
        assert obj['id'].startswith('door')
        assert obj['type'] == 'door_4'
        assert obj['kinematic']
        assert obj['openable']
        assert obj['structure']
        assert obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('doors')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_door_fully_defined():
    component = SpecificStructuralObjectsComponent({
        'doors': [{
            'num': 1,
            'labels': 'test_label',
            'material': 'AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
            'position': {
                'x': 2,
                'y': 0,
                'z': 3
            },
            'rotation_y': 46,
            'scale': {
                'x': 1.2,
                'y': 0.8,
                'z': .94
            },

        }]
    })

    assert isinstance(component.doors, List)
    pre_door = component.doors[0]
    assert isinstance(pre_door, StructuralDoorConfig)
    assert pre_door.num == 1
    assert pre_door.position == VectorFloatConfig(2, 0, 3)
    assert pre_door.rotation_y == 46
    assert pre_door.scale == VectorFloatConfig(1.2, .8, .94)
    assert (pre_door.material ==
            'AI2-THOR/Materials/Metals/BrushedAluminum_Blue')

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)

    objs = scene['objects']
    assert isinstance(objs, List)
    obj = objs[0]
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj['openable']
    assert obj['structure']
    show = obj['shows'][0]
    pos = show['position']
    scale = show['scale']
    assert pos['x'] == 2
    assert pos['y'] == 0
    assert pos['z'] == 3
    assert scale['x'] == 1.2
    assert scale['y'] == .8
    assert scale['z'] == .94
    assert show['rotation']['y'] == 46
    assert not obj['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('doors')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_door_fail_config():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'doors': [{
                'num': -2,
                'material': 'AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
                'position': {
                    'x': 2,
                    'y': 0,
                    'z': 3
                },
                'rotation_y': 46,
                'scale': {
                    'x': 1.2,
                    'y': 0.8,
                    'z': .94
                },

            }]
        })


def test_door_fail_config2():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'doors': [{
                'num': 1,
                'material': 'AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
                'position': {
                    'x': 2,
                    'y': 0,
                    'z': 3
                },
                'rotation_y': 'right_angle',
                'scale': {
                    'x': 1.2,
                    'y': 0.8,
                    'z': .94
                },

            }]
        })


def test_door_fail_common_location():
    component = SpecificStructuralObjectsComponent({
        'doors': [{
            'num': 2,
            'material': 'AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
            'position': {
                'x': 2,
                'y': 0,
                'z': 3
            },
            'rotation_y': {
                'min': 40,
                'max': 279
            },
            'scale': {
                'x': 1.2,
                'y': 0.8,
                'z': .94
            },

        }]
    })
    with pytest.raises(ILEException):
        component.update_ile_scene(prior_scene())


def test_placer_test_config_fail():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'placers': [{
                'num': 2,
                'placed_object_position': {
                    'x': 3,
                    'y': 0,
                    'z': 2
                },
                'placed_object_rotation': 27,
                'placed_object_scale': {
                    'x': .8,
                    'y': 1.1,
                    'z': 1.3
                },
                'placed_object_material':
                'AI2-THOR/Materials/Metals/BrushedAluminum_Blue',
                'placed_object_shape': 'ball',
                'activation_step': -5
            }]
        })


def test_door_fail_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'doors': [{
                'num': 2,
                'material': 'AI2-THOR/Materials/Fabrics/Carpet2',
                'position': {
                    'x': 2,
                    'y': 0,
                    'z': 3
                },
                'rotation_y': {
                    'min': 40,
                    'max': 279
                },
                'scale': {
                    'x': 1.2,
                    'y': 0.8,
                    'z': .94
                },

            }]
        })


def test_door_fail_material_group():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'doors': [{
                'num': 2,
                'material': 'FABRIC_MATERIALS',
                'position': {
                    'x': 2,
                    'y': 0,
                    'z': 3
                },
                'rotation_y': {
                    'min': 40,
                    'max': 279
                },
                'scale': {
                    'x': 1.2,
                    'y': 0.8,
                    'z': .94
                },

            }]
        })


def test_door_material_group():
    component = SpecificStructuralObjectsComponent({
        'doors': [{
            'num': 2,
            'material': 'WOOD_MATERIALS',

        }]
    })
    wood_mats = [mat[0] for mat in materials.WOOD_MATERIALS]
    assert isinstance(component.doors, List)
    pre_door = component.doors[0]
    assert isinstance(pre_door, StructuralDoorConfig)
    assert pre_door.material == 'WOOD_MATERIALS'
    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)

    objs = scene['objects']
    assert isinstance(objs, List)
    obj = objs[0]
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj['openable']
    assert obj['structure']
    assert obj['materials'][0] in wood_mats

    obj = objs[1]
    assert obj['id'].startswith('door')
    assert obj['type'] == 'door_4'
    assert obj['kinematic']
    assert obj['openable']
    assert obj['structure']
    assert obj['materials'][0] in wood_mats
    assert ObjectRepository.get_instance().has_label('doors')
    assert not ObjectRepository.get_instance().has_label('test_label')


def test_delayed():
    label = "after_object"
    scene = prior_scene()
    data = {
        "room_dimensions": {"x": 10, "y": 5, "z": 10},
        "structural_occluding_walls": [{
            "num": 1,
            "keyword_location": {
                "keyword": "adjacent",
                "relative_object_label": label
            },
            'labels': 'test_label',
            "type": "occludes"
        }],
        "specific_interactable_objects": {
            "num": 1,
            "labels": label
        }
    }

    component = SpecificStructuralObjectsComponent(data)

    scene = component.update_ile_scene(scene)
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 0
    assert component.get_num_delayed_actions() == 1

    object_comp = SpecificInteractableObjectsComponent(data)
    scene = object_comp.update_ile_scene(scene)
    assert len(objects) == 1

    scene = component.run_delayed_actions(scene)
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 2
    component.get_num_delayed_actions() == 0
    assert objects[0]['debug']['random_position']
    assert objects[1]['debug']['random_position']
    assert ObjectRepository.get_instance().has_label('occluding_walls')
    assert ObjectRepository.get_instance().has_label('test_label')


def test_structural_floor_materials_fail_restricted_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'floor_material_override': [{
                'num': 1,
                'material': materials.SOFA_1_MATERIALS[0].material
            }]
        })


def test_structural_floor_materials_successful_lava_material():
    component = SpecificStructuralObjectsComponent({
        'floor_material_override': [{
            'num': 1,
            'material': materials.LAVA_MATERIALS[0].material
        }]
    })
    assert (
        component.floor_material_override[0].material ==
        materials.LAVA_MATERIALS[0].material
    )


def test_structural_interior_wall_fail_restricted_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_walls': [{
                'num': 1,
                'material': materials.SOFA_1_MATERIALS[0].material
            }]
        })


def test_structural_interior_wall_fail_lava_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_walls': [{
                'num': 1,
                'material': materials.LAVA_MATERIALS[0].material
            }]
        })


def test_structural_l_occluder_fail_restricted_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_l_occluders': [{
                'num': 1,
                'material': materials.SOFA_1_MATERIALS[0].material
            }]
        })


def test_structural_l_occluder_fail_lava_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_l_occluders': [{
                'num': 1,
                'material': materials.LAVA_MATERIALS[0].material
            }]
        })


def test_structural_moving_occluder_pole_fail_restricted_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_moving_occluders': [{
                'num': 1,
                'pole_material': materials.SOFA_1_MATERIALS[0].material
            }]
        })


def test_structural_moving_occluder_pole_fail_lava_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_moving_occluders': [{
                'num': 1,
                'pole_material': materials.LAVA_MATERIALS[0].material
            }]
        })


def test_structural_moving_occluder_wall_fail_restricted_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_moving_occluders': [{
                'num': 1,
                'wall_material': materials.SOFA_1_MATERIALS[0].material
            }]
        })


def test_structural_moving_occluder_wall_fail_lava_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_moving_occluders': [{
                'num': 1,
                'wall_material': materials.LAVA_MATERIALS[0].material
            }]
        })


def test_structural_occluding_wall_fail_restricted_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_occluding_walls': [{
                'num': 1,
                'material': materials.SOFA_1_MATERIALS[0].material
            }]
        })


def test_structural_occluding_wall_fail_lava_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_occluding_walls': [{
                'num': 1,
                'material': materials.LAVA_MATERIALS[0].material
            }]
        })


def test_structural_platform_fail_restricted_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_platforms': [{
                'num': 1,
                'material': materials.SOFA_1_MATERIALS[0].material
            }]
        })


def test_structural_platform_fail_lava_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_platforms': [{
                'num': 1,
                'material': materials.LAVA_MATERIALS[0].material
            }]
        })


def test_structural_ramp_fail_restricted_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_ramps': [{
                'num': 1,
                'material': materials.SOFA_1_MATERIALS[0].material
            }]
        })


def test_structural_ramp_fail_lava_material():
    with pytest.raises(ILEException):
        SpecificStructuralObjectsComponent({
            'structural_ramps': [{
                'num': 1,
                'material': materials.LAVA_MATERIALS[0].material
            }]
        })
