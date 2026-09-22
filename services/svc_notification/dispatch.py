"""Notification dispatch logic."""

from __future__ import annotations

from shared.types import ServiceResult

MAX_RETRY_ATTEMPTS = 5
_BACKOFF_BASE_SECONDS = 2


def _compute_backoff(attempt: int) -> int:
    return _BACKOFF_BASE_SECONDS ** attempt


def dispatch_notification(
    correlation_id: str,
    channel: str,
    recipient: str,
    template_id: str,
    attempt: int = 0,
) -> ServiceResult:
    """Dispatch a templated notification to the given channel."""
    if channel not in {"email", "sms", "push"}:
        return ServiceResult(correlation_id=correlation_id, status="invalid_channel")

    if attempt >= MAX_RETRY_ATTEMPTS:
        return ServiceResult(correlation_id=correlation_id, status="retry_exhausted")

    return ServiceResult(
        correlation_id=correlation_id,
        status="queued",
        payload={
            "channel": channel,
            "recipient": recipient,
            "template_id": template_id,
            "attempt": attempt,
            "backoff_seconds": _compute_backoff(attempt),
        },
    )
