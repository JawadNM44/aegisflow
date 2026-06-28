"""Integration tests for AEGISFLOW observability platform."""
import httpx
import pytest

BASE = "http://localhost:8000"

@pytest.mark.asyncio
async def test_health():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["nodes"] > 0

@pytest.mark.asyncio
async def test_architecture():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/api/v1/architecture")
        assert r.status_code == 200
        data = r.json()
        assert "nodes" in data
        assert "edges" in data

@pytest.mark.asyncio
async def test_agents():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/api/v1/agents")
        assert r.status_code == 200
        agents = r.json()
        assert len(agents) >= 11
