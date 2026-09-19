# Q-FLOW — Backend Developer 1 Handoff Document

## 1. Implementation Status
- **Overall Status**: **COMPLETE** (Backend Developer 1 Scope)
- **Test Suite**: **60 tests passed** (0 failures, 0 errors, 100% pass rate)
- **FastAPI Application**: Server startup verified on port 8000 (`uvicorn app.main:app`)
- **REST API Integration**: Verified (13 endpoints operational)
- **WebSocket System**: Verified (`ws://127.0.0.1:8000/ws/traffic`)

---

## 2. Implemented Components

1. **Urban Network Graph (`backend/app/simulation/network.py`)**:
   - NetworkX-based 6-junction (`J1` to `J6`) bi-directional 2x3 grid urban network.
   - Multi-path pathfinding (`find_all_paths`) and shortest path rerouting (`get_shortest_path`) respecting `BLOCKED` and `CLOSED` statuses.
2. **Pydantic Domain Models (`backend/app/models/`)**:
   - `Road`: `road_id`, `source`, `destination`, `distance`, `capacity`, `travel_time`, `traffic_density`, `queue_length`, `status` (`OPEN`, `CONGESTED`, `BLOCKED`, `CLOSED`).
   - `Junction`: `junction_id`, `signal_phase`, `green_duration`, `red_duration`, `queue_length`, `vehicle_density`, `pedestrian_count`, `emergency_reserved`, `crossing_active`, `crossing_remaining_seconds`.
   - `TrafficState`, `VehicleDemand`, `SignalConfiguration`, `SignalPhase`, `Incident`, `IncidentType`, `TrafficMetrics`, `DiversionImpact`.
3. **Deterministic Traffic Simulator (`backend/app/simulation/traffic_engine.py`)**:
   - Seeded deterministic time-step simulation engine (`TrafficEngine`).
   - Computes vehicle flow, density, queue length, BPR travel time, and cumulative waiting time per tick.
4. **Traffic Scenarios (`backend/app/simulation/scenarios.py`)**:
   - Scenario engine supporting `traffic-surge`, `accident`, and `road-closure`.
5. **Incident Lifecycle System (`backend/app/services/incident_service.py`)**:
   - Manages `ACCIDENT` (`BLOCKED`) and `ROAD_CLOSURE` (`CLOSED`) incidents.
   - Automatic road status updates, incident resolution, and WebSocket event triggers.
6. **Classical Optimizer Baseline (`backend/app/optimization/classical.py`)**:
   - Rule-based adaptive signal controller (`ClassicalOptimizer`) extending green durations based on queue thresholds (> 10 vehicles) and vehicle density (> 0.6).
7. **Signal Controller & Pedestrian Safety (`backend/app/simulation/signal_engine.py`)**:
   - Validates signal phase configurations, movement conflict matrices, emergency corridor reservations (`create_reservation` / `release_reservation`), and non-bypassable pedestrian clearance countdowns.
8. **Metrics Service (`backend/app/services/metrics_service.py`)**:
   - Unified metric calculator evaluating average wait time, average queue length, max queue length, throughput, emergency travel time & delay, fuel (L), CO2 (kg), and pedestrian delay.
9. **Diversion Impact Service (`backend/app/services/diversion_service.py`)**:
   - Downstream diversion impact predictor evaluating candidate alternative paths, predicted congestion/queues, affected junctions, and risk level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
10. **FastAPI REST API Layer (`backend/app/api/`)**:
    - Routers for traffic, junctions, roads, incidents, scenarios, metrics, and classical optimization.
11. **WebSocket Real-Time Event Engine (`backend/app/websocket/events.py`)**:
    - WebSocket endpoint `/ws/traffic` broadcasting standardized `SystemEvent` payloads.

---

## 3. REST API Contract

| Endpoint Path | Method | Description | Request Body | Response Model |
|---|---|---|---|---|
| `GET /api/traffic` | GET | Returns overall network traffic state snapshot | None | `TrafficState` |
| `GET /api/traffic/junctions` | GET | Returns traffic state for all junctions | None | `List[Junction]` |
| `GET /api/traffic/roads` | GET | Returns traffic state for all roads | None | `List[Road]` |
| `GET /api/junctions/{junction_id}` | GET | Returns single junction state (or 404) | None | `Junction` |
| `GET /api/roads/{road_id}` | GET | Returns single road state (or 404) | None | `Road` |
| `GET /api/incidents` | GET | Returns active or historical incidents | Query `active_only: bool` | `List[Incident]` |
| `POST /api/incidents` | POST | Creates new incident (`ACCIDENT`/`ROAD_CLOSURE`) | `CreateIncidentRequest` | `Incident` (`201`) |
| `PATCH /api/incidents/{incident_id}` | PATCH | Updates/resolves incident | `UpdateIncidentRequest` | `Incident` (`200`) |
| `POST /api/scenarios/traffic-surge` | POST | Triggers traffic surge scenario | `TrafficSurgeRequest` | `TrafficState` |
| `POST /api/scenarios/accident` | POST | Triggers accident scenario | `ScenarioAccidentRequest` | `Incident` (`201`) |
| `POST /api/scenarios/road-closure` | POST | Triggers road closure scenario | `ScenarioRoadClosureRequest` | `Incident` (`201`) |
| `GET /api/metrics` | GET | Returns traffic & environmental performance metrics | None | `TrafficMetrics` |
| `GET /api/optimization/classical` | GET | Runs ClassicalOptimizer and returns signal configs | None | `Dict[str, SignalConfiguration]` |

