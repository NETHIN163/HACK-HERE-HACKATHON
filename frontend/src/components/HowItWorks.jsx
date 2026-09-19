import React, { useState } from 'react';
import { Cpu, Zap, Shield, AlertTriangle, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function HowItWorks() {
  const [activeTab, setActiveTab] = useState('discover');

  return (
    <section id="how-it-works" style={{ padding: '80px 32px', maxWidth: '1200px', margin: '0 auto', position: 'relative' }}>
      {/* Background orb glow */}
      <div style={{ position: 'absolute', top: '10%', right: '0', width: '400px', height: '400px', background: 'radial-gradient(circle, rgba(139, 92, 246, 0.12) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div style={{ textAlign: 'center', marginBottom: '50px' }}>
        <div className="glass-pill" style={{ marginBottom: '16px' }}>
          <Zap size={14} />
          <span>Core Platform Technology</span>
        </div>
        <h2 style={{ fontSize: '2.6rem', fontWeight: 800, color: '#f8fafc', marginBottom: '16px' }}>
          How Q-Flow Transforms Urban Mobility
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '1.05rem', maxWidth: '650px', margin: '0 auto' }}>
          From real-time traffic telemetry ingestion to quantum-powered QUBO signal execution and emergency corridor safety locks.
        </p>
      </div>

      {/* Feature Navigation Tabs */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', marginBottom: '32px', flexWrap: 'wrap' }}>
        {[
          { id: 'discover', label: '1. Real-Time Telemetry', icon: AlertTriangle },
          { id: 'qaoa', label: '2. Quantum QUBO Engine', icon: Cpu },
          { id: 'corridor', label: '3. Green Corridor Lock', icon: Zap },
          { id: 'conflict', label: '4. Incident Resolution', icon: Shield },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '10px 20px',
                borderRadius: '9999px',
                border: isActive ? '1px solid rgba(139, 92, 246, 0.4)' : '1px solid rgba(255, 255, 255, 0.08)',
                background: isActive ? 'rgba(139, 92, 246, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                color: isActive ? '#ffffff' : '#94a3b8',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.25s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <Icon size={14} color={isActive ? '#a78bfa' : '#94a3b8'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Feature Content Display Card */}
      <div className="glass-card-static" style={{ padding: '36px', borderRadius: '24px', border: '1px solid rgba(139, 92, 246, 0.2)' }}>
        {activeTab === 'discover' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', alignItems: 'center' }}>
            <div>
              <div className="glass-pill-cyan" style={{ marginBottom: '16px' }}>
                <span>Sub-Second Traffic Sensing</span>
              </div>
              <h3 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', marginBottom: '16px' }}>
                See Traffic Bottlenecks Where Legacy Systems Fail
              </h3>
              <p style={{ color: '#cbd5e1', lineHeight: 1.6, marginBottom: '20px', fontSize: '0.95rem' }}>
                Q-Flow continuously ingests queue length, vehicle density, road capacity, and emergency request signals across 4–8 connected intersections in a unified graph network.
              </p>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {[
                  'Live density monitoring across all direction lanes',
                  'Instant detection of emergency vehicle locations & ETA',
                  'Automatic vehicle wait-time & queue accumulation tracking',
                ].map((item, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#94a3b8', fontSize: '0.88rem' }}>
                    <CheckCircle2 size={16} color="#06b6d4" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Table Mockup */}
            <div style={{ background: '#090712', borderRadius: '16px', padding: '16px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                <span>Junction Node</span>
                <span>Queue Density</span>
                <span>Signal Status</span>
                <span>Severity</span>
              </div>
              {[
                { node: 'J1 (North Hub)', queue: '14 cars / min', status: 'GREEN CORRIDOR', sev: 'HIGH', color: '#10b981' },
                { node: 'J2 (Expressway)', queue: '22 cars / min', status: 'CONGESTED', sev: 'CRITICAL', color: '#f43f5e' },
                { node: 'J3 (Metro Central)', queue: '8 cars / min', status: 'ADAPTIVE', sev: 'MEDIUM', color: '#f59e0b' },
                { node: 'J4 (Trauma Gate)', queue: '3 cars / min', status: 'EMERGENCY LOCK', sev: 'LOW', color: '#a78bfa' },
              ].map((row, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: '0.8rem' }}>
                  <span style={{ fontWeight: 600, color: '#f8fafc' }}>{row.node}</span>
                  <span style={{ color: '#cbd5e1' }}>{row.queue}</span>
                  <span style={{ color: row.color, fontWeight: 700, fontSize: '0.75rem' }}>{row.status}</span>
                  <span style={{ padding: '2px 8px', borderRadius: '4px', background: `${row.color}15`, color: row.color, fontSize: '0.7rem', fontWeight: 700 }}>
                    {row.sev}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'qaoa' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', alignItems: 'center' }}>
            <div>
              <div className="glass-pill" style={{ marginBottom: '16px' }}>
                <span>Qiskit & PennyLane Integration</span>
              </div>
              <h3 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', marginBottom: '16px' }}>
                Hybrid Quantum-Classical Signal Optimization
              </h3>
              <p style={{ color: '#cbd5e1', lineHeight: 1.6, marginBottom: '20px', fontSize: '0.95rem' }}>
                Traffic signal timing across connected intersections is modeled as a Quadratic Unconstrained Binary Optimization (QUBO) problem. Q-Flow executes QAOA circuits to find global optimal phase durations 3.2x faster than classical exhaustive search.
              </p>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {[
                  'Ising Hamiltonian formulation targeting queue length minimization',
                  'Sub-50ms hybrid variational quantum solver (QAOA)',
                  'Dynamic green phase duration scaling based on live demand',
                ].map((item, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#94a3b8', fontSize: '0.88rem' }}>
                    <CheckCircle2 size={16} color="#a78bfa" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* QAOA Flowchart Mockup */}
            <div style={{ background: '#090712', borderRadius: '16px', padding: '24px', border: '1px solid rgba(139, 92, 246, 0.3)', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#a78bfa', textTransform: 'uppercase' }}>
                QUBO / QAOA Pipeline Execution
              </div>

              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>1. QUBO Objective Matrix</div>
                <div style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: '#67e8f9', marginTop: '4px' }}>
                  H = ∑ w_i * (Queue_i)^2 + λ * Penalty(Conflict)
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <ArrowRight size={18} color="#a78bfa" style={{ transform: 'rotate(90deg)' }} />
              </div>

              <div style={{ background: 'rgba(139, 92, 246, 0.1)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(139, 92, 246, 0.3)' }}>
                <div style={{ fontSize: '0.75rem', color: '#a78bfa' }}>2. QAOA Quantum Variational Ansatz</div>
                <div style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: '#ffffff', marginTop: '4px' }}>
                  |γ, β⟩ = ∏ e^(-i β_k H_B) e^(-i γ_k H_C) |+⟩
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <ArrowRight size={18} color="#a78bfa" style={{ transform: 'rotate(90deg)' }} />
              </div>

              <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                <div style={{ fontSize: '0.75rem', color: '#10b981' }}>3. Optimized Signal Allocation</div>
                <div style={{ fontSize: '0.8rem', color: '#ffffff', fontWeight: 600, marginTop: '4px' }}>
                  Phase Durations: J1=45s | J2=60s (Corridor) | J3=30s
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'corridor' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', alignItems: 'center' }}>
            <div>
              <div className="glass-pill-cyan" style={{ marginBottom: '16px' }}>
                <span>Dynamic Preemption Protocol</span>
              </div>
              <h3 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', marginBottom: '16px' }}>
                Instant Emergency Green Corridor Lock
              </h3>
              <p style={{ color: '#cbd5e1', lineHeight: 1.6, marginBottom: '20px', fontSize: '0.95rem' }}>
                When an ambulance triggers a trauma request, Q-Flow calculates the fastest candidate route and overrides signal phases along the entire path to guarantee green lights without creating side-street gridlocks.
              </p>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {[
                  'Automated signal preemption 30 seconds ahead of ambulance arrival',
                  'Side-street queue clearance buffer before lock activation',
                  'Self-healing phase restoration once emergency vehicle exits junction',
                ].map((item, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#94a3b8', fontSize: '0.88rem' }}>
                    <CheckCircle2 size={16} color="#06b6d4" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Visual Corridor Diagram */}
            <div style={{ background: '#090712', borderRadius: '16px', padding: '28px', border: '1px solid rgba(6, 182, 212, 0.3)', textAlign: 'center' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#67e8f9', marginBottom: '20px' }}>
                AMBULANCE AMB-01 → GREEN CORRIDOR ACTIVE
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', position: 'relative' }}>
                {['J1 (Pickup)', 'J2 (Transit)', 'J3 (Hospital)'].map((j, i) => (
                  <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', zIndex: 1 }}>
                    <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.2)', border: '2px solid #10b981', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 16px rgba(16, 185, 129, 0.5)' }}>
                      <Zap size={22} color="#10b981" />
                    </div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#f8fafc' }}>{j}</span>
                    <span style={{ fontSize: '0.65rem', color: '#10b981', fontWeight: 700 }}>GREEN LOCK</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'conflict' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', alignItems: 'center' }}>
            <div>
              <div className="glass-pill" style={{ marginBottom: '16px' }}>
                <span>Dynamic Incident Handling</span>
              </div>
              <h3 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', marginBottom: '16px' }}>
                Automated Incident & Rerouting Protocol
              </h3>
              <p style={{ color: '#cbd5e1', lineHeight: 1.6, marginBottom: '20px', fontSize: '0.95rem' }}>
                Whether facing sudden road closures, multi-vehicle accidents, or intersecting ambulance routes, Q-Flow’s conflict resolution engine dynamically computes alternative routes and avoids bottleneck collisions.
              </p>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {[
                  'Instant incident notification and road weight adjustment',
                  'Priority ranking matrix for overlapping emergency requests',
                  'Automatic environmental analysis (CO₂ and fuel savings calculation)',
                ].map((item, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#94a3b8', fontSize: '0.88rem' }}>
                    <CheckCircle2 size={16} color="#f43f5e" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Incident Alert Panel */}
            <div style={{ background: '#090712', borderRadius: '16px', padding: '24px', border: '1px solid rgba(244, 63, 94, 0.3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px', color: '#f43f5e' }}>
                <AlertTriangle size={20} />
                <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>INCIDENT DETECTED: ROAD J1-J2 BLOCKED</span>
              </div>
              <p style={{ fontSize: '0.8rem', color: '#cbd5e1', marginBottom: '16px' }}>
                Multi-vehicle accident reported. Q-Flow automatically updated graph edge weights and computed optimal bypass via J1 → J4 → J3.
              </p>
              <div style={{ background: 'rgba(244, 63, 94, 0.1)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(244, 63, 94, 0.2)', fontSize: '0.75rem', color: '#f8fafc' }}>
                Status: <strong style={{ color: '#10b981' }}>Bypass Route Calculated & Green Corridor Re-established</strong>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
