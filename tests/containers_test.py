import copy

import pytest
from machine_common_sense.config_manager import Vector3d

from generator import (
    ObjectDefinition,
    ObjectInteractableArea,
    definitions,
    geometry,
    instances,
    specific_objects
)
from generator.containers import (
    can_contain,
    can_contain_both,
    can_enclose,
    put_object_in_container,
    put_objects_in_container,
    shift_lid_positions_based_on_movement
)

DEFAULT_CONTAINER = definitions.finalize_object_definition(ObjectDefinition(
    type='box',
    attributes=['receptacle', 'openable'],
    dimensions=Vector3d(x=1, y=1, z=1),
    scale=Vector3d(x=1, y=1, z=1),
    enclosedAreas=[ObjectInteractableArea(
        area_id='',
        dimensions=Vector3d(x=1, y=1, z=1),
        position=Vector3d(x=0, y=0.5, z=0)
    ).to_dict()]
))


PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS = [
    'dog_on_wheels_2',
    'duck_on_wheels', 'chair_1', 'chair_2', 'table_1', 'table_3', 'shelf_1'
]


CONTAINERS = specific_objects.get_container_openable_definition_dataset(
    unshuffled=True
)
CONTAINER_DEFINITIONS = CONTAINERS.definitions_unique_shape_scale()


PICKUPABLES = specific_objects.get_pickupable_definition_dataset(
    unshuffled=True
)
PICKUPABLE_DEFINITIONS = PICKUPABLES.definitions_unique_shape_scale()


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
        print(f'\nOBJECT={obj_def.type} {obj_def.scale}')
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
            print(f'CONTAINER={container_def.type} {container_def.scale}')
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
    small = ObjectDefinition(dimensions=Vector3d(x=1, y=1, z=1))
    big = ObjectDefinition(dimensions=Vector3d(x=42, y=42, z=42))
    assert can_enclose({'dimensions': vars(big.dimensions)}, small) is not None
    assert can_enclose({'dimensions': vars(small.dimensions)}, big) is None


def test_can_contain():
    small1 = ObjectDefinition(dimensions=Vector3d(x=0.01, y=0.01, z=0.01))
    small2 = ObjectDefinition(dimensions=Vector3d(x=0.02, y=0.02, z=0.02))
    big = ObjectDefinition(dimensions=Vector3d(x=42, y=42, z=42))
    container_def = copy.deepcopy(DEFAULT_CONTAINER)
    assert can_contain(container_def, small1, small2) is not None
    assert can_contain(container_def, small1, big) is None
    assert can_contain(container_def, small1) is not None
    assert can_contain(container_def, big) is None


def test_can_contain_both():
    small1 = ObjectDefinition(dimensions=Vector3d(x=0.01, y=0.01, z=0.01))
    small2 = ObjectDefinition(dimensions=Vector3d(x=0.02, y=0.02, z=0.02))
    big = ObjectDefinition(dimensions=Vector3d(x=42, y=42, z=42))
    container_def = copy.deepcopy(DEFAULT_CONTAINER)
    assert can_contain_both(container_def, small1, small2) is not None
    assert can_contain_both(container_def, small1, big) is None


def test_containers():
    assert len(CONTAINER_DEFINITIONS) > 0
    for container_definition in CONTAINER_DEFINITIONS:
        assert len(container_definition.enclosedAreas)
        for enclosed_area in container_definition.enclosedAreas:
            dimensions = enclosed_area['dimensions']
            position = enclosed_area['position']
            # The position of the bottom of an object inside the enclosed area
            # should be greater than half the enclosed area's height so it
            # includes the base of the container itself.
            assert (dimensions['y'] / 2.0) < position['y']


