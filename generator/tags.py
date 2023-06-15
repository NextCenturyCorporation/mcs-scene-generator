import re
from types import SimpleNamespace
from typing import Any, Dict, List

from .objects import SceneObject

ALL = 'all'
ANY = 'any'

GOAL_DICT = {
    'RETRIEVAL': 'retrieval',
    'MULTI_RETRIEVAL': 'multi retrieval',
    'IMITATION': 'imitation',
    # Deprecated
    'TRAVERSAL': 'traversal',
    'TRANSFERRAL': 'transferral'
}

ROLE_DICT = {
    'AGENT': 'agent',
    'BLOB': 'blob',
    'COLLIDER': 'collider',
    'CONFUSOR': 'confusor',
    'CONTAINER': 'container',
    'CONTEXT': 'context',
    'HOME': 'home',
    'KEY': 'key',
    'INTUITIVE_PHYSICS_OCCLUDER': 'intuitive physics occluder',
    'LID': 'lid',
    'NON_TARGET': 'non target',
    'OBSTACLE': 'obstacle',
    'OCCLUDER': 'occluder',
    'PADDLE': 'paddle',
    'STATIC_OBJECT': 'static object',
    'STRUCTURAL': 'structural',
    'TARGET': 'target',
    'TOOL': 'tool',
    'WALL': 'wall',
    'GUIDERAILS': 'guiderail'
}

SCENE_BOOL_TAGS_DICT = {
    'INTERACTIVE': 'interactive',
    'PASSIVE': 'passive'
}

SCENE_OPTIONAL_TAGS_DICT = {
    # Multiple hypercubes
    'AGENT_SKINTONE': 'skintone',
    'AMBIGUOUS': 'ambiguous',
    'ANGLE': 'angle',
    'CORNER': 'corner',
    'CORRECT_DOOR': 'correctDoor',
    'DIRECTION': 'direction',
    'FALL_DOWN': 'fallDown',
    'MOVE_ACROSS': 'moveAcross',
    'NUM_FLOOR_FEATURES': 'numFloorFeatures',
    'PATH_RATIO': 'pathRatio',
    'ROTATION': 'rotation',
    'SETUP': 'sceneSetup',
    'TARGET_SIDE': 'targetSide',
    'TIPSY': 'tipsy',
    # Arithmetic, Number Comparison
    'REFERENCE_SIDE': 'referenceSide',
    # Imitation
    'CONTAINERS_SIDE': 'containersSide',
    'CONTAINERS_KIDNAP_ROTATION': 'containersKidnapRotation',
    'CONTAINER_TRIGGER_ORDER_SIDES': 'containerTriggerOrderSides',
    # Seeing Leads to Knowing
    'AGENT_FACING_DIRECTION': 'agentFacingDirection',
    'TARGET_BIN_GLOBAL_LOCATION': 'targetBinGlobalLocation',
    # Set Rotation
    'TURNTABLE_CONTAINER_TARGET_SIDE': 'turntableContainerTargetSide',
    # Shell Game
    'SHELL_GAME_MOVEMENT_DIRECTION': 'shellGameMovementDirection',
    'SHELL_GAME_CONTAINER_PICKED': 'shellGameContainerPicked',
    # Solidity
    'EXTENSION_SIDE': 'extensionSide',
    # Spatial Reorientation
    'STABLE_LANDMARK': 'stableLandmarkWall',
    'UNSTABLE_LANDMARK_SIDE': 'unstableLandmarkStartingSide',
    'UNSTABLE_LANDMARK_TYPE': 'unstableLandmarkType'
}

SCENE_ROLE_TAGS_DICT = {
    'COUNT': 'count',
    'PRESENT': 'present',

    'TRAINED': 'trained',
    'TRAINED_CATEGORY': 'trainedCategory',
    'TRAINED_COLOR': 'trainedColor',
    'TRAINED_COMBINATION': 'trainedCombination',
    'TRAINED_SHAPE': 'trainedShape',
    'TRAINED_SIZE': 'trainedSize',

    'UNTRAINED': 'untrained',
    'UNTRAINED_CATEGORY': 'untrainedCategory',
    'UNTRAINED_COLOR': 'untrainedColor',
    'UNTRAINED_COMBINATION': 'untrainedCombination',
    'UNTRAINED_SHAPE': 'untrainedShape',
    'UNTRAINED_SIZE': 'untrainedSize',

    'CONTAINED': 'contained',
    'UNCONTAINED': 'uncontained'
}

