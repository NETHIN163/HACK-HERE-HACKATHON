from typing import Dict, List, Optional, Tuple
from app.models.emergency import (
    AmbulanceStatus,
    EmergencyAssignment,
    EmergencyRequest,
    EmergencyRoute,
    EmergencyVehicle,
    RequestStatus,
    RouteStatus,
)
from app.services.emergency_routing_service import EmergencyRoutingService


class AmbulanceAssignmentService:
    """
    Ambulance Assignment Service (Backend Developer 2 Phase 2).
    Implements a deterministic multi-factor assignment algorithm selecting the optimal
    available ambulance for emergency dispatch based on travel time, distance, and stable tie-breaking.
    """

    def __init__(self, routing_service: EmergencyRoutingService):
        self.routing_service = routing_service

    def assign_ambulance_to_request(
        self,
        request_id: str,
        target_vehicle_id: Optional[str] = None,
    ) -> Optional[EmergencyAssignment]:
        """
        Assigns the optimal available ambulance to an emergency request using a deterministic rule:
        1. Primary: Lowest travel time to request origin.
        2. Secondary: Lowest total travel distance to request origin.
        3. Tertiary: Alphabetical vehicle_id for deterministic tie-breaking.
        
        State Updates:
        - Ambulance status -> DISPATCHED, assigned_request_id -> request_id
        - Request status -> ASSIGNED, vehicle_id -> ambulance_id
        """
        if request_id not in self.routing_service.requests:
            raise ValueError(f"Emergency request '{request_id}' not found.")

        req = self.routing_service.requests[request_id]

        if req.status == RequestStatus.ASSIGNED and req.vehicle_id:
            raise ValueError(f"Request '{request_id}' is already assigned to ambulance '{req.vehicle_id}'.")

        # 1. Filter available ambulances
        available_vehicles = [
            v for v in self.routing_service.vehicles.values()
            if v.status == AmbulanceStatus.AVAILABLE and (target_vehicle_id is None or v.vehicle_id == target_vehicle_id)
        ]

        if not available_vehicles:
            req.status = RequestStatus.UNROUTABLE
            return None

        # 2. Evaluate candidate routes for each available ambulance
        # Tuple: (travel_time, distance, vehicle_id, vehicle, route_to_origin, full_route)
        candidates: List[Tuple[float, float, str, EmergencyVehicle, EmergencyRoute, EmergencyRoute]] = []

        for veh in available_vehicles:
            # Route from ambulance current_location to request origin
            if veh.current_location == req.origin:
                # Ambulance is already at scene
                route_to_origin = EmergencyRoute(
                    route_id=f"RT_ZERO_{veh.vehicle_id}",
                    origin=veh.current_location,
                    destination=req.origin,
                    path=[req.origin],
                    road_ids=[],
                    total_distance=0.0,
                    estimated_travel_time=0.0,
                    status=RouteStatus.CALCULATED,
                )
            else:
                route_to_origin = self.routing_service.calculate_emergency_route(
                    origin=veh.current_location,
                    destination=req.origin,
                )

            if not route_to_origin:
                # No valid route available for this ambulance due to road blocks
                continue

            # Route from request origin to hospital destination
            route_to_dest = self.routing_service.calculate_emergency_route(
                origin=req.origin,
                destination=req.destination,
            )

            if not route_to_dest:
                # Scene-to-hospital route blocked
                continue

            # Build composite full route (ambulance -> origin -> destination)
            full_path = route_to_origin.path + route_to_dest.path[1:]
            full_road_ids = route_to_origin.road_ids + route_to_dest.road_ids
            full_dist = round(route_to_origin.total_distance + route_to_dest.total_distance, 2)
            full_time = round(route_to_origin.estimated_travel_time + route_to_dest.estimated_travel_time, 2)

            full_route = EmergencyRoute(
                route_id=f"RT_FULL_{veh.vehicle_id}_{req.request_id}",
                origin=veh.current_location,
                destination=req.destination,
                path=full_path,
                road_ids=full_road_ids,
                total_distance=full_dist,
                estimated_travel_time=full_time,
                status=RouteStatus.CALCULATED,
            )

            candidates.append((
                route_to_origin.estimated_travel_time,
                route_to_origin.total_distance,
                veh.vehicle_id,
                veh,
                route_to_origin,
                full_route,
            ))

        if not candidates:
            req.status = RequestStatus.UNROUTABLE
            return None

        # 3. Deterministic Sorting
        # Sort key: (time_to_origin, dist_to_origin, vehicle_id)
        candidates.sort(key=lambda c: (c[0], c[1], c[2]))
        best = candidates[0]

        best_time, best_dist, best_vid, best_veh, route_orig, full_route = best

        # 4. State Transitions
        best_veh.status = AmbulanceStatus.DISPATCHED
        best_veh.assigned_request_id = request_id

        req.status = RequestStatus.ASSIGNED
        req.vehicle_id = best_vid

        assign_id = f"ASG_{best_vid}_{request_id}"
        assignment = EmergencyAssignment(
            assignment_id=assign_id,
            request_id=request_id,
            vehicle_id=best_vid,
            route=full_route,
            timestamp=full_route.estimated_travel_time,
        )
        self.routing_service.assignments[assign_id] = assignment
        return assignment

    def release_ambulance(self, vehicle_id: str, new_location: Optional[str] = None) -> bool:
        """
        Releases a dispatched ambulance back to AVAILABLE status.
        Updates location if new_location specified, and completes associated request.
        """
        if vehicle_id not in self.routing_service.vehicles:
            return False

        veh = self.routing_service.vehicles[vehicle_id]

        if veh.assigned_request_id and veh.assigned_request_id in self.routing_service.requests:
            req = self.routing_service.requests[veh.assigned_request_id]
            req.status = RequestStatus.COMPLETED

        veh.assigned_request_id = None
        veh.status = AmbulanceStatus.AVAILABLE
        if new_location:
            if new_location in self.routing_service.network.junctions:
                veh.current_location = new_location

        return True
