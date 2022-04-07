import random
from dataclasses import dataclass
from typing import List, Union

from machine_common_sense.config_manager import Vector3d

from .defs import ConverterClass, choose_random


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


RandomizableVectorFloat3d = Union[VectorFloatConfig, List[VectorFloatConfig]]
RandomizableInt = Union[int, MinMaxInt, List[Union[int, MinMaxInt]]]
RandomizableFloat = Union[float, MinMaxFloat, List[Union[float, MinMaxFloat]]]
