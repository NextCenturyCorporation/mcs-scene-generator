import pytest
from machine_common_sense.config_manager import Vector3d

from generator import (
    ImmutableObjectDefinition,
    MaterialChoice,
    ObjectDefinition,
    SizeChoice,
    TypeChoice,
    definitions,
    materials,
)
from generator.definitions import (
    create_dataset,
    finalize_each_definition_choice,
    finalize_object_definition,
    finalize_object_materials_and_colors,
    retrieve_complete_definition_list,
)


def create_interesting_dataset():
    return create_dataset([[
        ObjectDefinition(type='a'),
        ObjectDefinition(type='b', chooseMaterialList=[
            MaterialChoice(
                materialCategory=['metal'],
                salientMaterials=['metal']
            ),
            MaterialChoice(
                materialCategory=['plastic'],
                salientMaterials=['plastic']
            )
        ]),
        ObjectDefinition(type='c', chooseSizeList=[
            SizeChoice(dimensions=Vector3d(1, 1, 1), mass=1),
            SizeChoice(dimensions=Vector3d(2, 2, 2), mass=2)
        ])
    ], [
        ObjectDefinition(type='d', chooseMaterialList=[
            MaterialChoice(
                materialCategory=['rubber'],
                salientMaterials=['rubber']
            ),
            MaterialChoice(
                materialCategory=['wood'],
                salientMaterials=['wood']
            )
        ], chooseSizeList=[
            SizeChoice(dimensions=Vector3d(3, 3, 3), mass=3),
            SizeChoice(dimensions=Vector3d(4, 4, 4), mass=4)
        ])
    ]], unshuffled=True)


def test_object_definition_arguments():
    for prop in definitions._object_definition_properties:
        args = {}
        args[prop] = None
        assert ObjectDefinition(**args)


def test_immutable_object_definition():
    definition = ObjectDefinition()
    immutable = ImmutableObjectDefinition(**vars(definition))
    assert immutable
    with pytest.raises(AttributeError):
        immutable.type = 'foobar'


def test_create_dataset():
    dataset = create_interesting_dataset()

    assert isinstance(dataset._definition_groups, tuple)
    assert isinstance(dataset._definition_groups[0], tuple)
    assert isinstance(dataset._definition_groups[1], tuple)

    assert len(dataset._definition_groups) == 2
    assert len(dataset._definition_groups[0]) == 5
    assert len(dataset._definition_groups[1]) == 4

    assert len(dataset._definition_groups[0][0]) == 1
    assert dataset._definition_groups[0][0][0].type == 'a'

    assert len(dataset._definition_groups[0][1]) == 10
    for definition in dataset._definition_groups[0][1]:
        assert definition.type == 'b'
        assert definition.materialCategory == ['metal']
        assert definition.salientMaterials == ['metal']

    assert len(dataset._definition_groups[0][2]) == 7
    for definition in dataset._definition_groups[0][2]:
        assert definition.type == 'b'
        assert definition.materialCategory == ['plastic']
        assert definition.salientMaterials == ['plastic']

    assert len(dataset._definition_groups[0][3]) == 1
    for definition in dataset._definition_groups[0][3]:
        assert definition.type == 'c'
        assert definition.dimensions == Vector3d(1, 1, 1)
        assert definition.mass == 1

    assert len(dataset._definition_groups[0][4]) == 1
    for definition in dataset._definition_groups[0][4]:
        assert definition.type == 'c'
        assert definition.dimensions == Vector3d(2, 2, 2)
        assert definition.mass == 2

    assert len(dataset._definition_groups[1][0]) == 2
    for definition in dataset._definition_groups[1][0]:
        assert definition.type == 'd'
        assert definition.materialCategory == ['rubber']
        assert definition.salientMaterials == ['rubber']
        assert definition.dimensions == Vector3d(3, 3, 3)
        assert definition.mass == 3

    assert len(dataset._definition_groups[1][1]) == 39
    for definition in dataset._definition_groups[1][1]:
        assert definition.type == 'd'
        assert definition.materialCategory == ['wood']
        assert definition.salientMaterials == ['wood']
        assert definition.dimensions == Vector3d(3, 3, 3)
        assert definition.mass == 3

    assert len(dataset._definition_groups[1][2]) == 2
    for definition in dataset._definition_groups[1][2]:
        assert definition.type == 'd'
        assert definition.materialCategory == ['rubber']
        assert definition.salientMaterials == ['rubber']
        assert definition.dimensions == Vector3d(4, 4, 4)
        assert definition.mass == 4

    assert len(dataset._definition_groups[1][3]) == 39
    for definition in dataset._definition_groups[1][3]:
        assert definition.type == 'd'
        assert definition.materialCategory == ['wood']
        assert definition.salientMaterials == ['wood']
        assert definition.dimensions == Vector3d(4, 4, 4)
        assert definition.mass == 4


