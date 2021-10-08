from generator import base_objects, definitions, specific_objects, util
from hypercube import (
    ObjectData,
    ObjectLocationPlan,
    ObjectPlan,
    ReceptacleData,
    TargetData,
)
from hypercube.object_data import identify_larger_definition

SOFA_1 = specific_objects._get('SOFA_1')
SOFA_1 = definitions.finalize_object_definition(SOFA_1)
SOCCER_BALL = base_objects.create_soccer_ball()


CASE_1_SUITCASE = specific_objects._get('CASE_1_SUITCASE')
CASE_1_SUITCASE = definitions.finalize_object_definition(
    CASE_1_SUITCASE,
    choice_size=CASE_1_SUITCASE.chooseSizeList[0]
)
CHEST_1_CUBOID = specific_objects._get('CHEST_1_CUBOID')
CHEST_1_CUBOID = definitions.finalize_object_definition(
    CHEST_1_CUBOID,
    choice_size=CHEST_1_CUBOID.chooseSizeList[0]
)


def test_identify_larger_definition():
    assert identify_larger_definition(SOFA_1, SOCCER_BALL) == SOFA_1
    assert identify_larger_definition(SOCCER_BALL, SOFA_1) == SOFA_1


def test_object_data_init():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    assert data.role == 'ROLE'
    assert data.location_plan_list == [ObjectLocationPlan.NONE]
    assert data.untrained_plan_list == [False]
    assert not data.original_definition
    assert not data.trained_definition
    assert not data.untrained_definition
    assert not data.trained_template
    assert not data.untrained_template
    assert data.instance_list == [None]

    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.RANDOM, True))
    assert data.role == 'ROLE'
    assert data.location_plan_list == [ObjectLocationPlan.RANDOM]
    assert data.untrained_plan_list == [True]
    assert not data.original_definition
    assert not data.trained_definition
    assert not data.untrained_definition
    assert not data.trained_template
    assert not data.untrained_template
    assert data.instance_list == [None]

    data = ObjectData('ROLE', ObjectPlan(
        ObjectLocationPlan.INSIDE_0,
        definition=SOCCER_BALL
    ))
    assert data.role == 'ROLE'
    assert data.location_plan_list == [ObjectLocationPlan.INSIDE_0]
    assert data.untrained_plan_list == [False]
    assert data.original_definition.type == 'soccer_ball'
    assert data.trained_definition.type == 'soccer_ball'
    assert data.untrained_definition.type == 'soccer_ball'
    assert not data.trained_template
    assert not data.untrained_template
    assert data.instance_list == [None]


def test_append_object_plan():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    data.append_object_plan(ObjectPlan(ObjectLocationPlan.RANDOM))
    assert data.location_plan_list == [
        ObjectLocationPlan.NONE, ObjectLocationPlan.RANDOM
    ]
    assert data.untrained_plan_list == [False, False]
    data.append_object_plan(ObjectPlan(ObjectLocationPlan.RANDOM, True))
    assert data.location_plan_list == [
        ObjectLocationPlan.NONE, ObjectLocationPlan.RANDOM,
        ObjectLocationPlan.RANDOM
    ]
    assert data.untrained_plan_list == [False, False, True]


def create_assign_location_test_data():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    data.location_plan_list = [
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.BACK,
        ObjectLocationPlan.BETWEEN,
        ObjectLocationPlan.CLOSE,
        ObjectLocationPlan.FAR,
        ObjectLocationPlan.FRONT,
        ObjectLocationPlan.INSIDE_0,
        ObjectLocationPlan.RANDOM,
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.BACK,
        ObjectLocationPlan.BETWEEN,
        ObjectLocationPlan.CLOSE,
        ObjectLocationPlan.FAR,
        ObjectLocationPlan.FRONT,
        ObjectLocationPlan.INSIDE_0,
        ObjectLocationPlan.RANDOM
    ]
    data.untrained_plan_list = [
        False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False
    ]
    data.instance_list = [
        None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None
    ]
    data.trained_definition = SOCCER_BALL
    data.trained_template = util.instantiate_object(data.trained_definition, {
        'position': {'x': 0, 'y': 0, 'z': 0},
        'rotation': {'x': 0, 'y': 0, 'z': 0}
    })
    return data


def test_assign_location_back():
    data = create_assign_location_test_data()
    data.assign_location_back({
        'position': {'x': 1, 'y': 0, 'z': 3},
        'rotation': {'x': 0, 'y': 5, 'z': 0}
    })
    for index, instance in enumerate(data.instance_list):
        if index in [1, 9]:
            assert instance
            assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 3}
            assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 5, 'z': 0}
        else:
            assert not instance


