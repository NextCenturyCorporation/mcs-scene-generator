from dataclasses import asdict, dataclass, field
from typing import List, Optional

from machine_common_sense.config_manager import (
    FloorTexturesConfig,
    Goal,
    PerformerStart,
    PhysicsConfig,
    RoomMaterials,
    Vector2dInt,
    Vector3d
)

from . import ObjectBounds, SceneObject, geometry

# TODO MCS-1234
# Wanted to use Pydantic, but need MCS to use it and release it first.
# This is temporary.
scene_aliases = {
    "ceiling_material": "ceilingMaterial",
    "floor_material": "floorMaterial",
    "floor_properties": "floorProperties",
    "floor_textures": "floorTextures",
    "intuitive_physics": "intuitivePhysics",
    "isometric_front_right": "isometricFrontRight",
    "partition_floor": "partitionFloor",
    "performer_start": "performerStart",
    "restrict_open_doors": "restrictOpenDoors",
    "restrict_open_objects": "restrictOpenObjects",
    "room_dimensions": "roomDimensions",
    "room_materials": "roomMaterials",
    "wall_material": "wallMaterial",
    "wall_properties": "wallProperties"
}


@dataclass
class PartitionFloor:
    leftHalf: Optional[float] = 0
    rightHalf: Optional[float] = 0


@dataclass
class Scene:
    '''Class for keeping track of scene.  This could eventually be replaced by
    or extend the SceneConfiguration class in MCS.  Some fields have duplicates
    commented out that are the field definintions for MCS.  However, we don't
    want to change everything all at once.'''
    ceiling_material: str = None
    debug: dict = field(default_factory=dict)
    floor_material: str = None
    floor_properties: PhysicsConfig = None
    floor_textures: List[FloorTexturesConfig] = field(default_factory=list)
    goal: Goal = None
    holes: List[Vector2dInt] = field(default_factory=list)
    intuitive_physics: bool = False
    isometric: bool = False
    isometric_front_right: bool = False
    lava: List[Vector2dInt] = field(default_factory=list)
    name: str = ""
    objects: List[SceneObject] = field(default_factory=list)
    partition_floor: PartitionFloor = None
    performer_start: PerformerStart = None
    restrict_open_doors: bool = None
    restrict_open_objects: bool = None
    room_dimensions: Vector3d = None
    room_materials: RoomMaterials = None
    screenshot: bool = False  # developer use only; for the image generator
    version: int = 2
    wall_material: str = None
    wall_properties: PhysicsConfig = None

    def __post_init__(self):
        # there is probably a better way to make sure each instance has unique
        # values for defaults.
        if self.goal is None:
            self.goal = Goal(metadata={})
        if self.performer_start is None:
            self.performer_start = PerformerStart(
                position=Vector3d(),
                rotation=Vector3d())
        if self.room_dimensions is None:
            self.room_dimensions = Vector3d(**geometry.DEFAULT_ROOM_DIMENSIONS)

    def set_room_dimensions(self, x: int, y: int, z: int):
        """convenience method to set room dimensions via components"""
        self.room_dimensions = Vector3d(x=x, y=y, z=z)

    def set_performer_start(self, start_position: Vector3d,
                            start_rotation: Vector3d):
        self.performer_start = PerformerStart(position=start_position,
                                              rotation=start_rotation)

    def set_performer_start_position(self, x: float, y: float, z: float):
        x = x if x is not None else self.performer_start.position.x
        y = y if y is not None else self.performer_start.position.y
        z = z if z is not None else self.performer_start.position.z
        self.performer_start.position = Vector3d(x=x, y=y, z=z)

    def set_performer_start_rotation(self, x: int, y: int):
        self.performer_start.rotation = Vector3d(x=x, y=y, z=0)

    def get_targets(self) -> List[SceneObject]:
        """Returns the list of all targets for this scene's goal, or an empty
        list if this scene has no goal or targets."""
        targets = []
        goal = self.goal or Goal()
        metadata = goal.metadata or {}
        target = metadata.get('target', {})
        targets_info = [target] if target else metadata.get('targets', [])
        for target_info in targets_info:
            target_id = target_info.get('id', {})
            for instance in (self.objects or []):
                if instance.get('id', '') == target_id:
                    targets.append(instance)
                    break
        return targets

    def get_object_by_id(self, object_id: str) -> Optional[SceneObject]:
        """Returns the object in this scene with the given ID, or None if such
        an object does not currently exist."""
        return next(filter(lambda x: x['id'] == object_id, self.objects), None)

    def find_bounds(
        self,
        ignore_ground: bool = False,
        ignore_ids: List[str] = None
    ) -> List[ObjectBounds]:
        """Calculate and return the bounds for all the given objects."""
        # Create a bounding box for each hole/lava and add it to the list.
        bounds = [] if ignore_ground else [
            geometry.generate_floor_area_bounds(area.x, area.z)
            for area in (self.holes + self.lava)
        ]

        if self.partition_floor and not ignore_ground:
            bounds += geometry.find_partition_floor_bounds(
                self.room_dimensions, self.partition_floor)

        # Add each object's bounding box to the list.
        for instance in self.objects:
            if instance.get('id') in (ignore_ids or []):
                continue
            try:
                bounds.append(instance['shows'][0]['boundingBox'])
            except (KeyError):
                ...
        return bounds

# TODO MCS-1234
# Wanted to use Pydantic, but need MCS to use it and release it first.
# Much of this is temporary.

    def to_dict(self):
        # return recursive_vars(self)
        data = asdict(self)
        for key, alias in scene_aliases.items():
            if key in data:
                data[alias] = data[key]
                del data[key]
        remove = [key for key in data if data[key] is None]
        for key in remove:
            del data[key]

        # manual conversion of pydantic classes
        for prop in ['holes', 'lava']:
            if prop in data:
                data[prop] = [area.dict() for area in data[prop]]
        if 'floorTextures' in data:
            data['floorTextures'] = [
                item.dict() for item in data['floorTextures']
            ]
        data['performerStart'] = data['performerStart'].dict()
        data['roomDimensions'] = data['roomDimensions'].dict()
        if 'roomMaterials' in data:
            data['roomMaterials'] = data['roomMaterials'].dict()
        data['goal'] = data['goal'].dict()
        for key, alias in [
            ('domains_info', 'domainsInfo'),
            ('objects_info', 'objectsInfo'),
            ('scene_info', 'sceneInfo'),
            ('triggered_by_target_sequence', 'triggeredByTargetSequence')
        ]:
            if key in data['goal']:
                data['goal'][alias] = data['goal'][key]
                del data['goal'][key]
        remove = [key for key in data['goal'] if data['goal'][key] is None]
        for key in remove:
            del data['goal'][key]

        data['objects'] = [dict(instance) for instance in data['objects']]
        return data


def get_step_limit_from_dimensions(room_x: int, room_z: int) -> int:
    room_x = room_x or geometry.DEFAULT_ROOM_DIMENSIONS['x']
    room_z = room_z or geometry.DEFAULT_ROOM_DIMENSIONS['z']
    steps_moving_around_the_room = ((room_x * 10) + (room_z * 10)) * 2
    steps_for_rotation = 100
    return int((steps_moving_around_the_room + steps_for_rotation) * 5)
