"""HTTP-style handlers for svc-core-api."""

from __future__ import annotations

from shared.types import HealthStatus


def health_check() -> HealthStatus:
    return HealthStatus(service="svc-core-api", healthy=True, version="2.1.0")
