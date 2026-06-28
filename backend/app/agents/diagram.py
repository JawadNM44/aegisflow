from __future__ import annotations

"""Diagram agent - specialized infrastructure analysis for AEGISFLOW."""

import asyncio
import random
from datetime import datetime

from app.agents.base import BaseAgent
from app.models.schemas import AgentStatus, HealthStatus, DiagramChange
from app.services.state import state
from app.services.websocket_manager import ws_manager


class DiagramAgent(BaseAgent):
    def __init__(self):
        super().__init__("Diagram")

    async def _run_impl(self):
        await self.log("info", "Diagram agent started")

    async def apply_analysis(self, analysis):
        await self.set_status(AgentStatus.WORKING, "Updating architecture diagram")
        arch = await state.get_architecture()
        changes = False

        for change in analysis.diagram_changes:
            if change.node_id and change.node_id in arch.nodes:
                if change.property == "health":
                    try:
                        new_health = HealthStatus(change.new_value)
                        arch.nodes[change.node_id].health = new_health
                        changes = True
                    except ValueError:
                        pass

        if changes:
            await state.update_architecture(arch)
            await ws_manager.broadcast_event("architecture", arch.model_dump())
            await self.log("info", f"Diagram updated with {len(analysis.diagram_changes)} changes")

        await self.set_status(AgentStatus.IDLE)
