#!/usr/bin/env python3

import argparse
import logging
import sys
from typing import List, Type

import yaml
from machine_common_sense.logging_config import LoggingConfig

from generator import MAX_TRIES, SceneException
from generator.scene import Scene
from generator.scene_saver import find_next_filename, save_scene_files
from ideal_learning_env import (
    ActionRestrictionsComponent,
    GlobalSettingsComponent,
    ILEComponent,
    ILEException,
    RandomInteractableObjectsComponent,
    RandomKeywordObjectsComponent,
    RandomStructuralObjectsComponent,
    ShortcutComponent,
    SpecificInteractableObjectsComponent,
    ValidPathComponent
)
from ideal_learning_env.agent_component import (
    RandomAgentComponent,
    SpecificAgentComponent
)
from ideal_learning_env.interactable_object_service import ObjectRepository
from ideal_learning_env.structural_objects_component import (
    SpecificStructuralObjectsComponent
)

logger = None

ILE_COMPONENTS: List[Type[ILEComponent]] = [
    GlobalSettingsComponent,
    ShortcutComponent,
    SpecificInteractableObjectsComponent,
    SpecificStructuralObjectsComponent,
    SpecificAgentComponent,
    RandomStructuralObjectsComponent,
    RandomKeywordObjectsComponent,
    RandomInteractableObjectsComponent,
    RandomAgentComponent,
    ActionRestrictionsComponent,
    ValidPathComponent,
]


def generate_ile_scene(
    component_list: List[ILEComponent],
    scene_index: int
) -> Scene:
    """Generate and return an ILE scene using the given ILE components that
    were initialized with the config data."""
    # Create a scene template.
    scene = Scene()
    scene.version = 2
    scene.debug['sceneNumber'] = scene_index
    scene.debug['training'] = True

    ObjectRepository.get_instance().clear()
    # Each component will update the scene template based on the config data.
    for component in component_list:
        scene = component.update_ile_scene(scene)

    scene = _handle_delayed_actions(component_list, scene)
    scene = _handle_actions_at_end_of_scene_generation(component_list, scene)
    return scene


def _handle_delayed_actions(component_list, scene):
    previous_sum = 0
    while True:
        # Deteremine the number of delayed actions.  If we can't perform one
        # of them each loop, we quit with error.
        new_sum = sum(
            component.get_num_delayed_actions() for component in component_list
        )

        # If there are no more actions, we are done!
        if new_sum == 0:
            break
        # If we didn't completed a delayed action last run, we're in an
        # infinite loop and should quit.
        if new_sum == previous_sum:
            reasons = []
            for component in component_list:
                reasons += component.get_delayed_action_error_strings()

            # backslash isn't allowed in fstring.
            nl = '\n'
            raise ILEException(
                f"Failed to execute any delayed actions.  This can occur when"
                f" a required label doesn't exist, a label is mispelled, or "
                f"there is a circular dependency.  Please verify all spellings"
                f".{nl}Reasons:{nl}  {f'{nl}  '.join(reasons)}"
            )

        # Swap the GlobalSettingsComponent to be after ShortcutComponent so
        # performer_look_at happens after any position change from
        # shortcut_component
        global_settings_component_index = component_list.index([
            c for c in component_list if
            isinstance(c, GlobalSettingsComponent)][0])
        shortcut_component_index = component_list.index([
            c for c in component_list if
            isinstance(c, ShortcutComponent)][0])
        temp = component_list[global_settings_component_index]
        component_list[global_settings_component_index] = component_list[
            shortcut_component_index]
        component_list[shortcut_component_index] = temp

        # Loop through components and run delayed actions if the components
        # have any.
        for component in component_list:
            if component.get_num_delayed_actions() > 0:
                scene = component.run_delayed_actions(scene)
        previous_sum = new_sum
    return scene


def _handle_actions_at_end_of_scene_generation(component_list, scene):
    for component in component_list:
        scene = component.run_actions_at_end_of_scene_generation(scene)
    return scene