def test_assign_location_between():
    data = create_assign_location_test_data()
    data.assign_location_between({
        'position': {'x': 1, 'y': 0, 'z': 3},
        'rotation': {'x': 0, 'y': 5, 'z': 0}
    }, [2])
    for index, instance in enumerate(data.instance_list):
        if index in [2]:
            assert instance
            assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 3}
            assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 5, 'z': 0}
        else:
            assert not instance

    data = create_assign_location_test_data()
    data.assign_location_between({
        'position': {'x': 1, 'y': 0, 'z': 3},
        'rotation': {'x': 0, 'y': 5, 'z': 0}
    }, [2, 10])
    for index, instance in enumerate(data.instance_list):
        if index in [2, 10]:
            assert instance
            assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 3}
            assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 5, 'z': 0}
        else:
            assert not instance


def test_assign_location_close():
    data = create_assign_location_test_data()
    data.assign_location_close({
        'position': {'x': 1, 'y': 0, 'z': 3},
        'rotation': {'x': 0, 'y': 5, 'z': 0}
    }, [3])
    for index, instance in enumerate(data.instance_list):
        if index in [3]:
            assert instance
            assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 3}
            assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 5, 'z': 0}
        else:
            assert not instance

    data = create_assign_location_test_data()
    data.assign_location_close({
        'position': {'x': 1, 'y': 0, 'z': 3},
        'rotation': {'x': 0, 'y': 5, 'z': 0}
    }, [3, 11])
    for index, instance in enumerate(data.instance_list):
        if index in [3, 11]:
            assert instance
            assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 3}
            assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 5, 'z': 0}
        else:
            assert not instance


def test_assign_location_far():
    data = create_assign_location_test_data()
    data.assign_location_far({
        'position': {'x': 1, 'y': 0, 'z': 3},
        'rotation': {'x': 0, 'y': 5, 'z': 0}
    }, [4])
    for index, instance in enumerate(data.instance_list):
        if index in [4]:
            assert instance
            assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 3}
            assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 5, 'z': 0}
        else:
            assert not instance

    data = create_assign_location_test_data()
    data.assign_location_far({
        'position': {'x': 1, 'y': 0, 'z': 3},
        'rotation': {'x': 0, 'y': 5, 'z': 0}
    }, [4, 12])
    for index, instance in enumerate(data.instance_list):
        if index in [4, 12]:
            assert instance
            assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 3}
            assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 5, 'z': 0}
        else:
            assert not instance


def test_assign_location_front():
    data = create_assign_location_test_data()
    data.assign_location_front({
        'position': {'x': 1, 'y': 0, 'z': 3},
        'rotation': {'x': 0, 'y': 5, 'z': 0}
    })
    for index, instance in enumerate(data.instance_list):
        if index in [5, 13]:
            assert instance
            assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 3}
            assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 5, 'z': 0}
        else:
            assert not instance


def test_assign_location_random():
    data = create_assign_location_test_data()
    data.assign_location_random({
        'position': {'x': 1, 'y': 0, 'z': 3},
        'rotation': {'x': 0, 'y': 5, 'z': 0}
    })
    for index, instance in enumerate(data.instance_list):
        if index in [7, 15]:
            assert instance
            assert instance['shows'][0]['position'] == {'x': 1, 'y': 0, 'z': 3}
            assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 5, 'z': 0}
        else:
            assert not instance


def test_contained_indexes():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    container_data = ReceptacleData(
        'LARGE_CONTAINER',
        ObjectPlan(ObjectLocationPlan.NONE)
    )
    assert data.contained_indexes([container_data]) == []

    data.location_plan_list = [
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.INSIDE_0,
        ObjectLocationPlan.RANDOM,
        ObjectLocationPlan.INSIDE_0
    ]
    assert data.contained_indexes([container_data]) == [
        (1, container_data, None), (3, container_data, None)
    ]

    confusor_data = ObjectData('CONFUSOR', ObjectPlan(ObjectLocationPlan.NONE))
    confusor_data.location_plan_list = [
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.NONE
    ]
    assert data.contained_indexes([container_data], confusor_data) == [
        (1, container_data, None), (3, container_data, None)
    ]

    confusor_data.location_plan_list = [
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.INSIDE_0
    ]
    assert data.contained_indexes([container_data], confusor_data) == [
        (1, container_data, None), (3, container_data, confusor_data)
    ]


def test_containerize_with():
    data_1 = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    assert not data_1.containerize_with(None)

    data_1.location_plan_list = [
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.INSIDE_0,
        ObjectLocationPlan.RANDOM,
        ObjectLocationPlan.INSIDE_0
    ]
    assert not data_1.containerize_with(None)

    data_2 = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    data_2.location_plan_list = [
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.NONE
    ]
    assert not data_1.containerize_with(data_2)

    data_2.location_plan_list = [
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.INSIDE_0
    ]
    assert data_1.containerize_with(data_2)


