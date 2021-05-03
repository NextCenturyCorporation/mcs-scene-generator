import intuitive_physics_hypercubes
import materials
import pytest
import random
import hypercubes
import util

from intuitive_physics_test_util import (
    BODY_TEMPLATE,
    get_object_list,
    verify_hypercube,
    verify_hypercube_variations,
    verify_hypercube_Collisions,
    verify_hypercube_ObjectPermanence,
    verify_hypercube_ShapeConstancy,
    verify_hypercube_SpatioTemporalContinuity,
    verify_object_fall_down_position,
    verify_object_tags,
    verify_same_object,
    verify_scene,
    verify_target_implausible_hide_step,
    verify_target_implausible_show_step,
    verify_target_implausible_shroud_step
)


def test_CollisionsHypercube_default_objects_move_across():
    hypercube = intuitive_physics_hypercubes.CollisionsHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None}
    )
    assert hypercube.is_move_across()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    object_dict = hypercube._create_default_objects(
        wall_material_tuple[0],
        wall_material_tuple[1]
    )
    assert verify_hypercube_variations(
        hypercube._variations_list,
        hypercube._target_list,
        hypercube._distractor_list,
        object_dict['target'],
        object_dict['non target'],
        1,
        1
    )
    assert verify_hypercube_Collisions(
        hypercube.is_move_across(),
        object_dict,
        hypercube._last_step,
        wall_material_tuple[0]
    )
    assert util.is_similar_except_in_color(
        object_dict['target'][0],
        object_dict['non target'][0],
        only_diagonal_size=True
    )


def test_CollisionsHypercube_default_scene_move_across():
    hypercube = intuitive_physics_hypercubes.CollisionsHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None}
    )
    assert hypercube.is_move_across()
    goal_template = hypercubes.initialize_goal(
        intuitive_physics_hypercubes.CollisionsHypercube.GOAL_TEMPLATE
    )
    scene = hypercube._create_default_scene(BODY_TEMPLATE, goal_template)
    verify_scene(scene, hypercube.is_move_across())
    assert 'collisions' == scene['goal']['sceneInfo']['tertiaryType']


def test_CollisionsHypercube_scenes_move_across():
    hypercube = intuitive_physics_hypercubes.CollisionsHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None}
    )
    assert hypercube.is_move_across()

    scene_list = hypercube.get_scenes()
    scene_dict = {}
    assert len(scene_list) == 3

    print(f'TARGET={hypercube._target_list[0]}')
    print(f'NON_TARGET={hypercube._distractor_list[0]}')

    for scene in scene_list:
        scene_id = scene['goal']['sceneInfo']['id'][0].lower()
        scene_dict[scene_id] = scene
        scene_name = scene['goal']['sceneInfo']['name']
        assert scene_name.startswith('COLL_')

    for i in ['a', 'c', 'h']:
        for j in [i + '2']:
            print(f'SCENE_ID={j}')
            scene = scene_dict[j]
            target_list = get_object_list(scene, 'target')
            non_target_list = get_object_list(scene, 'non target')
            occluder_list = get_object_list(
                scene,
                'intuitive physics occluder'
            )
            structural_object_list = get_object_list(scene, 'structural')

            assert len(target_list) == 1

            implausible = False
            eval_only = False

            # Verify non-target is in the scene.
            if i in ['c', 'h']:
                assert len(non_target_list) == 1
                assert util.is_similar_except_in_color(
                    target_list[0],
                    non_target_list[0],
                    only_diagonal_size=True
                )

            # Verify non-target is NOT in the scene.
            if i in ['a']:
                assert len(non_target_list) == 0

            # Verify target is NOT switched.
            if i in ['a', 'c', 'h']:
                assert verify_same_object(
                    target_list[0],
                    hypercube._variations_list[0].get('trained')
                )

            # Verify non-target is NOT switched.
            if i in ['c', 'h']:
                assert verify_same_object(
                    non_target_list[0],
                    hypercube._variations_list[1].get('trained')
                )

            # Verify non-target is repositioned.
            if i in ['h']:
                assert (
                    non_target_list[0]['shows'][0]['position']['x'] ==
                    hypercube._adjust_impact_position(
                        target_list[0],
                        non_target_list[0]
                    )
                )
                assert (
                    non_target_list[0]['shows'][0]['position']['z'] ==
                    target_list[0]['shows'][0]['position']['z']
                )

            # Verify non-target is NOT repositioned.
            if i in ['c']:
                assert (
                    non_target_list[0]['shows'][0]['position']['x'] ==
                    hypercube._distractor_list[0]['shows'][0]['position']['x']
                )
                assert (
                    non_target_list[0]['shows'][0]['position']['z'] ==
                    hypercube._distractor_list[0]['shows'][0]['position']['z']
                )

            assert len(occluder_list) == 0
            assert len(structural_object_list) == 0

            verify_scene(
                scene_dict[j],
                hypercube.is_move_across(),
                implausible,
                eval_only
            )

            verify_hypercube_Collisions(
                hypercube.is_move_across(),
                {
                    'target': target_list,
                    'non target': non_target_list,
                    'intuitive physics occluder': hypercube._occluder_list,
                    'context': hypercube._background_list
                },
                hypercube._last_step,
                scene_dict[j]['wallMaterial']
            )

            verify_object_tags(scene_dict[j], target_list, 'target', 'target')
            verify_object_tags(
                scene_dict[j],
                non_target_list,
                'non target',
                'non_target'
            )


