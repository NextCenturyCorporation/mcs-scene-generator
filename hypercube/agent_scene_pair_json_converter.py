import copy
import logging
import math
import random
import uuid
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

import shapely
from machine_common_sense.config_manager import Goal, Vector3d

from generator import (
    MaterialTuple,
    ObjectBounds,
    Scene,
    SceneException,
    SceneObject,
    geometry,
    materials,
    structures,
    tags
)

from .hypercubes import update_scene_objects

logger = logging.getLogger(__name__)


class ObjectConfig():
    def __init__(
        self,
        object_type: str,
        scale_xz: float,
        scale_y: float,
        rotation_x: float = 0,
        rotation_y: float = 0,
        rotation_z: float = 0,
        untrained: bool = False,
    ) -> None:
        self.object_type = object_type
        self.scale_xz = scale_xz
        self.scale_y = scale_y
        self.rotation_x = rotation_x
        self.rotation_y = rotation_y
        self.rotation_z = rotation_z
        self.untrained = untrained


class AgentConfig(ObjectConfig):
    def __init__(
        self,
        object_type: str,
        scale: float,
        rotation_x: float = 0,
        rotation_y: float = 0,
        rotation_z: float = 0,
        untrained: bool = False
    ) -> None:
        super().__init__(
            object_type,
            scale,
            scale,
            rotation_x,
            rotation_y,
            rotation_z,
            untrained
        )


class ObjectDimensions():
    def __init__(
        self,
        object_type: str,
        x: float,
        y: float,
        z: float,
        center_y: float = None
    ) -> None:
        self.object_type = object_type
        self.x = x
        self.y = y
        self.z = z
        self.center_y = (y / 2.0) if center_y is None else center_y

    def get_dict(self, scale: dict) -> dict:
        return {
            'x': self.x * scale['x'],
            'y': self.y * scale['y'],
            'z': self.z * scale['z']
        }


class ObjectConfigWithMaterial(ObjectConfig):
    def __init__(
        self,
        config: ObjectConfig,
        material: Tuple[str, List[str]]
    ) -> None:
        super().__init__(
            config.object_type,
            config.scale_xz,
            config.scale_y,
            config.rotation_x,
            config.rotation_y,
            config.rotation_z,
            config.untrained
        )
        self.material = material


class TrueObjectBounds(ObjectBounds):
    """Subclass of ObjectBounds that correctly represents the polygons for
    circular and triangular shapes."""
    true_poly: shapely.geometry.Polygon = None

    def __init__(
        self,
        bounds: ObjectBounds,
        true_poly: shapely.geometry.Polygon
    ):
        super().__init__(
            box_xz=bounds.box_xz,
            max_y=bounds.max_y,
            min_y=bounds.min_y
        )
        self.true_poly = true_poly

    def get_true_poly_points(self) -> List[Vector3d]:
        return [
            Vector3d(x=point[0], y=0, z=point[1]) for point in
            self.true_poly.exterior.coords
        ]


# Debug logging
SAVE_TRIALS_TO_FILE = False
TRIALS_SUFFIX = '_trials.txt'

EXPECTED = 'expected'
UNEXPECTED = 'unexpected'

# Use a 10x10 grid, with each cell 0.5 x 0.5, including the border wall.
GRID_MIN_X = -2.5
GRID_MAX_X = 2.5
GRID_MIN_Z = -2.5
GRID_MAX_Z = 2.5
MAX_DISTANCE = math.dist([GRID_MIN_X, GRID_MIN_Z], [GRID_MAX_X, GRID_MAX_Z])

JSON_BORDER_WALL_MIN_X = 0
JSON_BORDER_WALL_MIN_Z = 0
JSON_BORDER_WALL_MAX_X = 180
JSON_BORDER_WALL_MAX_Z = 180

# Grid used for positioning occluders in training scenes with occluders.
GRID = []
for x in range(0, int(GRID_MAX_X - GRID_MIN_X) * 10 + 1):
    for z in range(0, int(GRID_MAX_Z - GRID_MIN_Z) * 10 + 1):
        # Exclude area for the static border wall.
        if 5 < x < 40 and 5 < z < 40:
            GRID.append((round(x / 10.0, 1), round(z / 10.0, 1)))

# The wait time in steps before and after the agent's movement in each trial.
STARTING_STEP_WAIT_TIME = 3
PAUSED_STEP_WAIT_TIME = 2
DEFUSE_STEP_SKIP_TIME = 5
POST_DEFUSE_WAIT_TIME = 5

OBJECT_DIMENSIONS = {
    'blob_01': ObjectDimensions('blob_01', 0.26, 0.8, 0.3),
    'blob_02': ObjectDimensions('blob_02', 0.33, 0.78, 0.33),
    'blob_03': ObjectDimensions('blob_03', 0.25, 0.69, 0.25),
    'blob_04': ObjectDimensions('blob_04', 0.3, 0.53, 0.29, 0.225),
    'blob_05': ObjectDimensions('blob_05', 0.38, 0.56, 0.38, 0.24),
    'blob_06': ObjectDimensions('blob_06', 0.5, 0.5, 0.52),
    'blob_07': ObjectDimensions('blob_07', 0.25, 0.55, 0.25, 0.245),
    'blob_08': ObjectDimensions('blob_08', 0.24, 0.62, 0.15),
    'blob_09': ObjectDimensions('blob_09', 0.33, 0.78, 0.38),
    'blob_10': ObjectDimensions('blob_10', 0.24, 0.5, 0.24),
    'blob_11': ObjectDimensions('blob_11', 0.35, 0.58, 0.35),
    'blob_12': ObjectDimensions('blob_12', 0.3, 0.48, 0.3),
    'circle_frustum_with_base': ObjectDimensions(
        'circle_frustum_with_base', 1, 2, 1),
    'cone_with_base': ObjectDimensions('cone_with_base', 1, 2, 1),
    'cube': ObjectDimensions('cube', 1, 1, 1),
    'cube_hollow_narrow': ObjectDimensions('cube_hollow_narrow', 1, 1, 1, 0),
    'cube_hollow_wide': ObjectDimensions('cube_hollow_wide', 1, 1, 1, 0),
    'cylinder': ObjectDimensions('cylinder', 1, 2, 1),
    'hash': ObjectDimensions('hash', 1, 1, 1, 0),
    'letter_x': ObjectDimensions('letter_x', 1, 1, 1, 0),
    'lock_wall': ObjectDimensions('lock_wall', 1, 1, 1),
    'pyramid_with_base': ObjectDimensions('pyramid_with_base', 1, 2, 1),
    'semi_sphere_with_base': ObjectDimensions(
        'semi_sphere_with_base', 1, 2, 1),
    'sphere': ObjectDimensions('sphere', 1, 1, 1),
    'square_frustum_with_base': ObjectDimensions(
        'square_frustum_with_base', 1, 2, 1),
    'triangle': ObjectDimensions('triangle', 1, 1, 1),
    'tube_narrow': ObjectDimensions('tube_narrow', 1, 1, 1),
    'tube_wide': ObjectDimensions('tube_wide', 1, 1, 1),
}

ROUND_TYPES = [
    'blob_01', 'blob_02', 'blob_03', 'blob_04', 'blob_05', 'blob_06',
    'blob_07', 'blob_08', 'blob_09', 'blob_10', 'blob_11', 'blob_12',
    'circle_frustum', 'circle_frustum_with_base', 'cone', 'cone_with_base',
    'cylinder', 'semi_sphere', 'semi_sphere_with_base', 'sphere',
    'tube_narrow', 'tube_wide'
]

AGENT_OBJECT_CONFIG_LIST = [
    # Scaled to ensure that each agent's max X/Z dimension is 1.
    # Remove the C-shaped and S-shaped blobs for now.
    # AgentConfig('blob_01', 3.33),
    AgentConfig('blob_02', 3.03),
    AgentConfig('blob_03', 4),
    AgentConfig('blob_04', 3.33),
    AgentConfig('blob_05', 2.63),
    # AgentConfig('blob_06', 1.92),
    AgentConfig('blob_07', 4),
    # AgentConfig('blob_08', 4.16),
    # AgentConfig('blob_09', 2.63),
    AgentConfig('blob_10', 4.16),
    AgentConfig('blob_11', 2.85),
    AgentConfig('blob_12', 3.33),
]
AGENT_OBJECT_MATERIAL_LIST = [
    [materials.BLUE],
    [materials.GOLDENROD],
    [materials.GREEN],
    [materials.PURPLE]
]

GOAL_OBJECT_CONFIG_LIST = [
    # Scaled to ensure that each object's max X/Z dimension is 1
    ObjectConfig('circle_frustum_with_base', 1, 0.5),
    ObjectConfig('cone_with_base', 1, 0.5),
    ObjectConfig('cube', 0.707, 1, rotation_y=45),
    ObjectConfig('cube_hollow_narrow', 0.707, 1, rotation_y=45),
    ObjectConfig('cylinder', 1, 0.5),
    # TODO MCS-1614 Replace these types with square or cylindrical versions.
    # ObjectConfig('hash', 1, 1),
    # ObjectConfig('letter_x', 1, 1),
    ObjectConfig('pyramid_with_base', 0.707, 0.5, rotation_y=45),
    ObjectConfig('semi_sphere_with_base', 1, 0.5),
    ObjectConfig('sphere', 1, 1),
    ObjectConfig('square_frustum_with_base', 0.707, 0.5, rotation_y=45),
    ObjectConfig('tube_narrow', 1, 1)
]
GOAL_OBJECT_HIGHLIGHT_MATERIAL = materials.RED.material
GOAL_OBJECT_MATERIAL_LIST_BLUES = [
    materials.AZURE,
    materials.NAVY,
    materials.TEAL
]
GOAL_OBJECT_MATERIAL_LIST_GREENS = [
    materials.CHARTREUSE,
    materials.OLIVE,
    materials.SPRINGGREEN
]
GOAL_OBJECT_MATERIAL_LIST_PURPLES = [
    materials.INDIGO,
    materials.ROSE,
    materials.VIOLET
]
GOAL_OBJECT_MATERIAL_LIST_YELLOWS = [
    materials.BROWN,
    materials.ORANGE,
    materials.YELLOW
]

# Make the home object as short as possible, without it looking weird in Unity.
HOME_OBJECT_HEIGHT = [0.01, 0.02]
HOME_OBJECT_MATERIAL = materials.MAGENTA
HOME_OBJECT_SIZE = [0.5, 0.5]

WALL_OBJECT_HEIGHT = [0.0625, 0.125]
WALL_OBJECT_MATERIAL = materials.BLACK
WALL_OBJECT_SIZE = 0.5

FUSE_WALL_OBJECT_HEIGHT = [0.05, 0.1]
FUSE_WALL_OBJECT_MATERIAL = materials.LIME
FUSE_WALL_OBJECT_SIZE = [0.495, 0.495]

KEY_OBJECT_HEIGHT = [FUSE_WALL_OBJECT_HEIGHT[0], 0.35]
KEY_OBJECT_MATERIAL = materials.MAROON
KEY_OBJECT_SIZE = [FUSE_WALL_OBJECT_HEIGHT[1], 0.35]
KEY_OBJECT_TYPE = 'triangle'
KEY_OBJECT_ROTATION_X = 0
KEY_OBJECT_ROTATION_Y = {
    'positive_z': {
        'dimensions_x': 0.5,
        'dimensions_z': 0.25,
        'position_x': 0,
        'position_z': -0.25,
        'rotation_y': -45
    },
    'negative_z': {
        'dimensions_x': 0.5,
        'dimensions_z': 0.25,
        'position_x': 0,
        'position_z': 0.25,
        'rotation_y': 135
    },
    'positive_x': {
        'dimensions_x': 0.25,
        'dimensions_z': 0.5,
        'position_x': -0.25,
        'position_z': 0,
        'rotation_y': 45
    },
    'negative_x': {
        'dimensions_x': 0.25,
        'dimensions_z': 0.5,
        'position_x': 0.25,
        'position_z': 0,
        'rotation_y': -135
    }
}
KEY_OBJECT_ROTATION_Z = 90

LOCK_WALL_OBJECT_HEIGHT = FUSE_WALL_OBJECT_HEIGHT
LOCK_WALL_OBJECT_MATERIAL = FUSE_WALL_OBJECT_MATERIAL
LOCK_WALL_OBJECT_SIZE = FUSE_WALL_OBJECT_SIZE

OCCLUDER_OBJECT_HEIGHT_HELPER_HINDERER = [0.25, 0.5]
OCCLUDER_OBJECT_HEIGHT_TRUE_FALSE_BELIEF = [0.5, 1.0]
OCCLUDER_OBJECT_JSON_COORDS = [-35, 21]
OCCLUDER_OBJECT_MATERIAL = materials.WHITE
OCCLUDER_OBJECT_MATERIAL_HELPER_HINDERER = materials.CYAN
OCCLUDER_OBJECT_SIZE_NONAGENT = [0.25, 1.05]
OCCLUDER_OBJECT_SIZE_HELPER_HINDERER = [0.5, 1.0]
OCCLUDER_OBJECT_SIZE_TRUE_FALSE_BELIEF = [0.25, 0.85]
OCCLUDER_OBJECT_TYPE = 'cube'

PADDLE_OBJECT_HEIGHT = [0.25, 0.5]
PADDLE_OBJECT_MATERIAL = materials.BLACK
PADDLE_OBJECT_SIZE = [0.25, 1]
PADDLE_OBJECT_TYPE = 'cube'

# The floor and room walls should have bland colors and simple textures.
CEILING_MATERIAL = MaterialTuple("AI2-THOR/Materials/Walls/Drywall", ["white"])
FLOOR_OR_WALL_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Ceramics/BrownMarbleFake 1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/ConcreteBoards1", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/ConcreteFloor", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/GREYGRANITE", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/WhiteCountertop", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Wood/BedroomFloor1", ["brown"]),
    # Mark some brown textures as also orange because they look very similar.
    MaterialTuple("AI2-THOR/Materials/Wood/LightWoodCounters 1",
                  ["brown", "orange"]),
    MaterialTuple("AI2-THOR/Materials/Wood/LightWoodCounters3",
                  ["brown", "orange"]),
    MaterialTuple("AI2-THOR/Materials/Wood/LightWoodCounters4",
                  ["brown", "orange"]),
    MaterialTuple(
        "AI2-THOR/Materials/Wood/TexturesCom_WoodFine0050_1_seamless_S",
        ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WhiteWood", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WoodFloorsCross",
                  ["brown", "orange"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WoodGrain_Brown", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WoodGrain_Tan", ["brown"]),
    MaterialTuple("UnityAssetStore/Baby_Room/Models/Materials/wood 1",
                  ["brown"])
]
FLOOR_MATERIALS = FLOOR_OR_WALL_MATERIALS + [
    MaterialTuple("AI2-THOR/Materials/Fabrics/Carpet2", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetWhite", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetWhite 3", ["white"])
]
WALL_MATERIALS = FLOOR_OR_WALL_MATERIALS + [
    MaterialTuple("AI2-THOR/Materials/Walls/Drywall", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Walls/DrywallBeige", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Walls/Drywall4Tiled", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Walls/WallDrywallGrey", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Walls/YellowDrywall", ["yellow"])
]


