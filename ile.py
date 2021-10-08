#!/usr/bin/env python3

import argparse
import logging
from typing import Any, Dict, List, Type

import yaml
from machine_common_sense.logging_config import LoggingConfig

from generator import SceneException, util
from generator.scene_saver import find_next_filename, save_scene_files
from ideal_learning_env import (
    ActionRestrictionsComponent,
    GlobalSettingsComponent,
    ILEComponent,
    ILEException,
    RandomInteractableObjectsComponent,
    RandomKeywordObjectsComponent,
    RandomStructuralObjectsComponent,
    SpecificInteractableObjectsComponent,
)
from ideal_learning_env.interactable_object_config import ObjectRepository
from ideal_learning_env.structural_objects_component import (
    SpecificStructuralObjectsComponent,
)

ILE_COMPONENTS: List[Type[ILEComponent]] = [
    GlobalSettingsComponent,
    SpecificInteractableObjectsComponent,
    SpecificStructuralObjectsComponent,
    RandomStructuralObjectsComponent,
    RandomKeywordObjectsComponent,
    RandomInteractableObjectsComponent,
    ActionRestrictionsComponent
]


def generate_ile_scene(
    component_list: List[ILEComponent],
    scene_index: int
) -> Dict[str, Any]:
    """Generate and return an ILE scene using the given ILE components that
    were initialized with the config data."""
    # Create a scene template.
    scene = {
        'name': '',  # The name will be set later
        'version': 2,
        'objects': [],
        'goal': {
            'domainsInfo': {},
            'objectsInfo': {},
            'sceneInfo': {},
            'metadata': {}
        },
        'debug': {
            'sceneNumber': scene_index,
            'training': True
        }
    }
    ObjectRepository.get_instance().clear()
    # Each component will update the scene template based on the config data.
    for component in component_list:
        scene = component.update_ile_scene(scene)

    scene = _handle_delayed_actions(component_list, scene)

    return scene


def _handle_delayed_actions(component_list, scene):
    previous_sum = 0
    while True:
        # Deteremine the number of delayed actions.  If we can't perform one
        # of them each loop, we quit with error.
        new_sum = 0
        for component in component_list:
            new_sum += component.get_num_delayed_actions()

        # If there are no more actions, we are done!
        if new_sum == 0:
            break
        # If we didn't completed a delayed action last run, we're in an
        # infinite loop and should quit.
        if new_sum == previous_sum:
            raise ILEException("Failed to reduce delayed actions")
        # Loop through components and run delayed actions if the components
        # have any.
        for component in component_list:
            if component.get_num_delayed_actions() > 0:
                scene = component.run_delayed_actions(scene)
        previous_sum = new_sum
    return scene


def get_dev_logging_config(root_level: str = None):
    '''Note: This logging configuration needs the log directory to be
    created relative to the current working directory of the python
    execution.
    '''
    return {
        "version": 1,
        "root": {
            "level": root_level or 'DEBUG',
            "handlers": ["console", "debug-file"],
            "propagate": False
        },
        "loggers": {
            "ideal_learning_env": {
                "level": root_level or 'DEBUG',
                "handlers": ["console", "debug-file"],
                "propagate": False
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "precise",
                "level": root_level or 'DEBUG',
                "stream": "ext://sys.stdout"
            },
            "debug-file": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "precise",
                "filename": "logs/mcs.debug.log",
                "maxBytes": 10240000,
                "backupCount": 3
            },
            "info-file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "precise",
                "filename": "logs/mcs.info.log",
                "maxBytes": 10240000,
                "backupCount": 3
            }
        },
        "formatters": {
            "brief": {
                "format": "%(message)s"
            },
            "precise": {
                "format": "%(asctime)s <%(levelname)s>: %(message)s"
            },
            "full": {
                "format": "[%(name)s] %(asctime)s <%(levelname)s>: " +
                "%(message)s"
            }
        }
    }


def main(args):
    """Generate and save one or more MCS JSON scenes using the given config
    for the Ideal Learning Environment (ILE)."""
    logger = logging.getLogger()
    logger.info('Starting the Ideal Learning Environment Scene Generator')

    # Read the ILE config data from the YAML config file.
    config_data = {}
    if args.config:
        with open(args.config) as config_file:
            config_data = yaml.safe_load(config_file)

    # Initialize each ILE component using the config data.
    component_list = [
        component_class(config_data) for component_class in ILE_COMPONENTS
    ]

    for index in list(range(args.number)):
        scene = None
        # Find the next available scene filename and index. For example, if
        # name_1.json already exists, then start with name_2.json.
        scene_filename, scene_index = find_next_filename(
            f'{args.prefix}{"_" if args.prefix else ""}',
            index + 1,
            '06'
        )

        logger.info(
            f'Generating scene {index + 1} of {args.number}: '
            f'{scene_filename}'
        )

        # Try creating the scene multiple times, in case a randomized setup
        # doesn't work the first time.
        tries = 0
        while tries < util.MAX_TRIES:
            tries += 1
            try:
                scene = generate_ile_scene(component_list, scene_index)
                break
            except (
                ILEException,
                SceneException,
                RuntimeError,
                TypeError,
                ValueError,
                ZeroDivisionError
            ) as e:
                logging.error(
                    f'Failed to generate scene {scene_index} '
                    f'(try {tries} / {util.MAX_TRIES})',
                    exc_info=e
                )
                if args.throw_error or tries >= util.MAX_TRIES:
                    raise e
        # If successful, save the normal and debug JSON scene files.
        save_scene_files(scene, scene_filename)


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

    if args.log_config == "dev" or (not args.log_config and args.log_level):
        dev = get_dev_logging_config(args.log_level)
        LoggingConfig.init_logging(log_config=dev)
    elif args.log_config:
        LoggingConfig.init_logging(
            log_config=None,
            log_config_file=args.log_config
        )
    elif args.log_level:
        logging.getLogger().setLevel(args.log_level)

    main(args)
