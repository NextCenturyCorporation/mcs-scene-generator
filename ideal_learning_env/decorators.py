from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints
)

from .defs import ILEException
from .validators import NEWLINE, ILEValidator, exceptions_to_text


def _validate_cast_data(prop: str, data: Any, typing: Type) -> Any:
    """Validate that the given data is one of the given types and, if so, cast
    it into that type and return it. Raise an exception if it, or any of its
    nested properties (for dicts and lists), are invalid. Works on primitives,
    lists, dicts that are cast into classes, and unions."""

    # The data can always be null (all properties are optional).
    # If you want no null nested properties, see ValidateNoNullProp.
    if data is None:
        return data

    exceptions: List[str] = []

    # Retrieve all of the typings from a Union, if needed.
    typings: List[Type] = (
        list(get_args(typing)) if get_origin(typing) == Union else [typing]
    )

    # Loop over each possible typing and try to cast the data into that type.
    for viable_typing in typings:

        # The call to get_origin will return dict for Dict typings, list for
        # List typings, etc. It will return None for all primitive typings.
        origin_typing: Type = get_origin(viable_typing)

        # Prefer to use the typing origin (like dict or list) if it's not None.
        # Use tuples for consistency.
        tupled_typing: Tuple[Type, Type] = (
            (origin_typing,) if origin_typing else
            # A float can be an int, so add int to the typing, if needed.
            ((float, int) if viable_typing == float else (viable_typing,))
        )

        # Cast the data into its corresponding Python class or dict, if needed.
        try:
            cast_data = (
                tupled_typing[0](**data) if isinstance(data, dict) else data
            )
        except TypeError:
            exceptions.append(
                f'Cannot be type {tupled_typing[0].__name__} because it has '
                f'one or more unexpected nested properties: {data}'
            )
            # Try the next typing.
            continue

        # Validate the data typing.
        if not isinstance(cast_data, tupled_typing):
            exceptions.append(
                f'Cannot be type {tupled_typing[0].__name__} because it\'s '
                f'type {type(cast_data).__name__}'
            )
            # Try the next typing.
            continue

        # A bool must be a bool (needed because bool is a subclass of int).
        if viable_typing == int and isinstance(cast_data, bool):
            exceptions.append(
                f'Cannot be type {viable_typing.__name__} because it\'s '
                f'type {type(cast_data).__name__}'
            )
            # Try the next typing.
            continue

        # String properties must not be empty.
        if viable_typing == str and cast_data == '':
            exceptions.append(
                'Cannot be just an empty string; please delete it from your ' +
                'config file or set it to null'
            )
            # Try the next typing.
            continue

        if origin_typing == list:
            # Assume a List will always have only one type like List[str]
            nested_typing: Type = get_args(viable_typing)[0]
            # Validate the typings for the list's nested items.
            return [
                _validate_cast_data(
                    f'{prop}[{index}]',
                    item,
                    nested_typing
                )
                for index, item in enumerate(cast_data)
            ]

        # Assume a Dict will always have two types like Dict[str, Any]
        nested_typing_of_dict: Type = (
            get_args(viable_typing)[1] if origin_typing == dict else None
        )

        # Use get_type_hints to retrieve a dict containing the name of each
        # property in this class and its corresponding type hint Python class.
        # The function won't work with dicts so create it manually for them.
        props_to_typings: Dict[str, Type] = (
            dict([(key, nested_typing_of_dict) for key in cast_data])
            if origin_typing == dict else get_type_hints(viable_typing)
        )

        # Validate the typings of the object's or dict's nested properties.
        # For example, verify the properties in a Dict[str, int] are ints,
        # or the x, y, and z properties in a Vector3d are floats.
        # Primitive classes like "str" won't any, so nothing will happen.
        for nested_prop, nested_typing in props_to_typings.items():
            if nested_prop.startswith('_'):
                continue
            nested_data = _validate_cast_data(
                f'{prop}.{nested_prop}',
                cast_data[nested_prop] if isinstance(cast_data, dict) else
                getattr(cast_data, nested_prop),
                nested_typing
            )
            if isinstance(cast_data, dict):
                cast_data[nested_prop] = nested_data
            else:
                setattr(cast_data, nested_prop, nested_data)

        return cast_data

    raise ILEException(
        f'The following configured property is an invalid type:{NEWLINE}'
        f'{prop}: {data}{exceptions_to_text(exceptions)}'
    )


def ile_config_setter(validator: ILEValidator = None) -> Callable:
    """TODO"""

    def decoration_function(func: Callable) -> Callable:
        if not func.__name__.startswith('set_'):
            raise Exception(
                f'An @ile_config_setter function\'s name must start with '
                f'"set_" but is "{func.__name__}"'
            )
        # Identify the config property name within the setter function name.
        # This property name is used in error messages.
        prop_name = func.__name__[4:]

        # The "wraps" decorator will copy the original function's docstring
        # to this function.
        @wraps(func)
        def override_function(self, data: Any):
            if not hasattr(self, prop_name):
                raise Exception(
                    f'{self.__name__} must have a "{prop_name}" attribute for '
                    f'its @ile_config_setter function "{func.__name__}"'
                )

            # The data can always be null (all properties are optional).
            if data is None:
                return func(self, None)

            # Retrieve the type hint from this property's definition.
            typing = get_type_hints(self)[prop_name]

            # Ensure that the data is the proper type and cast it to that type.
            cast_data = _validate_cast_data(prop_name, data, typing)

            if cast_data is None:
                raise Exception(
                    f'The property {prop_name} must not be cast to None; '
                    f'please investigate why an error was not raised!'
                )

            # If needed, run any extra validation on this specific property.
            if validator:
                validator.validate(prop_name, cast_data)

            # Finally, pass the cast data into the original setter function.
            return func(self, cast_data)
        return override_function
    return decoration_function
