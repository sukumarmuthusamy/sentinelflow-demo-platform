"""Smoke tests ensuring OpenAPI contract files exist and are parseable."""

from pathlib import Path

import yaml

CONTRACTS_DIR = Path(__file__).resolve().parents[1] / "contracts"

EXPECTED_CONTRACTS = [
    "svc-core-api.yaml",
    "svc-analytics.yaml",
    "svc-notification.yaml",
    "svc-payment-api.yaml",
    "svc-inventory.yaml",
    "svc-order-events.yaml",
]


def test_all_contract_files_exist():
    for name in EXPECTED_CONTRACTS:
        path = CONTRACTS_DIR / name
        assert path.exists(), f"Missing contract: {name}"


def test_contracts_are_valid_yaml():
    for name in EXPECTED_CONTRACTS:
        data = yaml.safe_load((CONTRACTS_DIR / name).read_text(encoding="utf-8"))
        assert data["openapi"].startswith("3.")
        assert "paths" in data
