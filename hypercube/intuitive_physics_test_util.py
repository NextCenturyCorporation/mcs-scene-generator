import math

import pytest

from generator import definitions, materials, occluders

from . import intuitive_physics_hypercubes

BODY_TEMPLATE = {
    'name': '',
    'ceilingMaterial': 'AI2-THOR/Materials/Walls/Drywall',
    'floorMaterial': 'AI2-THOR/Materials/Fabrics/CarpetWhite 3',
    'wallMaterial': 'AI2-THOR/Materials/Walls/DrywallBeige',
    'performerStart': {
        'position': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0
        }
    },
    'objects': [],
    'goal': {},
    'debug': {
        'floorColors': ['white'],
        'wallColors': ['white']
    }
}


OPPOSITE_MATERIAL_STRING_LIST = [
    item[0] for item in materials.OPPOSITE_MATERIALS
]


CYLINDRICAL_SHAPES = [
    'cylinder', 'double_cone', 'dumbbell_1', 'dumbbell_2', 'tie_fighter',
    'tube_narrow', 'tube_wide'
]


def verify_scene(
    scene,
    is_move_across,
    implausible=False,
    eval_only=False,
    last_step=None
):
    assert scene['intuitivePhysics']
    assert scene['debug']['evaluationOnly'] == (eval_only or implausible)
    assert scene['goal']['answer']['choice'] == (
        'implausible' if implausible else 'plausible'
    )

    if is_move_across:
        assert scene['goal']['last_step'] == (last_step if last_step else 200)
    else:
        assert scene['goal']['last_step'] == (last_step if last_step else 160)
    assert scene['goal']['action_list'] == (
        [['Pass']] * scene['goal']['last_step']
    )
    assert scene['goal']['category'] == 'intuitive physics'
    assert scene['goal']['sceneInfo']['primaryType'] == 'passive'
    assert scene['goal']['sceneInfo']['secondaryType'] == 'intuitive physics'
    assert scene['goal']['sceneInfo']['quaternaryType'] == 'action none'

    if is_move_across:
        assert scene['goal']['sceneInfo']['moveAcross']
        assert 'move across' == scene['goal']['sceneInfo']['sceneSetup']
    else:
        assert scene['goal']['sceneInfo']['fallDown']
        assert 'fall down' == scene['goal']['sceneInfo']['sceneSetup']


def verify_hypercube(object_dict, room_wall_material):
    if len(object_dict.get('context', [])) > 5:
        print(f'[ERROR] TOO MANY BACKGROUND OBJECTS\n'
              f'{len(object_dict["background_object"])}')
        return False

    # Verify background object position.
    max_x = intuitive_physics_hypercubes.BACKGROUND_MAX_X
    min_z = intuitive_physics_hypercubes.BACKGROUND_MIN_Z
    max_z = intuitive_physics_hypercubes.BACKGROUND_MAX_Z
    for background_object in object_dict.get('context', []):
        for corner in background_object['shows'][0]['boundingBox']:
            if -max_x > corner['x'] > max_x:
                print(f'[ERROR] BACKGROUND OBJECT X BOUNDS SHOULD BE BETWEEN '
                      f'{-max_x} AND {max_x} BUT WAS {corner["x"]}\n'
                      f'OBJECT={background_object}')
            if min_z > corner['z'] > max_z:
                print(f'[ERROR] BACKGROUND OBJECT Z BOUNDS SHOULD BE BETWEEN '
                      f'{min_z} AND {max_z} BUT WAS {corner["z"]}\n'
                      f'OBJECT={background_object}')

    for occluder in object_dict.get('intuitive physics occluder', []):
        if 'wall' in occluder['debug']['shape']:
            if room_wall_material in occluder['materials']:
                print(f'[ERROR] OCCLUDER MATERIAL SAME AS ROOM WALL '
                      f'ROOM_WALL_MATERIAL={room_wall_material} '
                      f'OCCLUDER={occluder}')
                return False

    return True


def verify_object_tags(scene, object_list, role_info, role_prop):
    for instance in object_list:
        for info in instance['debug']['info']:
            assert info in scene['goal']['objectsInfo']['all']
            if info != role_info:
                assert info in scene['goal']['objectsInfo'][role_prop]
    return True


