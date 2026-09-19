"""Tests for svc-inventory."""

from services.svc_inventory.handlers import health_check
from services.svc_inventory.reservation import reserve_stock


def test_health_check():
    status = health_check()
    assert status.service == "svc-inventory"


def test_reserve_stock_succeeds_with_available_quantity():
    result = reserve_stock("corr-i1", "SKU-001", 1)
    assert result.status == "reserved"


def test_reserve_stock_fails_when_insufficient():
    result = reserve_stock("corr-i2", "SKU-UNKNOWN", 999)
    assert result.status == "insufficient_stock"