def test_ObjectPermanenceHypercube_default_objects_fall_down():
    hypercube = intuitive_physics_hypercubes.ObjectPermanenceHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_fall_down=True
    )
    assert hypercube.is_fall_down()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    object_dict = hypercube._create_default_objects(
        wall_material_tuple[0],
        wall_material_tuple[1]
    )
    assert verify_hypercube_variations(
        hypercube._variations_list,
        hypercube._target_list,
        hypercube._distractor_list,
        object_dict['target'],
        object_dict['non target'],
        2,
        0
    )
    assert verify_hypercube_ObjectPermanence(
        hypercube.is_move_across(),
        object_dict,
        hypercube._last_step,
        wall_material_tuple[0]
    )


def test_ObjectPermanenceHypercube_default_scene_fall_down():
    hypercube = intuitive_physics_hypercubes.ObjectPermanenceHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_fall_down=True
    )
    assert hypercube.is_fall_down()
    goal_template = hypercubes.initialize_goal(
        intuitive_physics_hypercubes.ObjectPermanenceHypercube.GOAL_TEMPLATE
    )
    scene = hypercube._create_default_scene(BODY_TEMPLATE, goal_template)
    verify_scene(scene, hypercube.is_move_across())
    assert 'object permanence' == scene['goal']['sceneInfo']['tertiaryType']


def test_ShapeConstancyHypercube_default_objects_fall_down():
    hypercube = intuitive_physics_hypercubes.ShapeConstancyHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_fall_down=True
    )
    assert hypercube.is_fall_down()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    object_dict = hypercube._create_default_objects(
        wall_material_tuple[0],
        wall_material_tuple[1]
    )
    assert verify_hypercube_variations(
        hypercube._variations_list,
        hypercube._target_list,
        hypercube._distractor_list,
        object_dict['target'],
        object_dict['non target'],
        2,
        0
    )
    assert verify_hypercube_ShapeConstancy(
        hypercube.is_move_across(),
        object_dict,
        hypercube._last_step,
        wall_material_tuple[0]
    )


def test_ShapeConstancyHypercube_default_scene_fall_down():
    hypercube = intuitive_physics_hypercubes.ShapeConstancyHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_fall_down=True
    )
    assert hypercube.is_fall_down()
    goal_template = hypercubes.initialize_goal(
        intuitive_physics_hypercubes.ShapeConstancyHypercube.GOAL_TEMPLATE
    )
    scene = hypercube._create_default_scene(BODY_TEMPLATE, goal_template)
    verify_scene(scene, hypercube.is_move_across())
    assert 'shape constancy' == scene['goal']['sceneInfo']['tertiaryType']


def test_SpatioTemporalContinuityHypercube_default_objects_move_across():
    hypercube = intuitive_physics_hypercubes.SpatioTemporalContinuityHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_move_across=True
    )
    assert hypercube.is_move_across()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    object_dict = hypercube._create_default_objects(
        wall_material_tuple[0],
        wall_material_tuple[1]
    )
    assert verify_hypercube_variations(
        hypercube._variations_list,
        hypercube._target_list,
        hypercube._distractor_list,
        object_dict['target'],
        object_dict['non target'],
        1,
        1
    )
    assert verify_hypercube_SpatioTemporalContinuity(
        hypercube.is_move_across(),
        object_dict,
        hypercube._last_step,
        wall_material_tuple[0],
        hypercube._target_list[0]
    )


def test_SpatioTemporalContinuityHypercube_default_scene_move_across():
    hypercube = intuitive_physics_hypercubes.SpatioTemporalContinuityHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_move_across=True
    )
    assert hypercube.is_move_across()
    goal_template = hypercubes.initialize_goal(
        intuitive_physics_hypercubes.SpatioTemporalContinuityHypercube.GOAL_TEMPLATE  # noqa: E501
    )
    scene = hypercube._create_default_scene(BODY_TEMPLATE, goal_template)
    verify_scene(scene, hypercube.is_move_across())
    assert (
        'spatio temporal continuity' ==
        scene['goal']['sceneInfo']['tertiaryType']
    )


def test_GravitySupportHypercube_default_objects_fall_down():
    hypercube = intuitive_physics_hypercubes.GravitySupportHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_fall_down=True
    )
    assert hypercube.is_fall_down()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    object_dict = hypercube._create_default_objects(
        wall_material_tuple[0],
        wall_material_tuple[1]
    )

    assert hypercube._pole
    assert hypercube._target
    assert hypercube._visible_support

    for variations in [hypercube._pole, hypercube._target]:
        symmetric = variations.get('symmetric')
        assert symmetric
        asymmetric_left = variations.get('asymmetric_left')
        asymmetric_right = variations.get('asymmetric_right')
        assert asymmetric_left
        assert asymmetric_right
        assert symmetric['id'] == asymmetric_left['id']
        assert symmetric['id'] == asymmetric_right['id']
        assert util.are_materials_equivalent(
            symmetric['materials'],
            asymmetric_left['materials']
        )
        assert util.are_materials_equivalent(
            symmetric['materials'],
            asymmetric_right['materials']
        )

    assert object_dict['target'] == [hypercube._target.get('symmetric')]
    assert object_dict['structural'] == [
        hypercube._pole.get('symmetric'), hypercube._visible_support
    ]

    assert verify_hypercube(object_dict, wall_material_tuple[0])

    assert verify_object_fall_down_position(object_dict['target'][0], 'TARGET')

    assert hypercube._last_step == 60


