"""CareerPilot audit and activity logging."""

from app.audit.event_store import get_activities, log_activity

__all__ = ["get_activities", "log_activity"]