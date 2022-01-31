#!/usr/bin/env python3

import argparse
import copy
import json
import logging
import os
import os.path
import random
from typing import Any, Dict

from generator import materials, tags
from generator.scene_saver import find_next_filename, save_scene_files

OUTPUT_TEMPLATE_JSON = """
{
  "name": "",
  "version": "2",
  "ceilingMaterial": "AI2-THOR/Materials/Walls/Drywall",
  "floorMaterial": "AI2-THOR/Materials/Fabrics/CarpetWhite 3",
  "wallMaterial": "AI2-THOR/Materials/Walls/DrywallBeige",
  "performerStart": {
    "position": {
      "x": 0,
      "y": 0,
      "z": 0
    },
    "rotation": {
      "x": 0,
      "y": 0,
      "z": 0
    }
  },
  "objects": [],
  "goal": {},
  "debug": {
      "floorColors": ["white"],
      "wallColors": ["white"]
  }
}
"""


OUTPUT_TEMPLATE = json.loads(OUTPUT_TEMPLATE_JSON)


class SceneGenerator():
    def __init__(self, hypercube_list) -> None:
        self.hypercube_list = hypercube_list

    def generate_body_template(self) -> Dict[str, Any]:
        global OUTPUT_TEMPLATE
        body = copy.deepcopy(OUTPUT_TEMPLATE)
        ceiling_and_wall_material_choice = random.choice(
            random.choice(materials.CEILING_AND_WALL_GROUPINGS)
        )
        body['ceilingMaterial'] = ceiling_and_wall_material_choice[0]
        body['wallMaterial'] = ceiling_and_wall_material_choice[0]
        body['debug']['wallColors'] = ceiling_and_wall_material_choice[1]
        floor_material_choice = random.choice(materials.FLOOR_MATERIALS)
        body['floorMaterial'] = floor_material_choice[0]
        body['debug']['floorColors'] = floor_material_choice[1]
        return body

    def generate_scenes(
        self,
        prefix: str,
        total: int,
        type_name: str,
        eval_name: str,
        sort_hypercube: bool,
        stop_on_error: bool,
        role_to_type: Dict[str, str]
    ) -> None:
        # If the file prefix is in a folder, ensure that folder exists.
        folder_name = os.path.dirname(prefix)
        if folder_name != '':
            os.makedirs(folder_name, exist_ok=True)

        # Find the hypercube factory with the given type.
        hypercube_factory = None
        for item in self.hypercube_list:
            if item.name == type_name:
                hypercube_factory = item
        if not hypercube_factory:
            raise ValueError(f'Failed to find {type_name} hypercube factory')

        # Generate all of the needed hypercubes.
        hypercubes = hypercube_factory.build(
            total,
            self.generate_body_template,
            role_to_type,
            stop_on_error,
            sort_hypercube
        )

        hypercube_index = 1
        for hypercube in hypercubes:
            # Identify the next available file name index.
            base_filename, hypercube_index = find_next_filename(
                f'{prefix}_',
                hypercube_index,
                '04',
                suffix='_01.json'
            )

            # Retrieve all of the scenes from this hypercubes.
            scenes = hypercube.get_scenes()

            # Randomly shuffle the scenes.
            if not sort_hypercube:
                random.shuffle(scenes)

            for scene_index, scene in enumerate(scenes):
                filename, scene_index = find_next_filename(
                    f'{base_filename}_',
                    scene_index + 1,
                    '02'
                )

                scene['debug']['hypercubeNumber'] = hypercube_index
                scene['debug']['sceneNumber'] = scene_index
                scene['debug']['evaluation'] = eval_name
                scene['debug']['training'] = hypercube_factory.training

                save_scene_files(
                    scene,
                    filename,
                    no_scene_id=bool(eval_name)
                )

    def generate_scenes_from_args(self, argv) -> None:
        parser = argparse.ArgumentParser(
            description='Generate MCS scene configuration JSON files.'
        )
        parser.add_argument(
            '-e',
            '--eval',
            default=None,
            help='MCS evaluation name [default=None]')
        parser.add_argument(
            '-p',
            '--prefix',
            required=True,
            help='Output filename prefix')
        parser.add_argument(
            '-t',
            '--type',
            required=True,
            choices=[item.name for item in self.hypercube_list],
            help='Type of hypercubes to generate')
        parser.add_argument(
            '-c',
            '--count',
            type=int,
            default=1,
            help='Number of hypercubes to generate [default=1]')
        parser.add_argument(
            '-s',
            '--seed',
            type=int,
            default=None,
            help='Random number seed [default=None]')
        parser.add_argument(
            '--sort-hypercube',
            default=False,
            action='store_true',
            help='Do not randomly shuffle hypercubes [default=False]')
        parser.add_argument(
            '--stop-on-error',
            default=False,
            action='store_true',
            help='Stop if an error occurs [default=False]')
        parser.add_argument(
            '-l',
            '--loglevel',
            # no public way to find this, apparently :(
            choices=logging._nameToLevel.keys(),
            help='Set log level')
        parser.add_argument(
            '--target',
            type=str,
            default=None,
            help='Specific target type (intuitive physics & agent scenes)')
        parser.add_argument(
            '--non-target',
            type=str,
            default=None,
            help='Specific non-target type (intuitive physics & agent scenes)')
        parser.add_argument(
            '--container',
            type=str,
            default=None,
            help='Specific main container type (interactive/container scenes)')
        parser.add_argument(
            '--obstacle',
            type=str,
            default=None,
            help='Specific main obstacle type (interactive/obstacle scenes)')
        parser.add_argument(
            '--occluder',
            type=str,
            default=None,
            help='Specific main occluder type (interactive/occluder scenes)')
        parser.add_argument(
            '--context',
            type=str,
            default=None,
            help='Specific context object type (interactive scenes)')
        parser.add_argument(
            '--agent',
            type=str,
            default=None,
            help='Specific agent type (agent scenes)')
        parser.add_argument(
            '--second-agent',
            type=str,
            default=None,
            help='Specific second agent type (multi-agent scenes)')
        parser.add_argument(
            '--symmetric',
            type=str,
            default=None,
            help='Specific symmetric target type (gravity support scenes)')
        parser.add_argument(
            '--asymmetric',
            type=str,
            default=None,
            help='Specific asymmetric target type (gravity support scenes)')

        args = parser.parse_args(argv[1:])
        random.seed(args.seed)

        if args.loglevel:
            logging.getLogger().setLevel(args.loglevel)

        role_to_type = {}
        role_to_type[tags.ROLES.AGENT] = args.agent
        role_to_type[tags.ROLES.CONTAINER] = args.container
        role_to_type[tags.ROLES.CONTEXT] = args.context
        role_to_type[tags.ROLES.NON_TARGET] = args.non_target
        role_to_type[tags.ROLES.OBSTACLE] = args.obstacle
        role_to_type[tags.ROLES.OCCLUDER] = args.occluder
        role_to_type[tags.ROLES.TARGET] = args.target
        role_to_type['symmetric'] = args.symmetric
        role_to_type['asymmetric'] = args.asymmetric
        role_to_type['second agent'] = args.second_agent

        self.generate_scenes(
            args.prefix,
            args.count,
            args.type,
            args.eval,
            args.sort_hypercube,
            args.stop_on_error,
            role_to_type
        )
