import argparse
import glob
import logging
import os

import machine_common_sense as mcs
import shapely
from shapely import affinity

from generator import optimal_path

DEBUG_DIRECTORY = './'
PERFORMER_AGENT_MAX_REACH = 1
PERFORMER_AGENT_MASS = 2
TROPHY_SIZE = (0.19, 0.14)


def action_to_string(action_data):
    """Return the given action data as a string."""
    action_text = action_data['action']
    for key, value in action_data['params'].items():
        action_text += ',' + key + '=' + value
    return action_text


def action_list_to_single_string(action_list):
    """Return the given action data list as a single string."""
    return ';'.join([
        action_to_string(action_data) for action_data in action_list
    ])


def find_distance_to(step_metadata, object_metadata):
    """Find and return the distance from the performer agent's current location
    to the object with the given object output metadata."""
    bounds = shapely.geometry.box(
        object_metadata.position['x'] - (TROPHY_SIZE[0] / 2.0),
        object_metadata.position['z'] - (TROPHY_SIZE[1] / 2.0),
        object_metadata.position['x'] + (TROPHY_SIZE[0] / 2.0),
        object_metadata.position['z'] + (TROPHY_SIZE[1] / 2.0)
    )
    bounds = affinity.rotate(bounds, -object_metadata.rotation['y'])
    distance = shapely.geometry.Point(
        step_metadata.position['x'],
        step_metadata.position['z']
    ).distance(bounds)
    return distance


def find_path_list(scene_data, debug_plots):
    """Find and return the list of each possible best path."""
    target_dict = find_target_dict(scene_data)
    path_list = optimal_path.find_possible_best_path_list(
        scene_data.get('roomDimensions'),
        scene_data['performerStart'],
        target_dict,
        [object_dict for object_dict in scene_data['objects'] if (
            # Ignore the target object.
            object_dict['id'] != target_dict['id'] and
            # Ignore any object inside a container.
            (not object_dict.get('locationParent', None)) and
            # Ignore any object light enough that won't obstruct the performer.
            (object_dict['mass'] > PERFORMER_AGENT_MASS)
        )],
        (DEBUG_DIRECTORY + scene_data['name']) if debug_plots else None
    )
    for path in path_list:
        if 'locationParent' in target_dict:
            optimal_path.open_container_and_pickup_target(
                path,
                target_dict['id'],
                [object_dict for object_dict in scene_data['objects'] if (
                    object_dict['id'] == target_dict['locationParent']
                )][0]
            )
        else:
            optimal_path.pickup_target(path, target_dict['id'])
    return path_list


def find_target_dict(scene_data):
    """Find and return the target dict from the scene data."""
    return scene_data['objects'][0]


def read_path_file(folder, name):
    """Read and return an action path from file."""
    path = optimal_path.ShortestPath([], None, None)
    with open(folder + '/' + name + '.txt', 'r') as action_file:
        for line in action_file:
            line_data = line.strip().split(',')
            action_data = {
                'action': line_data[0],
                'params': {}
            }
            for key_value in line_data[1:]:
                key_value_data = key_value.split('=')
                action_data['params'][key_value_data[0]] = key_value_data[1]
            path.action_list.append(action_data)
    return [path]


def run_scene_with_action_list(scene_data, controller, action_list):
    """Run the MCS scene with the given data using the given MCS controller and
    MCS action data list. Return the reward, obstructed status, and modified
    action data list."""
    modified_action_list = action_list

    # Start the scene.
    step_metadata = controller.start_scene(scene_data)

    opened = False
    target_dict = find_target_dict(scene_data)
    container_id = target_dict.get('locationParent', None)

    # Run each action from the scene's shortest path.
    for index, action_data in enumerate(action_list):
        action = action_data['action']
        params = action_data['params']
        step_metadata = controller.step(action, **params)
        # If the path was obstructed, just quit now.
        if step_metadata.return_status == 'OBSTRUCTED':
            return 0, index, action_list
        # Try to open the target's container if it's within reach and visible.
        if container_id and not opened:
            done, step_metadata, modified_action_list, opened = try_early_open(
                controller,
                step_metadata,
                action_list,
                index,
                container_id
            )
        # Try to pickup the target object if it's within reach and visible.
        else:
            done, step_metadata, modified_action_list = (
                try_early_pickup(controller, step_metadata, action_list, index)
            )
        # If trying to pickup the target early worked, end the scene now.
        if done:
            break

    # End the scene.
    controller.end_scene("", 1)

    # Return the reward received from the last action.
    return step_metadata.reward, -1, modified_action_list


