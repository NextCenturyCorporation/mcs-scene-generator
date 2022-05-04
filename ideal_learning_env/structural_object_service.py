from __future__ import annotations

import copy
import logging
import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import shapely
from machine_common_sense.config_manager import Vector3d

from generator import (
    ALL_LARGE_BLOCK_TOOLS,
    MAX_TRIES,
    MaterialTuple,
    ObjectBounds,
    geometry,
    gravity_support_objects,
    instances,
    intuitive_physics_objects,
    materials,
    mechanisms,
    occluders,
    specific_objects,
    structures,
)
from generator.base_objects import LARGE_BLOCK_TOOLS_TO_DIMENSIONS
from generator.scene import PartitionFloor, Scene
from ideal_learning_env.global_settings_component import (
    ROOM_MIN_XZ,
    ROOM_MIN_Y,
)
from ideal_learning_env.goal_services import TARGET_LABEL
from ideal_learning_env.interactable_object_service import (
    InteractableObjectConfig,
    InteractableObjectCreationService,
    KeywordLocationConfig,
)
from ideal_learning_env.object_services import (
    DEBUG_FINAL_POSITION_KEY,
    InstanceDefinitionLocationTuple,
    KeywordLocation,
    ObjectDefinition,
    ObjectRepository,
    RelativePositionConfig,
    add_random_placement_tag,
)

from .choosers import (
    SOCCER_BALL_SCALE_MAX,
    SOCCER_BALL_SCALE_MIN,
    choose_material_tuple_from_material,
    choose_position,
    choose_random,
    choose_rotation,
    choose_shape_material,
)
from .defs import ILEException, find_bounds
from .feature_creation_service import (
    BaseFeatureConfig,
    BaseObjectCreationService,
    FeatureCreationService,
    FeatureTypes,
    log_feature_template,
    position_relative_to,
    validate_all_locations_and_update_bounds,
)
from .numerics import (
    MinMaxFloat,
    MinMaxInt,
    VectorFloatConfig,
    VectorIntConfig,
)

logger = logging.getLogger(__name__)

# Magic numbers used to create ranges for size, location, scale etc for objects
PLATFORM_SCALE_MIN = 0.5
PLATFORM_SCALE_MAX = 3
RAMP_WIDTH_PERCENT_MIN = 0.05
RAMP_WIDTH_PERCENT_MAX = 0.5
RAMP_LENGTH_PERCENT_MIN = 0.05
RAMP_LENGTH_PERCENT_MAX = 1
WALL_WIDTH_PERCENT_MIN = 0.05
WALL_WIDTH_PERCENT_MAX = 0.5
RAMP_ANGLE_MIN = 15
RAMP_ANGLE_MAX = 45
L_OCCLUDER_SCALE_MIN = 0.5
L_OCCLUDER_SCALE_MAX = 2
DROPPER_THROWER_BUFFER = 0.2
# Ranges for Occluders when values are not specified
DEFAULT_MOVING_OCCLUDER_HEIGHT_MIN = 1
DEFAULT_MOVING_OCCLUDER_HEIGHT_MAX = occluders.OCCLUDER_HEIGHT_TALL
DEFAULT_MOVING_OCCLUDER_WIDTH_MIN = occluders.OCCLUDER_MIN_SCALE_X
DEFAULT_MOVING_OCCLUDER_WIDTH_MAX = 3
DEFAULT_MOVING_OCCLUDER_THICKNESS_MIN = occluders.OCCLUDER_THICKNESS
DEFAULT_MOVING_OCCLUDER_THICKNESS_MAX = occluders.OCCLUDER_THICKNESS
DEFAULT_MOVING_OCCLUDER_REPEAT_MIN = 1
DEFAULT_MOVING_OCCLUDER_REPEAT_MAX = 20
DEFAULT_OCCLUDER_ROTATION_MIN = 0
DEFAULT_OCCLUDER_ROTATION_MAX = 359
DEFAULT_OCCLUDING_WALL_HEIGHT = MinMaxFloat(1, 2)
DEFAULT_OCCLUDING_WALL_THICKNESS = MinMaxFloat(0.1, 0.5)
DEFAULT_OCCLUDING_WALL_WIDTH = MinMaxFloat(1, 2)

# multiply target's scale by these values to make
# sure target is sufficiently occluded.
DEFAULT_OCCLUDING_WALL_HEIGHT_MULTIPLIER = 3.0
DEFAULT_OCCLUDING_WALL_WIDTH_MULTIPLIER = 2.0

# Agents can wall over 0.1 height walls but not 0.15
DEFAULT_OCCLUDING_WALL_SHORT_SCALE_Y_MIN = 0.15

DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MIN = 0.2
DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MAX = 0.5

# Height of 0.9 blocks agent, but doesn't look like it should visually
OCCLUDING_WALL_HOLE_MAX_HEIGHT = 0.8
OCCLUDING_WALL_WIDTH_BUFFER = 0.6

ATTACHED_RAMP_MIN_WIDTH = .5
ATTACHED_RAMP_MAX_WIDTH = 1.5
ATTACHED_RAMP_MAX_LENGTH = 3
ATTACHED_RAMP_MIN_LENGTH = .5
TOP_PLATFORM_POSITION_MIN = 0.3

# These are arbitrary but they need to be high enough that a ramp can get up
# the top platform without being greater than 45 degress.
BOTTOM_PLATFORM_SCALE_BUFFER_MIN = geometry.PERFORMER_WIDTH
BOTTOM_PLATFORM_SCALE_BUFFER_MAX = 5

# used to determine where ramps can fit next to platforms.  When on the floor,
# we don't have a good way to determine this (particularly when rotated) so we
# use an arbitrarily large number and let the bounds checking determine if
# locations are valid later.
DEFAULT_AVAIABLE_LENGTHS = (10, 10, 10, 10)
RAMP_ROTATIONS = (90, 180, -90, 0)

# Labels for platforms/ramps
LABEL_PLATFORM = "platforms"
LABEL_RAMP = "ramps"
LABEL_BIDIRECTIONAL_RAMP = "bidirectional"
LABEL_CONNECTED_TO_RAMP = "connected_to_ramp"


def _retrieve_scaled_shapes_from_datasets(
    shapes_to_scales: Dict[str, List[Vector3d]]
) -> Dict[str, List[Union[MinMaxFloat, VectorFloatConfig]]]:
    """Return a dict mapping each shape in the given data to each scale
    option, maintaining its aspect ratio, to use as possible default scales."""
    output = {}
    for shape, scales in shapes_to_scales.items():
        if shape not in output:
            output[shape] = []
        output[shape].extend([
            VectorFloatConfig(x=scale.x, y=scale.y, z=scale.z)
            for scale in scales
        ])
    # Override soccer ball scales with specific ILE limitations.
    if 'soccer_ball' in output:
        # Use a single MinMaxFloat to ensure the ball has equal X/Y/Z scales.
        output['soccer_ball'] = [MinMaxFloat(
            min=SOCCER_BALL_SCALE_MIN,
            max=SOCCER_BALL_SCALE_MAX
        )]
    # Remove duplicate scales from the output.
    for shape in output.keys():
        unique_output = []
        for scale in output[shape]:
            if scale not in unique_output:
                unique_output.append(scale)
        output[shape] = unique_output
    return output


DROPPER_SHAPES_TO_SCALES = _retrieve_scaled_shapes_from_datasets({
    **specific_objects.ROLLABLE_TYPES_TO_SIZES,
    **intuitive_physics_objects.FALL_DOWN_TYPES_TO_SIZES,
    **gravity_support_objects.TYPES_TO_SIZES
})
DROPPER_SHAPES = sorted(list(DROPPER_SHAPES_TO_SCALES.keys()))

PLACER_SHAPES_TO_SCALES = _retrieve_scaled_shapes_from_datasets({
    **specific_objects.ROLLABLE_TYPES_TO_SIZES,
    **specific_objects.CONTAINER_TYPES_TO_SIZES,
    **intuitive_physics_objects.FALL_DOWN_TYPES_TO_SIZES,
    **gravity_support_objects.TYPES_TO_SIZES
})
PLACER_SHAPES = sorted(list(PLACER_SHAPES_TO_SCALES.keys()))

THROWER_SHAPES_TO_SCALES = _retrieve_scaled_shapes_from_datasets({
    **specific_objects.ROLLABLE_TYPES_TO_SIZES,
    **intuitive_physics_objects.MOVE_ACROSS_TYPES_TO_SIZES
})
THROWER_SHAPES = sorted(list(THROWER_SHAPES_TO_SCALES.keys()))


class WallSide(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    FRONT = "front"
    BACK = "back"


class OccluderOrigin(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    FRONT = "front"
    BACK = "back"
    TOP = "top"


class OccludingWallType(str, Enum):
    OCCLUDES = "occludes"
    THIN = "thin"
    SHORT = "short"
    HOLE = "hole"


class StructuralWallCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_WALL
        self._type = FeatureTypes.WALLS

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: StructuralWallConfig,
            source_template: StructuralWallConfig):
        """Creates a wall from the given template with
        specific values."""
        room_height = (
            scene.room_dimensions.y or geometry.DEFAULT_ROOM_DIMENSIONS['y'])
        args = {
            'position_x': reconciled.position.x,
            'position_y_modifier': reconciled.position.y,
            'position_z': reconciled.position.z,
            'rotation_y': reconciled.rotation_y,
            'material_tuple':
                choose_material_tuple_from_material(reconciled.material),
            'width': reconciled.width,
            'height': room_height
        }

        logger.trace(f'Creating interior wall:\nINPUT = {args}')
        new_obj = structures.create_interior_wall(
            **args)
        new_obj = _post_instance(
            scene, new_obj, reconciled, source_template, self._get_type())
        return new_obj

    def _handle_dependent_defaults(
            self, scene: Scene, template: StructuralWallConfig, source_template
    ) -> StructuralWallConfig:
        template = _handle_position_material_defaults(scene, template)
        _, max_room_dim = _get_room_min_max_dimensions(scene)
        template.rotation_y = (
            random.choice([0, 90, 180, 270])
            if template.rotation_y is None else
            template.rotation_y
        )
        template.position.y = 0
        template.width = (MinMaxFloat(
            max_room_dim * WALL_WIDTH_PERCENT_MIN,
            max_room_dim * WALL_WIDTH_PERCENT_MAX).convert_value()
            if template.width is None else template.width)
        return template

    def is_valid(self, scene, new_obj, bounds, try_num, retries):
        valid = (not is_wall_too_close(new_obj[0]))
        return valid and super().is_valid(
            scene, new_obj, bounds, try_num, retries)


class StructuralPlatformCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_PLATFORM
        self._type = FeatureTypes.PLATFORMS

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: StructuralPlatformConfig,
            source_template: StructuralPlatformConfig):
        """Creates a platform from the given template with
        specific values."""
        x = (
            reconciled.scale.x if isinstance(
                reconciled.scale,
                (Vector3d, VectorFloatConfig)) else reconciled.scale)
        y = (
            reconciled.scale.y if isinstance(
                reconciled.scale,
                (Vector3d, VectorFloatConfig)) else reconciled.scale)
        z = (
            reconciled.scale.z if isinstance(
                reconciled.scale,
                (Vector3d, VectorFloatConfig)) else reconciled.scale)
        args = {
            'position_x': reconciled.position.x,
            'position_y_modifier': reconciled.position.y,
            'position_z': reconciled.position.z,
            'rotation_y': reconciled.rotation_y,
            'material_tuple':
                choose_material_tuple_from_material(reconciled.material),
            'lips': reconciled.lips,
            'scale_x': x,
            'scale_y': y,
            'scale_z': z,
            'room_dimension_y': scene.room_dimensions.y,
            'auto_adjust_platform': reconciled.auto_adjust_platforms
        }

        logger.trace(f'Creating platform:\nINPUT = {args}')
        new_obj = [structures.create_platform(**args)]
        new_obj = _post_instance(
            scene, new_obj, reconciled, source_template, self._get_type())
        return new_obj

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: StructuralPlatformConfig,
            source_template
    ) -> StructuralPlatformConfig:
        reconciled = _handle_position_material_defaults(scene, reconciled)
        room_height = (
            scene.room_dimensions.y or geometry.DEFAULT_ROOM_DIMENSIONS['y'])
        # Wall height always equals room height.

        scale = Vector3d()
        if isinstance(reconciled.scale, Vector3d):
            scale.x = reconciled.scale.x
            # Restrict max height to room height.
            scale.y = min(reconciled.scale.y, room_height)
            scale.z = reconciled.scale.z
        else:
            scale.x = reconciled.scale
            # Restrict max height to room height.
            scale.y = min(reconciled.scale, room_height)
            scale.z = reconciled.scale
        reconciled.scale = scale
        return reconciled


class StructuralRampCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_RAMP
        self._type = FeatureTypes.RAMPS

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: StructuralRampConfig,
            source_template: StructuralRampConfig):
        """Creates a ramp from the given template with
        specific values."""
        args = {
            'position_x': reconciled.position.x,
            'position_y_modifier': reconciled.position.y,
            'position_z': reconciled.position.z,
            'rotation_y': reconciled.rotation_y,
            'material_tuple':
                choose_material_tuple_from_material(reconciled.material),
            'angle': reconciled.angle,
            'width': reconciled.width,
            'length': reconciled.length
        }

        logger.trace(f'Creating ramp:\nINPUT = {args}')
        new_obj = structures.create_ramp(**args)
        new_obj = _post_instance(
            scene, new_obj, reconciled, source_template, self._get_type())
        return new_obj

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: StructuralRampConfig,
            source_template
    ) -> StructuralRampConfig:
        reconciled = _handle_position_material_defaults(scene, reconciled)
        room_height = (
            scene.room_dimensions.y or geometry.DEFAULT_ROOM_DIMENSIONS['y'])
        min_room_dim, _ = _get_room_min_max_dimensions(scene)

        max_length = (
            (room_height - geometry.PERFORMER_HEIGHT) /
            math.tan(math.radians(reconciled.angle))
        )
        reconciled.width = getattr(reconciled, 'width', None) or MinMaxFloat(
            min_room_dim * RAMP_WIDTH_PERCENT_MIN,
            min_room_dim * RAMP_WIDTH_PERCENT_MAX
        ).convert_value()
        reconciled.length = getattr(reconciled, 'length', None) or MinMaxFloat(
            min_room_dim * RAMP_LENGTH_PERCENT_MIN,
            min(min_room_dim * RAMP_LENGTH_PERCENT_MAX, max_length)
        ).convert_value()
        return reconciled


class StructuralLOccluderCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_L_OCCLUDER
        self._type = FeatureTypes.L_OCCLUDERS

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: StructuralLOccluderConfig,
            source_template: StructuralLOccluderConfig):
        """Attempts to adds an L occluder from the given template with
        specific values."""
        args = {
            'flip': reconciled.backwards,
            'position_x': reconciled.position.x,
            'position_y_modifier': reconciled.position.y,
            'position_z': reconciled.position.z,
            'rotation_y': reconciled.rotation_y,
            'material_tuple':
                choose_material_tuple_from_material(reconciled.material),
            'scale_front_x': reconciled.scale_front_x,
            'scale_front_z': reconciled.scale_front_z,
            'scale_side_x': reconciled.scale_side_x,
            'scale_side_z': reconciled.scale_side_z,
            'scale_y': reconciled.scale_y
        }

        logger.trace(f'Creating l occluder:\nINPUT = {args}')
        new_obj = structures.create_l_occluder(
            **args)
        new_obj = _post_instance(
            scene, new_obj, reconciled, source_template, self._get_type())
        return new_obj

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: StructuralLOccluderConfig,
            source_template
    ) -> StructuralLOccluderConfig:
        reconciled = _handle_position_material_defaults(scene, reconciled)
        room_height = (
            scene.room_dimensions.y or geometry.DEFAULT_ROOM_DIMENSIONS['y'])
        reconciled.scale_y = min(reconciled.scale_y, room_height)
        return reconciled


class StructuralDropperCreationService(
        BaseObjectCreationService):
    bounds = []
    dropper = None

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_DROPPER
        self._type = FeatureTypes.DROPPERS

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: StructuralDropperConfig,
            source_template: StructuralDropperConfig):
        """Creates a dropper from the given template with
        specific values."""
        room_dim = scene.room_dimensions
        self.target, self.target_exists = _get_projectile_idl(
            reconciled,
            scene,
            self.bounds or [],
            DROPPER_SHAPES_TO_SCALES
        )
        projectile_dimensions = vars(self.target.definition.dimensions)
        args = {
            'position_x': reconciled.position_x,
            'position_z': reconciled.position_z,
            'room_dimensions_y': room_dim.y,
            'object_dimensions': projectile_dimensions,
            'last_step': scene.goal.get('last_step'),
            'dropping_step': reconciled.drop_step,
            'is_round': ('ball' in self.target.definition.shape)
        }
        logger.trace(f'Creating dropper:\nINPUT = {args}')
        new_obj = [
            mechanisms.create_dropping_device(
                **args)
        ]
        self.dropper = new_obj[0]
        if not self.target_exists:
            new_obj.append(self.target.instance)

        add_random_placement_tag(new_obj, source_template)
        return new_obj

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: StructuralDropperConfig,
            source_template
    ) -> StructuralDropperConfig:
        buffer = DROPPER_THROWER_BUFFER
        room_dim = scene.room_dimensions
        reconciled.position_x = (
            random.uniform(-room_dim.x /
                           2.0 + buffer, room_dim.x / 2.0 - buffer)
            if reconciled.position_x is None else reconciled.position_x)
        reconciled.position_z = (
            random.uniform(-room_dim.z /
                           2.0 + buffer, room_dim.z / 2.0 - buffer)
            if reconciled.position_z is None else reconciled.position_z)

        # If needed, adjust this device's position relative to another object.
        if source_template.position_relative:
            position_x, position_z = position_relative_to(
                # Use the config list from the source template.
                source_template.position_relative,
                (reconciled.position_x, reconciled.position_z),
                scene.performer_start.position,
                'dropping device'
            )
            if position_x is not None:
                reconciled.position_x = position_x
            if position_z is not None:
                reconciled.position_z = position_z

        # Save the projectile labels from the source template.
        self._target_labels = source_template.projectile_labels

        return reconciled

    def _on_valid_instances(self, scene, reconciled_template, new_obj):
        super()._on_valid_instances(scene, reconciled_template, new_obj)
        self._do_post_add(scene, reconciled_template)

    def _do_post_add(self, scene, reconciled):
        args = {
            'instance': self.target.instance,
            'dropping_device': self.dropper,
            'dropping_step': reconciled.drop_step
        }
        logger.trace(f'Positioning dropper object:\nINPUT = {args}')
        mechanisms.drop_object(**args)
        self.target.instance['debug']['positionedBy'] = 'mechanism'
        self.target.instance['debug'][DEBUG_FINAL_POSITION_KEY] = True

        if not self.target_exists:
            log_feature_template(
                'dropper object',
                'id',
                self.target.instance['id']
            )
        else:
            for i in range(len(scene.objects)):
                if scene.objects[i]['id'] == self.target.instance['id']:
                    scene.objects[i] = self.target.instance

        object_repo = ObjectRepository.get_instance()
        object_repo.add_to_labeled_objects(self.target, self._target_labels)


class StructuralThrowerCreationService(
        BaseObjectCreationService):
    bounds = []
    thrower = None

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_THROWER
        self._type = FeatureTypes.THROWERS

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: StructuralThrowerConfig,
            source_template: StructuralThrowerConfig):
        """Creates a thrower from the given template with
        specific values."""
        room_dim = scene.room_dimensions
        # Don't want to validate against the walls since the throwers
        # intentionally intersect with walls.
        room_dimensions_extended = Vector3d(
            x=room_dim.x + 2,
            y=room_dim.y,
            z=room_dim.z + 2
        )
        scene_copy = copy.deepcopy(scene)
        scene_copy.room_dimensions = room_dimensions_extended
        self.target, self.target_exists = _get_projectile_idl(
            reconciled,
            scene_copy,
            self.bounds or [],
            THROWER_SHAPES_TO_SCALES
        )
        wall_rot = {
            WallSide.LEFT.value: 0,
            WallSide.RIGHT: 180,
            WallSide.FRONT: 90,
            WallSide.BACK: 270}
        projectile_dimensions = vars(self.target.definition.dimensions)
        max_scale = max(projectile_dimensions['x'], projectile_dimensions['z'])
        wall = reconciled.wall
        if wall in [WallSide.FRONT, WallSide.BACK]:
            pos_x = reconciled.position_wall
            pos_z = (room_dim.z - max_scale) / \
                2.0 if wall == WallSide.FRONT else -(
                room_dim.z - max_scale) / 2.0
        if wall in [WallSide.LEFT, WallSide.RIGHT]:
            pos_z = reconciled.position_wall
            pos_x = -(room_dim.x - max_scale) / \
                2.0 if wall == WallSide.LEFT else (
                    room_dim.x - max_scale) / 2.0

        args = {
            'position_x': pos_x,
            'position_y': reconciled.height,
            'position_z': pos_z,
            'rotation_y': wall_rot[wall] + reconciled.rotation_y,
            'rotation_z': reconciled.rotation_z,
            'object_dimensions': projectile_dimensions,
            'object_rotation_y': self.target.definition.rotation.y,
            'last_step': scene.goal.get('last_step'),
            'throwing_step': reconciled.throw_step,
            'is_round': ('ball' in self.target.definition.shape)
        }
        logger.trace(f'Creating thrower:\nINPUT = {args}')
        new_obj = [
            mechanisms.create_throwing_device(
                **args)]
        self.thrower = new_obj[0]
        if not self.target_exists:
            new_obj.append(self.target.instance)

        add_random_placement_tag(new_obj, source_template)
        return new_obj

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: StructuralThrowerConfig,
            source_template
    ) -> StructuralThrowerConfig:
        room_dim = scene.room_dimensions
        buffer = DROPPER_THROWER_BUFFER
        on_side_wall = reconciled.wall in [WallSide.LEFT, WallSide.RIGHT]
        if reconciled.position_wall is None:
            if not on_side_wall:
                reconciled.position_wall = random.uniform(
                    -room_dim.x / 2.0 + buffer, room_dim.x /
                    2.0 - buffer)
            else:
                reconciled.position_wall = random.uniform(
                    -room_dim.z /
                    2.0 + buffer, room_dim.z /
                    2.0 - buffer)

        if reconciled.height is None:
            reconciled.height = random.uniform(
                buffer, room_dim.y - buffer)

        # If needed, adjust this device's position relative to another object.
        if source_template.position_relative:
            position_x, position_z = position_relative_to(
                # Use the config list from the source template.
                source_template.position_relative,
                (
                    reconciled.position_wall if not on_side_wall else 0,
                    reconciled.position_wall if on_side_wall else 0
                ),
                scene.performer_start.position,
                'throwing device'
            )
            if not on_side_wall and position_x is not None:
                reconciled.position_wall = position_x
            if on_side_wall and position_z is not None:
                reconciled.position_wall = position_z

        # Save the projectile labels from the source template.
        self._target_labels = source_template.projectile_labels

        return reconciled

    def is_valid(self, scene, new_obj, bounds, try_num, retries):
        # droppers are intentionally embedded in walls.
        altered_scene: Scene = copy.deepcopy(scene)
        altered_scene.room_dimensions.x += 2
        altered_scene.room_dimensions.z += 2
        # Throwers should ignore the holes and lava directly underneath them.
        bounds = find_bounds(scene, ignore_ground=True)
        return super().is_valid(
            altered_scene, new_obj, bounds, try_num, retries)

    def _on_valid_instances(self, scene, reconciled_template, new_obj):
        super()._on_valid_instances(scene, reconciled_template, new_obj)
        self._do_post_add(scene, reconciled_template)

    def _do_post_add(self, scene, reconciled):
        thrower = self.thrower
        force = reconciled.throw_force
        if reconciled.throw_force_multiplier:
            force = reconciled.throw_force_multiplier
            room_size = scene.room_dimensions
            on_side_wall = reconciled.wall in [WallSide.LEFT, WallSide.RIGHT]
            force *= room_size.x if on_side_wall else room_size.z
        elif force is None:
            force = choose_random(
                DEFAULT_THROW_FORCE_IMPULSE if reconciled.impulse else
                DEFAULT_THROW_FORCE_NON_IMPULSE
            )
        force *= self.target.definition.mass
        args = {
            'instance': self.target.instance,
            'throwing_device': thrower,
            'throwing_force': force,
            'throwing_step': reconciled.throw_step,
            'impulse': reconciled.impulse
        }
        logger.trace(f'Positioning thrower object:\nINPUT = {args}')
        self.target.instance['debug']['positionedBy'] = 'mechanism'
        self.target.instance['debug'][DEBUG_FINAL_POSITION_KEY] = True
        mechanisms.throw_object(**args)
        if not self.target_exists:
            log_feature_template(
                'thrower object',
                'id',
                self.target.instance['id']
            )
        else:
            for i in range(len(scene.objects)):
                if scene.objects[i]['id'] == self.target.instance['id']:
                    scene.objects[i] = self.target.instance

        object_repo = ObjectRepository.get_instance()
        object_repo.add_to_labeled_objects(self.target, self._target_labels)


class StructuralMovingOccluderCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_MOVING_OCCLUDER
        self._type = FeatureTypes.MOVING_OCCLUDERS

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: StructuralMovingOccluderConfig,
            source_template: StructuralMovingOccluderConfig):
        """Creates a moving occluder from the given template with
        specific values."""
        room_dim = scene.room_dimensions
        last_step_arg = scene.goal.get('last_step') if (
            not reconciled.repeat_movement and
            reconciled.move_up_before_last_step
        ) else None
        repeat_movement_arg = (
            None if not reconciled.repeat_movement else
            reconciled.repeat_interval
        )
        args = {
            'wall_material':
                choose_material_tuple_from_material(reconciled.wall_material),
            'pole_material':
                choose_material_tuple_from_material(reconciled.pole_material),
            'x_position': reconciled.position_x,
            'occluder_width': reconciled.occluder_width,
            'occluder_height': reconciled.occluder_height,
            'occluder_thickness': reconciled.occluder_thickness,
            'last_step': last_step_arg,
            'repeat_movement': repeat_movement_arg,
            'reverse_direction': reconciled.reverse_direction,
            'room_dimensions': vars(room_dim),
            'sideways_back': reconciled.origin == OccluderOrigin.BACK,
            'sideways_front': reconciled.origin == OccluderOrigin.FRONT,
            'sideways_left': reconciled.origin == OccluderOrigin.LEFT,
            'sideways_right': reconciled.origin == OccluderOrigin.RIGHT,
            'y_rotation': reconciled.rotation_y,
            'z_position': reconciled.position_z
        }

        logger.trace(f'Creating moving occluder:\nINPUT = {args}')
        new_obj = occluders.create_occluder(**args)
        new_obj = _post_instance(
            scene, new_obj, reconciled, source_template, self._get_type())
        return new_obj

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: StructuralMovingOccluderConfig,
            source_template
    ) -> StructuralMovingOccluderConfig:
        room_dim = scene.room_dimensions
        max_size = max(
            reconciled.occluder_thickness,
            reconciled.occluder_width)
        limit_x = room_dim.x - max_size
        limit_z = room_dim.z - max_size
        limit_x /= 2.0
        limit_z /= 2.0
        reconciled.position_x = (
            reconciled.position_x if reconciled.position_x is not None
            else random.uniform(-limit_x, limit_x))
        reconciled.position_z = (
            reconciled.position_z if reconciled.position_z is not None
            else random.uniform(-limit_z, limit_z))
        reconciled.occluder_height = min(
            reconciled.occluder_height, room_dim.y)
        reconciled.wall_material = _reconcile_material(
            reconciled.wall_material,
            materials.ROOM_WALL_MATERIALS
        )
        reconciled.pole_material = _reconcile_material(
            reconciled.pole_material,
            materials.METAL_MATERIALS
        )
        return reconciled

    def _on_valid_instances(self, scene, reconciled_template, new_obj):
        super()._on_valid_instances(scene, reconciled_template, new_obj)
        # Remove the template's labels from the occluder's pole; we only ever
        # want the configured labels to reference the occluder's wall.
        ObjectRepository.get_instance().remove_from_labeled_objects(
            new_obj[1]['id'],
            reconciled_template.labels
        )


