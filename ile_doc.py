#!/usr/bin/env python3

import re
from typing import List, Type, get_args, get_origin, get_type_hints

import pdoc

from ile import ILE_COMPONENTS

ILE_SIMPLE_CONFIG = 'ile_configs/auto_generated_null_template.yaml'

ILE_API_FILENAME = 'ILE_API.md'
ILE_API_HEADER = """# ILE API

[How to Use the ILE](./README.md)

#### Table of Content
- [Lists](#Lists)
- [Classes](#Classes)
- [Options](#Options)

## Lists

- [Agent settings](https://nextcenturycorporation.github.io/MCS/schema.html#agent-settings)
- [Interactable shapes](https://nextcenturycorporation.github.io/MCS/schema.html#interactable-objects)
- [Materials](https://nextcenturycorporation.github.io/MCS/schema.html#material-list)
- [Tool shapes](https://nextcenturycorporation.github.io/MCS/schema.html#tool-objects)

## Classes

Some [configurable ILE options](#Options) use the following classes
(represented as dicts in the YAML):

"""
ILE_API_MIDDLE = """
## Options

You may set the following options in your ILE (YAML) config file:

"""

ILE_COMPONENT_NAME = 'ideal_learning_env.components.ILEComponent'

REGEX_TO_MATCH_SIMPLE_EXAMPLE = "Simple Example:\n```\n\s*?((.|\n)*?)\n\s*?```"  # noqa: E501, W605


def retrieve_all_types(typing: Type) -> List[Type]:
    """Return a list containing the given type (and all its non-primitive
    properties, if it's a class), or, if the type has nested types (because
    it's a list, union, etc.), return all those types."""
    types: List[Type] = []
    # If not a list or union...
    if not get_origin(typing):
        if not isinstance(typing, (dict, float, int, str, tuple)):
            for nested in get_type_hints(typing).values():
                types.extend(retrieve_all_types(nested))
            return [typing] + types
        # Ignore all primitive types.
        return []
    # Else if a list or union...
    for nested in list(get_args(typing)):
        types.extend(retrieve_all_types(nested))
    return types


def main():
    """Auto-generate the ILE API markdown doc and example YAML config file."""
    # Gather all of the ILE classes that are used in config properties.
    types = []
    for component in ILE_COMPONENTS:
        for _, typing in get_type_hints(component).items():
            types.extend(retrieve_all_types(typing))
    types = [
        typing for typing in set(types)
        if typing.__module__.startswith('ideal_learning_env.')
    ]
    # Save all of the names of the ILE classes from the types.
    names = [f'{typing.__module__}.{typing.__name__}' for typing in types]
    # Gather all of the files containing ILE components or types.
    files = list(set([cls.__module__ for cls in ILE_COMPONENTS] + [
        typing.__module__ for typing in types
    ]))
    # Read the docstrings from each ILE class with pdoc.
    context = pdoc.Context()
    modules = [pdoc.Module(element, context=context) for element in files]
    pdoc.link_inheritance(context)
    # Retrieve a variable object for each class variable (ILE config file
    # property) in each ILE module that contains the variable's docstring.
    variables = []
    # Retrieve a class object for each ILE class used in config properties.
    configs = []
    for mod in modules:
        for cls in mod.classes():
            name = f'{cls.module.name}.{cls.name}'
            ancestors = [ancestor.name for ancestor in cls.mro()]
            # Ignore all helper classes defined in component files...
            if ILE_COMPONENT_NAME in ancestors:
                # Ignore class variables with UPPER_CASE names because they're
                # probably static class variables, not config variables.
                variables.extend([
                    var for var in cls.class_variables()
                    if var.name.islower()
                ])
            # ...unless those classes are used as config properties.
            if name in names:
                configs.extend([cls])
    # Sort the variables from all ILE components together, since users don't
    # need to know which specific config variables belong to which components.
    variables.sort(key=lambda x: x.name)
    configs.sort(key=lambda x: x.name)
    # Auto-generate and save the ILE API markdown doc.
    with open(ILE_API_FILENAME, 'w') as ile_api:
        ile_api.write(ILE_API_HEADER)
        for cls in configs:
            ile_api.write(f'#### {cls.name}\n\n{cls.docstring}\n\n')
        ile_api.write(ILE_API_MIDDLE)
        for var in variables:
            ile_api.write(f'#### {var.name}\n\n{var.docstring}\n\n')
    # Auto-generate and save the example YAML configuration files.
    with open(ILE_SIMPLE_CONFIG, 'w') as ile_config:
        for var in variables:
            match = re.search(REGEX_TO_MATCH_SIMPLE_EXAMPLE, var.docstring)
            if match:
                ile_config.write(f'{match.group(1)}\n')


if __name__ == '__main__':
    main()