def save_shortest_path(output_folder, output_filename, action_list):
    """Save the action list to file."""
    os.makedirs(output_folder, exist_ok=True)
    output_filename = output_folder + '/' + output_filename + '.txt'
    with open(output_filename, 'w') as output_file:
        for action_data in action_list:
            output_file.write(action_to_string(action_data) + '\n')


def try_early_open(controller, step_metadata, action_list, index, object_id):
    """Try to open the container early if it's visible and within reach; then,
    try to pickup the target; if successful, return the modified action data
    list."""
    for object_metadata in step_metadata.object_list:
        # If this is the output metadata for the container and it's visible...
        if object_metadata.uuid == object_id and object_metadata.visible:
            distance = find_distance_to(step_metadata, object_metadata)
            # If it's within reach...
            if distance <= PERFORMER_AGENT_MAX_REACH:
                # Run an open action.
                step_metadata = controller.step(
                    'OpenObject',
                    objectId=object_metadata.uuid
                )
                # If successful, modify the action list with the open action.
                if step_metadata.return_status == 'SUCCESSFUL':
                    action_list = action_list[:(index + 1)] + [{
                        'action': 'OpenObject',
                        'params': {'objectId': object_metadata.uuid}
                    }]
                # If out-of-reach...
                elif step_metadata.return_status == 'OUT_OF_REACH':
                    # Run a move action.
                    step_metadata = controller.step('MoveAhead')
                    # If obstructed, the early open failed, so return.
                    if step_metadata.return_status == 'OBSTRUCTED':
                        return False, step_metadata, action_list, False
                    # Else run an open action again.
                    step_metadata = controller.step(
                        'OpenObject',
                        objectId=object_metadata.uuid
                    )
                    # If the open action is obstructed or out-of-reach, the
                    # early open failed, so undo the move and return.
                    if (
                        step_metadata.return_status == 'OUT_OF_REACH' or
                        step_metadata.return_status == 'OBSTRUCTED'
                    ):
                        step_metadata = controller.step('MoveBack')
                        return False, step_metadata, action_list, False
                    # Else the early open was successful so modify the action
                    # list with the new move and open actions.
                    action_list = action_list[:(index + 1)] + [{
                        'action': 'MoveAhead',
                        'params': {}
                    }, {
                        'action': 'OpenObject',
                        'params': {'objectId': object_metadata.uuid}
                    }]
                # Else, assume the early open failed and return.
                else:
                    return False, step_metadata, action_list, False
                # If the early open was successful, try an early pickup.
                done, step_metadata, action_list = try_early_pickup(
                    controller,
                    step_metadata,
                    action_list,
                    index
                )
                return done, step_metadata, action_list, True
    # Return failed (object was not visible or not within reach).
    return False, step_metadata, action_list, False


def try_early_pickup(controller, step_metadata, action_list, index):
    """Try to pickup the target early if it's visible and within reach; if
    successful, return the modified action data list."""
    for object_metadata in step_metadata.object_list:
        # If this is the output metadata for the target and it's visible...
        if object_metadata.shape == 'trophy' and object_metadata.visible:
            distance = find_distance_to(step_metadata, object_metadata)
            # If it's within reach...
            if distance <= PERFORMER_AGENT_MAX_REACH:
                # Run a pickup action.
                step_metadata = controller.step(
                    'PickupObject',
                    objectId=object_metadata.uuid
                )
                # If successful, modify the action list with the pickup action.
                if step_metadata.return_status == 'SUCCESSFUL':
                    action_list = action_list[:(index + 1)] + [{
                        'action': 'PickupObject',
                        'params': {'objectId': object_metadata.uuid}
                    }]
                # If out-of-reach...
                elif step_metadata.return_status == 'OUT_OF_REACH':
                    # Run a move action.
                    step_metadata = controller.step('MoveAhead')
                    # If obstructed, the early pickup failed, so return.
                    if step_metadata.return_status == 'OBSTRUCTED':
                        return False, step_metadata, action_list
                    # Else run a pickup action again.
                    step_metadata = controller.step(
                        'PickupObject',
                        objectId=object_metadata.uuid
                    )
                    # If the pickup action is obstructed or out-of-reach, the
                    # early pickup failed, so undo the move and return.
                    if (
                        step_metadata.return_status == 'OUT_OF_REACH' or
                        step_metadata.return_status == 'OBSTRUCTED'
                    ):
                        step_metadata = controller.step('MoveBack')
                        return False, step_metadata, action_list
                    # Else the early pickup was successful so modify the action
                    # list with the new move and pickup actions.
                    action_list = action_list[:(index + 1)] + [{
                        'action': 'MoveAhead',
                        'params': {}
                    }, {
                        'action': 'PickupObject',
                        'params': {'objectId': object_metadata.uuid}
                    }]
                # Else, assume the early pickup failed and return.
                else:
                    return False, step_metadata, action_list
                # Return success.
                return True, step_metadata, action_list
    # Return failed (object was not visible or not within reach).
    return False, step_metadata, action_list


