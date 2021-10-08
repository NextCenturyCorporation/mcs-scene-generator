from typing import List

import pytest

from generator import FULL_TYPE_LIST, geometry, materials, util
from ideal_learning_env import (
    ILEException,
    InteractableObjectConfig,
    MinMaxInt,
    RandomInteractableObjectsComponent,
    SpecificInteractableObjectsComponent,
)
from ideal_learning_env.defs import ILEConfigurationException
from ideal_learning_env.interactable_objects_component import (
    KeywordObjectsConfig,
    RandomKeywordObjectsComponent,
)
from ideal_learning_env.object_services import ObjectRepository


def prior_scene():
    return {'debug': {}, 'goal': {}, 'performerStart':
            {'position':
             {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 0}},
            'roomDimensions': {'x': 10, 'y': 3, 'z': 10}}


def prior_scene_with_target():
    scene = prior_scene()
    target_object = {
        'id': '743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f',
        'type': 'soccer_ball',
        'mass': 1.0,
        'salientMaterials': ['rubber'],
        'debug':
            {'dimensions':
                {'x': 0.22,
                 'y': 0.22,
                 'z': 0.22},
             'info': [
                    'tiny', 'light', 'black', 'white', 'rubber', 'ball',
                    'black white', 'tiny light', 'tiny rubber',
                    'tiny black white', 'tiny ball', 'light rubber',
                    'light black white', 'light ball',
                    'rubber black white', 'rubber ball', 'black white ball',
                    'tiny light black white rubber ball'],
             'positionY': 0.11, 'role': '', 'shape': ['ball'],
             'size': 'tiny', 'untrainedCategory': False,
             'untrainedColor': False, 'untrainedCombination': False,
             'untrainedShape': False, 'untrainedSize': False, 'offset':
             {'x': 0, 'y': 0.11, 'z': 0}, 'materialCategory': [], 'color':
             ['black', 'white'], 'weight': 'light', 'goalString':
             'tiny light black white rubber ball', 'salientMaterials':
             ['rubber'], 'enclosedAreas': []}, 'moveable': True,
        'pickupable': True, 'shows': [
                 {'rotation': {'x': 0, 'y': 45, 'z': 0},
                  'position': {'x': -1.03, 'y': 0.11, 'z': 4.08},
                  'boundingBox': [
                      {'x': -0.8744365081389596, 'y': 0, 'z': 4.08},
                     {'x': -1.03, 'y': 0, 'z': 3.92443650813896},
                     {'x': -1.1855634918610405, 'y': 0, 'z': 4.08},
                     {'x': -1.0299999999999998, 'y': 0,
                          'z': 4.23556349186104}],
                  'stepBegin': 0, 'scale': {'x': 1, 'y': 1, 'z': 1}}],
        'materials': []}

    scene["objects"] = [target_object]
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
    return scene


@pytest.fixture(autouse=True)
def run_before_test():
    ObjectRepository.get_instance().clear()


def test_specific_objects_defaults():
    component = SpecificInteractableObjectsComponent({})
    assert component.specific_interactable_objects is None

    scene = component.update_ile_scene(prior_scene())
    objs = scene['objects']
    assert isinstance(objs, list)


def test_specific_objects_single():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {}
    })
    print(component)
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig)
    sio = component.specific_interactable_objects
    assert sio.material is None
    assert sio.num == 1
    assert sio.shape is None
    assert sio.scale == 1
    assert sio.rotation is None
    assert sio.position is None

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)


def test_specific_objects_array_single():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{}]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 1
    obj = component.specific_interactable_objects[0]
    assert obj.num == 1
    assert obj.material is None
    assert obj.position is None
    assert obj.rotation is None
    assert obj.scale == 1
    assert obj.shape is None

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    assert len(scene['objects']) == 1
    obj = scene['objects'][0]
    assert 'id' in obj
    assert 'mass' in obj
    assert 'type' in obj
    assert obj['type'] in FULL_TYPE_LIST
    assert 'materials' in obj
    assert isinstance(obj['materials'], list)
    if len(obj['materials']) > 0:
        assert obj['materials'][0] in materials.ALL_MATERIAL_STRINGS
    show = obj['shows'][0]
    assert show['scale']['x'] == show['scale']['z'] == 1
    assert 0 <= show['rotation']['y'] < 360
    assert -10 <= show['position']['x'] < 10
    assert -10 <= show['position']['z'] < 10