def test_GravitySupportHypercube_default_scene_fall_down():
    hypercube = intuitive_physics_hypercubes.GravitySupportHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_fall_down=True
    )
    assert hypercube.is_fall_down()
    goal_template = hypercubes.initialize_goal(
        intuitive_physics_hypercubes.GravitySupportHypercube.GOAL_TEMPLATE
    )
    scene = hypercube._create_default_scene(BODY_TEMPLATE, goal_template)
    verify_scene(scene, hypercube.is_move_across(), last_step=60)
    assert 'gravity support' == scene['goal']['sceneInfo']['tertiaryType']


def test_ObjectPermanenceHypercube_scenes_fall_down():
    hypercube = intuitive_physics_hypercubes.ObjectPermanenceHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_fall_down=True
    )
    assert hypercube.is_fall_down()

    scene_list = hypercube.get_scenes()
    scene_dict = {}
    target_dict = {}
    assert len(scene_list) == 90

    print(f'TARGET_1={hypercube._target_list[0]}')
    print(f'TARGET_2={hypercube._target_list[1]}')

    for scene in scene_list:
        scene_id = scene['goal']['sceneInfo']['id'][0].lower()
        scene_dict[scene_id] = scene
        target_dict[scene_id] = get_object_list(scene, 'target')
        scene_name = scene['goal']['sceneInfo']['name']
        assert scene_name.startswith('OBJP_')

    for i in [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'aa'
    ]:
        for j in [i + '1', i + '2', i + '3', i + '4']:
            if j not in scene_dict:
                continue

            print(f'SCENE_ID={j}')
            target_list = target_dict[j]
            assert len(target_list) == (1 if j.endswith('1') else 2)

            implausible = False
            eval_only = False

            # Verify object one not switched.
            if i in ['a', 'd', 'g', 'j', 'm', 'p', 's', 'v', 'y']:
                assert verify_same_object(
                    target_list[0],
                    hypercube._variations_list[0].get('trained')
                )

            # Verify object one switched with untrained size variation.
            if i in ['b', 'e', 'h', 'k', 'n', 'q', 't', 'w', 'z']:
                eval_only = True
                assert verify_same_object(
                    target_list[0],
                    hypercube._variations_list[0].get('untrained_size')
                )

            # Verify object one switched with untrained shape variation.
            if i in ['c', 'f', 'i', 'l', 'o', 'r', 'u', 'x', 'aa']:
                eval_only = True
                assert verify_same_object(
                    target_list[0],
                    hypercube._variations_list[0].get('untrained_shape')
                )

            # Verify object two not switched.
            if (
                i in ['a', 'b', 'c', 'j', 'k', 'l', 's', 't', 'u'] and
                (not j.endswith('1'))
            ):
                assert verify_same_object(
                    target_list[1],
                    hypercube._variations_list[1].get('trained')
                )

            # Verify object two switched with untrained size variation.
            if i in ['d', 'e', 'f', 'm', 'n', 'o', 'v', 'w', 'x']:
                eval_only = True
                assert verify_same_object(
                    target_list[1],
                    hypercube._variations_list[1].get('untrained_size')
                )

            # Verify object two switched with untrained shape variation.
            if i in ['g', 'h', 'i', 'p', 'q', 'r', 'y', 'z', 'aa']:
                eval_only = True
                assert verify_same_object(
                    target_list[1],
                    hypercube._variations_list[1].get('untrained_shape')
                )

            # Verify object one disappears.
            if i in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']:
                implausible = True
                assert verify_target_implausible_hide_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[0],
                    target_list[0]
                )
                assert (
                    target_list[0]['shows'][0]['stepBegin'] ==
                    hypercube._target_list[0]['shows'][0]['stepBegin']
                )

            # Verify object one appears.
            if i in ['j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r']:
                implausible = True
                assert verify_target_implausible_show_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[0],
                    target_list[0],
                    hypercube._target_list[0]['shows'][0]
                )
                assert 'hides' not in target_list[0]
                # Ignore verifying position if it will appear later.
                target_list[0]['ignorePosition'] = True
                target_list[0]['ignoreShowStep'] = True

            # Verify object two disappears.
            if j.endswith('4'):
                implausible = True
                assert verify_target_implausible_hide_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[1],
                    target_list[1]
                )
                assert (
                    target_list[1]['shows'][0]['stepBegin'] ==
                    hypercube._target_list[1]['shows'][0]['stepBegin']
                )

            # Verify object two appears.
            if j.endswith('3'):
                implausible = True
                assert verify_target_implausible_show_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[1],
                    target_list[1],
                    hypercube._target_list[1]['shows'][0]
                )
                assert 'hides' not in target_list[1]
                # Ignore verifying position if it will appear later.
                target_list[1]['ignorePosition'] = True
                target_list[1]['ignoreShowStep'] = True

            # Verify no change in object one.
            if i in ['s', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'aa']:
                assert 'hides' not in target_list[0]
                assert (
                    target_list[0]['shows'][0]['stepBegin'] ==
                    hypercube._target_list[0]['shows'][0]['stepBegin']
                )

            # Verify no change in object two.
            if j.endswith('2'):
                assert 'hides' not in target_list[1]
                assert (
                    target_list[1]['shows'][0]['stepBegin'] ==
                    hypercube._target_list[1]['shows'][0]['stepBegin']
                )

            verify_scene(
                scene_dict[j],
                hypercube.is_move_across(),
                implausible,
                eval_only
            )

            verify_hypercube_ObjectPermanence(hypercube.is_move_across(), {
                'target': target_list,
                'non target': hypercube._distractor_list,
                'intuitive physics occluder': hypercube._occluder_list,
                'context': hypercube._background_list
            }, hypercube._last_step, scene_dict[j]['wallMaterial'])

            verify_object_tags(scene_dict[j], target_list, 'target', 'target')


