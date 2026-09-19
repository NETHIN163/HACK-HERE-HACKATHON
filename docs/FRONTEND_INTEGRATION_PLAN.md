# Q-FLOW Frontend Integration Plan & UI Architecture

## 1. Existing Frontend Architecture Analysis

### Current Workspace State
- **Backend Infrastructure**: Complete FastAPI Python application (`/backend`) providing REST APIs and WebSocket real-time event broadcasts (`ws://localhost:8000/ws`). Verified with 120 passing unit/integration tests.
- **Frontend Filesystem Inspection**:
  - The repository currently contains a legacy HTML template (`/Clinic-1.0.0`) with static HTML files (`index.html`, `about.html`, etc.), Bootstrap 5, FontAwesome, and static JS vendor scripts.
  - **No React application or `package.json` setup exists in the codebase yet.**
- **Target Frontend Technology Stack**:
  - **Framework**: React 18+ (powered by Vite SPA scaffolding).
  - **Logic & Structure**: Modern JavaScript/JSX with React Hooks.
  - **Styling Strategy**: Custom Vanilla CSS with Design System CSS Variables.
  - **Design System Aesthetics**: Glassmorphic dark mode palette, vibrant HSL color accents, smooth gradients, modern typography (Google Fonts: Inter / Outfit), and subtle micro-animations.
  - **Dependencies Strategy**: Standard React dependencies (`lucide-react` icons, lightweight SVG graph layout). No unnecessary external state libraries (e.g. Redux/Zustand) — React Context + `useReducer` will be used for state management.

---

## 2. Backend API Mapping

The following table maps every REST API endpoint from **Backend Developer 1** and **Backend Developer 2** to its purpose, target frontend component, request/response payload schemas, and required UI state:

