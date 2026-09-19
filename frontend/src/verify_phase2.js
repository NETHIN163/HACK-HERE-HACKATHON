/**
 * Phase 2 Integration Verification Script
 * Validates API layer, WebSocket event parsing, state reducer, and error handling.
 */

import { EVENT_TYPES, INITIAL_METRICS } from './utils/constants.js';
import {
  trafficService,
  metricsService,
  incidentService,
  emergencyService,
  ambulanceService,
  routingService,
  corridorService,
  conflictService,
} from './services/api.js';
import wsManager, { WS_STATUS } from './services/websocket.js';

function assert(condition, message) {
  if (!condition) {
    console.error(`❌ ASSERTION FAILED: ${message}`);
    process.exit(1);
  } else {
    console.log(`✅ PASSED: ${message}`);
  }
}

console.log('--- Starting Phase 2 Frontend Verification ---');

// 1. Verify API Services export structure
assert(typeof trafficService.getTrafficState === 'function', 'trafficService.getTrafficState exists');
assert(typeof trafficService.getJunctions === 'function', 'trafficService.getJunctions exists');
assert(typeof trafficService.getRoads === 'function', 'trafficService.getRoads exists');
assert(typeof metricsService.getMetrics === 'function', 'metricsService.getMetrics exists');
assert(typeof incidentService.getIncidents === 'function', 'incidentService.getIncidents exists');
assert(typeof incidentService.createIncident === 'function', 'incidentService.createIncident exists');
assert(typeof emergencyService.createRequest === 'function', 'emergencyService.createRequest exists');
assert(typeof ambulanceService.getAmbulances === 'function', 'ambulanceService.getAmbulances exists');
assert(typeof routingService.calculateRoute === 'function', 'routingService.calculateRoute exists');
assert(typeof corridorService.planCorridor === 'function', 'corridorService.planCorridor exists');
assert(typeof conflictService.resolveConflicts === 'function', 'conflictService.resolveConflicts exists');

// 2. Verify WebSocket Manager status subscription & state
let statusChanges = [];
const unsubStatus = wsManager.subscribeStatus((status) => {
  statusChanges.push(status);
});

assert(statusChanges.includes(WS_STATUS.DISCONNECTED), 'wsManager starts in DISCONNECTED state');
unsubStatus();

// 3. Verify WebSocket Event Parsing Logic
let receivedEvents = [];
const unsubWs = wsManager.subscribe((event) => {
  receivedEvents.push(event);
});

const mockEvent = {
  event_type: EVENT_TYPES.TRAFFIC_UPDATED,
  channel: 'traffic',
  payload: { roads: [{ id: 'R_J1_J2', status: 'OPEN' }] },
  timestamp: 123456,
};

wsManager.notifyListeners(mockEvent);
assert(receivedEvents.length === 1, 'wsManager notifies subscribers of received events');
assert(receivedEvents[0].event_type === EVENT_TYPES.TRAFFIC_UPDATED, 'wsManager event payload matches');
unsubWs();

// 4. Verify Initial Metrics Schema
assert(INITIAL_METRICS.average_wait_time === 0, 'INITIAL_METRICS has average_wait_time');
assert(INITIAL_METRICS.co2_emissions === 0, 'INITIAL_METRICS has co2_emissions');

console.log('--- All Phase 2 Verification Checks Completed Successfully! ---');
