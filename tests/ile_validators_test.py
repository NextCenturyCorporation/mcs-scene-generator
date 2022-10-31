from dataclasses import dataclass
from typing import Any

import pytest

from ideal_learning_env import (
    ILEException,
    ILEValidator,
    MinMaxFloat,
    MinMaxInt,
    ValidateAnd,
    ValidateList,
    ValidateNoNullProp,
    ValidateNumber,
    ValidateOptions,
    ValidateOr,
    ValidateSpecific,
    VectorFloatConfig,
    VectorIntConfig
)


@dataclass
class ValidateAlwaysPass(ILEValidator):
    def _validate_prop(self, prop: str, data: Any) -> bool:
        return True


@dataclass
class ValidateAlwaysFail(ILEValidator):
    def _validate_prop(self, prop: str, data: Any) -> bool:
        raise ILEException('Always fail')


def test_validate_no_null_prop():
    validator = ValidateNoNullProp()
    validator.validate('key', [])
    validator.validate('key', {})
    validator.validate('key', [{}])
    validator.validate('key', {'a': 'b'})
    validator.validate('key', [{'a': 'b'}])


def test_validate_no_null_prop_dict_with_none():
    validator = ValidateNoNullProp()
    with pytest.raises(ILEException):
        validator.validate('key', {'a': 'b', 'c': None})


def test_validate_no_null_prop_list_with_dict_with_none():
    validator = ValidateNoNullProp()
    with pytest.raises(ILEException):
        validator.validate('key', [{'a': 'b', 'c': None}])


def test_validate_no_null_prop_list_with_none():
    validator = ValidateNoNullProp()
    with pytest.raises(ILEException):
        validator.validate('key', ['a', 'b', None])


def test_validate_no_null_prop_list_with_class_with_none():
    validator = ValidateNoNullProp()
    with pytest.raises(ILEException):
        validator.validate('key', [VectorIntConfig(0, 1, None)])


def test_validate_no_null_prop_class_with_none():
    validator = ValidateNoNullProp()
    with pytest.raises(ILEException):
        validator.validate('key', VectorIntConfig(0, 1, None))


def test_validate_number():
    validator = ValidateNumber(min_value=2, max_value=3)
    assert validator.validate('key', 2)
    assert validator.validate('key', 2.5)
    assert validator.validate('key', 3)


def test_validate_number_data_type_minmax():
    validator = ValidateNumber(min_value=2, max_value=6)
    assert validator.validate('key', MinMaxInt(2, 6))
    assert validator.validate('key', MinMaxInt(3, 5))
    assert validator.validate('key', MinMaxInt(4, 4))
    assert validator.validate('key', MinMaxFloat(2, 6))
    assert validator.validate('key', MinMaxFloat(2.1, 5.9))
    assert validator.validate('key', MinMaxFloat(3.33, 3.33))


def test_validate_number_data_type_minmax_with_max_above_max():
    validator = ValidateNumber(min_value=2, max_value=6)
    with pytest.raises(ILEException):
        assert validator.validate('key', MinMaxInt(4, 7))


def test_validate_number_data_type_minmax_with_max_below_min():
    validator = ValidateNumber(min_value=2, max_value=6)
    with pytest.raises(ILEException):
        assert validator.validate('key', MinMaxInt(2, 1))


def test_validate_number_data_type_minmax_with_min_above_max():
    validator = ValidateNumber(min_value=2, max_value=6)
    with pytest.raises(ILEException):
        assert validator.validate('key', MinMaxInt(7, 6))


def test_validate_number_data_type_minmax_with_min_below_min():
    validator = ValidateNumber(min_value=2, max_value=6)
    with pytest.raises(ILEException):
        assert validator.validate('key', MinMaxInt(1, 4))


def test_validate_number_data_type_vector():
    validator = ValidateNumber(min_value=2, max_value=6)
    assert validator.validate('key', VectorIntConfig(2, 4, 6))
    assert validator.validate('key', VectorFloatConfig(2, 4, 6))


def test_validate_number_data_type_vector_with_value_above_max():
    validator = ValidateNumber(min_value=2, max_value=6)
    with pytest.raises(ILEException):
        assert validator.validate('key', VectorIntConfig(2, 4, 8))


def test_validate_number_data_type_vector_with_value_below_min():
    validator = ValidateNumber(min_value=2, max_value=6)
    with pytest.raises(ILEException):
        assert validator.validate('key', VectorIntConfig(1, 4, 6))


def test_validate_number_negative_range():
    validator = ValidateNumber(min_value=-3, max_value=-2)
    assert validator.validate('key', -2)
    assert validator.validate('key', -2.5)
    assert validator.validate('key', -3)


def test_validate_number_max_only():
    validator = ValidateNumber(max_value=3)
    assert validator.validate('key', 3)
    assert validator.validate('key', -3)


