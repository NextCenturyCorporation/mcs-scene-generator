import pytest

from ideal_learning_env import ILEException, VectorFloatConfig
from ideal_learning_env.mock_component import MockClass, MockComponent


def test_ile_component_call_each_setter_on_init():
    component = MockComponent({})
    assert component._called_setter['bool_prop']
    assert component._called_setter['class_prop']
    assert component._called_setter['float_prop']
    assert component._called_setter['int_prop']
    assert component._called_setter['list_bool_prop']
    assert component._called_setter['list_class_prop']
    assert component._called_setter['list_float_prop']
    assert component._called_setter['list_int_prop']
    assert component._called_setter['list_str_prop']
    assert component._called_setter['str_prop']
    assert component._called_setter['union_bool_prop']
    assert component._called_setter['union_class_prop']
    assert component._called_setter['union_float_prop']
    assert component._called_setter['union_int_prop']
    assert component._called_setter['union_str_prop']


def test_ile_component_initialize_null():
    component = MockComponent({})
    assert component.bool_prop is None
    assert component.class_prop is None
    assert component.float_prop is None
    assert component.int_prop is None
    assert component.list_bool_prop is None
    assert component.list_class_prop is None
    assert component.list_float_prop is None
    assert component.list_int_prop is None
    assert component.list_str_prop is None
    assert component.str_prop is None
    assert component.union_bool_prop is None
    assert component.union_class_prop is None
    assert component.union_float_prop is None
    assert component.union_int_prop is None
    assert component.union_str_prop is None

    component = MockComponent({
        'bool_prop': None,
        'class_prop': None,
        'float_prop': None,
        'int_prop': None,
        'list_bool_prop': None,
        'list_class_prop': None,
        'list_float_prop': None,
        'list_int_prop': None,
        'list_str_prop': None,
        'str_prop': None,
        'union_bool_prop': None,
        'union_class_prop': None,
        'union_float_prop': None,
        'union_int_prop': None,
        'union_str_prop': None
    })
    assert component.bool_prop is None
    assert component.class_prop is None
    assert component.float_prop is None
    assert component.int_prop is None
    assert component.list_bool_prop is None
    assert component.list_class_prop is None
    assert component.list_float_prop is None
    assert component.list_int_prop is None
    assert component.list_str_prop is None
    assert component.str_prop is None
    assert component.union_bool_prop is None
    assert component.union_class_prop is None
    assert component.union_float_prop is None
    assert component.union_int_prop is None
    assert component.union_str_prop is None


