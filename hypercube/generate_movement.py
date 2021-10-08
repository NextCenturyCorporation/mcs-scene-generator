import json

from generator.occluders import OCCLUDER_BUFFER

from .intuitive_physics_hypercubes import (
    MAX_TARGET_Z,
    MIN_TARGET_Z,
    MOVEMENT_JSON_FILENAME,
    STEP_Z,
    object_x_to_occluder_x,
    retrieve_off_screen_position_x,
    validate_in_view,
)
from .movements import (
    DEEP_EXIT_LIST,
    DEEP_STOP_LIST,
    MOVE_EXIT_LIST,
    MOVE_STOP_LIST,
    TOSS_EXIT_LIST,
    TOSS_STOP_LIST,
)

"""
This script creates the movements.json data file with all the movements used
by the passive intuitive physics scenes. Rerun this script whenever you update
movements.py and commit movements.json to the git repository.
"""


# Somewhat arbitrary
SLOWDOWN = 0.02


EXIT_LIST = [
    ('deepExit', DEEP_EXIT_LIST, False, False),
    ('tossExit', TOSS_EXIT_LIST, False, False)
]


STOP_LIST = [
    ('moveStop', MOVE_STOP_LIST, True, False),
    ('deepStop', DEEP_STOP_LIST, True, False),
    ('tossStop', TOSS_STOP_LIST, True, True)
]


EXIT_STOP_LIST = EXIT_LIST + STOP_LIST


def mark_stop_step():
    """Mark the step on which the object will (almost completely) stop moving
    in each stop-on-screen movement."""
    for movement_list in [MOVE_STOP_LIST, DEEP_STOP_LIST, TOSS_STOP_LIST]:
        for movement in movement_list:
            for index, value in enumerate(movement['xDistanceByStep']):
                if index > 0:
                    prior = movement['xDistanceByStep'][index - 1]
                    if value < (prior + SLOWDOWN):
                        movement['stopStep'] = index
                        break
            if 'stopStep' not in movement:
                movement['stopStep'] = len(movement['xDistanceByStep']) - 1


def mark_land_step():
    """Mark the step on which the object will land on the ground in each
    toss-and-stop-on-screen movement."""
    for movement_list in [TOSS_STOP_LIST]:
        for movement in movement_list:
            y_list = [y for y in movement['yDistanceByStep'] if y >= SLOWDOWN]
            movement['landStep'] = len(y_list) - 1


def identify_matching_movement(starting_data_list, movement_data_list):
    """Return the full list of matching X/Z positions, steps, and movements."""
    if len(movement_data_list) == 0:
        return starting_data_list
    name, other_move_list, does_stop, does_land = movement_data_list[0]
    matching_data_list = []
    # Iterate over each item in the data list...
    for position_z, step, position_x, move_index_list in starting_data_list:
        # Iterate over each move in the move list...
        for index, other_move in enumerate(other_move_list):
            # Find each comparison step in the other move.
            other_step_list = (
                ([(step, (not does_stop))]) +
                ([(other_move['stopStep'], True)] if does_stop else []) +
                ([(other_move['landStep'], False)] if does_land else [])
            )
            successful = True
            for other_step, validate_position in other_step_list:
                if len(other_move['xDistanceByStep']) <= other_step:
                    successful = False
                    break
                # Identify the starting position.
                other_z = other_move.get('startZ', position_z)
                other_x = other_move.get('startX', (
                    -1 * retrieve_off_screen_position_x(other_z)
                ))
                # Find the step's comparison X position in the other move.
                other_position_x = object_x_to_occluder_x(
                    (other_x + other_move['xDistanceByStep'][other_step]),
                    (other_z + other_move['zDistanceByStep'][other_step])
                    if 'zDistanceByStep' in other_move else other_z
                )
                if (
                    other_position_x is None or
                    not validate_in_view(other_position_x)
                ):
                    successful = False
                    break
                # Verify that each X is almost the same, if needed.
                if validate_position and (
                    other_position_x >= (position_x + OCCLUDER_BUFFER) or
                    other_position_x <= (position_x - OCCLUDER_BUFFER)
                ):
                    successful = False
                    break
            # If all the X positions are approximately the same, then it's a
            # match! Add the data with this move's index to the output.
            if successful:
                matching_data_list.append((
                    position_z, step, position_x, move_index_list + [index]
                ))
    print(f'DONE {name} WITH {len(matching_data_list)}')
    # Call recursively on the next move.
    return identify_matching_movement(
        matching_data_list,
        movement_data_list[1:]
    )