class OccluderMode(Enum):
    HELPER_HINDERER = auto()
    NONAGENT_EVAL = auto()
    NONAGENT_TRAINING = auto()
    NONE = auto()
    TRUE_FALSE_BELIEF = auto()


EVAL_7_TASKS = [OccluderMode.HELPER_HINDERER, OccluderMode.TRUE_FALSE_BELIEF]


def _append_each_show_to_object(
    mcs_object: SceneObject,
    trial: List[Dict[str, Any]],
    trial_start_step: int,
    json_property: str,
    unit_size: Tuple[float, float],
    on_step_callback: Callable = None,
    rotation_y: int = 0,
    json_index: int = 0
) -> SceneObject:
    """Append a "shows" array element to the given moving object for each step
    in the given trial list."""

    latest_bounds = None

    # Add data for the object's movement across the frames to each step.
    step = trial_start_step
    for frame_index, frame in enumerate(trial):
        invoke_callback = False
        json_object = frame.get(json_property)
        # (Sometimes the key is not in some trials.)
        if json_object:
            json_object = json_object if json_property in [
                'agent', 'door', 'other_agent', 'paddle'
            ] else json_object[json_index]
            json_coords = json_object[0]
            if json_property == 'paddle':
                # The json_size isn't needed because the paddle's coordinates
                # are already centered.
                json_size = [0, 0]
                json_rotation = 360 - json_object[2]
            elif json_property == 'door':
                json_size = [20, 40]
                json_rotation = 0
            else:
                json_radius = json_object[1]
                json_size = [json_radius * 2, json_radius * 2]
                json_rotation = rotation_y
            # Move the object to its new position for the step...
            mcs_show = _create_show(
                step,
                mcs_object['type'],
                mcs_object['debug']['configHeight'],
                mcs_object['debug']['configSize'],
                json_coords,
                json_size,
                unit_size,
                json_rotation
            )
            latest_bounds = mcs_show['boundingBox']
            # ...But only if it actually has a new position/rotation.
            if (
                not mcs_object['shows'] or
                mcs_show['position'] != mcs_object['shows'][-1]['position'] or
                mcs_show['rotation'] != mcs_object['shows'][-1]['rotation']
            ):
                mcs_object['shows'].append(mcs_show)
                invoke_callback = True

        # If this object has appeared in this trial, update its bounds for the
        # step (overwriting any existing bounds); otherwise, just add None.
        if latest_bounds:
            if step < len(mcs_object['debug']['boundsAtStep']):
                mcs_object['debug']['boundsAtStep'][step] = latest_bounds
            else:
                mcs_object['debug']['boundsAtStep'].append(latest_bounds)
        else:
            mcs_object['debug']['boundsAtStep'].append(None)

        # If this object moved on this specific step, invoke the callback func.
        if invoke_callback and on_step_callback:
            mcs_object = on_step_callback(
                trial_start_step,
                json_object,
                mcs_object
            )

        step += 1

    # Add 1 for the EndHabituation action step at the end of the trial.
    step += 1
    mcs_object['debug']['boundsAtStep'].append(
        mcs_object['shows'][-1]['boundingBox']
    )

    # Remove the scale from each element in 'shows' except for the first, or
    # it will really mess up the simulation.
    for show in mcs_object['shows'][1:]:
        if 'scale' in show:
            del show['scale']

    return mcs_object


def _choose_config_list(
    trial_list: List[List[Dict[str, Any]]],
    config_list: List[Dict[str, Any]],
    object_type_list: List[str],
    material_list: List[List[MaterialTuple]],
    json_property: str
) -> List[ObjectConfigWithMaterial]:
    """Choose and return the shape and color of each object in the scene to use
    in both scenes across the pair so they always have the same config."""

    object_config_list = []

    # Minimum of 2 agent configs, for unexpected multiple agents scenes.
    object_count = 2 if json_property == 'agent' else 0
    # Retrieve the relevant object list from the first frame of each trial.
    # Use all trials since objects are sometimes added after the first trial.
    # Assume objects will never change shape/color across trials/frames.
    for trial in trial_list:
        json_objects = trial[0].get(json_property, [])
        if json_property == 'agent':
            other_agent = trial[0].get('other_agent')
            json_objects = (
                [json_objects] + trial[0].get('other_agents', []) +
                ([other_agent] if other_agent else [])
            )
        object_count = max(object_count, len(json_objects))
    logger.info(f'Found {object_count} {json_property} in the JSON')

    if json_property == 'agent':
        # Remove agent objects with pointy tops (e.g. cones, pyramids) from
        # scenes with keys (e.g. instrumental action) as requested by NYU.
        # Old prop: 'key' ... New prop: 'pin'
        if trial_list[0][0].get('pin', trial_list[0][0].get('key')):
            config_list = [config for config in config_list if (
                config.object_type != 'cone' and
                config.object_type != 'pyramid'
            )]

    used_type_list = []
    used_material_list = []

    # Randomly choose each object's shape and color config.
    for index in range(object_count):
        # Filter on type specified via command line argument.
        filtered_config_list = [
            config for config in config_list
            if config.object_type == object_type_list[index]
        ] if object_type_list[index] else config_list

        # Fall back on the original list.
        if not filtered_config_list:
            filtered_config_list = config_list

        # Filter out used types.
        filtered_config_list = [
            config for config in filtered_config_list
            if config.object_type not in used_type_list
        ]

        # If the first goal object is a round shape, then the second goal
        # object should not also be a round shape, and visa-versa.
        if json_property == 'objects':
            if len(used_type_list) == 1:
                filtered_config_list = [
                    config for config in filtered_config_list if (
                        (config.object_type in ROUND_TYPES) !=
                        (used_type_list[0] in ROUND_TYPES)
                    )
                ]

        if not filtered_config_list:
            raise SceneException(
                f'No more available {json_property} types: {used_type_list=}'
            )

        # Filter out used materials and colors.
        filtered_material_list = []
        for nested_material_list in material_list:
            is_used = False
            for used_material in used_material_list:
                if used_material in nested_material_list:
                    is_used = True
                    break
            if not is_used:
                filtered_material_list.append(nested_material_list)
        if not filtered_material_list:
            raise SceneException(
                f'No more available {json_property} materials: '
                f'{used_material_list=}'
            )

        chosen_config = random.choice(filtered_config_list)

        # Choose a random Y rotation for each agent.
        if json_property == 'agent':
            chosen_config.rotation_y = random.choice([0, 90, 180, 270])

        # Choose a random object config (type/size) and material.
        config_with_material = ObjectConfigWithMaterial(
            chosen_config,
            random.choice(random.choice(filtered_material_list))
        )
        object_config_list.append(config_with_material)

        # Add the chosen type and material to the "used" lists.
        used_type_list.append(config_with_material.object_type)
        used_material_list.append(config_with_material.material)

    return object_config_list


def _create_action_list(
    trial_list: List[List[Dict[str, Any]]]
) -> List[List[str]]:
    """Create and return the MCS scene's action list using the given trial
    list from the JSON file data."""
    action_list = []
    for index in range(0, len(trial_list)):
        # Add 1 for the EndHabituation action step at the end of the trial.
        total_steps = len(trial_list[index]) + 1
        action_list.extend([['Pass']] * (total_steps - 1))
        action_list.append(['EndHabituation'])
    # Remove the EndHabituation action from the last test trial.
    return action_list[:-1]


def _create_agent_object_list(
    trial_list: List[List[Dict[str, Any]]],
    agent_object_config_list: List[ObjectConfigWithMaterial],
    unit_size: Tuple[float, float]
) -> List[SceneObject]:
    """Create and return the MCS scene's agent object list using the given
    trial list from the JSON file data."""

    agent_object_list = []
    mcs_agents_unique = {}

    # Retrieve the agent data for each trial from the trial's first frame.
    # Assume each agent will never change shape/color.
    json_agents_unique = {}
    for trial_index, trial in enumerate(trial_list):
        for json_property in ['agent', 'other_agent', 'other_agents']:
            # The agent doesn't always appear in the first frame in some tasks.
            for frame in trial:
                json_agents = frame.get(json_property, [])
                if json_agents:
                    break
            # Assume a single 'agent' or 'other_agent' per trial.
            # Assume multiple 'other_agents' per trial.
            if json_property in ['agent', 'other_agent']:
                json_agents = [json_agents] if json_agents else []
            for agent_index, json_agent in enumerate(json_agents):
                json_icon = json_agent[2]
                if not json_icon:
                    raise Exception(
                        f'Missing agent icon {trial_index=} frame_index=0: '
                        f'{json_agent}'
                    )
                if json_icon not in json_agents_unique:
                    json_agents_unique[json_icon] = (json_agent, json_property)

    # Create each unique agent using its corresponding data from the JSON file.
    for index, json_icon in enumerate(list(json_agents_unique.keys())):
        json_agent, json_property = json_agents_unique[json_icon]
        json_coords = json_agent[0]
        json_radius = json_agent[1]
        json_size = [json_radius * 2, json_radius * 2]

        # Create the MCS agent object.
        config_with_material = agent_object_config_list[index]
        dimensions = OBJECT_DIMENSIONS[config_with_material.object_type]
        # Multiply the agent's scale based on its JSON radius and unit size.
        factor = json_radius * 2 * min(unit_size[0], unit_size[1])
        scale_xz = config_with_material.scale_xz * factor
        scale_y = config_with_material.scale_y * factor
        center_y = dimensions.center_y * config_with_material.scale_y * factor
        agent_object = _create_object(
            f'{json_property}_',
            config_with_material.object_type,
            config_with_material.material,
            [center_y, scale_y],
            [scale_xz, scale_xz],
            json_coords,
            json_size,
            unit_size,
            rotation_y=config_with_material.rotation_y
        )
        agent_object['hides'] = []
        # Set kinematic to avoid awkward shifting due to collision issues.
        agent_object['kinematic'] = True
        # Set physics so this agent's info is returned in the oracle metadata.
        agent_object['physics'] = True
        agent_object['debug'][
            tags.SCENE.UNTRAINED_SHAPE
        ] = config_with_material.untrained
        agent_object['debug']['trialToSteps'] = {}

        # Remove the object's first appearance (we will override it later).
        agent_object['shows'] = []
        agent_object['debug']['boundsAtStep'] = []

        # Save the agent in this function's output list.
        agent_object_list.append(agent_object)

        # Link the agent and its icon so we can update its movement across each
        # frame in the next code block.
        mcs_agents_unique[json_icon] = agent_object

    # Update each MCS agent object with its movement in each trials' frames.
    for trial_index, trial in enumerate(trial_list):
        step = _identify_trial_index_starting_step(trial_index, trial_list)
        last_step = step + len(trial)
        found_in_trial = {}
        for json_property in ['agent', 'other_agent', 'other_agents']:
            found_on_frame = 0
            # The agent doesn't always appear in the first frame in some tasks.
            for frame_index, frame in enumerate(trial):
                json_agents = frame.get(json_property, [])
                if json_agents:
                    found_on_frame = frame_index
                    break
            if json_property in ['agent', 'other_agent']:
                json_agents = [json_agents] if json_agents else []
            for agent_index, trial_json_agent in enumerate(json_agents):
                trial_json_icon = trial_json_agent[2]
                if not trial_json_icon:
                    raise Exception(
                        f'Missing agent icon {trial_index=} frame_index=0: '
                        f'{json_agent}'
                    )
                found_in_trial[trial_json_icon] = found_on_frame
                for json_icon, mcs_agent in mcs_agents_unique.items():
                    if json_icon == trial_json_icon:
                        # If the current agent is in this trial, then update
                        # its movement.
                        _append_each_show_to_object(
                            mcs_agent,
                            trial,
                            step,
                            json_property,
                            unit_size,
                            rotation_y=mcs_agent['debug']['configRotation'],
                            json_index=agent_index
                        )
        for json_icon, mcs_agent in mcs_agents_unique.items():
            mcs_agent['debug']['trialToSteps'][trial_index] = (step, last_step)
            # Skip if the agent was found in this trial on frame 0.
            if found_in_trial.get(json_icon) == 0:
                continue
            hide_until_frame = found_in_trial.get(json_icon, len(trial) + 1)
            # Else, hide the current agent during this trial.
            mcs_agent['hides'].append({
                'stepBegin': step
            })
            for _ in range(hide_until_frame):
                mcs_agent['debug']['boundsAtStep'].append(None)

    return agent_object_list


def _create_fuse_wall_object_list(
    trial_list: List[List[Dict[str, Any]]],
    unit_size: Tuple[float, float]
) -> List[SceneObject]:
    """Create and return the MCS scene's green fuse wall object list (used in
    the instrumental action scenes) using the given trial list from the JSON
    file data."""

    fuse_wall_object_list = []

    # Retrieve the complete fuse walls data from each frame of each trial.
    # Assume each trial will have new fuse walls, and all of the fuse walls in
    # a trial will be hidden on a specific frame.
    for trial_index, trial in enumerate(trial_list):
        # Identify the step on which this trial starts.
        step = _identify_trial_index_starting_step(trial_index, trial_list)

        # Must save object references to find removed walls.
        original_coords_to_object = {}

        # Generate the list of fuse walls used in this trial.
        for json_wall in trial[0].get('fuse_walls', []):
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
                'fuse_wall_',
                'cube',
                FUSE_WALL_OBJECT_MATERIAL,
                FUSE_WALL_OBJECT_HEIGHT,
                FUSE_WALL_OBJECT_SIZE,
                json_coords,
                json_size,
                unit_size
            )
            wall_object['kinematic'] = True
            wall_object['structure'] = True

            # Adjust the show step to sync with the trial step.
            wall_object['shows'][0]['stepBegin'] = step

            # Don't add duplicate walls.
            coords_property = str(json_coords[0]) + '_' + str(json_coords[1])
            if coords_property not in original_coords_to_object:
                fuse_wall_object_list.append(wall_object)
                # Save the reference to this wall object for later use.
                original_coords_to_object[coords_property] = wall_object

        for frame_index, frame in enumerate(trial):
            existing_coords = {}
            # Identify the fuse walls that still exist in this frame.
            for json_wall in frame.get('fuse_walls', []):
                json_coords = json_wall[0]
                existing_coords[
                    str(json_coords[0]) + '_' + str(json_coords[1])
                ] = True
            # Remove the fuse walls that don't exist in this frame.
            for coords, wall_object in original_coords_to_object.items():
                if (
                    coords not in existing_coords and
                    'hides' not in wall_object
                ):
                    wall_object['hides'] = [{
                        'stepBegin': step + frame_index
                    }]

    return fuse_wall_object_list


