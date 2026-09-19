/**
 * Centralized API Client Layer for Q-FLOW Backend
 * Supports Teammate Backend endpoints (/api/emergencies, /api/ambulances, /api/hospitals, /api/optimization, /api/incidents)
 */

import { API_BASE_URL } from '../utils/constants.js';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const errorMessage = (data && (data.error || data.detail)) || response.statusText || 'API Request Failed';
      throw new ApiError(errorMessage, response.status, data);
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(error.message || 'Network request failed', 0, null);
  }
}

// ==========================================
// 1. Traffic & Network Services
// ==========================================
export const trafficService = {
  getTrafficState: () => request('/api/emergencies'),
  getJunctions: () => request('/api/emergencies'),
  getRoads: () => request('/api/emergencies'),
  healthCheck: () => request('/health'),
};

// ==========================================
// 2. Incident Services
// ==========================================
export const incidentService = {
  createIncident: (u, v) =>
    request('/api/incidents', {
      method: 'POST',
      body: JSON.stringify({ u, v }),
    }),
  getIncidents: () => request('/api/emergencies'),
};

// ==========================================
// 3. Optimization Services (Classical & QAOA Hybrid)
// ==========================================
export const metricsService = {
  getMetrics: () => request('/api/optimization/run'),
};

export const optimizationService = {
  runOptimization: (junctions = ['J1', 'J2', 'J3'], mode = 'HYBRID') =>
    request('/api/optimization/run', {
      method: 'POST',
      body: JSON.stringify({ junctions, mode }),
    }),
  getClassicalOptimization: (junctions = ['J1', 'J2', 'J3']) =>
    request('/api/optimization/classical', {
      method: 'POST',
      body: JSON.stringify({ junctions }),
    }),
  getHybridOptimization: (junctions = ['J1', 'J2', 'J3']) =>
    request('/api/optimization/hybrid', {
      method: 'POST',
      body: JSON.stringify({ junctions }),
    }),
  getOptimizationResult: (rid) => request(`/api/optimization/${rid}`),
};

// ==========================================
// 4. Emergency Services
// ==========================================
export const emergencyService = {
  createRequest: (type = 'TRAUMA', priority = 1, pickup = 'J1', destination = null) =>
    request('/api/emergencies', {
      method: 'POST',
      body: JSON.stringify({ type, priority, pickup, destination }),
    }),
  getRequests: () => request('/api/emergencies'),
  getRequest: (eid) => request(`/api/emergencies/${eid}`),
  patchRequest: (eid, fields) =>
    request(`/api/emergencies/${eid}`, {
      method: 'PATCH',
      body: JSON.stringify(fields),
    }),
  assignAmbulance: (eid) =>
    request(`/api/emergencies/${eid}/assign`, {
      method: 'POST',
    }),
  optimizeRoute: (eid) =>
    request(`/api/emergencies/${eid}/optimize-route`, {
      method: 'POST',
    }),
  rerouteEmergency: (eid) =>
    request(`/api/emergencies/${eid}/reroute`, {
      method: 'POST',
    }),
  getRoute: (eid) => request(`/api/emergencies/${eid}/route`),
  getCorridor: (eid) => request(`/api/emergencies/${eid}/corridor`),
};

// ==========================================
// 5. Ambulance Fleet Services
// ==========================================
export const ambulanceService = {
  getAmbulances: () => request('/api/ambulances'),
  getAmbulance: (aid) => request(`/api/ambulances/${aid}`),
  assignToEmergency: (aid, emergencyId) =>
    request(`/api/ambulances/${aid}/assign`, {
      method: 'POST',
      body: JSON.stringify({ emergency_id: emergencyId }),
    }),
};

// ==========================================
// 6. Hospital Services
// ==========================================
export const hospitalService = {
  getHospitals: () => request('/api/hospitals'),
  getHospital: (hid) => request(`/api/hospitals/${hid}`),
};

// ==========================================
// 7. Conflict Resolution Services
// ==========================================
export const conflictService = {
  resolveConflict: (junction, ambulanceA, ambulanceB) =>
    request('/api/conflicts/resolve', {
      method: 'POST',
      body: JSON.stringify({
        junction,
        ambulance_a: ambulanceA,
        ambulance_b: ambulanceB,
      }),
    }),
};

export const routingService = {
  calculateRoute: async (origin, destination) => {
    const emergency = await emergencyService.createRequest('TRAUMA', 1, origin, destination);
    const route = await emergencyService.getRoute(emergency.emergency_id);
    return { ...route, path: route.nodes || route.path || [] };
  },
};

export default {
  traffic: trafficService,
  incidents: incidentService,
  optimization: optimizationService,
  emergency: emergencyService,
  ambulances: ambulanceService,
  hospitals: hospitalService,
  conflict: conflictService,
};