def verify_hypercube_variations(
    hypercube_variations_list,
    hypercube_target_list,
    hypercube_non_target_list,
    scene_target_list,
    scene_non_target_list,
    expected_target_length,
    expected_non_target_length
):
    assert len(scene_target_list) == expected_target_length
    assert len(hypercube_target_list) == expected_target_length
    assert len(hypercube_variations_list) == (
        expected_target_length + expected_non_target_length
    )

    for i in range(expected_target_length):
        assert scene_target_list[i] == hypercube_target_list[i]
        assert (
            scene_target_list[i] == hypercube_variations_list[i].get('trained')
        )

    for i in range(expected_non_target_length):
        assert scene_non_target_list[i] == hypercube_non_target_list[i]
        assert (
            scene_non_target_list[i] == hypercube_variations_list[
                i + expected_target_length
            ].get('trained')
        )

    for variations in hypercube_variations_list:
        trained_default = variations.get('trained')
        different_color = variations.get('different_color')
        different_shape = variations.get('different_shape')
        different_size = variations.get('different_size')
        untrained_shape = variations.get('untrained_shape')
        untrained_different_shape = (
            variations.get('untrained_different_shape')
        )
        untrained_size = variations.get('untrained_size')

        assert not trained_default['debug'].get('untrainedShape', False)
        assert not trained_default['debug'].get('untrainedSize', False)

        if different_color:
            assert not different_color['debug'].get('untrainedShape', False)
            assert not different_color['debug'].get('untrainedSize', False)
            assert definitions.is_similar_except_in_color(
                trained_default,
                different_color,
                only_diagonal_size=True
            )
            assert not definitions.do_materials_match(
                trained_default['materials'],
                different_color['materials'],
                trained_default['debug']['color'],
                different_color['debug']['color']
            )

        if different_shape:
            assert not different_shape['debug'].get('untrainedShape', False)
            assert not different_shape['debug'].get('untrainedSize', False)
            assert definitions.is_similar_except_in_shape(
                trained_default,
                different_shape,
                only_diagonal_size=True
            )
            assert definitions.do_materials_match(
                trained_default['materials'],
                different_shape['materials'],
                trained_default['debug']['color'],
                different_shape['debug']['color']
            )

        if different_size:
            assert not different_size['debug'].get('untrainedShape', False)
            assert not different_size['debug'].get('untrainedSize', False)
            assert definitions.is_similar_except_in_size(
                trained_default,
                different_size,
                only_diagonal_size=True
            )
            assert definitions.do_materials_match(
                trained_default['materials'],
                different_size['materials'],
                trained_default['debug']['color'],
                different_size['debug']['color']
            )

        if untrained_shape:
            assert not untrained_shape['debug'].get('untrainedSize', False)
            assert untrained_shape['debug'].get('untrainedShape', False)
            assert definitions.is_similar_except_in_shape(
                trained_default,
                untrained_shape,
                only_diagonal_size=True
            )
            assert definitions.do_materials_match(
                trained_default['materials'],
                untrained_shape['materials'],
                trained_default['debug']['color'],
                untrained_shape['debug']['color']
            )

        if untrained_different_shape:
            assert not (
                untrained_different_shape['debug'].get('untrainedSize', False)
            )
            assert (
                untrained_different_shape['debug'].get('untrainedShape', False)
            )
            assert definitions.is_similar_except_in_shape(
                untrained_shape,
                untrained_different_shape,
                only_diagonal_size=True
            )
            assert definitions.do_materials_match(
                trained_default['materials'],
                untrained_different_shape['materials'],
                trained_default['debug']['color'],
                untrained_different_shape['debug']['color']
            )

        if untrained_size:
            assert not untrained_size['debug'].get('untrainedShape', False)
            assert untrained_size['debug'].get('untrainedSize', False)
            assert definitions.is_similar_except_in_size(
                trained_default,
                untrained_size,
                only_diagonal_size=True
            )
            assert definitions.do_materials_match(
                trained_default['materials'],
                untrained_size['materials'],
                trained_default['debug']['color'],
                untrained_size['debug']['color']
            )

    return True


