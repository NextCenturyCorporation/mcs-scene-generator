import copy

import pytest
from machine_common_sense.config_manager import Vector3d

from generator import MaterialTuple, base_objects
from ideal_learning_env import (
    MinMax,
    MinMaxFloat,
    MinMaxInt,
    VectorFloatConfig,
    VectorIntConfig,
    choose_counts,
    choose_position,
    choose_random,
    choose_rotation,
    choose_scale
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


def test_choose_counts():
    item_a = {'id': 'a', 'num': 1}
    item_b = {'id': 'b', 'num': [2, 3]}
    item_c = {'id': 'c', 'num': MinMaxInt(4, 6)}
    item_d = {'id': 'd', 'num': [MinMaxInt(1, 2), MinMaxInt(7, 8)]}

    assert choose_counts([]) == []

    assert choose_counts([item_a]) == [(item_a, 1)]

    result = choose_counts([item_b])
    assert result == [(item_b, 2)] or result == [(item_b, 3)]

    result = choose_counts([item_a, item_b])
    assert (
        result == [(item_a, 1), (item_b, 2)] or
        result == [(item_a, 1), (item_b, 3)]
    )

    result = choose_counts([item_c])
    assert (
        result == [(item_c, 4)] or result == [(item_c, 5)] or
        result == [(item_c, 6)]
    )

    result = choose_counts([item_c, item_a])
    assert (
        result == [(item_c, 4), (item_a, 1)] or
        result == [(item_c, 5), (item_a, 1)] or
        result == [(item_c, 6), (item_a, 1)]
    )

    result = choose_counts([item_d])
    assert (
        result == [(item_d, 1)] or result == [(item_d, 2)] or
        result == [(item_d, 7)] or result == [(item_d, 8)]
    )

    result = choose_counts([item_d, item_a])
    assert (
        result == [(item_d, 1), (item_a, 1)] or
        result == [(item_d, 2), (item_a, 1)] or
        result == [(item_d, 7), (item_a, 1)] or
        result == [(item_d, 8), (item_a, 1)]
    )

    assert choose_counts([{}]) == [({}, 1)]
    assert choose_counts([{}, {}]) == [({}, 1), ({}, 1)]


def test_choose_counts_override_defaults():
    item_a = {'id': 'a', 'count': 1}
    item_b = {'id': 'b', 'count': [2, 3]}
    item_c = {'id': 'c', 'count': MinMaxInt(4, 6)}
    item_d = {'id': 'd', 'count': [MinMaxInt(1, 2), MinMaxInt(7, 8)]}

    assert choose_counts([item_a], 'count', 0) == [(item_a, 1)]

    result = choose_counts([item_b], 'count', 0)
    assert result == [(item_b, 2)] or result == [(item_b, 3)]

    result = choose_counts([item_c], 'count', 0)
    assert (
        result == [(item_c, 4)] or result == [(item_c, 5)] or
        result == [(item_c, 6)]
    )

    result = choose_counts([item_d], 'count', 0)
    assert (
        result == [(item_d, 1)] or result == [(item_d, 2)] or
        result == [(item_d, 7)] or result == [(item_d, 8)]
    )

    assert choose_counts([{}], 'count', 0) == [({}, 0)]
    assert choose_counts([{}, {}], 'count', 0) == [({}, 0), ({}, 0)]


def test_choose_position():
    assert choose_position(VectorFloatConfig(
        1, 2, 3)) == Vector3d(x=1, y=2, z=3)

    result = choose_position(VectorFloatConfig(1, [2, 3], MinMaxFloat(4, 5)))
    assert isinstance(result, Vector3d)
    assert result.x == 1
    assert result.y in [2, 3]
    assert 4 <= result.z <= 5

    result = choose_position([
        VectorFloatConfig(1, 2, 3),
        VectorFloatConfig(4, 5, 6)
    ])
    assert result in [Vector3d(x=1, y=2, z=3), Vector3d(x=4, y=5, z=6)]

    assert choose_position(VectorFloatConfig(1, None, 3)
                           ) == Vector3d(x=1, y=0, z=3)
    pos = choose_position(
        VectorFloatConfig(
            1,
            None,
            None),
        room_x=4,
        room_z=4,
        object_x=.5,
        object_z=0.5)
    assert pos.x == 1
    assert pos.y == 0
    assert -1.75 <= pos.z <= 1.75


def test_choose_position_random():
    result = choose_position(None, 1, 2, 4, 6, 8)
    assert isinstance(result, Vector3d)
    assert -1.5 <= result.x <= 1.5
    assert result.y == 0
    assert -3 <= result.z <= 3


def test_choose_position_within_bounds():
    position = VectorFloatConfig(
        [-4, -2.5, 0, 2.5, 4],
        7,
        MinMaxFloat(-5, 5))
    room_dimensions = VectorFloatConfig(5, 10, 5)
    bounds = 0.5
    result = choose_position(
        position=position,
        object_x=bounds,
        object_z=bounds,
        room_x=room_dimensions.x,
        room_y=room_dimensions.y,
        room_z=room_dimensions.z
    )

    assert isinstance(result, Vector3d)
    assert result.x in [-2.5, 0, 2.5]
    assert result.y == 7
    assert -2.75 <= result.z <= 2.75

    room_dimensions = VectorFloatConfig(3, 4, 5)
    position = VectorFloatConfig(
        1,
        MinMaxFloat(0, 5),
        [-5, -2, 0, 2, 5])
    result = choose_position(
        position=position,
        object_x=bounds,
        object_z=bounds,
        room_x=room_dimensions.x,
        room_y=room_dimensions.y,
        room_z=room_dimensions.z
    )

    assert isinstance(result, Vector3d)
    assert result.x == 1
    assert 0 <= result.y <= 3.75
    assert result.z in [-2, 0, 2]


def test_choose_position_within_bounds_placer_obj():
    position = VectorFloatConfig(
        [-4, -2.5, 0, 2.5, 4],
        9,
        MinMaxFloat(-5, 5))
    room_dimensions = VectorFloatConfig(5, 10, 5)
    bounds = 0.5
    result = choose_position(
        position=position,
        object_x=bounds,
        object_z=bounds,
        room_x=room_dimensions.x,
        room_y=room_dimensions.y,
        room_z=room_dimensions.z,
        is_placer_obj=True
    )

    assert isinstance(result, Vector3d)
    assert result.x in [-2.5, 0, 2.5]
    assert result.y == 9
    assert -2.75 <= result.z <= 2.75

    room_dimensions = VectorFloatConfig(3, 4, 5)
    position = VectorFloatConfig(
        1,
        MinMaxFloat(0, 5),
        [-5, -2, 0, 2, 5])
    result = choose_position(
        position=position,
        object_x=bounds,
        object_z=bounds,
        room_x=room_dimensions.x,
        room_y=room_dimensions.y,
        room_z=room_dimensions.z,
        is_placer_obj=True
    )

    assert isinstance(result, Vector3d)
    assert result.x == 1
    assert 0 <= result.y <= 5
    assert result.z in [-2, 0, 2]


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
    assert choice == Vector3d(x=0.9, y=0.8, z=0.7)

    choice = choose_random(VectorIntConfig(1, 2, 3))
    assert choice == Vector3d(x=1, y=2, z=3)

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
    assert choice.vector_prop == Vector3d(x=0.1, y=0.2, z=0.3)
    assert choice.list_vector_prop.x in [11, 12, 13]
    assert choice.list_vector_prop.y in [21, 22, 23]
    assert choice.list_vector_prop.z in [31, 32, 33]
    assert choice.union_vector_prop == Vector3d(x=0.9, y=0.8, z=0.7)


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
    assert choice.vector_prop == Vector3d(x=0.1, y=0.2, z=0.3)
    assert choice.list_vector_prop.x in [11, 12, 13]
    assert choice.list_vector_prop.y in [21, 22, 23]
    assert choice.list_vector_prop.z in [31, 32, 33]
    assert choice.union_vector_prop == Vector3d(x=0.9, y=0.8, z=0.7)


def test_choose_rotation():
    assert choose_rotation(VectorIntConfig(1, 2, 3)) == Vector3d(x=1, y=2, z=3)

    result = choose_rotation(VectorIntConfig(1, [2, 3], MinMaxInt(4, 5)))
    assert (
        result == Vector3d(x=1, y=2, z=4) or
        result == Vector3d(x=1, y=3, z=4) or
        result == Vector3d(x=1, y=2, z=5) or
        result == Vector3d(x=1, y=3, z=5)
    )

    result = choose_rotation([
        VectorIntConfig(1, 2, 3),
        VectorIntConfig(4, 5, 6)
    ])
    assert result == Vector3d(
        x=1, y=2, z=3) or result == Vector3d(x=4, y=5, z=6)


def test_choose_rotation_random():
    result = choose_rotation(None)
    assert isinstance(result, Vector3d)
    assert -1.5 <= result.x <= 1.5
    assert result.x == 0
    assert result.y in [0, 45, 90, 135, 180, 225, 270, 315]
    assert result.z == 0


def test_choose_scale():
    assert choose_scale(None, 'sofa_1') == 1
    assert choose_scale(1.5, 'sofa_1') == 1.5
    assert choose_scale([0.5, 1.5], 'sofa_1') in [0.5, 1.5]
    assert (
        choose_scale(VectorFloatConfig(1, 1.5, 2), 'sofa_1') ==
        Vector3d(x=1, y=1.5, z=2)
    )
    result = choose_scale([
        VectorFloatConfig(1, 1.5, 2),
        VectorFloatConfig(3, 3, 3)
    ], 'sofa_1')
    assert result == Vector3d(
        x=1, y=1.5, z=2) or result == Vector3d(x=3, y=3, z=3)
    result = choose_scale(MinMaxFloat(1.4, 1.6), 'sofa_1')
    assert 1.4 <= result <= 1.6
    result = choose_scale([
        MinMaxFloat(1.4, 1.6),
        MinMaxFloat(3.4, 3.6),
    ], 'sofa_1')
    assert (1.4 <= result <= 1.6) or (3.4 <= result <= 3.6)


def test_choose_scale_soccer_ball():
    result = choose_scale(None, 'soccer_ball')
    assert 1 <= result <= 3
    result = choose_scale(0.5, 'soccer_ball')
    assert 1 <= result <= 3
    assert choose_scale(1.5, 'soccer_ball') == 1.5
    assert choose_scale([0.5, 1.5], 'soccer_ball') == 1.5
    assert choose_scale([1, 2, 3], 'soccer_ball') in [1, 2, 3]
    result = choose_scale(VectorFloatConfig(1, 1.5, 2), 'soccer_ball')
    assert 1 <= result <= 3
    result = choose_scale([
        VectorFloatConfig(1, 1.5, 2),
        VectorFloatConfig(3, 3, 3)
    ], 'soccer_ball')
    assert result == Vector3d(x=3, y=3, z=3)
    result = choose_scale(MinMaxFloat(1.4, 1.6), 'soccer_ball')
    assert 1.4 <= result <= 1.6
    result = choose_scale([
        MinMaxFloat(1.4, 1.6),
        MinMaxFloat(3.4, 3.6),
    ], 'soccer_ball')
    assert 1.4 <= result <= 1.6


def test_choose_shape_material_both_none():
    expected_shape = "car_1"
    expected_material = ("AI2-THOR/Materials/Wood/WhiteWood", ["white"])
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
    shape, mat = choose_shape_material("soccer_ball", None)
    assert shape == "soccer_ball"
    assert mat is None


def test_choose_shape_material_material_none_restricted():
    shape_input = "sphere"
    restrictions = base_objects.get_material_restriction_strings(shape_input)
    shape, mat = choose_shape_material(shape_input, None)
    assert shape == shape_input
    assert mat is not None
    assert mat.material in restrictions


def test_choose_shape_material_shape_none():
    mat_input = "AI2-THOR/Materials/Fabrics/Sofa1_Brown"
    expected_shape = "sofa_1"
    temp = base_objects.FULL_TYPE_LIST
    base_objects.FULL_TYPE_LIST = [expected_shape]
    base_objects._MATERIAL_TO_VALID_TYPE["_all_types"] = []
    shape, mat = choose_shape_material(None, mat_input)
    base_objects.FULL_TYPE_LIST = temp
    assert shape == expected_shape
    assert mat.material == mat_input
    assert mat.color == ["brown"]


def test_choose_shape_material_shape_none_material_list():
    mat_input = [
        "AI2-THOR/Materials/Fabrics/Sofa1_Brown",
        "AI2-THOR/Materials/Fabrics/Sofa1_Red"
    ]
    expected_shape = "sofa_1"
    temp = base_objects.FULL_TYPE_LIST
    base_objects.FULL_TYPE_LIST = [expected_shape]
    base_objects._MATERIAL_TO_VALID_TYPE["_all_types"] = []
    shape, mat = choose_shape_material(None, mat_input)
    base_objects.FULL_TYPE_LIST = temp
    assert shape == expected_shape
    assert mat.material in mat_input
    assert mat.color[0] in ["brown", "red"]


def test_choose_shape_material_neither_none_restricted():
    shape_input = "sofa_1"
    mat_input = "AI2-THOR/Materials/Fabrics/Sofa1_Brown"
    shape, mat = choose_shape_material(shape_input, mat_input)
    assert shape == "sofa_1"
    assert mat.material == "AI2-THOR/Materials/Fabrics/Sofa1_Brown"
    assert mat.color == ["brown"]


def test_choose_shape_material_neither_none_restricted_category():
    shape_input = "sofa_1"
    mat_input = "SOFA_1_MATERIALS"
    shape, mat = choose_shape_material(shape_input, mat_input)
    assert shape == "sofa_1"
    assert mat.material.startswith("AI2-THOR/Materials/Fabrics/Sofa1_")


def test_choose_shape_material_neither_none_restricted_material_list():
    shape_input = "sofa_1"
    mat_input = [
        "AI2-THOR/Materials/Fabrics/Sofa1_Brown",
        "AI2-THOR/Materials/Fabrics/Sofa1_Red"
    ]
    shape, mat = choose_shape_material(shape_input, mat_input)
    assert shape == "sofa_1"
    assert mat.material in mat_input
    assert mat.color[0] in ["brown", "red"]


def test_choose_shape_material_neither_none_non_restricted():
    shape_input = "sphere"
    mat_input = "AI2-THOR/Materials/Fabrics/Carpet2"
    shape, mat = choose_shape_material(shape_input, mat_input)
    assert shape == "sphere"
    assert mat.material == "AI2-THOR/Materials/Fabrics/Carpet2"
    assert mat.color == ["brown"]


def test_choose_shape_material_neither_none_non_restricted_category():
    shape_input = "sphere"
    mat_input = "RUBBER_MATERIALS"
    shape, mat = choose_shape_material(shape_input, mat_input)
    assert shape == "sphere"
    assert mat.material.startswith("AI2-THOR/Materials/Plastics/")
    assert mat.material.endswith("Rubber")


def test_choose_shape_material_neither_none_non_restricted_material_list():
    shape_input = "sphere"
    mat_input = [
        "AI2-THOR/Materials/Fabrics/Carpet2",
        "AI2-THOR/Materials/Fabrics/Carpet8"
    ]
    shape, mat = choose_shape_material(shape_input, mat_input)
    assert shape == "sphere"
    assert mat.material in mat_input
    assert mat.color[0] in ["brown", "black"]


def test_choose_shape_material_neither_none_invalid():
    shape_input = "sofa_2"
    mat_input = "AI2-THOR/Materials/Fabrics/Sofa1_Brown"
    with pytest.raises(ILEException):
        choose_shape_material(shape_input, mat_input)


def test_choose_shape_material_both_none_with_prohibited():
    expected_shape = "car_1"
    expected_material = MaterialTuple(
        "AI2-THOR/Materials/Wood/WhiteWood",
        ["white"]
    )
    prohibited = MaterialTuple("AI2-THOR/Materials/Wood/BlackWood", ["black"])
    base_objects.FULL_TYPE_LIST = [expected_shape]
    func = base_objects._TYPES_TO_DETAILS[expected_shape].definition_function
    base_objects._TYPES_TO_DETAILS[expected_shape] = (
        base_objects.TypeDetailsTuple(
            func, [expected_material, prohibited]))
    shape, mat = choose_shape_material(None, None, prohibited.material)
    assert shape is not None
    assert mat is not None
    assert shape == expected_shape
    assert mat == expected_material


def test_choose_shape_material_category_with_prohibited():
    shape_input = "sphere"
    mat_input = "WOOD_MATERIALS"
    prohibited = "AI2-THOR/Materials/Wood/BlackWood"
    shape, mat = choose_shape_material(shape_input, mat_input, prohibited)
    assert shape == shape_input
    assert mat is not None
    assert mat.material != prohibited
    assert "black" not in mat.color


def test_choose_shape_material_material_none_restricted_with_prohibited():
    shape_input = "sphere"
    restrictions = base_objects.get_material_restriction_strings(shape_input)
    prohibited = "AI2-THOR/Materials/Wood/WhiteWood"
    assert prohibited in restrictions
    shape, mat = choose_shape_material(shape_input, None, prohibited)
    assert shape == shape_input
    assert mat is not None
    assert mat.material in restrictions
    assert mat.material != prohibited


def test_choose_shape_material_shape_none_with_prohibited():
    mat_input = [
        "AI2-THOR/Materials/Fabrics/Sofa1_Brown",
        "AI2-THOR/Materials/Fabrics/Sofa1_Red"
    ]
    prohibited = "AI2-THOR/Materials/Fabrics/Sofa1_Red"
    expected_shape = "sofa_1"
    temp = base_objects.FULL_TYPE_LIST
    base_objects.FULL_TYPE_LIST = [expected_shape]
    base_objects._MATERIAL_TO_VALID_TYPE["_all_types"] = []
    shape, mat = choose_shape_material(None, mat_input, prohibited)
    base_objects.FULL_TYPE_LIST = temp
    assert shape == expected_shape
    assert mat.material == "AI2-THOR/Materials/Fabrics/Sofa1_Brown"
    assert mat.color == ["brown"]


def test_choose_shape_material_neither_none_restricted_with_prohibited():
    shape_input = "sofa_1"
    mat_input = [
        "AI2-THOR/Materials/Fabrics/Sofa1_Brown",
        "AI2-THOR/Materials/Fabrics/Sofa1_Red"
    ]
    prohibited = "AI2-THOR/Materials/Fabrics/Sofa1_Red"
    shape, mat = choose_shape_material(shape_input, mat_input, prohibited)
    assert shape == "sofa_1"
    assert mat.material == "AI2-THOR/Materials/Fabrics/Sofa1_Brown"
    assert mat.color == ["brown"]


def test_choose_shape_material_neither_none_non_restricted_with_prohibited():
    shape_input = "sphere"
    mat_input = [
        "AI2-THOR/Materials/Fabrics/Carpet2",
        "AI2-THOR/Materials/Fabrics/Carpet8"
    ]
    prohibited = "AI2-THOR/Materials/Fabrics/Carpet8"
    shape, mat = choose_shape_material(shape_input, mat_input, prohibited)
    assert shape == "sphere"
    assert mat.material == "AI2-THOR/Materials/Fabrics/Carpet2"
    assert mat.color == ["brown"]


def test_choose_shape_material_prohibited_colors():
    shape_input = "sphere"
    mat_input = [
        "AI2-THOR/Materials/Wood/BlackWood",
        "AI2-THOR/Materials/Wood/WoodGrain_Brown",
        "AI2-THOR/Materials/Wood/WoodGrain_Tan"
    ]
    prohibited = "AI2-THOR/Materials/Wood/WoodGrain_Tan"
    shape, mat = choose_shape_material(shape_input, mat_input, prohibited)
    assert shape == "sphere"
    assert mat.material == "AI2-THOR/Materials/Wood/BlackWood"
    assert mat.color == ["black"]


def test_choose_shape_material_category_prohibited_colors():
    shape_input = "sphere"
    mat_input = "WOOD_MATERIALS"
    prohibited = "AI2-THOR/Materials/Wood/WoodGrain_Tan"
    shape, mat = choose_shape_material(shape_input, mat_input, prohibited)
    assert shape == "sphere"
    assert mat.material != prohibited
    assert "brown" not in mat.color