def _create_goal_object_list(
    trial_list: List[List[Dict[str, Any]]],
    goal_object_config_list: List[ObjectConfigWithMaterial],
    agent_start_bounds: ObjectBounds,
    filename_prefix: str,
    unit_size: Tuple[float, float]
) -> List[SceneObject]:
    """Create and return the MCS scene's goal object list using the given
    trial list from the JSON file data."""

    goal_object_list = []
    icons_to_objects = {}
    step = 0
    object_index = 0

    # Retrieve the object data for each trial using the trial's first frame.
    # Use all trials since objects are sometimes added after the first trial.
    # Assume each object will never change shape/color.
    for trial_index, trial in enumerate(trial_list):
        icons_this_trial = {}
        for json_object in trial[0].get('objects', []):
            json_coords = json_object[0]
            json_radius = json_object[1]
            json_icon = json_object[2]
            json_size = [json_radius * 2, json_radius * 2]
            icons_this_trial[json_icon] = True

            # Use the previously made MCS goal object, or create a new one.
            goal_object = icons_to_objects.get(json_icon)
            already_existed = (goal_object is not None)
            if not already_existed:
                config_with_material = goal_object_config_list[object_index]
                object_index += 1
                dimensions = OBJECT_DIMENSIONS[
                    config_with_material.object_type
                ]
                # Multiply the object's scale by JSON radius and unit size.
                factor = json_radius * 2 * min(unit_size[0], unit_size[1])
                scale_xz = config_with_material.scale_xz * factor
                scale_y = config_with_material.scale_y * factor
                center_y = (
                    dimensions.center_y * config_with_material.scale_y * factor
                )
                # Initialize the goal object.
                goal_object = _create_object(
                    'object_',
                    config_with_material.object_type,
                    config_with_material.material,
                    [center_y, scale_y],
                    [scale_xz, scale_xz],
                    json_coords,
                    json_size,
                    unit_size,
                    rotation_y=config_with_material.rotation_y
                )
                # The goal object should appear on this step.
                goal_object['shows'][0]['stepBegin'] = step
                # Set kinematic to avoid awkward shifting on collision.
                goal_object['kinematic'] = True
                # Set physics so object's info is returned in oracle metadata.
                goal_object['physics'] = True
                # Initialize other important properties.
                goal_object['changeMaterials'] = []
                goal_object['hides'] = []
                goal_object['debug']['agentTouches'] = {}
                for index in range(0, len(trial_list)):
                    goal_object['debug']['agentTouches'][index] = []
                for _ in range(0, step):
                    goal_object['debug']['boundsAtStep'].insert(0, None)
                goal_object['debug'][
                    tags.SCENE.UNTRAINED_SHAPE
                ] = config_with_material.untrained
                # Save the goal object.
                goal_object_list.append(goal_object)
                icons_to_objects[json_icon] = goal_object

            # If needed, add the object's new position in this trial.
            # Assume objects only change in position across trials, not frames.
            if already_existed:
                goal_object['shows'].append(_create_show(
                    step,
                    goal_object['type'],
                    goal_object['debug']['configHeight'],
                    goal_object['debug']['configSize'],
                    json_coords,
                    json_size,
                    unit_size,
                    rotation_y=goal_object['debug']['configRotation']
                ))

            # Add the object's bounds for each frame of the trial.
            for _ in range(0, len(trial) + (1 if already_existed else 0)):
                goal_object['debug']['boundsAtStep'].append(
                    goal_object['shows'][-1]['boundingBox']
                )

            # Mark each time the object's color changes to signal an agent
            # touches an object. We will change the object's color elsewhere.
            previous_color = json_object[3]
            for future_step, future_frame in enumerate(trial):
                if future_step == 0:
                    continue
                for future_object in future_frame.get('objects', []):
                    if future_object[2] != json_icon:
                        continue
                    if future_object[3] != previous_color:
                        previous_color = future_object[3]
                        agent_touches = goal_object['debug']['agentTouches']
                        agent_touches[trial_index].append(step + future_step)
                    break

        for icon, goal_object in icons_to_objects.items():
            if icon in icons_this_trial:
                continue
            goal_object['hides'].append({
                'stepBegin': step
            })
            for _ in range(0, len(trial) + 1):
                goal_object['debug']['boundsAtStep'].append(None)

        # Add 1 for the EndHabituation action step at the end of the trial.
        step += len(trial) + 1

    for goal_object in goal_object_list:
        for index, show in enumerate(goal_object['shows']):
            # We can't have the object's position on top of the agent's start
            # position or the agent and object will collide. This can happen
            # if the 2D icons overlap themselves in the original data.
            # (Only bother checking if a "home" is in the scene.)
            if agent_start_bounds and _do_objects_overlap(
                agent_start_bounds,
                show['boundingBox'],
                show['stepBegin']
            ):
                raise SceneException(
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
) -> SceneObject:
    """Create and return the MCS scene's home object using the given trial
    list from the JSON file data."""

    # Retrieve the home data from the first frame of the first trial.
    # Assume only one home and the home will never change.
    json_home = trial_list[0][0].get('home')
    if not json_home:
        return None
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


def _create_key_object(
    trial_list: List[List[Dict[str, Any]]],
    unit_size: Tuple[float, float],
    agent_object_list: List[SceneObject]
) -> Optional[SceneObject]:
    """Create and return the MCS scene's key object using the given trial
    list from the JSON file data."""

    # Retrieve the key data from the first frame of the first trial.
    # Assume the number of keys will never change, and the keys will
    # never change shape/color.
    # Old prop: 'key' ... New prop: 'pin'
    json_key_list = trial_list[0][0].get('pin', trial_list[0][0].get('key'))
    if not json_key_list:
        return None
    json_key = json_key_list[0]
    json_coords = json_key[0]
    json_radius = json_key[1]
    json_size = [json_radius * 2, json_radius * 2]

    # Create the MCS key object.
    key_object = _create_object(
        'key_',
        KEY_OBJECT_TYPE,
        KEY_OBJECT_MATERIAL,
        KEY_OBJECT_HEIGHT,
        KEY_OBJECT_SIZE,
        json_coords,
        json_size,
        unit_size
    )

    # Remove the object's first appearance (we will override it later).
    key_object['shows'] = []
    key_object['debug']['boundsAtStep'] = []

    def _callback(
        trial_start_step: int,
        json_key: Dict[str, Any],
        key_object: SceneObject
    ) -> SceneObject:
        _fix_key_triangle_rotation(trial_start_step, json_key, key_object)
        _fix_held_object_positions(
            trial_start_step,
            key_object,
            agent_object_list
        )
        return key_object

    # Move the key on each step as needed.
    for trial_index, trial in enumerate(trial_list):
        _append_each_show_to_object(
            key_object,
            trial,
            _identify_trial_index_starting_step(trial_index, trial_list),
            # Old prop: 'key' ... New prop: 'pin'
            'pin' if 'pin' in trial[0] else 'key',
            unit_size,
            _callback
        )

    # Override the key object with its correct scale.
    key_object['shows'][0]['scale'] = {
        'x': KEY_OBJECT_SIZE[0],
        'y': KEY_OBJECT_HEIGHT[1],
        'z': KEY_OBJECT_SIZE[1]
    }

    # In Eval 4, the key object had structure=True, but that was a bug, and has
    # been fixed for Eval 5 and beyond.

    # Set kinematic to avoid awkward shifting due to collision issues.
    key_object['kinematic'] = True
    # Set physics so this object's info is returned in the oracle metadata.
    key_object['physics'] = True

    key_object['hides'] = []

    return key_object


def _create_lock_wall_object_list(
    trial_list: List[List[Dict[str, Any]]],
    key_object: SceneObject,
    unit_size: Tuple[float, float]
) -> SceneObject:
    """Create and return the MCS scene's green lock wall object list (used in
    the instrumental action scenes) using the given trial list from the JSON
    file data."""

    lock_wall_object_list = []

    prop_is_lock = False

    # Retrieve the complete lock wall data from each frame of each trial.
    # Assume each trial will have a new lock wall, and the lock wall will be
    # hidden on a specific frame.
    for trial_index, trial in enumerate(trial_list):
        # Identify the step on which this trial starts.
        step = _identify_trial_index_starting_step(trial_index, trial_list)

        # Generate the lock wall used in this trial. Assume only one exists.
        # Old prop: 'lock' ... New prop: 'key'
        # Look for 'lock' FIRST, else it may try to use the old 'key' property.
        json_lock_list = trial[0].get('lock', trial[0].get('key'))
        if json_lock_list:
            prop_is_lock = ('lock' in trial[0])
            json_lock = json_lock_list[0]
            json_coords = json_lock[0]
            json_radius = json_lock[1]
            json_icon = json_lock[2]
            json_size = [json_radius * 2, json_radius * 2]

            # Create the MCS lock wall object.
            lock_object = _create_object(
                'lock_',
                'lock_wall',
                LOCK_WALL_OBJECT_MATERIAL,
                LOCK_WALL_OBJECT_HEIGHT,
                LOCK_WALL_OBJECT_SIZE,
                json_coords,
                json_size,
                unit_size
            )
            lock_object['kinematic'] = True
            lock_object['structure'] = True

            # Rotate the lock based on the JSON icon.
            rotation_y = 0
            if json_icon.endswith('slot90.png'):
                pass
            elif json_icon.endswith('slot180.png'):
                rotation_y = 270
            elif json_icon.endswith('slot270.png'):
                rotation_y = 180
            elif json_icon.endswith('slot0.png'):
                rotation_y = 90
            else:
                raise SceneException(
                    f'Lock is unexpected icon: {json_icon}'
                )
            lock_object['shows'][0]['rotation'] = {
                'x': 0,
                'y': rotation_y,
                'z': 0
            }
            lock_object['debug']['boundsAtStep'] = (
                ([None] * step) + [lock_object['shows'][0]['boundingBox']]
            )
            # Adjust the show step to sync with the trial step.
            lock_object['shows'][0]['stepBegin'] = step

            lock_wall_object_list.append(lock_object)

            for frame_index, frame in enumerate(trial):
                # For each frame in this trial, either repeat the lock wall
                # object's original boundsAtStep, or add a None if the lock
                # is hidden at that frame.
                # Old prop: 'lock' ... New prop: 'key'
                if not frame.get('lock' if prop_is_lock else 'key'):
                    lock_object['debug']['boundsAtStep'].append(None)
                    if 'hides' not in lock_object:
                        # Hide the lock wall if it doesn't exist in this frame.
                        lock_object['hides'] = [{
                            'stepBegin': step + frame_index
                        }]
                        key_object['hides'].append({
                            'stepBegin': step + frame_index
                        })
                else:
                    lock_object['debug']['boundsAtStep'].append(
                        lock_object['debug']['boundsAtStep'][-1]
                    )

        # Add a None to each previous lock's boundsAtStep for each frame in
        # this trial. Always do this even if no lock wall exists in this trial!
        for previous_lock_object in lock_wall_object_list:
            total = step + len(trial) + 1
            previous_lock_object['debug']['boundsAtStep'] = (
                previous_lock_object['debug']['boundsAtStep'] + ([None] * (
                    total - len(previous_lock_object['debug']['boundsAtStep'])
                ))
            )

    return lock_wall_object_list


def _create_object(
    id_prefix: str,
    object_type: str,
    object_material: Tuple[str, str],
    object_height: Tuple[float, float],
    object_size: Tuple[float, float],
    json_coords: Tuple[int, int],
    json_size: Tuple[int, int],
    unit_size: Tuple[float, float],
    rotation_y: int = 0
) -> SceneObject:
    """Create and return an MCS object using the given data."""
    dimensions = OBJECT_DIMENSIONS[object_type]
    mcs_object = SceneObject({
        'id': id_prefix + str(uuid.uuid4()),
        'type': object_type,
        'materials': [object_material.material],
        'debug': {
            'color': object_material.color,
            'info': object_material[1] + [object_type],
            # Save the object's height and size data for future use.
            'configHeight': object_height,
            'configSize': object_size,
            'configRotation': rotation_y
        },
        'shows': [_create_show(
            0,
            object_type,
            object_height,
            object_size,
            json_coords,
            json_size,
            unit_size,
            rotation_y
        )]
    })
    scale = mcs_object['shows'][0]['scale']
    mcs_object['debug']['dimensions'] = dimensions.get_dict(scale)
    mcs_object['debug']['info'].append(' '.join(mcs_object['debug']['info']))
    mcs_object['debug']['boundsAtStep'] = [
        mcs_object['shows'][0]['boundingBox']
    ]
    return mcs_object


