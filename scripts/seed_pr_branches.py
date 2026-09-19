#!/usr/bin/env python3
"""Create labeled demo PR branches for SentinelFlow live-mode evaluation.

Run from repo root after the baseline main branch is committed:
    python scripts/seed_pr_branches.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        check=check,
        text=True,
        capture_output=True,
    )


def git(*args: str) -> None:
    result = run("git", *args)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)


def write(path: str, content: str) -> None:
    full = REPO_ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8", newline="\n")


def append(path: str, content: str) -> None:
    full = REPO_ROOT / path
    existing = full.read_text(encoding="utf-8") if full.exists() else ""
    full.write_text(existing + content, encoding="utf-8", newline="\n")


def create_branch(branch: str, message: str, edits: list[tuple[str, str]]) -> None:
    git("checkout", "main")
    git("checkout", "-B", branch)
    for path, content in edits:
        write(path, content)
    paths = " ".join(f'"{p}"' for p, _ in edits)
    run("git", "add", *[p for p, _ in edits])
    git("commit", "-m", message)
    print(f"  created {branch}")


def main() -> int:
    if not (REPO_ROOT / ".git").exists():
        print("Error: run git init and commit baseline on main first.", file=sys.stderr)
        return 1

    git("checkout", "main")

    # --- PASS scenarios ---
    create_branch(
        "pr/001-docs-analytics",
        "docs: expand analytics documentation",
        [
            (
                "analytics_docs/readme.py",
                '''"""Analytics documentation strings (non-production code path)."""

README = """
# Analytics Service Documentation

Synthetic documentation for svc-analytics reporting pipelines.
This module is intentionally non-code and should not affect blast radius.

## Reporting cadence
- Daily aggregate rollups at 02:00 UTC
- Weekly payer mix reports on Mondays
"""
''',
            ),
        ],
    )

    create_branch(
        "pr/002-docs-inventory",
        "docs: add inventory reservation troubleshooting section",
        [
            (
                "docs/inventory-guide.md",
                """# Inventory Service Guide

Operational guide for `svc-inventory` reservation workflows.

## Reservation flow

1. Payment API calls `reserve_stock()` during checkout.
2. Stock is decremented atomically in the in-memory ledger.
3. Insufficient stock returns HTTP 409 equivalent status.

## Troubleshooting oversell alerts

If reservation failures spike during checkout:
- Verify payment API is not bypassing reservation on retry.
- Check SKU-001 ledger balance against warehouse feed.

