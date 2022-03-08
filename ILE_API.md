# ILE API

[How to Use the ILE](./README.md)

#### Table of Content
- [Lists](#Lists)
- [Classes](#Classes)
- [Options](#Options)

## Lists

- [Interactable shapes](https://nextcenturycorporation.github.io/MCS/schema.html#interactable-objects)
- [Materials](https://nextcenturycorporation.github.io/MCS/schema.html#material-list)
- [Tool shapes](https://nextcenturycorporation.github.io/MCS/schema.html#tool-objects)

## Classes

Some [configurable ILE options](#Options) use the following classes
(represented as dicts in the YAML):

#### FloorAreaConfig

Defines an area of the floor of the room.  Note: Coordinates must be
integers. Areas are always size 1x1 centered on the given X/Z coordinate.
Adjacent areas are combined.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of areas to be used with these parameters
- `position_x` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
list of MinMaxInt dicts): X position of the area.
- `position_z` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
list of MinMaxInt dicts): Z position of the area.

#### FloorMaterialConfig

Defines details of a specific material on a specific location of the
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

#### GoalConfig

A dict with str `category` and optional `target`, `target_1`, and
`target_2` properties that represents the goal and target object(s) in each
scene. The `target*` properties are only needed if required for the
specific category of goal. Each `target*` property is either an
InteractableObjectConfig dict or list of InteractableObjectConfig dicts.
For each list, one dict will be randomly chosen within the list in each
new scene.  All goal target objects will be assigned the 'target' label.

Example:
```
category: retrieval
target:
    shape: soccer_ball
    scale:
      min: 1.0
      max: 3.0
```

#### InteractableObjectConfig

Represents the template for a specific object (with one or more possible
variations) that will be added to each scene. Each template can have the
following optional properties:
- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict): The number
of objects with this template to generate in each scene. For a list or a
MinMaxInt, a new number will be randomly chosen for each scene.
Default: `1`
- `keyword_location`: ([KeywordLocationConfig](#KeywordLocationConfig)):
Used to identify one of the qualitative locations specified by keywords.
This field should not be set when `position` or `rotation` are also set.
- `labels` (string, or list of strings): labels to associate with this
object.  Components can use this label to reference this object or a group
of objects.  Labels do not need to be unique and when objects share a
labels, components have options to randomly choose one or choose all.  See
specific label options for details.
- `material` (string, or list of strings): The material (color/texture) to
use on this object in each scene. For a list, a new material will be
randomly chosen for each scene. Default: random
- `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
VectorFloatConfig dicts): The position of this object in each scene. For a
list, a new position will be randomly chosen for each scene.
Default: random
- `rotation` ([VectorIntConfig](#VectorIntConfig) dict, or list of
VectorIntConfig dicts): The rotation of this object in each scene. For a
list, a new rotation will be randomly chosen for each scene.
Default: random
- `identical_to` (str): used to match to another object with
the specified label, so that this definition can share that object's
exact shape, scale, and material.
- `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts, or [VectorFloatConfig](#VectorFloatConfig)
dict, or list of VectorFloatConfig dicts): The scale of this object in each
scene. A single float will be used as the scale for all object dimensions
(X/Y/Z). For a list or a MinMaxFloat, a new scale will be randomly chosen
for each scene. Default: `1`
- `shape` (string, or list of strings): The shape (object type) of this
object in each scene. For a list, a new shape will be randomly chosen for
each scene. Default: random
- `locked` (bool or list of bools): If true and the resulting object is
lockable, like a container or door, the object will be locked.  If the
object is not lockable, this field has no affect.

Example:
```
num: 1
material: "Custom/Materials/Blue"
position:
    x: 3
    z: 3
rotation:
    y: 90
scale: 1.5
shape: ball
```

Labels Example:
```
specific_interactable_objects:
  -
    num: 1
    position:
      x: 3
      z: 3
    rotation:
      y: 90
    shape: chest_3
    scale: 1.5
    labels: my_container
  -
    num: 1
    material: "Custom/Materials/Blue"
    scale: 0.5
    shape: ball
    keyword_location:
      keyword: in
      container_label: my_container
  -
    num: 1
    material: "Custom/Materials/Blue"
    scale: 0.5
    shape: ball
    keyword_location:
      keyword: adjacent
      relative_object_label: my_container
  -
    num: 2
    identical_to: my_container
```

#### KeywordLocationConfig

Describes an object's keyword location. Can have the following
properties:
- `keyword` (string, or list of strings): The keyword location, which can
be one of the following:
    - `adjacent` - The object will be placed next to another object.  The
    other object must be referenced by the 'relative_object_label' field.
    If multiple objects have this label, one will be randomly chosen.
    - `back` - The object will be placed in the 180 degree arc behind the
    performer's start position.
    - `behind` - The object will be placed behind another object, relative
    to the performer's start position.  The other object must be referenced
    by the 'relative_object_label' field.  If multiple objects have this
    label, one will be randomly chosen.
    - `between` - The object will be placed between the performer's start
    position and another object.  The other object must be referenced by
    the 'relative_object_label' field.  If multiple objects have this
    label, one will be randomly chosen.
    - `front` - The object will be placed in a line in front of the
    performer's start position.
    - `in` - The object will be placed inside a container.  The container
    must be referenced by the 'container_label' field.  If multiple objects
    have this label, one will be randomly chosen.
    - `in_with` - The object will be placed inside a container along with
    another object.  The container must be referenced by the
    'container_label' field.  The other object must be referenced by the
    'relative_object_label' field.  If multiple objects have these label,
    one will be randomly chosen for each field.
    - `occlude` - The object will be placed between the performer's start
    position and another object so that this object completely occludes the
    view of the other object.  The other object must be referenced by
    the 'relative_object_label' field.  If multiple objects have this
    label, one will be randomly chosen.
    - `on_center` - The object will be placed on top of another object
    in the center of the bounds.  This option is best for objects the are
    similar in size or for use cases where objects are desired to be
    centered.  The object must be referenced by the 'relative_object_label'
    field.  If multiple objects have this label,
    one will be randomly chosen.
    - `on_top` - The object will be placed on top of another object in a
    random location.  This option is best for when the object is
    significantly smaller than the object it is placed on (I.E. a small
    ball on a large platform).  If the objects are similar in size
    (I.E. two bowls), use 'on_center'.  The object must be referenced by
    the 'relative_object_label' field.  If multiple objects have this
    label, one will be randomly chosen.
- `container_label` (string, or list of strings): The label of a container
object that already exists in your configuration. Only required by some
keyword locations.
- `relative_object_label` (string, or list of strings): The label of a
second object that already exists in your configuration. Only required by
some keyword locations.

#### KeywordObjectsConfig

Describes a single group of a keyword objects.  Keyword objects has the
following properties:
- `keyword` (string, or list of strings): The type of object, like
confusor, container, obstacle, or occluder.
If an array is given, one will be chosen for each creation of this group.
    - `"confusors"`: Objects that are similar to the target in two of the
    following: color, shape, size.
    - `"containers"`: Receptacles that can contain other objects and can
    open and close, like chests.  These containers can be of any size.
    - `"containers_can_contain_target"`: Receptacles that can contain other
    objects and can open and close, like chests.  These containers
    will be large enough to contain the target.  If a goal target does
    not exist, generation will fail.
    - `"containers_cannot_contain_target"`: Receptacles that can contain
    other objects and can open and close, like chests.  These containers
    will not be large enough to contain the target.  If a goal target does
    not exist, generation will fail.
    - `"obstacles"`: Objects that prevent movement through/under them but
    allow sight through them, like chairs or tables with four individual
    legs.
    - `"occluders"`: Objects that prevent both movement through/under them
    AND sight through them, like sofas or bookcases with solid back panels.
    This is completely different from the occluders in passive
    intuitive physics scenes.
    - `"context"`: Objects (also called "distractors") that are small,
    pickupable, and serve to clutter the room to possibly distract the AI.
    They are never the same shape as the target object, if the scene has a
    goal with a target object.
    - `"open_topped_containers"`: Objects that can contain other objects
    but have no lid and open tops instead.
- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): The number of this object the user wants to create.
- `keyword_location`: ([KeywordLocationConfig](#KeywordLocationConfig)):
One of the keyword locations for this object or set of objects. Any choices
in `keyword_location` are made for each object inside the group, not the
group as a whole.

#### LavaTargetToolConfig

Defines details of the shortcut_lava_target_tool shortcut.  This shortcut
creates a room with a goal object on an island surrounded by lava. There
will also be a block tool to facilitate acquiring the goal object.
- `island_size` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
or list of MinMaxInt dicts): The width and lenght of the island inside the
lava.  Must produce value from 1 to 3.
Default: Random based on room size
- `front_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
The number of tiles of lava in front of the island.  Must produce value
between 2 and 6. Default: Random based on room size and island size
- `rear_lava_width` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
The number of tiles of lava behind of the island.  Must produce value
between 2 and 6. Default: Random based on room size, island size, and
other lava widths.
- `guide_rails` (bool, or list of bools): If True, guide rails will be
generated to guide the tool in the direction it is oriented.  If a target
exists, the guide rails will extend to the target.  This option cannot be
used with `tool_rotation`. Default: False
- `tool_rotation` (int, or list of ints, or [MinMaxInt](#MinMaxInt):
Angle that too should be rotated out of alignment with target.
This option cannot be used with `guide_rails`.  Default: 0
- `random_performer_position` (bool, or list of bools): If True, the
performer will be randomly placed in the room. They will not be placed in
the lava or the island   Default: False

#### MinMaxFloat

A dict with float `min` and float `max` properties that represents a
random inclusive numerical range. A float will be randomly chosen from
within the range in each new scene.

Example:
```
min: 0.5
max: 1.5
```

#### MinMaxInt

A dict with int `min` and int `max` properties that represents a
random inclusive numerical range. An int will be randomly chosen from
within the range in each new scene.

Example:
```
min: 1
max: 10
```

#### RandomStructuralObjectConfig

A dict that configures the number of structural objects that will be
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
    - `lava`: A random area in the floor is changed to a pool of lava.
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

#### StepBeginEnd

Contains a step range for a specific event.

- `begin` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list
of MinMaxInt dicts):
The step where the performer agent starts being frozen
and can only use the `"Pass"` action. For example, if 1, the performer
agent must pass immediately at the start of the scene.  This is an
inclusive limit.
- `end` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list
of MinMaxInt dicts):
The step where the performer agent ends being frozen and can resume
using actions besides `"Pass"`.  Therefore, this is an exclusive limit.

#### StructuralDoorConfig

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

#### StructuralDropperConfig

Defines details of a structural dropper and its dropped projectile.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of structures to be created with these parameters
- `drop_step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
list of MinMaxInt dicts): The step of the simulation in which the
projectile should be dropped.
- `labels` (string, or list of strings): A label or labels to be assigned
to this object. Always automatically assigned "droppers"
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

#### StructuralLOccluderConfig

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

#### StructuralMovingOccluderConfig

Defines details of a structural moving occluder.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of structures to be created with these parameters
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
- `repeat_interval` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
or list of MinMaxInt dicts): if `repeat_movement` is true, the number of
steps to wait before repeating the full movement.  Default is between 1
and 20.
- `repeat_movement` (bool, or list of bools): If true, repeat the
occluder's full movement and rotation indefinitely, using `repeat_interval`
as the number of steps to wait. Default: [true, false]
- `reverse_direction` (bool, or list of bools): Reverse the rotation
direction of a sideways wall by rotating the wall 180 degrees. Only used if
`origin` is set to a wall and not `top`. Default: [true, false]
- `rotation_y` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
or list of MinMaxInt dicts): Y rotation of a non-sideways occluder wall;
only used if any `origin` is set to `top`.  Default is 0 to 359.
- `labels` (string, or list of strings): A label or labels to be assigned
to this object. Always automatically assigned "moving_occluders"
- `wall_material` (string, or list of strings): Material of the occluder
wall (cube)

#### StructuralOccludingWallConfig

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

#### StructuralPlacerConfig

Defines details for an instance of a placer (cylinder) descending from the
ceiling on the given activation step to place an object with the given
position.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of areas to be used with these parameters
- `activation_step`: (int, or list of ints, or [MinMaxInt](#MinMaxInt)
dict): Step on which placer should begin downward movement. Default:
between 0 and 10
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

#### StructuralPlatformConfig

Defines details of a structural platform.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of structures to be created with these parameters
- `labels` (string, or list of strings): A label or labels to be assigned
to this object. Always automatically assigned "platforms"
- `material` (string, or list of strings): The structure's material or
material type.
- `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
VectorFloatConfig dicts): The structure's position in the scene
- `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
- `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts): Scale of the platform
- `lips` ([StructuralPlatformLipsConfig]
(#StructuralPlatformLipsConfig), or list of
StructuralPlatformLipsConfig): The platform's lips. Default: None
- `attached_ramps` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
or list of MinMaxInt dicts): Number of ramps that should be attached to
this platform to allow the performer to climb up to this platform.
Default: 0
- `platform_underneath` (bool or list of bools): If true, add a platform
below this platform that touches the floor on the bottom and this platform
on the top.  This platform will fully be encased in the x/z directions by
the platform created underneath.  Default: False
- `platform_underneath_attached_ramps` (int, or list of ints, or
[MinMaxInt](#MinMaxInt) dict, or list of MinMaxInt dicts): Number of ramps
that should be attached to the platform created below this platform to
allow the performer to climb onto that platform. Default: 0

#### StructuralPlatformLipsConfig

Defines the platform's lips with front, back,
left, and right configurations.

- `front` (bool) : Positive Z axis
- `back` (bool) : Negative Z axis
- `left` (bool) : Negative X axis
- `right` (bool) : Positive X axis

#### StructuralRampConfig

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
- `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
VectorFloatConfig dicts): The structure's position in the scene
- `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
- `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts): Width of the ramp
- `platform_underneath` (bool or list of bools): If true, add a platform
below this ramp that touches the floor on the bottom and the bottom of
this ramp on the top.  This ramp will fully be encased in the x/z
directions by the platform created underneath.  Default: False
- `platform_underneath_attached_ramps` (int, or list of ints, or
[MinMaxInt](#MinMaxInt) dict, or list of MinMaxInt dicts): Number of ramps
that should be attached to the platform created below this ramp to
allow the performer to climb onto that platform.  Default: 0

#### StructuralThrowerConfig

Defines details of a structural dropper and its thrown projectile.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of structures to be created with these parameters
- `labels` (string, or list of strings): A label or labels to be assigned
to this object. Always automatically assigned "throwers"
- `height` (float, or list of floats, or
[MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): The
height on the wall that the thrower will be placed.
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
- `rotation` (float, or list of floats, or
[MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): The angle
in which the thrower will be rotated to point upwards.  This value should
be between 0 and 15.
- `throw_force` (float, or list of floats, or
[MinMaxFloat](#MinMaxFloat) dict, or list of MinMaxFloat dicts): Force of
the throw put on the projectile.  This value will be multiplied by the
mass of the projectile.  Values between 500 and 1500 are typical.
- `throw_step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or
list of MinMaxInt dicts): The step of the simulation in which the
projectile should be thrown.
- `wall` (string, or list of strings): Which wall the thrower should be
placed on.  Options are: left, right, front, back.

#### StructuralWallConfig

Defines details of a structural interior wall.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of structures to be created with these parameters
- `height` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts): The height of the wall.
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

#### TeleportConfig

Contains data to describe when and where a teleport occurs.

- `step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): The step when the performer agent is teleported.
This field is required for teleport action restrictions.
- `position_x` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
dict, or list of MinMaxFloat dicts):
Position in X direction where the performer agent
is teleported.  This field along with `position_z` are required
if `rotation_y` is not set.
- `position_z` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
dict, or list of MinMaxFloat dicts):
Position in Z direction where the performer agent
is teleported.  This field along with `position_x` are required
if `rotation_y` is not set.
- `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
dict, or list of MinMaxFloat dicts):
Rotation in Y direction where the performer agent
is teleported.  This field is required for teleport action
restrictions if `position_x` and `position_z` are not both set.

#### ToolConfig

Defines details of a tool object.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of structures to be created with these parameters
- `labels` (string, or list of strings): A label or labels to be assigned
to this object. Always automatically assigned "platforms"
- `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
VectorFloatConfig dicts): The structure's position in the scene
- `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
- `shape` (string, or list of strings): The shape (object type) of this
object in each scene. For a list, a new shape will be randomly chosen for
each scene. Must be a valid [tool shape](#Lists). Default: random
- `guide_rails` (bool, or list of bools): If True, guide rails will be
generated to guide the tool in the direction it is oriented.  If a target
exists, the guide rails will extend to the target.  Default: random

#### TripleDoorConfig

Defines details of the triple door shortcut.  This short cut contains a
platform that bisects the room.  A wall with 3 doors (a.k.a. door occluder,
or "door-cluder" or "doorcluder") will bisect the room
in the perpendicular direction.

- `start_drop_step` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict,
or list of MinMaxInt dicts): Step number to start dropping the bisecting
wall with doors.  If None or less than 1, the wall will start in position.
Default: None
- `add_lips` (bool, or list of bools): If true, lips will be added on the
platform beyond the doors and wall such that the performer will be forced
to go through the corresponding door to enter the area behind it.
Default: True
- `add_freeze` (bool, or list of bools): If true and 'start_drop_step is'
greater than 0, the user will be frozen (forced to Pass) until the wall and
doors are in position.  If the 'start_drop_step' is None or less than 1,
this value has no effect.  Default: True
- `restrict_open_doors` (bool, or list of bools): If true, the performer
will only be able to open one door.  Using this feature and 'add_lips'
will result in a forced choice by the performer.  Default: True
- `door_material` (string, or list of strings): The material or material
type for the doors.
- `wall_material` (string, or list of strings): The material or material
type for the wall.

#### VectorFloatConfig

A dict with `x`, `y`, and `z` properties (each of which are either a
float, list of floats, or MinMaxFloat) that represents a global coordinate
in the scene. For each list, one float will be randomly chosen from the
list in each new scene; for each MinMaxFloat, one float will be randomly
chosen from within the corresponding range in each new scene.

Example:
```
x:
    - -0.5
    - -0.25
    - 0
    - 0.25
    - 0.5
y: 0.1
z:
    min: -0.5
    max: 0.5
```

#### VectorIntConfig

A dict with `x`, `y`, and `z` properties (each of which are either an
int, list of ints, or MinMaxInt) that represents a global coordinate
in the scene. For each list, one int will be randomly chosen from the
list in each new scene; for each MinMaxInt, one int will be randomly
chosen from within the corresponding range in each new scene.

Example:
```
x:
    - -1
    - 0
    - 1
y: 0
z:
    min: -1
    max: 1
```


## Options

You may set the following options in your ILE (YAML) config file:

#### ceiling_material

(string, or list of strings): A single material for the ceiling, or a
list of materials for the ceiling, from which one is chosen at random for
each scene. Default: random

Simple Example:
```
ceiling_material: null
```

Advanced Example:
```
ceiling_material: "Custom/Materials/GreyDrywallMCS"
```

#### check_valid_path

(bool): If true, checks for a valid path between the performer agent's
starting position and the target's position and retries generating the
current scene if one cannot be found. Considers all objects and structures
that the performer would hit when their position is y = 0 or are light
enough to be pushed.  The check also considers all holes and areas of lava
in the scene. Pathfinding is only done in two dimensions. Check is skipped
if false.
Default: False

Simple Example:
```
check_valid_path: false
```

Advanced Example:
```
check_valid_path: true
```

#### doors

([StructuralDoorConfig](#StructuralDoorConfig), or list
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

#### excluded_shapes

(string, or list of strings): Zero or more object shapes (types) to exclude
from being randomly generated. Objects with the listed shapes can still be
generated using specifically set configuration options, like the `type`
property in the `goal.target` and `specific_interactable_objects` options.
Useful if you want to avoid randomly generating additional objects of the
same shape as a configured goal target. Default: None

Simple Example:
```
excluded_shapes: null
```

Advanced Example:
```
excluded_shapes: "soccer_ball"
```

#### floor_material

(string, or list of strings): A single material for the floor, or a
list of materials for the floor, from which one is chosen at random for
each scene. Default: random

Simple Example:
```
floor_material: null
```

Advanced Example:
```
floor_material: "Custom/Materials/GreyCarpetMCS"
```

#### floor_material_override

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

#### freezes

(list of [StepBeginEnd](#StepBeginEnd) dicts): When a freeze
should occur.  A freeze forces the performer agent to only `"Pass"` for a
range of steps.  User should try to avoid freeze overlaps, but if using
ranges and choices, the ILE will retry on overlaps.  This field must be
blank or an empty array if `passive_scene` is `true`.

Simple Example:
```
freezes: null
```

Advanced Example:
```
freezes:
  -
    begin: 1
    end: 3
  -
    begin: [11, 13 ,15]
    end:
      min: 16
      max: 26

```

#### goal

([GoalConfig](#GoalConfig) dict): The goal category and target(s) in each
scene, if any. Default: None

Simple Example:
```
goal: null
```

Advanced Example:
```
goal:
    category: retrieval
    target:
        shape: soccer_ball
        scale:
          min: 1.0
          max: 3.0
```

#### holes

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

#### keyword_objects

([KeywordObjectsConfig](#KeywordObjectsConfig) dict, or list of
KeywordObjectsConfig dicts): Creates interactable objects of specific
categories like confusors, containers, obstacles, or occluders.
Default:
  * 0 to 10 context objects
  * 2 to 4 of container, obstacles, and occluders
```
keyword_objects:
    - keyword: ["containers", "obstacles", "occluders"]
    num:
        min: 2
        max: 4
    - keyword: "context"
        min: 0
        max: 10
```

All objects created here will be given the following labels.  For more
information see ([InteractableObjectConfig](#InteractableObjectConfig))
for more information on labels.
  - confusors: keywords_confusors
  - containers: keywords_containers
  - containers_can_contain_target:
      keywords_containers, keywords_containers_can_contain_target
  - containers_cannot_contain_target:
      keywords_containers, keywords_containers_cannot_contain_target
  - obstacles: keywords_obstacles
  - occluders: keywords_occluders
  - context: keywords_context
  - open_topped_containers: keywords_open_topped_containers

Simple Example:
```
keyword_objects: null
```

Advanced Example:
```
keyword_objects:
  -
    keyword: confusors
    num: 1
  -
    keyword: containers
    num:
      min: 0
      max: 3
  -
    keyword: containers_can_contain_target
    num: 1
    keyword_location:
      keyword: front
  -
    keyword: containers_cannot_contain_target
    num: 1
  -
    keyword: obstacles
    num: [2, 4]
    keyword_location:
      keyword: adjacent
      relative_object_label: other_object
  -
    keyword: occluders
    num: 1
  -
    keyword: context
    num: 20
```

Note: Creating too many random objects can increase the chance of failure.

#### last_step

(int, or list of ints): The last possible action step, or list of last
steps, from which one is chosen at random for each scene. Default: none
(unlimited)

Simple Example:
```
last_step: null
```

Advanced Example:
```
last_step: 1000
```

#### lava

([FloorAreaConfig](#FloorAreaConfig), or list of
[FloorAreaConfig](#FloorAreaConfig) dict) --
Groups of lava configurations. Default: 0


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

#### num_random_interactable_objects

(int, or [MinMaxInt](#MinMaxInt) dict): The number of random interactable
objects that will be added to each scene. Default: 0

Simple Example:
```
num_random_interactable_objects: null
```

Advanced Example:
```
num_random_interactable_objects:
    min: 1
    max: 10
```

#### passive_scene

(bool): Determine if scene should be considered passive and the
performer agent should be restricted to only use the `"Pass"` action.
If true, ILE will raise an exception if last_step is not set or either
`freezes`, `swivels` or `teleports` has any entries.

#### performer_start_position

([VectorFloatConfig](#VectorFloatConfig) dict, or list of VectorFloatConfig
dicts): The starting position of the performer agent, or a list of
positions, from which one is chosen at random for each scene. The
(optional) `y` is used to position on top of structural objects like
platforms. Default: random within the room

Simple Example:
```
performer_start_position: null
```

Advanced Example:
```
performer_start_position:
    x:
        - -1
        - -0.5
        - 0
        - 0.5
        - 1
    y: 0
    z:
        min: -1
        max: 1
```

#### performer_start_rotation

([VectorIntConfig](#VectorIntConfig) dict, or list of VectorIntConfig
dicts): The starting rotation of the performer agent, or a list of
rotations, from which one is chosen at random for each scene. The
(required) `y` is left/right and (optional) `x` is up/down. Default: random

Simple Example:
```
performer_start_rotation: null
```

Advanced Example:
```
performer_start_rotation:
    x: 0
    y:
        - 0
        - 90
        - 180
        - 270
```

#### placers

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

#### random_structural_objects

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

#### restrict_open_doors

(bool): If there are multiple doors in a scene, only allow for one door to
ever be opened.
Default: False

Simple Example:
```
restrict_open_doors: False
```

Advanced Example:
```
restrict_open_doors: True
```

#### room_dimensions

([VectorIntConfig](#VectorIntConfig) dict, or list of VectorIntConfig
dicts): The total dimensions for the room, or list of dimensions, from
which one is chosen at random for each scene. Rooms are always rectangular
or square. The X and Z must each be within [2, 100] and the Y must be
within [2, 10]. The room's bounds will be [-X/2, X/2] and [-Z/2, Z/2].
Default: random

Simple Example:
```
room_dimensions: null
```

Advanced Example:
```
room_dimensions:
    x: 10
    y:
        - 3
        - 4
        - 5
        - 6
    z:
        min: 5
        max: 10
```

#### room_shape

(string): Shape of the room to restrict the randomzed room dimensions if
`room_dimensions` weren't configured. Options: `rectangle`, `square`.
Default: None

Simple Example:
```
room_shape: null
```

Advanced Example:
```
room_shape: square
```

#### shortcut_bisecting_platform

(bool): Creates a platform bisecting the room.  The performer starts on one
end with a wall in front of them such that the performer is forced to make
a choice on which side they want to drop off and they cannot get back to
the other side.  Default: False

Simple Example:
```
shortcut_bisecting_platform: False
```

Advanced Example:
```
shortcut_bisecting_platform: True
```

#### shortcut_lava_room

(bool): Creates a room with lava on either side of the performer. The
performer will start in the center (non-lava) part.

Simple Example:
```
shortcut_lava_room: False
```

Advanced Example:
```
shortcut_lava_room: True
```

#### shortcut_lava_target_tool

(bool or [LavaTargetToolConfig](#LavaTargetToolConfig)):
Creates a room with a goal object on an island surrounded by lava.
There will also be a block tool to facilitate acquiring the goal object.
One dimension of the room must be 13 or greater.  The other dimension must
be 7 or greater.  By default, the target is a soccer ball with scale
between 1 and 3. The tool is a pushable tool object with a length equal
to the span from the front of the lava over the island to the back of the
lava.  It will have a width of either 0.5, 0.75, 1.0.

Simple Example:
```
shortcut_lava_target_tool: False
```

Advanced Example:
```
shortcut_lava_target_tool:
  island_size:
    min: 1
    max: 3
  front_lava_width: 2
  rear_lava_width: [2, 3]
  guide_rails: [True, False]
```

#### shortcut_ramp_to_platform

(bool): Creates a ramp with a platform connected to it such that a
performer can climb the ramp up to the platform. Will automatically add the
"platform_next_to_ramp" label to the platform and the
"ramp_next_to_platform" label to the ramp.  Default: False

Simple Example:
```
shortcut_ramp_to_platform: False
```

Advanced Example:
```
shortcut_ramp_to_platform: True
```

#### shortcut_start_on_platform

(bool): Ensures that the performer will start on top of a platform. In
order for this to work, `structural_platforms` needs to be specified
using the label `start_structure`.

Default: False

Simple Example:
```
shortcut_start_on_platform: False
```

Advanced Example:
```
shortcut_start_on_platform: True
```

#### shortcut_triple_door_choice

(bool or [TripleDoorConfig](#TripleDoorConfig)):
Creates a platform bisecting the room with a wall with 3 doors
(a.k.a. door occluder, or "door-cluder" or "doorcluder").
The performer starts on one end such that the performer is forced to make
a choice on which door they want to open.  By default, the doors will be
restricted so only one can be opened.  Default: False

Simple Example:
```
shortcut_triple_door_choice: False
```

Advanced Example:
```
shortcut_triple_door_choice:
  start_drop_step:
    min: 2
    max: 5
  add_lips: True
  add_freeze: [True, False]
  restrict_open_doors: True
```

#### specific_interactable_objects

([InteractableObjectConfig](#InteractableObjectConfig) dict, or list of
InteractableObjectConfig dicts): One or more specific objects (with one
or more possible variations) that will be added to each scene.

Simple Example:
```
specific_interactable_objects: null
```

Advanced Example:
```
specific_interactable_objects:
  -
    num: 1
    material: ["WOOD_MATERIALS", "PLASTIC_MATERIALS"]
    scale: 1.2
    shape: "table_2"
    position:
      x: 3
      z: 3
  -
    num:
      min: 10
      max: 30
    material:
      - "WOOD_MATERIALS"
      - "PLASTIC_MATERIALS"
      - "AI2-THOR/Materials/Metals/Brass 1"
    scale:
      min: 0.8
      max: 1.4
    shape:
      - "car_1"
      - "racecar_red"
      - "crayon_blue"
    position:
      x:
        min: -4
        max: 1
      z:
        min: -4
        max: 1
```

#### structural_droppers

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

#### structural_l_occluders

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

#### structural_moving_occluders

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

#### structural_occluding_walls

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

#### structural_platforms

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
    lips:
      front: True
      back: True
      left: False
      right: False
    scale:
      x: 1.1
      y: [0.5, 1]
      z:
        min: 0.3
        max: 1.3
```

#### structural_ramps

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

#### structural_throwers

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

#### structural_walls

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

#### swivels

(list of [StepBeginEnd](#StepBeginEnd) dicts): When a swivel
action should occur.  A swivel forces the performer agent to only
`"['LookDown', 'LookUp', 'RotateLeft', 'RotateRight']"` for a
range of steps.  User should try to avoid swivel (and freeze) overlaps
but if using ranges and choices, the ILE will retry on overlaps.
This field must be blank or an empty array if `passive_scene` is `true`.

Simple Example:
```
swivels: null
```

Advanced Example:
```
swivels:
  -
    begin: 7
    end: 9
  -
    begin: [16, 18, 20]
    end:
      min: 26
      max: 30

```

#### teleports

(list of [TeleportConfig](#TeleportConfig) dicts): When a
kidnap/teleport will occur and where the player agent should be teleported.
This field must contain either both position fields or the `rotation_y`
field or an exception will be thrown.  This field must be blank or an empty
array if `passive_scene` is `true`.

Simple Example:
```
teleports: null
```

Advanced Example:
```
teleports:
  -
    step: 5
    position_x: 3
    position_z: 6
    rotation_y: 45
  -
    step: [34, 36]
    position_x:
      min: -3
      max: 3
    position_z: [3, 5, 7]
  -
    step:
      min: 41
      max: 48
    rotation_y: [30, 120, 270]
```

#### tools

([ToolConfig](#ToolConfig), or list of [ToolConfig](#ToolConfig) dict) --
Groups of large block tool configurations and how many should be generated
from the given options.
Default: 0


Simple Example:
```
tools:
    - num: 0
```

Advanced Example:
```
tools:
    - num:
        min: 1
        max: 3
    - num: 1
      shape: tool_rect_1_00_x_9_00
      position:
        x: [1,2]
        y: 0
        z:
          min: -3
          max: 3
    - num: [1, 3]
      shape:
        - tool_rect_0_50_x_4_00
        - tool_rect_0_75_x_4_00
        - tool_rect_1_00_x_4_00
      position:
        x: [4, 5]
        y: 0
        z:
          min: -5
          max: -4


```

#### wall_back_material

(string, or list of strings): The material for the back wall, or list of
materials, from which one is chosen for each scene. Default: random

Simple Example:
```
wall_back_material: null
```

Advanced Example:
```
wall_back_material: "Custom/Materials/GreyDrywallMCS"
```

#### wall_front_material

(string, or list of strings): The material for the front wall, or list of
materials, from which one is chosen for each scene. Default: random

Simple Example:
```
wall_front_material: null
```

Advanced Example:
```
wall_front_material: "Custom/Materials/GreyDrywallMCS"
```

#### wall_left_material

(string, or list of strings): The material for the left wall, or list of
materials, from which one is chosen for each scene. Default: random

Simple Example:
```
wall_left_material: null
```

Advanced Example:
```
wall_left_material: "Custom/Materials/GreyDrywallMCS"
```

#### wall_right_material

(string, or list of strings): The material for the right wall, or list of
materials, from which one is chosen for each scene. Default: random

Simple Example:
```
wall_right_material: null
```

Advanced Example:
```
wall_right_material: "Custom/Materials/GreyDrywallMCS"
```

