import copy

import pytest
from machine_common_sense.config_manager import Vector3d

from generator import MaterialTuple, base_objects, materials
from ideal_learning_env import (
    MinMax,
    MinMaxFloat,
    MinMaxInt,
    VectorFloatConfig,
    VectorIntConfig,
    choose_position,
    choose_random,
    choose_rotation,
)
from ideal_learning_env.choosers import choose_shape_material
from ideal_learning_env.defs import ILEException
from ideal_learning_env.mock_component import MockClass


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    # Setup: fill with any logic you want
    saved_type_list = copy.deepcopy(base_objects.FULL_TYPE_LIST)
    saved_material_restrictions = copy.deepcopy(base_objects._TYPES_TO_DETAILS)
    saved_all_types = base_objects._MATERIAL_TO_VALID_TYPE["_all_types"]
    yield  # this is where the testing happens
    # Teardown : fill with any logic you want
    base_objects.FULL_TYPE_LIST = saved_type_list
    base_objects._TYPES_TO_DETAILS = saved_material_restrictions
    base_objects._MATERIAL_TO_VALID_TYPE["_all_types"] = saved_all_types


def test_choose_position():
    assert choose_position(VectorFloatConfig(1, 2, 3)) == Vector3d(1, 2, 3)

    result = choose_position(VectorFloatConfig(1, [2, 3], MinMaxFloat(4, 5)))
    assert isinstance(result, Vector3d)
    assert result.x == 1
    assert result.y in [2, 3]
    assert 4 <= result.z <= 5

    result = choose_position([
        VectorFloatConfig(1, 2, 3),
        VectorFloatConfig(4, 5, 6)
    ])
    assert result == Vector3d(1, 2, 3) or result == Vector3d(4, 5, 6)


def test_choose_position_random():
    result = choose_position(None, 1, 2, 4, 8)
    assert isinstance(result, Vector3d)
    assert -1.5 <= result.x <= 1.5
    assert result.y == 0
    assert -3 <= result.z <= 3


def test_choose_random():
    assert choose_random('a', str) == 'a'
    assert choose_random('', str) == ''
    assert choose_random(1, int) == 1
    assert choose_random(0, int) == 0
    assert choose_random(True, bool) is True
    assert choose_random(False, bool) is False
    assert choose_random({'key1': 'value1'}, dict) == {'key1': 'value1'}
    assert choose_random({'key2': 'value2'}, dict) == {'key2': 'value2'}


def test_choose_random_list():
    assert choose_random(['a'], str) == 'a'
    choice = choose_random(['a', 'b'], str)
    assert choice in ['a', 'b']
    assert choose_random([1], int) == 1
    choice = choose_random([1, 2], int)
    assert choice in [1, 2]
    assert choose_random([True], bool) is True
    choice = choose_random([True, False], bool)
    assert choice in [True, False]
    assert choose_random([{'key1': 'value1'}], dict) == {'key1': 'value1'}
    choice = choose_random([{'key1': 'value1'}, {'key2': 'value2'}], dict)
    assert choice in [{'key1': 'value1'}, {'key2': 'value2'}]


def test_choose_random_min_max():
    choice = choose_random(MinMaxFloat(0.0, 1.0), MinMax)
    assert 0.0 <= choice <= 1.0
    choice = choose_random(MinMaxInt(1, 10), MinMax)
    assert 1 <= choice <= 10


def test_choose_random_min_max_in_list():
    choice = choose_random([MinMaxInt(1, 10), MinMaxInt(21, 30)], MinMax)
    assert (1 <= choice <= 10) or (21 <= choice <= 30)


def test_choose_random_string_to_material_tuple():
    choice = choose_random('Custom/Materials/GreyWoodMCS', MaterialTuple)
    assert choice == MaterialTuple('Custom/Materials/GreyWoodMCS', ['grey'])
    choice = choose_random(['Custom/Materials/GreyWoodMCS'], MaterialTuple)
    assert choice == MaterialTuple('Custom/Materials/GreyWoodMCS', ['grey'])