---

## 4. WebSocket Event Contract

**Endpoint URL**: `ws://127.0.0.1:8000/ws/traffic`

### Event Schema
```json
{
  "event": "<event_type_string>",
  "entity": "<target_resource_id>",
  "data": { ... },
  "timestamp": 1789813907.809
}
```

### Event Catalog
1. `traffic.updated`: Broadcast on simulation ticks or network traffic state updates.
2. `signal.updated`: Broadcast when a junction's signal phase or green/red duration changes.
3. `incident.created`: Broadcast when a new accident or road closure occurs.
4. `incident.updated`: Broadcast when an incident severity changes or incident is resolved.
5. `pedestrian.updated`: Broadcast when pedestrian counts or crossing clearance countdowns change.
6. `route.impact_required`: Broadcast when a road status changes to `BLOCKED` or `CLOSED`.

---

## 5. Backend Developer 2 Integration Contract

Backend Developer 2 can import and consume the following services and data structures from `backend/app/`:

1. **Network Graph (`TrafficNetwork`)**:
   - Import: `from app.simulation.network import TrafficNetwork`
   - Access: `network.graph` (NetworkX `DiGraph`), `network.get_shortest_path(u, v, ignore_blocked=True)`, `network.find_all_paths(u, v)`.
2. **Road Status (`RoadStatus`)**:
   - Query road availability: `road.status in [RoadStatus.OPEN, RoadStatus.CONGESTED]`.
3. **Junction State (`Junction`)**:
   - Query signal phase, pedestrian clearance lock (`crossing_active`), and emergency reservation flag (`emergency_reserved`).
4. **Signal Controller Interface (`SignalController`)**:
   - Import: `from app.simulation.signal_engine import SignalController`
   - Reserve emergency corridor: `controller.create_reservation(junction_id, reservation_id)`
   - Release emergency corridor: `controller.release_reservation(junction_id, reservation_id)`
   - Apply signal phase configuration: `controller.apply_configuration(signal_config)`
5. **Traffic State Snapshot (`TrafficState`)**:
   - Import: `from app.models.traffic import TrafficState`
   - Consume full simulation snapshot for QUBO/QAOA cost matrix formulation.
6. **Traffic Metrics Calculator (`MetricsService`)**:
   - Import: `from app.services.metrics_service import MetricsService`
   - Evaluate Hybrid/QAOA optimization results on identical metrics interface: `MetricsService.calculate_metrics(traffic_state)`.
7. **Diversion Impact Service (`DiversionService`)**:
   - Import: `from app.services.diversion_service import DiversionService`
   - Estimate downstream diversion impact: `diversion_service.estimate_diversion_impact(blocked_road_id)`.

---

## 6. Explicit Ownership Boundaries

### Owned by Backend Developer 1:
- Urban Network Topology & NetworkX graph management
- Pydantic Domain Models (`Road`, `Junction`, `TrafficState`, `SignalConfiguration`, `Incident`, `Metrics`)
- Deterministic Traffic Simulation Engine & Traffic Surge Scenario
- Incident Management Lifecycle (`ACCIDENT`, `ROAD_CLOSURE`)
- Classical Baseline Optimizer (`ClassicalOptimizer`)
- Signal Controller & Pedestrian Clearance Safety Engine
- Traffic Metrics & Diversion Impact Services
- REST API Layer & WebSocket Event Broadcaster

### Owned by Backend Developer 2 (Do NOT take over in Dev 1 codebase):
- Ambulance Routing & Dispatch Workflows
- Emergency Assignment Systems
- Green Corridor Decision Logic
- QUBO / QAOA Quantum Optimizers & Hybrid Algorithms
- Emergency Conflict Resolution Engines
- Emergency-specific REST APIs (`/api/emergency/...`)

---

## 7. Testing Verification Status

- **Total Unit Tests Executed**: 60
- **Total Tests Passed**: **60 passed** (100% pass rate)
- **Execution Time**: 1.48s
- **Test Modules**:
  - `backend/tests/test_phase1.py` (Network Graph & Pydantic Models)
  - `backend/tests/test_phase2.py` (Traffic Simulation Engine & Surge)
  - `backend/tests/test_phase3.py` (Incident Lifecycle Management)
  - `backend/tests/test_phase4.py` (Classical Optimizer & Signal Controller)
  - `backend/tests/test_phase5.py` (Metrics & Diversion Impact Services)
  - `backend/tests/test_phase6_api.py` (FastAPI REST API Endpoints)
  - `backend/tests/test_phase7_websocket.py` (WebSocket Manager & Event Broadcasting)
  - `backend/tests/test_golden_demo.py` (End-to-End 15-stage Golden Demo Integration Test)

---

## 8. Known Limitations

1. **Grid Topology**: Default network consists of a 6-junction 2x3 grid (`J1` to `J6`).
2. **Simulation Abstraction**: Traffic engine uses BPR (Bureau of Public Roads) travel time curves and deterministic vehicle density/queue approximations suited for hackathon-level simulation.
3. **In-Memory Storage**: System state (network, incidents, active connections) is maintained in-memory for zero-latency 24-hour hackathon execution without requiring PostgreSQL/PostGIS.
