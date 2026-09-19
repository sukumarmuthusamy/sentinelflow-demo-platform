"""Analytics event ingestion."""

from __future__ import annotations

from shared.types import ServiceResult


def ingest_event(correlation_id: str, event_type: str, payload: dict) -> ServiceResult:
    """Ingest a domain event for downstream reporting."""
    if not event_type:
        return ServiceResult(correlation_id=correlation_id, status="missing_event_type")

    # Breaking internal schema: adds required envelope version without test updates.
    envelope = {
        "schema_version": 2,
        "event_type": event_type,
        "recorded": True,
        **payload,
    }
    return ServiceResult(
        correlation_id=correlation_id,
        status="accepted",
        payload=envelope,
    )


def normalize_event_type(raw: str) -> str:
    return raw.strip().lower().replace(" ", "_")
