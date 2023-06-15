import random
from dataclasses import dataclass
from typing import List, Union

from machine_common_sense.config_manager import Vector3d

from .defs import ConverterClass, choose_random, return_list


class MinMax(ConverterClass):
    """Represents a numerical range."""
    pass


@dataclass
class MinMaxFloat(MinMax):
    """A dict with float `min` and float `max` properties that represents a
    random inclusive numerical range. A float will be randomly chosen from
    within the range in each new scene.

    Example:
    ```
    min: 0.5
    max: 1.5
    ```
    """

    min: float
    max: float

    # Override
    def convert_value(self) -> float:
        return round(random.uniform(self.min, self.max), 4)


@dataclass
class MinMaxInt(MinMax):
    """A dict with int `min` and int `max` properties that represents a
    random inclusive numerical range. An int will be randomly chosen from
    within the range in each new scene.

    Example:
    ```
    min: 1
    max: 10
    ```
    """

    min: int
    max: int

    # Override
    def convert_value(self) -> int:
        return random.randint(self.min, self.max)


@dataclass
class VectorFloatConfig(ConverterClass):
    """A dict with `x`, `y`, and `z` properties (each of which are either a
    float, list of floats, or MinMaxFloat) that represents a global coordinate
    in the scene. For each list, one float will be randomly chosen from the
    list in each new scene; for each MinMaxFloat, one float will be randomly
    chosen from within the corresponding range in each new scene.

    Example:
    ```
    x:
        - -0.5
        - -0.25
        - 0
        - 0.25
        - 0.5
    y: 0.1
    z:
        min: -0.5
        max: 0.5
    ```
    """

    x: Union[float, List[float], MinMaxFloat] = None
    y: Union[float, List[float], MinMaxFloat] = None
    z: Union[float, List[float], MinMaxFloat] = None

    # Override
    def convert_value(self) -> Vector3d:
        return Vector3d(
            x=choose_random(self.x, float),
            y=choose_random(self.y, float),
            z=choose_random(self.z, float)
        )


@dataclass
class VectorIntConfig(ConverterClass):
    """A dict with `x`, `y`, and `z` properties (each of which are either an
    int, list of ints, or MinMaxInt) that represents a global coordinate
    in the scene. For each list, one int will be randomly chosen from the
    list in each new scene; for each MinMaxInt, one int will be randomly
    chosen from within the corresponding range in each new scene.

    Example:
    ```
    x:
        - -1
        - 0
        - 1
    y: 0
    z:
        min: -1
        max: 1
    ```
    """

    x: Union[int, List[int], MinMaxInt] = None
    y: Union[int, List[int], MinMaxInt] = None
    z: Union[int, List[int], MinMaxInt] = None

    # Override
    def convert_value(self) -> Vector3d:
        return Vector3d(
            x=choose_random(self.x, int),
            y=choose_random(self.y, int),
            z=choose_random(self.z, int)
        )


def retrieve_all_choices(choices: Union[int, float, List, MinMax]) -> List:
    """Returns the list of all choices for the given int, float, list, or
    MinMax configuration. Rounds all floats in expanded MinMaxFloats to one
    decimal place."""
    if isinstance(choices, list):
        outputs = []
        for choice in choices:
            outputs.extend(retrieve_all_choices(choice))
        return sorted(list(set(outputs)))
    if isinstance(choices, MinMaxInt):
        return list(range(choices.min, choices.max + 1))
    if isinstance(choices, MinMaxFloat):
        return [
            round(value / 10.0, 1) for value in
            list(range(round(choices.min * 10), round(choices.max * 10) + 1))
        ]
    return [choices]


def retrieve_all_vectors(
    vectors: List[Union[VectorIntConfig, VectorFloatConfig]]
) -> List[Vector3d]:
    """Returns the list of all possible vectors for the given vector
    configurations. Rounds all floats in expanded MinMaxFloats to one decimal
    place."""
    outputs = []
    for vector in return_list(vectors):
        x_choices = retrieve_all_choices(vector.x)
        y_choices = retrieve_all_choices(vector.y)
        z_choices = retrieve_all_choices(vector.z)
        for x_choice in x_choices:
            for y_choice in y_choices:
                for z_choice in z_choices:
                    outputs.append((x_choice, y_choice, z_choice))
    return sorted(
        [Vector3d(x=x, y=y, z=z) for x, y, z in set(outputs)],
        key=lambda x: list(vars(x).items())
    )


RandomizableVectorInt3d = Union[VectorIntConfig, List[VectorIntConfig]]
RandomizableVectorFloat3d = Union[VectorFloatConfig, List[VectorFloatConfig]]
RandomizableInt = Union[int, MinMaxInt, List[Union[int, MinMaxInt]]]
RandomizableFloat = Union[float, MinMaxFloat, List[Union[float, MinMaxFloat]]]

RandomizableVectorInt3dOrInt = Union[
    int, MinMaxInt, VectorIntConfig,
    List[Union[VectorIntConfig, int, MinMaxInt]]]
RandomizableVectorFloat3dOrFloat = Union[
    float, MinMaxFloat, VectorFloatConfig,
    List[Union[VectorFloatConfig, float, MinMaxFloat]]]
