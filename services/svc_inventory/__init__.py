"""Inventory reservation service (ecommerce-payments domain)."""

from services.svc_inventory.handlers import health_check
from services.svc_inventory.reservation import reserve_stock

__all__ = ["health_check", "reserve_stock"]
