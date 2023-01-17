import pytest
from machine_common_sense.config_manager import Vector3d

from generator import materials
from generator.base_objects import (
    ALL_LARGE_BLOCK_TOOLS,
    create_soccer_ball,
    create_specific_definition_from_base
)
from generator.geometry import MAX_TRIES, ORIGIN_LOCATION
from generator.instances import instantiate_object
from ideal_learning_env.defs import ILEDelayException, ILEException
from ideal_learning_env.numerics import (
    MinMaxFloat,
    MinMaxInt,
    VectorFloatConfig
)
from ideal_learning_env.object_services import (
    InstanceDefinitionLocationTuple,
    ObjectRepository
)
from ideal_learning_env.structural_object_service import (
    DEFAULT_MOVING_OCCLUDER_HEIGHT_MAX,
    DEFAULT_MOVING_OCCLUDER_HEIGHT_MIN,
    DEFAULT_MOVING_OCCLUDER_REPEAT_MAX,
    DEFAULT_MOVING_OCCLUDER_REPEAT_MIN,
    DEFAULT_MOVING_OCCLUDER_THICKNESS_MAX,
    DEFAULT_MOVING_OCCLUDER_THICKNESS_MIN,
    DEFAULT_MOVING_OCCLUDER_WIDTH_MAX,
    DEFAULT_MOVING_OCCLUDER_WIDTH_MIN,
    DEFAULT_OCCLUDER_ROTATION_MAX,
    DEFAULT_OCCLUDER_ROTATION_MIN,
    DOOR_MATERIAL_RESTRICTIONS,
    DROPPER_SHAPES,
    PLACER_SHAPES,
    THROWER_SHAPES,
    WALL_SIDES,
    FloorAreaConfig,
    FloorMaterialConfig,
    StructuralDoorConfig,
    StructuralDoorsCreationService,
    StructuralDropperConfig,
    StructuralDropperCreationService,
    StructuralFloorMaterialsCreationService,
    StructuralHolesCreationService,
    StructuralLavaCreationService,
    StructuralLOccluderConfig,
    StructuralLOccluderCreationService,
    StructuralMovingOccluderConfig,
    StructuralMovingOccluderCreationService,
    StructuralObjectMovementConfig,
    StructuralPlacerConfig,
    StructuralPlacersCreationService,
    StructuralPlatformConfig,
    StructuralPlatformCreationService,
    StructuralPlatformLipsConfig,
    StructuralRampConfig,
    StructuralRampCreationService,
    StructuralThrowerConfig,
    StructuralThrowerCreationService,
    StructuralToolsCreationService,
    StructuralTurntableConfig,
    StructuralTurntableCreationService,
    StructuralWallConfig,
    StructuralWallCreationService,
    ToolConfig,
    WallSide,
    is_wall_too_close
)
from tests.ile_helper import (
    prior_scene,
    prior_scene_custom_start,
    prior_scene_with_target
)


def material_tuple_group_to_string_list(group, existing_list=None):
    if existing_list is None:
        existing_list = []
    for item in group:
        if isinstance(item, list):
            existing_list += material_tuple_group_to_string_list(
                item, existing_list)
        elif isinstance(item, materials.MaterialTuple):
            existing_list.append(item.material)
        else:
            raise Exception("Not list or MaterialTuple")
    return existing_list


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()

    # Run test
    yield

    # Cleanup
    ObjectRepository.get_instance().clear()


def test_is_wall_too_close():
    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_horizontal_wall_is_far_vertically():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_horizontal_wall_is_far_horizontally():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 2, 'y': 0, 'z': 0.6},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_horizontal_wall_is_close_vertically():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0.6},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert is_wall_too_close(wall_instance)


def test_is_wall_too_close_horizontal_wall_is_close_vertically_edge_case():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 1, 'y': 0, 'z': 0.6},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert is_wall_too_close(wall_instance)


def test_is_wall_too_close_horizontal_walls_far():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    prev_wall_instance = {
        'id': 'test_prev_wall_2',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': -1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_vertical_wall_is_far_vertically():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 1, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_vertical_wall_is_far_horizontally():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0.6, 'y': 0, 'z': 2},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_vertical_wall_is_close_vertically():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0.6, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert is_wall_too_close(wall_instance)


def test_is_wall_too_close_vertical_wall_is_close_vertically_edge_case():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0.6, 'y': 0, 'z': 1},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert is_wall_too_close(wall_instance)


