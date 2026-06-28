from __future__ import annotations

"""cerebras service - infrastructure management for AEGISFLOW observability."""

import json
import re
from typing import Optional, Any
import httpx
import logging

from app.config import settings
from app.models.schemas import GemmaAnalysis, RemediationStep, RiskAssessment, DiagramChange

logger = logging.getLogger("aegisflow.cerebras")

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "severity": {"type": "string", "enum": ["sev1", "sev2", "sev3", "sev4"]},
        "probable_root_cause": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "affected_systems": {"type": "array", "items": {"type": "string"}},
        "recommended_remediation": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "order": {"type": "integer"},
                    "action": {"type": "string"},
                    "command": {"type": "string"},
                    "automated": {"type": "boolean"},
                    "requires_approval": {"type": "boolean"},
                    "status": {"type": "string"},
                },
                "required": ["order", "action", "automated"],
            },
        },
        "requires_human_approval": {"type": "boolean"},
        "diagram_changes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "node_id": {"type": "string"},
                    "edge_id": {"type": "string"},
                    "property": {"type": "string"},
                    "old_value": {},
                    "new_value": {},
                },
            },
        },
        "future_risk": {
            "type": "object",
            "properties": {
                "score": {"type": "number"},
                "factors": {"type": "array", "items": {"type": "string"}},
                "predicted_duration_minutes": {"type": "integer"},
                "sla_impact": {"type": "string"},
            },
        },
        "reasoning_trace": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["severity", "probable_root_cause", "confidence", "affected_systems", "recommended_remediation", "requires_human_approval"],
}


