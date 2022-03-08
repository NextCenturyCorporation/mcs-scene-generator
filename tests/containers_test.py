import copy

import pytest
from machine_common_sense.config_manager import Vector3d

from generator import (
    ObjectDefinition,
    ObjectInteractableArea,
    definitions,
    geometry,
    instances,
    specific_objects,
)
from generator.containers import (
    can_contain,
    can_contain_both,
    can_enclose,
    put_object_in_container,
    put_objects_in_container,
)

DEFAULT_CONTAINER = definitions.finalize_object_definition(ObjectDefinition(
    type='box',
    attributes=['receptacle', 'openable'],
    dimensions=Vector3d(1, 1, 1),
    scale=Vector3d(1, 1, 1),
    enclosedAreas=[ObjectInteractableArea(
        area_id='',
        dimensions=Vector3d(1, 1, 1),
        position=Vector3d(0, 0.5, 0)
    ).to_dict()]
))


PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS = [
    'duck_on_wheels', 'chair_1', 'chair_2', 'table_1', 'table_3', 'shelf_1'
]


CONTAINERS = specific_objects.get_container_definition_dataset(unshuffled=True)
CONTAINER_DEFINITIONS = [
    # Just use the first variation (color) of each object for faster testing.
    definition_variations[0]
    for definition_selections in CONTAINERS._definition_groups
    for definition_variations in definition_selections
]


PICKUPABLES = specific_objects.get_pickupable_definition_dataset(
    unshuffled=True
)
PICKUPABLE_DEFINITIONS = [
    # Just use the first variation (color) of each object for faster testing.
    definition_variations[0]
    for definition_selections in PICKUPABLES._definition_groups
    for definition_variations in definition_selections
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


@pytest.mark.slow
def test_put_object_in_container():
    for obj_def in PICKUPABLE_DEFINITIONS:
        print(f'\nOBJECT={obj_def}')
        obj_location = geometry.calc_obj_pos(
            {'x': 1, 'y': 0, 'z': 1}, [], obj_def)
        obj = instances.instantiate_object(obj_def, obj_location)
        obj_bounds = obj['shows'][0]['boundingBox']

        containments = get_valid_containments(obj_def)
        if (
            len(containments) == 0 and not obj_def.enclosedAreas and
            obj_def.type not in PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS
        ):
            print(
                f'pickupable object should have at least one containment: '
                f'{obj_def}'
            )
            assert False

        for container_def, containment in containments:
            print(f'\nCONTAINER={container_def}')
            area_index, rotations = containment
            container_location = geometry.calc_obj_pos(
                {'x': -1, 'y': 0, 'z': -1}, [], container_def)
            container = instances.instantiate_object(
                container_def, container_location)

            put_object_in_container(obj, container, area_index, rotations[0])

            enclosed_area = container_def.enclosedAreas[area_index]
            assert obj['locationParent'] == container['id']
            assert (
                obj['shows'][0]['position']['x'] ==
                enclosed_area['position']['x']
            )
            expected_position_y = (
                enclosed_area['position']['y'] -
                (enclosed_area['dimensions']['y'] / 2.0) + obj_def.positionY
            )
            assert (
                obj['shows'][0]['position']['y'] ==
                pytest.approx(expected_position_y)
            )
            assert (
                obj['shows'][0]['position']['z'] ==
                enclosed_area['position']['z']
            )
            assert obj['shows'][0]['rotation']
            assert obj['shows'][0]['boundingBox']
            assert obj['shows'][0]['boundingBox'] != obj_bounds


@pytest.mark.skip(reason="Runs very slowly and is not currently needed")
def test_put_objects_in_container():
    for obj_a_def in PICKUPABLE_DEFINITIONS:
        print(f'\nOBJECT_A={obj_a_def}')
        obj_a_location = geometry.calc_obj_pos(geometry.ORIGIN, [], obj_a_def)
        obj_a = instances.instantiate_object(obj_a_def, obj_a_location)
        obj_a_bounds = obj_a['shows'][0]['boundingBox']

        for obj_b_def in PICKUPABLE_DEFINITIONS:
            print(f'\nOBJECT_B={obj_b_def}')
            obj_b_location = geometry.calc_obj_pos(
                geometry.ORIGIN, [], obj_b_def)
            obj_b = instances.instantiate_object(obj_b_def, obj_b_location)
            obj_b_bounds = obj_b['shows'][0]['boundingBox']

            containments = get_valid_containments(obj_a_def, obj_b_def)
            if (
                len(containments) == 0 and
                not obj_a_def.enclosedAreas and
                not obj_b_def.enclosedAreas and
                obj_a_def.type not in
                PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS and
                obj_b_def.type not in
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
                container = instances.instantiate_object(
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
                assert geometry.are_adjacent(obj_a, obj_b)


def test_can_enclose():
    small = ObjectDefinition(dimensions=Vector3d(1, 1, 1))
    big = ObjectDefinition(dimensions=Vector3d(42, 42, 42))
    assert can_enclose({'dimensions': vars(big.dimensions)}, small) is not None
    assert can_enclose({'dimensions': vars(small.dimensions)}, big) is None


def test_can_contain():
    small1 = ObjectDefinition(dimensions=Vector3d(0.01, 0.01, 0.01))
    small2 = ObjectDefinition(dimensions=Vector3d(0.02, 0.02, 0.02))
    big = ObjectDefinition(dimensions=Vector3d(42, 42, 42))
    container_def = copy.deepcopy(DEFAULT_CONTAINER)
    assert can_contain(container_def, small1, small2) is not None
    assert can_contain(container_def, small1, big) is None
    assert can_contain(container_def, small1) is not None
    assert can_contain(container_def, big) is None


def test_can_contain_both():
    small1 = ObjectDefinition(dimensions=Vector3d(0.01, 0.01, 0.01))
    small2 = ObjectDefinition(dimensions=Vector3d(0.02, 0.02, 0.02))
    big = ObjectDefinition(dimensions=Vector3d(42, 42, 42))
    container_def = copy.deepcopy(DEFAULT_CONTAINER)
    assert can_contain_both(container_def, small1, small2) is not None
    assert can_contain_both(container_def, small1, big) is None


def test_containers():
    assert len(CONTAINER_DEFINITIONS) > 0