class StructuralPartitionFloorCreationService(BaseObjectCreationService):
    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_PARTITION_FLOOR
        self._type = FeatureTypes.PARTITION_FLOOR

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: PartitionFloorConfig,
            source_template: PartitionFloorConfig):
        return PartitionFloor(reconciled.leftHalf,
                              reconciled.rightHalf)

    def is_valid(self, scene: Scene, partitions: List,
                 bounds, try_num, retries):
        if partitions:
            part_bounds = geometry.find_partition_floor_bounds(
                scene.room_dimensions, partitions[0])
            for bb in part_bounds:
                if not geometry.validate_location_rect(
                    bb,
                    vars(scene.performer_start.position),
                    bounds,
                    vars(scene.room_dimensions)
                ):
                    return False
        return True

    def _on_valid_instances(
            self, scene: Scene, reconciled_template, partitions):
        if partitions:
            scene.partition_floor = partitions[0]
            log_feature_template(
                'partition_floor', 'partition_floor',
                partitions[0], [reconciled_template])


class StructuralLavaCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_HOLES_LAVA
        self._type = FeatureTypes.LAVA

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: FloorAreaConfig,
            source_template: FloorAreaConfig):
        """Creates lava from the given template with
        specific values."""
        return {'x': reconciled.position_x, 'z': reconciled.position_z}

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: FloorAreaConfig, source_template
    ) -> FloorAreaConfig:
        _add_floor_dependent_defaults(scene, reconciled)
        return reconciled

    def is_valid(self, scene: Scene, lava_pos: List, bounds, try_num, retries):
        return _is_valid_floor(
            scene,
            lava_pos[0],
            'lava',
            True,
            bounds,
            try_num,
            retries, self._get_type())

    def _on_valid_instances(self, scene, reconciled_template, new_obj):
        scene.lava += new_obj
        log_feature_template(
            'lava', 'lava', new_obj, [reconciled_template])


class StructuralHolesCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_HOLES_LAVA
        self._type = FeatureTypes.HOLES

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: FloorAreaConfig,
            source_template: FloorAreaConfig):
        """Creates a hole from the given template with
        specific values."""
        return {'x': reconciled.position_x, 'z': reconciled.position_z}

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: FloorAreaConfig, source_template
    ) -> FloorAreaConfig:
        _add_floor_dependent_defaults(scene, reconciled)
        return reconciled

    def is_valid(self, scene: Scene, lava_pos: List, bounds, try_num, retries):
        return _is_valid_floor(
            scene,
            lava_pos[0],
            'holes',
            True,
            bounds,
            try_num,
            retries, self._get_type())

    def _on_valid_instances(self, scene, reconciled_template, new_obj):
        scene.holes += new_obj
        log_feature_template(
            'holes', 'holes', new_obj, [reconciled_template])


class StructuralFloorMaterialsCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_FLOOR_MATERIALS
        self._type = FeatureTypes.FLOOR_MATERIALS

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: FloorMaterialConfig,
            source_template: FloorMaterialConfig):
        """Returns the floor material template.  This creation service
        uses the specific template itself to add to scene instead of
        creating it first."""
        return reconciled

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: FloorMaterialConfig,
            source_template
    ) -> FloorMaterialConfig:
        _add_floor_dependent_defaults(scene, reconciled)
        reconciled.material = _reconcile_material(
            reconciled.material,
            materials.WALL_MATERIALS
        )
        return reconciled

    def is_valid(self, scene: Scene, objs: List, bounds, try_num, retries):
        template: FloorMaterialConfig = objs[0]
        room_dim = scene.room_dimensions
        x = template.position_x
        z = template.position_z
        xmax = math.floor(room_dim.x / 2)
        zmax = math.floor(room_dim.z / 2)
        valid = not (x < -xmax or x > xmax or z < -zmax or z > zmax)
        if not valid:
            return False

        # make sure there is no lava here
        lava = scene.lava or []
        pos = {'x': template.position_x, 'z': template.position_z}
        if pos in lava:
            return False
        for existing in scene.floor_textures:
            for existing_pos in existing['positions']:
                if (existing_pos['x'] == template.position_x and
                        existing_pos['z'] == template.position_z):
                    return False
        return True

    def _on_valid_instances(
            self, scene: Scene, reconciled: FloorMaterialConfig,
            new_obj):
        mat = reconciled.material
        pos = {'x': reconciled.position_x, 'z': reconciled.position_z}
        added = False
        for existing in scene.floor_textures:
            if existing['material'] == mat:
                existing['positions'].append(pos)
                added = True
        if not added:
            scene.floor_textures.append({'material': mat, 'positions': [pos]})
        log_feature_template(
            'floor_materials', 'floor_materials', new_obj, [reconciled])


class StructuralOccludingWallsCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_OCCLUDING_WALL
        self._type = FeatureTypes.OCCLUDING_WALLS

    def create_feature_from_specific_values(
            self, scene: Scene, template: StructuralOccludingWallConfig,
            source_template: StructuralOccludingWallConfig):
        """Not currently implemented.  This creation service overrides
        add_to_scene itself for now."""
        room_dim = scene.room_dimensions
        defn = _get_occluding_wall_definition(template)
        if (template.keyword_location is not None):
            # setup keyword location
            idl = KeywordLocation.get_keyword_location_object_tuple(
                template.keyword_location, defn, scene.performer_start,
                self.bounds, room_dim)
            idl.instance['id'] = f"{template.type}-{idl.instance['id']}"
            result = _modify_for_hole(
                template.type, idl.instance, self.target_dim)
        else:
            # setup x, z location
            defn.scale = template.scale

            location = {
                'position': {
                    'x': template.position.x,
                    'y': template.scale.y / 2.0,
                    'z': template.position.z
                },
                'rotation': {
                    'x': 0,
                    'y': template.rotation_y,
                    'z': 0
                }
            }
            inst = instances.instantiate_object(defn, location)
            inst = structures.finalize_structural_object([inst])[0]
            inst['id'] = f"{template.type}-{inst['id']}"
            result = _modify_for_hole(template.type, inst, self.target_dim)
        add_random_placement_tag(result, source_template)
        return result

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: StructuralOccludingWallConfig,
            source_template: StructuralOccludingWallConfig
    ) -> StructuralOccludingWallConfig:
        obj_repo = ObjectRepository.get_instance()

        reconciled.material = _reconcile_material(
            reconciled.material,
            materials.ROOM_WALL_MATERIALS
        )

        if (
            reconciled.keyword_location is None and
            reconciled.position.x is None and
            reconciled.position.y is None and
            reconciled.position.z is None and
            any([(not idl.instance['debug'].get('positionedBy')) for idl in (
                obj_repo.get_all_from_labeled_objects(TARGET_LABEL)
                if obj_repo.has_label(TARGET_LABEL) else []
            )])
        ):
            reconciled.keyword_location = KeywordLocationConfig(keyword=(
                'between' if reconciled.type == OccludingWallType.THIN else
                'occlude'
            ), relative_object_label=TARGET_LABEL)

        # For thin occluding walls, replace an 'occlude' keyword_location with
        # 'between' because using 'occlude' doesn't make sense for thin walls!
        # This also helps configuring randomly generating occluding walls.
        if (
            reconciled.keyword_location and
            reconciled.keyword_location.keyword == 'occlude' and
            reconciled.type == OccludingWallType.THIN
        ):
            reconciled.keyword_location.keyword = 'between'

        self.target = None
        if (
            reconciled.keyword_location and
            reconciled.keyword_location.relative_object_label
        ):
            label = reconciled.keyword_location.relative_object_label
            self.target = obj_repo.get_one_from_labeled_objects(label)
            if self.target:
                reconciled.keyword_location.relative_object_label = (
                    self.target.instance['id'])

        reconciled.scale, self.target_dim = _get_occluding_wall_scale(
            reconciled, self.target, scene.room_dimensions.y)

        scale = reconciled.scale
        room_dim = scene.room_dimensions
        max_size = math.sqrt(math.pow(scale.x, 2) +
                             math.pow(scale.z, 2))
        limit_x = room_dim.x - max_size
        limit_z = room_dim.z - max_size

        reconciled.position.x = (
            MinMaxFloat(-limit_x, limit_x).convert_value()
            if reconciled.position.x is None else reconciled.position.x
        )
        reconciled.position.z = (
            MinMaxFloat(-limit_z, limit_z).convert_value()
            if reconciled.position.z is None else reconciled.position.z
        )

        return reconciled


class StructuralPlacersCreationService(
        BaseObjectCreationService):
    object_idl = None
    bounds = []

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_PLACER
        self._type = FeatureTypes.PLACERS

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: StructuralPlacerConfig,
            source_template: StructuralPlacerConfig):
        """Creates a placer from the given template with
        specific values."""
        room_dim = scene.room_dimensions

        idl = self.object_idl
        geometry.move_to_location(idl.instance, {
            'position': vars(reconciled.placed_object_position),
            'rotation': vars(
                VectorIntConfig(0, reconciled.placed_object_rotation, 0)
            )
        })

        idl.instance['debug']['positionedBy'] = 'mechanism'
        idl.instance['debug'][DEBUG_FINAL_POSITION_KEY] = True

        start_height = reconciled.placed_object_position.y or room_dim.y
        max_height = room_dim.y
        last_step = scene.goal.get("last_step")
        instance = idl.instance
        defn = idl.definition

        args = {
            'instance': instance,
            'activation_step': reconciled.activation_step,
            'start_height': start_height,
            'end_height': reconciled.end_height,
            'deactivation_step': reconciled.deactivation_step
        }
        logger.trace(f'Positioning placer object:\nINPUT = {args}')
        mechanisms.place_object(**args)

        objs = []
        if idl.instance not in scene.objects:
            objs.append(idl.instance)

        for index, placer_offset_x in enumerate(defn.placerOffsetX or [0]):
            # Adjust the placer offset based on the object's Y rotation.
            offset_line = shapely.geometry.LineString([
                [0, 0],
                [placer_offset_x, 0]
            ])
            offset_line = shapely.affinity.rotate(
                offset_line,
                -reconciled.placed_object_rotation,
                origin=(0, 0)
            )
            resolved_offset_x, resolved_offset_z = list(offset_line.coords)[1]
            # Adjust the placer position based on the offsets.
            position = copy.deepcopy(instance['shows'][0]['position'])
            position['x'] += resolved_offset_x
            position['z'] += resolved_offset_z
            # Create the new placer and add it to the scene.
            args = {
                'placed_object_position': position,
                'placed_object_dimensions': instance['debug']['dimensions'],
                'placed_object_offset_y': instance['debug']['positionY'],
                'activation_step': reconciled.activation_step,
                'end_height': reconciled.end_height,
                'max_height': max_height,
                'id_modifier': None,
                'last_step': last_step,
                'placed_object_placer_offset_y': defn.placerOffsetY[index],
                'deactivation_step': reconciled.deactivation_step
            }
            logger.trace(f'Creating placer:\nINPUT = {args}')
            placer = mechanisms.create_placer(**args)
            _post_instance(
                scene,
                placer,
                reconciled,
                source_template,
                self._get_type())
            objs.append(placer)

        return objs

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: StructuralPlacerConfig,
            source_template
    ) -> StructuralPlacerConfig:
        labels = (source_template.placed_object_labels if source_template is
                  not None else None)
        self.labels = labels
        room_dim = scene.room_dimensions
        defn = None
        if labels:
            self.object_idl = _get_existing_held_object_idl(labels)

        if not self.object_idl:
            # Choose a shape now, so we can set the default scale accordingly.
            shape, material = choose_shape_material(
                reconciled.placed_object_shape,
                reconciled.placed_object_material
            )
            # Use SHAPES_TO_SCALES to choose a default scale for the shape.
            # If the shape isn't in SHAPES_TO_SCALES, then something is wrong,
            # so throw an error.
            scale = (
                reconciled.placed_object_scale or
                PLACER_SHAPES_TO_SCALES[shape]
            )
            # Don't set position or rotation for now; it will be done soon.
            obj_cfg = InteractableObjectConfig(
                num=1,
                scale=scale,
                shape=shape,
                material=(
                    material[0] if isinstance(material, MaterialTuple) else
                    material
                ),
                labels=self.labels)

            srv: InteractableObjectCreationService = (
                FeatureCreationService.get_service(FeatureTypes.INTERACTABLE))
            obj_reconciled = srv.reconcile(scene, obj_cfg)
            instance = srv.create_feature_from_specific_values(
                scene, obj_reconciled, obj_cfg)
            defn = getattr(srv, 'defn', None)
            self.object_idl = InstanceDefinitionLocationTuple(
                instance, defn, None)

        defn = defn or self.object_idl.definition
        reconciled.placed_object_rotation = choose_rotation(
            VectorIntConfig(0, reconciled.placed_object_rotation, 0)).y
        reconciled.placed_object_position = choose_position(
            reconciled.placed_object_position,
            defn.dimensions.x,
            defn.dimensions.z,
            room_dim.x,
            room_dim.y,
            room_dim.z
        )

        # If needed, adjust this placer's position relative to another object.
        if source_template.position_relative:
            position_x, position_z = position_relative_to(
                # Use the config list from the source template.
                source_template.position_relative,
                (
                    reconciled.placed_object_position.x,
                    reconciled.placed_object_position.z
                ),
                scene.performer_start.position,
                'placer'
            )
            if position_x is not None:
                reconciled.placed_object_position.x = position_x
            if position_z is not None:
                reconciled.placed_object_position.z = position_z

        # Save the projectile labels from the source template.
        self._target_labels = source_template.placed_object_labels

        return reconciled

    def _on_valid_instances(
            self, scene: Scene, reconciled_template: StructuralPlacerConfig,
            new_obj: dict, key: str = 'objects'):

        self.object_idl.instance['debug']['positionedBy'] = 'mechanism'
        self.object_idl.instance['debug'][DEBUG_FINAL_POSITION_KEY] = True

        object_repo = ObjectRepository.get_instance()
        object_repo.add_to_labeled_objects(
            self.object_idl,
            self._target_labels
        )

        return super()._on_valid_instances(
            scene, reconciled_template, new_obj, key)


class StructuralDoorsCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._type = FeatureTypes.DOORS
        self._default_template = DEFAULT_TEMPLATE_DOOR

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: StructuralDoorConfig,
            source_template: StructuralDoorConfig):
        """Creates a door from the given template with
        specific values."""
        args = {
            'position_x': reconciled.position.x,
            'position_y': reconciled.position.y,
            'position_z': reconciled.position.z,
            'rotation_y': reconciled.rotation_y,
            'material_tuple':
                choose_material_tuple_from_material(reconciled.material),
            'wall_scale_x': reconciled.wall_scale_x,
            'wall_scale_y': reconciled.wall_scale_y,
            'wall_material_tuple':
                choose_material_tuple_from_material(reconciled.wall_material)

        }
        logger.trace(f'Creating door:\nINPUT = {args}')
        door_objs = structures.create_door(**args)
        door = door_objs[0]
        _post_instance(
            scene,
            door,
            reconciled,
            source_template,
            self._get_type())
        add_random_placement_tag(door_objs, source_template)
        return door_objs

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: StructuralDoorConfig,
            source_template
    ) -> StructuralDoorConfig:
        room_dim = scene.room_dimensions
        def_dim = geometry.DEFAULT_ROOM_DIMENSIONS
        room_width = room_dim.x or def_dim['x']
        room_length = room_dim.z or def_dim['z']
        reconciled.wall_material = _reconcile_material(
            reconciled.wall_material, [
                materials.METAL_MATERIALS,
                materials.PLASTIC_MATERIALS,
                materials.WOOD_MATERIALS,
            ]
        )
        reconciled.position.x = choose_random(
            MinMaxFloat(-room_width / 2.0, room_width / 2.0)
            if reconciled.position.x is None else reconciled.position.x
        )
        reconciled.position.y = (0 if reconciled.position.y is None
                                 else reconciled.position.y)
        reconciled.position.z = choose_random(
            MinMaxFloat(-room_length / 2.0, room_length / 2.0)
            if reconciled.position.z is None else reconciled.position.z
        )
        rot = reconciled.rotation_y
        default_wall_scale_x = MinMaxInt(
            ROOM_MIN_XZ,
            room_dim.x if rot in [0, 180] else room_dim.z
        )
        reconciled.wall_scale_x = choose_random(
            default_wall_scale_x
            if reconciled.wall_scale_x is None else
            reconciled.wall_scale_x)

        reconciled.wall_scale_y = choose_random(
            MinMaxInt(ROOM_MIN_Y, room_dim.y)
            if reconciled.wall_scale_y is None else
            reconciled.wall_scale_y)
        return reconciled


class StructuralToolsCreationService(
        BaseObjectCreationService):

    def __init__(self):
        self._default_template = DEFAULT_TEMPLATE_TOOL
        self._type = FeatureTypes.TOOLS

    def create_feature_from_specific_values(
            self, scene: Scene, reconciled: ToolConfig,
            source_template: ToolConfig):
        """Creates a tool from the given template with
        specific values."""
        args = {
            'object_type': reconciled.shape,
            'position_x': reconciled.position.x,
            'position_z': reconciled.position.z,
            'rotation_y': reconciled.rotation_y
        }
        logger.trace(f'Creating tool:\nINPUT = {args}')
        obj = structures.create_tool(**args)
        _post_instance(
            scene,
            obj,
            reconciled,
            source_template,
            self._get_type())
        return obj

    def _handle_dependent_defaults(
            self, scene: Scene, reconciled: ToolConfig,
            source_template: ToolConfig
    ) -> ToolConfig:
        room_dim = scene.room_dimensions
        def_dim = geometry.DEFAULT_ROOM_DIMENSIONS
        room_width = room_dim.x or def_dim['x']
        room_length = room_dim.z or def_dim['y']
        reconciled.position.x = (
            MinMaxFloat(-room_width / 2.0, room_width / 2.0).convert_value()
            if reconciled.position.x is None else reconciled.position.x
        )
        reconciled.position.z = (
            MinMaxFloat(-room_length / 2.0, room_length / 2.0).convert_value()
            if reconciled.position.z is None else reconciled.position.z
        )
        if not source_template.shape and (
                reconciled.width or reconciled.length):
            reconciled.shape = self.get_tool_from_dimensions(
                reconciled.width, reconciled.length)

        return reconciled

    def get_tool_from_dimensions(self, orig_width, orig_length):
        width = orig_width
        length = orig_length
        valid_widths = set()
        valid_lengths = set()
        for dim in LARGE_BLOCK_TOOLS_TO_DIMENSIONS.values():
            valid_widths.add(dim[0])
            valid_lengths.add(dim[1])
        if not width:
            width = choose_random(list(valid_widths))
        if not length:
            length = choose_random(list(valid_lengths))
        for shape, dim in LARGE_BLOCK_TOOLS_TO_DIMENSIONS.items():
            if dim == (width, length):
                return shape
        # For exception message, if no width or lenght specified,
        # just apply the word 'any'
        width = width or "Any"
        length = length or "Any"
        raise ILEException(
            f"Unable to find valid tool with dimensions width={width} "
            f"length={length}")


@dataclass
class PositionableStructuralObjectsConfig(BaseFeatureConfig):
    """Simple class used for user-positionable structural objects."""
    position: Union[VectorFloatConfig, List[VectorFloatConfig]] = None
    rotation_y: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    material: Union[str, List[str]] = None


@dataclass
class StructuralWallConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural interior wall.  The wall will be the
    height of the room.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "walls"
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): The width of the wall.
    """
    width: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None


@dataclass
class StructuralPlatformLipsConfig():
    """
    Defines the platform's lips with front, back,
    left, and right configurations.

    - `front` (bool) : Positive Z axis
    - `back` (bool) : Negative Z axis
    - `left` (bool) : Negative X axis
    - `right` (bool) : Positive X axis
    """
    front: bool = None
    back: bool = None
    left: bool = None
    right: bool = None


@dataclass
class StructuralPlatformConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural platform. The top of a platform should
    never exceed room_dimension_y - 1.25 if a target or performer are to be
    placed on top of the platform to ensure the performer can reach the target.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `attached_ramps` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): Number of ramps that should be attached to
    this platform to allow the performer to climb up to this platform.
    Default: 0
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "platforms"
    - `lips` ([StructuralPlatformLipsConfig]
    (#StructuralPlatformLipsConfig), or list of
    StructuralPlatformLipsConfig): The platform's lips. Default: None
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `platform_underneath` (bool or list of bools): If true, add a platform
    below this platform that touches the floor on the bottom and this platform
    on the top.  This platform will fully be encased in the x/z directions by
    the platform created underneath.  Default: False
    - `platform_underneath_attached_ramps` (int, or list of ints, or
    [MinMaxInt](#MinMaxInt) dict, or list of MinMaxInt dicts): Number of ramps
    that should be attached to the platform created below this platform to
    allow the performer to climb onto that platform. Default: 0
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Scale of the platform
    - `auto_adjust_platforms` (bool or list of bools): If true, makes sure all
    platform heights do not exceed 1.25 units below the y room dimension
    allowing the performer to always stand on top of a platform. For example,
    a room with a room_dimension_y = 4 and
    auto_adjusted_platforms = True will ensure that all platform heights
    do not exceed 2.75.  Default: False
    """
    lips: Union[StructuralPlatformLipsConfig,
                List[StructuralPlatformLipsConfig]] = None
    scale: Union[float, MinMaxFloat, List[Union[float, MinMaxFloat]],
                 VectorFloatConfig, List[VectorFloatConfig]] = None
    attached_ramps: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    platform_underneath: Union[bool, List[bool]] = None
    platform_underneath_attached_ramps: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None  # noqa
    auto_adjust_platforms: Union[bool, List[bool]] = False


