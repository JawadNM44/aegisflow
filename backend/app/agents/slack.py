from __future__ import annotations

"""Slack agent - specialized infrastructure analysis for AEGISFLOW."""

import json
from datetime import datetime

from app.agents.base import BaseAgent
from app.models.schemas import AgentStatus, Incident, IntegrationStatus
from app.config import settings
from app.services.websocket_manager import ws_manager


class SlackAgent(BaseAgent):
    def __init__(self):
        super().__init__("Slack")
        self._configured = bool(settings.slack_token)
        self._status = IntegrationStatus.CONNECTED if self._configured else IntegrationStatus.SIMULATED

    async def _run_impl(self):
        status = "connected" if self._configured else "simulated mode (no credentials)"
        await self.log("info", f"Slack Agent started ({status})")

    async def notify(self, incident: Incident):
        await self.set_status(AgentStatus.WORKING, f"Sending Slack notification for {incident.id}")
        await self.log("info", f"Notification: [{incident.severity}] {incident.title}")

        message = {
            "channel": settings.slack_channel,
            "text": f"*[{incident.severity.upper()}] {incident.title}*\nRoot Cause: {incident.root_cause}\nAffected: {', '.join(incident.affected_systems)}"
        }

        if self._configured:
            try:
                from slack_sdk import WebClient
                client = WebClient(token=settings.slack_token)
                client.chat_postMessage(**message)
                await self.log("info", "Slack notification sent")
            except Exception as e:
                await self.log("error", f"Slack API error: {e}")
                self._status = IntegrationStatus.ERROR
        else:
            await ws_manager.broadcast_event("integration_log", {
                "agent": "Slack",
                "type": "notification",
                "data": message,
                "simulated": True,
            })
            await self.log("info", "Slack notification simulated")

        await self.set_status(AgentStatus.IDLE)


class JiraAgent(BaseAgent):
    def __init__(self):
        super().__init__("Jira")
        self._configured = bool(settings.jira_url and settings.jira_token)
        self._status = IntegrationStatus.CONNECTED if self._configured else IntegrationStatus.SIMULATED

    async def _run_impl(self):
        status = "connected" if self._configured else "simulated mode (no credentials)"
        await self.log("info", f"Jira Agent started ({status})")

    async def create_ticket(self, incident: Incident):
        await self.set_status(AgentStatus.WORKING, f"Creating Jira ticket for {incident.id}")
        await self.log("info", f"Jira ticket: [{incident.severity}] {incident.title}")

        ticket = {
            "project": settings.jira_project,
            "summary": f"[{incident.severity.upper()}] {incident.title}",
            "description": f"Root Cause: {incident.root_cause}\n\nAffected Systems: {', '.join(incident.affected_systems)}\n\nConfidence: {incident.confidence}\n\nRemediation:\n" + "\n".join(f"{s.order}. {s.action}" for s in incident.remediation),
            "priority": incident.severity,
        }

        if self._configured:
            try:
                from jira import JIRA
                jira = JIRA(server=settings.jira_url, basic_auth=(settings.jira_email, settings.jira_token))
                jira.create_issue(**ticket)
                await self.log("info", "Jira ticket created")
            except Exception as e:
                await self.log("error", f"Jira API error: {e}")
                self._status = IntegrationStatus.ERROR
        else:
            await ws_manager.broadcast_event("integration_log", {
                "agent": "Jira",
                "type": "ticket",
                "data": ticket,
                "simulated": True,
            })
            await self.log("info", "Jira ticket simulated")

        await self.set_status(AgentStatus.IDLE)


class NotionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Notion")
        self._configured = bool(settings.notion_token)
        self._status = IntegrationStatus.CONNECTED if self._configured else IntegrationStatus.SIMULATED

    async def _run_impl(self):
        status = "connected" if self._configured else "simulated mode (no credentials)"
        await self.log("info", f"Notion Agent started ({status})")

    async def update_page(self, incident: Incident):
        await self.set_status(AgentStatus.WORKING, f"Updating Notion for {incident.id}")
        await self.log("info", f"Updating Notion page with incident {incident.title}")

        content = f"# Incident: {incident.title}\n\n"
        content += f"**Severity:** {incident.severity}\n"
        content += f"**Root Cause:** {incident.root_cause}\n"
        content += f"**Affected Systems:** {', '.join(incident.affected_systems)}\n"
        content += f"**Status:** {incident.status.value}\n\n"
        content += "## Remediation\n"
        for step in incident.remediation:
            content += f"- {step.action}\n"

        if self._configured:
            try:
                from notion_client import Client
                notion = Client(auth=settings.notion_token)
                notion.pages.update(page_id=settings.notion_page_id, properties={
                    "title": [{"text": {"content": f"Incident: {incident.title}"}}]
                })
                await self.log("info", "Notion page updated")
            except Exception as e:
                await self.log("error", f"Notion API error: {e}")
                self._status = IntegrationStatus.ERROR
        else:
            await ws_manager.broadcast_event("integration_log", {
                "agent": "Notion",
                "type": "page_update",
                "data": {"content": content},
                "simulated": True,
            })
            await self.log("info", "Notion update simulated")

        await self.set_status(AgentStatus.IDLE)