def _create_nonagent_occluder_object(
    trial_list: List[List[Dict[str, Any]]],
    agent_object: SceneObject,
    paddle_object: SceneObject,
    goal_object_list: List[SceneObject],
    occluder_mode: OccluderMode,
    unit_size: Tuple[float, float]
) -> Optional[SceneObject]:
    """Create and return the MCS scene's occluder object using the given trial
    list from the JSON file data."""

    scale_x = OCCLUDER_OBJECT_SIZE_NONAGENT[0]
    scale_z = OCCLUDER_OBJECT_SIZE_NONAGENT[1]

    json_size = [scale_x * unit_size[0], scale_z * unit_size[1]]

    # Ensure the occluder is always 1 taller than the agent.
    agent_height = agent_object['shows'][0]['boundingBox'].max_y
    occluder_height = max(0.5, round(agent_height * 10) / 10.0) + 1

    # Create the MCS occluder object.
    occluder_object = _create_object(
        'occluder_',
        OCCLUDER_OBJECT_TYPE,
        OCCLUDER_OBJECT_MATERIAL,
        [occluder_height / 2.0, occluder_height],
        [scale_x, scale_z],
        OCCLUDER_OBJECT_JSON_COORDS.copy(),
        json_size,
        unit_size,
        rotation_y=0
    )

    # Add the occluder's bounds for each other frame of the first trial.
    for _ in range(0, len(trial_list[0])):
        occluder_object['debug']['boundsAtStep'].append(
            occluder_object['shows'][-1]['boundingBox']
        )

    # Find the step for the start of the second trial.
    # Assume scenes will have more than one trial.
    step = _identify_trial_index_starting_step(1, trial_list)

    # Add data for the occluder's new position to each trial's start step.
    # Assume occluders only change in position across trials (not frames).
    for trial_index, trial in enumerate(trial_list):
        if trial_index == 0:
            continue

        is_final_trial = (trial_index == (len(trial_list) - 1))

        # For the final trial, in a training scene, position the occluder in a
        # random location where it does not block the view of anything
        # important in the scene.
        if is_final_trial and occluder_mode == OccluderMode.NONAGENT_TRAINING:
            observer_center = [4, -4]

            # Gather the bounds for all the important objects.
            agent_bounds_at_step = agent_object['debug']['boundsAtStep']
            paddle_bounds_at_step = paddle_object['debug']['boundsAtStep']
            unoccluded_data = []
            for unoccluded_bounds in agent_bounds_at_step[step:] + [
                instance['debug']['boundsAtStep'][step]
                for instance in goal_object_list
            ] + paddle_bounds_at_step[step:]:
                poly = unoccluded_bounds.true_poly
                center = list(poly.centroid.coords)[0]
                view = shapely.geometry.LineString([observer_center, center])
                unoccluded_data.append((unoccluded_bounds, view))

            # Generate a random grid.
            grid = [(x / unit_size[0], z / unit_size[1]) for x, z in GRID]
            random.shuffle(grid)

            # Try each location in the random grid to see if it's appropriate.
            for x, z in grid:
                json_coords = [x, z]
                # Create the "show" (and bounds) for this position.
                occluder_show = _create_show(
                    step,
                    occluder_object['type'],
                    occluder_object['debug']['configHeight'],
                    occluder_object['debug']['configSize'],
                    json_coords,
                    json_size,
                    unit_size,
                    # Perpendicular to the observer.
                    rotation_y=45
                )
                occluder_bounds = occluder_show['boundingBox']
                occluder_poly = occluder_bounds.true_poly
                for bounds, view in unoccluded_data:
                    # Ensure the occluder at this position will NOT obstruct
                    # the observer's view of the other object.
                    if view.intersects(occluder_poly):
                        occluder_show = None
                        break
                    # Ensure the occluder at this position will NOT overlap the
                    # other object.
                    if _do_objects_overlap(bounds, occluder_bounds, -1):
                        occluder_show = None
                        break
                if occluder_show:
                    logger.debug(
                        f'Occluder location {json_coords=} '
                        f'position={occluder_show["position"]}'
                    )
                    occluder_object['shows'].append(occluder_show)
                    occluder_object['debug']['jsonCoords'] = json_coords
                    occluder_object['debug']['jsonSize'] = json_size
                    break

        # For the final trial, in an evaluation scene, position the occluder
        # where the agent/non-agent would be hit by the paddle (this is
        # somewhere between the position of the paddle and the actual position
        # of the agent/non-agent).
        elif is_final_trial and occluder_mode == OccluderMode.NONAGENT_EVAL:
            # Find the starting position for the agent in this trial.
            agent_bounds_at_step = agent_object['debug']['boundsAtStep']
            agent_bounds = agent_bounds_at_step[step]
            agent_center = list(agent_bounds.true_poly.centroid.coords)[0]

            # Identify the step at which the agent begins to move.
            for agent_show in agent_object['shows']:
                if agent_show['stepBegin'] > step:
                    break
                agent_show = None

            # The paddle object would have pushed the agent about 30 steps
            # before it begins to move (from NYU).
            push_step = agent_show['stepBegin'] - 29
            for paddle_show in paddle_object['shows']:
                if paddle_show['stepBegin'] == push_step:
                    break
                paddle_show = None

            # Find the position for the paddle object in this trial.
            paddle_bounds = paddle_show['boundingBox']
            paddle_center = list(paddle_bounds.true_poly.centroid.coords)[0]

            # Find the position near the paddle at which the agent would be
            # found if it was to be pushed by the paddle.
            distance_over = PADDLE_OBJECT_SIZE[0] / 2.0
            distance_down = PADDLE_OBJECT_SIZE[1] / 2.0
            distance_diagonal = math.sqrt(distance_over**2 + distance_down**2)
            # Multiply by -1 because the angle should point downward.
            push_angle = math.radians(90) - math.acos((
                distance_diagonal**2 + distance_over**2 - distance_down**2
            ) / (2 * distance_diagonal * distance_over))
            # Subtract from 270 to covert the Unity rotation.
            paddle_angle = math.radians(270 - paddle_show['rotation']['y'])
            angle = push_angle + paddle_angle
            contact_center = [
                paddle_center[0] + distance_diagonal * math.cos(angle),
                paddle_center[1] + distance_diagonal * math.sin(angle)
            ]

            # Try positioning the occluder directly between the moving agent
            # and the performer (a.k.a. observer).
            hide_coords = [
                round((agent_center[0] - GRID_MIN_X) / unit_size[0]),
                round((agent_center[1] - GRID_MIN_Z) / unit_size[1])
            ]

            logger.debug(
                f'Finding location for occluder: {agent_center=} '
                f'{paddle_center=} {push_step=} {distance_diagonal=} '
                f'push_angle={math.degrees(push_angle)} '
                f'paddle_angle={math.degrees(paddle_angle)} '
                f'{contact_center=} {hide_coords=}'
            )

            occluder_object['debug']['contactPoint'] = contact_center
            occluder_object['debug']['hidePosition'] = agent_center
            occluder_object['debug']['hideCoords'] = hide_coords

            observer_center = [4, -4]
            view_to_contrast = shapely.geometry.LineString(
                [observer_center, contact_center]
            )
            view_to_agent = shapely.geometry.LineString(
                [observer_center, agent_center]
            )

            for z in range(0, 11):
                for i in range(20, 41):
                    # Occluder position to try.
                    json_coords = [
                        hide_coords[0] + i - (json_size[0] / 2.0),
                        hide_coords[1] - i - z - (json_size[1] / 2.0)
                    ]
                    # Create the "show" (and bounds) for this position.
                    occluder_show = _create_show(
                        step,
                        occluder_object['type'],
                        occluder_object['debug']['configHeight'],
                        occluder_object['debug']['configSize'],
                        json_coords,
                        json_size,
                        unit_size,
                        # Perpendicular to the observer.
                        rotation_y=45
                    )
                    occluder_poly = occluder_show['boundingBox'].true_poly

                    # Ensure the occluder at this position obstructs the view
                    # of both the agent and the paddle contact point.
                    if not view_to_contrast.intersects(occluder_poly):
                        logger.debug(
                            f'Move back: can see contact {json_coords=} '
                            f'occluder_position={occluder_show["position"]}'
                        )
                        occluder_show = None
                    if not view_to_agent.intersects(occluder_poly):
                        logger.debug(
                            f'Move back: can see agent {json_coords=} '
                            f'occluder_position={occluder_show["position"]}'
                        )
                        occluder_show = None

                    # Ensure the occluder does not intersect with the agent's
                    # movement.
                    if occluder_show:
                        for next_step, next_agent_bounds in enumerate(
                            agent_bounds_at_step[step:]
                        ):
                            if _do_objects_overlap(
                                next_agent_bounds,
                                occluder_show['boundingBox'],
                                step + next_step
                            ):
                                logger.debug(
                                    f'Move back: in the way {json_coords=} '
                                    f'occluder_position='
                                    f'{occluder_show["position"]}'
                                )
                                occluder_show = None
                                break

                    if occluder_show:
                        logger.debug(
                            f'Occluder location {json_coords=} '
                            f'position={occluder_show["position"]}'
                        )
                        occluder_object['shows'].append(occluder_show)
                        occluder_object['debug']['jsonCoords'] = json_coords
                        occluder_object['debug']['jsonSize'] = json_size
                        break
                if occluder_show:
                    break
            if not occluder_show:
                raise SceneException('Cannot find valid location for occluder')
        else:
            # Move the object to its new position for the trial.
            occluder_object['shows'].append(_create_show(
                step,
                occluder_object['type'],
                occluder_object['debug']['configHeight'],
                occluder_object['debug']['configSize'],
                OCCLUDER_OBJECT_JSON_COORDS.copy(),
                json_size,
                unit_size,
                rotation_y=0
            ))

        # Remove the scale from each element in 'shows' except for the
        # first, or it will really mess up the simulation.
        del occluder_object['shows'][-1]['scale']
        # Add the occluder's bounds for each frame of the trial.
        for _ in range(0, len(trial) + 1):
            occluder_object['debug']['boundsAtStep'].append(
                occluder_object['shows'][-1]['boundingBox']
            )

        # Add 1 for the EndHabituation action step at the end of the trial.
        step += len(trial) + 1

    occluder_object['structure'] = True
    # Set kinematic to avoid awkward shifting due to collision issues.
    occluder_object['kinematic'] = True
    # Set physics so this object's info is returned in the oracle metadata.
    occluder_object['physics'] = True

    return occluder_object


def _create_helper_hinderer_occluder_object(
    trial_list: List[List[Dict[str, Any]]],
    unit_size: Tuple[float, float]
) -> SceneObject:
    """Create and return the MCS scene's occluder objects using the given trial
    list from a helper-hinderer task JSON file data."""

    step = 0
    occluder_object = None

    # Add data for the occluder's new position to each trial's start step.
    for trial_index, trial in enumerate(trial_list):
        occluder_json = trial[0].get('door')
        # The occluder doesn't appear in all the trials.
        if not occluder_json:
            if occluder_object:
                occluder_object['hides'].append({
                    'stepBegin': step
                })
                for _ in range(0, len(trial) + 1):
                    occluder_object['debug']['boundsAtStep'].append(None)
        else:
            occluder_coords = occluder_json[0]
            occluder_size = occluder_json[1]

            if not occluder_object:
                # Create the MCS occluder object.
                occluder_object = _create_object(
                    'occluder_',
                    OCCLUDER_OBJECT_TYPE,
                    OCCLUDER_OBJECT_MATERIAL_HELPER_HINDERER,
                    OCCLUDER_OBJECT_HEIGHT_HELPER_HINDERER.copy(),
                    OCCLUDER_OBJECT_SIZE_HELPER_HINDERER.copy(),
                    occluder_coords,
                    occluder_size,
                    unit_size,
                    rotation_y=0
                )

                # Remove the first appearance (we override it later).
                occluder_object['shows'] = []
                occluder_object['hides'] = []
                occluder_object['structure'] = True
                occluder_object['kinematic'] = True
                occluder_object['physics'] = True
                occluder_object['debug']['boundsAtStep'] = []

                # Set its bounds as None for all the steps before it existed.
                for _ in range(0, step):
                    occluder_object['debug']['boundsAtStep'].append(None)

            # Add any movement to the occluder for the current trial.
            _append_each_show_to_object(
                occluder_object,
                trial,
                step,
                'door',
                unit_size
            )

        # Add 1 for the EndHabituation action step at the end of the trial.
        step += len(trial) + 1

    return occluder_object


def _create_true_false_belief_occluder_list(
    trial_list: List[List[Dict[str, Any]]],
    unit_size: Tuple[float, float]
) -> List[SceneObject]:
    """Create and return the MCS scene's occluder objects using the given trial
    list from a true-false-belief task JSON file data."""

    step = 0
    occluder_list = []

    # Add data for the occluder's new position to each trial's start step.
    # Assume occluders only change in position across trials (not frames).
    for trial_index, trial in enumerate(trial_list):
        occluder_json_list = trial[0].get('occluder')
        for occluder_index, occluder_json in enumerate(occluder_json_list):
            occluder_coords = occluder_json[0]
            occluder_size = occluder_json[1]
            if occluder_coords[0] <= 10:
                occluder_coords[0] = OCCLUDER_OBJECT_JSON_COORDS[0]

            if trial_index == 0:
                # Create the MCS occluder object.
                occluder_object = _create_object(
                    'occluder_',
                    OCCLUDER_OBJECT_TYPE,
                    OCCLUDER_OBJECT_MATERIAL,
                    OCCLUDER_OBJECT_HEIGHT_TRUE_FALSE_BELIEF.copy(),
                    OCCLUDER_OBJECT_SIZE_TRUE_FALSE_BELIEF.copy(),
                    occluder_coords,
                    occluder_size,
                    unit_size,
                    rotation_y=0
                )
                occluder_object['structure'] = True
                occluder_object['kinematic'] = True
                occluder_object['physics'] = True
                occluder_list.append(occluder_object)

            else:
                occluder_object = occluder_list[occluder_index]
                # Move the object to its new position for the trial.
                occluder_object['shows'].append(_create_show(
                    step,
                    occluder_object['type'],
                    occluder_object['debug']['configHeight'],
                    occluder_object['debug']['configSize'],
                    occluder_coords,
                    occluder_size,
                    unit_size,
                    rotation_y=0
                ))

                # Remove the scale from each element in 'shows' except for the
                # first, or it will really mess up the simulation.
                del occluder_object['shows'][-1]['scale']

            # Add the occluder's bounds for each frame of the trial.
            for _ in range(0, len(trial)):
                occluder_object['debug']['boundsAtStep'].append(
                    occluder_object['shows'][-1]['boundingBox']
                )

        # Add 1 for the EndHabituation action step at the end of the trial.
        step += len(trial) + 1

    return occluder_list


def _create_paddle_object(
    trial_list: List[List[Dict[str, Any]]],
    unit_size: Tuple[float, float]
) -> Optional[SceneObject]:
    """Create and return the MCS scene's paddle object using the given trial
    list from the JSON file data."""

    # Retrieve the paddle data from the first frame of the first trial.
    # Assume the number of paddles will never change, and the paddles will
    # never change shape/color.
    json_paddle = trial_list[0][0].get('paddle')
    if not json_paddle:
        return None
    json_coords = json_paddle[0]
    # The json_size isn't needed because the paddle's coordinates are already
    # centered.
    json_size = [0, 0]
    json_rotation = 360 - json_paddle[2]

    # Create the MCS paddle object.
    paddle_object = _create_object(
        'paddle_',
        PADDLE_OBJECT_TYPE,
        PADDLE_OBJECT_MATERIAL,
        PADDLE_OBJECT_HEIGHT,
        PADDLE_OBJECT_SIZE,
        json_coords,
        json_size,
        unit_size,
        rotation_y=json_rotation
    )

    # Remove the object's first appearance (we will override it later).
    paddle_object['shows'] = []
    paddle_object['hides'] = []
    paddle_object['debug']['boundsAtStep'] = []

    # Move the paddle on each step as needed.
    for trial_index, trial in enumerate(trial_list):
        _append_each_show_to_object(
            paddle_object,
            trial,
            _identify_trial_index_starting_step(trial_index, trial_list),
            'paddle',
            unit_size
        )
        if not trial[0].get('paddle'):
            # Hide the paddle if it's not shown in this trial.
            step = _identify_trial_index_starting_step(trial_index, trial_list)
            paddle_object['hides'].append({
                'stepBegin': step
            })
            for _ in range(len(trial) + 1):
                paddle_object['debug']['boundsAtStep'].append(None)

    # Set kinematic to avoid awkward shifting due to collision issues.
    paddle_object['kinematic'] = True
    # Set physics so this object's info is returned in the oracle metadata.
    paddle_object['physics'] = True

    return paddle_object


