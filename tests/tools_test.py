import pytest

from generator import ALL_LARGE_BLOCK_TOOLS, materials, tools


def test_get_tool_shape():
    # With length
    shape = tools.get_tool_shape(4, tools.TOOL_TYPES.RECT)
    assert shape in [
        'tool_rect_0_50_x_4_00',
        'tool_rect_0_75_x_4_00',
        'tool_rect_1_00_x_4_00'
    ]

    # With length and width
    shape = tools.get_tool_shape(4, tools.TOOL_TYPES.RECT, 0.5)
    assert shape == 'tool_rect_0_50_x_4_00'

    # No length
    shape = tools.get_tool_shape(None, tools.TOOL_TYPES.RECT)
    assert shape.startswith('tool_rect_')
    assert not shape.endswith('1_00')

    # Hooked tools
    shape = tools.get_tool_shape(4, tools.TOOL_TYPES.HOOKED)
    assert shape in [
        'tool_hooked_0_50_x_4_00',
        'tool_hooked_0_75_x_4_00',
        'tool_hooked_1_00_x_4_00'
    ]
    shape = tools.get_tool_shape(4, tools.TOOL_TYPES.HOOKED, 1)
    assert shape in ['tool_hooked_1_00_x_4_00']

    # Isosceles tools
    shape = tools.get_tool_shape(4, tools.TOOL_TYPES.ISOSCELES)
    assert shape in [
        'tool_isosceles_0_50_x_4_00',
        'tool_isosceles_0_75_x_4_00',
        'tool_isosceles_1_00_x_4_00'
    ]
    shape = tools.get_tool_shape(4, tools.TOOL_TYPES.ISOSCELES, 1)
    assert shape in ['tool_isosceles_1_00_x_4_00']

    # Other tools
    shape = tools.get_tool_shape(4, tools.TOOL_TYPES.SMALL)
    assert shape in [
        'tool_rect_0_50_x_1_00',
        'tool_rect_0_75_x_1_00',
        'tool_rect_1_00_x_1_00'
    ]
    shape = tools.get_tool_shape(4, tools.TOOL_TYPES.BROKEN)
    assert shape in [
        'tool_rect_0_50_x_1_00',
        'tool_rect_0_75_x_1_00',
        'tool_rect_1_00_x_1_00'
    ]
    shape = tools.get_tool_shape(4, tools.TOOL_TYPES.INACCESSIBLE)
    assert shape in [
        'tool_rect_0_50_x_4_00',
        'tool_rect_0_75_x_4_00',
        'tool_rect_1_00_x_4_00'
    ]

    shape = tools.get_tool_shape(6, tools.TOOL_TYPES.T_SHAPED)
    assert shape in [
        'tool_t_5_00_x_6_00'
    ]

    shape = tools.get_tool_shape(6, tools.TOOL_TYPES.I_SHAPED)
    assert shape in [
        'tool_i_5_00_x_6_00'
    ]

    # No matching tool shapes
    shape = tools.get_tool_shape(20, tools.TOOL_TYPES.RECT)
    assert shape is None
    shape = tools.get_tool_shape(4, tools.TOOL_TYPES.NO_TOOL)
    assert shape is None


def test_get_tool_width_from_type():
    assert tools.get_tool_width_from_type('tool_rect_0_50_x_4_00') == 0.5
    assert tools.get_tool_width_from_type('tool_rect_0_63_x_4_00') == 0.63
    assert tools.get_tool_width_from_type('tool_rect_0_75_x_4_00') == 0.75
    assert tools.get_tool_width_from_type('tool_rect_0_88_x_4_00') == 0.88
    assert tools.get_tool_width_from_type('tool_rect_1_00_x_4_00') == 1
    assert tools.get_tool_width_from_type('tool_rect_1_13_x_4_00') == 1.13
    assert tools.get_tool_width_from_type('tool_hooked_0_50_x_4_00') == 0.5
    assert tools.get_tool_width_from_type('tool_hooked_0_75_x_4_00') == 0.75
    assert tools.get_tool_width_from_type('tool_hooked_1_00_x_4_00') == 1
    assert tools.get_tool_width_from_type('tool_isosceles_0_50_x_4_00') == 0.5
    assert tools.get_tool_width_from_type('tool_isosceles_0_75_x_4_00') == 0.75
    assert tools.get_tool_width_from_type('tool_isosceles_1_00_x_4_00') == 1
    assert tools.get_tool_width_from_type('tool_t_5_00_x_6_00') == 5
    assert tools.get_tool_width_from_type('tool_i_5_00_x_6_00') == 5


def test_create_tool():
    tool_type = 'tool_rect_1_00_x_4_00'
    assert tool_type in ALL_LARGE_BLOCK_TOOLS
    tool = tools.create_tool(
        object_type=tool_type,
        position_x=1,
        position_z=2,
        rotation_y=180,
        material_tuple=materials.AZURE
    )

    assert tool['id'].startswith('tool_')
    assert tool['type'] == tool_type
    assert not tool.get('kinematic')
    assert not tool.get('structure')
    assert tool.get('moveable', True)
    assert 'mass' not in tool
    assert 'materials' in tool
    assert tool['materials'] == ['Custom/Materials/Azure']
    assert tool['debug']['info'] == [
        'azure', 'blue', 'tool', 'azure tool', 'blue tool',
        'azure blue tool'
    ]

    assert len(tool['shows']) == 1
    assert tool['shows'][0]['stepBegin'] == 0
    assert tool['shows'][0]['position'] == {'x': 1, 'y': 0.15, 'z': 2}
    assert tool['shows'][0]['rotation'] == {'x': 0, 'y': 180, 'z': 0}
    assert tool['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    tool_bounds = tool['shows'][0]['boundingBox']
    assert vars(tool_bounds.box_xz[0]) == pytest.approx(
        {'x': 0.5, 'y': 0, 'z': 0}
    )
    assert vars(tool_bounds.box_xz[1]) == pytest.approx(
        {'x': 0.5, 'y': 0, 'z': 4}
    )
    assert vars(tool_bounds.box_xz[2]) == pytest.approx(
        {'x': 1.5, 'y': 0, 'z': 4}
    )
    assert vars(tool_bounds.box_xz[3]) == pytest.approx(
        {'x': 1.5, 'y': 0, 'z': 0}
    )
    assert tool_bounds.max_y == 0.3
    assert tool_bounds.min_y == 0
