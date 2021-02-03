import pytest

import geometry
import objects
import util
from containers import put_object_in_container, put_objects_in_container, \
    can_enclose, can_contain_both, can_contain
from geometry import are_adjacent


DEFAULT_CONTAINER = {
    'type': 'box',
    'attributes': ['receptacle', 'openable'],
    'dimensions': {
        'x': 1,
        'y': 1,
        'z': 1
    },
    'mass': 1,
    'scale': {
        'x': 1,
        'y': 1,
        'z': 1
    },
    'enclosedAreas': [{
        'position': {
            'x': 0,
            'y': 0.5,
            'z': 0
        },
        'dimensions': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }]
}


PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS = [
    'duck_on_wheels', 'chair_1', 'chair_2', 'table_1', 'table_3'
]


CONTAINER_DEFINITIONS = [
    definition for definition_list in util.retrieve_complete_definition_list(
        objects.get(objects.ObjectDefinitionList.CONTAINERS)
    ) for definition in definition_list
]


PICKUPABLE_DEFINITIONS = [
    definition for definition_list in util.retrieve_complete_definition_list(
        objects.get(objects.ObjectDefinitionList.PICKUPABLES)
    ) for definition in definition_list
]


def get_valid_containments(object_a, object_b=None):
    valid_containments = []
    for definition in CONTAINER_DEFINITIONS:
        if object_b:
            containment = can_contain_both(definition, object_a, object_b)
        else:
            containment = can_contain(definition, object_a)
        if containment:
            valid_containments.append((definition, containment))
    return valid_containments


def test_put_object_in_container():
    for obj_def in PICKUPABLE_DEFINITIONS:
        print(f'\nOBJECT={obj_def}')
        obj_location = geometry.calc_obj_pos(
            {'x': 1, 'y': 0, 'z': 1}, [], obj_def)
        obj = util.instantiate_object(obj_def, obj_location)
        obj_bounds = obj['shows'][0]['boundingBox']

        containments = get_valid_containments(obj_def)
        if (
            len(containments) == 0 and
            not obj_def.get('enclosedAreas', []) and
            obj_def['type'] not in PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS
        ):
            print(
                f'pickupable object should have at least one containment: '
                f'{obj_def}'
            )
            assert False

        for container_def, containment in containments:
            area_index, rotations = containment
            container_location = geometry.calc_obj_pos(
                {'x': -1, 'y': 0, 'z': -1}, [], container_def)
            container = util.instantiate_object(
                container_def, container_location)

            put_object_in_container(obj, container, area_index, rotations[0])

            assert obj['locationParent'] == container['id']
            assert (
                obj['shows'][0]['position']['x'] ==
                container_def['enclosedAreas'][0]['position']['x']
            )
            expected_position_y = (
                container_def['enclosedAreas'][0]['position']['y'] -
                obj_def.get('offset', {}).get('y', 0) -
                (container_def['enclosedAreas'][area_index]['dimensions']['y'] / 2.0) +  # noqa: E501
                obj_def.get('positionY', 0)
            )
            assert obj['shows'][0]['position']['y'] == pytest.approx(
                expected_position_y)
            assert (
                obj['shows'][0]['position']['z'] ==
                container_def['enclosedAreas'][0]['position']['z']
            )
            assert obj['shows'][0]['rotation']
            assert obj['shows'][0]['boundingBox']
            assert obj['shows'][0]['boundingBox'] != obj_bounds


def test_put_objects_in_container():
    for obj_a_def in PICKUPABLE_DEFINITIONS:
        print(f'\nOBJECT_A={obj_a_def}')
        obj_a_location = geometry.calc_obj_pos(geometry.ORIGIN, [], obj_a_def)
        obj_a = util.instantiate_object(obj_a_def, obj_a_location)
        obj_a_bounds = obj_a['shows'][0]['boundingBox']

        for obj_b_def in PICKUPABLE_DEFINITIONS:
            print(f'\nOBJECT_B={obj_b_def}')
            obj_b_location = geometry.calc_obj_pos(
                geometry.ORIGIN, [], obj_b_def)
            obj_b = util.instantiate_object(obj_b_def, obj_b_location)
            obj_b_bounds = obj_b['shows'][0]['boundingBox']

            containments = get_valid_containments(obj_a_def, obj_b_def)
            if (
                len(containments) == 0 and
                not obj_a_def.get('enclosedAreas', []) and
                not obj_b_def.get('enclosedAreas', []) and
                obj_a_def['type'] not in
                PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS and
                obj_b_def['type'] not in
                PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS
            ):
                print(
                    f'pair of pickupable objects should have at least one '
                    f'containment:\nobject_a={obj_a_def}\n'
                    f'object_b={obj_b_def}')
                assert False

            for container_def, containment in containments:
                area_index, rotations, orientation = containment
                container_location = geometry.calc_obj_pos(
                    geometry.ORIGIN, [], container_def)
                container = util.instantiate_object(
                    container_def, container_location)

                put_objects_in_container(obj_a, obj_b,
                                         container, area_index,
                                         orientation,
                                         rotations[0], rotations[1])
                assert obj_a['locationParent'] == container['id']
                assert obj_b['locationParent'] == container['id']
                assert obj_a['shows'][0]['boundingBox']
                assert obj_b['shows'][0]['boundingBox']
                assert obj_a['shows'][0]['boundingBox'] != obj_a_bounds
                assert obj_b['shows'][0]['boundingBox'] != obj_b_bounds
                assert are_adjacent(obj_a, obj_b)


def test_can_enclose():
    small = {
        'dimensions': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }
    big = {
        'dimensions': {
            'x': 42,
            'y': 42,
            'z': 42
        }
    }
    assert can_enclose(big, small) is not None
    assert can_enclose(small, big) is None


def test_can_contain():
    small1 = {
        'dimensions': {
            'x': 0.01,
            'y': 0.01,
            'z': 0.01
        }
    }
    small2 = {
        'dimensions': {
            'x': 0.02,
            'y': 0.02,
            'z': 0.02
        }
    }
    big = {
        'dimensions': {
            'x': 42,
            'y': 42,
            'z': 42
        }
    }
    container_def = util.finalize_object_definition(DEFAULT_CONTAINER)
    assert can_contain(container_def, small1, small2) is not None
    assert can_contain(container_def, small1, big) is None
    assert can_contain(container_def, small1) is not None
    assert can_contain(container_def, big) is None


def test_can_contain_both():
    small1 = {
        'dimensions': {
            'x': 0.01,
            'y': 0.01,
            'z': 0.01
        }
    }
    small2 = {
        'dimensions': {
            'x': 0.02,
            'y': 0.02,
            'z': 0.02
        }
    }
    big = {
        'dimensions': {
            'x': 42,
            'y': 42,
            'z': 42
        }
    }
    container_def = util.finalize_object_definition(DEFAULT_CONTAINER)
    assert can_contain_both(container_def, small1, small2) is not None
    assert can_contain_both(container_def, small1, big) is None


def test_containers():
    assert len(CONTAINER_DEFINITIONS) > 0
