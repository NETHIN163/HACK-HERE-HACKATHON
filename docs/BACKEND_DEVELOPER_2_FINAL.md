# Backend Developer 2 — Final Integration & Architecture Specification

## 1. Backend Developer 2 Status
- **Status**: **COMPLETE** (Phases 1–8 fully implemented and validated)
- **Test Suite Result**: **120 / 120 tests passing (100% pass rate, 0 failures, 0 errors)**
- **FastAPI REST API Status**: Operational under `/api/emergency/...`
- **WebSocket Event System Status**: Operational with real-time broadcasts for emergency lifecycle events

---

## 2. Completed Phases (Phases 1–8 Summary)
- **Phase 1 — Emergency Routing Foundation**: Domain models (`EmergencyVehicle`, `EmergencyRequest`, `EmergencyRoute`, `EmergencyAssignment`) & NetworkX pathfinding excluding `BLOCKED`/`CLOSED` roads.
- **Phase 2 — Ambulance Assignment**: Rule-based deterministic assignment strategy (Travel Time $\rightarrow$ Route Distance $\rightarrow$ Vehicle ID tie-breaking).
- **Phase 3 — QUBO Formulation Foundation**: Binary quadratic formulation ($H(x) = x^T Q x$) encoding route travel times and quadratic single-choice constraints ($P = 1000.0$).
- **Phase 4 — QAOA Execution Layer**: Simulated/classical QAOA execution module providing deterministic ground-state evaluation suitable for MVP without requiring external quantum hardware.
- **Phase 5 — Green Corridor Decision Logic**: Emergency signal priority planning, junction sequence extraction, and pedestrian clearance lock validation (`SignalController` integration).
- **Phase 6 — Emergency Conflict Resolution**: Detection and resolution of overlapping emergency route priority requests (Priority Rating $\rightarrow$ Travel Time $\rightarrow$ Request Timestamp $\rightarrow$ ID tie-breaking).
- **Phase 7 — Emergency REST API & WebSocket Integration**: 16 REST endpoints under `/api/emergency/...` and 11 real-time WebSocket event broadcasts integrated into main FastAPI app.
- **Phase 8 — End-to-End Golden Demo & Final Integration**: Comprehensive 17-step integration test (`backend/tests/test_golden_demo_backend2.py`) validating the complete pipeline from network initialization to final ambulance release.

---

## 3. Emergency Architecture

```
                                +----------------------------------+
                                |  FastAPI App (app/main.py)       |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                | EmergencyService (Orchestrator) |
                                +----------------------------------+
                                                 |
         +--------------------+------------------+-------------------+---------------------+
         |                    |                     |                |                     |
         v                    v                     v                v                     v
+------------------+ +------------------+ +-------------------+ +-------------------+ +-------------------+
| Routing Service  | | Assignment Svc   | | QUBO + QAOA Layer | | Green Corridor    | | Conflict Res Svc |
| (NetworkX Graph) | | (Rule-based)     | | (app/optimization)| | Service           | | (Priority Rank)   |
+------------------+ +------------------+ +-------------------+ +-------------------+ +-------------------+
         |                    |                     |                |                     |
         +--------------------+------------------+--+----------------+---------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                | WebSocket broadcast_event()      |
                                +----------------------------------+
```

---

## 4. Emergency Workflow Pipeline

1. **Emergency Request**: `POST /api/emergency/requests` creates an `EmergencyRequest` in `PENDING` state.
2. **Ambulance Assignment**: `POST /api/emergency/assignments` selects the optimal available ambulance using shortest travel time to origin, updates vehicle state to `DISPATCHED`, and request status to `ASSIGNED`.
3. **Emergency Route**: `EmergencyRoutingService` calculates the shortest path over `TrafficNetwork` while strictly avoiding `BLOCKED` and `CLOSED` roads.
4. **QUBO Formulation**: Candidate emergency routes are converted into a binary QUBO problem ($H(x) = x^T Q x$).
5. **QAOA Execution**: `QAOAExecutionService` evaluates the QUBO energy matrix and identifies the optimal 1-hot decision vector.
6. **Green Corridor Planning**: `GreenCorridorService` identifies junction sequence, checks active pedestrian clearance locks, and creates a `GreenCorridorPlan`.
7. **Conflict Resolution**: `EmergencyConflictResolutionService` resolves competing priority requests for shared junctions deterministically.
8. **Signal Priority Activation**: Signal controllers apply temporary emergency priority phases safely.
9. **Corridor & Ambulance Release**: Once the emergency vehicle reaches its destination, the corridor is released (`RELEASED`), signal timing reverts to normal, and the ambulance returns to `AVAILABLE` status.

