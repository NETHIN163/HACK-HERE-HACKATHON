import time
from typing import Dict, List, Optional
from app.models.emergency import (
    AmbulanceStatus,
    EmergencyAssignment,
    EmergencyPriority,
    EmergencyRequest,
    EmergencyRoute,
    EmergencyVehicle,
    RequestStatus,
    RouteStatus,
)
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork


class EmergencyRoutingService:
    """
    Emergency Routing & Dispatch Service (Backend Developer 2 Foundation).
    Computes optimal emergency vehicle routes using NetworkX graph, avoiding BLOCKED/CLOSED roads
    and incorporating current travel-time information.
    """

    def __init__(self, network: TrafficNetwork):
        self.network = network
        self.vehicles: Dict[str, EmergencyVehicle] = {}
        self.requests: Dict[str, EmergencyRequest] = {}
        self.assignments: Dict[str, EmergencyAssignment] = {}

    def register_ambulance(self, vehicle_id: str, current_location: str) -> EmergencyVehicle:
        """Registers a new ambulance or updates location of existing vehicle."""
        if current_location not in self.network.junctions:
            raise ValueError(f"Invalid junction ID: '{current_location}' does not exist in network.")

        vehicle = EmergencyVehicle(
            vehicle_id=vehicle_id,
            current_location=current_location,
            status=AmbulanceStatus.AVAILABLE,
        )
        self.vehicles[vehicle_id] = vehicle
        return vehicle

    def create_emergency_request(
        self,
        request_id: str,
        origin: str,
        destination: str,
        priority: EmergencyPriority = EmergencyPriority.HIGH,
    ) -> EmergencyRequest:
        """Creates a new emergency dispatch request."""
        if origin not in self.network.junctions:
            raise ValueError(f"Invalid origin junction ID: '{origin}'")
        if destination not in self.network.junctions:
            raise ValueError(f"Invalid destination junction ID: '{destination}'")

        req = EmergencyRequest(
            request_id=request_id,
            origin=origin,
            destination=destination,
            priority=priority,
            status=RequestStatus.PENDING,
            timestamp=time.time(),
        )
        self.requests[request_id] = req
        return req

    def calculate_emergency_route(self, origin: str, destination: str) -> Optional[EmergencyRoute]:
        """
        Calculates optimal emergency route from origin to destination:
        1. Excludes BLOCKED and CLOSED roads.
        2. Considers current travel-time information.
        3. Returns EmergencyRoute object or None if no valid route exists.
        """
        if origin not in self.network.junctions or destination not in self.network.junctions:
            raise ValueError(f"Invalid origin ('{origin}') or destination ('{destination}').")

        # NetworkX path search ignoring BLOCKED and CLOSED roads, weighted by current travel_time
        path = self.network.get_shortest_path(origin, destination, ignore_blocked=True)
        if not path or len(path) < 2:
            return None

        road_ids: List[str] = []
        total_dist = 0.0
        total_time = 0.0

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            road_id = f"R_{u}_{v}"
            road = self.network.get_road(road_id)
            if not road or road.status in [RoadStatus.BLOCKED, RoadStatus.CLOSED]:
                # Double safety check: path contains an unavailable road
                return None
            road_ids.append(road_id)
            total_dist += road.distance
            total_time += road.travel_time

        route_id = f"ROUTE_EMG_{int(time.time() * 1000) % 100000}"
        return EmergencyRoute(
            route_id=route_id,
            origin=origin,
            destination=destination,
            path=path,
            road_ids=road_ids,
            total_distance=round(total_dist, 2),
            estimated_travel_time=round(total_time, 2),
            status=RouteStatus.CALCULATED,
        )

    def assign_emergency(
        self,
        request_id: str,
        vehicle_id: Optional[str] = None,
    ) -> Optional[EmergencyAssignment]:
        """
        Assigns an available ambulance to an emergency request and computes the emergency route.
        Updates vehicle and request statuses.
        """
        if request_id not in self.requests:
            raise ValueError(f"Emergency request '{request_id}' not found.")

        req = self.requests[request_id]

        # Select ambulance vehicle
        selected_vehicle: Optional[EmergencyVehicle] = None
        if vehicle_id:
            if vehicle_id not in self.vehicles:
                raise ValueError(f"Vehicle '{vehicle_id}' not registered.")
            selected_vehicle = self.vehicles[vehicle_id]
        else:
            # Find first available ambulance
            for veh in self.vehicles.values():
                if veh.status == AmbulanceStatus.AVAILABLE:
                    selected_vehicle = veh
                    break

        if not selected_vehicle:
            raise ValueError("No available ambulance found for dispatch.")

        # Calculate emergency route from request origin to destination
        route = self.calculate_emergency_route(req.origin, req.destination)
        if not route:
            req.status = RequestStatus.UNROUTABLE
            return None

        # Update vehicle & request statuses
        selected_vehicle.status = AmbulanceStatus.DISPATCHED
        selected_vehicle.assigned_request_id = request_id

        req.status = RequestStatus.ASSIGNED
        req.vehicle_id = selected_vehicle.vehicle_id

        assign_id = f"ASG_{int(time.time() * 1000) % 100000}"
        assignment = EmergencyAssignment(
            assignment_id=assign_id,
            request_id=request_id,
            vehicle_id=selected_vehicle.vehicle_id,
            route=route,
            timestamp=time.time(),
        )
        self.assignments[assign_id] = assignment
        return assignment