def test_is_back():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    assert not data.is_back()

    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.BACK))
    assert data.is_back()

    data = create_assign_location_test_data()
    assert data.is_back()


def test_is_between():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    assert not data.is_between()

    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.BETWEEN))
    assert data.is_between()

    data = create_assign_location_test_data()
    assert data.is_between()


def test_is_close():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    assert not data.is_close()

    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.CLOSE))
    assert data.is_close()

    data = create_assign_location_test_data()
    assert data.is_close()


def test_is_far():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    assert not data.is_far()

    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.FAR))
    assert data.is_far()

    data = create_assign_location_test_data()
    assert data.is_far()


def test_is_front():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    assert not data.is_front()

    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.FRONT))
    assert data.is_front()

    data = create_assign_location_test_data()
    assert data.is_front()


def test_is_inside():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    assert not data.is_inside()

    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.INSIDE_0))
    assert data.is_inside()

    data = create_assign_location_test_data()
    assert data.is_inside()


def test_is_random():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    assert not data.is_random()

    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.RANDOM))
    assert data.is_random()

    data = create_assign_location_test_data()
    assert data.is_random()


def test_larger_definition():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))

    data.trained_definition = SOFA_1
    data.untrained_definition = SOCCER_BALL
    assert data.larger_definition() == SOFA_1

    data.trained_definition = SOCCER_BALL
    data.untrained_definition = SOFA_1
    assert data.larger_definition() == SOFA_1


def test_larger_definition_of():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    data.trained_definition = SOFA_1
    data.untrained_definition = SOCCER_BALL
    assert data.larger_definition_of([]) == SOFA_1

    data.location_plan_list = [
        ObjectLocationPlan.BACK,
        ObjectLocationPlan.CLOSE,
        ObjectLocationPlan.FAR,
        ObjectLocationPlan.FRONT,
        ObjectLocationPlan.RANDOM,
        ObjectLocationPlan.NONE
    ]
    assert data.larger_definition_of([]) == SOFA_1


def test_larger_definition_of_with_containers():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    data.trained_definition = SOFA_1
    data.untrained_definition = SOCCER_BALL
    container_data = ReceptacleData(
        'LARGE_CONTAINER',
        ObjectPlan(ObjectLocationPlan.NONE)
    )
    container_data.trained_definition = CASE_1_SUITCASE
    container_data.untrained_definition = CHEST_1_CUBOID
    assert data.larger_definition_of([container_data]) == SOFA_1

    data.location_plan_list = [
        ObjectLocationPlan.NONE,
        ObjectLocationPlan.INSIDE_0,
        ObjectLocationPlan.RANDOM,
        ObjectLocationPlan.INSIDE_0
    ]
    assert data.larger_definition_of([container_data]) == CASE_1_SUITCASE


def test_larger_definition_of_with_second_object():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.RANDOM))
    data.trained_definition = SOCCER_BALL
    data.untrained_definition = SOCCER_BALL
    container_data = ReceptacleData(
        'LARGE_CONTAINER',
        ObjectPlan(ObjectLocationPlan.NONE)
    )
    container_data.trained_definition = CASE_1_SUITCASE
    container_data.untrained_definition = CHEST_1_CUBOID
    confusor_data = ObjectData('CONFUSOR', ObjectPlan(ObjectLocationPlan.NONE))
    confusor_data.trained_definition = SOFA_1
    confusor_data.untrained_definition = SOFA_1
    assert (
        data.larger_definition_of([container_data], confusor_data) ==
        SOCCER_BALL
    )

    confusor_data.location_plan_list = [ObjectLocationPlan.CLOSE]
    assert data.larger_definition_of([container_data], confusor_data) == SOFA_1

    data.location_plan_list = [ObjectLocationPlan.INSIDE_0]
    assert data.larger_definition_of([container_data], confusor_data) == (
        CASE_1_SUITCASE
    )

    confusor_data.location_plan_list = [ObjectLocationPlan.FAR]
    assert data.larger_definition_of([container_data], confusor_data) == (
        CASE_1_SUITCASE
    )


def test_locations_with_indexes():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.RANDOM))
    assert data.locations_with_indexes([]) == [
        (ObjectLocationPlan.RANDOM, [0])
    ]

    data.location_plan_list = [
        ObjectLocationPlan.CLOSE,
        ObjectLocationPlan.INSIDE_0,
        ObjectLocationPlan.RANDOM,
        ObjectLocationPlan.CLOSE,
        ObjectLocationPlan.INSIDE_0,
        ObjectLocationPlan.RANDOM
    ]
    container_data = ReceptacleData(
        'LARGE_CONTAINER',
        ObjectPlan(ObjectLocationPlan.NONE)
    )
    container_data.location_plan_list = [
        ObjectLocationPlan.BACK,
        ObjectLocationPlan.BACK,
        ObjectLocationPlan.BACK,
        ObjectLocationPlan.FRONT,
        ObjectLocationPlan.FRONT,
        ObjectLocationPlan.FRONT
    ]
    assert data.locations_with_indexes([container_data]) == [
        (ObjectLocationPlan.CLOSE, [0, 3]),
        (ObjectLocationPlan.BACK, [1]),
        (ObjectLocationPlan.RANDOM, [2, 5]),
        (ObjectLocationPlan.FRONT, [4])
    ]


