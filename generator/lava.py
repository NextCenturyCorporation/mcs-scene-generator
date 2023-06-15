import random
from dataclasses import dataclass

DEFAULT_LAVA_SEPARATION_FROM_WALL = 3
# Max lava width should be 6 for rect tools, 3 for hooked.
# (determined based on MAX_LAVA_WITH_ISLAND_WIDTH values)
MIN_LAVA_WIDTH_HOOKED_TOOL = 1
MAX_LAVA_WIDTH_HOOKED_TOOL = 3
MIN_LAVA_WIDTH = 2
MAX_LAVA_WIDTH = 6
MIN_LAVA_ISLAND_SIZE = 1
MAX_LAVA_ISLAND_SIZE = 5
MAX_LAVA_AREA_TOTAL_WIDTH = 9

# Min lava with island width should be 5
MAX_LAVA_WITH_ISLAND_WIDTH = 9
MIN_LAVA_WITH_ISLAND_WIDTH_HOOKED_TOOL = 3
MAX_LAVA_WITH_ISLAND_WIDTH_HOOKED_TOOL = 7

MIN_ISLAND_SIZE = 1
MAX_ISLAND_SIZE = 5


@dataclass
class LavaIslandSizes():
    """
    island_size is the safe area of in the center of the lava pool.
    For example: island size of 3 is a safe area of 3 x 3.
    The directional values are the widths of the lava pools
    which can be varying widths creating asymmetric pools
    """
    island_size: int = 0
    front: int = 0  # positive z axis
    rear: int = 0  # negative z axis
    left: int = 0  # negative x axis
    right: int = 0  # positive x axis


def random_lava_island(dim_x, dim_z):
    back_front_width = 0
    left_right_width = 0
    island_size = MIN_ISLAND_SIZE
    back = MIN_LAVA_WIDTH
    front = MIN_LAVA_WIDTH
    left = MIN_LAVA_WIDTH
    right = MIN_LAVA_WIDTH
    lava_widths = [back, front, left, right]

    """
    Skewed lava island widths for smaller rooms.
    Otherwise lava shifting will not work
    """
    if dim_x < 20 or dim_z < 20:
        return LavaIslandSizes(island_size, front, back, left, right)
    if dim_x < 30 or dim_z < 30:
        island_size = random.randint(MIN_ISLAND_SIZE, 3)
        for i in range(len(lava_widths)):
            lava_widths[i] = random.randint(MIN_LAVA_WIDTH, 3)
        return LavaIslandSizes(island_size, front, back, left, right)

    island_size = random.randint(MIN_ISLAND_SIZE, MAX_ISLAND_SIZE)
    back_front_width += island_size
    left_right_width += island_size
    back = random.randint(
        back,
        MAX_LAVA_AREA_TOTAL_WIDTH -
        back_front_width -
        front)
    back_front_width += back
    front = random.randint(front, MAX_LAVA_AREA_TOTAL_WIDTH - back_front_width)

    left = random.randint(
        left,
        MAX_LAVA_AREA_TOTAL_WIDTH -
        left_right_width -
        right)
    left_right_width += left
    right = random.randint(right, MAX_LAVA_AREA_TOTAL_WIDTH - left_right_width)

    return LavaIslandSizes(island_size, front, back, left, right)