def test_ShapeConstancyHypercube_scenes_fall_down():
    hypercube = intuitive_physics_hypercubes.ShapeConstancyHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_fall_down=True
    )
    assert hypercube.is_fall_down()

    scene_list = hypercube.get_scenes()
    scene_dict = {}
    target_dict = {}
    assert len(scene_list) == 42

    print(f'TARGET_1={hypercube._target_list[0]}')
    print(f'TARGET_2={hypercube._target_list[1]}')

    for scene in scene_list:
        scene_id = scene['goal']['sceneInfo']['id'][0].lower()
        scene_dict[scene_id] = scene
        target_dict[scene_id] = get_object_list(scene, 'target')
        scene_name = scene['goal']['sceneInfo']['name']
        assert scene_name.startswith('SHAP_')

    for i in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']:
        for j in [i + '1', i + '2', i + '3', i + '4']:
            if j not in scene_dict:
                continue

            print(f'SCENE_ID={j}')
            target_list = target_dict[j]

            target_index_1_b = -1
            target_index_2_b = -1
            target_list_size = 1

            if not j.endswith('1'):
                # Object two in scene.
                target_list_size += 1
            if i in ['e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']:
                # Object one transforms into new object.
                target_index_1_b = target_list_size
                target_list_size += 1
            if j.endswith('3') or j.endswith('4'):
                # Object two transforms into new object.
                target_index_2_b = target_list_size
                target_list_size += 1

            assert len(target_list) == target_list_size

            implausible = False
            eval_only = False

            # Verify object one not switched.
            if i in ['a', 'c', 'e', 'g', 'i', 'k']:
                assert verify_same_object(
                    target_list[0],
                    hypercube._variations_list[0].get('trained')
                )

            # Verify object one switched with untrained variation.
            if i in ['b', 'd', 'f', 'h', 'j', 'l']:
                eval_only = True
                assert verify_same_object(
                    target_list[0],
                    hypercube._variations_list[0].get('untrained_shape')
                )

            # Verify object two not switched.
            if i in ['a', 'b', 'e', 'f', 'i', 'j'] and (not j.endswith('1')):
                assert verify_same_object(
                    target_list[1],
                    hypercube._variations_list[1].get('trained')
                )

            # Verify object two switched with untrained shape variation.
            if i in ['c', 'd', 'g', 'h', 'k', 'l']:
                eval_only = True
                assert verify_same_object(
                    target_list[1],
                    hypercube._variations_list[1].get('untrained_shape')
                )

            # Verify object one transforms into different shape variation.
            if i in ['e', 'f', 'g', 'h']:
                implausible = True
                assert verify_same_object(
                    target_list[target_index_1_b],
                    hypercube._variations_list[0].get('different_shape')
                )
                assert (
                    target_list[0]['hides'][0]['stepBegin'] ==
                    target_list[target_index_1_b]['shows'][0]['stepBegin']
                )
                assert verify_target_implausible_hide_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[0],
                    target_list[0]
                )
                assert verify_target_implausible_show_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[0],
                    target_list[target_index_1_b],
                    hypercube._target_list[0]['shows'][0]
                )

            # Verify object one transforms into untrained shape variation.
            if i in ['i', 'j', 'k', 'l']:
                implausible = True
                assert verify_same_object(
                    target_list[target_index_1_b],
                    hypercube._variations_list[0].get(
                        'untrained_different_shape'
                    )
                )
                assert (
                    target_list[0]['hides'][0]['stepBegin'] ==
                    target_list[target_index_1_b]['shows'][0]['stepBegin']
                )
                assert verify_target_implausible_hide_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[0],
                    target_list[0]
                )
                assert verify_target_implausible_show_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[0],
                    target_list[target_index_1_b],
                    hypercube._target_list[0]['shows'][0]
                )

            # Verify object two transforms into different shape variation.
            if j.endswith('3'):
                implausible = True
                assert verify_same_object(
                    target_list[target_index_2_b],
                    hypercube._variations_list[1].get('different_shape')
                )
                print(f'ALPHA={target_list[1]}')
                print(f'BETA={target_list[target_index_2_b]}')
                assert (
                    target_list[1]['hides'][0]['stepBegin'] ==
                    target_list[target_index_2_b]['shows'][0]['stepBegin']
                )
                assert verify_target_implausible_hide_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[1],
                    target_list[1]
                )
                assert verify_target_implausible_show_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[1],
                    target_list[target_index_2_b],
                    hypercube._target_list[1]['shows'][0]
                )

            # Verify object two transforms into untrained shape variation.
            if j.endswith('4'):
                implausible = True
                assert verify_same_object(
                    target_list[target_index_2_b],
                    hypercube._variations_list[1].get(
                        'untrained_different_shape'
                    )
                )
                assert (
                    target_list[1]['hides'][0]['stepBegin'] ==
                    target_list[target_index_2_b]['shows'][0]['stepBegin']
                )
                assert verify_target_implausible_hide_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[1],
                    target_list[1]
                )
                assert verify_target_implausible_show_step(
                    hypercube.is_move_across(),
                    hypercube._occluder_list[1],
                    target_list[target_index_2_b],
                    hypercube._target_list[1]['shows'][0]
                )

            # Verify no change in object one.
            if i in ['a', 'b', 'c', 'd']:
                assert 'hides' not in target_list[0]

            # Verify no change in object two.
            if j.endswith('2'):
                assert 'hides' not in target_list[1]

            verify_scene(
                scene_dict[j],
                hypercube.is_move_across(),
                implausible,
                eval_only
            )

            verify_hypercube_ShapeConstancy(hypercube.is_move_across(), {
                'target': (
                    target_list[:1] if j.endswith('1') else target_list[:2]
                ),
                'non target': hypercube._distractor_list,
                'intuitive physics occluder': hypercube._occluder_list,
                'context': hypercube._background_list
            }, hypercube._last_step, scene_dict[j]['wallMaterial'])

            verify_object_tags(scene_dict[j], target_list, 'target', 'target')