def verify_hypercube_Collisions(
    is_move_across,
    object_dict,
    last_step,
    room_wall_material_name
):
    assert is_move_across
    assert last_step == 200

    assert verify_hypercube(object_dict, room_wall_material_name)
    assert verify_object_list_move_across(object_dict['target'], [])
    assert verify_occluder_list_move_across(
        object_dict['intuitive physics occluder'],
        object_dict['target'],
        ignore_x_position=True
    )

    assert len(object_dict['intuitive physics occluder']) == 2

    assert len(object_dict['target'][0]['materials'])
    for material in object_dict['target'][0]['materials']:
        assert material in OPPOSITE_MATERIAL_STRING_LIST

    # The non target is not in every scene in the collisions hypercube.
    if len(object_dict['non target']):
        target_material = object_dict['target'][0]['materials'][0]
        assert len(object_dict['non target'][0]['materials'])
        for material in object_dict['non target'][0]['materials']:
            assert material in OPPOSITE_MATERIAL_STRING_LIST
            assert material == materials.OPPOSITE_SETS[target_material][0]

    return True


def verify_hypercube_ObjectPermanence(
    is_move_across,
    object_dict,
    last_step,
    room_wall_material_name,
    eval_4=False
):
    assert verify_hypercube(object_dict, room_wall_material_name)

    assert len(object_dict['non target']) == 0

    if is_move_across:
        assert verify_object_list_move_across(
            object_dict['target'],
            object_dict['non target']
        )
        assert len(object_dict['intuitive physics occluder']) == (
            2 if eval_4 else 4
        )
        assert verify_occluder_list_move_across(
            object_dict['intuitive physics occluder'],
            object_dict['target'],
            ignore_x_position=eval_4
        )
        assert last_step == (240 if eval_4 else 200)

    else:
        assert verify_object_list_fall_down(
            object_dict['target'],
            object_dict['non target']
        )
        assert len(object_dict['intuitive physics occluder']) == 4
        assert verify_occluder_list_fall_down(
            object_dict['intuitive physics occluder'],
            object_dict['target']
        )
        assert last_step == 160

    return True


def verify_hypercube_ShapeConstancy(
    is_move_across,
    object_dict,
    last_step,
    room_wall_material_name
):
    assert verify_hypercube(object_dict, room_wall_material_name)

    assert len(object_dict['non target']) == 0

    if is_move_across:
        assert verify_object_list_move_across(
            object_dict['target'],
            object_dict['non target']
        )
        assert len(object_dict['intuitive physics occluder']) == 6
        assert verify_occluder_list_move_across(
            object_dict['intuitive physics occluder'],
            object_dict['target']
        )
        assert last_step == 200

    else:
        assert verify_object_list_fall_down(
            object_dict['target'],
            object_dict['non target']
        )
        assert len(object_dict['intuitive physics occluder']) == 4
        assert verify_occluder_list_fall_down(
            object_dict['intuitive physics occluder'],
            object_dict['target']
        )
        assert last_step == 160

    return True


def verify_hypercube_SpatioTemporalContinuity(
    is_move_across,
    object_dict,
    last_step,
    room_wall_material_name,
    hypercube_target,
    eval_4=False
):
    assert verify_hypercube(object_dict, room_wall_material_name)

    if is_move_across:
        assert verify_object_list_move_across(
            object_dict['target'],
            object_dict['non target']
        )
        assert len(object_dict['intuitive physics occluder']) == (
            4 if eval_4 else 6
        )
        # Pass the target here twice to verify both of its paired occluders.
        assert verify_occluder_list_move_across(
            object_dict['intuitive physics occluder'],
            [hypercube_target, hypercube_target],
            ignore_x_position=eval_4
        )
        assert last_step == 200

    else:
        assert verify_object_list_fall_down(
            object_dict['target'],
            object_dict['non target']
        )
        assert len(object_dict['intuitive physics occluder']) == 4
        assert verify_occluder_list_fall_down(
            object_dict['intuitive physics occluder'],
            [hypercube_target]
        )
        assert last_step == 160

    return True