def test_create_dataset_definitions_are_immutable():
    dataset = create_interesting_dataset()
    with pytest.raises(AttributeError):
        dataset._definition_groups[0][0][0].type = 'foobar'


def test_definition_dataset_choose_random_definition():
    dataset = create_interesting_dataset()
    definition = dataset.choose_random_definition()
    assert isinstance(definition, ObjectDefinition)


def test_definition_dataset_definitions():
    dataset = create_interesting_dataset()
    definitions = dataset.definitions(unshuffled=True)
    assert len(definitions) == 102
    for definition in definitions:
        assert isinstance(definition, ObjectDefinition)


def test_definition_dataset_filter_on_trained():
    dataset = create_dataset([[
        ObjectDefinition(type='a'),
        ObjectDefinition(type='b', untrainedCategory=True),
        ObjectDefinition(type='c', untrainedColor=True),
        ObjectDefinition(type='d', untrainedCombination=True),
        ObjectDefinition(type='e', untrainedShape=True),
        ObjectDefinition(type='f', untrainedSize=True),
        ObjectDefinition(
            type='g',
            untrainedCategory=True,
            untrainedColor=True,
            untrainedCombination=True,
            untrainedShape=True,
            untrainedSize=True
        ),
        ObjectDefinition(type='h')
    ]], unshuffled=True)

    actual_1 = dataset.filter_on_trained().definitions(unshuffled=True)
    assert len(actual_1) == 2
    assert actual_1[0].type == 'a'
    assert actual_1[1].type == 'h'


def test_definition_dataset_filter_on_untrained():
    dataset = create_dataset([[
        ObjectDefinition(type='a'),
        ObjectDefinition(type='b', untrainedCategory=True),
        ObjectDefinition(type='c', untrainedColor=True),
        ObjectDefinition(type='d', untrainedCombination=True),
        ObjectDefinition(type='e', untrainedShape=True),
        ObjectDefinition(type='f', untrainedSize=True),
        ObjectDefinition(
            type='g',
            untrainedCategory=True,
            untrainedColor=True,
            untrainedCombination=True,
            untrainedShape=True,
            untrainedSize=True
        ),
        ObjectDefinition(type='h')
    ]], unshuffled=True)

    actual_1 = dataset.filter_on_untrained('untrainedCategory').definitions(
        unshuffled=True
    )
    assert len(actual_1) == 1
    assert actual_1[0].type == 'b'

    actual_2 = dataset.filter_on_untrained('untrainedSize').definitions(
        unshuffled=True
    )
    assert len(actual_2) == 1
    assert actual_2[0].type == 'f'


