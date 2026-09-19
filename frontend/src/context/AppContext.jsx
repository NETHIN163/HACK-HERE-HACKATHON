/**
 * Central State Store (React Context + Reducer) for Q-FLOW Frontend
 */

import React, { createContext, useContext, useReducer } from 'react';
import { EVENT_TYPES, INITIAL_METRICS } from '../utils/constants.js';

const AppStateContext = createContext(null);
const AppDispatchContext = createContext(null);

const initialState = {
  trafficState: null,
  junctions: [],
  roads: [],
  incidents: [],
  signals: {},
  metrics: INITIAL_METRICS,
  emergencyRequests: [],
  ambulances: [],
  activeAssignments: [],
  activeRoutes: {},
  activeCorridors: [],
  activeConflicts: null,
  wsStatus: 'DISCONNECTED',
  apiConnected: false,
  lastEvent: null,
  logs: [],
  error: null,
};

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_WS_STATUS':
      return { ...state, wsStatus: action.payload };

    case 'SET_API_CONNECTED':
      return { ...state, apiConnected: action.payload };

    case 'SET_TRAFFIC_STATE':
      return {
        ...state,
        trafficState: action.payload,
        junctions: action.payload.junctions || state.junctions,
        roads: action.payload.roads || state.roads,
      };

    case 'SET_JUNCTIONS':
      return { ...state, junctions: action.payload };

    case 'SET_ROADS':
      return { ...state, roads: action.payload };

    case 'SET_INCIDENTS':
      return { ...state, incidents: action.payload };

    case 'ADD_INCIDENT':
      return {
        ...state,
        incidents: [action.payload, ...state.incidents.filter((i) => i.id !== action.payload.id)],
      };

    case 'UPDATE_INCIDENT':
      return {
        ...state,
        incidents: state.incidents.map((inc) => (inc.id === action.payload.id ? action.payload : inc)),
      };

    case 'SET_METRICS':
      return { ...state, metrics: action.payload };

    case 'SET_EMERGENCY_REQUESTS':
      return { ...state, emergencyRequests: action.payload };

    case 'ADD_EMERGENCY_REQUEST':
      return {
        ...state,
        emergencyRequests: [action.payload, ...state.emergencyRequests.filter((r) => r.request_id !== action.payload.request_id)],
      };

    case 'SET_AMBULANCES':
      return { ...state, ambulances: action.payload };

    case 'UPDATE_AMBULANCE':
      return {
        ...state,
        ambulances: [action.payload, ...state.ambulances.filter((a) => a.vehicle_id !== action.payload.vehicle_id)],
      };

    case 'SET_ASSIGNMENTS':
      return { ...state, activeAssignments: action.payload };

    case 'ADD_ASSIGNMENT':
      return {
        ...state,
        activeAssignments: [action.payload, ...state.activeAssignments.filter((a) => a.assignment_id !== action.payload.assignment_id)],
      };

    case 'SET_ACTIVE_CORRIDORS':
      return { ...state, activeCorridors: action.payload };

    case 'SET_CONFLICTS':
      return { ...state, activeConflicts: action.payload };

    case 'SET_ERROR':
      return { ...state, error: action.payload };

    case 'ADD_LOG':
      return {
        ...state,
        logs: [
          { id: Date.now() + Math.random(), timestamp: new Date().toLocaleTimeString(), text: action.payload },
          ...state.logs.slice(0, 99),
        ],
      };

    case 'HANDLE_WS_EVENT': {
      const event = action.payload;
      const eventType = event.event_type;
      const payload = event.payload || {};

      let updatedState = { ...state, lastEvent: event };

      // Append log
      const logText = `[WS Event] ${eventType}: ${JSON.stringify(payload).substring(0, 80)}`;
      const newLogs = [
        { id: Date.now() + Math.random(), timestamp: new Date().toLocaleTimeString(), text: logText },
        ...state.logs.slice(0, 99),
      ];
      updatedState.logs = newLogs;

      // Event dispatch logic matching Backend Developer 1 & 2 events
      switch (eventType) {
        case EVENT_TYPES.TRAFFIC_UPDATED:
          if (payload.roads) updatedState.roads = payload.roads;
          if (payload.junctions) updatedState.junctions = payload.junctions;
          break;

        case EVENT_TYPES.SIGNAL_UPDATED:
          if (payload.junction_id && payload.configuration) {
            updatedState.signals = {
              ...state.signals,
              [payload.junction_id]: payload.configuration,
            };
          }
          break;

        case EVENT_TYPES.INCIDENT_CREATED:
          updatedState.incidents = [payload, ...state.incidents.filter((i) => i.id !== payload.id)];
          break;

        case EVENT_TYPES.INCIDENT_UPDATED:
          updatedState.incidents = state.incidents.map((i) => (i.id === payload.id ? payload : i));
          break;

        case EVENT_TYPES.EMERGENCY_CREATED:
        case EVENT_TYPES.EMERGENCY_UPDATED:
          if (payload.request_id) {
            updatedState.emergencyRequests = [
              payload,
              ...state.emergencyRequests.filter((r) => r.request_id !== payload.request_id),
            ];
          }
          break;

        case EVENT_TYPES.AMBULANCE_REGISTERED:
        case EVENT_TYPES.AMBULANCE_ASSIGNED:
        case EVENT_TYPES.AMBULANCE_RELEASED:
          if (payload.vehicle_id) {
            updatedState.ambulances = [
              payload,
              ...state.ambulances.filter((a) => a.vehicle_id !== payload.vehicle_id),
            ];
          }
          break;

        case EVENT_TYPES.GREEN_CORRIDOR_ACTIVATED:
        case EVENT_TYPES.GREEN_CORRIDOR_PLANNED:
          if (payload.request_id || payload.plan_id) {
            updatedState.activeCorridors = [
              payload,
              ...state.activeCorridors.filter((c) => (c.request_id || c.plan_id) !== (payload.request_id || payload.plan_id)),
            ];
          }
          break;

        case EVENT_TYPES.GREEN_CORRIDOR_RELEASED:
          if (payload.request_id) {
            updatedState.activeCorridors = state.activeCorridors.filter((c) => c.request_id !== payload.request_id);
          }
          break;

        case EVENT_TYPES.EMERGENCY_CONFLICT_DETECTED:
        case EVENT_TYPES.EMERGENCY_CONFLICT_RESOLVED:
          updatedState.activeConflicts = payload;
          break;

        default:
          break;
      }

      return updatedState;
    }

    default:
      return state;
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppStateContext.Provider value={state}>
      <AppDispatchContext.Provider value={dispatch}>
        {children}
      </AppDispatchContext.Provider>
    </AppStateContext.Provider>
  );
}

export function useAppState() {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within an AppProvider');
  }
  return context;
}

export function useAppDispatch() {
  const context = useContext(AppDispatchContext);
  if (!context) {
    throw new Error('useAppDispatch must be used within an AppProvider');
  }
  return context;
}
