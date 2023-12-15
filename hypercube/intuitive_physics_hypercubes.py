import copy
import itertools
import json
import logging
import math
import random
import uuid
from abc import ABC, abstractmethod
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

from machine_common_sense.config_manager import Goal, PerformerStart, Vector3d
from shapely import affinity

from generator import (
    MAX_TRIES,
    DefinitionDataset,
    ImmutableObjectDefinition,
    MaterialTuple,
    ObjectBounds,
    ObjectDefinition,
    Scene,
    SceneException,
    SceneObject,
    geometry,
    gravity_support_objects,
    instances,
    materials,
    mechanisms,
    occluders,
    specific_objects,
    tags
)
from generator.intuitive_physics_objects import (
    get_fall_down_basic_shape_definition_dataset,
    get_fall_down_basic_shape_opposite_colors_definition_dataset,
    get_fall_down_complex_shape_definition_dataset,
    get_fall_down_complex_shape_opposite_colors_definition_dataset,
    get_move_across_basic_shape_definition_dataset,
    get_move_across_basic_shape_opposite_colors_definition_dataset,
    get_move_across_complex_shape_definition_dataset,
    get_move_across_complex_shape_opposite_colors_definition_dataset
)
from generator.intuitive_physics_util import (
    COLLISION_SPEEDS,
    MAX_TARGET_Z,
    MIN_TARGET_Z,
    choose_position_z,
    retrieve_off_screen_position_x,
    retrieve_off_screen_position_y
)

from .hypercubes import (
    Hypercube,
    HypercubeFactory,
    update_floor_and_walls,
    update_scene_objects,
    update_scene_objects_tag_lists
)

logger = logging.getLogger(__name__)

PLAUSIBLE = 'plausible'
IMPLAUSIBLE = 'implausible'

# The number of steps any object will take to fall and settle.
OBJECT_FALL_TIME = 36

LAST_STEP_MOVE_ACROSS = 200
LAST_STEP_FALL_DOWN = 160

EARLIEST_ACTION_STEP = occluders.OCCLUDER_MOVEMENT_TIME * 2 + 1

BACKGROUND_MAX_X = 6.5
BACKGROUND_MIN_Z = 3.25
BACKGROUND_MAX_Z = 4.95

TIPSY_OBJECT_TYPES = [
    'rollable_4',
    'rollable_6',
    'rollable_10',
    'rollable_11'
]

PERFORMER_START = PerformerStart(
    position=Vector3d(x=0, y=0, z=-4.5),
    rotation=Vector3d(x=0, y=0, z=0)
)

# Objects in Eval 5 collisions hypercubes were specifically required to have
# very different depths.
MAX_TARGET_Z_EXTENDED = 9.4
# In Eval 5, we've made novel objects even bigger, which means we need to make
# occluders bigger, which has limited how deep we can position the objects in
# hypercubes with two occluders (specifically spatio-temporal continuity).
MAX_TARGET_Z_RESTRICTED = 3.7

# Minimum separation distance between moving objects.
SEPARATION_Z = 1.1

# Assume the target object will be at most 1.0 wide, and then add some space
# for the no-support position, so each object is always in view of the camera.
# Restrict the max X to 0.5 at request of the psychology team.
GRAVITY_SUPPORT_MAX_ONSCREEN_X = 0.5

GRAVITY_SUPPORT_WIND_FORCE_X = 400

# Set the wind wait step to be the same as the placer wait step.
GRAVITY_SUPPORT_WIND_WAIT_STEP = mechanisms.PLACER_WAIT_STEP

ROUND_TYPES = ['ball', 'sphere'] + mechanisms.CYLINDRICAL_SHAPES.copy()

MOVEMENT_JSON_FILENAME = 'movements.json'


def load_movement_from_json_file():
    """Load all of the movement data from its JSON file."""
    data = None
    with open(MOVEMENT_JSON_FILENAME) as movement_file:
        data = json.load(movement_file)
    if data is None:
        raise SceneException(
            f'Cannot load passive intuitive physics movement data from '
            f'{MOVEMENT_JSON_FILENAME}')
    # Convert the position and step keys in each option list to numbers.
    for option_list_property in ['exitOnlyOptionList', 'exitStopOptionList']:
        for movement in data['moveExit']:
            old_position_dict = movement[option_list_property]
            new_position_dict = {}
            for str_position in old_position_dict.keys():
                old_step_dict = old_position_dict[str_position]
                new_step_dict = {}
                for str_step in old_position_dict[str_position].keys():
                    int_step = int(str_step)
                    new_step_dict[int_step] = old_step_dict[str_step]
                float_position = round(float(str_position), 2)
                new_position_dict[float_position] = new_step_dict

            movement[option_list_property] = new_position_dict
    return SimpleNamespace(
        MOVE_EXIT_LIST=data['moveExit'],
        DEEP_EXIT_LIST=data['deepExit'],
        TOSS_EXIT_LIST=data['tossExit'],
        MOVE_STOP_LIST=data['moveStop'],
        DEEP_STOP_LIST=data['deepStop'],
        TOSS_STOP_LIST=data['tossStop']
    )


MOVEMENT = load_movement_from_json_file()


def adjust_movement_to_position(
    movement: Optional[Dict[str, Any]],
    position: Dict[str, float],
    left_side: bool
) -> Optional[Dict[str, Any]]:
    """Adjust each X and Z distance in the distance-by-step lists in the given
    movement using the given starting position."""
    if not movement:
        return None
    end_x = 2 * abs(movement.get('startX', position['x']))
    # Add/subtract the object's starting position to/from its X/Z move
    # distance in each X/Z distance-by-step list.
    movement['xDistanceByStep'] = [
        round(
            ((1 if left_side else -1) * distance) +
            movement.get('startX', position['x']),
            4
        ) for distance in movement['xDistanceByStep']
        # Remove each X distance from the distance-by-step list after the
        # object moves off-screen.
        if (abs(distance) <= end_x)
    ]
    if 'zDistanceByStep' in movement:
        movement['zDistanceByStep'] = [
            round(distance + movement.get('startZ', position['z']), 4)
            for distance in movement['zDistanceByStep']
        ][0:len(movement['xDistanceByStep'])]
    return movement


def choose_move_across_object_position(
    left_side: bool,
    object_list: List[SceneObject],
    min_z: float = MIN_TARGET_Z,
    max_z: float = MAX_TARGET_Z
) -> Optional[Dict[str, float]]:
    """Return a new X/Y/Z position for a move-across object with the given
    side and Y position that is not too close to an existing object."""
    for _ in range(MAX_TRIES):
        position_z = choose_position_z(min_z, max_z)
        # Don't be too close to any existing object.
        for instance in object_list:
            object_z = instance['shows'][0]['position']['z']
            if (
                position_z < (object_z + SEPARATION_Z) and
                position_z > (object_z - SEPARATION_Z)
            ):
                position_z = None
                break
        if position_z is not None:
            break

    if position_z is None:
        return None

    position_x = retrieve_off_screen_position_x(position_z)

    return {
        'x': (-1 * position_x) if left_side else position_x,
        'y': 0,
        'z': position_z
    }


def object_x_to_occluder_x(object_x: float, object_z: float):
    """Return the X position for an occluder in front of an object at the given
    X/Z position."""
    return geometry.object_x_to_occluder_x(
        object_x,
        object_z,
        occluders.OCCLUDER_POSITION_Z,
        PERFORMER_START.position.x,
        PERFORMER_START.position.z
    )


def occluder_x_to_object_x(occluder_x: float, object_z: float):
    """Return the X position for an object at the given Z position in back of
    an occluder at the given X position."""
    return geometry.occluder_x_to_object_x(
        occluder_x,
        occluders.OCCLUDER_POSITION_Z,
        object_z,
        PERFORMER_START.position.x,
        PERFORMER_START.position.z
    )


def validate_in_view(
    occluder_x: float,
    min_x: float = -occluders.OCCLUDER_MAX_X,
    max_x: float = occluders.OCCLUDER_MAX_X,
    occluder_size_x: float = (
        occluders.OCCLUDER_MAX_SCALE_X + occluders.OCCLUDER_BUFFER
    )
) -> bool:
    """Return whether the given X position is within view of the camera."""
    min_position_x = min_x + (occluder_size_x / 2.0)
    max_position_x = max_x - (occluder_size_x / 2.0)
    return occluder_x >= min_position_x and occluder_x <= max_position_x


VARIATIONS = SimpleNamespace(
    TRAINED='trained',
    DIFFERENT_COLOR='different_color',
    DIFFERENT_SHAPE='different_shape',
    DIFFERENT_SIZE='different_size',
    UNTRAINED_SHAPE='untrained_shape',
    UNTRAINED_DIFFERENT_SHAPE='untrained_different_shape',
    UNTRAINED_SHAPE_DIFFERENT_SIZE='untrained_shape_different_size',
    UNTRAINED_SIZE='untrained_size',
    # Gravity Support
    SYMMETRIC='symmetric',
    ASYMMETRIC_LEFT='asymmetric_left',
    ASYMMETRIC_RIGHT='asymmetric_right'
)


class ObjectVariations():
    """Saves multiple variations of a single conceptual object. Each scene in a
    hypercube may use a variation of the object. Variations may be different in
    size, shape, position, color, etc."""

    def __init__(self, name_to_instance: Dict[str, SceneObject]) -> None:
        self._instances = name_to_instance

    def all(self) -> List[SceneObject]:
        """Return a list of instances for all variations."""
        return list(self._instances.values())

    def get(self, name) -> SceneObject:
        """Return an instance for the variation with the given name."""
        return self._instances.get(name)

    def get_max_size_x(self):
        """Return the max size X of instances across all variations."""
        # For a non-occluder, the size is its dimensions, NOT its scale!
        # Object may be seen at an angle, so use its diagonal distance.
        return max([math.sqrt(
            instance['debug']['dimensions']['x']**2 +
            instance['debug']['dimensions']['z']**2
        ) for instance in self.all()])


class TargetVariations(ObjectVariations):
    """Saves multiple variations of a single conceptual target. Each scene in a
    hypercube may use a variation of the target. Variations may be different in
    size, shape, position, color, etc."""

    def __init__(
        self,
        name_to_definition: Dict[str, ObjectDefinition],
        location: Dict[str, Any],
        is_fall_down=False
    ) -> None:
        self._definitions = name_to_definition
        self._is_fall_down = is_fall_down

        object_id = None

        object_instances = {}
        for name, definition in name_to_definition.items():
            adjusted_location = self._adjust_location(definition, location)
            # Instantiate each variation from the common target definition.
            object_instances[name] = instances.instantiate_object(
                definition,
                adjusted_location
            )
            object_instances[name]['shows'][0]['boundingBox'] = (
                geometry.create_bounds(
                    dimensions=vars(definition.dimensions),
                    offset=vars(definition.offset),
                    position=object_instances[name]['shows'][0]['position'],
                    rotation=object_instances[name]['shows'][0]['rotation'],
                    standing_y=definition.positionY
                )
            )
            # Ensure each instance uses the same ID and materials/colors.
            if not object_id:
                object_id = object_instances[name]['id']
            object_instances[name]['id'] = object_id
            object_instances[name]['debug']['role'] = tags.ROLES.TARGET

        super().__init__(object_instances)

    def _adjust_location(
        self,
        definition: ObjectDefinition,
        location: Dict[str, Any]
    ) -> Dict[str, Any]:
        location_copy = copy.deepcopy(location)
        location_copy['position']['y'] += definition.positionY
        if 'rotation' not in location_copy:
            location_copy['rotation'] = {
                'x': 0,
                'y': 0,
                'z': 0
            }
        # If the object's a cylinder, rotate it a little to be at an angle.
        if self._is_fall_down and definition.type in ROUND_TYPES:
            location_copy['rotation']['y'] = random.choice([45, -45])
        return location_copy


def retrieve_as_list(data: Any) -> List[Any]:
    return [data]


