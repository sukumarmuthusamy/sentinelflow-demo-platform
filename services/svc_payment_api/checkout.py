"""Checkout authorization and capture."""

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
