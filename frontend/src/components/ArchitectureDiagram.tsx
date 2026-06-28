/* ArchitectureDiagram component - AEGISFLOW dashboard UI for infrastructure observability. */

import React, { useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
  NodeProps,
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { C4Architecture } from '@/types';

const healthColors: Record<string, string> = {
  healthy: '#22c55e',
  warning: '#f59e0b',
  critical: '#ef4444',
  offline: '#6b7280',
};

const NodeIcon = ({ type, className }: { type: string; className?: string }) => {
  const props = { className: `w-5 h-5 ${className || ''}`, strokeWidth: 1.5 };
  const icons: Record<string, React.ReactNode> = {
    database: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v14c0 1.66 3.13 3 7 3s7-1.34 7-3V5"/><path d="M5 12c0 1.66 3.13 3 7 3s7-1.34 7-3"/></svg>,
    queue: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 6h16M4 12h16M4 18h16"/><circle cx="8" cy="6" r="1" fill="currentColor"/><circle cx="8" cy="12" r="1" fill="currentColor"/><circle cx="8" cy="18" r="1" fill="currentColor"/></svg>,
    load_balancer: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="3"/><path d="M12 9V3M12 21v-6M3 12h6M15 12h6"/></svg>,
    storage: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M2 4h20v16H2z"/><path d="M2 8h20"/><path d="M8 12h8"/></svg>,
    ci_cd: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M12 7v3l-5 7"/><path d="M12 10l5 7"/></svg>,
    api: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>,
    service: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><path d="M6 6h.01M6 18h.01"/></svg>,
    container_group: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Z"/><path d="M8 2v4M16 2v4"/><rect x="6" y="8" width="12" height="8" rx="1"/><path d="M10 12h4"/></svg>,
    component: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>,
    system: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M8 20v2M16 20v2"/><path d="M12 16v-4M9 13l3-3 3 3"/></svg>,
    cloud_run: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>,
    cloud_function: <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12s4.48 10 10 10"/><path d="M13 2.1S15 6 15 12s-2 9.9-2 9.9"/><path d="M2.1 13h19.8M2.1 11h19.8"/></svg>,
  };
  return <>{icons[type] || <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>}</>;
};

function CustomNode({ data }: NodeProps) {
  const health = data.health || 'healthy';
  const color = healthColors[health] || '#6b7280';
  const isCritical = health === 'critical';
  const isWarning = health === 'warning';

  return (
    <div
      className={`
        relative px-4 py-3 rounded-xl border-2 min-w-[150px] shadow-lg
        bg-gray-900/90 backdrop-blur-sm transition-all duration-300
        ${isCritical ? 'animate-pulse border-red-500 shadow-red-500/40' : 'border-gray-700 hover:border-gray-500'}
        ${isWarning ? 'border-yellow-500 shadow-yellow-500/30' : ''}
        ${health === 'healthy' ? 'border-emerald-500/50' : ''}
      `}
    >
      <div className="absolute -top-1.5 -right-1.5 w-3 h-3 rounded-full border-2 border-gray-900 shadow-sm" style={{ backgroundColor: color }} />
      <div className="mb-1.5 flex justify-center text-gray-300">
        <NodeIcon type={data.nodeType} />
      </div>
      <div className="text-sm font-bold text-white whitespace-nowrap text-center">{data.label}</div>
      <div className="text-[10px] text-gray-500 mt-0.5 text-center">{data.technology}</div>
      <Handle type="target" position={Position.Top} className="!bg-gray-600 !w-2.5 !h-2.5 !border-2 !border-gray-800" />
      <Handle type="source" position={Position.Bottom} className="!bg-gray-600 !w-2.5 !h-2.5 !border-2 !border-gray-800" />
    </div>
  );
}

const nodeTypes = { custom: CustomNode };

interface Props {
  architecture: C4Architecture | null;
}

export default function ArchitectureDiagram({ architecture }: Props) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!architecture || !architecture.nodes) return;

    const nodeMap = architecture.nodes;
    const edgeMap = architecture.edges;

    const flowNodes: Node[] = Object.values(nodeMap).map((n: any) => ({
      id: n.id,
      type: 'custom',
      position: { x: n.position?.x ?? 0, y: n.position?.y ?? 0 },
      data: {
        label: n.name,
        health: n.health || 'healthy',
        technology: n.technology || '',
        nodeType: n.type,
        description: n.description || '',
      },
    }));

    const flowEdges: Edge[] = Object.values(edgeMap).map((e: any) => {
      const sourceHealth = nodeMap[e.source]?.health || 'healthy';
      const targetHealth = nodeMap[e.target]?.health || 'healthy';
      const anyCritical = sourceHealth === 'critical' || targetHealth === 'critical';

      return {
        id: e.id,
        source: e.source,
        target: e.target,
        type: 'smoothstep',
        animated: anyCritical,
        style: {
          stroke: anyCritical ? '#ef4444' : '#4b5563',
          strokeWidth: anyCritical ? 3 : 2,
          strokeDasharray: e.type === 'async' ? '5,5' : undefined,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: anyCritical ? '#ef4444' : '#6b7280',
        },
      };
    });

    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [architecture, setNodes, setEdges]);

  if (!architecture || Object.keys(architecture.nodes || {}).length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-950/30">
        <div className="text-center text-gray-500">
          <svg className="w-12 h-12 mx-auto mb-3 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <p className="text-sm">Waiting for architecture data...</p>
          <p className="text-xs mt-1 text-gray-600">Connect to AEGISFLOW backend</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.15 }}
        minZoom={0.3}
        maxZoom={2.5}
        className="bg-gray-950/50"
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#1a2332" gap={24} size={1} />
        <Controls className="!bg-gray-800 !border-gray-700 !text-white [&>button]:!border-gray-600 [&>button]:!bg-gray-800 [&>button]:hover:!bg-gray-700" />
        <MiniMap
          nodeStrokeColor="#4b5563"
          nodeColor="#1f2937"
          maskColor="rgba(0,0,0,0.7)"
          className="!bg-gray-900 !border-gray-700 !rounded-lg"
          style={{ width: 150, height: 100 }}
        />
      </ReactFlow>
    </div>
  );
}
