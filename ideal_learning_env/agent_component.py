import logging
import random
from typing import Any, Dict, List, Union

from generator.agents import (
    AGENT_ANIMATIONS,
    AGENT_MOVEMENT_ANIMATIONS,
    AGENT_TYPES,
)
from ideal_learning_env.agent_service import (
    DEFAULT_TEMPLATE_AGENT_MOVEMENT,
    AgentConfig,
)
from ideal_learning_env.defs import find_bounds, return_list
from ideal_learning_env.feature_creation_service import (
    FeatureCreationService,
    FeatureTypes,
)
from ideal_learning_env.numerics import MinMaxInt

from .choosers import choose_counts, choose_random
from .components import ILEComponent
from .decorators import ile_config_setter
from .validators import ValidateNumber, ValidateOptions

logger = logging.getLogger(__name__)


class SpecificAgentComponent(ILEComponent):
    specific_agents: Union[AgentConfig, List[AgentConfig]] = None
    """
     ([AgentConfig](#AgentConfig) dict, or list of
    AgentConfig dicts): One or more specific agents (with one
    or more possible variations) that will be added to each scene.

    Simple Example:
    ```
    specific_agents: null
    ```

    Advanced Example:
    ```
    specific_agents:
      num: 15
      type: [agent_male_02, agent_female_02]
      agent_settings:
        chest: 2
        eyes: 1
      position:
        x: [1, 0, -1, 0.5, -0.5]
        y: 0
        z: [1, 0, -1]
      rotation_y: [0, 10, 350]
      actions:
        - step_begin: [1, 2]
          step_end: 7
          is_loop_animation: False
          id: ['TPM_clap', 'TPM_cry']
        - step_begin: [13, 14]
          step_end: 17
          is_loop_animation: True
          id: ['TPM_clap', 'TPM_cry']
      movement:
        animation: TPF_walk
        step_begin: [2, 4]
        bounds:
          - x: 2
            z: 0
          - x: 0
            z: 2
          - x: -2
            z: 0
          - x: 0
            z: -2
        num_points: 5
        repeat: True
    ```
    """

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['type'], options=AGENT_TYPES))
    @ile_config_setter(validator=ValidateOptions(
        props=['animation'], options=AGENT_MOVEMENT_ANIMATIONS))
    @ile_config_setter(validator=ValidateOptions(
        props=['id'], options=AGENT_ANIMATIONS))
    def set_specific_agents(self, data: Any) -> None:
        self.specific_agents = data

    def get_specific_agents(self) -> List[AgentConfig]:
        return self.specific_agents

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring specific agents...')

        bounds = find_bounds(scene)
        self._delayed_templates = []
        templates = return_list(self.specific_agents)
        for template, num in choose_counts(templates):
            logger.trace(
                f'Creating {num} of configured specific agent template = '
                f'{vars(template)}'
            )
            for _ in range(num):
                FeatureCreationService.create_feature(
                    scene, FeatureTypes.AGENT, template, bounds)

        return scene


MOVEMENT_CHANCE = 0.5


class RandomAgentComponent(ILEComponent):
    num_random_agents: Union[int, MinMaxInt,
                             List[Union[int, MinMaxInt]]] = False

    """
    (int, or [MinMaxInt](#MinMaxInt) dict, or list of ints or
    [MinMaxInt](#MinMaxInt) dicts): The number of random agents to add to the
    scene.  Default: `0`

    Simple Example:
    ```
    num_random_agents: 0
    ```

    Advanced Example:
    ```
    num_random_agents:
      min: 2
      max: 4
    ```
    """

    @ile_config_setter(validator=ValidateNumber(min_value=0, null_ok=True))
    def set_num_random_agents(self, data: Any) -> None:
        self.num_random_agents = data

    def get_num_random_agents(self) -> int:
        return choose_random(self.num_random_agents) or 0

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring random agents...')

        bounds = find_bounds(scene)
        num = self.get_num_random_agents()
        logger.trace(
            f'Creating {num} of random agents'
        )
        for _ in range(num):
            template = AgentConfig()
            if random.uniform(0, 1) < MOVEMENT_CHANCE:
                config = DEFAULT_TEMPLATE_AGENT_MOVEMENT
                template.movement = [config]
            FeatureCreationService.create_feature(
                scene, FeatureTypes.AGENT, template, bounds)
        return scene
