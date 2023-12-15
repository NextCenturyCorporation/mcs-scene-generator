from machine_common_sense.config_manager import (
    FloorTexturesConfig,
    Goal,
    Vector2dInt,
    Vector3d
)

from generator import ObjectBounds, SceneObject, geometry
from generator.scene import Scene, get_step_limit_from_dimensions

from .ile_helper import prior_scene_with_target, prior_scene_with_targets


def test_get_targets_none():
    scene = Scene()
    assert scene.get_targets() == []


def test_get_targets_single():
    scene = prior_scene_with_target()
    targets = scene.get_targets()
    assert len(targets) == 1
    obj = targets[0]
    assert obj["type"] == "soccer_ball"
    assert obj["id"] == "743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f"
    assert obj["moveable"]
    assert obj["pickupable"]
    show = obj["shows"][0]
    assert show["rotation"] == {"x": 0, "y": 45, "z": 0}
    assert show["position"] == {"x": -1.03, "y": 0.11, "z": 4.08}
    assert show["scale"] == {"x": 1, "y": 1, "z": 1}


def test_get_targets_many():
    scene = prior_scene_with_targets()
    targets = scene.get_targets()
    assert len(targets) == 2
    target_1 = targets[0]
    assert target_1['type'] == 'soccer_ball'
    assert target_1['id']
    assert target_1['moveable']
    assert target_1['pickupable']
    assert target_1['shows'][0]['position'] == {'x': 1, 'y': 0.11, 'z': 2}
    assert target_1['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert target_1['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    target_2 = targets[1]
    assert target_2['type'] == 'soccer_ball'
    assert target_2['id']
    assert target_2['moveable']
    assert target_2['pickupable']
    assert target_2['shows'][0]['position'] == {'x': 3, 'y': 0.11, 'z': 4}
    assert target_2['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert target_2['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}
    assert target_1['id'] != target_2['id']


def test_scene_default():
    scene = Scene()
    assert scene.ceiling_material is None
    assert scene.debug == {}
    assert scene.floor_material is None
    assert scene.floor_properties is None
    assert scene.floor_textures == []
    assert scene.goal == Goal(metadata={})
    assert scene.holes == []
    assert not scene.intuitive_physics
    assert not scene.isometric
    assert scene.lava == []
    assert scene.name == ""
    assert scene.objects == []
    assert scene.performer_start
    assert scene.performer_start.position == Vector3d()
    assert scene.performer_start.rotation == Vector3d()
    assert scene.room_dimensions == Vector3d(x=10, y=3, z=10)
    assert scene.room_materials is None
    assert not scene.restrict_open_doors
    assert not scene.screenshot
    assert scene.version == 2
    assert scene.wall_material is None
    assert scene.wall_properties is None


def test_set_room_dimensions():
    scene = Scene()
    scene.set_room_dimensions(4, 5, 6)
    assert scene.room_dimensions == Vector3d(x=4, y=5, z=6)


def test_set_performer_start():
    scene = Scene()
    assert scene.performer_start.position == Vector3d()
    assert scene.performer_start.rotation == Vector3d()
    position = Vector3d(x=1, y=2, z=3)
    rotation = Vector3d(x=4, y=5, z=6)
    scene.set_performer_start(position, rotation)
    assert scene.performer_start.position == Vector3d(x=1, y=2, z=3)
    assert scene.performer_start.rotation == Vector3d(x=4, y=5, z=6)


def test_set_performer_start_position():
    scene = Scene()
    assert scene.performer_start.position == Vector3d()
    scene.set_performer_start_position(1, 2, 3)
    assert scene.performer_start.position == Vector3d(x=1, y=2, z=3)
    scene.set_performer_start_position(4, None, 5)
    assert scene.performer_start.position == Vector3d(x=4, y=2, z=5)
    scene.set_performer_start_position(None, 6, None)
    assert scene.performer_start.position == Vector3d(x=4, y=6, z=5)
    scene.set_performer_start_position(None, 7, 8)
    assert scene.performer_start.position == Vector3d(x=4, y=7, z=8)


def test_set_performer_start_rotation():
    scene = Scene()
    assert scene.performer_start.rotation == Vector3d()
    scene.set_performer_start_rotation(0, 90)
    assert scene.performer_start.rotation == Vector3d(x=0, y=90, z=0)
    scene.set_performer_start_rotation(23, 258)
    assert scene.performer_start.rotation == Vector3d(x=23, y=258, z=0)


def test_to_dict():
    scene = Scene()
    d = scene.to_dict()
    assert d == {
        "version": 2,
        "debug": {},
        "goal": {
            "metadata": {}},
        "holes": [],
        "isometric": False,
        "isometricFrontRight": False,
        "lava": [],
        "name": "",
        "objects": [],
        "screenshot": False,
        "floorTextures": [],
        "intuitivePhysics": False,
        "performerStart": {
            "position": {
                "x": 0,
                "y": 0,
                "z": 0},
            "rotation": {
                "x": 0,
                "y": 0,
                "z": 0}},
        "roomDimensions": {
            "x": 10,
            "y": 3,
            "z": 10}}

    scene.set_performer_start_rotation(23, 258)
    scene.set_performer_start_position(1, 2, 3)
    scene.set_room_dimensions(4, 5, 6)
    scene.name = "test"
    scene.objects.append(SceneObject({"id": "pretend object"}))
    scene.lava.append(Vector2dInt(x=0, z=-1))
    scene.holes.append(Vector2dInt(x=3, z=4))
    scene.floor_textures.append(FloorTexturesConfig(
        material='floor_texture_a',
        positions=[Vector2dInt(x=-2, z=-3)]
    ))
    d = scene.to_dict()
    assert d == {
        "version": 2,
        "debug": {},
        "goal": {
            "metadata": {}},
        "holes": [{
            "x": 3,
            "z": 4
        }],
        "isometric": False,
        "isometricFrontRight": False,
        "lava": [{
            "x": 0,
            "z": -1
        }],
        "name": "test",
        "objects": [{"id": "pretend object"}],
        "screenshot": False,
        "floorTextures": [{
            'material': 'floor_texture_a',
            'positions': [{'x': -2, 'z': -3}]
        }],
        "intuitivePhysics": False,
        "performerStart": {
            "position": {
                "x": 1,
                "y": 2,
                "z": 3},
            "rotation": {
                "x": 23,
                "y": 258,
                "z": 0}},
        "roomDimensions": {
            "x": 4,
            "y": 5,
            "z": 6}}


def test_get_last_step():
    assert get_step_limit_from_dimensions(2, 2) == 900
    assert get_step_limit_from_dimensions(2, 20) == 2700
    assert get_step_limit_from_dimensions(20, 2) == 2700
    assert get_step_limit_from_dimensions(20, 20) == 4500
    assert get_step_limit_from_dimensions(10, 10) == 2500
    assert get_step_limit_from_dimensions(50, 50) == 10500
    assert get_step_limit_from_dimensions(10, 100) == 11500
    assert get_step_limit_from_dimensions(100, 100) == 20500

    assert get_step_limit_from_dimensions(None, None) == 2500
    assert get_step_limit_from_dimensions(None, 10) == 2500
    assert get_step_limit_from_dimensions(10, None) == 2500


def test_find_bounds():
    # Case 1: No objects
    scene = Scene(objects=[])
    assert scene.find_bounds() == []

    bounds_1 = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1),
        Vector3d(x=2, y=0, z=1),
        Vector3d(x=2, y=0, z=2),
        Vector3d(x=1, y=0, z=2)
    ], max_y=1, min_y=0)
    bounds_2 = ObjectBounds(box_xz=[
        Vector3d(x=-1, y=0, z=-1),
        Vector3d(x=-2, y=0, z=-1),
        Vector3d(x=-2, y=0, z=-2),
        Vector3d(x=-1, y=0, z=-2)
    ], max_y=1, min_y=0)

    # Case 2: 1 object
    scene = Scene(objects=[
        {'shows': [{'boundingBox': bounds_1}]}
    ])
    assert scene.find_bounds() == [bounds_1]

    # Case 3: 2 objects
    scene = Scene(objects=[
        {'shows': [{'boundingBox': bounds_1}]},
        {'shows': [{'boundingBox': bounds_2}]}
    ])
    assert scene.find_bounds() == [bounds_1, bounds_2]
    buffer = geometry.FLOOR_FEATURE_BOUNDS_BUFFER
    bounds_3 = ObjectBounds(box_xz=[
        Vector3d(x=2.5 + buffer, y=0, z=2.5 + buffer),
        Vector3d(x=3.5 - buffer, y=0, z=2.5 + buffer),
        Vector3d(x=3.5 - buffer, y=0, z=3.5 - buffer),
        Vector3d(x=2.5 + buffer, y=0, z=3.5 - buffer)
    ], max_y=100, min_y=0)
    bounds_4 = ObjectBounds(box_xz=[
        Vector3d(x=-3.5 + buffer, y=0, z=-3.5 + buffer),
        Vector3d(x=-2.5 - buffer, y=0, z=-3.5 + buffer),
        Vector3d(x=-2.5 - buffer, y=0, z=-2.5 - buffer),
        Vector3d(x=-3.5 + buffer, y=0, z=-2.5 - buffer)
    ], max_y=100, min_y=0)

    # Case 4: 1 hole
    scene = Scene(holes=[Vector2dInt(x=3, z=3)], objects=[])
    assert scene.find_bounds() == [bounds_3]

    # Case 5: 2 holes
    scene = Scene(
        holes=[Vector2dInt(x=3, z=3), Vector2dInt(x=-3, z=-3)],
        objects=[]
    )
    assert scene.find_bounds() == [bounds_3, bounds_4]

    # Case 6: holes and objects
    scene = Scene(
        holes=[Vector2dInt(x=3, z=3), Vector2dInt(x=-3, z=-3)],
        objects=[
            {'shows': [{'boundingBox': bounds_1}]},
            {'shows': [{'boundingBox': bounds_2}]}
        ]
    )
    assert scene.find_bounds() == [bounds_3, bounds_4, bounds_1, bounds_2]

    # Case 7: floor textures
    scene = Scene(floor_textures=[FloorTexturesConfig(
        material='blue',
        positions=[Vector2dInt(x=0, z=0)]
    )], objects=[])
    assert scene.find_bounds() == []

    # Case 8: 1 lava area
    scene = Scene(lava=[Vector2dInt(x=3, z=3)], objects=[])
    assert scene.find_bounds() == [bounds_3]

    # Case 9: 2 lava areas
    scene = Scene(
        lava=[Vector2dInt(x=3, z=3), Vector2dInt(x=-3, z=-3)],
        objects=[]
    )
    assert scene.find_bounds() == [bounds_3, bounds_4]

    # Case 10: lava areas and objects
    scene = Scene(
        lava=[Vector2dInt(x=3, z=3), Vector2dInt(x=-3, z=-3)],
        objects=[
            {'shows': [{'boundingBox': bounds_1}]},
            {'shows': [{'boundingBox': bounds_2}]}
        ]
    )
    assert scene.find_bounds() == [bounds_3, bounds_4, bounds_1, bounds_2]

    # Case 11: everything
    scene = Scene(floor_textures=FloorTexturesConfig(
        material='blue',
        positions=[Vector2dInt(x=0, z=0)]),
        lava=[Vector2dInt(x=3, z=3)],
        holes=[Vector2dInt(x=-3, z=-3)],
        objects=[
            {'shows': [{'boundingBox': bounds_1}]},
            {'shows': [{'boundingBox': bounds_2}]}
    ]
    )
    assert scene.find_bounds() == [bounds_4, bounds_3, bounds_1, bounds_2]


