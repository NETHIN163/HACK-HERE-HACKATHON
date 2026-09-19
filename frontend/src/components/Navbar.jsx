import React from 'react';
import { Activity, Cpu, Sparkles } from 'lucide-react';

export default function Navbar({ activeView, setActiveView }) {
  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        backgroundColor: 'rgba(11, 8, 19, 0.75)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        padding: '16px 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      {/* Brand Logo */}
      <div
        style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
        onClick={() => setActiveView('landing')}
      >
        <div
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #8b5cf6, #06b6d4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 16px rgba(139, 92, 246, 0.5)',
          }}
        >
          <Cpu size={20} color="#ffffff" />
        </div>
        <div>
          <span
            style={{
              fontSize: '1.4rem',
              fontWeight: 800,
              letterSpacing: '-0.5px',
              color: '#ffffff',
            }}
          >
            Q-FLOW
          </span>
          <span
            style={{
              marginLeft: '6px',
              fontSize: '0.65rem',
              fontWeight: 700,
              padding: '2px 6px',
              borderRadius: '4px',
              background: 'rgba(6, 182, 212, 0.15)',
              color: '#67e8f9',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            Quantum AI
          </span>
        </div>
      </div>

      {/* Nav Links */}
      <nav style={{ display: 'flex', alignItems: 'center', gap: '28px' }}>
        <a
          href="#how-it-works"
          style={{ color: '#cbd5e1', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500, transition: 'color 0.2s' }}
          onMouseEnter={(e) => (e.target.style.color = '#ffffff')}
          onMouseLeave={(e) => (e.target.style.color = '#cbd5e1')}
        >
          How It Works
        </a>
        <a
          href="#impact"
          style={{ color: '#cbd5e1', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500, transition: 'color 0.2s' }}
          onMouseEnter={(e) => (e.target.style.color = '#ffffff')}
          onMouseLeave={(e) => (e.target.style.color = '#cbd5e1')}
        >
          Impact
        </a>
        <a
          href="#architecture"
          style={{ color: '#cbd5e1', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500, transition: 'color 0.2s' }}
          onMouseEnter={(e) => (e.target.style.color = '#ffffff')}
          onMouseLeave={(e) => (e.target.style.color = '#cbd5e1')}
        >
          Architecture
        </a>
        <a
          href="#calculator"
          style={{ color: '#cbd5e1', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500, transition: 'color 0.2s' }}
          onMouseEnter={(e) => (e.target.style.color = '#ffffff')}
          onMouseLeave={(e) => (e.target.style.color = '#cbd5e1')}
        >
          ROI Calculator
        </a>
        <a
          href="#faq"
          style={{ color: '#cbd5e1', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500, transition: 'color 0.2s' }}
          onMouseEnter={(e) => (e.target.style.color = '#ffffff')}
          onMouseLeave={(e) => (e.target.style.color = '#cbd5e1')}
        >
          FAQ
        </a>
      </nav>

      {/* Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* View Switcher Pill */}
        <div
          style={{
            display: 'inline-flex',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '9999px',
            padding: '3px',
            border: '1px solid rgba(255, 255, 255, 0.08)',
          }}
        >
          <button
            onClick={() => setActiveView('landing')}
            style={{
              padding: '6px 14px',
              borderRadius: '9999px',
              border: 'none',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: activeView === 'landing' ? 'rgba(139, 92, 246, 0.3)' : 'transparent',
              color: activeView === 'landing' ? '#ffffff' : '#94a3b8',
            }}
          >
            Product Overview
          </button>
          <button
            onClick={() => setActiveView('ops')}
            style={{
              padding: '6px 14px',
              borderRadius: '9999px',
              border: 'none',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: activeView === 'ops' ? 'linear-gradient(135deg, #06b6d4, #3b82f6)' : 'transparent',
              color: activeView === 'ops' ? '#ffffff' : '#94a3b8',
              boxShadow: activeView === 'ops' ? '0 0 12px rgba(6, 182, 212, 0.4)' : 'none',
            }}
          >
            <Activity size={13} />
            Live Ops Center
          </button>
        </div>

        <button className="btn-orchid-primary" onClick={() => setActiveView('ops')}>
          <Sparkles size={16} />
          <span>Launch Simulator</span>
        </button>
      </div>
    </header>
  );
}