def _create_scene(
    starter_scene: Scene,
    goal_template: Goal,
    agent_object_config_list: List[ObjectConfigWithMaterial],
    goal_object_config_list: List[ObjectConfigWithMaterial],
    trial_list: List[List[Dict[str, Any]]],
    filename_prefix: str,
    platform_material: MaterialTuple,
    is_expected: bool,
    occluder_mode: OccluderMode = OccluderMode.NONE,
    rotate_room: bool = False
) -> Scene:
    """Create and return the MCS scene using the given templates, trial
    list, and expectedness answer from the JSON file data."""

    scene = copy.deepcopy(starter_scene)
    scene.version = 3
    scene.isometric = True
    if rotate_room:
        scene.isometric_front_right = True

    scene.goal = copy.deepcopy(goal_template)
    scene.goal.action_list = _create_action_list(trial_list)
    scene.goal.category = 'agents'
    scene.goal.habituation_total = len(trial_list) - 1
    scene.goal.last_step = len(scene.goal.action_list)
    scene.goal.metadata = {}
    scene.goal.answer = {
        'choice': EXPECTED if is_expected else UNEXPECTED
    }

    unit_size = _retrieve_unit_size(trial_list)
    wall_object_list = _create_wall_object_list(
        trial_list,
        unit_size,
        add_opening=(occluder_mode == OccluderMode.TRUE_FALSE_BELIEF),
        rotate_room=rotate_room
    )
    # IIRC the only tasks with multiple agents are the Multiple Agents task,
    # which has a different "agent" in the final trial, and the Imitation /
    # Social Approach tasks, which have an "agent" and multiple "other_agents".
    agent_object_list = _create_agent_object_list(
        trial_list,
        agent_object_config_list,
        unit_size
    )
    # Identify the primary agent.
    agent_object = agent_object_list[0]
    # Assume the primary agent is the only one moving around.
    agent_start_bounds = agent_object['shows'][0]['boundingBox']
    home_object = _create_home_object(trial_list, unit_size)
    goal_object_list = _create_goal_object_list(
        trial_list,
        goal_object_config_list,
        agent_start_bounds if home_object else None,
        filename_prefix,
        unit_size
    )
    key_object = _create_key_object(
        trial_list,
        unit_size,
        agent_object_list
    )
    lock_wall_list = _create_lock_wall_object_list(
        trial_list,
        key_object,
        unit_size
    )
    paddle_object = _create_paddle_object(trial_list, unit_size)
    target_list = goal_object_list[:1]
    non_target_list = goal_object_list[1:]

    # Update movement of goal objects in "test" trials for true/false belief.
    if occluder_mode == OccluderMode.TRUE_FALSE_BELIEF:
        def _callback(
            trial_start_step: int,
            json_key: Dict[str, Any],
            held_object: SceneObject
        ) -> SceneObject:
            return _fix_held_object_positions(
                trial_start_step,
                held_object,
                agent_object_list
            )

        final_trial_starting_step = _identify_trial_index_starting_step(
            len(trial_list) - 1,
            trial_list
        )

        # Move the goal object on each step in the final trial as needed.
        _append_each_show_to_object(
            goal_object_list[0],
            trial_list[-1],
            final_trial_starting_step,
            'objects',
            unit_size,
            _callback,
            goal_object_list[0]['shows'][0]['rotation']['y']
        )

    is_multi_agent = (
        'other_agents' in trial_list[0][0] or 'other_agent' in trial_list[0][0]
    )
    _remove_intersecting_agent_steps(
        agent_object_list,
        goal_object_list + lock_wall_list + wall_object_list +
        (agent_object_list[1:] if is_multi_agent else [])
    )
    _reposition_agents_away_from_paddle(
        agent_object_list,
        paddle_object
    )
    _remove_extraneous_object_show(
        agent_object_list + ([key_object] if key_object else []),
        trial_list
    )
    _move_agent_past_lock_location(agent_object_list, lock_wall_list)
    _move_agents_adjacent_to_goal(
        [agent_object] if is_multi_agent else agent_object_list,
        goal_object_list + (agent_object_list[1:] if is_multi_agent else []),
        trial_list,
        is_helper_hinderer=(occluder_mode == OccluderMode.HELPER_HINDERER)
    )
    # Extra check for the agent colliding with the paddle at any step.
    if paddle_object:
        for step, agent_bounds in enumerate(
            agent_object['debug']['boundsAtStep']
        ):
            paddle_bounds = paddle_object['debug']['boundsAtStep'][step]
            poly = agent_bounds.true_poly.intersection(paddle_bounds.true_poly)
            agent_area = round(agent_bounds.true_poly.area, 4)
            collision_area = 0 if poly.is_empty else round(poly.area, 4)
            area = round(collision_area / agent_area, 4)
            if area >= 0.05:
                raise SceneException(
                    f'Cannot convert {filename_prefix} because the paddle '
                    f'intersects too much with the agent: {step=} {area=}'
                )

    # If the agent is carrying the key on this step, move the key to be
    # centered directly above the agent.
    for key_show in (key_object['shows'] if key_object else []):
        if key_show['position']['y'] >= agent_start_bounds.max_y:
            position_x = KEY_OBJECT_ROTATION_Y[
                key_show['rotationProperty']
            ]['position_x']
            position_z = KEY_OBJECT_ROTATION_Y[
                key_show['rotationProperty']
            ]['position_z']
            agent_show = None
            for next_agent_show in agent_object['shows']:
                if next_agent_show['stepBegin'] > key_show['stepBegin']:
                    break
                agent_show = next_agent_show
            key_show['position']['x'] = (
                agent_show['position']['x'] + (position_x / 2.0)
            )
            key_show['position']['z'] = (
                agent_show['position']['z'] + (position_z / 2.0)
            )
        del key_show['rotationProperty']

    # Round object float properties to reduce the size of output scene files.
    for mcs_object in (
        agent_object_list + ([key_object] if key_object else []) +
        target_list + non_target_list
    ):
        for mcs_show in mcs_object['shows']:
            for a in ['x', 'y', 'z']:
                mcs_show['position'][a] = round(mcs_show['position'][a], 4)

    platform = structures.create_platform(
        position_x=4,
        position_z=(4 if rotate_room else -4),
        rotation_y=0,
        scale_x=0.5,
        scale_y=3,
        scale_z=0.5,
        room_dimension_y=10,
        material_tuple=platform_material
    )

    # Set distinct random materials for the floor and room walls.
    # Ensure they don't match the color of any important objects.
    excluded_colors = [
        color for mcs_object in (agent_object_list + goal_object_list)
        for color in mcs_object['debug']['color']
    ]
    scene.ceiling_material = CEILING_MATERIAL.material
    floor_choices = [choice for choice in FLOOR_MATERIALS if all([
        color not in excluded_colors for color in choice.color
    ])]
    floor_choice = random.choice(floor_choices)
    scene.floor_material = floor_choice.material
    scene.debug['floorColors'] = floor_choice.color
    wall_choices = [choice for choice in WALL_MATERIALS if all([
        color not in excluded_colors for color in choice.color
    ]) and choice.material != floor_choice.material]
    wall_choice = random.choice(wall_choices)
    scene.wall_material = wall_choice.material
    scene.debug['wallColors'] = wall_choice.color

    occluder_list = []
    if occluder_mode in [
        OccluderMode.NONAGENT_EVAL,
        OccluderMode.NONAGENT_TRAINING
    ]:
        occluder_list = [_create_nonagent_occluder_object(
            trial_list,
            agent_object,
            paddle_object,
            goal_object_list,
            occluder_mode,
            unit_size
        )]
    elif occluder_mode == OccluderMode.HELPER_HINDERER:
        occluder_list = [_create_helper_hinderer_occluder_object(
            trial_list,
            unit_size
        )]
        # In helper/hinderer scenes, ensure the primary agent does not collide
        # with the occluder, but DON'T test the other agents.
        _remove_intersecting_agent_steps([agent_object], occluder_list)
    elif occluder_mode == OccluderMode.TRUE_FALSE_BELIEF:
        occluder_list = _create_true_false_belief_occluder_list(
            trial_list,
            unit_size
        )

    role_to_object_list = {}
    role_to_object_list[tags.ROLES.AGENT] = agent_object_list
    role_to_object_list[tags.ROLES.HOME] = [home_object] if home_object else []
    role_to_object_list[tags.ROLES.KEY] = [key_object] if key_object else []
    role_to_object_list[tags.ROLES.PADDLE] = (
        [paddle_object] if paddle_object else []
    )
    role_to_object_list[tags.ROLES.NON_TARGET] = non_target_list
    role_to_object_list[tags.ROLES.STRUCTURAL] = [platform] + occluder_list
    role_to_object_list[tags.ROLES.TARGET] = target_list
    role_to_object_list[tags.ROLES.WALL] = wall_object_list + lock_wall_list

    scene = update_scene_objects(scene, role_to_object_list)
    return scene


def _create_show(
    begin_frame: int,
    object_type: str,
    object_height: Tuple[float, float],
    object_size: Tuple[float, float],
    json_coords: Tuple[int, int],
    json_size: Tuple[int, int],
    unit_size: Tuple[float, float],
    rotation_y: int = 0
) -> Dict[str, Any]:
    """Create and return an MCS object's 'shows' element using the given
    data."""
    dimensions = OBJECT_DIMENSIONS[object_type]
    mcs_show = {
        'stepBegin': begin_frame,
        'position': {
            'x': round(GRID_MIN_X + (
                (json_coords[0] + (json_size[0] / 2)) * unit_size[0]
            ), 4),
            'y': round(object_height[0], 4),
            'z': round(GRID_MIN_Z + (
                (json_coords[1] + (json_size[1] / 2)) * unit_size[1]
            ), 4)
        },
        'rotation': {'x': 0, 'y': rotation_y, 'z': 0},
        'scale': {
            'x': round(object_size[0], 4),
            'y': round(object_height[1], 4),
            'z': round(object_size[1], 4)
        }
    }
    mcs_show['boundingBox'] = _make_true_bounds(
        object_type=object_type,
        dimensions=dimensions.get_dict(mcs_show['scale']),
        offset={'x': 0, 'y': 0, 'z': 0},
        position=mcs_show['position'],
        rotation=mcs_show['rotation'],
        standing_y=(mcs_show['scale']['y'] * dimensions.y / 2.0)
    )
    return mcs_show


def _create_static_wall_object_list(
    trial_list: List[List[Dict[str, Any]]],
    unit_size: Tuple[float, float]
) -> List[SceneObject]:
    """Create and return the MCS scene's black static wall object list using
    the given trial list from the JSON file data."""

    static_wall_object_list = []

    step = 0
    for trial_index, trial in enumerate(trial_list):
        # Retrieve the wall data list from the first frame of each trial.
        json_wall_list = trial[0]['walls']

        # Only create new walls for the first trial or if they've changed.
        if (
            trial_index == 0 or
            json_wall_list != trial_list[trial_index - 1][0]['walls']
        ):
            # Assume the walls have changed, so hide any previous walls.
            for wall_object in static_wall_object_list:
                if not wall_object.get('hides'):
                    wall_object['hides'] = [{
                        'stepBegin': step
                    }]
                # Add the wall's bounds for each frame of the trial.
                for _ in range(0, len(trial) + 1):
                    wall_object['debug']['boundsAtStep'].append(None)

            for json_wall in json_wall_list:
                json_coords = json_wall[0]
                json_size = json_wall[1]

                # Ignore each part of border wall (we make it automatically)...
                if (
                    json_coords[0] == JSON_BORDER_WALL_MIN_X or
                    json_coords[0] == JSON_BORDER_WALL_MAX_X or
                    json_coords[1] == JSON_BORDER_WALL_MIN_Z or
                    json_coords[1] == JSON_BORDER_WALL_MAX_Z
                ):
                    continue

                # Create the MCS wall object and add it to the list.
                wall_object = _create_object(
                    'wall_',
                    'cube',
                    WALL_OBJECT_MATERIAL,
                    WALL_OBJECT_HEIGHT,
                    [WALL_OBJECT_SIZE, WALL_OBJECT_SIZE],
                    json_coords,
                    json_size,
                    unit_size
                )
                wall_object['kinematic'] = True
                wall_object['structure'] = True
                # Adjust the show step to sync with the trial step.
                wall_object['shows'][0]['stepBegin'] = step
                # Add the wall's bounds for each frame before the trial.
                for _ in range(0, step):
                    wall_object['debug']['boundsAtStep'].append(None)
                # Add the wall's bounds for each frame of the trial.
                for _ in range(0, len(trial) + 1):
                    wall_object['debug']['boundsAtStep'].append(
                        wall_object['shows'][-1]['boundingBox']
                    )
                static_wall_object_list.append(wall_object)
        else:
            for wall_object in static_wall_object_list:
                # Add the wall's bounds for each frame of the trial.
                for _ in range(0, len(trial) + 1):
                    wall_object['debug']['boundsAtStep'].append(
                        wall_object['shows'][-1]['boundingBox']
                    )

        # Add 1 for the EndHabituation action step at the end of the trial.
        step += len(trial) + 1

    return static_wall_object_list