This is synthetic documentation for SentinelFlow demo purposes.
""",
            ),
        ],
    )

    create_branch(
        "pr/003-notification-logging",
        "feat(notification): add structured dispatch logging with tests",
        [
            (
                "services/svc_notification/dispatch.py",
                '''"""Notification dispatch logic."""

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
''',
            ),
            (
                "tests/test_notification.py",
                '''"""Tests for svc-notification."""

from services.svc_notification.dispatch import dispatch_notification
from services.svc_notification.handlers import health_check


def test_health_check():
    status = health_check()
    assert status.service == "svc-notification"


def test_dispatch_notification_queues_valid_request():
    result = dispatch_notification("corr-n1", "email", "user@example.invalid", "tpl-1")
    assert result.status == "queued"
    assert result.payload["channel"] == "email"


def test_dispatch_notification_rejects_invalid_channel():
    result = dispatch_notification("corr-n2", "fax", "user@example.invalid", "tpl-1")
    assert result.status == "invalid_channel"


def test_dispatch_notification_accepts_push_channel():
    result = dispatch_notification("corr-n3", "push", "device-1", "tpl-push")
    assert result.status == "queued"
    assert result.payload["channel"] == "push"
''',
            ),
        ],
    )

    create_branch(
        "pr/004-order-events-metrics",
        "feat(order-events): expose published event counter with tests",
        [
            (
                "services/svc_order_events/publish.py",
                '''"""Order event publishing."""

from __future__ import annotations

from shared.types import ServiceResult

VALID_EVENT_TYPES = {"order.created", "order.paid", "order.shipped"}
_published_count = 0


def publish_order_event(
    correlation_id: str,
    order_id: str,
    event_type: str,
) -> ServiceResult:
    """Publish an order lifecycle event to downstream consumers."""
    global _published_count
    if event_type not in VALID_EVENT_TYPES:
        return ServiceResult(correlation_id=correlation_id, status="invalid_event_type")

    _published_count += 1
    return ServiceResult(
        correlation_id=correlation_id,
        status="published",
        payload={"order_id": order_id, "event_type": event_type, "total_published": _published_count},
    )


def published_event_count() -> int:
    return _published_count
''',
            ),
            (
                "tests/test_order_events.py",
                '''"""Tests for svc-order-events."""

from services.svc_order_events.handlers import health_check
from services.svc_order_events.publish import publish_order_event, published_event_count


def test_health_check():
    status = health_check()
    assert status.service == "svc-order-events"


def test_publish_order_event_accepts_valid_type():
    result = publish_order_event("corr-o1", "ord-1", "order.created")
    assert result.status == "published"


def test_publish_order_event_rejects_invalid_type():
    result = publish_order_event("corr-o2", "ord-2", "order.cancelled")
    assert result.status == "invalid_event_type"


def test_published_event_count_increments():
    before = published_event_count()
    publish_order_event("corr-o3", "ord-3", "order.paid")
    assert published_event_count() == before + 1
''',
            ),
        ],
    )

    create_branch(
        "pr/005-analytics-refactor",
        "refactor(analytics): extract payload validation helper with tests",
        [
            (
                "services/svc_analytics/ingest.py",
                '''"""Analytics event ingestion."""

from __future__ import annotations

from shared.types import ServiceResult


def _validate_payload(payload: dict) -> bool:
    return isinstance(payload, dict)


def ingest_event(correlation_id: str, event_type: str, payload: dict) -> ServiceResult:
    """Ingest a domain event for downstream reporting."""
    if not event_type:
        return ServiceResult(correlation_id=correlation_id, status="missing_event_type")
    if not _validate_payload(payload):
        return ServiceResult(correlation_id=correlation_id, status="invalid_payload")

    return ServiceResult(
        correlation_id=correlation_id,
        status="accepted",
        payload={"event_type": event_type, "recorded": True, **payload},
    )


def normalize_event_type(raw: str) -> str:
    """Normalize event type strings for consistent aggregation."""
    return raw.strip().lower().replace(" ", "_")
''',
            ),
            (
                "tests/test_analytics.py",
                '''"""Tests for svc-analytics."""

from services.svc_analytics.handlers import health_check
from services.svc_analytics.ingest import ingest_event, normalize_event_type


def test_health_check():
    status = health_check()
    assert status.service == "svc-analytics"


def test_ingest_event_accepts_valid_payload():
    result = ingest_event("corr-a1", "claim.submitted", {"count": 1})
    assert result.status == "accepted"


def test_normalize_event_type():
    assert normalize_event_type(" Claim Submitted ") == "claim_submitted"


def test_ingest_event_rejects_empty_event_type():
    result = ingest_event("corr-a2", "", {"count": 1})
    assert result.status == "missing_event_type"
''',
            ),
        ],
    )

    create_branch(
        "pr/006-core-api-config-comment",
        "chore(core-api): document idempotency window in config",
        [
            (
                "services/svc_core_api/config.py",
                '''"""Runtime configuration for svc-core-api."""

from __future__ import annotations

# Adjudication SLA in seconds before fail-closed timeout.
ADJUDICATION_TIMEOUT_SECONDS = 30

# Idempotency window for duplicate claim detection.
# Claims with the same correlation_id within this window are rejected.
IDEMPOTENCY_WINDOW_HOURS = 24
''',
            ),
        ],
    )

    # --- BLOCK: breaking contracts ---
    create_branch(
        "pr/007-breaking-core-api-contract",
        "feat(core-api)!: remove required member_id from claim submit contract",
        [
            (
                "contracts/svc-core-api.yaml",
                '''openapi: 3.1.0
info:
  title: svc-core-api contract
  version: 2.2.0
  x-effective-date: '2026-01-15'
  description: Synthetic OpenAPI contract for svc-core-api.
paths:
  /v1/core-api/health:
    get:
      operationId: svc-core-api_health
      summary: Health check
      responses:
        '200':
          description: OK
  /v1/core-api/claims/submit:
    post:
      operationId: svc-core-api_submit_claim
      summary: Submit a claim for adjudication
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ClaimSubmitRequest'
      responses:
        '202':
          description: Accepted
components:
  schemas:
    ClaimSubmitRequest:
      type: object
      required:
        - correlation_id
        - payload
      properties:
        correlation_id:
          type: string
        payload:
          type: object
        priority:
          type: string
          enum:
            - normal
            - urgent
''',
            ),
        ],
    )

    create_branch(
        "pr/008-breaking-payment-api-contract",
        "feat(payment-api)!: change checkout response from 202 to 200",
        [
            (
                "contracts/svc-payment-api.yaml",
                '''openapi: 3.1.0
info:
  title: svc-payment-api contract
  version: 3.1.0
  x-effective-date: '2026-01-15'
  description: Synthetic OpenAPI contract for svc-payment-api.
paths:
  /v1/payment-api/health:
    get:
      operationId: svc-payment-api_health
      summary: Health check
      responses:
        '200':
          description: OK
  /v1/payment-api/checkout:
    post:
      operationId: svc-payment-api_checkout
      summary: Authorize and capture a checkout payment
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CheckoutRequest'
      responses:
        '200':
          description: Captured immediately
components:
  schemas:
    CheckoutRequest:
      type: object
      required:
        - correlation_id
        - cart_id
        - amount_cents
        - payment_method_token
      properties:
        correlation_id:
          type: string
        cart_id:
          type: string
        amount_cents:
          type: integer
        payment_method_token:
          type: string
''',
            ),
        ],
    )

    create_branch(
        "pr/009-breaking-notification-contract",
        "feat(notification)!: rename dispatch operationId breaking clients",
        [
            (
                "contracts/svc-notification.yaml",
                '''openapi: 3.1.0
info:
  title: svc-notification contract
  version: 2.2.0
  x-effective-date: '2026-01-15'
  description: Synthetic OpenAPI contract for svc-notification.
paths:
  /v1/notification/health:
    get:
      operationId: svc-notification_health
      summary: Health check
      responses:
        '200':
          description: OK
  /v1/notification/dispatch:
    post:
      operationId: svc-notification_send_v2
      summary: Dispatch a notification
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DispatchRequest'
      responses:
        '202':
          description: Accepted
components:
  schemas:
    DispatchRequest:
      type: object
      required:
        - correlation_id
        - channel
        - recipient
        - template_id
      properties:
        correlation_id:
          type: string
        channel:
          type: string
        recipient:
          type: string
        template_id:
          type: string
''',
            ),
        ],
    )

    # --- BLOCK: secrets ---
    create_branch(
        "pr/010-aws-secret-core-api",
        "chore(core-api): add AWS credentials for demo migration",
        [
            (
                "services/svc_core_api/config.py",
                '''"""Runtime configuration for svc-core-api."""

from __future__ import annotations

# Adjudication SLA in seconds before fail-closed timeout.
ADJUDICATION_TIMEOUT_SECONDS = 30

# Idempotency window for duplicate claim detection.
IDEMPOTENCY_WINDOW_HOURS = 24

# SYNTHETIC SECRET FOR SENTINELFLOW EVAL — NOT A REAL CREDENTIAL
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
''',
            ),
        ],
    )

    create_branch(
        "pr/011-github-token-payment",
        "chore(payment-api): add processor API token for sandbox",
        [
            (
                "services/svc_payment_api/config.py",
                '''"""Runtime configuration for svc-payment-api."""

from __future__ import annotations

# Settlement batch window closes at this hour (UTC).
SETTLEMENT_BATCH_HOUR_UTC = 2

# Maximum checkout retry attempts before fail-closed.
CHECKOUT_MAX_RETRIES = 3

# SYNTHETIC SECRET FOR SENTINELFLOW EVAL — NOT A REAL CREDENTIAL
PAYMENT_PROCESSOR_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz12"
''',
            ),
        ],
    )

    create_branch(
        "pr/012-private-key-notification",
        "chore(notification): add signing key for webhook verification",
        [
            (
                "services/svc_notification/signing.py",
                '''"""Webhook signing helpers."""

from __future__ import annotations

# SYNTHETIC SECRET FOR SENTINELFLOW EVAL — NOT A REAL CREDENTIAL
WEBHOOK_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN
OPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQR
STUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV
-----END RSA PRIVATE KEY-----"""


