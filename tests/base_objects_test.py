from machine_common_sense.config_manager import Vector3d

from generator import ChosenMaterial, ObjectDefinition, base_objects


def test_all_types_exist():
    assert len(base_objects._TYPES_TO_DETAILS.keys())
    for object_type in base_objects._TYPES_TO_DETAILS:
        definition = base_objects.create_variable_definition_from_base(
            type=object_type,
            size_multiplier_list=[1],
            chosen_material_list=[]
        )
        assert isinstance(definition, ObjectDefinition)


def test_create_specific_definition_from_base():
    ball = base_objects.create_specific_definition_from_base(
        type='ball',
        color=['blue', 'yellow'],
        materials=['blue_yellow_material'],
        salient_materials=['plastic', 'hollow'],
        scale=2
    )
    assert isinstance(ball, ObjectDefinition)
    assert ball.type == 'ball'
    assert ball.chooseMaterialList == []
    assert ball.chooseSizeList == []
    assert ball.attributes == ['moveable', 'pickupable']
    assert ball.color == ['blue', 'yellow']
    assert ball.mass == 2
    assert ball.materials == ['blue_yellow_material']
    assert ball.salientMaterials == ['plastic', 'hollow']
    assert ball.scale == Vector3d(2, 2, 2)
    assert ball.shape == ['ball']


def test_create_specific_definition_from_base_scale_vector():
    ball = base_objects.create_specific_definition_from_base(
        type='ball',
        color=[],
        materials=[],
        salient_materials=[],
        scale=Vector3d(0.5, 1, 0.5)
    )
    assert isinstance(ball, ObjectDefinition)
    assert ball.type == 'ball'
    assert ball.chooseMaterialList == []
    assert ball.chooseSizeList == []
    assert ball.attributes == ['moveable', 'pickupable']
    assert ball.color == []
    assert ball.mass == 0.6667
    assert ball.materials == []
    assert ball.salientMaterials == []
    assert ball.scale == Vector3d(0.5, 1, 0.5)
    assert ball.shape == ['ball']


def test_create_specific_definition_from_base_unconfigurable_material():
    ball = base_objects.create_specific_definition_from_base(
        type='soccer_ball',
        color=['blue', 'yellow'],
        materials=['blue_yellow_material'],
        salient_materials=['plastic', 'hollow'],
        scale=2
    )
    assert isinstance(ball, ObjectDefinition)
    assert ball.type == 'soccer_ball'
    assert ball.chooseMaterialList == []
    assert ball.chooseSizeList == []
    assert ball.attributes == ['moveable', 'pickupable']
    assert ball.color == ['white', 'black']
    assert ball.mass == 2
    assert ball.materials == []
    assert ball.salientMaterials == ['rubber']
    assert ball.scale == Vector3d(2, 2, 2)
    assert ball.shape == ['ball']


def test_create_specific_definition_from_base_mass_override():
    ball = base_objects.create_specific_definition_from_base(
        type='ball',
        color=['grey'],
        materials=['grey_material'],
        salient_materials=['metal'],
        scale=2,
        mass_override=10
    )
    assert isinstance(ball, ObjectDefinition)
    assert ball.type == 'ball'
    assert ball.chooseMaterialList == []
    assert ball.chooseSizeList == []
    assert ball.attributes == ['moveable', 'pickupable']
    assert ball.color == ['grey']
    assert ball.mass == 10
    assert ball.materials == ['grey_material']
    assert ball.salientMaterials == ['metal']
    assert ball.scale == Vector3d(2, 2, 2)
    assert ball.shape == ['ball']


def test_create_variable_definition_from_base():
    ball = base_objects.create_variable_definition_from_base(
        type='ball',
        size_multiplier_list=[0.5, 1, 2, Vector3d(0.5, 1, 0.5)],
        chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.PLASTIC]
    )
    assert isinstance(ball, ObjectDefinition)
    assert ball.type == 'ball'
    assert ball.attributes == ['moveable', 'pickupable']
    assert ball.color is None
    assert ball.materials is None
    assert ball.salientMaterials is None
    assert ball.scale is None
    assert ball.shape == ['ball']

    assert len(ball.chooseMaterialList) == 2
    assert ball.chooseMaterialList[0].massMultiplier == 3
    assert ball.chooseMaterialList[0].materialCategory == ['metal']
    assert ball.chooseMaterialList[0].salientMaterials == ['metal']
    assert ball.chooseMaterialList[1].massMultiplier == 1
    assert ball.chooseMaterialList[1].materialCategory == ['plastic']
    assert ball.chooseMaterialList[1].salientMaterials == ['plastic']

    assert len(ball.chooseSizeList) == 4
    assert ball.chooseSizeList[0].dimensions == Vector3d(0.5, 0.5, 0.5)
    assert ball.chooseSizeList[0].mass == 0.5
    assert ball.chooseSizeList[0].scale == Vector3d(0.5, 0.5, 0.5)
    assert ball.chooseSizeList[1].dimensions == Vector3d(1, 1, 1)
    assert ball.chooseSizeList[1].mass == 1
    assert ball.chooseSizeList[1].scale == Vector3d(1, 1, 1)
    assert ball.chooseSizeList[2].dimensions == Vector3d(2, 2, 2)
    assert ball.chooseSizeList[2].mass == 2
    assert ball.chooseSizeList[2].scale == Vector3d(2, 2, 2)
    assert ball.chooseSizeList[3].dimensions == Vector3d(0.5, 1, 0.5)
    assert ball.chooseSizeList[3].mass == 0.6667
    assert ball.chooseSizeList[3].scale == Vector3d(0.5, 1, 0.5)


