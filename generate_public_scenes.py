#!/usr/bin/env python3

import sys

from hypercube import (
    SceneGenerator,
    agent_hypercubes,
    interactive_hypercubes,
    intuitive_physics_hypercubes,
)

HYPERCUBE_LIST = (
    interactive_hypercubes.INTERACTIVE_TRAINING_HYPERCUBE_LIST +
    interactive_hypercubes.INTERACTIVE_EVALUATION_HYPERCUBE_LIST +
    intuitive_physics_hypercubes.INTUITIVE_PHYSICS_TRAINING_HYPERCUBE_LIST +
    intuitive_physics_hypercubes.INTUITIVE_PHYSICS_EVALUATION_HYPERCUBE_LIST +
    agent_hypercubes.AGENT_TRAINING_HYPERCUBE_LIST +
    agent_hypercubes.AGENT_EVALUATION_HYPERCUBE_LIST
)


def main(argv):
    scene_generator = SceneGenerator(HYPERCUBE_LIST)
    scene_generator.generate_scenes_from_args(argv)


if __name__ == '__main__':
    main(sys.argv)