def sign_payload(payload: str) -> str:
    return f"signed:{hash(payload)}"
''',
            ),
        ],
    )

    # --- REVIEW: inadequate test coverage ---
    create_branch(
        "pr/013-core-api-adjudication-logic",
        "feat(core-api): add adjudication timeout enforcement without tests",
        [
            (
                "services/svc_core_api/claims.py",
                '''"""Claim intake and adjudication workflows."""

from __future__ import annotations

import time

from services.svc_analytics.ingest import ingest_event
from services.svc_core_api.config import ADJUDICATION_TIMEOUT_SECONDS, IDEMPOTENCY_WINDOW_HOURS
from services.svc_notification.dispatch import dispatch_notification
from shared.types import ServiceResult

_seen_correlation_ids: set[str] = set()
_adjudication_start: dict[str, float] = {}


def _enforce_adjudication_timeout(correlation_id: str) -> bool:
    started = _adjudication_start.get(correlation_id, time.monotonic())
    elapsed = time.monotonic() - started
    return elapsed <= ADJUDICATION_TIMEOUT_SECONDS


def submit_claim(
    correlation_id: str,
    member_id: str,
    payload: dict,
    priority: str = "normal",
) -> ServiceResult:
    """Submit a claim, notify downstream services, and return acceptance status."""
    if correlation_id in _seen_correlation_ids:
        return ServiceResult(correlation_id=correlation_id, status="duplicate")

    _adjudication_start[correlation_id] = time.monotonic()
    if not _enforce_adjudication_timeout(correlation_id):
        return ServiceResult(correlation_id=correlation_id, status="adjudication_timeout")

    _seen_correlation_ids.add(correlation_id)

    dispatch_notification(
        correlation_id=correlation_id,
        channel="email",
        recipient=f"member-{member_id}@example.invalid",
        template_id="claim-received",
    )
    ingest_event(
        correlation_id=correlation_id,
        event_type="claim.submitted",
        payload={"member_id": member_id, "priority": priority, "timeout_enforced": True},
    )

    return ServiceResult(
        correlation_id=correlation_id,
        status="accepted",
        payload={
            "member_id": member_id,
            "priority": priority,
            "sla_seconds": ADJUDICATION_TIMEOUT_SECONDS,
            "idempotency_hours": IDEMPOTENCY_WINDOW_HOURS,
        },
    )
