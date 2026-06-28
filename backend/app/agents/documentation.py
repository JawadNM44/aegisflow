from __future__ import annotations
from app.agents.base import BaseAgent
from app.models.schemas import AgentStatus, Incident, TimelineEvent
from app.services.state import state
from app.services.websocket_manager import ws_manager


class DocumentationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Documentation")

    async def _run_impl(self):
        await self.log("info", "Documentation Agent started")

    async def create_report(self, incident: Incident):
        await self.set_status(AgentStatus.WORKING, f"Creating incident report for {incident.id}")
        await self.log("info", f"Generating incident report for {incident.title}")

        report = f"""# Incident Report: {incident.title}

**ID:** {incident.id}
**Severity:** {incident.severity}
**Status:** {incident.status.value}
**Created:** {incident.created_at}

## Root Cause
{incident.root_cause}

## Affected Systems
{', '.join(incident.affected_systems)}

## Remediation Steps
"""
        for step in incident.remediation:
            report += f"{step.order}. {step.action} {'(automated)' if step.automated else '(manual)'}\n"

        report += f"""\n## Timeline
"""
        for t in incident.timeline:
            report += f"- [{t.type}] {t.message}\n"

        await state.agent_log(self.name, "info", f"Report generated ({len(report)} chars)", {"incident_id": incident.id})
        await ws_manager.broadcast_event("report", {"incident_id": incident.id, "content": report})
        await self.set_status(AgentStatus.IDLE)
