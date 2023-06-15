import pytest

from ideal_learning_env import (
    GlobalSettingsComponent,
    ObjectRepository,
    ShortcutComponent,
    SpecificInteractableObjectsComponent,
    SpecificStructuralObjectsComponent
)
from ile import generate_ile_scene


@pytest.fixture(autouse=True)
def run_around_test():
    # Prepare test
    ObjectRepository.get_instance().clear()

    # Run test
    yield

    # Cleanup
    ObjectRepository.get_instance().clear()


def test_start_on_platform_and_lava_partition():
    for _ in range(50):
        shortcut_data = {
            'shortcut_lava_room': True,
            'shortcut_start_on_platform': True
        }
        platform_data = {
            'structural_platforms': {
                'num': 1,
                'position': {
                    'x': 0,
                    'y': 0,
                    'z': -5.5
                },
                'rotation_y': 0,
                'scale': 1,
                'labels': 'start_structure'
            }
        }
        global_data = {
            'performer_look_at': 'target',
            "room_dimensions": {
                "x": 14,
                "y": 4,
                "z": 12
            }
        }
        soccer_ball_data = {
            "specific_interactable_objects": {
                "num": 1,
                "shape": "soccer_ball",
                "labels": "target",
                'position': {
                    'x': 2,
                    'y': 0,
                    'z': 4
                },
                'scale': 1
            }
        }

        shortcut_component = ShortcutComponent(shortcut_data)
        platform_component = SpecificStructuralObjectsComponent(platform_data)
        global_settings_component = GlobalSettingsComponent(global_data)
        interactable_objects_component = SpecificInteractableObjectsComponent(
            soccer_ball_data
        )
        component_list = [
            global_settings_component,
            shortcut_component,
            interactable_objects_component,
            platform_component
        ]

        scene = generate_ile_scene(
            component_list=component_list, scene_index=0)
        objects = scene.objects
        assert len(scene.objects) == 2
        assert objects[0]['type'] == 'soccer_ball'
        assert objects[0]['shows'][0]["position"] == {
            'x': 2.0, 'y': 0.11, 'z': 4.0}
        assert objects[0]['shows'][0]["scale"] == {
            'x': 1.0, 'y': 1.0, 'z': 1.0}
        assert objects[1]['type'] == 'cube'
        assert objects[1]['shows'][0]["position"] == {
            'x': 0.0, 'y': 0.5, 'z': -5.5}
        assert objects[1]['shows'][0]["scale"] == {
            'x': 1.0, 'y': 1.0, 'z': 1.0}
        assert scene.performer_start.rotation.x == 10
        assert scene.performer_start.rotation.y == 10
        assert pytest.approx(
            scene.performer_start.position.x, abs=0.175) == 0
        assert scene.performer_start.position.y == 1
        assert pytest.approx(
            scene.performer_start.position.z, abs=0.175) == -5.5
        assert pytest.approx(scene.partition_floor.leftHalf, 0.015) == 0.66
        assert pytest.approx(scene.partition_floor.rightHalf, 0.015) == 0.66
