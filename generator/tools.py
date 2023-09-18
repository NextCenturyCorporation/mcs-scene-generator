import copy
import random
import uuid
from enum import Enum
from types import SimpleNamespace
from typing import Tuple

from generator import materials
from generator.base_objects import (
    ALL_LARGE_BLOCK_TOOLS,
    LARGE_BLOCK_NOVEL_TOOLS_TO_DIMENSIONS,
    LARGE_BLOCK_TOOLS_TO_DIMENSIONS
)
from generator.objects import SceneObject
from generator.structures import create_interior_wall

from .geometry import (
    PERFORMER_HALF_WIDTH,
    ObjectBounds,
    create_bounds,
    rotate_point_around_origin
)
from .materials import MaterialTuple

MAX_TOOL_LENGTH = 9
USEFUL_LENGTH_MIN = 4

# Hooked Tool
HOOKED_TOOL_BUFFER = 2

# Tool Choice
MIN_TOOL_CHOICE_X_DIMENSION = 20
MIN_LAVA_ISLAND_LONG_ROOM_DIMENSION_LENGTH = 13
MIN_LAVA_ISLAND_SHORT_ROOM_DIMENSION_LENGTH = 7

TOOL_HEIGHT = 0.3
TOOL_TEMPLATE = {
    'id': 'tool_',
    'type': None,
    'materials': ['UnityAssetStore/YughuesFreeMetalMaterials/Materials/M_YFMM_13'],  # noqa: E501
    'debug': {
        'info': []
    },
    'shows': [{
        'stepBegin': 0,
        'position': {
            'x': 0,
            'y': TOOL_HEIGHT / 2.0,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'scale': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}


# broken tool
BROKEN_TOOL_VERTICAL_SEPARATION = 1.35
BROKEN_TOOL_HORIZONTAL_SEPARATION_MIN = 0.75
BROKEN_TOOL_HORIZONTAL_SEPARATION_MAX = 1.5

# inaccessible tool
INACCESSIBLE_TOOL_BLOCKING_WALL_HEIGHT = 0.25
INACCESSIBLE_TOOL_BLOCKING_WALL_WIDTH = 0.1
INACCESSIBLE_TOOL_BLOCKING_WALL_MINIMUM_SEPARATION = 0.5


class ImprobableToolOption(str, Enum):
    NO_TOOL = 'no_tool'
    TOO_SHORT_TOOL = 'too_short'
    BROKEN_TOOL = 'broken'
    INACCESSIBLE_TOOL = 'inaccessible'
    INACCESSIBLE_DIAGONAL = 'inaccessible_diagonal'
    INACCESSIBLE_ROTATED = 'inaccessible_rotated'
    INACCESSIBLE_MISALIGNED = 'inaccessible_misaligned'


TOOL_TYPES = SimpleNamespace(
    RECT="rectangular",
    HOOKED="hooked",
    BROKEN="broken",
    SMALL="small",
    INACCESSIBLE="inaccessible",
    INACCESSIBLE_DIAGONAL="inaccessible_diagonal",
    INACCESSIBLE_ROTATED="inaccessible_rotated",
    INACCESSIBLE_MISALIGNED="inaccessible_misaligned",
    ISOSCELES="isosceles",
    NO_TOOL="no_tool"
)


def get_tool_shape(
    tool_length: float,
    tool_category: TOOL_TYPES,
    tool_width: float = None
) -> str:
    """Returns the tool shape (object type) matching the given arguments, or
    None if no such tool shape exists. Both tool_length and/or tool_width can
    be None to randomly choose from any matching tool shapes."""
    if tool_category == TOOL_TYPES.NO_TOOL:
        return None
    if tool_category in [TOOL_TYPES.SMALL, TOOL_TYPES.BROKEN]:
        # Tool length must be 1 for SMALL and BROKEN tools.
        tool_length = 1

    tools = []
    for tool, (width, length) in LARGE_BLOCK_TOOLS_TO_DIMENSIONS.items():
        if tool_category == TOOL_TYPES.HOOKED:
            if 'hooked' not in tool:
                continue
        elif tool_category == TOOL_TYPES.ISOSCELES:
            if 'isosceles' not in tool:
                continue
        elif tool_category in [TOOL_TYPES.SMALL, TOOL_TYPES.BROKEN]:
            if 'rect' not in tool or length != 1:
                continue
        else:
            # Default to RECT tools (including for INACCESSIBLE type).
            if 'rect' not in tool or length < USEFUL_LENGTH_MIN:
                continue
        if tool_length and tool_length != length:
            continue
        # For asymmetric tools, use the width from the tool string rather than
        # from the actual dimensions.
        if tool_category in [TOOL_TYPES.HOOKED, TOOL_TYPES.ISOSCELES]:
            width = get_tool_width_from_type(tool)
        if tool_width and tool_width != width:
            continue
        tools.append(tool)

    return random.choice(tools) if tools else None


def get_tool_width_from_type(tool_type: str) -> float:
    # Assume tool type format: "tool_whatever_A_AA_x_B_BB"
    index = len(tool_type) - 11
    width = float(tool_type[index:(index + 4)].replace('_', '.'))
    return width


def finalize_tool(
    tool: SceneObject,
    width: float,
    length: float,
    bounds: ObjectBounds = None,
    material_tuple: MaterialTuple = None
) -> SceneObject:
    """Finalize and return the given tool."""
    tool['id'] += str(uuid.uuid4())
    tool['materials'] = [material_tuple.material]
    tool["debug"]["color"] = material_tuple.color
    tool['debug']['dimensions'] = {
        'x': width,
        'y': TOOL_HEIGHT,
        'z': length
    }
    colors = material_tuple.color
    tool['shows'][0]['boundingBox'] = bounds or create_bounds(
        dimensions=tool['debug']['dimensions'],
        offset={'x': 0, 'y': 0, 'z': 0},
        position=tool['shows'][0]['position'],
        rotation=tool['shows'][0]['rotation'],
        standing_y=(TOOL_HEIGHT * 0.5)
    )
    tool['debug']['info'] = colors + ['tool'] + [
        f'{color} tool' for color in colors
    ] + [f'{" ".join(colors)} tool']
    return tool


def create_tool(
    object_type: str,
    position_x: float = 0,
    position_z: float = 0,
    rotation_y: float = 0,
    bounds: ObjectBounds = None,
    material_tuple: MaterialTuple = materials.TOOL_MATERIALS[0]
) -> SceneObject:
    """Create and return an instance of a tool."""
    tool = SceneObject(copy.deepcopy(TOOL_TEMPLATE))
    tool['type'] = object_type
    tool['shows'][0]['position']['x'] = position_x
    tool['shows'][0]['position']['z'] = position_z
    tool['shows'][0]['rotation']['y'] = rotation_y
    dimensions = LARGE_BLOCK_TOOLS_TO_DIMENSIONS.get(object_type)
    if not dimensions:
        raise Exception(f'Tool object type must be in {ALL_LARGE_BLOCK_TOOLS}')
    tool = finalize_tool(
        tool,
        dimensions[0],
        dimensions[1],
        bounds,
        material_tuple
    )
    return tool


def get_novel_tool_shape(tool_length):
    tools = []
    tools = [
        tool
        for tool, (_, length) in LARGE_BLOCK_NOVEL_TOOLS_TO_DIMENSIONS.items()
        if (length == tool_length)
    ]
    return random.choice(tools)


def get_scene_tool_length(scene):
    for obj in scene.objects:
        if 'tool' in obj['type']:
            return float(obj['type'][-4:].replace("_", "."))


def get_too_small_tool():
    tools = [
        tool
        for tool, (_, length) in LARGE_BLOCK_TOOLS_TO_DIMENSIONS.items()
        if tool.startswith('tool_rect') and length < USEFUL_LENGTH_MIN
    ]
    return random.choice(tools)


def get_tool_choice_tool_object(scene, is_valid):
    for obj in scene.objects:
        if 'tool' in obj['type'] and obj['shows'][0]['position']['x'] >= 0 \
                and is_valid:
            return obj
        if 'tool' in obj['type'] and obj['shows'][0]['position']['x'] < 0 \
                and not is_valid:
            return obj


def change_obj_material(obj, material):
    obj['materials'] = [material[0]]
    obj['debug']['color'] = material[1]

    obj['debug']['info'] = list(map(lambda x: str.replace(
        x,
        "grey",
        material[1][0]),
        obj['debug']['info']))
    return obj


def create_broken_tool(
    object_type: str,
    direction: str,
    width_position: float,
    max_broken_tool_length_pos: float,
    min_broken_tool_length_pos: float,
    rotation_for_entire_tool: float,
    length: int,
    material_tuple: MaterialTuple = materials.TOOL_MATERIALS[0]
) -> SceneObject:
    """Create and return an instance of a broken tool."""
    tools_before_rotation = []
    final_tools = []
    current_pos = max_broken_tool_length_pos  # start at lava edge
    for _ in range(length):
        tool = SceneObject(copy.deepcopy(TOOL_TEMPLATE))
        tool['type'] = object_type
        tool['shows'][0]['position']['x'] = \
            (width_position + round(random.uniform(
                BROKEN_TOOL_HORIZONTAL_SEPARATION_MIN,
                BROKEN_TOOL_HORIZONTAL_SEPARATION_MAX), 2) *
             random.choice([-1, 1]) if direction == 'z' else current_pos)
        tool['shows'][0]['position']['z'] = \
            (width_position + round(random.uniform(
                BROKEN_TOOL_HORIZONTAL_SEPARATION_MIN,
                BROKEN_TOOL_HORIZONTAL_SEPARATION_MAX), 2) *
             random.choice([-1, 1]) if direction == 'x' else current_pos)
        tool['shows'][0]['rotation']['y'] = random.randint(0, 359)
        dimensions = LARGE_BLOCK_TOOLS_TO_DIMENSIONS.get(object_type)
        if not dimensions:
            raise Exception(
                f'Tool object type must be in {ALL_LARGE_BLOCK_TOOLS}')
        temp_tool = copy.deepcopy(tool)
        tools_before_rotation.append(temp_tool)
        current_pos -= BROKEN_TOOL_VERTICAL_SEPARATION
    center_of_tool = (max_broken_tool_length_pos +
                      min_broken_tool_length_pos) / 2
    for tool in tools_before_rotation:
        tool_pos = tool['shows'][0]['position']
        (x, z) = rotate_point_around_origin(
            origin_x=width_position if direction == 'z' else
            center_of_tool,
            origin_z=width_position if direction == 'x' else
            center_of_tool,
            point_x=tool_pos['x'],
            point_z=tool_pos['z'],
            rotation=rotation_for_entire_tool)
        tool_pos['x'] = round(x, 2)
        tool_pos['z'] = round(z, 2)
        tool = finalize_tool(
            tool,
            dimensions[0],
            dimensions[1],
            bounds=None,
            material_tuple=material_tuple
        )
        final_tools.append(tool)
    return final_tools


def create_inaccessible_tool(
    tool_type: str,
    long_direction: str,
    short_direction: str,
    original_short_position: float,
    original_long_position: float,
    tool_horizontal_offset: float,
    tool_offset_backward_from_lava: float,
    blocking_wall_horizontal_offset: float,
    tool_rotation_y: int,
    room_dimension_x: float,
    room_dimension_z: float,
    blocking_wall_material: MaterialTuple,
    bounds: ObjectBounds = None,
    material_tuple: MaterialTuple = materials.TOOL_MATERIALS[0]
) -> Tuple[SceneObject, SceneObject, str, float, float]:
    """
    Create and return an instance of an inaccessible tool and its blocking wall
    - `tool_type` (string): The type of tool
    - `long_direction` (string): The direction to tool extends to reach
    the target.
    - `short_direction` (string): The direction of the tool width
    - `original_short_position` (float): The original position of the tool
    that is centered with the target.
    - `original_long_position` (float): The original position of the tool that
    is shifted to the edge of the lava pool.
    - `tool_horizontal_offset` (float): The left and right offset the tool
    should be moved from the blocking wall position.
    - `tool_offset_backwards_from_lava` (float): The offset away from the
    lava pool the tool should move from its original position.
    - `blocking_wall_separation` (float): The separation from the tool the
    blocking wall should have. Negative numbers will be on left side, positive
    will be on right. The minimum separation should always be greater than or
    equal to 0.5 or less than or equal to -0.5.
    - `tool_rotation_y` (float): The rotation of the tool.
    - `room_dimension_x` (float): X Room dimension.
    - `room_dimension_z` (float): Z Room dimension.
    - `blocking_wall_material` (MaterialTyple): Material for the blocking wall.
    - `bounds` (ObjectBounds): Object Bounds. Default: None
    """
    # Make sure the blocking wall separation is valid
    if abs(blocking_wall_horizontal_offset) < \
            INACCESSIBLE_TOOL_BLOCKING_WALL_MINIMUM_SEPARATION:
        raise Exception(
            "The minimum separation of the inaccessible tool blocking "
            "wall should always be greater than or equal to "
            f"{INACCESSIBLE_TOOL_BLOCKING_WALL_MINIMUM_SEPARATION} or "
            f"less than or equal to "
            f"-{INACCESSIBLE_TOOL_BLOCKING_WALL_MINIMUM_SEPARATION}")

    """
    short direction is the axis of width when the tool is
    aligned with the target. Left right directions:
    For 'x' short direction when the tool long direction is on the z axis
    ------------------------
    |        (z+)          |
    |        front         |
    |(x-) left * right (x+)|
    |        back          |
    |        (z-)          |
    ------------------------

    For 'z' short direction the tool long direction is on the x axis
    everything is rotated clockwise ⟳ 90
    ------------------------
    |        (z+)          |
    |        left          |
    |(x-) back * front (x+)|
    |        right         |
    |        (z-)          |
    ------------------------
    """
    # Wall creation
    # Create a straight wall positioned vertically across the room
    # If z short direction reverse separation direction because left is now
    # z 'positive' axis instead of x 'negative' axis
    original_offset = blocking_wall_horizontal_offset
    if short_direction == 'z':
        blocking_wall_horizontal_offset *= -1
    blocking_wall_horizontal_offset = \
        original_short_position + blocking_wall_horizontal_offset
    length = room_dimension_z if short_direction == 'x' else room_dimension_x
    wall_rotation = 0 if short_direction == 'x' else 90
    x = blocking_wall_horizontal_offset if short_direction == 'x' else 0
    z = blocking_wall_horizontal_offset if short_direction == 'z' else 0
    horizontal_pos = x if short_direction == 'x' else z
    wall = create_interior_wall(
        position_x=x,
        position_z=z,
        rotation_y=wall_rotation,
        width=INACCESSIBLE_TOOL_BLOCKING_WALL_WIDTH,
        height=INACCESSIBLE_TOOL_BLOCKING_WALL_HEIGHT,
        material_tuple=blocking_wall_material,
        position_y_modifier=0,
        thickness=length
    )
    blocking_wall_pos_cutoff = (
        horizontal_pos +
        (INACCESSIBLE_TOOL_BLOCKING_WALL_WIDTH + PERFORMER_HALF_WIDTH) *
        (-1 if blocking_wall_horizontal_offset > 0 else 1))
    room_wall_pos_cutoff = (
        (room_dimension_x / 2 - PERFORMER_HALF_WIDTH) *
        (-1 if original_offset > 0 else 1) *
        (-1 if long_direction == 'x' else 1))

    adjusted_offset_x = 0
    adjusted_offset_z = 0
    base_x = wall['shows'][0]['position']['x']
    base_z = wall['shows'][0]['position']['z']
    # Make the tool twice, the first time figure out where its bounds are
    # after its been rotated.
    # Calculate the difference from its maximum or minimum bounds to the edge
    # of the wall and then shift the tool so its aligned perfectly to wall edge
    # Then apply the tool horizontal offset after so that the closet edge
    # of the tool is the correct horizontal offset away rather than the
    # the tool center.
    for _ in range(2):
        # Tool creation
        tool = SceneObject(copy.deepcopy(TOOL_TEMPLATE))
        tool['type'] = tool_type
        x = (
            ((base_x + tool_horizontal_offset) if short_direction == 'x' else
             (original_long_position - tool_offset_backward_from_lava)) +
            adjusted_offset_x
        )
        z = (
            ((base_z - tool_horizontal_offset) if short_direction == 'z' else
             (original_long_position - tool_offset_backward_from_lava)) -
            adjusted_offset_z
        )
        tool['shows'][0]['position']['x'] = x
        tool['shows'][0]['position']['z'] = z
        tool['shows'][0]['rotation']['y'] = tool_rotation_y
        dimensions = LARGE_BLOCK_TOOLS_TO_DIMENSIONS.get(tool_type)
        if not dimensions:
            raise Exception(
                f'Tool object type must be in {ALL_LARGE_BLOCK_TOOLS}')
        # Create the tool
        tool = finalize_tool(
            tool,
            dimensions[0],
            dimensions[1],
            bounds,
            material_tuple
        )
        tool_bounds = tool['shows'][0]['boundingBox'].box_xz
        # Maximum bounds and minimum bounds of tool in short direction
        maximum_bound = round(max(getattr(pos, short_direction)
                                  for pos in tool_bounds), 2)
        minimum_bound = round(min(getattr(pos, short_direction)
                                  for pos in tool_bounds), 2)
        cutoff = (wall['shows'][0][
            'position']['x' if short_direction == 'x' else 'z'] -
            (INACCESSIBLE_TOOL_BLOCKING_WALL_WIDTH *
             (1 if original_offset > 0 else -1) *
             (1 if long_direction == 'x' else -1)))
        if short_direction == 'x':
            difference = cutoff - \
                (maximum_bound if original_offset < 0 else minimum_bound)
            adjusted_offset_x += difference + tool_horizontal_offset
            adjusted_offset_z = 0
        else:
            difference = cutoff - \
                (maximum_bound if original_offset > 0 else minimum_bound)
            adjusted_offset_z -= difference - tool_horizontal_offset
            adjusted_offset_x = 0

    """
    Simple example of what we should have now.
    This example is with a negative blocking wall separation and
    tool long direction on the z axis, short direction on x axis.
    P = Performer
    T = Target
    * = Lava
    C1 = (cutoff 1) blocking_wall_pos_cutoff
    C2 = (cutoff 2) room_wall_pos_cutoff
    x = x wall
    z = z wall
    |--------(z+)-------|
    |         |B|  ***  |
    |         |l|  *T*  |
    (x-) |t|  |o|  ***  (x+)
    |    |o|  |c|       |
    |    |o|  |k|   P   |
    |    |l|  |k|       |
    |--------(z-)-------|
                [C1---C2]
    """
    return (tool, wall, short_direction, blocking_wall_pos_cutoff,
            room_wall_pos_cutoff)
