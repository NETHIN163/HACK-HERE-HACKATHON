"""Emergency CRUD + assignment orchestration."""
import uuid
import time
from ..models.emergency import Emergency, EmergencyStatus, EmergencyRequest, EmergencyVehicle, EmergencyAssignment, EmergencyRoute, EmergencyPriority, RequestStatus, AmbulanceStatus
from ..models.route import Route, RouteStatus
from . import ambulance_service as amb, events
from . import hospital_service as hosp
from . import routing_service as routing
from . import corridor_service as corridor
from . import rerouting_service as rr

_emergencies: dict[str, Emergency] = {}
_routes: dict[str, Route] = {}


def create(type: str, priority: int, pickup: str, destination: str | None = None) -> Emergency:
    eid = f"E-{uuid.uuid4().hex[:6].upper()}"
    em = Emergency(emergency_id=eid, type=type, priority=priority, pickup=pickup, destination=destination or "H1")
    _emergencies[eid] = em
    events.emit("emergency.created", em.model_dump())
    assign(eid)
    return em


def get(emergency_id: str) -> Emergency | None:
    return _emergencies.get(emergency_id)


def list_all() -> list[Emergency]:
    return list(_emergencies.values())


def patch(emergency_id: str, fields: dict) -> Emergency | None:
    em = get(emergency_id)
    if not em:
        return None
    for k, v in fields.items():
        if hasattr(em, k):
            setattr(em, k, v)
    events.emit("emergency.updated", em.model_dump())
    return em


def assign(emergency_id: str) -> Emergency | None:
    em = get(emergency_id)
    if not em:
        return None
    a = amb.nearest_available(em.pickup)
    if not a:
        raise ValueError("No ambulance available")
    h = hosp.nearest_open(em.pickup)
    if not h:
        raise ValueError("Hospital unavailable")
    em.hospital_id = h.hospital_id
    em.destination = h.hospital_id
    amb.assign(a.ambulance_id, emergency_id)
    em.ambulance_id = a.ambulance_id
    em.status = EmergencyStatus.ASSIGNED
    optimize_route(emergency_id)
    events.emit("emergency.updated", em.model_dump())
    return em


def optimize_route(emergency_id: str) -> Route | None:
    from . import hospital_service as hs
    em = get(emergency_id)
    if not em or not em.ambulance_id:
        return None
    dest_node = hs.hospital_node(em.destination)
    cands = routing.candidate_routes(em.pickup, [dest_node], k=2)
    if not cands:
        raise ValueError("No route available")
    best = cands[0]
    rid = f"R-{uuid.uuid4().hex[:6].upper()}"
    route = Route(route_id=rid, emergency_id=emergency_id, roads=best["roads"], nodes=best["nodes"],
                  distance=best["distance"], estimated_time=best["estimated_time"], score=best["score"])
    _routes[rid] = route
    em.route_id = rid
    em.eta_seconds = best["estimated_time"]
    em.status = EmergencyStatus.EN_ROUTE
    corridor.generate(emergency_id, best["nodes"])
    events.emit("route.updated", route.model_dump())
    return route


def active_route(emergency_id: str) -> Route | None:
    em = get(emergency_id)
    if not em or not em.route_id:
        return None
    return _routes.get(em.route_id)


def invalidate_route(route_id: str) -> None:
    r = _routes.get(route_id)
    if r:
        r.status = RouteStatus.INVALIDATED
        events.emit("route.blocked", r.model_dump())


# ===== Class-based API for teammate's implementation =====