def test_find_bounds_ignore_id():
    bounds_1 = ObjectBounds(box_xz=[
        Vector3d(x=1, y=0, z=1),
        Vector3d(x=2, y=0, z=1),
        Vector3d(x=2, y=0, z=2),
        Vector3d(x=1, y=0, z=2)
    ], max_y=1, min_y=0)
    bounds_2 = ObjectBounds(box_xz=[
        Vector3d(x=-1, y=0, z=-1),
        Vector3d(x=-2, y=0, z=-1),
        Vector3d(x=-2, y=0, z=-2),
        Vector3d(x=-1, y=0, z=-2)
    ], max_y=1, min_y=0)

    # Case 1: 1 object, ignore 0
    scene = Scene(objects=[
        {'id': 'id_1', 'shows': [{'boundingBox': bounds_1}]}
    ])
    assert scene.find_bounds(ignore_ids='absent_id') == [bounds_1]

    # Case 2: 1 object, ignore 1
    scene = Scene(objects=[
        {'id': 'id_1', 'shows': [{'boundingBox': bounds_1}]}
    ])
    assert scene.find_bounds(ignore_ids='id_1') == []

    # Case 3: 2 objects, ignore 1
    scene = Scene(objects=[
        {'id': 'id_1', 'shows': [{'boundingBox': bounds_1}]},
        {'id': 'id_2', 'shows': [{'boundingBox': bounds_2}]}
    ])
    assert scene.find_bounds(ignore_ids='id_1') == [bounds_2]

    # Case 4: 2 objects, ignore 2
    scene = Scene(objects=[
        {'id': 'id_1', 'shows': [{'boundingBox': bounds_1}]},
        {'id': 'id_2', 'shows': [{'boundingBox': bounds_2}]}
    ])
    assert scene.find_bounds(ignore_ids=['id_1', 'id_2']) == []
