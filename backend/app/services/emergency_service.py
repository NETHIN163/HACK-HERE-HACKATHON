from typing import Dict, List, Optional
from app.models.emergency import (
    AmbulanceStatus,
    EmergencyAssignment,
    EmergencyPriority,
    EmergencyRequest,
    EmergencyRoute,
    EmergencyVehicle,
    RequestStatus,
)
from app.models.emergency_conflict import EmergencyConflictResult
from app.models.green_corridor import GreenCorridorPlan
from app.models.qubo import QAOAResult, QUBOFormulation
from app.optimization.qaoa_execution import QAOAExecutionService
from app.optimization.qubo_formulation import QUBOFormulationService
from app.services.ambulance_assignment_service import AmbulanceAssignmentService
from app.services.emergency_conflict_resolution_service import EmergencyConflictResolutionService
from app.services.emergency_routing_service import EmergencyRoutingService
from app.services.green_corridor_service import GreenCorridorService
from app.services.traffic_service import traffic_service
from app.simulation.network import TrafficNetwork
from app.simulation.signal_engine import SignalController
from app.websocket.events import broadcast_event


class EmergencyService:
    """
    Central Orchestration Service for Backend Developer 2.
    Integrates Emergency Routing, Ambulance Assignment, QUBO Formulation, QAOA Execution,
    Green Corridor Management, and Conflict Resolution with real-time WebSocket broadcasts.
    """

    def __init__(self, network: Optional[TrafficNetwork] = None):
        self.network = network or traffic_service.network
        self.signal_controller = SignalController(network=self.network)
        
        # Instantiate services
        self.routing_service = EmergencyRoutingService(network=self.network)
        self.assignment_service = AmbulanceAssignmentService(routing_service=self.routing_service)
        self.qubo_service = QUBOFormulationService(network=self.network)
        self.qaoa_service = QAOAExecutionService(method="SIMULATED_QAOA")
        self.green_corridor_service = GreenCorridorService(
            signal_controller=self.signal_controller,
            network=self.network,
        )
        self.conflict_service = EmergencyConflictResolutionService(
            green_corridor_service=self.green_corridor_service,
            signal_controller=self.signal_controller,
            network=self.network,
        )

    # 1. Emergency Requests
    def create_request(
        self,
        request_id: str,
        origin: str,
        destination: str,
        priority: EmergencyPriority = EmergencyPriority.HIGH,
    ) -> EmergencyRequest:
        req = self.routing_service.create_emergency_request(
            request_id=request_id,
            origin=origin,
            destination=destination,
            priority=priority,
        )
        broadcast_event("emergency.created", f"request:{request_id}", req.model_dump())
        return req

    def get_request(self, request_id: str) -> Optional[EmergencyRequest]:
        return self.routing_service.requests.get(request_id)

    def get_all_requests(self) -> List[EmergencyRequest]:
        return list(self.routing_service.requests.values())

    # 2. Ambulances
    def register_ambulance(self, vehicle_id: str, current_location: str) -> EmergencyVehicle:
        veh = self.routing_service.register_ambulance(vehicle_id, current_location)
        broadcast_event("ambulance.registered", f"ambulance:{vehicle_id}", veh.model_dump())
        return veh

    def get_ambulance(self, vehicle_id: str) -> Optional[EmergencyVehicle]:
        return self.routing_service.vehicles.get(vehicle_id)

    def get_all_ambulances(self) -> List[EmergencyVehicle]:
        return list(self.routing_service.vehicles.values())

    # 3. Emergency Assignment
    def assign_ambulance(self, request_id: str, vehicle_id: Optional[str] = None) -> EmergencyAssignment:
        assignment = self.assignment_service.assign_ambulance_to_request(request_id, target_vehicle_id=vehicle_id)
        if not assignment:
            raise ValueError(f"No available ambulance or valid route found for request '{request_id}'.")

        broadcast_event("ambulance.assigned", f"request:{request_id}", assignment.model_dump())
        broadcast_event("emergency.route.updated", f"route:{assignment.route.route_id}", assignment.route.model_dump())
        return assignment

    def release_ambulance(self, vehicle_id: str, new_location: Optional[str] = None) -> bool:
        released = self.assignment_service.release_ambulance(vehicle_id, new_location)
        if released:
            broadcast_event("ambulance.released", f"ambulance:{vehicle_id}", {"vehicle_id": vehicle_id, "new_location": new_location})
        return released

    def get_assignment(self, assignment_id: str) -> Optional[EmergencyAssignment]:
        return self.routing_service.assignments.get(assignment_id)

    # 4. Emergency Routing
    def calculate_route(self, origin: str, destination: str) -> EmergencyRoute:
        route = self.routing_service.calculate_emergency_route(origin, destination)
        if not route:
            raise ValueError(f"No available emergency route between '{origin}' and '{destination}'.")
        broadcast_event("emergency.route.updated", f"route:{route.route_id}", route.model_dump())
        return route

    # 5. QUBO & QAOA Optimization
    def run_qaoa_route_optimization(self, origin: str, destination: str) -> QAOAResult:
        formulation = self.qubo_service.build_qubo_for_request(origin, destination)
        result = self.qaoa_service.execute_qaoa(formulation)
        if result.is_valid and result.selected_route:
            broadcast_event("emergency.route.updated", f"route:{result.selected_route.route_id}", result.selected_route.model_dump())
        return result

    # 6. Green Corridor
    def plan_corridor(self, assignment_id: str) -> GreenCorridorPlan:
        asg = self.get_assignment(assignment_id)
        if not asg:
            raise ValueError(f"Assignment '{assignment_id}' not found.")
        plan = self.green_corridor_service.plan_corridor(asg)
        broadcast_event("green_corridor.planned", f"corridor:{plan.corridor_id}", plan.model_dump())
        return plan

    def activate_corridor(self, request_id: str) -> GreenCorridorPlan:
        plan = self.green_corridor_service.activate_corridor(request_id)
        broadcast_event("green_corridor.activated", f"corridor:{plan.corridor_id}", plan.model_dump())
        return plan

    def release_corridor(self, request_id: str) -> GreenCorridorPlan:
        plan = self.green_corridor_service.release_corridor(request_id)
        broadcast_event("green_corridor.released", f"corridor:{plan.corridor_id}", plan.model_dump())
        return plan

    def get_active_corridors(self) -> List[GreenCorridorPlan]:
        return list(self.green_corridor_service.active_plans.values())

    # 7. Emergency Conflict Resolution
    def resolve_conflicts(self) -> EmergencyConflictResult:
        active_assignments = list(self.routing_service.assignments.values())
        result = self.conflict_service.resolve_conflicts(active_assignments, self.routing_service.requests)
        
        if result.status == "RESOLVED" and result.overlapping_junctions:
            broadcast_event("emergency.conflict.detected", "network", result.model_dump())
            broadcast_event("emergency.conflict.resolved", "network", result.model_dump())
        return result


# Shared global instance
emergency_service = EmergencyService()