def test_ile_component_initialize():
    component = MockComponent({
        'bool_prop': True,
        'class_prop': {
            'dict_prop': {'key1': 'value1'},
            'int_prop': 0,
            'list_dict_prop': [
                {'key2': 'value2'}, {'key3': 'value3', 'key4': 'value4'}
            ],
            'list_int_prop': [12, 34, 56, 78],
            'list_vector_prop': [{}, {'x': 1, 'y': 2, 'z': 3}],
            'union_int_prop': [78, 56, 34, 12],
            'union_vector_prop': {'x': 0.3, 'y': 0.2, 'z': 0.1},
            'vector_prop': {'x': 0.1, 'y': 0.2, 'z': 0.3}
        },
        'float_prop': 12.34,
        'int_prop': 100,
        'list_bool_prop': [False, True],
        'list_class_prop': [{}, {
            'dict_prop': {'key5': 'value5'},
            'int_prop': -1,
            'list_dict_prop': [
                {'key6': 'value6'}, {'key7': 'value7', 'key8': 'value8'}
            ],
            'list_int_prop': [87, 65, 43, 21],
            'list_vector_prop': [{}, {'x': 9, 'y': 8, 'z': 7}],
            'union_int_prop': [21, 43, 65, 87],
            'union_vector_prop': {'x': 0.7, 'y': 0.8, 'z': 0.9},
            'vector_prop': {'x': 0.9, 'y': 0.8, 'z': 0.7}
        }],
        'list_float_prop': [-1, -0.5, 0, 0.5, 1],
        'list_int_prop': [-2, -1, 0, 1, 2],
        'list_str_prop': ['a', 'b', 'c', 'd'],
        'str_prop': 'foobar',
        'union_bool_prop': False,
        'union_class_prop': {
            'dict_prop': {'keyA': 'valueA'},
            'int_prop': 999,
            'list_dict_prop': [
                {'keyB': 'valueB'}, {'keyC': 'valueC', 'keyD': 'valueD'}
            ],
            'list_int_prop': [123, 456],
            'list_vector_prop': [{}, {'x': 4, 'y': 5, 'z': 6}],
            'union_int_prop': [456, 123],
            'union_vector_prop': {'x': 0.6, 'y': 0.5, 'z': 0.4},
            'vector_prop': {'x': 0.4, 'y': 0.5, 'z': 0.6}
        },
        'union_float_prop': -12.34,
        'union_int_prop': -100,
        'union_str_prop': 'the quick brown fox'
    })
    assert component.bool_prop is True
    assert component.class_prop == MockClass(
        dict_prop={'key1': 'value1'},
        int_prop=0,
        list_dict_prop=[
            {'key2': 'value2'}, {'key3': 'value3', 'key4': 'value4'}
        ],
        list_int_prop=[12, 34, 56, 78],
        list_vector_prop=[VectorFloatConfig(), VectorFloatConfig(1, 2, 3)],
        union_int_prop=[78, 56, 34, 12],
        union_vector_prop=VectorFloatConfig(0.3, 0.2, 0.1),
        vector_prop=VectorFloatConfig(0.1, 0.2, 0.3)
    )
    assert component.float_prop == 12.34
    assert component.int_prop == 100
    assert component.list_bool_prop == [False, True]
    assert component.list_class_prop == [
        MockClass(),
        MockClass(
            dict_prop={'key5': 'value5'},
            int_prop=-1,
            list_dict_prop=[
                {'key6': 'value6'}, {'key7': 'value7', 'key8': 'value8'}
            ],
            list_int_prop=[87, 65, 43, 21],
            list_vector_prop=[VectorFloatConfig(), VectorFloatConfig(9, 8, 7)],
            union_int_prop=[21, 43, 65, 87],
            union_vector_prop=VectorFloatConfig(0.7, 0.8, 0.9),
            vector_prop=VectorFloatConfig(0.9, 0.8, 0.7)
        )
    ]
    assert component.list_float_prop == [-1, -0.5, 0, 0.5, 1]
    assert component.list_int_prop == [-2, -1, 0, 1, 2]
    assert component.list_str_prop == ['a', 'b', 'c', 'd']
    assert component.str_prop == 'foobar'
    assert component.union_bool_prop is False
    assert component.union_class_prop == MockClass(
        dict_prop={'keyA': 'valueA'},
        int_prop=999,
        list_dict_prop=[
            {'keyB': 'valueB'}, {'keyC': 'valueC', 'keyD': 'valueD'}
        ],
        list_int_prop=[123, 456],
        list_vector_prop=[VectorFloatConfig(), VectorFloatConfig(4, 5, 6)],
        union_int_prop=[456, 123],
        union_vector_prop=VectorFloatConfig(0.6, 0.5, 0.4),
        vector_prop=VectorFloatConfig(0.4, 0.5, 0.6)
    )
    assert component.union_float_prop == -12.34
    assert component.union_int_prop == -100
    assert component.union_str_prop == 'the quick brown fox'


