from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Type, Union

from .defs import ILEException
from .numerics import MinMax, VectorFloatConfig, VectorIntConfig

INDENTATION = '    '
NEWLINE = '\n'


def exceptions_to_text(exceptions: List[str]) -> str:
    return f'{(NEWLINE + INDENTATION).join([""] + exceptions)}'


@dataclass
class ILEValidator(ABC):
    """Run validation on specific input data. Alternatively, run validation on
    one or more specific nested properties within the input data. Property
    names that have multiple levels of nesting must use the dot syntax for
    Python classes and dicts (prop.prop) or the bracket syntax for lists
    (prop[index]). Property names must ignore the root variable's name."""

    props: List[str] = None
    ignores: List[str] = None

    def __post_init__(self):
        for attr_name in ['props', 'ignores']:
            attr = getattr(self, attr_name)
            if attr:
                attr_type = (
                    type(attr[0]) if isinstance(attr, list) else type(attr)
                )
                if attr_type != str:
                    raise Exception(
                        f'{self.__name__} expected "{attr_name}" to be a list '
                        f'of strings but got {attr} -- did you mean to '
                        f'set another attribute on this validator?'
                    )

    def _must_validate(self, prop: str) -> bool:
        """Return if the given property must be validated. The property name
        should start with the root variable's name."""
        prop_rootless = prop[prop.find('.') + 1:]
        if self.props:
            return prop_rootless in self.props
        if self.ignores:
            return prop_rootless not in self.ignores
        return True

    @abstractmethod
    def _validate_prop(self, prop: str, data: Any) -> bool:
        """Return if the given data for the given property is valid. The
        property name should start with the root variable's name."""
        pass

    def validate(self, prop: str, data: Any) -> bool:
        """Return if the given data for the given property is valid. The
        property name should start with the root variable's name."""
        if self._must_validate(prop):
            return self._validate_prop(prop, data)
        return True


@dataclass
class ValidateAnd(ILEValidator):
    """Validate that all of multiple given validators pass."""

    validators: List[ILEValidator] = None

    # Override
    def _validate_prop(self, prop: str, data: Any) -> bool:
        if not self.validators:
            raise Exception('ValidateAnd must have one or more validators')
        exceptions = []
        for validator in self.validators:
            try:
                validator.validate(prop, data)
            except Exception as e:
                exceptions.append(str(e))
        if len(exceptions):
            raise ILEException(
                f'The following configured property must pass each validation:'
                f'{NEWLINE}{prop}: {data}{exceptions_to_text(exceptions)}'
            )
        return True


@dataclass
class ValidateList(ILEValidator):
    """Validate that a list contains a specific number of elements."""

    max_count: int = -1
    min_count: int = -1

    # Override
    def _validate_prop(self, prop: str, data: List[Any]) -> bool:
        if data is None:
            raise ILEException(
                f'The property "{prop}" must be a list but is null'
            )
        if self.max_count >= 0 and len(data) > self.max_count:
            raise ILEException(
                f'The property "{prop}" must be a list with a max of '
                f'{self.max_count} elements but is {data}'
            )
        if self.min_count >= 0 and len(data) < self.min_count:
            raise ILEException(
                f'The property "{prop}" must be a list with a min of '
                f'{self.min_count} elements but is {data}'
            )
        return True


class ValidateNested(ILEValidator, ABC):
    """Validate recursively on the given data, including all of its elements
    if it's a list, or all of its attributes if it's a dict or Python class.
    Useful so subclasses can run specific validation on nested properties."""

    # Override
    def validate(self, prop: str, data: Any) -> bool:
        super().validate(prop, data)
        # If the data is a list, recur on all the list's elements.
        if isinstance(data, list):
            for index, item in enumerate(data):
                self.validate(f'{prop}[{index}]', item)
        # If the data is a dict, recur on all the dict's attributes.
        elif isinstance(data, dict):
            for key, value in data.items():
                self.validate(f'{prop}.{key}', value)
        else:
            try:
                # If the data is a class, recur on all the class's attributes.
                for key, value in vars(data).items():
                    self.validate(f'{prop}.{key}', value)
            except TypeError:
                # Else it's not a class, so do nothing.
                pass
        return True


