import random
from os import getuid

from machine_common_sense.config_manager import Goal, Vector3d

from generator import ObjectBounds, Scene
from generator.base_objects import create_soccer_ball
from generator.geometry import calculate_rotations
from generator.instances import instantiate_object
from ideal_learning_env.agent_component import SpecificAgentComponent
from ideal_learning_env.defs import TARGET_LABEL
from ideal_learning_env.interactable_objects_component import (
    SpecificInteractableObjectsComponent
)
from ideal_learning_env.object_services import (
    InstanceDefinitionLocationTuple,
    ObjectRepository
)
from ideal_learning_env.structural_objects_component import (
    SpecificStructuralObjectsComponent
)


def prior_scene(last_step: int = None):
    scene = Scene()
    if last_step:
        scene.goal.last_step = last_step
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


def prior_passive_scene(last_step: int = None):
    scene = Scene()
    scene.intuitive_physics = True
    scene.version = 3
    scene.set_performer_start_position(0, 0, -4.5)
    scene.set_performer_start_rotation(0, 0)
    scene.set_room_dimensions(20, 10, 20)
    if last_step:
        scene.goal.last_step = last_step
    return scene


def check_rotation(agent, object):
    a_steps, a_step_size, a_shift = 0, 0, 0
    object_position = object['shows'][0]['position']
    if ('rotates' in agent):
        a_steps = agent['rotates'][0]['stepEnd'] - \
            agent['rotates'][0]['stepBegin'] + 1
        a_step_size = agent['rotates'][0]['vector']['y']
        a_shift = a_step_size * a_steps

        if ('moveToPosition' in object['debug']):
            if (int(object['debug']['moveToPositionBy']) <=
                    agent['rotates'][0]['stepBegin']):
                object_position = object['debug']['moveToPosition']

    else:
        a_shift = 0
        a_step_size = 0
        a_steps = 0

    _, target_rotation = calculate_rotations(
        Vector3d(**agent['shows'][0]['position']),
        Vector3d(**object_position),
        True
    )

    curr_rotation = round(agent['shows'][0]['rotation']['y'], 0)
    target_rotation = round(target_rotation, 0)
    a_shift = round(a_shift, 0)

    if (a_shift > 0):
        # Clockwise rotation
        return (curr_rotation + a_shift % 360) == (target_rotation)
    elif (a_shift < 0):
        # Counter-Clockwise rotation
        # Negative angles make this complicated.
        if (abs(a_shift) < abs(curr_rotation)):
            return (curr_rotation + a_shift) == target_rotation
        else:
            return ((curr_rotation + a_shift + 360) % 360 == target_rotation)


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
    goal = Goal(
        metadata={
            "target": {
                "id": "743a91ad-fa2a-42a6-bf6b-2ac737ab7f8f"
            }
        },
        last_step=1000,
        category="retrieval"
    )
    scene.goal = goal
    ObjectRepository.get_instance().clear()
    if add_to_repo:
        target_defn = create_soccer_ball()
        target_loc = target_object['shows'][0]
        t = InstanceDefinitionLocationTuple(
            target_object, target_defn, target_loc)
        ObjectRepository.get_instance().add_to_labeled_objects(t, TARGET_LABEL)
    return scene


def prior_scene_with_targets():
    scene = prior_scene()
    target_1 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': 1, 'y': 0.11, 'z': 2}}
    )
    target_2 = instantiate_object(
        create_soccer_ball(),
        {'position': {'x': 3, 'y': 0.11, 'z': 4}}
    )
    scene.objects = [target_1, target_2]
    scene.goal = Goal(
        category='multi retrieval',
        metadata={
            'targets': [
                {'id': target_1['id']},
                {'id': target_2['id']}
            ]
        }
    )
    return scene