def test_choose_random_tuple_to_material_tuple():
    choice = choose_random(('mat1', ['color1']), MaterialTuple)
    assert choice == MaterialTuple('mat1', ['color1'])
    choice = choose_random([('mat1', ['color1'])], MaterialTuple)
    assert choice == MaterialTuple('mat1', ['color1'])


def test_choose_random_converter_class():
    choice = choose_random(VectorFloatConfig(0.9, 0.8, 0.7))
    assert choice == Vector3d(0.9, 0.8, 0.7)

    choice = choose_random(VectorIntConfig(1, 2, 3))
    assert choice == Vector3d(1, 2, 3)

    choice = choose_random(VectorIntConfig(1, 2, [3, 4]))
    assert isinstance(choice, Vector3d)
    assert choice.x == 1
    assert choice.y == 2
    assert choice.z in [3, 4]

    choice = choose_random(VectorIntConfig(1, 2, MinMaxInt(3, 8)))
    assert isinstance(choice, Vector3d)
    assert choice.x == 1
    assert choice.y == 2
    assert 3 <= choice.z <= 8


def test_choose_random_converter_class_in_list():
    choice = choose_random([VectorIntConfig(1, 2, MinMaxInt(3, 8))])
    assert isinstance(choice, Vector3d)
    assert choice.x == 1
    assert choice.y == 2
    assert 3 <= choice.z <= 8


def test_choose_random_class_variables():
    choice = choose_random(MockClass(
        int_prop=1,
        list_int_prop=[2, 3],
        union_int_prop=4
    ))
    assert isinstance(choice, MockClass)
    assert isinstance(choice.int_prop, int)
    assert isinstance(choice.list_int_prop, int)
    assert isinstance(choice.union_int_prop, int)
    assert choice.int_prop == 1
    assert choice.list_int_prop in [2, 3]
    assert choice.union_int_prop == 4

    choice = choose_random(MockClass(
        vector_prop=VectorFloatConfig(0.1, 0.2, 0.3),
        list_vector_prop=[
            VectorFloatConfig(11, 21, 31),
            VectorFloatConfig(12, 22, 32),
            VectorFloatConfig(13, 23, 33)
        ],
        union_vector_prop=VectorFloatConfig(0.9, 0.8, 0.7)
    ))
    assert isinstance(choice, MockClass)
    assert isinstance(choice.vector_prop, Vector3d)
    assert isinstance(choice.list_vector_prop, Vector3d)
    assert isinstance(choice.union_vector_prop, Vector3d)
    assert choice.vector_prop == Vector3d(0.1, 0.2, 0.3)
    assert choice.list_vector_prop.x in [11, 12, 13]
    assert choice.list_vector_prop.y in [21, 22, 23]
    assert choice.list_vector_prop.z in [31, 32, 33]
    assert choice.union_vector_prop == Vector3d(0.9, 0.8, 0.7)


def test_choose_random_class_variables_in_list():
    choice = choose_random([MockClass(
        int_prop=1,
        list_int_prop=[2, 3],
        union_int_prop=4
    )])
    assert isinstance(choice, MockClass)
    assert isinstance(choice.int_prop, int)
    assert isinstance(choice.list_int_prop, int)
    assert isinstance(choice.union_int_prop, int)
    assert choice.int_prop == 1
    assert choice.list_int_prop in [2, 3]
    assert choice.union_int_prop == 4

    choice = choose_random([MockClass(
        vector_prop=VectorFloatConfig(0.1, 0.2, 0.3),
        list_vector_prop=[
            VectorFloatConfig(11, 21, 31),
            VectorFloatConfig(12, 22, 32),
            VectorFloatConfig(13, 23, 33)
        ],
        union_vector_prop=VectorFloatConfig(0.9, 0.8, 0.7)
    )])
    assert isinstance(choice, MockClass)
    assert isinstance(choice.vector_prop, Vector3d)
    assert isinstance(choice.list_vector_prop, Vector3d)
    assert isinstance(choice.union_vector_prop, Vector3d)
    assert choice.vector_prop == Vector3d(0.1, 0.2, 0.3)
    assert choice.list_vector_prop.x in [11, 12, 13]
    assert choice.list_vector_prop.y in [21, 22, 23]
    assert choice.list_vector_prop.z in [31, 32, 33]
    assert choice.union_vector_prop == Vector3d(0.9, 0.8, 0.7)