# Properties of objectsInfo
OBJECTS = SimpleNamespace(
    ALL='all',
    **ROLE_DICT
)

# Possible object roles
ROLES = SimpleNamespace(
    **ROLE_DICT
)

# Properties of sceneInfo
SCENE = SimpleNamespace(
    PRIMARY='primaryType',
    SECONDARY='secondaryType',
    TERTIARY='tertiaryType',
    QUATERNARY='quaternaryType',
    DOMAIN_TYPE='domainType',

    ID='id',
    NAME='name',
    HYPERCUBE_ID='hypercubeId',
    SLICES='slices',

    ACTION_NONE='action none',
    ACTION_VARIABLE='action variable',
    ACTION_FULL='action full',

    INTERACTIVE_AGENTS='interactive agents',
    INTERACTIVE_OBJECTS='interactive objects',
    INTERACTIVE_PLACES='interactive places',
    PASSIVE_AGENTS='passive agents',
    PASSIVE_OBJECT='passive objects',

    INTUITIVE_PHYSICS='intuitive physics',
    COLLISIONS='collisions',
    GRAVITY_SUPPORT='gravity support',
    OBJECT_PERMANENCE='object permanence',
    SHAPE_CONSTANCY='shape constancy',
    SPATIO_TEMPORAL_CONTINUITY='spatio temporal continuity',

    AGENT_IDENTIFICATION='agent identification',
    ARITHMETIC='arithmetic',
    CONTAINER='container',
    HOLES='holes',
    IMITATION_TASK='imitation task',
    INTERACTIVE_COLLISION='interactive collision',
    INTERACTIVE_OBJECT_PERMANENCE='interactive object permanence',
    LAVA='lava',
    MOVING_TARGET_PREDICTION='moving target prediction',
    NUMBER_COMPARISON='number comparison',
    OCCLUDER='occluder',
    OBSTACLE='obstacle',
    RAMP='ramp',
    REFERENCE='spatial reference',
    REORIENTATION='spatial reorientation',
    SEEING_LEADS_TO_KNOWING='seeing leads to knowing',
    SET_ROTATION='set rotation',
    SHELL_GAME='shell game',
    SOCIAL_REFERENCING='social referencing',
    SOLIDITY='solidity',
    SPATIAL_ELIMINATION='spatial elimination',
    SUPPORT_RELATIONS='support relations',
    TRAJECTORY='trajectory',
    TOOL_USE='tool use',

    # For passive agent tasks:
    AGENTS='agents',

    **SCENE_BOOL_TAGS_DICT,
    **SCENE_OPTIONAL_TAGS_DICT,
    **SCENE_ROLE_TAGS_DICT,
    **GOAL_DICT
)

