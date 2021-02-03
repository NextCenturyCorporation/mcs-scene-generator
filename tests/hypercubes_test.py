from hypercubes import Hypercube, update_scene_objects


class MockHypercube(Hypercube):
    def __init__(self):
        super().__init__('mock', {}, {
            'category': 'mock',
            'domainsInfo': {},
            'sceneInfo': {'all': []}
        })

    def _create_scenes(self, body_template, goal_template):
        return [{**body_template, **{'goal': goal_template}}]

    def _get_training_scenes(self):
        return self._scenes


def create_tags_test_object_1():
    return {
        'id': 'test_sphere',
        'type': 'sphere',
        'dimensions': {
            'x': 0.1,
            'y': 0.1,
            'z': 0.1
        },
        'info': ['tiny', 'light', 'blue', 'plastic', 'ball'],
        'goalString': 'tiny light blue plastic ball',
        'mass': 0.5,
        'materials': ['test_material'],
        'materialCategory': ['plastic'],
        'salientMaterials': ['plastic'],
        'moveable': True,
        'untrainedCategory': False,
        'untrainedColor': False,
        'untrainedCombination': False,
        'untrainedShape': False,
        'untrainedSize': False,
        'pickupable': True,
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
        'dimensions': {
            'x': 0.5,
            'y': 0.5,
            'z': 0.5
        },
        'info': ['medium', 'light', 'yellow', 'plastic', 'cube'],
        'goalString': 'medium light yellow plastic cube',
        'mass': 2.5,
        'materials': ['test_material'],
        'materialCategory': ['plastic'],
        'salientMaterials': ['plastic'],
        'moveable': True,
        'untrainedCategory': False,
        'untrainedColor': False,
        'untrainedCombination': False,
        'untrainedShape': False,
        'untrainedSize': False,
        'pickupable': True,
        'shows': [{
            'stepBegin': 0,
            'position': {
                'x': 1,
                'y': 2,
                'z': 3
            }
        }]
    }


def test_Hypercube_create_scenes_on_init():
    hypercube = MockHypercube()
    assert len(hypercube._scenes) == 1


def test_Hypercube_init_scenes():
    hypercube = MockHypercube()
    scene = hypercube.get_scenes()[0]
    assert 'category' in scene['goal']
    assert 'domainsInfo' in scene['goal']
    assert 'objectsInfo' in scene['goal']
    assert 'sceneInfo' in scene['goal']


def test_Hypercube_tags():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_multiple_target():
    hypercube = MockHypercube()
    target_1 = create_tags_test_object_1()
    target_2 = create_tags_test_object_2()
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target_1, target_2]}
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count']['target'] == 2


def test_Hypercube_tags_with_obstacle():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['obstacle']
    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['obstacle']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['obstacle']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['obstacle']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['obstacle']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['obstacle']
    assert scene['goal']['sceneInfo']['uncontained']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count']['obstacle'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_multiple_target_multiple_obstacle():
    hypercube = MockHypercube()
    target_1 = create_tags_test_object_1()
    target_2 = create_tags_test_object_1()
    obstacle_1 = create_tags_test_object_2()
    obstacle_2 = create_tags_test_object_2()
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {
            'target': [target_1, target_2],
            'obstacle': [obstacle_1, obstacle_2]
        }
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['obstacle']
    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['obstacle']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['obstacle']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['obstacle']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['obstacle']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['obstacle']
    assert scene['goal']['sceneInfo']['uncontained']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 4
    assert scene['goal']['sceneInfo']['count']['obstacle'] == 2
    assert scene['goal']['sceneInfo']['count']['target'] == 2


def test_Hypercube_tags_with_intuitive_physics_occluder():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    occluder_wall = {'info': ['white']}
    occluder_pole = {'info': ['brown']}
    occluder_tag = 'intuitive_physics_occluder'
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {
            'target': [target],
            'intuitive physics occluder': [occluder_wall, occluder_pole]
        }
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'intuitive physics occluder',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'white', 'brown',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo'][occluder_tag]) == {
        'white', 'brown'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained'][occluder_tag]
    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['untrainedCategory'][occluder_tag]
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor'][occluder_tag]
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination'][occluder_tag]
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape'][occluder_tag]
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize'][occluder_tag]
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count'][occluder_tag] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1
    assert scene['goal']['sceneInfo']['present'][occluder_tag]
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['uncontained']['target']


