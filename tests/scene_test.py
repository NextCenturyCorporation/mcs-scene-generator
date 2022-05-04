from machine_common_sense.config_manager import Vector3d

from generator.scene import Scene, get_step_limit_from_dimensions

from .ile_helper import prior_scene_with_target


def test_get_target_object_None():
    scene = Scene()
    assert scene.get_target_object() is None


def test_get_target_object_with_target():
    scene = prior_scene_with_target()
    obj = scene.get_target_object()
    assert obj["type"] == "soccer_ball"
    assert obj["id"] == "743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f"
    assert obj["moveable"]
    assert obj["pickupable"]
    show = obj["shows"][0]
    assert show["rotation"] == {"x": 0, "y": 45, "z": 0}
    assert show["position"] == {"x": -1.03, "y": 0.11, "z": 4.08}
    assert show["scale"] == {"x": 1, "y": 1, "z": 1}


def test_scene_default():
    scene = Scene()
    assert scene.ceiling_material is None
    assert scene.debug == {}
    assert scene.floor_material is None
    assert scene.floor_properties is None
    assert scene.floor_textures == []
    assert scene.goal == {"metadata": {}}
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
    assert scene.version is None
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
    scene.set_performer_start_rotation(90)
    assert scene.performer_start.rotation == Vector3d(x=0, y=90, z=0)
    scene.set_performer_start_rotation(258)
    assert scene.performer_start.rotation == Vector3d(x=0, y=258, z=0)


def test_to_dict():
    scene = Scene()
    d = scene.to_dict()
    assert d == {
        "debug": {},
        "goal": {
            "metadata": {}},
        "holes": [],
        "isometric": False,
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

    scene.set_performer_start_rotation(258)
    scene.set_performer_start_position(1, 2, 3)
    scene.set_room_dimensions(4, 5, 6)
    scene.name = "test"
    scene.objects.append({"name": "pretend object"})
    scene.lava.append({
        "x": 0,
        "z": -1
    })
    scene.holes.append({
        "x": 3,
        "z": 4
    })
    d = scene.to_dict()
    assert d == {
        "debug": {},
        "goal": {
            "metadata": {}},
        "holes": [{
            "x": 3,
            "z": 4
        }],
        "isometric": False,
        "lava": [{
            "x": 0,
            "z": -1
        }],
        "name": "test",
        "objects": [{"name": "pretend object"}],
        "screenshot": False,
        "floorTextures": [],
        "intuitivePhysics": False,
        "performerStart": {
            "position": {
                "x": 1,
                "y": 2,
                "z": 3},
            "rotation": {
                "x": 0,
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