def test_recreate_both_templates():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    data.trained_definition = base_objects.create_soccer_ball()
    data.trained_template = {}

    data.recreate_both_templates()
    assert data.trained_template['type'] == 'soccer_ball'
    assert data.trained_template['shows'][0]['position'] == {
        'x': 0, 'y': 0, 'z': 0
    }
    assert data.trained_template['shows'][0]['rotation'] == {
        'x': 0, 'y': 0, 'z': 0
    }
    assert data.trained_template['id']
    assert not data.untrained_template

    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    data.trained_definition = base_objects.create_soccer_ball()
    data.trained_template = {}
    data.untrained_definition = (
        definitions.finalize_object_materials_and_colors(
            definitions.finalize_object_definition(
                specific_objects._get('SOFA_1')
            )
        )
    )[0]
    data.untrained_template = {}

    data.recreate_both_templates()
    assert data.trained_template['type'] == 'soccer_ball'
    assert data.trained_template['shows'][0]['position'] == {
        'x': 0, 'y': 0, 'z': 0
    }
    assert data.trained_template['shows'][0]['rotation'] == {
        'x': 0, 'y': 0, 'z': 0
    }
    assert data.trained_template['id']
    assert data.untrained_template['type'] == 'sofa_1'
    assert data.untrained_template['shows'][0]['position'] == {
        'x': 0, 'y': 0, 'z': 0
    }
    assert data.untrained_template['shows'][0]['rotation'] == {
        'x': 0, 'y': 0, 'z': 0
    }
    assert data.untrained_template['id']
    assert data.trained_template['id'] == data.untrained_template['id']


def test_reset_all_properties():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    data.trained_definition = {}
    data.untrained_definition = {}
    data.trained_template = {}
    data.untrained_template = {}
    data.instance_list = [{}, {}]

    data.reset_all_properties()
    assert not data.trained_definition
    assert not data.untrained_definition
    assert not data.trained_template
    assert not data.untrained_template
    assert data.instance_list == [None, None]

    data.original_definition = {'key': 'value'}
    data.trained_definition = {}
    data.untrained_definition = {}
    data.trained_template = {}
    data.untrained_template = {}
    data.instance_list = [{}, {}]

    data.reset_all_properties()
    assert data.trained_definition == {'key': 'value'}
    assert data.untrained_definition == {'key': 'value'}
    assert not data.trained_template
    assert not data.untrained_template
    assert data.instance_list == [None, None]


def test_reset_all_instances():
    data = ObjectData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    data.trained_definition = {}
    data.untrained_definition = {}
    data.trained_template = {}
    data.untrained_template = {}
    data.instance_list = [{}, {}]

    data.reset_all_instances()
    assert data.trained_definition is not None
    assert data.untrained_definition is not None
    assert data.trained_template is not None
    assert data.untrained_template is not None
    assert data.instance_list == [None, None]


def test_receptacle_data_init():
    data = ReceptacleData('ROLE', ObjectPlan(ObjectLocationPlan.NONE))
    assert data.role == 'ROLE'
    assert data.location_plan_list == [ObjectLocationPlan.NONE]
    assert data.untrained_plan_list == [False]
    assert not data.original_definition
    assert not data.trained_definition
    assert not data.untrained_definition
    assert not data.trained_template
    assert not data.untrained_template
    assert data.instance_list == [None]
    assert not data.trained_containment.area_index
    assert not data.trained_containment.orientation
    assert not data.trained_containment.target_angle
    assert not data.trained_containment.confusor_angle
    assert not data.untrained_containment.area_index
    assert not data.untrained_containment.orientation
    assert not data.untrained_containment.target_angle
    assert not data.untrained_containment.confusor_angle


def test_target_data_init():
    data = TargetData(ObjectPlan(ObjectLocationPlan.NONE), 1234)
    assert data.role == 'TARGET'
    assert data.location_plan_list == [ObjectLocationPlan.NONE]
    assert data.untrained_plan_list == [False]
    assert not data.original_definition
    assert not data.trained_definition
    assert not data.untrained_definition
    assert not data.trained_template
    assert not data.untrained_template
    assert data.instance_list == [None]
    assert data.choice == 1234
