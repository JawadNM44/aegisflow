from __future__ import annotations
"""In-memory state store for architecture, incidents, and agents."""
import uuid
from datetime import datetime
from typing import Optional
from collections import defaultdict

from app.models.schemas import (
    C4Architecture, C4Node, C4Edge,
    InfrastructureEvent, Incident, GemmaAnalysis,
    AgentInfo, AgentStatus, AgentLog, HealthStatus, NodeType, EdgeType
)
from app.config import settings


class StateStore:
    """Singleton state store with thread-safe access patterns."""
    _instance: StateStore | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.architecture = C4Architecture(version=1, last_updated=datetime.utcnow().isoformat())
        self.incidents: dict[str, Incident] = {}
        self.events: list[InfrastructureEvent] = []
        self.agents: dict[str, AgentInfo] = {}
        self.default_architecture()

    def default_architecture(self):
        nodes = {}
        edges = {}

        node_defs = [
            ("lb-1", NodeType.LOAD_BALANCER, "API Gateway", "Nginx", "Entry point", -300, -100),
            ("web-1", NodeType.SERVICE, "Web Frontend", "Next.js", "Customer dashboard", -100, -200),
            ("api-1", NodeType.API, "API Server", "FastAPI", "Backend API", -100, -50),
            ("auth-1", NodeType.SERVICE, "Auth Service", "OAuth 2.0", "Authentication & authorization", -300, 50),
            ("db-1", NodeType.DATABASE, "PostgreSQL", "Postgres 15", "Primary database", 100, -50),
            ("cache-1", NodeType.STORAGE, "Redis Cache", "Redis 7", "Session & cache store", 100, 100),
            ("queue-1", NodeType.QUEUE, "Message Queue", "RabbitMQ", "Async task processing", 300, 0),
            ("worker-1", NodeType.CONTAINER_GROUP, "Worker Pool", "Celery", "Background workers", 300, 100),
            ("storage-1", NodeType.STORAGE, "Object Storage", "GCP Cloud Storage", "File & asset storage", -100, 150),
            ("search-1", NodeType.DATABASE, "Search Index", "Elasticsearch", "Full-text search", 100, 200),
            ("ci-1", NodeType.CI_CD, "CI/CD Pipeline", "GitHub Actions", "Build & deploy pipeline", -500, -100),
            ("monitor-1", NodeType.COMPONENT, "Monitoring", "Prometheus + Grafana", "System monitoring & alerting", -500, 100),
            ("cdn-1", NodeType.COMPONENT, "CDN", "Cloudflare", "Content delivery", -300, -200),
        ]

        for nid, ntype, name, tech, desc, x, y in node_defs:
            nodes[nid] = C4Node(
                id=nid, type=ntype, name=name, technology=tech,
                description=desc, health=HealthStatus.HEALTHY,
                position={"x": float(x), "y": float(y)}
            )

        edge_defs = [
            ("e1", "cdn-1", "lb-1", EdgeType.DATA),
            ("e2", "lb-1", "web-1", EdgeType.SYNC),
            ("e3", "lb-1", "api-1", EdgeType.SYNC),
            ("e4", "web-1", "api-1", EdgeType.SYNC),
            ("e5", "api-1", "auth-1", EdgeType.SYNC),
            ("e6", "api-1", "db-1", EdgeType.SYNC),
            ("e7", "api-1", "cache-1", EdgeType.DATA),
            ("e8", "api-1", "queue-1", EdgeType.ASYNC),
            ("e9", "queue-1", "worker-1", EdgeType.ASYNC),
            ("e10", "worker-1", "db-1", EdgeType.DATA),
            ("e11", "api-1", "storage-1", EdgeType.DATA),
            ("e12", "api-1", "search-1", EdgeType.DATA),
            ("e13", "lb-1", "monitor-1", EdgeType.DATA),
            ("e14", "api-1", "monitor-1", EdgeType.DATA),
            ("e15", "ci-1", "api-1", EdgeType.DATA),
            ("e16", "ci-1", "web-1", EdgeType.DATA),
        ]

        for eid, src, tgt, etype in edge_defs:
            edges[eid] = C4Edge(id=eid, source=src, target=tgt, type=etype)

        self.architecture = C4Architecture(
            nodes=nodes, edges=edges,
            version=1,
            last_updated=datetime.utcnow().isoformat(),
        )

    async def get_architecture(self) -> C4Architecture:
        return self.architecture

    async def update_architecture(self, arch: C4Architecture):
        self.architecture = arch
        self.architecture.version += 1
        self.architecture.last_updated = datetime.utcnow().isoformat()

    async def update_node_health(self, node_id: str, health: HealthStatus):
        if node_id in self.architecture.nodes:
            self.architecture.nodes[node_id].health = health
            self.architecture.version += 1
            self.architecture.last_updated = datetime.utcnow().isoformat()

    async def add_incident(self, incident: Incident) -> Incident:
        self.incidents[incident.id] = incident
        return incident

    async def get_incident(self, incident_id: str) -> Incident | None:
        return self.incidents.get(incident_id)

    async def get_incidents(self, limit: int = 20) -> list[Incident]:
        return sorted(
            self.incidents.values(),
            key=lambda i: i.created_at,
            reverse=True,
        )[:limit]

    async def update_incident(self, incident: Incident):
        self.incidents[incident.id] = incident

    async def add_event(self, event: InfrastructureEvent):
        self.events.append(event)
        if len(self.events) > 500:
            self.events = self.events[-200:]

    async def get_events(self, limit: int = 50) -> list[InfrastructureEvent]:
        return self.events[-limit:]

    async def get_agent(self, name: str) -> AgentInfo | None:
        return self.agents.get(name)

    async def get_agents(self) -> list[AgentInfo]:
        return list(self.agents.values())

    async def set_agent(self, agent: AgentInfo):
        self.agents[agent.name] = agent

    async def agent_log(self, name: str, level: str, message: str, details: dict | None = None):
        if name not in self.agents:
            self.agents[name] = AgentInfo(name=name)
        self.agents[name].logs.append(
            AgentLog(level=level, message=message, details=details or {})
        )
        self.agents[name].last_active = datetime.utcnow().isoformat()
        if len(self.agents[name].logs) > 100:
            self.agents[name].logs = self.agents[name].logs[-50:]


state = StateStore()
