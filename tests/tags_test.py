from generator import tags


def test_domain_type():
    for task in vars(tags.TASKS).values():
        print(task)
        passive_agent = tags.is_passive_agent_task(task)
        passive_physics = tags.is_passive_physics_task(task)
        interactive_agents = tags.is_interactive_agents_task(task)
        interactive_objects = tags.is_interactive_objects_task(task)
        interactive_places = tags.is_interactive_places_task(task)
        if passive_agent:
            assert not passive_physics
            assert not interactive_agents
            assert not interactive_objects
            assert not interactive_places
        elif passive_physics:
            assert not interactive_agents
            assert not interactive_objects
            assert not interactive_places
        elif interactive_agents:
            assert not interactive_objects
            assert not interactive_places
        elif interactive_objects:
            assert not interactive_places
        else:
            assert interactive_places