def test_Hypercube_tags_target_enclosed():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'contained'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'contained'
    }

    assert not scene['goal']['sceneInfo']['uncontained']['target']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['contained']['target']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_target_untrained_category():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['untrainedCategory'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'untrained category', 'trained color', 'trained shape', 'trained size',
        'uncontained', 'trained combination'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'untrained category', 'trained color', 'trained shape', 'trained size',
        'uncontained', 'trained combination'
    }

    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['trainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedCategory']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_target_untrained_color():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['untrainedColor'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'untrained color', 'trained shape', 'trained size',
        'uncontained', 'trained combination'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'untrained color', 'trained shape', 'trained size',
        'uncontained', 'trained combination'
    }

    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['trainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedColor']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_target_untrained_combination():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['untrainedCombination'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'untrained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'untrained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['trainedCombination']['target']
    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedCombination']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_target_untrained_shape():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['untrainedShape'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'untrained shape',
        'trained size', 'uncontained', 'trained combination'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'untrained shape',
        'trained size', 'uncontained', 'trained combination'
    }

    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['trainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedShape']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_target_untrained_size():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['untrainedSize'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'untrained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'untrained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['trainedSize']['target']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']

    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_target_enclosed_untrained_everything():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    target['untrainedCategory'] = True
    target['untrainedColor'] = True
    target['untrainedShape'] = True
    target['untrainedSize'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(scene, {'target': [target]})

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }

    assert not scene['goal']['sceneInfo']['trainedCategory']['target']
    assert not scene['goal']['sceneInfo']['trainedColor']['target']
    assert not scene['goal']['sceneInfo']['trainedShape']['target']
    assert not scene['goal']['sceneInfo']['trainedSize']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['uncontained']['target']

    assert scene['goal']['sceneInfo']['contained']['target']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert scene['goal']['sceneInfo']['untrainedColor']['target']
    assert scene['goal']['sceneInfo']['untrainedShape']['target']
    assert scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_obstacle_enclosed():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['locationParent'] = 'parent'
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'contained', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'contained'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['uncontained']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['contained']['obstacle']
    assert scene['goal']['sceneInfo']['present']['obstacle']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['obstacle']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['obstacle']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['obstacle']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count']['obstacle'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_obstacle_untrained_category():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['untrainedCategory'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained', 'untrained category'
    }
    assert set(scene['goal']['objectsInfo']['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'untrained category', 'trained color', 'trained shape',
        'trained size', 'uncontained', 'trained combination'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['obstacle']
    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['trainedCategory']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['obstacle']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['obstacle']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['obstacle']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['obstacle']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['obstacle']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedCategory']['obstacle']

    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count']['obstacle'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_obstacle_untrained_color():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['untrainedColor'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained', 'untrained color',
    }
    assert set(scene['goal']['objectsInfo']['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'untrained color', 'trained shape', 'trained size',
        'uncontained', 'trained combination'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['obstacle']
    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['trainedColor']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['obstacle']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['obstacle']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['obstacle']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['obstacle']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedColor']['obstacle']

    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count']['obstacle'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_obstacle_untrained_combination():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['untrainedCombination'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained', 'untrained combination'
    }
    assert set(scene['goal']['objectsInfo']['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'untrained combination',
        'trained shape', 'trained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['obstacle']
    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['trainedCombination']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['obstacle']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['obstacle']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['obstacle']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['obstacle']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['obstacle']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedCombination']['obstacle']

    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count']['obstacle'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_obstacle_untrained_shape():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['untrainedShape'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained',
        'untrained shape'
    }
    assert set(scene['goal']['objectsInfo']['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'untrained shape',
        'trained size', 'uncontained', 'trained combination'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['obstacle']
    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['trainedShape']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['obstacle']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCategory']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['obstacle']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['obstacle']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedShape']['obstacle']

    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count']['obstacle'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_obstacle_untrained_size():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['untrainedSize'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained', 'untrained size'
    }
    assert set(scene['goal']['objectsInfo']['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'untrained size', 'uncontained'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['obstacle']
    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['trainedSize']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['present']['obstacle']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['obstacle']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['obstacle']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['obstacle']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedSize']['obstacle']

    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count']['obstacle'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_obstacle_enclosed_untrained_everything():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    obstacle = create_tags_test_object_2()
    obstacle['locationParent'] = 'parent'
    obstacle['untrainedCategory'] = True
    obstacle['untrainedColor'] = True
    obstacle['untrainedShape'] = True
    obstacle['untrainedSize'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained', 'contained',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size'
    }
    assert set(scene['goal']['objectsInfo']['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'trained category', 'trained color', 'trained combination',
        'trained shape', 'trained size', 'uncontained'
    }

    assert not scene['goal']['sceneInfo']['contained']['target']
    assert not scene['goal']['sceneInfo']['trainedCategory']['obstacle']
    assert not scene['goal']['sceneInfo']['trainedColor']['obstacle']
    assert not scene['goal']['sceneInfo']['trainedShape']['obstacle']
    assert not scene['goal']['sceneInfo']['trainedSize']['obstacle']
    assert not scene['goal']['sceneInfo']['uncontained']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert not scene['goal']['sceneInfo']['untrainedColor']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']
    assert not scene['goal']['sceneInfo']['untrainedShape']['target']
    assert not scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['contained']['obstacle']
    assert scene['goal']['sceneInfo']['present']['obstacle']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCategory']['target']
    assert scene['goal']['sceneInfo']['trainedColor']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['trainedShape']['target']
    assert scene['goal']['sceneInfo']['trainedSize']['target']
    assert scene['goal']['sceneInfo']['uncontained']['target']
    assert scene['goal']['sceneInfo']['untrainedCategory']['obstacle']
    assert scene['goal']['sceneInfo']['untrainedColor']['obstacle']
    assert scene['goal']['sceneInfo']['untrainedShape']['obstacle']
    assert scene['goal']['sceneInfo']['untrainedSize']['obstacle']

    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count']['obstacle'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1


def test_Hypercube_tags_target_obstacle_enclosed_untrained_everything():
    hypercube = MockHypercube()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    target['untrainedCategory'] = True
    target['untrainedColor'] = True
    target['untrainedShape'] = True
    target['untrainedSize'] = True
    obstacle = create_tags_test_object_2()
    obstacle['locationParent'] = 'parent'
    obstacle['untrainedCategory'] = True
    obstacle['untrainedColor'] = True
    obstacle['untrainedShape'] = True
    obstacle['untrainedSize'] = True
    scene = hypercube.get_scenes()[0]
    print(f'{scene}')
    scene = update_scene_objects(
        scene,
        {'target': [target], 'obstacle': [obstacle]}
    )

    assert set(scene['goal']['objectsInfo']['all']) == {
        'target', 'obstacle',
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }
    assert set(scene['goal']['objectsInfo']['obstacle']) == {
        'medium', 'light', 'yellow', 'plastic', 'cube',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }
    assert set(scene['goal']['objectsInfo']['target']) == {
        'tiny', 'light', 'blue', 'plastic', 'ball',
        'untrained category', 'untrained color', 'untrained shape',
        'untrained size', 'contained', 'trained combination'
    }

    assert not scene['goal']['sceneInfo']['trainedCategory']['obstacle']
    assert not scene['goal']['sceneInfo']['trainedCategory']['target']
    assert not scene['goal']['sceneInfo']['trainedColor']['obstacle']
    assert not scene['goal']['sceneInfo']['trainedColor']['target']
    assert not scene['goal']['sceneInfo']['trainedShape']['obstacle']
    assert not scene['goal']['sceneInfo']['trainedShape']['target']
    assert not scene['goal']['sceneInfo']['trainedSize']['obstacle']
    assert not scene['goal']['sceneInfo']['trainedSize']['target']
    assert not scene['goal']['sceneInfo']['uncontained']['obstacle']
    assert not scene['goal']['sceneInfo']['uncontained']['target']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['obstacle']
    assert not scene['goal']['sceneInfo']['untrainedCombination']['target']

    assert scene['goal']['sceneInfo']['contained']['obstacle']
    assert scene['goal']['sceneInfo']['contained']['target']
    assert scene['goal']['sceneInfo']['present']['obstacle']
    assert scene['goal']['sceneInfo']['present']['target']
    assert scene['goal']['sceneInfo']['trainedCombination']['obstacle']
    assert scene['goal']['sceneInfo']['trainedCombination']['target']
    assert scene['goal']['sceneInfo']['untrainedCategory']['obstacle']
    assert scene['goal']['sceneInfo']['untrainedCategory']['target']
    assert scene['goal']['sceneInfo']['untrainedColor']['obstacle']
    assert scene['goal']['sceneInfo']['untrainedColor']['target']
    assert scene['goal']['sceneInfo']['untrainedShape']['obstacle']
    assert scene['goal']['sceneInfo']['untrainedShape']['target']
    assert scene['goal']['sceneInfo']['untrainedSize']['obstacle']
    assert scene['goal']['sceneInfo']['untrainedSize']['target']

    assert scene['goal']['sceneInfo']['count']['all'] == 2
    assert scene['goal']['sceneInfo']['count']['obstacle'] == 1
    assert scene['goal']['sceneInfo']['count']['target'] == 1
