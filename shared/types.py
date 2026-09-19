"""Common datatypes used across demo services."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ServiceResult:
    """Standard result envelope for cross-service calls."""

    correlation_id: str
    status: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HealthStatus:
    service: str
    healthy: bool
    version: str
