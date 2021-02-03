import copy
import random
from typing import Any, Dict, List, Tuple
import uuid

import exceptions
import geometry
from separating_axis_theorem import sat_entry
import hypercubes
import tags


class ObjectConfig():
    def __init__(
        self,
        object_type: str,
        center_y: float,
        scale_x: float,
        scale_y: float,
        scale_z: float,
        untrained=False
    ) -> None:
        self.object_type = object_type
        self.center_y = center_y
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.scale_z = scale_z
        self.untrained = untrained


class ObjectConfigWithMaterial(ObjectConfig):
    def __init__(
        self,
        config: ObjectConfig,
        material: Tuple[str, List[str]]
    ) -> None:
        super().__init__(
            config.object_type,
            config.center_y,
            config.scale_x,
            config.scale_y,
            config.scale_z,
            config.untrained
        )
        self.material = material


EXPECTED = 'expected'
UNEXPECTED = 'unexpected'

# Use a 10x10 grid, with each cell 0.5 x 0.5, including the border wall.
GRID_MIN_X = -2.5
GRID_MAX_X = 2.5
GRID_MIN_Z = -2.5
GRID_MAX_Z = 2.5

JSON_BORDER_WALL_MIN_X = 0
JSON_BORDER_WALL_MIN_Z = 0
JSON_BORDER_WALL_MAX_X = 180
JSON_BORDER_WALL_MAX_Z = 180

# The wait time in steps before and after the agent's movement in each trial.
STEP_WAIT_TIME = 3

AGENT_OBJECT_CONFIG_LIST = [
    ObjectConfig('cone', 0.25, 0.225, 0.5, 0.225, False),
    ObjectConfig('cube', 0.25, 0.125, 0.5, 0.125, False),
    ObjectConfig('cylinder', 0.25, 0.225, 0.25, 0.225, False),
    ObjectConfig('square_frustum', 0.25, 0.225, 0.5, 0.225, False),
    ObjectConfig('circle_frustum', 0.25, 0.225, 0.5, 0.225, True),
    ObjectConfig('pyramid', 0.25, 0.225, 0.5, 0.225, True),
    ObjectConfig('tube_narrow', 0.25, 0.225, 0.5, 0.225, True),
    ObjectConfig('tube_wide', 0.25, 0.225, 0.5, 0.225, True)
]
AGENT_OBJECT_MATERIAL_LIST = [
    ('Custom/Materials/Blue', ['blue']),
    ('Custom/Materials/Green', ['green']),
    ('Custom/Materials/Purple', ['purple']),
    ('Custom/Materials/Red', ['red'])
]
FLOOR_OBJECT_MATERIAL = ('Custom/Materials/White', ['white'])
GOAL_OBJECT_CONFIG_LIST = [
    ObjectConfig('cube', 0.125, 0.225, 0.25, 0.225, False),
    ObjectConfig('cube', 0.0625, 0.225, 0.125, 0.225, False),
    ObjectConfig('cylinder', 0.0625, 0.225, 0.0625, 0.225, False),
    ObjectConfig('semi_sphere', 0.0625, 0.225, 0.25, 0.225, False),
    ObjectConfig('sphere', 0.125, 0.225, 0.25, 0.225, False),
    ObjectConfig('square_frustum', 0.0625, 0.225, 0.125, 0.225, False),
    ObjectConfig('cube_hollow_narrow', 0, 0.225, 0.25, 0.225, True),
    ObjectConfig('cube_hollow_wide', 0, 0.225, 0.25, 0.225, True),
    ObjectConfig('letter_x', 0, 0.225, 0.125, 0.225, True),
    ObjectConfig('hash', 0, 0.225, 0.125, 0.225, True),
    ObjectConfig('tube_narrow', 0.125, 0.225, 0.25, 0.225, True),
    ObjectConfig('tube_wide', 0.125, 0.225, 0.25, 0.225, True)
]
GOAL_OBJECT_MATERIAL_LIST = [
    ('Custom/Materials/Brown', ['brown']),
    ('Custom/Materials/Cyan', ['cyan']),
    ('Custom/Materials/Grey', ['grey']),
    ('Custom/Materials/Indigo', ['indigo']),
    ('Custom/Materials/Lime', ['lime']),
    ('Custom/Materials/Maroon', ['maroon']),
    ('Custom/Materials/Navy', ['navy']),
    ('Custom/Materials/Olive', ['olive']),
    ('Custom/Materials/Orange', ['orange']),
    ('Custom/Materials/Pink', ['pink']),
    ('Custom/Materials/Teal', ['teal']),
    ('Custom/Materials/Violet', ['violet']),
    ('Custom/Materials/Yellow', ['yellow'])
]
HOME_OBJECT_HEIGHT = [0.000625, 0.00125]
HOME_OBJECT_MATERIAL = ('Custom/Materials/Magenta', ['magenta'])
HOME_OBJECT_SIZE = [0.5, 0.5]
WALL_OBJECT_HEIGHT = [0.0625, 0.125]
WALL_OBJECT_MATERIAL = ('Custom/Materials/Black', ['black'])
WALL_OBJECT_SIZE = [0.5, 0.5]