def test_specific_objects_array_single_num_range():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": {
                "min": 2,
                "max": 4
            }
        }]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 1
    obj = component.specific_interactable_objects[0]
    assert obj.num.min == 2
    assert obj.num.max == 4
    assert obj.material is None
    assert obj.position is None
    assert obj.rotation is None
    assert obj.scale == 1
    assert obj.shape is None

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    assert 2 <= len(scene['objects']) <= 4
    for obj in scene['objects']:
        assert 'id' in obj
        assert 'mass' in obj
        assert 'type' in obj
        assert obj['type'] in FULL_TYPE_LIST
        assert 'materials' in obj
        assert isinstance(obj['materials'], list)
        if len(obj['materials']) > 0:
            assert obj['materials'][0] in materials.ALL_MATERIAL_STRINGS
        show = obj['shows'][0]
        assert show['scale']['x'] == show['scale']['z'] == 1
        assert 0 <= show['rotation']['y'] < 360
        assert -10 <= show['position']['x'] < 10
        assert -10 <= show['position']['z'] < 10


def test_specific_objects_array_single_mat_list_mixed():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 5,
            "material": [
                "PLASTIC_MATERIALS",
                "AI2-THOR/Materials/Metals/Brass 1"
            ]
        }]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 1
    obj = component.specific_interactable_objects[0]
    assert obj.num == 5
    assert isinstance(obj.material, list)

    scene = component.update_ile_scene(prior_scene())

    material_options = ["AI2-THOR/Materials/Metals/Brass 1"]

    for mat_color in materials.PLASTIC_MATERIALS:
        material_options.append(mat_color[0])

    assert isinstance(scene['objects'], list)
    assert len(scene['objects']) == 5
    for obj in scene['objects']:
        assert 'materials' in obj
        assert isinstance(obj['materials'], list)
        for mat in obj['materials']:
            assert mat in material_options


def test_specific_objects_single_shape():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "num": 7,
            "shape": "crayon_blue"
        }
    })
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig)
    obj = component.specific_interactable_objects
    assert obj.num == 7
    assert isinstance(obj.shape, str)
    assert obj.shape == "crayon_blue"

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    assert len(scene['objects']) == 7
    for obj in scene['objects']:
        assert 'type' in obj
        assert isinstance(obj['type'], str)
        assert obj['type'] == "crayon_blue"


def test_specific_objects_array_multiple_scale():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "scale": 1.5
        }, {
            "num": 3,
            "scale": {
                "x": 2,
                "y": [4.5, 5.5],
                "z": {
                    "min": 0,
                    "max": 0.5
                }
            }
        }]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 2
    obj = component.specific_interactable_objects[0]
    assert obj.num == 1
    assert obj.scale == 1.5
    obj = component.specific_interactable_objects[1]
    assert obj.num == 3
    s = obj.scale
    assert s.x == 2
    assert s.y == [4.5, 5.5]
    assert s.z.min == 0
    assert s.z.max == 0.5

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    assert len(scene['objects']) == 4
    objs = scene['objects']
    obj = objs[0]
    s = obj['shows'][0]['scale']
    assert isinstance(s, dict)
    assert s['x'] == 1.5
    assert (s['y'] * (1 if obj['type'] != 'cylinder' else 2)) == 1.5
    assert s['z'] == 1.5
    for i in range(3):
        obj = objs[i + 1]
        s = obj['shows'][0]['scale']
        assert s['x'] == 2
        assert (s['y'] * (1 if obj['type'] != 'cylinder' else 2)) in [4.5, 5.5]
        assert 0 <= s['z'] <= 0.5