| Category | HTTP Method | Endpoint Route | Purpose | Target Component / View | Request Data | Response Data | Required UI State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Traffic** | `GET` | `/api/traffic` | Fetch complete network state (roads & junctions) | `NetworkGraph`, `TrafficDashboard` | None | `{ timestamp, roads, junctions }` | `trafficState`, `isLoading` |
| | `GET` | `/api/traffic/junctions` | List all network junctions | `JunctionMonitor` | None | `List[Junction]` | `junctionsList` |
| | `GET` | `/api/traffic/roads` | List all network roads | `RoadMonitor` | None | `List[Road]` | `roadsList` |
| | `GET` | `/api/junctions/{junction_id}` | Fetch single junction state | `JunctionDetailModal` | `junction_id` | `Junction` | `selectedJunction` |
| | `GET` | `/api/roads/{road_id}` | Fetch single road state | `RoadDetailModal` | `road_id` | `Road` | `selectedRoad` |
| **Metrics** | `GET` | `/api/metrics` | Retrieve live metrics (wait time, queues, throughput, fuel, CO₂, pedestrian delay) | `MetricsBar`, `AnalyticsView` | None | `TrafficMetrics` | `metricsData` |
| **Incidents** | `GET` | `/api/incidents` | List active & historical incidents | `IncidentList`, `TrafficDashboard` | `active_only` (query param) | `List[Incident]` | `incidentsList` |
| | `POST` | `/api/incidents` | Create custom incident (Accident / Closure) | `IncidentControlPanel` | `{ type, road_id, severity, description }` | `Incident` | `activeIncidents` |
| | `PATCH` | `/api/incidents/{incident_id}` | Resolve or update incident state | `IncidentControlPanel` | `{ active, severity, description }` | `Incident` | `activeIncidents` |
| **Scenarios**| `POST` | `/api/scenarios/traffic-surge` | Trigger traffic surge scenario | `ScenarioControlPanel` | `{ surge_roads, surge_factor }` | `TrafficState` | `trafficState`, `scenarioActive` |
| | `POST` | `/api/scenarios/accident` | Trigger accident scenario | `ScenarioControlPanel` | `{ road_id, description }` | `Incident` | `incidentsList`, `roadStatus` |
| | `POST` | `/api/scenarios/road-closure` | Trigger road closure scenario | `ScenarioControlPanel` | `{ road_id, description }` | `Incident` | `incidentsList`, `roadStatus` |
| **Optimization**| `GET` | `/api/optimization/classical` | Retrieve classical signal timing optimization | `SignalOptimizerCard` | None | `Dict[str, SignalConfiguration]` | `classicalSignals` |
| **Emergency Requests** | `POST` | `/api/emergency/requests` | Create emergency dispatch request | `EmergencyDispatchModal` | `{ origin, destination, priority }` | `EmergencyRequest` | `emergencyRequests` |
| | `GET` | `/api/emergency/requests` | List all emergency requests | `EmergencyList` | None | `List[EmergencyRequest]` | `emergencyRequests` |
| | `GET` | `/api/emergency/requests/{request_id}` | Get single request details | `EmergencyDetailView` | `request_id` | `EmergencyRequest` | `selectedRequest` |
| **Ambulances** | `GET` | `/api/emergency/ambulances` | List ambulance fleet status & location | `AmbulanceFleetPanel` | None | `List[EmergencyVehicle]` | `ambulancesList` |
| | `POST` | `/api/emergency/ambulances` | Register ambulance or update location | `AmbulanceFleetPanel` | `{ vehicle_id, current_location }` | `EmergencyVehicle` | `ambulancesList` |
| | `GET` | `/api/emergency/ambulances/{vehicle_id}` | Get single ambulance details | `AmbulanceDetailModal` | `vehicle_id` | `EmergencyVehicle` | `selectedAmbulance` |
| **Assignments** | `POST` | `/api/emergency/assignments` | Assign available ambulance to request | `EmergencyDispatchModal` | `{ request_id, vehicle_id }` | `EmergencyAssignment` | `activeAssignments` |
| | `GET` | `/api/emergency/assignments/{assignment_id}` | Get assignment details | `EmergencyDetailView` | `assignment_id` | `EmergencyAssignment` | `selectedAssignment` |
| | `POST` | `/api/emergency/assignments/{assignment_id}/release` | Release assignment & ambulance | `EmergencyOperationsView` | `{ vehicle_id, new_location }` | `{ status }` | `activeAssignments`, `ambulancesList` |
| **Emergency Routing** | `POST` | `/api/emergency/routes` | Calculate route avoiding blocked roads | `EmergencyRouteCard` | `{ origin, destination }` | `EmergencyRoute` | `activeRoute` |
| **QUBO / QAOA** | `POST` | `/api/emergency/optimize` | Run QAOA quantum route optimization | `QuantumOptimizationPanel` | `{ candidate_routes, penalty_weight }` | `QAOAResult` | `qaoaResult`, `isOptimizing` |
| **Green Corridor** | `POST` | `/api/emergency/corridors/plan` | Plan Green Corridor for assignment | `GreenCorridorPanel` | `{ assignment_id }` | `GreenCorridorPlan` | `corridorPlans` |
| | `POST` | `/api/emergency/corridors/{request_id}/activate` | Activate Green Corridor signal priority | `GreenCorridorPanel` | `request_id` | `GreenCorridorPlan` | `activeCorridors` |
| | `POST` | `/api/emergency/corridors/{request_id}/release` | Release Green Corridor signal priority | `GreenCorridorPanel` | `request_id` | `GreenCorridorPlan` | `activeCorridors` |
| | `GET` | `/api/emergency/corridors/active` | Get active Green Corridor plans | `GreenCorridorPanel` | None | `List[GreenCorridorPlan]` | `activeCorridors` |
| **Conflict Resolution**| `POST` | `/api/emergency/conflicts/resolve` | Detect & resolve emergency priority conflicts | `ConflictResolutionModal` | `{ assignment_ids }` | `EmergencyConflictResult` | `activeConflicts` |

---

## 3. WebSocket Event Mapping

The frontend connects to `ws://localhost:8000/ws` and listens to the unified JSON event envelope:

```json
{
  "event_type": "string",
  "channel": "string",
  "payload": {},
  "timestamp": 123456789.0
}
```

### Event Dispatcher Mapping Table

