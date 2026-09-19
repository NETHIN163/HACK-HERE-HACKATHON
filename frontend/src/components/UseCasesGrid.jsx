import React from 'react';
import { ArrowUpRight, ShieldAlert, Truck, Sparkles, Building2, ChevronRight, ChevronLeft } from 'lucide-react';

export default function UseCasesGrid({ onSelectUseCase }) {
  const cases = [
    {
      icon: Truck,
      title: 'Accelerate Emergency Response to the Speed of Life',
      desc: 'Dynamic preemption corridors for ambulances, fire engines, and police units guaranteeing zero delay at busy intersections.',
      badge: 'Emergency Services',
      color: '#a78bfa',
    },
    {
      icon: Building2,
      title: 'Maintain City Grid Audit Readiness & Zero Accidents',
      desc: 'Real-time safety posture validation ensuring overlapping corridors never create orthogonal green signal conflicts.',
      badge: 'Municipal Traffic Dept',
      color: '#67e8f9',
    },
    {
      icon: ShieldAlert,
      title: 'Respond to Sudden Gridlocks at the Speed of Detection',
      desc: 'Automatic rerouting around traffic accidents, road closures, and localized congestion spikes using QUBO graph solvers.',
      badge: 'Smart City Ops',
      color: '#f43f5e',
    },
    {
      icon: Sparkles,
      title: '38% Citywide Carbon Offset & Idle Fuel Saved',
      desc: 'Eliminates unnecessary red light idling by adapting signal phase duration dynamically to real-time traffic demand.',
      badge: 'Green City Sustainability',
      color: '#10b981',
    },
  ];

  const scrollTrack = (direction) => {
    const el = document.getElementById('horizontal-track');
    if (el) {
      const scrollAmount = direction === 'left' ? -400 : 400;
      el.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  return (
    <section style={{ padding: '60px 32px 80px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '32px' }}>
        <div>
          <div className="glass-pill" style={{ marginBottom: '12px' }}>
            <Sparkles size={14} />
            <span>Horizontal Motion Track</span>
          </div>
          <h2 style={{ fontSize: '2.4rem', fontWeight: 800, color: '#f8fafc' }}>
            Tailored Municipal Deployments
          </h2>
        </div>

        {/* Scroll Arrows */}
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            className="btn-orchid-secondary"
            style={{ padding: '10px 14px', borderRadius: '50%' }}
            onClick={() => scrollTrack('left')}
          >
            <ChevronLeft size={18} />
          </button>
          <button
            className="btn-orchid-secondary"
            style={{ padding: '10px 14px', borderRadius: '50%' }}
            onClick={() => scrollTrack('right')}
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      {/* Horizontal Scroll Cards Track */}
      <div id="horizontal-track" className="horizontal-scroll-track">
        {cases.map((c, idx) => {
          const Icon = c.icon;
          return (
            <div
              key={idx}
              className="horizontal-scroll-item glass-card ar-card-3d"
              style={{
                padding: '32px',
                borderRadius: '24px',
                display: 'flex',
                flexDirection: 'column',
                justify: 'space-between',
                cursor: 'pointer',
              }}
              onClick={() => onSelectUseCase && onSelectUseCase(c)}
            >
              <div className="ar-holo-reflection" />
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: `${c.color}15`, border: `1px solid ${c.color}35`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon size={24} color={c.color} />
                  </div>
                  <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'rgba(139, 92, 246, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <ArrowUpRight size={18} color="#a78bfa" />
                  </div>
                </div>

                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: c.color, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '10px' }}>
                  {c.badge}
                </div>

                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginBottom: '12px', lineHeight: 1.4 }}>
                  {c.title}
                </h3>

                <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: 1.6 }}>
                  {c.desc}
                </p>
              </div>

              <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.06)', fontSize: '0.8rem', fontWeight: 600, color: '#a78bfa', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>Launch simulation module</span>
                <ArrowUpRight size={14} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
