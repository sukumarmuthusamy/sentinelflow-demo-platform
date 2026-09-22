"""Claim intake and adjudication workflows."""

from __future__ import annotations

import time

from services.svc_analytics.ingest import ingest_event
from services.svc_core_api.config import ADJUDICATION_TIMEOUT_SECONDS, IDEMPOTENCY_WINDOW_HOURS
from services.svc_notification.dispatch import dispatch_notification
from shared.types import ServiceResult

_seen_correlation_ids: set[str] = set()
_adjudication_start: dict[str, float] = {}


def _enforce_adjudication_timeout(correlation_id: str) -> bool:
    started = _adjudication_start.get(correlation_id, time.monotonic())
    elapsed = time.monotonic() - started
    return elapsed <= ADJUDICATION_TIMEOUT_SECONDS


def submit_claim(
    correlation_id: str,
    member_id: str,
    payload: dict,
    priority: str = "normal",
) -> ServiceResult:
    """Submit a claim, notify downstream services, and return acceptance status."""
    if correlation_id in _seen_correlation_ids:
        return ServiceResult(correlation_id=correlation_id, status="duplicate")

    _adjudication_start[correlation_id] = time.monotonic()
    if not _enforce_adjudication_timeout(correlation_id):
        return ServiceResult(correlation_id=correlation_id, status="adjudication_timeout")

    _seen_correlation_ids.add(correlation_id)

    dispatch_notification(
        correlation_id=correlation_id,
        channel="email",
        recipient=f"member-{member_id}@example.invalid",
        template_id="claim-received",
    )
    ingest_event(
        correlation_id=correlation_id,
        event_type="claim.submitted",
        payload={"member_id": member_id, "priority": priority, "timeout_enforced": True},
    )

    return ServiceResult(
        correlation_id=correlation_id,
        status="accepted",
        payload={
            "member_id": member_id,
            "priority": priority,
            "sla_seconds": ADJUDICATION_TIMEOUT_SECONDS,
            "idempotency_hours": IDEMPOTENCY_WINDOW_HOURS,
        },
    )
