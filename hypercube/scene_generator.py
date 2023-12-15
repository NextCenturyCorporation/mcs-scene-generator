#!/usr/bin/env python3

import argparse
import copy
import logging
import os
import os.path
import random
from typing import Any, Dict

from machine_common_sense.logging_config import LoggingConfig

from generator import MAX_TRIES, Scene, SceneException, materials, tags
from generator.scene_saver import find_next_filename, save_scene_files

STARTER_SCENE = Scene(
    version=2,
    ceiling_material="AI2-THOR/Materials/Walls/Drywall",
    floor_material="AI2-THOR/Materials/Fabrics/CarpetWhite 3",
    wall_material="AI2-THOR/Materials/Walls/DrywallBeige",
    debug={
        "floorColors": ["white"],
        "wallColors": ["white"]
    }
)


class SceneGenerator():
    excluded_materials = []

    def __init__(self, hypercube_list) -> None:
        self.hypercube_list = hypercube_list

    def generate_starter_scene(self) -> Dict[str, Any]:
        global STARTER_SCENE
        starter_scene = copy.deepcopy(STARTER_SCENE)
        excluded = self.excluded_materials.copy()

        dark_colors = ['grey', 'black']
        dark_room = True

        ceiling_material_choice = self._get_material(
            materials.CEILING_MATERIALS)
        excluded.append(ceiling_material_choice.material)

        while dark_room:
            wall_material_choice = self._get_material(
                materials.ROOM_WALL_MATERIALS, excluded)
            excluded.append(wall_material_choice.material)
            floor_material_choice = self._get_material(
                materials.FLOOR_MATERIALS, excluded)
            if not (any(map(lambda v: v in wall_material_choice.color, dark_colors)) and any(  # noqa
                    map(lambda v: v in floor_material_choice.color, dark_colors))):  # noqa
                dark_room = False
            else:
                excluded = excluded[:-1]

        starter_scene.ceiling_material = ceiling_material_choice[0]
        starter_scene.wall_material = wall_material_choice[0]
        starter_scene.debug['wallColors'] = wall_material_choice[1]
        starter_scene.floor_material = floor_material_choice[0]
        starter_scene.debug['floorColors'] = floor_material_choice[1]
        return starter_scene

    def _get_material(self, materials, excluded_materials=None):
        if excluded_materials is None:
            excluded_materials = []
        filtered_materials = [
            material_tuple for material_tuple in materials
            if material_tuple.material not in excluded_materials
        ]
        return random.choice(filtered_materials)

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
        logger = logging.getLogger(__name__)

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

        # Create all of the needed hypercubes.
        hypercubes = hypercube_factory.generate_hypercubes(
            total,
            self.generate_starter_scene,
            role_to_type,
            stop_on_error,
            sort_hypercube
        )

        logger.info(f'Generating {len(hypercubes)} {type_name} hypercubes')
        index = -1
        hypercube_index = 1
        failed_info = []
        count = 0
        for index, hypercube in enumerate(hypercubes):
            # Identify the next available file name index.
            base_filename, hypercube_index = find_next_filename(
                f'{prefix}_',
                hypercube_index,
                '04',
                suffix='_01.json'
            )

            # Create and retrieve all of the scenes from this hypercubes.
            scenes = None
            for try_index in range(MAX_TRIES + 1):
                try:
                    scenes = hypercube.generate_scenes()
                    break
                except (
                    SceneException,
                    RuntimeError,
                    TypeError,
                    ValueError,
                    ZeroDivisionError
                ) as e:
                    if stop_on_error:
                        raise e from e
                    logger.exception(f'Failed to make a {type_name} hypercube')
                    info = hypercube.get_info()
                    if info and info not in failed_info:
                        failed_info.append(info)

            if not scenes:
                logger.warn('Skipping hypercube...')
                continue

            # Randomly shuffle the scenes.
            if not sort_hypercube:
                random.shuffle(scenes)

            for scene_index, scene in enumerate(scenes):
                filename, scene_index = find_next_filename(
                    f'{base_filename}_',
                    scene_index + 1,
                    '02'
                )

                scene.debug['hypercubeNumber'] = hypercube_index
                scene.debug['sceneNumber'] = scene_index
                scene.debug['evaluation'] = eval_name
                scene.debug['training'] = hypercube_factory.training

                save_scene_files(
                    scene,
                    filename,
                    no_scene_id=bool(eval_name)
                )

            count += 1
            logger.info(
                f'Saved {type_name} hypercube {count} / {total} '
                f'({len(scenes)} scenes): {base_filename}'
            )
            if count == total:
                break

        logger.info(f'Finished {count} {type_name} hypercubes')

        if failed_info:
            logger.warn('The following hypercubes failed:')
            for info in failed_info:
                logger.warn(f'{info}')

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
            choices=list(sorted([item.name for item in self.hypercube_list])),
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

        cfg = LoggingConfig.get_configurable_logging_config(
            log_level=args.loglevel or 'INFO',
            logger_names=['hypercube', 'generator', 'secret'],
            console=True, debug_file=False, info_file=False,
            log_file_name="hypercube", file_format='precise',
            console_format='precise'
        )
        LoggingConfig.init_logging(log_config=cfg)

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