def _create_trial_frame_list(
    trial: List[Dict[str, Any]],
    trial_index: int,
    rotate_room: bool = False
) -> List[Dict[str, Any]]:
    """Return all the frames in the given trial that we want to keep in the
    final MCS scene using the agent's movement. Skip about half of the frames
    to make the MCS simulation a bit quicker."""

    frame_list = []
    starting_coords = {}
    previous_coords = {}
    json_property_list = [
        'agent', 'fuse_walls', 'other_agent', 'other_agents', 'key', 'lock',
        'occluder', 'paddle', 'pin'
    ]
    for json_property in json_property_list:
        starting_coords[json_property] = trial[0].get(json_property)
        previous_coords[json_property] = trial[0].get(json_property)
    starting_frame_count = STARTING_STEP_WAIT_TIME
    paused_frame_count = PAUSED_STEP_WAIT_TIME
    defuse_frame_count = DEFUSE_STEP_SKIP_TIME
    skip_next = False

    for index, frame in enumerate(trial):
        # Keep or remove frames based on the movement of the agents/objects.
        coords = {}
        for json_property in json_property_list:
            coords[json_property] = frame.get(json_property)
        # Only keep a specific number of the trial's starting frames.
        check_objects = ['agent', 'other_agent', 'other_agents', 'paddle']
        if all([
            coords[json_property] == starting_coords[json_property]
            for json_property in check_objects
        ]):
            if starting_frame_count > 0:
                frame_list.append(frame)
                starting_frame_count -= 1
            continue
        # Reset in case another pause happens in the middle of the trial.
        starting_frame_count = STARTING_STEP_WAIT_TIME
        # Remove the last frames of any trial with a paddle because the paddle
        # will just keep spinning for an excessively long time, and then it
        # will stop as the 2D version of the scene "fades out".
        if coords['paddle'] and index >= (len(trial) - 50):
            continue
        # Only keep a specific number of the trial's agent-is-paused frames.
        if coords['agent'] == previous_coords['agent']:
            is_repeated = True
            for json_property in json_property_list:
                if coords[json_property] != previous_coords[json_property]:
                    is_repeated = False
                    check_objects = ['other_agent', 'other_agents', 'paddle']
                    if json_property not in check_objects:
                        skip_next = False
            # If a separate object is changing, don't skip this frame.
            if is_repeated:
                if paused_frame_count > 0:
                    frame_list.append(frame)
                    paused_frame_count -= 1
                continue
        # Reset the paused frame count if an object moves again.
        paused_frame_count = PAUSED_STEP_WAIT_TIME
        if coords['fuse_walls'] != previous_coords['fuse_walls']:
            only_fuse_wall = len(coords['fuse_walls'])
            for json_property in json_property_list:
                if json_property == 'fuse_walls':
                    continue
                if coords[json_property] != previous_coords[json_property]:
                    only_fuse_wall = False
                    break
            if only_fuse_wall:
                if defuse_frame_count == DEFUSE_STEP_SKIP_TIME:
                    frame_list.append(frame)
                    defuse_frame_count = 0
                defuse_frame_count += 1
                continue
            # If all the fuse walls are gone now, add a few steps of buffer
            # before the agent starts moving by copying the frame.
            if (
                len(coords['fuse_walls']) == 0 and
                len(previous_coords['fuse_walls']) > 0
            ):
                for _ in range(POST_DEFUSE_WAIT_TIME):
                    frame_list.append(frame)
        defuse_frame_count = DEFUSE_STEP_SKIP_TIME
        # Skip this frame if we used the previous frame.
        # Keep it if it's the last frame of the trial.
        if skip_next and index < (len(trial) - 1):
            skip_next = False
            continue
        # Record this frame for future comparison.
        for json_property in json_property_list:
            previous_coords[json_property] = coords[json_property]
        # Else keep this frame.
        frame_list.append(frame)
        skip_next = True

    # For ease, convert single element 'other_agents' into 'other_agent'
    for frame_index, frame in enumerate(frame_list):
        if 'other_agents' in frame and 'other_agent' not in frame:
            if len(frame['other_agents']) == 1:
                frame['other_agent'] = frame['other_agents'][0]
                del frame['other_agents']

    # For trials in which agent(s) move outside the grid world, add frames to
    # depict the movement for the 3D version of the trial.
    output_list = []
    previous_frame = None
    previous_agent_entrance = False
    for frame_index, frame in enumerate(frame_list):
        skip = False
        for json_prop in ['agent', 'other_agent']:
            # Keep frames in which the agent is inside the grid world.
            if not frame.get(json_prop) or frame[json_prop][0][0] <= 180:
                continue

            # Ignore frames in which the agent is on the right edge.
            # We'll add new frames in later.
            if 180 < frame[json_prop][0][0] < 200:
                skip = True

            # Skip repeat frames in which an agent is outside the grid world.
            elif frame == previous_frame:
                skip = True

            # Add frames to make the agent move out from behind a border wall
            # and into the grid world.
            elif not previous_frame or not previous_frame.get(json_prop):
                logger.debug(
                    f'Adding frames before {frame_index} to move an agent '
                    f'on-screen'
                )
                skip = True
                entrance_coords = (
                    [[i, -16] for i in range(141, 191, 5)] +
                    [[186, i] for i in range(-11, 99, 5)] + [[181, 94]]
                ) if rotate_room else (
                    [[i, 204] for i in range(141, 191, 5)] +
                    [[186, i] for i in range(199, 89, -5)] + [[181, 94]]
                )
                # If another agent already moved out from behind this wall,
                # make sure this agent doesn't collide with the other agent.
                if previous_agent_entrance:
                    additional_coords = (
                        [[i, -16] for i in range(116, 141, 5)]
                    ) if rotate_room else (
                        [[i, 204] for i in range(116, 141, 5)]
                    )
                    entrance_coords = additional_coords + entrance_coords
                previous_agent_entrance = True
                for coords in entrance_coords:
                    new_frame = copy.deepcopy(frame)
                    new_frame[json_prop][0] = coords
                    output_list.append(new_frame)

            # Add frames to make the agent move out from the grid world and out
            # of the movement path of the other agent.
            elif previous_frame[json_prop][0][0] < 200:
                logger.debug(
                    f'Adding frames after {frame_index} to move an agent '
                    f'off-screen'
                )
                skip = True
                exit_coords = (
                    [[186, i] for i in range(99, 139, 5)]
                ) if rotate_room else (
                    [[186, i] for i in range(89, 49, -5)]
                )
                for coords in exit_coords:
                    new_frame = copy.deepcopy(frame)
                    new_frame[json_prop][0] = coords
                    output_list.append(new_frame)

            # Edge case.
            elif frame[json_prop][0] == [201, 94]:
                logger.debug(f'Skipping extra frame {frame_index}')
                skip = True

        if not skip:
            output_list.append(frame)
        previous_frame = frame

    logger.info(
        f'Trial={trial_index + 1} Frames={len(trial)} Steps={len(output_list)}'
    )
    return output_list


def _create_wall_object_list(
    trial_list: List[List[Dict[str, Any]]],
    unit_size: Tuple[float, float],
    add_opening: bool = False,
    rotate_room: bool = False
) -> List[SceneObject]:
    """Create and return the MCS scene's wall object list using the given
    trial list from the JSON file data."""
    fuse_wall_list = _create_fuse_wall_object_list(trial_list, unit_size)
    static_wall_list = _create_static_wall_object_list(trial_list, unit_size)
    height = WALL_OBJECT_HEIGHT[1]
    size = WALL_OBJECT_SIZE
    # Create four static black border walls...
    wall_property_list = [
        ('wall_grid_front', (0, 2.25), (5, size), height),
        ('wall_grid_back', (0, -2.25), (5, size), height),
        ('wall_grid_left', (-2.25, 0), (size, 4), height),
        ('wall_grid_right', (2.25, 0), (size, 4), height)
    ]
    if add_opening:
        # ...OR create border walls with an opening in them for specific tasks.
        front_height = height if rotate_room else 1
        back_height = 1 if rotate_room else height
        wall_property_list = [
            ('wall_grid_front', (0, 2.25), (4, size), front_height),
            ('wall_grid_back', (0, -2.25), (4, size), back_height),
            ('wall_grid_left', (-2.25, 0), (size, 5), height),
            ('wall_grid_right_1', (1.75, -1.5), (size, 1.0), height),
            ('wall_grid_right_2', (1.75, 1.5), (size, 1.0), height),
        ]
    for name, position, size, height in wall_property_list:
        wall_object = SceneObject({
            'id': name,
            'type': 'cube',
            'materials': [WALL_OBJECT_MATERIAL[0]],
            'shows': [{
                'stepBegin': 0,
                'position': {
                    'x': position[0],
                    'y': round(height / 2.0, 4),
                    'z': position[1]
                },
                'rotation': {
                    'x': 0,
                    'y': 0,
                    'z': 0
                },
                'scale': {
                    'x': size[0],
                    'y': height,
                    'z': size[1]
                }
            }],
            'kinematic': True,
            'structure': True,
            'debug': {
                'info': WALL_OBJECT_MATERIAL[1] + ['cube'],
            }
        })
        wall_object['debug']['info'].append(
            ' '.join(wall_object['debug']['info'])
        )
        wall_object['shows'][0]['boundingBox'] = _make_true_bounds(
            object_type='cube',
            dimensions=wall_object['shows'][0]['scale'],
            offset={'x': 0, 'y': 0, 'z': 0},
            position=wall_object['shows'][0]['position'],
            rotation=wall_object['shows'][0]['rotation'],
            standing_y=(wall_object['shows'][0]['scale']['y'] / 2.0)
        )
        wall_object['debug']['boundsAtStep'] = []
        for trial in trial_list:
            # Add the wall's bounds for each frame of the trial.
            for _ in range(0, len(trial) + 1):
                wall_object['debug']['boundsAtStep'].append(
                    wall_object['shows'][-1]['boundingBox']
                )
        static_wall_list.append(wall_object)
    return static_wall_list + fuse_wall_list


def _do_objects_overlap(
    bounds_1: TrueObjectBounds,
    bounds_2: TrueObjectBounds,
    step: int
) -> bool:
    """Returns whether the two objects represented by the given "true bounds"
    overlap using their corresponding "true_poly" properties."""
    # Using "overlaps" instead of "intersects" appears to work better since it
    # still returns False if a single point in the perimeters touch, which is
    # especially important for agents potentially bumping into walls.
    # Also call on "within" since "overlaps" apparently doesn't do that.
    return (
        bounds_1.true_poly.overlaps(bounds_2.true_poly) or
        bounds_1.true_poly.within(bounds_2.true_poly) or
        bounds_2.true_poly.within(bounds_1.true_poly)
    )


def _fix_held_object_positions(
    trial_start_step: int,
    held_object: SceneObject,
    agent_object_list: List[SceneObject]
) -> SceneObject:
    """Adjust the object's height to above the agent when it starts moving."""
    if len(held_object['shows']) == 1:
        return held_object
    latest_show = held_object['shows'][-1]
    previous_show = held_object['shows'][-2]

    # Do nothing if the object hasn't actually moved.
    if (
        previous_show['position']['x'] == latest_show['position']['x'] and
        previous_show['position']['z'] == latest_show['position']['z']
    ):
        return held_object

    # Do nothing if the object just appeared in this trial.
    if (
        previous_show['stepBegin'] < trial_start_step and
        latest_show['stepBegin'] >= trial_start_step
    ):
        return held_object

    # See if any agent has moved close enough to this object to collide with it
    # since the object appeared, or the last step on which it was moved.
    previous_step = max(trial_start_step, previous_show['stepBegin'] + 1)
    for step in range(previous_step, latest_show['stepBegin'] + 1):
        for agent_object in agent_object_list:
            agent_bounds = agent_object['debug']['boundsAtStep'][step]
            object_bounds = held_object['debug']['boundsAtStep'][step]

            # Skip if this agent or the object doesn't appear at this step.
            if not agent_bounds or not object_bounds:
                continue

            # Skip if this agent doesn't collide with the object at this step.
            if not _do_objects_overlap(agent_bounds, object_bounds, step):
                continue

            agent_height = agent_bounds.max_y
            position_y = latest_show['position']['y']
            held_object['shows'].pop()

            # At each step between the collision step and the object's next
            # "show" step, adjust the height and position of the object so
            # it's above the center point of this agent.
            for s in range(step, latest_show['stepBegin'] + 1):
                agent_bounds = agent_object['debug']['boundsAtStep'][s]
                agent_poly = agent_bounds.true_poly
                agent_center = list(agent_poly.centroid.coords)[0]
                mcs_show = copy.deepcopy(latest_show)
                mcs_show['position']['x'] = round(agent_center[0], 4)
                mcs_show['position']['y'] = position_y + agent_height
                mcs_show['position']['z'] = round(agent_center[1], 4)
                mcs_show['stepBegin'] = s
                bounding_box = _make_true_bounds(
                    object_type=held_object['type'],
                    dimensions=held_object['debug']['dimensions'],
                    offset={'x': 0, 'y': 0, 'z': 0},
                    position=mcs_show['position'],
                    rotation=mcs_show['rotation'],
                    standing_y=(
                        held_object['shows'][0]['scale']['y'] *
                        held_object['debug']['dimensions']['y'] / 2.0
                    )
                )
                mcs_show['boundingBox'] = bounding_box
                held_object['shows'].append(mcs_show)
                held_object['debug']['boundsAtStep'][s] = bounding_box
                logger.debug(
                    f'Adjusted the position for object={held_object["type"]} '
                    f'held by agent={agent_object["type"]} at step={s}'
                )

            return held_object

    return held_object


def _fix_key_triangle_rotation(
    trial_start_step: int,
    json_key: Dict[str, Any],
    key_object: SceneObject
) -> SceneObject:
    """Update the given key object's location on a specific step (frame) in the
    current trial using the given JSON key data. Used as the on_step_callback
    parameter to _append_each_show_to_object on key objects."""

    # Rotate the key based on the JSON icon.
    json_icon = json_key[2]
    rotation_property = None
    if json_icon.endswith('triangle90.png'):
        rotation_property = 'negative_z'
    elif json_icon.endswith('triangle180.png'):
        rotation_property = 'positive_x'
    elif json_icon.endswith('triangle270.png'):
        rotation_property = 'positive_z'
    elif json_icon.endswith('triangle0.png'):
        rotation_property = 'negative_x'
    else:
        raise SceneException(f'Key is unexpected icon: {json_icon}')
    this_show = key_object['shows'][-1]
    this_show['rotation'] = {
        'x': KEY_OBJECT_ROTATION_X,
        'y': KEY_OBJECT_ROTATION_Y[rotation_property]['rotation_y'],
        'z': KEY_OBJECT_ROTATION_Z
    }
    # Save the rotation property for use in _create_key_object
    this_show['rotationProperty'] = rotation_property

    # Adjust the key's location based on its rotation (since the triangle isn't
    # centered on the X/Z axis). Also adjust its bounding box accordingly.
    this_show['position']['x'] += (
        KEY_OBJECT_ROTATION_Y[rotation_property]['position_x']
    )
    this_show['position']['z'] += (
        KEY_OBJECT_ROTATION_Y[rotation_property]['position_z']
    )
    dimensions_x = KEY_OBJECT_ROTATION_Y[rotation_property]['dimensions_x']
    dimensions_z = KEY_OBJECT_ROTATION_Y[rotation_property]['dimensions_z']
    this_show['boundingBox'] = _make_true_bounds(
        object_type=KEY_OBJECT_TYPE,
        dimensions={
            'x': dimensions_x,
            'y': KEY_OBJECT_HEIGHT[1],
            'z': dimensions_z
        },
        offset={'x': 0, 'y': 0, 'z': 0},
        position={
            'x': this_show['position']['x'] - (dimensions_x / 2.0),
            'y': this_show['position']['y'],
            'z': this_show['position']['z'] - (dimensions_z / 2.0)
        },
        rotation=this_show['rotation'],
        standing_y=(KEY_OBJECT_HEIGHT[1] / 2.0)
    )

    return key_object


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


