/**
 * Q-FLOW System Constants & Configuration
 */

export const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://localhost:8000';
export const WS_URL = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_WS_URL) || 'ws://localhost:8000/ws';

export const EVENT_TYPES = {
  TRAFFIC_UPDATED: 'traffic.updated',
  SIGNAL_UPDATED: 'signal.updated',
  INCIDENT_CREATED: 'incident.created',
  INCIDENT_UPDATED: 'incident.updated',
  PEDESTRIAN_UPDATED: 'pedestrian.updated',
  EMERGENCY_CREATED: 'emergency.created',
  EMERGENCY_UPDATED: 'emergency.updated',
  AMBULANCE_REGISTERED: 'ambulance.registered',
  AMBULANCE_ASSIGNED: 'ambulance.assigned',
  AMBULANCE_RELEASED: 'ambulance.released',
  EMERGENCY_ROUTE_UPDATED: 'emergency.route.updated',
  GREEN_CORRIDOR_PLANNED: 'green_corridor.planned',
  GREEN_CORRIDOR_ACTIVATED: 'green_corridor.activated',
  GREEN_CORRIDOR_RELEASED: 'green_corridor.released',
  EMERGENCY_CONFLICT_DETECTED: 'emergency.conflict.detected',
  EMERGENCY_CONFLICT_RESOLVED: 'emergency.conflict.resolved',
};

export const JUNCTION_COORDINATES = {
  J1: { x: 150, y: 150, name: 'North West Hub' },
  J2: { x: 450, y: 150, name: 'North East Station' },
  J3: { x: 750, y: 150, name: 'Hospital District' },
  J4: { x: 150, y: 450, name: 'South West Plaza' },
  J5: { x: 450, y: 450, name: 'Central Intersection' },
  J6: { x: 750, y: 450, name: 'South East Gate' },
};

export const INITIAL_METRICS = {
  average_wait_time: 0,
  queue_length: 0,
  throughput: 0,
  fuel_consumption: 0,
  co2_emissions: 0,
  pedestrian_delay: 0,
};