def verify_object_fall_down(instance, name):
    verify_object_fall_down_position(instance, name)

    # Verify object X and Z rotation.
    expected_rotation_x = 90 if instance['type'] in CYLINDRICAL_SHAPES else 0
    rotation = instance['shows'][0]['rotation']
    if rotation['x'] != expected_rotation_x:
        print(f'[ERROR] {name} X ROTATION SHOULD BE {expected_rotation_x} BUT '
              f'WAS {rotation["x"]}\n{name}={instance}')
        return False
    if rotation['z'] != 0:
        print(f'[ERROR] {name} Z ROTATION SHOULD BE ZERO BUT WAS '
              f'{rotation["z"]}\n{name}={instance}')
        return False

    if not (name == 'TARGET' and instance.get('ignoreShowStep', False)):
        # Verify object show step.
        min_begin = intuitive_physics_hypercubes.EARLIEST_ACTION_STEP
        max_begin = (
            intuitive_physics_hypercubes.LAST_STEP_FALL_DOWN -
            occluders.OCCLUDER_MOVEMENT_TIME -
            intuitive_physics_hypercubes.OBJECT_FALL_TIME
        )
        if min_begin > instance['shows'][0]['stepBegin'] > max_begin:
            print(f'[ERROR] {name} SHOW STEP BEGIN SHOULD BE BETWEEN '
                  f'{min_begin} AND {max_begin}\n{name}={instance}')
            return False

    # Verify object force properties.
    if 'forces' in instance:
        print(f'[ERROR] {name} SHOULD NOT HAVE FORCES LIST (GRAVITY IS '
              f'APPLIED AUTOMATICALLY)\n{name}={instance}')
        return False

    return True


def verify_object_fall_down_position(instance, name, bigger=False):
    # Verify object X and Y and Z position.
    max_x = occluders.OCCLUDER_MAX_X - (occluders.OCCLUDER_BUFFER / 2.0) + (
        0.5 if bigger else 0
    )
    x_position = instance['shows'][0]['position']['x']
    if -max_x > x_position or x_position > max_x:
        print(f'[ERROR] {name} X POSITION SHOULD BE BETWEEN {-max_x} AND '
              f'{max_x}\n{name}={instance}')
        return False

    min_z = intuitive_physics_hypercubes.MIN_TARGET_Z
    max_z = intuitive_physics_hypercubes.MAX_TARGET_Z
    z_position = instance['shows'][0]['position']['z']
    if z_position < min_z or z_position > max_z:
        print(f'[ERROR] {name} Z POSITION SHOULD BE WITHIN [{min_z}, '
              f'{max_z}]\n{name}={instance}')
        return False

    if not (name == 'TARGET' and instance.get('ignorePosition', False)):
        y_position = instance['shows'][0]['position']['y']
        y_expected = (
            intuitive_physics_hypercubes.retrieve_off_screen_position_y(
                z_position
            )
        )
        if y_position < y_expected:
            print(f'[ERROR] {name} Y POSITION SHOULD BE GREATER THAN '
                  f'{y_expected} BUT WAS {y_position}\n{name}={instance}')
            return False

    return True


def verify_object_list_fall_down(target_list, distractor_list):
    for target in target_list:
        assert verify_object_fall_down(target, 'TARGET')
    for distractor in distractor_list:
        assert verify_object_fall_down(distractor, 'NON-TARGET')

    # Verify each object position relative to one another.
    separation = (occluders.OCCLUDER_MIN_SCALE_X * 2) + \
        occluders.OCCLUDER_SEPARATION_X
    object_list = target_list + distractor_list
    for i in range(len(object_list)):
        for j in range(len(object_list)):
            if i != j:
                x_1 = object_list[i]['shows'][0]['position']['x']
                x_2 = object_list[j]['shows'][0]['position']['x']
                if abs(x_1 - x_2) < separation:
                    print(f'[ERROR] X POSITIONS USED BY TWO FALL DOWN OBJECTS '
                          f'ARE TOO CLOSE BECAUSE SEPARATION MUST BE AT LEAST '
                          f'{separation} BUT WAS {abs(x_1 - x_2)} '
                          f'X_1={x_1} X_2={x_2}\nOBJECT_LISTt={object_list}')
                    return False

    return True