def _choose_config_list(
    trial_list: List[List[Dict[str, Any]]],
    config_list: List[Dict[str, Any]],
    object_type_list: List[str],
    material_list: List[str],
    json_property: str
) -> List[ObjectConfigWithMaterial]:
    """Choose and return the shape and color of each object in the scene to use
    in both scenes across the pair so they always have the same config."""

    object_config_list = []

    # Ensure multiple objects won't have the same config or material.
    used_config_index_list = []
    used_material_index_list = []

    # Retrieve the relevant data from the first frame of the first trial.
    # Assume the number of objects will never change across trials, and
    # objects will never change shape/color across trials/frames.
    json_object_list = trial_list[0][0][json_property]

    # TODO Update this once the JSON 'agent' data becomes a list.
    if json_property == 'agent':
        json_object_list = [json_object_list]

    # Randomly choose each object's shape and color config.
    for index, json_object in enumerate(json_object_list):
        filtered_config_list = [
            config for config in config_list
            if config.object_type == object_type_list[index]
        ] if object_type_list[index] else config_list
        config_with_material = _choose_object_config(
            filtered_config_list if len(filtered_config_list) > 0
            else config_list,
            material_list,
            used_config_index_list,
            used_material_index_list
        )
        object_config_list.append(config_with_material)

    return object_config_list


def _choose_object_config(
    config_list: List[Dict[str, Any]],
    material_list: List[str],
    used_config_index_list: List[int],
    used_material_index_list: List[int]
) -> ObjectConfigWithMaterial:
    """Choose and return a random config and material from the given lists
    that aren't already used. Modifies the given used index lists."""

    config_index_list = range(0, len(config_list))
    config_index = random.choice(config_index_list)
    while config_index in used_config_index_list:
        config_index = random.choice(config_index_list)
    used_config_index_list.append(config_index)
    config = config_list[config_index]

    material_index_list = range(0, len(material_list))
    material_index = random.choice(material_index_list)
    while material_index in used_material_index_list:
        material_index = random.choice(material_index_list)
    used_material_index_list.append(material_index)
    material = material_list[material_index]

    return ObjectConfigWithMaterial(config, material)


def _create_action_list(
    trial_list: List[List[Dict[str, Any]]]
) -> List[List[str]]:
    """Create and return the MCS scene's action list using the given trial
    list from the JSON file data."""
    action_list = []
    for index in range(0, len(trial_list)):
        # Add 1 for the EndHabituation action step at the end of the trial.
        total_steps = len(trial_list[index]) + 1
        print(f'Trial={index+1} Frames={len(trial_list[index])} Steps='
              f'{total_steps}')
        action_list.extend([['Pass']] * (total_steps - 1))
        action_list.append(['EndHabituation'])
    # Remove the EndHabituation action from the last test trial.
    return action_list[:-1]