def test_SpatioTemporalContinuityHypercube_scenes_move_across():
    hypercube = intuitive_physics_hypercubes.SpatioTemporalContinuityHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_move_across=True
    )
    assert hypercube.is_move_across()

    scene_list = hypercube.get_scenes()
    scene_dict = {}
    target_dict = {}
    non_target_dict = {}
    occluder_dict = {}
    assert len(scene_list) == 42

    print(f'TARGET={hypercube._target_list[0]}')
    print(f'NON_TARGET={hypercube._distractor_list[0]}')

    for scene in scene_list:
        scene_id = scene['goal']['sceneInfo']['id'][0].lower()
        scene_dict[scene_id] = scene
        target_dict[scene_id] = get_object_list(scene, 'target')
        non_target_dict[scene_id] = get_object_list(scene, 'non target')
        occluder_dict[scene_id] = get_object_list(
            scene,
            'intuitive physics occluder'
        )
        scene_name = scene['goal']['sceneInfo']['name']
        assert scene_name.startswith('STC_')

    for i in [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
        'o', 'p', 'q', 'r'
    ]:
        for j in [i + '1', i + '2', i + '3', i + '4']:
            if j not in scene_dict:
                continue

            print(f'SCENE_ID={j}')
            target_list = target_dict[j]
            non_target_list = non_target_dict[j]
            occluder_list = occluder_dict[j]

            implausible = False
            eval_only = False

            # Verify target is or is not in scene.
            if i in ['a', 'd', 'g', 'j', 'm', 'p']:
                assert len(target_list) == 0

                if j.endswith('2') or j.endswith('4'):
                    eval_only = True
            else:
                assert len(target_list) == 1

                # Verify target not switched.
                if j.endswith('1') or j.endswith('3'):
                    assert verify_same_object(
                        target_list[0],
                        hypercube._variations_list[0].get('trained')
                    )

                # Verify target switched with untrained variation.
                if j.endswith('2') or j.endswith('4'):
                    eval_only = True
                    assert verify_same_object(
                        target_list[0],
                        hypercube._variations_list[0].get('untrained_shape')
                    )

                # Verify target object shrouded.
                if i in ['d', 'e', 'f', 'j', 'k', 'l', 'p', 'q', 'r']:
                    implausible = True
                    assert verify_target_implausible_shroud_step(
                        hypercube.is_move_across(),
                        hypercube._occluder_list[0],
                        hypercube._occluder_list[2],
                        target_list[0]
                    )

                # Verify no change in target object.
                if i in ['a', 'b', 'c', 'g', 'h', 'i', 'm', 'n', 'o']:
                    assert 'shrouds' not in target_list[0]

            # Verify non-target is or is not in scene.
            if i in ['c', 'f', 'i', 'l', 'o', 'r']:
                assert len(non_target_list) == 1

                # Verify non-target not switched.
                if j.endswith('1') or j.endswith('2'):
                    assert verify_same_object(
                        non_target_list[0],
                        hypercube._variations_list[1].get('trained')
                    )

                # Verify non-target switched with untrained shape variation.
                if j.endswith('3') or j.endswith('4'):
                    eval_only = True
                    assert verify_same_object(
                        non_target_list[0],
                        hypercube._variations_list[1].get('untrained_shape')
                    )
            else:
                assert len(non_target_list) == 0

                if j.endswith('3') or j.endswith('4'):
                    eval_only = True

            # Verify occluders are or are not in scene.
            if i in ['a', 'b', 'c', 'd', 'e', 'f']:
                assert len(occluder_list) == 6
            elif i in ['g', 'h', 'i', 'j', 'k', 'l']:
                assert len(occluder_list) == 4
            else:
                assert len(occluder_list) == 0

            if i in ['d', 'j', 'p']:
                eval_only = True

            verify_scene(
                scene_dict[j],
                hypercube.is_move_across(),
                implausible,
                eval_only
            )

            verify_hypercube_SpatioTemporalContinuity(
                hypercube.is_move_across(),
                {
                    'target': target_list,
                    'non target': non_target_list,
                    'intuitive physics occluder': hypercube._occluder_list,
                    'context': hypercube._background_list
                },
                hypercube._last_step,
                scene_dict[j]['wallMaterial'],
                hypercube._target_list[0]
            )

            verify_object_tags(scene_dict[j], target_list, 'target', 'target')
            verify_object_tags(scene_dict[j], non_target_list, 'non target',
                               'non_target')