def test_specific_objects_array_multiple_position_rotation():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "position": {
                "x": 1.5
            }
        }, {
            "num": 3,
            "position": {
                "x": 2,
                "y": .1,
                "z": {
                    "min": -5,
                    "max": 3.2
                }
            },
            "rotation": {
                "y": {
                    "min": 40,
                    "max": 279
                }
            }
        }]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 2
    obj = component.specific_interactable_objects[0]
    assert obj.num == 1
    assert obj.position.x == 1.5
    obj = component.specific_interactable_objects[1]
    assert obj.num == 3
    p = obj.position
    assert p.x == 2
    assert p.y == 0.1
    assert p.z.min == -5
    assert p.z.max == 3.2

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    assert len(scene['objects']) == 4
    objs = scene['objects']
    obj = objs[0]
    show = obj['shows'][0]
    assert 'position' in show
    p = show['position']
    assert isinstance(p, dict)
    assert p['x'] == 1.5
    assert p['y'] == 0
    assert p['z'] == 0
    for i in range(3):
        obj = objs[i + 1]['shows'][0]
        p = obj['position']
        assert p['x'] == 2
        assert p['y'] == 0.1
        assert -5 <= p['z'] <= 3.2
        r = obj['rotation']
        assert 40 <= r['y'] <= 279


def test_specific_objects_array_multiple():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{}, {}]
    })
    assert isinstance(component.specific_interactable_objects, list)
    assert len(component.specific_interactable_objects) == 2
    for obj in component.specific_interactable_objects:
        assert obj.num == 1
        assert obj.material is None
        assert obj.position is None
        assert obj.rotation is None
        assert obj.scale == 1
        assert obj.shape is None

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    assert len(scene['objects']) == 2
    for obj in scene['objects']:
        assert 'id' in obj
        assert 'mass' in obj
        assert 'type' in obj
        assert obj['type'] in FULL_TYPE_LIST
        assert 'materials' in obj
        print(obj['materials'])
        assert isinstance(obj['materials'], list)
        for mat in obj['materials']:
            assert mat in materials.ALL_MATERIAL_STRINGS
        show = obj['shows'][0]
        assert show['scale']['x'] == show['scale']['z'] == 1
        assert 0 <= show['rotation']['y'] < 360
        assert -10 <= show['position']['x'] < 10
        assert -10 <= show['position']['z'] < 10


def test_random_interactable_objects_config_component():
    component = RandomInteractableObjectsComponent({})
    assert component.num_random_interactable_objects is None

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) < 31


def test_random_interactable_objects_config_component_configured():
    component = RandomInteractableObjectsComponent({
        'num_random_interactable_objects': 5
    })
    assert component.num_random_interactable_objects == 5

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 5


def test_random_interactable_objects_config_component_configured_min_max():
    component = RandomInteractableObjectsComponent({
        'num_random_interactable_objects': MinMaxInt(1, 4)
    })
    assert component.num_random_interactable_objects == MinMaxInt(1, 4)

    scene = component.update_ile_scene(prior_scene())
    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert 1 <= len(objs) <= 4


def test_random_interactable_objects_config_component_fail():
    with pytest.raises(ILEException):
        RandomInteractableObjectsComponent({
            'num_random_interactable_objects': ''
        })


def test_random_interactable_objects_config_component_overlap():
    component = RandomInteractableObjectsComponent({
        'num_random_interactable_objects': 10
    })
    assert component.num_random_interactable_objects == 10

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    for obj_1 in objs:
        bounds = [
            obj_2['shows'][0]['boundingBox']
            for obj_2 in objs
            if obj_1['id'] != obj_2['id']
        ]

        assert geometry.validate_location_rect(
            obj_1['shows'][0]['boundingBox'],
            scene['performerStart']['position'],
            bounds,
            scene['roomDimensions']
        )


def test_random_interactable_objects_types_none():
    component = RandomKeywordObjectsComponent({})

    assert component.keyword_objects is None

    computed = component.get_keyword_objects()
    assert isinstance(computed, List)
    assert len(computed) == 2
    assert computed[0].keyword in ["containers", "obstacles", "occluders"]
    assert 2 <= computed[0].num <= 4
    assert computed[1].keyword == "context"
    assert 0 <= computed[1].num <= 10

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    # occluders create 2 objects
    assert 2 <= len(objs) <= 18
    for obj in objs:
        ...