def main(args):
    """Generate and save one or more MCS JSON scenes using the given config
    for the Interactive Learning Environment (ILE)."""
    logger.info('[*] Starting the ILE Scene Generator')

    # Read the ILE config data from the YAML config file.
    config_data = {}
    if args.config:
        logger.info(f'[*] Reading options from ILE config file: {args.config}')
        with open(args.config) as config_file:
            config_data = yaml.safe_load(config_file)

    # Initialize each ILE component using the config data.
    component_list = [
        component_class(config_data) for component_class in ILE_COMPONENTS
    ]

    max_tries = 1 if args.throw_error else MAX_TRIES
    suffix = ".json"
    for index in list(range(args.number)):
        scene = None
        # Find the next available scene filename and index. For example, if
        # name_1.json already exists, then start with name_2.json.
        scene_filename, scene_index = find_next_filename(
            f'{args.prefix}{"_" if args.prefix else ""}',
            index + 1,
            '06', suffix=suffix
        )

        logger.info(
            f'[+] Generating scene {index + 1} of {args.number}, '
            f'filename: {scene_filename}{suffix}'
        )

        # Try creating the scene multiple times, in case a randomized setup
        # doesn't work the first time.
        tries = 0
        while tries < max_tries:
            tries += 1
            try:
                if (tries > 1):
                    logger.info(
                        f'Retrying generaton of scene {index + 1} of '
                        f'{args.number} (try {tries} / {max_tries}), '
                        f'filename: {scene_filename}{suffix}'
                    )
                scene = generate_ile_scene(component_list, scene_index)
                break
            except (
                ILEException,
                SceneException,
                RuntimeError,
                TypeError,
                ValueError,
                ZeroDivisionError
            ):
                error_message = (
                    f'Failed to generate scene {index + 1} of '
                    f'{args.number} (try {tries} / {max_tries}), '
                    f'filename: {scene_filename}{suffix}'
                )
                if logger.isEnabledFor(logging.DEBUG) or (tries >= max_tries):
                    logging.exception(error_message)
                else:
                    logger.info(error_message)
                if tries >= max_tries:
                    sys.exit(1)

        # If successful, save the normal and debug JSON scene files.
        save_scene_files(scene, scene_filename)
        logger.info(
            f'Finished generating scene {index + 1} of {args.number}, '
            f'filename: {scene_filename}{suffix}'
        )
    logger.info(f"[*] Generated {args.number} scenes successfully!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate MCS scene configuration JSON files.'
    )
    parser.add_argument(
        '-c',
        '--config',
        type=str,
        help='Path to ILE YAML config file'
    )
    parser.add_argument(
        '-n',
        '--number',
        type=int,
        default=1,
        help='Generate number of output scene files'
    )
    parser.add_argument(
        '-p',
        '--prefix',
        type=str,
        default='',
        help='Filename prefix of output scene files'
    )
    parser.add_argument(
        '--log-config',
        help='Log config should be either a file or "dev" for default ' +
        'development logging.'
    )
    parser.add_argument(
        '-l',
        '--log-level',
        choices=logging._nameToLevel.keys(),
        help='Log level.  Only used if log-config is not set'
    )
    parser.add_argument(
        '--throw-error',
        default=False,
        action='store_true',
        help='Stop immediately if errors are thrown [default=False]'
    )

    args = parser.parse_args()

    if args.log_config == "dev":
        dev = LoggingConfig.get_configurable_logging_config(
            log_level=args.log_level or 'DEBUG',
            logger_names=['ideal_learning_env'],
            console=True, debug_file=True, info_file=False,
            log_file_name="mcs", file_format='precise',
            console_format='precise'
        )
        LoggingConfig.init_logging(log_config=dev)
    elif not args.log_config:
        std = LoggingConfig.get_configurable_logging_config(
            log_level=args.log_level or 'INFO',
            logger_names=['ideal_learning_env'],
            console=True, debug_file=False, info_file=False,
            log_file_name="mcs", file_format='precise',
            console_format='precise'
        )
        LoggingConfig.init_logging(log_config=std)
    else:
        LoggingConfig.init_logging(
            log_config=None,
            log_config_file=args.log_config
        )
    logger = logging.getLogger('ideal_learning_env')
    main(args)
