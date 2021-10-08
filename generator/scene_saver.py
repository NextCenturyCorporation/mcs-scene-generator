#!/usr/bin/env python3

import copy
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(1, '../pretty_json')
from pretty_json import PrettyJsonEncoder, PrettyJsonNoIndent


def _json_no_indent(data: Dict[str, Any], prop_list: List[str]) -> None:
    """Wrap the given data with PrettyJsonNoIndent for the encoder."""
    for prop in prop_list:
        if prop in data:
            data[prop] = PrettyJsonNoIndent(data[prop])


def _strip_debug_data(scene: Dict[str, Any]) -> None:
    """Remove internal debug data that should only be in debug files."""
    scene.pop('debug', None)
    for instance in scene['objects']:
        _strip_debug_object_data(instance)
    for goal_key in ('answer', 'domainsInfo', 'objectsInfo', 'sceneInfo'):
        scene['goal'].pop(goal_key, None)
    if 'metadata' in scene['goal']:
        for target_key in ['target', 'target_1', 'target_2']:
            if scene['goal']['metadata'].get(target_key, None):
                scene['goal']['metadata'][target_key].pop('info', None)


def _strip_debug_misleading_data(scene: Dict[str, Any]) -> None:
    """Remove misleading internal debug data not needed in debug files."""
    for instance in scene['objects']:
        if 'movement' in instance['debug']:
            for movement_property in [
                'moveExit', 'deepExit', 'tossExit',
                'moveStop', 'deepStop', 'tossStop'
            ]:
                if instance['debug']['movement'].get(movement_property):
                    for axis in ['x', 'y', 'z']:
                        distance_property = axis + 'DistanceByStep'
                        instance['debug']['movement'][movement_property].pop(
                            distance_property,
                            None
                        )


def _strip_debug_object_data(instance: Dict[str, Any]) -> None:
    """Remove internal debug data from the given object."""
    instance.pop('debug', None)
    if 'shows' in instance:
        for show in instance['shows']:
            show.pop('boundingBox', None)


def _write_scene_file(filename: str, scene: Dict[str, Any]) -> None:
    # Use PrettyJsonNoIndent on some of the lists and dicts in the
    # output scene because the indentation from the normal Python JSON
    # module spaces them out far too much.
    scene = copy.deepcopy(scene)

    _json_no_indent(scene['goal'], [
        'action_list', 'domain_list', 'type_list', 'task_list', 'info_list'
    ])
    if 'metadata' in scene['goal']:
        for target in ['target', 'target_1', 'target_2']:
            if target in scene['goal']['metadata']:
                _json_no_indent(scene['goal']['metadata'][target], [
                    'info', 'image'
                ])

    for instance in scene['objects']:
        _json_no_indent(instance, ['materials', 'salientMaterials', 'states'])
        if 'debug' in instance:
            _json_no_indent(instance['debug'], 'info')

    # If the filename contains a directory, ensure that directory exists.
    path = Path(filename)
    path.parents[0].mkdir(parents=True, exist_ok=True)

    with open(filename, 'w') as out:
        # PrettyJsonEncoder doesn't work with json.dump so use json.dumps
        try:
            out.write(json.dumps(scene, cls=PrettyJsonEncoder, indent=2))
        except Exception as e:
            logging.error(scene, e)


def find_next_filename(
    prefix: str,
    index: int,
    indent: str,
    suffix: str = '.json'
) -> Tuple[int, str]:
    """Find the next available filename with the given prefix, indented index,
    and and suffix (file extension), then return the filename without the
    suffix (file extension) and the next available index."""
    while True:
        filename = f'{prefix}{index:{indent}}'
        if not os.path.exists(f'{filename}{suffix}'):
            break
        index += 1
    return filename, index


def save_scene_files(
    scene: Dict[str, Any],
    scene_filename: str,
    no_scene_id: bool = False
) -> int:
    """Save the given scene as a normal JSON file and a debug JSON file."""

    # The debug scene filename has the scene ID for debugging.
    scene_id = scene.get('goal', {}).get('sceneInfo', {}).get('id', [None])[0]
    debug_filename = (
        scene_filename if (no_scene_id or not scene_id) else
        f'{scene_filename}_{scene_id}'
    )

    # Ensure that the scene's 'name' property doesn't have a directory.
    scene['name'] = Path(scene_filename).name

    # Save the scene as both normal and debug JSON files.
    _strip_debug_misleading_data(scene)
    _write_scene_file(debug_filename + '_debug.json', scene)
    _strip_debug_data(scene)
    _write_scene_file(scene_filename + '.json', scene)
