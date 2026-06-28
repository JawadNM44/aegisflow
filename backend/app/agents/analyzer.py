from __future__ import annotations

"""Analyzer agent - specialized infrastructure analysis for AEGISFLOW."""

import asyncio
import json
from datetime import datetime

from app.agents.base import BaseAgent
from app.models.schemas import (
    AgentStatus, Incident, IncidentStatus, GemmaAnalysis, TimelineEvent,
    EventSeverity
)
from app.models.events import EventBus
from app.services.state import state
from app.services.cerebras import cerebras
from app.services.websocket_manager import ws_manager
from app.models.schemas import InfrastructureEvent


class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Analyzer")
        self._analysis_queue: asyncio.Queue = asyncio.Queue()

    async def invoke_analysis(self, event: InfrastructureEvent):
        await self._analysis_queue.put(event)

    async def _run_impl(self):
        await self.log("info", "Analyzer agent started (powered by Gemma 4 on Cerebras)")

        while True:
            try:
                event = await asyncio.wait_for(self._analysis_queue.get(), timeout=1.0)
                await self._analyze(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                await self.log("error", f"Analysis error: {e}")

    async def _on_event(self, event):
        if event.requires_analysis and event.severity in (EventSeverity.WARNING, EventSeverity.CRITICAL):
            await self.invoke_analysis(event)

    async def _analyze(self, event: InfrastructureEvent):
        await self.set_status(AgentStatus.WORKING, f"Analyzing: {event.title}")
        await self.log("info", f"Analyzing event: {event.title}", {"event_id": event.id})
        await asyncio.sleep(0.5)

        arch_data = await state.get_architecture()
        event_data = event.model_dump()
        arch_dict = arch_data.model_dump()

        analysis = cerebras.analyze_event(event_data, arch_dict)

        await self.log("info",
            f"Analysis complete: severity={analysis.severity}, confidence={analysis.confidence}",
            {"root_cause": analysis.probable_root_cause[:100]}
        )

        severity_map = {"sev1": EventSeverity.CRITICAL, "sev2": EventSeverity.WARNING,
                        "sev3": EventSeverity.INFO, "sev4": EventSeverity.INFO}

        incident = Incident(
            id=f"inc-{event.id}",
            title=event.title,
            severity=analysis.severity,
            status=IncidentStatus.INVESTIGATING,
            root_cause=analysis.probable_root_cause,
            confidence=analysis.confidence,
            affected_systems=analysis.affected_systems,
            blast_radius=analysis.affected_systems[:],
            remediation=analysis.recommended_remediation,
            requires_approval=analysis.requires_human_approval,
            ai_analysis=analysis,
            event_id=event.id,
            timeline=[
                TimelineEvent(type="event_received", message=f"Event: {event.title}", actor="system"),
                TimelineEvent(type="ai_analysis", message=f"Gemma 4 analysis: {analysis.severity}", actor="ai"),
                TimelineEvent(type="root_cause", message=f"Root cause: {analysis.probable_root_cause[:80]}", actor="ai"),
            ],
        )
        await state.add_incident(incident)
        await ws_manager.broadcast_event("incident", incident.model_dump())
        await ws_manager.broadcast_event("analysis", analysis.model_dump())
        await ws_manager.broadcast_event("architecture", arch_data.model_dump())

        from app.agents import orchestrator as agent_orch
        diagram_agent = agent_orch.agents.get("Diagram")
        root_cause_agent = agent_orch.agents.get("RootCause")
        doc_agent = agent_orch.agents.get("Documentation")
        slack_agent = agent_orch.agents.get("Slack")
        jira_agent = agent_orch.agents.get("Jira")
        notion_agent = agent_orch.agents.get("Notion")

        if diagram_agent:
            await diagram_agent.apply_analysis(analysis)

        if analysis.severity in ("sev1", "sev2") and root_cause_agent:
            await root_cause_agent.investigate(event)

        if slack_agent:
            await slack_agent.notify(incident)

        if jira_agent:
            await jira_agent.create_ticket(incident)

        if doc_agent:
            await doc_agent.create_report(incident)

        if notion_agent and analysis.severity in ("sev1",):
            await notion_agent.update_page(incident)

        await self.set_status(AgentStatus.IDLE)
