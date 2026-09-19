"""Analytics ingestion service (healthcare-claims domain)."""

from services.svc_analytics.handlers import health_check
from services.svc_analytics.ingest import ingest_event

__all__ = ["health_check", "ingest_event"]