class IntuitivePhysicsHypercube(Hypercube, ABC):
    def __init__(
        self,
        name: str,
        starter_scene: Scene,
        goal_template: Goal,
        role_to_type: Dict[str, str],
        is_fall_down=False,
        is_move_across=False,
        only_basic_shapes=False,
        only_complex_shapes=False,
        training=False,
        last_step=None
    ) -> None:
        self._role_to_type = role_to_type

        # Choose fall-down or move-across if needed.
        if not is_fall_down and not is_move_across:
            is_fall_down = random.choice([False, True])
            is_move_across = not is_fall_down

        self._init_each_object_definition_list(
            is_fall_down,
            only_basic_shapes,
            only_complex_shapes
        )

        if is_fall_down:
            self._last_step = last_step if last_step else LAST_STEP_FALL_DOWN
            self._scene_setup_function = (
                IntuitivePhysicsHypercube._generate_fall_down
            )
        elif is_move_across:
            self._last_step = last_step if last_step else LAST_STEP_MOVE_ACROSS
            self._scene_setup_function = (
                IntuitivePhysicsHypercube._generate_move_across
            )

        super().__init__(name, starter_scene, goal_template, training=training)

    @abstractmethod
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Scene
    ) -> Dict[str, Scene]:
        """Create and return a collection of new intuitive physics scenes."""
        pass

    # Override
    def _create_scenes(
        self,
        starter_scene: Scene,
        goal_template: Goal
    ) -> List[Scene]:
        default_scene = self._create_default_scene(
            starter_scene,
            goal_template
        )
        scenes = self._create_intuitive_physics_scenes(default_scene)
        for scene in scenes.values():
            # Update the scene info tags for the evaluation UI.
            scene.goal.scene_info[tags.SCENE.ID] = [
                scene_id.upper() for scene_id
                in scene.goal.scene_info[tags.SCENE.ID]
            ]
        return list(scenes.values())

    # Override
    def _get_training_scenes(self) -> List[Scene]:
        return [scene for scene in self._scenes if (
            scene.goal.answer['choice'] == PLAUSIBLE and
            (not scene.debug['evaluationOnly'])
        )]

    def _get_fall_down_object_count(self) -> int:
        """Return the number of objects for the fall-down scene."""
        # Always generate two objects for all fall-down scenes in Eval 3.
        # We may remove one or more of them later for specific scenes.
        return 2

    def _get_fall_down_occluder_count(self) -> int:
        """Return the number of occluders for the fall-down scene."""
        # Always generate two occluders for all fall-down scenes in Eval 3.
        # We may remove one or more of them later for specific scenes.
        return 2

    def _get_move_across_object_count(self) -> int:
        """Return the number of objects for the move-across scene."""
        # Always generate two objects for all move-across scenes in Eval 3.
        # We may remove one or more of them later for specific scenes.
        return 2

    def _get_move_across_occluder_count(self) -> int:
        """Return the number of occluders for the move-across scene."""
        # Always generate three occluders for all move-across scenes in Eval 3.
        # We may remove one or more of them later for specific scenes.
        return 3

    def _get_object_max_z(self) -> int:
        """Return the maximum Z position for an object."""
        return MAX_TARGET_Z

    def _get_object_min_z(self) -> int:
        """Return the minimum Z position for an object."""
        return MIN_TARGET_Z

    def _choose_all_movements(
        self,
        position: Dict[str, float],
        left_side: bool
    ) -> Optional[Dict[str, Any]]:
        """Choose and return the movement data."""

        # Whether to generate more than just move-and-exit-the-screen movement.
        option_list_property = (
            'exitStopOptionList' if self._does_have_stop_move()
            else 'exitOnlyOptionList' if (
                self._does_have_deep_move() or self._does_have_toss_move()
            ) else None
        )
        # Round the Z position because we're using it as a dict key.
        position_z = round(position['z'], 2)

        # Randomly try each available move-and-exit-the-screen movement.
        move_exit_index_list = list(range(len(MOVEMENT.MOVE_EXIT_LIST)))
        random.shuffle(move_exit_index_list)
        for index in move_exit_index_list:
            move_exit = MOVEMENT.MOVE_EXIT_LIST[index]
            # If more than one movement is needed, and the Z position isn't in
            # the option list, then this movement won't work, so skip it.
            if (
                option_list_property and
                position_z not in move_exit[option_list_property]
            ):
                logger.debug(
                    f'Move-Exit with force={move_exit["forceX"]} missing '
                    f'Z={position_z} but does have Z: '
                    f'{list(move_exit[option_list_property].keys())}'
                )
                continue

            occluder_data = self._choose_all_paired_occluder_lists(
                position['x'],
                position_z,
                move_exit,
                option_list_property,
                left_side
            )

            if not occluder_data:
                continue

            step_list, position_list, option = occluder_data

            # Ensure that both roll-across-linearly-in-depth movements have the
            # same direction as in the original movement.
            deep_exit = copy.deepcopy(
                MOVEMENT.DEEP_EXIT_LIST[option['deepExit']]
            ) if self._does_have_deep_move() else None
            deep_stop = copy.deepcopy(
                MOVEMENT.DEEP_STOP_LIST[option['deepStop']]
            ) if (
                self._does_have_stop_move() and
                self._does_have_deep_move()
            ) else None
            if deep_exit:
                deep_exit['startX'] *= (1 if left_side else -1)
                deep_exit = adjust_movement_to_position(
                    deep_exit,
                    position,
                    left_side
                )
            if deep_stop:
                deep_stop['startX'] *= (1 if left_side else -1)
                deep_stop = adjust_movement_to_position(
                    deep_stop,
                    position,
                    left_side
                ) if deep_stop else None

            # Validate that both roll-across-linearly-in-depth movements have
            # the same starting positions (This should already be done in the
            # generate_movement.py script but check again just in case!)
            if deep_exit and deep_stop and (
                deep_exit['startX'] != deep_stop['startX'] or
                deep_exit['startZ'] != deep_stop['startZ']
            ):
                logger.debug(
                    'Deep-Exit and Deep-Stop do not have same position'
                )
                continue

            # Validate that the toss-and-stop-on-screen movement is in the
            # camera's view. (This should already be done in the
            # generate_movement.py script but check again just in case!)
            toss_stop = adjust_movement_to_position(
                copy.deepcopy(MOVEMENT.TOSS_STOP_LIST[option['tossStop']]),
                position,
                left_side
            ) if (
                self._does_have_stop_move() and
                self._does_have_toss_move()
            ) else None
            if toss_stop:
                skip = False
                for step in (step_list + [toss_stop['landStep']]):
                    occluder_x = object_x_to_occluder_x(
                        toss_stop['xDistanceByStep'][step]
                        if step < len(toss_stop['xDistanceByStep']) else
                        toss_stop['xDistanceByStep'][-1],
                        position_z
                    )
                    if occluder_x is None or not (
                        self._validate_in_view(occluder_x)
                    ):
                        skip = True
                        break
                if skip:
                    logger.debug(
                        f'Toss-Stop with force=({toss_stop["forceX"]},'
                        f'{toss_stop["forceY"]}) not in view at step={step} '
                        f'with occluder X={occluder_x}:\n{toss_stop}'
                    )
                    continue

            # Copy the movement so we can delete and/or adjust its properties.
            # Do this here, and one-at-a-time, for better runtime performance.
            move_exit = copy.deepcopy(move_exit)

            # Delete each option list from the copy now for better performance
            # and easier debugging (we shouldn't need them any more).
            del move_exit['exitOnlyOptionList']
            del move_exit['exitStopOptionList']

            # Return the occluders' step list, occluders' position list, and
            # each movement with adjusted X and Z distances for the specific
            # starting position.
            return {
                'active': 'moveExit',
                'stepList': step_list,
                'positionList': position_list,
                'moveExit': adjust_movement_to_position(
                    move_exit,
                    position,
                    left_side
                ),
                'deepExit': deep_exit,
                'tossExit': adjust_movement_to_position(
                    copy.deepcopy(MOVEMENT.TOSS_EXIT_LIST[option['tossExit']]),
                    position,
                    left_side
                ) if self._does_have_toss_move() else None,
                'moveStop': adjust_movement_to_position(
                    copy.deepcopy(MOVEMENT.MOVE_STOP_LIST[option['moveStop']]),
                    position,
                    left_side
                ) if self._does_have_stop_move() else None,
                'deepStop': deep_stop,
                'tossStop': toss_stop
            }
        return None

    def _choose_all_paired_occluder_lists(
        self,
        starting_x: float,
        position_z: float,
        move_exit: Dict[str, Any],
        option_list_property: str,
        left_side: bool
    ) -> Optional[Tuple[List[int], List[float], Dict[str, int]]]:
        """Choose and return the implausible event step and X position lists
        for paired occluders using the given object movement and starting
        position. Return None if impossible using the given movement."""
        occluder_count = max(
            len(self._find_move_across_paired_list(None)),
            1
        )

        # Each step will correspond to the X position of a moving object.
        step_option_list = list(
            move_exit[option_list_property][position_z].items()
            if option_list_property else [
                (step, None) for step in
                range(len(move_exit['xDistanceByStep']))
            ]
        )

        # Filter the step list depending on if an occluder at that step's
        # corresponding X position is within the camera's view.
        step_position_option_list = []
        for step, option_list in step_option_list:
            position_x = starting_x + (
                (1 if left_side else -1) * move_exit['xDistanceByStep'][step]
            )

            # Adjust the X position for the occluder using the sight angle
            # from the camera so the occluder will properly hide the object
            # positioned at the given depth (Z).
            occluder_x = object_x_to_occluder_x(position_x, position_z)

            # If OK, add this step and corresponding X position to the list.
            if occluder_x is not None and self._validate_in_view(occluder_x):
                step_position_option_list.append((
                    step,
                    round(position_x, 4),
                    round(occluder_x, 4),
                    option_list
                ))

        if len(step_position_option_list) < occluder_count:
            logger.debug(
                f'Move-Exit with force={move_exit["forceX"]} and Z='
                f'{position_z} does not have enough occluder positions'
            )
            return None

        # Nest the list and copy if for each paired occluder.
        product_input_list = [
            step_position_option_list for _ in range(occluder_count)
        ]

        # Generate and randomly order each possible combination of occluder
        # step (and corresponding X position) for each paired occluder.
        cartesian_product_list = list(itertools.product(*product_input_list))
        random.shuffle(cartesian_product_list)

        # Find a set of occluder steps/positions for each paired occluder that
        # aren't too close to one another.
        for data_list in cartesian_product_list:
            failed = False
            occluder_step_list = []
            occluder_position_list = []
            filtered_option_list = []

            for step, position_x, occluder_x, option_list in data_list:
                # Ensure new occluder won't be too close to existing occluder.
                too_close = False
                for _, previous_occluder_position_x in occluder_position_list:
                    too_close = occluders.calculate_separation_distance(
                        previous_occluder_position_x,
                        self._get_occluder_max_scale_x(),
                        occluder_x,
                        self._get_occluder_max_scale_x()
                    ) < 0
                    if too_close:
                        break
                if too_close:
                    failed = True
                    break

                if option_list:
                    previous_option_list = filtered_option_list.copy()
                    filtered_option_list = []
                    for option in option_list:
                        keep = (len(previous_option_list) == 0)
                        for previous_option in previous_option_list:
                            if previous_option == option:
                                keep = True
                                break
                        if keep:
                            filtered_option_list.append(option)
                    if not len(filtered_option_list):
                        failed = True
                        break

                occluder_step_list.append(step)
                occluder_position_list.append((position_x, occluder_x))

            # If successful, this movement will work!
            if not failed and (
                not option_list_property or len(filtered_option_list) > 0
            ):
                # Randomly choose an available option from the list.
                random.shuffle(filtered_option_list)
                return occluder_step_list, [
                    position_x for position_x, _ in occluder_position_list
                ], (
                    filtered_option_list[0] if len(filtered_option_list)
                    else None
                )

        # If unsuccessful, this movement won't work.
        logger.debug(
            f'Move-Exit with force={move_exit["forceX"]} and Z='
            f'{position_z} will have occluders too close together'
        )
        return None

    def _choose_move_across_occluder_data(
        self,
        paired_variations: TargetVariations,
        index: int
    ) -> Tuple[float, float]:
        """Return the X position and size for a paired move-across occluder."""
        paired_object = paired_variations.get(VARIATIONS.TRAINED)
        paired_size_x = paired_variations.get_max_size_x()

        occluder_min_size_x = min(
            # Add a buffer to the occluder's minimum scale to handle minor
            # changes in size or distance-by-step with switched objects.
            paired_size_x + self._get_occluder_buffer(),
            self._get_occluder_max_scale_x()
        )

        # Use an X position so that the object will be hidden behind the
        # occluder (set in _choose_all_movements).
        occluder_position_x = object_x_to_occluder_x(
            paired_object['debug']['movement']['positionList'][index],
            paired_object['shows'][0]['position']['z']
        )

        # Choose a random size.
        occluder_size_x = geometry.random_real(
            occluder_min_size_x,
            self._get_occluder_max_scale_x()
        )

        return occluder_position_x, occluder_size_x

    def _choose_object_variations(
        self,
        location: Dict[str, Any],
        index: int
    ) -> TargetVariations:
        """Return trained and untrained variations of an object definition for
        a target or non-target object positioned at the given location."""
        # Restrict the target object to a specific type, if a specific type was
        # given as input.
        role = tags.ROLES.TARGET if index == 0 else tags.ROLES.NON_TARGET
        object_type = self._role_to_type[role]

        # Choose the trained target object definition. Finalize its materials
        # and colors now, in case a different color variation is needed.
        definitions = {}
        definitions[VARIATIONS.TRAINED] = self._trained_dataset.filter_on_type(
            must_be=([object_type] if object_type else [])
        ).choose_random_definition()

        # Sometimes object variations must have colors that are completely
        # the same as or opposite to the trained variation's colors.
        material_categories = definitions[VARIATIONS.TRAINED].materialCategory
        if 'object_opposite' in material_categories:
            base_material_list = []
            for material in definitions[VARIATIONS.TRAINED].materials:
                opposite = materials.OPPOSITE_SETS[material][0]
                same = materials.OPPOSITE_SETS[opposite][0]
                base_material_list.extend([opposite, same])

            def _callback(definition: ImmutableObjectDefinition) -> bool:
                # Only use the copies of this object definition that have the
                # same or opposite colors/materials.
                return definition.materials[0] in base_material_list

            self._trained_dataset = self._trained_dataset.filter_on_custom(
                _callback
            )
            self._untrained_shape_dataset = (
                self._untrained_shape_dataset.filter_on_custom(_callback)
            )
            self._untrained_size_dataset = (
                self._untrained_size_dataset.filter_on_custom(_callback)
            )

        # trained different color
        if self._does_need_target_variations(VARIATIONS.DIFFERENT_COLOR):
            different_color_dataset = (
                self._trained_dataset.filter_on_similar_except_color(
                    definitions[VARIATIONS.TRAINED],
                    only_diagonal_size=True
                )
            )
            if not different_color_dataset.size():
                raise SceneException(
                    f'Cannot find different trained color variation for '
                    f'intuitive physics trained object definition\n'
                    f'TRAINED: {definitions[VARIATIONS.TRAINED]}')
            definitions[VARIATIONS.DIFFERENT_COLOR] = (
                different_color_dataset.choose_random_definition()
            )

        # trained different shape
        if self._does_need_target_variations(VARIATIONS.DIFFERENT_SHAPE):
            different_shape_dataset = (
                self._trained_dataset.filter_on_similar_except_shape(
                    definitions[VARIATIONS.TRAINED],
                    only_diagonal_size=True
                )
            )
            if not different_shape_dataset.size():
                raise SceneException(
                    f'Cannot find different trained shape variation for '
                    f'intuitive physics trained object definition\n'
                    f'TRAINED: {definitions[VARIATIONS.TRAINED]}')
            definitions[VARIATIONS.DIFFERENT_SHAPE] = (
                different_shape_dataset.choose_random_definition()
            )

        # trained different size
        if self._does_need_target_variations(VARIATIONS.DIFFERENT_SIZE):
            different_size_dataset = (
                self._trained_dataset.filter_on_similar_except_size(
                    definitions[VARIATIONS.TRAINED],
                    only_diagonal_size=True
                )
            )
            if not different_size_dataset.size():
                raise SceneException(
                    f'Cannot find different trained size variation for '
                    f'intuitive physics trained object definition\n'
                    f'TRAINED: {definitions[VARIATIONS.TRAINED]}')
            definitions[VARIATIONS.DIFFERENT_SIZE] = (
                different_size_dataset.choose_random_definition()
            )

        # untrained different shape
        if self._does_need_target_variations(VARIATIONS.UNTRAINED_SHAPE):
            untrained_shape_dataset = (
                self._untrained_shape_dataset.filter_on_similar_except_shape(
                    definitions[VARIATIONS.TRAINED],
                    only_diagonal_size=True
                )
            )
            if not untrained_shape_dataset.size():
                raise SceneException(
                    f'Cannot find one untrained shape variation for '
                    f'intuitive physics trained object definition\n'
                    f'TRAINED: {definitions[VARIATIONS.TRAINED]}')
            definitions[VARIATIONS.UNTRAINED_SHAPE] = (
                untrained_shape_dataset.choose_random_definition()
            )

            # untrained another different shape
            if self._does_need_target_variations(
                VARIATIONS.UNTRAINED_DIFFERENT_SHAPE
            ):
                different_untrained_shape_dataset = (
                    untrained_shape_dataset.filter_on_similar_except_shape(
                        definitions[VARIATIONS.UNTRAINED_SHAPE],
                        only_diagonal_size=True
                    )
                )
                if not different_untrained_shape_dataset.size():
                    raise SceneException(
                        f'Cannot find different (second) untrained shape '
                        f'variation for intuitive physics trained and '
                        f'untrained shape object definitions\n'
                        f'TRAINED: {definitions[VARIATIONS.TRAINED]}\n'
                        f'UNTRAINED: '
                        f'{definitions[VARIATIONS.UNTRAINED_SHAPE]}')
                definitions[VARIATIONS.UNTRAINED_DIFFERENT_SHAPE] = (
                    different_untrained_shape_dataset.choose_random_definition()  # noqa: E501
                )

            # untrained different size of untrained shape
            if self._does_need_target_variations(
                VARIATIONS.UNTRAINED_SHAPE_DIFFERENT_SIZE
            ):
                untrained_shape_different_size_dataset = (
                    self._untrained_shape_dataset.filter_on_similar_except_size(  # noqa: E501
                        definitions[VARIATIONS.UNTRAINED_SHAPE],
                        only_diagonal_size=True
                    )
                )
                if not untrained_shape_different_size_dataset.size():
                    raise SceneException(
                        f'Cannot find different (second) untrained size '
                        f'variation for intuitive physics trained and '
                        f'untrained shape object definitions\n'
                        f'TRAINED: {definitions[VARIATIONS.TRAINED]}\n'
                        f'UNTRAINED: '
                        f'{definitions[VARIATIONS.UNTRAINED_SHAPE]}')
                definitions[VARIATIONS.UNTRAINED_SHAPE_DIFFERENT_SIZE] = (
                    untrained_shape_different_size_dataset.choose_random_definition()  # noqa: E501
                )

        # untrained different size
        if self._does_need_target_variations(VARIATIONS.UNTRAINED_SIZE):
            untrained_size_dataset = (
                self._untrained_size_dataset.filter_on_similar_except_size(
                    definitions[VARIATIONS.TRAINED],
                    only_diagonal_size=True
                )
            )
            if not untrained_size_dataset.size():
                raise SceneException(
                    f'Cannot find one untrained size variation for '
                    f'intuitive physics trained object definition\n'
                    f'TRAINED: {definitions[VARIATIONS.TRAINED]}')
            definitions[VARIATIONS.UNTRAINED_SIZE] = (
                untrained_size_dataset.choose_random_definition()
            )

        return TargetVariations(definitions, location, self.is_fall_down())

    def _create_default_scene(
        self,
        starter_scene: Scene,
        goal_template: Goal
    ) -> Scene:
        """Create and return this hypercube's default scene JSON using the
        given templates that will be shared by each scene in this hypercube."""
        scene = copy.deepcopy(starter_scene)
        scene.version = 3
        scene.debug['evaluationOnly'] = False
        scene.performer_start = PERFORMER_START
        scene.intuitive_physics = True

        # Choose a new room wall material from a restricted list.
        room_wall_material_choice = copy.deepcopy(random.choice(
            random.choice(materials.INTUITIVE_PHYSICS_WALL_GROUPINGS)
        ))
        scene.wall_material = room_wall_material_choice.material
        scene.debug['wallColors'] = room_wall_material_choice.color

        scene.goal = copy.deepcopy(goal_template)
        scene.goal.answer = {
            'choice': PLAUSIBLE
        }
        scene.goal.scene_info[tags.SCENE.FALL_DOWN] = self.is_fall_down()
        scene.goal.scene_info[tags.SCENE.MOVE_ACROSS] = (
            self.is_move_across()
        )
        scene.goal.scene_info[tags.SCENE.SETUP] = (
            tags.tag_to_label(tags.SCENE.FALL_DOWN) if self.is_fall_down()
            else tags.tag_to_label(tags.SCENE.MOVE_ACROSS)
        )
        scene.goal.last_step = self._last_step
        scene.goal.action_list = [['Pass']] * scene.goal.last_step
        scene.goal.description = ''
        scene.goal.metadata = {}

        role_to_object_list = self._create_default_objects(
            room_wall_material_choice
        )
        occluder_colors = [
            color for occluder in
            role_to_object_list.get(tags.ROLES.INTUITIVE_PHYSICS_OCCLUDER, [])
            for color in occluder['debug']['color']
        ]
        scene = update_scene_objects(scene, role_to_object_list)
        scene = update_floor_and_walls(
            starter_scene,
            role_to_object_list,
            retrieve_as_list,
            [scene],
            wall_material_list=[
                copy.deepcopy(material_option)
                for material_list in materials.INTUITIVE_PHYSICS_WALL_GROUPINGS
                for material_option in material_list if all([
                    color not in occluder_colors
                    for color in material_option.color
                ])
            ]
        )[0]

        return scene

    def _create_default_objects(
        self,
        room_wall_material: MaterialTuple
    ) -> Dict[str, Any]:
        """Generate and return this hypercube's objects in a dict of roles with
        their corresponding object lists."""
        occluder_wall_material_list = (
            self._find_structural_object_material_list(room_wall_material)
        )
        moving_object_list, occluder_list = self._scene_setup_function(
            self,
            occluder_wall_material_list
        )
        # Each occluder should have the same movement/rotation.
        if len(occluder_list) > 2:
            max_scale_x = 0
            # Loop over the occluder wall objects (at each even index).
            for occluder_index in range(0, len(occluder_list), 2):
                max_scale_x = max(
                    max_scale_x,
                    occluder_list[occluder_index]['shows'][0]['scale']['x']
                )
            # Adjust each occluder's movement/rotation to use the max scale.
            for occluder_index in range(0, len(occluder_list), 2):
                occluder_list[occluder_index]
                occluders.adjust_movement_and_rotation_to_scale(
                    occluder_list[occluder_index:(occluder_index + 2)],
                    self.is_fall_down(),
                    self._last_step,
                    x_scale_override=max_scale_x
                )
        target_list, distractor_list = self._identify_targets_and_non_targets(
            moving_object_list
        )
        self._target_list = target_list
        self._distractor_list = distractor_list
        self._occluder_list = occluder_list
        # Don't generate background (context) objects for any scenes in Eval 3.
        self._background_list = []
        role_to_object_list = {}
        role_to_object_list[tags.ROLES.TARGET] = self._target_list
        role_to_object_list[tags.ROLES.NON_TARGET] = (
            self._distractor_list
        )
        role_to_object_list[tags.ROLES.INTUITIVE_PHYSICS_OCCLUDER] = (
            self._occluder_list
        )
        role_to_object_list[tags.ROLES.CONTEXT] = self._background_list
        return role_to_object_list

    def _does_have_deep_move(self) -> bool:
        """Return whether this hypercube must generate deep movement."""
        return False

    def _does_have_stop_move(self) -> bool:
        """Return whether this hypercube must generate stop movement."""
        return False

    def _does_have_toss_move(self) -> bool:
        """Return whether this hypercube must generate toss movement."""
        return False

    def _does_need_target_variations(self, variation_tag: str) -> bool:
        """Return whether this hypercube must generate a variation of the
        target object with the given tag."""
        return False

    def _find_fall_down_paired_list(self) -> List[TargetVariations]:
        """Return objects that must be paired with occluders in fall-down
        scenes."""
        return self._variations_list

    def _find_move_across_paired_list(
        self,
        target_variation: TargetVariations
    ) -> List[TargetVariations]:
        """Return objects that must be paired with occluders in move-across
        scenes."""
        return [target_variation]

    def _find_structural_object_material_list(
        self,
        room_wall_material: MaterialTuple
    ) -> List[Tuple[str, List[str]]]:
        """Find and return the material list for any structural objects in the
        scene (like occluders) that isn't the same as the room's wall
        material."""
        structural_object_material_list = []
        for material_list in materials.INTUITIVE_PHYSICS_WALL_GROUPINGS:
            filtered_material_list = []
            for material in material_list:
                if (material.material != room_wall_material.material) and all([
                    color not in room_wall_material.color
                    for color in material.color
                ]):
                    filtered_material_list.append(copy.deepcopy(material))
            structural_object_material_list.append(filtered_material_list)
        return structural_object_material_list

    def _generate_background_object_list(self) -> List[SceneObject]:
        """Generate and return the list of background (a.k.a. context) objects,
        behind the moving objects, positioned near the room's back wall."""

        def random_x(room_dimensions: Dict[str, float]) -> float:
            return geometry.random_real(-BACKGROUND_MAX_X, BACKGROUND_MAX_X)

        def random_z(room_dimensions: Dict[str, float]) -> float:
            # Choose Z values so each background object is positioned between
            # moving objects and the back wall of the room.
            return geometry.random_real(BACKGROUND_MIN_Z, BACKGROUND_MAX_Z)

        background_count = random.choices((0, 1, 2, 3, 4, 5),
                                          (50, 10, 10, 10, 10, 10))[0]
        background_object_list = []
        background_bounds_list = []
        dataset = specific_objects.get_non_pickupable_definition_dataset()

        for _ in range(background_count):
            location = None
            while not location:
                background_definition = dataset.choose_random_definition()
                location = geometry.calc_obj_pos(geometry.ORIGIN,
                                                 background_bounds_list,
                                                 background_definition,
                                                 random_x, random_z)
                if location:
                    # Ensure entire bounds is within background
                    for point in location['boundingBox'].box_xz:
                        x = point['x']
                        z = point['z']
                        if (
                            x < -BACKGROUND_MAX_X or x > BACKGROUND_MAX_X or
                            z < BACKGROUND_MIN_Z or z > BACKGROUND_MAX_Z
                        ):
                            # If not, reset and try again
                            location = None
                            del background_bounds_list[-1]
                            break
            background_object = instances.instantiate_object(
                background_definition,
                location
            )
            background_object_list.append(background_object)
            background_bounds_list.append(location['boundingBox'])

        return background_object_list

    def _generate_fall_down(
        self,
        occluder_wall_material_list: List[List[Tuple]]
    ) -> Tuple[List[SceneObject], List[SceneObject]]:
        """Generate and return fall-down objects and occluders."""
        object_list = None
        occluder_list = None
        latest_exception = None
        for _ in range(MAX_TRIES):
            try:
                object_list = self._generate_fall_down_object_list()
                occluder_list = self._generate_fall_down_paired_occluder_list(
                    occluder_wall_material_list
                )
                self._generate_occluder_list(
                    self._get_fall_down_occluder_count() -
                    int(len(occluder_list) / 2),
                    occluder_list,
                    occluder_wall_material_list,
                    True
                )
                break
            except SceneException as e:
                latest_exception = e
        if not object_list or not occluder_list:
            raise latest_exception from latest_exception
        return object_list, occluder_list

    def _generate_fall_down_object_list(self) -> List[SceneObject]:
        """Generate and return fall-down objects."""
        object_list = []
        self._variations_list = []

        # Use roughly the same show step-begin on each fall-down object.
        latest_action_step = (
            self._last_step - occluders.OCCLUDER_MOVEMENT_TIME -
            OBJECT_FALL_TIME
        )
        show_step = random.randint(EARLIEST_ACTION_STEP, latest_action_step)
        occluder_default_max_x = occluders.OCCLUDER_MAX_X - (
            self._get_occluder_max_scale_x() / 2.0
        )

        for i in range(self._get_fall_down_object_count()):
            successful = False
            for _ in range(MAX_TRIES):
                # Ensure the random X position is within the camera's view.
                x_position = geometry.random_real(
                    -occluder_default_max_x,
                    occluder_default_max_x
                )

                z_position = choose_position_z(
                    self._get_object_min_z(),
                    self._get_object_max_z()
                )

                # Each object must have an occluder so ensure that they're each
                # positioned far enough away from one another.
                too_close = False
                for instance in object_list:
                    too_close = occluders.calculate_separation_distance(
                        object_x_to_occluder_x(x_position, z_position),
                        self._get_occluder_max_scale_x(),
                        object_x_to_occluder_x(
                            instance['shows'][0]['position']['x'],
                            instance['shows'][0]['position']['z']
                        ),
                        self._get_occluder_max_scale_x()
                    ) < 0
                    if too_close:
                        break
                if not too_close:
                    successful = True
                    break
            if not successful:
                raise SceneException(
                    f'Cannot position object to fall down object_list='
                    f'{object_list}')

            object_location = {
                'position': {
                    'x': x_position,
                    'y': retrieve_off_screen_position_y(z_position),
                    'z': z_position
                }
            }

            # Add minor variation to this object's show step.
            object_show_step = random.randint(
                max(EARLIEST_ACTION_STEP, show_step - 1),
                min(latest_action_step, show_step + 1)
            )

            variations = self._choose_object_variations(object_location, i)
            for instance in variations.all():
                instance['shows'][0]['stepBegin'] = object_show_step

            object_list.append(variations.get(VARIATIONS.TRAINED))
            self._variations_list.append(variations)

        return object_list

    def _generate_fall_down_paired_occluder(
        self,
        paired_variations: TargetVariations,
        occluder_list: List[SceneObject],
        occluder_wall_material_list: List[List[Tuple]]
    ) -> List[SceneObject]:
        """Generate and return one fall-down paired occluder that must be
        positioned underneath the paired object."""
        paired_object = paired_variations.get(VARIATIONS.TRAINED)
        paired_x = paired_object['shows'][0]['position']['x']
        paired_size = paired_variations.get_max_size_x()
        occluder_max_size_x = self._get_occluder_max_scale_x()
        occluder_min_size_x = min(
            # Add a buffer to the occluder's minimum scale to handle minor
            # changes in size or position-by-step with switched objects.
            paired_size + self._get_occluder_buffer(),
            occluder_max_size_x
        )

        # Adjust the X position using the sight angle from the camera
        # to the object so an occluder will properly hide the object.
        paired_z = paired_object['shows'][0]['position']['z']
        x_position = object_x_to_occluder_x(paired_x, paired_z)

        for occluder in occluder_list:
            if occluder['debug']['shape'] == ['pole']:
                continue
            occluder_x = occluder['shows'][0]['position']['x']
            occluder_size = occluder['shows'][0]['scale']['x']
            # Ensure that each occluder is positioned far enough away from one
            # another (this should be done previously, but check again).
            distance = occluders.calculate_separation_distance(
                occluder_x,
                occluder_size,
                x_position,
                paired_size
            )
            if distance < 0:
                logger.debug(
                    f'OBJECT={paired_object}\nOCCLUDER_LIST={occluder_list}'
                )
                raise SceneException(
                    f'Two fall-down objects were positioned too close '
                    f'distance={distance} object_position={x_position} '
                    f'object_size={paired_size} '
                    f'occluder_position={occluder_x} '
                    f'occluder_size={occluder_size}')
            if distance < (occluder_max_size_x - occluder_min_size_x):
                occluder_max_size_x = occluder_min_size_x + distance

        # Choose a random size.
        if occluder_max_size_x <= occluder_min_size_x:
            x_scale = occluder_min_size_x
        else:
            x_scale = geometry.random_real(
                occluder_min_size_x,
                occluder_max_size_x
            )

        # Choose a left or right sideways pole based on its X position.
        sideways_left = (x_position < 0)
        # If a previous occluder exists, we may need to change our choice.
        if len(occluder_list) > 0:
            # Assume a max of two occluders in fall-down scenes.
            previous_wall = occluder_list[0]
            previous_pole = occluder_list[1]
            previous_x = previous_wall['shows'][0]['position']['x']
            # If both occluders are positioned on the same side of the scene...
            if (
                (sideways_left and previous_x < 0) or
                (not sideways_left and previous_x >= 0)
            ):
                # If the new occluder is closer to the center of the scene than
                # the previous occluder, just change the side its pole is on.
                if (
                    (sideways_left and x_position > previous_x) or
                    (not sideways_left and x_position < previous_x)
                ):
                    sideways_left = (not sideways_left)
                # Else, change the side the previous occluder's pole is on.
                else:
                    previous_pole['shows'][0]['position']['x'] = (
                        occluders.generate_sideways_pole_position_x(
                            previous_wall['shows'][0]['position']['x'],
                            previous_wall['shows'][0]['scale']['x'],
                            (not sideways_left)
                        )
                    )

        return occluders.create_occluder(
            copy.deepcopy(random.choice(random.choice(
                occluder_wall_material_list
            ))),
            copy.deepcopy(random.choice(materials.METAL_MATERIALS)),
            x_position,
            x_scale,
            last_step=self._last_step,
            occluder_height=self._get_occluder_height(),
            sideways_left=sideways_left,
            sideways_right=(not sideways_left)
        )

    def _generate_fall_down_paired_occluder_list(
        self,
        occluder_wall_material_list: List[List[Tuple]]
    ) -> List[SceneObject]:
        """Generate and return needed fall-down paired occluders."""
        paired_list = self._find_fall_down_paired_list()
        occluder_list = []
        for paired_variations in paired_list:
            occluder = self._generate_fall_down_paired_occluder(
                paired_variations,
                occluder_list,
                occluder_wall_material_list
            )
            if not occluder:
                raise SceneException(
                    f'Cannot create fall-down paired occluder object='
                    f'{paired_variations.get("trained")} '
                    f'occluder_list={occluder_list}')
            occluder_list.extend(occluder)
        return occluder_list

    def _generate_move_across(
        self,
        occluder_wall_material_list: List[List[Tuple]]
    ) -> Tuple[List[SceneObject], List[SceneObject]]:
        """Generate and return move-across objects and occluders."""
        object_list = None
        occluder_list = None
        latest_exception = None
        object_list = self._generate_move_across_object_list(
            self._last_step - occluders.OCCLUDER_MOVEMENT_TIME
        )
        for _ in range(MAX_TRIES):
            try:
                occluder_list = (
                    self._generate_move_across_paired_occluder_list(
                        object_list,
                        occluder_wall_material_list
                    )
                )
                self._generate_occluder_list(
                    self._get_move_across_occluder_count() -
                    int(len(occluder_list) / 2),
                    occluder_list,
                    occluder_wall_material_list,
                    False
                )
                break
            except SceneException as e:
                latest_exception = e
        if not object_list or not occluder_list:
            raise latest_exception from latest_exception
        return object_list, occluder_list

    def _generate_move_across_object_list_helper(
        self,
        left_side: bool
    ) -> Tuple[List, List, float]:
        """Helper function for _generate_move_across_object_list. Returns an
        object_list, a variations_list, and a max_movement, in that order."""
        max_movement = 0
        object_list = []
        variations_list = []

        for i in range(self._get_move_across_object_count()):
            move_dict = None
            for _ in range(MAX_TRIES):
                # Choose the object's position and define its location.
                object_position = choose_move_across_object_position(
                    left_side,
                    object_list,
                    min_z=self._get_object_min_z(),
                    max_z=self._get_object_max_z()
                )
                if object_position is None:
                    continue
                object_location = {
                    'position': object_position
                }

                # Choose the object's movement to set its default
                # variation's forces and starting Y position.
                move_dict = self._choose_all_movements(
                    object_position,
                    left_side
                )
                if move_dict:
                    break
            if not move_dict:
                raise SceneException(
                    f'Cannot find a valid movement option for object '
                    f'number {i + 1} after max try count: '
                    f'{object_position=} {left_side=} '
                    f'deep_move={self._does_have_deep_move()} '
                    f'stop_move={self._does_have_stop_move()} '
                    f'toss_move={self._does_have_toss_move()} '
                )

            max_movement = max(
                max_movement,
                len(move_dict[move_dict['active']]['xDistanceByStep'])
            )

            # Create the object and its variations.
            variations = self._choose_object_variations(object_location, i)

            for instance in variations.all():
                instance['debug']['movement'] = move_dict

            object_list.append(variations.get(VARIATIONS.TRAINED))
            variations_list.append(variations)

        return object_list, variations_list, max_movement

    def _generate_move_across_object_list(
        self,
        last_action_step: int
    ) -> List[SceneObject]:
        """Generate and return move-across objects."""
        object_count = self._get_move_across_object_count()

        # Each move-across object enters from the same side in Eval 3.
        left_side = random.choice([True, False])

        max_movement = 0
        object_list = []
        self._variations_list = []
        last_exception = None

        for _ in range(MAX_TRIES):
            try:
                data = self._generate_move_across_object_list_helper(left_side)
                object_list, variations_list, max_movement = data
                self._variations_list = variations_list
                break
            except SceneException as e:
                last_exception = e

        if not object_list:
            raise last_exception

        # Adjust the latest action step by the slowest chosen movement.
        latest_action_step = max(
            EARLIEST_ACTION_STEP,
            (self._last_step - occluders.OCCLUDER_MOVEMENT_TIME - max_movement)
        )

        step_separation = (5 * (object_count - 1))
        if (latest_action_step - EARLIEST_ACTION_STEP) < step_separation:
            raise SceneException(
                f'Cannot set object show step because move-across scene does '
                f'not have enough action step variance: {step_separation} '
                f'earliest={EARLIEST_ACTION_STEP} latest={latest_action_step}')

        show_step_list = []
        while len(show_step_list) < object_count:
            for i in range(object_count):
                show_step = random.randint(EARLIEST_ACTION_STEP,
                                           latest_action_step)
                redo = False
                for existing_show_step in show_step_list:
                    if (
                        show_step >= (existing_show_step - 5) and
                        show_step <= (existing_show_step + 5)
                    ):
                        redo = True
                        break
                if redo:
                    show_step_list = []
                    break
                show_step_list.append(show_step)

        for i in range(object_count):
            # Assign the needed properties to each of the object's variations.
            for instance in self._variations_list[i].all():
                instance['shows'][0]['stepBegin'] = show_step_list[i]
                movement = instance['debug']['movement'][
                    instance['debug']['movement']['active']
                ]
                instance['forces'] = [{
                    'stepBegin': show_step_list[i],
                    'stepEnd': show_step_list[i],
                    'vector': {
                        'x': movement['forceX'] * instance['mass'],
                        'y': movement.get('forceY', 0) * instance['mass'],
                        'z': movement.get('forceZ', 0) * instance['mass']
                    }
                }]

                # Reverse the force and facing if moving right-to-left.
                if not left_side:
                    instance['forces'][0]['vector']['x'] *= -1
                    # Assume all objects start facing left-to-right.
                    instance['shows'][0]['rotation']['y'] += 180

        return object_list

    def _generate_move_across_paired_occluder(
        self,
        paired_variations: TargetVariations,
        occluder_list: List[SceneObject],
        occluder_wall_material_list: List[List[Tuple]],
        index: int
    ) -> List[SceneObject]:
        """Generate and return one move-across paired occluder that must be
        positioned at one of the paired object's distance_by_step so that it
        will properly hide the paired object during the implausible event."""
        x_position, x_scale = self._choose_move_across_occluder_data(
            paired_variations,
            index
        )

        return occluders.create_occluder(
            copy.deepcopy(random.choice(random.choice(
                occluder_wall_material_list
            ))),
            copy.deepcopy(random.choice(materials.METAL_MATERIALS)),
            x_position,
            x_scale,
            last_step=self._last_step,
            occluder_height=self._get_occluder_height()
        )

    def _generate_move_across_paired_occluder_list(
        self,
        object_list: List[SceneObject],
        occluder_wall_material_list: List[List[Tuple]]
    ) -> List[SceneObject]:
        """Generate and return needed move-across paired occluders."""
        paired_list = self._find_move_across_paired_list(
            self._variations_list[0]
        )
        occluder_list = []
        for index, paired_variations in enumerate(paired_list):
            occluder = self._generate_move_across_paired_occluder(
                paired_variations,
                occluder_list,
                occluder_wall_material_list,
                index
            )
            if not occluder:
                raise SceneException(
                    f'Cannot create move-across paired object='
                    f'{paired_variations.get("trained")} '
                    f'occluder_list={occluder_list}')
            occluder_list.extend(occluder)
        return occluder_list

    def _generate_occluder(
        self,
        occluder_list: List[SceneObject],
        occluder_wall_material_list: List[List[Tuple]],
        sideways: bool
    ) -> List[SceneObject]:
        """Generate and return a single occluder."""
        successful = False
        for _ in range(MAX_TRIES):
            # Choose a random size.
            x_scale = geometry.random_real(
                occluders.OCCLUDER_MIN_SCALE_X,
                self._get_occluder_max_scale_x()
            )
            x_position = occluders.generate_occluder_position(x_scale,
                                                              occluder_list)
            if x_position is not None:
                successful = True
                break
        if successful:
            # Choose a left or right sideways pole based on its X position.
            sideways_left = (x_position < 0) if self.is_fall_down() else False
            sideways_right = (
                (not sideways_left) if self.is_fall_down() else False
            )
            return occluders.create_occluder(
                copy.deepcopy(random.choice(random.choice(
                    occluder_wall_material_list
                ))),
                copy.deepcopy(random.choice(materials.METAL_MATERIALS)),
                x_position,
                x_scale,
                last_step=self._last_step,
                occluder_height=self._get_occluder_height(),
                sideways_left=sideways_left,
                sideways_right=sideways_right
            )
        return None

    def _generate_occluder_list(
        self,
        number: int,
        occluder_list: List[SceneObject],
        occluder_wall_material_list: List[List[Tuple]],
        sideways: bool
    ) -> None:
        """Generate occluders and add them to the given occluder_list."""
        for _ in range(number):
            occluder = self._generate_occluder(occluder_list,
                                               occluder_wall_material_list,
                                               sideways)
            if not occluder:
                raise SceneException(
                    f'Cannot create occluder number {len(occluder_list) + 1} '
                    f'within existing occluder_list={occluder_list}')
            occluder_list.extend(occluder)

    def _get_occluder_buffer(self) -> int:
        """Return the occluder buffer to use."""
        if self._does_have_stop_move():
            # Increase the buffer for any hypercubes with the stop movement
            # due to greater variability in the speed of rolling objects.
            return occluders.OCCLUDER_BUFFER_EXIT_AND_STOP
        if not (self._does_have_deep_move() or self._does_have_toss_move()):
            # Decrease the buffer for any hypercubes with only normal movement
            # since we do not need to cross reference multiple movement.
            return occluders.OCCLUDER_BUFFER
        return occluders.OCCLUDER_BUFFER_MULTIPLE_EXIT

    def _get_occluder_height(self) -> int:
        """Return the occluder height to use."""
        return occluders.OCCLUDER_HEIGHT

    def _get_occluder_max_scale_x(self) -> float:
        """Return the occluder's max scale X."""
        return occluders.OCCLUDER_MAX_SCALE_X + self._get_occluder_buffer()

    def _init_each_object_definition_list(
        self,
        is_fall_down: bool,
        only_basic_shapes: bool,
        only_complex_shapes: bool
    ) -> None:
        """Set each object definition list needed by this hypercube, used in
        _choose_object_variations."""

        if only_basic_shapes:
            complex_shapes = False
        elif only_complex_shapes:
            complex_shapes = True
        else:
            complex_shapes = random.choice([True, True, True, False])

        # List with each possible intuitive physics object definition (shape)
        # and material (color) combination for the specific scene setup.
        definition_dataset = self._retrieve_definition_data(
            is_fall_down,
            complex_shapes
        )
        self._trained_dataset = definition_dataset.filter_on_trained()
        self._untrained_shape_dataset = definition_dataset.filter_on_untrained(
            tags.SCENE.UNTRAINED_SHAPE
        )
        self._untrained_size_dataset = definition_dataset.filter_on_untrained(
            tags.SCENE.UNTRAINED_SIZE
        )

    def _identify_targets_and_non_targets(
        self,
        moving_object_list: List[SceneObject]
    ) -> Tuple[List[SceneObject], List[SceneObject]]:
        """Return the two separate target and non-target lists using the given
        moving object list."""
        return moving_object_list, []

    def _retrieve_definition_data(
        self,
        is_fall_down: bool,
        complex_shapes: bool
    ) -> DefinitionDataset:
        """Return the full base object definition dataset for the hypercube."""
        if complex_shapes:
            return (
                get_fall_down_complex_shape_definition_dataset()
                if is_fall_down else
                get_move_across_complex_shape_definition_dataset()
            )
        return (
            get_fall_down_basic_shape_definition_dataset()
            if is_fall_down else
            get_move_across_basic_shape_definition_dataset()
        )

    def _update_object_tags(
        self,
        scene: Scene,
        object_list: List[SceneObject],
        role: str
    ) -> Scene:
        """Update and return the given scene with info from targets in the
        given list because targets were added or removed."""

        important_tag_list = [
            tags.SCENE.TRAINED, tags.SCENE.TRAINED_COLOR,
            tags.SCENE.TRAINED_COMBINATION, tags.SCENE.TRAINED_SHAPE,
            tags.SCENE.TRAINED_SIZE, tags.SCENE.UNTRAINED,
            tags.SCENE.UNTRAINED_COLOR, tags.SCENE.UNTRAINED_COMBINATION,
            tags.SCENE.UNTRAINED_SHAPE, tags.SCENE.UNTRAINED_SIZE
        ]

        for tag in important_tag_list:
            scene.goal.scene_info[tag][tags.role_to_key(role)] = False

        scene.goal.objects_info['all'] = []
        scene.goal.objects_info[tags.role_to_key(role)] = []

        for instance in object_list:
            role_to_object_list = {}
            role_to_object_list[role] = object_list
            tags.append_object_tags_of_type(
                scene.goal.scene_info,
                scene.goal.objects_info,
                role_to_object_list,
                role
            )
            scene.goal.objects_info[tags.role_to_key(role)].extend(
                instance['debug']['info']
            )
            instance['debug']['info'].append(role)
            instance['debug']['role'] = role
            instance['debug'][tags.role_to_tag(role)] = True

        scene = update_scene_objects_tag_lists(scene)
        return scene

    def _update_hypercube_scene_info_tags(
        self,
        scenes: Dict[str, Scene]
    ) -> Dict[str, Any]:
        """Update and return the hypercube and target tags in each scene from
        the given scene dictionary."""

        for scene_id, scene in scenes.items():
            # Update the target-specific and non-target-specific scene tags
            # since a target or non-target may have been changed or added.
            for role in [tags.ROLES.TARGET, tags.ROLES.NON_TARGET]:
                self._update_object_tags(scene, [
                    instance for instance in scene.objects
                    if instance['debug']['role'] == role
                ], role)

            scene.goal.scene_info[tags.SCENE.ID] = [scene_id]
            scene.goal.scene_info[tags.SCENE.TIPSY] = False
            for obj in scene.objects:
                if obj['type'] in TIPSY_OBJECT_TYPES:
                    scene.goal.scene_info[tags.SCENE.TIPSY] = True

    def _validate_in_view(
        self,
        occluder_x: float,
        occluder_size_x: float = None
    ) -> bool:
        """Return whether the given X position is within view of the camera."""
        return validate_in_view(
            occluder_x,
            occluder_size_x=(
                occluder_size_x or self._get_occluder_max_scale_x()
            )
        )

    def is_fall_down(self) -> bool:
        """Return if this is a fall-down hypercube."""
        return self._scene_setup_function == (
            IntuitivePhysicsHypercube._generate_fall_down
        )

    def is_move_across(self) -> bool:
        """Return if this is a move-across hypercube."""
        return self._scene_setup_function == (
            IntuitivePhysicsHypercube._generate_move_across
        )


