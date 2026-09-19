import React from 'react';
import { Cpu, Zap, Activity, ShieldCheck, Leaf, Sparkles } from 'lucide-react';

export default function HorizontalTicker() {
  const tickerItems = [
    { text: 'QAOA VARIATIONAL SOLVER: 14.2ms EXECUTION', icon: Cpu, color: '#06b6d4' },
    { text: 'EMERGENCY GREEN CORRIDOR: 100% PREEMPTION LOCK', icon: Zap, color: '#10b981' },
    { text: 'QISKIT AER ISING HAMILTONIAN: OPTIMAL PHASE STATE', icon: Activity, color: '#a78bfa' },
    { text: 'ZERO COLLISION CONFLICT RESOLUTION PROTOCOL', icon: ShieldCheck, color: '#3b82f6' },
    { text: '38% CO₂ EMISSIONS & FUEL IDLE WASTE REDUCTION', icon: Leaf, color: '#10b981' },
    { text: 'PENNYLANE QUANTUM CIRCUIT GRADIENT OPTIMIZER', icon: Sparkles, color: '#f59e0b' },
  ];

  // Duplicate list to create seamless infinite marquee loop
  const fullList = [...tickerItems, ...tickerItems];

  return (
    <div
      style={{
        width: '100%',
        overflow: 'hidden',
        background: 'rgba(11, 8, 19, 0.8)',
        borderTop: '1px solid rgba(139, 92, 246, 0.2)',
        borderBottom: '1px solid rgba(6, 182, 212, 0.2)',
        padding: '14px 0',
        backdropFilter: 'blur(12px)',
        position: 'relative',
        zIndex: 10,
      }}
    >
      <div className="marquee-track">
        {fullList.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={idx}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '10px',
                padding: '6px 20px',
                marginRight: '16px',
                borderRadius: '9999px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                whiteSpace: 'nowrap',
                fontSize: '0.8rem',
                fontWeight: 700,
                letterSpacing: '0.5px',
              }}
            >
              <Icon size={14} color={item.color} />
              <span style={{ color: '#ffffff' }}>{item.text}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