def test_finalize_each_definition_choice():
    definition = ObjectDefinition(
        type='test_type',
        chooseMaterialList=[
            MaterialChoice(
                materialCategory=['metal'],
                salientMaterials=['metal']
            ),
            MaterialChoice(
                materialCategory=['plastic'],
                salientMaterials=['plastic']
            )
        ],
        chooseSizeList=[
            SizeChoice(dimensions=Vector3d(1, 1, 1), mass=1),
            SizeChoice(dimensions=Vector3d(2, 2, 2), mass=2)
        ]
    )
    definition_list = finalize_each_definition_choice(
        definition,
        unshuffled=True
    )
    assert len(definition_list) == 4
    assert definition_list[0].type == 'test_type'
    assert definition_list[0].materialCategory == ['metal']
    assert definition_list[0].salientMaterials == ['metal']
    assert definition_list[0].dimensions == Vector3d(1, 1, 1)
    assert definition_list[0].mass == 1
    assert definition_list[1].type == 'test_type'
    assert definition_list[1].materialCategory == ['plastic']
    assert definition_list[1].salientMaterials == ['plastic']
    assert definition_list[1].dimensions == Vector3d(1, 1, 1)
    assert definition_list[1].mass == 1
    assert definition_list[2].type == 'test_type'
    assert definition_list[2].materialCategory == ['metal']
    assert definition_list[2].salientMaterials == ['metal']
    assert definition_list[2].dimensions == Vector3d(2, 2, 2)
    assert definition_list[2].mass == 2
    assert definition_list[3].type == 'test_type'
    assert definition_list[3].materialCategory == ['plastic']
    assert definition_list[3].salientMaterials == ['plastic']
    assert definition_list[3].dimensions == Vector3d(2, 2, 2)
    assert definition_list[3].mass == 2


def test_finalize_object_definition():
    dimensions = Vector3d(**{'x': 1, 'y': 1, 'z': 1})
    mass = 12.34
    material_category = ['plastic']
    salient_materials = ['plastic', 'hollow']
    raw_definition = ObjectDefinition(
        type='type1',
        mass=56.78,
        chooseMaterialList=[MaterialChoice(
            materialCategory=material_category,
            salientMaterials=salient_materials
        )],
        chooseSizeList=[SizeChoice(dimensions=dimensions, mass=mass)]
    )
    final_definition = finalize_object_definition(raw_definition)
    assert final_definition.dimensions == dimensions
    assert final_definition.mass == mass
    assert final_definition.materialCategory == material_category
    assert final_definition.salientMaterials == salient_materials


def test_finalize_object_materials_and_colors():
    materials.TEST_MATERIALS = [
        ('test_material_grey', ['grey']),
        ('test_material_multicolor', ['blue', 'yellow'])
    ]
    definition = ObjectDefinition(
        type='test_type',
        mass=1,
        dimensions=Vector3d(0.5, 0.5, 0.5),
        shape=['test_shape'],
        size='test_size',
        scale=Vector3d(1, 1, 1),
        attributes=[],
        materialCategory=['test']
    )
    definition_list = finalize_object_materials_and_colors(
        definition,
        unshuffled=True
    )
    assert len(definition_list) == 2
    assert definition_list[0].materials == ['test_material_grey']
    assert definition_list[0].color == ['grey']
    assert definition_list[1].materials == ['test_material_multicolor']
    assert definition_list[1].color == ['blue', 'yellow']


def test_finalize_object_materials_and_colors_multiple_material_categories():
    materials.TEST1_MATERIALS = [
        ('test_material_grey', ['grey']),
        ('test_material_multicolor', ['blue', 'yellow'])
    ]
    materials.TEST2_MATERIALS = [
        ('test_material_green', ['green']),
        ('test_material_red', ['red'])
    ]
    definition = ObjectDefinition(
        type='test_type',
        mass=1,
        dimensions=Vector3d(0.5, 0.5, 0.5),
        shape=['test_shape'],
        size='test_size',
        scale=Vector3d(1, 1, 1),
        attributes=[],
        materialCategory=['test1', 'test2']
    )
    definition_list = finalize_object_materials_and_colors(
        definition,
        unshuffled=True
    )
    assert len(definition_list) == 4
    assert definition_list[0].materials == [
        'test_material_grey', 'test_material_green'
    ]
    assert definition_list[0].color == ['grey', 'green']
    assert definition_list[1].materials == [
        'test_material_multicolor', 'test_material_green'
    ]
    assert definition_list[1].color == ['blue', 'yellow', 'green']
    assert definition_list[2].materials == [
        'test_material_grey', 'test_material_red'
    ]
    assert definition_list[2].color == ['grey', 'red']
    assert definition_list[3].materials == [
        'test_material_multicolor', 'test_material_red'
    ]
    assert definition_list[3].color == ['blue', 'yellow', 'red']


