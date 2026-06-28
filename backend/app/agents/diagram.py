from __future__ import annotations

"""Diagram agent - specialized infrastructure analysis for AEGISFLOW."""

import asyncio
import random
from datetime import datetime

from app.agents.base import BaseAgent
from app.models.schemas import AgentStatus, HealthStatus, DiagramChange
from app.services.state import state
from app.services.websocket_manager import ws_manager
from app.services.cerebras import cerebras


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

            gemma_result = cerebras.ask_gemma(
                "You are a diagram visualization analyst. Output JSON with 'impact_summary' (string) describing the visual impact of changes.",
                f"""Describe the visual impact of these diagram changes:
Changes: {[{'node': c.node_id, 'property': c.property, 'new_value': c.new_value} for c in analysis.diagram_changes]}
Total Nodes: {len(arch.nodes)}
Current Healthy: {sum(1 for n in arch.nodes.values() if n.health == HealthStatus.HEALTHY)}
Current Critical: {sum(1 for n in arch.nodes.values() if n.health == HealthStatus.CRITICAL)}""",
            )
            if gemma_result:
                await self.log("info", f"Gemma 4 diagram summary: {gemma_result.get('impact_summary', '')[:100]}")

            await self.log("info", f"Diagram updated with {len(analysis.diagram_changes)} changes")

        await self.set_status(AgentStatus.IDLE)
