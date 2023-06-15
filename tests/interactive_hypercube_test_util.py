from generator import Scene, tags
from hypercube import scene_generator

STARTER_SCENE = scene_generator.STARTER_SCENE


def find_object(object_list, prefix):
    results = list(filter(lambda x: x['type'].startswith(prefix), object_list))
    return results[0] if len(results) else None


def find_objects(object_list, prefix):
    return list(filter(lambda x: x['type'].startswith(prefix), object_list))


def map_id_to_scene(scenes):
    scene_dict = {}
    for index, scene in enumerate(scenes):
        scene_id = scene.goal.scene_info['id'][0].lower()
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
    rotation=None,
    category='retrieval',
    passive=False
):
    assert scene
    assert scene.version == 2
    assert (scene.goal.category == category)
    assert not scene.goal.description if passive else \
        scene.goal.description
    assert scene.goal.last_step

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
    assert len(scene.goal.scene_info['slices']) == slice_count

    assert (scene.goal.scene_info['primaryType'] == 'interactive' or
            (scene.goal.scene_info['primaryType'] == 'passive' and passive))
    # TODO: MCS-1683: verify secondaryType/newer categories within ingest/UI
    assert (scene.goal.scene_info['secondaryType'] == category or
            scene.goal.scene_info['secondaryType'] == 'retrieval' or
            scene.goal.scene_info['secondaryType'] == 'passive' and passive)
    assert scene.goal.scene_info['tertiaryType'] == task_type
    assert scene.goal.scene_info['quaternaryType'] == (
        'action none' if (
            passive and scene.goal.scene_info['primaryType'] == 'passive')
        else
        'action variable' if bool(scene.goal.action_list) else
        'action full'
    )

    assert scene.goal.scene_info['domainType'] == (
        tags.get_domain_type(task_type)
    )
