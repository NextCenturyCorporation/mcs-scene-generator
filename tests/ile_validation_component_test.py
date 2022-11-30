import pytest
from machine_common_sense.config_manager import Vector3d

from generator import ObjectBounds
from ideal_learning_env.defs import ILEException
from ideal_learning_env.object_services import ObjectRepository
from ideal_learning_env.validation_component import ValidPathComponent

from .ile_helper import prior_scene, prior_scene_with_target


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()

    # Run test
    yield

    # Cleanup
    ObjectRepository.get_instance().clear()


def test_valid_path_off_by_defaults():
    component = ValidPathComponent({})
    assert component.check_valid_path is None
    assert component.get_check_valid_path() is False

    component.update_ile_scene(prior_scene())
    assert component.last_distance is None
    assert component.last_path is None
    # Just don't raise.


def test_valid_path_no_obstacles():
    component = ValidPathComponent({'check_valid_path': True})
    assert component.check_valid_path
    assert component.get_check_valid_path()

    component.update_ile_scene(prior_scene_with_target(add_to_repo=True))
    assert component.last_distance == pytest.approx(4.2, 0.1)
    # second path entry is location of target
    assert component.last_path == [(0, 0), (-1.03, 4.08)]
    # Just don't raise.


def test_valid_path_no_target():
    component = ValidPathComponent({'check_valid_path': True})
    assert component.check_valid_path
    assert component.get_check_valid_path()

    component.update_ile_scene(prior_scene())
    assert component._delayed_target


def test_valid_path_no_valid_performer_start():
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target()
    scene.set_performer_start_position(x=10, y=0.5, z=10)
    assert component.check_valid_path

    assert component.get_check_valid_path()

    component.update_ile_scene(scene)
    assert component._delayed_performer_start


def test_valid_path_blocked_by_holes():
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target()
    # create blocked by holes
    holes = scene.holes
    for i in range(11):
        holes.append({'x': i - 5, 'z': 2})

    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_valid_path_blocked_by_lava():
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target()

    # create blocked by lava
    scene.lava = [{'x': i - 5, 'z': 2} for i in range(11)]

    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_valid_path_blocked_by_platforms():
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target()
    # create blocked by platform
    objs = scene.objects
    bb = ObjectBounds([Vector3d(x=4.9, y=0, z=2.4386),
                       Vector3d(x=4.9, y=0, z=-2.4386),
                       Vector3d(x=-4.9, y=0, z=-2.4386),
                       Vector3d(x=-4.9, y=0, z=2.4386)],
                      max_y=2.0, min_y=0.0)

    platform = {
        "id": "platform_8c30bd12-0f0f-494f-a127-de362a54e79d",
        "type": "cube",
        "debug": {
            "color": [
              "red"
            ],
            "info": [
                "red",
                "platform",
                "red platform"
            ],
            "dimensions": {
                "x": 9.8,
                "y": 0.5,
                "z": 0.8772
            },
            "random_position": False,
            "labels": [
                "platforms"
            ]
        },
        "mass": 537,
        "materials": [
            "UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1"],
        "kinematic": True,
        "structure": True,
        "shows": [
            {
                "stepBegin": 0,
                "position": {
                    "x": 0,
                    "y": 0.25,
                    "z": 2
                },
                "rotation": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
                "scale": {
                    "x": 9.8,
                    "y": 0.5,
                    "z": 0.8772
                },
                "boundingBox": bb
            }
        ]
    }
    objs.append(platform)

    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_valid_path_blocked_by_ramp():
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target()
    # create blocked by ramp
    objs = scene.objects
    bb = ObjectBounds([Vector3d(x=4.9, y=0, z=2.4386),
                       Vector3d(x=4.9, y=0, z=-2.4386),
                       Vector3d(x=-4.9, y=0, z=-2.4386),
                       Vector3d(x=-4.9, y=0, z=2.4386)],
                      max_y=2.0, min_y=0.0)

    ramp = {
        "id": "ramp_8c30bd12-0f0f-494f-a127-de362a54e79d",
        "type": "triangle",
        "debug": {
            "color": [
              "red"
            ],
            "info": [
                "red",
                "ramp",
                "red ramp"
            ],
            "dimensions": {
                "x": 9.8,
                "y": 0.5,
                "z": 0.8772
            },
            "random_position": False,
            "labels": [
                "ramps"
            ]
        },
        "mass": 537,
        "materials": [
            "UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1"],
        "kinematic": True,
        "structure": True,
        "shows": [
            {
                "stepBegin": 0,
                "position": {
                    "x": 0,
                    "y": 0.25,
                    "z": 2
                },
                "rotation": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
                "scale": {
                    "x": 9.8,
                    "y": 0.5,
                    "z": 0.8772
                },
                "boundingBox": bb
            }
        ]
    }
    objs.append(ramp)

    with pytest.raises(ILEException):
        component.update_ile_scene(scene)