def test_is_wall_too_close_vertical_walls_far():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 1, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    prev_wall_instance = {
        'id': 'test_prev_wall_2',
        'shows': [{
            'position': {'x': -1, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_horizontal_t():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0.55},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_vertical_t():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0.55},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_horizontal_wall_180_is_close_vertically():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0.6},
            'rotation': {'x': 0, 'y': 180, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert is_wall_too_close(wall_instance)


def test_is_wall_too_close_vertical_wall_270_is_close_vertically():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0.6, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 270, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 90, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert is_wall_too_close(wall_instance)


def test_is_wall_too_close_identical():
    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    wall = InstanceDefinitionLocationTuple(wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(wall, 'walls')
    assert is_wall_too_close(wall_instance)


def test_is_wall_too_close_old_wall_is_diagonal_and_close():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0.6},
            'rotation': {'x': 0, 'y': 5, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_new_wall_is_diagonal_and_close():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0.6},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 5, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_both_walls_are_diagonal_and_close():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0.6},
            'rotation': {'x': 0, 'y': 5, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 5, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    # TODO Should this work (return True) in the future?
    assert not is_wall_too_close(wall_instance)


def test_is_wall_too_close_both_walls_are_diagonal_and_close_mod_180():
    prev_wall_instance = {
        'id': 'test_prev_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0.6},
            'rotation': {'x': 0, 'y': 185, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    prev_wall = InstanceDefinitionLocationTuple(prev_wall_instance, None, None)
    ObjectRepository.get_instance().add_to_labeled_objects(prev_wall, 'walls')

    wall_instance = {
        'id': 'test_wall',
        'shows': [{
            'position': {'x': 0, 'y': 0, 'z': 0},
            'rotation': {'x': 0, 'y': 5, 'z': 0},
            'scale': {'x': 1, 'y': 1, 'z': 0.1}
        }]
    }
    # TODO Should this work (return True) in the future?
    assert not is_wall_too_close(wall_instance)


def test_door_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralDoorsCreationService()
    tmp = StructuralDoorConfig(1)
    r1: StructuralDoorConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert r1.material in DOOR_MATERIAL_RESTRICTIONS
    assert -rd.x / 2.0 < r1.position.x < rd.x / 2.0
    assert r1.position.y == 0
    assert -rd.z / 2.0 < r1.position.z < rd.z / 2.0
    assert r1.rotation_y in [0, 90, 180, 270]
    assert r1.wall_material in material_tuple_group_to_string_list(
        materials.ROOM_WALL_MATERIALS)
    assert 2 <= r1.wall_scale_x <= 10
    assert 2 <= r1.wall_scale_y <= 3

    tmp2 = StructuralDoorConfig(
        num=[2, 3],
        position=VectorFloatConfig([3, 2], MinMaxFloat(0, 2), 3),
        rotation_y=[90, 180],
        wall_scale_x=[2, 2.2],
        wall_scale_y=MinMaxFloat(2.1, 2.2),
        material=["AI2-THOR/Materials/Walls/DrywallOrange",
                  "AI2-THOR/Materials/Plastics/BlackPlastic"],
        wall_material="AI2-THOR/Materials/Metals/BrushedAluminum_Blue")
    srv = StructuralDoorsCreationService()
    r2: StructuralDoorConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position.x in [2, 3]
    assert 0 <= r2.position.y <= 2
    assert r2.position.z == 3
    assert r2.rotation_y in [90, 180]
    assert r2.wall_scale_x in [2, 2.2]
    assert 2.1 <= r2.wall_scale_y <= 2.2
    assert r2.material in ["AI2-THOR/Materials/Walls/DrywallOrange",
                           "AI2-THOR/Materials/Plastics/BlackPlastic"]
    assert r2.wall_material == (
        "AI2-THOR/Materials/Metals/BrushedAluminum_Blue")


def test_dropper_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralDropperCreationService()
    tmp = StructuralDropperConfig(1)
    r1: StructuralDropperConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert 0 <= r1.drop_step <= 10
    assert -rd.x / 2.0 <= r1.position_x <= rd.x / 2.0
    assert -rd.z / 2.0 <= r1.position_z <= rd.z / 2.0
    assert r1.projectile_material is None
    assert r1.projectile_labels is None
    assert r1.projectile_scale is None
    assert r1.projectile_shape in DROPPER_SHAPES

    tmp2 = StructuralDropperConfig(
        num=[2, 3], drop_step=[3, 5], position_x=[-2, 2],
        position_z=MinMaxFloat(1, 2), projectile_scale=[1, 1.2],
        projectile_material="AI2-THOR/Materials/Plastics/BlackPlastic",
        projectile_shape=["ball", "soccer_ball"])
    srv = StructuralDropperCreationService()
    r2: StructuralDropperConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position_x in [-2, 2]
    assert 1 <= r2.position_z <= 2
    assert r2.drop_step in [3, 5]
    assert r2.projectile_shape in ["ball", "soccer_ball"]
    assert r2.projectile_scale in [1, 1.2]
    assert r2.projectile_material == "AI2-THOR/Materials/Plastics/BlackPlastic"


def test_floor_material_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralFloorMaterialsCreationService()
    tmp = FloorMaterialConfig(1)
    r1: FloorMaterialConfig = srv.reconcile(scene, tmp)

    assert r1.num == 1
    assert -rd.x / 2.0 <= r1.position_x <= rd.x / 2.0
    assert -rd.z / 2.0 <= r1.position_z <= rd.z / 2.0
    assert r1.material in material_tuple_group_to_string_list(
        materials.FLOOR_MATERIALS + materials.ROOM_WALL_MATERIALS)

    tmp2 = FloorMaterialConfig(
        [2, 3], position_x=[-2, 2],
        position_z=MinMaxFloat(1, 2),
        material="CERAMIC_MATERIALS")
    srv = StructuralFloorMaterialsCreationService()
    r2: FloorMaterialConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position_x in [-2, 2]
    assert 1 <= r2.position_z <= 2
    assert r2.material in material_tuple_group_to_string_list(
        materials.CERAMIC_MATERIALS)


def test_holes_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralHolesCreationService()
    tmp = FloorAreaConfig(1)
    r1: FloorAreaConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert -rd.x / 2.0 <= r1.position_x <= rd.x / 2.0
    assert -rd.z / 2.0 <= r1.position_z <= rd.z / 2.0

    tmp2 = FloorAreaConfig(
        [2, 3], position_x=[-2, 2],
        position_z=MinMaxFloat(1, 2))
    srv = StructuralHolesCreationService()
    r2: FloorAreaConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position_x in [-2, 2]
    assert 1 <= r2.position_z <= 2


def test_lava_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralLavaCreationService()
    tmp = FloorAreaConfig(1)
    r1: FloorAreaConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert -rd.x / 2.0 <= r1.position_x <= rd.x / 2.0
    assert -rd.z / 2.0 <= r1.position_z <= rd.z / 2.0

    tmp2 = FloorAreaConfig(
        [2, 3], position_x=[-2, 2],
        position_z=MinMaxFloat(1, 2))
    srv = StructuralLavaCreationService()
    r2: FloorAreaConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position_x in [-2, 2]
    assert 1 <= r2.position_z <= 2


def test_l_occluder_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralLOccluderCreationService()
    tmp = StructuralLOccluderConfig(1)
    r1: StructuralLOccluderConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert isinstance(r1.backwards, bool)
    assert r1.rotation_y in [0, 90, 180, 270]
    assert -rd.x / 2.0 <= r1.position.x <= rd.x / 2.0
    assert r1.position.y == 0
    assert -rd.z / 2.0 <= r1.position.z <= rd.z / 2.0
    assert 0.5 <= r1.scale_front_x <= 2
    assert 0.5 <= r1.scale_front_z <= 2
    assert 0.5 <= r1.scale_side_x <= 2
    assert 0.5 <= r1.scale_side_z <= 2
    assert 0.5 <= r1.scale_y <= 2

    tmp2 = StructuralLOccluderConfig(
        num=[2, 3], backwards=True, rotation_y=MinMaxInt(230, 260),
        scale_front_x=[1, 2], scale_front_z=[0.5, 0.75],
        scale_side_x=MinMaxFloat(0.7, 0.8), scale_side_z=MinMaxFloat(1.1, 1.2),
        scale_y=[0.9, MinMaxFloat(1.8, 1.9)],
        position=VectorFloatConfig(3, 0, [2, 3]))
    srv = StructuralLOccluderCreationService()
    r2: StructuralLOccluderConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.backwards
    assert r2.position.x == 3
    assert r2.position.y == 0
    assert r2.position.z in [2, 3]
    assert 230 <= r2.rotation_y <= 260
    assert r2.scale_front_x in [1, 2]
    assert r2.scale_front_z in [0.5, 0.75]
    assert 0.7 <= r2.scale_side_x <= 0.8
    assert 1.1 <= r2.scale_side_z <= 1.2
    assert r2.scale_y == 0.9 or (1.8 <= r2.scale_y <= 1.9)


def test_moving_occluder_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralMovingOccluderCreationService()
    tmp = StructuralMovingOccluderConfig(1)
    r1: StructuralMovingOccluderConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert r1.origin in ['top', 'top', 'top', 'top',
                         'right', 'left', 'front', 'back']
    assert -rd.x / 2.0 <= r1.position_x <= rd.x / 2.0
    assert -rd.z / 2.0 <= r1.position_z <= rd.z / 2.0

    assert (DEFAULT_MOVING_OCCLUDER_HEIGHT_MIN <=
            r1.occluder_height <= DEFAULT_MOVING_OCCLUDER_HEIGHT_MAX)
    assert (DEFAULT_MOVING_OCCLUDER_THICKNESS_MIN <=
            r1.occluder_thickness <= DEFAULT_MOVING_OCCLUDER_THICKNESS_MAX)
    assert (DEFAULT_MOVING_OCCLUDER_WIDTH_MIN <=
            r1.occluder_width <= DEFAULT_MOVING_OCCLUDER_WIDTH_MAX)
    assert (DEFAULT_OCCLUDER_ROTATION_MIN <=
            r1.rotation_y <= DEFAULT_OCCLUDER_ROTATION_MAX)
    assert (DEFAULT_MOVING_OCCLUDER_REPEAT_MIN <=
            r1.repeat_interval <= DEFAULT_MOVING_OCCLUDER_REPEAT_MAX)
    assert isinstance(r1.repeat_movement, bool)

    tmp2 = StructuralMovingOccluderConfig(
        num=[2, 3], rotation_y=MinMaxInt(230, 260),
        position_x=3, position_z=[2, 3],
        origin='left', occluder_height=[1, 2], occluder_thickness=0.1,
        occluder_width=0.5, repeat_interval=[2, 3], repeat_movement=True
    )
    srv = StructuralMovingOccluderCreationService()
    r2: StructuralMovingOccluderConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position_x == 3
    assert r2.position_z in [2, 3]
    assert 230 <= r2.rotation_y <= 260
    assert r2.origin == 'left'
    assert r2.occluder_height in [1, 2]
    assert r2.occluder_thickness == 0.1
    assert r2.occluder_width == 0.5
    assert r2.repeat_interval in [2, 3]
    assert r2.repeat_movement


def test_placer_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralPlacersCreationService()
    tmp = StructuralPlacerConfig(1)
    r1: StructuralPlacerConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert -rd.x / 2.0 <= r1.placed_object_position.x <= rd.x / 2.0
    assert -rd.z / 2.0 <= r1.placed_object_position.z <= rd.z / 2.0
    assert (0 <= r1.placed_object_rotation <= 359)
    assert r1.placed_object_shape in PLACER_SHAPES
    assert 0 <= r1.activation_step <= 10
    assert r1.end_height == 0

    tmp2 = StructuralPlacerConfig(
        num=[2, 3], placed_object_rotation=MinMaxInt(230, 260),
        placed_object_position=VectorFloatConfig(3, 0, [2, 3]),
        placed_object_scale=4, placed_object_shape='soccer_ball',
        activation_step=MinMaxInt(90, 100), end_height=[5, 6]
    )
    srv = StructuralPlacersCreationService()
    r2: StructuralPlacerConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.placed_object_position.x == 3
    assert r2.placed_object_position.y == 0
    assert r2.placed_object_position.z in [2, 3]
    assert 230 <= r2.placed_object_rotation <= 260
    assert r2.placed_object_scale == 4
    assert r2.placed_object_shape == 'soccer_ball'
    assert 90 <= r2.activation_step <= 100
    assert r2.end_height in [5, 6]

    support_platform_instance = {
        'id': 'test_platform',
        'shows': [{
            'position': {'x': 2, 'y': 0.35, 'z': 4},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 1, 'y': 0.70, 'z': 0.1}
        }]
    }
    supp_plat = InstanceDefinitionLocationTuple(
        support_platform_instance, None, None)
    tmp3 = StructuralPlacerConfig(
        num=1, placed_object_rotation=MinMaxInt(230, 260),
        placed_object_position=VectorFloatConfig(3, 0, [2, 3]),
        placed_object_scale=4, placed_object_shape='soccer_ball',
        activation_step=MinMaxInt(90, 100), end_height=[5, 6],
        end_height_relative_object_label='supp_plat'
    )
    ObjectRepository.get_instance().add_to_labeled_objects(
        supp_plat,
        'supp_plat'
    )
    srv = StructuralPlacersCreationService()
    r3: StructuralPlacerConfig = srv.reconcile(scene, tmp3)
    assert r3.num == 1
    assert r3.placed_object_position.x == 3
    assert r3.placed_object_position.y == 0
    assert r3.placed_object_position.z in [2, 3]
    assert r3.placed_object_shape in PLACER_SHAPES
    assert 0 <= r3.activation_step <= 100
    assert r3.end_height == .7

    # Test empty_placer config
    tmp4 = StructuralPlacerConfig(
        num=[2, 3], placed_object_rotation=MinMaxInt(230, 260),
        placed_object_position=VectorFloatConfig(3, 0, [2, 3]),
        placed_object_scale=4, placed_object_shape='soccer_ball',
        activation_step=MinMaxInt(90, 100), end_height=[5, 6],
        empty_placer=True
    )
    srv = StructuralPlacersCreationService()
    r4: StructuralPlacerConfig = srv.reconcile(scene, tmp4)

    assert r4.num in [2, 3]
    assert r4.end_height in [5, 6]
    assert r4.empty_placer is True

    # Test pickup_object placer config
    tmp5 = StructuralPlacerConfig(
        num=[2, 3], placed_object_rotation=MinMaxInt(230, 260),
        placed_object_position=VectorFloatConfig(3, 0, [2, 3]),
        placed_object_scale=4, placed_object_shape='soccer_ball',
        activation_step=MinMaxInt(90, 100), end_height=[5, 6],
        pickup_object=True
    )
    srv = StructuralPlacersCreationService()
    r5: StructuralPlacerConfig = srv.reconcile(scene, tmp5)

    assert r5.num in [2, 3]
    assert r5.end_height in [5, 6]
    assert r5.pickup_object is True

    # Test move_object placer config
    tmp6 = StructuralPlacerConfig(
        num=1, placed_object_rotation=MinMaxInt(230, 260),
        placed_object_position=VectorFloatConfig(3, 0, 3),
        move_object_end_position=VectorFloatConfig(-3, 0, 3),
        placed_object_scale=1, placed_object_shape='crate_1',
        activation_step=MinMaxInt(90, 100), end_height=[5, 6],
        move_object_y=2
    )
    srv = StructuralPlacersCreationService()
    r6: StructuralPlacerConfig = srv.reconcile(scene, tmp6)

    assert r6.num == 1
    assert r6.end_height in [5, 6]
    assert r6.placed_object_position == Vector3d(x=3.0, y=0.0, z=3.0)
    assert r6.move_object_end_position == Vector3d(x=-3.0, y=0.0, z=3.0)
    assert r6.move_object_y == 2


def test_placer_creation_reconcile_activate_after():
    object_repository = ObjectRepository.get_instance()
    mock_moving_object = {
        'id': 'object_1',
        'moves': [{'stepBegin': 41, 'stepEnd': 50}]
    }
    mock_idl = InstanceDefinitionLocationTuple(mock_moving_object, {}, {})
    object_repository.add_to_labeled_objects(mock_idl, 'label_1')

    scene = prior_scene()
    service = StructuralPlacersCreationService()
    config = service.reconcile(scene, StructuralPlacerConfig(
        activate_after=['label_1'],
        # This will be overridden
        activation_step=100
    ))
    assert config.activation_step == 51


def test_placer_creation_reconcile_activate_after_delay():
    scene = prior_scene()
    service = StructuralPlacersCreationService()
    with pytest.raises(ILEDelayException):
        # Error because no objects with this label are in the ObjectRepository
        service.reconcile(scene, StructuralPlacerConfig(
            activate_after=['label_1']
        ))


def test_placer_creation_reconcile_activate_on_start_or_after_after():
    object_repository = ObjectRepository.get_instance()
    mock_moving_object = {
        'id': 'object_1',
        'moves': [{'stepBegin': 1, 'stepEnd': 10}]
    }
    mock_idl = InstanceDefinitionLocationTuple(mock_moving_object, {}, {})
    object_repository.add_to_labeled_objects(mock_idl, 'label_1')

    scene = prior_scene()
    service = StructuralPlacersCreationService()
    config = service.reconcile(scene, StructuralPlacerConfig(
        activate_on_start_or_after=['label_1'],
        # This will be overridden
        activation_step=100
    ))
    assert config.activation_step == 11


def test_placer_creation_reconcile_activate_on_start_or_after_start():
    object_repository = ObjectRepository.get_instance()
    mock_moving_object = {
        'id': 'object_1',
        'moves': [{'stepBegin': 41, 'stepEnd': 50}]
    }
    mock_idl = InstanceDefinitionLocationTuple(mock_moving_object, {}, {})
    object_repository.add_to_labeled_objects(mock_idl, 'label_1')

    scene = prior_scene()
    service = StructuralPlacersCreationService()
    config = service.reconcile(scene, StructuralPlacerConfig(
        activate_on_start_or_after=['label_1'],
        # This will be overridden
        activation_step=100
    ))
    assert config.activation_step == 1


def test_placer_creation_reconcile_activate_on_start_or_after_multiple():
    object_repository = ObjectRepository.get_instance()
    mock_moving_object_1 = {
        'id': 'object_1',
        'moves': [{'stepBegin': 1, 'stepEnd': 10}]
    }
    mock_idl_1 = InstanceDefinitionLocationTuple(mock_moving_object_1, {}, {})
    object_repository.add_to_labeled_objects(mock_idl_1, 'label_1')
    mock_moving_object_2 = {
        'id': 'object_2',
        'moves': [{'stepBegin': 41, 'stepEnd': 50}]
    }
    mock_idl_2 = InstanceDefinitionLocationTuple(mock_moving_object_2, {}, {})
    object_repository.add_to_labeled_objects(mock_idl_2, 'label_2')

    scene = prior_scene()
    service = StructuralPlacersCreationService()
    config = service.reconcile(scene, StructuralPlacerConfig(
        activate_on_start_or_after=['label_1', 'label_2'],
        # This will be overridden
        activation_step=100
    ))
    assert config.activation_step == 51


def test_placer_creation_reconcile_activate_on_start_or_after_delay():
    scene = prior_scene()
    service = StructuralPlacersCreationService()
    with pytest.raises(ILEDelayException):
        # Error because no objects with this label are in the ObjectRepository
        service.reconcile(scene, StructuralPlacerConfig(
            activate_on_start_or_after=['label_1']
        ))


def test_placer_creation_reconcile_existing_object_required_true():
    object_repository = ObjectRepository.get_instance()
    definition = create_soccer_ball()
    location = {'position': {'x': 2, 'y': 0, 'z': 4}}
    instance = instantiate_object(definition, location)
    idl = InstanceDefinitionLocationTuple(instance, definition, location)
    object_repository.add_to_labeled_objects(idl, 'label_1')

    scene = prior_scene()
    service = StructuralPlacersCreationService()
    service.reconcile(scene, StructuralPlacerConfig(
        placed_object_labels='label_1',
        existing_object_required=True
    ))


def test_placer_creation_reconcile_existing_object_required_true_delay():
    scene = prior_scene()
    service = StructuralPlacersCreationService()
    with pytest.raises(ILEDelayException):
        # Error because no objects with this label are in the ObjectRepository
        service.reconcile(scene, StructuralPlacerConfig(
            placed_object_labels='label_1',
            existing_object_required=True
        ))


def test_placer_creation_reconcile_existing_object_required_false():
    scene = prior_scene()
    service = StructuralPlacersCreationService()
    service.reconcile(scene, StructuralPlacerConfig(
        placed_object_labels='label_1',
        existing_object_required=False
    ))


def test_placer_creation_reconcile_retain_position():
    object_repository = ObjectRepository.get_instance()
    definition = create_soccer_ball()
    location = {'position': {'x': 2, 'y': 0, 'z': 4}}
    instance = instantiate_object(definition, location)
    idl = InstanceDefinitionLocationTuple(instance, definition, location)
    object_repository.add_to_labeled_objects(idl, 'label_1')

    scene = prior_scene()
    service = StructuralPlacersCreationService()
    config = service.reconcile(scene, StructuralPlacerConfig(
        placed_object_labels='label_1',
        retain_position=True
    ))
    assert config.placed_object_position.x == 2
    assert config.placed_object_position.z == 4


def test_platform_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralPlatformCreationService()
    srv.bounds = []
    tmp = StructuralPlatformConfig(num=1)
    r1: StructuralPlatformConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert r1.lips == StructuralPlatformLipsConfig(False, False, False, False)
    assert r1.material in material_tuple_group_to_string_list(
        materials.ROOM_WALL_MATERIALS)
    assert -rd.x / 2.0 < r1.position.x < rd.x / 2.0
    assert r1.position.y == 0
    assert -rd.z / 2.0 < r1.position.z < rd.z / 2.0
    assert r1.rotation_y in [0, 90, 180, 270]
    assert 0.5 <= r1.scale.x <= 3
    assert 0.5 <= r1.scale.y <= 3
    assert 0.5 <= r1.scale.z <= 3
    assert r1.attached_ramps == 0
    assert r1.platform_underneath_attached_ramps == 0
    assert r1.platform_underneath is False

    tmp2 = StructuralPlatformConfig(
        num=[2, 3],
        position=VectorFloatConfig([3, 2], MinMaxFloat(0, 2), 3),
        rotation_y=[90, 180],
        material=["AI2-THOR/Materials/Walls/DrywallOrange",
                  "AI2-THOR/Materials/Plastics/BlackPlastic"],
        lips=None, scale=[1, VectorFloatConfig(1.2, 1.3, 1.4)])
    srv = StructuralPlatformCreationService()
    r2: StructuralPlatformConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position.x in [2, 3]
    assert 0 <= r2.position.y <= 2
    assert r2.position.z == 3
    assert r2.rotation_y in [90, 180]
    assert r2.material in ["AI2-THOR/Materials/Walls/DrywallOrange",
                           "AI2-THOR/Materials/Plastics/BlackPlastic"]
    assert r2.lips == StructuralPlatformLipsConfig(False, False, False, False)
    assert r2.scale in [Vector3d(x=1, y=1, z=1),
                        Vector3d(x=1.2, y=1.3, z=1.4)]
    assert r2.attached_ramps == 0
    assert r2.platform_underneath_attached_ramps == 0
    assert r2.platform_underneath is False

    tmp3 = StructuralPlatformConfig(
        num=[2, 3],
        position=VectorFloatConfig(0, None, 0),
        rotation_y=0,
        material=["AI2-THOR/Materials/Walls/DrywallOrange",
                  "AI2-THOR/Materials/Plastics/BlackPlastic"],
        lips=None, scale=1, attached_ramps=[6, 8], platform_underneath=True,
        platform_underneath_attached_ramps=MinMaxInt(2, 4))
    srv = StructuralPlatformCreationService()
    r3: StructuralPlatformConfig = srv.reconcile(scene, tmp3)

    assert r3.num in [2, 3]
    assert r3.position.x == 0
    assert 0.3 <= r3.position.y <= 3
    assert r3.position.z == 0
    assert r3.rotation_y == 0
    assert r3.material in ["AI2-THOR/Materials/Walls/DrywallOrange",
                           "AI2-THOR/Materials/Plastics/BlackPlastic"]
    assert r3.lips == StructuralPlatformLipsConfig(False, False, False, False)
    assert r3.scale == Vector3d(x=1, y=1, z=1)
    assert r3.attached_ramps in [6, 8]
    assert 2 <= r3.platform_underneath_attached_ramps <= 4
    assert r3.platform_underneath is True


def test_ramp_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralRampCreationService()
    tmp = StructuralRampConfig(1)
    r1: StructuralRampConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert r1.material in material_tuple_group_to_string_list(
        materials.ROOM_WALL_MATERIALS)
    assert -rd.x / 2.0 < r1.position.x < rd.x / 2.0
    assert r1.position.y == 0
    assert -rd.z / 2.0 < r1.position.z < rd.z / 2.0
    assert r1.rotation_y in [0, 90, 180, 270]
    assert 15 <= r1.angle <= 45
    assert r1.length < 10
    assert 0 < r1.width <= min(rd.x, rd.z) / 2.0
    assert r1.platform_underneath_attached_ramps == 0
    assert r1.platform_underneath is False

    tmp2 = StructuralRampConfig(
        num=[2, 3],
        position=VectorFloatConfig([3, 2], MinMaxFloat(0, 2), 3),
        rotation_y=[90, 180],
        material=["AI2-THOR/Materials/Walls/DrywallOrange",
                  "AI2-THOR/Materials/Plastics/BlackPlastic"],
        angle=45, width=1, length=2)
    srv = StructuralRampCreationService()
    r2: StructuralRampConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position.x in [2, 3]
    assert 0 <= r2.position.y <= 2
    assert r2.position.z == 3
    assert r2.rotation_y in [90, 180]
    assert r2.material in ["AI2-THOR/Materials/Walls/DrywallOrange",
                           "AI2-THOR/Materials/Plastics/BlackPlastic"]
    assert r2.angle == 45
    assert r2.width == 1
    assert r2.length == 2
    assert r2.platform_underneath_attached_ramps == 0
    assert r2.platform_underneath is False

    tmp3 = StructuralRampConfig(
        num=[2, 3],
        position=VectorFloatConfig(0, None, 0),
        rotation_y=0,
        material=["AI2-THOR/Materials/Walls/DrywallOrange",
                  "AI2-THOR/Materials/Plastics/BlackPlastic"],
        platform_underneath=True,
        platform_underneath_attached_ramps=MinMaxInt(2, 4))
    srv = StructuralRampCreationService()
    r3: StructuralRampConfig = srv.reconcile(scene, tmp3)

    assert r3.num in [2, 3]
    assert r3.position.x == 0
    assert 0.3 <= r3.position.y <= 3
    assert r3.position.z == 0
    assert r3.rotation_y == 0
    assert r3.material in ["AI2-THOR/Materials/Walls/DrywallOrange",
                           "AI2-THOR/Materials/Plastics/BlackPlastic"]
    assert 2 <= r3.platform_underneath_attached_ramps <= 4
    assert r3.platform_underneath is True


def test_thrower_creation_reconcile():
    scene = prior_scene()
    srv = StructuralThrowerCreationService()
    tmp = StructuralThrowerConfig(1)
    r1: StructuralThrowerConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert r1.impulse
    assert r1.wall in [
        WallSide.FRONT.value,
        WallSide.BACK.value,
        WallSide.LEFT.value,
        WallSide.RIGHT.value]
    assert 5 <= r1.throw_step <= 10
    assert r1.throw_force is None
    assert -45 <= r1.rotation_y <= 45
    assert 0 <= r1.rotation_z <= 15
    assert r1.projectile_shape in THROWER_SHAPES
    assert -5 <= r1.position_wall <= 5
    assert 0.2 <= r1.height <= 2.8
    assert r1.projectile_material is None
    assert r1.projectile_scale is None

    tmp2 = StructuralThrowerConfig(
        num=[2, 3], wall=WallSide.FRONT.value, throw_step=[50, 60],
        throw_force=MinMaxInt(14, 16), rotation_y=2, rotation_z=22,
        position_wall=-2,
        height=1.2, projectile_shape="ball", projectile_scale=1,
        projectile_material="AI2-THOR/Materials/Walls/DrywallOrange")
    srv = StructuralThrowerCreationService()
    r2: StructuralThrowerConfig = srv.reconcile(scene, tmp2)

    assert r2.wall == WallSide.FRONT.value
    assert r2.throw_step in [50, 60]
    assert 14 <= r2.throw_force <= 16
    assert r2.rotation_y == 2
    assert r2.rotation_z == 22
    assert r2.position_wall == -2
    assert r2.height == 1.2
    assert r2.projectile_shape == 'ball'
    assert r2.projectile_material == "AI2-THOR/Materials/Walls/DrywallOrange"
    assert r2.projectile_scale == 1


def test_tool_creation_reconcile():
    scene = prior_scene()
    srv = StructuralToolsCreationService()
    tmp = ToolConfig(1)
    r1: ToolConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert -5 < r1.position.x < 5
    assert r1.position.y == 0
    assert -5 < r1.position.z < 5
    assert 0 <= r1.rotation_y < 360
    assert r1.shape in ALL_LARGE_BLOCK_TOOLS
    assert r1.guide_rails is False

    tmp2 = ToolConfig(
        num=[2, 3],
        position=VectorFloatConfig([3, 2], MinMaxFloat(0, 2), 3),
        rotation_y=[90, 180],
        shape=['imaginary_tool_1', 'imaginary_tool_2'], guide_rails=True)
    srv = StructuralToolsCreationService()
    r2: ToolConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position.x in [2, 3]
    assert 0 <= r2.position.y <= 2
    assert r2.position.z == 3
    assert r2.rotation_y in [90, 180]
    assert r2.shape in ["imaginary_tool_1",
                        "imaginary_tool_2"]
    assert r2.guide_rails is True


def test_tool_creation_reconcile_by_size():
    scene = prior_scene()
    template = ToolConfig(num=1, width=0.75, length=6)
    srv = StructuralToolsCreationService()
    r1: ToolConfig = srv.reconcile(scene, template)

    assert r1.num == 1
    assert r1.shape == 'tool_rect_0_75_x_6_00'

    template2 = ToolConfig(num=1, length=6)
    srv = StructuralToolsCreationService()
    r2: ToolConfig = srv.reconcile(scene, template2)

    assert r2.num == 1
    assert r2.shape in [
        'tool_rect_0_50_x_6_00',
        'tool_rect_0_75_x_6_00',
        'tool_rect_1_00_x_6_00',
        'tool_hooked_0_50_x_6_00',
        'tool_hooked_0_75_x_6_00',
        'tool_hooked_1_00_x_6_00']


def test_tool_creation_reconcile_by_size_error():
    scene = prior_scene()
    template = ToolConfig(num=1, width=0.76, length=6)
    srv = StructuralToolsCreationService()
    with pytest.raises(ILEException):
        srv.reconcile(scene, template)


def test_wall_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralWallCreationService()
    tmp = StructuralWallConfig(1)
    r1: StructuralWallConfig = srv.reconcile(scene, tmp)

    assert r1.num == 1
    assert r1.material in material_tuple_group_to_string_list(
        materials.ROOM_WALL_MATERIALS)
    assert -rd.x / 2.0 < r1.position.x < rd.x / 2.0
    assert r1.position.y == 0
    assert -rd.z / 2.0 < r1.position.z < rd.z / 2.0
    assert r1.rotation_y in [0, 90, 180, 270]
    assert 0 < r1.width <= 5

    tmp2 = StructuralWallConfig(
        num=[2, 3],
        position=VectorFloatConfig([3, 2], MinMaxFloat(0, 2), 3),
        rotation_y=[90, 180],
        material=["AI2-THOR/Materials/Walls/DrywallOrange",
                  "AI2-THOR/Materials/Plastics/BlackPlastic"],
        width=[3, 4])
    srv = StructuralWallCreationService()
    r2: StructuralWallConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position.x in [2, 3]
    assert 0 <= r2.position.y <= 2
    assert r2.position.z == 3
    assert r2.rotation_y in [90, 180]
    assert r2.material in ["AI2-THOR/Materials/Walls/DrywallOrange",
                           "AI2-THOR/Materials/Plastics/BlackPlastic"]
    assert r2.width in [3, 4]


def test_door_create():
    temp = StructuralDoorConfig(
        num=1,
        material="AI2-THOR/Materials/Plastics/BlackPlastic",
        position=VectorFloatConfig(1, 2, 3), rotation_y=90,
        wall_material="AI2-THOR/Materials/Walls/DrywallOrange",
        wall_scale_x=3, wall_scale_y=2.2)
    doors = StructuralDoorsCreationService(
    ).create_feature_from_specific_values(prior_scene(), temp, None)
    assert len(doors) == 4
    door = doors[0]
    twall = doors[1]
    lwall = doors[2]
    rwall = doors[3]
    assert door['type'] == 'door_4'
    assert door['id'].startswith('door')
    pos = door['shows'][0]['position']
    rot = door['shows'][0]['rotation']
    scale = door['shows'][0]['scale']
    assert pos == {'x': 1, 'y': 2, 'z': 3}
    assert rot == {'x': 0, 'y': 90, 'z': 0}
    assert scale == {'x': 1, 'y': 1, 'z': 1}
    assert door['materials'] == ["AI2-THOR/Materials/Plastics/BlackPlastic"]
    assert door['kinematic']
    assert door['openable']

    assert twall['type'] == 'cube'
    assert twall['id'].startswith('wall_top')
    pos = twall['shows'][0]['position']
    rot = twall['shows'][0]['rotation']
    scale = twall['shows'][0]['scale']
    assert pos == {'x': 1, 'y': 4.1, 'z': 3}
    assert rot == {'x': 0, 'y': 90, 'z': 0}
    assert scale == {'x': 3, 'y': pytest.approx(0.2), 'z': 0.1}
    assert twall['materials'] == ["AI2-THOR/Materials/Walls/DrywallOrange"]
    assert twall['kinematic']
    assert twall['structure']

    assert lwall['type'] == 'cube'
    assert lwall['id'].startswith('wall_left')
    pos = lwall['shows'][0]['position']
    rot = lwall['shows'][0]['rotation']
    scale = lwall['shows'][0]['scale']
    assert pos == {'x': 1, 'y': 3, 'z': 2.04}
    assert rot == {'x': 0, 'y': 90, 'z': 0}
    assert scale == {'x': 1.08, 'y': 2, 'z': 0.1}
    assert lwall['materials'] == ["AI2-THOR/Materials/Walls/DrywallOrange"]
    assert lwall['kinematic']
    assert lwall['structure']

    assert rwall['type'] == 'cube'
    assert rwall['id'].startswith('wall_right')
    pos = rwall['shows'][0]['position']
    rot = rwall['shows'][0]['rotation']
    scale = rwall['shows'][0]['scale']
    assert pos == {'x': 1, 'y': 3, 'z': 3.96}
    assert rot == {'x': 0, 'y': 90, 'z': 0}
    assert scale == {'x': 1.08, 'y': 2, 'z': 0.1}
    assert rwall['materials'] == ["AI2-THOR/Materials/Walls/DrywallOrange"]
    assert rwall['kinematic']
    assert rwall['structure']


def test_dropper_create():
    temp = StructuralDropperConfig(
        num=1, position_x=2, position_z=-2, drop_step=3,
        projectile_shape="ball",
        projectile_material="AI2-THOR/Materials/Wood/LightWoodCounters 1",
        projectile_scale=VectorFloatConfig(1, 1.1, 1.2))
    scene = prior_scene()
    srv = StructuralDropperCreationService()
    obj = srv.create_feature_from_specific_values(scene, temp, None)[0]
    assert len(obj)
    assert obj['id'].startswith("dropping_device")
    assert obj['type'] == 'tube_wide'
    assert obj['states'] == [['held'], ['held'], ['released']]
    show = obj['shows'][0]
    show['position'] == {'x': 2, 'y': 2.31, 'z': -2}
    show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    show['scale'] == {'x': 1.25, 'y': 1.38, 'z': 1.25}

    obj = srv.target.instance

    assert obj['materials'] == ["AI2-THOR/Materials/Wood/LightWoodCounters 1"]
    assert obj['type'] == 'ball'
    assert obj['moveable']
    assert obj['pickupable']
    show = obj['shows'][0]
    show['scale'] == {'x': 1, 'y': 1.1, 'z': 1.2}


def test_floor_material_create():
    temp = FloorMaterialConfig(
        material="AI2-THOR/Materials/Walls/DrywallRed",
        position_x=3,
        position_z=-3)
    floor = StructuralFloorMaterialsCreationService(
    ).create_feature_from_specific_values(prior_scene(), temp, None)
    assert floor == temp

    scene = prior_scene()
    StructuralFloorMaterialsCreationService(
    ).add_to_scene(scene, temp, [])
    assert scene.floor_textures
    text = scene.floor_textures[0]
    assert text['material'] == "AI2-THOR/Materials/Walls/DrywallRed"
    assert text['positions'] == [{'x': 3, 'z': -3}]


def test_holes_create():
    temp = FloorAreaConfig(position_x=3, position_z=-4)
    holes = StructuralHolesCreationService(
    ).create_feature_from_specific_values(prior_scene(), temp, None)
    assert holes == {'x': 3, 'z': -4}


def test_l_occluder_create():
    temp = StructuralLOccluderConfig(
        backwards=True, position=VectorFloatConfig(x=2.1, y=0, z=-3.4),
        rotation_y=34, material="AI2-THOR/Materials/Walls/DrywallRed",
        scale_front_x=1.1, scale_front_z=1.2,
        scale_side_x=1.3, scale_side_z=1.4, scale_y=1.5)
    occl = StructuralLOccluderCreationService(
    ).create_feature_from_specific_values(prior_scene(), temp, None)
    o1 = occl[0]
    o2 = occl[1]
    assert o1['id'].startswith('occluder_front_')
    assert o1['type'] == 'cube'
    assert o1['kinematic']
    assert o1['structure']
    assert o1['materials'] == ["AI2-THOR/Materials/Walls/DrywallRed"]
    show = o1['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 2.1, 'y': 0.75, 'z': -3.4}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 1.1, 'y': 1.5, 'z': 1.2}

    assert o2['id'].startswith('occluder_side_')
    assert o2['type'] == 'cube'
    assert o2['kinematic']
    assert o2['structure']
    assert o2['materials'] == ["AI2-THOR/Materials/Walls/DrywallRed"]
    show = o2['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': pytest.approx(
        2.744047), 'y': 0.75, 'z': pytest.approx(-2.2663318)}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 1.3, 'y': 1.5, 'z': 1.4}


def test_lava_create():
    temp = FloorAreaConfig(position_x=-1, position_z=4)
    lava = StructuralLavaCreationService().create_feature_from_specific_values(
        prior_scene(), temp, None)
    assert lava == {'x': -1, 'z': 4}


def test_moving_occluder_create():
    temp = StructuralMovingOccluderConfig(
        origin="left", wall_material="AI2-THOR/Materials/Walls/DrywallRed",
        pole_material="AI2-THOR/Materials/Metals/Brass 1",
        position_x=2.2, position_z=-2.3, occluder_height=1.2,
        occluder_width=2.2, occluder_thickness=0.2, repeat_movement=True,
        repeat_interval=3)
    occl = StructuralMovingOccluderCreationService(
    ).create_feature_from_specific_values(prior_scene(), temp, None)
    o1 = occl[0]
    o2 = occl[1]
    assert o1['id'].startswith('occluder_wall_')
    assert o1['type'] == 'cube'
    assert o1['kinematic']
    assert o1['structure']
    assert o1['materials'] == ["AI2-THOR/Materials/Walls/DrywallRed"]
    show = o1['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 2.2, 'y': 0.6, 'z': -2.3}
    assert rot == {'x': 0, 'y': 0, 'z': 0}
    assert scale == {'x': 2.2, 'y': 1.2, 'z': 0.2}

    move1 = o1['moves'][0]
    assert move1['stepBegin'] == 1
    assert move1['stepEnd'] == 6
    assert move1['vector'] == {'x': 0, 'y': 0.25, 'z': 0}
    assert move1['repeat']
    assert move1['stepWait'] == 34
    move2 = o2['moves'][1]
    assert move2['stepBegin'] == 31
    assert move2['stepEnd'] == 36
    assert move2['vector'] == {'x': -0.25, 'y': 0, 'z': 0}
    assert move2['repeat']
    assert move2['stepWait'] == 34

    assert o2['id'].startswith('occluder_pole_')
    assert o2['type'] == 'cylinder'
    assert o2['kinematic']
    assert o2['structure']
    assert o2['materials'] == ["AI2-THOR/Materials/Metals/Brass 1"]
    show = o2['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': -1.95, 'y': 0.6, 'z': -2.3}
    assert rot == {'x': 0, 'y': 0, 'z': 90}
    assert scale == {'x': 0.195, 'y': 3.05, 'z': 0.195}
    move1 = o2['moves'][0]
    assert move1['stepBegin'] == 1
    assert move1['stepEnd'] == 6
    assert move1['vector'] == {'x': 0.25, 'y': 0, 'z': 0}
    assert move1['repeat']
    assert move1['stepWait'] == 34
    move2 = o2['moves'][1]
    assert move2['stepBegin'] == 31
    assert move2['stepEnd'] == 36
    assert move2['vector'] == {'x': -0.25, 'y': 0, 'z': 0}
    assert move2['repeat']
    assert move2['stepWait'] == 34


def test_placer_create():
    temp = StructuralPlacerConfig(
        activation_step=3, end_height=2.2,
        placed_object_position=VectorFloatConfig(1.1, 0, 1.3),
        placed_object_scale=1.4, placed_object_rotation=34,
        placed_object_shape="ball",
        placed_object_material="AI2-THOR/Materials/Wood/WhiteWood")
    scene = prior_scene_with_target()
    srv = StructuralPlacersCreationService()
    srv.object_idl = InstanceDefinitionLocationTuple(
        scene.objects[0], create_soccer_ball(), None)
    placer = srv.create_feature_from_specific_values(scene, temp, None)

    placer = placer[0]
    assert placer['id'].startswith('placer_')
    assert placer['type'] == 'cylinder'
    assert placer['kinematic']
    assert placer['structure']

    show = placer['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == pytest.approx({'x': 1.1, 'y': 3.32, 'z': 1.3})
    assert rot == {'x': 0, 'y': 0, 'z': 0}
    assert scale == {'x': 0.05, 'y': pytest.approx(0.4), 'z': 0.05}

    move1 = placer['moves'][0]
    move2 = placer['moves'][1]
    assert move1['stepBegin'] == 3
    assert move1['stepEnd'] == 4
    assert move1['vector'] == {'x': 0, 'y': -0.25, 'z': 0}

    assert move2['stepBegin'] == 15
    assert move2['stepEnd'] == 15
    assert move2['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    target = scene.objects[0]
    show = target['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 2.81, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}

    move1 = target['moves'][0]
    assert move1['stepBegin'] == 3
    assert move1['stepEnd'] == 4
    assert move1['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_placer_create_with_non_zero_position_y():
    temp = StructuralPlacerConfig(
        activation_step=3, end_height=0.4,
        placed_object_position=VectorFloatConfig(1.1, 1.2, 1.3),
        placed_object_scale=1.4, placed_object_rotation=34,
        placed_object_shape="ball",
        placed_object_material="AI2-THOR/Materials/Wood/WhiteWood")
    scene = prior_scene_with_target()
    srv = StructuralPlacersCreationService()
    srv.object_idl = InstanceDefinitionLocationTuple(
        scene.objects[0], create_soccer_ball(), None)
    placer = srv.create_feature_from_specific_values(scene, temp, None)

    placer = placer[0]
    assert placer['id'].startswith('placer_')
    assert placer['type'] == 'cylinder'
    assert placer['kinematic']
    assert placer['structure']

    show = placer['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': pytest.approx(2.42), 'z': 1.3}
    assert rot == {'x': 0, 'y': 0, 'z': 0}
    assert scale == {'x': 0.05, 'y': 1.3, 'z': 0.05}

    move1 = placer['moves'][0]
    move2 = placer['moves'][1]
    assert move1['stepBegin'] == 3
    assert move1['stepEnd'] == 4
    assert move1['vector'] == {'x': 0, 'y': -0.25, 'z': 0}

    assert move2['stepBegin'] == 15
    assert move2['stepEnd'] == 15
    assert move2['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    target = scene.objects[0]
    show = target['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': pytest.approx(1.01), 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}

    move1 = target['moves'][0]
    assert move1['stepBegin'] == 3
    assert move1['stepEnd'] == 4
    assert move1['vector'] == {'x': 0, 'y': -0.25, 'z': 0}


def test_placer_create_container_asymmetric():
    temp = StructuralPlacerConfig(
        activation_step=3, end_height=1.6,
        placed_object_position=VectorFloatConfig(1.1, 0, 1.3),
        placed_object_scale=1.4, placed_object_rotation=0,
        placed_object_shape="container_asymmetric_01",
        placed_object_material="AI2-THOR/Materials/Wood/WhiteWood")
    scene = prior_scene()
    srv = StructuralPlacersCreationService()
    defn = create_specific_definition_from_base(
        'container_asymmetric_01',
        ['white'],
        ['AI2-THOR/Materials/Wood/WhiteWood'],
        None,
        1.4
    )
    location = ORIGIN_LOCATION
    instance = instantiate_object(defn, location)
    srv.object_idl = InstanceDefinitionLocationTuple(instance, defn, location)
    objects = srv.create_feature_from_specific_values(scene, temp, None)
    assert len(objects) == 3

    container = objects[0]
    assert container['type'] == 'container_asymmetric_01'
    assert container['kinematic']

    show = container['shows'][0]
    assert show['position'] == {'x': 1.1, 'y': pytest.approx(2.1), 'z': 1.3}
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 1.4, 'y': 1.4, 'z': 1.4}

    assert len(container['moves']) == 1
    assert container['moves'][0]['stepBegin'] == 3
    assert container['moves'][0]['stepEnd'] == 4
    assert container['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}

    assert len(container['togglePhysics']) == 1
    assert container['togglePhysics'][0]['stepBegin'] == 10

    placer = objects[1]
    assert placer['id'].startswith('placer_')
    assert placer['type'] == 'cylinder'
    assert placer['kinematic']
    assert placer['structure']

    show = placer['shows'][0]
    assert show['position'] == {
        'x': pytest.approx(1.66), 'y': pytest.approx(3.08), 'z': 1.3
    }
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.25, 'y': pytest.approx(0.7), 'z': 0.25}

    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 3
    assert placer['moves'][0]['stepEnd'] == 4
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 15
    assert placer['moves'][1]['stepEnd'] == 15
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 10

    placer = objects[2]
    assert placer['id'].startswith('placer_')
    assert placer['type'] == 'cylinder'
    assert placer['kinematic']
    assert placer['structure']

    show = placer['shows'][0]
    assert show['position'] == {
        'x': pytest.approx(0.54), 'y': pytest.approx(3.64), 'z': 1.3
    }
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.25, 'y': pytest.approx(0.7), 'z': 0.25}

    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 3
    assert placer['moves'][0]['stepEnd'] == 4
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 15
    assert placer['moves'][1]['stepEnd'] == 15
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 10


def test_placer_create_container_asymmetric_with_rotation():
    temp = StructuralPlacerConfig(
        activation_step=3, end_height=1.6,
        placed_object_position=VectorFloatConfig(1.1, 0, 1.3),
        placed_object_scale=1.4, placed_object_rotation=34,
        placed_object_shape="container_asymmetric_01",
        placed_object_material="AI2-THOR/Materials/Wood/WhiteWood")
    scene = prior_scene()
    srv = StructuralPlacersCreationService()
    defn = create_specific_definition_from_base(
        'container_asymmetric_01',
        ['white'],
        ['AI2-THOR/Materials/Wood/WhiteWood'],
        None,
        1.4
    )
    location = ORIGIN_LOCATION
    instance = instantiate_object(defn, location)
    srv.object_idl = InstanceDefinitionLocationTuple(instance, defn, location)
    objects = srv.create_feature_from_specific_values(scene, temp, None)
    assert len(objects) == 3

    container = objects[0]
    assert container['type'] == 'container_asymmetric_01'
    assert container['kinematic']

    show = container['shows'][0]
    assert show['position'] == {'x': 1.1, 'y': pytest.approx(2.1), 'z': 1.3}
    assert show['rotation'] == {'x': 0, 'y': 34, 'z': 0}
    assert show['scale'] == {'x': 1.4, 'y': 1.4, 'z': 1.4}

    assert len(container['moves']) == 1
    assert container['moves'][0]['stepBegin'] == 3
    assert container['moves'][0]['stepEnd'] == 4
    assert container['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}

    assert len(container['togglePhysics']) == 1
    assert container['togglePhysics'][0]['stepBegin'] == 10

    placer = objects[1]
    assert placer['id'].startswith('placer_')
    assert placer['type'] == 'cylinder'
    assert placer['kinematic']
    assert placer['structure']

    show = placer['shows'][0]
    assert show['position'] == {
        'x': pytest.approx(1.564261),
        'y': pytest.approx(3.08),
        'z': pytest.approx(0.986852)
    }
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.25, 'y': pytest.approx(0.7), 'z': 0.25}

    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 3
    assert placer['moves'][0]['stepEnd'] == 4
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 15
    assert placer['moves'][1]['stepEnd'] == 15
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 10

    placer = objects[2]
    assert placer['id'].startswith('placer_')
    assert placer['type'] == 'cylinder'
    assert placer['kinematic']
    assert placer['structure']

    show = placer['shows'][0]
    assert show['position'] == {
        'x': pytest.approx(0.635739),
        'y': pytest.approx(3.64),
        'z': pytest.approx(1.613148)
    }
    assert show['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert show['scale'] == {'x': 0.25, 'y': pytest.approx(0.7), 'z': 0.25}

    assert len(placer['moves']) == 2
    assert placer['moves'][0]['stepBegin'] == 3
    assert placer['moves'][0]['stepEnd'] == 4
    assert placer['moves'][0]['vector'] == {'x': 0, 'y': -0.25, 'z': 0}
    assert placer['moves'][1]['stepBegin'] == 15
    assert placer['moves'][1]['stepEnd'] == 15
    assert placer['moves'][1]['vector'] == {'x': 0, 'y': 0.25, 'z': 0}

    assert len(placer['changeMaterials']) == 1
    assert placer['changeMaterials'][0]['stepBegin'] == 10


def test_platform_create():
    scene = prior_scene()
    scene.room_dimensions.y = 10
    temp = StructuralPlatformConfig(
        position=VectorFloatConfig(1.1, 1.2, 1.3),
        rotation_y=34,
        material="AI2-THOR/Materials/Ceramics/BrownMarbleFake 1",
        lips=StructuralPlatformLipsConfig(False, True, False, True),
        scale=0.6, attached_ramps=0, platform_underneath=False,
        platform_underneath_attached_ramps=0)
    platforms = StructuralPlatformCreationService(
    ).create_feature_from_specific_values(scene, temp, None)

    plat = platforms[0]
    assert plat
    assert plat['id'].startswith('platform_')
    assert plat['type'] == 'cube'
    assert plat['kinematic']
    assert plat['structure']
    assert plat['materials'] == [
        "AI2-THOR/Materials/Ceramics/BrownMarbleFake 1"]
    assert plat['lips'] == {
        'front': False,
        'back': True,
        'left': False,
        'right': True}
    show = plat['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 1.5, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 0.6, 'y': 0.6, 'z': 0.6}


def test_platform_create_too_tall_auto_adjust():
    scene = prior_scene()
    scene.room_dimensions.y = 5
    temp = StructuralPlatformConfig(
        position=VectorFloatConfig(1.1, 3, 1.3),
        rotation_y=34,
        material="AI2-THOR/Materials/Ceramics/BrownMarbleFake 1",
        lips=StructuralPlatformLipsConfig(False, True, False, True),
        scale=2, attached_ramps=0, platform_underneath=False,
        platform_underneath_attached_ramps=0, auto_adjust_platforms=True)
    platforms = StructuralPlatformCreationService(
    ).create_feature_from_specific_values(scene, temp, None)

    plat = platforms[0]
    assert plat
    assert plat['id'].startswith('platform_')
    assert plat['type'] == 'cube'
    assert plat['kinematic']
    assert plat['structure']
    assert plat['materials'] == [
        "AI2-THOR/Materials/Ceramics/BrownMarbleFake 1"]
    assert plat['lips'] == {
        'front': False,
        'back': True,
        'left': False,
        'right': True}
    show = plat['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 3.375, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 2, 'y': 0.75, 'z': 2}


def test_platform_create_too_tall_no_auto_adjust():
    scene = prior_scene()
    scene.room_dimensions.x = 10
    scene.room_dimensions.y = 5
    scene.room_dimensions.z = 10
    temp = StructuralPlatformConfig(
        position=VectorFloatConfig(1.1, 0, 1.3),
        rotation_y=34,
        material="AI2-THOR/Materials/Ceramics/BrownMarbleFake 1",
        lips=StructuralPlatformLipsConfig(False, True, False, True),
        scale=4.9, attached_ramps=0, platform_underneath=False,
        platform_underneath_attached_ramps=0)
    platforms = StructuralPlatformCreationService(
    ).create_feature_from_specific_values(scene, temp, None)

    plat = platforms[0]
    assert plat
    assert plat['id'].startswith('platform_')
    assert plat['type'] == 'cube'
    assert plat['kinematic']
    assert plat['structure']
    assert plat['materials'] == [
        "AI2-THOR/Materials/Ceramics/BrownMarbleFake 1"]
    assert plat['lips'] == {
        'front': False,
        'back': True,
        'left': False,
        'right': True}
    show = plat['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 2.45, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 4.9, 'y': 4.9, 'z': 4.9}


def test_platform_create_under():
    scene = prior_scene()
    scene.room_dimensions.y = 10
    temp = StructuralPlatformConfig(
        position=VectorFloatConfig(1.1, 1.2, 1.3),
        rotation_y=34, material="AI2-THOR/Materials/Metals/WhiteMetal",
        lips=StructuralPlatformLipsConfig(True, True, True, True),
        scale=0.6, attached_ramps=1, platform_underneath=True,
        platform_underneath_attached_ramps=2)
    platforms = StructuralPlatformCreationService(
    ).create_feature_from_specific_values(scene, temp, None)

    plat = platforms[0]
    assert plat
    assert plat['id'].startswith('platform_')
    assert plat['type'] == 'cube'
    assert plat['kinematic']
    assert plat['structure']
    assert plat['materials'] == [
        "AI2-THOR/Materials/Metals/WhiteMetal"]
    assert plat['lips']['back']
    assert plat['lips']['right']
    assert plat['lips']['front']
    assert plat['lips']['left']
    assert plat['lips']['gaps']
    show = plat['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 1.5, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 0.6, 'y': 0.6, 'z': 0.6}

    plat = platforms[1]
    assert plat
    assert plat['id'].startswith('platform_')
    assert plat['type'] == 'cube'
    assert plat['kinematic']
    assert plat['structure']
    assert plat['materials'] != [
        "AI2-THOR/Materials/Metals/WhiteMetal"]
    below_mat = plat['materials']
    assert plat['lips']['back']
    assert plat['lips']['right']
    assert plat['lips']['front']
    assert plat['lips']['left']
    assert plat['lips']['gaps']
    show = plat['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert pos['y'] == 0.6
    assert scale['y'] == 1.2

    ramp = platforms[2]
    assert ramp
    assert ramp['id'].startswith('ramp_')
    assert ramp['type'] == 'triangle'
    assert ramp['kinematic']
    assert ramp['structure']
    assert ramp['materials'] == [
        "AI2-THOR/Materials/Metals/WhiteMetal"]
    show = ramp['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos['y'] == pytest.approx(1.5)
    assert scale['y'] == pytest.approx(0.6)

    ramp = platforms[3]
    assert ramp
    assert ramp['id'].startswith('ramp_')
    assert ramp['type'] == 'triangle'
    assert ramp['kinematic']
    assert ramp['structure']
    assert ramp['materials'] == below_mat
    show = ramp['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos['y'] == pytest.approx(0.6)
    assert scale['y'] == pytest.approx(1.2)

    ramp = platforms[4]
    assert ramp
    assert ramp['id'].startswith('ramp_')
    assert ramp['type'] == 'triangle'
    assert ramp['kinematic']
    assert ramp['structure']
    assert ramp['materials'] == below_mat
    show = ramp['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos['y'] == pytest.approx(0.6)
    assert scale['y'] == pytest.approx(1.2)


def test_platform_create_min_scale_no_lips():
    scene = prior_scene()
    config = StructuralPlatformConfig(
        scale=0.5,
        lips=StructuralPlatformLipsConfig(False, False, False, False),
        attached_ramps=0,
        platform_underneath=False,
        platform_underneath_attached_ramps=0
    )
    service = StructuralPlatformCreationService()
    objects, _ = service.add_to_scene(scene, config, [])
    assert len(objects) == 1

    assert objects[0]
    assert objects[0]['id'].startswith('platform_')
    assert objects[0]['type'] == 'cube'
    assert objects[0]['kinematic']
    assert objects[0]['structure']
    assert objects[0]['lips'] == {
        'front': False,
        'back': False,
        'left': False,
        'right': False
    }
    # All scales should be as configured.
    assert objects[0]['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}


def test_platform_create_min_scale_with_lips():
    scene = prior_scene()
    config = StructuralPlatformConfig(
        scale=0.5,
        lips=StructuralPlatformLipsConfig(True, True, True, True),
        attached_ramps=0,
        platform_underneath=False,
        platform_underneath_attached_ramps=0
    )
    service = StructuralPlatformCreationService()
    objects, _ = service.add_to_scene(scene, config, [])
    assert len(objects) == 1

    assert objects[0]
    assert objects[0]['id'].startswith('platform_')
    assert objects[0]['type'] == 'cube'
    assert objects[0]['kinematic']
    assert objects[0]['structure']
    assert objects[0]['lips'] == {
        'front': True,
        'back': True,
        'left': True,
        'right': True
    }
    # The X and Y scales should be increased to 0.8.
    assert objects[0]['shows'][0]['scale'] == {'x': 0.8, 'y': 0.5, 'z': 0.8}


def test_ramp_create():
    temp = StructuralRampConfig(
        angle=45, position=VectorFloatConfig(1.1, 1.2, 1.3), rotation_y=34,
        material="AI2-THOR/Materials/Metals/WhiteMetal",
        width=2, length=3, platform_underneath=False,
        platform_underneath_attached_ramps=0)
    ramp = StructuralRampCreationService().create_feature_from_specific_values(
        prior_scene(), temp, None)

    ramp = ramp[0]
    assert ramp
    assert ramp['id'].startswith('ramp_')
    assert ramp['type'] == 'triangle'
    assert ramp['kinematic']
    assert ramp['structure']
    assert ramp['materials'] == [
        "AI2-THOR/Materials/Metals/WhiteMetal"]

    show = ramp['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': pytest.approx(2.7), 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    # 45 degrees means length == height
    assert scale == {'x': 2, 'y': pytest.approx(3), 'z': 3}


def test_thrower_create():
    temp = StructuralThrowerConfig(
        height=1.3, wall='front', position_wall=0.1, rotation_y=0,
        rotation_z=2, throw_step=5,
        throw_force=5, projectile_shape='ball',
        projectile_material="AI2-THOR/Materials/Plastics/BlueRubber",
        projectile_scale=0.3)
    scene = prior_scene_custom_start(4, 4)
    srv = StructuralThrowerCreationService()
    objs = srv.create_feature_from_specific_values(scene, temp, None)

    thrower = objs[0]
    assert thrower
    assert thrower['id'].startswith('throwing_device_')
    assert thrower['type'] == 'tube_wide'
    assert thrower['kinematic']
    assert thrower['structure']
    assert thrower['materials'] == ['Custom/Materials/Grey']
    assert thrower['states'] == [
        ['held'], ['held'], ['held'], ['held'], ['released']
    ]
    show = thrower['shows'][0]
    pos = show['position']
    rot = show['rotation']

    assert pos['x'] == 0.1
    assert pos['y'] == 1.3
    assert rot == {'x': 0, 'y': 90, 'z': 92}

    proj = objs[1]
    assert proj
    assert proj['type'] == 'ball'
    # Note, the ball hasn't been positioned yet


def test_wall_create():
    temp = StructuralWallConfig(
        position=VectorFloatConfig(1.1, 0, 1.3), rotation_y=34,
        width=2.2,
        material="AI2-THOR/Materials/Plastics/WhitePlastic")
    wall = StructuralWallCreationService().create_feature_from_specific_values(
        prior_scene(), temp, None)

    wall = wall[0]
    assert wall
    assert wall['id'].startswith('wall_')
    assert wall['type'] == 'cube'
    assert wall['kinematic']
    assert wall['structure']
    assert wall['materials'] == [
        "AI2-THOR/Materials/Plastics/WhitePlastic"]

    show = wall['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 1.5, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 2.2, 'y': 3, 'z': 0.1}


def test_tool_create():
    temp = ToolConfig(
        position=VectorFloatConfig(1.1, 1.2, 1.3), rotation_y=34,
        guide_rails=True, shape='tool_rect_0_75_x_4_00')
    tool = StructuralToolsCreationService(
    ).create_feature_from_specific_values(prior_scene(), temp, None)

    assert tool
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_4_00'
    show = tool['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 0.15, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 1, 'y': 1, 'z': 1}


def test_tool_create_hooked():
    temp = ToolConfig(
        position=VectorFloatConfig(1.1, 1.2, 1.3), rotation_y=34,
        guide_rails=False, shape='tool_hooked_0_75_x_4_00')
    tool = StructuralToolsCreationService(
    ).create_feature_from_specific_values(prior_scene(), temp, None)

    assert tool
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_hooked_0_75_x_4_00'
    show = tool['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 0.15, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 1, 'y': 1, 'z': 1}


def test_tool_create_short():
    temp = ToolConfig(
        position=VectorFloatConfig(1.1, 1.2, 1.3), rotation_y=34,
        guide_rails=False, shape='tool_rect_0_75_x_1_00')
    tool = StructuralToolsCreationService(
    ).create_feature_from_specific_values(prior_scene(), temp, None)

    assert tool
    assert tool['id'].startswith('tool_')
    assert tool['type'] == 'tool_rect_0_75_x_1_00'
    show = tool['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 0.15, 'z': 1.3}
    assert rot == {'x': 0, 'y': 34, 'z': 0}
    assert scale == {'x': 1, 'y': 1, 'z': 1}


def test_turntable_creation_reconcile():
    scene = prior_scene()
    rd = scene.room_dimensions
    srv = StructuralTurntableCreationService()
    tmp = StructuralTurntableConfig(1)
    r1: StructuralTurntableConfig = srv.reconcile(scene, tmp)
    assert r1.num == 1
    assert -rd.x / 2.0 <= r1.position.x <= rd.x / 2.0
    assert -rd.z / 2.0 <= r1.position.z <= rd.z / 2.0
    assert r1.position.y == 0
    assert r1.rotation_y == 0
    assert r1.material is not None
    assert r1.labels is None
    assert r1.turntable_height == 0.1
    assert 0.5 <= r1.turntable_radius < 1.5
    assert r1.turntable_movement is not None
    assert 0 <= r1.turntable_movement.step_begin <= 10
    # Rotate either 90, 180, 270, or 360 degrees.
    assert r1.turntable_movement.step_end in [
        r1.turntable_movement.step_begin + 17,
        r1.turntable_movement.step_begin + 35,
        r1.turntable_movement.step_begin + 53,
        r1.turntable_movement.step_begin + 71
    ]
    assert r1.turntable_movement.rotation_y in [5, -5]

    tmp2 = StructuralTurntableConfig(
        num=[2, 3], position=VectorFloatConfig(1, 0, 1),
        turntable_height=[0.5, 1], turntable_radius=[1, 1.5],
        rotation_y=2,
        material="AI2-THOR/Materials/Plastics/BlackPlastic",
        turntable_movement=StructuralObjectMovementConfig(
            step_begin=1, step_end=12, rotation_y=8
        )
    )
    srv = StructuralTurntableCreationService()
    r2: StructuralTurntableConfig = srv.reconcile(scene, tmp2)

    assert r2.num in [2, 3]
    assert r2.position.x == 1
    assert r2.position.y == 0
    assert r2.position.z == 1
    assert r2.rotation_y == 2
    assert r2.turntable_height in [0.5, 1]
    assert r2.turntable_radius in [1, 1.5]
    assert r2.material == "AI2-THOR/Materials/Plastics/BlackPlastic"
    assert r2.turntable_movement is not None
    assert r2.turntable_movement.step_begin == 1
    assert r2.turntable_movement.step_end == 12
    assert r2.turntable_movement.rotation_y == 8


def test_turntable_create():
    temp = StructuralTurntableConfig(
        position=VectorFloatConfig(1.1, 0, 1.3),
        turntable_height=0.4, turntable_radius=2,
        rotation_y=2,
        material="AI2-THOR/Materials/Plastics/BlackPlastic",
        turntable_movement=StructuralObjectMovementConfig(
            step_begin=5, step_end=15, rotation_y=15
        )
    )
    turntable = StructuralTurntableCreationService(
    ).create_feature_from_specific_values(prior_scene(), temp, None)

    assert turntable
    assert turntable['id'].startswith('turntable_')
    assert turntable['type'] == 'rotating_cog'
    show = turntable['shows'][0]
    pos = show['position']
    rot = show['rotation']
    scale = show['scale']
    assert pos == {'x': 1.1, 'y': 0.2, 'z': 1.3}
    assert rot == {'x': 0, 'y': 2, 'z': 0}
    assert scale == {'x': 4, 'y': 20, 'z': 4}
    movement = turntable['rotates'][0]
    assert movement['stepBegin'] == 5
    assert movement['stepEnd'] == 15
    assert movement['vector'] == {'x': 0, 'y': 15, 'z': 0}


def test_turntable_end_after_rotation():
    scene = prior_scene()
    service = StructuralTurntableCreationService()
    config = service.reconcile(scene, StructuralTurntableConfig(
        position=VectorFloatConfig(-1, 0, -2),
        rotation_y=3,
        turntable_radius=0.5,
        turntable_movement=StructuralObjectMovementConfig(
            rotation_y=-4,
            step_begin=5,
            end_after_rotation=100
        )
    ))
    turntable = service.create_feature_from_specific_values(
        scene,
        config,
        None
    )

    assert turntable
    assert turntable['id'].startswith('turntable_')
    assert turntable['type'] == 'rotating_cog'
    assert turntable['shows'][0]['position'] == {'x': -1, 'y': 0.05, 'z': -2}
    assert turntable['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert turntable['shows'][0]['scale'] == {'x': 1, 'y': 5, 'z': 1}
    assert turntable['rotates'][0]['stepBegin'] == 5
    assert turntable['rotates'][0]['stepEnd'] == 29
    assert turntable['rotates'][0]['vector'] == {'x': 0, 'y': -4, 'z': 0}


def test_turntable_rotation_y_zero_step_end():
    scene = prior_scene()
    service = StructuralTurntableCreationService()
    config = service.reconcile(scene, StructuralTurntableConfig(
        position=VectorFloatConfig(-1, 0, -2),
        rotation_y=3,
        turntable_radius=0.5,
        turntable_movement=StructuralObjectMovementConfig(
            rotation_y=0,
            step_begin=5,
            step_end=10
        )
    ))
    turntable = service.create_feature_from_specific_values(
        scene,
        config,
        None
    )

    assert turntable
    assert turntable['id'].startswith('turntable_')
    assert turntable['type'] == 'rotating_cog'
    assert turntable['shows'][0]['position'] == {'x': -1, 'y': 0.05, 'z': -2}
    assert turntable['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert turntable['shows'][0]['scale'] == {'x': 1, 'y': 5, 'z': 1}
    assert turntable['rotates'][0]['stepBegin'] == 5
    assert turntable['rotates'][0]['stepEnd'] == 5
    assert turntable['rotates'][0]['vector'] == {'x': 0, 'y': 0, 'z': 0}


def test_turntable_rotation_y_zero_end_after_rotation():
    scene = prior_scene()
    service = StructuralTurntableCreationService()
    config = service.reconcile(scene, StructuralTurntableConfig(
        position=VectorFloatConfig(-1, 0, -2),
        rotation_y=3,
        turntable_radius=0.5,
        turntable_movement=StructuralObjectMovementConfig(
            rotation_y=0,
            step_begin=5,
            end_after_rotation=30
        )
    ))
    turntable = service.create_feature_from_specific_values(
        scene,
        config,
        None
    )

    assert turntable
    assert turntable['id'].startswith('turntable_')
    assert turntable['type'] == 'rotating_cog'
    assert turntable['shows'][0]['position'] == {'x': -1, 'y': 0.05, 'z': -2}
    assert turntable['shows'][0]['rotation'] == {'x': 0, 'y': 3, 'z': 0}
    assert turntable['shows'][0]['scale'] == {'x': 1, 'y': 5, 'z': 1}
    assert turntable['rotates'][0]['stepBegin'] == 5
    assert turntable['rotates'][0]['stepEnd'] == 5
    assert turntable['rotates'][0]['vector'] == {'x': 0, 'y': 0, 'z': 0}


def test_platform_long_with_two_ramps():
    scene = prior_scene()
    scene.room_dimensions.x = 10
    scene.room_dimensions.y = 8
    scene.room_dimensions.z = 10
    # lips, attached_ramps, and platform_underneath_attached_ramps
    # will be overrided
    temp = StructuralPlatformConfig(
        num=1,
        position=VectorFloatConfig(1, 2, 3),
        rotation_y=0,
        scale=1,
        material="AI2-THOR/Materials/Ceramics/BrownMarbleFake 1",
        lips=StructuralPlatformLipsConfig(False, False, False, False),
        attached_ramps=1,
        platform_underneath=False,
        platform_underneath_attached_ramps=3,
        long_with_two_ramps=True
    )
    platform_two_ramps = StructuralPlatformCreationService(
    ).create_feature_from_specific_values(scene, temp, None)

    assert len(platform_two_ramps) == 3
    plat = platform_two_ramps[0]
    ramp_1 = platform_two_ramps[1]
    ramp_2 = platform_two_ramps[2]
    assert plat['id'].startswith('platform_')
    assert ramp_1['id'].startswith('ramp_')
    assert ramp_2['id'].startswith('ramp_')

    plat_scale = plat['shows'][0]['scale']
    plat_pos = plat['shows'][0]['position']
    long_x = plat_scale['x'] > plat_scale['z']
    assert (plat_scale['x'] == scene.room_dimensions.x if
            long_x else plat_scale['x'] == 1)
    assert (
        plat_scale['z'] == scene.room_dimensions.z if not
        long_x else plat_scale['z'] == 1)
    assert plat_pos['x'] == 0 if long_x else plat_pos['x'] == 1
    assert plat_pos['z'] == 0 if not long_x else plat_pos['z'] == 3

    lips = plat['lips']
    assert lips['front'] and lips['back'] and lips['left'] and lips['right']
    assert (lips['gaps']['front'] and lips['gaps']['back'] if long_x else
            lips['gaps']['left'] and lips['gaps']['right'])

    ramp_1_pos = ramp_1['shows'][0]['position']
    ramp_2_pos = ramp_2['shows'][0]['position']
    assert (
        round(ramp_1_pos['z']) < round(ramp_2_pos['z']) if long_x else
        round(ramp_1_pos['x']) < round(ramp_2_pos['x']))

    ramp_1_rot = ramp_1['shows'][0]['rotation']['y']
    ramp_2_rot = ramp_2['shows'][0]['rotation']['y']
    assert abs(abs(ramp_1_rot) - abs(ramp_2_rot)) == 180


def test_platform_long_with_two_ramps_times_stacked():
    scene = prior_scene()
    scene.room_dimensions.x = 25
    scene.room_dimensions.y = 8
    scene.room_dimensions.z = 25

    # lips, attached_ramps, and platform_underneath_attached_ramps
    # will be overrided
    temp = StructuralPlatformConfig(
        num=1,
        position=VectorFloatConfig(1, 2, 3),
        rotation_y=0,
        scale=1,
        material="AI2-THOR/Materials/Ceramics/BrownMarbleFake 1",
        lips=StructuralPlatformLipsConfig(False, False, False, False),
        attached_ramps=1,
        platform_underneath=True,
        platform_underneath_attached_ramps=3,
        long_with_two_ramps=True
    )

    # Sometimes it cannot generate a valid scene when stacking the platforms
    # but it usually works on the second or third try
    valid = False
    for _ in range(MAX_TRIES):
        try:
            platform_two_ramps = StructuralPlatformCreationService(
            ).create_feature_from_specific_values(scene, temp, None)
        except Exception:
            continue

        assert len(platform_two_ramps) == 6
        assert platform_two_ramps[0]['shows'][0]['position']['y'] > \
            platform_two_ramps[1]['shows'][0]['position']['y']
        for i in range(2):
            plat = platform_two_ramps[i]
            ramp_1 = platform_two_ramps[i * 2 + 2]
            ramp_2 = platform_two_ramps[i * 2 + 3]
            assert plat['id'].startswith('platform_')
            assert ramp_1['id'].startswith('ramp_')
            assert ramp_2['id'].startswith('ramp_')

            plat_scale = plat['shows'][0]['scale']
            plat_pos = plat['shows'][0]['position']
            long_x = plat_scale['x'] > plat_scale['z']
            assert (plat_scale['x'] == scene.room_dimensions.x if
                    long_x else plat_scale['x'] == 1 if i == 0 else
                    plat_scale['x'] > 1)
            assert (
                plat_scale['z'] == scene.room_dimensions.z if not
                long_x else plat_scale['z'] == 1 if i == 0 else
                plat_scale['z'] > 1)
            assert plat_pos['x'] == 0 if long_x else plat_pos['x'] == 1
            assert plat_pos['z'] == 0 if not long_x else plat_pos['z'] == 3

            lips = plat['lips']
            assert (lips['front'] and lips['back'] and
                    lips['left'] and lips['right'])
            assert (lips['gaps']['front'] and lips['gaps']['back'] if
                    long_x else lips['gaps']['left'] and lips['gaps']['right'])

            ramp_1_pos = ramp_1['shows'][0]['position']
            ramp_2_pos = ramp_2['shows'][0]['position']
            assert (
                round(ramp_1_pos['z']) < round(ramp_2_pos['z']) if long_x else
                round(ramp_1_pos['x']) < round(ramp_2_pos['x']))

            ramp_1_rot = ramp_1['shows'][0]['rotation']['y']
            ramp_2_rot = ramp_2['shows'][0]['rotation']['y']
            assert abs(abs(ramp_1_rot) - abs(ramp_2_rot)) == 180
        valid = True
        break
    assert valid


def test_platform_adjacent_to_wall():
    scene = prior_scene()
    x = 10
    z = 8
    scene.room_dimensions.x = x
    scene.room_dimensions.y = 4
    scene.room_dimensions.z = z
    pos_x = 1
    pos_z = 3
    scale = 1
    half_scale = scale / 2
    for side in WALL_SIDES:
        temp = StructuralPlatformConfig(
            num=1,
            position=VectorFloatConfig(pos_x, 2, pos_z),
            rotation_y=0,
            scale=scale,
            material="AI2-THOR/Materials/Ceramics/BrownMarbleFake 1",
            lips=StructuralPlatformLipsConfig(False, False, False, False),
            attached_ramps=1,
            platform_underneath=False,
            platform_underneath_attached_ramps=0,
            adjacent_to_wall=[side]
        )
        platform_adjacent_to_wall = StructuralPlatformCreationService(
        ).create_feature_from_specific_values(scene, temp, None)
        side_x = -1 if 'left' in side else 1 if 'right' in side else 0
        side_z = -1 if 'back' in side else 1 if 'front' in side else 0
        plat = platform_adjacent_to_wall[0]
        ramp = platform_adjacent_to_wall[1]
        plat_pos = plat['shows'][0]['position']
        ramp_pos = ramp['shows'][0]['position']
        if side_x:
            assert plat_pos['x'] == side_x * (x / 2 - half_scale)
            assert (ramp_pos['x'] > side_x * (x / 2 + half_scale) if
                    side_x == -1 else
                    ramp_pos['x'] < side_x * (x / 2 + half_scale))
            assert ramp['shows'][0]['rotation']['y'] != -side_x * 90
        else:
            plat_pos['x'] == pos_x
        if side_z:
            assert plat_pos['z'] == side_z * (z / 2 - half_scale)
            assert (ramp_pos['z'] > side_z * (z / 2 + half_scale) if
                    side_z == -1 else
                    ramp_pos['z'] < side_z * (z / 2 + half_scale))
            assert abs(ramp['shows'][0]['rotation']['y']) != (
                0 if side_z == -1 else 180)
        else:
            plat_pos['z'] == pos_z


def test_platform_stacked_adjacent_to_wall():
    scene = prior_scene()
    x = 10
    z = 8
    scene.room_dimensions.x = x
    scene.room_dimensions.y = 4
    scene.room_dimensions.z = z
    pos_x = 1
    pos_z = 3
    scale = 1
    for side in WALL_SIDES:
        temp = StructuralPlatformConfig(
            num=1,
            position=VectorFloatConfig(pos_x, 2, pos_z),
            rotation_y=0,
            scale=scale,
            material="AI2-THOR/Materials/Ceramics/BrownMarbleFake 1",
            lips=StructuralPlatformLipsConfig(False, False, False, False),
            attached_ramps=1,
            platform_underneath=True,
            platform_underneath_attached_ramps=1,
            adjacent_to_wall=[side]
        )
        platform_adjacent_to_wall = StructuralPlatformCreationService(
        ).create_feature_from_specific_values(scene, temp, None)
        side_x = -1 if 'left' in side else 1 if 'right' in side else 0
        side_z = -1 if 'back' in side else 1 if 'front' in side else 0
        for i in range(2):
            plat = platform_adjacent_to_wall[i]
            ramp = platform_adjacent_to_wall[i + 2]
            plat_pos = plat['shows'][0]['position']
            ramp_pos = ramp['shows'][0]['position']
            half_scale_x = plat['shows'][0]['scale']['x'] / 2
            half_scale_z = plat['shows'][0]['scale']['z'] / 2
            # Check a different scale if the platform is rotated
            # 90 or 270 degrees
            scale_check_x = half_scale_z if abs(
                plat['shows'][0]['rotation']['y']) % 180 != 0 else half_scale_x
            scale_check_z = half_scale_x if abs(
                plat['shows'][0]['rotation']['y']) % 180 != 0 else half_scale_z
            if side_x:
                assert round(plat_pos['x'], 3) == round(
                    side_x * (x / 2 - scale_check_x), 3)
                assert (ramp_pos['x'] > side_x * (x / 2 + scale_check_x) if
                        side_x == -1 else
                        ramp_pos['x'] < side_x * (x / 2 + scale_check_x))
                assert ramp['shows'][0]['rotation']['y'] != -side_x * 90
            else:
                plat_pos['x'] == pos_x
            if side_z:
                assert round(plat_pos['z'], 2) == round(
                    side_z * (z / 2 - scale_check_z), 2)
                assert (ramp_pos['z'] > side_z * (z / 2 + scale_check_z) if
                        side_z == -1 else
                        ramp_pos['z'] < side_z * (z / 2 + scale_check_z))
                assert abs(ramp['shows'][0]['rotation']['y']) != (
                    0 if side_z == -1 else 180)
            else:
                plat_pos['z'] == pos_z