@dataclass
class StructuralRampConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural ramp.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `angle` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Angle of the ramp upward from the floor
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "ramps"
    - `length` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Length of the ramp along the floor.  This
    is the 'adjacent' side and not the hypotenuse.
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `platform_underneath` (bool or list of bools): If true, add a platform
    below this ramp that touches the floor on the bottom and the bottom of
    this ramp on the top.  This ramp will fully be encased in the x/z
    directions by the platform created underneath.  Default: False
    - `platform_underneath_attached_ramps` (int, or list of ints, or
    [MinMaxInt](#MinMaxInt) dict, or list of MinMaxInt dicts): Number of ramps
    that should be attached to the platform created below this ramp to
    allow the performer to climb onto that platform.  Default: 0
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Width of the ramp
    """
    angle: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    width: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    length: Union[float, MinMaxFloat,
                  List[Union[float, MinMaxFloat]]] = None
    platform_underneath: Union[bool, List[bool]] = None
    platform_underneath_attached_ramps: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None  # noqa


@dataclass
class StructuralLOccluderConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural L-shaped occluder.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `backwards` (bool, or list of bools): Whether to create a backwards L.
    Default: [true, false]
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "l_occluders"
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `scale_front_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale in the x direction of the front
    part of the occluder
    - `scale_front_z` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale in the z direction of the front
    part of the occluder
    - `scale_side_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale in the x direction of the side
    part of the occluder
    - `scale_side_z` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale in the z direction of the side
    part of the occluder
    - `scale_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale in the y direction for the
    entire occluder
    """
    backwards: Union[bool, List[bool]] = None
    scale_front_x: Union[float, MinMaxFloat,
                         List[Union[float, MinMaxFloat]]] = None
    scale_front_z: Union[float, MinMaxFloat,
                         List[Union[float, MinMaxFloat]]] = None
    scale_side_x: Union[float, MinMaxFloat,
                        List[Union[float, MinMaxFloat]]] = None
    scale_side_z: Union[float, MinMaxFloat,
                        List[Union[float, MinMaxFloat]]] = None
    scale_y: Union[float, MinMaxFloat,
                   List[Union[float, MinMaxFloat]]] = None


@dataclass
class StructuralDropperConfig(BaseFeatureConfig):
    """
    Defines details of a structural dropper and its dropped projectile.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `drop_step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): The step of the simulation in which the
    projectile should be dropped.
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "droppers"
    - `position_relative` ([RelativePositionConfig](#RelativePositionConfig)
    dict, or list of RelativePositionConfig dicts): Configuration options for
    positioning this object relative to another object, rather than using
    `position_x` or `position_z`. If configuring this as a list, then all
    listed options will be applied to each scene in the listed order, with
    later options overriding earlier options if necessary. Default: not used
    - `position_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Position in the x direction of the of
    the ceiling where the dropper should be placed.
    - `position_z` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Position in the z direction of the of
    the ceiling where the dropper should be placed.
    - `projectile_labels` (string, or list of strings): A label for an existing
    object in your ILE configuration that will be used as this device's
    projectile, or new label(s) to associate with a new projectile object.
    Other configuration options may use this label to reference this object or
    a group of objects. Labels are not unique, and when multiple objects share
    labels, the ILE may choose one available object or all of them, depending
    on the specific option. The ILE will ignore any objects that have keyword
    locations or are used by other droppers/placers/throwers.
    - `projectile_material` (string, or list of strings): The projectiles's
    material or material type.
    - `projectile_scale` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Scale of
    the projectile.  Default is a value between 0.2 and 2.
    - `projectile_shape` (string, or list of strings): The shape or type of
    the projectile.
    """
    position_x: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    position_z: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    drop_step: Union[int, MinMaxInt,
                     List[Union[int, MinMaxInt]]] = None
    projectile_shape: Union[str, List[str]] = None
    projectile_material: Union[str, List[str]] = None
    projectile_scale: Union[float, MinMaxFloat,
                            List[Union[float, MinMaxFloat]],
                            VectorFloatConfig, List[VectorFloatConfig]] = None
    projectile_labels: Union[str, List[str]] = None
    position_relative: Union[
        RelativePositionConfig,
        List[RelativePositionConfig]
    ] = None


@dataclass
class StructuralThrowerConfig(BaseFeatureConfig):
    """
    Defines details of a structural dropper and its thrown projectile.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `height` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): The
    height on the wall that the thrower will be placed.
    - `impulse` (bool, or list of bools): Whether to use "impulse" force mode.
    We recommend using impulse force mode moving forward. Please note that the
    default `throw_force` is different for impulse and non-impulse force modes.
    Default: true
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "throwers"
    - `position_relative` ([RelativePositionConfig](#RelativePositionConfig)
    dict, or list of RelativePositionConfig dicts): Configuration options for
    positioning this object relative to another object, rather than using
    `position_wall`. If configuring this as a list, then all listed options
    will be applied to each scene in the listed order, with later options
    overriding earlier options if necessary. Default: not used
    - `position_wall` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): The
    position along the wall that the thrower will be placed.
    - `projectile_labels` (string, or list of strings): A label for an existing
    object in your ILE configuration that will be used as this device's
    projectile, or new label(s) to associate with a new projectile object.
    Other configuration options may use this label to reference this object or
    a group of objects. Labels are not unique, and when multiple objects share
    labels, the ILE may choose one available object or all of them, depending
    on the specific option. The ILE will ignore any objects that have keyword
    locations or are used by other droppers/placers/throwers.
    - `projectile_material` (string, or list of strings): The projectiles's
    material or material type.
    - `projectile_scale` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Scale of
    the projectile.  Default is a value between 0.2 and 2.
    - `projectile_shape` (string, or list of strings): The shape or type of
    the projectile.
    - `rotation_y` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): The angle
    in which the thrower will be rotated from its original position on the wall
    to point sideways (either left or right), with 0 being the center.
    This value should be between -45 and 45. Default: random value between
    -45 and 45.
    - `rotation_z` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): The angle
    in which the thrower will be rotated to point upwards.  This value should
    be between 0 and 15. Default: random value between 0 and 15.
    - `throw_force` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Force of
    the throw put on the projectile.  This value will be multiplied by the
    mass of the projectile.  Default: between 5 and 20 for impulse force mode,
    or between 500 and 2000 for non-impulse force mode
    - `throw_force_multiplier` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Force of
    the throw put on the projectile, that will be multiplied by the appropriate
    room dimension for the thrower's wall position (X for left/right, Z for
    front/back). If set, overrides the `throw_force`.
    - `throw_step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): The step of the simulation in which the
    projectile should be thrown.
    - `wall` (string, or list of strings): Which wall the thrower should be
    placed on.  Options are: left, right, front, back.
    """
    wall: Union[str, List[str]] = None
    position_wall: Union[float, MinMaxFloat,
                         List[Union[float, MinMaxFloat]]] = None
    height: Union[float, MinMaxFloat,
                  List[Union[float, MinMaxFloat]]] = None
    rotation_y: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    rotation_z: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    throw_step: Union[int, MinMaxInt,
                      List[Union[int, MinMaxInt]]] = None
    throw_force: Union[float, MinMaxFloat,
                       List[Union[float, MinMaxFloat]]] = None
    projectile_shape: Union[str, List[str]] = None
    projectile_material: Union[str, List[str]] = None
    projectile_scale: Union[float, MinMaxFloat,
                            List[Union[float, MinMaxFloat]],
                            VectorFloatConfig, List[VectorFloatConfig]] = None
    projectile_labels: Union[str, List[str]] = None
    position_relative: Union[
        RelativePositionConfig,
        List[RelativePositionConfig]
    ] = None
    impulse: Union[bool, List[bool]] = True
    throw_force_multiplier: Union[
        float, MinMaxFloat, List[Union[float, MinMaxFloat]]
    ] = None


@dataclass
class StructuralMovingOccluderConfig(BaseFeatureConfig):
    """
    Defines details of a structural moving occluder.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "moving_occluders"
    - `occluder_height` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Height (Y
    scale) of the occluder wall.  Default is between .25 and 2.5.
    - `occluder_thickness` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Thickness
    (Z scale) of the occluder wall.  Default is between .02 and 0.5.
    - `occluder_width` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Width (X
    scale) of the occluder wall.  Default is between .25 and 4.
    - `origin` (string, or list of strings): Location that the occluder's pole
    will originate from.  Options are `top`, `front`, `back`, `left`, `right`.
    Default is weighted such that `top` occurs 50% of the time and the sides
    are each 12.5%.  Users can weight options by included them more than once
    in an array.  For example, the default can be represented as:
    ```
    ['top', 'top', 'top', 'top', 'front', 'back', 'left', 'right']
    ```
    - `pole_material` (string, or list of strings): Material of the occluder
    pole (cylinder)
    - `position_x` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): X
    position of the center of the occluder
    - `position_z` (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Z
    position of the center of the occluder
    - `move_up_before_last_step` (bool, or list of bools): If true, repeat the
    occluder's full movement and rotation before the scene's last step. Ignored
    if `last_step` isn't configured, or if `repeat_movement` is true.
    Default: false
    - `repeat_interval` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): if `repeat_movement` is true, the number of
    steps to wait before repeating the full movement.  Default is between 1
    and 20.
    - `repeat_movement` (bool, or list of bools): If true, repeat the
    occluder's full movement and rotation indefinitely, using `repeat_interval`
    as the number of steps to wait. Default: false
    - `reverse_direction` (bool, or list of bools): Reverse the rotation
    direction of a sideways wall by rotating the wall 180 degrees. Only used if
    `origin` is set to a wall and not `top`. Default: [true, false]
    - `rotation_y` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
    or list of MinMaxInt dicts): Y rotation of a non-sideways occluder wall;
    only used if any `origin` is set to `top`.  Default is 0 to 359.
    - `wall_material` (string, or list of strings): Material of the occluder
    wall (cube)
    """

    wall_material: Union[str, List[str]] = None
    pole_material: Union[str, List[str]] = None
    position_x: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    position_z: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    origin: Union[str, List[str]] = None
    occluder_height: Union[float, MinMaxFloat,
                           List[Union[float, MinMaxFloat]]] = None
    occluder_width: Union[float, MinMaxFloat,
                          List[Union[float, MinMaxFloat]]] = None
    occluder_thickness: Union[float, MinMaxFloat,
                              List[Union[float, MinMaxFloat]]] = None
    repeat_movement: Union[bool, List[bool]] = None
    repeat_interval: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    reverse_direction: Union[bool, List[bool]] = None
    rotation_y: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    move_up_before_last_step: Union[bool, List[bool]] = None


@dataclass
class PartitionFloorConfig():
    leftHalf: Optional[float] = None
    rightHalf: Optional[float] = None


@dataclass
class FloorAreaConfig(BaseFeatureConfig):
    """Defines an area of the floor of the room.  Note: Coordinates must be
    integers. Areas are always size 1x1 centered on the given X/Z coordinate.
    Adjacent areas are combined.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of areas to be used with these parameters
    - `position_x` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): X position of the area.
    - `position_z` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): Z position of the area.
    """
    position_x: Union[int, MinMaxInt,
                      List[Union[int, MinMaxInt]]] = None
    position_z: Union[int, MinMaxInt,
                      List[Union[int, MinMaxInt]]] = None


@dataclass
class FloorMaterialConfig(FloorAreaConfig):
    """Defines details of a specific material on a specific location of the
    floor.  Be careful if num is greater than 1, be sure there are
    possibilities such that enough floor areas can be generated.
    Note: Coordinates must be integers. Areas are always size 1x1 centered on
    the given X/Z coordinate. Adjacent areas are combined.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of areas to be used with these parameters
    - `material` (string, or list of strings): The floor's material or
    material type.
    - `position_x` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): X position of the area.
    - `position_z` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
    list of MinMaxInt dicts): Z position of the area.
    """
    material: Union[str, List[str]] = None


@dataclass
class StructuralOccludingWallConfig(PositionableStructuralObjectsConfig):
    """
     - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of walls to be created with these parameters
    - `keyword_location`: ([KeywordLocationConfig](#KeywordLocationConfig)):
    Used to identify one of the qualitative locations specified by keywords.
    This field should not be set when `position` or `rotation` are also set.
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "occluding_walls"
    - `material` (string, or list of strings): The wall's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The wall's position in the scene.  Will be
    overrided by keyword location.
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The wall's rotation in the scene.
    Will be overrided by keyword location.
    - `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts): Scale of the wall.  Default is scaled to
    target size.  This will override the scale provided by the `type` field.
    - `type` (string, or list of strings): describes the type of occluding
    wall. Types include:
      `occludes` - occludes the target or object.
      `short` - wide enough, but not tall enough to occlude the target.
      `thin` - tall enough, but not wide enough to occlude the target.
      `hole` - wall with a hole that reveals the target.
    Default: ['occludes', 'occludes', 'occludes', 'short', 'thin', 'hole']
    """
    type: Union[str, List[str]] = None
    scale: Union[float, MinMaxFloat, List[Union[float, MinMaxFloat]],
                 VectorFloatConfig, List[VectorFloatConfig]] = None
    keyword_location: Union[KeywordLocationConfig,
                            List[KeywordLocationConfig]] = None


@dataclass
class StructuralPlacerConfig(BaseFeatureConfig):
    """Defines details for an instance of a placer (cylinder) descending from
    the ceiling on the given activation step to place an object with the given
    position. For some object shapes (specifically `container_symmetric_*` and
    `container_asymmetric_*`), two placers will be made and attached to the
    object.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of areas to be used with these parameters
    - `activation_step`: (int, or list of ints, or [MinMaxInt](#MinMaxInt)
    dict, or list of MinMaxInt dicts): Step on which the placer should begin
    its downward movement. Default: between 0 and 10
    - `deactivation_step`: (int, or list of ints, or [MinMaxInt](#MinMaxInt)
    dict, or list of MinMaxInt dicts): Step on which the placer should release
    its held object. This number must be a step after the end of the placer's
    downward movement. Default: At the end of the placer's downward movement
    - `end_height`: (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict): Height at which the placer should release its held object. Default:
    0 (so the held object is in contact with the floor)
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "placers"
    - `placed_object_labels` (string, or list of strings): A label for an
    existing object in your configuration that will be used as this device's
    placed object, or new label(s) to associate with a new placed object.
    Other configuration options may use this label to reference this object or
    a group of objects. Labels are not unique, and when multiple objects share
    labels, the ILE may choose one available object or all of them, depending
    on the specific option. The ILE will ignore any objects that have keyword
    locations or are used by other droppers/placers/throwers.
    - `placed_object_material` (string, or list of strings): The material
    (color/texture) to use on the placed object in each scene. For a list, a
    new material will be randomly chosen for each scene. Default: random
    - `placed_object_position`: ([VectorFloatConfig](#VectorFloatConfig) dict,
    or list of VectorFloatConfig dicts): The placed object's position in the
    scene
    - `placed_object_rotation`: (int, or list of ints, or
    [MinMaxInt](#MinMaxInt) dict, or list of MinMaxInt dicts): The placed
    object's rotation on the y axis.
    - `placed_object_scale`: (float, or list of floats, or
    [MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Placed
    object's scale.  Default is a value between 0.2 and 2.
    - `placed_object_shape` (string, or list of strings): The shape (object
    type) of the placed object. For a list, a new shape will be randomly
    chosen for each scene. Default: random
    - `position_relative` ([RelativePositionConfig](#RelativePositionConfig)
    dict, or list of RelativePositionConfig dicts): Configuration options for
    positioning this object relative to another object, rather than using
    `position_x` or `position_z`. If configuring this as a list, then all
    listed options will be applied to each scene in the listed order, with
    later options overriding earlier options if necessary. Default: not used
    """

    num: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = 0
    activation_step: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = None
    end_height: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    placed_object_position: Union[VectorFloatConfig,
                                  List[VectorFloatConfig]] = None
    placed_object_scale: Union[float, MinMaxFloat,
                               VectorFloatConfig,
                               List[Union[float, MinMaxFloat,
                                          VectorFloatConfig]]] = None
    placed_object_rotation: Union[int, MinMaxInt,
                                  List[Union[int, MinMaxInt]]] = None
    placed_object_shape: Union[str, List[str]] = None
    placed_object_material: Union[str, List[str]] = None
    placed_object_labels: Union[str, List[str]] = None
    deactivation_step: Union[
        int, MinMaxInt, List[Union[int, MinMaxInt]]
    ] = None
    position_relative: Union[
        RelativePositionConfig,
        List[RelativePositionConfig]
    ] = None


@dataclass
class StructuralDoorConfig(PositionableStructuralObjectsConfig):
    """
    Defines details of a structural door that can be opened and closed.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "doors"
    - `material` (string, or list of strings): The structure's material or
    material type.
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene.
    For doors, must be 0, 90, 180, or 270
    - `wall_material` (string, or list of strings): The material for the wall
    around the door.
    - `wall_scale_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale of the walls around the door in
    the x direction.  Default: A random value between 2 and the size of the
    room in the direction parallel with the door and wall.
    - `wall_scale_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): Scale of the walls around the door in
    the y direction.  The door will be 2 units high, so this scale must be
    greater than 2 for the top wall to appear.  Default: A random value between
    2 and the height of the room.
    """
    wall_material: Union[str, List[str]] = None
    wall_scale_x: Union[float, MinMaxFloat,
                        List[Union[float, MinMaxFloat]]] = None
    wall_scale_y: Union[float, MinMaxFloat,
                        List[Union[float, MinMaxFloat]]] = None


# TODO MCS-1206 Move into the interactable object component
@dataclass
class ToolConfig(BaseFeatureConfig):
    """
    Defines details of a tool object.

    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
    MinMaxInt dicts): Number of structures to be created with these parameters
    - `guide_rails` (bool, or list of bools): If True, guide rails will be
    generated to guide the tool in the direction it is oriented.  If a target
    exists, the guide rails will extend to the target.  Default: random
    - `labels` (string, or list of strings): A label or labels to be assigned
    to this object. Always automatically assigned "platforms"
    - `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
    VectorFloatConfig dicts): The structure's position in the scene
    - `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
    dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
    - `shape` (string, or list of strings): The shape (object type) of this
    object in each scene. For a list, a new shape will be randomly chosen for
    each scene. Must be a valid [tool shape](#Lists). If set, `length` and
    `width` are ignored.  Default: random
    - `length` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list
    of MinMaxInt dicts): The length of the tool.  Tools only have specific
    sizes and the values much match exactly.  Valid lengths are integers
    4 to 9. If shape is set, this value is ignored. Default: Use shape
    - `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
    or list of MinMaxFloat dicts):  The width of the tool.  Tools only have
    specific sizes and the values much match exactly.  Valid widths are
    0.5, 0.75, 1.0. If shape is set, this value is ignored. Default: Use shape
    """
    position: Union[VectorFloatConfig, List[VectorFloatConfig]] = None
    rotation_y: Union[float, MinMaxFloat,
                      List[Union[float, MinMaxFloat]]] = None
    shape: Union[str, List[str]] = None
    length: Union[int, MinMaxInt,
                  List[Union[float, MinMaxInt]]] = None
    width: Union[float, MinMaxFloat,
                 List[Union[float, MinMaxFloat]]] = None
    guide_rails: Union[bool, List[bool]] = False


DEFAULT_TEMPLATE_DROPPER = StructuralDropperConfig(
    num=0,
    drop_step=MinMaxInt(0, 10),
    projectile_shape=DROPPER_SHAPES,
    position_relative=None
)

DEFAULT_TEMPLATE_THROWER = StructuralThrowerConfig(
    num=0,
    wall=[
        WallSide.FRONT.value,
        WallSide.BACK.value,
        WallSide.LEFT.value,
        WallSide.RIGHT.value],
    impulse=True,
    throw_step=MinMaxInt(0, 10),
    throw_force=None,
    throw_force_multiplier=None,
    rotation_y=[0, MinMaxInt(-45, 45)],
    rotation_z=[0, MinMaxInt(0, 15)],
    projectile_shape=THROWER_SHAPES,
    position_relative=None
)
DEFAULT_THROW_FORCE_IMPULSE = MinMaxInt(5, 20)
DEFAULT_THROW_FORCE_NON_IMPULSE = MinMaxInt(500, 2000)

DEFAULT_TEMPLATE_PARTITION_FLOOR = PartitionFloorConfig(
    leftHalf=0,
    rightHalf=0
)

DEFAULT_TEMPLATE_MOVING_OCCLUDER = StructuralMovingOccluderConfig(
    num=0,
    origin=['top', 'top', 'top', 'top',
            'right', 'left', 'front', 'back'],
    reverse_direction=[True, False],
    occluder_height=MinMaxFloat(
        DEFAULT_MOVING_OCCLUDER_HEIGHT_MIN,
        DEFAULT_MOVING_OCCLUDER_HEIGHT_MAX),
    occluder_thickness=MinMaxFloat(
        DEFAULT_MOVING_OCCLUDER_THICKNESS_MIN,
        DEFAULT_MOVING_OCCLUDER_THICKNESS_MAX),
    occluder_width=MinMaxFloat(
        DEFAULT_MOVING_OCCLUDER_WIDTH_MIN,
        DEFAULT_MOVING_OCCLUDER_WIDTH_MAX),
    rotation_y=MinMaxFloat(
        DEFAULT_OCCLUDER_ROTATION_MIN, DEFAULT_OCCLUDER_ROTATION_MAX),
    move_up_before_last_step=False,
    repeat_movement=False,
    repeat_interval=MinMaxInt(DEFAULT_MOVING_OCCLUDER_REPEAT_MIN,
                              DEFAULT_MOVING_OCCLUDER_REPEAT_MAX))

DEFAULT_TEMPLATE_PLATFORM = StructuralPlatformConfig(
    num=0,
    lips=StructuralPlatformLipsConfig(False, False, False, False),
    rotation_y=[0, 90, 180, 270],
    position=VectorFloatConfig(None, None, None),
    scale=MinMaxFloat(PLATFORM_SCALE_MIN, PLATFORM_SCALE_MAX),
    attached_ramps=0, platform_underneath=False,
    platform_underneath_attached_ramps=0,
    auto_adjust_platforms=False)

DEFAULT_TEMPLATE_WALL = StructuralWallConfig(
    num=0, position=VectorFloatConfig(None, None, None),
    rotation_y=[0, 90, 180, 270])

DEFAULT_TEMPLATE_RAMP = StructuralRampConfig(
    num=0, position=VectorFloatConfig(None, None, None),
    rotation_y=[0, 90, 180, 270],
    angle=MinMaxFloat(RAMP_ANGLE_MIN, RAMP_ANGLE_MAX),
    platform_underneath=False, platform_underneath_attached_ramps=0)

DEFAULT_TEMPLATE_L_OCCLUDER = StructuralLOccluderConfig(
    num=0, position=VectorFloatConfig(None, None, None),
    rotation_y=[0, 90, 180, 270],
    scale_front_x=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX),
    scale_front_z=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX),
    scale_side_x=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX),
    scale_side_z=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX),
    scale_y=MinMaxFloat(L_OCCLUDER_SCALE_MIN, L_OCCLUDER_SCALE_MAX),
    backwards=[True, False])