def _create_agent_object_list(
    trial_list: List[List[Dict[str, Any]]],
    agent_object_config_list: List[ObjectConfigWithMaterial],
    unit_size: Tuple[float, float]
) -> List[Dict[str, Any]]:
    """Create and return the MCS scene's agent object list using the given
    trial list from the JSON file data."""

    agent_object_list = []

    # Retrieve the agent data from the first frame of the first trial.
    # Assume only one agent and the agent will never change shape/color.
    json_agent = trial_list[0][0]['agent']
    json_coords = json_agent[0]
    json_radius = json_agent[1]
    json_size = [json_radius * 2, json_radius * 2]

    # Create the MCS agent object.
    config_with_material = agent_object_config_list[0]
    agent_object = _create_object(
        'agent_',
        config_with_material.object_type,
        config_with_material.material,
        [config_with_material.center_y, config_with_material.scale_y],
        [config_with_material.scale_x, config_with_material.scale_z],
        json_coords,
        json_size,
        unit_size
    )
    agent_object[tags.SCENE.UNTRAINED_SHAPE] = config_with_material.untrained
    agent_object_list.append(agent_object)

    # Remove the agent's first appearance (we will override it later).
    agent_object['shows'] = []
    agent_object['boundsAtStep'] = []

    # Add data for the agent's movement across the frames to each step.
    step = 0
    for trial in trial_list:
        for frame in trial:
            json_agent = frame['agent']
            json_coords = json_agent[0]
            json_radius = json_agent[1]
            json_size = [json_radius * 2, json_radius * 2]
            # Move the agent to its new position for the step.
            agent_object['shows'].append(_create_show(
                step,
                agent_object['configHeight'],
                agent_object['configSize'],
                json_coords,
                json_size,
                unit_size
            ))
            step += 1
            agent_object['boundsAtStep'].append(
                agent_object['shows'][-1]['boundingBox']
            )
        # Add 1 for the EndHabituation action step at the end of the trial.
        step += 1
        agent_object['boundsAtStep'].append(
            agent_object['shows'][-1]['boundingBox']
        )

    # Remove the scale from each element in 'shows' except for the first, or
    # it will really mess up the simulation.
    for show in agent_object['shows'][1:]:
        del show['scale']

    return agent_object_list


def _create_goal_object_list(
    trial_list: List[List[Dict[str, Any]]],
    goal_object_config_list: List[ObjectConfigWithMaterial],
    agent_start_bounds: List[Dict[str, float]],
    filename_prefix: str,
    unit_size: Tuple[float, float]
) -> List[Dict[str, Any]]:
    """Create and return the MCS scene's goal object list using the given
    trial list from the JSON file data."""

    goal_object_list = []

    # Retrieve the objects data from the first frame of the first trial.
    # Assume the number of objects will never change, and the objects will
    # never change shape/color.
    for index, json_object in enumerate(trial_list[0][0]['objects']):
        json_coords = json_object[0]
        json_radius = json_object[1]
        json_size = [json_radius * 2, json_radius * 2]

        # Create the MCS goal object.
        config_with_material = goal_object_config_list[index]
        goal_object = _create_object(
            'object_',
            config_with_material.object_type,
            config_with_material.material,
            [config_with_material.center_y, config_with_material.scale_y],
            [config_with_material.scale_x, config_with_material.scale_z],
            json_coords,
            json_size,
            unit_size
        )
        goal_object[
            tags.SCENE.UNTRAINED_SHAPE
        ] = config_with_material.untrained
        goal_object_list.append(goal_object)

        # Add the object's bounds for each other frame of the first trial.
        for _ in range(0, len(trial_list[0])):
            goal_object['boundsAtStep'].append(
                goal_object['shows'][-1]['boundingBox']
            )

    # Find the step for the start of the second trial.
    # Assume scenes will have more than one trial.
    step = _identify_trial_index_starting_step(1, trial_list)

    # Add data for each object's new position to each trial's start step.
    # Assume objects only change in position across trials (not frames).
    for trial in trial_list[1:]:
        for index, json_object in enumerate(trial[0]['objects']):
            goal_object = goal_object_list[index]
            json_coords = json_object[0]
            json_radius = json_object[1]
            json_size = [json_radius * 2, json_radius * 2]
            # Move the object to its new position for the trial.
            goal_object['shows'].append(_create_show(
                step,
                goal_object['configHeight'],
                goal_object['configSize'],
                json_coords,
                json_size,
                unit_size
            ))
            # Add the object's bounds for each frame of the trial.
            for _ in range(0, len(trial) + 1):
                goal_object['boundsAtStep'].append(
                    goal_object['shows'][-1]['boundingBox']
                )
        # Add 1 for the EndHabituation action step at the end of the trial.
        step += len(trial) + 1

    for goal_object in goal_object_list:
        for index, show in enumerate(goal_object['shows']):
            # We can't have the object's position on top of the agent's start
            # position or the agent and object will collide. This can happen
            # if the 2D icons overlap themselves in the original data.
            if sat_entry(agent_start_bounds, show['boundingBox']):
                raise exceptions.SceneException(
                    f'Cannot convert {filename_prefix} because an object is '
                    f'on the agent\'s home in trial {index + 1}')
            # Remove the scale from each element in 'shows' except for the
            # first, or it will really mess up the simulation.
            if index > 0:
                del show['scale']

    return goal_object_list