def test_retrieve_complete_definition_list():
    list_1 = [ObjectDefinition(type='ball', mass=1)]
    actual_1 = retrieve_complete_definition_list([list_1])
    assert len(actual_1) == 1
    assert len(actual_1[0]) == 1
    assert len(actual_1[0][0]) == 1

    list_2 = [ObjectDefinition(
        type='ball',
        chooseSizeList=[SizeChoice(mass=1), SizeChoice(mass=2)]
    )]
    actual_2 = retrieve_complete_definition_list([list_2])
    assert len(actual_2) == 1
    assert len(actual_2[0]) == 2
    assert len(actual_2[0][0]) == 1
    assert len(actual_2[0][1]) == 1

    list_3 = [ObjectDefinition(type='sofa'), ObjectDefinition(
        type='ball',
        chooseSizeList=[SizeChoice(mass=1), SizeChoice(mass=2)]
    )]
    actual_3 = retrieve_complete_definition_list([list_3])
    assert len(actual_3) == 1
    assert len(actual_3[0]) == 3
    assert len(actual_3[0][0]) == 1
    assert len(actual_3[0][1]) == 1
    assert len(actual_3[0][2]) == 1

    list_4 = [ObjectDefinition(
        type='sofa',
        chooseSizeList=[SizeChoice(mass=1), SizeChoice(mass=3)]
    ), ObjectDefinition(
        type='ball',
        chooseSizeList=[SizeChoice(mass=1), SizeChoice(mass=2)]
    )]
    actual_4 = retrieve_complete_definition_list([list_4])
    assert len(actual_4) == 1
    assert len(actual_4[0]) == 4
    assert len(actual_4[0][0]) == 1
    assert len(actual_4[0][1]) == 1
    assert len(actual_4[0][2]) == 1
    assert len(actual_4[0][3]) == 1

    list_5 = [ObjectDefinition(chooseTypeList=[
        TypeChoice(type='sphere'),
        TypeChoice(type='cube')
    ])]
    actual_5 = retrieve_complete_definition_list([list_5])
    assert len(actual_5) == 1
    assert len(actual_5[0]) == 2
    assert len(actual_5[0][0]) == 1
    assert len(actual_5[0][1]) == 1

    list_6 = [
        ObjectDefinition(type='sofa'),
        ObjectDefinition(chooseTypeList=[
            TypeChoice(type='sphere'),
            TypeChoice(type='cube')
        ])
    ]
    actual_6 = retrieve_complete_definition_list([list_6])
    assert len(actual_6) == 1
    assert len(actual_6[0]) == 3
    assert len(actual_6[0][0]) == 1
    assert len(actual_6[0][1]) == 1
    assert len(actual_6[0][2]) == 1

    list_7 = [ObjectDefinition(chooseTypeList=[
        TypeChoice(type='ball'),
        TypeChoice(type='sofa')
    ]), ObjectDefinition(chooseTypeList=[
        TypeChoice(type='sphere'),
        TypeChoice(type='cube')
    ])]
    actual_7 = retrieve_complete_definition_list([list_7])
    assert len(actual_7) == 1
    assert len(actual_7[0]) == 4
    assert len(actual_7[0][0]) == 1
    assert len(actual_7[0][1]) == 1
    assert len(actual_7[0][2]) == 1
    assert len(actual_7[0][3]) == 1

    list_8 = [ObjectDefinition(chooseMaterialList=[
        MaterialChoice(materialCategory=['block_blank']),
        MaterialChoice(materialCategory=['rubber'])
    ], chooseSizeList=[
        SizeChoice(mass=1),
        SizeChoice(mass=2)
    ], chooseTypeList=[
        TypeChoice(type='ball'),
        TypeChoice(type='sofa')
    ])]
    actual_8 = retrieve_complete_definition_list([list_8], unshuffled=True)
    assert len(actual_8) == 1
    assert len(actual_8[0]) == 8
    assert len(actual_8[0][0]) == 6
    assert len(actual_8[0][1]) == 2
    assert len(actual_8[0][2]) == 6
    assert len(actual_8[0][3]) == 2
    assert len(actual_8[0][4]) == 6
    assert len(actual_8[0][5]) == 2
    assert len(actual_8[0][6]) == 6
    assert len(actual_8[0][7]) == 2