DEFAULT_TEMPLATE_HOLES_LAVA = FloorAreaConfig(0)

DEFAULT_TEMPLATE_FLOOR_MATERIALS = FloorMaterialConfig(0)

DEFAULT_TEMPLATE_OCCLUDING_WALL = StructuralOccludingWallConfig(
    num=0,
    type=['occludes', 'occludes', 'occludes', 'short', 'thin', 'hole'],
    keyword_location=None,
    scale=None, rotation_y=MinMaxFloat(
        DEFAULT_OCCLUDER_ROTATION_MIN, DEFAULT_OCCLUDER_ROTATION_MAX),
    material=[mat[0] for mat in materials.WALL_MATERIALS],
    position=VectorFloatConfig(None, None, None))

DEFAULT_TEMPLATE_PLACER = StructuralPlacerConfig(
    0,
    placed_object_position=None,
    placed_object_rotation=MinMaxInt(0, 359),
    placed_object_scale=None,
    placed_object_shape=PLACER_SHAPES,
    activation_step=MinMaxInt(0, 10),
    deactivation_step=None,
    end_height=0,
    position_relative=None
)

DOOR_MATERIAL_RESTRICTIONS = [mat[0] for mat in (materials.METAL_MATERIALS +
                                                 materials.PLASTIC_MATERIALS +
                                                 materials.WOOD_MATERIALS)]

DEFAULT_TEMPLATE_DOOR = StructuralDoorConfig(
    num=0, position=VectorFloatConfig(None, None, None),
    rotation_y=[0, 90, 180, 270],
    material=DOOR_MATERIAL_RESTRICTIONS,
    wall_material=materials.WALL_MATERIALS,
    wall_scale_x=None, wall_scale_y=None)

DEFAULT_TEMPLATE_TOOL = ToolConfig(
    num=0, position=VectorFloatConfig(None, 0, None),
    rotation_y=MinMaxInt(0, 359),
    shape=ALL_LARGE_BLOCK_TOOLS.copy(), guide_rails=False
)


# This is structural only
def _post_instance(scene, new_obj, template, source_template, type):
    add_random_placement_tag(new_obj, source_template)
    plat_under = getattr(template, 'platform_underneath', None)
    new_objs = new_obj if isinstance(new_obj, list) else [new_obj]
    new_obj = new_objs[0]
    for obj in new_objs:
        extra_labels = (
            source_template.labels
            if source_template and source_template.labels
            else [])
        extra_labels = extra_labels if isinstance(
            extra_labels, list) else [extra_labels]
        obj['debug']['labels'] = (
            [type.lower()] + (extra_labels))
    if plat_under or getattr(
            template, 'attached_ramps', None):
        if(new_obj and new_obj["debug"]["labels"] is not None):
            new_obj["debug"]["labels"].append(LABEL_CONNECTED_TO_RAMP)
        else:
            new_obj["debug"]["labels"] = [LABEL_CONNECTED_TO_RAMP]
        # if we ever try to attach to l_occluders, this won't work
        new_objs = _add_platform_attached_objects(scene, template, new_obj)
    return new_objs


def _handle_position_material_defaults(
        scene: Scene,
        template: BaseFeatureConfig
) -> BaseFeatureConfig:
    """Convenience method for many of the structural objects"""
    room_dim = scene.room_dimensions or {}
    def_dim = geometry.DEFAULT_ROOM_DIMENSIONS
    room_width = room_dim.x or def_dim['x']
    room_length = room_dim.z or def_dim['z']

    template.position = (
        VectorFloatConfig(None, None, None)
        if template.position is None else template.position)
    template.position.x = (
        MinMaxFloat(-room_width / 2.0, room_width / 2.0).convert_value()
        if template.position.x is None else template.position.x
    )
    template.position.z = (
        MinMaxFloat(-room_length / 2.0, room_length / 2.0).convert_value()
        if template.position.z is None else template.position.z
    )
    template.rot = (geometry.random_rotation()
                    if template.rotation_y is None
                    else template.rotation_y)
    template.material = _reconcile_material(
        template.material, materials.ROOM_WALL_MATERIALS
    )

    plat_under = getattr(template, 'platform_underneath', None)
    if template.position.y == 0 and plat_under:
        # this assumes we never want to put these structures in holes
        raise ILEException("Cannot put platform underneath structural "
                           "object with y position less than 0")

    room_height = room_dim.y or def_dim['y']
    if template.position.y is None:
        if plat_under:
            # what should the default be?
            template.position.y = MinMaxFloat(
                TOP_PLATFORM_POSITION_MIN,
                room_height - geometry.PERFORMER_HEIGHT).convert_value()
        else:
            template.position.y = 0
    return template


def _is_valid_floor(
        scene: Scene, floor_pos, key, restrict_under_user,
        bounds, try_num, retries, type_str):
    room_dim = scene.room_dimensions
    x = floor_pos['x']
    z = floor_pos['z']
    perf_x = round(scene.performer_start.position.x)
    perf_z = round(scene.performer_start.position.z)
    xmax = math.floor(room_dim.x / 2)
    zmax = math.floor(room_dim.z / 2)
    valid = not (x < -xmax or x > xmax or z < -zmax or z > zmax)
    bb = geometry.generate_floor_area_bounds(
        floor_pos['x'],
        floor_pos['z']
    )
    # It is expected that some holes/lava will extend beyond the walls, so we
    # extend the room bounds.
    room_dim_extended = Vector3d(
        x=scene.room_dimensions.x + 1,
        y=scene.room_dimensions.y,
        z=scene.room_dimensions.z + 1)
    valid = valid and geometry.validate_location_rect(
        bb,
        vars(scene.performer_start.position),
        bounds,
        vars(room_dim_extended))
    valid = valid and floor_pos not in getattr(scene, key, '')
    restricted = restrict_under_user and x == perf_x and z == perf_z
    valid = valid and not restricted
    if valid:
        bounds.append(bb)
        return valid
    else:
        # Checks if enabled for TRACE logging.
        if logger.isEnabledFor(logging.TRACE):
            logger.trace(
                f'Failed validating location of {type_str} on'
                f' try {try_num + 1} of {retries}.'
                f'\nFAILED FLOOR POSITION = {floor_pos}'
            )
        else:
            logger.debug(
                f'Failed validating location of {type_str} on'
                f' try {try_num + 1} of {retries}.'
            )


def _add_floor_dependent_defaults(scene, reconciled):
    """Convenience method for floor features"""
    room_dim = scene.room_dimensions
    xmax = math.floor(room_dim.x / 2)
    zmax = math.floor(room_dim.z / 2)
    reconciled.position_x = (
        reconciled.position_x if reconciled.position_x is not None
        else random.randint(-xmax, xmax))
    reconciled.position_z = (
        reconciled.position_z if reconciled.position_z is not None
        else random.randint(-zmax, zmax)
    )


