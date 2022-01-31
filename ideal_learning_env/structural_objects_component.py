import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from generator import MAX_TRIES, materials
from ideal_learning_env.structural_object_generator import (
    ALL_THROWABLE_SHAPES,
    DOOR_MATERIAL_RESTRICTIONS,
    PLATFORM_SCALE_MIN,
    BaseStructuralObjectsConfig,
    FloorAreaConfig,
    FloorMaterialConfig,
    OccludingWallType,
    StructuralDoorConfig,
    StructuralDropperConfig,
    StructuralLOccluderConfig,
    StructuralMovingOccluderConfig,
    StructuralOccludingWallConfig,
    StructuralPlacerConfig,
    StructuralPlatformConfig,
    StructuralRampConfig,
    StructuralThrowerConfig,
    StructuralTypes,
    StructuralWallConfig,
    WallSide,
    add_structural_object_with_retries_or_throw,
)

from .choosers import choose_random
from .components import ILEComponent
from .decorators import ile_config_setter
from .defs import ILEDelayException, find_bounds
from .interactable_object_config import KeywordLocationConfig
from .numerics import MinMaxInt
from .object_services import TARGET_LABEL, ObjectRepository
from .validators import ValidateNumber, ValidateOptions

logger = logging.getLogger(__name__)


@dataclass
class RandomStructuralObjectConfig():
    """A dict that configures the number of structural objects that will be
    added to each scene. Each dict can have the following optional properties:
    - `type` (string, or list of strings): A type or a list of types that are
    options for this group.  The options include the following:
        - `doors`: A random door.
        - `droppers`: A random dropper that drops a random object between step
            0 and step 10.
        - `floor_materials`: A random floor area's texture is changed to a
            different texture.
        - `holes`: A hole in the room's floor in a random location.  A hole is
            just where the floor has dropped to where the performer agent
            cannot get back up if it falls down.  Random holes will not appear
            below the performer agent's start position.  Note: Holes can end
            up appearing below objects which can cause the objects to fall
            into the hole.
        - `l_occluders`: A random L-shaped occluder.
        - `lava`: A random floor area's texture is changed to lava.
        - `moving_occluders`: A random occluder on a pole that moves up and
            rotates to reveal anything behind it and then back down.  It may
            repeat the movement indefinitely or stop after the first iteration.
        - `occluding_walls`: A random occluding wall.
        - `placers`: A random placer putting down a random object.
        - `platforms`: A random platform.
        - `ramps`: A random ramp.
        - `throwers`: A random thrower that throws a random object between step
            0 and step 10.  Throw force is 500 to 1000 times the mass of the
            thrown object.
        - `walls`: A random interior room wall.
    Default: All types
    - `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt)): The number of
    structural objects that should be generated in this group.  Each object is
    one of the type choices.
    - `keyword_location`: ([KeywordLocationConfig](#KeywordLocationConfig)):
    Used to identify one of the qualitative locations specified by keywords.
    This field should not be set when `position` or `rotation` are also set.
    Currently only used by `occluding_walls`.
    - `labels` (string, or list of strings): One or more labels that are
    automatically assigned to the random object.
    - `relative_object_label` (string, or list of strings): One or more labels
    that are automatically used by random droppers, placers, and throwers as
    the placed/projectile object labels. Currently ignored by all other
    structural object types.
    """

    type: Union[str, List[str]] = None
    num: Union[int, MinMaxInt, List[Union[int, MinMaxInt]]] = 0
    keyword_location: Union[KeywordLocationConfig,
                            List[KeywordLocationConfig]] = None
    labels: Union[str, List[str]] = None
    relative_object_label: Union[str, List[str]] = None