---

## 5. REST API Summary

| Category | HTTP Method | Route | Description |
| :--- | :--- | :--- | :--- |
| **Emergency Requests** | `POST` | `/api/emergency/requests` | Create emergency dispatch request |
| | `GET` | `/api/emergency/requests` | List all emergency requests |
| | `GET` | `/api/emergency/requests/{request_id}` | Retrieve single emergency request |
| **Ambulances** | `GET` | `/api/emergency/ambulances` | List all registered ambulances and statuses |
| | `POST` | `/api/emergency/ambulances` | Register ambulance or update location |
| | `GET` | `/api/emergency/ambulances/{vehicle_id}` | Retrieve single ambulance state |
| **Assignments** | `POST` | `/api/emergency/assignments` | Assign available ambulance to emergency request |
| | `GET` | `/api/emergency/assignments/{assignment_id}` | Retrieve assignment details |
| | `POST` | `/api/emergency/assignments/{assignment_id}/release` | Release ambulance assignment |
| **Routing** | `POST` | `/api/emergency/routes` | Calculate emergency route excluding blocked roads |
| **QUBO / QAOA** | `POST` | `/api/emergency/optimize` | Run QAOA quantum route optimization |
| **Green Corridor** | `POST` | `/api/emergency/corridors/plan` | Create Green Corridor plan |
| | `POST` | `/api/emergency/corridors/{request_id}/activate` | Activate Green Corridor priority signals |
| | `POST` | `/api/emergency/corridors/{request_id}/release` | Release active Green Corridor |
| | `GET` | `/api/emergency/corridors/active` | Retrieve active Green Corridor state |
| **Conflict Resolution**| `POST` | `/api/emergency/conflicts/resolve` | Detect and resolve emergency priority conflicts |

---

## 6. WebSocket Event Summary

All events are broadcasted in real time over `ws://host/ws` with the unified payload structure:

- `emergency.created` — Emitted when an emergency request is created.
- `emergency.updated` — Emitted when request status or priority changes.
- `ambulance.registered` — Emitted when an ambulance is registered or updates location.
- `ambulance.assigned` — Emitted when an ambulance is assigned to a request.
- `ambulance.released` — Emitted when an ambulance completes dispatch and returns to `AVAILABLE`.
- `emergency.route.updated` — Emitted when emergency route is calculated or updated.
- `green_corridor.planned` — Emitted when a Green Corridor plan is generated.
- `green_corridor.activated` — Emitted when Green Corridor signal priority is activated.
- `green_corridor.released` — Emitted when Green Corridor priority is released.
- `emergency.conflict.detected` — Emitted when overlapping emergency requests are detected.
- `emergency.conflict.resolved` — Emitted when emergency conflict resolution policy is applied.

---

## 7. QUBO / QAOA Approach

- **QUBO Formulation** (`app/optimization/qubo_formulation.py`):
  - Formulates emergency route selection as $H(x) = \sum_k c_k x_k + P (\sum_k x_k - 1)^2 + \sum_{k \in \text{ineligible}} P_{\text{ineligible}} x_k$.
  - Assigns heavy penalties ($P = 1000.0$, $P_{\text{ineligible}} = 10000.0$) to prevent selecting multiple routes or routes traversing `BLOCKED`/`CLOSED` roads.
- **QAOA Execution** (`app/optimization/qaoa_execution.py`):
  - Provides a deterministic simulated/classical ground-state solver for production deployment without external quantum hardware requirements.
  - Returns a structured `QAOAResult` containing the optimal binary decision vector and selected `EmergencyRoute`.