# Types of hypercubes
TYPES = SimpleNamespace(
    COLLISIONS_MOVES='objectMovesOffScreen',
    COLLISIONS_OCCLUDERS='occluders',
    COLLISIONS_REVEALS='occluderReveals',
    COLLISIONS_TRAINED='objectsTrained',

    GRAVITY_SUPPORT_PLAUSIBLE='plausible',
    GRAVITY_SUPPORT_TARGET_POSITION='targetPosition',
    GRAVITY_SUPPORT_TARGET_TYPE='targetType',

    OBJECT_PERMANENCE_SETUP='setup',
    OBJECT_PERMANENCE_MOVEMENT='movement',
    OBJECT_PERMANENCE_OBJECT_ONE='objectOne',
    OBJECT_PERMANENCE_OBJECT_TWO='objectTwo',
    OBJECT_PERMANENCE_NOVELTY_ONE='objectOneNovelty',
    OBJECT_PERMANENCE_NOVELTY_TWO='objectTwoNovelty',

    SHAPE_CONSTANCY_OBJECT_ONE='objectOne',
    SHAPE_CONSTANCY_OBJECT_TWO='objectTwo',
    SHAPE_CONSTANCY_TRAINED_ONE='objectOneBeginsTrained',
    SHAPE_CONSTANCY_TRAINED_TWO='objectTwoBeginsTrained',

    SPATIO_TEMPORAL_CONTINUITY_MOVEMENT='movement',
    SPATIO_TEMPORAL_CONTINUITY_OBJECTS='objects',
    SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS='occluders',
    SPATIO_TEMPORAL_CONTINUITY_PLAUSIBLE='plausible',
    SPATIO_TEMPORAL_CONTINUITY_TARGET_TRAINED='targetTrained',
    SPATIO_TEMPORAL_CONTINUITY_NON_TARGET_TRAINED='nonTargetTrained',

    INTERACTIVE_CONTAINERS_LARGE='largeContainers',
    INTERACTIVE_CONTAINERS_SMALL='smallContainers',
    INTERACTIVE_CONTAINERS_TRAINED='containersTrained',
    INTERACTIVE_OBSTACLE_BETWEEN='obstacleBetween',
    INTERACTIVE_OBSTACLE_TRAINED='obstacleTrained',
    INTERACTIVE_OCCLUDERS='occluders',
    INTERACTIVE_OCCLUDERS_TRAINED='occludersTrained',
    INTERACTIVE_TARGET_BEHIND='targetBehind',
    INTERACTIVE_TARGET_HIDDEN='targetHidden',
    INTERACTIVE_TARGET_INSIDE='targetInside',

    AGENT_BACKGROUND_AGENT_ONE_GOAL='agents agent one goal',
    AGENT_BACKGROUND_AGENT_PREFERENCE='agents agent preference',
    AGENT_BACKGROUND_COLLECT='agents collect',
    AGENT_BACKGROUND_INSTRUMENTAL_ACTION='agents instrumental action',
    AGENT_BACKGROUND_INSTRUMENTAL_APPROACH='agents instrumental approach',
    AGENT_BACKGROUND_INSTRUMENTAL_IMITATION='agents instrumental imitation',
    AGENT_BACKGROUND_MULTIPLE_AGENTS='agents multiple agents',
    AGENT_BACKGROUND_NON_AGENT_ONE_GOAL='agents nonagent one goal',
    AGENT_BACKGROUND_NON_AGENT_PREFERENCE='agents nonagent preference',
    AGENT_BACKGROUND_OBJECT_PREFERENCE='agents object preference',
    AGENT_BACKGROUND_SINGLE_OBJECT='agents single object',
    AGENT_BACKGROUND_SOCIAL_APPROACH='agents social approach',
    AGENT_BACKGROUND_SOCIAL_IMITATION='agents social imitation',

    AGENT_EVALUATION_AGENT_NON_AGENT='agents agent nonagent',
    AGENT_EVALUATION_APPROACH='agents approach',
    AGENT_EVALUATION_EFFICIENT_IRRATIONAL='agents efficient action irrational',
    AGENT_EVALUATION_EFFICIENT_PATH='agents efficient action path lure',
    AGENT_EVALUATION_EFFICIENT_TIME='agents efficient action time control',
    AGENT_EVALUATION_IMITATION='agents imitation',
    AGENT_EVALUATION_INACCESSIBLE_GOAL='agents inaccessible goal',
    AGENT_EVALUATION_INSTRUMENTAL_BLOCKING_BARRIERS='agents instrumental action blocking barriers',  # noqa: E501
    AGENT_EVALUATION_INSTRUMENTAL_INCONSEQUENTIAL_BARRIERS='agents instrumental action inconsequential barriers',  # noqa: E501
    AGENT_EVALUATION_INSTRUMENTAL_NO_BARRIERS='agents instrumental action no barriers',  # noqa: E501
    AGENT_EVALUATION_MULTIPLE_AGENTS='agents multiple agents',
    AGENT_EVALUATION_OBJECT_PREFERENCE='agents object preference',

    AGENT_EXAMPLE='agents examples'
)


