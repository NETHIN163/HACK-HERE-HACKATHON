import React from 'react';
import { Cpu, ShieldCheck, Award } from 'lucide-react';

export default function Footer() {
  return (
    <footer
      style={{
        backgroundColor: '#07050e',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        padding: '60px 32px 32px',
        color: '#94a3b8',
        fontSize: '0.85rem',
      }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1.5fr', gap: '40px', marginBottom: '48px' }}>
          {/* Brand col */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'linear-gradient(135deg, #8b5cf6, #06b6d4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Cpu size={18} color="#ffffff" />
              </div>
              <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#ffffff' }}>Q-FLOW</span>
            </div>
            <p style={{ color: '#64748b', lineHeight: 1.6, maxWidth: '280px' }}>
              Quantum-Assisted Smart Traffic Signal Optimization & Emergency Green Corridor Network.
            </p>
          </div>

          {/* Col 2 */}
          <div>
            <h4 style={{ color: '#f8fafc', fontWeight: 700, marginBottom: '14px', fontSize: '0.9rem' }}>Product</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <a href="#how-it-works" style={{ color: '#94a3b8', textDecoration: 'none' }}>QUBO Signal Solver</a>
              <a href="#how-it-works" style={{ color: '#94a3b8', textDecoration: 'none' }}>Green Corridor Lock</a>
              <a href="#architecture" style={{ color: '#94a3b8', textDecoration: 'none' }}>Incident Rerouting</a>
              <a href="#calculator" style={{ color: '#94a3b8', textDecoration: 'none' }}>ROI Calculator</a>
            </div>
          </div>

          {/* Col 3 */}
          <div>
            <h4 style={{ color: '#f8fafc', fontWeight: 700, marginBottom: '14px', fontSize: '0.9rem' }}>Use Cases</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <a href="#impact" style={{ color: '#94a3b8', textDecoration: 'none' }}>Emergency Ambulances</a>
              <a href="#impact" style={{ color: '#94a3b8', textDecoration: 'none' }}>Metropolitan Transit</a>
              <a href="#impact" style={{ color: '#94a3b8', textDecoration: 'none' }}>Incident Clearances</a>
              <a href="#impact" style={{ color: '#94a3b8', textDecoration: 'none' }}>Emissions Reduction</a>
            </div>
          </div>

          {/* Compliance & Standards */}
          <div>
            <h4 style={{ color: '#f8fafc', fontWeight: 700, marginBottom: '14px', fontSize: '0.9rem' }}>Standards & Security</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {[
                { label: 'Qiskit Quantum', color: '#a78bfa' },
                { label: 'PennyLane AI', color: '#67e8f9' },
                { label: 'SOC2 Type II', color: '#10b981' },
                { label: 'ISO 27001', color: '#3b82f6' },
                { label: 'IEEE Traffic Standard', color: '#f59e0b' },
              ].map((badge, i) => (
                <div key={i} style={{ padding: '6px 12px', borderRadius: '6px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', fontSize: '0.75rem', fontWeight: 600, color: badge.color, display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <ShieldCheck size={12} />
                  <span>{badge.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#64748b', fontSize: '0.8rem' }}>
          <div>© 2026 Q-Flow Technologies Inc. All Rights Reserved. Hackathon Edition.</div>
          <div style={{ display: 'flex', gap: '20px' }}>
            <a href="#privacy" style={{ color: '#64748b', textDecoration: 'none' }}>Terms of Service</a>
            <a href="#privacy" style={{ color: '#64748b', textDecoration: 'none' }}>Privacy Policy</a>
            <a href="#privacy" style={{ color: '#64748b', textDecoration: 'none' }}>Security Policy</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