class CerebrasClient:
    _instance: CerebrasClient | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.api_key = settings.cerebras_api_key
        self.base_url = settings.cerebras_base_url
        self.model = settings.gemma_model
        self.client = httpx.Client(timeout=30.0)
        self.simulation_mode = not bool(self.api_key)

    def analyze_event(self, event_data: dict, architecture: dict) -> GemmaAnalysis:
        if self.simulation_mode:
            return self._simulate_analysis(event_data)

        try:
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self._system_prompt()},
                        {"role": "user", "content": self._build_prompt(event_data, architecture)},
                    ],
                    "response_format": {"type": "json_object"},
                    "reasoning_effort": "high" if event_data.get("severity") == "critical" else "medium",
                    "temperature": 0.1,
                    "max_tokens": 4096,
                },
            )
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            repaired = self._repair_json(parsed, event_data)

            # Capture Cerebras timing info (in seconds, convert to ms)
            time_info = result.get("time_info", {})
            analysis = GemmaAnalysis(**repaired)
            total_time_sec = time_info.get("total_time", None)
            if total_time_sec is not None:
                analysis.inference_time_ms = round(total_time_sec * 1000, 1)
            elif time_info:
                queue = time_info.get("queue_time", 0)
                prompt = time_info.get("prompt_time", 0)
                completion = time_info.get("completion_time", 0)
                analysis.inference_time_ms = round((queue + prompt + completion) * 1000, 1)

            logger.info(f"Gemma 4 analysis: severity={analysis.severity}, confidence={analysis.confidence}, time={analysis.inference_time_ms}ms")
            return analysis
        except Exception as e:
            logger.warning(f"Gemma 4 API error: {e}, falling back")
            return self._simulate_analysis(event_data)

    def _repair_json(self, parsed: dict, event_data: dict) -> dict:
        if not isinstance(parsed.get("affected_systems"), list):
            affected = parsed.get("affected_systems", {})
            if isinstance(affected, dict):
                values = []
                for v in affected.values():
                    if isinstance(v, str):
                        values.append(v)
                    elif isinstance(v, list):
                        values.extend(v)
                parsed["affected_systems"] = values or event_data.get("affected_nodes", [])
            else:
                parsed["affected_systems"] = event_data.get("affected_nodes", [])

        if not isinstance(parsed.get("recommended_remediation"), list):
            parsed["recommended_remediation"] = []

        for step in parsed.get("recommended_remediation", []):
            if not isinstance(step, dict):
                continue
            step.setdefault("order", 1)
            step.setdefault("action", "Investigate and remediate")
            step.setdefault("automated", False)
            step.setdefault("requires_approval", False)
            step.setdefault("status", "pending")

        if not isinstance(parsed.get("diagram_changes"), list):
            parsed["diagram_changes"] = []

        if not isinstance(parsed.get("reasoning_trace"), list):
            parsed["reasoning_trace"] = []

        return parsed

    def _system_prompt(self) -> str:
        return f"""You are AEGISFLOW's infrastructure analysis engine, powered by Gemma 4 on Cerebras.
Your role is to analyze cloud infrastructure events and return structured incident analysis.

You MUST output valid JSON with exactly these fields:
- severity: string ("sev1" for critical outage, "sev2" for degraded service, "sev3" for minor issue, "sev4" for informational)
- probable_root_cause: string describing the likely cause
- confidence: number between 0.0 and 1.0
- affected_systems: array of strings listing all affected node IDs
- recommended_remediation: array of objects with order (int), action (string), automated (bool), requires_approval (bool), status (string)
- requires_human_approval: boolean
- diagram_changes: array of objects with node_id (string), property (string), new_value
- future_risk: object with score (0-1), factors (string array), predicted_duration_minutes (int)
- reasoning_trace: array of strings showing step-by-step reasoning

IMPORTANT: affected_systems must be a flat JSON array of strings, NOT an object.
Example: ["db-1", "api-1", "queue-1"]"""

    def _build_prompt(self, event_data: dict, architecture: dict) -> str:
        nodes_health = []
        for nid, node in architecture.get("nodes", {}).items():
            nodes_health.append(f"  {nid} ({node.get('name','')}): {node.get('health','unknown')} - {node.get('type','')}")

        return f"""Analyze this infrastructure event and return structured JSON.

EVENT:
  Title: {event_data.get('title', 'N/A')}
  Severity: {event_data.get('severity', 'N/A')}
  Type: {event_data.get('type', 'N/A')}
  Message: {event_data.get('message', 'N/A')}
  Affected Nodes: {event_data.get('affected_nodes', [])}

CURRENT INFRASTRUCTURE:
{chr(10).join(nodes_health)}

DEPENDENCY EDGES:
{json.dumps([{"from": e.get("source"), "to": e.get("target"), "type": e.get("type")} for e in architecture.get("edges", {}).values()], indent=2)}

Determine: severity, root cause, confidence, affected systems (as a flat array of strings), remediation steps, approval requirements, diagram changes, future risk, and reasoning trace."""

    def _simulate_analysis(self, event_data: dict) -> GemmaAnalysis:
        sev = event_data.get("severity", "info")
        if isinstance(sev, str):
            sev_str = sev
        elif hasattr(sev, 'value'):
            sev_str = sev.value
        else:
            sev_str = str(sev)
        severity_map = {"critical": "sev1", "warning": "sev2", "info": "sev3"}
        severity = severity_map.get(sev_str, "sev3")

        affected = event_data.get("affected_nodes", [])
        title = event_data.get("title", "Unknown Event")

        return GemmaAnalysis(
            severity=severity,
            probable_root_cause=f"Root cause: {title}",
            confidence=0.85,
            affected_systems=affected,
            recommended_remediation=[
                RemediationStep(order=1, action="Verify service health status", automated=True),
                RemediationStep(order=2, action="Check logs for error patterns", automated=True),
                RemediationStep(order=3, action="Restart affected services", automated=False, requires_approval=True),
            ],
            requires_human_approval=severity == "sev1",
            diagram_changes=[
                DiagramChange(node_id=nid, property="health", new_value="critical" if sev_str == "critical" else "warning")
                for nid in affected
            ],
            future_risk=RiskAssessment(
                score=0.7 if sev_str == "critical" else 0.3,
                factors=["Dependency health degraded", "Multiple related services affected"],
                predicted_duration_minutes=15,
            ),
            inference_time_ms=0.0,
            reasoning_trace=[
                f"Event: {title}",
                f"Affected: {affected}",
                "Correlating dependencies",
                "Analyzing propagation",
                "Generating remediation",
            ],
        )


    def ask_gemma(self, system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> dict | None:
        """Generic Gemma 4 call for any agent. Returns parsed JSON or None."""
        if self.simulation_mode or not self.api_key:
            return None
        try:
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1,
                    "max_tokens": max_tokens,
                },
            )
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as e:
            logger.warning(f"Gemma 4 call failed: {e}")
            return None

    def analyze_diagram(self, base64_image: str, prompt: str = "Analyze this infrastructure diagram.") -> dict | None:
        """Send a diagram image to Gemma 4 for multimodal analysis."""
        if self.simulation_mode or not self.api_key:
            return None
        try:
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                            ],
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2048,
                },
            )
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            time_info = data.get("time_info", {})
            total_time = time_info.get("total_time", 0)
            logger.info(f"Gemma 4 diagram analysis: {len(content)} chars in {total_time*1000:.0f}ms")
            return {"analysis": content, "inference_time_ms": round(total_time * 1000, 1) if total_time else None}
        except Exception as e:
            logger.warning(f"Gemma 4 diagram analysis failed: {e}")
            return None


cerebras = CerebrasClient()