def _make_true_bounds(
    object_type: str,
    # TODO MCS-697 MCS-698 Use Vector3d instead of Dict
    dimensions: Dict[str, float],
    offset: Optional[Dict[str, float]],
    position: Dict[str, float],
    rotation: Dict[str, float],
    standing_y: float
) -> TrueObjectBounds:
    """Create and return the "true bounds" for the instantiated object
    represented by the given arguments. The returned bounds will include a
    "true_poly" property which may be circular or triangular if appropriate
    based on the object's
    type."""
    bounds = geometry.create_bounds(
        dimensions=dimensions,
        offset=offset,
        position=position,
        rotation=rotation,
        standing_y=standing_y
    )
    true_poly = bounds.polygon_xz
    # Agents and "goal" objects may be circular rather than square.
    if object_type in ROUND_TYPES:
        center = shapely.geometry.Point(position['x'], position['z'])
        circle = center.buffer(1.0)
        true_poly = shapely.affinity.scale(
            circle,
            (dimensions['x'] / 2.0),
            (dimensions['z'] / 2.0)
        )
        true_poly = shapely.affinity.rotate(
            true_poly,
            -rotation['y'],
            origin=(position['x'], position['z'])
        )
    # Currently only "key" objects are triangles.
    if object_type == 'triangle':
        back = position['z'] - (dimensions['z'] / 2.0)
        front = position['z'] + (dimensions['z'] / 2.0)
        left = position['x'] - (dimensions['x'] / 2.0)
        right = position['x'] + (dimensions['x'] / 2.0)
        # Assume that the triangle's Z rotation is 90, and its X rotation is 0.
        true_poly = shapely.geometry.Polygon([
            (left, front), (right, front), (right, back)
        ])
        true_poly = shapely.affinity.rotate(
            true_poly,
            -rotation['y'],
            origin=(position['x'], position['z'])
        )
    return TrueObjectBounds(bounds=bounds, true_poly=true_poly)


def _move_agent_past_lock_location(
    agent_object_list: List[SceneObject],
    lock_wall_list: List[SceneObject]
) -> None:
    """Adjust the agent's movement onto and away from the lock space before
    and after inserting the key and removing the fuse walls."""
    # Assume only one agent in instrumental action scenes.
    agent_object = agent_object_list[0]
    # Assume only one lock per trial, and each lock is only hidden one time.
    for lock_object in lock_wall_list:
        # Sometimes the agent can just ignore the lock, so it never disappears.
        if 'hides' not in lock_object:
            continue
        # Find the first agent movement after the lock is removed.
        for index, show in enumerate(agent_object['shows']):
            if show['stepBegin'] > lock_object['hides'][0]['stepBegin']:
                break
        # This movement will depict the agent teleporting to the center of the
        # lock's now-removed position, which we don't want, so just delete it.
        del agent_object['shows'][index]
        # Remove each following movement that would also be within the lock's
        # position. We'll replace the removed movement next.
        remove_list = []
        lock_bounds = lock_object['debug']['boundsAtStep'][
            lock_object['hides'][0]['stepBegin'] - 1
        ]
        for index_2, target_show in enumerate(agent_object['shows'][(index):]):
            if _do_objects_overlap(
                target_show['boundingBox'],
                lock_bounds,
                target_show['stepBegin']
            ):
                remove_list.append(index + index_2)
            else:
                # Break once the movement exits the lock's position.
                break
        remove_list.reverse()
        for i in remove_list:
            del agent_object['shows'][i]
        # Identify the agent's positions before and after moving through the
        # lock's position, so we can replace the movement between them.
        position_x = agent_object['shows'][index - 1]['position']['x']
        position_z = agent_object['shows'][index - 1]['position']['z']
        target_position_x = target_show['position']['x']
        target_position_z = target_show['position']['z']
        # Identify the number of steps that the movement should take (longer
        # distances will take more steps).
        distance = math.sqrt(
            (target_position_x - position_x)**2 +
            (target_position_z - position_z)**2
        )
        # We expect the distance to be at most 0.7, which is the diagonal of a
        # 0.5 x 0.5 grid cell.
        move_time = min(
            max(1, int(round(distance / math.sqrt(2) * 10))),
            POST_DEFUSE_WAIT_TIME
        )
        # Divide the movement over the number of steps.
        fragment_x = (target_position_x - position_x) / move_time
        fragment_z = (target_position_z - position_z) / move_time
        # Adjust the existing show for the 1st fragment of movement as needed.
        target_show['stepBegin'] -= (move_time - 1)
        target_show['position']['x'] = position_x + fragment_x
        target_show['position']['z'] = position_z + fragment_z
        # Insert a new show for each successive fragment of movement.
        for amount in range(1, move_time):
            new_show = copy.deepcopy(target_show)
            new_show['stepBegin'] += amount
            new_show['position']['x'] += (fragment_x * amount)
            new_show['position']['z'] += (fragment_z * amount)
            agent_object['shows'].insert(index + amount, new_show)


def _move_agent_adjacent_to_goal(
    agent_object: SceneObject,
    goal_object_list: List[SceneObject],
    trial_list: List[List[Dict[str, Any]]],
    is_helper_hinderer: bool = False
) -> None:
    """Ensure the agent is directly adjacent to its goal in each trial."""
    trial_index_to_step = {}
    for trial_index in range(len(trial_list) + 1):
        step = _identify_trial_index_starting_step(trial_index, trial_list)
        trial_index_to_step[trial_index] = step

    for trial_index in range(len(trial_list)):
        first_step = trial_index_to_step[trial_index]
        final_step = trial_index_to_step[trial_index + 1] - 1

        # Identify each of the agent object's "shows" in this trial.
        agent_shows = [
            agent_show for agent_show in agent_object['shows']
            if first_step <= agent_show['stepBegin'] <= final_step
        ]

        # Skip this trial if the agent does not ever appear.
        if not agent_shows:
            continue

        # Calculate the distance on each step from the agent to the closest
        # goal object.
        closest_object_distances = [(MAX_DISTANCE, None, None, None)]

        for goal_object in goal_object_list:
            # In helper-hinderer scenes, ignore all agents during habituation
            # trials, because we may move near them, but not touch them.
            if is_helper_hinderer and (
                goal_object['type'].startswith('blob_')
            ) and trial_index != (len(trial_list) - 1):
                continue

            # Identify the goal object's "show" in this trial.
            # Assume each object will only have one "show" per trial.
            goal_show = None
            for show in goal_object['shows']:
                if show['stepBegin'] <= final_step:
                    goal_show = show
                if final_step < show['stepBegin']:
                    break
            if goal_show:
                show_step = goal_show['stepBegin']
                for hide in goal_object.get('hides', []):
                    if show_step <= hide['stepBegin'] <= final_step:
                        goal_show = None
                        break

            # Skip this object if it does not ever appear in this trial.
            if not goal_show:
                continue

            agent_shows_measure_distances = []

            agent_touches = goal_object['debug'].get('agentTouches', {})
            has_touches = any(
                [len(touches) > 0 for touches in agent_touches.values()]
            )
            if has_touches:
                # If we know an agent touches an object in this trial because
                # the object's color changes, only calculate the distances for
                # the step(s) on which an agent touches an object.
                # Assume an agent only "touches" ONE object in each trial.
                for touch_step in agent_touches[trial_index]:
                    touch_agent_show = agent_shows[0]
                    for agent_show in agent_shows[1:]:
                        if agent_show['stepBegin'] > touch_step:
                            break
                        touch_agent_show = agent_show
                    agent_shows_measure_distances.append(touch_agent_show)
            else:
                # Otherwise calculate the distances for ALL the steps.
                agent_shows_measure_distances = agent_shows

            goal_poly = goal_show['boundingBox'].true_poly

            # Calculate the distance on each step from the agent to the object.
            distance_tuples = []
            for agent_show in agent_shows_measure_distances:
                agent_poly = agent_show['boundingBox'].true_poly
                distance = round(agent_poly.distance(goal_poly), 4)
                distance_tuples.append(
                    (distance, agent_show, goal_show, goal_object)
                )

            # Sort the distances between the agent and the object on each step.
            distance_tuples = list(sorted(
                distance_tuples,
                # Later steps should be ordered before earlier steps with
                # the same distance.
                key=lambda x: (x[0], -x[1]['stepBegin'])
            ))

            # Skip this object if the agent never gets very close to it.
            if not distance_tuples or distance_tuples[0][0] > 0.19:
                logger.warning(
                    f'Cannot adjust agent position next to goal object: '
                    f'trial={trial_index + 1} agent={agent_object["type"]} '
                    f'object={goal_object["type"]} distance='
                    f'{distance_tuples[0][0] if distance_tuples else None}'
                )
                continue

            # See if the object is closer to the agent than any other object at
            # any step; the agent is probably touching the closest object.
            if distance_tuples[0][0] < closest_object_distances[0][0]:
                closest_object_distances = distance_tuples

        # Skip if no agents and/or goal objects are in this trial.
        if not closest_object_distances[0][1]:
            continue

        goal_object = closest_object_distances[0][3]
        highlight = True

        for data in closest_object_distances:
            logger.debug(
                f'distance={data[0]} step={data[1]["stepBegin"]}'
            )

        # Determine how many times the agent should touch the object. In
        # scenes with no color change (agentTouches is 0), use 1.
        agent_touches = goal_object['debug'].get('agentTouches', {})
        touch_count = len(agent_touches.get(trial_index) or [{}])
        # If the agent touches the object more than once, resort the list so
        # the touches are ordered by step rather than distance.
        if touch_count > 1:
            closest_object_distances = list(sorted(
                closest_object_distances,
                key=lambda x: x[1]['stepBegin']
            ))
        for index in range(touch_count):
            distance = closest_object_distances[index][0]
            agent_show = closest_object_distances[index][1]
            goal_show = closest_object_distances[index][2]
            old_position = agent_show['position'].copy()

            # Find the nearest distance from the agent to the goal.
            agent_point, goal_point = shapely.ops.nearest_points(
                agent_show['boundingBox'].true_poly,
                goal_show['boundingBox'].true_poly
            )
            diff_x = goal_point.coords[0][0] - agent_point.coords[0][0]
            diff_z = goal_point.coords[0][1] - agent_point.coords[0][1]

            # Move the agent directly adjacent to the goal.
            new_position = agent_show['position']
            new_position['x'] = round(new_position['x'] + diff_x, 4)
            new_position['z'] = round(new_position['z'] + diff_z, 4)
            agent_dimensions = agent_object['debug']['dimensions']
            agent_show['boundingBox'] = _make_true_bounds(
                object_type=agent_object['type'],
                dimensions={
                    'x': agent_dimensions['x'],
                    'y': agent_dimensions['y'],
                    'z': agent_dimensions['z']
                },
                offset={'x': 0, 'y': 0, 'z': 0},
                position=new_position,
                rotation=agent_show['rotation'],
                standing_y=(agent_dimensions['y'] / 2.0)
            )
            bounds_at_step = agent_object['debug']['boundsAtStep']
            old_bounds = bounds_at_step[agent_show['stepBegin']]
            for bounds_index in range(agent_show['stepBegin'], final_step):
                if bounds_index >= len(bounds_at_step):
                    break
                if bounds_at_step[bounds_index] == old_bounds:
                    bounds_at_step[bounds_index] = agent_show['boundingBox']

            logger.debug(
                f'Moving agent next to goal object: trial={trial_index + 1} '
                f'step={agent_show["stepBegin"]} '
                f'agent={agent_object["type"]} '
                f'object={goal_object["type"]} '
                f'old_position={(old_position["x"], old_position["z"])} '
                f'new_position={(new_position["x"], new_position["z"])} '
                f'distance={distance}'
            )

            # Toggle the color for ALL goal objects on the step the agent
            # touches one of them.
            for goal_object in goal_object_list:
                if goal_object['type'].startswith('blob_'):
                    continue
                goal_object['changeMaterials'].append({
                    'stepBegin': agent_show['stepBegin'],
                    'materials': (
                        [GOAL_OBJECT_HIGHLIGHT_MATERIAL] if highlight
                        else goal_object['materials']
                    )
                })

            # If the agent touches the object multiple times, toggle the
            # highlight color.
            highlight = (not highlight)

        # Reset materials for ALL goal objects before the next trial.
        for goal_object in goal_object_list:
            if goal_object['type'].startswith('blob_'):
                continue
            goal_object['changeMaterials'].append({
                'stepBegin': final_step + 1,
                'materials': goal_object['materials']
            })
            # Ensure the changeMaterials list is sorted by start step!
            goal_object['changeMaterials'] = list(sorted(
                goal_object['changeMaterials'],
                key=lambda x: x['stepBegin']
            ))


def _move_agents_adjacent_to_goal(
    agent_object_list: List[SceneObject],
    goal_object_list: List[SceneObject],
    trial_list: List[List[Dict[str, Any]]],
    is_helper_hinderer: bool = False
) -> None:
    """Ensure the agents are directly adjacent to its goal in each trial."""
    for agent_object in agent_object_list:
        _move_agent_adjacent_to_goal(
            agent_object,
            goal_object_list,
            trial_list,
            is_helper_hinderer=is_helper_hinderer
        )


def _remove_extraneous_object_show(
    object_list: List[SceneObject],
    trial_list: List[List[Dict[str, Any]]]
) -> None:
    """Remove each moving object's 'shows' array element that is the same as
    its previous array element, since they aren't needed, and we can therefore
    reduce the size of the JSON output file. Assume that each object should
    always be shown at the start of each trial."""
    starting_step_list = [
        _identify_trial_index_starting_step(trial_index, trial_list)
        for trial_index in range(len(trial_list))
    ]
    for mcs_object in object_list:
        mcs_object['debug']['extraneousSteps'] = []
        show_list = mcs_object['shows'][:1]
        for show in mcs_object['shows'][1:]:
            # Ignore it if the position/rotation are the same as the previous.
            if (
                show['position'] != show_list[-1]['position'] or
                show.get('rotation', {}) != show_list[-1].get('rotation', {})
            ):
                show_list.append(show)
            # Ensure that we show the object at the start of each trial.
            else:
                for starting_step in starting_step_list:
                    if starting_step == show['stepBegin']:
                        show_list.append(show)
                        break
                if show != show_list[-1]:
                    mcs_object['debug']['extraneousSteps'].append(
                        show['stepBegin']
                    )
        mcs_object['shows'] = show_list