def test_random_interactable_objects_types_containers():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'containers',
            'num': 4,
        }
    })

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'containers'
    assert computed[0].num == 4

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 4
    for obj in objs:
        assert obj['receptacle']

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 4 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS))


def test_random_interactable_objects_types_containers_contain_without_target():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'containers_can_contain_target',
            'num': 4
        }]
    })
    assert (component.keyword_objects[0].keyword ==
            'containers_can_contain_target')
    assert component.keyword_objects[0].num == 4

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'containers_can_contain_target'
    assert computed[0].num == 4

    with pytest.raises(ILEConfigurationException):
        component.update_ile_scene(prior_scene())


def test_random_interactable_objects_types_containers_contain_target():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'containers_can_contain_target',
            'num': 2
        }]
    })
    assert (component.keyword_objects[0].keyword ==
            'containers_can_contain_target')
    assert component.keyword_objects[0].num == 2

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'containers_can_contain_target'
    assert computed[0].num == 2

    scene = component.update_ile_scene(prior_scene_with_target())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 3
    for i, obj in enumerate(objs):
        if i != 0:
            assert obj['receptacle']

    assert 2 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 2 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS))
    assert 2 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS_CAN_CONTAIN_TARGET))  # noqa


def test_random_interactable_objects_types_containers_min_max():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'containers',
            'num': {
                'min': 1,
                'max': 3
            }
        }]
    })
    assert component.keyword_objects[0].keyword == 'containers'
    assert component.keyword_objects[0].num.min == 1
    assert component.keyword_objects[0].num.max == 3

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'containers'
    assert 1 <= computed[0].num <= 3

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert 1 <= len(objs) <= 3
    for obj in objs:
        assert obj['receptacle']

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 1 <= len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS)) <= 3


def test_random_interactable_objects_types_confusors():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'confusors',
            'num': {
                'min': 2,
                'max': 4
            }
        }]
    })
    assert component.keyword_objects[0].keyword == 'confusors'
    assert component.keyword_objects[0].num.min == 2
    assert component.keyword_objects[0].num.max == 4

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'confusors'
    assert 2 <= computed[0].num <= 4

    scene = component.update_ile_scene(prior_scene_with_target())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert 3 <= len(objs) <= 5
    goal = None
    for idx, obj in enumerate(objs):
        if idx == 0:
            # assume this is the goal
            assert obj['type'] == 'soccer_ball'
            goal = obj
            continue
        assert obj['moveable']
        sim_color = util.is_similar_except_in_color(obj, goal)
        sim_shape = util.is_similar_except_in_shape(obj, goal)
        sim_size = util.is_similar_except_in_size(obj, goal)
        assert sim_color or sim_shape or sim_size

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 2 <= len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONFUSORS)) <= 4


def test_random_interactable_objects_types_obstacles():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'obstacles',
            'num': 2
        }]
    })
    assert component.keyword_objects[0].keyword == 'obstacles'
    assert component.keyword_objects[0].num == 2

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'obstacles'
    assert computed[0].num == 2

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 1 <= len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_OBSTACLES)) <= 2


def test_random_interactable_objects_types_obstacles_with_target():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'obstacles',
            'num': 2
        }]
    })
    assert component.keyword_objects[0].keyword == 'obstacles'
    assert component.keyword_objects[0].num == 2

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'obstacles'
    assert computed[0].num == 2

    scene = component.update_ile_scene(prior_scene_with_target())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 3

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 2 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_OBSTACLES))


def test_random_interactable_objects_types_occluders():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'occluders',
            'num': 3
        }]
    })
    assert component.keyword_objects[0].keyword == 'occluders'
    assert component.keyword_objects[0].num == 3

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'occluders'
    assert computed[0].num == 3

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 3

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 3 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_OCCLUDERS))