def test_validate_number_min_only():
    validator = ValidateNumber(min_value=2)
    assert validator.validate('key', 2)
    assert validator.validate('key', 20)


def test_validate_number_above_max():
    validator = ValidateNumber(min_value=2, max_value=3)
    with pytest.raises(ILEException):
        validator.validate('key', 3.01)


def test_validate_number_below_min():
    validator = ValidateNumber(min_value=2, max_value=3)
    with pytest.raises(ILEException):
        validator.validate('key', 1)


def test_validate_number_but_is_none():
    validator = ValidateNumber(min_value=2, max_value=3)
    with pytest.raises(ILEException):
        validator.validate('key', None)


def test_validate_number_list():
    validator = ValidateNumber(min_value=2, max_value=3)
    assert validator.validate('key', [])
    assert validator.validate('key', [2])
    assert validator.validate('key', [2, 3, 2, 3])


def test_validate_number_list_fail():
    validator = ValidateNumber(min_value=2, max_value=3)
    with pytest.raises(ILEException):
        validator.validate('key', [3, 2, 1])


def test_validate_number_list_with_none():
    validator = ValidateNumber(min_value=2, max_value=3)
    with pytest.raises(ILEException):
        validator.validate('key', [3, 2, None])


def test_validate_and_one_pass():
    validator = ValidateAnd(validators=[
        ValidateAlwaysFail('key', None),
        ValidateAlwaysFail('key', None),
        ValidateAlwaysPass('key', None),
        ValidateAlwaysFail('key', None)
    ])
    with pytest.raises(ILEException):
        assert validator.validate('key', 5)


def test_validate_and_all_pass():
    validator = ValidateAnd(validators=[
        ValidateAlwaysPass('key', None),
        ValidateAlwaysPass('key', None),
        ValidateAlwaysPass('key', None),
        ValidateAlwaysPass('key', None)
    ])
    assert validator.validate('key', 5)


def test_validate_and_all_fail():
    validator = ValidateAnd(validators=[
        ValidateAlwaysFail('key', None),
        ValidateAlwaysFail('key', None),
        ValidateAlwaysFail('key', None),
        ValidateAlwaysFail('key', None)
    ])
    with pytest.raises(ILEException):
        validator.validate('key', 5)


def test_validate_and_no_validators():
    validator = ValidateAnd()
    with pytest.raises(Exception):
        validator.validate('key', 5)


def test_validate_or_one_pass():
    validator = ValidateOr(validators=[
        ValidateAlwaysFail('key', None),
        ValidateAlwaysFail('key', None),
        ValidateAlwaysPass('key', None),
        ValidateAlwaysFail('key', None)
    ])
    assert validator.validate('key', 5)


def test_validate_or_all_pass():
    validator = ValidateOr(validators=[
        ValidateAlwaysPass('key', None),
        ValidateAlwaysPass('key', None),
        ValidateAlwaysPass('key', None),
        ValidateAlwaysPass('key', None)
    ])
    assert validator.validate('key', 5)


def test_validate_or_all_fail():
    validator = ValidateOr(validators=[
        ValidateAlwaysFail('key', None),
        ValidateAlwaysFail('key', None),
        ValidateAlwaysFail('key', None),
        ValidateAlwaysFail('key', None)
    ])
    with pytest.raises(ILEException):
        validator.validate('key', 5)


def test_validate_or_no_validators():
    validator = ValidateOr()
    with pytest.raises(Exception):
        validator.validate('key', 5)


def test_validate_list():
    validator = ValidateList()
    assert validator.validate('key', [3, 5])


def test_validate_list_empty_array():
    validator = ValidateList()
    assert validator.validate('key', [])


def test_validate_list_empty_array_min_ok():
    validator = ValidateList(min_count=5)
    assert validator.validate('key', [1, 2, 3, 4, 5, 6])


def test_validate_list_empty_array_min_raise():
    validator = ValidateList(min_count=5)
    with pytest.raises(ILEException):
        validator.validate('key', [1, 2, 3, 4])


def test_validate_list_empty_array_max_ok():
    validator = ValidateList(max_count=3)
    assert validator.validate('key', [1, 2, 3])


def test_validate_list_empty_array_max_raise():
    validator = ValidateList(max_count=3)
    with pytest.raises(ILEException):
        validator.validate('key', [1, 2, 3, 4])


def test_validate_options():
    validator = ValidateOptions(options=['a', 'b', 'c'])
    validator.validate('key', 'a')
    validator.validate('key', 'b')
    validator.validate('key', 'c')
    with pytest.raises(ILEException):
        validator.validate('key', 'd')


def test_validate_specific():
    validator = ValidateSpecific(typing=int)
    validator.validate('key', 0)
    validator.validate('key', 1)
    validator.validate('key', -10)
    with pytest.raises(ILEException):
        validator.validate('key', 1.0)
