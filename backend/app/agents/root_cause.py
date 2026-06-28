from __future__ import annotations

"""Root_Cause agent - specialized infrastructure analysis for AEGISFLOW."""

import asyncio
from app.agents.base import BaseAgent
from app.models.schemas import AgentStatus, IncidentStatus, TimelineEvent, InfrastructureEvent
from app.services.state import state
from app.services.websocket_manager import ws_manager
from app.services.cerebras import cerebras


class RootCauseAgent(BaseAgent):
    def __init__(self):
        super().__init__("RootCause")

    async def _run_impl(self):
        await self.log("info", "Root Cause Agent started")

    async def investigate(self, event: InfrastructureEvent):
        await self.set_status(AgentStatus.WORKING, f"Investigating: {event.title}")
        await self.log("info", f"Deep investigation started for: {event.title}")

        arch = await state.get_architecture()
        arch_dict = arch.model_dump()
        event_dict = event.model_dump()
        event_dict["investigation_depth"] = "full"
        event_dict["title"] = f"Deep investigation: {event.title}"
        analysis = cerebras.analyze_event(event_dict, arch_dict)

        incidents = await state.get_incidents()
        for inc in incidents:
            if inc.event_id == event.id:
                inc.status = IncidentStatus.MITIGATING
                inc.root_cause = analysis.probable_root_cause
                inc.confidence = analysis.confidence
                inc.timeline.append(
                    TimelineEvent(type="deep_investigation", message=f"Root cause investigation: {analysis.probable_root_cause[:80]}", actor="root_cause_agent")
                )
                await state.update_incident(inc)
                await ws_manager.broadcast_event("incident", inc.model_dump())
                break

        await self.log("info", f"Root cause determined: {analysis.probable_root_cause[:80]}")
        await self.set_status(AgentStatus.IDLE)
