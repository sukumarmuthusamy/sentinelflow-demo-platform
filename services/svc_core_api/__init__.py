"""Core claims API service (healthcare-claims domain)."""

from services.svc_core_api.claims import submit_claim
from services.svc_core_api.handlers import health_check

__all__ = ["health_check", "submit_claim"]
