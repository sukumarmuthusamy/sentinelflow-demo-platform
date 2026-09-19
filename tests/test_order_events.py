"""Tests for svc-order-events."""

from services.svc_order_events.handlers import health_check
from services.svc_order_events.publish import publish_order_event


def test_health_check():
    status = health_check()
    assert status.service == "svc-order-events"


def test_publish_order_event_accepts_valid_type():
    result = publish_order_event("corr-o1", "ord-1", "order.created")
    assert result.status == "published"


def test_publish_order_event_rejects_invalid_type():
    result = publish_order_event("corr-o2", "ord-2", "order.cancelled")
    assert result.status == "invalid_event_type"
