import re
from types import SimpleNamespace
from typing import Any, Dict, List


ALL = 'all'
ANY = 'any'

GOAL_DICT = {
    'TRAVERSAL': 'traversal',
    'RETRIEVAL': 'retrieval',
    'TRANSFERRAL': 'transferral'
}

ROLE_DICT = {
    'AGENT': 'agent',
    'CONFUSOR': 'confusor',
    'CONTAINER': 'container',
    'CONTEXT': 'context',
    'HOME': 'home',
    'INTUITIVE_PHYSICS_OCCLUDER': 'intuitive physics occluder',
    'NON_TARGET': 'non target',
    'OBSTACLE': 'obstacle',
    'OCCLUDER': 'occluder',
    'STRUCTURAL': 'structural',
    'TARGET': 'target',
    'WALL': 'wall'
}

SCENE_BOOL_TAGS_DICT = {
    'INTERACTIVE': 'interactive',
    'PASSIVE': 'passive'
}

SCENE_OPTIONAL_TAGS_DICT = {
    'DIRECTION': 'direction',
    'FALL_DOWN': 'fallDown',
    'MOVE_ACROSS': 'moveAcross',
    'SETUP': 'sceneSetup'
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

    ID='id',
    NAME='name',
    HYPERCUBE_ID='hypercubeId',
    SLICES='slices',

    ACTION_NONE='action none',
    ACTION_FULL='action full',

    INTUITIVE_PHYSICS='intuitive physics',
    COLLISIONS='collisions',
    GRAVITY_SUPPORT='gravity support',
    OBJECT_PERMANENCE='object permanence',
    SHAPE_CONSTANCY='shape constancy',
    SPATIO_TEMPORAL_CONTINUITY='spatio temporal continuity',

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

    AGENT_BACKGROUND_SINGLE_OBJECT='agents single object',
    AGENT_BACKGROUND_OBJECT_PREFERENCE='agents object preference',
    AGENT_BACKGROUND_UNDIRECTED_MOVEMENT='agents undirected movement',
    AGENT_EVALUATION_OBJECT_PREFERENCE='agents object preference',
    AGENT_EVALUATION_EFFICIENT_ACTION_A='agents efficient action path lure',
    AGENT_EVALUATION_EFFICIENT_ACTION_B='agents efficient action time control'
)

CELLS = SimpleNamespace(
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
        HALF='half support',
        MINIMAL='minimal support',
        NONE='no support'
    ),
    GRAVITY_SUPPORT_TARGET_TYPE=SimpleNamespace(
        ASYMMETRIC='asymmetric',
        SYMMETRIC='symmetric'
    ),

    OBJECT_PERMANENCE_SETUP=SimpleNamespace(
        EXIT='move across whole scene',
        STOP='stop behind an occluder'
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
    )
)

# MCS core domains
DOMAINS = SimpleNamespace(
    OBJECTS='objects',
    OBJECTS_1='objects have depth and move in 3D space',
    OBJECTS_2='objects move separately from one another except on contact',
    OBJECTS_3='objects change motion on contact and do not pass through one another',  # noqa: E501
    OBJECTS_4='objects persist and can be tracked briefly over occlusion',
    OBJECTS_5='unseen objects can cause visible outcomes',
    OBJECTS_6='occluded objects are the same if their visible surfaces align',
    OBJECTS_7='objects are connected if their visible parts move together',
    OBJECTS_8='objects belong to kinds with distinctive forms and functions',
    OBJECTS_9='learn object labels from language',
    OBJECTS_10='objects fall if not supported under center of mass',

    PLACES='places',
    PLACES_1='observed agents navigate to goal by path of least resistance',
    PLACES_2='keep track of location',
    PLACES_3='ability to learn the layout of their environment',
    PLACES_4='navigate by encoding distances and directions of stable surfaces',  # noqa: E501

    AGENTS='agents',
    AGENTS_1='agents can change object motion',
    AGENTS_2='agents have goals',
    AGENTS_3='agents act efficiently',
    AGENTS_4='unseen agents can cause visible outcomes',
    AGENTS_5='judge amount of effort agent expends to cause outcomes',
    AGENTS_6='infer if agents help or hinder and adjust their positive or negative behavior',  # noqa: E501
    AGENTS_7='learn which agents to reach for',
    AGENTS_8='understand what agents can or cannot see',
    AGENTS_9='understand simple dispositions and preferences of agents',
    AGENTS_10='anticipate actions based on credibility of referential behavior',  # noqa: E501
    AGENTS_11='help others in response to salient cues of need'
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

    INTERACTIVE_CONTAINER='intcon',
    INTERACTIVE_OBSTACLE='intobs',
    INTERACTIVE_OCCLUDER='intocc'
)


def append_object_tags(
    scene_info: Dict[str, Any],
    objects_info: Dict[str, Any],
    role_to_object_list: Dict[str, List[Dict[str, Any]]]
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
    role_to_object_list: Dict[str, List[Dict[str, Any]]],
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
    instance: Dict[str, Any],
    role: str,
    trained_tag: str,
    untrained_tag: str
) -> None:
    """Appends 'trained' or 'untrained' tags of the given type for the given
    instance with the given role onto the given scene_info and objects_info
    collections."""

    if instance.get(untrained_tag, False):
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