def test_GravitySupportHypercube_scenes_fall_down():
    hypercube = intuitive_physics_hypercubes.GravitySupportHypercube(
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_fall_down=True
    )
    assert hypercube.is_fall_down()

    scene_list = hypercube.get_scenes()
    scene_dict = {}
    assert len(scene_list) == 16

    print(f'SYMMETRIC={hypercube._target.get("symmetric")}')
    print(f'ASYMMETRIC_LEFT={hypercube._target.get("asymmetric_left")}')
    print(f'ASYMMETRIC_RIGHT={hypercube._target.get("asymmetric_right")}')
    print(f'POLE_SYMMETRIC={hypercube._pole.get("symmetric")}')
    print(f'POLE_ASYMMETRIC_LEFT={hypercube._pole.get("asymmetric_left")}')
    print(f'POLE_ASYMMETRIC_RIGHT={hypercube._pole.get("asymmetric_right")}')
    print(f'VISIBLE_SUPPORT={hypercube._visible_support}')

    show_step = hypercube._target.get('symmetric')['moves'][0]['stepBegin']
    z_position = hypercube._target.get(
        'symmetric'
    )['shows'][0]['position']['z']

    for scene in scene_list:
        scene_id = scene['goal']['sceneInfo']['id'][0].lower()
        scene_dict[scene_id] = scene
        scene_name = scene['goal']['sceneInfo']['name']
        assert scene_name.startswith('GRAV_')

    for i in [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
        'o', 'p'
    ]:
        for j in [i + '1']:
            scene = scene_dict[j]
            is_positive = (
                scene['goal']['sceneInfo']['direction'] == 'right'
            )
            print(f'SCENE_ID={j} IS_POSITIVE_DIRECTION={is_positive}')

            target = scene['objects'][0]
            pole = scene['objects'][1]
            visible_support = scene['objects'][2]
            invisible_support = (
                scene['objects'][3] if len(scene['objects']) > 3 else None
            )

            # How much time the target will need to move with the pole.
            y_difference = target['shows'][0]['position']['y'] - (
                target['dimensions']['y'] / 2.0
            ) - visible_support['dimensions']['y']
            if i in ['o', 'p']:
                assert invisible_support
                y_difference -= invisible_support['dimensions']['y']
            move_step_count = int(y_difference / 0.25) - 1

            # Verify scene-agnostic target properties.
            assert verify_object_fall_down_position(target, 'TARGET', True)
            assert target['kinematic']
            assert 'moves' in target
            assert len(target['moves']) == 1
            assert target['moves'][0]['stepBegin'] == show_step
            assert target['moves'][0]['stepEnd'] == show_step + move_step_count
            assert 'togglePhysics' in target
            assert len(target['togglePhysics']) == 1
            assert target['togglePhysics'][0]['stepBegin'] == (
                show_step + move_step_count + 6
            )
            assert 'changeMaterials' not in target
            assert 'shrouds' not in target

            # Verify scene-agnostic pole properties.
            assert pole['kinematic']
            assert pole['structure']
            assert 'moves' in pole
            assert len(pole['moves']) == 2
            assert pole['moves'][0]['stepBegin'] == show_step
            assert pole['moves'][0]['stepEnd'] == show_step + move_step_count
            assert pole['moves'][1]['stepBegin'] == (
                show_step + move_step_count + 11
            )
            assert pole['moves'][1]['stepEnd'] == (
                pole['moves'][1]['stepBegin'] + move_step_count
            )
            assert 'changeMaterials' in pole
            assert len(pole['changeMaterials']) == 1
            assert pole['changeMaterials'][0]['stepBegin'] == (
                show_step + move_step_count + 6
            )
            assert 'shrouds' not in pole
            assert 'togglePhysics' not in pole

            # Verify scene-agnostic visible support properties.
            assert verify_same_object(
                visible_support,
                hypercube._visible_support
            )
            assert visible_support['kinematic']
            assert visible_support['structure']
            assert 'changeMaterials' not in visible_support
            assert 'moves' not in visible_support
            assert 'moves' not in visible_support
            assert 'shrouds' not in visible_support
            assert 'togglePhysics' not in visible_support

            # Verify target and pole are symmetric.
            if i in ['a', 'c', 'e', 'g', 'i', 'k', 'm', 'o']:
                assert verify_same_object(
                    target,
                    hypercube._target.get('symmetric')
                )
                assert verify_same_object(
                    pole,
                    hypercube._pole.get('symmetric')
                )

            # Verify target and pole are asymmetric.
            if i in ['b', 'd', 'f', 'h', 'j', 'l', 'n', 'p']:
                assert verify_same_object(
                    target,
                    hypercube._target.get('asymmetric_left')
                )
                assert verify_same_object(
                    pole,
                    hypercube._pole.get('asymmetric_left')
                )
                definition = hypercube._target._definitions['asymmetric_left']
                # Verify heavy side unsupported.
                if i in ['b', 'd', 'f', 'h', 'j', 'l', 'n', 'p']:
                    assert target['shows'][0]['rotation']['y'] == (
                        definition.get('rotation', {'y': 0})['y'] +
                        (180 if is_positive else 0)
                    )

            target_position = target['shows'][0]['position']['x']

            # Verify no-support position.
            if i in ['a', 'b', 'c', 'd']:
                modifier = (1 if is_positive else -1) * (
                    (visible_support['dimensions']['x'] / 2.0) +
                    (0.55 * target['dimensions']['x'])
                )
                min_position = (
                    visible_support['shows'][0]['position']['x'] + modifier
                )
                if is_positive:
                    assert target_position >= min_position
                else:
                    assert target_position <= min_position

            # Verify minimal-support position.
            if i in ['e', 'f', 'g', 'h']:
                modifier = (1 if is_positive else -1) * (
                    (visible_support['dimensions']['x'] / 2.0) +
                    (0.45 * target['dimensions']['x'])
                )
                expected_position = (
                    visible_support['shows'][0]['position']['x'] + modifier
                )
                assert target_position == pytest.approx(expected_position)

            # Verify 25%-support position.
            if i in ['i', 'j', 'k', 'l']:
                modifier = (1 if is_positive else -1) * (
                    (visible_support['dimensions']['x'] / 2.0) +
                    (0.25 * target['dimensions']['x'])
                )
                expected_position = (
                    visible_support['shows'][0]['position']['x'] + modifier
                )
                # Adjust asymmetric object position to center of mass.
                if i in ['j', 'l']:
                    asymmetric_center = hypercube._find_center_of_mass_x(
                        hypercube._target._definitions['asymmetric_left'],
                        (not is_positive)
                    )
                    expected_position += asymmetric_center
                assert target_position == pytest.approx(expected_position)

            # Verify full-support position.
            if i in ['m', 'n', 'o', 'p']:
                expected_position = (
                    visible_support['shows'][0]['position']['x']
                )
                assert target_position == pytest.approx(expected_position)

            implausible = False

            # Verify implausible scene with invisible support.
            if i in ['c', 'd', 'g', 'h', 'k', 'l', 'o', 'p']:
                implausible = True
                assert len(scene['objects']) == 4
                assert invisible_support
                assert invisible_support['id'] != visible_support['id']
                assert invisible_support['kinematic']
                assert invisible_support['structure']
                assert 'shrouds' in invisible_support
                assert len(invisible_support['shrouds']) == 1
                assert invisible_support['shrouds'][0]['stepBegin'] == 0
                assert invisible_support['shrouds'][0]['stepEnd'] == 61
                assert 'moves' not in invisible_support
                assert 'togglePhysics' not in invisible_support
                # Invisible support on the floor next to the visible support.
                if i in ['c', 'd', 'g', 'h', 'k', 'l']:
                    if is_positive:
                        assert (
                            invisible_support['shows'][0]['position']['x'] >
                            visible_support['shows'][0]['position']['x'] +
                            (visible_support['dimensions']['x'] / 2.0)
                        )
                    else:
                        assert (
                            invisible_support['shows'][0]['position']['x'] <
                            visible_support['shows'][0]['position']['x'] -
                            (visible_support['dimensions']['x'] / 2.0)
                        )
                    assert (
                        invisible_support['shows'][0]['position']['y'] ==
                        pytest.approx(
                            invisible_support['dimensions']['y'] / 2.0
                        )
                    )
                # Invisible support on top of the visible support.
                if i in ['o', 'p']:
                    assert invisible_support['shows'][0]['position']['x'] == (
                        visible_support['shows'][0]['position']['x']
                    )
                    assert invisible_support['shows'][0]['position']['y'] == (
                        visible_support['dimensions']['y'] +
                        (invisible_support['dimensions']['y'] / 2.0)
                    )
            else:
                assert len(scene['objects']) == 3

            # Verify implausible scene with invisible wind.
            if i in []:
                implausible = True
                assert 'forces' in target
                assert len(target['forces']) == 1
                assert target['forces'][0]['stepBegin'] == (
                    target['togglePhysics'][0]['stepBegin'] + 11
                )
                assert target['forces'][0]['vector']['x'] == (
                    (1 if is_positive else -1) * target['mass'] * 250
                )
                assert target['forces'][0]['vector']['y'] == 0
                assert target['forces'][0]['vector']['z'] == 0
            else:
                assert 'forces' not in target

            verify_scene(
                scene_dict[j],
                hypercube.is_move_across(),
                implausible,
                last_step=60
            )

            for instance in scene['objects']:
                # Verify each object will only appear once, and only move with
                # the "moves" property.
                assert len(instance['shows']) == 1
                # Verify each object has the same Z position.
                assert instance['shows'][0]['position']['z'] == z_position

            verify_object_tags(scene_dict[j], [target], 'target', 'target')


