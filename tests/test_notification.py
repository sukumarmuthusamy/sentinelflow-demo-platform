"""Tests for svc-notification."""

from services.svc_notification.dispatch import dispatch_notification
from services.svc_notification.handlers import health_check


def test_health_check():
    status = health_check()
    assert status.service == "svc-notification"


def test_dispatch_notification_queues_valid_request():
    result = dispatch_notification("corr-n1", "email", "user@example.invalid", "tpl-1")
    assert result.status == "queued"
    assert result.payload["channel"] == "email"


def test_dispatch_notification_rejects_invalid_channel():
    result = dispatch_notification("corr-n2", "fax", "user@example.invalid", "tpl-1")
    assert result.status == "invalid_channel"


def test_dispatch_notification_accepts_push_channel():
    result = dispatch_notification("corr-n3", "push", "device-1", "tpl-push")
    assert result.status == "queued"
    assert result.payload["channel"] == "push"
