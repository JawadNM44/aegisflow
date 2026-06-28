/* useWebSocket - AEGISFLOW frontend useWebSocket for dashboard data management. */

import { useEffect, useRef, useCallback, useState } from 'react';
import type { WSMessage, C4Architecture, Incident } from '@/types';
import { api } from '@/lib/api';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/ws';

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [architecture, setArchitecture] = useState<C4Architecture | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const listenersRef = useRef<Map<string, Set<(data: any) => void>>>(new Map());
  const initializedRef = useRef(false);

  const addListener = useCallback((type: string, cb: (data: any) => void) => {
    if (!listenersRef.current.has(type)) listenersRef.current.set(type, new Set());
    listenersRef.current.get(type)!.add(cb);
    return () => listenersRef.current.get(type)?.delete(cb);
  }, []);

  // Initial data load
  useEffect(() => {
    if (initializedRef.current) return;

    api.getArchitecture().then((arch) => {
      setArchitecture(arch);
    }).catch(() => {});

    api.getIncidents().then((inc) => {
      setIncidents(inc);
    }).catch(() => {});

    initializedRef.current = true;
  }, []);

  // Poll for data every 3s as fallback (catches WS gaps)
  useEffect(() => {
    const poll = setInterval(() => {
      api.getArchitecture().then(setArchitecture).catch(() => {});
      api.getIncidents().then(setIncidents).catch(() => {});
    }, 3000);
    return () => clearInterval(poll);
  }, []);

  useEffect(() => {
    let reconnectTimer: ReturnType<typeof setTimeout>;
    let pingTimer: ReturnType<typeof setInterval>;
    let isDestroyed = false;

    function connect() {
      if (isDestroyed) return;
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        // Send keepalive ping every 15s to prevent WS timeout
        pingTimer = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ action: "ping" }));
          }
        }, 15000);
      };

      ws.onmessage = (event) => {
        try {
          const msg: WSMessage = JSON.parse(event.data);
          const type = msg.type;

          if (type === 'init' && msg.architecture) {
            setArchitecture(msg.architecture);
          }
          if (type === 'architecture' && msg.data) {
            setArchitecture(msg.data);
          }
          if (type === 'incidents' && msg.incidents) {
            setIncidents(msg.incidents);
          }
          if (type === 'incident' && msg.data) {
            setIncidents(prev => {
              const idx = prev.findIndex(i => i.id === msg.data!.id);
              if (idx >= 0) {
                const next = [...prev];
                next[idx] = msg.data;
                return next;
              }
              return [msg.data, ...prev].slice(0, 50);
            });
          }
          if (type === 'event' && msg.data) {
            setEvents(prev => [msg.data, ...prev].slice(0, 100));
          }
          if (type === 'integration_log' && msg.data) {
            // handled by IntegrationPanel
          }

          const cbs = listenersRef.current.get(type);
          if (cbs) cbs.forEach(cb => cb(msg.data || msg));
        } catch (e) {
          console.error('WS parse error:', e);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        clearInterval(pingTimer);
        wsRef.current = null;
        if (!isDestroyed) {
          reconnectTimer = setTimeout(connect, 3000);
        }
      };

      ws.onerror = () => ws.close();
    }

    connect();

    return () => {
      isDestroyed = true;
      clearTimeout(reconnectTimer);
      clearInterval(pingTimer);
      wsRef.current?.close();
    };
  }, []);

  return { connected, architecture, incidents, events, addListener };
}
