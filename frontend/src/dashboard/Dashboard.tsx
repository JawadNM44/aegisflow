import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Shield, Activity, Bot, Bell, Radio, Gauge, Box, Loader, Zap } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { api } from '@/lib/api';
import IncidentPanel from '@/components/IncidentPanel';
import AgentConsole from '@/components/AgentConsole';
import IntegrationPanel from '@/components/IntegrationPanel';
import SimulationControls from '@/components/SimulationControls';
import type { AgentInfo } from '@/types';

const DynamicArchitecture = dynamic(() => import('@/components/ArchitectureDiagram'), { ssr: false });

type Tab = 'incidents' | 'agents' | 'integrations' | 'simulation';

export default function Dashboard() {
  const { connected, architecture, incidents } = useWebSocket();
  const [activeTab, setActiveTab] = useState<Tab>('incidents');
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [integrationStatuses, setIntegrationStatuses] = useState({});
  const [cerebrasSpeed, setCerebrasSpeed] = useState<number | null>(null);

  useEffect(() => {
    function refresh() {
      api.getAgents().then(setAgents).catch(() => {});
      api.getHealth().then(h => {
        if (h.cerebras_speed_ms) setCerebrasSpeed(h.cerebras_speed_ms);
      }).catch(() => {});
    }
    refresh();
    const interval = setInterval(refresh, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    api.get('/integrations/status').then(setIntegrationStatuses).catch(() => {});
  }, []);

  const nodeCount = architecture ? Object.keys(architecture.nodes || {}).length : 0;
  const edgeCount = architecture ? Object.keys(architecture.edges || {}).length : 0;
  const criticalCount = architecture
    ? Object.values(architecture.nodes || {}).filter((n: any) => n.health === 'critical').length
    : 0;
  const warningCount = architecture
    ? Object.values(architecture.nodes || {}).filter((n: any) => n.health === 'warning').length
    : 0;
  const healthyCount = architecture
    ? Object.values(architecture.nodes || {}).filter((n: any) => n.health === 'healthy').length
    : 0;

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'incidents', label: 'Incidents', icon: <Bell className="w-4 h-4" /> },
    { id: 'agents', label: 'Agents', icon: <Bot className="w-4 h-4" /> },
    { id: 'integrations', label: 'Integrations', icon: <Radio className="w-4 h-4" /> },
    { id: 'simulation', label: 'Simulate', icon: <Gauge className="w-4 h-4" /> },
  ];

  return (
    <div className="h-screen flex flex-col bg-gray-950 text-white overflow-hidden">
      {/* Header */}
      <header className="shrink-0 border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm px-6 py-3 flex items-center gap-4 z-10">
        <div className="flex items-center gap-2">
          <Shield className="w-6 h-6 text-cyan-400" />
          <h1 className="text-lg font-bold tracking-tight">
            <span className="text-cyan-400">AEGIS</span>FLOW
          </h1>
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-400 ml-4">
          <span className="flex items-center gap-1">
            <Box className="w-3 h-3" /> {nodeCount} nodes
          </span>
          <span className="flex items-center gap-1">
            <Activity className="w-3 h-3" /> {edgeCount} edges
          </span>
          {criticalCount > 0 && (
            <span className="flex items-center gap-1 text-red-400 font-semibold">
              <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
              {criticalCount} critical
            </span>
          )}
          {warningCount > 0 && criticalCount === 0 && (
            <span className="flex items-center gap-1 text-yellow-400">
              <span className="w-2 h-2 rounded-full bg-yellow-400" />
              {warningCount} warning
            </span>
          )}
        </div>
        <div className="flex-1" />
        {cerebrasSpeed != null && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-indigo-900/40 border border-indigo-700/40 text-indigo-300 mr-3">
            <Zap className="w-3 h-3 text-indigo-400" />
            <span className="text-xs font-semibold">{cerebrasSpeed.toFixed(0)}ms</span>
            <span className="text-[10px] text-indigo-500">via Cerebras</span>
          </div>
        )}
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-red-400'} transition-colors`} />
          <span className="text-xs text-gray-400">{connected ? 'Live' : 'Connecting...'}</span>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Architecture Diagram - center */}
        <div className="flex-1 relative">
          <DynamicArchitecture architecture={architecture} />
        </div>

        {/* Right panel */}
        <div className="w-80 shrink-0 border-l border-gray-800 bg-gray-900/50 flex flex-col">
          {/* Tab bar */}
          <div className="shrink-0 flex border-b border-gray-800">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-cyan-400 border-b-2 border-cyan-400 bg-cyan-400/5'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-hidden p-3">
            {activeTab === 'incidents' && <IncidentPanel incidents={incidents} />}
            {activeTab === 'agents' && <AgentConsole agents={agents} />}
            {activeTab === 'integrations' && <IntegrationPanel statuses={integrationStatuses} />}
            {activeTab === 'simulation' && <SimulationControls />}
          </div>

          {/* Footer stats */}
          <div className="shrink-0 border-t border-gray-800 p-3">
            <div className="grid grid-cols-3 gap-2">
              <div className="text-center">
                <div className="text-lg font-bold text-emerald-400">{healthyCount}</div>
                <div className="text-xs text-gray-500">Healthy</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-yellow-400">{warningCount}</div>
                <div className="text-xs text-gray-500">Warning</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-red-400">{criticalCount}</div>
                <div className="text-xs text-gray-500">Critical</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
