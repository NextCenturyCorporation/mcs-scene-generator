import logging
from dataclasses import dataclass
from typing import List, Union

from ideal_learning_env.defs import ILEConfigurationException, ILEException
from ideal_learning_env.numerics import MinMaxInt

logger = logging.getLogger(__name__)


@dataclass
class StepBeginEnd():
    """
    Contains a step range for a specific event.

    - `begin` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list
    of MinMaxInt dicts):
    The step where the performer agent starts being frozen
    and can only use the `"Pass"` action. For example, if 1, the performer
    agent must pass immediately at the start of the scene.  This is an
    inclusive limit.
    - `end` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list
    of MinMaxInt dicts):
    The step where the performer agent ends being frozen and can resume
    using actions besides `"Pass"`.  Therefore, this is an exclusive limit.
    """
    begin: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    end: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None


def add_freezes(goal: dict, freezes: List[StepBeginEnd]):
    goal['action_list'] = goal.get('action_list', [])
    al = goal['action_list']
    limit = 1
    for f in freezes:
        f.begin = 1 if f.begin is None else f.begin
        if f.end is None:
            if goal['last_step'] is None:
                raise ILEConfigurationException(
                    "Configuration error.  A freeze without an 'end' "
                    "requires 'last_step' to be set.")
            else:
                # Add one so we include the last step.  End is exclusive.
                f.end = goal['last_step'] + 1
        if (limit > f.begin):
            raise ILEException(f"Freezes overlapped at {limit}")
        if f.begin >= f.end:
            raise ILEException(
                f"Freezes has begin >= end ({f.begin} >= {f.end})")
        num_free = f.begin - limit
        num_limited = f.end - f.begin
        al += ([[]] * (num_free))
        al += ([['Pass']] * (num_limited))
        limit = f.end