def test_valid_path_with_platform_and_ramp():
    platform_bb = ObjectBounds([Vector3d(x=2.5, y=0, z=-1.5),
                                Vector3d(x=2.5, y=0, z=-2.5),
                                Vector3d(x=1.5, y=0, z=-2.5),
                                Vector3d(x=1.5, y=0, z=-1.5)],
                               max_y=0.5, min_y=0.0)

    ramp_bb = ObjectBounds([Vector3d(x=2.5, y=0, z=-1.6343),
                            Vector3d(x=3.0177, y=0, z=-1.6343),
                            Vector3d(x=3.0177, y=0, z=-2.4928),
                            Vector3d(x=2.5, y=0, z=-2.4928)],
                           max_y=0.5, min_y=0.0)
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target()
    scene.set_performer_start_position(x=1.9, y=0.5, z=-2.009)
    scene.set_performer_start_rotation(x=0, y=225)

    objs = scene.objects

    platform = {
        "id": "platform_34a5ce6b-8d0d-476f-a82f-74d18ca7e0c0",
        "type": "cube",
        "debug": {
            "color": [
              "red"
            ],
            "info": [
                "red",
                "platform",
                "red platform"
            ],
            "dimensions": {
                "x": 1,
                "y": 0.5,
                "z": 1
            },
            "random_position": False,
            "labels": [
                "platforms",
                "start_structure",
                "connected_to_ramp"
            ],
            "gaps": {
                "right": [
                    {
                        "high": 0.8657,
                        "low": 0.0072
                    }
                ]
            }
        },
        "mass": 62,
        "materials": ["AI2-THOR/Materials/Ceramics/RedBrick"],
        "kinematic": True,
        "structure": True,
        "lips": {
            "front": False,
            "back": False,
            "left": False,
            "right": False
        },
        "shows": [
            {
                "stepBegin": 0,
                "position": {
                    "x": 2,
                    "y": 0.25,
                    "z": -2
                },
                "rotation": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
                "scale": {
                    "x": 1,
                    "y": 0.5,
                    "z": 1
                },
                "boundingBox": platform_bb
            }
        ]
    }
    ramp = {
        "id": "ramp_c72350a6-c113-4f51-b061-b041cfd7b1a3",
        "type": "triangle",
        "debug": {
            "color": [
              "red"
            ],
            "info": [
                "red",
                "ramp",
                "ramp_44.00360316240082_degree",
                "red ramp",
                "red ramp_44.00360316240082_degree"
            ],
            "dimensions": {
                "x": 0.8585,
                "y": 0.5,
                "z": 0.5177
            },
            "random_position": True,
            "labels": [
                "ramps",
                "bidirectional"
            ]
        },
        "mass": 28,
        "materials": ["AI2-THOR/Materials/Ceramics/RedBrick"],
        "kinematic": True,
        "structure": True,
        "shows": [
            {
                "stepBegin": 0,
                "position": {
                    "x": 2.7588,
                    "y": 0.25,
                    "z": -2.0635
                },
                "rotation": {
                    "x": 0,
                    "y": 270,
                    "z": 0
                },
                "scale": {
                    "x": 0.8585,
                    "y": 0.5,
                    "z": 0.5177
                },
                "boundingBox": ramp_bb
            }
        ]
    }
    objs.append(platform)
    objs.append(ramp)

    component.update_ile_scene(scene)
    assert component.last_distance == pytest.approx(9.049129686470053)


