/**
 * Centralized API Client Layer for Q-FLOW Backend
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
      const errorMessage = (data && data.detail) || response.statusText || 'API Request Failed';
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
// 1. Traffic Services (Backend 1)
// ==========================================
export const trafficService = {
  getTrafficState: () => request('/api/traffic'),
  getJunctions: () => request('/api/traffic/junctions'),
  getRoads: () => request('/api/traffic/roads'),
  getJunction: (junctionId) => request(`/api/junctions/${junctionId}`),
  getRoad: (roadId) => request(`/api/roads/${roadId}`),
};

// ==========================================
// 2. Metrics Services (Backend 1)
// ==========================================
export const metricsService = {
  getMetrics: () => request('/api/metrics'),
};

// ==========================================
// 3. Incident Services (Backend 1)
// ==========================================
export const incidentService = {
  getIncidents: (activeOnly = true) => request(`/api/incidents?active_only=${activeOnly}`),
  createIncident: (incidentData) =>
    request('/api/incidents', {
      method: 'POST',
      body: JSON.stringify(incidentData),
    }),
  updateIncident: (incidentId, updateData) =>
    request(`/api/incidents/${incidentId}`, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    }),
  triggerSurgeScenario: (surgeData = {}) =>
    request('/api/scenarios/traffic-surge', {
      method: 'POST',
      body: JSON.stringify(surgeData),
    }),
  triggerAccidentScenario: (accidentData = {}) =>
    request('/api/scenarios/accident', {
      method: 'POST',
      body: JSON.stringify(accidentData),
    }),
  triggerClosureScenario: (closureData = {}) =>
    request('/api/scenarios/road-closure', {
      method: 'POST',
      body: JSON.stringify(closureData),
    }),
};

// ==========================================
// 4. Optimization Services (Backend 1)
// ==========================================
export const optimizationService = {
  getClassicalOptimization: () => request('/api/optimization/classical'),
};

// ==========================================
// 5. Emergency Services (Backend 2)
// ==========================================
export const emergencyService = {
  createRequest: (requestData) =>
    request('/api/emergency/requests', {
      method: 'POST',
      body: JSON.stringify(requestData),
    }),
  getRequests: () => request('/api/emergency/requests'),
  getRequest: (requestId) => request(`/api/emergency/requests/${requestId}`),
};

// ==========================================
// 6. Ambulance Services (Backend 2)
// ==========================================
export const ambulanceService = {
  getAmbulances: () => request('/api/emergency/ambulances'),
  registerAmbulance: (ambulanceData) =>
    request('/api/emergency/ambulances', {
      method: 'POST',
      body: JSON.stringify(ambulanceData),
    }),
  getAmbulance: (vehicleId) => request(`/api/emergency/ambulances/${vehicleId}`),
  createAssignment: (assignmentData) =>
    request('/api/emergency/assignments', {
      method: 'POST',
      body: JSON.stringify(assignmentData),
    }),
  getAssignment: (assignmentId) => request(`/api/emergency/assignments/${assignmentId}`),
  releaseAssignment: (assignmentId, releaseData = {}) =>
    request(`/api/emergency/assignments/${assignmentId}/release`, {
      method: 'POST',
      body: JSON.stringify(releaseData),
    }),
};

// ==========================================
// 7. Route & QUBO/QAOA Services (Backend 2)
// ==========================================
export const routingService = {
  calculateRoute: (origin, destination) =>
    request('/api/emergency/routes', {
      method: 'POST',
      body: JSON.stringify({ origin, destination }),
    }),
  runQuantumOptimization: (payload) =>
    request('/api/emergency/optimize', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};

// ==========================================
// 8. Corridor Services (Backend 2)
// ==========================================
export const corridorService = {
  planCorridor: (payload) =>
    request('/api/emergency/corridors/plan', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  activateCorridor: (requestId) =>
    request(`/api/emergency/corridors/${requestId}/activate`, {
      method: 'POST',
    }),
  releaseCorridor: (requestId) =>
    request(`/api/emergency/corridors/${requestId}/release`, {
      method: 'POST',
    }),
  getActiveCorridors: () => request('/api/emergency/corridors/active'),
};

// ==========================================
// 9. Conflict Resolution Services (Backend 2)
// ==========================================
export const conflictService = {
  resolveConflicts: (assignmentIds) =>
    request('/api/emergency/conflicts/resolve', {
      method: 'POST',
      body: JSON.stringify({ assignment_ids: assignmentIds }),
    }),
};

export default {
  traffic: trafficService,
  metrics: metricsService,
  incidents: incidentService,
  optimization: optimizationService,
  emergency: emergencyService,
  ambulances: ambulanceService,
  routing: routingService,
  corridor: corridorService,
  conflict: conflictService,
};
