import json
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from .components import ILEComponent
from .decorators import ile_config_setter
from .numerics import VectorFloatConfig


@dataclass
class MockClass():
    dict_prop: Dict[str, str] = None
    int_prop: int = None
    list_dict_prop: List[Dict[str, str]] = None
    list_int_prop: List[int] = None
    list_vector_prop: List[VectorFloatConfig] = None
    union_int_prop: Union[int, List[int]] = None
    union_vector_prop: Union[VectorFloatConfig, List[VectorFloatConfig]] = None
    vector_prop: VectorFloatConfig = None


class MockComponent(ILEComponent):
    """Mock ILE component for unit testing."""

    bool_prop: bool = None
    class_prop: MockClass = None
    float_prop: float = None
    int_prop: int = None
    list_bool_prop: List[bool] = None
    list_class_prop: List[MockClass] = None
    list_float_prop: List[float] = None
    list_int_prop: List[int] = None
    list_str_prop: List[str] = None
    str_prop: str = None
    union_bool_prop: Union[bool, List[bool]] = None
    union_class_prop: Union[MockClass, List[MockClass]] = None
    union_float_prop: Union[float, List[float]] = None
    union_int_prop: Union[int, List[int]] = None
    union_str_prop: Union[str, List[str]] = None

    _called_setter: Dict[str, bool] = {}

    @ile_config_setter()
    def set_bool_prop(self, data: Any) -> None:
        self._called_setter['bool_prop'] = True
        self.bool_prop = data

    @ile_config_setter()
    def set_class_prop(self, data: Any) -> None:
        self._called_setter['class_prop'] = True
        self.class_prop = data

    @ile_config_setter()
    def set_float_prop(self, data: Any) -> None:
        self._called_setter['float_prop'] = True
        self.float_prop = data

    @ile_config_setter()
    def set_int_prop(self, data: Any) -> None:
        self._called_setter['int_prop'] = True
        self.int_prop = data

    @ile_config_setter()
    def set_list_bool_prop(self, data: Any) -> None:
        self._called_setter['list_bool_prop'] = True
        self.list_bool_prop = data

    @ile_config_setter()
    def set_list_class_prop(self, data: Any) -> None:
        self._called_setter['list_class_prop'] = True
        self.list_class_prop = data

    @ile_config_setter()
    def set_list_float_prop(self, data: Any) -> None:
        self._called_setter['list_float_prop'] = True
        self.list_float_prop = data

    @ile_config_setter()
    def set_list_int_prop(self, data: Any) -> None:
        self._called_setter['list_int_prop'] = True
        self.list_int_prop = data

    @ile_config_setter()
    def set_list_str_prop(self, data: Any) -> None:
        self._called_setter['list_str_prop'] = True
        self.list_str_prop = data

    @ile_config_setter()
    def set_str_prop(self, data: Any) -> None:
        self._called_setter['str_prop'] = True
        self.str_prop = data

    @ile_config_setter()
    def set_union_bool_prop(self, data: Any) -> None:
        self._called_setter['union_bool_prop'] = True
        self.union_bool_prop = data

    @ile_config_setter()
    def set_union_class_prop(self, data: Any) -> None:
        self._called_setter['union_class_prop'] = True
        self.union_class_prop = data

    @ile_config_setter()
    def set_union_float_prop(self, data: Any) -> None:
        self._called_setter['union_float_prop'] = True
        self.union_float_prop = data

    @ile_config_setter()
    def set_union_int_prop(self, data: Any) -> None:
        self._called_setter['union_int_prop'] = True
        self.union_int_prop = data

    @ile_config_setter()
    def set_union_str_prop(self, data: Any) -> None:
        self._called_setter['union_str_prop'] = True
        self.union_str_prop = data

    def __get_scene_data(self, data: Any):
        if isinstance(data, list):
            return [self.__get_scene_data(item) for item in data]
        try:
            # Use json to ensure this returns all nested classes as dicts too.
            return json.loads(json.dumps(data, default=lambda x: vars(x)))
        except TypeError:
            return data

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        for prop, attr in vars(self).items():
            if attr is not None and not prop.startswith('_'):
                scene[prop] = self.__get_scene_data(attr)
        return scene