def test_ile_component_update():
    component = MockComponent({
        'bool_prop': True,
        'class_prop': {
            'dict_prop': {'key1': 'value1'},
            'int_prop': 0,
            'list_dict_prop': [
                {'key2': 'value2'}, {'key3': 'value3', 'key4': 'value4'}
            ],
            'list_int_prop': [12, 34, 56, 78],
            'list_vector_prop': [{}, {'x': 1, 'y': 2, 'z': 3}],
            'union_int_prop': [78, 56, 34, 12],
            'union_vector_prop': {'x': 0.3, 'y': 0.2, 'z': 0.1},
            'vector_prop': {'x': 0.1, 'y': 0.2, 'z': 0.3}
        },
        'float_prop': 12.34,
        'int_prop': 100,
        'list_bool_prop': [False, True],
        'list_class_prop': [{}, {
            'dict_prop': {'key5': 'value5'},
            'int_prop': -1,
            'list_dict_prop': [
                {'key6': 'value6'}, {'key7': 'value7', 'key8': 'value8'}
            ],
            'list_int_prop': [87, 65, 43, 21],
            'list_vector_prop': [{}, {'x': 9, 'y': 8, 'z': 7}],
            'union_int_prop': [21, 43, 65, 87],
            'union_vector_prop': {'x': 0.7, 'y': 0.8, 'z': 0.9},
            'vector_prop': {'x': 0.9, 'y': 0.8, 'z': 0.7}
        }],
        'list_float_prop': [-1, -0.5, 0, 0.5, 1],
        'list_int_prop': [-2, -1, 0, 1, 2],
        'list_str_prop': ['a', 'b', 'c', 'd'],
        'str_prop': 'foobar',
        'union_bool_prop': False,
        'union_class_prop': {
            'dict_prop': {'keyA': 'valueA'},
            'int_prop': 999,
            'list_dict_prop': [
                {'keyB': 'valueB'}, {'keyC': 'valueC', 'keyD': 'valueD'}
            ],
            'list_int_prop': [123, 456],
            'list_vector_prop': [{}, {'x': 4, 'y': 5, 'z': 6}],
            'union_int_prop': [456, 123],
            'union_vector_prop': {'x': 0.6, 'y': 0.5, 'z': 0.4},
            'vector_prop': {'x': 0.4, 'y': 0.5, 'z': 0.6}
        },
        'union_float_prop': -12.34,
        'union_int_prop': -100,
        'union_str_prop': 'the quick brown fox'
    })
    scene = component.update_ile_scene({'existing_prop': True})
    assert scene['existing_prop'] is True
    assert scene['bool_prop'] is True
    assert scene['class_prop'] == {
        'dict_prop': {'key1': 'value1'},
        'int_prop': 0,
        'list_dict_prop': [
            {'key2': 'value2'}, {'key3': 'value3', 'key4': 'value4'}
        ],
        'list_int_prop': [12, 34, 56, 78],
        'list_vector_prop': [
            {'x': None, 'y': None, 'z': None},
            {'x': 1, 'y': 2, 'z': 3}
        ],
        'union_int_prop': [78, 56, 34, 12],
        'union_vector_prop': {'x': 0.3, 'y': 0.2, 'z': 0.1},
        'vector_prop': {'x': 0.1, 'y': 0.2, 'z': 0.3}
    }
    assert scene['float_prop'] == 12.34
    assert scene['int_prop'] == 100
    assert scene['list_bool_prop'] == [False, True]
    assert scene['list_class_prop'] == [{
        'dict_prop': None,
        'int_prop': None,
        'list_dict_prop': None,
        'list_int_prop': None,
        'list_vector_prop': None,
        'union_int_prop': None,
        'union_vector_prop': None,
        'vector_prop': None
    }, {
        'dict_prop': {'key5': 'value5'},
        'int_prop': -1,
        'list_dict_prop': [
            {'key6': 'value6'}, {'key7': 'value7', 'key8': 'value8'}
        ],
        'list_int_prop': [87, 65, 43, 21],
        'list_vector_prop': [
            {'x': None, 'y': None, 'z': None},
            {'x': 9, 'y': 8, 'z': 7}
        ],
        'union_int_prop': [21, 43, 65, 87],
        'union_vector_prop': {'x': 0.7, 'y': 0.8, 'z': 0.9},
        'vector_prop': {'x': 0.9, 'y': 0.8, 'z': 0.7}
    }]
    assert scene['list_float_prop'] == [-1, -0.5, 0, 0.5, 1]
    assert scene['list_int_prop'] == [-2, -1, 0, 1, 2]
    assert scene['list_str_prop'] == ['a', 'b', 'c', 'd']
    assert scene['str_prop'] == 'foobar'
    assert scene['union_bool_prop'] is False
    assert scene['union_class_prop'] == {
        'dict_prop': {'keyA': 'valueA'},
        'int_prop': 999,
        'list_dict_prop': [
            {'keyB': 'valueB'}, {'keyC': 'valueC', 'keyD': 'valueD'}
        ],
        'list_int_prop': [123, 456],
        'list_vector_prop': [
            {'x': None, 'y': None, 'z': None},
            {'x': 4, 'y': 5, 'z': 6}
        ],
        'union_int_prop': [456, 123],
        'union_vector_prop': {'x': 0.6, 'y': 0.5, 'z': 0.4},
        'vector_prop': {'x': 0.4, 'y': 0.5, 'z': 0.6}
    }
    assert scene['union_float_prop'] == -12.34
    assert scene['union_int_prop'] == -100
    assert scene['union_str_prop'] == 'the quick brown fox'


def test_ile_component_validate_fail_bool():
    with pytest.raises(ILEException):
        MockComponent({
            'bool_prop': 'foobar'
        })


def test_ile_component_validate_fail_class():
    with pytest.raises(ILEException):
        MockComponent({
            'class_prop': 'foobar'
        })


