"""Notification dispatch service (healthcare-claims domain)."""

from services.svc_notification.dispatch import dispatch_notification
from services.svc_notification.handlers import health_check

__all__ = ["dispatch_notification", "health_check"]