class SpecificStructuralObjectsComponent(ILEComponent):
    """Adds specific structural objects to an ILE scene.  Users can specify
    more exact values, ranges, or leave blank each type of structural object.
    When a choice is specified, each generated scene will have a different
    value generated within that choice.

    This component requires performerStart.location to be set in the scene
    prior. This is typically handles by the GlobalSettingsComponent"""

    structural_walls: Union[
        StructuralWallConfig,
        List[StructuralWallConfig]] = None
    """
    ([StructuralWallConfig](#StructuralWallConfig) dict, or list of
    [StructuralWallConfig](#StructuralWallConfig) dicts): Template(s)
    containing properties needed to create an interior wall.  Default: None

    Simple Example:
    ```
    structural_walls:
      num: 0
    ```

    Advanced Example:
    ```
    structural_walls:
        num:
          min: 1
          max: 3
        position:
          x: 1
          y: 0
          z: 2
        rotation_y: 30
        material: 'PLASTIC_MATERIALS'
        width: .5
        height: .3
    ```
    """

    structural_platforms: Union[
        StructuralPlatformConfig,
        List[StructuralPlatformConfig]] = None
    """
    ([StructuralPlatformConfig](#StructuralPlatformConfig) dict, or list of
    [StructuralPlatformConfig](#StructuralPlatformConfig) dicts): Template(s)
    containing properties needed to create a platform.  Default: None

    Simple Example:
    ```
    structural_platforms:
      num: 0
    ```

    Advanced Example:
    ```
    structural_platforms:
        num: [1, 2, 4]
        position:
          x: 1
          y: 0
          z: 2
        rotation_y: 30
        material: 'PLASTIC_MATERIALS'
        scale:
          x: 1.1
          y: [0.5, 1]
          z:
            min: 0.3
            max: 1.3
    ```
    """

    structural_l_occluders: Union[
        StructuralLOccluderConfig,
        List[StructuralLOccluderConfig]] = None
    """
    ([StructuralOccluderConfig](#StructuralOccluderConfig) dict, or list of
    [StructuralOccluderConfig](#StructuralOccluderConfig) dicts): Template(s)
    containing properties needed to create an L-shaped occluder.  Default: None

    Simple Example
    ```
    structural_l_occluders:
      num: 0
    ```

    Advanced Example:
    ```
    structural_l_occluders:
        num: 2
        position:
          x: 1
          y: 0
          z: 2
        rotation_y: 30
        material: 'AI2-THOR/Materials/Metals/Brass 1'
        scale_front_x: 0.3
        scale_front_z: [0.4, 0.5, 0.6]
        scale_side_x:
          min: 0.1
          max: 2.1
        scale_side_z: 0.6
        scale_y: 0.7
    ```
    """

    structural_ramps: Union[
        StructuralRampConfig,
        List[StructuralRampConfig]] = None
    """
    ([StructuralRampConfig](#StructuralRampConfig) dict, or list of
    [StructuralRampConfig](#StructuralRampConfig) dicts): Template(s)
    containing properties needed to create a ramp.  Default: None

    Simple Example:
    ```
    structural_ramps:
      num: 0
    ```

    Advanced Example:
    ```
    structural_ramps:
        num:
          min: 0
          max: 3
        position:
          x: 1
          y: 0
          z: 2
        rotation_y: 30
        material: 'AI2-THOR/Materials/Metals/Brass 1'
        angle: 30
        width: 0.4
        length: 0.5
    ```
    """

    structural_droppers: Union[
        StructuralDropperConfig,
        List[StructuralDropperConfig]] = None
    """
    ([StructuralDropperConfig](#StructuralDropperConfig) dict, or list of
    [StructuralDropperConfig](#StructuralDropperConfig) dicts): Template(s)
    containing properties needed to create a droppers.  Default: None

    Simple Example:
    ```
    structural_droppers:
      num: 0
    ```

    Advanced Example:
    ```
    structural_droppers:
      num:
        min: 0
        max: 3
      position_x:
        min: -1
        max: 1
      position_z:
        - 1
        - 2
        - 5
      drop_step: 2
      projectile_material: 'AI2-THOR/Materials/Metals/Brass 1'
      projectile_shape: soccer_ball
      projectile_scale: 0.85
    ```
    """

    structural_throwers: Union[
        StructuralThrowerConfig,
        List[StructuralThrowerConfig]] = None
    """
    ([StructuralThrowerConfig](#StructuralThrowerConfig) dict, or list of
    [StructuralThrowerConfig](#StructuralThrowerConfig) dicts): Template(s)
    containing properties needed to create a droppers.  Default: None

    Simple Example:
    ```
    structural_throwers:
      num: 0
    ```

    Advanced Example:
    ```
    structural_throwers:
      num:
        min: 0
        max: 3
      wall: [front, left]
      position_wall:
        min: -1
        max: 3
      height:
        - 1
        - 2
        - 1.5
      rotation:
        min: 3
        max: 7
      throw_force: [600, 1000, 1200]
      throw_step: 2
      projectile_material: 'AI2-THOR/Materials/Metals/Brass 1'
      projectile_shape: soccer_ball
      projectile_scale: 0.85
    ```
    """

    structural_moving_occluders: Union[
        StructuralMovingOccluderConfig,
        List[StructuralMovingOccluderConfig]] = None
    """
    ([StructuralMovingOccluderConfig](#StructuralMovingOccluderConfig) dict,
    or list of
    [StructuralMovingOccluderConfig](#StructuralMovingOccluderConfig) dicts):
    Template(s) containing properties needed to create a structural moving
    occluders.  Default: None

    Simple Example:
    ```
    structural_moving_occluders:
      num: 0
    ```

    Advanced Example:
    ```
    structural_moving_occluders:
      num:
        min: 0
        max: 3
      wall_material: 'AI2-THOR/Materials/Metals/Brass 1'
      pole_material: 'AI2-THOR/Materials/Metals/Brass 1'
      position_x:
        - 1
        - 2
        - 1.5
      position_z:
        min: -3
        max: 2.5
      origin: top
      occluder_height: 0.9
      occluder_width: 1.1
      occluder_thickness: 0.07
      repeat_movement: true
      repeat_interval: 5
      rotation_y: 90
    ```
    """

    holes: Union[FloorAreaConfig, List[FloorAreaConfig]] = 0
    """
    ([FloorAreaConfig](#FloorAreaConfig), or list of
    [FloorAreaConfig](#FloorAreaConfig) dict) --
    Groups of hole configurations and how many should be generated from the
    given options.  Note: Holes can end up appearing below objects which can
    cause the objects to fall into the hole.
    Default: 0


    Simple Example:
    ```
    holes:
        - num: 0
    ```

    Advanced Example:
    ```
    holes:
        - num:
            min: 0
            max: 2
        - num: 1
          position_x: 2
          position_z: 2
        - num: [1, 3]
          position_x: [4, 5]
          position_z:
            min: -5
            max: -4
    ```
    """
    floor_material_override: Union[FloorMaterialConfig,
                                   List[FloorMaterialConfig]] = 0
    """
    ([FloorMaterialConfig](#FloorMaterialConfig), or list of
    [FloorMaterialConfig](#FloorMaterialConfig) dict) --
    Groups of floor material configurations and how many should be generated
    from the given options.
    Default: 0


    Simple Example:
    ```
    floor_material_override:
        - num: 0
    ```

    Advanced Example:
    ```
    floor_material_override:
        - num:
            min: 0
            max: 2
        - num: 1
          position_x: 2
          position_z: 2
          material: PLASTIC_MATERIALS
        - num: [1, 3]
          position_x: [4, 5]
          position_z:
            min: -5
            max: -4
          material: AI2-THOR/Materials/Metals/BrushedAluminum_Blue

    ```
    """

    lava: Union[FloorAreaConfig, List[FloorAreaConfig]] = None
    """
    ([FloorAreaConfig](#FloorAreaConfig), or list of
    [FloorAreaConfig](#FloorAreaConfig) dict) --
    Groups of lava configurations. Shortcut for the "floor_material_override"
    option with the lava material.
    Default: 0


    Simple Example:
    ```
    lava:
        - num: 0
    ```

    Advanced Example:
    ```
    lava:
        - num:
            min: 0
            max: 2
        - num: 1
          position_x: 1
          position_z: 1
        - num: [1, 3]
          position_x: [-5, -4]
          position_z:
            min: -5
            max: -4
    ```
    """

    doors: Union[StructuralDoorConfig,
                 List[StructuralDoorConfig]] = 0
    """
    ([StructuralDoorConfig](#FloorStructuralDoorConfigMaterialConfig), or list
    of [StructuralDoorConfig](#StructuralDoorConfig) dict) --
    Groups of door configurations and how many should be generated from the
    given options.  Note: Doors do not contain any frame or wall support.
    Default: 0


    Simple Example:
    ```
    doors:
        - num: 0
    ```

    Advanced Example:
    ```
    doors:
        - num:
            min: 1
            max: 3
        - num: 1
          position:
            x: [1,2]
            y: 0
            z:
              min: -3
              max: 3
          scale: [1, 0.5]
          material: PLASTIC_MATERIALS
        - num: [1, 3]
          position:
            x: [4, 5]
            y: 0
            z:
              min: -5
              max: -4
          scale:
            x: 1
            y:
              min: .5
              max: 2
            z: [.75, 1.25]
          material: AI2-THOR/Materials/Metals/BrushedAluminum_Blue


    ```
    """

    placers: Union[StructuralPlacerConfig, List[StructuralPlacerConfig]] = 0
    """
    ([StructuralPlacerConfig](#StructuralPlacerConfig), or list of
    [StructuralPlacerConfig](#StructuralPlacerConfig) dict) --
    Groups of Placer configurations and how many should be generated
    from the given options.
    Default: 0


    Simple Example:
    ```
    placers:
        - num: 0
    ```

    Advanced Example:
    ```
    placers:
        - num:
            min: 0
            max: 2
        - num: 1
          placed_object_position:
            x: 2
            y: [3, 4]
            z:
              min: -2
              max: 0
          placed_object_scale: 1.2
          placed_object_rotation: 45
          material: PLASTIC_MATERIALS
          shape: case_1
          activation_step:
            min: 3
            max: 8
          labels: [placed_object, placed_case]
        - num: [5, 10]
          shape: ball
          material: AI2-THOR/Materials/Metals/BrushedAluminum_Blue

    ```
    """

    structural_occluding_walls: Union[StructuralOccludingWallConfig,
                                      List[StructuralOccludingWallConfig]] = 0
    """
    ([StructuralOccludingWallConfig](#StructuralOccludingWallConfig) dict,
    or list of
    [StructuralOccludingWallConfig](#StructuralOccludingWallConfig) dicts):
    Template(s) containing properties needed to create a occluding walls.
    Requires a goal and target.  Default: None

    Simple Example:
    ```
    structural_occluding_walls:
      num: 0
    ```

    Advanced Example:
    ```
    structural_occluding_walls:
      - num:
          min: 0
          max: 3
        material: 'AI2-THOR/Materials/Walls/DrywallGreen'
        keyword_location:
          keyword: between
          relative_object_label: target
      - num: 2
        material: 'WALL_MATERIALS'
        position:
          x: [1, -5]
          y: 2
          z: 1.5
        rotation_y:
          min: 30
          max: 60
        scale:
          x: 3
          y: 4
    ```
    """

    def get_structural_walls(self) -> int:
        return self._get_val(self.structural_walls, StructuralWallConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_structural_walls(self, data: Any) -> None:
        self.structural_walls = data

    def get_structural_platforms(self) -> int:
        return self._get_val(self.structural_platforms,
                             StructuralPlatformConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    @ile_config_setter(validator=ValidateNumber(
        props=['scale', 'scale.x', 'scale.y', 'scale.z'],
        min_value=PLATFORM_SCALE_MIN,
        null_ok=True
    ))
    def set_structural_platforms(self, data: Any) -> None:
        self.structural_platforms = data

    def get_structural_l_occluders(self) -> int:
        return self._get_val(self.structural_l_occluders,
                             StructuralLOccluderConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_structural_l_occluders(self, data: Any) -> None:
        self.structural_l_occluders = data

    def get_structural_ramps(self) -> int:
        return self._get_val(self.structural_ramps, StructuralRampConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    def set_structural_ramps(self, data: Any) -> None:
        self.structural_ramps = data

    def get_structural_droppers(self) -> int:
        return self._get_val(self.structural_droppers, StructuralDropperConfig)

    @ile_config_setter(validator=ValidateNumber(
        props=['drop_step', 'projectile_scale'],
        min_value=0, null_ok=True))
    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['projectile_material'],
        options=(materials.ALL_CONFIGURABLE_MATERIAL_LISTS_AND_STRINGS)
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['projectile_shape'],
        options=ALL_THROWABLE_SHAPES
    ))
    def set_structural_droppers(self, data: Any) -> None:
        self.structural_droppers = data

    def get_structural_throwers(self) -> int:
        return self._get_val(self.structural_throwers,
                             StructuralThrowerConfig)

    @ile_config_setter(validator=ValidateNumber(
        props=['throw_step', 'throw_force', 'height', 'projectile_scale'],
        min_value=0, null_ok=True))
    @ile_config_setter(validator=ValidateNumber(
        props=['rotation'], min_value=0, max_value=15, null_ok=True))
    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['projectile_material'],
        options=(materials.ALL_CONFIGURABLE_MATERIAL_LISTS_AND_STRINGS)
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['projectile_shape'],
        options=ALL_THROWABLE_SHAPES
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['wall'],
        options=(
            WallSide.LEFT, WallSide.RIGHT, WallSide.FRONT, WallSide.BACK
        )
    ))
    def set_structural_throwers(self, data: Any) -> None:
        self.structural_throwers = data

    def get_structural_moving_occluders(self) -> int:
        return self._get_val(self.structural_moving_occluders,
                             StructuralMovingOccluderConfig)

    @ile_config_setter(validator=ValidateNumber(
        props=['occluder_width', 'occluder_height', 'occluder_thickness'],
        min_value=0, null_ok=True))
    @ile_config_setter(validator=ValidateNumber(
        props=['position_x', 'position_z', 'rotation_y'],
        null_ok=True))
    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['wall_material', 'pole_material'],
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['origin'],
        options=(
            'top', 'front', 'back', 'left', 'right'
        )
    ))
    def set_structural_moving_occluders(self, data: Any) -> None:
        self.structural_moving_occluders = data

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateNumber(
        props=['position_x', 'position_z'],
        null_ok=True
    ))
    def set_holes(self, data: Any) -> None:
        self.holes = data

    def get_holes(self) -> int:
        return self._get_val(self.holes, FloorAreaConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateNumber(
        props=['position_x', 'position_z'],
        null_ok=True
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(
            materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS +
            [item.material for item in materials.LAVA_MATERIALS] +
            ['LAVA_MATERIALS']
        )
    ))
    def set_floor_material_override(self, data: Any) -> None:
        self.floor_material_override = data

    def get_floor_material_override(self) -> int:
        return self._get_val(self.floor_material_override, FloorMaterialConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateNumber(
        props=['position_x', 'position_z'],
        null_ok=True
    ))
    def set_lava(self, data: Any) -> None:
        self.lava = data

    def get_lava(self) -> FloorAreaConfig:
        return self._get_val(self.lava, FloorAreaConfig)

    def _get_lava_as_floor_materials(self) -> List[FloorMaterialConfig]:
        if not self.lava:
            return None
        areas = (self.lava if isinstance(self.lava, list) else [self.lava])
        return [FloorMaterialConfig(
            num=area.num,
            position_x=area.position_x,
            position_z=area.position_z,
            material=materials.LAVA_MATERIALS[0].material
        ) for area in areas]

    def get_structural_occluding_walls(self) -> int:
        return self._get_val(
            self.structural_occluding_walls, StructuralOccludingWallConfig)

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(materials.ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS)
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['type'],
        options=(
            OccludingWallType.OCCLUDES, OccludingWallType.SHORT,
            OccludingWallType.THIN, OccludingWallType.HOLE
        )
    ))
    def set_structural_occluding_walls(self, data: Any) -> None:
        self.structural_occluding_walls = data

    @ile_config_setter(validator=ValidateNumber(props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateNumber(
        props=['activation_step'], min_value=0,
        null_ok=True
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['placed_object_material'],
        options=(materials.ALL_CONFIGURABLE_MATERIAL_LISTS_AND_STRINGS)
    ))
    @ile_config_setter(validator=ValidateOptions(
        props=['placed_object_shape'],
        options=ALL_THROWABLE_SHAPES
    ))
    def set_placers(self, data: Any) -> None:
        self.placers = data

    def get_placers(self) -> int:
        return self._get_val(self.placers, StructuralPlacerConfig)

    @ile_config_setter(validator=ValidateNumber(
        props=['num'], min_value=0))
    @ile_config_setter(validator=ValidateOptions(
        props=['material'],
        options=(DOOR_MATERIAL_RESTRICTIONS +
                 ["METAL_MATERIALS", "PLASTIC_MATERIALS", "WOOD_MATERIALS"]
                 )
    ))
    def set_doors(self, data: Any) -> None:
        self.doors = data

    def get_doors(self) -> int:
        return self._get_val(self.doors, StructuralDoorConfig)

    def _get_val(self, data, type):
        if data is None:
            return None
        return choose_random(
            [] if data is None else data, type
        )

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring specific structural objects...')
        self._delayed_templates = []

        scene['objects'] = scene.get('objects', [])
        scene['holes'] = scene.get('holes', [])
        scene['floorTextures'] = scene.get('floorTextures', [])
        bounds = find_bounds(scene)

        mat_to_loc = {}

        structural_type_templates = [
            (StructuralTypes.WALLS, self.structural_walls),
            (StructuralTypes.PLATFORMS, self.structural_platforms),
            (StructuralTypes.L_OCCLUDERS, self.structural_l_occluders),
            (StructuralTypes.RAMPS, self.structural_ramps),
            (StructuralTypes.DROPPERS, self.structural_droppers),
            (StructuralTypes.THROWERS, self.structural_throwers),
            (StructuralTypes.MOVING_OCCLUDERS,
             self.structural_moving_occluders),
            (StructuralTypes.HOLES, self.holes),
            (StructuralTypes.FLOOR_MATERIALS, self.floor_material_override),
            # Ensure that the lava is returned as a FloorMaterialConfig here.
            (StructuralTypes.LAVA, self._get_lava_as_floor_materials()),
            (StructuralTypes.OCCLUDING_WALLS, self.structural_occluding_walls),
            (StructuralTypes.PLACERS, self.placers),
            (StructuralTypes.DOORS, self.doors)
        ]

        existing_holes = []
        existing_floor_materials = []

        for s_type, templates in structural_type_templates:
            if not isinstance(templates, List):
                templates = [templates]
            for template in templates:
                num_template = choose_random(template)
                if num_template:
                    for i in range(num_template.num):
                        try:
                            add_structural_object_with_retries_or_throw(
                                scene, bounds, MAX_TRIES, template,
                                s_type, i, existing_holes, mat_to_loc,
                                existing_floor_materials)
                        except ILEDelayException as e:
                            logger.trace(
                                f"Failed to generate {s_type}"
                                f" due to needing delay.",
                                exc_info=e)
                            self._delayed_templates.append((s_type, template))

        for mat, value in mat_to_loc.items():
            scene['floorTextures'].append(
                {"material": mat, "positions": value})

        return scene

    def get_num_delayed_actions(self) -> int:
        return len(self._delayed_templates)

    def run_delayed_actions(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        delayed = self._delayed_templates
        self._delayed_templates = []
        if delayed:
            bounds = find_bounds(scene)
            mat_to_loc = {}
            existing_holes = []
            existing_floor_materials = []
            for s_type, template in delayed:
                try:
                    add_structural_object_with_retries_or_throw(
                        scene, bounds, MAX_TRIES, template,
                        s_type, 0, existing_holes, mat_to_loc,
                        existing_floor_materials)
                except ILEDelayException:
                    self._delayed_templates.append((s_type, template))
        return scene


class RandomStructuralObjectsComponent(ILEComponent):
    """Adds random structural objects to an ILE scene.  Users can specify an
    exact number or a range.  When a range is specified, each generated scene
    will have a uniformly distributed random number be generated within that
    range, inclusively.  Alternatively, the user can specify an object with
    a number or range for each type of structural object, wall, l occluder,
    platform, ramp, moving_occluder, holes, floor materials, doors.

    This component requires performerStart.location to be set in the scene
    prior. This is typically handles by the GlobalSettingsComponent"""
    random_structural_objects: Union[RandomStructuralObjectConfig,
                                     List[RandomStructuralObjectConfig]] = 0
    """
    ([RandomStructuralObjectConfig](#RandomStructuralObjectConfig), or list of
    [RandomStructuralObjectConfig](#RandomStructuralObjectConfig) dict) --
    Groups of random object types and how many should be generated from the
    type options.
    Default: 2 to 4 of all types
    ```
    random_structural_objects:
      - type:
          - doors
          - droppers
          - floor_materials
          - holes
          - l_occluders
          - lava
          - moving_occluders
          - placers
          - platforms
          - ramps
          - throwers
          - walls
        num:
          min: 2
          max: 4
    ```

    Simple Example:
    ```
    random_structural_objects: null
    ```

    Advanced Example:
    ```
    random_structural_objects:
      - type:
          - doors
          - droppers
          - floor_materials
          - holes
          - l_occluders
          - lava
          - moving_occluders
          - placers
          - platforms
          - ramps
          - throwers
          - walls
        num:
            min: 0
            max: 2
      - type: ['walls', 'l_occluders']
        num: [3, 5, 7]
      - type: 'walls'
        num: 2
    ```
    """

    ALL_TYPES = [item.name.lower() for item in StructuralTypes]
    ALL_TYPES_NO_TARGET = [
        item.name.lower() for item in StructuralTypes
        # The following StructuralTypes need a target object:
        if item not in [StructuralTypes.OCCLUDING_WALLS]
    ]
    DEFAULT_VALUE = [RandomStructuralObjectConfig(
        ALL_TYPES_NO_TARGET,
        MinMaxInt(2, 4)
    )]

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

    # Override
    def update_ile_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        logger.info('Configuring random structural objects...')

        existing_holes = []
        existing_floor_materials = []
        mat_to_loc = {}

        scene['holes'] = scene.get('holes', [])
        scene['floorTextures'] = scene.get('floorTextures', [])
        scene['objects'] = scene.get('objects', [])
        bounds = find_bounds(scene)
        templates = self.random_structural_objects
        using_default = False
        if templates is None:
            templates = self.DEFAULT_VALUE
            using_default = True
        templates = templates if isinstance(templates, List) else [templates]

        logger.trace(f'Choosing random structural objects: {templates}')

        # List all the valid types for randomly generated structural objects.
        target_exists = ObjectRepository.get_instance().has_label(TARGET_LABEL)
        all_types = (
            self.ALL_TYPES if target_exists else self.ALL_TYPES_NO_TARGET
        )

        for template in templates:
            num = choose_random(template.num)
            for i in range(num):
                type = choose_random(template.type or all_types)
                structural_type = StructuralTypes[type.upper()]
                if using_default:
                    logger.info(
                        f'Using default setting to generate random '
                        f'structural object number {i + 1} / {num + 1}: '
                        f'{structural_type.name.lower().replace("_", " ")}'
                    )
                else:
                    logger.debug(
                        f'Using configured setting to generate random '
                        f'structural object number {i + 1} / {num + 1}: '
                        f'{structural_type.name.lower().replace("_", " ")}'
                    )
                random_template = self._create_random_template(type, template)
                add_structural_object_with_retries_or_throw(
                    scene, bounds, MAX_TRIES, random_template, structural_type,
                    i, existing_holes, mat_to_loc, existing_floor_materials)

        for mat, value in mat_to_loc.items():
            scene['floorTextures'].append(
                {"material": mat, "positions": value})

        return scene

    def _create_random_template(
        self,
        type_string: str,
        template: RandomStructuralObjectConfig
    ) -> Optional[BaseStructuralObjectsConfig]:
        structural_type = StructuralTypes[type_string.upper()]
        # If set, assign the config template's relative object label to the new
        # template that's passed into the structural object generator.
        relative_object_label = template.relative_object_label
        if structural_type == StructuralTypes.DOORS:
            return StructuralDoorConfig(labels=template.labels)
        if structural_type == StructuralTypes.DROPPERS:
            return StructuralDropperConfig(
                labels=template.labels,
                projectile_labels=relative_object_label
            )
        if structural_type == StructuralTypes.PLACERS:
            return StructuralPlacerConfig(
                labels=template.labels,
                placed_object_labels=relative_object_label
            )
        if structural_type == StructuralTypes.L_OCCLUDERS:
            return StructuralLOccluderConfig(labels=template.labels)
        if structural_type == StructuralTypes.MOVING_OCCLUDERS:
            return StructuralMovingOccluderConfig(labels=template.labels)
        if structural_type == StructuralTypes.OCCLUDING_WALLS:
            return StructuralOccludingWallConfig(
                keyword_location=template.keyword_location,
                labels=template.labels
            )
        if structural_type == StructuralTypes.PLATFORMS:
            return StructuralPlatformConfig(labels=template.labels)
        if structural_type == StructuralTypes.RAMPS:
            return StructuralRampConfig(labels=template.labels)
        if structural_type == StructuralTypes.THROWERS:
            return StructuralThrowerConfig(
                labels=template.labels,
                projectile_labels=relative_object_label
            )
        if structural_type == StructuralTypes.WALLS:
            return StructuralWallConfig(labels=template.labels)
        # Otherwise return None; defaults will be used automatically.
        return None

    def get_random_structural_objects(
            self) -> List[RandomStructuralObjectConfig]:
        rso = self.random_structural_objects
        if rso is None:
            return self.DEFAULT_VALUE
        if not isinstance(rso, List):
            rso = [rso]
        return [choose_random(obj) for obj in rso]

    # If not null, each number must be an integer zero or greater.
    @ile_config_setter(validator=ValidateNumber(
        props=[
            'num'],
        min_value=0)
    )
    def set_random_structural_objects(self, data: Any) -> None:
        self.random_structural_objects = data