def test_ObjectPermanenceHypercubeEval4_default_objects_move_across():
    hypercube = intuitive_physics_hypercubes.ObjectPermanenceHypercubeEval4(  # noqa: E501
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_move_across=True
    )
    assert hypercube.is_move_across()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    object_dict = hypercube._create_default_objects(
        wall_material_tuple[0],
        wall_material_tuple[1]
    )
    assert verify_hypercube_variations(
        hypercube._variations_list,
        hypercube._target_list,
        hypercube._distractor_list,
        object_dict['target'],
        object_dict['non target'],
        1,
        0
    )
    assert verify_hypercube_ObjectPermanence(
        hypercube.is_move_across(),
        object_dict,
        hypercube._last_step,
        wall_material_tuple[0],
        eval_4=True
    )


def test_ObjectPermanenceHypercubeEval4_default_scene_move_across():
    hypercube = intuitive_physics_hypercubes.ObjectPermanenceHypercubeEval4(  # noqa: E501
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_move_across=True
    )
    assert hypercube.is_move_across()
    goal_template = hypercubes.initialize_goal(
        intuitive_physics_hypercubes.ObjectPermanenceHypercube.GOAL_TEMPLATE
    )
    scene = hypercube._create_default_scene(BODY_TEMPLATE, goal_template)
    verify_scene(scene, hypercube.is_move_across(), last_step=240)
    assert 'object permanence' == scene['goal']['sceneInfo']['tertiaryType']