def verify_object_move_across(instance, name):
    left_to_right = (instance['shows'][0]['position']['x'] < 0)
    last_action_step = intuitive_physics_hypercubes.LAST_STEP_MOVE_ACROSS - \
        occluders.OCCLUDER_MOVEMENT_TIME

    # Verify object X and Z rotation.
    expected_rotation_x = 90 if instance['type'] in CYLINDRICAL_SHAPES else 0
    rotation = instance['shows'][0]['rotation']
    if rotation['x'] != expected_rotation_x:
        print(f'[ERROR] {name} X ROTATION SHOULD BE {expected_rotation_x} BUT '
              f'WAS {rotation["x"]}\n{name}={instance}')
        return False
    if rotation['z'] != 0:
        print(f'[ERROR] {name} Z ROTATION SHOULD BE ZERO BUT WAS '
              f'{rotation["z"]}\n{name}={instance}')
        return False

    if not (name == 'TARGET' and instance.get('ignorePosition', False)):
        # Verify object X and Z position.
        x_position = instance['shows'][0]['position']['x']
        z_position = instance['shows'][0]['position']['z']

        min_z = intuitive_physics_hypercubes.MIN_TARGET_Z
        max_z = intuitive_physics_hypercubes.MAX_TARGET_Z
        if z_position < min_z or z_position > max_z:
            print(f'[ERROR] {name} Z POSITION SHOULD BE WITHIN [{min_z}, '
                  f'{max_z}]\n{name}={instance}')
            return False

        x_expected = (
            intuitive_physics_hypercubes.retrieve_off_screen_position_x(
                z_position
            ) * (-1 if x_position < 0 else 1)
        )
        if x_position != pytest.approx(x_expected):
            print(f'[ERROR] {name} X POSITION SHOULD BE {x_expected} BUT WAS '
                  f'{x_position}\n{name}={instance}')
            return False

        # Verify object distance-by-step list.
        distance_by_step = (
            instance['debug']['movement']['moveExit']['xDistanceByStep']
        )
        for i in range(len(distance_by_step) - 1):
            position = distance_by_step[i]
            position_next = distance_by_step[i + 1]
            if left_to_right:
                if position >= position_next:
                    print(f'[ERROR] LEFT-TO-RIGHT {name} DISTANCE BY STEP '
                          f'SHOULD BE INCREASING\n{name}={instance}\n'
                          f'X_POSITION={position}\n'
                          f'X_POSITION_NEXT={position_next}')
                    return False
            else:
                if position <= position_next:
                    print(f'[ERROR] RIGHT-TO-LEFT {name} DISTANCE BY STEP '
                          f'SHOULD BE DECREASING\n{name}={instance}\n'
                          f'X_POSITION={position}\n'
                          f'X_POSITION_NEXT={position_next}')
                    return False

        # Verify object force properties.
        if (
            instance['forces'][0]['stepEnd'] !=
            instance['forces'][0]['stepBegin']
        ):
            print(f'[ERROR] {name} FORCE STEP END SHOULD BE SAME AS FORCE '
                  f'STEP BEGIN\n{name}={instance}')
            return False
        if left_to_right:
            if instance['forces'][0]['vector']['x'] < 0:
                print(f'[ERROR] LEFT-TO-RIGHT {name} FORCE VECTOR X SHOULD BE '
                      f'POSITIVE\n{name}={instance}')
                return False
        else:
            if (
                instance['forces'][0]['vector']['x'] > 0 and
                not instance['forces'][0].get('relative')
            ):
                print(f'[ERROR] RIGHT-TO-LEFT {name} NON-RELATIVE FORCE '
                      f'VECTOR X SHOULD BE NEGATIVE\n{name}={instance}')
                return False

    if (not name == 'TARGET' and not instance.get('ignoreShowStep', False)):
        # Verify object show step.
        min_begin = intuitive_physics_hypercubes.EARLIEST_ACTION_STEP
        max_begin = last_action_step - len(
            instance['debug']['movement']['moveExit']['xDistanceByStep']
        ) - 1
        if min_begin > instance['shows'][0]['stepBegin'] > max_begin:
            print(f'[ERROR] {name} SHOW STEP BEGIN SHOULD BE BETWEEN '
                  f'{min_begin} AND {max_begin}\n{name}={instance}')
            return False
        if (
            instance['forces'][0]['stepBegin'] !=
            instance['shows'][0]['stepBegin']
        ):
            print(f'[ERROR] {name} FORCE STEP BEGIN SHOULD BE SAME AS SHOW '
                  f'STEP BEGIN\n{name}={instance}')
            return False

    return True


