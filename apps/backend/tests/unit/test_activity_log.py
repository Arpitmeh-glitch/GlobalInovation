from datetime import datetime, timezone

import pytest

from app.audit.event_store import get_activities, log_activity


@pytest.mark.asyncio
async def test_activity_log_returns_newest_first(isolated_backend_state, monkeypatch: pytest.MonkeyPatch) -> None:
    timestamps = iter(
        [
            datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
            datetime(2026, 1, 2, tzinfo=timezone.utc).isoformat(),
        ]
    )
    monkeypatch.setattr("app.audit.event_store._now_iso", lambda: next(timestamps))

    older = await log_activity("job_discovery", "searched jobs", user_id="user-1")
    newer = await log_activity("match", "analyzed match", user_id="user-1")

    activities = await get_activities(user_id="user-1")
    assert [item["id"] for item in activities] == [newer["id"], older["id"]]
    assert activities[0]["created_at"] > activities[1]["created_at"]


@pytest.mark.asyncio
async def test_activity_log_filters_and_paginates(isolated_backend_state) -> None:
    await log_activity("job_discovery", "one")
    await log_activity("match", "two")
    await log_activity("match", "three")

    matches = await get_activities(activity_type="match", limit=1, offset=1)
    assert len(matches) == 1
    assert matches[0]["action"] == "two"


@pytest.mark.asyncio
async def test_public_activity_dao_persists_and_lists_events(isolated_backend_state) -> None:
    created = await isolated_backend_state.create_agent_activity(
        activity_type="demo",
        action="reset",
        details={"demo": True},
        user_id="demo-user",
        created_at="2026-01-01T00:00:00+00:00",
    )

    events = await isolated_backend_state.list_agent_activities(user_id="demo-user")
    assert events == [created]


@pytest.mark.asyncio
async def test_activity_log_redacts_sensitive_values_before_persisting(isolated_backend_state) -> None:
    created = await log_activity(
        "settings",
        "received credentials",
        details={
            "authorization": "Bearer secret123",
            "api_key": "sk-live-example123",
            "nested": {"password": "correct-horse"},
            "message": "token=abc123 and secret=hidden-value",
        },
    )

    stored = await get_activities()
    details = stored[0]["details"]
    assert created["details"] == details
    assert details["authorization"] == "[REDACTED]"
    assert details["api_key"] == "[REDACTED]"
    assert details["nested"]["password"] == "[REDACTED]"
    assert "secret123" not in str(details)
    assert "sk-live-example123" not in str(details)
    assert "hidden-value" not in str(details)
    assert "[REDACTED]" in details["message"]
