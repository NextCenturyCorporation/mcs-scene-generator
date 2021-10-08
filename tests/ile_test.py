from ideal_learning_env.mock_component import MockComponent
from ile import generate_ile_scene


def test_generate_ile_scene():
    scene = generate_ile_scene([], 1)
    assert scene == {
        'name': '',
        'version': 2,
        'objects': [],
        'goal': {
            'domainsInfo': {},
            'objectsInfo': {},
            'sceneInfo': {},
            'metadata': {}
        },
        'debug': {
            'sceneNumber': 1,
            'training': True
        }
    }


def test_generate_ile_scene_with_mock_components():
    component_1 = MockComponent({
        'str_prop': 'foobar'
    })
    component_2 = MockComponent({
        'bool_prop': True,
        'float_prop': 12.34,
        'int_prop': 100
    })
    scene = generate_ile_scene([component_1, component_2], 2)
    assert scene == {
        'name': '',
        'version': 2,
        'objects': [],
        'goal': {
            'domainsInfo': {},
            'objectsInfo': {},
            'sceneInfo': {},
            'metadata': {}
        },
        'debug': {
            'sceneNumber': 2,
            'training': True
        },
        'bool_prop': True,
        'float_prop': 12.34,
        'int_prop': 100,
        'str_prop': 'foobar'
    }
