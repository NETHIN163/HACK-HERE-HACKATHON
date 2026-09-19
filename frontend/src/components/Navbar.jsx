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
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
        padding: '16px 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.03)',
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
            background: 'linear-gradient(135deg, #0071e3, #6e56cf)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px rgba(0, 113, 227, 0.3)',
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
              color: '#1d1d1f',
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
              background: 'rgba(0, 113, 227, 0.08)',
              color: '#0071e3',
              border: '1px solid rgba(0, 113, 227, 0.2)',
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
          style={{ color: '#515154', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500, transition: 'color 0.2s' }}
          onMouseEnter={(e) => (e.target.style.color = '#0071e3')}
          onMouseLeave={(e) => (e.target.style.color = '#515154')}
        >
          How It Works
        </a>
        <a
          href="#impact"
          style={{ color: '#515154', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500, transition: 'color 0.2s' }}
          onMouseEnter={(e) => (e.target.style.color = '#0071e3')}
          onMouseLeave={(e) => (e.target.style.color = '#515154')}
        >
          Impact
        </a>
        <a
          href="#architecture"
          style={{ color: '#515154', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500, transition: 'color 0.2s' }}
          onMouseEnter={(e) => (e.target.style.color = '#0071e3')}
          onMouseLeave={(e) => (e.target.style.color = '#515154')}
        >
          Architecture
        </a>
        <a
          href="#calculator"
          style={{ color: '#515154', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500, transition: 'color 0.2s' }}
          onMouseEnter={(e) => (e.target.style.color = '#0071e3')}
          onMouseLeave={(e) => (e.target.style.color = '#515154')}
        >
          ROI Calculator
        </a>
        <a
          href="#faq"
          style={{ color: '#515154', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500, transition: 'color 0.2s' }}
          onMouseEnter={(e) => (e.target.style.color = '#0071e3')}
          onMouseLeave={(e) => (e.target.style.color = '#515154')}
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
            background: 'rgba(0, 0, 0, 0.05)',
            borderRadius: '9999px',
            padding: '3px',
            border: '1px solid rgba(0, 0, 0, 0.08)',
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
              background: activeView === 'landing' ? 'rgba(0, 113, 227, 0.12)' : 'transparent',
              color: activeView === 'landing' ? '#0071e3' : '#86868b',
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
              background: activeView === 'ops' ? '#0071e3' : 'transparent',
              color: activeView === 'ops' ? '#ffffff' : '#86868b',
              boxShadow: activeView === 'ops' ? '0 2px 10px rgba(0, 113, 227, 0.3)' : 'none',
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
