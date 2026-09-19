"""Runtime configuration for svc-payment-api."""

from __future__ import annotations

# Settlement batch window closes at this hour (UTC).
SETTLEMENT_BATCH_HOUR_UTC = 2

# Maximum checkout retry attempts before fail-closed.
CHECKOUT_MAX_RETRIES = 3
