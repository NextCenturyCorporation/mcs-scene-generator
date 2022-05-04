from os import getuid

from machine_common_sense.config_manager import Vector3d

from generator import ObjectBounds, base_objects
from generator.scene import Scene
from ideal_learning_env.goal_services import TARGET_LABEL
from ideal_learning_env.object_services import (
    InstanceDefinitionLocationTuple,
    ObjectRepository,
)


def prior_scene(last_step: int = None):
    scene = Scene()
    if last_step:
        scene.goal['last_step'] = last_step
    return scene


def prior_scene_custom_size(x, z):
    scene = Scene()
    scene.set_room_dimensions(x, 3, z)
    return scene


def prior_scene_custom_start(start_x=0, start_z=0):
    scene = Scene()
    scene.set_performer_start_position(start_x, 0, start_z)
    return scene


def prior_scene_custom(size_x=10, size_z=10, start_x=0, start_z=0):
    scene = Scene()
    scene.set_performer_start_position(start_x, 0, start_z)
    scene.set_room_dimensions(size_x, 3, size_z)
    return scene


def prior_scene_with_target(
        size_x=10, size_z=10, start_x=0, start_z=0, add_to_repo=False):
    scene = prior_scene_custom(size_x, size_z, start_x, start_z)
    target_object = {
        'id': '743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f',
        'type': 'soccer_ball',
        'mass': 1.0,
        'salientMaterials': ['rubber'],
        'debug':
            {'dimensions':
                {'x': 0.22,
                 'y': 0.22,
                 'z': 0.22},
             'info': [
                    'tiny', 'light', 'black', 'white', 'rubber', 'ball',
                    'black white', 'tiny light', 'tiny rubber',
                    'tiny black white', 'tiny ball', 'light rubber',
                    'light black white', 'light ball',
                    'rubber black white', 'rubber ball', 'black white ball',
                    'tiny light black white rubber ball'],
             'positionY': 0.11, 'role': '', 'shape': ['ball'],
             'size': 'tiny', 'untrainedCategory': False,
             'untrainedColor': False, 'untrainedCombination': False,
             'untrainedShape': False, 'untrainedSize': False, 'offset':
             {'x': 0, 'y': 0.11, 'z': 0}, 'materialCategory': [], 'color':
             ['black', 'white'], 'weight': 'light', 'goalString':
             'tiny light black white rubber ball', 'salientMaterials':
             ['rubber'], 'enclosedAreas': []}, 'moveable': True,
        'pickupable': True, 'shows': [
                 {'rotation': {'x': 0, 'y': 45, 'z': 0},
                  'position': {'x': -1.03, 'y': 0.11, 'z': 4.08},
                  'boundingBox': ObjectBounds(box_xz=[
                      Vector3d(**{'x': -0.8744, 'y': 0, 'z': 4.08}),
                      Vector3d(**{'x': -1.03, 'y': 0, 'z': 3.9244}),
                      Vector3d(**{'x': -1.1856, 'y': 0, 'z': 4.08}),
                      Vector3d(**{'x': -1.03, 'y': 0, 'z': 4.2356})
                  ], max_y=0.22, min_y=0),
                  'stepBegin': 0, 'scale': {'x': 1, 'y': 1, 'z': 1}}],
        'materials': []}

    scene.objects = [target_object]
    goal = {
        "metadata": {
            "target": {
                "id": "743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f"
            }
        },
        "last_step": 1000,
        "category": "retrieval"
    }
    scene.goal = goal
    ObjectRepository.get_instance().clear()
    if add_to_repo:
        target_defn = base_objects.create_soccer_ball()
        target_loc = target_object['shows'][0]
        t = InstanceDefinitionLocationTuple(
            target_object, target_defn, target_loc)
        ObjectRepository.get_instance().add_to_labeled_objects(t, TARGET_LABEL)
    return scene


def prior_scene_with_wall(
    size_x: int = 10,
    size_z: int = 10,
    start_x: float = 0,
    start_z: float = 0,
    target: bool = False
) -> Scene:
    scene = (
        prior_scene_with_target(size_x, size_z, start_x, start_z) if target
        else prior_scene_custom(size_x, size_z, start_x, start_z)
    )
    instance = {
        'id': 'occluding_wall',
        'type': 'cube',
        'mass': 100,
        'materials': ['Custom/MCS/Grey'],
        'shows': [{
            'position': {'x': -2, 'y': 0.5, 'z': 1},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': {'x': 2, 'y': 1, 'z': 0.1},
            'stepBegin': 0,
            'boundingBox': ObjectBounds(box_xz=[
                Vector3d(x=-1, y=0, z=1.1), Vector3d(x=-3, y=0, z=1.1),
                Vector3d(x=-3, y=0, z=0.9), Vector3d(x=-1, y=0, z=0.9)
            ], max_y=1, min_y=0)
        }]
    }
    scene.objects.append(instance)
    idl = InstanceDefinitionLocationTuple(instance, None, instance['shows'][0])
    ObjectRepository.get_instance().add_to_labeled_objects(idl, 'test_wall')
    return scene


def add_object_with_position_to_repo(label, x, y, z):
    """This function adds an object to the repo, but with very limited
    features.  We can add more features as needed"""
    obj_repo = ObjectRepository.get_instance()
    idl = InstanceDefinitionLocationTuple({
        'id': getuid(),
        'shows': [{
            'position': {
                'x': x,
                'y': y,
                'z': z
            },
            'boundingBox': ObjectBounds(
                box_xz=[], max_y=y + 0.5, min_y=y - 0.5)

        }]
    }, None, None)
    obj_repo.add_to_labeled_objects(idl, label)
