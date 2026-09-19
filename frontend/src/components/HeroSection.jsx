import React, { useState } from 'react';
import { ArrowRight, Sparkles, Activity, ShieldCheck, Zap, Cpu } from 'lucide-react';

export default function HeroSection({ onExploreOps }) {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const handlePointerMove = (event) => {
    const bounds = event.currentTarget.getBoundingClientRect();
    setTilt({
      x: ((event.clientX - bounds.left) / bounds.width - 0.5) * 2,
      y: ((event.clientY - bounds.top) / bounds.height - 0.5) * -2,
    });
  };

  const handlePointerLeave = () => {
    setTilt({ x: 0, y: 0 });
  };

  return (
    <section
      className="editorial-hero"
      onPointerMove={handlePointerMove}
      onPointerLeave={handlePointerLeave}
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

      {/* Floating Soft Particles */}
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
          transform: `perspective(1000px) rotateX(${tilt.y * 0.8}deg) rotateY(${tilt.x * 0.8}deg)`,
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
            color: '#1d1d1f',
          }}
        >
          Legacy Traffic Systems <br />
          <span className="text-gradient-purple">See Less and Less</span>
        </h1>

        {/* Subtitle */}
        <p
          style={{
            fontSize: '1.2rem',
            color: '#515154',
            maxWidth: '780px',
            margin: '0 auto 40px',
            lineHeight: 1.6,
            fontWeight: 400,
          }}
        >
          Legacy traffic controllers operate on rigid fixed timers. As urban congestion and emergency calls escalate, critical dispatch pathways gridlock out of view. <strong style={{ color: '#1d1d1f' }}>Q-Flow</strong> leverages hybrid QUBO & QAOA quantum optimization to dynamically route ambulances and synchronize green corridors in real time.
        </p>

        {/* Hero CTA Buttons */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginBottom: '60px' }}>
          <button className="btn-orchid-primary" onClick={onExploreOps}>
            <span>Launch Live Simulator</span>
            <ArrowRight size={18} />
          </button>
          <button className="btn-orchid-secondary" onClick={onExploreOps}>
            <Activity size={18} color="#0071e3" />
            <span>Explore Live Telemetry</span>
          </button>
        </div>
      </div>

      {/* Hero Interactive 3D Card Holographic Container */}
      <div
        className="ar-card-3d"
        id="simulator"
        style={{
          padding: '28px',
          borderRadius: '28px',
          border: '1px solid rgba(0, 113, 227, 0.2)',
          textAlign: 'left',
          position: 'relative',
          overflow: 'hidden',
           transform: `perspective(1000px) rotateX(${tilt.y * 1.2}deg) rotateY(${tilt.x * 1.2}deg) translateZ(10px)`,
          transition: 'transform 0.15s ease-out',
          zIndex: 2,
        }}
      >
        <div className="ar-holo-reflection" />
        {/* Glow overlay */}
        <div style={{ position: 'absolute', top: -50, right: -50, width: '250px', height: '250px', background: 'radial-gradient(circle, rgba(0, 113, 227, 0.12) 0%, transparent 70%)', pointerEvents: 'none' }} />

        <div className="generative-network-graph" aria-label="Animated six junction network graph">
          <div className="graph-caption"><span className="graph-live-dot" /> LIVE TOPOLOGY SYNTHESIS <b>6 NODES / 8 LINKS</b></div>
          {['j1-j2', 'j2-j3', 'j1-j4', 'j2-j5', 'j3-j6', 'j4-j5', 'j5-j6', 'j2-j4'].map((edge, index) => (
            <span key={edge} className={`graph-edge graph-edge-${edge}`} style={{ animationDelay: `${index * 0.35}s` }}><i /></span>
          ))}
          {[
            ['j1', 'J1', 'NORTH'], ['j2', 'J2', 'EAST'], ['j3', 'J3', 'METRO'],
            ['j4', 'J4', 'TRAUMA'], ['j5', 'J5', 'WEST'], ['j6', 'J6', 'SOUTH'],
          ].map(([className, id, label]) => (
            <span key={id} className={`graph-node graph-node-${className}`}><b>{id}</b><small>{label}</small></span>
          ))}
        </div>

        {/* Header bar of preview */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid rgba(0,0,0,0.06)', paddingBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '8px', background: 'linear-gradient(135deg, #0071e3, #6e56cf)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Cpu size={16} color="#ffffff" />
            </div>
            <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#1d1d1f', letterSpacing: '0.5px' }}>
              3D QUANTUM NETWORK GRAPH SIMULATOR
            </span>
          </div>
          <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem', color: '#86868b' }}>
            <span>Topology: <strong style={{ color: '#0071e3' }}>6 Connected Junctions</strong></span>
            <span>QAOA Execution: <strong style={{ color: '#34c759' }}>14.2 ms</strong></span>
            <span>Preemption: <strong style={{ color: '#6e56cf' }}>Corridor Active</strong></span>
          </div>
        </div>

        {/* Content grid preview */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '20px' }}>
          {/* Signal grid */}
          <div style={{ background: 'rgba(245, 245, 247, 0.8)', padding: '20px', borderRadius: '16px', border: '1px solid rgba(0,0,0,0.06)' }}>
            <div style={{ fontSize: '0.8rem', color: '#86868b', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '12px' }}>
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
                <div key={idx} className="glass-card" style={{ padding: '12px', borderRadius: '12px', border: '1px solid rgba(0,0,0,0.06)' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#1d1d1f', marginBottom: '4px' }}>{j.name}</div>
                  <div style={{ fontSize: '0.65rem', fontWeight: 700, color: j.status.includes('CORRIDOR') ? '#34c759' : '#0071e3', marginBottom: '4px' }}>
                    {j.status}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#86868b' }}>Queue: {j.queue}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Telemetry Panel */}
          <div style={{ background: 'rgba(245, 245, 247, 0.8)', padding: '20px', borderRadius: '16px', border: '1px solid rgba(0,0,0,0.06)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#86868b', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '12px' }}>
                Quantum vs Classical Impact
              </div>
              <div style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                  <span style={{ color: '#515154' }}>Ambulance Travel Time</span>
                  <span style={{ color: '#34c759', fontWeight: 700 }}>-75% Faster</span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(0,0,0,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: '75%', height: '100%', background: 'linear-gradient(90deg, #34c759, #0071e3)' }} />
                </div>
              </div>

              <div style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                  <span style={{ color: '#515154' }}>Fuel & Emissions Reduced</span>
                  <span style={{ color: '#6e56cf', fontWeight: 700 }}>-38% CO₂ Saved</span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(0,0,0,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: '62%', height: '100%', background: 'linear-gradient(90deg, #6e56cf, #a78bfa)' }} />
                </div>
              </div>
            </div>

            <div style={{ background: 'rgba(110, 86, 207, 0.08)', border: '1px solid rgba(110, 86, 207, 0.2)', padding: '12px', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ShieldCheck size={18} color="#6e56cf" />
              <span style={{ fontSize: '0.75rem', color: '#515154', lineHeight: 1.4 }}>
                100% Green Corridor Priority Enforced via Qiskit QUBO formulation
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
