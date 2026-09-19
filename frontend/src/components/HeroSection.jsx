import React, { useState } from 'react';
import { ArrowRight, Sparkles, Activity, ShieldCheck, Zap, Cpu } from 'lucide-react';

export default function HeroSection({ onExploreOps }) {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    setMousePos({ x: (x / rect.width) * 30, y: -(y / rect.height) * 30 });
  };

  const handleMouseLeave = () => {
    setMousePos({ x: 0, y: 0 });
  };

  return (
    <section
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        padding: '80px 32px 60px',
        maxWidth: '1200px',
        margin: '0 auto',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Laser Beam Motion Scanline */}
      <div className="ar-laser-beam" />

      {/* Floating Animated Bubbles */}
      <div className="bubble bubble-1" />
      <div className="bubble bubble-2" />
      <div className="bubble bubble-3" />
      <div className="bubble bubble-4" />

      {/* Pill Badge */}
      <div style={{ marginBottom: '24px', position: 'relative', zIndex: 2 }}>
        <div className="glass-pill">
          <Sparkles size={14} />
          <span>Quantum Motion Graphics Engine</span>
        </div>
      </div>

      {/* Main Title with 3D Parallax Perspective */}
      <div
        style={{
          transform: `perspective(1000px) rotateX(${mousePos.y * 0.3}deg) rotateY(${mousePos.x * 0.3}deg)`,
          transition: 'transform 0.1s ease-out',
          position: 'relative',
          zIndex: 2,
        }}
      >
        <h1
          style={{
            fontSize: '3.8rem',
            fontWeight: 800,
            lineHeight: 1.1,
            letterSpacing: '-1.5px',
            marginBottom: '24px',
            maxWidth: '900px',
            margin: '0 auto 24px',
          }}
        >
          Legacy Traffic Systems <br />
          <span className="text-gradient-purple">See Less and Less</span>
        </h1>

        {/* Subtitle */}
        <p
          style={{
            fontSize: '1.2rem',
            color: '#cbd5e1',
            maxWidth: '780px',
            margin: '0 auto 40px',
            lineHeight: 1.6,
            fontWeight: 400,
          }}
        >
          Legacy traffic controllers operate on rigid fixed timers. As urban congestion and emergency calls escalate, critical dispatch pathways gridlock out of view. <strong style={{ color: '#ffffff' }}>Q-Flow</strong> leverages hybrid QUBO & QAOA quantum optimization to dynamically route ambulances and synchronize green corridors in real time.
        </p>

        {/* Hero CTA Buttons */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginBottom: '60px' }}>
          <button className="btn-orchid-primary" onClick={onExploreOps}>
            <span>Launch Live Simulator</span>
            <ArrowRight size={18} />
          </button>
          <button className="btn-orchid-glow" onClick={onExploreOps}>
            <Activity size={18} />
            <span>Explore Live Telemetry</span>
          </button>
        </div>
      </div>

      {/* Hero Interactive 3D Card Holographic Container */}
      <div
        className="ar-card-3d"
        style={{
          padding: '28px',
          borderRadius: '28px',
          border: '1px solid rgba(139, 92, 246, 0.4)',
          textAlign: 'left',
          position: 'relative',
          overflow: 'hidden',
          transform: `perspective(1000px) rotateX(${mousePos.y * 0.5}deg) rotateY(${mousePos.x * 0.5}deg) translateZ(10px)`,
          transition: 'transform 0.15s ease-out',
          zIndex: 2,
        }}
      >
        <div className="ar-holo-reflection" />
        {/* Glow overlay */}
        <div style={{ position: 'absolute', top: -50, right: -50, width: '250px', height: '250px', background: 'radial-gradient(circle, rgba(6, 182, 212, 0.25) 0%, transparent 70%)', pointerEvents: 'none' }} />

        {/* Header bar of preview */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '8px', background: 'linear-gradient(135deg, #06b6d4, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Cpu size={16} color="#ffffff" />
            </div>
            <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '0.5px' }}>
              3D QUANTUM NETWORK GRAPH SIMULATOR
            </span>
          </div>
          <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem', color: '#94a3b8' }}>
            <span>Topology: <strong style={{ color: '#06b6d4' }}>6 Connected Junctions</strong></span>
            <span>QAOA Execution: <strong style={{ color: '#10b981' }}>14.2 ms</strong></span>
            <span>Preemption: <strong style={{ color: '#a78bfa' }}>Corridor Active</strong></span>
          </div>
        </div>

        {/* Content grid preview */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '20px' }}>
          {/* Signal grid */}
          <div style={{ background: 'rgba(11, 8, 19, 0.7)', padding: '20px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.06)' }}>
            <div style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '12px' }}>
              Adaptive Signal Allocation (Qiskit QUBO)
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
              {[
                { name: 'J1: North Central', status: 'GREEN CORRIDOR', queue: '2 vehicles', mode: 'QAOA Lock' },
                { name: 'J2: East Expressway', status: 'ADAPTIVE GREEN', queue: '5 vehicles', mode: 'QUBO Opt' },
                { name: 'J3: Metro Hub', status: 'GREEN CORRIDOR', queue: '1 vehicle', mode: 'QAOA Lock' },
                { name: 'J4: Trauma Center', status: 'CLEARING', queue: '0 vehicles', mode: 'Priority Lock' },
                { name: 'J5: West Avenue', status: 'DYNAMIC ADAPT', queue: '8 vehicles', mode: 'Adaptive' },
                { name: 'J6: South Bypass', status: 'OPTIMIZED', queue: '4 vehicles', mode: 'QUBO Opt' },
              ].map((j, idx) => (
                <div key={idx} className="glass-card" style={{ padding: '12px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#f8fafc', marginBottom: '4px' }}>{j.name}</div>
                  <div style={{ fontSize: '0.65rem', fontWeight: 700, color: j.status.includes('CORRIDOR') ? '#10b981' : '#06b6d4', marginBottom: '4px' }}>
                    {j.status}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>Queue: {j.queue}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Telemetry Panel */}
          <div style={{ background: 'rgba(11, 8, 19, 0.7)', padding: '20px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.06)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '12px' }}>
                Quantum vs Classical Impact
              </div>
              <div style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                  <span style={{ color: '#cbd5e1' }}>Ambulance Travel Time</span>
                  <span style={{ color: '#10b981', fontWeight: 700 }}>-75% Faster</span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: '75%', height: '100%', background: 'linear-gradient(90deg, #10b981, #06b6d4)' }} />
                </div>
              </div>

              <div style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                  <span style={{ color: '#cbd5e1' }}>Fuel & Emissions Reduced</span>
                  <span style={{ color: '#a78bfa', fontWeight: 700 }}>-38% CO₂ Saved</span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: '62%', height: '100%', background: 'linear-gradient(90deg, #8b5cf6, #a78bfa)' }} />
                </div>
              </div>
            </div>

            <div style={{ background: 'rgba(139, 92, 246, 0.12)', border: '1px solid rgba(139, 92, 246, 0.3)', padding: '12px', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ShieldCheck size={18} color="#a78bfa" />
              <span style={{ fontSize: '0.75rem', color: '#cbd5e1', lineHeight: 1.4 }}>
                100% Green Corridor Priority Enforced via Qiskit QUBO formulation
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
