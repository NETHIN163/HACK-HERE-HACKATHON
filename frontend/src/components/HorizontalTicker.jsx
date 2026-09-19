import React from 'react';
import { Cpu, Zap, Activity, ShieldCheck, Leaf, Sparkles } from 'lucide-react';

export default function HorizontalTicker() {
  const tickerItems = [
    { text: 'QAOA VARIATIONAL SOLVER: 14.2ms EXECUTION', icon: Cpu, color: '#0071e3' },
    { text: 'EMERGENCY GREEN CORRIDOR: 100% PREEMPTION LOCK', icon: Zap, color: '#34c759' },
    { text: 'QISKIT AER ISING HAMILTONIAN: OPTIMAL PHASE STATE', icon: Activity, color: '#6e56cf' },
    { text: 'ZERO COLLISION CONFLICT RESOLUTION PROTOCOL', icon: ShieldCheck, color: '#0071e3' },
    { text: '38% CO₂ EMISSIONS & FUEL IDLE WASTE REDUCTION', icon: Leaf, color: '#34c759' },
    { text: 'PENNYLANE QUANTUM CIRCUIT GRADIENT OPTIMIZER', icon: Sparkles, color: '#ff9500' },
  ];

  // Duplicate list to create seamless infinite marquee loop
  const fullList = [...tickerItems, ...tickerItems];

  return (
    <div
      style={{
        width: '100%',
        overflow: 'hidden',
        background: 'rgba(255, 255, 255, 0.8)',
        borderTop: '1px solid rgba(0, 0, 0, 0.06)',
        borderBottom: '1px solid rgba(0, 0, 0, 0.06)',
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
                background: 'rgba(0, 0, 0, 0.03)',
                border: '1px solid rgba(0, 0, 0, 0.06)',
                whiteSpace: 'nowrap',
                fontSize: '0.8rem',
                fontWeight: 700,
                letterSpacing: '0.5px',
              }}
            >
              <Icon size={14} color={item.color} />
              <span style={{ color: '#1d1d1f' }}>{item.text}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