---

## 8. Ambulance Assignment Logic

- **Candidate Evaluation**: Filters available ambulances (`status == AVAILABLE`) and computes route to emergency scene + scene to destination hospital.
- **Deterministic Selection Ranking**:
  1. Primary: Lowest estimated travel time to scene.
  2. Secondary: Lowest travel distance to scene.
  3. Tertiary: Alphabetical `vehicle_id` tie-breaking.
- **State Management**: Updates ambulance to `DISPATCHED` and request to `ASSIGNED`. Prevents duplicate dispatch assignments.

---

## 9. Green Corridor Decision Logic

- **Plan Construction**: Identifies ordered sequence of junctions along selected route.
- **Safety Locks**:
  - Validates active pedestrian crossings. If clearance is active (`crossing_remaining_seconds > 0`), priority activation is safely deferred.
  - Validates signal movement safety through Backend 1's `SignalController`.
- **Lifecycle**: `PLANNED` $\rightarrow$ `ACTIVE` $\rightarrow$ `RELEASED`.

---

## 10. Emergency Conflict Resolution

- **Overlap Detection**: Maps all active emergency routes across junctions and road segments to identify multi-vehicle conflicts.
- **Resolution Policy**:
  1. Emergency Priority Rating (`CRITICAL` > `HIGH` > `MEDIUM` > `LOW`).
  2. Route Travel Time (Shorter travel time receives priority).
  3. Request Timestamp (Earlier timestamp receives priority).
  4. Alphabetical Request ID string sorting for deterministic tie-breaking.
- **Outcome**: Grants corridor priority to the winning request while safely deferring losing requests at shared junctions until the winning corridor is released.

---

## 11. Golden Demo Workflow (17 Steps)

The dedicated integration test (`backend/tests/test_golden_demo_backend2.py`) validates:
1. **Network Initialization**: Loads `TrafficNetwork` with junctions and roads.
2. **Initial Traffic**: Validates initial density, queue lengths, travel times.
3. **Traffic Surge**: Triggers traffic surge and validates congestion response.
4. **Incident**: Creates accident incident blocking road `R_J1_J4`.
5. **Emergency Request**: Creates `CRITICAL` priority request `REQ_GD2_1`.
6. **Ambulance Assignment**: Registers ambulances and assigns `AMB_GD2_1`.
7. **Emergency Route**: Calculates route avoiding blocked road `R_J1_J4`.
8. **QUBO**: Formulates binary QUBO problem matrix.
9. **QAOA**: Solves QUBO formulation using simulated QAOA execution.
10. **Green Corridor**: Plans `GreenCorridorPlan` for junction sequence `['J1', 'J2', 'J3']`.
11. **Conflict Resolution**: Validates single-request and multi-request conflict resolution.
12. **Activate Green Corridor**: Activates signal priority safely through `SignalController`.
13. **Traffic/Signal Updates**: Verifies real-time API and WebSocket event broadcasting during active corridor.
14. **Metrics**: Validates calculation of waiting time, queues, throughput, delay, fuel, and CO₂ metrics.
15. **Corridor Release**: Releases active Green Corridor and grants deferred request.
16. **Ambulance Release**: Releases ambulance back to `AVAILABLE` state and reuses it for a new request.
17. **Final State Validation**: Confirms clean network state, zero stale active corridors, and correct road statuses.

---

## 12. Test Results

- **Backend Developer 1 Tests**: 60 passed
- **Backend Developer 2 Tests**: 60 passed
- **Total Suite**: **120 / 120 passed (100% pass rate, 0 failures, 0 errors)**

---

## 13. Known Limitations & Assumptions

1. **Simulated Quantum Execution**: QAOA layer operates in deterministic simulated execution mode so the application runs reliably without requiring external quantum hardware.
2. **Frontend Scope Boundary**: React UI integration is strictly outside Backend Developer 2 and ready for frontend integration in Phase 9.
3. **Database Scope**: In-memory state storage is used for the MVP scope; production database persistence layers can be wired to the service interfaces if required in future releases.
