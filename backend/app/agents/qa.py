from __future__ import annotations

"""Qa agent - specialized infrastructure analysis for AEGISFLOW."""

import asyncio
from app.agents.base import BaseAgent
from app.models.schemas import AgentStatus, HealthStatus
from app.services.state import state
from app.services.websocket_manager import ws_manager


class QAAgent(BaseAgent):
    def __init__(self):
        super().__init__("QA")

    async def _run_impl(self):
        await self.log("info", "QA Agent started")
        while True:
            await asyncio.sleep(30)
            await self._validate()

    async def _validate(self):
        await self.set_status(AgentStatus.WORKING, "Validating system integrity")
        arch = await state.get_architecture()

        issues = []
        for nid, node in arch.nodes.items():
            if node.health == HealthStatus.CRITICAL:
                issues.append(f"{node.name} is CRITICAL")
            elif node.health == HealthStatus.OFFLINE:
                issues.append(f"{node.name} is OFFLINE")

        orphans = []
        connected_nodes = set()
        for edge in arch.edges.values():
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)
        for nid in arch.nodes:
            if nid not in connected_nodes:
                orphans.append(arch.nodes[nid].name)

        report = {
            "total_nodes": len(arch.nodes),
            "total_edges": len(arch.edges),
            "issues": issues,
            "orphans": orphans,
            "healthy": sum(1 for n in arch.nodes.values() if n.health == HealthStatus.HEALTHY),
        }

        if issues:
            await self.log("warning", f"Integrity issues: {len(issues)} problems found", report)
        elif orphans:
            await self.log("warning", f"Orphaned nodes: {orphans}", report)
        else:
            await self.log("info", "System integrity check passed", report)

        await ws_manager.broadcast_event("qa_report", report)
        await self.set_status(AgentStatus.IDLE)