class CollisionsHypercube(IntuitivePhysicsHypercube):
    def __init__(
        self,
        starter_scene: Scene,
        role_to_type: Dict[str, str],
        training=False,
        last_step=None
    ):
        # If the target object is near the camera (50% of hypercubes).
        self._is_target_near = random.choice([True, False])
        super().__init__(
            tags.ABBREV.COLLISIONS.upper(),
            starter_scene,
            tags.TASKS.COLLISIONS,
            role_to_type,
            # Collision scenes are always move-across.
            is_fall_down=False,
            is_move_across=True,
            training=training,
            last_step=last_step
        )

    def _adjust_impact_position(
        self,
        target: SceneObject,
        non_target: SceneObject
    ) -> Dict[str, Any]:
        """Find and return an X position for the given non-target object so
        that the target object will impact the non-target object at the exact
        end/beginning of a step."""
        left_side = (target['shows'][0]['position']['x'] < 0)
        separation = (
            target['debug']['dimensions']['x'] +
            non_target['debug']['dimensions']['x']
        ) / 2.0
        base_position = target['debug']['movement']['positionList'][0]
        for position in (
            target['debug']['movement']['moveExit']['xDistanceByStep']
        ):
            if left_side and (position + separation >= base_position):
                break
            if not left_side and (position - separation <= base_position):
                break
        return position + (separation if left_side else -separation)

    # Override
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Scene
    ) -> Dict[str, Scene]:
        """Create and return a collection of new intuitive physics scenes."""
        target_variations = self._variations_list[0]
        target_trained = target_variations.get(VARIATIONS.TRAINED)

        non_target_variations = self._variations_list[1]
        non_target_trained = non_target_variations.get(VARIATIONS.TRAINED)

        # Initialize individual hypercube scenes.
        scenes = {}
        for i in ['a', 'c', 'h']:
            scenes[i + '2'] = copy.deepcopy(default_scene)

        # Initialize default collision tags in scenes.
        for scene in scenes.values():
            scene.goal.scene_info[
                tags.TYPES.COLLISIONS_MOVES
            ] = tags.CELLS.COLLISIONS_MOVES.ONE
            scene.goal.scene_info[
                tags.TYPES.COLLISIONS_OCCLUDERS
            ] = tags.CELLS.COLLISIONS_OCCLUDERS.NO
            scene.goal.scene_info[
                tags.TYPES.COLLISIONS_TRAINED
            ] = tags.CELLS.COLLISIONS_TRAINED.YES
            scene.goal.scene_info[
                tags.TYPES.COLLISIONS_REVEALS
            ] = tags.CELLS.COLLISIONS_REVEALS.EMPTY
            # Remove the occluder from each scene.
            remove_id_list = [
                occluder['id'] for occluder in self._occluder_list
            ]
            scene.objects = [
                instance for instance in scene.objects
                if instance['id'] not in remove_id_list
            ]

        # Remove the non-target object from the scene.
        scene = scenes['a2']
        scene.goal.scene_info[
            tags.TYPES.COLLISIONS_REVEALS
        ] = tags.CELLS.COLLISIONS_REVEALS.EMPTY
        objects = scene.objects
        for index in range(len(objects)):
            if objects[index]['id'] == non_target_trained['id']:
                del objects[index]
                break

        # Reposition the non-target object to the target object's Z position.
        scene = scenes['h2']
        scene.goal.scene_info[
            tags.TYPES.COLLISIONS_MOVES
        ] = tags.CELLS.COLLISIONS_MOVES.TWO
        scene.goal.scene_info[
            tags.TYPES.COLLISIONS_REVEALS
        ] = tags.CELLS.COLLISIONS_REVEALS.ON_PATH
        for instance in scene.objects:
            if instance['id'] == non_target_trained['id']:
                instance['shows'][0]['position']['x'] = (
                    self._adjust_impact_position(target_trained, instance)
                )
                instance['shows'][0]['position']['z'] = (
                    target_trained['shows'][0]['position']['z']
                )
                break

        # Finalize scenes.
        self._update_hypercube_scene_info_tags(scenes)

        return scenes

    # Override
    def _get_slices(self) -> List[str]:
        return [
            tags.TYPES.COLLISIONS_MOVES,
            tags.TYPES.COLLISIONS_OCCLUDERS,
            tags.TYPES.COLLISIONS_REVEALS,
            tags.TYPES.COLLISIONS_TRAINED
        ]

    # Override
    def _does_need_target_variations(self, variation_tag: str) -> bool:
        """Return whether this hypercube must generate a variation of the
        target object with the given tag."""
        return (
            variation_tag == VARIATIONS.UNTRAINED_SHAPE or
            variation_tag == VARIATIONS.DIFFERENT_COLOR
        )

    # Override
    def _get_move_across_object_count(self) -> int:
        """Return the number of objects for the move-across scene."""
        return 1

    # Override
    def _get_move_across_occluder_count(self) -> int:
        """Return the number of occluders for the move-across scene."""
        return 1

    # Override
    def _get_object_max_z(self) -> int:
        """Return the maximum Z position for an object."""
        if self._is_target_near:
            # The target should not be positioned past the first quarter.
            return MIN_TARGET_Z + (MAX_TARGET_Z_EXTENDED / 4.0)
        return MAX_TARGET_Z_EXTENDED

    # Override
    def _get_object_min_z(self) -> int:
        """Return the minimum Z position for an object."""
        if self._is_target_near:
            return MIN_TARGET_Z
        # The target should not be positioned in front of the final quarter.
        return MAX_TARGET_Z_EXTENDED - (MAX_TARGET_Z_EXTENDED / 4.0)

    # Override
    def _identify_targets_and_non_targets(
        self,
        target_object_list: List[SceneObject]
    ) -> Tuple[List[SceneObject], List[SceneObject]]:
        """Return the two separate target and non-target lists using the given
        moving object list."""
        target_variations = self._variations_list[0]
        target_trained = target_variations.get(VARIATIONS.TRAINED)
        target_untrained = target_variations.get(VARIATIONS.UNTRAINED_SHAPE)

        # Adjust the target's speed to ensure the non-target exits the screen.
        speed = random.choice(COLLISION_SPEEDS)
        for target in [target_trained, target_untrained]:
            target['forces'][0]['vector']['x'] = speed * target['mass'] * (
                -1 if target['forces'][0]['vector']['x'] < 0 else 1
            )

        # Create the non-target using the target's different color variation.
        non_target_trained = copy.deepcopy(
            target_variations.get(VARIATIONS.DIFFERENT_COLOR)
        )
        non_target_trained['id'] = str(uuid.uuid4())
        non_target_trained['debug']['role'] = tags.ROLES.NON_TARGET
        non_target_trained['forces'] = []
        non_target_trained['shows'][0]['stepBegin'] = 0

        # Move the non-target to a Z position opposite from the target: if
        # _is_target_near, then the non-target should be far, and visa-versa.
        # (We may move it again in specific scenes later.)
        non_target_trained['shows'][0]['position']['z'] = choose_position_z(
            (MAX_TARGET_Z_EXTENDED - (MAX_TARGET_Z_EXTENDED / 4.0))
            if self._is_target_near else MIN_TARGET_Z,
            MAX_TARGET_Z_EXTENDED if self._is_target_near else
            (MIN_TARGET_Z + (MAX_TARGET_Z_EXTENDED / 4.0))
        )

        # Move the non-target to an X position directly behind the occluder.
        # (We may move it again in specific scenes later)
        non_target_trained['shows'][0]['position']['x'] = (
            occluder_x_to_object_x(
                object_x_to_occluder_x(
                    self._adjust_impact_position(
                        target_trained,
                        non_target_trained
                    ),
                    target_trained['shows'][0]['position']['z']
                ),
                non_target_trained['shows'][0]['position']['z']
            )
        )

        # Create the untrained shape non-target.
        non_target_untrained = copy.deepcopy(target_untrained)
        non_target_untrained['id'] = non_target_trained['id']
        non_target_untrained['debug']['role'] = (
            non_target_trained['debug']['role']
        )
        non_target_untrained['forces'] = []
        non_target_untrained['shows'][0]['stepBegin'] = 0
        non_target_untrained['shows'][0]['position']['x'] = (
            non_target_trained['shows'][0]['position']['x']
        )
        non_target_untrained['shows'][0]['position']['z'] = (
            non_target_trained['shows'][0]['position']['z']
        )
        non_target_untrained['debug']['color'] = (
            non_target_trained['debug']['color']
        )
        # Set the correct number of material strings needed by
        # the untrained shape in its 'materials' array.
        # Assume all intuitive physics objects that need more
        # than one material string will use the same material
        # string as each element in the array.
        non_target_untrained['materials'] = (
            [non_target_trained['materials'][0]] *
            len(non_target_untrained['materials'])
        )

        # Save the non-target's variations for later use.
        non_target_instances = {}
        non_target_instances[VARIATIONS.TRAINED] = non_target_trained
        non_target_instances[VARIATIONS.UNTRAINED_SHAPE] = non_target_untrained
        self._variations_list.append(ObjectVariations(non_target_instances))
        return target_object_list, [non_target_trained]

    # Override
    def _init_each_object_definition_list(
        self,
        is_fall_down: bool,
        only_basic_shapes: bool,
        only_complex_shapes: bool
    ) -> None:
        """Set each object definition list needed by this hypercube, used in
        _choose_object_variations."""

        super()._init_each_object_definition_list(
            is_fall_down,
            only_basic_shapes,
            only_complex_shapes
        )

        # Don't use balls/spheres in Eval 4 Collision/OP/STC hypercubes.
        # They don't completely stop upon collision, so they roll out into view
        # from behind the occluder.
        self._trained_dataset = self._trained_dataset.filter_on_type(
            cannot_be=['ball', 'sphere']
        )
        self._untrained_shape_dataset = (
            self._untrained_shape_dataset.filter_on_type(
                cannot_be=['ball', 'sphere']
            )
        )
        self._untrained_size_dataset = (
            self._untrained_size_dataset.filter_on_type(
                cannot_be=['ball', 'sphere']
            )
        )

    # Override
    def _retrieve_definition_data(
        self,
        is_fall_down: bool,
        complex_shapes: bool
    ) -> DefinitionDataset:
        """Return the full base object definition dataset for the hypercube."""
        if complex_shapes:
            return (
                get_fall_down_complex_shape_opposite_colors_definition_dataset()  # noqa: E501
                if is_fall_down else
                get_move_across_complex_shape_opposite_colors_definition_dataset()  # noqa: E501
            )
        return (
            get_fall_down_basic_shape_opposite_colors_definition_dataset()
            if is_fall_down else
            get_move_across_basic_shape_opposite_colors_definition_dataset()
        )

    # Override
    def _validate_in_view(
        self,
        occluder_x: float,
        occluder_size_x: float = None
    ) -> bool:
        """Return whether the given X position is within view of the camera."""
        # Use a buffer because we'll increase the size of the occluder later.
        max_x = occluders.OCCLUDER_MAX_X - occluders.OCCLUDER_MAX_SCALE_X
        return validate_in_view(
            occluder_x,
            -max_x,
            max_x,
            occluder_size_x or self._get_occluder_max_scale_x()
        )