| Backend Event | Triggering Action | Affected UI State | Target Component | Frontend UI Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `traffic.updated` | Simulation tick / Surge | `trafficState` | `NetworkGraph`, `MetricsBar` | Smoothly updates road densities, travel times, queue lengths |
| `signal.updated` | Signal timing change | `junctionSignals` | `NetworkGraph`, `JunctionMonitor` | Animates traffic signal phase indicators (RED / GREEN / YELLOW) |
| `incident.created` | Accident or Road Closure | `incidentsList`, `roads` | `NetworkGraph`, `IncidentPanel` | Highlights road as BLOCKED/CLOSED (red pulsing overlay), displays alert toast |
| `incident.updated` | Incident resolved | `incidentsList`, `roads` | `NetworkGraph`, `IncidentPanel` | Restores road status to OPEN (green outline), updates incident list |
| `pedestrian.updated` | Pedestrian crossing active | `pedestrianLocks` | `NetworkGraph`, `SignalMonitor` | Shows pedestrian clearance countdown timer lock on junction |
| `emergency.created` | New emergency request | `emergencyRequests` | `EmergencyOperationsView` | Plays notification pulse, adds request to emergency queue |
| `emergency.updated` | Status/priority change | `emergencyRequests` | `EmergencyOperationsView` | Updates request status tag and priority badge |
| `ambulance.registered` | New vehicle registered | `ambulancesList` | `AmbulanceFleetPanel` | Updates ambulance fleet list and map location badge |
| `ambulance.assigned` | Vehicle assigned | `ambulancesList`, `assignments` | `NetworkGraph`, `EmergencyPanel` | Animates ambulance icon onto assigned route origin |
| `ambulance.released` | Dispatch completed | `ambulancesList`, `assignments` | `NetworkGraph`, `EmergencyPanel` | Returns ambulance icon to available fleet pool |
| `emergency.route.updated` | Route calculated | `activeRoute` | `NetworkGraph`, `RouteCard` | Renders cyan emergency path overlay on network map |
| `green_corridor.planned` | Corridor plan created | `corridorPlans` | `GreenCorridorPanel` | Displays ordered junction priority sequence |
| `green_corridor.activated` | Signal priority active | `activeCorridors` | `NetworkGraph`, `CorridorBadge` | Illuminates Green Corridor glowing path and priority badges |
| `green_corridor.released` | Priority released | `activeCorridors` | `NetworkGraph`, `CorridorBadge` | Deactivates glowing corridor overlay, restores normal signals |
| `emergency.conflict.detected`| Overlapping route priority | `activeConflicts` | `ConflictResolutionModal` | Displays amber conflict warning banner with overlapping junctions |
| `emergency.conflict.resolved`| Policy applied | `activeConflicts` | `ConflictResolutionModal` | Shows granted winner request and deferred request status badges |

---

## 4. Proposed UI Architecture

```
frontend/
├── index.html
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── index.css                     # Design Tokens, Glassmorphism, Theme Variables
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.jsx            # System Status, WS Indicator, Active Mode
│   │   │   ├── Sidebar.jsx           # Mode Navigation (Traffic, Emergency, Analytics)
│   │   │   └── ToastContainer.jsx    # Real-time WebSocket Alert Notifications
│   │   ├── network/
│   │   │   ├── NetworkGraph.jsx      # Interactive SVG Node-Link Network Visualization
│   │   │   ├── JunctionNode.jsx     # Junction Node SVG component with Signal Status
│   │   │   ├── RoadEdge.jsx          # Dynamic Road Edge SVG with Congestion/Corridor Colors
│   │   │   └── VehicleMarker.jsx     # Animated Ambulance Vehicle SVG Marker
│   │   ├── traffic/
│   │   │   ├── TrafficDashboard.jsx  # Main Traffic Operations Center
│   │   │   ├── ScenarioControls.jsx  # Traffic Surge, Accident & Closure Trigger Controls
│   │   │   ├── IncidentList.jsx      # Active Incidents Table & Resolution Buttons
│   │   │   └── MetricsBar.jsx        # Top-level Live KPI Counter Cards
│   │   ├── emergency/
│   │   │   ├── EmergencyOperations.jsx# Main Emergency Dispatch & Operations Center
│   │   │   ├── EmergencyList.jsx     # Active Emergency Requests Queue & Dispatch Buttons
│   │   │   ├── AmbulanceFleet.jsx    # Ambulance Status Cards & Availability Toggles
│   │   │   ├── QaoaOptimizer.jsx     # QUBO/QAOA Quantum Optimization View & Solution Card
│   │   │   ├── GreenCorridor.jsx     # Green Corridor Lifecycle (Plan/Activate/Release)
│   │   │   └── ConflictResolver.jsx  # Conflict Resolution Modal & Priority Hierarchy
│   │   └── analytics/
│   │       ├── MetricsDashboard.jsx  # Detailed Analytics (Wait time, CO2, Fuel, Throughput)
│   │       └── MetricCard.jsx        # Animated Gauge & Metric Counter Component
│   ├── context/
│   │   ├── AppContext.jsx            # Central React Context Store
│   │   └── WebSocketContext.jsx      # WebSocket Live Connection & Event Provider
│   ├── services/
│   │   ├── api.js                    # Axios / Fetch REST API Client Wrapper
│   │   └── websocket.js              # WebSocket Client Manager with Reconnect Logic
│   └── utils/
│       ├── constants.js              # Junction Coordinates, Road Definitions, Colors
│       └── formatters.js             # Travel time, Queue length, Metric formatters
```

### Network Visualization Specification
- **Representation**: An interactive SVG Node-Link Graph mapping NetworkX junctions (`J1`-`J6`) onto fixed canvas coordinates with directed road edges (`R_J1_J2`, `R_J1_J4`, etc.).
- **Visual Encodings**:
  - `OPEN` Road: Sleek Cyan/Blue edge line.
  - `CONGESTED` Road: Orange line with pulse animation.
  - `BLOCKED` / `CLOSED` Road: Glowing Red dashed line with hazard icons.
  - `Green Corridor`: Glowing Emerald Green highlighted path with directional pulse arrows.
  - `Ambulance`: Pulsing Red/White emergency vehicle badge sliding along nodes.