def prior_scene_with_wall(
    size_x: int = 10,
    size_z: int = 10,
    start_x: float = 0,
    start_z: float = 0,
    target: bool = False,
    passive: bool = False
) -> Scene:
    scene = prior_passive_scene() if passive else (
        prior_scene_with_target(size_x, size_z, start_x, start_z) if target
        else prior_scene_custom(size_x, size_z, start_x, start_z)
    )
    instance = {
        'id': 'occluding_wall',
        'type': 'cube',
        'debug': {},
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


def create_test_obj_scene(
        perf_start_x=0, perf_start_z=3,
        object_start_x=0, object_start_z=0):
    """This creates a scene with a small object in the room.
    The object shapes here are not irregular in shape (ex. hooked_tool)
    to keep things simple. This is mostly useful for `sidesteps`
    testing which requires an object already being in the scene for
    the performer to sidestep.
    """
    scene = prior_scene_custom_start(
        start_x=perf_start_x, start_z=perf_start_z)
    object_component = SpecificInteractableObjectsComponent({
        "specific_interactable_objects": [{
            "num": 1,
            "labels": "object",
            "scale": 0.1,
            "shape": ["block_blue_letter_s", "apple_1", "truck_3", "chest_6"],
            "position": {
                "x": object_start_x,
                "z": object_start_z
            }
        }]
    })
    return object_component.update_ile_scene(scene)


def create_placers_turntables_scene(
        placer_start_step=1, turntable_start_step=1):
    """This creates a scene with a turntable and placer useful for
    `freeze_while_moving` testing.
    """
    scene = prior_scene_custom(10, 10, 0, 4)
    structural_component = SpecificStructuralObjectsComponent({
        'structural_turntables': [{
            'num': 1,
            'position': {
                'x': 0,
                'y': 0,
                'z': 0
            },
            'rotation_y': 0,
            'turntable_radius': 2,
            'turntable_movement': {
                'step_begin': turntable_start_step,
                'step_end': turntable_start_step + 10,
                'rotation_y': 5,
            }
        }],
        'placers': [{
            'num': 1,
            'activation_step': placer_start_step,
            "deactivation_step": placer_start_step + 10,
            'end_height': 0
        }]
    })
    ObjectRepository.get_instance().clear()
    scene = structural_component.update_ile_scene(scene)
    return scene


def create_agent_scene(number_of_agents=1):
    """This creates a scene with an agent with random actions useful for
    `freeze_while_moving` testing.
    """
    scene = prior_scene_custom(10, 10, 0, 4)
    step_begin_options = list(range(1, 9999))
    agent_component = SpecificAgentComponent({
        'specific_agents': {
            'num': number_of_agents,
            'pointing': {
                'step_begin': step_begin_options,
                'walk_distance': 0.6
            }
        }
    })
    ObjectRepository.get_instance().clear()
    scene = agent_component.update_ile_scene(scene)
    return scene


def create_random_agent_placer_turntable_scene():
    """This creates a scene with agent, placers, and turntables for
    `freeze_while_moving` testing with random setup.
    """
    number_of_agents = random.randint(1, 5)
    number_of_placers = random.randint(1, 5)
    number_of_turntables = random.randint(1, 5)
    structural_step_begin_options = list(range(1, 1000))
    structural_step_end_options = list(range(1000, 2000))
    agent_step_begin_options = list(range(1, 2000))

    scene = prior_scene_custom(100, 100, 0, 4)

    agent_component = SpecificAgentComponent({
        'specific_agents': {
            'num': number_of_agents,
            'pointing': {
                'step_begin': agent_step_begin_options,
                'walk_distance': 0.6
            }
        }
    })
    structural_component = SpecificStructuralObjectsComponent({
        'structural_turntables': [{
            'num': number_of_turntables,
            'rotation_y': 0,
            'turntable_radius': 2,
            'turntable_movement': {
                'step_begin': structural_step_begin_options,
                'step_end': structural_step_end_options,
                'rotation_y': 5,
            }
        }],
        'placers': [{
            'num': number_of_placers,
            'activation_step': structural_step_begin_options,
            "deactivation_step": structural_step_end_options,
            'end_height': 0
        }]
    })
    ObjectRepository.get_instance().clear()
    scene = structural_component.update_ile_scene(scene)
    scene = agent_component.update_ile_scene(scene)
    return scene


def create_specific_agent_placer_turntable_scene(
        agent_start, placer_start, turntable_start):
    """This creates a scene with agent, placers, and turntables for
    `freeze_while_moving` testing with specific setup.
    """
    scene = prior_scene_custom(20, 20, 0, 4)
    agent_component = SpecificAgentComponent({
        'specific_agents': {
            'num': 1,
            'pointing': {
                'step_begin': agent_start,
                'walk_distance': 0.6
            }
        }
    })
    structural_component = SpecificStructuralObjectsComponent({
        'structural_turntables': [{
            'num': 1,
            'rotation_y': 0,
            'turntable_radius': 2,
            'turntable_movement': {
                'step_begin': turntable_start,
                'step_end': turntable_start + 10,
                'rotation_y': 5,
            }
        }],
        'placers': [{
            'num': 1,
            'activation_step': placer_start,
            "deactivation_step": placer_start + 10,
            'end_height': 0
        }]
    })
    ObjectRepository.get_instance().clear()
    scene = structural_component.update_ile_scene(scene)
    scene = agent_component.update_ile_scene(scene)
    return scene
