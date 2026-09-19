"""Tests for svc-core-api."""

from services.svc_core_api.claims import submit_claim
from services.svc_core_api.handlers import health_check


def test_health_check():
    status = health_check()
    assert status.service == "svc-core-api"
    assert status.healthy is True


def test_submit_claim_accepts_new_request():
    result = submit_claim("corr-1", "M-100", {"diagnosis": "Z00"})
    assert result.status == "accepted"
    assert result.payload["member_id"] == "M-100"


def test_submit_claim_rejects_duplicate():
    submit_claim("corr-dup", "M-101", {})
    result = submit_claim("corr-dup", "M-101", {})
    assert result.status == "duplicate"
