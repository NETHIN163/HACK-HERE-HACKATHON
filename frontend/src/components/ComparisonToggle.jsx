import React, { useState } from 'react';
import { Shield, Sparkles, Check, X, ArrowRight } from 'lucide-react';

export default function ComparisonToggle() {
  const [mode, setMode] = useState('with'); // 'before' or 'with'

  return (
    <section id="architecture" style={{ padding: '80px 32px', maxWidth: '1200px', margin: '0 auto', textAlign: 'center' }}>
      <div style={{ marginBottom: '40px' }}>
        <div className="glass-pill" style={{ marginBottom: '16px' }}>
          <Sparkles size={14} />
          <span>Architecture & Capability</span>
        </div>
        <h2 style={{ fontSize: '2.6rem', fontWeight: 800, color: '#f8fafc', marginBottom: '16px' }}>
          Simple, Fast, Automated
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '1.05rem', maxWidth: '650px', margin: '0 auto' }}>
          Replacing rigid, costly legacy traffic hardware with a cloud-native, quantum-assisted network orchestration platform.
        </p>
      </div>

      {/* Toggle Selector */}
      <div style={{ display: 'inline-flex', background: 'rgba(255, 255, 255, 0.05)', padding: '4px', borderRadius: '9999px', border: '1px solid rgba(255, 255, 255, 0.08)', marginBottom: '40px' }}>
        <button
          onClick={() => setMode('before')}
          style={{
            padding: '10px 24px',
            borderRadius: '9999px',
            border: 'none',
            fontSize: '0.9rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.25s ease',
            background: mode === 'before' ? 'rgba(239, 68, 68, 0.2)' : 'transparent',
            color: mode === 'before' ? '#f43f5e' : '#94a3b8',
          }}
        >
          Before Q-Flow
        </button>
        <button
          onClick={() => setMode('with')}
          style={{
            padding: '10px 24px',
            borderRadius: '9999px',
            border: 'none',
            fontSize: '0.9rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.25s ease',
            background: mode === 'with' ? 'linear-gradient(135deg, #8b5cf6, #06b6d4)' : 'transparent',
            color: mode === 'with' ? '#ffffff' : '#94a3b8',
            boxShadow: mode === 'with' ? '0 0 16px rgba(139, 92, 246, 0.4)' : 'none',
          }}
        >
          With Q-Flow
        </button>
      </div>

      {/* Comparison Grid Box */}
      <div className="glass-card-static" style={{ padding: '40px', borderRadius: '24px', border: mode === 'with' ? '1px solid rgba(139, 92, 246, 0.3)' : '1px solid rgba(239, 68, 68, 0.3)', textAlign: 'left' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '32px' }}>
          {[
            {
              category: 'Signal Timing Logic',
              before: 'Fixed timer cycles (e.g. 60s/30s) regardless of live queue spikes',
              with: 'QAOA & QUBO adaptive phase allocation updated sub-second',
            },
            {
              category: 'Emergency Dispatch',
              before: 'Manual siren clearance; ambulances trapped in gridlocks',
              with: 'Automated Green Corridor preemption lock 30s ahead',
            },
            {
              category: 'Incident Response',
              before: 'Manual dispatch rerouting takes 15–20 minutes',
              with: 'Sub-50ms dynamic graph reweighting & bypass path calculation',
            },
            {
              category: 'Environmental CO₂ Impact',
              before: 'High fuel waste from long idle queues at red lights',
              with: 'Up to 38% reduction in idling fuel consumption & emissions',
            },
          ].map((item, idx) => (
            <div key={idx} style={{ background: 'rgba(11, 8, 19, 0.6)', padding: '20px', borderRadius: '14px', border: '1px solid rgba(255,255,255,0.05)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: mode === 'with' ? '#a78bfa' : '#f43f5e', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
                  {item.category}
                </div>
                <div style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                  {mode === 'with' ? item.with : item.before}
                </div>
              </div>
              <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 600, color: mode === 'with' ? '#10b981' : '#f43f5e' }}>
                {mode === 'with' ? <Check size={14} /> : <X size={14} />}
                <span>{mode === 'with' ? 'Automated Quantum AI' : 'Manual / Legacy Bottleneck'}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Node Comparison Grid */}
        <div style={{ background: '#07050e', padding: '24px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.06)' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc', marginBottom: '16px' }}>
            {mode === 'with' ? 'Q-FLOW QUANTUM-COORDINATED NETWORK GRAPH' : 'LEGACY ISOLATED INTERSECTION MATRIX'}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px' }}>
            {['App 1: J1 North', 'App 2: J2 East', 'App 3: J3 Hub', 'App 4: J4 Trauma', 'App 5: J5 Avenue', 'App 6: J6 South'].map((app, i) => (
              <div key={i} style={{ background: mode === 'with' ? 'rgba(139, 92, 246, 0.1)' : 'rgba(239, 68, 68, 0.08)', padding: '12px', borderRadius: '10px', border: mode === 'with' ? '1px solid rgba(139, 92, 246, 0.3)' : '1px solid rgba(239, 68, 68, 0.2)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>{app}</div>
                <div style={{ fontSize: '0.65rem', color: mode === 'with' ? '#67e8f9' : '#f43f5e', fontWeight: 600 }}>
                  {mode === 'with' ? 'QUBO Synced' : 'Uncoordinated'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
