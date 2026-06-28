"""Tests for Cerebras client JSON repair and fallback logic."""
from app.services.cerebras import CerebrasClient

client = CerebrasClient()

def test_repair_affected_systems():
    parsed = {"affected_systems": {"db-1": "critical", "api-1": "warning"}}
    repaired = client._repair_json(parsed, {})
    assert isinstance(repaired["affected_systems"], list)
    assert "db-1" in repaired["affected_systems"]

def test_repair_missing_remediation():
    parsed = {"severity": "sev1"}
    repaired = client._repair_json(parsed, {"severity": "critical"})
    assert isinstance(repaired["recommended_remediation"], list)
