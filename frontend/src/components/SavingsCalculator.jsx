import React, { useState } from 'react';
import { Calculator, DollarSign, Clock, Leaf, ArrowRight, Play } from 'lucide-react';

export default function SavingsCalculator({ onLaunchSimulator }) {
  const [population, setPopulation] = useState(500000); // 500k city
  const [emergencies, setEmergencies] = useState(40); // 40 calls/day
  const [intersections, setIntersections] = useState(50); // 50 signals

  // Derived savings formulas
  const annualEmergencyTimeSavedHours = Math.round(emergencies * 365 * (12 / 60)); // ~12 mins saved per dispatch
  const annualFuelSavedDollars = Math.round(intersections * 14200); // ~$14.2k per signal saved from idle queue reduction
  const annualCO2SavedTons = Math.round(intersections * 48); // ~48 tons per signal/year

  return (
    <section id="calculator" style={{ padding: '80px 32px', maxWidth: '1200px', margin: '0 auto', textAlign: 'center', position: 'relative' }}>
      {/* Horizontal glowing neon separator above */}
      <div className="neon-divider" />

      <div style={{ marginBottom: '40px' }}>
        <div className="glass-pill-cyan" style={{ marginBottom: '16px' }}>
          <Calculator size={14} />
          <span>Interactive City Impact Model</span>
        </div>
        <h2 style={{ fontSize: '2.6rem', fontWeight: 800, color: '#f8fafc', marginBottom: '16px' }}>
          What Can Q-Flow Do For Your City?
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '1.05rem', maxWidth: '650px', margin: '0 auto' }}>
          Adjust the sliders below to estimate your municipality’s annual emergency dispatch time saved, fuel reduction, and carbon offset.
        </p>
      </div>

      {/* Main Interactive Calculator Card */}
      <div className="glass-card-static" style={{ padding: '40px', borderRadius: '24px', border: '1px solid rgba(6, 182, 212, 0.3)', textAlign: 'left' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px', alignItems: 'center' }}>
          {/* Sliders Input Panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
            {/* Slider 1 */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 600 }}>
                <span style={{ color: '#cbd5e1' }}>City Population</span>
                <span style={{ color: '#67e8f9' }}>{population.toLocaleString()} Residents</span>
              </div>
              <input
                type="range"
                min="100000"
                max="2000000"
                step="50000"
                value={population}
                onChange={(e) => setPopulation(Number(e.target.value))}
                style={{ width: '100%', accentColor: '#06b6d4', cursor: 'pointer' }}
              />
            </div>

            {/* Slider 2 */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 600 }}>
                <span style={{ color: '#cbd5e1' }}>Daily Emergency Ambulance Calls</span>
                <span style={{ color: '#a78bfa' }}>{emergencies} Dispatch Calls / Day</span>
              </div>
              <input
                type="range"
                min="10"
                max="200"
                step="5"
                value={emergencies}
                onChange={(e) => setEmergencies(Number(e.target.value))}
                style={{ width: '100%', accentColor: '#8b5cf6', cursor: 'pointer' }}
              />
            </div>

            {/* Slider 3 */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 600 }}>
                <span style={{ color: '#cbd5e1' }}>Managed Traffic Intersections</span>
                <span style={{ color: '#10b981' }}>{intersections} Signals</span>
              </div>
              <input
                type="range"
                min="10"
                max="300"
                step="5"
                value={intersections}
                onChange={(e) => setIntersections(Number(e.target.value))}
                style={{ width: '100%', accentColor: '#10b981', cursor: 'pointer' }}
              />
            </div>
          </div>

          {/* Savings Output Cards Grid */}
          <div style={{ background: '#090712', borderRadius: '20px', padding: '28px', border: '1px solid rgba(255,255,255,0.08)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Estimated Annual Savings & Impact
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              {/* Box 1 */}
              <div style={{ background: 'rgba(139, 92, 246, 0.1)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(139, 92, 246, 0.25)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#a78bfa', fontSize: '0.8rem', marginBottom: '6px' }}>
                  <Clock size={16} />
                  <span>Dispatch Time Saved</span>
                </div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#ffffff' }}>
                  {annualEmergencyTimeSavedHours.toLocaleString()} <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#a78bfa' }}>Hours/yr</span>
                </div>
              </div>

              {/* Box 2 */}
              <div style={{ background: 'rgba(6, 182, 212, 0.1)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(6, 182, 212, 0.25)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#67e8f9', fontSize: '0.8rem', marginBottom: '6px' }}>
                  <DollarSign size={16} />
                  <span>Fuel Idle Cost Saved</span>
                </div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#ffffff' }}>
                  ${(annualFuelSavedDollars / 1000).toFixed(0)}k <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#67e8f9' }}>/year</span>
                </div>
              </div>

              {/* Box 3 */}
              <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.25)', gridColumn: 'span 2' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981', fontSize: '0.8rem', marginBottom: '6px' }}>
                  <Leaf size={16} />
                  <span>Carbon Emissions Offset</span>
                </div>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#ffffff' }}>
                  {annualCO2SavedTons.toLocaleString()} <span style={{ fontSize: '1rem', fontWeight: 600, color: '#10b981' }}>Metric Tons CO₂ / year</span>
                </div>
              </div>
            </div>

            <button className="btn-orchid-glow" style={{ width: '100%', justifyContent: 'center', display: 'flex', alignItems: 'center', gap: '8px' }} onClick={onLaunchSimulator}>
              <Play size={16} />
              <span>Launch Live Simulation with Model Parameters</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
