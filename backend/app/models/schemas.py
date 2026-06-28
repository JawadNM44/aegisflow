from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


class NodeType(str, Enum):
    SYSTEM = "system"
    CONTAINER = "container"
    COMPONENT = "component"
    CODE = "code"
    DATABASE = "database"
    QUEUE = "queue"
    LOAD_BALANCER = "load_balancer"
    STORAGE = "storage"
    CI_CD = "ci_cd"
    API = "api"
    CONTAINER_GROUP = "container_group"
    POD = "pod"
    DEPLOYMENT = "deployment"
    SERVICE = "service"
    CLOUD_RUN = "cloud_run"
    CLOUD_FUNCTION = "cloud_function"


class EdgeType(str, Enum):
    SYNC = "sync"
    ASYNC = "async"
    DATA = "data"
    DEPENDS_ON = "depends_on"


class EventType(str, Enum):
    DEPLOYMENT = "deployment"
    FAILURE = "failure"
    SCALING = "scaling"
    CONFIG_CHANGE = "config_change"
    HEALTH_CHANGE = "health_change"
    NETWORK_ISSUE = "network_issue"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SECURITY_EVENT = "security_event"
    CUSTOM = "custom"


class EventSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AgentStatus(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"
    DISABLED = "disabled"


# --- C4 Architecture Models ---

class C4Node(BaseModel):
    id: str
    type: NodeType = NodeType.COMPONENT
    name: str
    technology: str = ""
    description: str = ""
    health: HealthStatus = HealthStatus.HEALTHY
    metadata: dict[str, Any] = Field(default_factory=dict)
    position: dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    group: Optional[str] = None
    parent: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)


class C4Edge(BaseModel):
    id: str
    source: str
    target: str
    type: EdgeType = EdgeType.SYNC
    protocol: str = ""
    description: str = ""
    health: HealthStatus = HealthStatus.HEALTHY
    metadata: dict[str, Any] = Field(default_factory=dict)
    animated: bool = False


class C4Architecture(BaseModel):
    nodes: dict[str, C4Node] = Field(default_factory=dict)
    edges: dict[str, C4Edge] = Field(default_factory=dict)
    version: int = 0
    last_updated: str = ""


# --- Event Models ---

class InfrastructureEvent(BaseModel):
    id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    source: str
    type: EventType = EventType.CUSTOM
    severity: EventSeverity = EventSeverity.INFO
    title: str
    message: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    affected_nodes: list[str] = Field(default_factory=list)
    correlation_id: Optional[str] = None
    requires_analysis: bool = True


# --- Incident Models ---

class RemediationStep(BaseModel):
    order: int
    action: str
    command: Optional[str] = None
    automated: bool = False
    requires_approval: bool = False
    status: str = "pending"


class TimelineEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    type: str
    message: str
    actor: str = "system"
    details: dict[str, Any] = Field(default_factory=dict)


class RiskAssessment(BaseModel):
    score: float = Field(ge=0, le=1)
    factors: list[str] = Field(default_factory=list)
    predicted_duration_minutes: Optional[int] = None
    sla_impact: Optional[str] = None


class DiagramChange(BaseModel):
    node_id: Optional[str] = None
    edge_id: Optional[str] = None
    property: str
    old_value: Any = None
    new_value: Any = None


class GemmaAnalysis(BaseModel):
    severity: str = "sev3"
    probable_root_cause: str = ""
    confidence: float = Field(default=0.0, ge=0, le=1)
    affected_systems: list[str] = Field(default_factory=list)
    recommended_remediation: list[RemediationStep] = Field(default_factory=list)
    requires_human_approval: bool = False
    diagram_changes: list[DiagramChange] = Field(default_factory=list)
    future_risk: Optional[RiskAssessment] = None
    reasoning_trace: list[str] = Field(default_factory=list)
    inference_time_ms: Optional[float] = None


class Incident(BaseModel):
    id: str
    title: str
    severity: str = "sev3"
    status: IncidentStatus = IncidentStatus.OPEN
    root_cause: str = ""
    confidence: float = 0.0
    affected_systems: list[str] = Field(default_factory=list)
    blast_radius: list[str] = Field(default_factory=list)
    remediation: list[RemediationStep] = Field(default_factory=list)
    requires_approval: bool = False
    approval_granted: Optional[bool] = None
    timeline: list[TimelineEvent] = Field(default_factory=list)
    ai_analysis: Optional[GemmaAnalysis] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    resolved_at: Optional[str] = None
    event_id: Optional[str] = None


# --- Agent Models ---

class AgentInfo(BaseModel):
    name: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    last_active: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    error_count: int = 0
    logs: list[AgentLog] = Field(default_factory=list, max_length=100)


class AgentLog(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    level: str = "info"
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


# --- Integration Models ---

class IntegrationStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    SIMULATED = "simulated"


class IntegrationConfig(BaseModel):
    name: str
    enabled: bool = False
    configured: bool = False
    status: IntegrationStatus = IntegrationStatus.DISCONNECTED


# --- Simulation ---

class SimulationCommand(BaseModel):
    action: str  # kill, degrade, restore, deploy, scale
    target: str  # node id or name
    severity: Optional[str] = "critical"
    delay: int = 0
