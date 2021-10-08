import random
from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    List,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from generator import MaterialTuple
from generator.materials import find_colors

TRACE = 5


class ILEException(Exception):
    def __init__(self, message: str = ''):
        super().__init__(message)


class ILEDelayException(ILEException):
    """Exception to indicate that the current action may be able to be
    performed after another component completes its actions."""
    ...


class ILEConfigurationException(Exception):
    """Configuration exceptions should be thrown when the ILE configuration
    file has been configured in a way that cannot be processed and no retries
    are necessary.

    For example, if a goal target is required, but no goal target has been
    configured, the ILE Scene Generator should fail with this exception.
    """

    def __init__(self, message: str = ''):
        super().__init__(message)


class ConverterClass(ABC):
    """Used when a class in the config file needs to be changed to another
    when chosen.  An example would be VectorFloatConfig converted to
    Vector3D."""

    @abstractmethod
    def convert_value(self) -> Any:
        """Return an instance of this object with its converted class."""
        return None


def choose_random(data: Any, data_type: Type = None) -> Any:
    """Return the data, if it's a single choice; a single element from the
    data, if it's a list; or a value within a numeric range, if it's a MinMax.
    The given type is used to handle specific edge cases."""
    output_typing: Type = (
        get_args(data_type)[0] if get_origin(data_type) == Union else data_type
    )
    choice = data

    # If the data's a list, choose a random item from the list.
    if isinstance(choice, list):
        # Don't return the choice; let this function continue to act upon it.
        choice = random.choice(choice)

    # If the data's a ConverterClass, let it handle its own conversion.
    if isinstance(choice, ConverterClass):
        return choice.convert_value()

    # If the data's not None and not a primitive type, assume it's a class.
    if choice and not isinstance(choice, (dict, float, int, str, tuple)):
        data_class = type(choice)
        data_typings: Dict[str, Type] = get_type_hints(choice.__class__)
        data_choices: Dict[str, Any] = {}
        # Choose random values for each nested property in the class.
        for prop, typing in data_typings.items():
            data_choices[prop] = choose_random(getattr(choice, prop), typing)
        return data_class(**data_choices)

    # If the typing is MaterialTuple, assume the data's either a str or tuple.
    if output_typing == MaterialTuple:
        # TODO MCS-813 Change tuple to MaterialTuple
        return (
            MaterialTuple(choice[0], choice[1]) if isinstance(choice, tuple)
            else MaterialTuple(choice, find_colors(choice))
        )

    return choice


def find_bounds(objects: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Calculate and return the bounds for all the given objects."""
    return [instance['shows'][0]['boundingBox'] for instance in objects]
