import copy

from generator import Scene, tags
from hypercube import Hypercube
from hypercube.hypercubes import update_floor_and_walls, update_scene_objects


class MockHypercube(Hypercube):
    def __init__(self):
        super().__init__('mock', Scene(), 'mock')

    def _create_scenes(self, starter_scene, goal_template):
        scene = copy.deepcopy(starter_scene)
        scene.goal = copy.deepcopy(goal_template)
        return [scene]

    def _get_slices(self):
        return []

    def _get_training_scenes(self):
        return self._scenes


def create_tags_test_object_1():
    return {
        'id': 'test_sphere',
        'type': 'sphere',
        'mass': 0.5,
        'materials': ['test_material'],
        'moveable': True,
        'pickupable': True,
        'salientMaterials': ['plastic'],
        'debug': {
            'dimensions': {
                'x': 0.1,
                'y': 0.1,
                'z': 0.1
            },
            'info': ['tiny', 'light', 'blue', 'plastic', 'ball'],
            'goalString': 'tiny light blue plastic ball',
            'materialCategory': ['plastic'],
            'untrainedCategory': False,
            'untrainedColor': False,
            'untrainedCombination': False,
            'untrainedShape': False,
            'untrainedSize': False
        },
        'shows': [{
            'stepBegin': 0,
            'position': {
                'x': 0,
                'y': 0,
                'z': 0
            }
        }]
    }


def create_tags_test_object_2():
    return {
        'id': 'test_cube',
        'type': 'cube',
        'mass': 2.5,
        'materials': ['test_material'],
        'moveable': True,
        'pickupable': True,
        'salientMaterials': ['plastic'],
        'debug': {
            'dimensions': {
                'x': 0.5,
                'y': 0.5,
                'z': 0.5
            },
            'info': ['medium', 'light', 'yellow', 'plastic', 'cube'],
            'goalString': 'medium light yellow plastic cube',
            'materialCategory': ['plastic'],
            'untrainedCategory': False,
            'untrainedColor': False,
            'untrainedCombination': False,
            'untrainedShape': False,
            'untrainedSize': False
        },
        'shows': [{
            'stepBegin': 0,
            'position': {
                'x': 1,
                'y': 2,
                'z': 3
            }
        }]
    }


def test_Hypercube_does_not_generate_scenes_on_init():
    hypercube = MockHypercube()
    assert len(hypercube._scenes) == 0


def test_Hypercube_generate_scenes():
    hypercube = MockHypercube()
    scenes = hypercube.generate_scenes()
    assert len(scenes) == 1
    scene = scenes[0]
    assert scene.goal.category
    assert scene.goal.domains_info
    assert scene.goal.objects_info
    assert scene.goal.scene_info