def verify_object_list_move_across(target_list, distractor_list):
    for target in target_list:
        assert verify_object_move_across(target, 'TARGET')
    for distractor in distractor_list:
        assert verify_object_move_across(distractor, 'NON-TARGET')

    # Verify each object position relative to one another.
    position_dict = {}
    object_list = target_list + distractor_list
    for instance in object_list:
        x_str = str(instance['shows'][0]['position']['x'])
        z_str = str(instance['shows'][0]['position']['z'])
        if x_str in position_dict and z_str in position_dict[x_str]:
            print(f'[ERROR] SAME LOCATION USED BY TWO MOVE ACROSS OBJECTS '
                  f'X={x_str} Z={z_str}\nOBJECT_LIST={object_list}')
            return False
        position_dict[x_str] = position_dict[x_str] if x_str in position_dict \
            else {}
        position_dict[x_str][z_str] = True

    for object_1 in object_list:
        x_1 = object_1['shows'][0]['position']['x']
        z_1 = object_1['shows'][0]['position']['z']
        for object_2 in object_list:
            if object_1 != object_2:
                begin_1 = object_1['shows'][0]['stepBegin']
                begin_2 = object_2['shows'][0]['stepBegin']
                if begin_1 > (begin_2 - 5) and begin_1 < (begin_2 + 5):
                    print(f'[ERROR] MOVE ACROSS OBJECTS SHOULD NOT HAVE SHOW '
                          f'STEP BEGIN WITHIN FIVE STEPS OF ONE ANOTHER\n'
                          f'OBJECT_1={object_1}\nOBJECT_2={object_2}')
                    return False
                x_2 = object_2['shows'][0]['position']['x']
                z_2 = object_2['shows'][0]['position']['z']
                if z_2 == z_1 and abs(x_2) > abs(x_1):
                    if begin_2 <= begin_1:
                        print(f'[ERROR] MOVE ACROSS OBJECT IN FRONT OF SECOND '
                              f'OBJECT SHOULD HAVE SMALLER SHOW STEP BEGIN\n'
                              f'OBJECT_1={object_1}\nOBJECT_2={object_2}')
                        return False
                    force_1 = (
                        object_1['debug']['movement']['moveExit']['force'] *
                        object_1['mass']
                    )
                    force_2 = (
                        object_2['debug']['movement']['moveExit']['force'] *
                        object_2['mass']
                    )
                    if abs(force_2) > abs(force_1):
                        print(f'[ERROR] MOVE ACROSS OBJECT IN FRONT OF SECOND '
                              f'OBJECT SHOULD HAVE GREATER FORCE\n'
                              f'OBJECT_1={object_1}\nOBJECT_2={object_2}')
                        return False

    return True


def verify_occluder(occluder_wall, occluder_pole, sideways=False):
    # Verify occluder wall scale.
    min_scale = occluders.OCCLUDER_MIN_SCALE_X
    max_scale = occluders.OCCLUDER_MAX_SCALE_X + occluders.OCCLUDER_BUFFER
    if min_scale > occluder_wall['shows'][0]['scale']['x'] > max_scale:
        print(f'[ERROR] OCCLUDER WALL X SCALE SHOULD BE BETWEEN {min_scale} '
              f'AND {max_scale}\nOCCLUDER_WALL={occluder_wall}')
        return False

    # Verify occluder wall position.
    max_x = occluders.OCCLUDER_MAX_X - \
        (occluder_wall['shows'][0]['scale']['x'] / 2.0)
    if -max_x > occluder_wall['shows'][0]['position']['x'] > max_x:
        print(f'[ERROR] OCCLUDER WALL X POSITION SHOULD BE BETWEEN {-max_x} '
              f'AND {max_x}\nOCCLUDER_WALL={occluder_wall}')
        return False
    if (not sideways) and (
        occluder_pole['shows'][0]['position']['x'] !=
        occluder_wall['shows'][0]['position']['x']
    ):
        print(f'[ERROR] OCCLUDER POLE X POSITION SHOULD BE SAME AS '
              f'OCCLUDER WALL\nOCCLUDER_POLE={occluder_pole}\n'
              f'OCCLUDER_WALL={occluder_wall}')
        return False

    return True