def main(args):
    # Identify all the _debug.json MCS scene files.
    filename_list = glob.glob(args.file_path_prefix + '*_debug.json')
    filename_list.sort()

    if len(filename_list) == 0:
        print(f'No files ending in _debug.json with prefix: '
              f'{args.file_path_prefix}')
        return

    # Start a single MCS controller for testing all the MCS scene files.
    controller = mcs.create_controller(args.mcs_unity_build, debug=True,
                                       history_enabled=False)

    finished_file_list = []
    failed_file_list = []

    for filename in filename_list:
        print('**************************************')
        print(f'>>>>> {filename}')
        obstructed_path_text_list = []
        reward = None
        # Load the scene data from its JSON file.
        scene_data, status = mcs.load_config_json_file(filename)
        if status is not None:
            print(status)
            continue
        # Find each possible best path for the scene.
        path_list = (
            read_path_file(args.action_file_folder, scene_data.name)
            if args.read_existing
            else find_path_list(scene_data, args.debug_plots)
        )
        if args.debug_actions:
            for i, path in enumerate(path_list):
                save_shortest_path(
                    DEBUG_DIRECTORY + scene_data.name + '/',
                    scene_data.name + '_' + str(i),
                    path.action_list
                )
        for i, path in enumerate(path_list):
            print(f'>>>>> Shortest Path {i}: {len(path_list[0].action_list)}')
            # If this path starts with a series of actions that was already
            # tried and returned obstructed, then skip this path.
            path_text = action_list_to_single_string(path.action_list)
            obstructed = False
            for obstructed_path_text in obstructed_path_text_list:
                if path_text.startswith(obstructed_path_text):
                    obstructed = True
                    break
            if obstructed:
                print(f'>>>>> Skipping Obstructed Path {i}')
                continue
            # Test the path to see if it will return a positive reward.
            reward, obstructed_step, modified_action_list = (
                run_scene_with_action_list(
                    scene_data,
                    controller,
                    path.action_list
                )
            )
            # If the path was obstructed, then try the next path.
            if obstructed_step >= 0:
                reward = None
                obstructed_path_text_list.append(action_list_to_single_string(
                    path.action_list[:(obstructed_step + 1)]
                ))
                continue
            if reward:
                print(f'>>>>> Reward: {reward}')
            # If the reward was negative, then try the next path.
            if reward < 0:
                reward = None
                continue
            if len(modified_action_list) < len(path.action_list):
                print(f'>>>>> Modified Path {i} : {len(modified_action_list)}')
            # If the reward was positive, save this path and mark it finished.
            save_shortest_path(
                args.action_file_folder,
                scene_data['name'],
                modified_action_list
            )
            finished_file_list.append((filename, len(modified_action_list)))
            break
        # If no path returned a positive reward, this file failed.
        if (not path_list) or (reward is None) or (reward <= 0):
            failed_file_list.append(filename)

    # Print the successful and failed files.
    print('**************************************')
    print('Successful:')
    if len(finished_file_list) == 0:
        print('None')
    for filename, total_steps in finished_file_list:
        print(f'({total_steps}) {filename}')
    print('Failed:')
    if len(failed_file_list) == 0:
        print('None')
    for filename in failed_file_list:
        print(filename)


if __name__ == "__main__":
    # Read command line arguments.
    parser = argparse.ArgumentParser(description='Find and Test Shortest Path')
    parser.add_argument(
        'mcs_unity_build',
        help='File path to the MCS unity build file')
    parser.add_argument(
        'file_path_prefix',
        help='File path prefix for the _debug.json MCS scene files')
    parser.add_argument(
        'action_file_folder',
        help='Folder for the output files containing action lists')
    parser.add_argument(
        '--read-existing',
        default=False,
        action='store_true',
        help='Read an existing action file from the action_file_folder')
    parser.add_argument(
        '--debug-actions',
        default=False,
        action='store_true',
        help='Save the actions of each possible path to text file')
    parser.add_argument(
        '--debug-plots',
        default=False,
        action='store_true',
        help='Save the plots of each possible path to image files')
    parser.add_argument(
        '-v',
        '--verbose',
        default=False,
        action='store_true',
        help='Show debug log messages')
    args = parser.parse_args()

    logging.basicConfig(format='%(message)s', level=(
        logging.DEBUG if args.verbose else logging.ERROR
    ))

    main(args)