def test_choose_rotation():
    assert choose_rotation(VectorIntConfig(1, 2, 3)) == Vector3d(1, 2, 3)

    result = choose_rotation(VectorIntConfig(1, [2, 3], MinMaxInt(4, 5)))
    assert (
        result == Vector3d(1, 2, 4) or result == Vector3d(1, 3, 4) or
        result == Vector3d(1, 2, 5) or result == Vector3d(1, 3, 5)
    )

    result = choose_rotation([
        VectorIntConfig(1, 2, 3),
        VectorIntConfig(4, 5, 6)
    ])
    assert result == Vector3d(1, 2, 3) or result == Vector3d(4, 5, 6)


def test_choose_rotation_random():
    result = choose_rotation(None)
    assert isinstance(result, Vector3d)
    assert -1.5 <= result.x <= 1.5
    assert result.x == 0
    assert result.y in [0, 45, 90, 135, 180, 225, 270, 315]
    assert result.z == 0


def test_choose_shape_material_both_none():
    expected_shape = 'car_1'
    expected_material = ("AI2-THOR/Materials/Wood/WhiteWood", ["white"]),
    base_objects.FULL_TYPE_LIST = [expected_shape]
    func = base_objects._TYPES_TO_DETAILS[expected_shape].definition_function
    base_objects._TYPES_TO_DETAILS[expected_shape] = (
        base_objects.TypeDetailsTuple(
            func, [expected_material]))
    shape, mat = choose_shape_material(None, None)
    assert shape is not None
    assert mat is not None
    assert shape == expected_shape
    assert mat == expected_material


def test_choose_shape_material_material_none_non_restricted():
    shape, mat = choose_shape_material('soccer_ball', None)
    assert shape == 'soccer_ball'
    assert mat is not None
    assert mat in materials.ALL_MATERIAL_TUPLES


def test_choose_shape_material_material_none_restricted():
    shape, mat = choose_shape_material('ball', None)
    assert shape == 'ball'
    assert mat is not None
    assert mat in base_objects.get_material_restriction(shape)


def test_choose_shape_material_shape_none():
    mat_input = "AI2-THOR/Materials/Fabrics/Sofa1_Brown"
    expected_shape = "sofa_1"
    temp = base_objects.FULL_TYPE_LIST
    base_objects.FULL_TYPE_LIST = [expected_shape]
    base_objects._MATERIAL_TO_VALID_TYPE["_all_types"] = []
    shape, mat = choose_shape_material(None, mat_input)
    base_objects.FULL_TYPE_LIST = temp
    assert shape == expected_shape
    assert mat[0] == mat_input
    assert mat[1] == ["brown"]


def test_choose_shape_material_neither_none_restricted():
    shape_input = "sofa_1"
    mat_input = "AI2-THOR/Materials/Fabrics/Sofa1_Brown"
    shape, mat = choose_shape_material(shape_input, mat_input)
    assert shape == "sofa_1"
    assert mat[0] == "AI2-THOR/Materials/Fabrics/Sofa1_Brown"
    assert mat[1] == ['brown']


def test_choose_shape_material_neither_none_non_restricted():
    shape_input = "apple_1"
    mat_input = "AI2-THOR/Materials/Fabrics/BedroomCarpet"
    shape, mat = choose_shape_material(shape_input, mat_input)
    assert shape == "apple_1"
    assert mat[0] == "AI2-THOR/Materials/Fabrics/BedroomCarpet"
    assert mat[1] == ['blue']


def test_choose_shape_material_neither_none_invalid():
    shape_input = "sofa_2"
    mat_input = "AI2-THOR/Materials/Fabrics/Sofa1_Brown"
    with pytest.raises(ILEException):
        choose_shape_material(shape_input, mat_input)