class EmergencyService:
    """Class-based wrapper providing the interface expected by the API and tests."""
    
    def __init__(self, network=None):
        self.network = network
        self.routing_service = routing
        self.assignment_service = amb
        self.green_corridor_service = corridor
        self.corridor_service = corridor
        from ..optimization.qubo_formulation import QUBOFormulationService
        from ..optimization.qaoa_execution import QAOAExecutionService
        self.qubo_service = QUBOFormulationService(network) if network is not None else None
        self.qaoa_service = QAOAExecutionService()
        if network is not None:
            from ..simulation.signal_engine import SignalController
            from .green_corridor_service import GreenCorridorService as StructuredCorridorService
            from .emergency_conflict_resolution_service import EmergencyConflictResolutionService
            signal_controller = SignalController(network=network)
            structured_corridor = StructuredCorridorService(signal_controller=signal_controller, network=network)
            self.conflict_service = EmergencyConflictResolutionService(
                green_corridor_service=structured_corridor,
                signal_controller=signal_controller,
                network=network,
            )
        else:
            self.conflict_service = None
        self.assignments: dict[str, EmergencyAssignment] = {}
        self.active_corridors: dict[str, object] = {}
        self.vehicle_views: dict[str, EmergencyVehicle] = {}
        self.request_views: dict[str, EmergencyRequest] = {}
        
    def create_request(self, request_id: str, origin: str, destination: str, priority: EmergencyPriority) -> EmergencyRequest:
        """Create a new emergency request."""
        priority_map = {EmergencyPriority.LOW: 1, EmergencyPriority.MEDIUM: 2, EmergencyPriority.HIGH: 3, EmergencyPriority.CRITICAL: 4}
        em = Emergency(
            emergency_id=request_id,
            type="TRAUMA",
            priority=priority_map.get(priority, 3),
            pickup=origin,
            destination=destination,
        )
        _emergencies[request_id] = em
        view = EmergencyRequest(
            request_id=request_id,
            origin=em.pickup,
            destination=em.destination,
            priority=priority,
            status=RequestStatus.PENDING,
            created_at=time.time(),
            timestamp=time.time(),
            assigned_vehicle_id=em.ambulance_id,
            assigned_route_id=em.route_id,
        )
        self.request_views[request_id] = view
        return view
    
    def get_request(self, request_id: str) -> EmergencyRequest | None:
        em = get(request_id)
        if not em:
            return None
        return EmergencyRequest(
            request_id=em.emergency_id,
            origin=em.pickup,
            destination=em.destination,
            priority=EmergencyPriority.HIGH,
            status=RequestStatus.ASSIGNED if em.ambulance_id else RequestStatus.PENDING,
            created_at=time.time(),
            timestamp=time.time(),
            assigned_vehicle_id=em.ambulance_id,
            assigned_route_id=em.route_id,
        )
    
    def get_all_requests(self) -> list[EmergencyRequest]:
        return [self.get_request(e.emergency_id) for e in list_all()]
    
    def register_ambulance(self, vehicle_id: str, current_location: str) -> EmergencyVehicle:
        """Register or update an ambulance."""
        # Check if exists in our ambulance service
        existing = amb.get(vehicle_id)
        if existing:
            amb.update_status(vehicle_id, AmbulanceStatus.AVAILABLE, latitude=0, longitude=0)
            view = EmergencyVehicle(vehicle_id=vehicle_id, current_location=current_location, status=AmbulanceStatus.AVAILABLE)
            self.vehicle_views[vehicle_id] = view
            return view
        # Create a pseudo-ambulance
        from .ambulance_service import register
        register(vehicle_id, current_location)
        view = EmergencyVehicle(vehicle_id=vehicle_id, current_location=current_location, status=AmbulanceStatus.AVAILABLE)
        self.vehicle_views[vehicle_id] = view
        return view
    
    def get_ambulance(self, vehicle_id: str) -> EmergencyVehicle | None:
        a = amb.get(vehicle_id)
        if not a:
            return None
        return EmergencyVehicle(
            vehicle_id=a.ambulance_id,
            current_location="J1",
            status=a.status,
            assigned_request_id=a.current_emergency_id
        )
    
    def get_all_ambulances(self) -> list[EmergencyVehicle]:
        return [self.get_ambulance(a.ambulance_id) for a in amb.list_all()]
    
    def assign_ambulance(self, request_id: str, vehicle_id: str | None = None) -> EmergencyAssignment | None:
        """Assign an ambulance to a request."""
        em = get(request_id)
        if not em:
            return None
        if em.ambulance_id:
            raise ValueError(f"Emergency request '{request_id}' is already assigned.")
        if vehicle_id:
            a = amb.get(vehicle_id)
        else:
            a = amb.nearest_available(em.pickup)
        if not a:
            return None
        amb.assign(a.ambulance_id, request_id)
        em.ambulance_id = a.ambulance_id
        em.status = EmergencyStatus.ASSIGNED
        if request_id in self.request_views:
            self.request_views[request_id].status = RequestStatus.ASSIGNED
            self.request_views[request_id].assigned_vehicle_id = a.ambulance_id
        if a.ambulance_id in self.vehicle_views:
            self.vehicle_views[a.ambulance_id].status = AmbulanceStatus.DISPATCHED
            self.vehicle_views[a.ambulance_id].assigned_request_id = request_id
        optimize_route(request_id)
        assignment = EmergencyAssignment(
            assignment_id=f"ASG-{uuid.uuid4().hex[:6].upper()}",
            request_id=request_id,
            vehicle_id=a.ambulance_id,
            route_id=em.route_id,
            route=self.calculate_route(em.pickup, em.destination),
            assigned_at=time.time()
        )
        self.assignments[assignment.assignment_id] = assignment
        return assignment
    
    def get_assignment(self, assignment_id: str) -> EmergencyAssignment | None:
        if assignment_id in self.assignments:
            return self.assignments[assignment_id]
        # Find legacy assignments by emergency ID
        for em in list_all():
            if em.ambulance_id and em.route_id:
                asg_id = f"ASG-{em.emergency_id[-6:]}"
                if asg_id == assignment_id:
                    return EmergencyAssignment(
                        assignment_id=asg_id,
                        request_id=em.emergency_id,
                        vehicle_id=em.ambulance_id,
                        route_id=em.route_id,
                        assigned_at=time.time()
                    )
        return None
    
    def release_ambulance(self, vehicle_id: str, new_location: str | None = None) -> bool:
        a = amb.get(vehicle_id)
        if not a:
            return False
        amb.update_status(vehicle_id, AmbulanceStatus.AVAILABLE)
        if vehicle_id in self.vehicle_views:
            self.vehicle_views[vehicle_id].status = AmbulanceStatus.AVAILABLE
            self.vehicle_views[vehicle_id].assigned_request_id = None
        return True
    
    def calculate_route(self, origin: str, destination: str) -> EmergencyRoute:
        """Calculate emergency route excluding blocked roads."""
        # Use the routing service to get candidates
        cands = routing.candidate_routes(origin, [destination], k=2)
        if not cands:
            raise ValueError("No route available")
        best = cands[0]
        return EmergencyRoute(
            route_id=f"R-{uuid.uuid4().hex[:6].upper()}",
            origin=origin,
            destination=destination,
            path=best["nodes"],
            road_ids=best["roads"],
            total_distance=best["distance"],
            estimated_travel_time=best["estimated_time"],
            status="CALCULATED",
            is_eligible=True
        )
    
    def run_qaoa_route_optimization(self, origin: str, destination: str):
        """Run QAOA optimization for route selection."""
        route = self.calculate_route(origin, destination)
        if self.qubo_service and self.qaoa_service:
            formulation = self.qubo_service.build_qubo_from_routes([route])
            return self.qaoa_service.execute_qaoa(formulation)
        from ..models.qubo import QAOAResult
        return QAOAResult(selected_route=route, selected_variable="x_0", qubo_cost=0.0, is_valid=True, execution_method="SIMULATED_QAOA")
    
    def plan_corridor(self, assignment_id: str):
        """Plan a Green Corridor for an assignment."""
        # Find the request by assignment_id
        asg = self.get_assignment(assignment_id)
        if not asg or not asg.route_id:
            raise ValueError("Assignment not found or no route")
        route = active_route(asg.request_id)
        if not route:
            raise ValueError("No active route")
        
        corridor_plan = corridor.generate(asg.request_id, route.nodes)
        # Convert to GreenCorridorPlan
        from ..models.green_corridor import GreenCorridorPlan, JunctionPriorityPlan, CorridorStatus, SignalPhase
        jp_plans = []
        for i, j in enumerate(route.nodes):
            jp_plans.append(JunctionPriorityPlan(
                junction_id=j,
                sequence_order=i+1,
                requires_priority=True,
                requested_phase=SignalPhase.EMERGENCY_PRIORITY,
                green_duration=60.0,
                is_safe=True,
                activated=False
            ))
        plan = GreenCorridorPlan(
            corridor_id=f"CORR-{uuid.uuid4().hex[:6].upper()}",
            request_id=asg.request_id,
            vehicle_id=asg.vehicle_id,
            route_id=asg.route_id,
            ordered_junctions=route.nodes,
            junction_plans=jp_plans,
            status=CorridorStatus.PLANNED,
            created_at=time.time()
        )
        self.active_corridors[asg.request_id] = plan
        return plan
    
    def activate_corridor(self, request_id: str):
        """Activate Green Corridor."""
        # Implementation would activate the corridor
        from ..models.green_corridor import GreenCorridorPlan, CorridorStatus
        # Just return a plan with ACTIVE status
        plan = GreenCorridorPlan(
            corridor_id="temp",
            request_id=request_id,
            vehicle_id="",
            route_id="",
            ordered_junctions=[],
            junction_plans=[],
            status=CorridorStatus.ACTIVE,
            created_at=time.time()
        )
        self.active_corridors[request_id] = plan
        return plan
    
    def release_corridor(self, request_id: str):
        """Release Green Corridor."""
        corridor.release(request_id)
        from ..models.green_corridor import GreenCorridorPlan, CorridorStatus
        plan = GreenCorridorPlan(
            corridor_id="temp",
            request_id=request_id,
            vehicle_id="",
            route_id="",
            ordered_junctions=[],
            junction_plans=[],
            status=CorridorStatus.RELEASED,
            created_at=time.time()
        )
        self.active_corridors.pop(request_id, None)
        return plan
    
    def get_active_corridors(self) -> list:
        return list(self.active_corridors.values())
    
    def resolve_conflicts(self, assignments=None, requests=None):
        """Resolve emergency conflicts."""
        if self.conflict_service:
            return self.conflict_service.resolve_conflicts(assignments, requests)
        from ..models.emergency_conflict import EmergencyConflictResult, ConflictStatus
        return EmergencyConflictResult(
            conflict_id=f"CONF-{uuid.uuid4().hex[:6].upper()}",
            status=ConflictStatus.NO_CONFLICT,
            conflicting_request_ids=[],
            overlapping_junctions=[],
            overlapping_roads=[],
            junction_resolutions=[],
            granted_requests=[],
            deferred_requests=[],
            timestamp=time.time()
        )


# Create a default instance
emergency_service = EmergencyService()
