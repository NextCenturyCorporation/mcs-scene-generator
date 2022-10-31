from generator import Scene
from hypercube import scene_generator

STARTER_SCENE = scene_generator.STARTER_SCENE


def map_id_to_scene(scenes):
    scene_dict = {}
    for index, scene in enumerate(scenes):
        scene_id = scene.goal['sceneInfo']['id'][0].lower()
        scene_dict[scene_id] = (scene, index)
    return scene_dict


def verify_scene(
    scene: Scene,
    task_type,
    slice_count,
    dimensions=None,
    holes=False,
    lava=False,
    partition_floor=False,
    position=None,
    rotation=None
):
    assert scene
    assert scene.version == 2
    assert scene.goal['category'] == 'retrieval'
    assert scene.goal['description']
    assert scene.goal['last_step']

    if dimensions:
        assert scene.room_dimensions.x == dimensions[0]
        assert scene.room_dimensions.y == dimensions[1]
        assert scene.room_dimensions.z == dimensions[2]
    else:
        # Assume room dimensions are always defined, but may be random
        assert scene.room_dimensions

    if position:
        assert scene.performer_start.position.x == position[0]
        assert scene.performer_start.position.y == position[1]
        assert scene.performer_start.position.z == position[2]
    else:
        # Assume performer start position is always defined, but may be random
        assert scene.performer_start.position

    if rotation:
        assert scene.performer_start.rotation.x == rotation[0]
        assert scene.performer_start.rotation.y == rotation[1]
    else:
        # Assume performer start rotation is always defined, but may be random
        assert scene.performer_start.rotation

    # The floor_textures property is not currently used
    assert not scene.floor_textures

    # Properties only used in passive scenes
    assert not scene.intuitive_physics
    assert not scene.isometric

    assert bool(scene.holes) == holes
    assert bool(scene.lava) == lava
    assert bool(scene.partition_floor) == partition_floor
    assert len(scene.goal['sceneInfo']['slices']) == slice_count

    assert scene.goal['sceneInfo']['primaryType'] == 'interactive'
    assert scene.goal['sceneInfo']['secondaryType'] == 'retrieval'
    assert scene.goal['sceneInfo']['tertiaryType'] == task_type
    assert scene.goal['sceneInfo']['quaternaryType'] == (
        'action variable' if bool(scene.goal.get('action_list')) else
        'action full'
    )
