import React from 'react';
import { Sparkles, TrendingUp, Clock, ShieldCheck } from 'lucide-react';

export default function ImpactStats() {
  return (
    <section id="impact" style={{ padding: '60px 32px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <div className="glass-pill" style={{ marginBottom: '16px' }}>
          <Sparkles size={14} />
          <span>What Cities Achieve</span>
        </div>
        <h2 style={{ fontSize: '2.4rem', fontWeight: 800, color: '#1d1d1f' }}>
          Measurable Impact Across Every Corridor
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
        {/* Card 1 */}
        <div className="glass-card" style={{ padding: '36px 28px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '4rem', fontWeight: 800, letterSpacing: '-2px', color: '#1d1d1f', marginBottom: '12px', background: 'linear-gradient(135deg, #1d1d1f, #0071e3)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              75%
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#1d1d1f', marginBottom: '12px' }}>
              Cut emergency travel time by
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#86868b', lineHeight: 1.5 }}>
              Imagine reducing emergency ambulance travel time from 16 minutes down to under 4 minutes across dense urban gridlocks.
            </p>
          </div>
          <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid rgba(0,0,0,0.06)', display: 'flex', alignItems: 'center', gap: '8px', color: '#0071e3', fontSize: '0.8rem', fontWeight: 600 }}>
            <Clock size={16} />
            <span>Green Corridor Preemption</span>
          </div>
        </div>

        {/* Card 2 */}
        <div className="glass-card" style={{ padding: '36px 28px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '4rem', fontWeight: 800, letterSpacing: '-2px', color: '#1d1d1f', marginBottom: '12px', background: 'linear-gradient(135deg, #1d1d1f, #6e56cf)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              97%
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#1d1d1f', marginBottom: '12px' }}>
              Reduce gridlock congestion cost by
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#86868b', lineHeight: 1.5 }}>
              Eliminate unnecessary waiting times and vehicle idle fuel waste by replacing static timers with adaptive QUBO quantum optimization.
            </p>
          </div>
          <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid rgba(0,0,0,0.06)', display: 'flex', alignItems: 'center', gap: '8px', color: '#6e56cf', fontSize: '0.8rem', fontWeight: 600 }}>
            <TrendingUp size={16} />
            <span>QUBO Signal Balancing</span>
          </div>
        </div>

        {/* Card 3 */}
        <div className="glass-card" style={{ padding: '36px 28px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '4rem', fontWeight: 800, letterSpacing: '-2px', color: '#1d1d1f', marginBottom: '12px', background: 'linear-gradient(135deg, #1d1d1f, #34c759)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              275%
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#1d1d1f', marginBottom: '12px' }}>
              Increase corridor safety compliance by
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#86868b', lineHeight: 1.5 }}>
              Guaranteed safety clearances at overlapping emergency intersections with zero collision risks and automated signal phase resets.
            </p>
          </div>
          <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid rgba(0,0,0,0.06)', display: 'flex', alignItems: 'center', gap: '8px', color: '#34c759', fontSize: '0.8rem', fontWeight: 600 }}>
            <ShieldCheck size={16} />
            <span>Conflict Resolution Protocol</span>
          </div>
        </div>
      </div>
    </section>
  );
}