def test_ObjectPermanenceHypercubeEval4_scenes_move_across():
    hypercube = intuitive_physics_hypercubes.ObjectPermanenceHypercubeEval4(  # noqa: E501
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_move_across=True
    )
    assert hypercube.is_move_across()

    scene_list = hypercube.get_scenes()
    scene_dict = {}
    target_dict = {}
    assert len(scene_list) == 2

    print(f'TARGET={hypercube._target_list[0]}')

    for scene in scene_list:
        scene_id = scene['goal']['sceneInfo']['id'][0].lower()
        scene_dict[scene_id] = scene
        target_dict[scene_id] = get_object_list(scene, 'target')
        scene_name = scene['goal']['sceneInfo']['name']
        assert scene_name.startswith('OBJP_')

    for i in ['j']:
        for j in [i + '1', i + '2']:
            print(f'SCENE_ID={j}')
            target_list = target_dict[j]
            assert len(target_list) == 1

            implausible = False
            eval_only = False

            # Verify target not switched.
            assert verify_same_object(
                target_list[0],
                hypercube._variations_list[0].get('trained')
            )

            # Verify no change in target.
            assert 'hides' not in target_list[0]
            assert (
                target_list[0]['shows'][0]['stepBegin'] ==
                hypercube._target_list[0]['shows'][0]['stepBegin']
            )

            is_left = target_list[0]['shows'][0]['position']['x'] < 0

            # Verify normal exit/stop movement.
            target_movement = target_list[0]['movement']
            move_property = 'moveStop' if j.endswith('1') else 'moveExit'
            assert target_movement['active'] == move_property
            assert target_list[0]['forces'][0]['vector']['x'] == (
                target_movement[move_property]['forceX'] *
                target_list[0]['mass'] * (1 if is_left else -1)
            )

            verify_scene(
                scene_dict[j],
                hypercube.is_move_across(),
                implausible,
                eval_only,
                last_step=240
            )

            verify_hypercube_ObjectPermanence(
                hypercube.is_move_across(),
                {
                    'target': target_list,
                    'non target': hypercube._distractor_list,
                    'intuitive physics occluder': hypercube._occluder_list,
                    'context': hypercube._background_list
                },
                hypercube._last_step,
                scene_dict[j]['wallMaterial'],
                eval_4=True
            )

            verify_object_tags(scene_dict[j], target_list, 'target', 'target')


def test_SpatioTemporalContinuityHypercubeEval4_default_objects_move_across():
    hypercube = intuitive_physics_hypercubes.SpatioTemporalContinuityHypercubeEval4(  # noqa: E501
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_move_across=True
    )
    assert hypercube.is_move_across()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    object_dict = hypercube._create_default_objects(
        wall_material_tuple[0],
        wall_material_tuple[1]
    )
    assert verify_hypercube_variations(
        hypercube._variations_list,
        hypercube._target_list,
        hypercube._distractor_list,
        object_dict['target'],
        object_dict['non target'],
        1,
        0
    )
    assert verify_hypercube_SpatioTemporalContinuity(
        hypercube.is_move_across(),
        object_dict,
        hypercube._last_step,
        wall_material_tuple[0],
        hypercube._target_list[0],
        eval_4=True
    )


def test_SpatioTemporalContinuityHypercubeEval4_default_scene_move_across():
    hypercube = intuitive_physics_hypercubes.SpatioTemporalContinuityHypercubeEval4(  # noqa: E501
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_move_across=True
    )
    assert hypercube.is_move_across()
    goal_template = hypercubes.initialize_goal(
        intuitive_physics_hypercubes.SpatioTemporalContinuityHypercube.GOAL_TEMPLATE  # noqa: E501
    )
    scene = hypercube._create_default_scene(BODY_TEMPLATE, goal_template)
    verify_scene(scene, hypercube.is_move_across())
    assert (
        'spatio temporal continuity' ==
        scene['goal']['sceneInfo']['tertiaryType']
    )


def test_SpatioTemporalContinuityHypercubeEval4_scenes_move_across():
    hypercube = intuitive_physics_hypercubes.SpatioTemporalContinuityHypercubeEval4(  # noqa: E501
        BODY_TEMPLATE,
        {'target': None, 'non target': None},
        is_move_across=True
    )
    assert hypercube.is_move_across()

    scene_list = hypercube.get_scenes()
    scene_dict = {}
    target_dict = {}
    non_target_dict = {}
    occluder_dict = {}
    assert len(scene_list) == 2

    print(f'TARGET={hypercube._target_list[0]}')

    for scene in scene_list:
        scene_id = scene['goal']['sceneInfo']['id'][0].lower()
        scene_dict[scene_id] = scene
        target_dict[scene_id] = get_object_list(scene, 'target')
        non_target_dict[scene_id] = get_object_list(scene, 'non target')
        occluder_dict[scene_id] = get_object_list(
            scene,
            'intuitive physics occluder'
        )
        scene_name = scene['goal']['sceneInfo']['name']
        assert scene_name.startswith('STC_')

    for i in ['a', 'e']:
        for j in [i + '1']:
            print(f'SCENE_ID={j}')
            target_list = target_dict[j]
            non_target_list = non_target_dict[j]
            occluder_list = occluder_dict[j]

            implausible = False
            eval_only = False

            assert len(target_list) == 1
            assert len(non_target_list) == 0

            # Verify target not switched.
            assert verify_same_object(
                target_list[0],
                hypercube._variations_list[0].get('trained')
            )

            # Verify no change in target object.
            if i in ['a']:
                assert 'shrouds' not in target_list[0]

            # Verify occluders are or are not in scene.
            if i in ['a']:
                assert len(occluder_list) == 4
            else:
                assert len(occluder_list) == 0

            verify_scene(
                scene_dict[j],
                hypercube.is_move_across(),
                implausible,
                eval_only
            )

            verify_hypercube_SpatioTemporalContinuity(
                hypercube.is_move_across(),
                {
                    'target': target_list,
                    'non target': non_target_list,
                    'intuitive physics occluder': hypercube._occluder_list,
                    'context': hypercube._background_list
                },
                hypercube._last_step,
                scene_dict[j]['wallMaterial'],
                hypercube._target_list[0],
                eval_4=True
            )

            verify_object_tags(scene_dict[j], target_list, 'target', 'target')
            verify_object_tags(scene_dict[j], non_target_list, 'non target',
                               'non_target')