class GravitySupportHypercube(IntuitivePhysicsHypercube):
    def __init__(
        self,
        starter_scene: Scene,
        role_to_type: Dict[str, str],
        training=False,
        is_fall_down=False,
        is_move_across=False
    ):
        super().__init__(
            tags.ABBREV.GRAVITY_SUPPORT.upper(),
            starter_scene,
            tags.TASKS.GRAVITY_SUPPORT,
            role_to_type,
            # All gravity support scenes are fall-down in Eval 4.
            is_fall_down=True,
            is_move_across=False,
            training=training,
            last_step=100
        )

    # Override
    def _create_default_objects(
        self,
        room_wall_material: MaterialTuple
    ) -> SceneObject:
        """Generate and return this hypercube's objects in a dict of roles with
        their corresponding object lists."""

        self._target = self._create_gravity_support_target()
        structural_object_material_list = (
            self._find_structural_object_material_list(room_wall_material)
        )
        self._visible_support = self._create_visible_support_object(
            self._target,
            structural_object_material_list
        )

        for instance in self._target.all():
            # The bottom of the target object must be off-screen.
            min_height = retrieve_off_screen_position_y(
                instance['shows'][0]['position']['z']
            )
            # Adjust the target's starting Y position by the visible support's
            # size so the target ends its movement directly above the visible
            # support. (Subtract 0.5 because that's the minimum support size.)
            start_height = (
                min_height + instance['debug']['dimensions']['y'] +
                self._visible_support['debug']['dimensions']['y'] - 0.5
            )

            # Add downward movement and other properties to target.
            mechanisms.place_object(
                instance=instance,
                activation_step=instance['shows'][0]['stepBegin'],
                start_height=start_height,
                end_height=self._visible_support['debug']['dimensions']['y']
            )

        self._pole = self._create_pole(self._target, self._visible_support)

        # Save the default objects. These objects will be replaced as needed in
        # _create_intuitive_physics_scenes.
        role_to_object_list = {}
        role_to_object_list[tags.ROLES.TARGET] = [
            self._target.get(VARIATIONS.SYMMETRIC)
        ]
        role_to_object_list[tags.ROLES.STRUCTURAL] = [
            self._pole.get(VARIATIONS.SYMMETRIC), self._visible_support
        ]
        return role_to_object_list

    # Override
    def _init_each_object_definition_list(
        self,
        is_fall_down: bool,
        only_basic_shapes: bool,
        only_complex_shapes: bool
    ) -> None:
        """Set each object definition list needed by this hypercube, used in
        _choose_object_variations."""
        # Not used since we override _create_default_objects.
        pass

    def _create_gravity_support_target(self) -> TargetVariations:
        # Retrieve each base target object definition lists.
        symmetric_dataset = (
            gravity_support_objects.get_symmetric_target_definition_dataset()
        )

        # Restrict object to a specific type, if type was given as input.
        symmetric_object_type = self._role_to_type.get('symmetric')
        asymmetric_object_type = self._role_to_type.get('asymmetric')

        # Choose symmetric target object definition.
        definitions = {}
        definitions[VARIATIONS.SYMMETRIC] = symmetric_dataset.filter_on_type(
            must_be=([symmetric_object_type] if symmetric_object_type else [])
        ).choose_random_definition()

        # Restrict asymmetric target object definition to same size/material.
        asymmetric_dataset = (
            gravity_support_objects.get_asymmetric_target_definition_dataset()
        ).filter_on_similar_except_shape(
            definitions[VARIATIONS.SYMMETRIC],
            only_diagonal_size=True
        )

        if not asymmetric_dataset.size():
            raise SceneException(
                f'Intuitive physics gravity support symmetric object does not '
                f'have any asymmetric shapes with the same size and material: '
                f'{definitions[VARIATIONS.SYMMETRIC]}')

        # Choose asymmetric target object definition.
        definitions[VARIATIONS.ASYMMETRIC_LEFT] = (
            asymmetric_dataset.filter_on_type(must_be=(
                [asymmetric_object_type] if asymmetric_object_type else []
            ))
        ).choose_random_definition()

        # Copy the asymmetric target object to add a reversed definition.
        # (We'll rotate the reversed instance later.)
        definitions[VARIATIONS.ASYMMETRIC_RIGHT] = copy.deepcopy(
            definitions[VARIATIONS.ASYMMETRIC_LEFT]
        )

        # Choose target object location.
        target_z_position = choose_position_z(MIN_TARGET_Z, MAX_TARGET_Z)
        target_location = {
            'position': {
                'x': random.randrange(
                    round(-GRAVITY_SUPPORT_MAX_ONSCREEN_X * 100),
                    round(GRAVITY_SUPPORT_MAX_ONSCREEN_X * 100),
                    5
                ) / 100.0,
                # The target's Y position will be adjusted later.
                'y': 0,
                'z': target_z_position
            }
        }

        target_variations = TargetVariations(
            definitions,
            target_location,
            self.is_fall_down()
        )

        # Rotate the asymmetric target instance so it's reversed.
        reversed_instance = target_variations.get(VARIATIONS.ASYMMETRIC_RIGHT)
        reversed_instance['shows'][0]['rotation']['y'] += 180

        # Choose step to appear and start downward movement.
        show_step = random.randint(1, 21)

        for instance in target_variations.all():
            instance['shows'][0]['stepBegin'] = show_step

        return target_variations

    def _create_pole(
        self,
        target_variations: TargetVariations,
        visible_support: SceneObject
    ) -> ObjectVariations:
        target_symmetric = target_variations.get(VARIATIONS.SYMMETRIC)
        target_asymmetric_left = target_variations.get(
            VARIATIONS.ASYMMETRIC_LEFT
        )
        target_asymmetric_right = target_variations.get(
            VARIATIONS.ASYMMETRIC_RIGHT
        )
        pole_id = 'placer_' + str(uuid.uuid4())

        # Create a pole variation for all target variations.
        pole_instances = {}
        for name, target, multiplier in [
            (VARIATIONS.SYMMETRIC, target_symmetric, 0),
            (VARIATIONS.ASYMMETRIC_LEFT, target_asymmetric_left, 1),
            (VARIATIONS.ASYMMETRIC_RIGHT, target_asymmetric_right, -1)
        ]:
            target_definition = target_variations._definitions[name]
            # Assume all gravity support objects will only need one placer.
            placer_offset_x = (target_definition.placerOffsetX or [0])[0]
            placer_offset_y = (target_definition.placerOffsetY or [0])[0]
            pole_instances[name] = mechanisms.create_placer(
                placed_object_position=target['shows'][0]['position'],
                placed_object_dimensions=target['debug']['dimensions'],
                placed_object_offset_y=target['debug']['positionY'],
                activation_step=target['shows'][0]['stepBegin'],
                end_height=visible_support['debug']['dimensions']['y'],
                # This just informs the length of the placer, which isn't
                # really important, so just make it a large enough value.
                max_height=10,
                placed_object_placer_offset_y=placer_offset_y
            )
            # Each pole variation should have the same ID.
            pole_instances[name]['id'] = pole_id

            # Update the pole's position with the asymmetric offset, if any.
            # The pole is normally positioned over the middle of the target,
            # but may be adjusted with asymmetric shapes like triangles or Ls.
            target_rotation = target_definition.rotation.y
            target_offset_x = placer_offset_x * (
                target['shows'][0]['scale']['z']
                if (target_rotation == -90 or target_rotation == 90)
                else target['shows'][0]['scale']['x']
            )
            pole_instances[name]['shows'][0]['position']['x'] += (
                multiplier * target_offset_x
            )

        return ObjectVariations(pole_instances)

    def _create_visible_support_object(
        self,
        target_variations: TargetVariations,
        structural_object_material_list: List[Tuple[str, List[str]]]
    ) -> SceneObject:
        target_symmetric = target_variations.get(VARIATIONS.SYMMETRIC)
        # Retrieve the finalized definition for the visible support.
        # Restrict the possible sizes to the same or bigger than the target.
        definition = (
            gravity_support_objects.get_visible_support_object_definition(
                target_symmetric['debug']['dimensions']['x']
            )
        )
        # Choose a random material (and color) from the given list.
        material_and_color = random.choice(random.choice(
            structural_object_material_list
        ))
        definition.materials = [material_and_color[0]]
        definition.color = material_and_color[1]
        # Create and return the visible support positioned under the target.
        location = {
            'position': {
                # Assume all target variations will have the same X position.
                'x': target_symmetric['shows'][0]['position']['x'],
                'y': definition.positionY,
                # Assume all target variations will have the same Z position.
                'z': target_symmetric['shows'][0]['position']['z']
            }
        }
        return instances.instantiate_object(definition, location)

    def _get_scene_ids(self) -> List[str]:
        return [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p'
        ]

    def _get_scene_ids_implausible(self) -> List[int]:
        return ['c', 'd', 'g', 'h', 'k', 'l', 'o', 'p']

    def _get_scene_ids_implausible_center_of_mass(self) -> List[int]:
        return ['o', 'p']

    def _get_scene_ids_implausible_float(self) -> List[int]:
        # Override in a subclass
        return []

    def _get_scene_ids_implausible_force(self) -> List[int]:
        # Override in a subclass
        return []

    def _get_scene_ids_implausible_support(self) -> List[int]:
        return ['c', 'd', 'g', 'h', 'k', 'l']

    def _get_scene_ids_move_target(self) -> List[int]:
        return ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']

    def _get_scene_ids_target_support_none(self) -> List[int]:
        return ['a', 'b', 'c', 'd']

    def _get_scene_ids_target_support_minimal(self) -> List[int]:
        return ['e', 'f', 'g', 'h']

    def _get_scene_ids_target_support_25(self) -> List[int]:
        return ['i', 'j', 'k', 'l']

    def _get_scene_ids_target_support_49(self) -> List[int]:
        # Override in a subclass
        return []

    def _get_scene_ids_target_support_75(self) -> List[int]:
        # Override in a subclass
        return []

    # Override
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Scene
    ) -> Dict[str, Scene]:
        """Create and return a collection of new intuitive physics scenes."""
        target_id = self._target.get(VARIATIONS.SYMMETRIC)['id']
        pole_id = self._pole.get(VARIATIONS.SYMMETRIC)['id']

        # Choose to move the target right (positive) or left (negative).
        is_positive = random.choice([True, False])

        # Choose the multipler of the target's movement in no-support scenes.
        # Must be a max of 1.5 so the target is always in view of the camera.
        no_support_multiplier = 0.5 + (random.randint(1, 10) / 20.0)

        # Choose the height of the invisible support in the implausible
        # full-support scenes (evenly divisible by PLACER_MOVE_AMOUNT).
        implausible_support_y = random.randint(
            1,
            round(1 / mechanisms.PLACER_MOVE_AMOUNT)
        )

        # Initialize scenes.
        scenes = {}
        for i in self._get_scene_ids():
            scenes[i + '1'] = copy.deepcopy(default_scene)
            scenes[i + '1'].goal.scene_info[tags.SCENE.DIRECTION] = (
                'right' if is_positive else 'left'
            )

        # Initialize gravity support tags in scenes.
        for scene in scenes.values():
            scene.goal.scene_info[
                tags.TYPES.GRAVITY_SUPPORT_PLAUSIBLE
            ] = tags.CELLS.GRAVITY_SUPPORT_PLAUSIBLE.YES
            scene.goal.scene_info[
                tags.TYPES.GRAVITY_SUPPORT_TARGET_POSITION
            ] = tags.CELLS.GRAVITY_SUPPORT_TARGET_POSITION.FULL
            scene.goal.scene_info[
                tags.TYPES.GRAVITY_SUPPORT_TARGET_TYPE
            ] = tags.CELLS.GRAVITY_SUPPORT_TARGET_TYPE.SYMMETRIC

        # Switch target with its asymmetric variation.
        self._update_asymmetric_target_slice_scene(scenes, is_positive)

        # Move target X position.
        for i in self._get_scene_ids_move_target():
            if (i + '1') not in scenes:
                continue
            scene = scenes[i + '1']
            x_position_multiplier = 0
            # Move target to its no-support X position.
            if i in self._get_scene_ids_target_support_none():
                scene.goal.scene_info[
                    tags.TYPES.GRAVITY_SUPPORT_TARGET_POSITION
                ] = tags.CELLS.GRAVITY_SUPPORT_TARGET_POSITION.NONE
                x_position_multiplier = no_support_multiplier
            # Move target to its minimal-support (5%) X position.
            if i in self._get_scene_ids_target_support_minimal():
                scene.goal.scene_info[
                    tags.TYPES.GRAVITY_SUPPORT_TARGET_POSITION
                ] = tags.CELLS.GRAVITY_SUPPORT_TARGET_POSITION.MINIMAL
                x_position_multiplier = 0.45
            # Move target to its 25%-supported X position.
            if i in self._get_scene_ids_target_support_25():
                scene.goal.scene_info[
                    tags.TYPES.GRAVITY_SUPPORT_TARGET_POSITION
                ] = tags.CELLS.GRAVITY_SUPPORT_TARGET_POSITION.TWENTY_FIVE
                x_position_multiplier = 0.25
            # Move target to its 49%-supported X position.
            if i in self._get_scene_ids_target_support_49():
                scene.goal.scene_info[
                    tags.TYPES.GRAVITY_SUPPORT_TARGET_POSITION
                ] = tags.CELLS.GRAVITY_SUPPORT_TARGET_POSITION.FORTY_NINE
                x_position_multiplier = 0.01
            # Move target to its 75%-supported X position.
            if i in self._get_scene_ids_target_support_75():
                scene.goal.scene_info[
                    tags.TYPES.GRAVITY_SUPPORT_TARGET_POSITION
                ] = tags.CELLS.GRAVITY_SUPPORT_TARGET_POSITION.SEVENTY_FIVE
                x_position_multiplier = -0.25
            for instance in scene.objects:
                if instance['id'] == target_id:
                    modifier = (((
                        self._visible_support['debug']['dimensions']['x'] / 2.0
                    ) + (
                        x_position_multiplier *
                        instance['debug']['dimensions']['x']
                    )) * (1 if is_positive else -1))
                    instance['shows'][0]['position']['x'] += modifier
                    break
            for instance in scene.objects:
                if instance['id'] == pole_id:
                    instance['shows'][0]['position']['x'] += modifier
                    break

        # Implausible scenes.
        for i in self._get_scene_ids_implausible():
            if (i + '1') not in scenes:
                continue
            scene = scenes[i + '1']
            scene.debug['evaluationOnly'] = True
            scene.goal.answer['choice'] = IMPLAUSIBLE
            scene.goal.scene_info[
                tags.TYPES.GRAVITY_SUPPORT_PLAUSIBLE
            ] = tags.CELLS.GRAVITY_SUPPORT_PLAUSIBLE.NO
            # Add an invisible support on the floor next to the visible one.
            if i in self._get_scene_ids_implausible_support():
                target = None
                for instance in scene.objects:
                    if instance['id'] == target_id:
                        self._place_invisible_support_on_floor(
                            scene,
                            instance,
                            is_positive
                        )
                        break
            # Add an invisible wind to blow over the target object.
            if i in self._get_scene_ids_implausible_force():
                for instance in scene.objects:
                    if instance['id'] == target_id:
                        self._shove_target_off_its_support(
                            instance,
                            is_positive
                        )
                        break
            # Add an invisible support on top of the visible support.
            if i in self._get_scene_ids_implausible_float():
                target = None
                pole = None
                for instance in scene.objects:
                    if instance['id'] == target_id:
                        target = instance
                    if instance['id'] == pole_id:
                        pole = instance
                self._stack_invisible_support_on_support(
                    scene,
                    target,
                    pole,
                    implausible_support_y
                )
            # Add an implausible center of mass to the target object.
            if i in self._get_scene_ids_implausible_center_of_mass():
                target = None
                for instance in scene.objects:
                    if instance['id'] == target_id:
                        target = instance
                self._change_object_center_of_mass(
                    target,
                    self._visible_support['debug']['dimensions']['y'],
                    is_positive
                )

        # Finalize scenes.
        self._update_hypercube_scene_info_tags(scenes)

        return scenes

    # Override
    def _get_slices(self) -> List[str]:
        return [
            tags.TYPES.GRAVITY_SUPPORT_PLAUSIBLE,
            tags.TYPES.GRAVITY_SUPPORT_TARGET_POSITION,
            tags.TYPES.GRAVITY_SUPPORT_TARGET_TYPE
        ]

    def _update_asymmetric_target_slice_scene(
        self,
        scenes: Dict[str, Scene],
        is_positive: bool
    ) -> None:
        """Update the scene with the given asymmetric target slice ID."""
        target_asymmetric_left = self._target.get(VARIATIONS.ASYMMETRIC_LEFT)
        target_asymmetric_right = self._target.get(VARIATIONS.ASYMMETRIC_RIGHT)
        pole_asymmetric_left = self._pole.get(VARIATIONS.ASYMMETRIC_LEFT)
        pole_asymmetric_right = self._pole.get(VARIATIONS.ASYMMETRIC_RIGHT)
        for i in ['b', 'd', 'f', 'h', 'j', 'l', 'n', 'p']:
            if (i + '1') not in scenes:
                continue
            scene = scenes[i + '1']
            scene.goal.scene_info[
                tags.TYPES.GRAVITY_SUPPORT_TARGET_TYPE
            ] = tags.CELLS.GRAVITY_SUPPORT_TARGET_TYPE.ASYMMETRIC
            # Assume any asymmetric object is right-to-left (like an L).
            # Create copies of the corresponding target and pole.
            target_asymmetric = copy.deepcopy(
                target_asymmetric_right if is_positive
                else target_asymmetric_left
            )
            pole_asymmetric = copy.deepcopy(
                pole_asymmetric_right if is_positive else pole_asymmetric_left
            )
            for index in range(len(scene.objects)):
                if scene.objects[index]['id'] == target_asymmetric['id']:
                    scene.objects[index] = target_asymmetric
                if scene.objects[index]['id'] == pole_asymmetric['id']:
                    scene.objects[index] = pole_asymmetric

    def _change_object_center_of_mass(
        self,
        target: SceneObject,
        visible_support_height: float,
        is_positive: bool
    ) -> None:
        target['centerOfMass'] = {
            'x': 0,
            'y': 0,
            'z': 0
        }
        target['resetCenterOfMass'] = True
        target['resetCenterOfMassAtY'] = target['debug']['positionY'] + (
            visible_support_height / 2.0
        )
        width_key = 'z' if (
            target['shows'][0]['rotation']['y'] == -90 or
            target['shows'][0]['rotation']['y'] == 90
        ) else 'x'
        target['centerOfMass'][width_key] = (
            round((target['debug']['dimensions']['x'] * 2.0), 4) + 0.05
        ) * (
            (1 if is_positive else -1) * (-1 if width_key == 'z' else 1) *
            # Assume asymmetric objects will always have a Y rotation of either
            # 90 or 180 for heavy side unsupported, or 0 or -90 for supported.
            (-1 if target['shows'][0]['rotation']['y'] > 0 else 1)
        )

    def _find_center_of_mass_x(
        self,
        target_asymmetric_definition: ObjectDefinition,
        flip: bool
    ) -> float:
        # Assume each asymmetric definition has a poly property.
        target_asymmetric_poly = target_asymmetric_definition.poly

        # Make the polygon bigger based on the definition's dimensions/scale.
        target_asymmetric_poly = affinity.scale(
            target_asymmetric_poly,
            xfact=target_asymmetric_definition.dimensions.x,
            yfact=target_asymmetric_definition.dimensions.y,
            origin=(0, 0)
        )

        # If needed, flip the asymmetric target.
        if flip:
            target_asymmetric_poly = affinity.scale(
                target_asymmetric_poly,
                xfact=-1,
                origin=(0, 0)
            )

        # Use shapely to find the asymmetric target's center of mass.
        return target_asymmetric_poly.centroid.coords[0][0]

    def _position_on_center_of_mass(
        self,
        target_asymmetric_definition: ObjectDefinition,
        target_asymmetric: SceneObject,
        pole_asymmetric: SceneObject,
        target_symmetric: SceneObject,
        flip: bool
    ) -> None:
        asymmetric_center = self._find_center_of_mass_x(
            target_asymmetric_definition,
            flip
        )

        # Adjust the position of each asymmetric object for its center of mass.
        pole_asymmetric['shows'][0]['position']['x'] -= asymmetric_center
        target_asymmetric_show = target_asymmetric['shows'][0]
        target_asymmetric_show['position']['x'] -= asymmetric_center
        target_asymmetric_show['boundingBox'] = ObjectBounds(
            box_xz=[
                Vector3d(x=corner.x - asymmetric_center,
                         y=corner.y, z=corner.z)
                for corner in target_asymmetric_show['boundingBox'].box_xz
            ],
            max_y=target_asymmetric_show['boundingBox'].max_y,
            min_y=target_asymmetric_show['boundingBox'].min_y
        )

    def _place_invisible_support_on_floor(
        self,
        scene: Scene,
        target: SceneObject,
        is_positive: bool
    ) -> None:
        invisible_support = copy.deepcopy(self._visible_support)
        invisible_support['id'] = 'invisible_support'
        invisible_support['shows'][0]['position']['x'] += (
            (1 if is_positive else -1) *
            (self._visible_support['debug']['dimensions']['x'] + 0.05)
        )
        invisible_support['shrouds'] = [{
            'stepBegin': 0,
            'stepEnd': self._last_step + 1
        }]

        # If the target is in its no-support position, we may just need to move
        # the invisible support directly under the target.
        target_position = target['shows'][0]['position']['x']
        support_position = invisible_support['shows'][0]['position']['x']
        if (
            (is_positive and target_position > support_position) or
            (not is_positive and target_position < support_position)
        ):
            invisible_support['shows'][0]['position']['x'] = target_position

        scene.objects.append(invisible_support)

    def _shove_target_off_its_support(
        self,
        instance: SceneObject,
        is_positive: bool
    ) -> None:
        wind_step = instance['togglePhysics'][0]['stepBegin'] + 1 + (
            2 * GRAVITY_SUPPORT_WIND_WAIT_STEP
        )
        instance['forces'] = [{
            'stepBegin': wind_step,
            'stepEnd': wind_step,
            'vector': {
                'x': (
                    (1 if is_positive else -1) * instance['mass'] *
                    GRAVITY_SUPPORT_WIND_FORCE_X
                ),
                'y': 0,
                'z': 0
            }
        }]

    def _stack_invisible_support_on_support(
        self,
        scene: Scene,
        target: SceneObject,
        pole: SceneObject,
        implausible_support_y: float
    ) -> None:
        invisible_support = copy.deepcopy(self._visible_support)
        invisible_support['id'] = 'invisible_support'
        height = implausible_support_y * mechanisms.PLACER_MOVE_AMOUNT
        invisible_support['debug']['dimensions']['y'] = height
        invisible_support['shows'][0]['scale']['y'] = height
        invisible_support['shows'][0]['position']['y'] = (
            self._visible_support['debug']['dimensions']['y'] +
            (invisible_support['shows'][0]['scale']['y'] / 2.0)
        )
        invisible_support['shrouds'] = [{
            'stepBegin': 0,
            'stepEnd': self._last_step + 1
        }]
        scene.objects.append(invisible_support)
        target['moves'][0]['stepEnd'] -= implausible_support_y
        target['togglePhysics'][0]['stepBegin'] -= implausible_support_y
        pole['changeMaterials'][0]['stepBegin'] -= implausible_support_y
        pole['moves'][0]['stepEnd'] -= implausible_support_y
        pole['moves'][1]['stepBegin'] -= implausible_support_y
        pole['moves'][1]['stepEnd'] -= (2 * implausible_support_y)