def test_shift_lid_positions_based_on_movement():
    """
    Makes 3 separate instances of containers with separate lids and placers.
    Containers have unique rotations and move vectors global and local based.
    """
    objects = [{
        "id": "container_1",
        "type": "separate_container",
        "debug": {
            'lidId': "lid_1",
            'lidPlacerId': "placer_1"
        },
        "shows": [{
            "position": {
                "x": 0,
                "y": 0.0,
                "z": 0
            },
            "rotation": {
                "x": 0,
                "y": 45,
                "z": 0
            }
        }],
        "moves": [{
            "stepBegin": 1,
            "stepEnd": 12,
            "globalSpace": True,
            "vector": {
                "x": 0.135,
                "y": 0,
                "z": 0
            }
        }, {
            "stepBegin": 16,
            "stepEnd": 23,
            "vector": {
                "x": 0,
                "y": 0,
                "z": -0.175
            }
        }, {
            "stepBegin": 21,
            "stepEnd": 27,
            "globalSpace": True,
            "vector": {
                "x": -0.125,
                "y": 0,
                "z": 0.15
            }
        }, {
            "stepBegin": 55,
            "stepEnd": 62,
            "vector": {
                "x": 0.2,
                "y": 0,
                "z": 0.1
            }
        }]
    }, {
        "id": "lid_1",
        "type": "lid",
        "shows": [{
            "position": {
                "x": 0,
                "y": 4.4,
                "z": 0
            },
            "rotation": {
                "x": 0,
                "y": 45,
                "z": 0
            }
        }],
        "lidAttachment": {
            "stepBegin": 32,
            "lidAttachmentObjId": "container_1"
        },
    },
        {
        "id": "placer_1",
        "type": "cylinder",
        "shows": [{
            "position": {
                "x": 0,
                "y": 6.325,
                "z": 0
            },
        }],
    }, {
        "id": "container_2",
        "type": "separate_container",
        "debug": {
            'lidId': "lid_2",
            'lidPlacerId': "placer_2"
        },
        "shows": [{
            "position": {
                "x": -1,
                "y": 0.0,
                "z": 1
            },
            "rotation": {
                "x": 0,
                "y": -33,
                "z": 0
            }
        }],
        "moves": [{
            "stepBegin": 1,
            "stepEnd": 10,
            "globalSpace": True,
            "vector": {
                "x": 0.15,
                "y": 0,
                "z": 0
            }
        }, {
            "stepBegin": 25,
            "stepEnd": 26,
            "globalSpace": True,
            "vector": {
                "x": 0.125,
                "y": 0,
                "z": 0.175
            }
        }, {
            "stepBegin": 55,
            "stepEnd": 62,
            "vector": {
                "x": 0.2,
                "y": 0,
                "z": 0.15
            }
        }]
    }, {
        "id": "lid_2",
        "type": "lid",
        "shows": [{
            "position": {
                "x": 0,
                "y": 4.4,
                "z": 0
            },
            "rotation": {
                "x": 0,
                "y": 45,
                "z": 0
            }
        }],
        "lidAttachment": {
            "stepBegin": 28,
            "lidAttachmentObjId": "container_2"
        },
    },
        {
        "id": "placer_2",
        "type": "cylinder",
        "shows": [{
            "position": {
                "x": 0,
                "y": 6.325,
                "z": 0
            },
        }],
    }, {
        "id": "container_3",
        "type": "separate_container",
        "debug": {
            'lidId': "lid_3",
            'lidPlacerId': "placer_3"
        },
        "shows": [{
            "position": {
                "x": 1,
                "y": 0.0,
                "z": -1
            },
            "rotation": {
                "x": 0,
                "y": 123,
                "z": 0
            }
        }],
        "moves": [{
            "stepBegin": 1,
            "stepEnd": 15,
            "globalSpace": True,
            "vector": {
                "x": -0.135,
                "y": 0,
                "z": 0
            }
        }, {
            "stepBegin": 16,
            "stepEnd": 20,
            "vector": {
                "x": 0,
                "y": 0,
                "z": 0.175
            }
        }, {
            "stepBegin": 22,
            "stepEnd": 24,
            "vector": {
                "x": 0,
                "y": 0,
                "z": 0.175
            }
        }, {
            "stepBegin": 25,
            "stepEnd": 27,
            "globalSpace": True,
            "vector": {
                "x": 0.125,
                "y": 0,
                "z": 0.15
            }
        }, {
            "stepBegin": 50,
            "stepEnd": 57,
            "vector": {
                "x": 0.15,
                "y": 0,
                "z": -0.19
            }
        }]
    }, {
        "id": "lid_3",
        "type": "lid",
        "shows": [{
            "position": {
                "x": 0,
                "y": 4.4,
                "z": 0
            },
            "rotation": {
                "x": 0,
                "y": 45,
                "z": 0
            }
        }],
        "lidAttachment": {
            "stepBegin": 63,
            "lidAttachmentObjId": "container_3"
        },
    },
        {
        "id": "placer_3",
        "type": "cylinder",
        "shows": [{
            "position": {
                "x": 0,
                "y": 6.325,
                "z": 0
            },
        }],
    }]

    objects = shift_lid_positions_based_on_movement(objects)

    # lid_1 placer_1
    assert round(objects[1]['shows'][0]['position']['x'], 4) == -0.2449
    assert round(objects[1]['shows'][0]['position']['z'], 4) == 0.0601
    assert round(objects[2]['shows'][0]['position']['x'], 4) == -0.2449
    assert round(objects[2]['shows'][0]['position']['z'], 4) == 0.0601

    # lid_2 placer_2
    assert round(objects[4]['shows'][0]['position']['x'], 4) == 0.75
    assert round(objects[4]['shows'][0]['position']['z'], 4) == 1.35
    assert round(objects[5]['shows'][0]['position']['x'], 4) == 0.75
    assert round(objects[5]['shows'][0]['position']['z'], 4) == 1.35

    # lid_3 placer_3
    assert round(objects[7]['shows'][0]['position']['x'], 4) == -1.4042
    assert round(objects[7]['shows'][0]['position']['z'], 4) == -1.491
    assert round(objects[8]['shows'][0]['position']['x'], 4) == -1.4042
    assert round(objects[8]['shows'][0]['position']['z'], 4) == -1.491
