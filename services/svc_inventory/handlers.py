"""HTTP-style handlers for svc-inventory."""

from __future__ import annotations

from shared.types import HealthStatus


def health_check() -> HealthStatus:
    return HealthStatus(service="svc-inventory", healthy=True, version="1.4.0")