class ObjectPermanenceHypercube(IntuitivePhysicsHypercube):
    def __init__(
        self,
        starter_scene: Scene,
        role_to_type: Dict[str, str],
        training=False,
        is_fall_down=False,
        is_move_across=False,
        last_step=None
    ):
        super().__init__(
            tags.ABBREV.OBJECT_PERMANENCE.upper(),
            starter_scene,
            tags.TASKS.OBJECT_PERMANENCE,
            role_to_type,
            is_fall_down=is_fall_down,
            is_move_across=is_move_across,
            training=training,
            last_step=last_step
        )

    def _appear_behind_occluder(
        self,
        scene: Scene,
        target_id: str
    ) -> None:
        target = [
            instance for instance in scene.objects
            if instance['id'] == target_id
        ][0]

        if self.is_move_across():
            self._appear_behind_occluder_move_across(target)
        elif self.is_fall_down():
            self._appear_behind_occluder_fall_down(target)
        else:
            raise SceneException('Unknown scene setup function!')

    def _appear_behind_occluder_fall_down(
        self,
        target: SceneObject
    ) -> None:
        # Implausible event happens after target falls behind occluder.
        implausible_event_step = (
            OBJECT_FALL_TIME + target['shows'][0]['stepBegin']
        )
        # Set target's Y position stationary on the ground.
        y_position = retrieve_off_screen_position_y(
            target['shows'][0]['position']['z']
        )
        target['shows'][0]['position']['y'] -= y_position
        # Set target to appear at implausible event step.
        target['shows'][0]['stepBegin'] = implausible_event_step

    def _appear_behind_occluder_move_across(
        self,
        target: SceneObject
    ) -> None:
        # Held back in Eval 4 (see override in secret file).
        pass

    def _disappear_behind_occluder(
        self,
        scene: Scene,
        target_id: str
    ) -> None:
        target = [
            instance for instance in scene.objects
            if instance['id'] == target_id
        ][0]

        if self.is_move_across():
            self._disappear_behind_occluder_move_across(target)
        elif self.is_fall_down():
            self._disappear_behind_occluder_fall_down(target)
        else:
            raise SceneException('Unknown scene setup function!')

    def _disappear_behind_occluder_fall_down(
        self,
        target: SceneObject
    ) -> None:
        # Implausible event happens after target falls behind occluder.
        implausible_event_step = (
            OBJECT_FALL_TIME + target['shows'][0]['stepBegin']
        )
        # Set target to disappear at implausible event step.
        target['hides'] = [{
            'stepBegin': implausible_event_step
        }]

    def _disappear_behind_occluder_move_across(
        self,
        target: SceneObject
    ) -> None:
        # Held back in Eval 4 (see override in secret file).
        pass

    # Override
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Scene
    ) -> Dict[str, Scene]:
        """Create and return a collection of new intuitive physics scenes."""
        target_id_1 = self._target_list[0]['id']
        target_id_2 = self._target_list[1]['id']

        # Variations on object one.
        variations_1 = self._variations_list[0]
        shape_variation_1 = variations_1.get(VARIATIONS.UNTRAINED_SHAPE)
        size_variation_1 = variations_1.get(VARIATIONS.UNTRAINED_SIZE)

        # Variations on object two.
        variations_2 = self._variations_list[1]
        shape_variation_2 = variations_2.get(VARIATIONS.UNTRAINED_SHAPE)
        size_variation_2 = variations_2.get(VARIATIONS.UNTRAINED_SIZE)

        # Initialize scenes.
        scenes = {}
        for i in ['a', 'b', 'c', 'j', 'k', 'l', 's', 't', 'u']:
            scenes[i + '1'] = copy.deepcopy(default_scene)
        for i in [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'aa'
        ]:
            for j in [i + '2', i + '3', i + '4']:
                scenes[j] = copy.deepcopy(default_scene)

        # Initialize object permanence tags in scenes.
        for scene in scenes.values():
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_OBJECT_ONE
            ] = tags.CELLS.OBJECT_PERMANENCE_OBJECT_ONE.NO_CHANGE
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_OBJECT_TWO
            ] = tags.CELLS.OBJECT_PERMANENCE_OBJECT_TWO.NO_CHANGE
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_NOVELTY_ONE
            ] = tags.CELLS.OBJECT_PERMANENCE_NOVELTY_ONE.NONE
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_NOVELTY_TWO
            ] = tags.CELLS.OBJECT_PERMANENCE_NOVELTY_TWO.NONE

        # Remove object two completely.
        for i in ['a', 'b', 'c', 'j', 'k', 'l', 's', 't', 'u']:
            scene = scenes[i + '1']
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_OBJECT_TWO
            ] = tags.CELLS.OBJECT_PERMANENCE_OBJECT_TWO.NONE
            for index in range(len(scene.objects)):
                if scene.objects[index]['id'] == target_id_2:
                    del scene.objects[index]
                    break

        # Switch object one with its untrained size variation.
        for i in ['b', 'e', 'h', 'k', 'n', 'q', 't', 'w', 'z']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                if j not in scenes:
                    continue
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.scene_info[
                    tags.TYPES.OBJECT_PERMANENCE_NOVELTY_ONE
                ] = tags.CELLS.OBJECT_PERMANENCE_NOVELTY_ONE.SIZE
                for index in range(len(scene.objects)):
                    if scene.objects[index]['id'] == target_id_1:
                        scene.objects[index] = (
                            copy.deepcopy(size_variation_1)
                        )
                        break

        # Switch object one with its untrained shape variation.
        for i in ['c', 'f', 'i', 'l', 'o', 'r', 'u', 'x', 'aa']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                if j not in scenes:
                    continue
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.scene_info[
                    tags.TYPES.OBJECT_PERMANENCE_NOVELTY_ONE
                ] = tags.CELLS.OBJECT_PERMANENCE_NOVELTY_ONE.SHAPE
                for index in range(len(scene.objects)):
                    if scene.objects[index]['id'] == target_id_1:
                        scene.objects[index] = (
                            copy.deepcopy(shape_variation_1)
                        )
                        break

        # Switch object two with its untrained size variation.
        for i in ['d', 'e', 'f', 'm', 'n', 'o', 'v', 'w', 'x']:
            for j in [i + '2', i + '3', i + '4']:
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.scene_info[
                    tags.TYPES.OBJECT_PERMANENCE_NOVELTY_TWO
                ] = tags.CELLS.OBJECT_PERMANENCE_NOVELTY_TWO.SIZE
                for index in range(len(scene.objects)):
                    if scene.objects[index]['id'] == target_id_2:
                        scene.objects[index] = (
                            copy.deepcopy(size_variation_2)
                        )
                        break

        # Switch object two with its untrained shape variation.
        for i in ['g', 'h', 'i', 'p', 'q', 'r', 'y', 'z', 'aa']:
            for j in [i + '2', i + '3', i + '4']:
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.scene_info[
                    tags.TYPES.OBJECT_PERMANENCE_NOVELTY_TWO
                ] = tags.CELLS.OBJECT_PERMANENCE_NOVELTY_TWO.SHAPE
                for index in range(len(scene.objects)):
                    if scene.objects[index]['id'] == target_id_2:
                        scene.objects[index] = (
                            copy.deepcopy(shape_variation_2)
                        )
                        break

        # Make object one disappear.
        for i in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                if j not in scenes:
                    continue
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.answer['choice'] = IMPLAUSIBLE
                scene.goal.scene_info[
                    tags.TYPES.OBJECT_PERMANENCE_OBJECT_ONE
                ] = tags.CELLS.OBJECT_PERMANENCE_OBJECT_ONE.DISAPPEAR
                self._disappear_behind_occluder(scene, target_id_1)

        # Make object one appear.
        for i in ['j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                if j not in scenes:
                    continue
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.answer['choice'] = IMPLAUSIBLE
                scene.goal.scene_info[
                    tags.TYPES.OBJECT_PERMANENCE_OBJECT_ONE
                ] = tags.CELLS.OBJECT_PERMANENCE_OBJECT_ONE.APPEAR
                self._appear_behind_occluder(scene, target_id_1)

        for i in [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'aa'
        ]:
            # Make object two disappear.
            scene = scenes[i + '4']
            scene.debug['evaluationOnly'] = True
            scene.goal.answer['choice'] = IMPLAUSIBLE
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_OBJECT_TWO
            ] = tags.CELLS.OBJECT_PERMANENCE_OBJECT_TWO.DISAPPEAR
            self._disappear_behind_occluder(scene, target_id_2)

            # Make object two appear.
            scene = scenes[i + '3']
            scene.debug['evaluationOnly'] = True
            scene.goal.answer['choice'] = IMPLAUSIBLE
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_OBJECT_TWO
            ] = tags.CELLS.OBJECT_PERMANENCE_OBJECT_TWO.APPEAR
            self._appear_behind_occluder(scene, target_id_2)

        # Finalize scenes.
        self._update_hypercube_scene_info_tags(scenes)

        return scenes

    # Override
    def _get_slices(self) -> List[str]:
        return [
            tags.TYPES.OBJECT_PERMANENCE_OBJECT_ONE,
            tags.TYPES.OBJECT_PERMANENCE_OBJECT_TWO,
            tags.TYPES.OBJECT_PERMANENCE_NOVELTY_ONE,
            tags.TYPES.OBJECT_PERMANENCE_NOVELTY_TWO
        ]

    # Override
    def _does_need_target_variations(self, variation_tag: str) -> bool:
        """Return whether this hypercube must generate a variation of the
        target object with the given tag."""
        return (
            variation_tag == VARIATIONS.UNTRAINED_SHAPE or
            variation_tag == VARIATIONS.UNTRAINED_SIZE
        )


