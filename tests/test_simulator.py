"""Tests for the infrastructure failure simulator."""
import pytest
from app.models.schemas import EventType, EventSeverity, HealthStatus
from app.models.events import EventBus
from app.services.state import state
from app.services.simulator import simulator

@pytest.mark.asyncio
async def test_failure_injection():
    result = await simulator.inject_failure("PostgreSQL", "critical")
    assert result["success"] is True
    node_id = "db-1"
    assert state.architecture.nodes[node_id].health == HealthStatus.CRITICAL

@pytest.mark.asyncio
async def test_service_restore():
    await simulator.inject_failure("Redis", "warning")
    result = await simulator.restore_service("redis")
    assert result["success"] is True
