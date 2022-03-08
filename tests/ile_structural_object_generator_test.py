import pytest

from ideal_learning_env.object_services import (
    InstanceDefinitionLocationTuple,
    ObjectRepository,
)
from ideal_learning_env.structural_object_generator import is_wall_too_close


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
