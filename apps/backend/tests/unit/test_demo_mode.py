from copy import deepcopy

import pytest

from app.agent.demo_mode import DemoModeManager
from app.audit.event_store import log_activity


@pytest.mark.asyncio
async def test_demo_status_confirms_isolation_and_metadata() -> None:
    manager = DemoModeManager()

    status = await manager.get_demo_status()

    assert status.is_demo_mode is True
    assert status.demo_user_id == "demo-user-careerpilot"
    assert status.demo_scenario == "default"
    assert status.metadata["isolated"] is True
    assert status.metadata["real_data_mutated"] is False


@pytest.mark.asyncio
async def test_demo_reset_is_idempotent(isolated_backend_state) -> None:
    manager = DemoModeManager()

    first = await manager.reset_demo_state("cloud_security")
    first_status = await manager.get_demo_status()
    first_profile = await manager.get_demo_profile()
    first_jobs = await manager.get_demo_jobs()
    first_activities = await manager.get_demo_activities()

    second = await manager.reset_demo_state("cloud_security")
    second_status = await manager.get_demo_status()
    second_profile = await manager.get_demo_profile()
    second_jobs = await manager.get_demo_jobs()
    second_activities = await manager.get_demo_activities()

    assert first.model_dump() == second.model_dump()
    assert first_status == second_status
    assert first_profile == second_profile
    assert first_jobs == second_jobs
    assert first_activities == second_activities


@pytest.mark.asyncio
async def test_demo_reset_does_not_touch_real_activity_records(isolated_backend_state) -> None:
    manager = DemoModeManager()
    real_event = await log_activity(
        "real_event",
        "user_action",
        {"note": "keep this"},
        user_id="real-user-1",
    )
    real_snapshot = deepcopy(real_event)

    await manager.reset_demo_state()

    from app.audit.event_store import get_activities

    real_events = await get_activities(user_id="real-user-1")
    assert real_events == [real_snapshot]
    assert all(event["user_id"] == manager.DEMO_USER_ID for event in await manager.get_demo_activities())