CELLS = SimpleNamespace(
    AGENT_SKINTONE=SimpleNamespace(
        LIGHT='light',
        MEDIUM='medium',
        DARK='dark'
    ),

    COLLISIONS_MOVES=SimpleNamespace(
        ONE='first object',
        TWO='second object'
    ),
    COLLISIONS_OCCLUDERS=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    COLLISIONS_REVEALS=SimpleNamespace(
        EMPTY='empty scene',
        ON_PATH='second object on path',
        BEHIND_PATH='second object behind path'
    ),
    COLLISIONS_TRAINED=SimpleNamespace(
        YES='yes',
        NO='no'
    ),

    GRAVITY_SUPPORT_PLAUSIBLE=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    GRAVITY_SUPPORT_TARGET_POSITION=SimpleNamespace(
        FULL='full support',
        TWENTY_FIVE='twenty five percent support',
        FORTY_NINE='forty nine percent support',
        SEVENTY_FIVE='seventy five percent support',
        MINIMAL='minimal support',
        NONE='no support'
    ),
    GRAVITY_SUPPORT_TARGET_TYPE=SimpleNamespace(
        ASYMMETRIC='asymmetric',
        SYMMETRIC='symmetric'
    ),

    OBJECT_PERMANENCE_SETUP=SimpleNamespace(
        EXIT='move across whole scene',
        STOP='stop behind an occluder',
        FALLS='falls behind an occluder'
    ),
    OBJECT_PERMANENCE_MOVEMENT=SimpleNamespace(
        LINEAR='linear movement constant depth',
        LINEAR_IN_DEPTH='linear movement in depth',
        TOSSED='tossed movement'
    ),
    OBJECT_PERMANENCE_OBJECT_ONE=SimpleNamespace(
        NO_CHANGE='no change',
        APPEAR='appears',
        DISAPPEAR='disappears'
    ),
    OBJECT_PERMANENCE_OBJECT_TWO=SimpleNamespace(
        NONE='none',
        NO_CHANGE='no change',
        APPEAR='appears',
        DISAPPEAR='disappears'
    ),
    OBJECT_PERMANENCE_NOVELTY_ONE=SimpleNamespace(
        NONE='none',
        SHAPE='untrained shape',
        SIZE='untrained size'
    ),
    OBJECT_PERMANENCE_NOVELTY_TWO=SimpleNamespace(
        NONE='none',
        SHAPE='untrained shape',
        SIZE='untrained size'
    ),

    SHAPE_CONSTANCY_OBJECT_ONE=SimpleNamespace(
        NO_CHANGE='no change',
        TRAINED_SHAPE='change into trained shape',
        UNTRAINED_SHAPE='change into untrained shape'
    ),
    SHAPE_CONSTANCY_OBJECT_TWO=SimpleNamespace(
        NONE='none',
        NO_CHANGE='no change',
        TRAINED_SHAPE='change into trained shape',
        UNTRAINED_SHAPE='change into untrained shape'
    ),
    SHAPE_CONSTANCY_TRAINED_ONE=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    SHAPE_CONSTANCY_TRAINED_TWO=SimpleNamespace(
        YES='yes',
        NO='no'
    ),

    SPATIO_TEMPORAL_CONTINUITY_MOVEMENT=SimpleNamespace(
        LINEAR='linear movement constant depth',
        LINEAR_IN_DEPTH='linear movement in depth',
        TOSSED='tossed movement'
    ),
    SPATIO_TEMPORAL_CONTINUITY_OBJECTS=SimpleNamespace(
        ZERO=0,
        ONE=1,
        TWO=2
    ),
    SPATIO_TEMPORAL_CONTINUITY_OCCLUDERS=SimpleNamespace(
        ZERO=0,
        TWO=2,
        THREE=3
    ),
    SPATIO_TEMPORAL_CONTINUITY_PLAUSIBLE=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    SPATIO_TEMPORAL_CONTINUITY_TARGET_TRAINED=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    SPATIO_TEMPORAL_CONTINUITY_NON_TARGET_TRAINED=SimpleNamespace(
        YES='yes',
        NO='no'
    ),

    INTERACTIVE_CONTAINERS_LARGE=SimpleNamespace(
        ONE=1,
        TWO=2,
        THREE=3
    ),
    INTERACTIVE_CONTAINERS_SMALL=SimpleNamespace(
        ZERO=0,
        ONE=1,
        TWO=2
    ),
    INTERACTIVE_CONTAINERS_TRAINED=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    INTERACTIVE_OBSTACLE_BETWEEN=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    INTERACTIVE_OBSTACLE_TRAINED=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    INTERACTIVE_OCCLUDERS=SimpleNamespace(
        ONE=1,
        TWO=2,
        THREE=3
    ),
    INTERACTIVE_OCCLUDERS_TRAINED=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    INTERACTIVE_TARGET_BEHIND=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    INTERACTIVE_TARGET_HIDDEN=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    INTERACTIVE_TARGET_INSIDE=SimpleNamespace(
        YES='yes',
        NO='no'
    ),
    REFERENCE_SIDE=SimpleNamespace(
        LEFT='left',
        RIGHT='right'
    ),

    TURNTABLE_CONTAINER_TARGET_SIDE=SimpleNamespace(
        LEFT='left',
        MIDDLE='middle',
        RIGHT='right'
    ),
    ROTATION=SimpleNamespace(
        CLOCKWISE='clockwise',
        COUNTER_CLOCKWISE='counterClockwise'
    ),
    SIDE=SimpleNamespace(
        LEFT='left',
        RIGHT='right',
        EITHER='either'
    ),

    CONTAINERS_SIDE=SimpleNamespace(
        LEFT='left',
        RIGHT='right'
    ),
    CONTAINERS_KIDNAP_ROTATION=SimpleNamespace(
        FORTY_FIVE=45,
        NINETY=90,
        ONE_THIRTY_FIVE=135,
        TWO_TWENTY_FIVE=225,
        TWO_SEVENTY=270,
        THREE_FIFTEEN=315
    ),
    SHELL_GAME_MOVEMENT_DIRECTION=SimpleNamespace(
        LEFT='left',
        RIGHT='right'
    ),
    SHELL_GAME_CONTAINER_PICKED=SimpleNamespace(
        LEFT='left',
        MIDDLE='middle',
        RIGHT='right'
    ),
    TARGET_BIN_GLOBAL_LOCATION=SimpleNamespace(
        FRONT_RIGHT='front_right',
        BACK_RIGHT='back_right',
        BACK_LEFT='back_left',
        FRONT_LEFT='front_left'
    ),
    AGENT_FACING_DIRECTION=SimpleNamespace(
        LEFT='left',
        RIGHT='right',
    )
)