def test_valid_path_with_platform_and_ramp_delayed():
    platform_bb = ObjectBounds([Vector3d(x=2.5, y=0, z=-1.5),
                                Vector3d(x=2.5, y=0, z=-2.5),
                                Vector3d(x=1.5, y=0, z=-2.5),
                                Vector3d(x=1.5, y=0, z=-1.5)],
                               max_y=0.5, min_y=0.0)

    ramp_bb = ObjectBounds([Vector3d(x=2.5, y=0, z=-1.6343),
                            Vector3d(x=3.0177, y=0, z=-1.6343),
                            Vector3d(x=3.0177, y=0, z=-2.4928),
                            Vector3d(x=2.5, y=0, z=-2.4928)],
                           max_y=0.5, min_y=0.0)
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target()
    # start with invalid performer position
    scene.set_performer_start_position(x=10, y=0.5, z=10)
    scene.set_performer_start_rotation(x=0, y=225)

    objs = scene.objects

    platform = {
        "id": "platform_34a5ce6b-8d0d-476f-a82f-74d18ca7e0c0",
        "type": "cube",
        "debug": {
            "color": [
              "red"
            ],
            "info": [
                "red",
                "platform",
                "red platform"
            ],
            "dimensions": {
                "x": 1,
                "y": 0.5,
                "z": 1
            },
            "random_position": False,
            "labels": [
                "platforms",
                "start_structure",
                "connected_to_ramp"
            ],
            "gaps": {
                "right": [
                    {
                        "high": 0.8657,
                        "low": 0.0072
                    }
                ]
            }
        },
        "mass": 62,
        "materials": ["AI2-THOR/Materials/Ceramics/RedBrick"],
        "kinematic": True,
        "structure": True,
        "lips": {
            "front": False,
            "back": False,
            "left": False,
            "right": False
        },
        "shows": [
            {
                "stepBegin": 0,
                "position": {
                    "x": 2,
                    "y": 0.25,
                    "z": -2
                },
                "rotation": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
                "scale": {
                    "x": 1,
                    "y": 0.5,
                    "z": 1
                },
                "boundingBox": platform_bb
            }
        ]
    }
    ramp = {
        "id": "ramp_c72350a6-c113-4f51-b061-b041cfd7b1a3",
        "type": "triangle",
        "debug": {
            "color": [
              "red"
            ],
            "info": [
                "red",
                "ramp",
                "ramp_44.00360316240082_degree",
                "red ramp",
                "red ramp_44.00360316240082_degree"
            ],
            "dimensions": {
                "x": 0.8585,
                "y": 0.5,
                "z": 0.5177
            },
            "random_position": True,
            "labels": [
                "ramps",
                "bidirectional"
            ]
        },
        "mass": 28,
        "materials": ["AI2-THOR/Materials/Ceramics/RedBrick"],
        "kinematic": True,
        "structure": True,
        "shows": [
            {
                "stepBegin": 0,
                "position": {
                    "x": 2.7588,
                    "y": 0.25,
                    "z": -2.0635
                },
                "rotation": {
                    "x": 0,
                    "y": 270,
                    "z": 0
                },
                "scale": {
                    "x": 0.8585,
                    "y": 0.5,
                    "z": 0.5177
                },
                "boundingBox": ramp_bb
            }
        ]
    }
    objs.append(platform)
    objs.append(ramp)

    component.update_ile_scene(scene)
    assert component._delayed_performer_start
    assert component.get_num_delayed_actions() == 1

    scene.set_performer_start_position(x=1.9, y=0.5, z=-2.009)

    scene = component.run_delayed_actions(scene)
    assert component.last_distance == pytest.approx(9.049129686470053)


def test_valid_path_with_lava_and_holes():
    component = ValidPathComponent({'check_valid_path': True})
    scene = prior_scene_with_target(start_x=-3, start_z=-3)
    # create blocked by holes
    holes = scene.holes
    for i in range(8):
        holes.append({'x': i - 5, 'z': 3})

    scene.lava = [{'x': i - 3, 'z': 0} for i in range(8)]

    component.update_ile_scene(scene)
    assert component.last_distance == pytest.approx(15, 0.1)
