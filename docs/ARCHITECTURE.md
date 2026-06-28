# System Architecture — AEGISFLOW

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AEGISFLOW PLATFORM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   FRONTEND   │◄───│  WEBSOCKET   │◄───│   BACKEND    │◄───│  AGENTS    │ │
│  │  (Next.js)   │    │   SERVER     │    │  (FastAPI)   │    │  (Multi-   │ │
│  │              │    │              │    │              │    │   Agent)   │ │
│  │ • React Flow │    │ • Events     │    │ • REST API   │    │            │ │
│  │ • Dashboard  │    │ • Commands   │    │ • Auth       │    │ • Planner  │ │
│  │ • Timeline   │    │ • State Sync │    │ • State      │    │ • Watcher  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    │ • Diagram  │ │
│                                                                  │ • Analyzer │ │
│                                                                  │ • RootCause│ │
│                                                                  │ • Doc      │ │
│                                                                  │ • Slack    │ │
│                                                                  │ • Jira     │ │
│                                                                  │ • Notion   │ │
│                                                                  │ • QA       │ │
│                                                                  │ • Arch     │ │
│                                                                  └─────┬──────┘ │
│                                                                        │        │
│                              ┌───────────────────────────────────────┘        │
│                              ▼                                                  │
│                    ┌─────────────────────┐                                     │
│                    │   GEMMA 4 (Cerebras)│                                     │
│                    │   • Structured Out  │                                     │
│                    │   • Tool Calling    │                                     │
│                    │   • Multimodal      │                                     │
│                    │   • reasoning_effort│                                     │
│                    └─────────────────────┘                                     │
│                              │                                                  │
│          ┌───────────────────┼───────────────────┐                             │
│          ▼                   ▼                   ▼                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                       │
│   │  INFRASTR.  │    │  INTEGRAT.  │    │   STATE     │                       │
│   │  PROVIDERS  │    │   CLIENTS   │    │  (Redis/    │                       │
│   │             │    │             │    │   In-Memory)│                       │
│   │ • Docker    │    │ • Slack     │    │             │                       │
│   │ • K8s       │    │ • Jira      │    │ • C4 Model  │                       │
│   │ • GCP       │    │ • Notion    │    │ • Events    │                       │
│   │ • GitHub    │    │ • GitHub    │    │ • Incidents │                       │
│   │ • Simulator │    │             │    │ • Agents    │                       │
│   └─────────────┘    └─────────────┘    └─────────────┘                       │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Backend (FastAPI)
- **REST API**: `/api/v1/architecture`, `/api/v1/incidents`, `/api/v1/agents`, `/api/v1/integrations`
- **WebSocket**: `/ws/architecture`, `/ws/incidents`, `/ws/agents` for real-time updates
- **Authentication**: JWT-based (simplified for demo)
- **State Management**: Redis for production, in-memory dict for demo

### Frontend (Next.js + React Flow)
- **Architecture View**: Interactive C4 diagram (Context, Container, Component, Code levels)
- **Incident Timeline**: Chronological event stream with AI analysis
- **Agent Console**: Live agent activity feed
- **Integration Panel**: Slack/Jira/Notion status and actions
- **Simulation Controls**: Inject failures, deployments, scaling events

### Agent Framework
```
BaseAgent
  ├── PlannerAgent (orchestrator)
  ├── WatcherAgent (infrastructure polling)
  ├── DiagramAgent (C4 model maintenance)
  ├── AnalyzerAgent (Gemma 4 reasoning)
  ├── RootCauseAgent (deep investigation)
  ├── DocumentationAgent (incident reports)
  ├── SlackAgent (notifications)
  ├── JiraAgent (issue creation)
  ├── NotionAgent (documentation)
  ├── QAAgent (integrity validation)
  └── ArchitectureAgent (model sync)
```

