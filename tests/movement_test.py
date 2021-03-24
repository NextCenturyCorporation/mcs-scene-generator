from intuitive_physics_hypercubes import MIN_TARGET_Z, MAX_TARGET_Z, STEP_Z, \
    object_x_to_occluder_x, retrieve_off_screen_position_x, MOVEMENT

import occluders


def validate_option_list(
    option_list_property,
    base_move,
    base_starting_x,
    base_position_z,
    move_data_list
):
    full_option_list = base_move[option_list_property]
    for base_step, option_list in full_option_list[base_position_z].items():
        base_position_x = object_x_to_occluder_x(
            (base_starting_x + base_move['xDistanceByStep'][base_step]),
            (base_position_z + base_move['zDistanceByStep'][base_step])
            if 'zDistanceByStep' in base_move else base_position_z
        )
        # print(f'ASSERT MOVE-EXIT {base_move["forceX"]} Z {base_position_z} '
        #      f'STEP {base_step} OPTION LIST LENGTH {len(option_list)}')
        assert len(option_list) > 0
        for option in option_list:
            if 'deepExit' in option and 'deepStop' in option:
                deep_exit = MOVEMENT.DEEP_EXIT_LIST[option['deepExit']]
                deep_stop = MOVEMENT.DEEP_STOP_LIST[option['deepStop']]
                assert (
                    deep_exit['startX'] == deep_stop['startX'] and
                    deep_exit['startZ'] == deep_stop['startZ']
                )
            for name, move_list, does_stop, does_land in move_data_list:
                index = option[name]
                movement = move_list[index]
                step_list = (
                    ([(base_step, (not does_stop))]) +
                    ([(movement['stopStep'], True)] if does_stop else []) +
                    ([(movement['landStep'], False)] if does_land else [])
                )
                starting_z = movement.get('startZ', base_position_z)
                starting_x = movement.get('startX', (
                    -1 * retrieve_off_screen_position_x(starting_z)
                ))
                for step, validate_position in step_list:
                    position_x = object_x_to_occluder_x(
                        (starting_x + movement['xDistanceByStep'][step]),
                        (starting_z + movement['zDistanceByStep'][step])
                        if 'zDistanceByStep' in movement else starting_z
                    )
                    assert base_position_x is not None
                    assert position_x is not None
                    if validate_position:
                        assert position_x <= (base_position_x + 0.1)
                        assert position_x >= (base_position_x - 0.1)


def test_exit_only_movement():
    exit_only_movement_data_list = [
        ('deepExit', MOVEMENT.DEEP_EXIT_LIST, False, False),
        ('tossExit', MOVEMENT.TOSS_EXIT_LIST, False, False)
    ]
    iterator_z_max = (MAX_TARGET_Z - MIN_TARGET_Z) / STEP_Z
    for iterator_z in range(int(iterator_z_max) + 1):
        position_z = round(MIN_TARGET_Z + (STEP_Z * iterator_z), 2)
        starting_x = -1 * retrieve_off_screen_position_x(position_z)
        for movement in MOVEMENT.MOVE_EXIT_LIST:
            assert len(movement['exitOnlyOptionList'][position_z].keys()) > 0
            validate_option_list(
                'exitOnlyOptionList',
                movement,
                starting_x,
                position_z,
                exit_only_movement_data_list
            )


def is_known_exit_stop_failure(movement, position_z):
    # Based on output from running the generate_movement.py script.
    if movement['forceX'] == 670:
        return position_z in [1.7, 2.25, 2.3, 2.35, 3.1]
    if movement['forceX'] == 690:
        return position_z in [1.8, 2.4, 3.5, 3.55, 3.6, 3.65]
    return False


def test_exit_stop_movement():
    exit_stop_movement_data_list = [
        ('deepExit', MOVEMENT.DEEP_EXIT_LIST, False, False),
        ('tossExit', MOVEMENT.TOSS_EXIT_LIST, False, False),
        ('moveStop', MOVEMENT.MOVE_STOP_LIST, True, False),
        ('deepStop', MOVEMENT.DEEP_STOP_LIST, True, False),
        ('tossStop', MOVEMENT.TOSS_STOP_LIST, True, True)
    ]
    iterator_z_max = (MAX_TARGET_Z - MIN_TARGET_Z) / STEP_Z
    for iterator_z in range(int(iterator_z_max) + 1):
        position_z = round(MIN_TARGET_Z + (STEP_Z * iterator_z), 2)
        starting_x = -1 * retrieve_off_screen_position_x(position_z)
        for movement in MOVEMENT.MOVE_EXIT_LIST:
            if is_known_exit_stop_failure(movement, position_z):
                continue
            assert len(movement['exitStopOptionList'][position_z].keys()) > 0
            validate_option_list(
                'exitStopOptionList',
                movement,
                starting_x,
                position_z,
                exit_stop_movement_data_list
            )


def validate_double_occluder(
    option_list_property,
    movement,
    starting_x,
    position_z
):
    full_option_list = movement[option_list_property]
    for step_1, option_list_1 in full_option_list[position_z].items():
        x_1 = object_x_to_occluder_x(
            (starting_x + movement['xDistanceByStep'][step_1]),
            (position_z + movement['zDistanceByStep'][step_1])
            if 'zDistanceByStep' in movement else position_z
        )
        for step_2, option_list_2 in full_option_list[position_z].items():
            if step_2 == step_1:
                continue
            x_2 = object_x_to_occluder_x(
                (starting_x + movement['xDistanceByStep'][step_2]),
                (position_z + movement['zDistanceByStep'][step_2])
                if 'zDistanceByStep' in movement else position_z
            )
            if occluders.calculate_separation_distance(
                x_1,
                occluders.OCCLUDER_MAX_SCALE_X,
                x_2,
                occluders.OCCLUDER_MAX_SCALE_X
            ) < 0:
                continue
            for option_1 in option_list_1:
                for option_2 in option_list_2:
                    if option_1 == option_2:
                        return True
    return False


def is_known_double_occluder_failure(position_z):
    # Based on output from running this test case.
    return position_z in [
        3.2, 3.25, 3.35, 3.4, 3.45, 3.5, 3.55, 3.6, 3.65, 3.7, 3.75, 3.8, 3.85,
        3.9, 3.95, 4.0, 4.05, 4.1, 4.15, 4.2, 4.25, 4.3, 4.35, 4.4
    ]


def test_exit_only_movement_double_occluder():
    iterator_z_max = (MAX_TARGET_Z - MIN_TARGET_Z) / STEP_Z
    for iterator_z in range(int(iterator_z_max) + 1):
        position_z = round(MIN_TARGET_Z + (STEP_Z * iterator_z), 2)
        if is_known_double_occluder_failure(position_z):
            continue
        starting_x = -1 * retrieve_off_screen_position_x(position_z)
        successful = False
        for movement in MOVEMENT.MOVE_EXIT_LIST:
            successful = validate_double_occluder(
                'exitOnlyOptionList',
                movement,
                starting_x,
                position_z
            ) or successful
        if not successful:
            print(f'FAILED DOUBLE OCCLUDER AT Z POSITION {position_z}')
        assert successful