def _add_platform_attached_objects(
        scene,
        orig_template: Union[StructuralPlatformConfig,
                             StructuralRampConfig],
        obj: dict):
    # Ideally, we've position everything and then rotate everything around a
    # single axis.  Doing this is harder with some of the utlity functions
    # available and can limit retries since objects may be moved outside the
    # room late.  Therefore, we create and place each additional object and
    # then rotate it around the original objects position.  To create some
    # objects, we need information from objects from a pre-rotation state.
    # We simply return and store these states when needed.

    # bounds to test ramps to make sure they don't hit each other.  We'll
    # check all objects against all other objects when finished.
    local_bounds = []
    objs = [obj]
    new_platform = None
    top_pos = rotation_point = obj['shows'][0]['position']
    top_scale = obj['shows'][0]['scale']
    mat = obj['materials'][0]
    rotation_y = obj['shows'][0]['rotation']['y']
    below_pre_rot_pos = None

    if getattr(orig_template, 'platform_underneath', None):
        new_platform, below_pre_rot_pos = _add_platform_below(
            scene, obj, rotation_point, orig_template)
        objs += [new_platform]
        below_scale = new_platform['shows'][0]['scale']
    if getattr(orig_template, 'attached_ramps', None):
        # These values are just large to tell the system they have
        # essentially unlimited space for ramps when we don't know.
        # We can't determine exactly how much space when the base flooring
        # isn't rotated the same (I.E. the floor)
        available_lengths = DEFAULT_AVAIABLE_LENGTHS
        if below_pre_rot_pos:
            available_lengths = _get_space_around_platform(
                top_pos=top_pos,
                top_scale=top_scale,
                bottom_pos=below_pre_rot_pos,
                bottom_scale=below_scale)

        # Attach ramps
        gaps = []
        for i in range(orig_template.attached_ramps):
            logger.trace(
                f"Attempting to attach ramp {i}/"
                f"{orig_template.attached_ramps} to platform.")
            gap = _add_valid_ramp_with_retries(
                scene, objs, bounds=local_bounds,
                pre_rot_pos=top_pos,
                scale=top_scale,
                rotation_y=rotation_y,
                rotation_point=rotation_point,
                material=mat,
                max_angle=45,
                available_lengths=available_lengths)
            gaps.append(gap)
        _add_gaps_to_object(gaps, obj)

    if getattr(orig_template, 'platform_underneath_attached_ramps',
               None) and new_platform:
        gaps = []
        for i in range(orig_template.platform_underneath_attached_ramps):
            logger.trace(
                f"Attempting to attach ramp {i}/"
                f"{orig_template.platform_underneath_attached_ramps} to "
                f"underneath platform.")
            new_mat = new_platform['materials'][0]
            gap = _add_valid_ramp_with_retries(
                scene, objs, bounds=local_bounds,
                pre_rot_pos=below_pre_rot_pos,
                scale=below_scale,
                rotation_y=rotation_y,
                rotation_point=rotation_point,
                material=new_mat,
                max_angle=45,
                available_lengths=DEFAULT_AVAIABLE_LENGTHS)
            gaps.append(gap)
        _add_gaps_to_object(gaps, new_platform)
    return objs


def _add_gaps_to_object(gaps_list, obj):
    all_gaps = {}
    lips_gaps = {}
    lips_cfg = obj['lips']

    for gap in gaps_list:
        side = gap['side']
        _add_gaps_to_dict(all_gaps, side, gap)
        if not lips_cfg[side]:
            continue
        _add_gaps_to_dict(lips_gaps, side, gap)
    if all_gaps:
        obj['debug']['gaps'] = all_gaps
    if lips_gaps:
        obj['lips']['gaps'] = lips_gaps


def _add_gaps_to_dict(gaps_dict, side, gap_to_copy):
    gaps = gaps_dict.get(side, [])
    gap = copy.deepcopy(gap_to_copy)
    gap.pop('side')
    gaps.append(gap)
    gaps = sorted(gaps, key=lambda item: item['low'])
    gaps_dict[side] = gaps


def _add_platform_below(scene, obj, rotation_point, top_template):
    show = obj['shows'][0]
    scale = show['scale']
    pos = show['position']
    min_y = show['boundingBox'].min_y
    for _ in range(MAX_TRIES):
        # some assumptions:
        # rotation between platforms is fixed

        max_room_dim = max(
            scene.room_dimensions.x,
            scene.room_dimensions.z)
        x0, z0, scale_x, scale_z = _get_under_platform_position_scale(
            scale, pos, max_room_dim)

        # rotation around arbitrary center is:
        # x1 = (x0 -xc) cos(theta) - (z0 -zc)sin(theta) + xc
        # z1 = (x0 -xc) sin(theat) + (z0 -zc)cos(theta) + zc
        # rotate position around obj position
        r_point_x = rotation_point['x']
        r_point_z = rotation_point['z']
        radians = math.radians(obj['shows'][0]['rotation']['y'])
        x = (x0 - r_point_x) * math.cos(radians) - \
            (z0 - r_point_z) * math.sin(radians) + r_point_x
        z = -(x0 - r_point_x) * math.sin(radians) - \
            (z0 - r_point_z) * math.cos(radians) + r_point_z

        labels_to_use = list()
        labels_to_use.append(LABEL_CONNECTED_TO_RAMP)

        if(top_template.labels is not None):
            if(isinstance(top_template.labels, str)):
                labels_to_use.append(top_template.labels)
            else:
                labels_to_use.extend(top_template.labels)

        new_template = StructuralPlatformConfig(
            num=1,
            position=VectorFloatConfig(x, 0, z),
            rotation_y=show['rotation']['y'],
            scale=VectorFloatConfig(
                scale_x,
                min_y,
                scale_z),
            lips=top_template.lips,
            labels=labels_to_use)
        srv = StructuralPlatformCreationService()
        reconciled = srv.reconcile(scene, new_template)
        new_platform = srv.create_feature_from_specific_values(
            scene, reconciled, new_template)
        new_platform = (new_platform[0] if isinstance(new_platform, List)
                        else new_platform)
        new_platform['debug']['random_position'] = True
        return new_platform, {'x': x0, 'y': min_y * 0.5, 'z': z0}

    raise ILEException("Failed to add platform under existing platform.")


def _get_under_platform_position_scale(top_scale, top_position, max_room_dim):
    # How do we want to determine the position and scale of the platform below?
    # This has a range which is determined based on the top objects scale.
    # We then choose a random position where the top object entirely fits on
    # the bottom platform.

    # top_scale['y'] is the ramp length at 45 degrees (max angle)
    scale_min_buffer = max(
        top_scale['y'] +
        BOTTOM_PLATFORM_SCALE_BUFFER_MIN,
        top_scale['y'] * 2)
    scale_max_buffer = min(
        max_room_dim - geometry.PERFORMER_WIDTH -
        min(top_scale['x'], top_scale['z']),
        top_scale['y'] +
        BOTTOM_PLATFORM_SCALE_BUFFER_MAX)
    scale_x = MinMaxFloat(
        # Note: top_scale
        top_scale['x'] + scale_min_buffer,
        top_scale['x'] + scale_max_buffer
    ).convert_value()
    scale_z = MinMaxFloat(
        top_scale['z'] + scale_min_buffer,
        top_scale['z'] + scale_max_buffer
    ).convert_value()

    top_pos_x = _get_pre_rotate_under_position(
        top_scale, top_position, scale_x, 'x')
    top_pos_z = _get_pre_rotate_under_position(
        top_scale, top_position, scale_z, 'z')

    return top_pos_x, top_pos_z, scale_x, scale_z


def _get_pre_rotate_under_position(
        top_scale, top_position, bot_scale, key):
    """determine the range of positions in one dimension for a platform under
    another platform or ramp to ensure the top (original) object is
    entirely contained in the bottom in this one dimension.
    """
    pos_min = top_position[key] + top_scale[key] * 0.5 - bot_scale * 0.5
    pos_max = top_position[key] - top_scale[key] * 0.5 + bot_scale * 0.5
    return random.uniform(pos_min, pos_max)


def _add_valid_ramp_with_retries(
        scene, objs, bounds,
        pre_rot_pos, scale, rotation_y,
        rotation_point, material,
        max_angle, available_lengths):
    """ Returns gap location"""
    for i in range(MAX_TRIES):
        logger.trace(f"attempting to find ramp, try #{i}")
        ramp, gap = _get_attached_ramp(
            scene,
            pre_rot_pos=pre_rot_pos, scale=scale,
            rotation_y=rotation_y,
            rotation_point=rotation_point,
            material=material,
            available_lengths=available_lengths,
            max_angle=max_angle)
        if validate_all_locations_and_update_bounds(
                [ramp], scene, bounds):
            objs.append(ramp)
            return gap
    raise ILEException("Unable to find valid location to attach ramp to "
                       "platform.  This is usually due too many ramps for the"
                       "amount of space.")


def _get_attached_ramp(scene: Scene, pre_rot_pos: dict, scale: dict,
                       rotation_y, rotation_point, material, available_lengths,
                       max_angle=89,
                       ):
    ppx = pre_rot_pos['x']
    ppy = pre_rot_pos['y']
    ppz = pre_rot_pos['z']
    psx = scale['x']
    psy = scale['y']
    psz = scale['z']

    r_point_x = rotation_point['x']
    r_point_z = rotation_point['z']

    performer_buffer = geometry.PERFORMER_HALF_WIDTH * 2
    # then randomize which edge we choose first
    edge_choices = [0, 1, 2, 3]
    random.shuffle(edge_choices)

    # get how much room we have for a ramp in this edge if on top of
    # another platform
    # default to a high number.  Ignore the space check if platform is on
    # floor.

    valid_edge = False
    # verify there is enough space for a ramp
    for edge in edge_choices:
        max_ramp_length = min(
            available_lengths[edge] -
            performer_buffer,
            ATTACHED_RAMP_MAX_LENGTH)
        min_ramp_length = psy / math.tan(math.radians(max_angle))
        min_ramp_length = max(min_ramp_length, ATTACHED_RAMP_MIN_LENGTH)
        # what angle do we need to get to the necessary height given the max
        # length.
        angle_needed = math.degrees(math.atan(psy / (max_ramp_length)))
        # make sure ramp isn't wider than platform
        ramp_width_max = min(
            ATTACHED_RAMP_MAX_WIDTH,
            psz if edge %
            2 == 0 else psx)
        if (angle_needed <= max_angle and angle_needed >=
                0 and max_ramp_length > min_ramp_length and
                ramp_width_max >= ATTACHED_RAMP_MIN_WIDTH):
            scale = VectorFloatConfig(
                MinMaxFloat(ATTACHED_RAMP_MIN_WIDTH, ramp_width_max),
                psy,
                MinMaxFloat(min_ramp_length, max_ramp_length))
            scale = choose_random(scale)
            valid_edge = True
            break

    if not valid_edge:
        raise ILEException(
            f"Unable to add ramp to given platform with angle less than "
            f"{max_angle}")

    rsx = scale.x
    rsz = scale.z
    rot = rotation_y

    # need to rotate ramps when all is done so they go from the platform down.
    rot_add = RAMP_ROTATIONS[edge]

    rpy = ppy - 0.5 * psy

    length = rsz
    r_angle = math.degrees(math.atan(psy / rsz))

    # determing the position of the ramp is somewhat complicated.
    # The steps are:
    #  Determine position as if there is no rotation.
    #  Rotate the position around the center (position) of the platform

    # x limit when x of ramp is outside the platform relative to platform
    # origin
    x_limit_out = psx * 0.5 + 0.5 * rsz
    # x limit when x of ramp is inside the platform relative to platform origin
    x_limit_in = psx * 0.5 - 0.5 * rsx
    # same with z
    z_limit_out = psz * 0.5 + 0.5 * rsz
    z_limit_in = psz * 0.5 - 0.5 * rsx

    # position ranges as if platform has no rotation.  Each
    # index corresponds to one edge of the platform.
    non_rot_x_min = [-x_limit_out, -x_limit_in, x_limit_out, -x_limit_in]
    non_rot_x_max = [-x_limit_out, x_limit_in, x_limit_out, x_limit_in]
    non_rot_z_min = [-z_limit_in, -z_limit_out, -z_limit_in, z_limit_out]
    non_rot_z_max = [z_limit_in, -z_limit_out, z_limit_in, z_limit_out]

    # rotation around arbitrary center is:
    # x1 = (x0 -xc) cos(theta) - (z0 -zc)sin(theta) + xc
    # z1 = (x0 -xc) sin(theat) + (z0 -zc)cos(theta) + zc
    rel_x0 = random.uniform(non_rot_x_min[edge], non_rot_x_max[edge])
    rel_z0 = random.uniform(non_rot_z_min[edge], non_rot_z_max[edge])

    if edge % 2 == 0:
        # on left or right, we need to determine range in z
        # ramp width is always x so always use rsx
        gap = _get_lip_gap(rel_z0, rsx, ppz, psz, edge)
    else:
        # on front or back, we need to determine range in x
        gap = _get_lip_gap(rel_x0, rsx, ppx, psx, edge)

    x0 = rel_x0 + ppx
    z0 = rel_z0 + ppz

    radians = math.radians(rot)
    rpx = (x0 - r_point_x) * math.cos(radians) - \
        (z0 - r_point_z) * math.sin(radians) + r_point_x
    rpz = -(x0 - r_point_x) * math.sin(radians) - \
        (z0 - r_point_z) * math.cos(radians) + r_point_z

    pos = VectorFloatConfig(rpx, rpy, rpz)

    rot = (rot + rot_add) % 360
    new_template = StructuralRampConfig(
        num=1, labels=LABEL_BIDIRECTIONAL_RAMP,
        position=pos, rotation_y=rot, angle=r_angle,
        length=length, width=rsx, material=material)
    svc = StructuralRampCreationService()
    reconciled = svc.reconcile(scene, new_template)
    new_ramp = (svc.create_feature_from_specific_values(
        scene, reconciled, new_template))
    new_ramp = (new_ramp[0] if isinstance(new_ramp, List)
                else new_ramp)
    new_ramp['debug']['random_position'] = True
    return new_ramp, gap


def _get_lip_gap(ramp_pos, ramp_scale, plat_pos, plat_scale, edge):
    # ramp_pos is relative to the platform.  To get the actual position, we
    # would add plat_pos as we do in the function where this is called.
    # However that should get factored out so we don't need it.
    # edge 0 = -x left, 1=-z back, 2=+x right, 3=+z front
    gap = {'side': ['left', 'back', 'right', 'front'][edge]}
    gap['high'] = (ramp_pos + ramp_scale * 0.5 +
                   plat_scale * 0.5) / plat_scale
    gap['low'] = (ramp_pos - ramp_scale * 0.5 + plat_scale * 0.5) / plat_scale
    # I'm not sure why I need to reverse the direction here.
    if edge % 2 == 0:
        temp = 1 - gap['high']
        gap['high'] = 1 - gap['low']
        gap['low'] = temp
    return gap