class ShapeConstancyHypercube(IntuitivePhysicsHypercube):
    def __init__(
        self,
        starter_scene: Scene,
        role_to_type: Dict[str, str],
        training=False,
        is_fall_down=False,
        is_move_across=False,
        last_step=None
    ):
        super().__init__(
            tags.ABBREV.SHAPE_CONSTANCY.upper(),
            starter_scene,
            tags.TASKS.SHAPE_CONSTANCY,
            role_to_type,
            is_fall_down=is_fall_down,
            is_move_across=is_move_across,
            training=training,
            last_step=last_step
        )

    def _turn_a_into_b(
        self,
        scene: Scene,
        target_id: str,
        template_b: SceneObject
    ) -> None:
        target_a = [
            instance for instance in scene.objects
            if instance['id'] == target_id
        ][0]
        target_b = copy.deepcopy(template_b)

        if self.is_move_across():
            # Implausible event happens after target moves behind occluder.
            target_hidden_step = target_a['debug']['movement']['stepList'][0]
            implausible_event_step = target_hidden_step + \
                target_a['forces'][0]['stepBegin']
            implausible_event_x = (
                target_a['debug']['movement']['positionList'][0]
            )
            # Give object B the movement of object A.
            target_b['forces'] = copy.deepcopy(target_a['forces'])
            target_b['debug']['movement'] = target_a['debug']['movement']

        elif self.is_fall_down():
            # Implausible event happens after target falls behind occluder.
            implausible_event_step = (
                OBJECT_FALL_TIME + target_a['shows'][0]['stepBegin']
            )
            implausible_event_x = target_a['shows'][0]['position']['x']
            # Set target's Y position stationary on the ground.
            y_position = retrieve_off_screen_position_y(
                target_b['shows'][0]['position']['z']
            )
            target_b['shows'][0]['position']['y'] -= y_position

        else:
            raise SceneException('Unknown scene setup function!')

        # Hide object A at the implausible event step and show object B in
        # object A's old position behind the occluder.
        target_a['hides'] = [{
            'stepBegin': implausible_event_step
        }]
        target_b['shows'][0]['stepBegin'] = implausible_event_step
        target_b['shows'][0]['position']['x'] = implausible_event_x

        # Add object B to the scene.
        scene.objects.append(target_b)

    # Override
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Scene
    ) -> Dict[str, Scene]:
        """Create and return a collection of new intuitive physics scenes."""
        target_id_1 = self._target_list[0]['id']
        target_id_2 = self._target_list[1]['id']

        # Variations on object one.
        variations_1 = self._variations_list[0]
        trained_variation_1_b = variations_1.get(VARIATIONS.DIFFERENT_SHAPE)
        untrained_variation_1_a = variations_1.get(VARIATIONS.UNTRAINED_SHAPE)
        untrained_variation_1_b = variations_1.get(
            VARIATIONS.UNTRAINED_DIFFERENT_SHAPE
        )

        # Variations on object two.
        variations_2 = self._variations_list[1]
        trained_variation_2_b = variations_2.get(VARIATIONS.DIFFERENT_SHAPE)
        untrained_variation_2_a = variations_2.get(VARIATIONS.UNTRAINED_SHAPE)
        untrained_variation_2_b = variations_2.get(
            VARIATIONS.UNTRAINED_DIFFERENT_SHAPE
        )

        # Initialize scenes.
        scenes = {}
        # Cell list reduced to these cells.  We tried to keep as much other
        # code as possible
        cell_list = ['a1', 'a2', 'e1', 'e2', 'e3',
                     'b1', 'd2', 'j1', 'l2', 'l4']
        for j in cell_list:
            scenes[j] = copy.deepcopy(default_scene)

        # Initialize shape constancy tags in scenes.
        for scene in scenes.values():
            scene.goal.scene_info[
                tags.TYPES.SHAPE_CONSTANCY_OBJECT_ONE
            ] = tags.CELLS.SHAPE_CONSTANCY_OBJECT_ONE.NO_CHANGE
            scene.goal.scene_info[
                tags.TYPES.SHAPE_CONSTANCY_OBJECT_TWO
            ] = tags.CELLS.SHAPE_CONSTANCY_OBJECT_TWO.NO_CHANGE
            scene.goal.scene_info[
                tags.TYPES.SHAPE_CONSTANCY_TRAINED_ONE
            ] = tags.CELLS.SHAPE_CONSTANCY_TRAINED_ONE.YES
            scene.goal.scene_info[
                tags.TYPES.SHAPE_CONSTANCY_TRAINED_TWO
            ] = tags.CELLS.SHAPE_CONSTANCY_TRAINED_TWO.YES

        # Remove object two completely.
        for i in ['a', 'b', 'e', 'f', 'i', 'j']:
            j = i + '1'
            if j not in scenes:
                continue
            scene = scenes[i + '1']
            scene.goal.scene_info[
                tags.TYPES.SHAPE_CONSTANCY_OBJECT_TWO
            ] = tags.CELLS.SHAPE_CONSTANCY_OBJECT_TWO.NONE
            for index in range(len(scene.objects)):
                if scene.objects[index]['id'] == target_id_2:
                    del scene.objects[index]
                    break

        # Switch object one with its untrained variation.
        for i in ['b', 'd', 'f', 'h', 'j', 'l']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                if j not in scenes:
                    continue
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.scene_info[
                    tags.TYPES.SHAPE_CONSTANCY_TRAINED_ONE
                ] = tags.CELLS.SHAPE_CONSTANCY_TRAINED_ONE.NO
                for index in range(len(scene.objects)):
                    if scene.objects[index]['id'] == target_id_1:
                        scene.objects[index] = (
                            copy.deepcopy(untrained_variation_1_a)
                        )
                        break

        # Switch object two with its untrained variation.
        for i in ['c', 'd', 'g', 'h', 'k', 'l']:
            for j in [i + '2', i + '3', i + '4']:
                if j not in scenes:
                    continue
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.scene_info[
                    tags.TYPES.SHAPE_CONSTANCY_TRAINED_TWO
                ] = tags.CELLS.SHAPE_CONSTANCY_TRAINED_TWO.NO
                for index in range(len(scene.objects)):
                    if scene.objects[index]['id'] == target_id_2:
                        scene.objects[index] = (
                            copy.deepcopy(untrained_variation_2_a)
                        )
                        break

        # Object one transforms into a different trained shape.
        for i in ['e', 'f', 'g', 'h']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                if j not in scenes:
                    continue
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.answer['choice'] = IMPLAUSIBLE
                scene.goal.scene_info[
                    tags.TYPES.SHAPE_CONSTANCY_OBJECT_ONE
                ] = tags.CELLS.SHAPE_CONSTANCY_OBJECT_ONE.TRAINED_SHAPE
                self._turn_a_into_b(scene, target_id_1, trained_variation_1_b)

        # Object one transforms into a different untrained shape.
        for i in ['i', 'j', 'k', 'l']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                if j not in scenes:
                    continue
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.answer['choice'] = IMPLAUSIBLE
                scene.goal.scene_info[
                    tags.TYPES.SHAPE_CONSTANCY_OBJECT_ONE
                ] = tags.CELLS.SHAPE_CONSTANCY_OBJECT_ONE.UNTRAINED_SHAPE
                self._turn_a_into_b(
                    scene,
                    target_id_1,
                    untrained_variation_1_b
                )

        # The next two sections of code used to be applied to all letters for
        # their 3 cell and 4 cell respectively.  We removed all 3 and 4 cells
        # except 2 so those are hard coded below.

        # Object two transforms into a different trained shape.
        scene = scenes['e3']
        scene.debug['evaluationOnly'] = True
        scene.goal.answer['choice'] = IMPLAUSIBLE
        scene.goal.scene_info[
            tags.TYPES.SHAPE_CONSTANCY_OBJECT_TWO
        ] = tags.CELLS.SHAPE_CONSTANCY_OBJECT_TWO.TRAINED_SHAPE
        self._turn_a_into_b(scene, target_id_2, trained_variation_2_b)

        # Object two transforms into a different untrained shape.
        scene = scenes['l4']
        scene.debug['evaluationOnly'] = True
        scene.goal.answer['choice'] = IMPLAUSIBLE
        scene.goal.scene_info[
            tags.TYPES.SHAPE_CONSTANCY_OBJECT_TWO
        ] = tags.CELLS.SHAPE_CONSTANCY_OBJECT_TWO.UNTRAINED_SHAPE
        self._turn_a_into_b(
            scene,
            target_id_2,
            untrained_variation_2_b
        )

        # Finalize scenes.
        self._update_hypercube_scene_info_tags(scenes)

        return scenes

    # Override
    def _get_slices(self) -> List[str]:
        return [
            tags.TYPES.SHAPE_CONSTANCY_OBJECT_ONE,
            tags.TYPES.SHAPE_CONSTANCY_OBJECT_TWO,
            tags.TYPES.SHAPE_CONSTANCY_TRAINED_ONE,
            tags.TYPES.SHAPE_CONSTANCY_TRAINED_TWO
        ]

    # Override
    def _does_need_target_variations(self, variation_tag: str) -> bool:
        """Return whether this hypercube must generate a variation of the
        target object with the given tag."""
        return (
            variation_tag == VARIATIONS.UNTRAINED_SHAPE or
            variation_tag == VARIATIONS.DIFFERENT_SHAPE or
            variation_tag == VARIATIONS.UNTRAINED_DIFFERENT_SHAPE
        )