def _create_home_object(
    trial_list: List[List[Dict[str, Any]]],
    unit_size: Tuple[float, float]
) -> Dict[str, Any]:
    """Create and return the MCS scene's home object using the given trial
    list from the JSON file data."""

    # Retrieve the home data from the first frame of the first trial.
    # Assume only one home and the home will never change.
    json_home = trial_list[0][0]['home']
    json_coords = json_home[0]
    json_radius = json_home[1]
    json_size = [json_radius * 2, json_radius * 2]

    # Create the MCS home object.
    home_object = _create_object(
        'home_',
        'cube',
        HOME_OBJECT_MATERIAL,
        HOME_OBJECT_HEIGHT,
        HOME_OBJECT_SIZE,
        json_coords,
        json_size,
        unit_size
    )
    home_object['kinematic'] = True
    home_object['structure'] = True
    return home_object


def _create_object(
    id_prefix: str,
    object_type: str,
    object_material: Tuple[str, str],
    object_height: Tuple[float, float],
    object_size: Tuple[float, float],
    json_coords: Tuple[int, int],
    json_size: Tuple[int, int],
    unit_size: Tuple[float, float]
) -> Dict[str, Any]:
    """Create and return an MCS object using the given data."""
    mcs_object = {
        'id': id_prefix + str(uuid.uuid4()),
        'type': object_type,
        'materials': [object_material[0]],
        'info': object_material[1] + [object_type],
        # Save the object's height and size data for future use.
        'configHeight': object_height,
        'configSize': object_size,
        'shows': [_create_show(
            0,
            object_height,
            object_size,
            json_coords,
            json_size,
            unit_size
        )]
    }
    mcs_object['info'].append(' '.join(mcs_object['info']))
    mcs_object['boundsAtStep'] = [mcs_object['shows'][0]['boundingBox']]
    return mcs_object


def _create_scene(
    body_template: Dict[str, Any],
    goal_template: Dict[str, Any],
    agent_object_config_list: List[ObjectConfigWithMaterial],
    goal_object_config_list: List[ObjectConfigWithMaterial],
    trial_list: List[List[Dict[str, Any]]],
    filename_prefix: str,
    is_expected: bool
) -> Dict[str, Any]:
    """Create and return the MCS scene using the given templates, trial
    list, and expectedness answer from the JSON file data."""

    scene = copy.deepcopy(body_template)
    scene['isometric'] = True
    scene['ceilingMaterial'] = None
    scene['floorMaterial'] = FLOOR_OBJECT_MATERIAL[0]
    scene['wallMaterial'] = WALL_OBJECT_MATERIAL[0]

    scene['goal'] = copy.deepcopy(goal_template)
    scene['goal']['action_list'] = _create_action_list(trial_list)
    scene['goal']['habituation_total'] = len(trial_list) - 1
    scene['goal']['last_step'] = len(scene['goal']['action_list'])
    scene['goal']['answer'] = {
        'choice': EXPECTED if is_expected else UNEXPECTED
    }

    unit_size = _retrieve_unit_size(trial_list)
    wall_object_list = _create_wall_object_list(trial_list, unit_size)
    agent_object_list = _create_agent_object_list(
        trial_list,
        agent_object_config_list,
        unit_size
    )
    # Assume only one agent, and the agent will always start on the same spot.
    agent_start_bounds = agent_object_list[0]['shows'][0]['boundingBox']
    goal_object_list = _create_goal_object_list(
        trial_list,
        goal_object_config_list,
        agent_start_bounds,
        filename_prefix,
        unit_size
    )
    home_object = _create_home_object(trial_list, unit_size)
    target, non_target_list = _identify_target_object(
        trial_list,
        goal_object_list
    )

    _remove_intersecting_agent_steps(agent_object_list, goal_object_list)
    _remove_extraneous_agent_shows(agent_object_list)

    role_to_object_list = {}
    role_to_object_list[tags.ROLES.AGENT] = agent_object_list
    role_to_object_list[tags.ROLES.HOME] = [home_object]
    role_to_object_list[tags.ROLES.NON_TARGET] = non_target_list
    role_to_object_list[tags.ROLES.TARGET] = [target]
    role_to_object_list[tags.ROLES.WALL] = wall_object_list

    scene = hypercubes.update_scene_objects(scene, role_to_object_list)
    return scene