def _get_space_around_platform(
        top_pos: dict, top_scale: dict, bottom_pos: dict, bottom_scale: dict):
    """All values must be pre-rotation and both objects must have the same
    rotation applied.
    """
    # delta pos
    dposx = bottom_pos['x'] - top_pos['x']
    dposz = bottom_pos['z'] - top_pos['z']
    # delta scale
    dscalex = bottom_scale['x'] - top_scale['x']
    dscalez = bottom_scale['z'] - top_scale['z']

    x_positive = dposx + dscalex / 2
    x_negative = -dposx + dscalex / 2

    z_positive = dposz + dscalez / 2
    z_negative = -dposz + dscalez / 2
    logger.debug(f" Area around platform for ramps: "
                 f"{[x_negative, z_negative, x_positive, z_positive]}")
    return [x_negative, z_negative, x_positive, z_positive]


def _get_occluding_wall_scale(
    template: StructuralOccludingWallConfig,
    target: InstanceDefinitionLocationTuple,
    room_height: float
) -> tuple(Vector3d, Vector3d):
    scale = template.scale
    if scale is None:
        scale = Vector3d()
    if isinstance(scale, (int, float)):
        scale = Vector3d(x=scale, y=scale, z=scale)

    dim = None
    if target:
        try:
            # Try and fall back to definition
            temp_dim = target.instance['debug']['dimensions']
            dim = Vector3d(x=temp_dim['x'], y=temp_dim['y'], z=temp_dim['z'])
        except Exception:
            dim = target.definition.dimensions

    if not scale.x:
        if template.type == OccludingWallType.THIN:
            scale.x = (min(dim.x, dim.z) * random.uniform(
                DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MIN,
                DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MAX
            )) if dim else DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MIN
        elif template.type == OccludingWallType.HOLE:
            scale.x = (
                max(dim.x, dim.z) + OCCLUDING_WALL_WIDTH_BUFFER
            ) if dim else choose_random(DEFAULT_OCCLUDING_WALL_WIDTH)
        else:
            scale.x = (
                max(dim.x, dim.z) * DEFAULT_OCCLUDING_WALL_WIDTH_MULTIPLIER
            ) if dim else choose_random(DEFAULT_OCCLUDING_WALL_WIDTH)

    if not scale.y:
        if template.type == OccludingWallType.SHORT:
            scale.y = (dim.y * random.uniform(
                DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MIN,
                DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MAX
            )) if dim else DEFAULT_OCCLUDING_WALL_SHORT_THIN_SCALE_MIN
            scale.y = max(scale.y, DEFAULT_OCCLUDING_WALL_SHORT_SCALE_Y_MIN)
        elif template.type == OccludingWallType.HOLE:
            scale.y = (
                dim.y + min(OCCLUDING_WALL_HOLE_MAX_HEIGHT, dim.y)
            ) if dim else choose_random(DEFAULT_OCCLUDING_WALL_HEIGHT)
        else:
            scale.y = (
                dim.y * DEFAULT_OCCLUDING_WALL_HEIGHT_MULTIPLIER
            ) if dim else choose_random(DEFAULT_OCCLUDING_WALL_HEIGHT)

    if not scale.z:
        scale.z = choose_random(DEFAULT_OCCLUDING_WALL_THICKNESS)

    # Restrict max height to room height.
    scale.y = min(scale.y, room_height)
    return (scale, dim)


def _get_occluding_wall_definition(
        template: StructuralOccludingWallConfig) -> ObjectDefinition:
    return ObjectDefinition(
        type='cube',
        attributes=['structure', 'kinematic'],
        color=template.material[1],
        scale=template.scale,
        dimensions=template.scale,
        materials=[template.material],
        materialCategory=[],
        salientMaterials=[],
        shape=['cube'],
        size='huge'
    )


def _get_room_min_max_dimensions(scene):
    room_dim = scene.room_dimensions or {}
    def_dim = geometry.DEFAULT_ROOM_DIMENSIONS
    room_width = room_dim.x or def_dim['x']
    room_length = room_dim.z or def_dim['z']

    min_room_dim = min(room_width, room_length)
    max_room_dim = max(room_width, room_length)
    return min_room_dim, max_room_dim


def _reconcile_material(material_choice, default_material_lists):
    material = material_choice
    if material:
        if isinstance(material, str):
            # This handles groups like CERAMIC_MATERIALS
            material = choose_material_tuple_from_material(material_choice)
    else:
        material = default_material_lists
        while(isinstance(material, list)):
            material = random.choice(material)

    if isinstance(material, materials.MaterialTuple):
        return material[0]
    else:
        return material


def _modify_for_hole(type, base, target_dimensions):
    show = base['shows'][0]
    if type == OccludingWallType.HOLE:
        # boost position by half of each section.  each section is half
        # the height
        show['position']['y'] = show['scale']['y'] / 4.0
        # copy instance and create new instances.
        l_col, r_col, top = _convert_base_occluding_wall_to_holed_wall(
            base, target_dimensions)
        walls = structures.finalize_structural_object(
            [l_col, r_col, top])
        return walls
    else:
        show['position']['y'] = show['scale']['y'] / 2.0
        obj = structures.finalize_structural_object([base])[0]
        return [obj]


def _convert_base_occluding_wall_to_holed_wall(
        base: dict, target_dim: Vector3d):
    l_col = copy.deepcopy(base)
    r_col = copy.deepcopy(base)
    top = copy.deepcopy(base)

    rot = base['shows'][0]['rotation']['y']
    l_pos = l_col['shows'][0]['position']
    l_scale = l_col['shows'][0]['scale']
    r_pos = r_col['shows'][0]['position']
    r_scale = r_col['shows'][0]['scale']
    t_pos = top['shows'][0]['position']
    t_scale = top['shows'][0]['scale']

    if t_scale['y'] / 2 > OCCLUDING_WALL_HOLE_MAX_HEIGHT:
        hole_height = OCCLUDING_WALL_HOLE_MAX_HEIGHT
    else:
        hole_height = t_scale['y'] / 2

    l_scale['x'] = OCCLUDING_WALL_WIDTH_BUFFER / 2.0
    r_scale['x'] = OCCLUDING_WALL_WIDTH_BUFFER / 2.0
    l_scale['y'] = hole_height
    r_scale['y'] = hole_height
    t_scale['y'] -= hole_height
    r_pos['y'] = hole_height / 2.0
    l_pos['y'] = hole_height / 2.0
    t_pos['y'] = hole_height + (t_scale['y'] / 2.0)
    sin = math.sin(math.radians(rot))
    cos = math.cos(math.radians(rot))
    shift = t_scale['x'] - l_scale['x']
    shift /= 2.0

    l_pos['x'] -= shift * cos
    l_pos['z'] += shift * sin
    r_pos['x'] += shift * cos
    r_pos['z'] -= shift * sin

    # scale x/3, y/2, z, shifted -x/3 (note rotation)
    # scale x/3, y/2, z, shifted -x/3 (note rotation)
    # scale x, y/2, z, shifted y
    l_col['id'] = f"l_col-{l_col['id']}"
    r_col['id'] = f"r_col-{r_col['id']}"
    top['id'] = f"top-{top['id']}"
    return l_col, r_col, top


def _get_existing_held_object_idl(
    labels: Union[str, List[str]]
) -> Optional[InstanceDefinitionLocationTuple]:
    object_repository = ObjectRepository.get_instance()
    shuffled_labels = (
        labels if isinstance(labels, list) else [labels]
    ) if labels else []
    random.shuffle(shuffled_labels)
    idl_count = 0
    for label in shuffled_labels:
        if not object_repository.has_label(label):
            continue
        idls = object_repository.get_all_from_labeled_objects(label).copy()
        idl_count += len(idls)
        random.shuffle(idls)
        for idl in idls:
            # Verify that this object has not already been given a final
            # position by another mechanism or keyword location.
            if idl.instance['debug'].get(DEBUG_FINAL_POSITION_KEY):
                continue
            return idl
    # If a target object does not exist or was already used by another
    # mechanism, do not generate a new one; just raise an error.
    if labels == TARGET_LABEL or labels == [TARGET_LABEL]:
        error_message = (
            f'all {idl_count} matching object(s) were already used with other '
            f'mechanisms or positioned with keyword locations'
        ) if idl_count else 'no matching object(s) were previously generated'
        raise ILEException(
            f'Failed to find an available object with the "{TARGET_LABEL}" '
            f'label for a dropper/placer/thrower because {error_message}.'
        )
    return None


def _get_projectile_idl(
    template: Union[StructuralDropperConfig, StructuralThrowerConfig],
    scene: Scene,
    bounds_list: List[ObjectBounds],
    shapes_to_scales: Dict[str, VectorFloatConfig]
) -> Tuple[InstanceDefinitionLocationTuple, bool]:
    labels = template.projectile_labels if template else None
    if labels:
        idl = _get_existing_held_object_idl(labels)
        if idl:
            return idl, True

    use_random = template is None or (template.projectile_shape is None and
                                      template.projectile_material is None and
                                      template.projectile_scale is None)
    if use_random:
        proj = InteractableObjectConfig(labels=labels)
    else:
        # Choose a shape now, so we can set the default scale accordingly.
        shape, material = choose_shape_material(
            template.projectile_shape,
            template.projectile_material
        )
        # Use shapes_to_scales to choose a default scale for the shape.
        # If the shape isn't in shapes_to_scales, then something is wrong,
        # so throw an error.
        scale = template.projectile_scale or shapes_to_scales[shape]
        proj = InteractableObjectConfig(
            labels=(
                [label for label in labels if label != TARGET_LABEL]
                if isinstance(labels, list) else labels
            ),
            material=(
                material[0] if isinstance(material, MaterialTuple) else
                material
            ),
            shape=shape,
            scale=scale
        )
    srv = InteractableObjectCreationService()
    proj_reconciled = srv.reconcile(scene, proj)
    srv.create_feature_from_specific_values(
        scene, proj_reconciled, proj)
    idl = srv.idl
    idl.instance['debug']['positionedBy'] = 'mechanism'
    idl.instance['debug'][DEBUG_FINAL_POSITION_KEY] = True
    return idl, False


def is_wall_too_close(new_wall: Dict[str, Any]) -> bool:
    """Return if the given wall object is too close to any existing parallel
    walls in the object repository."""
    new_wall_rotation = new_wall['shows'][0]['rotation']
    # Only run this check if the wall is perfectly horizontal or vertical.
    # TODO Should we check all existing walls that are parallel to this wall,
    #      regardless of starting rotation? We'd need to update the math.
    if new_wall_rotation['y'] % 90 != 0:
        return False
    new_wall_is_horizontal = (new_wall_rotation['y'] % 180 == 0)
    new_wall_position = new_wall['shows'][0]['position']
    new_wall_scale = new_wall['shows'][0]['scale']
    new_wall_thickness_halved = (new_wall_scale['z'] / 2.0)
    new_wall_width_halved = (new_wall_scale['x'] / 2.0)
    object_repository = ObjectRepository.get_instance()
    walls = object_repository.get_all_from_labeled_objects('walls') or []
    for old_wall in walls:
        old_wall_position = old_wall.instance['shows'][0]['position']
        old_wall_rotation = old_wall.instance['shows'][0]['rotation']
        # Only check this wall if it's perfectly horizontal or vertical.
        if old_wall_rotation['y'] % 90 != 0:
            continue
        old_wall_is_horizontal = (old_wall_rotation['y'] % 180 == 0)
        if old_wall_is_horizontal == new_wall_is_horizontal:
            major_axis = 'z' if old_wall_is_horizontal else 'x'
            minor_axis = 'x' if old_wall_is_horizontal else 'z'
            old_wall_scale = old_wall.instance['shows'][0]['scale']
            old_wall_thickness_halved = (old_wall_scale['z'] / 2.0)
            old_wall_width_halved = (old_wall_scale['x'] / 2.0)
            distance_adjacent = (abs(
                new_wall_position[minor_axis] - old_wall_position[minor_axis]
            ) - old_wall_width_halved - new_wall_width_halved)
            if distance_adjacent > 0:
                continue
            distance_across = (abs(
                new_wall_position[major_axis] - old_wall_position[major_axis]
            ) - old_wall_thickness_halved - new_wall_thickness_halved)
            if distance_across < geometry.PERFORMER_WIDTH:
                return True
    return False


for feature_type, creation_service in [
    (FeatureTypes.DOORS, StructuralDoorsCreationService),
    (FeatureTypes.DROPPERS, StructuralDropperCreationService),
    (FeatureTypes.FLOOR_MATERIALS, StructuralFloorMaterialsCreationService),
    (FeatureTypes.HOLES, StructuralHolesCreationService),
    (FeatureTypes.L_OCCLUDERS, StructuralLOccluderCreationService),
    (FeatureTypes.LAVA, StructuralLavaCreationService),
    (FeatureTypes.PARTITION_FLOOR, StructuralPartitionFloorCreationService),
    (FeatureTypes.MOVING_OCCLUDERS, StructuralMovingOccluderCreationService),
    (FeatureTypes.OCCLUDING_WALLS, StructuralOccludingWallsCreationService),
    (FeatureTypes.PLACERS, StructuralPlacersCreationService),
    (FeatureTypes.PLATFORMS, StructuralPlatformCreationService),
    (FeatureTypes.RAMPS, StructuralRampCreationService),
    (FeatureTypes.THROWERS, StructuralThrowerCreationService),
    (FeatureTypes.WALLS, StructuralWallCreationService),
    (FeatureTypes.TOOLS, StructuralToolsCreationService)
]:
    FeatureCreationService.register_creation_service(
        feature_type, creation_service)