def _remove_intersecting_agent_steps(
    agent_object_list: List[SceneObject],
    other_object_list: List[SceneObject]
) -> None:
    """Remove each agent object's step that intersects with any goal object's
    location at that step, since sometimes the agent moves a little too close
    to the goal object."""
    for agent_object in agent_object_list:
        trial_to_steps = agent_object['debug']['trialToSteps']
        agent_object['debug']['intersectingSteps'] = []

        for trial_index in sorted(list(trial_to_steps.keys())):
            remove_step_list = []
            # Identify the steps of the trial.
            trial_start, trial_end = trial_to_steps[trial_index]
            # Loop over each step, starting from the final step in the trial.
            for step in range(trial_end, trial_start - 1, -1):
                agent_bounds = agent_object['debug']['boundsAtStep'][step]
                # If the agent is hidden on this step, skip it.
                if not agent_bounds:
                    continue
                agent_poly = agent_bounds.true_poly
                # Look for intersections with other objects.
                for other_object in other_object_list:
                    if other_object['id'] == agent_object['id']:
                        continue
                    object_bounds = other_object['debug']['boundsAtStep'][step]
                    # If the object is hidden on this step, skip it.
                    if not object_bounds:
                        continue
                    # If the object is now being held above an agent, skip it.
                    if round(object_bounds.min_y, 3) > 0:
                        continue
                    intersection = _do_objects_overlap(
                        agent_bounds,
                        object_bounds,
                        step
                    )
                    if not intersection:
                        continue
                    # If the agent intersects an object, remove this movement
                    # step, UNLESS it intersects with a wall in the middle of
                    # its movement, when it has one or more non-intersecting
                    # steps later (since this would cause the agent to jump).
                    should_remove_this_step = True
                    if other_object['id'].startswith('wall_'):
                        for next_step in range(step + 1, trial_end + 1):
                            if next_step not in remove_step_list:
                                should_remove_this_step = False
                                break
                    if should_remove_this_step:
                        agent_center = list(agent_poly.centroid.coords)[0]
                        agent_center = (
                            round(agent_center[0], 4),
                            round(agent_center[1], 4)
                        )
                        logger.debug(
                            f'Removing {agent_center} '
                            f'at step {step} due to agent intersecting with '
                            f'{other_object["id"]}'
                        )
                        remove_step_list.append(step)
                        break
            # Remove all the intersecting steps for this trial.
            agent_object['shows'] = [
                show for show in agent_object['shows']
                if show['stepBegin'] not in remove_step_list
            ]
            agent_object['debug']['intersectingSteps'].extend(remove_step_list)
            # Update the agent's boundsAtStep.
            last_step = len(agent_object['debug']['boundsAtStep'])
            for agent_show in list(reversed(agent_object['shows'])):
                show_step = agent_show['stepBegin']
                bounds = agent_show['boundingBox']
                for step in range(show_step, last_step):
                    agent_object['debug']['boundsAtStep'][step] = bounds
                last_step = show_step

        agent_object['debug']['intersectingSteps'].sort()


def _reposition_agents_away_from_paddle(
    agent_object_list: List[SceneObject],
    paddle_object: SceneObject
) -> None:
    if not paddle_object:
        return
    # Map each step to the corresponding "show" for the paddle.
    step_to_paddle_show = {}
    for paddle_show in paddle_object['shows']:
        step = paddle_show['stepBegin']
        step_to_paddle_show[step] = paddle_show
    for agent_object in agent_object_list:
        agent_bounds_at_step = agent_object['debug']['boundsAtStep']
        trial_to_steps = agent_object['debug']['trialToSteps']
        # Loop over all the trials in REVERSE order.
        for trial_index in list(range(len(trial_to_steps) - 1, -1, -1)):
            # Identify the start and end steps for the current trial.
            trial_start, trial_end = trial_to_steps[trial_index]
            # Identify the agent's "shows" for the current trial.
            agent_shows = [
                show for show in agent_object['shows']
                if trial_start <= show['stepBegin'] <= trial_end
            ]
            if not agent_shows:
                continue
            # See if the spinning paddle would ever intersect the agent's
            # starting position of the current trial. If not, the agent does
            # not begin near the paddle, so skip checking the current trial.
            agent_bounds = agent_bounds_at_step[agent_shows[0]['stepBegin']]
            skip = True
            for step in range(trial_start, trial_end + 1):
                if not step_to_paddle_show.get(step):
                    continue
                paddle_bounds = paddle_object['debug']['boundsAtStep'][step]
                if _do_objects_overlap(
                    agent_bounds,
                    paddle_bounds,
                    step
                ):
                    skip = False
                    break
            if skip:
                continue
            # Keep record of the most recent valid "show" location.
            valid_show = None
            previously_intersects = False
            # Loop over all the "shows" in REVERSE order.
            for agent_show in list(reversed(agent_shows)):
                step = agent_show['stepBegin']
                # See if the paddle and agent would intersect.
                if not step_to_paddle_show.get(step):
                    continue
                agent_bounds = agent_bounds_at_step[step]
                paddle_bounds = paddle_object['debug']['boundsAtStep'][step]
                intersects = _do_objects_overlap(
                    agent_bounds,
                    paddle_bounds,
                    step
                )
                if intersects and not previously_intersects:
                    # Allow exactly one step of intersection; it is probably
                    # minor and ensures the paddle and agent actually "touch".
                    valid_show = agent_show
                    previously_intersects = True
                elif intersects or previously_intersects:
                    logger.debug(
                        f'Replacing {agent_show["position"]} with '
                        f'{valid_show["position"]} at step {step} '
                        f'due to agent intersecting with paddle'
                    )
                    # Move the agent to the most recent valid "show" location.
                    agent_show['position'] = valid_show['position'].copy()
                    agent_show['rotation'] = valid_show['rotation'].copy()
                    agent_bounds_at_step[step] = agent_bounds_at_step[
                        valid_show['stepBegin']
                    ]
                    previously_intersects = True
                else:
                    # Otherwise keep the agent at its current location.
                    valid_show = agent_show


def _retrieve_unit_size(
    trial_list: List[List[Dict[str, Any]]]
) -> Tuple[float, float]:
    """Return the unit size of this scene's grid."""
    # Assume the JSON grid size will never change.
    json_grid = trial_list[0][0]['size']
    grid_size_x = (GRID_MAX_X - GRID_MIN_X) / json_grid[0]
    grid_size_z = (GRID_MAX_Z - GRID_MIN_Z) / json_grid[1]
    return [grid_size_x, grid_size_z]


def _save_trials(trial_list: List[List[Dict[str, Any]]], filename_prefix: str):
    """Save the modified JSON list of trials to text file for debugging."""
    with open(f'{filename_prefix}{TRIALS_SUFFIX}', 'w') as output_file:
        for trial_index, trial in enumerate(trial_list):
            step = _identify_trial_index_starting_step(trial_index, trial_list)
            output_file.write(f'TRIAL {trial_index + 1} (STEP {step})\n\n')
            for frame_index, frame in enumerate(trial):
                output_file.write(
                    f'FRAME {frame_index + 1} (STEP {step + frame_index})\n'
                )
                output_file.write(f'AGENT {frame.get("agent")}\n')
                output_file.write(
                    f'OTHER AGENT {frame.get("other_agent")}\n'
                )
                output_file.write(
                    f'OTHER AGENTS {frame.get("other_agents")}\n'
                )
                output_file.write(f'DOOR {frame.get("door")}\n')
                output_file.write(f'FUSE_WALLS {frame.get("fuse_walls")}\n')
                output_file.write(f'KEY {frame.get("key")}\n')
                output_file.write(f'LOCK {frame.get("lock")}\n')
                output_file.write(f'OBJECTS {frame.get("objects")}\n')
                output_file.write(f'OCCLUDER {frame.get("occluder")}\n')
                output_file.write(f'PADDLE {frame.get("paddle")}\n')
                output_file.write(f'PIN {frame.get("pin")}\n')
                output_file.write('\n')


def _validate_trials(
    trial_list: List[List[Dict[str, Any]]],
    filename_prefix: str,
    suffix: str
) -> List[List[Dict[str, Any]]]:
    """Fix some formatting issues in the NYU JSON scene files."""

    logger.info(f'Found {len(trial_list)} trials...')

    if len(trial_list) > 9:
        if all([isinstance(trial, list) for trial in trial_list[:8]]):
            final_trial = trial_list[8:]
            trial_list = trial_list[:8] + [final_trial]
            logger.info(
                f'Collapsed {len(final_trial)} frames to use as final trial.'
            )

    if len(trial_list) > 9:
        raise Exception(f'Too many trials in {filename_prefix}{suffix}')

    # Sometimes frames (which are supposed to be dicts) are accidentally lists
    # of frames instead, so just add all the nested frames to the trial.
    for trial_index, trial in enumerate(trial_list):
        new_trial = []
        for frame_index, frame in enumerate(trial):
            if isinstance(frame, dict):
                new_trial.append(frame)
            elif isinstance(frame, list):
                logger.warn(
                    f'FRAME IS LIST {filename_prefix}{suffix} '
                    f'trial {trial_index + 1} frame {frame_index + 1} / '
                    f'{len(trial)}'
                )
                new_trial.extend(frame)
            else:
                # If it's not a dict or a list, something's wrong...
                raise Exception(
                    f'FRAME IS {type(frame).__name__.upper()} '
                    f'{filename_prefix}{suffix} '
                    f'trial {trial_index + 1} frame {frame_index + 1} / '
                    f'{len(trial)}'
                )
        trial_list[trial_index] = new_trial

    return trial_list


def convert_scene_pair(
    starter_scene: Dict[str, Any],
    goal_template: Goal,
    trial_list_expected: List[List[Dict[str, Any]]],
    trial_list_unexpected: List[List[Dict[str, Any]]],
    filename_prefix: str,
    role_to_type: Dict[str, str],
    untrained: bool,
    toggle: bool = False,
    occluder_mode: OccluderMode = OccluderMode.NONE
) -> List[Dict[str, Any]]:
    """Create and return the pair of MCS scenes using the given templates
    and trial lists from the JSON file data."""

    is_eval_7 = occluder_mode in EVAL_7_TASKS
    rotate_room = False
    if is_eval_7:
        rotate_room = toggle

    # Ignore untrained for now.
    untrained = False

    trial_list_expected = _validate_trials(
        trial_list_expected,
        filename_prefix,
        'e'
    )
    trial_list_unexpected = _validate_trials(
        trial_list_unexpected,
        filename_prefix,
        'u'
    ) if trial_list_unexpected else None

    # Create the converted trial lists for both of the scenes. This will
    # remove extraneous frames from all of the trials.
    converted_trial_list_expected = [
        _create_trial_frame_list(trial, index, rotate_room) for index, trial
        in enumerate(trial_list_expected)
    ]

    if SAVE_TRIALS_TO_FILE:
        _save_trials(
            converted_trial_list_expected,
            f'{filename_prefix[(filename_prefix.rfind("/") + 1):]}e'
        )

    # Choose the shape and color of each object in a scene so we can use them
    # in both scenes across the pair so they will always have the same config.
    agent_object_config_list = _choose_config_list(
        converted_trial_list_expected,
        [
            config for config in AGENT_OBJECT_CONFIG_LIST
            if config.untrained == untrained
        ],
        [
            role_to_type[tags.ROLES.AGENT],
            role_to_type['second agent'],
            None
        ],
        AGENT_OBJECT_MATERIAL_LIST,
        'agent'
    )

    agent_material_list = [item.material for item in agent_object_config_list]
    goal_object_material_list = []
    if materials.BLUE not in agent_material_list:
        goal_object_material_list.append(GOAL_OBJECT_MATERIAL_LIST_BLUES)
    if materials.GOLDENROD not in agent_material_list:
        goal_object_material_list.append(GOAL_OBJECT_MATERIAL_LIST_YELLOWS)
    if materials.GREEN not in agent_material_list:
        goal_object_material_list.append(GOAL_OBJECT_MATERIAL_LIST_GREENS)
    if materials.PURPLE not in agent_material_list:
        goal_object_material_list.append(GOAL_OBJECT_MATERIAL_LIST_PURPLES)

    goal_object_config_list = _choose_config_list(
        converted_trial_list_expected,
        [
            config for config in GOAL_OBJECT_CONFIG_LIST
            if config.untrained == untrained
        ],
        [
            role_to_type[tags.ROLES.TARGET],
            role_to_type[tags.ROLES.NON_TARGET],
            None
        ],
        goal_object_material_list,
        'objects'
    )

    # Ensure the two scenes have exactly the same platform material.
    platform_material = random.choice(materials.WALL_MATERIALS)

    logger.info('Generating expected MCS agent scene from JSON data')
    scene_expected = _create_scene(
        starter_scene,
        goal_template,
        agent_object_config_list,
        goal_object_config_list,
        converted_trial_list_expected,
        filename_prefix,
        platform_material,
        is_expected=True,
        occluder_mode=occluder_mode,
        rotate_room=rotate_room
    )
    scenes = [scene_expected]

    # Training datasets will not have any unexpected scenes.
    if trial_list_unexpected:
        logger.info('Generating unexpected MCS agent scene from JSON data')
        converted_trial_list_unexpected = [
            _create_trial_frame_list(trial, index, rotate_room)
            for index, trial in enumerate(trial_list_unexpected)
        ]
        if SAVE_TRIALS_TO_FILE:
            _save_trials(
                converted_trial_list_unexpected,
                f'{filename_prefix[(filename_prefix.rfind("/") + 1):]}u'
            )
        scene_unexpected = _create_scene(
            starter_scene,
            goal_template,
            agent_object_config_list,
            goal_object_config_list,
            converted_trial_list_unexpected,
            filename_prefix,
            platform_material,
            is_expected=False,
            occluder_mode=occluder_mode,
            rotate_room=rotate_room
        )
        # Ensure the two scenes have exactly the same room materials.
        for prop in ['ceiling_material', 'floor_material', 'wall_material']:
            setattr(scene_unexpected, prop, getattr(scene_expected, prop))
        for prop in ['floorColors', 'wallColors']:
            scene_unexpected.debug[prop] = scene_expected.debug[prop]
        scenes.append(scene_unexpected)

    return scenes
