export type HealthStatus = 'healthy' | 'warning' | 'critical' | 'offline';

export type NodeType =
  | 'system' | 'container' | 'component' | 'code'
  | 'database' | 'queue' | 'load_balancer' | 'storage'
  | 'ci_cd' | 'api' | 'container_group' | 'pod'
  | 'deployment' | 'service' | 'cloud_run' | 'cloud_function';

export type EdgeType = 'sync' | 'async' | 'data' | 'depends_on';

export type EventSeverity = 'info' | 'warning' | 'critical';
export type EventType =
  | 'deployment' | 'failure' | 'scaling' | 'config_change'
  | 'health_change' | 'network_issue' | 'resource_exhaustion'
  | 'security_event' | 'custom';

export type IncidentSeverity = 'sev1' | 'sev2' | 'sev3' | 'sev4';
export type IncidentStatus = 'open' | 'investigating' | 'mitigating' | 'resolved' | 'closed';

export interface C4Node {
  id: string;
  type: NodeType;
  name: string;
  technology: string;
  description: string;
  health: HealthStatus;
  metadata: Record<string, any>;
  position: { x: number; y: number };
  group?: string;
  parent?: string;
  properties: Record<string, any>;
}

export interface C4Edge {
  id: string;
  source: string;
  target: string;
  type: EdgeType;
  protocol: string;
  description: string;
  health: HealthStatus;
  metadata: Record<string, any>;
  animated: boolean;
}

export interface C4Architecture {
  nodes: Record<string, C4Node>;
  edges: Record<string, C4Edge>;
  version: number;
  last_updated: string;
}

export interface InfrastructureEvent {
  id: string;
  timestamp: string;
  source: string;
  type: EventType;
  severity: EventSeverity;
  title: string;
  message: string;
  payload: Record<string, any>;
  affected_nodes: string[];
  correlation_id?: string;
  requires_analysis: boolean;
}

export interface RemediationStep {
  order: number;
  action: string;
  command?: string;
  automated: boolean;
  requires_approval: boolean;
  status: string;
}

export interface TimelineEvent {
  timestamp: string;
  type: string;
  message: string;
  actor: string;
  details: Record<string, any>;
}

export interface RiskAssessment {
  score: number;
  factors: string[];
  predicted_duration_minutes?: number;
  sla_impact?: string;
}

export interface DiagramChange {
  node_id?: string;
  edge_id?: string;
  property: string;
  old_value?: any;
  new_value?: any;
}

export interface GemmaAnalysis {
  severity: IncidentSeverity;
  probable_root_cause: string;
  confidence: number;
  affected_systems: string[];
  recommended_remediation: RemediationStep[];
  requires_human_approval: boolean;
  diagram_changes: DiagramChange[];
  future_risk?: RiskAssessment;
  reasoning_trace: string[];
  inference_time_ms?: number;
}

export interface Incident {
  id: string;
  title: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  root_cause: string;
  confidence: number;
  affected_systems: string[];
  blast_radius: string[];
  remediation: RemediationStep[];
  requires_approval: boolean;
  approval_granted?: boolean;
  timeline: TimelineEvent[];
  ai_analysis?: GemmaAnalysis;
  created_at: string;
  resolved_at?: string;
  event_id?: string;
}

export interface AgentInfo {
  name: string;
  status: 'idle' | 'working' | 'error' | 'disabled';
  current_task?: string;
  last_active: string;
  error_count: number;
  logs: AgentLog[];
}

export interface AgentLog {
  timestamp: string;
  level: string;
  message: string;
  details: Record<string, any>;
}

export interface WSMessage {
  type: string;
  data?: any;
  architecture?: C4Architecture;
  incidents?: Incident[];
  message?: string;
  [key: string]: any;
}