def test_retrieve_complete_definition_list_nested_list():
    list_1 = [[ObjectDefinition(chooseTypeList=[
        TypeChoice(type='ball'),
        TypeChoice(type='sofa')
    ])], [ObjectDefinition(chooseTypeList=[
        TypeChoice(type='sphere'),
        TypeChoice(type='cube')
    ])]]
    actual_1 = retrieve_complete_definition_list(list_1)
    assert len(actual_1) == 2
    assert len(actual_1[0]) == 2
    assert len(actual_1[1]) == 2
    assert len(actual_1[0][0]) == 1
    assert len(actual_1[0][1]) == 1
    assert len(actual_1[1][0]) == 1
    assert len(actual_1[1][1]) == 1

    type_list_a = [item.type for item in (actual_1[0][0] + actual_1[0][1])]
    type_list_b = [item.type for item in (actual_1[1][0] + actual_1[1][1])]
    assert (
        (
            'ball' in type_list_a and 'sofa' in type_list_a and
            'sphere' in type_list_b and 'cube' in type_list_b
        ) or (
            'ball' in type_list_b and 'sofa' in type_list_b and
            'sphere' in type_list_a and 'cube' in type_list_a
        )
    )


def test_retrieve_complete_definition_list_choose_material():
    defs = [ObjectDefinition(type='metal_thing', chooseMaterialList=[
        MaterialChoice(materialCategory=['metal'])
    ]), ObjectDefinition(type='plastic_thing', chooseMaterialList=[
        MaterialChoice(materialCategory=['plastic'])
    ]), ObjectDefinition(type='rubber_thing', chooseMaterialList=[
        MaterialChoice(materialCategory=['rubber'])
    ]), ObjectDefinition(type='wood_thing', chooseMaterialList=[
        MaterialChoice(materialCategory=['wood'])
    ]), ObjectDefinition(type='other_thing', chooseMaterialList=[
        MaterialChoice(materialCategory=['metal']),
        MaterialChoice(materialCategory=['plastic']),
        MaterialChoice(materialCategory=['rubber']),
        MaterialChoice(materialCategory=['wood'])
    ])]

    actual = retrieve_complete_definition_list([defs], unshuffled=True)
    assert len(actual) == 1
    assert len(actual[0]) == 8
    assert len(actual[0][0]) == 10
    assert len(actual[0][1]) == 7
    assert len(actual[0][2]) == 2
    assert len(actual[0][3]) == 39
    assert len(actual[0][4]) == 10
    assert len(actual[0][5]) == 7
    assert len(actual[0][6]) == 2
    assert len(actual[0][7]) == 39

    for definition in actual[0][0]:
        assert definition.type == 'metal_thing'

    for definition in (actual[0][0] + actual[0][4]):
        assert definition.materialCategory == ['metal']
        assert definition.materials

    for definition in actual[0][1]:
        assert definition.type == 'plastic_thing'

    for definition in (actual[0][1] + actual[0][5]):
        assert definition.materialCategory == ['plastic']
        assert definition.materials

    for definition in actual[0][2]:
        assert definition.type == 'rubber_thing'

    for definition in (actual[0][2] + actual[0][6]):
        assert definition.materialCategory == ['rubber']
        assert definition.materials

    for definition in actual[0][3]:
        assert definition.type == 'wood_thing'

    for definition in (actual[0][3] + actual[0][7]):
        assert definition.materialCategory == ['wood']
        assert definition.materials

    for definition in (
        actual[0][4] + actual[0][5] + actual[0][6] + actual[0][7]
    ):
        assert definition.type == 'other_thing'


def test_retrieve_complete_definition_list_unshuffled():
    list_1 = [[ObjectDefinition(chooseTypeList=[
        TypeChoice(type='ball'),
        TypeChoice(type='sofa')
    ])], [ObjectDefinition(chooseTypeList=[
        TypeChoice(type='sphere'),
        TypeChoice(type='cube')
    ])]]
    actual_1 = retrieve_complete_definition_list(list_1, unshuffled=True)
    assert actual_1[0][0][0].type == 'ball'
    assert actual_1[0][1][0].type == 'sofa'
    assert actual_1[1][0][0].type == 'sphere'
    assert actual_1[1][1][0].type == 'cube'