def verify_occluder_list(occluder_list, target_list, sideways=False):
    for i in range(int(len(occluder_list) / 2)):
        assert verify_occluder(occluder_list[i * 2],
                               occluder_list[(i * 2) + 1],
                               sideways)

    # Each even index is a wall and each odd is a pole.
    # Only look at the wall indices.
    for i in range(int(len(occluder_list) / 2)):
        for j in range(int(len(occluder_list) / 2)):
            if i != j:
                separation = (
                    occluders.OCCLUDER_SEPARATION_X +
                    (occluder_list[i * 2]['shows'][0]['scale']['x'] / 2.0) +
                    (occluder_list[j * 2]['shows'][0]['scale']['x'] / 2.0)
                )
                x_1 = occluder_list[i * 2]['shows'][0]['position']['x']
                x_2 = occluder_list[j * 2]['shows'][0]['position']['x']
                if abs(x_1 - x_2) < separation:
                    print(f'[ERROR] X POSITIONS USED BY TWO OCCLUDERS ARE TOO '
                          f'CLOSE BECAUSE SEPARATION MUST BE AT LEAST '
                          f'{separation} BUT WAS {abs(x_1 - x_2)} X_1={x_1} '
                          f'X_2={x_2}\nOCCLUDER_LIST={occluder_list}')
                    return False

    for i in range(len(target_list)):
        target = target_list[i]
        occluder_wall = occluder_list[i * 2]
        target_size = math.sqrt(
            target['debug']['dimensions']['x']**2 +
            target['debug']['dimensions']['z']**2
        )
        if occluder_wall['shows'][0]['scale']['x'] < target_size:
            print(f'[ERROR] PAIRED OCCLUDER WALL X SCALE SHOULD BE GREATER '
                  f'THAN TARGET DIAGONAL X\nOCCLUDER_WALL={occluder_wall}\n'
                  f'TARGET={target}')
            return False

    return True


def verify_occluder_list_fall_down(occluder_list, target_list):
    assert verify_occluder_list(occluder_list, target_list, sideways=True)

    for i in range(len(target_list)):
        target = target_list[i]
        occluder_wall = occluder_list[i * 2]
        adjusted_x = intuitive_physics_hypercubes.occluder_x_to_object_x(
            occluder_wall['shows'][0]['position']['x'],
            target['shows'][0]['position']['z']
        )
        if target['shows'][0]['position']['x'] != pytest.approx(adjusted_x):
            print(f'[ERROR] PAIRED FALL DOWN OCCLUDER WALL X POSITION '
                  f'SHOULD BE CALCULATED FROM TARGET X POSITION\n'
                  f'OCCLUDER_WALL={occluder_wall}\nTARGET={target}\n'
                  f'ADJUSTED_X={adjusted_x}')
            return False

    return True


def verify_occluder_list_move_across(
    occluder_list,
    target_list,
    ignore_x_position=False
):
    assert verify_occluder_list(occluder_list, target_list)

    for i in range(len(target_list)):
        target = target_list[i]
        occluder_wall = occluder_list[i * 2]
        adjusted_x = intuitive_physics_hypercubes.occluder_x_to_object_x(
            occluder_wall['shows'][0]['position']['x'],
            target['shows'][0]['position']['z']
        )
        x_position_verified = False
        for position in (
            target['debug']['movement']['moveExit']['xDistanceByStep']
        ):
            if position == pytest.approx(adjusted_x):
                x_position_verified = True
                break
        if not ignore_x_position and not x_position_verified:
            print(f'[ERROR] PAIRED MOVE ACROSS OCCLUDER WALL X POSITION '
                  f'SHOULD BE CALCULATED FROM TARGET DISTANCE BY STEP LIST\n'
                  f'OCCLUDER_WALL={occluder_wall}\nTARGET={target}\n'
                  f'ADJUSTED_X={adjusted_x}')
            return False

    return True


def verify_target_implausible_hide_step(is_move_across, occluder, target):
    if is_move_across:
        verified = False
        movement = target['debug']['movement'][
            target['debug']['movement']['active']
        ]
        possible_step_offset_list = (
            target['debug']['movement']['stepList'] +
            ([movement['stopStep']] if 'stopStep' in movement else [])
        )
        for possible_step_offset in possible_step_offset_list:
            if possible_step_offset == 0:
                continue
            if target['hides'][0]['stepBegin'] != (
                target['shows'][0]['stepBegin'] + possible_step_offset
            ):
                continue
            verified = True
            break
        assert verified
    else:
        assert target['hides'][0]['stepBegin'] == (
            target['shows'][0]['stepBegin'] +
            intuitive_physics_hypercubes.OBJECT_FALL_TIME
        )
    return True