# MCS core domains
DOMAINS = SimpleNamespace(
    OBJECTS='objects',
    PLACES='places',
    AGENTS='agents',
)

# Interactive scene hypercube object locations
LOCATIONS = SimpleNamespace(
    BACK='in back of performer start',
    CLOSE='very close to target',
    FAR='far away from target',
    FRONT='in front of performer start',
    RANDOM='random'
)


ABBREV = SimpleNamespace(
    COLLISIONS='coll',
    GRAVITY_SUPPORT='grav',
    OBJECT_PERMANENCE='objp',
    SHAPE_CONSTANCY='shap',
    SPATIO_TEMPORAL_CONTINUITY='stc',

    AGENT_IDENTIFICATION='agident',
    ARITHMETIC='arith',
    HOLES='holes',
    IMITATION_TASK='imit',
    INTERACTIVE_COLLISION='intcoll',
    INTERACTIVE_CONTAINER='intcon',
    INTERACTIVE_OBJECT_PERMANENCE='intobjp',
    INTERACTIVE_OBSTACLE='intobs',
    INTERACTIVE_OCCLUDER='intocc',
    LAVA='lava',
    MOVING_TARGET_PREDICTION='movtar',
    NUMBER_COMPARISON='numcomp',
    RAMP='ramp',
    REFERENCE='ref',
    REORIENTATION='reor',
    SEEING_LEADS_TO_KNOWING='seeknow',
    SET_ROTATION='setrot',
    SHELL_GAME='shell',
    SOLIDITY='solidity',
    SPATIAL_ELIMINATION='spateli',
    SUPPORT_RELATIONS='suprel',
    TRAJECTORY='traj',
    TOOL_USE='tool',
)


def append_object_tags(
    scene_info: Dict[str, Any],
    objects_info: Dict[str, Any],
    role_to_object_list: Dict[str, List[SceneObject]]
) -> None:
    """Appends object-specific tags from the given role_to_object_list onto
    the given scene_info and objects_info collections."""

    # Ignore all interior walls and intuitive physics occluders.
    ignore_role_list = [
        ROLES.INTUITIVE_PHYSICS_OCCLUDER, ROLES.STRUCTURAL, ROLES.WALL
    ]

    for role in ROLE_DICT.values():
        if (role not in ignore_role_list) and (role in role_to_object_list):
            append_object_tags_of_type(scene_info, objects_info,
                                       role_to_object_list, role)


