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

from .objects import SceneObject
from .scene import Scene


def _convert_non_serializable_data(scene: Scene) -> None:
    """Convert all non-JSON-serializable data from the given scene."""
    # Convert the boundingBox from an ObjectBounds into a serializable dict.
    for instance in scene.objects:
        if 'boundsAtStep' in instance['debug']:
            del instance['debug']['boundsAtStep']
        for show in instance['shows']:
            if not show.get('boundingBox'):
                continue
            bb = show['boundingBox']
            bb = bb if isinstance(bb, dict) else vars(bb)
            box_xz = bb['box_xz']
            box_xz = [el if isinstance(el, dict) else vars(el)
                      for el in box_xz]
            show['boundingBox'] = [{
                'x': corner['x'],
                'y': bb['min_y'],
                'z': corner['z']
            } for corner in box_xz] + [{
                'x': corner['x'],
                'y': bb['max_y'],
                'z': corner['z']
            } for corner in box_xz]


def _json_no_indent(data: Dict[str, Any], prop_list: List[str]) -> None:
    """Wrap the given data with PrettyJsonNoIndent for the encoder."""
    for prop in prop_list:
        if prop in data:
            data[prop] = PrettyJsonNoIndent(data[prop])


def _strip_debug_data(scene_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Remove internal debug data that should only be in debug files."""
    del scene_dict['debug']
    for instance in scene_dict['objects']:
        _strip_debug_object_data(instance)
    for goal_key in ('answer', 'domainsInfo', 'objectsInfo', 'sceneInfo'):
        if goal_key in scene_dict['goal']:
            del scene_dict['goal'][goal_key]
    if scene_dict['goal']['metadata']:
        for target_key in ['target', 'target_1', 'target_2']:
            if scene_dict['goal']['metadata'].get(target_key, None):
                scene_dict['goal']['metadata'][target_key].pop('info', None)
    return scene_dict


def _strip_debug_misleading_data(scene: Scene) -> None:
    """Remove misleading internal debug data not needed in debug files."""
    for instance in scene.objects:
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


def _strip_debug_object_data(instance: SceneObject) -> None:
    """Remove internal debug data from the given object."""
    instance.pop('debug', None)
    if 'shows' in instance:
        for show in instance['shows']:
            show.pop('boundingBox', None)


def _truncate_floats_in_dict(data: Dict[str, Any]) -> None:
    """Truncate all the floats in the given dict."""
    for prop in data:
        if isinstance(data[prop], float):
            data[prop] = round(data[prop], 4)
        if isinstance(data[prop], list):
            _truncate_floats_in_list(data[prop])
        if isinstance(data[prop], dict):
            _truncate_floats_in_dict(data[prop])


def _truncate_floats_in_list(data: List[Any]) -> None:
    """Truncate all the floats in the given list."""
    for i in range(len(data)):
        if isinstance(data[i], float):
            data[i] = round(data[i], 4)
        if isinstance(data[i], list):
            _truncate_floats_in_list(data[i])
        if isinstance(data[i], dict):
            _truncate_floats_in_dict(data[i])


def _ready_scene_for_writing(scene: Scene) -> Dict[str, Any]:
    _strip_debug_misleading_data(scene)
    _convert_non_serializable_data(scene)
    scene_dict = scene.to_dict()
    _truncate_floats_in_dict(scene_dict)

    # Use PrettyJsonNoIndent on some of the lists and dicts in the
    # output scene because the indentation from the normal Python JSON
    # module spaces them out far too much.
    _json_no_indent(scene_dict['goal'], [
        'action_list', 'domain_list', 'type_list', 'task_list', 'info_list'
    ])
    if 'metadata' in scene_dict['goal']:
        for target in ['target', 'target_1', 'target_2']:
            if target in scene_dict['goal']['metadata']:
                _json_no_indent(scene_dict['goal']['metadata'][target], [
                    'info', 'image'
                ])
    for instance in scene_dict['objects']:
        _json_no_indent(instance, ['materials', 'salientMaterials', 'states'])
        if 'debug' in instance:
            _json_no_indent(instance['debug'], 'info')

    return scene_dict


def _write_scene_file(filename: str, scene_dict: Dict[str, Any]) -> None:
    # If the filename contains a directory, ensure that directory exists.
    path = Path(filename)
    path.parents[0].mkdir(parents=True, exist_ok=True)

    with open(filename, 'w') as out:
        # PrettyJsonEncoder doesn't work with json.dump so use json.dumps
        try:
            out.write(
                json.dumps(
                    scene_dict,
                    cls=PrettyJsonEncoder,
                    indent=2))
        except Exception as e:
            logging.error(scene_dict, e)
            raise e from e


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
    scene: Scene,
    scene_filename: str,
    no_scene_id: bool = False,
    no_debug_file: bool = False,
    only_debug_file: bool = False
) -> int:
    """Save the given scene as a normal JSON file and a debug JSON file."""

    # The debug scene filename has the scene ID for debugging.
    scene_id = (scene.goal.scene_info or {}).get('id', [None])[0]
    debug_filename = (
        scene_filename if (no_scene_id or not scene_id) else
        f'{scene_filename}_{scene_id}'
    )

    # Ensure that the scene's 'name' property doesn't have a directory.
    scene_copy = copy.deepcopy(scene)
    scene_copy.name = Path(scene_filename).name
    scene_dict = _ready_scene_for_writing(scene_copy)

    # Save the scene as both normal and debug JSON files.
    if not no_debug_file:
        _write_scene_file(debug_filename + '_debug.json', scene_dict)
    scene_dict = _strip_debug_data(scene_dict)
    if not only_debug_file:
        _write_scene_file(scene_filename + '.json', scene_dict)
