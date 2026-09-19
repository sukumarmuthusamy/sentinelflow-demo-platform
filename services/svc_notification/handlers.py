"""HTTP-style handlers for svc-notification."""

from __future__ import annotations

from shared.types import HealthStatus


def health_check() -> HealthStatus:
    return HealthStatus(service="svc-notification", healthy=True, version="2.1.0")
