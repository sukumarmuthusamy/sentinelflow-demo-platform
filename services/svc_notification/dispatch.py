"""Notification dispatch logic."""

from __future__ import annotations

from shared.types import ServiceResult

MAX_RETRY_ATTEMPTS = 3


def dispatch_notification(
    correlation_id: str,
    channel: str,
    recipient: str,
    template_id: str,
) -> ServiceResult:
    """Dispatch a templated notification to the given channel."""
    if channel not in {"email", "sms", "push"}:
        return ServiceResult(correlation_id=correlation_id, status="invalid_channel")

    return ServiceResult(
        correlation_id=correlation_id,
        status="queued",
        payload={
            "channel": channel,
            "recipient": recipient,
            "template_id": template_id,
        },
    )
