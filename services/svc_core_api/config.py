"""Runtime configuration for svc-core-api."""

from __future__ import annotations

# Adjudication SLA in seconds before fail-closed timeout.
ADJUDICATION_TIMEOUT_SECONDS = 30

# Idempotency window for duplicate claim detection.
# Claims with the same correlation_id within this window are rejected.
IDEMPOTENCY_WINDOW_HOURS = 24