def append_object_tags_of_type(
    scene_info: Dict[str, Any],
    objects_info: Dict[str, Any],
    role_to_object_list: Dict[str, List[SceneObject]],
    role: str
) -> None:
    """Appends object-specific tags from the object_list in the given
    role_to_object_list collection with the given role onto the given
    scene_info and objects_info collections."""

    familiar_novel_tuples = [
        (SCENE.TRAINED_CATEGORY, SCENE.UNTRAINED_CATEGORY),
        (SCENE.TRAINED_COLOR, SCENE.UNTRAINED_COLOR),
        (SCENE.TRAINED_SHAPE, SCENE.UNTRAINED_SHAPE),
        (SCENE.TRAINED_SIZE, SCENE.UNTRAINED_SIZE),
        (SCENE.TRAINED_COMBINATION, SCENE.UNTRAINED_COMBINATION)
    ]

    for instance in role_to_object_list[role]:
        if instance.get('locationParent', None):
            scene_info[SCENE.CONTAINED][role_to_key(role)] = True
            objects_info[role_to_key(role)].append(tag_to_label(
                SCENE.CONTAINED
            ))
        else:
            scene_info[SCENE.UNCONTAINED][role_to_key(role)] = True
            objects_info[role_to_key(role)].append(tag_to_label(
                SCENE.UNCONTAINED
            ))

        for familiar_novel in familiar_novel_tuples:
            append_familiarity_object_tags(
                scene_info,
                objects_info,
                instance,
                role,
                familiar_novel[0],
                familiar_novel[1]
            )


def append_familiarity_object_tags(
    scene_info: Dict[str, Any],
    objects_info: Dict[str, Any],
    instance: SceneObject,
    role: str,
    trained_tag: str,
    untrained_tag: str
) -> None:
    """Appends 'trained' or 'untrained' tags of the given type for the given
    instance with the given role onto the given scene_info and objects_info
    collections."""

    if instance['debug'].get(untrained_tag, False):
        scene_info[SCENE.UNTRAINED][ANY] = True
        scene_info[SCENE.UNTRAINED][role_to_key(role)] = True
        scene_info[untrained_tag][ANY] = True
        scene_info[untrained_tag][role_to_key(role)] = True
        objects_info[role_to_key(role)].append(tag_to_label(untrained_tag))
    else:
        scene_info[SCENE.TRAINED][ANY] = True
        scene_info[SCENE.TRAINED][role_to_key(role)] = True
        scene_info[trained_tag][ANY] = True
        scene_info[trained_tag][role_to_key(role)] = True
        objects_info[role_to_key(role)].append(tag_to_label(trained_tag))


def role_to_key(role: str) -> str:
    """Return the dict key string (no whitespace) for the given object role."""
    return role.replace(' ', '_')


def role_to_tag(role: str) -> str:
    """Return the isRole object bool tag for the given object role."""
    return 'is' + role.title().replace(' ', '')


def tag_to_label(tag: str) -> str:
    """Return the spaced and lowercased label for the given camelCase tag."""
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', tag).lower()


def get_domain_type(task: str) -> str:
    if (is_interactive_agents_task(task)):
        return SCENE.INTERACTIVE_AGENTS
    if (is_interactive_objects_task(task)):
        return SCENE.INTERACTIVE_OBJECTS
    if (is_interactive_places_task(task)):
        return SCENE.INTERACTIVE_PLACES
    if (is_passive_agent_task(task)):
        return SCENE.PASSIVE_AGENTS
    if (is_passive_physics_task(task)):
        return SCENE.PASSIVE_OBJECT


