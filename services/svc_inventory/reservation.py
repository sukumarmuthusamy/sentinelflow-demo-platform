"""Inventory reservation logic."""

from __future__ import annotations

from shared.types import ServiceResult

# Synthetic in-memory stock ledger for demo purposes.
_STOCK: dict[str, int] = {
    "SKU-001": 100,
    "SKU-002": 50,
    "SKU-003": 25,
}


def reserve_stock(correlation_id: str, sku: str, quantity: int) -> ServiceResult:
    """Reserve inventory for a checkout cart line item."""
    available = _STOCK.get(sku, 0)
    if quantity > available:
        return ServiceResult(correlation_id=correlation_id, status="insufficient_stock")

    _STOCK[sku] = available - quantity
    return ServiceResult(
        correlation_id=correlation_id,
        status="reserved",
        payload={"sku": sku, "quantity": quantity, "remaining": _STOCK[sku]},
    )
