#!/usr/bin/env python3

import sys

from hypercube import SceneGenerator, agent_hypercubes, interactive_hypercubes
from secret import interactive_object_permanence_hypercubes
from secret import (
    intuitive_physics_hypercubes as secret_intuitive_physics_hypercubes,
)
from secret import reorientation_hypercubes

HYPERCUBE_LIST = (
    interactive_hypercubes.INTERACTIVE_TRAINING_HYPERCUBE_LIST +
    interactive_hypercubes.INTERACTIVE_EVALUATION_HYPERCUBE_LIST +
    secret_intuitive_physics_hypercubes.SECRET_INTUITIVE_PHYSICS_TRAINING_HYPERCUBE_LIST +  # noqa: E501
    secret_intuitive_physics_hypercubes.SECRET_INTUITIVE_PHYSICS_EVALUATION_HYPERCUBE_LIST +  # noqa: E501
    interactive_object_permanence_hypercubes.EVALUATION_HYPERCUBE_LIST +
    reorientation_hypercubes.EVALUATION_HYPERCUBE_LIST +
    agent_hypercubes.AGENT_TRAINING_HYPERCUBE_LIST +
    agent_hypercubes.AGENT_EVALUATION_HYPERCUBE_LIST
)


def main(argv):
    scene_generator = SceneGenerator(HYPERCUBE_LIST)
    scene_generator.generate_scenes_from_args(argv)


if __name__ == '__main__':
    main(sys.argv)