### Gemma 4 Integration (Cerebras)
- **Endpoint**: `https://api.cerebras.ai/v1/chat/completions`
- **Model**: `gemma-4-27b` (or latest available)
- **Features Used**:
  - Structured Outputs (JSON Schema)
  - Tool Calling (for agent actions)
  - Multimodal (image analysis)
  - `reasoning_effort`: "high" for root cause, "medium" for triage
- **Prompt Strategy**: System prompt with C4 model context, event schema, output schema

### Data Models

#### C4 Architecture Model
```typescript
interface C4Node {
  id: string;
  type: 'system' | 'container' | 'component' | 'code';
  name: string;
  technology: string;
  description: string;
  health: 'healthy' | 'warning' | 'critical' | 'offline';
  metadata: Record<string, any>;
  position: { x: number; y: number };
}

interface C4Edge {
  id: string;
  source: string;
  target: string;
  type: 'sync' | 'async' | 'data';
  protocol: string;
  description: string;
  health: 'healthy' | 'degraded' | 'failed';
}
```

#### Event Model
```typescript
interface InfrastructureEvent {
  id: string;
  timestamp: string;
  source: string;
  type: 'deployment' | 'failure' | 'scaling' | 'config_change' | 'health_change';
  severity: 'info' | 'warning' | 'critical';
  payload: Record<string, any>;
  affected_nodes: string[];
  correlation_id?: string;
}
```

#### Incident Model
```typescript
interface Incident {
  id: string;
  title: string;
  severity: 'sev1' | 'sev2' | 'sev3' | 'sev4';
  status: 'open' | 'investigating' | 'mitigating' | 'resolved' | 'closed';
  root_cause: string;
  confidence: number;
  affected_systems: string[];
  blast_radius: string[];
  remediation: RemediationStep[];
  requires_approval: boolean;
  timeline: TimelineEvent[];
  ai_analysis: GemmaAnalysis;
  created_at: string;
  resolved_at?: string;
}
```

#### Gemma Analysis Output (Structured)
```typescript
interface GemmaAnalysis {
  severity: 'sev1' | 'sev2' | 'sev3' | 'sev4';
  probable_root_cause: string;
  confidence: number; // 0-1
  affected_systems: string[];
  recommended_remediation: RemediationStep[];
  requires_human_approval: boolean;
  diagram_changes: DiagramChange[];
  future_risk: RiskAssessment;
  reasoning_trace: string[];
}
```

## Data Flow

### Event Ingestion → Analysis → Action
```
Infrastructure Event
       │
       ▼
Watcher Agent (polling/webhook)
       │
       ▼
Event Bus (Redis Streams / In-Memory)
       │
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
Diagram Agent       Analyzer Agent      Planner Agent
(Update C4)         (Gemma Reasoning)   (Orchestrate)
       │                  │                  │
       │                  ▼                  │
       │         ┌─────────────────┐         │
       │         │  Structured     │         │
       │         │  JSON Output    │         │
       │         └────────┬────────┘         │
       │                  │                  │
       ▼                  ▼                  ▼
  WebSocket           Incident           Agent
  Broadcast         Created            Commands
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
              ┌───────────────────────┐
              │   Integration Agents  │
              │  (Slack, Jira, Notion)│
              └───────────────────────┘
```

## Deployment Architecture

### Development (Docker Compose)
```
services:
  frontend:    Next.js dev server (port 3000)
  backend:     FastAPI + Uvicorn (port 8000)
  websocket:   FastAPI WebSocket (port 8001)
  redis:       Redis 7 (port 6379)
  simulator:   Infrastructure simulator (port 8002)
```

### Production (Kubernetes)
- Frontend: Vercel or K8s Deployment + Ingress
- Backend: K8s Deployment + HPA
- WebSocket: K8s Deployment with sticky sessions
- Redis: Redis Cluster or Cloud Provider
- Agents: K8s Jobs/CronJobs or separate Deployments

## Security Considerations
- API keys stored in environment variables / Kubernetes Secrets
- JWT for API authentication
- WebSocket authentication via token query param
- Integration tokens encrypted at rest
- Audit logging for all agent actions