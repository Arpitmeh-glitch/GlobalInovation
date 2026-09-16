"""Persistent, redacted activity events for CareerPilot."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Literal

from app.database import db

REDACTED = "[REDACTED]"
ActivityStatus = Literal["success", "failure"]

_SENSITIVE_KEY = re.compile(
    r"(?:api[_-]?key|authorization|bearer|password|passwd|secret|token|credential)",
    re.IGNORECASE,
)
_BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE)
_SECRET_KEY_VALUE = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]+|(?:api[_-]?key|password|passwd|secret|token)\s*[:=]\s*)[^\s,;]+",
    re.IGNORECASE,
)


def redact_sensitive_data(value: Any, *, key: str | None = None) -> Any:
    """Return JSON-compatible details with common credentials removed."""
    if key is not None and _SENSITIVE_KEY.search(key):
        return REDACTED
    if isinstance(value, Mapping):
        return {str(item_key): redact_sensitive_data(item_value, key=str(item_key)) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [redact_sensitive_data(item) for item in value]
    if isinstance(value, tuple):
        return [redact_sensitive_data(item) for item in value]
    if isinstance(value, str):
        return _SECRET_KEY_VALUE.sub(REDACTED, _BEARER.sub(REDACTED, value))
    return value


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _activity_payload(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "activity_type": row["activity_type"],
        "action": row["action"],
        "details": redact_sensitive_data(row.get("details") or {}),
        "status": row["status"],
        "created_at": row["created_at"],
    }


async def log_activity(
    activity_type: str,
    action: str,
    details: Mapping[str, Any] | None = None,
    *,
    user_id: str | None = None,
    status: ActivityStatus = "success",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Persist one redacted activity event and return its public payload."""
    if status not in ("success", "failure"):
        raise ValueError("Activity status must be success or failure")
    redacted_details = redact_sensitive_data(dict(details or {}))
    row = await db.create_agent_activity(
        activity_type=activity_type,
        action=action,
        details=redacted_details,
        user_id=user_id,
        status=status,
        created_at=created_at or _now_iso(),
    )
    return _activity_payload(row)


async def get_activities(
    *,
    activity_type: str | None = None,
    user_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return redacted activities newest-first with deterministic tie ordering."""
    rows = await db.list_agent_activities(
        activity_type=activity_type,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return [_activity_payload(row) for row in rows]