def test_create_variable_definition_from_base_attributes_overrides():
    ball = base_objects.create_variable_definition_from_base(
        type='ball',
        attributes_overrides=[],
        size_multiplier_list=[0.5, 1, 2, Vector3d(0.5, 1, 0.5)],
        chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.PLASTIC]
    )
    assert isinstance(ball, ObjectDefinition)
    assert ball.type == 'ball'
    assert ball.attributes == []


def test_create_variable_definition_from_base_cylinder():
    cylinder = base_objects.create_variable_definition_from_base(
        type='cylinder',
        size_multiplier_list=[0.5, 1, 2, Vector3d(0.5, 1, 0.5)],
        chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.PLASTIC]
    )
    assert isinstance(cylinder, ObjectDefinition)
    assert cylinder.type == 'cylinder'
    assert cylinder.attributes == ['physics']
    assert cylinder.color is None
    assert cylinder.materials is None
    assert cylinder.salientMaterials is None
    assert cylinder.scale is None
    assert cylinder.shape == ['cylinder']

    assert len(cylinder.chooseSizeList) == 4
    assert cylinder.chooseSizeList[0].dimensions == Vector3d(0.5, 0.5, 0.5)
    assert cylinder.chooseSizeList[0].mass == 0.5
    assert cylinder.chooseSizeList[0].scale == Vector3d(0.5, 0.25, 0.5)
    assert cylinder.chooseSizeList[1].dimensions == Vector3d(1, 1, 1)
    assert cylinder.chooseSizeList[1].mass == 1
    assert cylinder.chooseSizeList[1].scale == Vector3d(1, 0.5, 1)
    assert cylinder.chooseSizeList[2].dimensions == Vector3d(2, 2, 2)
    assert cylinder.chooseSizeList[2].mass == 2
    assert cylinder.chooseSizeList[2].scale == Vector3d(2, 1, 2)
    assert cylinder.chooseSizeList[3].dimensions == Vector3d(0.5, 1, 0.5)
    assert cylinder.chooseSizeList[3].mass == 0.6667
    assert cylinder.chooseSizeList[3].scale == Vector3d(0.5, 0.5, 0.5)


def test_create_variable_definition_from_base_multiple_material_category():
    table_1 = base_objects.create_variable_definition_from_base(
        type='table_1',
        size_multiplier_list=[1],
        chosen_material_list=[ChosenMaterial.METAL, ChosenMaterial.WOOD]
    )
    assert isinstance(table_1, ObjectDefinition)
    assert table_1.type == 'table_1'

    assert len(table_1.chooseMaterialList) == 2
    assert table_1.chooseMaterialList[0].massMultiplier == 3
    assert table_1.chooseMaterialList[0].materialCategory == ['metal', 'metal']
    assert table_1.chooseMaterialList[0].salientMaterials == ['metal']
    assert table_1.chooseMaterialList[1].massMultiplier == 2
    assert table_1.chooseMaterialList[1].materialCategory == ['wood', 'wood']
    assert table_1.chooseMaterialList[1].salientMaterials == ['wood']


def test_create_soccer_ball():
    ball = base_objects.create_soccer_ball()
    assert isinstance(ball, ObjectDefinition)
    assert ball.type == 'soccer_ball'
    assert ball.attributes == ['moveable', 'pickupable']
    assert ball.color == ['white', 'black']
    assert ball.dimensions == Vector3d(0.22, 0.22, 0.22)
    assert ball.mass == 1
    assert ball.materials == []
    assert ball.offset == Vector3d(0, 0.11, 0)
    assert ball.positionY == 0.11
    assert ball.salientMaterials == ['rubber']
    assert ball.scale == Vector3d(1, 1, 1)
    assert ball.shape == ['ball']
