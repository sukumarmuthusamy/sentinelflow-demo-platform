"""Tests for svc-analytics."""

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
