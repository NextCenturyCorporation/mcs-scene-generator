from dataclasses import asdict, dataclass, field
from typing import List, Optional

from machine_common_sense.config_manager import (
    FloorTexturesConfig,
    PerformerStart,
    PhysicsConfig,
    RoomMaterials,
    Vector3d,
)

from generator.geometry import DEFAULT_ROOM_DIMENSIONS

# TODO MCS-1234
# Wanted to use Pydantic, but need MCS to use it and release it first.
# This is temporary.
scene_aliases = {
    "ceiling_material": "ceilingMaterial",
    "floor_material": "floorMaterial",
    "floor_properties": "floorProperties",
    "floor_textures": "floorTextures",
    "intuitive_physics": "intuitivePhysics",
    "partition_floor": "partitionFloor",
    "performer_start": "performerStart",
    "restrict_open_doors": "restrictOpenDoors",
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
    # goal: Goal = None
    goal: dict = None
    # holes: List[Vector2dInt] = field(default_factory=list)
    holes: List = field(default_factory=list)
    intuitive_physics: bool = False
    isometric: bool = False
    # lava: List[Vector2dInt] = field(default_factory=list)
    lava: List = field(default_factory=list)
    name: str = ""
    # objects: List[SceneObject] = field(default_factory=list)
    objects: List = field(default_factory=list)
    partition_floor: PartitionFloor = None
    performer_start: PerformerStart = None
    restrict_open_doors: bool = None
    room_dimensions: Vector3d = None
    room_materials: RoomMaterials = None
    screenshot: bool = False  # developer use only; for the image generator
    version: int = None
    wall_material: str = None
    wall_properties: PhysicsConfig = None

    def __post_init__(self):
        # there is probably a better way to make sure each instance has unique
        # values for defaults.
        if self.goal is None:
            self.goal = {
                "metadata": {}
            }
        if self.performer_start is None:
            self.performer_start = PerformerStart(
                position=Vector3d(),
                rotation=Vector3d())
        if self.room_dimensions is None:
            self.room_dimensions = Vector3d(**DEFAULT_ROOM_DIMENSIONS)

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

    def set_performer_start_rotation(self, y: int):
        self.performer_start.rotation = Vector3d(x=0, y=y, z=0)

    def get_target_object(self):
        tgt = None
        goal = self.goal or {}
        metadata = goal.get('metadata', {})
        tar = metadata.get('target', {})
        targetId = tar.get('id', {})
        for o in self.objects or []:
            if o.get('id', '') == targetId:
                tgt = o
                break
        return tgt

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
        data['performerStart'] = data['performerStart'].dict()
        data['roomDimensions'] = data['roomDimensions'].dict()
        return data


def get_step_limit_from_dimensions(room_x: int, room_z: int) -> int:
    room_x = room_x or DEFAULT_ROOM_DIMENSIONS['x']
    room_z = room_z or DEFAULT_ROOM_DIMENSIONS['z']
    steps_moving_around_the_room = ((room_x * 10) + (room_z * 10)) * 2
    steps_for_rotation = 100
    return int((steps_moving_around_the_room + steps_for_rotation) * 5)
