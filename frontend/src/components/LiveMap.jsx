import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { CheckCircle2, MapPin, Navigation, Radio, Route, TrafficCone } from 'lucide-react';

const CENTER = [11.0805, 76.9565];
const JUNCTIONS = [
  { id: 'J1', name: 'Saravanampatti North', lat: 11.0915, lng: 76.9505 },
  { id: 'J2', name: 'Sathy Road Junction', lat: 11.085, lng: 76.962 },
  { id: 'J3', name: 'Kovilpalayam Link', lat: 11.094, lng: 76.978 },
  { id: 'J4', name: 'CHIL SEZ Gate', lat: 11.071, lng: 76.949 },
  { id: 'J5', name: 'Central Saravanampatti', lat: 11.075, lng: 76.963 },
  { id: 'J6', name: 'Keeranatham Bypass', lat: 11.067, lng: 76.976 },
];
const ROUTE = ['J1', 'J2', 'J3'];

function markerIcon(color, label) {
  return L.divIcon({
    className: 'qflow-map-marker',
    html: `<span style="--marker-color:${color}">${label}</span>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  });
}

export default function LiveMap({ activeCorridor, vehicleTracker }) {
  const mapElement = useRef(null);
  const mapRef = useRef(null);
  const layersRef = useRef(null);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (!mapElement.current || mapRef.current) return undefined;
    const map = L.map(mapElement.current, { zoomControl: false }).setView(CENTER, 14);
    L.control.zoom({ position: 'bottomright' }).addTo(map);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);
    layersRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;
    setMapReady(true);
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!mapReady || !layersRef.current) return;
    const layers = layersRef.current;
    layers.clearLayers();
    const byId = Object.fromEntries(JUNCTIONS.map((junction) => [junction.id, junction]));
    const route = vehicleTracker?.route?.length ? vehicleTracker.route : (activeCorridor?.path?.length ? activeCorridor.path : ROUTE);
    const currentIndex = vehicleTracker?.currentStepIndex || 0;
    const path = route
      .map((id) => byId[id])
      .filter(Boolean)
      .map((junction) => [junction.lat, junction.lng]);
    const clearedPath = path.slice(0, Math.min(currentIndex + 1, path.length));
    const pendingPath = path.slice(Math.max(currentIndex, 0));
    if (pendingPath.length > 1) L.polyline(pendingPath, { color: '#64748b', weight: 5, opacity: 0.55, dashArray: '8 10' }).addTo(layers);
    if (clearedPath.length > 1) L.polyline(clearedPath, { color: '#12b981', weight: 8, opacity: 0.92 }).addTo(layers);
    if (path.length > 1 && currentIndex === 0) L.polyline(path, { color: '#f59e0b', weight: 4, opacity: 0.75, dashArray: '8 8' }).addTo(layers);
    JUNCTIONS.forEach((junction) => {
      const routeIndex = route.indexOf(junction.id);
      const cleared = routeIndex >= 0 && routeIndex < currentIndex;
      const current = routeIndex === currentIndex;
      const corridorActive = activeCorridor?.path?.includes(junction.id);
      const color = cleared ? '#12b981' : current ? '#f59e0b' : corridorActive ? '#087ea4' : '#475569';
      const status = cleared ? 'Traffic cleared' : current ? 'Ambulance here / signal priority' : corridorActive ? 'Green corridor reserved' : 'Adaptive signal node';
      L.marker([junction.lat, junction.lng], { icon: markerIcon(color, junction.id) })
        .bindPopup(`<strong>${junction.name}</strong><br />${status}`)
        .addTo(layers);
    });
    const currentId = route[currentIndex] || route[0] || 'J1';
    const current = byId[currentId] || byId.J1;
    L.marker([current.lat + 0.001, current.lng], { icon: markerIcon('#f59e0b', 'A') })
      .bindPopup(`<strong>AMB-01</strong><br />${vehicleTracker?.status || 'STANDBY'}<br />Saravanampatti demo telemetry`)
      .addTo(layers);
  }, [activeCorridor, mapReady, vehicleTracker]);

  return (
    <section className="live-map-page">
      <div className="page-heading-row">
        <div>
          <span className="eyebrow-label"><Radio size={13} /> SARAVANAMPATTI / COIMBATORE</span>
          <h2>Live traffic map</h2>
          <p>Adaptive signal network, emergency route and simulated ambulance position.</p>
        </div>
        <div className="map-location-chip"><MapPin size={15} /> Local prototype coordinates</div>
      </div>
      <div className="map-shell">
        <div ref={mapElement} className="leaflet-map" aria-label="Saravanampatti traffic map" />
        <div className="map-legend">
          <span><i className="legend-dot legend-green" /> Cleared traffic</span>
          <span><i className="legend-dot legend-amber" /> Ambulance / current</span>
          <span><i className="legend-dot legend-blue" /> Reserved route</span>
        </div>
      </div>
      <div className="route-process-panel">
        <div className="route-process-title"><Route size={16} /> AMBULANCE ROUTE PROCESS</div>
        <div className="route-process-flow">
          {(vehicleTracker?.route?.length ? vehicleTracker.route : ROUTE).map((junctionId, index) => {
            const cleared = index < (vehicleTracker?.currentStepIndex || 0);
            const current = index === (vehicleTracker?.currentStepIndex || 0);
            return <div className={`route-process-step ${cleared ? 'is-cleared' : ''} ${current ? 'is-current' : ''}`} key={`${junctionId}-${index}`}>
              {cleared ? <CheckCircle2 size={15} /> : <TrafficCone size={15} />}
              <strong>{junctionId}</strong><span>{cleared ? 'Traffic cleared' : current ? 'Processing now' : 'Pending'}</span>
            </div>;
          })}
        </div>
      </div>
      <div className="map-stat-row">
        <div><Navigation size={16} /><strong>6</strong><span>connected junctions</span></div>
        <div><Radio size={16} /><strong>{vehicleTracker?.active ? 'LIVE' : 'READY'}</strong><span>vehicle telemetry</span></div>
        <div><CheckCircle2 size={16} /><strong>{Math.min(vehicleTracker?.currentStepIndex || 0, (vehicleTracker?.route?.length || 1) - 1)}</strong><span>junctions cleared</span></div>
      </div>
    </section>
  );
}
