# Q-FLOW — BACKEND DEVELOPER 2
## OpenCode Task Specification — Emergency Routing, Ambulances, Green Corridor & Quantum Optimization

You own the **emergency workflow, ambulance management, route optimization, dynamic rerouting, Green Corridor, two-ambulance conflict handling, emergency APIs, QUBO/QAOA integration, and classical-vs-hybrid evaluation orchestration**.

Backend Developer 1 owns the traffic simulation, network state, incidents, classical traffic baseline, and signal infrastructure.

---

# 1. Core Responsibility

Implement the backend for:

```text
Emergency
→ Ambulance Assignment
→ Hospital Assignment
→ Route Optimization
→ Green Corridor
→ Live Monitoring
→ Accident on Route
→ Route Invalidation
→ Diversion Prediction
→ Dynamic Rerouting
→ Updated Green Corridor
→ Two-Ambulance Conflict
→ Hospital Arrival
→ Analytics
```

---

# 2. Stack

Use:

- Python
- FastAPI
- NetworkX
- Pydantic
- Qiskit
- Qiskit Aer
- NumPy
- Shared traffic/network services

Do not require real quantum hardware.

---

# 3. Suggested Structure

```text
backend/
└── app/
    ├── api/
    │   ├── emergencies.py
    │   ├── ambulances.py
    │   ├── hospitals.py
    │   ├── routes.py
    │   └── optimization.py
    ├── models/
    │   ├── ambulance.py
    │   ├── hospital.py
    │   ├── emergency.py
    │   ├── route.py
    │   └── corridor.py
    ├── services/
    │   ├── emergency_service.py
    │   ├── ambulance_service.py
    │   ├── routing_service.py
    │   ├── rerouting_service.py
    │   ├── corridor_service.py
    │   └── conflict_service.py
    └── optimization/
        ├── qubo.py
        ├── qaoa.py
        └── evaluator.py
```

Reuse Backend Developer 1's network and traffic services.

---

# 4. Data Models

## Ambulance

```text
ambulance_id
vehicle_number
status
latitude
longitude
current_emergency_id
current_hospital_id
current_route_id
eta_seconds
```

Statuses:

```text
AVAILABLE
EN_ROUTE
AT_PICKUP
TRANSPORTING
AT_HOSPITAL
REROUTING
DELAYED
```

## Hospital

```text
hospital_id
name
latitude
longitude
emergency_capacity
status
```

## Emergency

```text
emergency_id
type
priority
pickup
destination
ambulance_id
hospital_id
status
route_id
eta_seconds
```

---

# 5. Emergency APIs

Implement:

```text
POST /api/emergencies
GET  /api/emergencies
GET  /api/emergencies/{id}
PATCH /api/emergencies/{id}

GET  /api/ambulances
GET  /api/ambulances/{id}
POST /api/ambulances/{id}/assign

GET  /api/hospitals
GET  /api/hospitals/{id}

POST /api/emergencies/{id}/optimize-route
POST /api/emergencies/{id}/reroute
GET  /api/emergencies/{id}/route
```

Keep the final contract synchronized with both frontend developers.

---

# 6. Route Optimization

Do not use only shortest distance.

Consider:

```text
traffic density
road capacity
queue length
travel time
signal delay
accidents
road closures
pedestrian conditions where available
emergency priority
other emergency vehicles
hospital destination
predicted diversion impact
```

Use NetworkX.

Generate at least two candidate routes when feasible.

Each route should contain:

```text
roads
distance
estimated_time
score
status
```

---

# 7. Route Scoring

Implement a configurable weighted score.

Conceptually:

```text
route_cost =
    travel_time_weight * travel_time
  + congestion_weight * congestion
  + queue_weight * queue
  + signal_delay_weight * signal_delay
  + diversion_weight * predicted_diversion
  + safety_weight * safety_penalty
```

Blocked roads must be excluded.

Keep weights configurable.

Do not claim the weights are scientifically optimal; they are prototype parameters.

---

# 8. Accident on Active Route

This is a mandatory feature.

When an incident occurs:

```text
Detect Incident
↓
Check Active Emergency Routes
↓
Is Current Route Affected?
↓
Invalidate Old Route
↓
Release Old Signal Reservations
↓
Update Network
↓
Generate Alternatives
↓
Predict Diversion Impact
↓
Select Feasible Route
↓
Calculate New ETA
↓
Generate New Green Corridor
↓
Update Signals
```

The ambulance must never continue toward a blocked road.

---

# 9. Dynamic Rerouting

Implement:

```python
reroute_emergency(emergency_id)
```

Requirements:

- Check current road status.
- Remove blocked edges.
- Generate alternatives.
- Evaluate traffic.
- Estimate diversion.
- Select feasible route.
- Update ETA.
- Replace active route.
- Emit route update event.

If the new route later becomes blocked, reroute again.

---

# 10. Green Corridor

Implement a service that converts an emergency route into signal reservations.

Example:

```text
J1 → J2 → J3 → J5

J1 GREEN
J2 RESERVED
J3 PREPARING
J5 RESERVED
```

Requirements:

- Only compatible signal phases.
- No conflicting simultaneous greens.
- Temporary reservations.
- Release reservations after the ambulance passes or the route is invalidated.

---

# 11. Two-Ambulance Conflict

If two ambulances approach the same intersection from conflicting directions:

```text
Detect conflict
↓
Reserve intersection
↓
Choose safe sequence
↓
Apply clearance
↓
Release ambulance A
↓
Clear intersection
↓
Release ambulance B
```

The priority decision must be deterministic.

Possible prototype inputs:

```text
configured emergency priority
ETA
remaining route delay
dispatch priority
```

Do not diagnose medical urgency.

Never issue simultaneous conflicting greens.

---

# 12. Pedestrian Safety Integration

Before activating an emergency phase:

```text
Check pedestrian crossing
↓
If active:
    allow safe clearance
↓
Then activate emergency-compatible phase
```

Use the pedestrian state supplied by the traffic service.

---

# 13. QUBO

Implement a small QUBO suitable for the hackathon.

Example decision variables:

```text
x(junction, phase)
```

or another compact encoding that can represent signal choices.

Objective can include:

```text
waiting time
queue length
congestion
emergency delay
fuel estimate
CO2 estimate
pedestrian delay
safety penalties
```

Include penalty terms for invalid/conflicting configurations.

Keep the problem small enough for simulation.

---

# 14. QAOA

Use:

```text
Qiskit
Qiskit Aer
```

Pipeline:

```text
Traffic State
↓
QUBO
↓
QAOA
↓
Quantum Simulator
↓
Measurements
↓
Candidate Solutions
↓
Classical Feasibility Evaluation
↓
Best Feasible Candidate
```

The result must be converted into a traffic signal configuration.

Do not claim guaranteed global optimality or automatic quantum speedup.

---

# 15. Optimization API

Implement:

```text
POST /api/optimization/run
GET  /api/optimization/{id}
GET  /api/optimization/{id}/candidates
POST /api/optimization/classical
POST /api/optimization/hybrid
```

Example response:

```json
{
  "status": "COMPLETED",
  "mode": "HYBRID",
  "variables": 24,
  "candidates": 16,
  "objective": 761,
  "configuration": {
    "J1": "PHASE_2",
    "J2": "PHASE_1",
    "J3": "PHASE_2"
  }
}
```

---

# 16. Classical vs Hybrid Evaluation

Both methods must be evaluated against the same traffic scenario.

Metrics:

```text
average_waiting_time
maximum_queue
emergency_travel_time
emergency_delay
throughput
fuel_estimate
co2_estimate
pedestrian_delay
```

Return raw measured values.

Do not hard-code a result that makes one method appear superior.

---

# 17. WebSocket Events

Publish:

```text
emergency.created
emergency.updated
ambulance.position_updated
route.updated
route.blocked
reroute.started
reroute.completed
green_corridor.updated
optimization.completed
```

Use the shared event format.

---

# 18. Error Handling

Handle:

```text
No ambulance available
No route available
All routes blocked
Hospital unavailable
Invalid emergency
Emergency not found
Rerouting failure
Optimization failure
Quantum simulator failure
```

Use consistent JSON error responses.

---

# 19. Testing

Test:

- Emergency creation
- Ambulance assignment
- Hospital assignment
- Candidate route generation
- Blocked road exclusion
- Accident-on-route rerouting
- ETA update
- Green Corridor generation
- Green Corridor release
- Two-ambulance conflict
- Pedestrian clearance
- QUBO generation
- QAOA execution
- Classical vs hybrid evaluation

At minimum, create one deterministic Golden Demo test.

---

# 20. Integration With Backend Developer 1

Consume:

```text
Road graph
Road status
Traffic state
Junction state
Signal controller
Pedestrian state
Diversion impact service
Traffic metrics
Incident events
```

Do not duplicate those systems.

Provide to Frontend:

```text
Emergency state
Ambulance state
Route state
ETA
Green Corridor
Reroute events
Conflict decisions
Optimization results
```

## Priority

If time is limited:

**Emergency APIs → Routing → Accident Reroute → Green Corridor → Two-Ambulance Conflict → QUBO → QAOA → Evaluation**
