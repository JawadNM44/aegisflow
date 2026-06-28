from __future__ import annotations

"""Documentation agent - specialized infrastructure analysis for AEGISFLOW."""

from app.agents.base import BaseAgent
from app.models.schemas import AgentStatus, Incident, TimelineEvent
from app.services.state import state
from app.services.websocket_manager import ws_manager
from app.services.cerebras import cerebras


class DocumentationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Documentation")

    async def _run_impl(self):
        await self.log("info", "Documentation Agent started")

    async def create_report(self, incident: Incident):
        await self.set_status(AgentStatus.WORKING, f"Creating incident report for {incident.id}")
        await self.log("info", f"Generating incident report for {incident.title}")

        report = None
        gemma_result = cerebras.ask_gemma(
            "You are an incident report writer. Output JSON with a single 'report' key containing a markdown incident report.",
            f"""Write a professional post-incident report for:
Title: {incident.title}
Severity: {incident.severity}
Root Cause: {incident.root_cause}
Affected: {', '.join(incident.affected_systems)}
Confidence: {incident.confidence}
Remediation: {[s.action for s in incident.remediation]}
Timeline: {[t.message for t in incident.timeline]}""",
        )
        if gemma_result and "report" in gemma_result:
            report = gemma_result["report"]

        if not report:
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

        await state.agent_log(self.name, "info", f"Report generated ({len(report)} chars, {'Gemma 4' if gemma_result else 'template'})", {"incident_id": incident.id})
        await ws_manager.broadcast_event("report", {"incident_id": incident.id, "content": report})
        await self.set_status(AgentStatus.IDLE)