def _create_show(
    begin_frame: int,
    object_height: Tuple[float, float],
    object_size: Tuple[float, float],
    json_coords: Tuple[int, int],
    json_size: Tuple[int, int],
    unit_size: Tuple[float, float]
) -> Dict[str, Any]:
    """Create and return an MCS object's 'shows' element using the given
    data."""
    mcs_show = {
        'stepBegin': begin_frame,
        'position': {
            'x': GRID_MIN_X + (
                (json_coords[0] + (json_size[0] / 2)) * unit_size[0]
            ),
            'y': object_height[0],
            'z': GRID_MIN_Z + (
                (json_coords[1] + (json_size[1] / 2)) * unit_size[1]
            )
        },
        'scale': {
            'x': object_size[0],
            'y': object_height[1],
            'z': object_size[1]
        }
    }
    mcs_show['boundingBox'] = geometry.calc_obj_coords(
        mcs_show['position']['x'],
        mcs_show['position']['z'],
        mcs_show['scale']['x'] / 2.0,
        mcs_show['scale']['z'] / 2.0,
        0,
        0,
        0
    )
    return mcs_show


def _create_trial_frame_list(
    trial: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Return all the frames in the given trial that we want to keep in the
    final MCS scene using the agent's movement."""

    frame_list = []
    starting_coords = trial[0]['agent'][0]
    previous_coords = starting_coords
    starting_frame_count = STEP_WAIT_TIME
    ending_frame_count = STEP_WAIT_TIME - 1
    skip_next = False

    for frame in trial:
        # Keep or remove frames using the agent's movement.
        json_coords = frame['agent'][0]
        # Only keep a specific number of the trial's start frames.
        if json_coords == starting_coords:
            if starting_frame_count > 0:
                frame_list.append(frame)
                starting_frame_count -= 1
            continue
        # Only keep a specific number of the trial's end frames.
        if json_coords == previous_coords:
            if ending_frame_count > 0:
                frame_list.append(frame)
                ending_frame_count -= 1
            continue
        # Skip this frame if we used the previous frame.
        if skip_next:
            skip_next = False
            continue
        # Else keep this frame.
        frame_list.append(frame)
        previous_coords = json_coords
        skip_next = True

    return frame_list


def _create_wall_object_list(
    trial_list: List[List[Dict[str, Any]]],
    unit_size: Tuple[float, float]
) -> List[Dict[str, Any]]:
    """Create and return the MCS scene's wall object list using the given
    trial list from the JSON file data."""

    wall_object_list = []

    # Must save wall object references to find the removed wall, if any.
    wall_coords_to_object = {}

    # Retrieve the walls data from the first frame of the first trial.
    # Assume the walls will never change, except sometimes in the final
    # trial, in which case a wall may be removed.
    for json_wall in trial_list[0][0]['walls']:
        json_coords = json_wall[0]
        json_size = json_wall[1]

        # Ignore each part of border wall (we make it automatically).
        if (
            json_coords[0] == JSON_BORDER_WALL_MIN_X or
            json_coords[0] == JSON_BORDER_WALL_MAX_X or
            json_coords[1] == JSON_BORDER_WALL_MIN_Z or
            json_coords[1] == JSON_BORDER_WALL_MAX_Z
        ):
            continue

        # Create the MCS wall object.
        wall_object = _create_object(
            'wall_',
            'cube',
            WALL_OBJECT_MATERIAL,
            WALL_OBJECT_HEIGHT,
            WALL_OBJECT_SIZE,
            json_coords,
            json_size,
            unit_size
        )
        wall_object['kinematic'] = True
        wall_object['structure'] = True
        wall_object_list.append(wall_object)

        # Save the reference to this wall object for later use.
        wall_coords_to_object[
            str(json_coords[0]) + '_' + str(json_coords[1])
        ] = wall_object

    # Find and hide the removed wall in the final trial, if any.
    for json_wall in trial_list[-1][0]['walls']:
        json_coords = json_wall[0]
        wall_coords = str(json_coords[0]) + '_' + str(json_coords[1])
        if wall_coords in wall_coords_to_object:
            del wall_coords_to_object[wall_coords]
    if len(wall_coords_to_object.items()) > 0:
        hide_step = _identify_trial_index_starting_step(
            len(trial_list) - 1,
            trial_list
        )
        for wall_object in wall_coords_to_object.values():
            wall_object['hides'] = [{
                'stepBegin': hide_step
            }]

    return wall_object_list


def _identify_target_object(
    trial_list: List[List[Dict[str, Any]]],
    object_list: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    # TODO
    # return target, non_target_list
    return object_list[0], object_list[1:]


def _identify_trial_index_starting_step(
    index: int,
    trial_list: List[List[Dict[str, Any]]]
) -> int:
    """Return the MCS step at the start of the trial with the given
    index."""
    step = 0
    for prior_index in range(0, index):
        # Add 1 for the EndHabituation action step at the end of the trial.
        step += len(trial_list[prior_index]) + 1
    return step


def _remove_extraneous_agent_shows(
    agent_object_list: List[Dict[str, Any]]
) -> None:
    """Remove each agent object's 'shows' array element that is the same as its
    previous array element, since they aren't needed, and we can therefore
    reduce the size of the JSON output file."""
    for agent_object in agent_object_list:
        show_list = agent_object['shows'][:1]
        for show in agent_object['shows'][1:]:
            if (
                show['position']['x'] != show_list[-1]['position']['x'] or
                show['position']['z'] != show_list[-1]['position']['z']
            ):
                show_list.append(show)
        agent_object['shows'] = show_list


def _remove_intersecting_agent_steps(
    agent_object_list: List[Dict[str, Any]],
    goal_object_list: List[Dict[str, Any]]
) -> None:
    """Remove each agent object's step that intersects with any goal object's
    location at that step, since sometimes the agent moves a little too close
    to the goal object."""
    for agent_object in agent_object_list:
        remove_step_list = []
        for step, agent_bounds in enumerate(agent_object['boundsAtStep']):
            for goal_object in goal_object_list:
                goal_object_bounds = goal_object['boundsAtStep'][step]
                if sat_entry(agent_bounds, goal_object_bounds):
                    remove_step_list.append(step)
        agent_object['shows'] = [
            show for show in agent_object['shows']
            if show['stepBegin'] not in remove_step_list
        ]


def _retrieve_unit_size(
    trial_list: List[List[Dict[str, Any]]]
) -> Tuple[float, float]:
    """Return the unit size of this scene's grid."""
    # Assume the JSON grid size will never change.
    json_grid = trial_list[0][0]['size']
    grid_size_x = (GRID_MAX_X - GRID_MIN_X) / json_grid[0]
    grid_size_z = (GRID_MAX_Z - GRID_MIN_Z) / json_grid[1]
    return [grid_size_x, grid_size_z]


def convert_scene_pair(
    body_template: Dict[str, Any],
    goal_template: Dict[str, Any],
    trial_list_expected: List[List[Dict[str, Any]]],
    trial_list_unexpected: List[List[Dict[str, Any]]],
    filename_prefix: str,
    role_to_type: Dict[str, str],
    untrained: bool
) -> List[Dict[str, Any]]:
    """Create and return the pair of MCS scenes using the given templates
    and trial lists from the JSON file data."""

    # Create the converted trial lists for both of the scenes. This will
    # remove extraneous frames from all of the trials.
    converted_trial_list_expected = [
        _create_trial_frame_list(trial) for trial in trial_list_expected
    ]

    # Choose the shape and color of each object in a scene so we can use them
    # in both scenes across the pair so they will always have the same config.
    agent_object_config_list = _choose_config_list(
        converted_trial_list_expected,
        [
            config for config in AGENT_OBJECT_CONFIG_LIST
            if config.untrained == untrained
        ],
        [role_to_type[tags.ROLES.AGENT]],
        AGENT_OBJECT_MATERIAL_LIST,
        'agent'
    )
    goal_object_config_list = _choose_config_list(
        converted_trial_list_expected,
        [
            config for config in GOAL_OBJECT_CONFIG_LIST
            if config.untrained == untrained
        ],
        [role_to_type[tags.ROLES.TARGET], role_to_type[tags.ROLES.NON_TARGET]],
        GOAL_OBJECT_MATERIAL_LIST,
        'objects'
    )

    print('Generating expected MCS agent scene from JSON data')
    scene_expected = _create_scene(
        body_template,
        goal_template,
        agent_object_config_list,
        goal_object_config_list,
        converted_trial_list_expected,
        filename_prefix,
        is_expected=True
    )
    scenes = [scene_expected]

    # Training datasets will not have any unexpected scenes.
    if trial_list_unexpected:
        print('Generating unexpected MCS agent scene from JSON data')
        converted_trial_list_unexpected = [
            _create_trial_frame_list(trial) for trial in trial_list_unexpected
        ]
        scene_unexpected = _create_scene(
            body_template,
            goal_template,
            agent_object_config_list,
            goal_object_config_list,
            converted_trial_list_unexpected,
            filename_prefix,
            is_expected=False
        )
        scenes.append(scene_unexpected)

    return scenes
