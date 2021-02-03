#!/usr/bin/env python3

import argparse
import copy
import json
import logging
import os
import os.path
import random
import sys
from typing import Any, Dict, List

import materials
import tags

sys.path.insert(1, '../pretty_json')
from pretty_json import PrettyJsonEncoder, PrettyJsonNoIndent


OUTPUT_TEMPLATE_JSON = """
{
  "name": "",
  "version": "2",
  "ceilingMaterial": "AI2-THOR/Materials/Walls/Drywall",
  "floorMaterial": "AI2-THOR/Materials/Fabrics/CarpetWhite 3",
  "wallMaterial": "AI2-THOR/Materials/Walls/DrywallBeige",
  "floorColors": ["white"],
  "wallColors": ["white"],
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
  "goal": {}
}
"""


OUTPUT_TEMPLATE = json.loads(OUTPUT_TEMPLATE_JSON)


class SceneGenerator():
    def __init__(self, hypercube_list) -> None:
        self.hypercube_list = hypercube_list

    def strip_debug_misleading_data(self, body: Dict[str, Any]) -> None:
        """Remove misleading internal debug data not needed in debug files."""
        for obj in body['objects']:
            obj.pop('speed', None)

    def strip_debug_data(self, body: Dict[str, Any]) -> None:
        """Remove internal debug data that should only be in debug files."""
        body.pop('floorColors', None)
        body.pop('wallColors', None)
        for obj in body['objects']:
            self.strip_debug_object_data(obj)
        for goal_key in ('answer', 'domainsInfo', 'objectsInfo', 'sceneInfo'):
            body['goal'].pop(goal_key, None)
        if 'metadata' in body['goal']:
            for target_key in ['target', 'target_1', 'target_2']:
                if body['goal']['metadata'].get(target_key, None):
                    body['goal']['metadata'][target_key].pop('info', None)

    def strip_debug_object_data(self, obj: Dict[str, Any]) -> None:
        """Remove internal debug data from the given object."""
        obj.pop('info', None)
        obj.pop('goalString', None)
        obj.pop('dimensions', None)
        obj.pop('offset', None)
        obj.pop('closedDimensions', None)
        obj.pop('closedOffset', None)
        obj.pop('enclosedAreas', None)
        obj.pop('openAreas', None)
        obj.pop('speed', None)
        obj.pop('isParentOf', None)
        obj.pop('parentArea', None)
        obj.pop('materialCategory', None)
        obj.pop('untrainedCategory', None)
        obj.pop('untrainedColor', None)
        obj.pop('untrainedCombination', None)
        obj.pop('untrainedShape', None)
        obj.pop('untrainedSize', None)
        obj.pop('color', None)
        obj.pop('shape', None)
        obj.pop('size', None)
        obj.pop('weight', None)
        obj.pop('role', None)
        obj.pop('boundsAtStep', None)
        obj.pop('configHeight', None)
        obj.pop('configSize', None)
        for role in tags.ROLE_DICT.values():
            obj.pop(tags.role_to_tag(role), None)
        if 'shows' in obj:
            for show in obj['shows']:
                show.pop('boundingBox', None)

    def generate_body_template(self) -> Dict[str, Any]:
        global OUTPUT_TEMPLATE
        body = copy.deepcopy(OUTPUT_TEMPLATE)
        ceiling_and_wall_material_choice = random.choice(
            random.choice(materials.CEILING_AND_WALL_MATERIALS)
        )
        body['ceilingMaterial'] = ceiling_and_wall_material_choice[0]
        body['wallMaterial'] = ceiling_and_wall_material_choice[0]
        body['wallColors'] = ceiling_and_wall_material_choice[1]
        floor_material_choice = random.choice(materials.FLOOR_MATERIALS)
        body['floorMaterial'] = floor_material_choice[0]
        body['floorColors'] = floor_material_choice[1]
        return body

    def write_scene(self, name: str, scene: Dict[str, Any]) -> None:
        # Use PrettyJsonNoIndent on some of the lists and dicts in the
        # output body because the indentation from the normal Python JSON
        # module spaces them out far too much.
        body = copy.deepcopy(scene)

        # Use PrettyJsonNoIndent on some of the lists and dicts in the
        # output body because the indentation from the normal Python JSON
        # module spaces them out far too much.
        self.wrap_with_json_no_indent(body['goal'], [
            'action_list', 'domain_list', 'type_list', 'task_list', 'info_list'
        ])
        if 'metadata' in body['goal']:
            for target in ['target', 'target_1', 'target_2']:
                if target in body['goal']['metadata']:
                    self.wrap_with_json_no_indent(
                        body['goal']['metadata'][target],
                        ['info', 'image']
                    )

        for object_config in body['objects']:
            self.wrap_with_json_no_indent(
                object_config,
                ['info', 'materials', 'salientMaterials', 'states']
            )

        with open(name, 'w') as out:
            # PrettyJsonEncoder doesn't work with json.dump so use json.dumps
            try:
                out.write(json.dumps(body, cls=PrettyJsonEncoder, indent=2))
            except Exception as e:
                logging.error(body, e)

    def wrap_with_json_no_indent(
        self,
        data: Dict[str, Any],
        prop_list: List[str]
    ) -> None:
        for prop in prop_list:
            if prop in data:
                data[prop] = PrettyJsonNoIndent(data[prop])

    def generate_scenes(
        self,
        prefix: str,
        total: int,
        type_name: str,
        eval_number: int,
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
            stop_on_error
        )

        hypercube_index = 1
        for hypercube in hypercubes:
            # Identify the next available file name index.
            while True:
                file_name = f'{prefix}_{hypercube_index:04}'
                if not os.path.exists(file_name + '_01.json'):
                    break
                hypercube_index += 1

            # Retrieve all of the scenes from this hypercubes.
            scenes = hypercube.get_scenes()

            # Randomly shuffle the scenes.
            if not sort_hypercube:
                random.shuffle(scenes)

            for scene_index, scene in enumerate(scenes):
                scene_copy = copy.deepcopy(scene)
                scene_id = scene.get('goal', {}).get('sceneInfo', {}).get(
                    'id',
                    None
                )[0]

                # The normal scene filename should only have the scene index.
                scene_filename = f'{file_name}_{(scene_index + 1):02}'

                # The debug scene filename has the scene ID for debugging.
                debug_filename = f'{scene_filename}_{scene_id}'

                # Assign additional hypercube and scene tags.
                scene_copy['name'] = scene_filename
                scene_copy['hypercubeNumber'] = hypercube_index
                scene_copy['sceneNumber'] = (scene_index + 1)
                scene_copy['evaluation'] = (
                    eval_number if eval_number > 0 else None
                )
                scene_copy['training'] = hypercube_factory.training

                # Save the scene as both normal and debug JSON files.
                self.strip_debug_misleading_data(scene_copy)
                self.write_scene(debug_filename + '_debug.json', scene_copy)
                self.strip_debug_data(scene_copy)
                self.write_scene(scene_filename + '.json', scene_copy)

    def generate_scenes_from_args(self, argv) -> None:
        parser = argparse.ArgumentParser(
            description='Generate MCS scene configuration JSON files.'
        )
        parser.add_argument(
            '-e',
            '--eval',
            type=int,
            default=0,
            help='MCS evaluation number [default=None]')
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

        self.generate_scenes(
            args.prefix,
            args.count,
            args.type,
            args.eval,
            args.sort_hypercube,
            args.stop_on_error,
            role_to_type
        )