@dataclass
class ValidateNoNullProp(ValidateNested):
    """Validate that some given data is not null, including all of its elements
    if it's a list, or all of its attributes if it's a dict or Python class,
    recursively."""

    # Override
    def _validate_prop(self, prop: str, data: Any) -> bool:
        # Validate that the data isn't null.
        if data is None:
            raise ILEException(f'The property "{prop}" must not be null')
        return True


@dataclass
class ValidateNumber(ValidateNested):
    """Validate that a number is within a range, including all of its elements
    if it's a list, or all of its attributes if it's a dict or Python class,
    recursively."""

    max_value: float = None
    min_value: float = None
    null_ok: bool = False

    # Override
    def _validate_prop(self, prop: str, data: Union[float, int]) -> bool:
        # Validate that the data isn't null (this won't affect null top-level
        # properties because of behavior in ile_config_setter).
        if data is None:
            if self.null_ok:
                return True
            else:
                raise ILEException(
                    f'The property "{prop}" must be a number but is null'
                )
        if isinstance(data, (float, int)):
            if self.min_value is not None and data < self.min_value:
                raise ILEException(
                    f'The property "{prop}" must be greater than or equal to '
                    f'{self.min_value} but is {data}'
                )
            if self.max_value is not None and data > self.max_value:
                raise ILEException(
                    f'The property "{prop}" must be less than or equal to '
                    f'{self.max_value} but is {data}'
                )
        elif isinstance(data, MinMax):
            if self.min_value is not None:
                if data.min < self.min_value or data.max < self.min_value:
                    raise ILEException(
                        f'The property "{prop}" must have min and max values '
                        f'that are greater than or equal to {self.min_value} '
                        f'but is {data}'
                    )
            if self.max_value is not None and data.max > self.max_value:
                if data.min > self.max_value or data.max > self.max_value:
                    raise ILEException(
                        f'The property "{prop}" must have min and max values '
                        f'that are less than or equal to {self.max_value} '
                        f'but is {data}'
                    )
        elif isinstance(data, (VectorFloatConfig, VectorIntConfig)):
            for key, value in [('x', data.x), ('y', data.y), ('z', data.z)]:
                self.validate(f'{prop}.{key}', value)
        elif not isinstance(data, list):
            raise ILEException(
                f'The property "{prop}" must be a single number, list of '
                f'numbers, or MinMax, but is a {type(data).__name__}'
            )
        return True


@dataclass
class ValidateOptions(ValidateNested):
    """Validate that the given data is one from a list of specific options,
    or is null."""

    options: List[Any] = None

    # Override
    def _validate_prop(self, prop: str, data: Any) -> bool:
        if not self.options:
            raise Exception('ValidateOptions must have one or more options')
        if data is None:
            return True
        for data_item in (data if isinstance(data, list) else [data]):
            if data_item not in self.options:
                raise ILEException(
                    f'The property "{prop}" must be one of the following: '
                    f'{", ".join(self.options)}'
                )
        return True


@dataclass
class ValidateOr(ILEValidator):
    """Validate that one of multiple given validators pass."""

    validators: List[ILEValidator] = None

    # Override
    def _validate_prop(self, prop: str, data: Any) -> bool:
        if not self.validators:
            raise Exception('ValidateOr must have one or more validators')
        exceptions = []
        for validator in self.validators:
            try:
                # Return on the first passed validation.
                if validator.validate(prop, data):
                    return True
            except Exception as e:
                exceptions.append(str(e))
        # If this hasn't returned yet, none of the validators passed.
        raise ILEException(
            f'The following configured property must pass one validation:'
            f'{NEWLINE}{prop}: {data}{exceptions_to_text(exceptions)}'
        )


@dataclass
class ValidateSpecific(ILEValidator):
    """Validate that the given data is a specific type, or is null. The given
    data CANNOT be a list of that type."""

    typing: Type = None

    # Override
    def _validate_prop(self, prop: str, data: Any) -> bool:
        if not self.typing:
            raise Exception('ValidateSpecific must have a typing')
        if (data is not None) and (not isinstance(data, self.typing)):
            raise ILEException(
                f'The property "{prop}" must be a {self.typing.__name__} '
                f'or null but is a {type(data).__name__}'
            )
        return True