def test_Hypercube_tags():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene.goal.objects_info['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['target']

    assert scene.goal.scene_info['count']['all'] == 1
    assert scene.goal.scene_info['count']['target'] == 1
    targets = scene.get_targets()
    if (len(targets) >= 1):
        assert scene.goal.scene_info[tags.SCENE.DISTANCE] is not None


def test_Hypercube_tags_multiple_target():
    hypercube = MockHypercube()
    target_1 = create_tags_test_object_1()
    target_2 = create_tags_test_object_2()
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target_1, target_2]}
    )

    assert set(scene.goal.objects_info['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['target']

    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count']['target'] == 2

    targets = scene.get_targets()
    if (len(targets) >= 1):
        assert scene.goal.scene_info[tags.SCENE.DISTANCE] is not None


def test_Hypercube_tags_with_obstacle():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene.goal.objects_info['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['obstacle']
    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['untrainedCategory']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['obstacle']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['obstacle']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['obstacle']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['obstacle']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['obstacle']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['obstacle']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['obstacle']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['obstacle']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['obstacle']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['obstacle']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['obstacle']
    assert scene.goal.scene_info['uncontained']['target']

    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count']['obstacle'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_multiple_target_multiple_obstacle():
    hypercube = MockHypercube()
    target_1 = create_tags_test_object_1()
    target_2 = create_tags_test_object_1()
    obstacle_1 = create_tags_test_object_2()
    obstacle_2 = create_tags_test_object_2()
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {
            'target': [target_1, target_2],
            'obstacle': [obstacle_1, obstacle_2]
        }
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene.goal.objects_info['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['obstacle']
    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['untrainedCategory']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['obstacle']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['obstacle']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['obstacle']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['obstacle']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['obstacle']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['obstacle']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['obstacle']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['obstacle']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['obstacle']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['obstacle']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['obstacle']
    assert scene.goal.scene_info['uncontained']['target']

    assert scene.goal.scene_info['count']['all'] == 4
    assert scene.goal.scene_info['count']['obstacle'] == 2
    assert scene.goal.scene_info['count']['target'] == 2


def test_Hypercube_tags_with_intuitive_physics_occluder():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    occluder_wall = {'debug': {'info': ['white']}}
    occluder_pole = {'debug': {'info': ['brown']}}
    occluder_tag = 'intuitive_physics_occluder'
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {
            'target': [target],
            'intuitive physics occluder': [occluder_wall, occluder_pole]
        }
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'intuitive physics occluder',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'white', 'brown',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene.goal.objects_info[occluder_tag]) == {
        'white', 'brown'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained'][occluder_tag]
    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['untrainedCategory'][occluder_tag]
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor'][occluder_tag]
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination'][occluder_tag]
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape'][occluder_tag]
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize'][occluder_tag]
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count'][occluder_tag] == 1
    assert scene.goal.scene_info['count']['target'] == 1
    assert scene.goal.scene_info['present'][occluder_tag]
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['uncontained']['target']


def test_Hypercube_tags_target_enclosed():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene.goal.objects_info['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'contained'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'contained'
    }

    assert not scene.goal.scene_info['uncontained']['target']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['contained']['target']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['target']

    assert scene.goal.scene_info['count']['all'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_target_untrained_category():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['debug']['untrainedCategory'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene.goal.objects_info['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'untrained category', 'trained color', 'trained shape', 'trained size',
        'uncontained', 'trained combination'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'untrained category', 'trained color', 'trained shape', 'trained size',
        'uncontained', 'trained combination'
    }

    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['trainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedCategory']['target']

    assert scene.goal.scene_info['count']['all'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_target_untrained_color():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['debug']['untrainedColor'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene.goal.objects_info['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'untrained color', 'trained shape', 'trained size',
        'uncontained', 'trained combination'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'untrained color', 'trained shape', 'trained size',
        'uncontained', 'trained combination'
    }

    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['trainedColor']['target']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedColor']['target']

    assert scene.goal.scene_info['count']['all'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_target_untrained_combination():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['debug']['untrainedCombination'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene.goal.objects_info['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'untrained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'untrained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['trainedCombination']['target']
    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedCombination']['target']

    assert scene.goal.scene_info['count']['all'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_target_untrained_shape():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['debug']['untrainedShape'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene.goal.objects_info['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'untrained shape',
        'trained size', 'uncontained', 'trained combination'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'untrained shape',
        'trained size', 'uncontained', 'trained combination'
    }

    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['trainedShape']['target']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedShape']['target']

    assert scene.goal.scene_info['count']['all'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_target_untrained_size():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['debug']['untrainedSize'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene.goal.objects_info['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'untrained size', 'uncontained'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'untrained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['trainedSize']['target']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['target']

    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['count']['all'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_target_enclosed_untrained_everything():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    target['debug']['untrainedCategory'] = True
    target['debug']['untrainedColor'] = True
    target['debug']['untrainedShape'] = True
    target['debug']['untrainedSize'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene.goal.objects_info['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }

    assert not scene.goal.scene_info['trainedCategory']['target']
    assert not scene.goal.scene_info['trainedColor']['target']
    assert not scene.goal.scene_info['trainedShape']['target']
    assert not scene.goal.scene_info['trainedSize']['target']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['uncontained']['target']

    assert scene.goal.scene_info['contained']['target']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['untrainedCategory']['target']
    assert scene.goal.scene_info['untrainedColor']['target']
    assert scene.goal.scene_info['untrainedShape']['target']
    assert scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['count']['all'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_obstacle_enclosed():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['locationParent'] = 'parent'
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'contained', 'uncontained'
    }
    assert set(scene.goal.objects_info['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'contained'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['uncontained']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedColor']['obstacle']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['obstacle']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['obstacle']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['obstacle']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['contained']['obstacle']
    assert scene.goal.scene_info['present']['obstacle']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['obstacle']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['obstacle']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['obstacle']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['obstacle']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['obstacle']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['target']

    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count']['obstacle'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_obstacle_untrained_category():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['debug']['untrainedCategory'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained', 'untrained category'
    }
    assert set(scene.goal.objects_info['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'untrained category', 'trained color', 'trained shape',
        'trained size', 'uncontained', 'trained combination'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['obstacle']
    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['trainedCategory']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['obstacle']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['obstacle']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['obstacle']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['obstacle']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['obstacle']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['obstacle']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['obstacle']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['obstacle']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['obstacle']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['obstacle']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedCategory']['obstacle']

    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count']['obstacle'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_obstacle_untrained_color():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['debug']['untrainedColor'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained', 'untrained color',
    }
    assert set(scene.goal.objects_info['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'untrained color', 'trained shape', 'trained size',
        'uncontained', 'trained combination'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['obstacle']
    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['trainedColor']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['obstacle']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['obstacle']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['obstacle']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['obstacle']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['obstacle']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['obstacle']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['obstacle']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['obstacle']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['obstacle']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedColor']['obstacle']

    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count']['obstacle'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_obstacle_untrained_combination():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['debug']['untrainedCombination'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained', 'untrained combination'
    }
    assert set(scene.goal.objects_info['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'untrained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['obstacle']
    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['trainedCombination']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['obstacle']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['obstacle']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['obstacle']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['obstacle']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['obstacle']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['obstacle']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['obstacle']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['obstacle']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['obstacle']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedCombination']['obstacle']

    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count']['obstacle'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_obstacle_untrained_shape():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['debug']['untrainedShape'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained',
        'untrained shape'
    }
    assert set(scene.goal.objects_info['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'untrained shape',
        'trained size', 'uncontained', 'trained combination'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['obstacle']
    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['trainedShape']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['obstacle']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['obstacle']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['obstacle']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['obstacle']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedColor']['obstacle']
    assert scene.goal.scene_info['trainedCategory']['obstacle']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['obstacle']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['obstacle']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['obstacle']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedShape']['obstacle']

    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count']['obstacle'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_obstacle_untrained_size():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['debug']['untrainedSize'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained', 'untrained size'
    }
    assert set(scene.goal.objects_info['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'untrained size', 'uncontained'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['obstacle']
    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['trainedSize']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['obstacle']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['obstacle']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['obstacle']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['present']['obstacle']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['obstacle']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['obstacle']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['obstacle']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['obstacle']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['obstacle']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedSize']['obstacle']

    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count']['obstacle'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_obstacle_enclosed_untrained_everything():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['locationParent'] = 'parent'
    obstacle['debug']['untrainedCategory'] = True
    obstacle['debug']['untrainedColor'] = True
    obstacle['debug']['untrainedShape'] = True
    obstacle['debug']['untrainedSize'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained', 'contained',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size'
    }
    assert set(scene.goal.objects_info['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene.goal.scene_info['contained']['target']
    assert not scene.goal.scene_info['trainedCategory']['obstacle']
    assert not scene.goal.scene_info['trainedColor']['obstacle']
    assert not scene.goal.scene_info['trainedShape']['obstacle']
    assert not scene.goal.scene_info['trainedSize']['obstacle']
    assert not scene.goal.scene_info['uncontained']['obstacle']
    assert not scene.goal.scene_info['untrainedCategory']['target']
    assert not scene.goal.scene_info['untrainedColor']['target']
    assert not scene.goal.scene_info['untrainedCombination']['obstacle']
    assert not scene.goal.scene_info['untrainedCombination']['target']
    assert not scene.goal.scene_info['untrainedShape']['target']
    assert not scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['contained']['obstacle']
    assert scene.goal.scene_info['present']['obstacle']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCategory']['target']
    assert scene.goal.scene_info['trainedColor']['target']
    assert scene.goal.scene_info['trainedCombination']['obstacle']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['trainedShape']['target']
    assert scene.goal.scene_info['trainedSize']['target']
    assert scene.goal.scene_info['uncontained']['target']
    assert scene.goal.scene_info['untrainedCategory']['obstacle']
    assert scene.goal.scene_info['untrainedColor']['obstacle']
    assert scene.goal.scene_info['untrainedShape']['obstacle']
    assert scene.goal.scene_info['untrainedSize']['obstacle']

    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count']['obstacle'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def test_Hypercube_tags_target_obstacle_enclosed_untrained_everything():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    target['debug']['untrainedCategory'] = True
    target['debug']['untrainedColor'] = True
    target['debug']['untrainedShape'] = True
    target['debug']['untrainedSize'] = True
    obstacle = create_tags_test_object_2()
    obstacle['locationParent'] = 'parent'
    obstacle['debug']['untrainedCategory'] = True
    obstacle['debug']['untrainedColor'] = True
    obstacle['debug']['untrainedShape'] = True
    obstacle['debug']['untrainedSize'] = True
    scene = hypercube.generate_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene.goal.objects_info['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }
    assert set(scene.goal.objects_info['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }
    assert set(scene.goal.objects_info['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }

    assert not scene.goal.scene_info['trainedCategory']['obstacle']
    assert not scene.goal.scene_info['trainedCategory']['target']
    assert not scene.goal.scene_info['trainedColor']['obstacle']
    assert not scene.goal.scene_info['trainedColor']['target']
    assert not scene.goal.scene_info['trainedShape']['obstacle']
    assert not scene.goal.scene_info['trainedShape']['target']
    assert not scene.goal.scene_info['trainedSize']['obstacle']
    assert not scene.goal.scene_info['trainedSize']['target']
    assert not scene.goal.scene_info['uncontained']['obstacle']
    assert not scene.goal.scene_info['uncontained']['target']
    assert not scene.goal.scene_info['untrainedCombination']['obstacle']
    assert not scene.goal.scene_info['untrainedCombination']['target']

    assert scene.goal.scene_info['contained']['obstacle']
    assert scene.goal.scene_info['contained']['target']
    assert scene.goal.scene_info['present']['obstacle']
    assert scene.goal.scene_info['present']['target']
    assert scene.goal.scene_info['trainedCombination']['obstacle']
    assert scene.goal.scene_info['trainedCombination']['target']
    assert scene.goal.scene_info['untrainedCategory']['obstacle']
    assert scene.goal.scene_info['untrainedCategory']['target']
    assert scene.goal.scene_info['untrainedColor']['obstacle']
    assert scene.goal.scene_info['untrainedColor']['target']
    assert scene.goal.scene_info['untrainedShape']['obstacle']
    assert scene.goal.scene_info['untrainedShape']['target']
    assert scene.goal.scene_info['untrainedSize']['obstacle']
    assert scene.goal.scene_info['untrainedSize']['target']

    assert scene.goal.scene_info['count']['all'] == 2
    assert scene.goal.scene_info['count']['obstacle'] == 1
    assert scene.goal.scene_info['count']['target'] == 1


def retrieve_object_list_from_data(object_data):
    return [object_data]


def test_update_floor_and_walls():
    template = Scene()

    for color_1 in [
        'black', 'blue', 'brown', 'green', 'grey', 'orange', 'purple',
        'red', 'white', 'yellow'
    ]:
        print(f'COLOR_1 {color_1}')

        # Test with no objects
        starter_scene = copy.deepcopy(template)
        starter_scene.debug['floorColors'] = [color_1]
        starter_scene.floor_material = [color_1]
        starter_scene.debug['wallColors'] = [color_1]
        starter_scene.wall_material = [color_1]
        role_to_object_data_list = {}
        scenes = [copy.deepcopy(starter_scene), copy.deepcopy(starter_scene)]
        update_floor_and_walls(
            starter_scene,
            role_to_object_data_list,
            retrieve_object_list_from_data,
            scenes
        )
        for scene in scenes:
            assert scene.debug['floorColors'] == [color_1]
            assert scene.floor_material == [color_1]
            assert scene.debug['wallColors'] == [color_1]
            assert scene.wall_material == [color_1]

        # Test with one object
        starter_scene = copy.deepcopy(template)
        starter_scene.debug['floorColors'] = [color_1]
        starter_scene.floor_material = [color_1]
        starter_scene.debug['wallColors'] = [color_1]
        starter_scene.wall_material = [color_1]
        role_to_object_data_list = {
            'target': [{'debug': {'color': [color_1]}}]
        }
        scenes = [copy.deepcopy(starter_scene), copy.deepcopy(starter_scene)]
        update_floor_and_walls(
            starter_scene,
            role_to_object_data_list,
            retrieve_object_list_from_data,
            scenes
        )
        for scene in scenes:
            assert scene.debug['floorColors'] != [color_1]
            assert scene.floor_material != [color_1]
            assert scene.debug['wallColors'] != [color_1]
            assert scene.wall_material != [color_1]

        for color_2 in [
            'black', 'blue', 'brown', 'green', 'grey', 'orange', 'purple',
            'red', 'white', 'yellow'
        ]:
            if color_1 == color_2:
                continue

            print(f'COLOR_2 {color_2}')

            # Test with one objects
            starter_scene = copy.deepcopy(template)
            starter_scene.debug['floorColors'] = [color_1]
            starter_scene.floor_material = [color_1]
            starter_scene.debug['wallColors'] = [color_2]
            starter_scene.wall_material = [color_2]
            role_to_object_data_list = {
                'target': [{'debug': {'color': [color_1]}}]
            }
            scenes = [
                copy.deepcopy(starter_scene),
                copy.deepcopy(starter_scene)
            ]
            update_floor_and_walls(
                starter_scene,
                role_to_object_data_list,
                retrieve_object_list_from_data,
                scenes
            )
            for scene in scenes:
                assert scene.debug['floorColors'] != [color_1]
                assert scene.floor_material != [color_1]
                assert scene.debug['wallColors'] == [color_2]
                assert scene.wall_material == [color_2]

            # Test with multiple objects
            starter_scene = copy.deepcopy(template)
            starter_scene.debug['floorColors'] = [color_1]
            starter_scene.floor_material = [color_1]
            starter_scene.debug['wallColors'] = [color_2]
            starter_scene.wall_material = [color_2]
            role_to_object_data_list = {
                'target': [{'debug': {'color': [color_1]}}],
                'non_target': [{'debug': {'color': [color_2]}}]
            }
            scenes = [
                copy.deepcopy(starter_scene),
                copy.deepcopy(starter_scene)
            ]
            update_floor_and_walls(
                starter_scene,
                role_to_object_data_list,
                retrieve_object_list_from_data,
                scenes
            )
            for scene in scenes:
                assert scene.debug['floorColors'] != [color_1]
                assert scene.debug['floorColors'] != [color_2]
                assert scene.floor_material != [color_1]
                assert scene.floor_material != [color_2]
                assert scene.debug['wallColors'] != [color_2]
                assert scene.debug['wallColors'] != [color_1]
                assert scene.wall_material != [color_2]
                assert scene.wall_material != [color_1]
