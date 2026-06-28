"""Watcher agent - specialized infrastructure analysis for AEGISFLOW."""
from __future__ import annotations
import asyncio
from app.agents.base import BaseAgent
from app.models.schemas import AgentStatus, HealthStatus, TimelineEvent
from app.services.state import state
from app.services.websocket_manager import ws_manager


class WatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__("Watcher")

    async def _run_impl(self):
        await self.log("info", "Watcher agent started")
        while True:
            await asyncio.sleep(15)
            await self._poll()
            await asyncio.sleep(15)

    async def _poll(self):
        await self.set_status(AgentStatus.WORKING, "Polling infrastructure")
        await self.log("info", "Infrastructure health check complete")
        healthy_count = sum(1 for n in state.architecture.nodes.values() if n.health == HealthStatus.HEALTHY)
        total_count = len(state.architecture.nodes)
        await self.log("info", f"Health: {healthy_count}/{total_count} services healthy")
        await ws_manager.broadcast_event("health_check", {
            "healthy": healthy_count,
            "total": total_count,
        })
        await self.set_status(AgentStatus.IDLE)