def save_matching_movement(
    movement,
    matching_data_list,
    option_list_property,
    movement_data_list
):
    """Add each data item in the given list to the option list with the given
    property."""
    for matching_data in matching_data_list:
        position_z, step, _, move_index_list = matching_data
        if step not in movement[option_list_property][position_z]:
            movement[option_list_property][position_z][step] = []
        # Save each movement's name with its matching index.
        option = {}
        for index, movement_index in enumerate(move_index_list):
            option[movement_data_list[index][0]] = movement_index
        # If this option will have both deep movements, ensure that they will
        # both use the same X/Z starting position (if not, skip it!).
        if 'deepExit' in option and 'deepStop' in option:
            deep_exit = DEEP_EXIT_LIST[option['deepExit']]
            deep_stop = DEEP_STOP_LIST[option['deepStop']]
            if (
                deep_exit['startX'] != deep_stop['startX'] or
                deep_exit['startZ'] != deep_stop['startZ']
            ):
                # Delete the empty array first to avoid an issue later.
                if len(movement[option_list_property][position_z][step]) == 0:
                    del movement[option_list_property][position_z][step]
                continue
        # Add it as an option in this list.
        movement[option_list_property][position_z][step].append(option)


def make_each_full_option_list():
    """Make each option list in each move-and-exit-the-screen movement."""
    iterator_z_max = (MAX_TARGET_Z - MIN_TARGET_Z) / STEP_Z
    for movement in MOVE_EXIT_LIST:
        movement['exitOnlyOptionList'] = {}
        movement['exitStopOptionList'] = {}
        exit_only_starting_data_list = []
        exit_stop_starting_data_list = []
        # Iterate over each possible Z position...
        for iterator_z in range(int(iterator_z_max) + 1):
            position_z = round(MIN_TARGET_Z + (STEP_Z * iterator_z), 2)
            starting_x = -1 * retrieve_off_screen_position_x(position_z)
            # Add each possible Z position as a key in each option list.
            movement['exitOnlyOptionList'][position_z] = {}
            movement['exitStopOptionList'][position_z] = {}
            # Iterate over each step in the current movement...
            for step in range(len(movement['xDistanceByStep'])):
                position_x = object_x_to_occluder_x(
                    (starting_x + movement['xDistanceByStep'][step]),
                    (position_z + movement['zDistanceByStep'][step])
                    if 'zDistanceByStep' in movement else position_z
                )
                if (
                    # Skip step 0 because it will never be within view.
                    position_x is None or step == 0 or
                    # Ensure an occluder at this X position is within view.
                    not validate_in_view(position_x)
                ):
                    continue
                # Add the X/Z position with its step to each data list.
                exit_only_starting_data_list.append(
                    (position_z, step, position_x, [])
                )
                exit_stop_starting_data_list.append(
                    (position_z, step, position_x, [])
                )
        print(f'MAKING exitOnlyOptionList ON moveExit {movement["forceX"]}')
        exit_only_matching_data_list = identify_matching_movement(
            exit_only_starting_data_list,
            EXIT_LIST
        )
        print(f'SAVING exitOnlyOptionList ON moveExit {movement["forceX"]}')
        save_matching_movement(
            movement,
            exit_only_matching_data_list,
            'exitOnlyOptionList',
            EXIT_LIST
        )
        print(f'MAKING exitStopOptionList ON moveExit {movement["forceX"]}')
        exit_stop_matching_data_list = identify_matching_movement(
            exit_stop_starting_data_list,
            EXIT_STOP_LIST
        )
        print(f'SAVING exitStopOptionList ON moveExit {movement["forceX"]}')
        save_matching_movement(
            movement,
            exit_stop_matching_data_list,
            'exitStopOptionList',
            EXIT_STOP_LIST
        )
        for iterator_z in range(int(iterator_z_max) + 1):
            position_z = round(MIN_TARGET_Z + (STEP_Z * iterator_z), 2)
            if len(movement['exitStopOptionList'][position_z].keys()) == 0:
                print(f'FAILURE: {position_z} !!!!!')
            else:
                print(f'SUCCESS: {position_z}')


def save_movement_to_json_file():
    with open(MOVEMENT_JSON_FILENAME, 'w') as movement_file:
        json.dump({
            'moveExit': MOVE_EXIT_LIST,
            'deepExit': DEEP_EXIT_LIST,
            'tossExit': TOSS_EXIT_LIST,
            'moveStop': MOVE_STOP_LIST,
            'deepStop': DEEP_STOP_LIST,
            'tossStop': TOSS_STOP_LIST,
        }, movement_file)


def main():
    print('GENERATING PASSIVE INTUITIVE PHYSICS MOVEMENT (PLEASE WAIT)...')
    mark_stop_step()
    mark_land_step()
    make_each_full_option_list()
    save_movement_to_json_file()
    print('FINISHED GENERATING MOVEMENT')


if __name__ == '__main__':
    main()