def test_random_interactable_objects_types_occluders_with_target():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'occluders',
            'num': 3
        }]
    })
    assert component.keyword_objects[0].keyword == 'occluders'
    assert component.keyword_objects[0].num == 3

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'occluders'
    assert computed[0].num == 3

    scene = component.update_ile_scene(prior_scene_with_target())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 4

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 3 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_OCCLUDERS))


def test_random_interactable_objects_types_context():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'context',
            'num': 5
        }
    })

    assert component.keyword_objects.keyword == 'context'
    assert component.keyword_objects.num == 5

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'context'
    assert computed[0].num == 5

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 5

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 5 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTEXT))


def test_random_interactable_objects_types_occluder_front():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': {
            'keyword': 'containers',
            'num': 4,
            'keyword_location': {
                'keyword': 'front'
            }
        }
    })

    computed = component.get_keyword_objects()
    assert len(computed) == 1
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'containers'
    assert computed[0].num == 4

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 4
    for obj in objs:
        assert obj['receptacle']
        pos = obj['shows'][0]['position']
        assert pos['x'] == 0
        assert pos['z'] > 0

    assert 1 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 4 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS))


def test_random_interactable_objects_types_context_in_containers():
    component = RandomKeywordObjectsComponent({
        'keyword_objects': [{
            'keyword': 'containers',
            'num': 1,
        }, {
            'keyword': 'context',
            'num': 1,
            'keyword_location': {
                'keyword': 'adjacent',
                'relative_object_label':
                RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS
            }}
        ]
    })

    computed = component.get_keyword_objects()
    assert len(computed) == 2
    assert isinstance(computed[0], KeywordObjectsConfig)
    assert computed[0].keyword == 'containers'
    assert computed[0].num == 1

    assert isinstance(computed[1], KeywordObjectsConfig)
    assert computed[1].keyword == 'context'
    assert computed[1].num == 1
    assert computed[1].keyword_location.keyword == 'adjacent'
    assert (computed[1].keyword_location.relative_object_label ==
            RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS)

    scene = component.update_ile_scene(prior_scene())

    assert isinstance(scene['objects'], list)
    objs = scene['objects']
    assert len(objs) == 2
    assert objs[0]['receptacle']

    assert 2 == len(ObjectRepository.get_instance()._labeled_object_store)
    assert 1 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTAINERS))
    assert 1 == len(ObjectRepository.get_instance()
                    .get_all_from_labeled_objects(
        RandomKeywordObjectsComponent.LABEL_KEYWORDS_CONTEXT))


def test_specific_objects_delayed_action():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": {
            "keyword_location": {
                "keyword": "in",
                "container_label": "no_object"
            }
        }
    })
    assert isinstance(
        component.specific_interactable_objects,
        InteractableObjectConfig)
    sio = component.specific_interactable_objects
    assert sio.material is None
    assert sio.num == 1
    assert sio.shape is None
    assert sio.scale == 1
    assert sio.rotation is None
    assert sio.position is None

    scene = component.update_ile_scene(prior_scene())
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 0
    component.get_num_delayed_actions() == 1


def test_specific_objects_delayed_action_adjacent():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "keyword_location": {
                "keyword": "adjacent",
                "relative_object_label": "after_object"
            }
        }, {
            "labels": "after_object"
        }]
    })

    scene = component.update_ile_scene(prior_scene())
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 1
    assert component.get_num_delayed_actions() == 1

    scene = component.run_delayed_actions(scene)
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 2
    component.get_num_delayed_actions() == 0
    #  objects[1][]


def test_specific_objects_delayed_action_in():
    component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "shape": "crayon_blue",
            "keyword_location": {
                "keyword": "in",
                "container_label": "chest"
            }
        }, {
            "labels": "chest",
            "shape": "chest_3"
        }]
    })

    scene = component.update_ile_scene(prior_scene())
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 1
    assert component.get_num_delayed_actions() == 1

    scene = component.run_delayed_actions(scene)
    objects = scene['objects']
    assert isinstance(objects, list)
    assert len(objects) == 2
    component.get_num_delayed_actions() == 0
    assert objects[1]['locationParent'] == objects[0]['id']
