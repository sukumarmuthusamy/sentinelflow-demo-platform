"""Inventory reservation logic."""

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
