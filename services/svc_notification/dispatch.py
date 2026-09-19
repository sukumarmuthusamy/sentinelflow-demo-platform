"""Notification dispatch logic."""

from __future__ import annotations

import logging

from shared.types import ServiceResult

logger = logging.getLogger(__name__)
MAX_RETRY_ATTEMPTS = 3


def dispatch_notification(
    correlation_id: str,
    channel: str,
    recipient: str,
    template_id: str,
) -> ServiceResult:
    """Dispatch a templated notification to the given channel."""
    if channel not in {"email", "sms", "push"}:
        logger.warning("invalid channel=%s correlation_id=%s", channel, correlation_id)
        return ServiceResult(correlation_id=correlation_id, status="invalid_channel")

    logger.info(
        "dispatch queued channel=%s template=%s correlation_id=%s",
        channel,
        template_id,
        correlation_id,
    )
    return ServiceResult(
        correlation_id=correlation_id,
        status="queued",
        payload={
            "channel": channel,
            "recipient": recipient,
            "template_id": template_id,
        },
    )