''',
            ),
        ],
    )

    create_branch(
        "pr/014-cross-service-analytics-change",
        "feat(analytics): change event schema consumed by notification templates",
        [
            (
                "services/svc_analytics/ingest.py",
                '''"""Analytics event ingestion."""

from __future__ import annotations

from shared.types import ServiceResult


def ingest_event(correlation_id: str, event_type: str, payload: dict) -> ServiceResult:
    """Ingest a domain event for downstream reporting."""
    if not event_type:
        return ServiceResult(correlation_id=correlation_id, status="missing_event_type")

    # Breaking internal schema: adds required envelope version without test updates.
    envelope = {
        "schema_version": 2,
        "event_type": event_type,
        "recorded": True,
        **payload,
    }
    return ServiceResult(
        correlation_id=correlation_id,
        status="accepted",
        payload=envelope,
    )


def normalize_event_type(raw: str) -> str:
    return raw.strip().lower().replace(" ", "_")
''',
            ),
            (
                "services/svc_notification/dispatch.py",
                '''"""Notification dispatch logic."""

from __future__ import annotations

from shared.types import ServiceResult

MAX_RETRY_ATTEMPTS = 3


def dispatch_notification(
    correlation_id: str,
    channel: str,
    recipient: str,
    template_id: str,
) -> ServiceResult:
    """Dispatch a templated notification to the given channel."""
    if channel not in {"email", "sms", "push"}:
        return ServiceResult(correlation_id=correlation_id, status="invalid_channel")

    # Now expects analytics schema_version=2 in upstream payloads.
    required_schema_version = 2
    return ServiceResult(
        correlation_id=correlation_id,
        status="queued",
        payload={
            "channel": channel,
            "recipient": recipient,
            "template_id": template_id,
            "required_schema_version": required_schema_version,
        },
    )
''',
            ),
        ],
    )

    create_branch(
        "pr/015-payment-capture-flow",
        "feat(payment-api): add partial capture path with minimal test updates",
        [
            (
                "services/svc_payment_api/checkout.py",
                '''"""Checkout authorization and capture."""

from __future__ import annotations

from services.svc_inventory.reservation import reserve_stock
from services.svc_order_events.publish import publish_order_event
from services.svc_payment_api.config import CHECKOUT_MAX_RETRIES, SETTLEMENT_BATCH_HOUR_UTC
from shared.types import ServiceResult

_processed_checkouts: set[str] = set()


