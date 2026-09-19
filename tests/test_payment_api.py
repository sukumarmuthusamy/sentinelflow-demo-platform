"""Tests for svc-payment-api."""

from services.svc_payment_api.checkout import process_checkout
from services.svc_payment_api.handlers import health_check


def test_health_check():
    status = health_check()
    assert status.service == "svc-payment-api"


def test_process_checkout_captures_payment():
    result = process_checkout("corr-p1", "cart-1", 4999, "tok_abc123")
    assert result.status == "captured"
    assert "order_id" in result.payload


def test_process_checkout_rejects_duplicate():
    process_checkout("corr-p2", "cart-2", 1000, "tok_dup")
    result = process_checkout("corr-p2", "cart-2", 1000, "tok_dup")
    assert result.status == "duplicate"