def test_ile_component_validate_fail_class_nested_class():
    with pytest.raises(ILEException):
        MockComponent({
            'class_prop': {
                'vector_prop': {'x': 0.1, 'y': 0.2, 'z': 'foobar'}
            }
        })


def test_ile_component_validate_fail_class_nested_dict():
    with pytest.raises(ILEException):
        MockComponent({
            'class_prop': {
                'dict_prop': {'key': 1234}
            }
        })


def test_ile_component_validate_fail_class_nested_list():
    with pytest.raises(ILEException):
        MockComponent({
            'class_prop': {
                'list_int_prop': [12, 'foobar']
            }
        })


def test_ile_component_validate_fail_class_nested_primitive():
    with pytest.raises(ILEException):
        MockComponent({
            'class_prop': {
                'int_prop': 'foobar'
            }
        })


def test_ile_component_validate_fail_float():
    with pytest.raises(ILEException):
        MockComponent({
            'float_prop': 'foobar'
        })


def test_ile_component_validate_fail_int():
    with pytest.raises(ILEException):
        MockComponent({
            'int_prop': 'foobar'
        })


def test_ile_component_validate_fail_int_if_bool():
    # Specific case since bool extends int
    with pytest.raises(ILEException):
        MockComponent({
            'int_prop': True
        })


def test_ile_component_validate_fail_list_bool():
    with pytest.raises(ILEException):
        MockComponent({
            'list_bool_prop': [False, 'foobar']
        })


def test_ile_component_validate_fail_list_class():
    with pytest.raises(ILEException):
        MockComponent({
            'list_class_prop': [{
                'dict_prop': {'key1': 'value1'},
                'int_prop': 0,
                'list_dict_prop': [
                    {'key2': 'value2'}, {'key3': 'value3', 'key4': 'value4'}
                ],
                'list_int_prop': [12, 34, 56, 78],
                'list_vector_prop': [{}, {'x': 1, 'y': 2, 'z': 3}],
                'union_int_prop': [78, 56, 34, 12],
                'union_vector_prop': {'x': 0.3, 'y': 0.2, 'z': 0.1},
                'vector_prop': {'x': 0.1, 'y': 0.2, 'z': 0.3}
            }, 'foobar']
        })


def test_ile_component_validate_fail_list_class_nested_class():
    with pytest.raises(ILEException):
        MockComponent({
            'list_class_prop': [{
                'vector_prop': {'x': 0.1, 'y': 0.2, 'z': 'foobar'}
            }]
        })


def test_ile_component_validate_fail_list_class_nested_dict():
    with pytest.raises(ILEException):
        MockComponent({
            'list_class_prop': [{
                'dict_prop': {'key': 1234}
            }]
        })


def test_ile_component_validate_fail_list_class_nested_list():
    with pytest.raises(ILEException):
        MockComponent({
            'list_class_prop': [{
                'list_int_prop': [12, 'foobar']
            }]
        })


def test_ile_component_validate_fail_list_class_nested_primitive():
    with pytest.raises(ILEException):
        MockComponent({
            'list_class_prop': [{
                'int_prop': 'foobar'
            }]
        })


def test_ile_component_validate_fail_list_float():
    with pytest.raises(ILEException):
        MockComponent({
            'list_float_prop': [1.0, 'foobar']
        })


def test_ile_component_validate_fail_list_int():
    with pytest.raises(ILEException):
        MockComponent({
            'list_int_prop': [1, 'foobar']
        })


def test_ile_component_validate_fail_list_int_if_bool():
    # Specific case since bool extends int
    with pytest.raises(ILEException):
        MockComponent({
            'list_int_prop': [True]
        })


def test_ile_component_validate_fail_list_str():
    with pytest.raises(ILEException):
        MockComponent({
            'list_str_prop': ['foobar', 1]
        })


def test_ile_component_validate_fail_list_str_empty():
    with pytest.raises(ILEException):
        MockComponent({
            'list_str_prop': ['']
        })


def test_ile_component_validate_fail_str():
    with pytest.raises(ILEException):
        MockComponent({
            'str_prop': 1
        })


def test_ile_component_validate_fail_str_empty():
    with pytest.raises(ILEException):
        MockComponent({
            'str_prop': ''
        })


def test_ile_component_validate_fail_union_bool():
    with pytest.raises(ILEException):
        MockComponent({
            'union_bool_prop': 'foobar'
        })