class SpatioTemporalContinuityHypercube(IntuitivePhysicsHypercube):
    def __init__(
        self,
        starter_scene: Scene,
        role_to_type: Dict[str, str],
        training=False,
        is_fall_down=False,
        is_move_across=False,
        last_step=None
    ):
        super().__init__(
            tags.ABBREV.SPATIO_TEMPORAL_CONTINUITY.upper(),
            starter_scene,
            tags.TASKS.SPATIO_TEMPORAL_CONTINUITY,
            role_to_type,
            is_fall_down=is_fall_down,
            is_move_across=is_move_across,
            training=training,
            last_step=last_step
        )

    def _shroud_object(self, scene: Scene, target_id: str) -> None:
        target = [
            instance for instance in scene.objects
            if instance['id'] == target_id
        ][0]

        if self.is_move_across():
            # Implausible event happens after target moves behind occluder.
            # Shroud target until it moves behind second occluder.
            target_hidden_step_1 = target['debug']['movement']['stepList'][0]
            target_hidden_step_2 = target['debug']['movement']['stepList'][1]
            if target_hidden_step_1 < target_hidden_step_2:
                occluder_start_index = target_hidden_step_1
                occluder_end_index = target_hidden_step_2
            else:
                occluder_start_index = target_hidden_step_2
                occluder_end_index = target_hidden_step_1

            target['shrouds'] = [{
                'stepBegin': (
                    occluder_start_index + target['forces'][0]['stepBegin'] + 1
                ),
                'stepEnd': (
                    target['shows'][0]['stepBegin'] + occluder_end_index + 1
                )
            }]

        elif self.is_fall_down():
            # TODO If we ever need STC fall-down scenes in a future eval.
            raise SceneException('STC fall-down hypercubes not yet supported!')

        else:
            raise SceneException('Unknown scene setup function!')

    # Override
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Scene
    ) -> Dict[str, Scene]:
        """Create and return a collection of new intuitive physics scenes."""
        target_id = self._target_list[0]['id']
        non_target_id = self._distractor_list[0]['id']

        # Variations on target.
        target_untrained_variation = self._variations_list[0].get(
            VARIATIONS.UNTRAINED_SHAPE
        )

        # Variations on non-target.
        non_target_untrained_variation = self._variations_list[1].get(
            VARIATIONS.UNTRAINED_SHAPE
        )

        for instance in self._variations_list[1].all():
            instance['debug']['role'] = tags.ROLES.NON_TARGET

        # Initialize scenes.
        scenes = {}
        for i in [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r'
        ]:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                scenes[j] = copy.deepcopy(default_scene)

        # Initialize spatio temporal continuity tags in scenes.
        for scene in scenes.values():
            scene.goal.scene_info[
                tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OBJECTS
            ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_OBJECTS.TWO
            scene.goal.scene_info[
                tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS
            ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS.THREE
            scene.goal.scene_info[
                tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_PLAUSIBLE
            ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_PLAUSIBLE.YES
            scene.goal.scene_info[
                tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_TARGET_TRAINED
            ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_TARGET_TRAINED.YES
            scene.goal.scene_info[
                tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_NON_TARGET_TRAINED
            ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_NON_TARGET_TRAINED.YES

        # Remove the non-target.
        for i in ['a', 'd', 'g', 'j', 'm', 'p', 'b', 'e', 'h', 'k', 'n', 'q']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                scene = scenes[j]
                scene.goal.scene_info[
                    tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OBJECTS
                ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_OBJECTS.ONE
                for index in range(len(scene.objects)):
                    if scene.objects[index]['id'] == non_target_id:
                        del scene.objects[index]
                        break

        # Remove the target.
        for i in ['a', 'd', 'g', 'j', 'm', 'p']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                scene = scenes[j]
                scene.goal.scene_info[
                    tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OBJECTS
                ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_OBJECTS.ZERO
                for index in range(len(scene.objects)):
                    if scene.objects[index]['id'] == target_id:
                        del scene.objects[index]
                        break

        # Remove the one unpaired occluder.
        for i in ['g', 'h', 'i', 'j', 'k', 'l']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                scene = scenes[j]
                scene.goal.scene_info[
                    tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS
                ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS.TWO
                remove_id_list = [
                    self._occluder_list[-2]['id'],
                    self._occluder_list[-1]['id']
                ]
                scene.objects = [
                    instance for instance in scene.objects
                    if instance['id'] not in remove_id_list
                ]

        # Remove every occluder.
        for i in ['m', 'n', 'o', 'p', 'q', 'r']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                scene = scenes[j]
                scene.goal.scene_info[
                    tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS
                ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS.ZERO
                remove_id_list = [
                    occluder['id'] for occluder in self._occluder_list
                ]
                scene.objects = [
                    instance for instance in scene.objects
                    if instance['id'] not in remove_id_list
                ]

        for i in [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r'
        ]:
            # Switch the target with its untrained variation.
            for j in [i + '2', i + '4']:
                scene = scenes[j]
                scene.goal.scene_info[
                    tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_TARGET_TRAINED
                ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_TARGET_TRAINED.NO
                scene.debug['evaluationOnly'] = True
                for index in range(len(scene.objects)):
                    if scene.objects[index]['id'] == target_id:
                        scene.objects[index] = (
                            copy.deepcopy(target_untrained_variation)
                        )
                        break

            # Switch the non-target with its untrained variation.
            for j in [i + '3', i + '4']:
                scene = scenes[j]
                scene.goal.scene_info[
                    tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_NON_TARGET_TRAINED
                ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_NON_TARGET_TRAINED.NO
                scene.debug['evaluationOnly'] = True
                for index in range(len(scene.objects)):
                    if scene.objects[index]['id'] == non_target_id:
                        scene.objects[index] = (
                            copy.deepcopy(non_target_untrained_variation)
                        )
                        break

        # Make target temporarily invisible (shrouded) as it moves between two
        # paired occluders (ignoring scenes in which the target was removed).
        for i in ['e', 'f', 'k', 'l', 'q', 'r']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True
                scene.goal.answer['choice'] = IMPLAUSIBLE
                scene.goal.scene_info[
                    tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_PLAUSIBLE
                ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_PLAUSIBLE.NO
                self._shroud_object(scene, target_id)

        for i in ['d', 'j', 'p']:
            for j in [i + '1', i + '2', i + '3', i + '4']:
                scene = scenes[j]
                scene.debug['evaluationOnly'] = True

        # Finalize scenes.
        self._update_hypercube_scene_info_tags(scenes)

        # Consolidate specific redundant scenes (STC only).
        for i in ['a', 'd', 'g', 'j', 'm', 'p']:
            for j in [i + '2', i + '3', i + '4']:
                scenes[i + '1'].goal.scene_info[tags.SCENE.ID].append(j)
                del scenes[j]
        for i in ['b', 'e', 'h', 'k', 'n', 'q']:
            scenes[i + '1'].goal.scene_info[tags.SCENE.ID].append(i + '3')
            del scenes[i + '3']
            scenes[i + '2'].goal.scene_info[tags.SCENE.ID].append(i + '4')
            del scenes[i + '4']

        return scenes

    # Override
    def _get_slices(self) -> List[str]:
        return [
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OBJECTS,
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS,
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_PLAUSIBLE,
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_TARGET_TRAINED,
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_NON_TARGET_TRAINED
        ]

    # Override
    def _does_need_target_variations(self, variation_tag: str) -> bool:
        """Return whether this hypercube must generate a variation of the
        target object with the given tag."""
        return variation_tag == VARIATIONS.UNTRAINED_SHAPE

    # Override
    def _find_move_across_paired_list(
        self,
        target_variation: TargetVariations
    ) -> List[TargetVariations]:
        """Return objects that must be paired with occluders in move-across
        scenes."""
        # Generate two occluders paired with the target object.
        return [target_variation, target_variation]

    # Override
    def _identify_targets_and_non_targets(
        self,
        moving_object_list: List[SceneObject]
    ) -> Tuple[List[SceneObject], List[SceneObject]]:
        """Return the two separate target and non-target lists using the given
        moving object list."""
        # STC scenes will always have one target and one non-target in Eval 3.
        return moving_object_list[:1], moving_object_list[1:]


class ObjectPermanenceHypercubeEval4(ObjectPermanenceHypercube):
    def __init__(
        self,
        starter_scene: Scene,
        role_to_type: Dict[str, str],
        training=False,
        is_fall_down=False,
        is_move_across=False
    ):
        super().__init__(
            starter_scene,
            role_to_type,
            # All object permanence scenes are move-across in Eval 4.
            is_fall_down=False,
            is_move_across=True,
            training=training,
            # All object permanence scenes must be longer in Eval 4 due to the
            # length of the target's "stop" movement variations.
            last_step=240
        )

    # Override
    def _choose_move_across_occluder_data(
        self,
        paired_variations: TargetVariations,
        index: int
    ) -> Tuple[float, float]:
        """Return the X position and size for a paired move-across occluder."""
        paired_object = paired_variations.get(VARIATIONS.TRAINED)
        paired_position = paired_object['shows'][0]['position']
        paired_size_x = paired_variations.get_max_size_x()
        paired_object_movement = paired_object['debug']['movement']

        toss_stop = paired_object_movement['tossStop']
        step = paired_object_movement['stepList'][index]
        land_step = toss_stop['landStep']

        # Retrieve the occluder X position of both the implausible event step
        # and the land step for the toss-and-stop-on-screen movement.
        x_list = [
            object_x_to_occluder_x(
                paired_object_movement['positionList'][index],
                paired_position['z']
            ),
            object_x_to_occluder_x(
                toss_stop['xDistanceByStep'][land_step]
                if land_step < len(toss_stop['xDistanceByStep']) else
                toss_stop['xDistanceByStep'][-1],
                paired_position['z']
            )
        ]
        x_list_debug = {
            'pairedPosition': x_list[0],
            'tossLandPosition': x_list[1]
        }

        # Then retrieve the occluder X position of the implausible event step
        # and stop step for each stop-on-screen movement.
        for move_name in ['moveStop', 'deepStop', 'tossStop']:
            movement = paired_object_movement[move_name]

            implausible_event_x = object_x_to_occluder_x(
                movement['xDistanceByStep'][step],
                movement['zDistanceByStep'][step]
                if 'zDistanceByStep' in movement else paired_position['z']
            )
            x_list.append(implausible_event_x)
            x_list_debug[move_name + 'PairedPosition'] = implausible_event_x

            stop_step = movement['stopStep'] if (
                movement['stopStep'] < len(movement['xDistanceByStep'])
            ) else -1
            stop_x = object_x_to_occluder_x(
                movement['xDistanceByStep'][stop_step],
                movement['zDistanceByStep'][stop_step]
                if 'zDistanceByStep' in movement else paired_position['z']
            )
            if stop_x is not None:
                x_list.append(stop_x)
                x_list_debug[move_name + 'EndingPosition'] = stop_x

        # Sort the list to identify the bounds of the occluder so that it hides
        # the implausible event step, land step, and all stop steps.
        x_list = sorted(x_list)
        x_1 = x_list[0] - ((paired_size_x + self._get_occluder_buffer()) / 2.0)
        x_2 = x_list[-1] + (
            (paired_size_x + self._get_occluder_buffer()) / 2.0
        )

        occluder_size_x = x_2 - x_1
        occluder_position_x = x_2 - (occluder_size_x / 2.0)

        # Ensure the occluder is within the camera view.
        if not self._validate_in_view(occluder_position_x, occluder_size_x):
            raise SceneException(
                f'Occluder from {x_list[0]} to {x_list[-1]} out of bounds at '
                f'step {step} with original occluder X '
                f'{paired_object_movement["positionList"][index]}\n'
                f'moveStop {paired_object_movement["moveStop"]}\n'
                f'deepStop {paired_object_movement["deepStop"]}\n'
                f'tossStop {paired_object_movement["tossStop"]}\n'
                f'{occluder_position_x=} and {occluder_size_x=}'
            )

        paired_object_movement['occluderPosition'] = x_list_debug
        paired_object_movement['diagonalSize'] = paired_size_x
        return occluder_position_x, occluder_size_x

    # Override
    def _does_have_deep_move(self) -> bool:
        """Return whether this hypercube must generate deep movement."""
        return True

    # Override
    def _does_have_stop_move(self) -> bool:
        """Return whether this hypercube must generate stop movement."""
        return True

    # Override
    def _does_have_toss_move(self) -> bool:
        """Return whether this hypercube must generate toss movement."""
        return True

    # Override
    def _get_move_across_object_count(self) -> int:
        """Return the number of objects for the move-across scene."""
        return 1

    # Override
    def _get_move_across_occluder_count(self) -> int:
        """Return the number of occluders for the move-across scene."""
        return 1

    # Override
    def _get_occluder_height(self) -> int:
        """Return the occluder height to use."""
        return occluders.OCCLUDER_HEIGHT_TALL

    # Override
    def _init_each_object_definition_list(
        self,
        is_fall_down: bool,
        only_basic_shapes: bool,
        only_complex_shapes: bool
    ) -> None:
        """Set each object definition list needed by this hypercube, used in
        _choose_object_variations."""

        super()._init_each_object_definition_list(
            is_fall_down,
            only_basic_shapes=False,
            only_complex_shapes=True
        )

        # Don't use balls/spheres or cylinders in Eval 4 OP hypercubes.
        # They don't stop in sync with other objects in "stop" movement scenes.
        self._trained_dataset = self._trained_dataset.filter_on_type(
            cannot_be=ROUND_TYPES
        )
        self._untrained_shape_dataset = (
            self._untrained_shape_dataset.filter_on_type(
                cannot_be=ROUND_TYPES
            )
        )
        self._untrained_size_dataset = (
            self._untrained_size_dataset.filter_on_type(
                cannot_be=ROUND_TYPES
            )
        )

    # Override
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Scene
    ) -> Dict[str, Scene]:
        """Create and return a collection of new intuitive physics scenes."""
        # Initialize scenes.
        scenes = {}
        for j in self._get_scene_ids():
            scenes[j] = copy.deepcopy(default_scene)

        # Initialize object permanence tags in scenes.
        for scene in scenes.values():
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_SETUP
            ] = tags.CELLS.OBJECT_PERMANENCE_SETUP.EXIT
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_MOVEMENT
            ] = tags.CELLS.OBJECT_PERMANENCE_MOVEMENT.LINEAR
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_OBJECT_ONE
            ] = tags.CELLS.OBJECT_PERMANENCE_OBJECT_ONE.NO_CHANGE
            scene.goal.scene_info[
                tags.TYPES.OBJECT_PERMANENCE_NOVELTY_ONE
            ] = tags.CELLS.OBJECT_PERMANENCE_NOVELTY_ONE.NONE

        scenes = self._design_object_permanence_eval_4_scenes(scenes)

        # Finalize scenes.
        self._update_hypercube_scene_info_tags(scenes)

        return scenes

    # Override
    def _get_slices(self) -> List[str]:
        return [
            tags.TYPES.OBJECT_PERMANENCE_SETUP,
            tags.TYPES.OBJECT_PERMANENCE_MOVEMENT,
            tags.TYPES.OBJECT_PERMANENCE_OBJECT_ONE,
            tags.TYPES.OBJECT_PERMANENCE_NOVELTY_ONE
        ]

    def _design_object_permanence_eval_4_scenes(
        self,
        scenes: Dict[str, Scene]
    ) -> Dict[str, Scene]:
        target_id = self._target_list[0]['id']

        # Variations on the object.
        variations = self._variations_list[0]
        trained_variation = variations.get(VARIATIONS.TRAINED)
        move_stop = trained_variation['debug']['movement']['moveStop']

        # Switch the "exit" movement with the "stop" movement.
        scene = scenes['j1']
        scene.goal.scene_info[
            tags.TYPES.OBJECT_PERMANENCE_SETUP
        ] = tags.CELLS.OBJECT_PERMANENCE_SETUP.STOP
        for instance in scene.objects:
            if instance['id'] == target_id:
                is_positive = instance['forces'][0]['vector']['x'] > 0
                instance['forces'][0]['vector'] = {
                    'x': (
                        move_stop['forceX'] * instance['mass'] *
                        (1 if is_positive else -1)
                    ),
                    'y': 0,
                    'z': 0
                }
                # Remove any lingering momentum.
                instance['togglePhysics'] = [{
                    'stepBegin': (
                        instance['shows'][0]['stepBegin'] +
                        move_stop['stopStep'] + 1
                    )
                }]
                # Mark active movement name for testing and debugging.
                instance['debug']['movement']['active'] = 'moveStop'

        return scenes

    def _get_scene_ids(self) -> List[str]:
        # Only J1 and J2 are available for training.
        return ['j1', 'j2']


class SpatioTemporalContinuityHypercubeEval4(
    SpatioTemporalContinuityHypercube
):

    def __init__(
        self,
        starter_scene: Scene,
        role_to_type: Dict[str, str],
        training=False,
        is_fall_down=False,
        is_move_across=False
    ):
        super().__init__(
            starter_scene,
            role_to_type,
            is_fall_down=False,
            # All spatio-temporal continuity scenes are move-across in Eval 4.
            is_move_across=True,
            training=training
        )

    # Override
    def _does_have_deep_move(self) -> bool:
        """Return whether this hypercube must generate deep movement."""
        return True

    # Override
    def _does_have_toss_move(self) -> bool:
        """Return whether this hypercube must generate toss movement."""
        return True

    # Override
    def _get_move_across_object_count(self) -> int:
        """Return the number of objects for the move-across scene."""
        return 1

    # Override
    def _get_move_across_occluder_count(self) -> int:
        """Return the number of occluders for the move-across scene."""
        # This hypercube will generate two occluders, but for some reason this
        # function needs to return 1.
        return 1

    # Override
    def _get_object_max_z(self) -> int:
        """Return the maximum Z position for an object."""
        return MAX_TARGET_Z_RESTRICTED

    # Override
    def _get_occluder_height(self) -> int:
        """Return the occluder height to use."""
        return occluders.OCCLUDER_HEIGHT_TALL

    # Override
    def _init_each_object_definition_list(
        self,
        is_fall_down: bool,
        only_basic_shapes: bool,
        only_complex_shapes: bool
    ) -> None:
        """Set each object definition list needed by this hypercube, used in
        _choose_object_variations."""

        super()._init_each_object_definition_list(
            is_fall_down,
            only_basic_shapes,
            only_complex_shapes
        )

        # Don't use balls/spheres in Eval 4 Collision/OP/STC hypercubes.
        # They don't roll at the same pace as other objects.
        self._trained_dataset = self._trained_dataset.filter_on_type(
            cannot_be=['ball', 'sphere']
        )
        self._untrained_shape_dataset = (
            self._untrained_shape_dataset.filter_on_type(
                cannot_be=['ball', 'sphere']
            )
        )
        self._untrained_size_dataset = (
            self._untrained_size_dataset.filter_on_type(
                cannot_be=['ball', 'sphere']
            )
        )

    # Override
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Scene
    ) -> Dict[str, Scene]:
        """Create and return a collection of new intuitive physics scenes."""
        # Initialize scenes.
        scenes = {}
        for j in self._get_scene_ids():
            scenes[j] = copy.deepcopy(default_scene)

        # Initialize spatio temporal continuity tags in scenes.
        for scene in scenes.values():
            scene.goal.scene_info[
                tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_MOVEMENT
            ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_MOVEMENT.LINEAR
            scene.goal.scene_info[
                tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OBJECTS
            ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_OBJECTS.ONE
            scene.goal.scene_info[
                tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS
            ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS.TWO
            scene.goal.scene_info[
                tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_PLAUSIBLE
            ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_PLAUSIBLE.YES
            scene.goal.scene_info[
                tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_TARGET_TRAINED
            ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_TARGET_TRAINED.YES

        scenes = self._design_spatio_temporal_continuity_eval_4_scenes(scenes)

        # Finalize scenes.
        self._update_hypercube_scene_info_tags(scenes)

        return scenes

    # Override
    def _get_slices(self) -> List[str]:
        return [
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_MOVEMENT,
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OBJECTS,
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS,
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_PLAUSIBLE,
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_TARGET_TRAINED
        ]

    def _design_spatio_temporal_continuity_eval_4_scenes(
        self,
        scenes: Dict[str, Scene]
    ) -> Dict[str, Scene]:
        # Remove every occluder.
        scene = scenes['e1']
        scene.goal.scene_info[
            tags.TYPES.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS
        ] = tags.CELLS.SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS.ZERO
        remove_id_list = [
            occluder['id'] for occluder in self._occluder_list
        ]
        scene.objects = [
            instance for instance in scene.objects
            if instance['id'] not in remove_id_list
        ]
        return scenes

    def _get_scene_ids(self) -> List[str]:
        # Only A1 and E1 are available for training.
        return ['a1', 'e1']


class CollisionsTrainingHypercubeFactory(HypercubeFactory):
    def __init__(self) -> None:
        super().__init__('CollisionTraining', training=True)

    def _build(self, starter_scene: Scene) -> Hypercube:
        return CollisionsHypercube(
            starter_scene,
            self.role_to_type,
            self.training
        )


class GravitySupportTrainingHypercubeFactory(HypercubeFactory):
    def __init__(self) -> None:
        super().__init__('GravitySupportTraining', training=True)

    def _build(self, starter_scene: Scene) -> Hypercube:
        return GravitySupportHypercube(
            starter_scene,
            self.role_to_type,
            self.training
        )


class ObjectPermanenceTraining4HypercubeFactory(HypercubeFactory):
    def __init__(self) -> None:
        super().__init__('ObjectPermanenceTraining', training=True)

    def _build(self, starter_scene: Scene) -> Hypercube:
        return ObjectPermanenceHypercubeEval4(
            starter_scene,
            self.role_to_type,
            self.training
        )


class ShapeConstancyTrainingHypercubeFactory(HypercubeFactory):
    def __init__(self) -> None:
        super().__init__('ShapeConstancyTraining', training=True)

    def _build(self, starter_scene: Scene) -> Hypercube:
        return ShapeConstancyHypercube(
            starter_scene,
            self.role_to_type,
            self.training,
            # All shape constancy scenes are fall-down in Eval 3.
            is_fall_down=True
        )


class SpatioTemporalContinuityTraining4HypercubeFactory(HypercubeFactory):
    def __init__(self) -> None:
        super().__init__('SpatioTemporalContinuityTraining', training=True)

    def _build(self, starter_scene: Scene) -> Hypercube:
        return SpatioTemporalContinuityHypercubeEval4(
            starter_scene,
            self.role_to_type,
            self.training
        )


class GravitySupportEvaluationHypercubeFactory(HypercubeFactory):
    def __init__(self) -> None:
        super().__init__('GravitySupport', training=False)

    def _build(self, starter_scene: Scene) -> Hypercube:
        return GravitySupportHypercube(
            starter_scene,
            self.role_to_type,
            self.training
        )


class ShapeConstancyEvaluationHypercubeFactory(HypercubeFactory):
    def __init__(self) -> None:
        super().__init__('ShapeConstancy', training=False)

    def _build(self, starter_scene: Scene) -> Hypercube:
        return ShapeConstancyHypercube(
            starter_scene,
            self.role_to_type,
            self.training,
            # All shape constancy scenes are fall-down in Eval 3.
            is_fall_down=True
        )


INTUITIVE_PHYSICS_TRAINING_HYPERCUBE_LIST = [
    CollisionsTrainingHypercubeFactory(),
    GravitySupportTrainingHypercubeFactory(),
    ObjectPermanenceTraining4HypercubeFactory(),
    ShapeConstancyTrainingHypercubeFactory(),
    SpatioTemporalContinuityTraining4HypercubeFactory()
]


INTUITIVE_PHYSICS_EVALUATION_HYPERCUBE_LIST = [
    GravitySupportEvaluationHypercubeFactory(),
    ShapeConstancyEvaluationHypercubeFactory()
]
