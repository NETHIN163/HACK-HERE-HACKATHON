import React from 'react';
import { Activity, Bell, Cpu, Search, SlidersHorizontal } from 'lucide-react';

export default function Navbar({ activeView, setActiveView }) {
  const navigateTo = (event, view, target) => {
    event.preventDefault();
    setActiveView(view);
    if (target) {
      window.setTimeout(() => document.getElementById(target)?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 0);
    }
  };

  return (
    <>
      <div className="telemetry-ribbon">
        <span><i className="status-dot" /> QISKIT AER ISING HAMILTONIAN: OPTIMAL PHASE STATE</span>
        <span className="ribbon-secondary">ZERO COLLISION CONFLICT RESOLUTION PROTOCOL</span>
        <span className="ribbon-secondary">-38% CO2 EMISSIONS &amp; FUEL IDLE WASTE REDUCTION</span>
        <strong>GRID STATUS: STABLE</strong>
      </div>
      <header className="editorial-nav">
        <button className="brand-lockup" onClick={() => setActiveView('landing')}>
          <span className="brand-mark"><Cpu size={17} /></span>
          <span>AETHER // QUANTUM MOBILITY</span>
          <small>QAOA CORE V4.2</small>
        </button>
        <nav className="editorial-links">
          <a href="#simulator" onClick={(event) => navigateTo(event, 'landing', 'simulator')}>Network Graph</a>
          <a href="#city-ops" onClick={(event) => navigateTo(event, 'ops')}>City Ops</a>
          <a href="#impact" onClick={(event) => navigateTo(event, 'landing', 'impact')}>Impact ROI</a>
        </nav>
        <div className="nav-actions">
          <label className="nav-search"><Search size={14} /><input aria-label="Search network" placeholder="Search intersection..." /></label>
          <button className="icon-button" title="System telemetry"><SlidersHorizontal size={16} /></button>
          <button className="icon-button alert-icon" title="Corridor alerts"><Bell size={16} /></button>
          <button className="deploy-button" onClick={() => setActiveView('ops')}><Activity size={14} /> Deploy Simulator</button>
        </div>
      </header>
    </>
  );
}
