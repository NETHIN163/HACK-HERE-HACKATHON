import React from 'react';
import { Activity, Clock3, MapPin, Route, Siren, Truck } from 'lucide-react';

export default function AmbulanceTracking({ vehicleTracker, activeCorridor, onDispatch }) {
  const tracker = vehicleTracker || { active: false, vehicleId: 'AMB-01', status: 'STANDBY', speedKmh: 0, etaSeconds: 0, distanceKm: 0, totalDistanceKm: 4.8, progressPercent: 0, route: ['J1', 'J2', 'J3'] };
  return (
    <section className="ambulance-page">
      <div className="page-heading-row">
        <div>
          <span className="eyebrow-label"><Siren size={13} /> EMERGENCY MOBILITY</span>
          <h2>Ambulance command</h2>
          <p>Follow the assigned vehicle, route progress, ETA and protected green corridor.</p>
        </div>
        <div className="map-location-chip"><MapPin size={15} /> Saravanampatti / Coimbatore</div>
      </div>
      <div className="ambulance-layout">
        <div className="ambulance-hero-panel">
          <div className="ambulance-hero-top"><div className="ambulance-title"><Truck size={22} /><div><strong>{tracker.vehicleId}</strong><span>{tracker.status}</span></div></div><span className={tracker.active ? 'live-pill' : 'idle-pill'}>{tracker.active ? 'LIVE TRACKING' : 'STANDBY'}</span></div>
          <div className="route-track">
            {tracker.route.map((node, index) => <div className="route-node" key={`${node}-${index}`}><span className={index <= tracker.currentStepIndex ? 'route-node-dot active' : 'route-node-dot'}>{node}</span><small>{index === tracker.currentStepIndex ? 'Current' : index < tracker.currentStepIndex ? 'Cleared' : 'Pending'}</small></div>)}
          </div>
          <div className="route-progress"><span style={{ width: `${tracker.progressPercent}%` }} /></div>
          <div className="ambulance-metrics"><div><Activity size={16} /><strong>{tracker.speedKmh} km/h</strong><span>Current speed</span></div><div><Clock3 size={16} /><strong>{tracker.etaSeconds}s</strong><span>ETA</span></div><div><Route size={16} /><strong>{tracker.distanceKm}/{tracker.totalDistanceKm} km</strong><span>Route progress</span></div></div>
        </div>
        <div className="ambulance-side-panel">
          <div className="side-panel-label">CORRIDOR STATUS</div>
          <strong>{activeCorridor ? activeCorridor.status : 'No active corridor'}</strong>
          <p>{activeCorridor ? `Protected path: ${activeCorridor.path.join(' → ')}` : 'Dispatch an ambulance to reserve signals along the safest route.'}</p>
          <button className="camera-action camera-action-primary" onClick={onDispatch}><Siren size={17} /> {tracker.active ? 'Dispatch another scenario' : 'Start ambulance demo'}</button>
        </div>
      </div>
    </section>
  );
}