def is_passive_agent_task(task: str) -> bool:
    """Returns whether the given task is a passive agent task."""
    return task in [
        TYPES.AGENT_BACKGROUND_AGENT_ONE_GOAL,
        TYPES.AGENT_BACKGROUND_AGENT_PREFERENCE,
        TYPES.AGENT_BACKGROUND_COLLECT,
        TYPES.AGENT_BACKGROUND_INSTRUMENTAL_ACTION,
        TYPES.AGENT_BACKGROUND_INSTRUMENTAL_APPROACH,
        TYPES.AGENT_BACKGROUND_INSTRUMENTAL_IMITATION,
        TYPES.AGENT_BACKGROUND_MULTIPLE_AGENTS,
        TYPES.AGENT_BACKGROUND_NON_AGENT_ONE_GOAL,
        TYPES.AGENT_BACKGROUND_NON_AGENT_PREFERENCE,
        TYPES.AGENT_BACKGROUND_OBJECT_PREFERENCE,
        TYPES.AGENT_BACKGROUND_SINGLE_OBJECT,
        TYPES.AGENT_BACKGROUND_SOCIAL_APPROACH,
        TYPES.AGENT_BACKGROUND_SOCIAL_IMITATION,
        TYPES.AGENT_EVALUATION_AGENT_NON_AGENT,
        TYPES.AGENT_EVALUATION_APPROACH,
        TYPES.AGENT_EVALUATION_EFFICIENT_IRRATIONAL,
        TYPES.AGENT_EVALUATION_EFFICIENT_PATH,
        TYPES.AGENT_EVALUATION_EFFICIENT_TIME,
        TYPES.AGENT_EVALUATION_IMITATION,
        TYPES.AGENT_EVALUATION_INACCESSIBLE_GOAL,
        TYPES.AGENT_EVALUATION_INSTRUMENTAL_BLOCKING_BARRIERS,
        TYPES.AGENT_EVALUATION_INSTRUMENTAL_INCONSEQUENTIAL_BARRIERS,
        TYPES.AGENT_EVALUATION_INSTRUMENTAL_NO_BARRIERS,
        TYPES.AGENT_EVALUATION_MULTIPLE_AGENTS,
        TYPES.AGENT_EVALUATION_OBJECT_PREFERENCE,
        TYPES.AGENT_EXAMPLE,
        # While the Seeing Leads to Knowing hypercube will set its secondary
        # type and goal category as "passive" (not "agents"), to differentiate
        # it from the NYU passive agent tasks, its domain type should always
        # be "passive agents", so keep it in this list.
        SCENE.SEEING_LEADS_TO_KNOWING
    ]


def is_passive_physics_task(task: str) -> bool:
    """Returns whether the given task is a passive physics task."""
    return task in [
        SCENE.COLLISIONS,
        SCENE.GRAVITY_SUPPORT,
        SCENE.OBJECT_PERMANENCE,
        SCENE.SEEING_LEADS_TO_KNOWING,
        SCENE.SHAPE_CONSTANCY,
        SCENE.SPATIO_TEMPORAL_CONTINUITY
    ]


def is_multi_retrieval(task: str) -> bool:
    """Returns whether the given task is a multi-retrieval task."""
    return task in [
        SCENE.ARITHMETIC,
        SCENE.NUMBER_COMPARISON
    ]


def is_interactive_places_task(task: str) -> bool:
    """Returns whether the given task is a interactive places task."""
    return task in [
        SCENE.CONTAINER,
        SCENE.HOLES,
        SCENE.LAVA,
        SCENE.OCCLUDER,
        SCENE.OBSTACLE,
        SCENE.RAMP,
        SCENE.REORIENTATION,
        SCENE.SET_ROTATION,
        SCENE.SHELL_GAME,
        SCENE.SPATIAL_ELIMINATION
    ]


def is_interactive_agents_task(task: str) -> bool:
    """Returns whether the given task is a interactive agents task."""
    return task in [
        SCENE.AGENT_IDENTIFICATION,
        SCENE.IMITATION_TASK,
        SCENE.SOCIAL_REFERENCING,
        SCENE.REFERENCE
    ]


def is_interactive_objects_task(task: str) -> bool:
    """Returns whether the given task is a interactive objects task."""
    return task in [
        SCENE.ARITHMETIC,
        SCENE.INTERACTIVE_COLLISION,
        SCENE.INTERACTIVE_OBJECT_PERMANENCE,
        SCENE.MOVING_TARGET_PREDICTION,
        SCENE.NUMBER_COMPARISON,
        SCENE.SOLIDITY,
        SCENE.SUPPORT_RELATIONS,
        SCENE.TRAJECTORY,
        SCENE.TOOL_USE
    ]