def process_checkout(
    correlation_id: str,
    cart_id: str,
    amount_cents: int,
    payment_method_token: str,
    sku: str = "SKU-001",
    quantity: int = 1,
    partial_capture: bool = False,
) -> ServiceResult:
    """Authorize payment, reserve inventory, and publish order events."""
    if correlation_id in _processed_checkouts:
        return ServiceResult(correlation_id=correlation_id, status="duplicate")

    reservation = reserve_stock(correlation_id, sku, quantity)
    if reservation.status != "reserved":
        return reservation

    _processed_checkouts.add(correlation_id)
    order_id = f"ord-{cart_id}"

    publish_order_event(correlation_id, order_id, "order.created")
    capture_status = "partial_captured" if partial_capture else "captured"
    if not partial_capture:
        publish_order_event(correlation_id, order_id, "order.paid")

    return ServiceResult(
        correlation_id=correlation_id,
        status=capture_status,
        payload={
            "cart_id": cart_id,
            "amount_cents": amount_cents,
            "order_id": order_id,
            "partial_capture": partial_capture,
            "settlement_hour_utc": SETTLEMENT_BATCH_HOUR_UTC,
            "max_retries": CHECKOUT_MAX_RETRIES,
            "token_prefix": payment_method_token[:4],
        },
    )
''',
            ),
        ],
    )

    create_branch(
        "pr/016-order-events-schema-change",
        "feat(order-events): add order.refunded event type without contract/test sync",
        [
            (
                "services/svc_order_events/publish.py",
                '''"""Order event publishing."""

from __future__ import annotations

from shared.types import ServiceResult

VALID_EVENT_TYPES = {"order.created", "order.paid", "order.shipped", "order.refunded"}


def publish_order_event(
    correlation_id: str,
    order_id: str,
    event_type: str,
) -> ServiceResult:
    """Publish an order lifecycle event to downstream consumers."""
    if event_type not in VALID_EVENT_TYPES:
        return ServiceResult(correlation_id=correlation_id, status="invalid_event_type")

    return ServiceResult(
        correlation_id=correlation_id,
        status="published",
        payload={"order_id": order_id, "event_type": event_type, "refund_capable": True},
    )
''',
            ),
        ],
    )

    create_branch(
        "pr/017-notification-retry-logic",
        "feat(notification): implement exponential backoff retries without tests",
        [
            (
                "services/svc_notification/dispatch.py",
                '''"""Notification dispatch logic."""

from __future__ import annotations

from shared.types import ServiceResult

MAX_RETRY_ATTEMPTS = 5
_BACKOFF_BASE_SECONDS = 2


def _compute_backoff(attempt: int) -> int:
    return _BACKOFF_BASE_SECONDS ** attempt


def dispatch_notification(
    correlation_id: str,
    channel: str,
    recipient: str,
    template_id: str,
    attempt: int = 0,
) -> ServiceResult:
    """Dispatch a templated notification to the given channel."""
    if channel not in {"email", "sms", "push"}:
        return ServiceResult(correlation_id=correlation_id, status="invalid_channel")

    if attempt >= MAX_RETRY_ATTEMPTS:
        return ServiceResult(correlation_id=correlation_id, status="retry_exhausted")

    return ServiceResult(
        correlation_id=correlation_id,
        status="queued",
        payload={
            "channel": channel,
            "recipient": recipient,
            "template_id": template_id,
            "attempt": attempt,
            "backoff_seconds": _compute_backoff(attempt),
        },
    )
''',
            ),
        ],
    )

    create_branch(
        "pr/018-inventory-reservation-change",
        "feat(inventory): add soft-reservation TTL without adequate regression tests",
        [
            (
                "services/svc_inventory/reservation.py",
                '''"""Inventory reservation logic."""

from __future__ import annotations

from shared.types import ServiceResult

_STOCK: dict[str, int] = {
    "SKU-001": 100,
    "SKU-002": 50,
    "SKU-003": 25,
}
_SOFT_RESERVATIONS: dict[str, tuple[int, int]] = {}

SOFT_RESERVATION_TTL_SECONDS = 900


def reserve_stock(correlation_id: str, sku: str, quantity: int, soft: bool = False) -> ServiceResult:
    """Reserve inventory for a checkout cart line item."""
    available = _STOCK.get(sku, 0)
    if quantity > available:
        return ServiceResult(correlation_id=correlation_id, status="insufficient_stock")

    if soft:
        _SOFT_RESERVATIONS[correlation_id] = (quantity, SOFT_RESERVATION_TTL_SECONDS)
        return ServiceResult(
            correlation_id=correlation_id,
            status="soft_reserved",
            payload={"sku": sku, "quantity": quantity, "ttl_seconds": SOFT_RESERVATION_TTL_SECONDS},
        )

    _STOCK[sku] = available - quantity
    return ServiceResult(
        correlation_id=correlation_id,
        status="reserved",
        payload={"sku": sku, "quantity": quantity, "remaining": _STOCK[sku]},
    )
''',
            ),
        ],
    )

    git("checkout", "main")
    print("\nAll 18 demo PR branches created. Run scripts/create_demo_prs.ps1 after pushing to GitHub.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
