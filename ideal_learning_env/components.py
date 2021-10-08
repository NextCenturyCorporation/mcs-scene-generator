from abc import ABC, abstractmethod
from typing import Any, Dict, get_type_hints


class ILEComponent(ABC):
    """Manages a specific subset of ILE config file properties by reading and
    saving those properties from the config data, validating those properties,
    creating default values for any unassigned properties, and updating those
    properties in scene templates."""

    def __init__(self, data: Dict[str, Any]):
        # Loop over each config property in this component and call its setter
        # to initialize and validate that property using the given data.
        for prop in get_type_hints(self):
            if prop.startswith('_'):
                continue
            setter_name = f'set_{prop}'
            if not hasattr(self, setter_name):
                raise Exception(
                    f'{self.__name__} must have a "{setter_name}" function'
                )
            setter_func = getattr(self, setter_name)
            setter_func(data.get(prop))

    @abstractmethod
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """Update and return the given scene with this component's config."""
        return scene

    def get_num_delayed_actions(self) -> int:
        """Returns the number of actions the component needs to perform, but
        needed to delay.  This number cannot go up after calls to
        run_delayed_actions()."""
        return 0

    def run_delayed_actions(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """Called to execute any delayed actions and execute them if possible.
        """
        return scene