def test_ile_component_validate_fail_union_class():
    with pytest.raises(ILEException):
        MockComponent({
            'union_class_prop': 'foobar'
        })


def test_ile_component_validate_fail_union_class_nested_class():
    with pytest.raises(ILEException):
        MockComponent({
            'union_class_prop': {
                'vector_prop': {'x': 0.1, 'y': 0.2, 'z': 'foobar'}
            }
        })


def test_ile_component_validate_fail_union_class_nested_dict():
    with pytest.raises(ILEException):
        MockComponent({
            'union_class_prop': {
                'dict_prop': {'key': 1234}
            }
        })


def test_ile_component_validate_fail_union_class_nested_list():
    with pytest.raises(ILEException):
        MockComponent({
            'union_class_prop': {
                'list_int_prop': [12, 'foobar']
            }
        })


def test_ile_component_validate_fail_union_class_nested_primitive():
    with pytest.raises(ILEException):
        MockComponent({
            'union_class_prop': {
                'int_prop': 'foobar'
            }
        })


def test_ile_component_validate_fail_union_float():
    with pytest.raises(ILEException):
        MockComponent({
            'union_float_prop': 'foobar'
        })


def test_ile_component_validate_fail_union_int():
    with pytest.raises(ILEException):
        MockComponent({
            'union_int_prop': 'foobar'
        })


def test_ile_component_validate_fail_union_int_if_bool():
    # Specific case since bool extends int
    with pytest.raises(ILEException):
        MockComponent({
            'union_int_prop': True
        })


def test_ile_component_validate_fail_union_list_bool():
    with pytest.raises(ILEException):
        MockComponent({
            'union_bool_prop': [False, 'foobar']
        })


def test_ile_component_validate_fail_union_list_class():
    with pytest.raises(ILEException):
        MockComponent({
            'union_class_prop': [{
                'dict_prop': {'key1': 'value1'},
                'int_prop': 0,
                'list_dict_prop': [
                    {'key2': 'value2'}, {'key3': 'value3', 'key4': 'value4'}
                ],
                'list_int_prop': [12, 34, 56, 78],
                'list_vector_prop': [{}, {'x': 1, 'y': 2, 'z': 3}],
                'union_int_prop': [78, 56, 34, 12],
                'union_vector_prop': {'x': 0.3, 'y': 0.2, 'z': 0.1},
                'vector_prop': {'x': 0.1, 'y': 0.2, 'z': 0.3}
            }, 'foobar']
        })


def test_ile_component_validate_fail_union_list_class_nested_class():
    with pytest.raises(ILEException):
        MockComponent({
            'union_class_prop': [{
                'vector_prop': {'x': 0.1, 'y': 0.2, 'z': 'foobar'}
            }]
        })


def test_ile_component_validate_fail_union_list_class_nested_dict():
    with pytest.raises(ILEException):
        MockComponent({
            'union_class_prop': [{
                'dict_prop': {'key': 1234}
            }]
        })


def test_ile_component_validate_fail_union_list_class_nested_list():
    with pytest.raises(ILEException):
        MockComponent({
            'union_class_prop': [{
                'list_int_prop': [12, 'foobar']
            }]
        })


def test_ile_component_validate_fail_union_list_class_nested_primitive():
    with pytest.raises(ILEException):
        MockComponent({
            'union_class_prop': [{
                'int_prop': 'foobar'
            }]
        })


def test_ile_component_validate_fail_union_list_float():
    with pytest.raises(ILEException):
        MockComponent({
            'union_float_prop': [1.0, 'foobar']
        })


def test_ile_component_validate_fail_union_list_int():
    with pytest.raises(ILEException):
        MockComponent({
            'union_int_prop': [1, 'foobar']
        })


def test_ile_component_validate_fail_union_list_int_if_bool():
    # Specific case since bool extends int
    with pytest.raises(ILEException):
        MockComponent({
            'union_int_prop': [True]
        })


def test_ile_component_validate_fail_union_list_str():
    with pytest.raises(ILEException):
        MockComponent({
            'union_str_prop': ['foobar', 1]
        })


def test_ile_component_validate_fail_union_list_str_empty():
    with pytest.raises(ILEException):
        MockComponent({
            'union_str_prop': ['']
        })


def test_ile_component_validate_fail_union_str():
    with pytest.raises(ILEException):
        MockComponent({
            'union_str_prop': 1
        })


def test_ile_component_validate_fail_union_str_empty():
    with pytest.raises(ILEException):
        MockComponent({
            'union_str_prop': ''
        })
