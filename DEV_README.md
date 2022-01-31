# Scene Generator Developer Usage

For the main docs, please see the main [README](./README.md) file.

## Testing

Unit tests may take a few minutes to run due to their stochastic nature. Also some of the tests are not completely deterministic such as those that generate and verify that random hypercubes are within expected parameters. If you see a test fail, it may do so intermittently, but it's also useful if you can save the error log and create a new ticket. Thanks.

To run:

```
python -m pytest -vv
```

If you have a lot of extra files in this folder (scenes, images, videos, zips, etc.), the tests may take a long time to start, so you can just run:

```
python -m pytest tests/* -vv
```

If you want to ignore a subset of files by filename pattern, use `find`. For example, to ignore all test files matching starting with `ile`:

```
python -m pytest $(find tests/*.py ! -name 'ile*') -vv
```

## Linting

We are currently using [flake8](https://flake8.pycqa.org/en/latest/) and [autopep8](https://pypi.org/project/autopep8/) for linting and formatting our Python code. This is enforced within the python_api and scene_generator projects. Both are [PEP 8](https://www.python.org/dev/peps/pep-0008/) compliant (besides some inline exceptions), although we are ignoring the following rules:
- **E402**: Module level import not at top of file
- **W504**: Line break occurred after a binary operator

A full list of error codes and warnings enforced can be found [here](https://flake8.pycqa.org/en/latest/user/error-codes.html)

Both have settings so that they should run on save within Visual Studio Code [settings.json](../.vscode/settings.json) as well as on commit after running `pre-commit install` (see [.pre-commit-config.yaml](../../.pre-commit-config.yaml) and [.flake8](../../.flake8)), but can also be run on the command line:


```
flake8 --per-file-ignores="materials.py:E501"
```

and

```
autopep8 --in-place --aggressive --recursive <directory>
```

or

```
autopep8 --in-place --aggressive <file>
```

## Creating New ILE Components

The ILE uses "ILE Components" to manage specific subsets of ILE config file properties. An ILE Component reads and saves the properties from the config file that are relevant to its behavior, validates those properties, creates default values for any unassigned properties, and updates those properties in scene templates to generate scenes. To add support for new config file properties, you either need to create a new ILE Component for those properties, or extend an existing ILE Component (whatever makes the most sense within the codebase).

To create an ILE Component subclass:
1. Create a new class that extends ILEComponent (from `ideal_learning_env/components.py`). Steps 2-5 affect this new component.
2. Define each config file property as an attribute on the class with a type hint and a docstring. The type should be a primitive, a Python class, a list of primitives or Python classes, or a union of primitives, lists, and/or Python classes; please avoid using dicts if possible. The docstring should have both a "Simple Example" and an "Advanced Example" blocks of working YAML code surrounded by two sets of three backticks (see the example below). Any class attributes that are not also intended to be config file properties should be marked as protected or private (named with a leading underscore `_`).
3. Define a `set_<property_name>(self, data: Any) -> None` function for each class attribute you defined in Step 2 above with an `@ile_config_setter()` decorator (from `ideal_learning_env/decorators.py`). The function should just set your class's attribute to the given data: `self.<property_name> = data`. The decorator will automatically read the property from the config file data, validate its type, and cast it. You can run additional validation (e.g. ensure that a number is within a specific range, or that the X/Y/Z attributes of a Vector are not null), by passing an `ILEValidator` using the `validator` argument to the decorator function: `@ile_config_setter(validator=<ILEValidator()>)`.
4. Optionally (but recommended), define a `get_property_name(self)` function for each class attribute to return that variable, or a default value if it wasn't configured. Get input from the design team to decide on what the defaults should be. You can use the `choose_random` functions (from `ideal_learning_env/choosers.py`) to randomly choose single values from lists or MinMax classes.
5. Override the `update_ile_scene` function. Hopefully this is just a matter of setting the relevant properties on the scene with the output of your corresponding getter functions. Please see the [JSON schema](https://nextcenturycorporation.github.io/MCS/schema.html) for details on all of the scene file properties.
6. Add your new class to the list of `ILE_COMPONENTS` in `ile.py`
7. Add your new properties to a config file and run the ILE to test your component.
8. Create some unit tests for your new class and run the unit test suite.
9. When you commit your new class, the API doc and sample config files should automatically update with the new properties.

Example ILE Component attribute and docstring:
```python
    room_dimensions: Union[VectorIntConfig, List[VectorIntConfig]] = None
    """
    ([VectorIntConfig](#VectorIntConfig) dict, or list of VectorIntConfig
    dicts) -- The total dimensions for the room, or list of dimensions, from
    which one is chosen at random for each scene. Rooms are always rectangular
    or square. The X and Z must each be within [2, 15] and the Y must be within
    [2, 10]. The room's bounds will be [-X/2, X/2] and [-Z/2, Z/2].
    Default: random

    Simple Example:
    ```
    room_dimensions: null
    ```

    Advanced Example:
    ```
    room_dimensions:
        x: 10
        y:
            - 3
            - 4
            - 5
            - 6
        z:
            min: 5
            max: 10
    ```
    """
```

Copyright 2022 CACI
