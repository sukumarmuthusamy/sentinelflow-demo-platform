"""HTTP-style handlers for svc-order-events."""

from __future__ import annotations

from shared.types import HealthStatus


def health_check() -> HealthStatus:
    return HealthStatus(service="svc-order-events", healthy=True, version="1.2.0")
