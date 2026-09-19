/**
 * Q-FLOW Phase 2 Developer Integration Verification Dashboard
 */

import React, { useState, useEffect } from 'react';
import ConnectionStatus from './components/ConnectionStatus';
import { useAppState, useAppDispatch } from './context/AppContext';
import { useWebSocket } from './context/WebSocketContext';
import {
  trafficService,
  metricsService,
  incidentService,
  emergencyService,
  ambulanceService,
  routingService,
} from './services/api';

export default function App() {
  const { wsStatus, apiConnected, junctions, roads, incidents, metrics, emergencyRequests, ambulances, logs, error } =
    useAppState();
  const dispatch = useAppDispatch();
  const { connect, disconnect } = useWebSocket();

  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');

  // Verify API Connection on mount
  useEffect(() => {
    checkApiConnection();
  }, []);

  const checkApiConnection = async () => {
    try {
      setLoading(true);
      const data = await trafficService.getTrafficState();
      dispatch({ type: 'SET_TRAFFIC_STATE', payload: data });
      dispatch({ type: 'SET_API_CONNECTED', payload: true });
      dispatch({ type: 'ADD_LOG', payload: 'API Check Success: Traffic state retrieved' });
    } catch (err) {
      dispatch({ type: 'SET_API_CONNECTED', payload: false });
      dispatch({ type: 'SET_ERROR', payload: `API Connection Failed: ${err.message}` });
      dispatch({ type: 'ADD_LOG', payload: `API Check Error: ${err.message}` });
    } finally {
      setLoading(false);
    }
  };

  const handleFetchJunctions = async () => {
    try {
      setLoading(true);
      const data = await trafficService.getJunctions();
      dispatch({ type: 'SET_JUNCTIONS', payload: data });
      dispatch({ type: 'ADD_LOG', payload: `Fetched ${data.length} junctions` });
    } catch (err) {
      dispatch({ type: 'SET_ERROR', payload: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleFetchRoads = async () => {
    try {
      setLoading(true);
      const data = await trafficService.getRoads();
      dispatch({ type: 'SET_ROADS', payload: data });
      dispatch({ type: 'ADD_LOG', payload: `Fetched ${data.length} roads` });
    } catch (err) {
      dispatch({ type: 'SET_ERROR', payload: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleFetchIncidents = async () => {
    try {
      setLoading(true);
      const data = await incidentService.getIncidents();
      dispatch({ type: 'SET_INCIDENTS', payload: data });
      dispatch({ type: 'ADD_LOG', payload: `Fetched ${data.length} incidents` });
    } catch (err) {
      dispatch({ type: 'SET_ERROR', payload: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleFetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await metricsService.getMetrics();
      dispatch({ type: 'SET_METRICS', payload: data });
      dispatch({ type: 'ADD_LOG', payload: 'Fetched live traffic metrics' });
    } catch (err) {
      dispatch({ type: 'SET_ERROR', payload: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleFetchAmbulances = async () => {
    try {
      setLoading(true);
      const data = await ambulanceService.getAmbulances();
      dispatch({ type: 'SET_AMBULANCES', payload: data });
      dispatch({ type: 'ADD_LOG', payload: `Fetched ${data.length} ambulances` });
    } catch (err) {
      dispatch({ type: 'SET_ERROR', payload: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleTestEmergencyRequest = async () => {
    try {
      setLoading(true);
      const reqData = {
        origin: 'J1',
        destination: 'J3',
        priority: 1,
      };
      const result = await emergencyService.createRequest(reqData);
      dispatch({ type: 'ADD_EMERGENCY_REQUEST', payload: result });
      dispatch({ type: 'ADD_LOG', payload: `Created Emergency Request: ${result.request_id}` });
    } catch (err) {
      dispatch({ type: 'SET_ERROR', payload: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleTestEmergencyRoute = async () => {
    try {
      setLoading(true);
      const route = await routingService.calculateRoute('J1', 'J3');
      dispatch({ type: 'ADD_LOG', payload: `Calculated Route J1->J3: ${route.selected_path.join('->')}` });
    } catch (err) {
      dispatch({ type: 'SET_ERROR', payload: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <header
        className="glass-panel"
        style={{
          padding: '20px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Q-FLOW <span style={{ color: 'var(--accent-cyan)', fontSize: '1rem' }}>| Phase 2 Foundation</span>
          </h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Frontend API Layer + WebSocket Client + State Foundation Verification
          </p>
        </div>
        <ConnectionStatus />
      </header>

      {/* Error Alert */}
      {error && (
        <div
          className="glass-panel"
          style={{
            padding: '12px 16px',
            marginBottom: '20px',
            borderColor: 'var(--status-blocked)',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span style={{ color: 'var(--status-blocked)', fontSize: '0.9rem', fontWeight: 500 }}>{error}</span>
          <button
            onClick={() => dispatch({ type: 'SET_ERROR', payload: null })}
            className="btn-secondary"
            style={{ padding: '4px 8px', fontSize: '0.75rem' }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Integration Verification Action Bar */}
      <section className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px', color: 'var(--accent-cyan)' }}>
          API & WebSocket Verification Suite
        </h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          <button className="btn-primary" onClick={checkApiConnection} disabled={loading}>
            1. Check Traffic API
          </button>
          <button className="btn-secondary" onClick={handleFetchJunctions} disabled={loading}>
            2. Fetch Junctions ({junctions.length})
          </button>
          <button className="btn-secondary" onClick={handleFetchRoads} disabled={loading}>
            3. Fetch Roads ({roads.length})
          </button>
          <button className="btn-secondary" onClick={handleFetchIncidents} disabled={loading}>
            4. Fetch Incidents ({incidents.length})
          </button>
          <button className="btn-secondary" onClick={handleFetchMetrics} disabled={loading}>
            5. Fetch Metrics
          </button>
          <button className="btn-secondary" onClick={handleFetchAmbulances} disabled={loading}>
            6. Fetch Ambulances ({ambulances.length})
          </button>
          <button className="btn-primary" onClick={handleTestEmergencyRequest} disabled={loading}>
            7. Test Emergency Request API
          </button>
          <button className="btn-primary" onClick={handleTestEmergencyRoute} disabled={loading}>
            8. Test Emergency Route API
          </button>
          <button className="btn-secondary" onClick={disconnect} style={{ color: 'var(--status-blocked)' }}>
            Disconnect WS
          </button>
          <button className="btn-secondary" onClick={connect} style={{ color: 'var(--status-open)' }}>
            Reconnect WS
          </button>
        </div>
      </section>

      {/* Main Grid State View */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Left Column: State Summary */}
        <section className="glass-panel" style={{ padding: '20px' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px' }}>Current State Foundation Summary</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>API Status</div>
              <div style={{ fontWeight: 600, color: apiConnected ? 'var(--status-open)' : 'var(--status-blocked)' }}>
                {apiConnected ? 'CONNECTED' : 'UNAVAILABLE'}
              </div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>WS Status</div>
              <div style={{ fontWeight: 600, color: wsStatus === 'CONNECTED' ? 'var(--status-open)' : 'var(--status-congested)' }}>
                {wsStatus}
              </div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Junctions / Roads</div>
              <div style={{ fontWeight: 600 }}>
                {junctions.length} Junctions / {roads.length} Roads
              </div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Incidents Active</div>
              <div style={{ fontWeight: 600 }}>{incidents.length} Active</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Emergency Requests</div>
              <div style={{ fontWeight: 600 }}>{emergencyRequests.length} Created</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Ambulances Fleet</div>
              <div style={{ fontWeight: 600 }}>{ambulances.length} Registered</div>
            </div>
          </div>

          <div style={{ marginTop: '16px', background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Live Metrics Snapshot</div>
            <div style={{ fontSize: '0.8rem', fontFamily: 'monospace' }}>
              Wait Time: {metrics.average_wait_time}s | Queues: {metrics.queue_length} | Throughput: {metrics.throughput}
            </div>
          </div>
        </section>

        {/* Right Column: Live Event Log Stream */}
        <section className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 600 }}>Live Integration Event Log</h2>
            <button
              className="btn-secondary"
              style={{ padding: '2px 8px', fontSize: '0.75rem' }}
              onClick={() => dispatch({ type: 'ADD_LOG', payload: 'Log cleared' })}
            >
              Clear Logs
            </button>
          </div>
          <div
            style={{
              height: '240px',
              overflowY: 'auto',
              background: '#070a12',
              borderRadius: '8px',
              padding: '12px',
              fontFamily: 'monospace',
              fontSize: '0.75rem',
              border: '1px solid var(--border-subtle)',
            }}
          >
            {logs.length === 0 ? (
              <div style={{ color: 'var(--text-muted)' }}>Waiting for events or actions...</div>
            ) : (
              logs.map((log) => (
                <div key={log.id} style={{ marginBottom: '6px', borderBottom: '1px solid rgba(255,255,255,0.03)', paddingBottom: '4px' }}>
                  <span style={{ color: 'var(--accent-cyan)' }}>[{log.timestamp}]</span>{' '}
                  <span style={{ color: 'var(--text-secondary)' }}>{log.text}</span>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