def verify_target_implausible_show_step(is_move_across, occluder, target,
                                        original_show_action, shows_index=0):
    if is_move_across:
        verified = False
        movement = target['debug']['movement'][
            target['debug']['movement']['active']
        ]
        possible_step_offset_list = (
            target['debug']['movement']['stepList'] +
            ([movement['stopStep']] if 'stopStep' in movement else [])
        )
        for possible_step_offset in possible_step_offset_list:
            if possible_step_offset == 0:
                continue
            if target['shows'][shows_index]['stepBegin'] != (
                original_show_action['stepBegin'] + possible_step_offset
            ) and shows_index == 0:
                continue
            actual_x = intuitive_physics_hypercubes.object_x_to_occluder_x(
                target['shows'][shows_index]['position']['x'],
                movement['zDistanceByStep'][possible_step_offset]
                if 'zDistanceByStep' in movement
                else target['shows'][shows_index]['position']['z']
            )
            expected_x = intuitive_physics_hypercubes.object_x_to_occluder_x(
                movement['xDistanceByStep'][possible_step_offset],
                movement['zDistanceByStep'][possible_step_offset]
                if 'zDistanceByStep' in movement
                else original_show_action['position']['z']
            )
            if not (
                actual_x >= (expected_x - 0.15) and
                actual_x <= (expected_x + 0.15)
            ):
                continue
            actual_z = target['shows'][shows_index]['position']['z']
            expected_z = (
                movement['zDistanceByStep'][possible_step_offset]
                if 'zDistanceByStep' in movement
                else original_show_action['position']['z']
            )
            if actual_z != expected_z:
                print(f'BAD Z {actual_z} VS {expected_z}')
                continue
            verified = True
            break
        if not verified:
            print(
                f'TARGET POSITION {target["shows"][shows_index]["position"]} '
                f'STEP LIST {possible_step_offset_list} '
                f'MOVEMENT X POSITION AT STEP LIST INDEX 0 '
                f'{movement["xDistanceByStep"][possible_step_offset_list[0]]} '
                f'ACTIVE {target["movement"]["active"]} MOVEMENT {movement}'
            )
        assert verified
    else:
        assert target['shows'][0]['stepBegin'] == (
            original_show_action['stepBegin'] +
            intuitive_physics_hypercubes.OBJECT_FALL_TIME
        )
        assert target['shows'][0]['position']['x'] == (
            original_show_action['position']['x']
        )
        assert target['shows'][0]['position']['z'] == (
            original_show_action['position']['z']
        )
    return True


def verify_target_implausible_shroud_step(is_move_across, occluder_1,
                                          occluder_2, target):
    if is_move_across:
        verified = False
        movement = target['debug']['movement'][
            target['debug']['movement']['active']
        ]
        possible_step_offset_list = (
            target['debug']['movement']['stepList'] +
            ([movement['stopStep']] if 'stopStep' in movement else [])
        )
        for possible_step_offset_1 in possible_step_offset_list:
            if possible_step_offset_1 == 0:
                continue
            for possible_step_offset_2 in possible_step_offset_list:
                if possible_step_offset_1 == possible_step_offset_2:
                    continue
                if possible_step_offset_2 == 0:
                    continue
                if target['shrouds'][0]['stepBegin'] != (
                    target['shows'][0]['stepBegin'] +
                    min(possible_step_offset_1, possible_step_offset_2) + 1
                ):
                    continue
                if target['shrouds'][0]['stepEnd'] != (
                    target['shows'][0]['stepBegin'] +
                    max(possible_step_offset_1, possible_step_offset_2) + 1
                ):
                    continue
                verified = True
                break
            if verified:
                break
        assert verified
    else:
        # TODO If we ever need STC fall-down scenes in a future eval.
        pass
    return True


def get_object_list(scene, role):
    return [
        instance for instance in scene['objects']
        if instance['debug']['role'] == role
    ]


def verify_same_object(one, two):
    # TODO Is this good enough?
    return (
        one['id'] == two['id'] and
        one['type'] == two['type'] and
        one['mass'] == two['mass'] and
        one['materials'] == two['materials'] and
        one['debug']['dimensions'] == two['debug']['dimensions']
    )
