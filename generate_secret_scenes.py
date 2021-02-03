#!/usr/bin/env python3

import sys

import agent_hypercubes
import interactive_hypercubes
import secret_intuitive_physics_hypercubes

from scene_generator import SceneGenerator


HYPERCUBE_LIST = (
    interactive_hypercubes.INTERACTIVE_TRAINING_HYPERCUBE_LIST +
    interactive_hypercubes.INTERACTIVE_EVALUATION_HYPERCUBE_LIST +
    secret_intuitive_physics_hypercubes.SECRET_INTUITIVE_PHYSICS_TRAINING_HYPERCUBE_LIST +  # noqa: E501
    secret_intuitive_physics_hypercubes.SECRET_INTUITIVE_PHYSICS_EVALUATION_HYPERCUBE_LIST +  # noqa: E501
    agent_hypercubes.AGENT_TRAINING_HYPERCUBE_LIST +
    agent_hypercubes.AGENT_EVALUATION_HYPERCUBE_LIST
)


def main(argv):
    scene_generator = SceneGenerator(HYPERCUBE_LIST)
    scene_generator.generate_scenes_from_args(argv)


if __name__ == '__main__':
    main(sys.argv)