---

## 5. State Management Strategy

To maintain high performance and simplicity without unnecessary external dependencies:

1. **Global App State (`AppContext.jsx`)**:
   - `activeTab`: Currently selected view (`TRAFFIC`, `EMERGENCY`, `ANALYTICS`).
   - `notifications`: List of live alert toasts.

2. **Server & Live WebSocket State (`WebSocketContext.jsx`)**:
   - `trafficState`: Live snapshot of roads and junctions.
   - `incidents`: Map of active incidents.
   - `emergencyRequests`: Map of emergency dispatch requests.
   - `ambulances`: Map of ambulance vehicle states.
   - `activeCorridors`: List of active Green Corridor plans.
   - `activeConflicts`: Current conflict resolution object.
   - `metrics`: Latest calculated metrics (`TrafficMetrics`).

3. **Component Local State (`useState`)**:
   - Form state for emergency request creation.
   - Modal visibility (`isDispatchOpen`, `isConflictModalOpen`).
   - Hovered node/road tooltips.

---

## 6. Error & Loading State Strategy

- **API Failure / Network Disconnection**:
  - Top header displays a clear **"WebSocket Disconnected — Retrying..."** status badge.
  - Exponential backoff reconnect strategy (1s, 2s, 5s, max 10s).
- **Loading States**:
  - Skeleton cards during initial REST API fetches.
  - Button spinner during QAOA optimization execution (`Optimizing Route via QAOA...`).
- **Domain Validation Error Handling**:
  - **No Ambulance Available**: Banner notification — *"No eligible ambulance found in fleet."*
  - **All Routes Blocked**: Alert — *"Destination Unroutable — All path combinations BLOCKED."*
  - **Pedestrian Clearance Lock**: Warning tag — *"Priority Deferred — Pedestrian clearance active (Xs remaining)."*
  - **Emergency Conflict**: Toast banner — *"Conflict Detected — Priority granted to higher-urgency request."*

---

## 7. Demo Workflow Design (Golden Demo Flow)

The UI will feature an explicit **Demo Control Bar** for one-click hackathon demonstration of the complete 17-step pipeline:

```
[1. Baseline Traffic] ──> [2. Trigger Surge] ──> [3. Simulate Accident] ──> [4. Request Emergency]
                                                                                   │
                                                                                   ▼
[8. Release Corridor] <── [7. Activate Corridor] <── [6. QAOA Optimize] <── [5. Dispatch Ambulance]
         │
         ▼
[9. Verify Reset & Metrics]
```

Each step visually illuminates the affected panel and updates the central Network Graph in real time.

---

## 8. Frontend Integration Risks & Mitigation

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Port Configuration & CORS** | API requests blocked during development | Configure Vite proxy in `vite.config.js` (`/api` & `/ws` target `http://localhost:8000`) |
| **WebSocket Reconnection Gaps** | UI state gets stale during brief disconnects | Perform full state REST fetch (`GET /api/traffic`, `/api/emergency/requests`) upon reconnect |
| **Async State Race Conditions** | Rapid WS events overwrite pending user input | Separate local form draft state from global WS live state stores |
| **Network Node Layout Placement** | Overlapping SVG nodes or unreadable edges | Use fixed, well-spaced canvas coordinates for `J1`-`J6` based on network layout |
| **Uncaptured Backend Errors** | Silent UI freeze on backend 400/500 | Wrap API calls in `try/catch` and display structured `detail` error toasts |

---

## 9. Implementation Order

- **Phase 1 (Current)**: Frontend Integration Analysis & UI Architecture (Documented in `docs/FRONTEND_INTEGRATION_PLAN.md`).
- **Phase 2**: Frontend Project Scaffolding & Core Design System (Vite setup, CSS tokens, Layout, Header, Navigation).
- **Phase 3**: API Client & Real-time WebSocket Service Layer (`api.js`, `websocket.js`, Context Providers).
- **Phase 4**: Interactive Network Graph Component (`NetworkGraph`, SVG Roads, Junction Nodes, Signal Status).
- **Phase 5**: Traffic Control & Scenario Components (Traffic Surge, Incident Creation, Incident List, Metrics Bar).
- **Phase 6**: Emergency Operations & Dispatch Components (Request Modal, Ambulance Fleet, QAOA Optimization Card, Green Corridor Panel, Conflict Modal).
- **Phase 7**: End-to-End Golden Demo Integration & Verification (Demo Control Bar, Full Workflow Test).

---

## 10. Exact Next Phase

The exact next phase to execute is **Phase 2 — Frontend Project Scaffolding & Core Design System Setup**.
