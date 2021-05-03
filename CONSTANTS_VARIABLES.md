# Constants and Variables Overview

For variables with multiple possible options, each option has the same chance of being chosen unless otherwise stated.

## Eval 4

Variables:
- Floor material (color/texture): 20 options
- Wall and ceiling material (color/texture): 46 options

Constants:
- Camera aspect ratio, clipping planes, field of view

### Passive Intuitive Physics

Variables:
- Object type (shape): See https://github.com/NextCenturyCorporation/mcs-scene-generator#intuitive-physics-scenes
- Object size (scale): Between 6 and 10 options per object type, depending on the type
- Object material (color/texture): 22 options per object type
- Object Z position (depth axis): Between 1.6 and 4.4
- Occluder material (color/texture): 12 options for wall piece, 8 options for pole piece

Constants:
- Performer agent starting location: position = (0, -4.5), rotation = 0, height = 1.5
- Occluder Z position (depth axis): 1
- Occluder Y scale: 2 for collision and shape constancy scenes, 3 for object permanence and spatio-temporal continuity scenes
- Occluder Z scale: 0.1
- No context objects in the background (near the back wall)

#### Passive Gravity Support

Variables:
- Object first appearance step: Between 1 and 10
- Supporting object: rectangular prism with 66 size options and 12 material options
- Supporting object X position (left-to-right axis): Between -1.5 and 1.5
- Asymmetric object rotation: 2 options (either facing left or facing right)

Hypercube Slices:
- Target object type (shape): either symmetric or asymmetric
- Target object X position (left-to-right): either directly above the supporting object, or to the side

Constants:
- Scene length: 60 steps
- Number of objects: 1 target, 1 supporting, 1 pole
- Pole materials (colors/textures): always magenta and cyan

#### Passive Shape Constancy

Variables:
- Object first appearance step: Between 81 and 100
- Object X position (left-to-right axis): Between -3 and 3
- Occluder width: Minimum of the corresponding object's width, maximum of 1.4

Hypercube Slices:
- Number of falling objects: either 1 or 2

Constants:
- Scene length: 200 steps
- Number of occluders: 2
- Occluder X position (left-to-right axis): centered on its corresponding object's X position

#### Passive Collisions

Variables:
- Object direction: 2 options (either left-to-right or right-to-left)
- Object first appearance step: Between 81 and 120
- Object X/Z (deep) movement speeds: 20 options
- Object X/Y (toss) movement speeds: 24 options

Hypercube Slices:
- Position of second object: either same depth as moving object, different depth than moving object, or never in scene

Constants:
- Scene length: 200 steps

#### Passive Object Permanence

Variables:
- Object direction: 2 options (either left-to-right or right-to-left)
- Object first appearance step: Between 81 and 160
- Object X movement speeds: 6 options that exit the scene, 18 options that naturally come to a stop in the middle of the scene
- Object X/Z (deep) movement speeds: 20 options, 30 options that naturally come to a stop in the middle of the scene
- Object X/Y (toss) movement speeds: 24 options, 42 options that naturally come to a stop in the middle of the scene
- Occluder width: Minimum of the corresponding object's width, no maximum

Hypercube Slices:
- Movement type: either on X axis only, on both X and Z axes (deep), or on both X and Y axes (toss)
- Movement type: either exits the scene, or naturally comes to a stop in the middle of the scene

Constants:
- Scene length: 240 steps
- Number of moving objects: 1
- Number of occluders: 1
- Occluder X position (left-to-right axis): centered on the X position of the implausible event

#### Passive Spatio-Temporal Continuity

Variables:
- Object direction: 2 options (either left-to-right or right-to-left)
- Object first appearance step: Between 81 and 120
- Object X movement speeds: 6 options
- Object X/Z (deep) movement speeds: 20 options
- Object X/Y (toss) movement speeds: 24 options
- Occluder width: Minimum of the corresponding object's width, maximum of 1.4

Hypercube Slices:
- Movement type: either on X axis only, on both X and Z axes (deep), or on both X and Y axes (toss)

Constants:
- Scene length: 200 steps
- Number of moving objects: 1
- Number of occluders: 2
- Occluder X position (left-to-right axis): centered on the X position of the implausible event

### Interactive

Variables:
- Performer agent starting location: anywhere within the room's bounds of (-5, 5) with random rotation in 45 degree increments
- Context objects: Between 0 and 10, on a bell curve
- Object type (shape): Any object currently available [from our JSON SCHEMA](https://github.com/NextCenturyCorporation/MCS/blob/master/machine_common_sense/scenes/SCHEMA.md#object-list), except as noted in that documentation.
- Object size (scale): Between 1 and 10 options, depending on the object's type
- Object material (color/texture): Between 1 and 40 options, depending on the object's type

Constants:
- Scene length: 10,000 steps
- Target object: `soccer_ball`
- No interiors walls, platforms, or ramps
- No confusors

#### Interactive Containers

Variables:
- Container type (shape): 6 options (does NOT use the cardboard boxes with the four flaps)
- Large container size (scale): Between 2 and 5 options per object type, depending on the type
- Small container size (scale): 2 options per object type
- Container material (color/texture): 16 options per object type
- Container location: anywhere within the room's bounds of (-5, 5) with random rotation in 45 degree increments

Hypercube Slices:
- Is the target object positioned inside a container: either yes or no
- Number of container objects large enough to hold the target: Between 1 and 3
- Number of container objects too small to hold the target: Between 0 and 2

Constants:
- All containers start closed
- No obstacles
- No occluders

#### Interactive Obstacles

Variables:
- Obstacle type (shape): 27 options, like tables and chairs

Hypercube Slices:
- Target location: either in front of the performer agent (within its starting camera view based on its starting rotation) or in back of the performer agent (not in its starting camera view)
- Obstacle location: either between the performer agent and the target, or behind the target

Constants:
- 1 obstacle
- No containers
- No occluders

#### Interactive Occluders

Variables:
- Occluder type (shape): 19 options, like sofas and bookcases

Hypercube Slices:
- Target location: either in front of the performer agent (within its starting camera view based on its starting rotation) or in back of the performer agent (not in its starting camera view)
- Primary occluder location: either between the performer agent and the target, or behind the target
- Number of occluder objects: Between 1 and 3 (but always includes the "primary" occluder)

Constants:
- No containers
- No obstacles
