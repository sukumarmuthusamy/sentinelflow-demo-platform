"""HTTP-style handlers for svc-payment-api."""

from __future__ import annotations

from shared.types import HealthStatus


def health_check() -> HealthStatus:
    return HealthStatus(service="svc-payment-api", healthy=True, version="3.0.0")
