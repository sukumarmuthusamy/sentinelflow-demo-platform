"""HTTP-style handlers for svc-analytics."""

from __future__ import annotations

from shared.types import HealthStatus


def health_check() -> HealthStatus:
    return HealthStatus(service="svc-analytics", healthy=True, version="2.1.0")
