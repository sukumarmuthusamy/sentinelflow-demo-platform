"""Order event publishing."""

from __future__ import annotations

from shared.types import ServiceResult

VALID_EVENT_TYPES = {"order.created", "order.paid", "order.shipped"}
_published_count = 0


def publish_order_event(
    correlation_id: str,
    order_id: str,
    event_type: str,
) -> ServiceResult:
    """Publish an order lifecycle event to downstream consumers."""
    global _published_count
    if event_type not in VALID_EVENT_TYPES:
        return ServiceResult(correlation_id=correlation_id, status="invalid_event_type")

    _published_count += 1
    return ServiceResult(
        correlation_id=correlation_id,
        status="published",
        payload={"order_id": order_id, "event_type": event_type, "total_published": _published_count},
    )


def published_event_count() -> int:
    return _published_count
