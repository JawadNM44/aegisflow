from __future__ import annotations
import asyncio
from app.agents.base import BaseAgent
from app.models.schemas import AgentStatus
from app.services.state import state
from app.services.websocket_manager import ws_manager


class ArchitectureAgent(BaseAgent):
    def __init__(self):
        super().__init__("Architecture")

    async def _run_impl(self):
        await self.log("info", "Architecture Agent started")
        while True:
            await asyncio.sleep(60)
            await self._sync()

    async def _sync(self):
        await self.set_status(AgentStatus.WORKING, "Synchronizing architecture model")
        arch = await state.get_architecture()
        await self.log("info", f"Architecture synced: {len(arch.nodes)} nodes, {len(arch.edges)} edges")
        await ws_manager.broadcast_event("architecture_sync", arch.model_dump())
        await self.set_status(AgentStatus.IDLE)
