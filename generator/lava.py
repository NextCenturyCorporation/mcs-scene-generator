import random
from dataclasses import dataclass
from typing import List

from machine_common_sense.config_manager import Vector2dInt

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


def create_square_lava_pool_points(
    point_1: Vector2dInt,
    point_2: Vector2dInt,
    cells_to_ignore: List[Vector2dInt] = []
) -> List[Vector2dInt]:
    '''
    Create square pool but works with points
    '''

    lava_squares = create_square_lava_pool(point_1, point_2, cells_to_ignore)
    if type(lava_squares) is Exception:
        new_point_1 = Vector2dInt(
            x=min(point_1.x, point_2.x),
            z=min(point_1.z, point_2.z)
        )
        new_point_2 = Vector2dInt(
            x=max(point_1.x, point_2.x),
            z=max(point_1.z, point_2.z)
        )
        lava_squares = create_square_lava_pool(
            new_point_1, new_point_2, cells_to_ignore)

    return lava_squares


def create_square_lava_pool(
    rear_left_corner: Vector2dInt,
    front_right_corner: Vector2dInt,
    cells_to_ignore: List[Vector2dInt] = []
) -> List[Vector2dInt]:
    """
    Create a square of lava that is includes the corners. cells_to_ignore
    should be an array of Vector2dInt
    """
    lava_squares = []

    if (rear_left_corner.x > front_right_corner.x):
        return Exception("The right side is further left than the left side.")
    if (rear_left_corner.z > front_right_corner.z):
        return Exception(
            "The rear side is further forward than the front side.")

    x_pos = rear_left_corner.x
    z_pos = rear_left_corner.z

    while x_pos <= front_right_corner.x:
        while z_pos <= front_right_corner.z:
            lava_squares.append(Vector2dInt(x=x_pos, z=z_pos))
            z_pos = z_pos + 1
        z_pos = rear_left_corner.z
        x_pos = x_pos + 1

    for ele in cells_to_ignore:
        lava_squares.remove(Vector2dInt(x=ele.x, z=ele.z))

    return lava_squares


def create_L_lava_pool(
    point1: Vector2dInt,
    middle_point: Vector2dInt,
    point2: Vector2dInt
) -> List[Vector2dInt]:
    lava_squares = []
    lava_squares2 = []

    lava_squares = create_square_lava_pool(point1, middle_point)
    if type(lava_squares) is Exception:
        lava_squares = create_square_lava_pool(middle_point, point1)

    lava_squares2 = create_square_lava_pool(point2, middle_point)
    if type(lava_squares2) is Exception:
        lava_squares2 = create_square_lava_pool(middle_point, point2)

    for ele in lava_squares2:
        # Skip the extra middle cell
        if ele.x == middle_point.x and ele.z == middle_point.z:
            continue
        lava_squares.append(ele)

    return lava_squares


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
