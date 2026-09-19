"""Analytics event ingestion."""

from __future__ import annotations

from shared.types import ServiceResult


def _validate_payload(payload: dict) -> bool:
    return isinstance(payload, dict)


def ingest_event(correlation_id: str, event_type: str, payload: dict) -> ServiceResult:
    """Ingest a domain event for downstream reporting."""
    if not event_type:
        return ServiceResult(correlation_id=correlation_id, status="missing_event_type")
    if not _validate_payload(payload):
        return ServiceResult(correlation_id=correlation_id, status="invalid_payload")

    return ServiceResult(
        correlation_id=correlation_id,
        status="accepted",
        payload={"event_type": event_type, "recorded": True, **payload},
    )


def normalize_event_type(raw: str) -> str:
    """Normalize event type strings for consistent aggregation."""
    return raw.strip().lower().replace(" ", "_")
