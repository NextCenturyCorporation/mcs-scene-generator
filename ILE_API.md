# ILE API

[How to Run the ILE](./README.md#ile-scene-generator)

#### Table of Content:
- [Classes](#Classes)
- [Options](#Options)

#### Example Configuration Files:
- [Simple](./ile_config.yaml)
- [Advanced](./ile_config_advanced.yaml)

#### Noteworthy Configuration Options:
- The [goal](#goal) option, if you want to set a goal for your scenes,
like "find and pickup the soccer ball" (by default, there is no goal: the
scenes can be used for undirected exploration).
- The [last_step](#last_step) option, if you want to force your scenes to end
after a specific number of actions/steps.

## Classes

Some [configurable ILE options](#Options) use the following classes
(represented as dicts in the YAML):

#### GoalConfig

A dict with str `category` and optional `target`, `target_1`, and
`target_2` properties that represents the goal and target object(s) in each
scene. The `target*` properties are only needed if required for the
specific category of goal. Each `target*` property is either an
InteractableObjectConfig dict or list of InteractableObjectConfig dicts.
For each list, one dict will be randomly chosen within the list in each
new scene.

Example:
```
category: retrieval
target:
    shape: soccer_ball
```

#### InteractableObjectConfig

Represents the template for a specific object (with one or more possible
variations) that will be added to each scene. Each template can have the
following optional properties:
- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict): The number
of objects with this template to generate in each scene. For a list or a
MinMaxInt, a new number will be randomly chosen for each scene.
Default: `1`
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
- `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts, or [VectorFloatConfig](#VectorFloatConfig)
dict, or list of VectorFloatConfig dicts): The scale of this object in each
scene. A single float will be used as the scale for all object dimensions
(X/Y/Z). For a list or a MinMaxFloat, a new scale will be randomly chosen
for each scene. Default: `1`
- `shape` (string, or list of strings): The shape (object type) of this
object in each scene. For a list, a new shape will be randomly chosen for
each scene. Default: random
- `keyword_location`: ([KeywordLocationConfig](#KeywordLocationConfig)):
Used to identify one of the qualitative locations specified by keywords.
This field should not be set when `position` or `rotation` are also set.
- `label` (string, or list of strings): labels to associate with this
object.  Components can use this label to reference this object or a group
of objects.  Labels do not need to be unique and when objects share a
labels, components have options to randomly choose one or choose all.  See
specific label options for details.

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
```

#### KeywordLocationConfig

Describes an object's keyword location. Can have the following
properties:
- `keyword` (string, or list of strings): The keyword location, which can
be one of the following:
    - `front` - The object will be placed in a line in front of the
    performer's start position.
    - `back` - The object will be placed in the 180 degree arc behind the
    performer's start position.
    - `between` - The object will be placed between the performer's start
    position and another object.  The other object must be referenced by
    the 'relative_object_label' field.  If multiple objects have this
    label, one will be randomly chosen.
    - `adjacent` - The object will be placed next to another object.  The
    other object must be referenced by the 'relative_object_label' field.
    If multiple objects have this label, one will be randomly chosen.
    - `in` - The object will be placed inside a container.  The container
    must be referenced by the 'container_label' field.  If multiple objects
    have this label, one will be randomly chosen.
    - `in_with` - The object will be placed inside a container along with
    another object.  The container must be referenced by the
    'container_label' field.  The other object must be referenced by the
    'relative_object_label'
    field.  If multiple objects have these label, one will be randomly
    chosen for each field.
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
- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): The number of this object the user wants to create.
- `keyword_location`: ([KeywordLocationConfig](#KeywordLocationConfig)):
One of the keyword locations for this object or set of objects. Any choices
in `keyword_location` are made for each object inside the group, not the
group as a whole.

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
    - `l_occluders`: Random L-shaped occluders
    - `platforms`: Random platforms
    - `ramps`: Random ramps
    - `walls` Random interior room walls
Default: All types
- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt)): The number of
structural objects that should be generated in this group.  Each object is
one of the type choices.

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

#### StructuralLOccluderConfig

Defines details of a structural L-shaped occluder.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of structures to be created with these parameters
- `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
VectorFloatConfig dicts): The structure's position in the scene
- `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
- `material` (string, or list of strings): The structure's material or
material type.
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

#### StructuralPlatformConfig

Defines details of a structural platform.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of structures to be created with these parameters
- `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
VectorFloatConfig dicts): The structure's position in the scene
- `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
- `material` (string, or list of strings): The structure's material or
material type.
- `scale` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts): Scale of the platform

#### StructuralRampConfig

Defines details of a structural ramp.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of structures to be created with these parameters
- `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
VectorFloatConfig dicts): The structure's position in the scene
- `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
- `material` (string, or list of strings): The structure's material or
material type.
- `angle` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts): Angle of the ramp upward from the floor
- `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts): Width of the ramp
- `length` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts): Length of the ramp

#### StructuralWallConfig

Defines details of a structural interior wall.

- `num` (int, or list of ints, or [MinMaxInt](#MinMaxInt) dict, or list of
MinMaxInt dicts): Number of structures to be created with these parameters
- `position` ([VectorFloatConfig](#VectorFloatConfig) dict, or list of
VectorFloatConfig dicts): The structure's position in the scene
- `rotation_y` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat)
dict, or list of MinMaxFloat dicts): The structure's rotation in the scene
- `material` (string, or list of strings): The structure's material or
material type.
- `width` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts): The width of the wall.
- `height` (float, or list of floats, or [MinMaxFloat](#MinMaxFloat) dict,
or list of MinMaxFloat dicts): The height of the wall.

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

#### floor_physics

(dict with bool `enable`, float `angularDrag`, float `bounciness`, float
`drag`, float `dynamicFriction`, and float `staticFriction` keys, or list
of dicts): The friction, drag, and bounciness to set for the whole floor,
or a list of settings, from which one is chosen at random for each scene.
Must set `enable` to `true`; all other values must be within [0, 1].
Default: see example

Simple Example:
```
floor_physics: null
```

Advanced Example:
```
floor_physics:
    enable: false
    angularDrag: 0.5
    bounciness: 0
    drag: 0
    dynamicFriction: 0.6
    staticFriction: 0.6
```

#### freezes

(list of [StepBeginEnd](#StepBeginEnd) dicts): When a freeze
should occur.  A freeze forces the performer agent to only `"Pass"` for a
range of steps.  User should try to avoid freeze overlaps, but if using
ranges and choices, the ILE will retry on overlaps.  This field must be
blank or an empty array if `passive_scene` is `true`.

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
  - containers: keywords_container
  - containers_can_contain_target:
      keywords_container, keywords_container_can_contain_target
  - containers_cannot_contain_target:
      keywords_container, keywords_container_cannot_contain_target
  - obstacles: keywords_obstacles
  - occluders: keywords_occluders
  - context: keywords_context

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
`freezes` or `teleports` has any entries.

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

#### random_structural_objects

([RandomStructuralObjectConfig](#RandomStructuralObjectConfig), or list of
[RandomStructuralObjectConfig](#RandomStructuralObjectConfig) dict) --
Groups of random object types and how many should be generated from the
type options.
Default: 2 to 4 of all types
```
random_structural_objects:
  - type: ['walls','platforms','ramps','l_occluders']
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
  - type: ['walls','platforms','ramps','l_occluders']
    num:
        min: 0
        max: 2
  - type: ['walls','l_occluders']
    num: [3, 5, 7]
  - type: 'walls'
    num: 2
```

#### room_dimensions

([VectorIntConfig](#VectorIntConfig) dict, or list of VectorIntConfig
dicts): The total dimensions for the room, or list of dimensions, from
which one is chosen at random for each scene. Rooms are always rectangular
or square. The X and Z must each be within [2, 15] and the Y must be within
[2, 10]. The room's bounds will be [-X/2, X/2] and [-Z/2, Z/2].
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

#### teleports

(list of [TeleportConfig](#TeleportConfig) dicts): When a
kidnap/teleport will occur and where the player agent should be teleported.
This field must contain either both position fields or the `rotation_y`
field or an exception will be thrown.  This field must be blank or an empty
array if `passive_scene` is `true`.

Simple Example:
```
passive_scene: false
freezes: null
teleports: null
```

Advanced Example:
```
passive_scene: false
freezes:
  -
    begin: 1
    end: 3
  -
    begin: [11, 13 ,15]
    end:
      min: 16
      max: 26

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

